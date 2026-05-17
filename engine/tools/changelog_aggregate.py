"""Per-session changelog aggregator (Engine reference Session-4 full impl, Paideia port).

Synthesizes Keep-a-Changelog ``[Unreleased]`` views on demand from per-session
changelog entries at ``engine/changelog/<YYYY>/<S-NNNN>-<slug>.md``.

Replaces the monolithic ``engine/ENGINE_LOG.md`` aggregation surface per ADR 0092.
The structured per-session archives at ``engine/session/archive/S-NNNN.json``
carry the canonical session record; this aggregator produces the
chronological / categorical narrative view that the historical ENGINE_LOG's
``[Unreleased]`` section provided.

What it does
------------
1. Walks ``engine/changelog/<YYYY>/`` for ``S-*.md`` entries (skips ``_*``
   directory prefixes including ``_history/``).
2. Parses each entry's YAML frontmatter (hand-rolled simple parser — no PyYAML
   dep) + body lines.
3. Validates each entry against ``engine/schemas/changelog-entry.schema.json``
   via ``jsonschema.Draft202012Validator``.
4. Optionally filters by ``--since <git-tag>`` (entries with ``closed_at`` >
   tag committer-date via ``git log -1 --format=%cI <tag>``) and/or
   ``--module <name>`` (frontmatter ``module`` exact match).
5. Groups remaining entries by ``material_change_class``.
6. Emits Keep-a-Changelog markdown (default) or JSON.

CLI
---
- ``--since <git-tag>``  — filter to entries closed after tag committer-date.
- ``--module <name>``    — filter to entries with matching module.
- ``--format markdown``  — default; Keep-a-Changelog ``[Unreleased]`` markdown.
- ``--format json``      — JSON object: ``{"unreleased_since": <tag|null>, "entries": [...]}``.
- ``--validate-only``    — schema-validate all entries, report violations, no output.
- ``--changelog-root P`` — override changelog root (tests).
- ``--schema-path P``    — override schema path (tests).

Exit codes
----------
- 0  — success (or no entries, or validate-only-clean).
- 2  — verification refused (schema violation in --validate-only mode).
- 3  — generic error (git tag missing, IO failure, malformed frontmatter).

Cross-references
----------------
- ADR 0092 — substrate decision; this aggregator is the Engine reference's
  planned Session-4-scope full implementation.
- engine/changelog/README.md — directory layout + discipline.
- engine/schemas/changelog-entry.schema.json — frontmatter contract.
- engine/tools/timestamps.py — canonical timestamp parsing (ADR 0058).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone  # noqa: F401 — datetime used by mypy via type annotations
from pathlib import Path
from typing import Any

import jsonschema  # type: ignore[import-untyped]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timestamps import parse as parse_timestamp  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHANGELOG_ROOT = REPO_ROOT / "engine" / "changelog"
DEFAULT_SCHEMA_PATH = REPO_ROOT / "engine" / "schemas" / "changelog-entry.schema.json"

FRONTMATTER_DELIMITER = "---"
SESSION_ID_PATTERN = re.compile(r"^S-(\d{4})$")
FILENAME_PATTERN = re.compile(r"^(S-\d{4})-(.+)\.md$")

# Material-change classes from the schema; order is the rendering order
# in markdown output (mirrors Keep-a-Changelog Added/Changed/Removed ordering
# preference — schema-content classes first, infrastructure last).
CLASS_RENDER_ORDER = [
    "adr",
    "policy",
    "check",
    "audit",
    "operation",
    "tool",
    "skill",
    "module",
    "schema",
    "infrastructure",
    "docs",
    "mixed",
]

CLASS_HEADINGS = {
    "adr": "ADRs",
    "policy": "Policies",
    "check": "Checks",
    "audit": "Audits",
    "operation": "Operations",
    "tool": "Tools",
    "skill": "Skills",
    "module": "Modules",
    "schema": "Schemas",
    "infrastructure": "Infrastructure",
    "docs": "Docs",
    "mixed": "Mixed",
}


def _err(msg: str) -> None:
    print(f"[changelog-aggregate] {msg}", file=sys.stderr)


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """Split a markdown file's YAML frontmatter from its body.

    Returns ``(frontmatter_dict, body_lines)``. The frontmatter parser is
    minimal — only handles ``key: value`` pairs on single lines, with optional
    quoted values. Sufficient for the changelog-entry schema, which has no
    nested structures.

    Raises ``ValueError`` if the frontmatter delimiter is missing or malformed.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        raise ValueError("missing opening --- delimiter")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == FRONTMATTER_DELIMITER:
            end = i
            break
    if end is None:
        raise ValueError("missing closing --- delimiter")
    fm: dict[str, str] = {}
    for raw in lines[1:end]:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"frontmatter line lacks colon: {raw!r}")
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        fm[key] = value
    body = lines[end + 1 :]
    return fm, body


