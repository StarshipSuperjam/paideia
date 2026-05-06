"""One-shot rename: diary_skipped → mempalace_diary_write_skipped.

Per ADR 0056 (S-0078) and the user-confirmed "rename" decision in the plan
at /Users/shanekidd/.claude/plans/use-of-mempalace-by-velvety-pebble.md.

Background
----------
The pre-S-0078 contract carried a manually-recorded ``diary_skipped`` count
in ``outcome_summary_soft_warns``. The S-0078 mechanization replaces that
manual record with the ``mempalace_diary_write_skipped`` category emitted
by ``validate.py --final-check`` based on telemetry from
``engine/session/current_mempalace.jsonl``. To keep the persistent-warn
3-of-5 surface continuous across the rename, this script walks every
existing ``engine/session/archive/S-*.json`` file and renames the key.

Behavior
--------
For each archive in ``engine/session/archive/``:

1. Load JSON.
2. If ``outcome_summary_soft_warns.diary_skipped`` exists:
   - Add the value to ``outcome_summary_soft_warns.mempalace_diary_write_skipped``
     (creating the new key if absent; summing if both happen to exist).
   - Delete the ``diary_skipped`` key.
   - Write the file back atomically (write to ``.tmp``, then rename).
3. Print one line per archive touched: ``[migrate] S-NNNN.json diary_skipped=N``.

Idempotency
-----------
Re-running on an already-migrated tree is a no-op (no archives carry
``diary_skipped``). Safe to invoke multiple times.

CLI
---
- ``migrate_diary_skipped_archive_field.py`` — runs against
  ``engine/session/archive/`` under the script's repo root.
- ``--archive-dir PATH`` — override the directory (used by tests).
- ``--dry-run`` — report what WOULD change; do not write.

Exit code
---------
- ``0`` — migration complete (or dry-run report emitted).
- The non-zero path is reserved.

Out of scope
------------
- No re-counting from raw telemetry. The migration is mechanical: rename
  the key, preserve the count.
- No deletion of zero-valued ``diary_skipped`` keys outside of merging
  them into the new key (the ADR 0042 contract treats absence and zero
  as equivalent).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARCHIVE_DIR = REPO_ROOT / "engine" / "session" / "archive"
OLD_KEY = "diary_skipped"
NEW_KEY = "mempalace_diary_write_skipped"

# Surgical line-pattern for the diary_skipped entry inside
# outcome_summary_soft_warns. Matches the leading whitespace, the key, the
# integer value, and an optional trailing comma + newline. Preserving the
# rest of the file's formatting matters because existing archives use
# inconsistent JSON serialization (some lines compact, some indented), and
# json.dumps would normalize all of it — generating churn in the diff that
# obscures the actual rename.
DIARY_LINE_RE = re.compile(
    r'(?P<indent>[ \t]*)"diary_skipped"\s*:\s*(?P<value>-?\d+)(?P<trail>,?)\n'
)


def parse_value_from_match(m: "re.Match[str]") -> int:
    try:
        return int(m.group("value"))
    except (TypeError, ValueError):
        return 0


def migrate_one(path: Path, dry_run: bool) -> tuple[bool, int]:
    """Migrate one archive file. Returns (touched, old_value).

    Strategy: surgical text replacement preserving original formatting.
    Use json.loads only for validation — never write json.dumps back, which
    would normalize and re-escape Unicode (em dashes, arrows, ≥, etc.).

    Three behaviors based on value:

    - Value == 0: remove the entire ``diary_skipped`` line. Per ADR 0042,
      a zero count is equivalent to absence — no information lost.
    - Value > 0: rename in place to ``mempalace_diary_write_skipped`` with
      the same value, preserving indentation and trailing-comma shape.
    - Field not in outcome_summary_soft_warns: no-op.
    """
    try:
        text = path.read_text(encoding="utf-8")
        # Validate JSON parses; bail on malformed files rather than mangle.
        data: dict[str, Any] = json.loads(text)
    except (OSError, json.JSONDecodeError):
        return False, 0

    soft_warns = data.get("outcome_summary_soft_warns")
    if not isinstance(soft_warns, dict):
        return False, 0
    if OLD_KEY not in soft_warns:
        return False, 0

    raw_value = soft_warns[OLD_KEY]
    try:
        old_value = int(raw_value) if not isinstance(raw_value, bool) else 0
    except (TypeError, ValueError):
        old_value = 0

    match = DIARY_LINE_RE.search(text)
    if match is None:
        # Field is in JSON but pattern didn't match (edge: same-line dict
        # with no newline, exotic whitespace). Bail rather than mangle.
        return False, old_value

    if old_value <= 0:
        # Remove the line entirely. If diary_skipped was the LAST key in
        # its dict (no trailing comma on the matched line), removing only
        # this line leaves the previous line's trailing comma dangling —
        # invalid JSON. Detect via has-trailing-comma; if absent, also
        # strip the preceding line's trailing comma.
        if match.group("trail"):
            new_text = text[: match.start()] + text[match.end() :]
        else:
            # Last-key case: walk back from match.start() and strip the
            # ", " or "," before the preceding newline.
            preceding = text[: match.start()]
            stripped = re.sub(r",(\s*)$", r"\1", preceding)
            new_text = stripped + text[match.end() :]
    else:
        # Rename in place; preserve indent + trailing comma.
        replacement = (
            f'{match.group("indent")}"{NEW_KEY}": {old_value}{match.group("trail")}\n'
        )
        new_text = text[: match.start()] + replacement + text[match.end() :]

    # Validate the result still parses (defense against pattern mishap).
    try:
        json.loads(new_text)
    except json.JSONDecodeError:
        return False, old_value

    if dry_run:
        return True, old_value

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(new_text, encoding="utf-8")
    tmp_path.replace(path)

    return True, old_value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "One-shot migration: rename outcome_summary_soft_warns."
            f"{OLD_KEY} → {NEW_KEY} across every archive. Per ADR 0056 "
            "(S-0078)."
        ),
    )
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=DEFAULT_ARCHIVE_DIR,
        help="Archive directory to walk (default: engine/session/archive/).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what WOULD change; do not write.",
    )
    args = parser.parse_args(argv)

    archive_dir: Path = args.archive_dir
    if not archive_dir.is_dir():
        print(
            f"[migrate-diary-skipped] {archive_dir} is not a directory; "
            "nothing to migrate.",
            file=sys.stderr,
        )
        return 0

    archives = sorted(archive_dir.glob("S-*.json"))
    touched_count = 0
    total_renamed = 0

    for archive in archives:
        touched, old_value = migrate_one(archive, args.dry_run)
        if touched:
            touched_count += 1
            total_renamed += old_value
            verb = "[dry-run]" if args.dry_run else "[migrate]"
            print(
                f"{verb} {archive.name} {OLD_KEY}={old_value} → {NEW_KEY}",
                flush=True,
            )

    print(
        f"[migrate-diary-skipped] {touched_count}/{len(archives)} archives "
        f"touched; total {OLD_KEY} count migrated: {total_renamed}.",
        flush=True,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
