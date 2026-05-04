#!/usr/bin/env python3
"""Paideia repo-structure validator and code/SQL discipline gate runner.

Module contract — what this file is and is not.

This module is the project's static-structure validator. It runs at every
commit via the pre-commit hook (engine/tools/hooks/pre-commit) and on
demand from the CLI. Three responsibility families live here:

1. Repo-structure checks (Phase 0+, always-on) — verify that the
   state-of-record artifacts (top-level files, session counter JSON,
   ADR Status fields, ADR-vs-index consistency, ENGINE_LOG format,
   STATE.md current-phase pointer, CROSS_REFERENCES.md link resolution,
   files expected from S-0002 onward) match their structural contracts.
   See validate_repo_structure().

2. Code-discipline gates (post-S-0026 per ADR 0038) — invoke ruff,
   mypy --strict, and pytest against staged Python files under engine/.
   See validate_code_gates().

3. SQL-discipline gates (post-S-0027 per ADR 0039 + migration-discipline.md)
   — check transaction wrap, CASCADE presence on learner-state FKs,
   RLS-enable on public.* tables, and CHECK constraint shape on
   enum-modeled TEXT columns against staged SQL files under
   product/seed-graph/migrations/. See validate_sql_gates().

A fourth responsibility (graph audit per ADR 0016) runs against the
live Supabase DB when ``SUPABASE_DB_URL`` is set in the environment;
absence of the env var skips the audit (records ``graph_audit_skipped``)
so non-seed-authoring sessions are not gated on DB connectivity. See
validate_graph().

A fifth responsibility (shared-state health probes per ADR 0045) runs
the chromadb palace and git repo probes — added at S-0035 to catch
silent corruption of cross-session shared state at the moment a
session boots or a commit is attempted, rather than letting it persist
until the next session reads. See validate_shared_state_health().

Invariants this module preserves:

- Read-only with respect to the repo. The validator never modifies tracked
  files. Only writes are to engine/tools/validate-history.jsonl (telemetry,
  appended) and to stdout/stderr (the run's report).
- Deterministic for a given working tree. Two runs against the same tree
  produce the same checks_run list, hard_fails, and soft_warns categories.
  Telemetry rows differ in timestamp and duration_ms only.
- Resilient to absent optional files. Files expected from later sessions
  (e.g., engine/operations/README.md before S-0002) are soft-warned, not
  hard-failed.
- Single-process, single-threaded. ValidationResult accumulates results
  across the run; concurrent access is not supported.

Non-responsibilities:

- No auto-fix. The validator reports; it does not modify state.
- No DB writes. The graph audit reads via psycopg with the service-role
  connection string; writes happen via Supabase migrations only.
- No git or worktree management. The pre-commit hook handles git; this
  module receives staged-file paths and runs gates against them.

Output contract:

- Stdout: structured summary lines, one per check category, plus
  per-category soft-warn counts.
- Stderr: per-failure detail lines tagged [hard-fail] or
  [soft-warn:<category>].
- Exit code: 0 (clean), 1 (soft-warn only), 2 (hard-fail).

Telemetry side effect:

Every invocation appends a single JSON line to
engine/tools/validate-history.jsonl:

    {
      "timestamp": ISO-8601 UTC,
      "session_id": "S-NNNN" or "outside-session",
      "checks_run": [...],
      "hard_fails": int,
      "soft_warns": {category: count, ...},
      "duration_ms": float
    }

Health checks per ADR 0022 consume this JSONL for trend analysis.

CLI invocation:

    python3 engine/tools/validate.py
        Run repo-structure checks plus the graph-audit stub.

    python3 engine/tools/validate.py --code-gates --files <path> [<path> ...]
        Run code-discipline gates (ruff, mypy --strict, pytest) against
        the named files. Gate runs are independent of the structure run;
        each invocation does one thing.

    python3 engine/tools/validate.py --sql-gates --files <path> [<path> ...]
        Run SQL-discipline gates (transaction wrap, CASCADE presence,
        RLS-enable, CHECK constraint shape on enum-modeled columns)
        against the named SQL files. Mutually exclusive with --code-gates.

    python3 engine/tools/validate.py --health-probe-only
        Run only the shared-state health probes (chromadb palace +
        repo config) without the structure or graph checks. Used by
        the SessionStart hook for sub-second boot-time verification.
        Mutually exclusive with the gate flags.

    python3 engine/tools/validate.py --export-snapshot path/to/file.json
        Write a JSON snapshot of the live graph (nodes + edges) to
        the given path and exit. Per ADR 0016 + gate T2-F. Requires
        SUPABASE_DB_URL set; mutually exclusive with the other modes.

Module contracts referenced:

- ADR 0016 — graph-construction live-validation contract; see validate_graph().
- ADR 0022 — periodic health-check telemetry contract; consumes the JSONL.
- ADR 0037 — engine/product partition; informs ENGINE_ADR_DIR / PRODUCT_ADR_DIR.
- ADR 0038 — code-discipline contract; see validate_code_gates().
- ADR 0039 — universal expression contract; the SQL/migrations row's Layer 2
  is implemented by validate_sql_gates().
- ADR 0045 — shared-state integrity discipline; subprocess env scrubbing
  via :mod:`scrub_env`, chromadb palace and git repo probes are wired
  through validate_shared_state_health(); pre-commit subprocesses (ruff,
  mypy, pytest) pass scrubbed envs to prevent the S-0033 GIT_DIR-leak
  vector.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Local helper at engine/tools/scrub_env.py — see ADR 0045.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrub_env import scrubbed_env  # noqa: E402


# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------

# Validator lives at engine/tools/validate.py post-S-0024 migration; REPO_ROOT
# walks three levels up (validate.py → tools/ → engine/ → repo root).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
HISTORY_FILE = REPO_ROOT / "engine" / "tools" / "validate-history.jsonl"

REQUIRED_TOP_LEVEL = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "ROADMAP.md",
    "HANDOFF.md",
    "CLAUDE.md",
]

# Engine-side required files (post-S-0024 migration per ADR 0037).
REQUIRED_ENGINE_FILES = [
    "engine/STATE.md",
    "engine/ENGINE_LOG.md",
]

# Files whose existence is expected from S-0002 onward — we soft-skip if
# they don't exist yet during S-0001. Paths reflect post-S-0024 layout.
EXPECTED_FROM_S0002 = [
    "product/docs/MISSION.md",
    "product/docs/CROSS_REFERENCES.md",
    "engine/operations/README.md",
]

# ADR collection split across engine/adr/ and product/adr/ post-S-0024
# per ADR 0037's partition.
ENGINE_ADR_DIR = REPO_ROOT / "engine" / "adr"
PRODUCT_ADR_DIR = REPO_ROOT / "product" / "adr"

# Shared-state probe scripts (per ADR 0045). Run as subprocesses so a
# native segfault (e.g., chromadb_rust_bindings on a corrupt HNSW
# segment — the S-0034 vector) terminates the probe process at exit
# code 139 rather than crashing the validator. The wrapper treats 139
# as hard-broken.
PROBE_PALACE = REPO_ROOT / "engine" / "tools" / "probe_palace.py"
PROBE_REPO = REPO_ROOT / "engine" / "tools" / "probe_repo.py"

# Issue-collisions scanner (per ADR 0048). Surfaces open GitHub Issues
# whose body or title contains keywords from this session's
# declared_scope or paths from the staged commit. Best-effort — gh
# failure (no auth, no network, repo not on GitHub) is silently skipped.
SCAN_ISSUE_COLLISIONS = REPO_ROOT / "engine" / "tools" / "scan_issue_collisions.py"


# ---------------------------------------------------------------------------
# Result accumulator
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    """Aggregator for check outcomes across a single validate.py invocation.

    Two-tier outcome model is the load-bearing design choice. Hard-fails
    block the pre-commit hook (the runner exits 2); soft-warns are advisory
    (exit 1) and feed health-check telemetry per ADR 0022. Per-function
    validators (validate_repo_structure, validate_code_gates, validate_graph)
    each return their own ValidationResult; main() merges them via merge().

    Fields:
        checks_run: ordered list of check-category names attempted in this run.
            Records coverage regardless of pass/fail; downstream telemetry
            distinguishes "check ran and was clean" from "check did not run".
        hard_fails: list of failure messages. Any non-empty list causes exit 2.
            Messages accumulate so a single run surfaces all blockers rather
            than one-at-a-time.
        soft_warns: dict from stable category string to list of messages.
            Categories are the telemetry aggregation key (e.g.,
            "adr_index_inconsistent", "cross_reference_broken").

    Concurrency: single-process, single-threaded. The dataclass is mutable
    and not safe for concurrent use; each validate.py run owns its instance.

    Non-responsibilities:
        - Does not enforce category-name conventions. Callers pass any string;
          consistency with existing categories is the caller's responsibility
          for telemetry comparability.
        - Does not deduplicate. Repeated add_check/hard_fail/soft_warn calls
          with identical arguments record duplicates.
    """

    checks_run: list[str] = field(default_factory=list)
    hard_fails: list[str] = field(default_factory=list)
    soft_warns: dict[str, list[str]] = field(default_factory=dict)

    def add_check(self, name: str) -> None:
        """Record that a check category named ``name`` was attempted.

        Append-only; duplicates are recorded as duplicates. The pass/fail
        status is conveyed separately via hard_fail/soft_warn.
        """
        self.checks_run.append(name)

    def hard_fail(self, msg: str) -> None:
        """Record a blocking failure with message ``msg``.

        Hard-fails accumulate; the run continues so a single pass surfaces
        all blockers. The runner exits 2 if any hard-fail is recorded.
        """
        self.hard_fails.append(msg)

    def soft_warn(self, category: str, msg: str) -> None:
        """Record an advisory warning under telemetry category ``category``.

        Categories aggregate across runs in the JSONL telemetry log; use
        established names (see existing call sites for the catalog) to
        preserve cross-session comparability. Within a category, messages
        accumulate in encounter order.
        """
        self.soft_warns.setdefault(category, []).append(msg)

    def merge(self, other: ValidationResult) -> None:
        """Merge ``other``'s outcomes into self in-place.

        Concatenates checks_run and hard_fails preserving order; extends
        each soft-warn category list. ``other`` is not mutated. Used by
        main() to combine per-function results into a single overall
        aggregate.
        """
        self.checks_run.extend(other.checks_run)
        self.hard_fails.extend(other.hard_fails)
        for cat, msgs in other.soft_warns.items():
            self.soft_warns.setdefault(cat, []).extend(msgs)


# ---------------------------------------------------------------------------
# Repo-structure checks (Phase 0+)
# ---------------------------------------------------------------------------


def validate_repo_structure() -> ValidationResult:
    """Run the always-on repo-structure check suite; return the result.

    Pure with respect to repo state — reads files, returns a value, performs
    no writes. Telemetry side effects (JSONL append, stdout/stderr) live in
    main(), not here.

    Check categories (in run order):

    - top_level_required, engine_required: existence checks for the project's
      load-bearing root files (README.md, LICENSE, SECURITY.md, ROADMAP.md,
      HANDOFF.md, CLAUDE.md) and engine-required files (engine/STATE.md,
      engine/ENGINE_LOG.md). Hard-fail on missing.
    - session_register, session_current: JSON schema checks on
      engine/session/register_state.json (always present) and
      engine/session/current.json (only between eager-claim and archive).
      Hard-fail on missing required keys, malformed JSON, or non-S-NNNN id.
    - engine_log_format, state_current_phase: lightweight format checks on
      ENGINE_LOG.md (has [Unreleased] section) and STATE.md (has
      "Current phase" field). Soft-warn on absence — these files may be
      mid-edit during a session.
    - adr_status: every ADR file under engine/adr/ and product/adr/ carries
      a Status field (Nygard template). Soft-warn on missing.
    - adr_index_consistency: each subtree's README.md indexes its ADRs and
      the indexed Status keyword matches the file's. Soft-warn on either
      direction of mismatch — the index is human-curated and tolerates
      formatting variation.
    - cross_references_resolve: every relative-path link in
      product/docs/CROSS_REFERENCES.md resolves to a file. Soft-warn on
      broken targets.
    - future_files_present: files expected from S-0002 onward exist.
      Soft-warn during S-0001; hard-fail equivalent does not exist
      (intentional — the validator runs from S-0001's first commit).

    Returns:
        ValidationResult with checks_run populated for every category attempted
        and hard_fails / soft_warns populated as the checks run. Empty result
        means all checks ran and all passed.

    Non-responsibilities:
        - Does not validate ADR cross-link integrity beyond the
          CROSS_REFERENCES.md file itself. ADR-internal links (e.g., ADR
          0036 referencing ADR 0027) are not resolved.
        - Does not enforce ENGINE_LOG entry quality. Only the section
          header presence is checked.
        - Does not connect to any database. Graph-side checks live in
          validate_graph().
    """
    r = ValidationResult()

    # Top-level required files
    r.add_check("top_level_required")
    for name in REQUIRED_TOP_LEVEL:
        if not (REPO_ROOT / name).is_file():
            r.hard_fail(f"missing required top-level file: {name}")

    # Engine-required files (post-S-0024 migration)
    r.add_check("engine_required")
    for name in REQUIRED_ENGINE_FILES:
        if not (REPO_ROOT / name).is_file():
            r.hard_fail(f"missing required engine file: {name}")

    # engine/session/ scaffolding
    r.add_check("session_register")
    register_path = REPO_ROOT / "engine" / "session" / "register_state.json"
    if not register_path.is_file():
        r.hard_fail("missing engine/session/register_state.json")
    else:
        try:
            register = json.loads(register_path.read_text())
            for key in ("next_id", "last_claimed", "current_status"):
                if key not in register:
                    r.hard_fail(
                        f"engine/session/register_state.json missing key: {key}"
                    )
        except json.JSONDecodeError as e:
            r.hard_fail(f"engine/session/register_state.json is not valid JSON: {e}")

    # current.json schema (only if file exists — may be archived between sessions)
    r.add_check("session_current")
    current_path = REPO_ROOT / "engine" / "session" / "current.json"
    if current_path.is_file():
        try:
            current = json.loads(current_path.read_text())
            for key in ("id", "started_at", "status", "working_on"):
                if key not in current:
                    r.hard_fail(f"engine/session/current.json missing key: {key}")
            if not re.match(r"^S-\d{4}$", current.get("id", "")):
                r.hard_fail(
                    f"engine/session/current.json id does not match S-NNNN "
                    f"format: {current.get('id')}"
                )
        except json.JSONDecodeError as e:
            r.hard_fail(f"engine/session/current.json is not valid JSON: {e}")

    # engine/ENGINE_LOG.md parseable as Keep-a-Changelog (lightweight check:
    # has [Unreleased] section). The file is the renamed CHANGELOG.md per ADR
    # 0037 (engine / product wall); it carries the dated narrative for
    # material engine changes. The CHANGELOG.md filename is reserved for
    # future learner-visible product release content (first entry at Phase 9).
    r.add_check("engine_log_format")
    engine_log_path = REPO_ROOT / "engine" / "ENGINE_LOG.md"
    if engine_log_path.is_file():
        text = engine_log_path.read_text()
        if "[Unreleased]" not in text and "## [Unreleased]" not in text:
            r.soft_warn(
                "engine_log_format",
                "engine/ENGINE_LOG.md missing [Unreleased] section header",
            )

    # engine/STATE.md current-phase pointer
    r.add_check("state_current_phase")
    state_path = REPO_ROOT / "engine" / "STATE.md"
    if state_path.is_file():
        text = state_path.read_text()
        if "Current phase" not in text:
            r.soft_warn(
                "state_format",
                "engine/STATE.md missing 'Current phase' field",
            )

    # health_check_overdue (per ADR 0022 Consequences amendment at S-0041).
    # The SessionStart hook surfaces "due" and "overdue" at boot; this
    # validator check is defense-in-depth so a silently-failing hook (the
    # S-0033 / S-0034 vector pattern) cannot mask a slid cadence trigger.
    # Fires when (next_id - last_audit_session) > cadence — strictly past
    # the natural firing slot, which the hook surface already covered.
    # Skips quietly when the optional fields are absent (legacy
    # register_state.json pre-S-0041); the legacy state cannot violate the
    # contract because the field that anchors the contract isn't present.
    r.add_check("health_check_overdue")
    if register_path.is_file():
        try:
            register = json.loads(register_path.read_text())
        except (OSError, json.JSONDecodeError):
            register = None
        if isinstance(register, dict):
            next_id_raw = register.get("next_id")
            last_audit_raw = register.get("last_audit_session")
            cadence_raw = register.get("health_check_cadence", 10)
            if (
                isinstance(next_id_raw, str)
                and isinstance(last_audit_raw, str)
                and isinstance(cadence_raw, int)
                and cadence_raw > 0
                and re.match(r"^\d+$", next_id_raw)
                and re.match(r"^S-\d{4}$", last_audit_raw)
            ):
                next_int = int(next_id_raw)
                audit_int = int(last_audit_raw[2:])
                slots_since = next_int - audit_int
                if slots_since > cadence_raw:
                    overdue_by = slots_since - cadence_raw
                    r.soft_warn(
                        "health_check_overdue",
                        f"next session S-{next_int:04d} is {slots_since} slots "
                        f"since last audit {last_audit_raw}; cadence is "
                        f"{cadence_raw} (overdue by {overdue_by}). Run "
                        f"engine/tools/health_check.py --session "
                        f"S-{next_int:04d} or document explicit deferral in "
                        "outcome_summary.",
                    )

    # ADR Status fields. Iterates both engine/adr/ and product/adr/ post the
    # S-0024 partition. Accepts the Nygard template's bold form (`- **Status:**
    # Accepted`), plain form (`Status: Accepted`), and the bold-around-label
    # variant (`- **Status**: Accepted`). Any of: leading list-bullet/
    # whitespace/asterisks, the literal "Status", optional whitespace/
    # asterisks, a colon, optional whitespace/asterisks, then a non-whitespace
    # value.
    r.add_check("adr_status")
    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if not adr_dir.is_dir():
            continue
        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            text = adr_file.read_text()
            if not re.search(r"^[\s*\-]*Status[\s*]*:[\s*]*\S", text, re.MULTILINE):
                r.soft_warn(
                    "adr_missing_status",
                    f"{adr_file.relative_to(REPO_ROOT)}: no Status field found",
                )

    # ADR index/file consistency. Each subtree (engine/adr/, product/adr/) has
    # its own README.md index; this check runs per-subtree.
    # Soft-warn `adr_index_inconsistent` covers two cases:
    #   - ADR file present but not referenced from its subtree's README.md
    #   - ADR file's Status core keyword differs from the index's status
    #     column for that ADR (Accepted / Superseded / Deprecated / Proposed)
    # Soft-warn rather than hard-fail because the index is human-curated and
    # the formatting tolerates variation (markdown links inside the status
    # column, supersession pointers, etc.); false positives should refine
    # the check rather than be papered over.
    r.add_check("adr_index_consistency")

    # Index rows look like `| [NNNN](NNNN-...md) | Title | Status |`.
    # Match the leading bracketed NNNN as the row anchor and the third
    # cell's contents as the index status. Multiple sections share the
    # same row format, so a single regex covers all per-phase tables.
    row_pattern = re.compile(
        r"^\|\s*\[(\d{4})\]\([^)]+\)\s*\|\s*[^|]+\|\s*([^|]+?)\s*\|"
    )
    file_status_pattern = re.compile(
        r"^[\s*\-]*Status[\s*]*:[\s*]*(.+?)\s*$",
        re.MULTILINE,
    )
    status_keywords = ("superseded", "deprecated", "accepted", "proposed")

    def _core_status(s: str) -> str:
        stripped = re.sub(r"[*_`]", "", s).lower()
        for kw in status_keywords:
            if kw in stripped:
                return kw
        return ""

    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        index_path = adr_dir / "README.md"
        if not (adr_dir.is_dir() and index_path.is_file()):
            continue
        index_rel = index_path.relative_to(REPO_ROOT)
        index_text = index_path.read_text()
        indexed_status: dict[str, str] = {}
        for line in index_text.splitlines():
            m = row_pattern.match(line)
            if m:
                indexed_status[m.group(1)] = m.group(2).strip()

        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            num = adr_file.name[:4]
            rel = adr_file.relative_to(REPO_ROOT)

            if num not in indexed_status:
                r.soft_warn(
                    "adr_index_inconsistent",
                    f"{rel}: ADR not referenced in {index_rel} index",
                )
                continue

            text = adr_file.read_text()
            m = file_status_pattern.search(text)
            if not m:
                # adr_missing_status already covers this case
                continue

            file_core = _core_status(m.group(1))
            index_core = _core_status(indexed_status[num])
            if file_core and index_core and file_core != index_core:
                r.soft_warn(
                    "adr_index_inconsistent",
                    f"{rel}: status keyword mismatch — file '{file_core}', "
                    f"index '{index_core}'",
                )

    # product/docs/CROSS_REFERENCES.md entries resolve (S-0002 onward).
    # Links are resolved relative to the file's directory (standard markdown
    # behavior), then normalized so paths above repo-root flag as broken.
    r.add_check("cross_references_resolve")
    cross_ref_path = REPO_ROOT / "product" / "docs" / "CROSS_REFERENCES.md"
    if cross_ref_path.is_file():
        text = cross_ref_path.read_text()
        link_dir = cross_ref_path.parent
        for match in re.finditer(r"\]\(([^)]+\.md)\)", text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "#")):
                continue
            target_path = (link_dir / target).resolve()
            if not target_path.is_file():
                r.soft_warn(
                    "cross_reference_broken",
                    f"product/docs/CROSS_REFERENCES.md → {target} does not exist",
                )

    # Files expected from S-0002 (soft-skip during S-0001)
    r.add_check("future_files_present")
    for name in EXPECTED_FROM_S0002:
        if not (REPO_ROOT / name).is_file():
            r.soft_warn(
                "expected_future_file_missing",
                f"{name} not yet authored (will land in S-0002 or later)",
            )

    # Cascade-analysis discipline checks per ADR 0041 (S-0029 onward).
    r.merge(validate_superseded_adr_currency())
    r.merge(validate_adr_back_reference_orphan())
    r.merge(validate_adr_consequences_deliverable_audit())

    return r


# ---------------------------------------------------------------------------
# Shared-state health probes (post-S-0035 per ADR 0045)
# ---------------------------------------------------------------------------


def validate_shared_state_health() -> ValidationResult:
    """Run the shared-state health probes; return the result.

    Two probes wrap external scripts so a native segfault (from
    ``chromadb_rust_bindings`` on a corrupt HNSW segment — the S-0034
    vector) terminates the probe process at exit code 139 instead of
    crashing the validator itself. Exit-code interpretation:

    - 0: probe healthy. No record beyond ``add_check``.
    - 1: probe suspect. Recorded as soft-warn under the probe's
      category (``chromadb_palace_health`` or ``repo_config_health``).
      The probe's stderr is the soft-warn body.
    - 2: probe hard-broken. Recorded as hard-fail; validator exits 2.
    - 139 (SIGSEGV): treated as hard-broken. The wrapper records the
      segfault and triggers the same exit-2 path. For chromadb this is
      the S-0034 vector — the rust binding faults on a corrupt segment
      before any Python exception can be raised.

    Probe scripts:

    - ``engine/tools/probe_palace.py`` — opens chromadb
      ``PersistentClient`` at ``~/.mempalace/palace``, lists
      collections, calls ``get_collection() + count()`` on each.
      Sub-second on a 130 MB palace per the S-0034 measurement.
    - ``engine/tools/probe_repo.py`` — checks effective ``core.bare``,
      parent-clone direct ``core.bare``, and HEAD resolution.

    The check categories are stable across boot-time and pre-commit
    invocations so the soft-warn lifecycle (per ADR 0042) treats
    findings from both contexts as the same category. A boot-probe
    finding accumulates in the same archive bucket as a pre-commit
    finding, supporting cross-session persistence detection.

    Returns:
        ValidationResult with ``checks_run`` populated for both probes
        and ``hard_fails`` / ``soft_warns`` populated as the probes run.

    Non-responsibilities:
        - Does not perform rollback or repair. The probes report
          state; remediation is the caller's responsibility.
        - Does not retry on transient failure. A single subprocess
          run per probe; flakes show up as hard-fails on that run.
        - Does not handle network-side state (Supabase, GitHub).
          Those have their own health surfaces.
    """
    r = ValidationResult()

    probes = (
        (PROBE_PALACE, "chromadb_palace_health", "palace"),
        (PROBE_REPO, "repo_config_health", "repo"),
    )

    for probe_path, category, probe_name in probes:
        check_name = f"shared_state_{probe_name}"
        r.add_check(check_name)
        if not probe_path.is_file():
            r.soft_warn(
                category,
                f"probe script missing: {probe_path.relative_to(REPO_ROOT)}",
            )
            continue
        proc = subprocess.run(
            ["python3", str(probe_path)],
            capture_output=True,
            text=True,
            env=scrubbed_env(),
        )
        # Probes emit findings on stderr by convention; fall back to
        # stdout if stderr is empty (covers an unexpected exit-code
        # path where the probe reported on stdout).
        body = (proc.stderr.strip() or proc.stdout.strip()) or "(no output)"
        if proc.returncode == 0:
            continue
        if proc.returncode == 1:
            r.soft_warn(category, body)
        elif proc.returncode == 2:
            r.hard_fail(f"{probe_name} probe hard-broken:\n{body}")
        elif proc.returncode == 139:
            r.hard_fail(
                f"{probe_name} probe segfaulted (SIGSEGV); treating as "
                f"hard-broken. For the palace probe this is the S-0034 "
                f"corruption signature.\n{body}"
            )
        else:
            r.hard_fail(
                f"{probe_name} probe exited {proc.returncode} (unexpected):\n{body}"
            )

    return r


# ---------------------------------------------------------------------------
# Issue-collision check (post-S-0042 per ADR 0048)
# ---------------------------------------------------------------------------


def validate_issue_collisions() -> ValidationResult:
    """Scan open GitHub Issues for keyword/path overlap with this session.

    Wraps ``engine/tools/scan_issue_collisions.py``. Exit-code semantics
    mirror the scanner's own contract:

    - 0: no collisions; clean.
    - 1: one or more collisions found; recorded as ``issue_collision``
      soft-warns. The scanner's stderr lines (one per collision) become
      the soft-warn bodies.

    A ``gh`` failure (no auth, no network, repo not on GitHub) emits a
    stderr note inside the scanner and the scanner returns 0 — the
    check is best-effort, never blocking. The same posture applies if
    the scanner itself is missing (treated as not-installed; a single
    soft-warn surfaces and the validator continues).

    Returns:
        ValidationResult with ``issue_collision`` soft-warns when open
        Issues touch the session's scope, or empty when clean.

    Non-responsibilities:
        - Does not create, update, or close Issues.
        - Does not enforce any first-commit-only gating; the scanner's
          input is the staged-files diff, which is empty on a no-op
          run, so the check is naturally cheap when there's nothing to
          match. The session decides whether to address each warn.
    """
    r = ValidationResult()
    r.add_check("issue_collision")

    if not SCAN_ISSUE_COLLISIONS.is_file():
        try:
            display_path = str(SCAN_ISSUE_COLLISIONS.relative_to(REPO_ROOT))
        except ValueError:
            display_path = str(SCAN_ISSUE_COLLISIONS)
        r.soft_warn(
            "issue_collision",
            f"scan_issue_collisions.py missing at {display_path}",
        )
        return r

    proc = subprocess.run(
        ["python3", str(SCAN_ISSUE_COLLISIONS)],
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )

    if proc.returncode == 0:
        return r

    if proc.returncode == 1:
        # Each stderr line beginning with "[scan-issue-collisions]" is a
        # collision finding. Strip the prefix for cleaner soft-warn bodies.
        for line in proc.stderr.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("[scan-issue-collisions]"):
                line = line[len("[scan-issue-collisions]") :].strip()
            r.soft_warn("issue_collision", line)
        return r

    # Unexpected exit code — surface as soft-warn so the run continues.
    r.soft_warn(
        "issue_collision",
        f"scan_issue_collisions.py exited {proc.returncode} (unexpected): "
        f"{proc.stderr.strip() or '(no output)'}",
    )
    return r


# ---------------------------------------------------------------------------
# Scope-discipline checks (post-S-0042 per ADR 0049)
# ---------------------------------------------------------------------------


_PHASE_TOKEN_RE = re.compile(r"phase:\s*([A-Za-z0-9_.\-]+)", re.IGNORECASE)


def _build_plan_phase_identifiers() -> set[str]:
    """Return phase identifier tokens from build_plan/MANIFEST.md.

    Lower-cased; tolerant of formatting variations (P_3 vs Phase 3
    vs 3) by treating the manifest as a corpus the declared phase
    must appear inside.
    """
    manifest = REPO_ROOT / "build_plan" / "MANIFEST.md"
    if not manifest.is_file():
        return set()
    text = manifest.read_text().lower()
    tokens: set[str] = set()
    for match in re.findall(r"\bp_\d+(?:\.\d+)?\b", text):
        tokens.add(match.lower())
    for match in re.findall(r"phase\s*\d+(?:\.\d+)?", text):
        tokens.add(match.lower())
    for match in re.findall(r"\b\d+\.\d+\b", text):
        tokens.add(match.lower())
    return tokens


def validate_scope_discipline() -> ValidationResult:
    """Soft-warn on missing/mismatched declared_scope and on
    delivered=false at shutdown.

    Three categories per ADR 0049:

    - ``empty_declared_scope`` — current.json missing the field or
      holding an empty string. Skipped silently when current.json
      itself is absent (exploration mode).
    - ``phase_mismatch_declared_scope`` — declared_scope contains a
      ``phase:`` token whose identifier doesn't appear in
      ``build_plan/MANIFEST.md``. The literal string starting with
      ``NA`` (any case, with or without suffix like
      ``NA-engine-apparatus``) is treated as the explicit "no
      build-plan phase" marker for operational sessions and skips
      the manifest match.
    - ``scope_delivery_non_yes`` — current.json has ``scope_delivery``
      with ``delivered: false``, regardless of
      ``user_confirmed_changes``. The warn is signal for cross-session
      aggregation, not punishment.

    Returns:
        ValidationResult with the three checks always registered.
    """
    r = ValidationResult()
    r.add_check("empty_declared_scope")
    r.add_check("phase_mismatch_declared_scope")
    r.add_check("scope_delivery_non_yes")

    current = REPO_ROOT / "engine" / "session" / "current.json"
    if not current.is_file():
        return r

    try:
        data = json.loads(current.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        r.soft_warn("empty_declared_scope", f"current.json unreadable: {exc}")
        return r

    scope = data.get("declared_scope")
    if not isinstance(scope, str) or not scope.strip():
        r.soft_warn(
            "empty_declared_scope",
            "current.json has no declared_scope field; per ADR 0049 the "
            "eager-claim ritual must write this field as a 1-3 sentence "
            "statement of what the session commits to deliver.",
        )
    else:
        phase_match = _PHASE_TOKEN_RE.search(scope)
        if phase_match:
            value = phase_match.group(1).lower()
            if not value.startswith("na"):
                manifest = REPO_ROOT / "build_plan" / "MANIFEST.md"
                manifest_text = (
                    manifest.read_text().lower() if manifest.is_file() else ""
                )
                manifest_tokens = _build_plan_phase_identifiers()
                if value not in manifest_text and not any(
                    value in tok or tok in value for tok in manifest_tokens
                ):
                    r.soft_warn(
                        "phase_mismatch_declared_scope",
                        f"declared_scope phase token '{value}' does not "
                        f"appear in build_plan/MANIFEST.md. Either correct "
                        f"the identifier or, if this is operational work "
                        f"with no build-plan phase, use 'phase: NA-...'.",
                    )

    delivery = data.get("scope_delivery")
    if isinstance(delivery, dict) and delivery.get("delivered") is False:
        user_confirmed = delivery.get("user_confirmed_changes", False)
        explanation = delivery.get("explanation") or "(no explanation)"
        r.soft_warn(
            "scope_delivery_non_yes",
            f"scope_delivery.delivered=false "
            f"(user_confirmed_changes={user_confirmed}); "
            f"explanation: {str(explanation)[:200]}",
        )

    return r


# ---------------------------------------------------------------------------
# Routine-mode soft-warns (post-S-0044 per ADR 0051)
# ---------------------------------------------------------------------------


def validate_routine_mode() -> ValidationResult:
    """Soft-warns specific to routine-mode sessions per ADR 0051.

    Two checks, both no-op when not in routine mode:

    - ``routine_no_target_reference`` — current_plan.md exists but
      doesn't mention the active task's id or name. Suggests the
      routine session's plan drifted from the target.
    - ``routine_issue_spam`` — more than 3 GitHub issues were created
      since the session's started_at. Confused-session containment;
      legitimate fix-this-many findings ride through (the warn is
      advisory, not blocking).

    Detection: routine mode = auto_target.json AND current_plan.md
    both exist AND a task has status ``in_progress``. Any of the three
    missing → both checks are no-ops.

    Issue counting: ``gh issue list --state all --search
    "created:>=YYYY-MM-DD"`` with a 10-second timeout. Failure modes
    (gh unavailable, unauthenticated, network error, timeout) are
    silent — the project is offline-tolerant.
    """
    r = ValidationResult()
    r.add_check("routine_no_target_reference")
    r.add_check("routine_issue_spam")

    target_path = REPO_ROOT / "engine" / "session" / "auto_target.json"
    plan_path = REPO_ROOT / "engine" / "session" / "current_plan.md"
    current_path = REPO_ROOT / "engine" / "session" / "current.json"

    if not target_path.exists() or not plan_path.exists():
        return r  # not in routine mode

    try:
        target = json.loads(target_path.read_text())
    except (OSError, json.JSONDecodeError):
        return r

    active = next(
        (t for t in target.get("tasks", []) if t.get("status") == "in_progress"),
        None,
    )
    if active is None:
        return r  # not in routine mode

    # Check 1: plan references active task
    try:
        plan_text = plan_path.read_text()
    except OSError:
        plan_text = ""
    task_id = str(active.get("id", ""))
    task_name = str(active.get("name", ""))
    has_id_ref = bool(task_id) and task_id in plan_text
    has_name_ref = bool(task_name) and task_name in plan_text
    if not (has_id_ref or has_name_ref):
        r.soft_warn(
            "routine_no_target_reference",
            f"current_plan.md does not reference active task '{task_id}' "
            f"or its name; routine session may have drifted from target.",
        )

    # Check 2: issue spam (best-effort; silent on tool unavailability)
    if not current_path.exists():
        return r
    try:
        current = json.loads(current_path.read_text())
    except (OSError, json.JSONDecodeError):
        return r
    started_at = current.get("started_at")
    if not isinstance(started_at, str) or len(started_at) < 10:
        return r

    date_prefix = started_at[:10]  # YYYY-MM-DD
    try:
        proc = subprocess.run(
            [
                "gh",
                "issue",
                "list",
                "--state",
                "all",
                "--limit",
                "30",
                "--json",
                "number,createdAt",
                "--search",
                f"created:>={date_prefix}",
            ],
            capture_output=True,
            text=True,
            env=scrubbed_env(),
            timeout=10,
            check=True,
        )
    except (
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        FileNotFoundError,
    ):
        return r

    try:
        issues = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return r

    count = sum(
        1
        for i in issues
        if isinstance(i, dict)
        and isinstance(i.get("createdAt"), str)
        and i["createdAt"] >= started_at
    )
    if count > 3:
        r.soft_warn(
            "routine_issue_spam",
            f"routine session has created {count} issues since {started_at}; "
            f"review for legitimacy or session-confusion (defense-in-depth, "
            f"per ADR 0051).",
        )

    return r


# ---------------------------------------------------------------------------
# Cascade-analysis checks (post-S-0029 per ADR 0041)
# ---------------------------------------------------------------------------


def _tracked_md_files(exclude_dirs: list[str]) -> list[Path]:
    """Return tracked Markdown files in the repo, excluding named directories.

    Walks REPO_ROOT for *.md files, skipping any path whose parts include any
    name in ``exclude_dirs``. Excludes .git, .claude/worktrees, node_modules,
    and any directories the caller specifies.

    Used by the cascade-analysis checks to scope their grep without importing
    git tooling. Approximation of `git ls-files '*.md'` excluding the common
    untracked-but-present cases (worktree mirrors, hook caches).

    Non-responsibilities:
        - Does not call git. Consumers that need exact tracked-file membership
          should invoke git ls-files directly.
    """
    skip = {".git", "node_modules", "__pycache__"} | set(exclude_dirs)
    out: list[Path] = []
    for path in REPO_ROOT.rglob("*.md"):
        # Skip if any part of the path matches a skip name OR if path is
        # under .claude/worktrees/ (worktree mirrors duplicate tracked files).
        parts = path.relative_to(REPO_ROOT).parts
        if any(p in skip for p in parts):
            continue
        if len(parts) >= 2 and parts[0] == ".claude" and parts[1] == "worktrees":
            continue
        out.append(path)
    return out


def validate_superseded_adr_currency() -> ValidationResult:
    """Soft-warn on docs that cite a Superseded ADR without historical marker.

    For each ADR with Status `Superseded by ADR NNNN`, finds the new ADR's
    id and greps tracked .md files (excluding ADR files themselves and
    ENGINE_LOG.md / product/CHANGELOG.md). Soft-warns on any citation of
    the superseded ADR's id whose surrounding 50 chars do not include
    "superseded" (case-insensitive) or the new ADR's id.

    Per ADR 0041 / cascade-discipline.md.

    Returns:
        ValidationResult with check ``cascade_superseded_adr_currency``
        recorded and soft-warns under category
        ``superseded_adr_currency``.

    Non-responsibilities:
        - Does not parse markdown link syntax beyond looking for the ADR
          id substring. False positives possible if an ADR id appears
          incidentally in unrelated prose.
        - Does not modify any file.
    """
    r = ValidationResult()
    r.add_check("cascade_superseded_adr_currency")

    superseded_pattern = re.compile(
        r"^[\s*\-]*Status[\s*]*:[\s*]*Superseded by ADR\s+(\d{4})",
        re.MULTILINE | re.IGNORECASE,
    )

    superseded_map: dict[str, str] = {}  # old_id -> new_id
    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if not adr_dir.is_dir():
            continue
        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            text = adr_file.read_text()
            m = superseded_pattern.search(text)
            if m:
                old_id = adr_file.name[:4]
                superseded_map[old_id] = m.group(1)

    if not superseded_map:
        return r

    md_files = _tracked_md_files(exclude_dirs=[])
    for md_path in md_files:
        rel = md_path.relative_to(REPO_ROOT)
        # Skip ADR files (their narration of supersession is appropriate).
        parts = rel.parts
        if "adr" in parts:
            continue
        # Skip the changelog files (their job is historical narration).
        if rel.name in {"ENGINE_LOG.md", "CHANGELOG.md"}:
            continue
        try:
            text = md_path.read_text()
        except OSError:
            continue
        for old_id, new_id in superseded_map.items():
            for match in re.finditer(rf"ADR\s+{old_id}\b", text):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                window = text[start:end].lower()
                if "superseded" in window or new_id in window:
                    continue
                r.soft_warn(
                    "superseded_adr_currency",
                    f"{rel}: cites ADR {old_id} (superseded by ADR {new_id}) "
                    f"without historical marker",
                )
    return r


def _has_orphan_ok_annotation(adr_text: str) -> bool:
    """Return True if an ADR carries the Orphan-OK suppression header.

    The annotation form is `- **Orphan-OK:** <reason>; revisit at <id>` per
    cascade-discipline.md. The pattern matches the bold-around-label form
    permissively to tolerate authoring variation.
    """
    return bool(
        re.search(
            r"^[\s*\-]*Orphan-OK[\s*]*:[\s*]*\S",
            adr_text,
            re.MULTILINE | re.IGNORECASE,
        )
    )


def validate_adr_back_reference_orphan() -> ValidationResult:
    """Soft-warn on Accepted ADRs with no inbound citation outside their subtree.

    For each ADR with Status `Accepted`, greps tracked .md files outside
    `*/adr/*` for the ADR's id. Soft-warns when zero matches found, unless
    the ADR carries an `Orphan-OK` annotation.

    Per ADR 0041 / cascade-discipline.md.

    Returns:
        ValidationResult with check ``cascade_adr_back_reference_orphan``
        recorded and soft-warns under category ``adr_back_reference_orphan``.

    Non-responsibilities:
        - Does not distinguish ENGINE_LOG.md mentions from substantive
          citations. ENGINE_LOG entries naming an ADR count as inbound
          (an ADR that landed and got logged is not orphaned in the
          sense this check targets).
    """
    r = ValidationResult()
    r.add_check("cascade_adr_back_reference_orphan")

    accepted_status = re.compile(
        r"^[\s*\-]*Status[\s*]*:[\s*]*Accepted\b",
        re.MULTILINE | re.IGNORECASE,
    )

    md_files = _tracked_md_files(exclude_dirs=[])
    non_adr_md = [p for p in md_files if "adr" not in p.relative_to(REPO_ROOT).parts]

    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if not adr_dir.is_dir():
            continue
        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            text = adr_file.read_text()
            if not accepted_status.search(text):
                continue
            if _has_orphan_ok_annotation(text):
                continue
            adr_id = adr_file.name[:4]
            cited = False
            for md_path in non_adr_md:
                try:
                    md_text = md_path.read_text()
                except OSError:
                    continue
                if re.search(rf"\b(?:ADR\s+)?{adr_id}\b", md_text):
                    # Disambiguate: bare four-digit numbers occur in many
                    # contexts. Require either "ADR <id>" or the id appearing
                    # adjacent to a markdown link to the ADR file.
                    if re.search(rf"ADR\s+{adr_id}\b|\b{adr_id}-[\w-]+\.md", md_text):
                        cited = True
                        break
            if not cited:
                rel = adr_file.relative_to(REPO_ROOT)
                r.soft_warn(
                    "adr_back_reference_orphan",
                    f"{rel}: Accepted ADR has no inbound citation outside */adr/*; "
                    "annotate Orphan-OK to suppress if intentional",
                )
    return r


def validate_adr_consequences_deliverable_audit() -> ValidationResult:
    """Soft-warn on ADR Consequences promises whose target session closed without delivery.

    Heuristic regex against each ADR's Consequences section for substrings of
    the form ``(anticipated|lands?|expected|targeted) (around |at |in )?S-NNNN``.
    For each match, checks whether the named session is closed (per
    `engine/session/archive/`); if closed, looks for a backtick-wrapped or
    markdown-link path also mentioned nearby and soft-warns when that path
    does not exist on disk.

    Per ADR 0041 / cascade-discipline.md. The check's value is partial
    coverage of a class with zero coverage today; false negatives are
    acknowledged.

    Returns:
        ValidationResult with check ``cascade_adr_consequences_deliverable``
        recorded and soft-warns under category
        ``adr_consequences_deliverable_audit``.

    Non-responsibilities:
        - Does not catch promises in prose forms that don't match the
          regex (e.g., "ships at the next milestone").
        - Does not retroactively check that a delivered file matches the
          ADR's Consequences description; only that something at the named
          path exists.
    """
    r = ValidationResult()
    r.add_check("cascade_adr_consequences_deliverable")

    archive_dir = REPO_ROOT / "engine" / "session" / "archive"
    if not archive_dir.is_dir():
        return r
    archives_closed = {p.stem for p in archive_dir.glob("S-[0-9][0-9][0-9][0-9].json")}

    deliverable_pattern = re.compile(
        r"(?:anticipated|lands?|expected|targeted)\s+"
        r"(?:around\s+|at\s+|in\s+)?S-(\d{4})",
        re.IGNORECASE,
    )
    consequences_pattern = re.compile(
        r"^##\s+Consequences\s*$.*?(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if not adr_dir.is_dir():
            continue
        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            text = adr_file.read_text()
            cons_match = consequences_pattern.search(text)
            if not cons_match:
                continue
            cons_text = cons_match.group(0)
            for m in deliverable_pattern.finditer(cons_text):
                target_session = f"S-{m.group(1)}"
                if target_session not in archives_closed:
                    continue
                window_start = max(0, m.start() - 200)
                window_end = min(len(cons_text), m.end() + 200)
                window = cons_text[window_start:window_end]
                paths = re.findall(r"`([\w./_-]+\.(?:py|md|sql|json))`", window)
                paths += re.findall(r"\]\(([\w./_-]+\.(?:py|md|sql|json))\)", window)
                # Resolve each path against both repo root AND the ADR file's
                # directory (relative-link convention in markdown). A path
                # that resolves under either is considered delivered.
                missing = []
                for p in paths:
                    if (REPO_ROOT / p).exists():
                        continue
                    if (adr_file.parent / p).resolve().exists():
                        continue
                    missing.append(p)
                if missing:
                    rel = adr_file.relative_to(REPO_ROOT)
                    r.soft_warn(
                        "adr_consequences_deliverable_audit",
                        f"{rel}: Consequences promised {missing} for "
                        f"{target_session} (closed) — file(s) absent on disk",
                    )
    return r


# ---------------------------------------------------------------------------
# Code-discipline gates (post-S-0026 per ADR 0038)
# ---------------------------------------------------------------------------


def validate_code_gates(files: list[Path]) -> ValidationResult:
    """Run the code-discipline gate stack against the given Python files.

    Implements Layer 2 of the ADR 0038 expression contract for AI-authored
    code. The gates run as subprocesses against the named files; each gate
    failure is recorded as a hard-fail. Soft-warns are not used at this
    layer — type errors, lint violations, format failures, missing tests,
    and test failures are all blocking.

    Gates (in run order):

    - ruff_check: ``python3 -m ruff check <files>``. Hard-fail on non-zero
      exit. Lint-rule violations across the project's ruff configuration.
    - ruff_format: ``python3 -m ruff format --check <files>``. Hard-fail
      on non-zero exit. The file's existing format does not match the
      project style.
    - mypy_strict: ``python3 -m mypy --strict <files>``. Hard-fail on
      non-zero exit. Annotation gaps, Any leakage, missing return types,
      and other strict-mode issues.
    - test_presence: each non-test source file (file whose name does not
      start with ``test_`` and whose path is not under a ``tests/``
      directory) has a sibling ``test_<name>.py`` or a
      ``tests/test_<name>.py``. Hard-fail on missing.
    - pytest_run: ``python3 -m pytest <test_files>`` against the discovered
      test files. Hard-fail on non-zero exit.

    Inputs:
        files: list of absolute Paths to Python source files. May be empty
            (returns a ValidationResult with the ``code_gates_empty`` check
            recorded and no failures).

    Returns:
        ValidationResult with check categories
        ``code_gates_ruff_check``, ``code_gates_ruff_format``,
        ``code_gates_mypy``, ``code_gates_test_presence``,
        ``code_gates_pytest`` populated as each gate runs. Hard-fail
        messages include the failing tool's stdout (and stderr where
        useful) so the offending gate's output is visible without re-running.

    Non-responsibilities:
        - Does not modify files (no auto-fix). Callers run ``ruff check
          --fix`` or ``ruff format`` manually after seeing the failures.
        - Does not install the gate-stack tools. The caller arranges
          installation per engine/tools/requirements.txt.
        - Does not validate that the gate-stack tools are on PATH. The
          ``python3 -m`` invocation pattern means importable presence
          suffices; if a tool is not importable, the subprocess returns
          non-zero and the failure surfaces as that gate's hard-fail.
        - Does not enforce contract-block presence (Layer 1) or perform
          cold-context review (Layer 3). Those layers are enforced
          elsewhere — Layer 1 by authoring discipline at the moment of
          edit; Layer 3 by the session-shutdown sub-agent pass.
    """
    r = ValidationResult()

    if not files:
        r.add_check("code_gates_empty")
        return r

    file_args = [str(f) for f in files]

    # Layer 2 gate 1: ruff check (lint)
    # All four code-gate subprocesses pass env=scrubbed_env() per ADR 0045
    # to prevent GIT_DIR / GIT_WORK_TREE leakage from a parent context
    # (e.g., the pre-commit hook's own git invocations) into pytest tests
    # that subprocess git — the S-0033 vector that wrote core.bare=true
    # to the parent's .git/config.
    r.add_check("code_gates_ruff_check")
    proc = subprocess.run(
        ["python3", "-m", "ruff", "check", *file_args],
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    if proc.returncode != 0:
        r.hard_fail(f"ruff check failed:\n{proc.stdout}{proc.stderr}".rstrip())

    # Layer 2 gate 2: ruff format --check
    r.add_check("code_gates_ruff_format")
    proc = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", *file_args],
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    if proc.returncode != 0:
        r.hard_fail(f"ruff format check failed:\n{proc.stdout}{proc.stderr}".rstrip())

    # Layer 2 gate 3: mypy --strict
    r.add_check("code_gates_mypy")
    proc = subprocess.run(
        ["python3", "-m", "mypy", "--strict", *file_args],
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    if proc.returncode != 0:
        r.hard_fail(f"mypy --strict failed:\n{proc.stdout}{proc.stderr}".rstrip())

    # Layer 2 gate 4: test presence — each non-test source file has a
    # corresponding test_<name>.py (sibling or in tests/ subdirectory).
    # conftest.py is exempted because pytest treats it as a fixture-sharing
    # module that's exercised transitively by every test in its directory;
    # writing test_conftest.py would be circular.
    r.add_check("code_gates_test_presence")
    test_files: list[Path] = []
    for f in files:
        if f.name.startswith("test_") or f.name == "conftest.py" or "tests" in f.parts:
            # Test files and conftest fixtures don't need their own tests.
            continue
        sibling_test = f.parent / f"test_{f.name}"
        nested_test = f.parent / "tests" / f"test_{f.name}"
        if sibling_test.is_file():
            test_files.append(sibling_test)
        elif nested_test.is_file():
            test_files.append(nested_test)
        else:
            rel = f.relative_to(REPO_ROOT) if REPO_ROOT in f.parents else f
            r.hard_fail(
                f"no test file for {rel}: expected test_{f.name} alongside "
                f"or under {f.parent.name}/tests/"
            )

    # Layer 2 gate 5: pytest run against the discovered test files
    r.add_check("code_gates_pytest")
    if test_files:
        test_args = [str(t) for t in test_files]
        proc = subprocess.run(
            ["python3", "-m", "pytest", "-q", *test_args],
            capture_output=True,
            text=True,
            env=scrubbed_env(),
        )
        if proc.returncode != 0:
            r.hard_fail(f"pytest failed:\n{proc.stdout}{proc.stderr}".rstrip())

    return r


# ---------------------------------------------------------------------------
# SQL-discipline gates (post-S-0027 per ADR 0039 + migration-discipline.md)
# ---------------------------------------------------------------------------


# Enum-modeled TEXT columns that require CHECK (... IN (...)) constraints per
# migration-discipline.md Layer 2. The list is maintained alongside the gate;
# a column added here updates the gate without a posture change. Names are
# matched as case-insensitive identifiers in CREATE TABLE column lists.
SQL_ENUM_COLUMNS = (
    "confidence_level",
    "interaction_type",
    "friction_type",
    "suggested_review_focus",
    "status",
)


def _strip_sql_line_comments(text: str) -> str:
    """Return ``text`` with ``--`` line comments stripped.

    SQL gate checks operate on the non-comment body of a migration so that
    keywords appearing inside contract-comment headers (``-- REFERENCES
    users(id)``) do not produce false-positive matches against gate
    expectations.

    The function strips from the first ``--`` on a line through the line's
    end. Block comments (``/* ... */``) are not stripped — migrations
    authored under [`migration-discipline.md`] use line comments only;
    block comments inside the migration body would be flagged as a
    refinement signal rather than silently swallowed.

    Inputs:
        text: SQL source text.

    Returns:
        Text with each line truncated at the first ``--``. Trailing
        newlines and inter-statement structure are preserved.

    Non-responsibilities:
        - Does not parse strings; an in-string ``--`` (e.g.,
          ``'a--b'``) is stripped along with the rest of the line. SQL
          migrations under this contract use string literals rarely
          and never with ``--`` tokens; the simplification is acceptable.
        - Does not handle block comments.
    """
    out_lines: list[str] = []
    for line in text.splitlines():
        idx = line.find("--")
        if idx == -1:
            out_lines.append(line)
        else:
            out_lines.append(line[:idx])
    return "\n".join(out_lines)


def _check_transaction_wrap(text: str, rel_path: str) -> str | None:
    """Return a hard-fail message if ``text`` lacks a transaction wrap, else None.

    A migration is wrapped if its non-comment body begins with ``BEGIN``
    (with or without a trailing ``;``) and ends with ``COMMIT`` or ``END``
    (with or without a trailing ``;``). Whitespace around the keywords is
    tolerated. Multiple BEGIN/COMMIT pairs are accepted; the check
    requires only that the outer envelope exists.

    Inputs:
        text: SQL source text with line comments already stripped.
        rel_path: Relative path used in the failure message.

    Returns:
        A hard-fail message string if the wrap is missing; ``None`` if
        the wrap is present.

    Non-responsibilities:
        - Does not parse SQL syntactically; missing semicolons or
          out-of-order statements are not the gate's concern.
        - Does not enforce a single transaction; nested or sequential
          transactions are accepted.
    """
    body = text.strip()
    if not body:
        return f"{rel_path}: empty migration body (transaction wrap absent)"
    head_match = re.match(r"BEGIN\b", body, re.IGNORECASE)
    if not head_match:
        return (
            f"{rel_path}: migration does not start with BEGIN; "
            "see migration-discipline.md Layer 2 transaction wrap."
        )
    tail_match = re.search(r"\b(COMMIT|END)\b\s*;?\s*$", body, re.IGNORECASE)
    if not tail_match:
        return (
            f"{rel_path}: migration does not end with COMMIT or END; "
            "see migration-discipline.md Layer 2 transaction wrap."
        )
    return None


def _check_cascade_present(text: str, rel_path: str) -> list[str]:
    """Return hard-fail messages for FKs to users(id) lacking ON DELETE CASCADE.

    Per [ADR 0031](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md),
    every learner-state FK to ``users(id)`` (or ``public.users(id)``) carries
    ``ON DELETE CASCADE``. The gate scans for ``REFERENCES (public.)?users\\(id\\)``
    matches and verifies that ``ON DELETE CASCADE`` appears within the same
    statement (delimited by the next semicolon).

    Inputs:
        text: SQL source text with line comments already stripped.
        rel_path: Relative path used in failure messages.

    Returns:
        List of hard-fail messages. Empty list means every FK match
        carries CASCADE. One message per offending FK reference so the
        author sees all violations in a single pass.

    Non-responsibilities:
        - Does not validate the CASCADE keyword spelling beyond
          ``ON DELETE CASCADE`` (case-insensitive). Variants like
          ``ON DELETE RESTRICT`` are flagged as missing CASCADE.
        - Does not detect CASCADE-by-trigger patterns. A migration that
          implements cascade via trigger instead of declarative FK must
          opt out via a comment naming the design choice and gate the
          comment via the cold-review pass; no automated opt-out exists.
        - Does not check FKs to other tables. Only ``users(id)`` is
          scoped here per ADR 0031's load-bearing requirement.
    """
    fails: list[str] = []
    # Find each REFERENCES (public.)?users(id) match and the statement it
    # belongs to. A statement is delimited by semicolons in the cleaned text.
    fk_pattern = re.compile(
        r"REFERENCES\s+(?:public\.)?users\s*\(\s*id\s*\)",
        re.IGNORECASE,
    )
    cascade_pattern = re.compile(r"ON\s+DELETE\s+CASCADE", re.IGNORECASE)
    # Split into statements
    statements = text.split(";")
    for stmt in statements:
        if not fk_pattern.search(stmt):
            continue
        if not cascade_pattern.search(stmt):
            # Take a snippet of the offending statement for the message
            snippet = " ".join(stmt.split())[:120]
            fails.append(
                f"{rel_path}: FK to users(id) without ON DELETE CASCADE; "
                f"statement: {snippet}... "
                "(see ADR 0031 + migration-discipline.md Layer 2)"
            )
    return fails


def _check_rls_enabled(text: str, rel_path: str) -> list[str]:
    """Return hard-fail messages for public.* CREATE TABLE without RLS-enable.

    Per [`migration-discipline.md`] Layer 2 + the S-0027 build-readiness
    decision (RLS on with v1 policies in Phase 3), every ``CREATE TABLE``
    in the ``public.*`` namespace must be paired with an explicit
    ``ALTER TABLE <name> ENABLE ROW LEVEL SECURITY`` somewhere in the same
    migration file. RLS-disable requires an explicit comment naming the
    deferral; the comment-based opt-out is detected by the literal token
    ``RLS-DEFERRED`` appearing on a comment line earlier in the file
    (line comments are stripped before the gate runs, so the opt-out
    marker must appear in the ORIGINAL text — the gate re-reads the
    original to detect it).

    Inputs:
        text: SQL source text with line comments already stripped.
        rel_path: Relative path used in failure messages.

    Returns:
        List of hard-fail messages. One per offending CREATE TABLE.

    Non-responsibilities:
        - Does not require an RLS policy to exist, only the enable
          statement. Policy authoring discipline lives in the migration's
          contract block (Layer 1) and the cold-review pass (Layer 3).
        - Does not check RLS on tables outside ``public.*``. The
          ``auth.*`` and ``storage.*`` schemas are Supabase-managed and
          their RLS posture is out of project scope.
    """
    fails: list[str] = []
    # CREATE TABLE [IF NOT EXISTS] (public.)?<name> (...
    table_pattern = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:public\.)?(\w+)",
        re.IGNORECASE,
    )
    enable_rls_pattern = re.compile(
        r"ALTER\s+TABLE\s+(?:public\.)?(\w+)\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY",
        re.IGNORECASE,
    )
    enabled_tables = {m.group(1).lower() for m in enable_rls_pattern.finditer(text)}
    for match in table_pattern.finditer(text):
        table_name = match.group(1).lower()
        if table_name in enabled_tables:
            continue
        fails.append(
            f"{rel_path}: CREATE TABLE public.{table_name} without "
            "ALTER TABLE ... ENABLE ROW LEVEL SECURITY in same migration; "
            "see migration-discipline.md Layer 2 RLS-enable gate."
        )
    return fails


def _check_enum_check_constraints(
    text: str, rel_path: str, original_text: str
) -> list[str]:
    """Return hard-fail messages for enum-modeled columns missing CHECK constraints.

    For each column name in ``SQL_ENUM_COLUMNS``, if the migration declares
    a column with that name in any ``CREATE TABLE`` statement, the
    migration must include a CHECK constraint of shape
    ``CHECK (<column> IN (...))`` somewhere in the same file.

    The check is structural — the constraint may be defined inline at
    column declaration, as a table-level CONSTRAINT clause, or via a
    later ALTER TABLE. All forms are accepted as long as the column
    name appears inside a ``CHECK (... IN (...))`` clause.

    Inputs:
        text: SQL source text with line comments already stripped (for
            column-declaration matching).
        rel_path: Relative path used in failure messages.
        original_text: Pre-strip text (currently unused; reserved for
            future opt-out comment markers symmetric to RLS-DEFERRED).

    Returns:
        List of hard-fail messages. One per offending column declaration.

    Non-responsibilities:
        - Does not validate the enum values themselves. Authoring
          discipline (the per-migration contract block + cold-review
          pass) verifies that the IN list matches the declared
          vocabulary in TENSION_VOCABULARY.md or the relevant ADR.
        - Does not require constraints on non-enum columns. The list
          ``SQL_ENUM_COLUMNS`` is the gate's universe.
        - Does not detect type mismatches (e.g., a column declared
          INTEGER but listed in SQL_ENUM_COLUMNS). Type expectations
          live in the build-readiness report.
    """
    del original_text  # reserved for future opt-out marker support
    fails: list[str] = []
    for col_name in SQL_ENUM_COLUMNS:
        # Find each occurrence of the column name in a column-declaration
        # context: <name> followed by a TEXT/VARCHAR type indicator. The
        # check is conservative — a column whose name appears in a
        # comment-stripped body inside a TEXT-typed declaration triggers
        # the CHECK requirement.
        col_decl_pattern = re.compile(
            rf"\b{col_name}\b\s+(?:TEXT|VARCHAR(?:\s*\(\s*\d+\s*\))?)",
            re.IGNORECASE,
        )
        if not col_decl_pattern.search(text):
            continue
        # Require a CHECK (... <col_name> ... IN (...)) somewhere in the file.
        check_pattern = re.compile(
            rf"CHECK\s*\([^)]*\b{col_name}\b[^)]*\bIN\s*\(",
            re.IGNORECASE | re.DOTALL,
        )
        if not check_pattern.search(text):
            fails.append(
                f"{rel_path}: column '{col_name}' declared but no "
                f"CHECK ({col_name} IN (...)) constraint found; "
                "see migration-discipline.md Layer 2 enum-CHECK gate."
            )
    return fails


def validate_sql_gates(files: list[Path]) -> ValidationResult:
    """Run the SQL-discipline gate stack against the given migration files.

    Implements Layer 2 of the [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md)
    universal expression contract for the SQL/migrations pattern. The gates
    run in-process against the file contents (no subprocesses); each gate
    failure is recorded as a hard-fail. Soft-warns are not used at this
    layer — missing CASCADE, missing RLS-enable, missing transaction wrap,
    and malformed CHECK constraints are all blocking.

    Gates (in run order, per file):

    - sql_gates_transaction_wrap: file's non-comment body begins with
      ``BEGIN`` and ends with ``COMMIT`` or ``END``. Hard-fail on absence
      of either bookend.
    - sql_gates_cascade_present: every ``REFERENCES (public.)?users(id)``
      occurs within a statement that also includes
      ``ON DELETE CASCADE``. Hard-fail otherwise. Per [ADR 0031](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md).
    - sql_gates_rls_enabled: every ``CREATE TABLE`` in ``public.*`` is
      paired with ``ALTER TABLE <name> ENABLE ROW LEVEL SECURITY`` in the
      same file. Hard-fail otherwise.
    - sql_gates_enum_checks: every column declared with a name in
      ``SQL_ENUM_COLUMNS`` and a TEXT/VARCHAR type carries a
      ``CHECK (<name> IN (...))`` constraint somewhere in the same file.
      Hard-fail otherwise.

    Inputs:
        files: list of absolute Paths to ``.sql`` files. May be empty
            (returns a ValidationResult with the ``sql_gates_empty``
            check recorded and no failures). Each file is read into
            memory; the gate stack runs in-process.

    Returns:
        ValidationResult with check categories
        ``sql_gates_transaction_wrap``, ``sql_gates_cascade_present``,
        ``sql_gates_rls_enabled``, ``sql_gates_enum_checks`` populated
        as each gate runs across the input files. Hard-fail messages
        cite the offending file and the gate that flagged it; the
        per-gate helpers preserve enough context to locate the
        violation without re-running the gate.

    Non-responsibilities:
        - Does not modify files. The gates report; the author fixes.
        - Does not validate SQL syntax beyond the keyword-level checks
          listed above. Postgres parser-level validation belongs to
          ``supabase db push`` at deploy time and to the optional
          ``sqlfluff`` linter (not yet wired; refinement under this
          contract when added).
        - Does not connect to a database. Pure static analysis.
        - Does not enforce contract-block presence (Layer 1) or perform
          cold-context review (Layer 3). Those layers are enforced
          elsewhere — Layer 1 by authoring discipline at the moment of
          edit; Layer 3 by the session-shutdown sub-agent pass per
          [`session-shutdown-sequence.md`].
        - Does not enforce naming conventions, file ordering, or
          rollback authorship beyond what the four gates above cover.
          Those are Layer 1 + Layer 3 concerns.
    """
    r = ValidationResult()

    if not files:
        r.add_check("sql_gates_empty")
        return r

    r.add_check("sql_gates_transaction_wrap")
    r.add_check("sql_gates_cascade_present")
    r.add_check("sql_gates_rls_enabled")
    r.add_check("sql_gates_enum_checks")

    for f in files:
        rel = str(f.relative_to(REPO_ROOT)) if REPO_ROOT in f.parents else str(f)
        try:
            original_text = f.read_text()
        except OSError as e:
            r.hard_fail(f"{rel}: failed to read file: {e}")
            continue
        cleaned = _strip_sql_line_comments(original_text)

        wrap_fail = _check_transaction_wrap(cleaned, rel)
        if wrap_fail is not None:
            r.hard_fail(wrap_fail)

        for msg in _check_cascade_present(cleaned, rel):
            r.hard_fail(msg)

        for msg in _check_rls_enabled(cleaned, rel):
            r.hard_fail(msg)

        for msg in _check_enum_check_constraints(cleaned, rel, original_text):
            r.hard_fail(msg)

    return r


# ---------------------------------------------------------------------------
# Graph audit extension point (Phase 4+)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Graph audit (Phase 4+, per ADR 0016 + build_readiness/phase_4_graph_validation.md)
# ---------------------------------------------------------------------------

# Env var consumed by validate_graph(); see .env.example for format.
# When unset, the audit skips with a graph_audit_skipped check rather
# than hard-failing — non-seed-authoring sessions are not gated on
# DB connectivity. Set to the service-role pooler URL (gate T1-C);
# service-role bypasses RLS so the audit observes ground truth.
SUPABASE_DB_URL_ENV = "SUPABASE_DB_URL"

# Canonical edge-type registry, parsed at audit time per ADR 0016 +
# gate T2-G. Path is post-S-0024 partition (was supabase/migrations/).
PREDICATE_MANIFEST_PATH = (
    REPO_ROOT / "product" / "seed-graph" / "migrations" / "PREDICATE_MANIFEST.md"
)

# The seven soft-warn categories enumerated by ADR 0016 + gate T2-D.
# Registered in checks_run up-front so cross-session telemetry sees
# "category ran and was clean" distinct from "category did not run."
GRAPH_SOFT_WARN_CATEGORIES = (
    "undeclared_predicate",
    "attribute_shape_inconsistency",
    "missing_rigor_score",
    "render_readiness_violation",
    "synthetic_review_queue",
    "orphan_leaf",
    "suspicious_cross_domain_ratio",
)

# Forbidden tokens for the render_readiness check (gate T2-D, applying
# the ADR 0027 enumeration to node-label authoring).
SCAFFOLDING_TOKENS = ("service_node", "synthetic", "stub")

# Thresholds (gate T2-D). Conservative defaults; T3-C marks the
# attribute-shape threshold for Phase 5 calibration once seed-graph
# distribution becomes observable.
CROSS_DOMAIN_RATIO_THRESHOLD = 0.40
ATTRIBUTE_SHAPE_MINORITY_THRESHOLD = 0.30

# Schema-default rigor_score_computed value (per 0002_nodes.sql:67).
# A node carrying inbound prerequisite edges with rigor still at the
# default is the missing_rigor_score signal.
RIGOR_SCORE_DEFAULT = 0.5

# The structural prerequisite predicate (gate T2-G; per
# 0003_edges.sql:54 column default and architecture.md:182).
PREREQUISITE_EDGE_TYPE = "pedagogical_prerequisite"


def _read_predicate_manifest(
    manifest_path: Path = PREDICATE_MANIFEST_PATH,
) -> set[str]:
    """Parse declared predicates from the PREDICATE_MANIFEST.md registry.

    Reads the ``## Predicate registry`` markdown table and returns the
    set of names from its first column. Backticks and surrounding
    whitespace are stripped; the header row, the dash separator, and
    any placeholder rows (e.g. ``*(none yet)*``) are skipped.

    Inputs:
        manifest_path: absolute path to PREDICATE_MANIFEST.md. Defaults
            to the repo's canonical location.

    Returns:
        Set of declared predicate names. Empty when the file is absent
        or the registry section contains only placeholder rows.

    Non-responsibilities:
        - Does not validate the table's other columns. Schema drift in
          the registry's domain/range/cardinality columns is a docs
          concern caught by manual review, not by this parser.
        - Does not parse the ``## Reserved-but-unused predicates``
          section. Reserved entries are not declared for usage; an
          edge using one would still fire ``undeclared_predicate``.
    """
    if not manifest_path.is_file():
        return set()
    declared: set[str] = set()
    in_registry = False
    for raw in manifest_path.read_text().splitlines():
        if raw.startswith("## Predicate registry"):
            in_registry = True
            continue
        if in_registry and raw.startswith("## "):
            break
        if not in_registry:
            continue
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0].strip().strip("`")
        if not first or first.startswith("---"):
            continue
        if first.lower() == "predicate":
            continue
        if first.startswith("*("):
            continue
        declared.add(first)
    return declared


def _read_graph_from_db(
    connection_string: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Read nodes and edges from the live Supabase DB via psycopg.

    Pure I/O — returns row dicts in encounter order. Tests monkey-patch
    this function with fixture data; callers should not rely on column
    ordering or NULL handling beyond what each row's mapping carries.

    psycopg is imported lazily so the module loads even when the
    dependency is absent (the audit-skip path covers the unset-env
    case without requiring psycopg installation).

    Inputs:
        connection_string: Postgres URL with credentials. Use the
            service-role pooler URL — the audit bypasses RLS to
            observe ground truth (gate T1-C).

    Returns:
        ``(nodes, edges)``. ``nodes`` carry id, label, domain,
        summary, teaching_notes, rigor_score_computed,
        confidence_level, status. ``edges`` carry source_id,
        target_id, edge_type.

    Non-responsibilities:
        - Does not catch psycopg or import errors. The orchestrator
          (validate_graph) wraps this call so failures land as
          hard-fails on the ValidationResult.
        - Does not select archived columns (created_at, updated_at,
          provenance, weight, confidence, evidence). The audit's
          checks consume only the columns above.
    """
    # Lazy imports per module contract — psycopg is optional and absent
    # when SUPABASE_DB_URL is unset (the audit-skip path covers that).
    # The per-line type-ignore guards each statement because mypy may
    # not see the dependency in the current environment; the
    # ImportError branch in validate_graph() handles the actual
    # missing-package case at runtime.
    import psycopg  # type: ignore[import-not-found,unused-ignore]
    from psycopg.rows import dict_row  # type: ignore[import-not-found,unused-ignore]

    with psycopg.connect(connection_string) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, label, domain, summary, teaching_notes, "
                "rigor_score_computed, confidence_level, status "
                "FROM public.nodes"
            )
            nodes = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT source_id, target_id, edge_type FROM public.edges")
            edges = [dict(r) for r in cur.fetchall()]
    return nodes, edges


