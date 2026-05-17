"""Deterministic step-13 archive mutation tool (per S-0194 / closes the empirical S-0185/0187/0190/0191 closure-failure lapse class).

What this replaces
------------------
Pre-S-0194, step 13 of ``engine/operations/session-shutdown-sequence.md``
was a manual procedure:

    mv engine/session/current.json engine/session/archive/S-NNNN.json
    # ...then edit the archive JSON by hand to add `closed_at` and
    # change `status` from `in_progress` to `closed`...
    # ...then edit engine/session/register_state.json to set
    # `current_status: "closed"`.

Four of the last ten sessions (S-0185, S-0187, S-0190, S-0191) closed
with archive JSONs missing one or both of those manually-edited fields.
The mistakes silently rode the close commit because the existing
``audit_archive_structured_fields.py`` defended other archive fields but
not ``closed_at`` or ``status`` (extended at S-0194 — see that file's
REQUIRED_ARCHIVE_FIELDS). This tool is the mechanical replacement for
the manual edit class.

What it does
------------
1. Reads ``engine/session/current.json``.
2. Validates the in-flight payload has the expected shape
   (``id`` matches ``^S-\\d{4}$``, ``status`` is ``in_progress``).
3. Adds ``closed_at`` (canonical UTC second-precision timestamp via
   ``engine.tools.timestamps.emit()`` — satisfies the
   ``timestamp_helper_bypass`` ADR 0058 contract).
4. Sets ``status`` to ``closed`` (default) or ``closed_partial`` (when
   ``--partial`` is passed; matches the budget-cap-reached close shape
   per session-shutdown-sequence.md "Partial closure" section).
5. Writes the mutated payload to ``engine/session/archive/S-NNNN.json``.
6. Atomically updates ``engine/session/register_state.json`` to flip
   ``current_status`` from ``in_progress`` to ``closed``.
7. Deletes ``engine/session/current.json``.

Idempotency
-----------
Re-running on an already-archived session is safe. The tool checks for
the destination archive's existence first; if present AND its content
matches what would be written (same ``id``, same ``status``, same
non-null ``closed_at``), the run is a no-op exiting 0. If present but
with DIFFERENT content (a partial prior run, manual edit, or different
session id), the tool refuses with exit 2 — the user must adjudicate.

Exit codes (matches the build_lifecycle_push.py / routine_lifecycle_push.py
/ apply_migration.py wrapper convention)
---------------------------------------
- ``0`` — archived successfully (or idempotent no-op match).
- ``2`` — verification refused (malformed current.json, archive already
  exists with different content, register_state out-of-shape, missing
  required field on the in-flight payload).
- ``3`` — generic filesystem error.

CLI
---
- ``archive_session.py`` — default operation; closes as ``status="closed"``.
- ``--partial`` — close as ``status="closed_partial"`` (budget-cap path).
- ``--repo-root PATH`` — override repo root for tests.
- ``--current-path PATH`` — override the in-flight current.json path.

Cross-references
----------------
- engine/operations/session-shutdown-sequence.md step 13 (Layer 1
  procedure this tool mechanizes).
- engine/tools/audit_archive_structured_fields.py REQUIRED_ARCHIVE_FIELDS
  (the defense this tool feeds clean output into).
- engine/tools/timestamps.py (canonical timestamp surface per ADR 0058).
- engine/tools/build_lifecycle_push.py (sibling wrapper, exit-code shape source).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timestamps import emit as emit_timestamp  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_PATH = REPO_ROOT / "engine" / "session" / "current.json"
DEFAULT_ARCHIVE_DIR = REPO_ROOT / "engine" / "session" / "archive"
DEFAULT_REGISTER_PATH = REPO_ROOT / "engine" / "session" / "register_state.json"
SESSION_ID_PATTERN = re.compile(r"^S-(\d{4})$")


def _err(msg: str) -> None:
    print(f"[archive-session] {msg}", file=sys.stderr)


def _ok(msg: str) -> None:
    print(f"[archive-session] {msg}")


def _validate_inflight(payload: dict[str, Any]) -> tuple[bool, str]:
    """Return (ok, reason) for an in-flight current.json payload.

    Rejects: missing/malformed id, status not in_progress (suggests a
    prior partial run), missing started_at (load-bearing for the archive
    canon).
    """
    sid = payload.get("id")
    if not isinstance(sid, str) or not SESSION_ID_PATTERN.match(sid):
        return False, f"id={sid!r} is not in canonical S-NNNN form"
    status = payload.get("status")
    if status != "in_progress":
        return (
            False,
            f"current.json status={status!r}; expected 'in_progress'. If a "
            f"prior archive attempt left current.json in an unexpected "
            f"state, manually adjudicate before retrying.",
        )
    started_at = payload.get("started_at")
    if not isinstance(started_at, str) or not started_at.strip():
        return False, f"started_at={started_at!r} missing or empty"
    return True, ""


def _validate_register(payload: dict[str, Any], session_id: str) -> tuple[bool, str]:
    """Return (ok, reason) for the register_state.json payload."""
    cs = payload.get("current_status")
    if cs not in ("in_progress", "closed"):
        return (
            False,
            f"register_state.json current_status={cs!r}; expected "
            f"'in_progress' (or 'closed' for idempotent reruns).",
        )
    last = payload.get("last_claimed")
    if last != session_id:
        return (
            False,
            f"register_state.json last_claimed={last!r} but in-flight "
            f"session is {session_id!r}; eager-claim/close mismatch.",
        )
    return True, ""


def archive_session(
    current_path: Path,
    archive_dir: Path,
    register_path: Path,
    partial: bool = False,
) -> int:
    """Run the step-13 mutation. Returns the CLI exit code."""
    if not current_path.is_file():
        _err(f"current.json not found at {current_path}; nothing to archive.")
        return 2
    try:
        current = json.loads(current_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _err(f"current.json is not valid JSON: {exc}")
        return 2
    if not isinstance(current, dict):
        _err(
            f"current.json top-level is not a JSON object (got {type(current).__name__})."
        )
        return 2

    ok, reason = _validate_inflight(current)
    if not ok:
        _err(f"verification refused: {reason}")
        return 2

    sid: str = current["id"]
    archive_path = archive_dir / f"{sid}.json"
    new_status = "closed_partial" if partial else "closed"
    new_closed_at = emit_timestamp()

    # Idempotent-rerun check. If the archive already exists, compare its
    # content. Match → no-op success. Diff on closed_at/status alone (e.g.,
    # the rerun would change closed_at to a later timestamp) → refuse so
    # the user adjudicates rather than the tool silently overwriting.
    if archive_path.exists():
        try:
            existing = json.loads(archive_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            _err(
                f"archive {archive_path} exists but is not valid JSON: {exc}. "
                f"Manual adjudication required."
            )
            return 2
        if (
            existing.get("id") == sid
            and existing.get("status") in ("closed", "closed_partial")
            and isinstance(existing.get("closed_at"), str)
            and existing.get("closed_at", "").strip()
        ):
            _ok(
                f"archive {archive_path.name} already exists with status="
                f"{existing.get('status')!r} and closed_at={existing.get('closed_at')!r}; "
                f"idempotent no-op (still cleaning up current.json + register if needed)."
            )
            # Still ensure current.json is gone and register reflects closed.
            try:
                current_path.unlink(missing_ok=True)
            except OSError as exc:
                _err(f"could not unlink current.json: {exc}")
                return 3
            _flip_register_to_closed(register_path, sid)
            return 0
        _err(
            f"archive {archive_path} exists but content does not match the "
            f"expected post-close shape (id={existing.get('id')!r}, "
            f"status={existing.get('status')!r}, closed_at="
            f"{existing.get('closed_at')!r}). Manual adjudication required."
        )
        return 2

    # Register-state pre-check. Tolerate current_status='closed' as a
    # legitimate idempotent-rerun-after-archive-write state.
    if not register_path.is_file():
        _err(f"register_state.json not found at {register_path}.")
        return 2
    try:
        register = json.loads(register_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _err(f"register_state.json is not valid JSON: {exc}")
        return 2
    ok, reason = _validate_register(register, sid)
    if not ok:
        _err(f"verification refused: {reason}")
        return 2

    # Build the archive payload — preserve every existing field; add
    # closed_at + status.
    archive_payload: dict[str, Any] = dict(current)
    archive_payload["status"] = new_status
    archive_payload["closed_at"] = new_closed_at

    # Write archive (pretty-printed to match existing format).
    try:
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path.write_text(
            json.dumps(archive_payload, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        _err(f"could not write archive {archive_path}: {exc}")
        return 3

    # Flip register_state.
    rc = _flip_register_to_closed(register_path, sid)
    if rc != 0:
        return rc

    # Delete current.json.
    try:
        current_path.unlink()
    except OSError as exc:
        _err(f"could not unlink current.json after archive write: {exc}")
        return 3

    _ok(
        f"archived {sid} → {archive_path.name} (status={new_status}, "
        f"closed_at={new_closed_at}); register_state.json flipped to closed; "
        f"current.json removed."
    )
    return 0


def _flip_register_to_closed(register_path: Path, session_id: str) -> int:
    """Idempotently set register_state.current_status to 'closed'.

    Returns 0 on success, 3 on filesystem error.
    """
    try:
        register = json.loads(register_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        _err(f"could not read register_state.json for flip: {exc}")
        return 3
    if register.get("current_status") == "closed":
        return 0
    register["current_status"] = "closed"
    register["last_claimed"] = session_id
    try:
        register_path.write_text(
            json.dumps(register, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        _err(f"could not write register_state.json: {exc}")
        return 3
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministic step-13 archive mutation. Replaces the manual "
            "mv + JSON edits with a single idempotent call. Per S-0194 / "
            "engine/operations/session-shutdown-sequence.md step 13."
        ),
    )
    parser.add_argument(
        "--partial",
        action="store_true",
        help=(
            "Close as status='closed_partial' (budget-cap-reached close "
            "per the Partial closure section of session-shutdown-sequence.md)."
        ),
    )
    parser.add_argument(
        "--current-path",
        type=Path,
        default=DEFAULT_CURRENT_PATH,
        help="Path to current.json (default: engine/session/current.json).",
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=DEFAULT_ARCHIVE_DIR,
        help="Archive directory (default: engine/session/archive/).",
    )
    parser.add_argument(
        "--register-path",
        type=Path,
        default=DEFAULT_REGISTER_PATH,
        help="register_state.json path (default: engine/session/register_state.json).",
    )
    args = parser.parse_args(argv)
    return archive_session(
        args.current_path, args.archive_dir, args.register_path, partial=args.partial
    )


if __name__ == "__main__":
    sys.exit(main())