def parse_entry(path: Path) -> dict[str, Any]:
    """Parse a per-session changelog entry file.

    Returns ``{"path": Path, "frontmatter": dict, "body_lines": list[str],
    "body_text": str, "line_count": int}``. Schema validation is the caller's
    responsibility (separate concern from parsing).
    """
    text = path.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    fm, body_lines = parse_frontmatter(text)
    return {
        "path": path,
        "frontmatter": fm,
        "body_lines": body_lines,
        "body_text": "\n".join(body_lines).strip(),
        "line_count": line_count,
    }


def list_entries(changelog_root: Path) -> list[Path]:
    """Walk ``<YYYY>/`` subdirectories for ``S-*.md`` entries.

    Skips any directory whose name starts with ``_`` (including ``_history``).
    Sorts entries by ``(year_dir_name, filename)`` for stable output.
    """
    entries: list[Path] = []
    if not changelog_root.is_dir():
        return entries
    for year_dir in sorted(changelog_root.iterdir()):
        if not year_dir.is_dir() or year_dir.name.startswith("_"):
            continue
        for entry in sorted(year_dir.glob("S-*.md")):
            if entry.is_file():
                entries.append(entry)
    return entries


def tag_committer_date(tag: str) -> datetime:
    """Resolve a git tag to its committer-date UTC.

    Raises ``RuntimeError`` if the tag is missing or git fails.
    """
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", tag],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git tag '{tag}' not found: {result.stderr.strip()}")
    iso = result.stdout.strip()
    if not iso:
        raise RuntimeError(f"git tag '{tag}' resolves to empty timestamp")
    # git's %cI output is already ISO-8601 with offset; route through the
    # canonical parser per ADR 0058 (timestamps.parse normalises Z and
    # naive-datetime cases). The `Z`-vs-`+00:00` shapes both round-trip.
    return parse_timestamp(iso).astimezone(timezone.utc)


def parse_closed_at(value: str) -> datetime:
    """Parse the entry's ``closed_at`` ISO 8601 string into a UTC datetime."""
    try:
        return parse_timestamp(value).astimezone(timezone.utc)
    except Exception as exc:  # noqa: BLE001 — re-raise with context
        raise ValueError(f"invalid closed_at {value!r}: {exc}") from exc


def filter_entries(
    parsed: list[dict[str, Any]],
    since: datetime | None,
    module: str | None,
) -> list[dict[str, Any]]:
    """Apply --since and --module filters."""
    out = []
    for entry in parsed:
        fm = entry["frontmatter"]
        if module is not None and fm.get("module") != module:
            continue
        if since is not None:
            closed_at = parse_closed_at(fm["closed_at"])
            if closed_at <= since:
                continue
        out.append(entry)
    return out