def _detect_duplicate_node_ids(nodes: list[dict[str, Any]]) -> list[str]:
    """Return ids that appear in ``nodes`` more than once, sorted."""
    seen: dict[str, int] = {}
    for n in nodes:
        nid = n.get("id")
        if nid is None:
            continue
        seen[nid] = seen.get(nid, 0) + 1
    return sorted(nid for nid, count in seen.items() if count > 1)


def _detect_dangling_edges(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> list[tuple[str, str, str]]:
    """Return ``(source_id, target_id, missing_endpoint)`` for each
    edge whose source or target id is not present in ``nodes``.

    ``missing_endpoint`` is ``"source"`` or ``"target"``. When both
    endpoints are absent only the source is reported (the order
    matters less than reporting the existence of the dangling edge).
    """
    node_ids = {n["id"] for n in nodes if n.get("id") is not None}
    dangling: list[tuple[str, str, str]] = []
    for e in edges:
        s = e.get("source_id")
        t = e.get("target_id")
        if s is None or t is None:
            continue
        if s not in node_ids:
            dangling.append((s, t, "source"))
        elif t not in node_ids:
            dangling.append((s, t, "target"))
    return dangling


def _detect_prerequisite_cycles(
    edges: list[dict[str, Any]],
) -> list[list[str]]:
    """Return cycles in the pedagogical_prerequisite-edge subgraph.

    Restricts to edges with ``edge_type == 'pedagogical_prerequisite'``
    (gate T2-A). Other edge types may legitimately cycle (mutual
    historical influence is not a structural error). Implementation
    is iterative Kosaraju SCC plus a self-loop pass; an SCC of size
    > 1 or a singleton with a self-edge constitutes a cycle.

    Each returned cycle is the SCC's node ids in sorted order, for
    deterministic reporting.

    Non-responsibilities:
        - Does not return the cycle's specific edge sequence. The
          ``A -> B -> C -> A`` traversal is recoverable from the SCC
          plus the original edge list; the validator's job is to flag
          the existence of a cycle, not narrate it.
    """
    adj: dict[str, list[str]] = {}
    rev: dict[str, list[str]] = {}
    self_loops: set[str] = set()
    nodes_in_subgraph: set[str] = set()
    for e in edges:
        if e.get("edge_type") != PREREQUISITE_EDGE_TYPE:
            continue
        s = e.get("source_id")
        t = e.get("target_id")
        if s is None or t is None:
            continue
        nodes_in_subgraph.add(s)
        nodes_in_subgraph.add(t)
        adj.setdefault(s, []).append(t)
        adj.setdefault(t, [])
        rev.setdefault(t, []).append(s)
        rev.setdefault(s, [])
        if s == t:
            self_loops.add(s)

    visited: set[str] = set()
    order: list[str] = []
    for start in sorted(nodes_in_subgraph):
        if start in visited:
            continue
        visited.add(start)
        stack: list[tuple[str, Any]] = [(start, iter(adj.get(start, [])))]
        while stack:
            u, it = stack[-1]
            for v in it:
                if v not in visited:
                    visited.add(v)
                    stack.append((v, iter(adj.get(v, []))))
                    break
            else:
                order.append(u)
                stack.pop()

    assigned: set[str] = set()
    components: list[list[str]] = []
    for u in reversed(order):
        if u in assigned:
            continue
        comp: list[str] = []
        comp_stack: list[str] = [u]
        assigned.add(u)
        while comp_stack:
            x = comp_stack.pop()
            comp.append(x)
            for y in rev.get(x, []):
                if y not in assigned:
                    assigned.add(y)
                    comp_stack.append(y)
        components.append(comp)

    cycles: list[list[str]] = []
    for comp in components:
        if len(comp) > 1:
            cycles.append(sorted(comp))
        elif len(comp) == 1 and comp[0] in self_loops:
            cycles.append(list(comp))
    # Stable order on the outer list so disjoint cycles report
    # deterministically across runs and across the two-pass DFS's
    # arbitrary component-emission order.
    cycles.sort()
    return cycles


def _detect_undeclared_predicates(
    edges: list[dict[str, Any]], declared: set[str]
) -> dict[str, int]:
    """Return ``edge_type -> count`` for types not in ``declared``."""
    undeclared: dict[str, int] = {}
    for e in edges:
        et = e.get("edge_type")
        if et is None or et in declared:
            continue
        undeclared[et] = undeclared.get(et, 0) + 1
    return undeclared


def _detect_attribute_shape_inconsistency(
    nodes: list[dict[str, Any]],
    minority_threshold: float = ATTRIBUTE_SHAPE_MINORITY_THRESHOLD,
) -> list[tuple[str, int, int]]:
    """Return ``(domain_tag, populated, null)`` for tags whose
    ``teaching_notes`` mix is more even than ``minority_threshold``.

    A domain tag fires when the smaller of the two classes (populated,
    NULL/empty) exceeds ``minority_threshold`` share of the tag's node
    population — i.e., a real split exists rather than an
    all-or-nothing distribution. Threshold default ``0.30`` (gate T2-D);
    Phase 5 calibration is a T3-C deferral.

    Non-responsibilities:
        - Does not check other attributes. The v1 metric is
          teaching_notes population; future categories (summary
          length variance, aliases coverage) are extensions, not
          this category's scope.
    """
    by_domain: dict[str, list[bool]] = {}
    for n in nodes:
        domain = n.get("domain") or []
        populated = bool(n.get("teaching_notes"))
        for d in domain:
            by_domain.setdefault(d, []).append(populated)

    findings: list[tuple[str, int, int]] = []
    for d, flags in sorted(by_domain.items()):
        total = len(flags)
        if total == 0:
            continue
        populated_count = sum(1 for f in flags if f)
        null_count = total - populated_count
        minority = min(populated_count, null_count)
        if minority / total > minority_threshold:
            findings.append((d, populated_count, null_count))
    return findings


def _detect_missing_rigor_score(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> list[str]:
    """Return ids of nodes with inbound prereq edges and default rigor.

    "Default rigor" means ``rigor_score_computed`` equals
    ``RIGOR_SCORE_DEFAULT`` (0.5, the schema column default per
    0002_nodes.sql:67) or is None. The presence of inbound prereq
    edges is the topology condition under which the architecture.md
    formula at lines 69-77 produces a non-default value.

    Non-responsibilities:
        - Does not compute the actual rigor score. The check fires on
          "could be computed but wasn't"; computing the value is the
          author's job (or a future automation), not the validator's.
    """
    inbound_prereq: set[str] = set()
    for e in edges:
        if e.get("edge_type") != PREREQUISITE_EDGE_TYPE:
            continue
        t = e.get("target_id")
        if t is not None:
            inbound_prereq.add(t)
    findings: list[str] = []
    for n in nodes:
        nid = n.get("id")
        if nid is None or nid not in inbound_prereq:
            continue
        rigor = n.get("rigor_score_computed")
        if rigor is None or rigor == RIGOR_SCORE_DEFAULT:
            findings.append(nid)
    return sorted(findings)


def _detect_render_readiness_violations(
    nodes: list[dict[str, Any]],
) -> list[tuple[str, str, str]]:
    """Return ``(id, label, token)`` for nodes whose label contains a
    forbidden scaffolding token (per ADR 0027 + gate T2-D)."""
    findings: list[tuple[str, str, str]] = []
    for n in nodes:
        nid = n.get("id")
        label = n.get("label")
        if nid is None or label is None:
            continue
        lower = label.lower()
        for token in SCAFFOLDING_TOKENS:
            if token in lower:
                findings.append((nid, label, token))
                break
    return findings


def _detect_synthetic_review_queue(nodes: list[dict[str, Any]]) -> list[str]:
    """Return ids of nodes with ``confidence_level == 'SYNTHETIC'``.

    Per ADR 0030 + self-correction.md, synthetic-confidence nodes
    populate the Opus batch review queue. The category is a counter,
    not a defect — every such node fires.
    """
    return sorted(
        n["id"]
        for n in nodes
        if n.get("confidence_level") == "SYNTHETIC" and n.get("id") is not None
    )


def _detect_orphan_leaves(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> list[str]:
    """Return ids of nodes with zero inbound and zero outbound prereq edges.

    Non-prerequisite edge types (historical_influence, etc.) do not
    count toward in/out degree for this category — gate T2-D is
    explicit on the prerequisite-only restriction.
    """
    has_inbound: set[str] = set()
    has_outbound: set[str] = set()
    for e in edges:
        if e.get("edge_type") != PREREQUISITE_EDGE_TYPE:
            continue
        s = e.get("source_id")
        t = e.get("target_id")
        if s is not None:
            has_outbound.add(s)
        if t is not None:
            has_inbound.add(t)
    findings: list[str] = []
    for n in nodes:
        nid = n.get("id")
        if nid is None:
            continue
        if nid not in has_inbound and nid not in has_outbound:
            findings.append(nid)
    return sorted(findings)


def _detect_suspicious_cross_domain_ratio(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    threshold: float = CROSS_DOMAIN_RATIO_THRESHOLD,
) -> list[tuple[str, int, int]]:
    """Return ``(domain_tag, total_inbound, cross_domain)`` for tags
    whose share of cross-domain inbound prerequisite edges exceeds
    ``threshold``.

    A "cross-domain" inbound edge is one whose source node's
    ``domain[]`` array shares no element with the target tag. The
    aggregation is per target tag — a node carrying multiple domain
    tags contributes its inbound edges to each tag's bucket
    independently.

    Threshold default ``0.40`` (gate T2-D). The signal is "this tag's
    interior is sustained from outside it" — likely a missing service
    node on the inside that those external prerequisites should
    reach instead.
    """
    by_id: dict[str, list[str]] = {
        n["id"]: list(n.get("domain") or []) for n in nodes if n.get("id") is not None
    }

    counts: dict[str, dict[str, int]] = {}
    for e in edges:
        if e.get("edge_type") != PREREQUISITE_EDGE_TYPE:
            continue
        s = e.get("source_id")
        t = e.get("target_id")
        if s is None or t is None or t not in by_id:
            continue
        target_domains = by_id.get(t) or []
        source_domains = by_id.get(s) or []
        for d in target_domains:
            bucket = counts.setdefault(d, {"total": 0, "cross": 0})
            bucket["total"] += 1
            if d not in source_domains:
                bucket["cross"] += 1

    findings: list[tuple[str, int, int]] = []
    for d, c in sorted(counts.items()):
        total = c["total"]
        cross = c["cross"]
        if total > 0 and cross / total > threshold:
            findings.append((d, total, cross))
    return findings


def _write_snapshot(
    snapshot_path: Path,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> None:
    """Write nodes and edges to a JSON snapshot for offline review.

    Per gate T2-F. No row filtering — full dump. ``default=str``
    coerces non-JSON-native types (datetime, UUID) to strings so the
    output is portable to any JSON consumer without a custom decoder.
    Parent directory is created if absent.
    """
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"nodes": nodes, "edges": edges}
    snapshot_path.write_text(
        json.dumps(payload, default=str, indent=2, sort_keys=True) + "\n"
    )


def validate_graph(
    connection_string: str | None = None,
    export_snapshot: Path | None = None,
) -> ValidationResult:
    """Validate the live Supabase graph against ADR 0016's contract.

    Connects to the live Supabase DB via psycopg, runs three hard-fail
    checks (duplicate node IDs, dangling edge references, prerequisite
    cycles via Kosaraju SCC) plus seven soft-warn categories
    (undeclared_predicate, attribute_shape_inconsistency,
    missing_rigor_score, render_readiness_violation,
    synthetic_review_queue, orphan_leaf,
    suspicious_cross_domain_ratio), and returns a categorized result.

    Connection string resolution: the explicit ``connection_string``
    argument wins; otherwise the ``SUPABASE_DB_URL`` environment
    variable is consulted. When neither is set, the audit skips
    cleanly with a ``graph_audit_skipped`` check — non-seed-authoring
    sessions are not gated on DB connectivity. Use the service-role
    pooler URL (gate T1-C); service-role bypasses RLS so the audit
    observes ground truth distinct from anon-filtered views.

    Inputs:
        connection_string: Postgres URL. None falls back to the env
            var; if both are absent the audit is skipped.
        export_snapshot: when set, writes a full nodes-and-edges JSON
            dump to this path and skips the validation checks
            (the ``--export-snapshot`` mode per gate T2-F).

    Returns:
        ValidationResult. Hard-fails populate when structural integrity
        breaks (the three categories above). Soft-warns populate by
        category; every category is registered in ``checks_run`` even
        when it fires zero findings, so cross-session telemetry can
        distinguish "category clean" from "category did not run."
        The ``graph_audit_skipped`` and ``graph_export_snapshot``
        check categories are mutually exclusive paths through this
        function.

    Runtime budget: <3s on the schema-only state per
    [`build_plan/P_2_graph_validation.md:54`]. Phase 5 seed content
    will grow the budget; the per-check structure (set membership,
    single-pass aggregation, iterative Kosaraju) keeps the validator
    linear in nodes + edges.

    Non-responsibilities:
        - Does not write back to the DB. DB writes happen via Supabase
          migrations only; the audit is read-only.
        - Does not enforce sub-signal NULL discipline on
          ``learner_events``. That contract lives at the SQL CHECK
          layer per gate T2-B; ``validate_graph()`` operates on
          nodes and edges only.
        - Does not validate enum values on node columns
          (confidence_level, status). The CHECK constraints at the
          SQL layer cannot be violated post-insert without bypassing
          the schema; this validator does not duplicate that work.
        - Does not run any check against ``edges`` that the schema's
          FK constraint already prevents at insert time (the dangling
          check runs anyway as defense-in-depth, covering any
          post-restore window before constraints are validated; gate
          T2-C).
    """
    r = ValidationResult()

    conn_str = connection_string or os.environ.get(SUPABASE_DB_URL_ENV)
    if not conn_str:
        r.add_check("graph_audit_skipped")
        return r

    try:
        nodes, edges = _read_graph_from_db(conn_str)
    except ImportError as exc:
        r.add_check("graph_audit")
        r.hard_fail(
            f"graph_audit: psycopg import failed ({exc!s}); "
            f"run `pip install -r engine/tools/requirements.txt`"
        )
        return r
    except Exception as exc:  # noqa: BLE001  (psycopg connect/query errors)
        r.add_check("graph_audit")
        r.hard_fail(
            f"graph_audit: DB connection or query failed "
            f"({type(exc).__name__}: {exc!s})"
        )
        return r

    if export_snapshot is not None:
        _write_snapshot(export_snapshot, nodes, edges)
        r.add_check("graph_export_snapshot")
        return r

    r.add_check("graph_audit")

    for nid in _detect_duplicate_node_ids(nodes):
        r.hard_fail(f"duplicate_node_id: {nid}")

    for s, t, missing in _detect_dangling_edges(nodes, edges):
        r.hard_fail(f"dangling_edge: source={s!r} target={t!r} (missing {missing})")

    for cycle in _detect_prerequisite_cycles(edges):
        r.hard_fail(f"prerequisite_cycle: [{', '.join(cycle)}]")

    # Register every soft-warn category in checks_run up-front. A
    # category that fires zero findings should still appear in the
    # check log so cross-session telemetry distinguishes "ran clean"
    # from "did not run" (the schema convention at
    # session-shutdown-sequence.md "outcome_summary_soft_warns").
    for cat in GRAPH_SOFT_WARN_CATEGORIES:
        r.add_check(cat)

    declared = _read_predicate_manifest()
    for et, count in sorted(_detect_undeclared_predicates(edges, declared).items()):
        r.soft_warn(
            "undeclared_predicate",
            f"edge_type={et!r} (count={count})",
        )

    for d, pop, null in _detect_attribute_shape_inconsistency(nodes):
        r.soft_warn(
            "attribute_shape_inconsistency",
            f"domain={d!r} teaching_notes_populated={pop} null={null}",
        )

    for nid in _detect_missing_rigor_score(nodes, edges):
        r.soft_warn("missing_rigor_score", f"node_id={nid!r}")

    for nid, label, token in _detect_render_readiness_violations(nodes):
        r.soft_warn(
            "render_readiness_violation",
            f"node_id={nid!r} label={label!r} token={token!r}",
        )

    for nid in _detect_synthetic_review_queue(nodes):
        r.soft_warn("synthetic_review_queue", f"node_id={nid!r}")

    for nid in _detect_orphan_leaves(nodes, edges):
        r.soft_warn("orphan_leaf", f"node_id={nid!r}")

    for d, total, cross in _detect_suspicious_cross_domain_ratio(nodes, edges):
        r.soft_warn(
            "suspicious_cross_domain_ratio",
            f"domain={d!r} total_inbound={total} cross_domain={cross}",
        )

    return r


# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------


def session_id_from_current() -> str:
    """Return the in-progress session id, or 'outside-session' if none.

    Reads engine/session/current.json. The file exists only between an
    eager-claim ritual's commit and the matching session-shutdown archive,
    so absence is the normal case for invocations between sessions.

    Returns:
        ``"S-NNNN"`` when current.json exists and has an ``id`` field;
        ``"outside-session"`` when the file is absent, malformed, or
        lacks an id. Never raises — telemetry is best-effort.
    """
    current_path = REPO_ROOT / "engine" / "session" / "current.json"
    if not current_path.is_file():
        return "outside-session"
    try:
        current = json.loads(current_path.read_text())
        return str(current.get("id", "outside-session"))
    except json.JSONDecodeError:
        return "outside-session"


def append_history(record: dict[str, Any]) -> None:
    """Append a JSONL telemetry record to engine/tools/validate-history.jsonl.

    Best-effort: never raises. The file is gitignored (per .gitignore's
    ``engine/tools/validate-history.jsonl`` rule); telemetry is per-clone,
    not committed. ADR 0022 health checks consume the file for trend analysis.

    Inputs:
        record: dict serializable to JSON. Caller is responsible for shape;
            health-check telemetry expects keys ``timestamp``, ``session_id``,
            ``checks_run``, ``hard_fails``, ``soft_warns``, ``duration_ms``.

    Side effect:
        Creates the parent directory if absent (mkdir parents=True). Appends
        a single line ``json.dumps(record, separators=(",", ":")) + "\\n"``.
        File-system errors are swallowed (OSError caught) so a failed
        telemetry write never poisons a validate run.

    Non-responsibilities:
        - Does not rotate the JSONL file. Health checks are responsible for
          summarization and pruning.
        - Does not validate the record shape.
    """
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with HISTORY_FILE.open("a") as f:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns the process exit code (0/1/2).

    Four invocation modes are mutually exclusive:

    - **Default (no flags)**: run validate_repo_structure +
      validate_shared_state_health + validate_graph. Aggregates
      results, prints summary to stdout, details to stderr, appends
      telemetry to the JSONL log.
    - **--code-gates --files <path>...**: run validate_code_gates
      against the named files. Useful for pre-commit hook integration
      where the hook passes the staged Python files. Skips
      repo-structure, shared-state-health, and graph checks; the
      structure run is invoked separately by the hook.
    - **--sql-gates --files <path>...**: run validate_sql_gates
      against the named SQL files. Useful for pre-commit hook
      integration where the hook passes staged migration files under
      product/seed-graph/migrations/. Mutually exclusive with
      --code-gates.
    - **--health-probe-only**: run only validate_shared_state_health.
      Used by the SessionStart hook for sub-second boot-time
      verification. Mutually exclusive with the gate flags.

    Inputs:
        argv: optional argument list (for testability). When None, falls
            back to sys.argv[1:].

    Returns:
        Process exit code. 0 = clean, 1 = soft-warn only, 2 = hard-fail.

    Non-responsibilities:
        - Does not enforce mutual exclusion between --code-gates and
          --sql-gates beyond the dispatch precedence (--code-gates wins
          if both are set; the pre-commit hook invokes them in
          separate calls and never sets both). --health-probe-only
          overrides both gate flags when present (the probe is fast
          enough that any concurrent invocation is the caller's bug).
    """
    parser = argparse.ArgumentParser(
        description="Paideia repo-structure validator and code/SQL gate runner",
    )
    parser.add_argument(
        "--code-gates",
        action="store_true",
        help="Run code-discipline gates (ruff, mypy, pytest) instead of "
        "the default repo-structure + graph stub run.",
    )
    parser.add_argument(
        "--sql-gates",
        action="store_true",
        help="Run SQL-discipline gates (transaction wrap, CASCADE, RLS, "
        "enum CHECK) instead of the default run. Mutually exclusive with "
        "--code-gates.",
    )
    parser.add_argument(
        "--health-probe-only",
        action="store_true",
        help="Run only the shared-state health probes (chromadb palace + "
        "repo config). Used by the SessionStart hook for sub-second "
        "boot-time verification. Mutually exclusive with gate flags.",
    )
    parser.add_argument(
        "--export-snapshot",
        type=Path,
        default=None,
        metavar="PATH",
        help="Write a JSON snapshot of the live graph (nodes + edges) to "
        "PATH and exit. Per gate T2-F. Mutually exclusive with gate "
        "and probe flags; requires SUPABASE_DB_URL set in the env.",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        type=Path,
        default=[],
        help="Files to pass to --code-gates or --sql-gates. Required when "
        "either gate flag is set.",
    )
    args = parser.parse_args(argv)

    start = time.monotonic()
    overall = ValidationResult()

    if args.health_probe_only:
        overall.merge(validate_shared_state_health())
    elif args.code_gates:
        overall.merge(validate_code_gates(args.files))
    elif args.sql_gates:
        overall.merge(validate_sql_gates(args.files))
    elif args.export_snapshot is not None:
        overall.merge(validate_graph(export_snapshot=args.export_snapshot))
    else:
        overall.merge(validate_repo_structure())
        overall.merge(validate_shared_state_health())
        overall.merge(validate_issue_collisions())
        overall.merge(validate_scope_discipline())
        overall.merge(validate_routine_mode())
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
