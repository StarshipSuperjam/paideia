"""Parse the Persistent-warn annotation section of tools-validate-interpretation.md.

Layer 1 contract: Issue #133 / S-0196 (annotated-baselines bucket for the
boot persistent-warn surface per ADR 0042).

Purpose
-------
The boot persistent-warn surface in ``engine/tools/hooks/session-start.sh``
splits ``>=3/5`` firings into two output lanes: action-needed (categories
without a documented expected-firing annotation) and annotated-baselines
(categories whose persistence is explicitly expected per the annotation
section of ``engine/operations/tools-validate-interpretation.md``).

The hook calls this script once at boot to obtain the canonical list of
annotated category names — one per line on stdout. The annotation
section's markdown is the single source of truth; this parser is the
small adapter the shell-level hook needs to read it.

Section shape
-------------
The annotated categories live under the ``## Persistent-warn annotation``
H2 header in ``engine/operations/tools-validate-interpretation.md``. Each
entry is an H3 of the form ``### `<category_name>` (annotated S-NNNN)``.
The parser walks lines from the H2 marker forward, capturing every H3
``### `<name>``` until the next ``## `` header (which terminates the
section).

Categories from sibling sections (``## Actively-tracked, deferred re-audit``,
``## Informational-only-accepted``, etc.) are NOT captured — only the
explicit Persistent-warn annotation section drives boot-surface
suppression. Categories that should suppress migrate INTO this section.

Exit codes
----------
- ``0`` — section parsed successfully; categories printed (possibly zero).
- ``2`` — ops-doc file absent OR the ``## Persistent-warn annotation``
  H2 header is missing. Caller falls back to empty list (all categories
  surface as action-needed — preserves visibility on parser break).

CLI
---
- ``scan_persistent_warn_annotations.py`` — default; auto-resolves
  ``engine/operations/tools-validate-interpretation.md`` from this file.
- ``scan_persistent_warn_annotations.py --ops-doc PATH`` — override the
  source path (used by pytests for fixture-driven testing).

Out of scope
------------
- No write side. This script is read-only; no edits to the markdown.
- No semantic validation. A category present in the section is treated
  as annotated regardless of the annotation body's content. The
  per-entry quality of the annotation prose is a human-review concern.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OPS_DOC = (
    REPO_ROOT / "engine" / "operations" / "tools-validate-interpretation.md"
)

_SECTION_HEADER = "## Persistent-warn annotation"
_H2_PATTERN = re.compile(r"^##\s")
_CATEGORY_PATTERN = re.compile(r"^###\s+`([a-z][a-z0-9_]*)`")


def extract_annotated_categories(ops_doc_text: str) -> list[str]:
    """Walk ops_doc_text, return ordered list of annotated category names.

    Raises ValueError if the Persistent-warn annotation H2 header is
    missing — the caller distinguishes "section missing" from "section
    present but empty" (the latter returns []).
    """
    lines = ops_doc_text.splitlines()
    in_section = False
    categories: list[str] = []

    for line in lines:
        if line.rstrip() == _SECTION_HEADER:
            in_section = True
            continue
        if not in_section:
            continue
        # Any subsequent H2 header terminates the section.
        if _H2_PATTERN.match(line):
            break
        m = _CATEGORY_PATTERN.match(line)
        if m:
            categories.append(m.group(1))

    if not in_section:
        raise ValueError(f"section header {_SECTION_HEADER!r} not found in ops doc")

    return categories


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--ops-doc",
        type=Path,
        default=DEFAULT_OPS_DOC,
        help="Path to tools-validate-interpretation.md (default: auto-resolved)",
    )
    args = parser.parse_args(argv)

    if not args.ops_doc.exists():
        print(
            f"[scan_persistent_warn_annotations] ops doc not found: {args.ops_doc}",
            file=sys.stderr,
        )
        return 2

    text = args.ops_doc.read_text(encoding="utf-8")
    try:
        categories = extract_annotated_categories(text)
    except ValueError as exc:
        print(f"[scan_persistent_warn_annotations] {exc}", file=sys.stderr)
        return 2

    for cat in categories:
        print(cat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