def group_by_class(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group entries by ``material_change_class``. Unknown classes bucket under ``mixed``."""
    groups: dict[str, list[dict[str, Any]]] = {cls: [] for cls in CLASS_RENDER_ORDER}
    for entry in entries:
        cls = entry["frontmatter"].get("material_change_class", "mixed")
        if cls not in groups:
            cls = "mixed"
        groups[cls].append(entry)
    return groups


def emit_markdown(groups: dict[str, list[dict[str, Any]]], since: str | None) -> str:
    """Render Keep-a-Changelog markdown."""
    header = (
        f"# Changelog [Unreleased since {since}]"
        if since
        else "# Changelog [Unreleased]"
    )
    total = sum(len(es) for es in groups.values())
    if total == 0:
        return f"{header}\n\n_no entries_\n"
    out = [header, ""]
    for cls in CLASS_RENDER_ORDER:
        bucket = groups.get(cls, [])
        if not bucket:
            continue
        out.append(f"## {CLASS_HEADINGS[cls]}")
        out.append("")
        for entry in bucket:
            fm = entry["frontmatter"]
            sid = fm.get("session_id", "?")
            module = fm.get("module", "?")
            summary = fm.get("summary", "(no summary)")
            out.append(f"- **{sid}** _({module})_ — {summary}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def emit_json(groups: dict[str, list[dict[str, Any]]], since: str | None) -> str:
    """Render JSON."""
    payload: dict[str, Any] = {"unreleased_since": since, "entries": []}
    for cls in CLASS_RENDER_ORDER:
        for entry in groups.get(cls, []):
            try:
                rel_path = str(entry["path"].relative_to(REPO_ROOT))
            except ValueError:
                rel_path = str(entry["path"])
            payload["entries"].append(
                {
                    "session_id": entry["frontmatter"].get("session_id"),
                    "session_type": entry["frontmatter"].get("session_type"),
                    "closed_at": entry["frontmatter"].get("closed_at"),
                    "material_change_class": entry["frontmatter"].get(
                        "material_change_class"
                    ),
                    "module": entry["frontmatter"].get("module"),
                    "summary": entry["frontmatter"].get("summary"),
                    "path": rel_path,
                    "line_count": entry["line_count"],
                }
            )
    return json.dumps(payload, indent=2, sort_keys=False)


def validate_all(
    entries: list[dict[str, Any]],
    schema: dict[str, Any],
) -> list[tuple[Path, str]]:
    """Return a list of (path, error_message) for each schema violation."""
    validator = jsonschema.Draft202012Validator(schema)
    violations: list[tuple[Path, str]] = []
    for entry in entries:
        for err in validator.iter_errors(entry["frontmatter"]):
            violations.append((entry["path"], err.message))
        m = FILENAME_PATTERN.match(entry["path"].name)
        if m:
            fid = m.group(1)
            sid = entry["frontmatter"].get("session_id")
            if sid is not None and sid != fid:
                violations.append(
                    (
                        entry["path"],
                        f"filename session_id {fid} != frontmatter session_id {sid}",
                    )
                )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggregate per-session changelog entries."
    )
    parser.add_argument(
        "--since", help="Git tag; filter to entries closed after tag committer-date."
    )
    parser.add_argument(
        "--module", help="Filter to entries with matching frontmatter module."
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Schema-validate all entries; report violations to stderr; no output.",
    )
    parser.add_argument(
        "--changelog-root",
        type=Path,
        default=DEFAULT_CHANGELOG_ROOT,
        help="Override changelog root (tests).",
    )
    parser.add_argument(
        "--schema-path",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help="Override schema path (tests).",
    )
    args = parser.parse_args()

    schema_path: Path = args.schema_path
    if not schema_path.is_file():
        _err(f"schema not found at {schema_path}")
        return 3
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _err(f"schema parse failed: {exc}")
        return 3

    paths = list_entries(args.changelog_root)
    parsed: list[dict[str, Any]] = []
    for path in paths:
        try:
            parsed.append(parse_entry(path))
        except (OSError, ValueError) as exc:
            _err(f"parse failed for {path}: {exc}")
            return 3

    violations = validate_all(parsed, schema)
    if args.validate_only:
        if violations:
            for path, msg in violations:
                _err(f"violation in {path}: {msg}")
            return 2
        print(f"validated {len(parsed)} entries; no violations")
        return 0
    if violations:
        for path, msg in violations:
            _err(f"violation in {path}: {msg}")
        return 2

    since_dt: datetime | None = None
    if args.since:
        try:
            since_dt = tag_committer_date(args.since)
        except RuntimeError as exc:
            _err(str(exc))
            return 3

    filtered = filter_entries(parsed, since_dt, args.module)
    groups = group_by_class(filtered)

    if args.format == "json":
        print(emit_json(groups, args.since))
    else:
        print(emit_markdown(groups, args.since))
    return 0


if __name__ == "__main__":
    sys.exit(main())
