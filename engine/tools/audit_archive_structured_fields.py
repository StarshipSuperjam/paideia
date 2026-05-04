"""Session-shutdown audit for missing structured archive fields.

Layer 1 contract per ADR 0042 + ADR 0048.

Purpose
-------
Defend the persistent-warn surface (per ADR 0042) against silent
field-absence lapses in session archives. The surface counts categories
inside ``outcome_summary_soft_warns`` and flags persistence at 3-of-5
recent archives. The mechanism *cannot detect a missing field* — a
session that forgets to write the field is invisible to the surface for
the next 5 sessions.

Empirical evidence: the S-0052 health-check audit found that S-0043
through S-0047 (five consecutive archives) lacked the field entirely
(not empty — the JSON key was absent). The boot-surface message
"calibration window in effect (4/5 structured archives; surface defers
until 5)" was the visible symptom; the root cause was the absent field.

This audit fires at session-shutdown after the structured field is
written and BEFORE the archive is committed. Hard-fail blocks the close.

Symmetric in shape to ``audit_handoff_dispositions.py`` — that audit
catches HANDOFF disposition lapses; this audit catches archive-field
lapses. Both fire from the pre-commit hook on closing commits, both
exit 2 on hard-fail, both report to stderr.

Inputs
------
The session's in-flight ``engine/session/current.json``. The audit
reads the file, validates the field, and exits.

Detection
---------
1. ``outcome_summary_soft_warns`` key missing → hard-fail.
2. ``outcome_summary_soft_warns`` value is JSON ``null`` → hard-fail.
3. ``outcome_summary_soft_warns`` value is ``{}`` (empty dict) → pass.
   Empty is the legitimate shape for a session whose validate.py emitted
   no warnings (rare but possible). The optional secondary check below
   catches the "default-empty written without thought" failure mode
   without blocking the legitimate case.

Optional secondary check (soft-warn only, exit 0)
-------------------------------------------------
If ``outcome_summary_soft_warns`` is present but empty AND the session
had >= 3 commits (counted via the auto-detected eager-claim range), emit
a stderr soft-warn pointing at the likely "wrote empty by default"
pattern. This is an advisory; the field is technically present and
non-null, so the hard-fail does not fire.

Exit codes
----------
- ``0`` — field present and non-null (with optional soft-warn note).
- ``2`` — field absent or null. Per-finding detail to stderr.

CLI
---
- ``audit_archive_structured_fields.py`` — defaults to
  ``engine/session/current.json`` under the script's repo root.
- ``audit_archive_structured_fields.py --current-path PATH`` — override
  the input path (any file with the same JSON shape works).
- ``audit_archive_structured_fields.py --from-stdin`` — read the JSON
  from stdin instead. Used by the pre-commit hook on closing commits,
  which pipes the staged archive content via ``git show :<path>``.
  current.json has been deleted in the staged commit at that point.
- ``audit_archive_structured_fields.py --repo-root PATH`` — override
  for test fixtures (used when computing the eager-claim range for
  the optional secondary check).

Out of scope
------------
- No detection of *malformed* ``outcome_summary_soft_warns`` shapes
  (e.g., a list instead of a dict, or string keys with non-int values).
  ``validate.py`` writes the field; if it goes wrong upstream, that's
  a validate.py bug, not this audit's concern.
- No archive-history audit. This fires only against the in-flight
  ``current.json``. Retroactively detecting lapses across past archives
  belongs in ``health_check.py`` (see S-0052 Finding C for prior art).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_PATH = REPO_ROOT / "engine" / "session" / "current.json"
EAGER_CLAIM_PATTERN = re.compile(
    r"^chore\(session\): eager-claim S-\d{4}\b", re.MULTILINE
)
EMPTY_DICT_COMMIT_THRESHOLD = 3


def load_current(path: Path) -> dict[str, object]:
    """Read and parse the in-flight session file."""
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, object] = json.load(f)
        return data


def session_commit_count(repo: Path) -> int | None:
    """Best-effort count of commits since the eager-claim.

    Returns None if no eager-claim is found in the recent history (in which
    case the secondary check is skipped). The count includes the eager-claim
    commit itself, so a typical 'just-claimed-no-other-commits' session
    returns 1.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "log", "--format=%s", "-n", "50"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    lines = result.stdout.splitlines()
    for idx, subject in enumerate(lines):
        if EAGER_CLAIM_PATTERN.match(subject):
            return idx + 1
    return None


