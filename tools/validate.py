#!/usr/bin/env python3
"""
Paideia repo-structure validator.

Runs at every commit (via the pre-commit hook) and on demand. Validates the
state-of-record artifacts (top-level files, session counter, ADRs, CHANGELOG,
docs/) for structural integrity.

This script is the seed for what becomes the Phase 4 graph audit utility.
The graph-audit extension point lives in `validate_graph()` below — see ADR
0016 for the full contract that lands when Phase 4 is built.

Behavior summary
----------------
- Repo-structure checks (Phase 0+): always run; defensive against missing
  files (warns + skips checks for files that haven't been authored yet).
- Graph-audit checks (Phase 4+): stub that does nothing today; will gain
  hard-fail and soft-warn checks against the live Supabase DB when fleshed.

Output
------
- Stdout: structured summary lines (one per check category)
- Stderr: soft-warn details
- Exit code: 0 (clean), 1 (soft-warn only), 2 (hard-fail)

Telemetry
---------
Every invocation appends a single line to `tools/validate-history.jsonl`:

    {
      "timestamp": ISO-8601 UTC,
      "session_id": "S-NNNN" or "outside-session",
      "checks_run": [...],
      "hard_fails": int,
      "soft_warns": {category: count, ...},
      "duration_ms": float
    }

Health checks (per ADR 0022) consume this JSONL for trend analysis.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
HISTORY_FILE = REPO_ROOT / "tools" / "validate-history.jsonl"

REQUIRED_TOP_LEVEL = [
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "SECURITY.md",
    "STATE.md",
    "ROADMAP.md",
    "HANDOFF.md",
]

# Files whose existence is expected from S-0002 onward — we soft-skip if
# they don't exist yet during S-0001.
EXPECTED_FROM_S0002 = [
    "CLAUDE.md",
    "docs/MISSION.md",
    "docs/CROSS_REFERENCES.md",
    "docs/operations/README.md",
]

# ADR collection lives here from S-0003 onward.
ADR_DIR = REPO_ROOT / "adr"


# ---------------------------------------------------------------------------
# Result accumulator
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    """Aggregates check outcomes across the run."""

    checks_run: list[str] = field(default_factory=list)
    hard_fails: list[str] = field(default_factory=list)
    soft_warns: dict[str, list[str]] = field(default_factory=dict)

    def add_check(self, name: str) -> None:
        self.checks_run.append(name)

    def hard_fail(self, msg: str) -> None:
        self.hard_fails.append(msg)

    def soft_warn(self, category: str, msg: str) -> None:
        self.soft_warns.setdefault(category, []).append(msg)

    def merge(self, other: ValidationResult) -> None:
        self.checks_run.extend(other.checks_run)
        self.hard_fails.extend(other.hard_fails)
        for cat, msgs in other.soft_warns.items():
            self.soft_warns.setdefault(cat, []).extend(msgs)


# ---------------------------------------------------------------------------
# Repo-structure checks (Phase 0+)
# ---------------------------------------------------------------------------


def validate_repo_structure() -> ValidationResult:
    """Validate top-level files, session/, ADRs, CHANGELOG, STATE, ROADMAP.

    Soft-warns are recoverable; hard-fails require fixing before commit.
    """
    r = ValidationResult()

    # Top-level required files
    r.add_check("top_level_required")
    for name in REQUIRED_TOP_LEVEL:
        if not (REPO_ROOT / name).is_file():
            r.hard_fail(f"missing required top-level file: {name}")

    # session/ scaffolding
    r.add_check("session_register")
    register_path = REPO_ROOT / "session" / "register_state.json"
    if not register_path.is_file():
        r.hard_fail("missing session/register_state.json")
    else:
        try:
            register = json.loads(register_path.read_text())
            for key in ("next_id", "last_claimed", "current_status"):
                if key not in register:
                    r.hard_fail(f"session/register_state.json missing key: {key}")
        except json.JSONDecodeError as e:
            r.hard_fail(f"session/register_state.json is not valid JSON: {e}")

    # current.json schema (only if file exists — may be archived between sessions)
    r.add_check("session_current")
    current_path = REPO_ROOT / "session" / "current.json"
    if current_path.is_file():
        try:
            current = json.loads(current_path.read_text())
            for key in ("id", "started_at", "status", "working_on"):
                if key not in current:
                    r.hard_fail(f"session/current.json missing key: {key}")
            if not re.match(r"^S-\d{4}$", current.get("id", "")):
                r.hard_fail(
                    f"session/current.json id does not match S-NNNN format: "
                    f"{current.get('id')}"
                )
        except json.JSONDecodeError as e:
            r.hard_fail(f"session/current.json is not valid JSON: {e}")

    # CHANGELOG.md parseable as Keep-a-Changelog (lightweight check: has
    # [Unreleased] section)
    r.add_check("changelog_format")
    changelog_path = REPO_ROOT / "CHANGELOG.md"
    if changelog_path.is_file():
        text = changelog_path.read_text()
        if "[Unreleased]" not in text and "## [Unreleased]" not in text:
            r.soft_warn(
                "changelog_format",
                "CHANGELOG.md missing [Unreleased] section header",
            )

    # STATE.md current-phase pointer
    r.add_check("state_current_phase")
    state_path = REPO_ROOT / "STATE.md"
    if state_path.is_file():
        text = state_path.read_text()
        if "Current phase" not in text:
            r.soft_warn(
                "state_format",
                "STATE.md missing 'Current phase' field",
            )

    # ADR Status fields (only when adr/ exists — S-0003 onward)
    r.add_check("adr_status")
    if ADR_DIR.is_dir():
        for adr_file in sorted(ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md")):
            text = adr_file.read_text()
            # Look for "Status:" line
            if not re.search(r"^[*-]?\s*Status:\s*\S", text, re.MULTILINE):
                r.soft_warn(
                    "adr_missing_status",
                    f"{adr_file.relative_to(REPO_ROOT)}: no Status field found",
                )

    # docs/CROSS_REFERENCES.md entries resolve (S-0002 onward)
    r.add_check("cross_references_resolve")
    cross_ref_path = REPO_ROOT / "docs" / "CROSS_REFERENCES.md"
    if cross_ref_path.is_file():
        text = cross_ref_path.read_text()
        # Find [link](path) targets, verify they exist
        for match in re.finditer(r"\]\(([^)]+\.md)\)", text):
            target = match.group(1)
            # Skip URLs and anchors-only
            if target.startswith(("http://", "https://", "#")):
                continue
            target_path = REPO_ROOT / target
            if not target_path.is_file():
                r.soft_warn(
                    "cross_reference_broken",
                    f"docs/CROSS_REFERENCES.md → {target} does not exist",
                )

    # Files expected from S-0002 (soft-skip during S-0001)
    r.add_check("future_files_present")
    for name in EXPECTED_FROM_S0002:
        if not (REPO_ROOT / name).is_file():
            r.soft_warn(
                "expected_future_file_missing",
                f"{name} not yet authored (will land in S-0002 or later)",
            )

    return r


# ---------------------------------------------------------------------------
# Graph audit extension point (Phase 4+)
# ---------------------------------------------------------------------------


def validate_graph(connection_string: str | None = None) -> ValidationResult:
    """Validate the live Supabase graph against ADR 0016's contract.

    **STUB — Phase 4 implementation pending.**

    See [adr/0016-graph-construction-needs-live-validation.md]. When fleshed,
    this function MUST connect to the live Supabase DB via psycopg, run the
    following checks against the post-`db push` state, and return a
    ValidationResult with categorized soft-warns and hard-fails.

    Hard-fails (exit 2):
      * Duplicate node IDs.
      * Dangling edge references (source_id or target_id not in nodes).
      * Cycles in the prerequisite-edge subgraph (detect via SCC/Kosaraju).

    Soft-warns by category (printed to stderr, counted, logged to JSONL):
      * undeclared_predicate          — edge.type not in PREDICATE_MANIFEST.md
      * attribute_shape_inconsistency — same-domain nodes with materially
                                        different attribute coverage
      * missing_rigor_score           — rigor_score_computed null when
                                        topology data is sufficient
      * render_readiness_violation    — labels containing scaffolding tokens
                                        ("service_node", "synthetic", "stub")
      * synthetic_review_queue        — confidence_level=SYNTHETIC nodes
                                        flagged for review
      * orphan_leaf                   — zero inbound + zero outbound
                                        prerequisite edges
      * suspicious_cross_domain_ratio — subdomain with > 40% cross-domain
                                        inbound edges (likely missing service
                                        node)

    Runtime budget: <3s on 100-node test seed.

    Modes (added when fleshed):
      * `--validate-only` (default): read-only; categorical counts; exit 0/1/2
      * `--export-snapshot path/to/snapshot.json`: dump current state for
        offline review

    No write-back path. DB writes happen via Supabase migrations only.
    """
    r = ValidationResult()
    r.add_check("graph_audit_stub")
    # Stub: nothing to do until Phase 4. Existence of this function and
    # docstring is the load-bearing anchor that ADR 0016's lesson lands.
    return r


# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------


def session_id_from_current() -> str:
    """Return the in-progress session id, or 'outside-session' if none."""
    current_path = REPO_ROOT / "session" / "current.json"
    if not current_path.is_file():
        return "outside-session"
    try:
        current = json.loads(current_path.read_text())
        return str(current.get("id", "outside-session"))
    except json.JSONDecodeError:
        return "outside-session"


def append_history(record: dict[str, Any]) -> None:
    """Append a JSONL telemetry record. Best-effort; never fails the run."""
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with HISTORY_FILE.open("a") as f:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    start = time.monotonic()
    overall = ValidationResult()
    overall.merge(validate_repo_structure())
    overall.merge(validate_graph())
    duration_ms = (time.monotonic() - start) * 1000

    # Print summary to stdout
    print(f"[validate] checks run: {len(overall.checks_run)}")
    print(f"[validate] hard fails: {len(overall.hard_fails)}")
    soft_total = sum(len(v) for v in overall.soft_warns.values())
    print(f"[validate] soft warns: {soft_total}")
    if overall.soft_warns:
        for cat, msgs in overall.soft_warns.items():
            print(f"  {cat}: {len(msgs)}")

    # Print details to stderr
    for fail in overall.hard_fails:
        print(f"[hard-fail] {fail}", file=sys.stderr)
    for cat, msgs in overall.soft_warns.items():
        for msg in msgs:
            print(f"[soft-warn:{cat}] {msg}", file=sys.stderr)

    # Telemetry
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id_from_current(),
        "checks_run": overall.checks_run,
        "hard_fails": len(overall.hard_fails),
        "soft_warns": {k: len(v) for k, v in overall.soft_warns.items()},
        "duration_ms": round(duration_ms, 2),
    }
    append_history(record)

    if overall.hard_fails:
        return 2
    if soft_total > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
