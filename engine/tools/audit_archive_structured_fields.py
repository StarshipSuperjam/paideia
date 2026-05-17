"""Session-shutdown audit for missing structured archive fields.

Layer 1 contract per ADR 0042 + ADR 0048; parameterized at S-0078 per
ADR 0056 (this session) and Issue #20 closure.

Purpose
-------
Defend the archive structured-field contract against silent field-absence
lapses. Multiple ADRs have added structured fields to the archive over
time, and each accumulates an audit-coverage gap unless the audit is
extended to cover the new field. Issue #20 (S-0065 Finding A; S-0077
strengthening evidence) flagged the recurring pattern:

==============  =====================================  =============================  ============
Added by        Field                                  Field-absence emerged at       Caught at
==============  =====================================  =============================  ============
ADR 0042        ``outcome_summary_soft_warns``         S-0057 archive                 S-0065
ADR 0051        ``mode``                               S-0065 + S-0069 archives       S-0077
ADR 0056        ``mempalace_activity`` (this session)  (none yet — S-0078 forward)    n/a
==============  =====================================  =============================  ============

The S-0078 closure parameterizes the audit to a declarative
``REQUIRED_ARCHIVE_FIELDS`` list. Future structured-field ADRs add a row
to that list in the same session per ADR 0053 mechanism-first-exercise-gate
framing — no audit code change required.

In-flight mode (default)
------------------------
Reads the in-flight ``engine/session/current.json``; for every required
field whose ``since_session`` is ``<=`` the session's id, validates the
field is present, non-null, and of the expected shape. Hard-fails block
the close commit (the pre-commit hook invokes via ``--from-stdin`` on
``chore(session): close S-NNNN`` commits).

Archive-history mode (``--archive-history``)
--------------------------------------------
Walks every ``engine/session/archive/S-NNNN.json`` and reports any
archive whose session id is ``>=`` a field's ``since_session`` but lacks
the field (or carries it with the wrong shape). Informational only — does
NOT modify historical archives. Closes Issue #20: the health-check audit
pass that surfaces the lapse class as a structured cross-archive report
instead of relying on per-audit ad-hoc grep.

Detection
---------
For each field in ``REQUIRED_ARCHIVE_FIELDS``:

1. If ``current_session_id < since_session_id``: skip (field not yet
   required at this session's vintage).
2. Field absent → hard-fail.
3. Field is JSON ``null`` → hard-fail.
4. Field has the wrong shape (dict expected got list, etc.) → hard-fail.
5. Field is the legitimate empty value (``{}`` for dict, ``""`` for str,
   ``0`` for int) → pass with optional advisory.

Optional secondary check (soft-warn only, exit 0)
-------------------------------------------------
For ``outcome_summary_soft_warns`` specifically: if the field is present
but ``{}`` AND the session had ``>= 3`` commits since eager-claim, emit
a stderr advisory pointing at the likely "wrote empty by default"
pattern. Preserved from the pre-S-0078 contract.

Exit codes
----------
- ``0`` — every required field present and well-formed (in-flight mode);
  archive-history report emitted (informational mode).
- ``2`` — at least one field absent, null, or malformed (in-flight mode).

CLI
---
- ``audit_archive_structured_fields.py`` — defaults to
  ``engine/session/current.json`` under the script's repo root.
- ``--current-path PATH`` — override the input path.
- ``--from-stdin`` — read the JSON from stdin instead. Used by the
  pre-commit hook on closing commits.
- ``--repo-root PATH`` — override for test fixtures (used when computing
  the eager-claim range for the optional secondary check).
- ``--archive-history`` — walk every archive, emit Markdown report to
  stdout, exit 0. Informational mode for Issue #20.

Out of scope
------------
- No detection of malformed nested values within a structured field
  (e.g., a string-keyed dict whose values aren't ints). ``validate.py``
  writes the fields; per-field invariants belong upstream.
- No backfill of historical archives. Archive-history mode REPORTS;
  it does not modify.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_PATH = REPO_ROOT / "engine" / "session" / "current.json"
ARCHIVE_DIR = REPO_ROOT / "engine" / "session" / "archive"
EAGER_CLAIM_PATTERN = re.compile(
    r"^chore\(session\): eager-claim S-\d{4}\b", re.MULTILINE
)
SESSION_ID_PATTERN = re.compile(r"^S-(\d{4})$")
EMPTY_DICT_COMMIT_THRESHOLD = 3


# Declarative field set. Each entry names a structured archive field, the
# session vintage from which it became required, the expected JSON shape,
# and the ADR that introduced it. An optional `allowed_values` key (a list)
# constrains a string field to a canonical vocabulary — a value outside the
# set hard-fails, the same as a shape mismatch. Add a row when a new
# structured-field ADR lands — do NOT change the audit logic itself.
REQUIRED_ARCHIVE_FIELDS: list[dict[str, Any]] = [
    {
        "field": "outcome_summary_soft_warns",
        "since_session": "S-0055",
        "shape": "dict",
        "adr": "ADR 0042",
    },
    {
        "field": "mode",
        "since_session": "S-0048",
        "shape": "str",
        "adr": "ADR 0051",
        # Canonical session-execution-style vocabulary (S-0157 / Issue #121):
        # "interactive" for /start-engine build sessions, "routine" for
        # unattended cadence-fired routine sessions. The value records the
        # durable execution style, not a project-phase label. Pre-S-0157
        # archives carried drift (build / engine / interactive_build) —
        # backfilled to "interactive" at S-0157.
        "allowed_values": ["interactive", "routine"],
    },
    {
        "field": "mempalace_activity",
        "since_session": "S-0078",
        "shape": "dict",
        "adr": "ADR 0056 (S-0078)",
    },
    {
        "field": "engine_memory_activity",
        "since_session": "S-0192",
        "shape": "dict",
        "adr": "ADR 0091 (S-0192)",
    },
    {
        "field": "next_session_handle",
        "since_session": "S-0100",
        "shape": "str_or_null",
        "adr": "ADR 0049 Decision 6 (S-0100 amendment)",
    },
]


def parse_session_id(session_str: str | None) -> int | None:
    """Parse 'S-NNNN' to integer NNNN. Returns None on malformed input."""
    if not isinstance(session_str, str):
        return None
    m = SESSION_ID_PATTERN.match(session_str.strip())
    if m is None:
        return None
    return int(m.group(1))


def shape_check(value: Any, expected: str) -> str | None:
    """Return error string if value's shape doesn't match expected, else None.

    The `str_or_null` shape (S-0100) accepts either a string or None — the
    only nullable shape token. Used by `next_session_handle` per ADR 0049
    Decision 6, where null is a load-bearing semantic ("explicit no defer")
    distinct from missing (which still hard-fails as a forgotten field).
    Other shape tokens reject None at the top of the function so a missing
    placeholder doesn't pass the audit silently.
    """
    if expected == "str_or_null":
        if value is None:
            return None
        if not isinstance(value, str):
            return f"expected str or null, got {type(value).__name__}"
        return None
    if value is None:
        return "value is null"
    if expected == "dict":
        if not isinstance(value, dict):
            return f"expected dict, got {type(value).__name__}"
    elif expected == "str":
        if not isinstance(value, str):
            return f"expected str, got {type(value).__name__}"
    elif expected == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            return f"expected int, got {type(value).__name__}"
    elif expected == "list":
        if not isinstance(value, list):
            return f"expected list, got {type(value).__name__}"
    else:
        return f"unknown expected shape '{expected}' (audit bug)"
    return None


def applicable_fields(session_id_int: int | None) -> list[dict[str, Any]]:
    """Return REQUIRED_ARCHIVE_FIELDS rows applicable to a session id."""
    if session_id_int is None:
        # Session id unparseable — defensively check every field. The check
        # itself will hard-fail if the session lacks any of them.
        return list(REQUIRED_ARCHIVE_FIELDS)
    out: list[dict[str, Any]] = []
    for row in REQUIRED_ARCHIVE_FIELDS:
        since = parse_session_id(row.get("since_session"))
        if since is not None and session_id_int >= since:
            out.append(row)
    return out


def session_commit_count(repo: Path) -> int | None:
    """Best-effort count of commits since the eager-claim.

    Returns None if no eager-claim is found in the recent history.
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