def main(argv: list[str] | None = None) -> int:
    """CLI entry. Returns 0 on clean, 2 on hard-fail."""
    parser = argparse.ArgumentParser(
        description=(
            "Audit the in-flight engine/session/current.json for the "
            "outcome_summary_soft_warns structured field. Defends ADR 0042's "
            "persistent-warn surface against silent field-absence lapses."
        ),
    )
    parser.add_argument(
        "--current-path",
        type=Path,
        default=DEFAULT_CURRENT_PATH,
        help="Path to current.json (default: engine/session/current.json).",
    )
    parser.add_argument(
        "--from-stdin",
        action="store_true",
        help=(
            "Read the JSON from stdin instead of --current-path. Used by the "
            "pre-commit hook on closing commits where current.json has been "
            "deleted and the staged archive content is piped in."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root for git invocations (used by the secondary check).",
    )
    args = parser.parse_args(argv)

    current_path: Path = args.current_path
    repo: Path = args.repo_root
    source_label = "stdin" if args.from_stdin else str(current_path)

    if args.from_stdin:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            print(
                f"[audit-archive-structured-fields] stdin is not valid JSON: {exc}",
                file=sys.stderr,
            )
            return 2
    else:
        if not current_path.is_file():
            print(
                f"[audit-archive-structured-fields] {current_path} not found; "
                "nothing to audit (no in-flight session).",
                flush=True,
            )
            return 0

        try:
            data = load_current(current_path)
        except json.JSONDecodeError as exc:
            print(
                f"[audit-archive-structured-fields] {current_path} is not valid "
                f"JSON: {exc}",
                file=sys.stderr,
            )
            return 2

    field = "outcome_summary_soft_warns"
    if field not in data:
        print(
            f"[audit-archive-structured-fields] HARD-FAIL: "
            f"{source_label} is missing the '{field}' key.",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print(
            "Per ADR 0042, every session archive must carry "
            f"'{field}' (a dict mapping soft-warn category names to counts; "
            "{} is acceptable for a clean session).",
            file=sys.stderr,
        )
        print(
            "Write the field at the shutdown step that builds outcome_summary "
            "(see engine/operations/session-shutdown-sequence.md step 8). "
            "Empirical lapses: S-0043 through S-0047 each lacked this field, "
            "blinding the persistent-warn surface for 5 consecutive sessions.",
            file=sys.stderr,
        )
        return 2

    value = data[field]
    if value is None:
        print(
            f"[audit-archive-structured-fields] HARD-FAIL: "
            f"{source_label} has '{field}' set to null.",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print(
            "Null is a placeholder, not a value. If the session genuinely had "
            "no soft-warns, write {} (empty dict). If validate.py reported "
            "warnings, write the per-category counts dict.",
            file=sys.stderr,
        )
        return 2

    if not isinstance(value, dict):
        print(
            f"[audit-archive-structured-fields] HARD-FAIL: "
            f"{source_label} has '{field}' of type "
            f"{type(value).__name__}, expected dict.",
            file=sys.stderr,
        )
        return 2

    # Field is present, non-null, dict. Optional secondary check: if empty
    # and the session had multiple commits, surface a stderr advisory.
    if value == {}:
        commit_count = session_commit_count(repo)
        if commit_count is not None and commit_count >= EMPTY_DICT_COMMIT_THRESHOLD:
            print(
                f"[audit-archive-structured-fields] advisory: '{field}' is "
                f"empty but session has {commit_count} commits since "
                f"eager-claim. If validate.py emitted soft-warns during the "
                f"session, the field may have been written empty-by-default. "
                f"Confirm the empty value is intentional.",
                file=sys.stderr,
            )

    n = len(value) if isinstance(value, dict) else 0
    print(
        f"[audit-archive-structured-fields] PASS: '{field}' present "
        f"with {n} categor{'y' if n == 1 else 'ies'}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
