#!/usr/bin/env python3
"""Diagnose + recover from a partial session close (per ADR 0100 Item 4).

Ported from Engine's ``.engine/tools/lifecycle/recover_partial_close.py``
and adapted to Paideia's archive layout (single ``engine/session/current.json``
+ ``engine/session/archive/S-NNNN.json`` + ``register_state.json``).

A clean close is a sequence of mutations:

1. Update ``register_state.json`` ``current_status`` → ``"closed"``.
2. Update ``engine/STATE.md`` Current + Last session rows.
3. Author ``engine/changelog/<YYYY>/S-NNNN-<topic>.md``.
4. Fill ``current.json``'s ``outcome_summary`` + ``scope_delivery`` +
   ``next_session_handle``.
5. ``git mv engine/session/current.json engine/session/archive/S-NNNN.json``.
6. Commit + FF + push via ``build_lifecycle_push.py close``.

If anything between steps 1 and 6 fails (validator hard-fail, allowlist
refusal, network error), the working-tree state can land in one of seven
shapes. This tool diagnoses the shape mechanically and offers three
narrow recovery actions. Each action shape-verifies before mutating;
refuses on shape mismatch.

State shapes
------------

  STATE                                        | current.json | archive | close commit | register
  ---------------------------------------------|--------------|---------|--------------|-----------
  ARCHIVE_AND_CURRENT_AND_NO_CLOSE_COMMIT      | present      | present | absent       | in_progress
  ARCHIVE_AND_CURRENT_BUT_CLOSE_COMMITTED      | present      | present | present      | closed
  CURRENT_ONLY                                 | present      | absent  | absent       | in_progress
  ARCHIVE_ORPHAN_NO_COMMIT                     | absent       | present | absent       | in_progress
  CLOSE_PENDING_REGISTER_FLIP                  | absent       | present | absent       | in_progress* (matches archived session)
  CLOSE_CLEAN                                  | absent       | present | present      | closed
  NOTHING_TO_RECOVER                           | absent       | absent  | (any)        | closed/absent

Recovery flags
--------------

- ``--remove-active`` — delete duplicate ``current.json`` when in
  ARCHIVE_AND_CURRENT_*. Verifies same session ID before mutating.
- ``--rollback-archive`` — move archive back to ``current.json`` +
  restore register ``current_status: in_progress``. For ARCHIVE_ORPHAN_*
  shapes (archive landed but close commit refused). Refuses if a close
  commit is already on HEAD (use ``git revert`` instead).
- ``--land-close`` — stage pending register flip + STATE.md + changelog
  edits and author the missing close commit. For CLOSE_PENDING_REGISTER_FLIP.
  Refuses if shape doesn't match.

All actions emit a structured pre-flight report; refuse with explicit
reason and exit code 2 if shape doesn't match.

Exit codes
----------

- 0 — diagnosis emitted (no flags), or recovery succeeded
- 2 — recovery refused (shape mismatch); no mutation performed
- 3 — recovery action error (e.g., git mv failed); state may be partially
  mutated and requires manual cleanup

Per ADR 0100 (Engine pattern port).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SESSION_DIR_REL = "engine/session"
CURRENT_REL = f"{SESSION_DIR_REL}/current.json"
REGISTER_REL = f"{SESSION_DIR_REL}/register_state.json"
ARCHIVE_DIR_REL = f"{SESSION_DIR_REL}/archive"
CLOSE_COMMIT_SUBJECT_RE = re.compile(r"^chore\(session\): close (S-\d{4})\b")


def _run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run ``git <args>`` from ``cwd``; return (rc, stdout, stderr)."""
    proc = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def repo_root() -> Path:
    rc, out, _err = _run_git(["rev-parse", "--show-toplevel"], cwd=Path.cwd())
    if rc != 0 or not out:
        raise RuntimeError("not in a git repo (or git rev-parse failed)")
    return Path(out).resolve()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _current_session_id(root: Path) -> str | None:
    """Read current.json's id field; None if file absent or malformed."""
    current = _read_json(root / CURRENT_REL)
    if current is None:
        return None
    return current.get("id")