def audit_one(
    data: dict[str, Any], source_label: str, repo: Path | None
) -> tuple[int, list[str]]:
    """Audit a single session payload. Returns (exit_code, advisory_lines).

    Hard-fail messages are printed to stderr inside this function.
    Advisory lines are returned for the caller to print (stderr) — they
    do not affect the exit code.
    """
    session_id_str = data.get("id") if isinstance(data.get("id"), str) else None
    session_id_int = parse_session_id(session_id_str)
    fields = applicable_fields(session_id_int)
    advisories: list[str] = []
    failures: list[str] = []

    for row in fields:
        field = row["field"]
        expected = row["shape"]
        adr = row.get("adr", "(unknown ADR)")
        since = row.get("since_session", "(unknown vintage)")

        if field not in data:
            failures.append(
                f"{source_label} is missing the '{field}' key "
                f"(required since {since} per {adr})."
            )
            continue

        err = shape_check(data[field], expected)
        if err is not None:
            failures.append(
                f"{source_label} has '{field}' with bad shape: {err} "
                f"(required since {since} per {adr})."
            )
            continue

        # Optional value-vocabulary check (S-0157 / Issue #121). A field
        # carrying an `allowed_values` list hard-fails on any value outside
        # the set — same severity as a shape mismatch. Used by `mode` to
        # pin the canonical {interactive, routine} vocabulary.
        allowed = row.get("allowed_values")
        if allowed is not None and data[field] not in allowed:
            failures.append(
                f"{source_label} has '{field}' = {data[field]!r}, not in the "
                f"allowed value set {allowed} (required since {since} per {adr})."
            )
            continue

        # Optional secondary check, scoped to outcome_summary_soft_warns.
        if (
            field == "outcome_summary_soft_warns"
            and data[field] == {}
            and repo is not None
        ):
            commit_count = session_commit_count(repo)
            if commit_count is not None and commit_count >= EMPTY_DICT_COMMIT_THRESHOLD:
                advisories.append(
                    f"advisory: '{field}' is empty but session has "
                    f"{commit_count} commits since eager-claim. If "
                    f"validate.py emitted soft-warns during the session, the "
                    f"field may have been written empty-by-default. Confirm."
                )

    if failures:
        for msg in failures:
            print(
                f"[audit-archive-structured-fields] HARD-FAIL: {msg}",
                file=sys.stderr,
            )
        print("", file=sys.stderr)
        print(
            "Per the relevant ADR, every session archive must carry the "
            "named structured field with the expected shape. See "
            "engine/operations/session-shutdown-sequence.md and "
            "engine/tools/audit_archive_structured_fields.py "
            "REQUIRED_ARCHIVE_FIELDS for the field-set declaration.",
            file=sys.stderr,
        )
        return 2, advisories

    return 0, advisories