def _register_status(root: Path) -> tuple[str | None, str | None]:
    """Return (current_status, last_claimed). Each may be None if absent."""
    register = _read_json(root / REGISTER_REL)
    if register is None:
        return None, None
    return register.get("current_status"), register.get("last_claimed")


def _archive_for(root: Path, session_id: str) -> Path:
    return root / ARCHIVE_DIR_REL / f"{session_id}.json"


def _head_close_commit_session(root: Path) -> str | None:
    """If HEAD commit subject matches ``close S-NNNN``, return that ID."""
    rc, out, _err = _run_git(["log", "-1", "--pretty=%s", "HEAD"], cwd=root)
    if rc != 0:
        return None
    match = CLOSE_COMMIT_SUBJECT_RE.match(out)
    if match:
        return match.group(1)
    return None


def diagnose(root: Path) -> dict[str, Any]:
    """Return diagnosis dict naming the state + hint."""
    current_id = _current_session_id(root)
    register_status, last_claimed = _register_status(root)

    # Determine which session ID to inspect for archive presence.
    target_id = current_id or last_claimed
    archive_path = _archive_for(root, target_id) if target_id else None
    archive_present = bool(archive_path and archive_path.exists())

    head_close_id = _head_close_commit_session(root)
    close_committed_for_target = bool(target_id and head_close_id == target_id)

    current_present = current_id is not None

    if current_present and archive_present and not close_committed_for_target:
        state = "ARCHIVE_AND_CURRENT_AND_NO_CLOSE_COMMIT"
        hint = (
            "Archive written + current.json still present, close commit "
            "not landed. Likely the validator/wrapper rejected the close "
            "commit between archive write and final commit. "
            "Use --rollback-archive to restore pre-close state, OR "
            "--remove-active if you intend to keep the archive and land "
            "the close commit manually."
        )
    elif current_present and archive_present and close_committed_for_target:
        state = "ARCHIVE_AND_CURRENT_BUT_CLOSE_COMMITTED"
        hint = (
            "Close commit landed but current.json wasn't removed. "
            "Safe to clean up with --remove-active. The next session "
            "boot would otherwise route through the eager-claim collision "
            "check."
        )
    elif current_present and not archive_present:
        state = "CURRENT_ONLY"
        hint = (
            "In-flight session, no close attempted. Nothing to recover; "
            "continue working or invoke session-shutdown-sequence cleanly."
        )
    elif not current_present and archive_present and not close_committed_for_target:
        # current.json gone, archive landed, no close commit. Two sub-shapes:
        # (a) the close commit failed to author (CLOSE_PENDING_REGISTER_FLIP
        #     — register flip + STATE.md + changelog updates are in the working
        #     tree, possibly staged), (b) the archive write completed but
        # everything else is missing (ARCHIVE_ORPHAN_NO_COMMIT).
        # Discriminator: working-tree edits/staged changes to register/STATE.md/changelog.
        # register_status is NOT a discriminator — it can be either "in_progress"
        # (close flow didn't reach the flip yet) or "closed" (flip is in working
        # tree but not committed).
        rc, status_out, _ = _run_git(["status", "--porcelain"], cwd=root)
        has_close_artifacts = False
        if rc == 0:
            relevant = (REGISTER_REL, "engine/STATE.md", "engine/changelog/")
            for line in status_out.splitlines():
                if len(line) < 4:
                    continue
                path = line[3:]
                if any(path.startswith(r) for r in relevant):
                    has_close_artifacts = True
                    break
        if has_close_artifacts:
            state = "CLOSE_PENDING_REGISTER_FLIP"
            hint = (
                "Archive landed + close artifacts staged/modified "
                "(register/STATE.md/changelog) but the close commit "
                "didn't author. Use --land-close to stage + commit the "
                "pending close artifacts. If the validator rejects "
                "again, address the hard-fail and retry."
            )
        else:
            state = "ARCHIVE_ORPHAN_NO_COMMIT"
            hint = (
                "Archive present but no current.json, no close commit, "
                "and no close-artifact edits in the working tree. The "
                "in-flight state is lost; use --rollback-archive to "
                "remove the orphan archive + restore register to "
                "in_progress, then re-author the close from scratch."
            )
    elif not current_present and archive_present and close_committed_for_target:
        state = "CLOSE_CLEAN"
        hint = "Session closed cleanly. No recovery needed."
    elif not current_present and not archive_present:
        state = "NOTHING_TO_RECOVER"
        hint = "No active session, no archive. Nothing to recover."
    else:
        state = "UNKNOWN"
        hint = (
            "Unrecognized state combination — inspect by hand. Please "
            "file an Issue with the shape signature so this tool can "
            "be extended."
        )

    return {
        "target_session_id": target_id,
        "current_present": current_present,
        "archive_present": archive_present,
        "close_committed": close_committed_for_target,
        "register_status": register_status,
        "register_last_claimed": last_claimed,
        "state": state,
        "hint": hint,
    }


def _print_diagnosis(diag: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(diag, indent=2))
        return
    print(f"=== diagnosis ===")
    for k in (
        "target_session_id",
        "current_present",
        "archive_present",
        "close_committed",
        "register_status",
        "register_last_claimed",
    ):
        print(f"  {k}: {diag[k]}")
    print(f"  state: {diag['state']}")
    print(f"  hint: {diag['hint']}")


def action_remove_active(root: Path, diag: dict[str, Any]) -> int:
    """Delete duplicate current.json. Refuses if shape mismatch."""
    accepted = {
        "ARCHIVE_AND_CURRENT_AND_NO_CLOSE_COMMIT",
        "ARCHIVE_AND_CURRENT_BUT_CLOSE_COMMITTED",
    }
    if diag["state"] not in accepted:
        print(
            f"[refuse] --remove-active: state {diag['state']!r} not in "
            f"{sorted(accepted)}; refusing to mutate.",
            file=sys.stderr,
        )
        return 2
    if not diag["current_present"]:
        print(
            "[refuse] --remove-active: current.json absent (no duplicate to remove).",
            file=sys.stderr,
        )
        return 2

    # Verify session IDs match (current.json id == archive's S-NNNN)
    current = _read_json(root / CURRENT_REL)
    if current is None or current.get("id") != diag["target_session_id"]:
        print(
            "[refuse] --remove-active: current.json id mismatch vs archive id; "
            "refusing to mutate.",
            file=sys.stderr,
        )
        return 2

    (root / CURRENT_REL).unlink()
    print(f"[recovered] removed duplicate {CURRENT_REL}", file=sys.stderr)
    return 0


def action_rollback_archive(root: Path, diag: dict[str, Any]) -> int:
    """Move archive back to current.json + restore register to in_progress."""
    accepted = {
        "ARCHIVE_AND_CURRENT_AND_NO_CLOSE_COMMIT",
        "ARCHIVE_ORPHAN_NO_COMMIT",
    }
    if diag["state"] not in accepted:
        print(
            f"[refuse] --rollback-archive: state {diag['state']!r} not in "
            f"{sorted(accepted)}; refusing to mutate.",
            file=sys.stderr,
        )
        return 2
    if diag["close_committed"]:
        print(
            "[refuse] --rollback-archive: close commit already landed; "
            "rollback would orphan the commit. Use `git revert` instead.",
            file=sys.stderr,
        )
        return 2

    target_id = diag["target_session_id"]
    if not target_id:
        print(
            "[refuse] --rollback-archive: no target session ID resolvable.",
            file=sys.stderr,
        )
        return 2
    archive = _archive_for(root, target_id)
    if not archive.exists():
        print(
            f"[refuse] --rollback-archive: archive {archive} does not exist.",
            file=sys.stderr,
        )
        return 2

    current = root / CURRENT_REL

    # If both archive and current.json exist (state ARCHIVE_AND_CURRENT_*),
    # the rollback intent is "discard the archive, keep the in-flight state."
    # If only archive exists, the rollback intent is "restore the archive
    # to in-flight state."
    if current.exists():
        # State ARCHIVE_AND_CURRENT_*: just remove the archive.
        archive.unlink()
        print(
            f"[recovered] removed orphan archive {archive.relative_to(root)}",
            file=sys.stderr,
        )
        return 0

    # State ARCHIVE_ORPHAN_NO_COMMIT: move archive back to current.json.
    archive.rename(current)
    print(
        f"[recovered] restored {CURRENT_REL} from "
        f"{archive.relative_to(root)}",
        file=sys.stderr,
    )
    # Restore register to in_progress (if it was already in_progress, no-op).
    register = _read_json(root / REGISTER_REL)
    if register and register.get("current_status") != "in_progress":
        register["current_status"] = "in_progress"
        (root / REGISTER_REL).write_text(
            json.dumps(register, indent=2) + "\n", encoding="utf-8"
        )
        print(
            f"[recovered] flipped {REGISTER_REL} current_status → in_progress",
            file=sys.stderr,
        )
    return 0