def archive_history_report(archive_dir: Path) -> str:
    """Walk archives, return a Markdown report of structured-field gaps."""
    if not archive_dir.is_dir():
        return f"# Archive-history report\n\n_no archive directory at {archive_dir}_\n"

    lines: list[str] = [
        "# Archive-history audit — structured-field gaps",
        "",
        "Per Issue #20 (S-0065 origin; S-0078 mechanization). Walks every "
        "`engine/session/archive/S-*.json` and reports any archive whose "
        "session id is `>=` a required field's `since_session` but which "
        "lacks the field, carries it with the wrong shape, or carries a "
        "value outside the field's `allowed_values` set.",
        "",
        "Informational only. Historical archives are not modified.",
        "",
        "## Findings",
        "",
    ]

    findings_count = 0
    archives = sorted(archive_dir.glob("S-*.json"))
    for archive in archives:
        try:
            payload = json.loads(archive.read_text())
        except (json.JSONDecodeError, OSError):
            lines.append(f"- **{archive.name}** — could not read or parse.")
            findings_count += 1
            continue

        session_id_int = parse_session_id(
            payload.get("id") if isinstance(payload.get("id"), str) else archive.stem
        )
        if session_id_int is None:
            session_id_int = parse_session_id(archive.stem)

        for row in applicable_fields(session_id_int):
            field = row["field"]
            expected = row["shape"]
            since = row.get("since_session", "?")
            adr = row.get("adr", "?")
            if field not in payload:
                lines.append(
                    f"- **{archive.name}** missing `{field}` "
                    f"(required since {since} per {adr})."
                )
                findings_count += 1
                continue
            err = shape_check(payload[field], expected)
            if err is not None:
                lines.append(
                    f"- **{archive.name}** has `{field}` with bad shape "
                    f"({err}) (required since {since} per {adr})."
                )
                findings_count += 1
                continue
            allowed = row.get("allowed_values")
            if allowed is not None and payload[field] not in allowed:
                lines.append(
                    f"- **{archive.name}** has `{field}` = "
                    f"`{payload[field]!r}`, not in the allowed value set "
                    f"{allowed} (required since {since} per {adr})."
                )
                findings_count += 1

    if findings_count == 0:
        lines.append(
            "_no findings — every applicable archive carries every "
            "required field with the expected shape._"
        )
    else:
        lines.insert(
            len(lines),
            f"\n**Total findings: {findings_count}** across {len(archives)} archives.",
        )

    lines.append("")
    lines.append("## Field set audited")
    lines.append("")
    for row in REQUIRED_ARCHIVE_FIELDS:
        allowed = row.get("allowed_values")
        allowed_note = f"; allowed values {allowed}" if allowed is not None else ""
        lines.append(
            f"- `{row['field']}` — required since {row['since_session']} "
            f"({row['shape']}){allowed_note}; per {row['adr']}."
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry. Returns 0 on clean, 2 on hard-fail."""
    parser = argparse.ArgumentParser(
        description=(
            "Audit structured archive fields. Defaults to the in-flight "
            "engine/session/current.json. --archive-history walks every "
            "archive and emits a Markdown report (informational; closes "
            "Issue #20)."
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
        help="Repo root for git invocations.",
    )
    parser.add_argument(
        "--archive-history",
        action="store_true",
        help=(
            "Walk every engine/session/archive/S-*.json, emit Markdown "
            "report to stdout, exit 0. Informational mode for Issue #20."
        ),
    )
    args = parser.parse_args(argv)

    if args.archive_history:
        archive_dir = args.repo_root / "engine" / "session" / "archive"
        print(archive_history_report(archive_dir))
        return 0

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
            data = json.loads(current_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(
                f"[audit-archive-structured-fields] {current_path} is not valid "
                f"JSON: {exc}",
                file=sys.stderr,
            )
            return 2

    rc, advisories = audit_one(data, source_label, repo)
    for advisory in advisories:
        print(f"[audit-archive-structured-fields] {advisory}", file=sys.stderr)

    if rc == 0:
        n_fields = len(applicable_fields(parse_session_id(data.get("id"))))
        print(
            f"[audit-archive-structured-fields] PASS: {n_fields} "
            f"required field{'s' if n_fields != 1 else ''} present "
            f"with expected shape{'s' if n_fields != 1 else ''}."
        )

    return rc


if __name__ == "__main__":
    sys.exit(main())