def action_land_close(root: Path, diag: dict[str, Any]) -> int:
    """Stage pending close artifacts + author the missing close commit.

    Intended for state CLOSE_PENDING_REGISTER_FLIP. Stages all working-tree
    edits to register_state.json + STATE.md + engine/changelog/, then
    commits with the canonical close subject. Per ADR 0048 disposition
    discipline, any HANDOFF additions get audited at the next commit.
    """
    if diag["state"] != "CLOSE_PENDING_REGISTER_FLIP":
        print(
            f"[refuse] --land-close: state {diag['state']!r} != "
            "CLOSE_PENDING_REGISTER_FLIP; refusing to mutate.",
            file=sys.stderr,
        )
        return 2
    target_id = diag["target_session_id"]
    if not target_id:
        print(
            "[refuse] --land-close: no target session ID resolvable.",
            file=sys.stderr,
        )
        return 2

    # Stage register + STATE.md + changelog edits + the archive (just in case).
    paths_to_stage = [
        REGISTER_REL,
        "engine/STATE.md",
        "engine/changelog/",
        ARCHIVE_DIR_REL,
    ]
    rc, _out, err = _run_git(["add", *paths_to_stage], cwd=root)
    if rc != 0:
        print(f"[error] --land-close: git add failed: {err}", file=sys.stderr)
        return 3

    # Verify the staged set includes at least one close artifact.
    rc, out, _ = _run_git(
        ["diff", "--cached", "--name-only"], cwd=root
    )
    if rc != 0 or not out:
        print(
            "[refuse] --land-close: nothing staged after add; cannot author commit.",
            file=sys.stderr,
        )
        return 2

    subject = f"chore(session): close {target_id} — recovered via recover_partial_close.py"
    body = (
        f"Authored by engine/tools/recover_partial_close.py --land-close.\n"
        f"Pre-flight diagnosis: {diag['state']}.\n"
        f"Recovered after close commit failed mid-shutdown sequence.\n\n"
        f"Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
    )
    rc, _out, err = _run_git(
        ["commit", "-m", subject, "-m", body], cwd=root
    )
    if rc != 0:
        print(
            f"[error] --land-close: git commit failed (pre-commit hook may "
            f"have rejected): {err}",
            file=sys.stderr,
        )
        return 3
    print(
        f"[recovered] authored close commit for {target_id}",
        file=sys.stderr,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--remove-active",
        action="store_true",
        help="remove duplicate current.json (when archive landed but current.json wasn't deleted)",
    )
    parser.add_argument(
        "--rollback-archive",
        action="store_true",
        help="move archive back to current.json + restore register (only safe pre-commit)",
    )
    parser.add_argument(
        "--land-close",
        action="store_true",
        help="stage pending close artifacts + author the missing close commit (CLOSE_PENDING_REGISTER_FLIP)",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit diagnosis as JSON"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="override repo root (for test fixtures)",
    )
    args = parser.parse_args(argv)

    flag_count = sum(
        [args.remove_active, args.rollback_archive, args.land_close]
    )
    if flag_count > 1:
        print(
            "[refuse] specify at most one of --remove-active / "
            "--rollback-archive / --land-close.",
            file=sys.stderr,
        )
        return 2

    root = args.repo_root.resolve() if args.repo_root else repo_root()
    diag = diagnose(root)
    _print_diagnosis(diag, as_json=args.json)

    if args.remove_active:
        return action_remove_active(root, diag)
    if args.rollback_archive:
        return action_rollback_archive(root, diag)
    if args.land_close:
        return action_land_close(root, diag)
    return 0


if __name__ == "__main__":
    sys.exit(main())
