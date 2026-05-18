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
the git repo + session-dir probes — added at S-0035 to catch silent
corruption of cross-session shared state at the moment a session
boots or a commit is attempted, rather than letting it persist until
the next session reads. See validate_shared_state_health().

Invariants this module preserves:

- Read-only with respect to the repo. The validator never modifies tracked
  files. Only writes are to engine/tools/validate-history.jsonl (telemetry,
  appended) and to stdout/stderr (the run's report).
- Deterministic for a given working tree. Two runs against the same tree
  produce the same checks_run list, hard_fails, and soft_warns categories.
  Telemetry rows differ in timestamp and the three duration fields
  (``duration_structural_ms`` / ``duration_graph_audit_ms`` /
  ``duration_total_ms``) only.
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
      "duration_structural_ms": float,
      "duration_graph_audit_ms": float,
      "duration_total_ms": float
    }

The per-phase fields land at S-0126 per ADR 0063: structural-phase checks
are in-process (no DB) and target < 500ms; the graph-audit phase consults
the live DB per ADR 0016 and targets < 5s; total runtime targets < 6s. The
``validator_runtime_phase_regression`` soft-warn fires when any phase
exceeds 1.5x its tiered target across 3 consecutive runs. Pre-S-0126
entries carry the prior ``duration_ms`` field instead; the regression
check skips entries lacking the per-phase fields. Health checks per ADR
0022 consume this JSONL for trend analysis.

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
        Run only the shared-state health probes (git repo + session
        dir) without the structure or graph checks. Used by the
        SessionStart hook for sub-second boot-time verification.
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
  via :mod:`scrub_env`, git repo + session-dir probes are wired through
  validate_shared_state_health(); pre-commit subprocesses (ruff, mypy,
  pytest) pass scrubbed envs to prevent the S-0033 GIT_DIR-leak vector.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple

# Local helpers at engine/tools/{scrub_env,_venv_reexec}.py — ADR 0045 / Issue #14.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv_reexec import ensure_venv_python  # noqa: E402

# Re-exec under venv only when invoked as a script. Calling
# ``ensure_venv_python()`` at module-import time meant pytest's collection
# of ``test_validate.py`` triggered a mid-process ``os.execv`` to the venv
# python — which the harness's bash output capture cannot follow (the
# replacement process inherits the FDs but the wrapper has already detached
# the read end on the original process). Symptom: pytest engine/tools
# reports "collecting ..." and exits with no test output, looking like a
# silent hang. Direct invocations (``python3 engine/tools/validate.py``)
# still re-exec via the ``__main__`` branch below — discovered at S-0190
# while debugging the engine/tools regression "hang" that was actually
# successful tests with invisible output.
if __name__ == "__main__":
    ensure_venv_python()

from scrub_env import scrubbed_env  # noqa: E402
from timestamps import emit_micros  # noqa: E402  # ADR 0058


# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------

# Validator lives at engine/tools/validate.py post-S-0024 migration; REPO_ROOT
# walks three levels up (validate.py → tools/ → engine/ → repo root). REPO_ROOT
# resolves to the ACTIVE clone (worktree or main repo) and is used for
# repo-internal path resolution (STATE.md, required files, etc.) where the
# active-clone perspective is correct.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_canonical_history_path(cwd: Path | None = None) -> Path:
    """Resolve the validate-history.jsonl path to the canonical main-repo location.

    Per ADR 0063 Consequences amendment (S-0205, Issue #150): the regression-check
    input is a single time-series of runs across the project's actual validate
    activity, not per-clone activity. Each worktree has its own checkout of
    validate.py, so `Path(__file__).resolve().parent.parent.parent` resolves to
    the worktree's root — per-clone HISTORY_FILE resolution fragments the time
    series and structurally defeats `validate_runtime_phase_regression()`.

    Resolution: ``git rev-parse --git-common-dir`` returns ``<main-repo>/.git``
    from any worktree or from the main repo itself. The main-repo root is the
    parent of that ``.git`` directory; the canonical history path is
    ``<main-repo>/engine/tools/validate-history.jsonl``.

    Concurrent-write safety: JSONL records are ~250-1000 bytes; POSIX guarantees
    atomic append for writes ≤ PIPE_BUF (4KB) on local filesystems, so
    concurrent sessions appending to the canonical file do not interleave at
    the byte level.

    Falls back to the per-clone path (``cwd`` or REPO_ROOT-relative) on any
    subprocess failure — covers running outside a git repo (tarball extraction,
    test harness with no git fixture, etc.).

    Inputs:
        cwd: optional working directory for the ``git rev-parse`` subprocess.
            Defaults to ``REPO_ROOT`` (the active clone's root). Tests pass
            tmp-fixture paths.
    """
    base = cwd if cwd is not None else REPO_ROOT
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=base,
            env=scrubbed_env(),
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            common_dir = Path(proc.stdout.strip())
            # `git rev-parse --git-common-dir` returns <main-repo>/.git from any
            # worktree (or from the main repo itself). The parent of the .git
            # directory is the main-repo root.
            main_repo = common_dir.parent if common_dir.name == ".git" else common_dir
            return main_repo / "engine" / "tools" / "validate-history.jsonl"
    except (OSError, subprocess.TimeoutExpired):
        pass
    # Fallback: per-clone path (pre-fix behavior). Defensive — never raises;
    # telemetry is best-effort.
    return base / "engine" / "tools" / "validate-history.jsonl"


HISTORY_FILE = _resolve_canonical_history_path()

REQUIRED_TOP_LEVEL = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "ROADMAP.md",
    "HANDOFF.md",
    "CLAUDE.md",
]

# Engine-side required files (post-S-0024 migration per ADR 0037; ENGINE_LOG.md
# retired at S-0198 per ADR 0092 — replaced with the engine/changelog/ directory
# pattern whose README is the new foundation surface).
REQUIRED_ENGINE_FILES = [
    "engine/STATE.md",
    "engine/changelog/README.md",
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
# native segfault (the S-0034 vector pattern) terminates the probe
# process at exit code 139 rather than crashing the validator. The
# wrapper treats 139 as hard-broken. engine_memory uses
# ``engine.memory.connection.healthcheck()`` invoked on first connect
# (no boot-time subprocess) — its integrity check is in-process.
PROBE_REPO = REPO_ROOT / "engine" / "tools" / "probe_repo.py"
PROBE_SESSION_DIR = REPO_ROOT / "engine" / "tools" / "probe_session_dir.py"

# Issue-collisions scanner (per ADR 0048). Surfaces open GitHub Issues
# whose body or title contains keywords from this session's
# declared_scope or paths from the staged commit. Best-effort — gh
# failure (no auth, no network, repo not on GitHub) is silently skipped.
SCAN_ISSUE_COLLISIONS = REPO_ROOT / "engine" / "tools" / "scan_issue_collisions.py"

# Session register (per ADR 0048). Some validator checks read
# configuration from here at runtime — primarily the health-check
# cadence. Authoritative source for the session-counter state.
REGISTER_STATE_PATH = REPO_ROOT / "engine" / "session" / "register_state.json"


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
      engine/changelog/README.md). Hard-fail on missing.
    - session_register, session_current: JSON schema checks on
      engine/session/register_state.json (always present) and
      engine/session/current.json (only between eager-claim and archive).
      Hard-fail on missing required keys, malformed JSON, or non-S-NNNN id.
    - state_current_phase: lightweight format check on STATE.md (has
      "Current phase" field). Soft-warn on absence — file may be mid-edit.
    - changelog_entries, changelog_readme_governance: per-session changelog
      entry schema + line-cap validation; governance README line-cap. Per
      ADR 0092.
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

    # engine/ENGINE_LOG.md format check retired at S-0198 per ADR 0092 — the
    # monolithic file moved to engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md;
    # new content lands as per-session entries at engine/changelog/<YYYY>/.
    # The changelog_entries + changelog_readme_governance checks (below) are
    # the replacement enforcement surface.

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
    r.merge(validate_duplicate_adr_number())

    return r


# ---------------------------------------------------------------------------
# Shared-state health probes (post-S-0035 per ADR 0045)
# ---------------------------------------------------------------------------


def validate_shared_state_health() -> ValidationResult:
    """Run the shared-state health probes; return the result.

    Each probe runs as a subprocess so a native segfault (the S-0034
    vector pattern) terminates the probe process at exit code 139
    instead of crashing the validator itself. Exit-code interpretation:

    - 0: probe healthy. No record beyond ``add_check``.
    - 1: probe suspect. Recorded as soft-warn under the probe's
      category (``repo_config_health`` etc.). The probe's stderr is
      the soft-warn body.
    - 2: probe hard-broken. Recorded as hard-fail; validator exits 2.
    - 139 (SIGSEGV): treated as hard-broken.

    Probe scripts:

    - ``engine/tools/probe_repo.py`` — checks effective ``core.bare``,
      parent-clone direct ``core.bare``, and HEAD resolution.
    - ``engine/tools/probe_session_dir.py`` — scans the parent repo's
      ``engine/session/`` for stray files matching the macOS Finder /
      iCloud-sync duplicate pattern (``current N.json``). Per Issue #57.

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
        (PROBE_REPO, "repo_config_health", "repo"),
        (PROBE_SESSION_DIR, "session_dir_strays", "session_dir"),
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

        # engine_memory's SQLite + FTS5 substrate has its integrity
        # check at connect time via ``healthcheck()`` (per ADR 0091) —
        # no boot-time subprocess surface here. The probe loop covers
        # repo + session-dir integrity only.

        if proc.returncode == 0:
            continue
        if proc.returncode == 1:
            r.soft_warn(category, body)
        elif proc.returncode == 2:
            r.hard_fail(f"{probe_name} probe hard-broken:\n{body}")
        elif proc.returncode == 139:
            r.hard_fail(
                f"{probe_name} probe segfaulted (SIGSEGV); treating as "
                f"hard-broken.\n{body}"
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
      holding an empty string AND the session is running in routine
      mode (``current.json.mode == "routine"``). Skipped silently when
      current.json itself is absent (exploration mode) OR when the
      session is non-routine (interactive build sessions don't require
      declared_scope per ADR 0049 §Routine-mode scope-lock; the field
      is a routine-mode contract surface). Gate added at S-0125 per
      S-0121 audit Retire-F.
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
    mode = data.get("mode")
    if not isinstance(scope, str) or not scope.strip():
        if mode == "routine":
            r.soft_warn(
                "empty_declared_scope",
                "current.json has no declared_scope field; per ADR 0049 "
                "the routine-mode eager-claim ritual must write this field "
                "as a 1-3 sentence statement of what the session commits "
                "to deliver.",
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
    id and greps tracked .md files (excluding ADR files themselves, the
    legacy ENGINE_LOG.md / product/CHANGELOG.md filenames, and the
    engine/changelog/ directory per ADR 0092). Soft-warns on any citation of
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
        # Skip the changelog surfaces (their job is historical narration).
        # Pre-ADR 0092: ENGINE_LOG.md was a single file; the legacy match
        # stays as defense-in-depth in case the file resurfaces (e.g., during
        # the cutover-window). Post-ADR 0092: per-session entries live at
        # engine/changelog/<YYYY>/, and the historical archive at
        # engine/changelog/_history/ — directory-prefix exclusion covers both.
        if rel.name in {"ENGINE_LOG.md", "CHANGELOG.md"}:
            continue
        if rel.parts[:2] == ("engine", "changelog"):
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
    """Soft-warn on Accepted or Deprecated ADRs with no inbound citation outside their subtree.

    For each ADR with Status `Accepted` or `Deprecated`, greps tracked .md
    files outside `*/adr/*` for the ADR's id. Soft-warns when zero matches
    found, unless the ADR carries an `Orphan-OK` annotation.

    Per ADR 0041 / cascade-discipline.md. Deprecated coverage added at
    S-0139 per ADR 0077 — a decision-record that records why an approach
    was abandoned is just as load-bearing as one that records an active
    contract; both should be cited by something downstream rather than
    silently rot.

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

    eligible_status = re.compile(
        r"^[\s*\-]*Status[\s*]*:[\s*]*(Accepted|Deprecated)\b",
        re.MULTILINE | re.IGNORECASE,
    )

    md_files = _tracked_md_files(exclude_dirs=[])
    non_adr_md = [p for p in md_files if "adr" not in p.relative_to(REPO_ROOT).parts]

    # Inverted-index pre-scan per S-0151 Issue #116. Pre-S-0151 the inner
    # loop ran two regex searches per (ADR, md-file) pair — ~25,000
    # regex searches at the S-0146 corpus size (85 ADRs × ~300 non-ADR md
    # files), dominating the structural phase at ~376ms median. The
    # citation patterns "ADR NNNN" and "NNNN-*.md" both have the
    # 4-digit-id as a capture group, so a single pre-scan of every non-ADR
    # md file extracts the union of cited IDs into a set; the per-ADR
    # check then becomes O(1) set membership. ~2.4× speedup vs the
    # cache-only variant per the /tmp/probe_inverted_index_S0151.py
    # empirical measurement (170ms median vs 407ms). Output is byte-identical
    # to the pre-S-0151 pairwise-regex version per the same probe's
    # equivalence check.
    citation_pattern = re.compile(r"ADR\s+(\d{4})\b|\b(\d{4})-[\w-]+\.md")
    cited_ids: set[str] = set()
    for md_path in non_adr_md:
        try:
            md_text = md_path.read_text()
        except OSError:
            continue
        for m in citation_pattern.finditer(md_text):
            adr_id = m.group(1) or m.group(2)
            if adr_id:
                cited_ids.add(adr_id)

    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if not adr_dir.is_dir():
            continue
        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            text = adr_file.read_text()
            if not eligible_status.search(text):
                continue
            if _has_orphan_ok_annotation(text):
                continue
            adr_id = adr_file.name[:4]
            if adr_id not in cited_ids:
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


def validate_duplicate_adr_number() -> ValidationResult:
    """Soft-warn on any ADR number appearing in both engine/adr and product/adr.

    Per ADR 0037 the engine/product partition shares a single ADR numbering
    sequence — numbers must not duplicate across the partition. The pre-S-0149
    state carried a collision at slot 0052 (engine 0052 + product 0052) per
    Issue #91; the renumber at S-0149 closed it. This check is defense-in-depth
    against recurrence — author-time mistakes in either partition surface here
    at structural-phase validate time rather than via post-hoc audit.

    Returns:
        ValidationResult with check ``cascade_duplicate_adr_number`` recorded
        and soft-warns under category ``duplicate_adr_number``.

    Non-responsibilities:
        - Does not handle the case of two engine ADRs or two product ADRs
          sharing a number (within-partition); a file-system glob would
          fail to write the second file with the same name.
        - Does not propose a renumber. Reports the collision and exits.
    """
    r = ValidationResult()
    r.add_check("cascade_duplicate_adr_number")

    engine_numbers: dict[str, Path] = {}
    if ENGINE_ADR_DIR.is_dir():
        for adr in sorted(ENGINE_ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md")):
            engine_numbers[adr.name[:4]] = adr

    product_numbers: dict[str, Path] = {}
    if PRODUCT_ADR_DIR.is_dir():
        for adr in sorted(PRODUCT_ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md")):
            product_numbers[adr.name[:4]] = adr

    for num in sorted(set(engine_numbers) & set(product_numbers)):
        engine_rel = engine_numbers[num].relative_to(REPO_ROOT)
        product_rel = product_numbers[num].relative_to(REPO_ROOT)
        r.soft_warn(
            "duplicate_adr_number",
            f"ADR number {num} appears in both partitions — {engine_rel} and "
            f"{product_rel}. Per ADR 0037 the sequence is shared; renumber one "
            f"per engine/operations/cascade-discipline.md procedure.",
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

# Path-aware graph-audit skip (Issue #142). Pre-commit invocations of
# validate.py inherit SUPABASE_DB_URL from the walk-up loader (ADR 0049)
# regardless of whether the staged change actually touches the graph.
# When pgbouncer is paused or under load, psycopg.connect() can hang
# inside psycopg.wait_c past the connect_timeout in ways the S-0186
# fix did not cover (transaction-pool URL strips session-level
# options=-c statement_timeout=...). The cheapest mitigation per the
# Issue's three-direction analysis is to bypass connection entirely
# when no staged path is graph-affecting. The set below is conservative:
# the migrations directory (where seed authoring lives), the validator
# itself (changes to audit logic warrant a re-run), and the migration
# apply wrapper (changes to the apply path warrant a re-run). Manual
# (non-pre-commit) invocations of validate.py are not affected — the
# path-aware skip only fires when staged paths are inspectable and
# none intersect this prefix set.
GRAPH_AFFECTING_PATH_PREFIXES = (
    "product/seed-graph/migrations/",
    "engine/tools/validate.py",
    "engine/tools/apply_migration.py",
)

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
    # S-0146: three soft-warns from the S-0122 Phase 5 production-audit
    # closeout (Issue #62; per engine/build_readiness/phase_5_audit_system_input.md
    # Proposals 1, 2b, 3+5 merged). Proposal 4 (historical_node_as_prereq_source)
    # awaits node-class schema extension — tracked separately.
    "edge_evidence_empty",
    "top_level_discipline_label_as_prereq_source",
    "prereq_direction_summary_inconsistency",
)

# Canonical top-level discipline labels for the
# top_level_discipline_label_as_prereq_source soft-warn (Issue #62
# Proposal 2b; per engine/build_readiness/phase_5_audit_system_input.md:48).
# A node whose label is in this set, sources >=3 prereq edges, and whose
# targets span >=2 distinct domains is the umbrella-as-prereq-source pattern.
TOP_LEVEL_DISCIPLINE_LABELS: frozenset[str] = frozenset(
    {
        "philosophy_of_language",
        "philosophy_of_science",
        "philosophy_of_mind",
        "political_philosophy",
        "metaethics",
        "epistemology",
        "metaphysics",
        "ethics",
        "logic",
        "aesthetics",
    }
)

# Connecting-phrase patterns for prereq_direction_summary_inconsistency
# (Issue #62 Proposal 3+5 merged; per audit input doc:64-67). Anchored
# on the 5 documented cross-bridge reversal cases (CB-E-47, CB-E-63,
# CB-E-65, CB-E-69, CB-E-70). These appear between target.label and
# source.label in the target's summary when the edge direction is
# semantically reversed (the target depends on the source per the
# summary's own structural prose).
DIRECTION_REVERSAL_PHRASES: tuple[str, ...] = (
    "the broader",  # CB-E-70: "morality is the broader normative framework"
    "the contents of",  # CB-E-63: "propositions are the contents of propositional attitudes"
    "the content of",
    "an instance of",
    "a kind of",
    "a type of",
    "a form of",
    "a special case of",
    "applied to",
    "a property of",
    "the class of",
    "the category of",
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


# S-0187: client-side wall-clock cap for the whole _read_graph_from_db()
# block. The server-side ``options="-c statement_timeout=30000"``
# parameter S-0186 set is silently stripped by Supabase's pgbouncer
# pooler in transaction-pool mode — pgbouncer only forwards
# session-level parameters that arrive on a fresh session connection,
# and the project's SUPABASE_DB_URL is the transaction-pool URL.
# Empirical evidence: S-0187 boot observed an 8+ minute hang on
# validate.py's pre-commit-hook run with the connection's TCP socket
# transitioning from ESTABLISHED to gone (the connect AND the queries
# both completed at some level) yet the process still hung — the
# downstream behavior is consistent with statement_timeout never
# firing server-side and the client waiting on an idle socket.
# 45 s = server-side 30 s budget + connect 10 s + 5 s margin.
_GRAPH_AUDIT_WALL_CLOCK_TIMEOUT_S = 45.0


def _read_graph_from_db(
    connection_string: str,
    *,
    wall_clock_timeout_s: float = _GRAPH_AUDIT_WALL_CLOCK_TIMEOUT_S,
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
        wall_clock_timeout_s: client-side total-wall-clock cap on the
            connect + query block (S-0187). Default
            ``_GRAPH_AUDIT_WALL_CLOCK_TIMEOUT_S`` (45 s). Tests pass a
            small value to exercise the cancellation path.

    Returns:
        ``(nodes, edges)``. ``nodes`` carry id, label, domain,
        summary, teaching_notes, rigor_score_computed,
        confidence_level, status. ``edges`` carry id, source_id,
        target_id, edge_type, evidence.

    Non-responsibilities:
        - Does not catch psycopg or import errors. The orchestrator
          (validate_graph) wraps this call so failures land as
          hard-fails on the ValidationResult.
        - Does not select archived columns (created_at, updated_at,
          provenance, weight, confidence). The audit's checks consume
          only the columns above.
    """
    # Lazy imports per module contract — psycopg is optional and absent
    # when SUPABASE_DB_URL is unset (the audit-skip path covers that).
    # The per-line type-ignore guards each statement because mypy may
    # not see the dependency in the current environment; the
    # ImportError branch in validate_graph() handles the actual
    # missing-package case at runtime.
    import psycopg  # type: ignore[import-not-found,unused-ignore]
    from psycopg.rows import dict_row  # type: ignore[import-not-found,unused-ignore]

    # Three layers of cap (S-0184/0185/0186/0187):
    #   1. ``connect_timeout=10`` — bounds the initial connect phase.
    #   2. ``options="-c statement_timeout=30000"`` — server-side cap,
    #      EFFECTIVE ONLY on direct-connection URLs. The Supabase
    #      transaction-pool URL strips this parameter silently; on
    #      that URL the layer is inert. Retained as a no-cost
    #      defense-in-depth for direct-connection URLs.
    #   3. ``wall_clock_timeout_s`` (S-0187) — client-side watchdog
    #      thread that calls ``conn.cancel()`` (PQcancel; protocol-
    #      level query termination) if total time in the block
    #      exceeds the cap. Layer 3 is the load-bearing protection
    #      against Supabase pgbouncer's parameter-stripping.
    with psycopg.connect(
        connection_string,
        connect_timeout=10,
        options="-c statement_timeout=30000",
    ) as conn:
        done = threading.Event()

        def _watchdog() -> None:
            # Block up to wall_clock_timeout_s. ``done`` is set when
            # the queries return cleanly; an unset event after the
            # wait means the queries are still in flight beyond the
            # cap. ``conn.cancel()`` issues PQcancel which terminates
            # the in-flight query at the protocol level — psycopg
            # raises ``psycopg.errors.QueryCanceled`` (a subclass of
            # ``Exception``) from the blocked ``cur.execute()`` /
            # ``cur.fetchall()`` call, which bubbles up to
            # ``validate_graph()``'s ``except Exception`` and lands
            # as a ``graph_audit`` hard-fail with the cancellation
            # message.
            if not done.wait(wall_clock_timeout_s):
                try:
                    conn.cancel()
                except Exception:  # noqa: BLE001  # daemon thread; swallow
                    # Failure in the watchdog is best-effort — the
                    # primary path either succeeds (cap not hit) or
                    # the query is already in some other terminal
                    # state. Errors here can't bubble back to the
                    # caller without joining the thread, which
                    # would defeat the watchdog's purpose.
                    pass

        watcher = threading.Thread(
            target=_watchdog, name="validate-graph-audit-watchdog", daemon=True
        )
        watcher.start()
        try:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT id, label, domain, summary, teaching_notes, "
                    "rigor_score_computed, confidence_level, status "
                    "FROM public.nodes"
                )
                nodes = [dict(r) for r in cur.fetchall()]
                cur.execute(
                    "SELECT id, source_id, target_id, edge_type, evidence FROM public.edges"
                )
                edges = [dict(r) for r in cur.fetchall()]
        finally:
            done.set()
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


def _detect_edge_evidence_empty(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> list[tuple[str, str, str]]:
    """Return ``(edge_id, source_id, target_id)`` for cross-domain
    pedagogical-prerequisite edges whose ``evidence`` field is NULL or
    empty.

    Per Issue #62 Proposal 1 (S-0122 audit input doc:7-23). Empirical
    basis: the ``evidence`` field on ``pedagogical_prerequisite_edge``
    is universally NULL across all 536 Phase 5 edges. The 5
    contradicted-by-own-prose reversals (CB-E-47, CB-E-63, CB-E-65,
    CB-E-69, CB-E-70) all had pedagogical-warrant prose in the
    migration's ``teaching_notes`` that argued the opposite direction
    from the authored edge — visible at authoring time if the
    ``evidence`` field had been populated.

    Cross-bridges only: within-subdomain edges run cleaner (5.0–21.0%
    defect rate vs 35.2% for cross-bridges) and their pedagogical
    justification is often implicit in the parent migration's
    narrative. The high-value population for evidence-field discipline
    is cross-bridges where rationale benefits from explicit recording.
    """
    by_id: dict[str, list[str]] = {
        n["id"]: list(n.get("domain") or []) for n in nodes if n.get("id") is not None
    }
    findings: list[tuple[str, str, str]] = []
    for e in edges:
        if e.get("edge_type") != PREREQUISITE_EDGE_TYPE:
            continue
        s = e.get("source_id")
        t = e.get("target_id")
        if s is None or t is None:
            continue
        source_domains = set(by_id.get(s) or [])
        target_domains = set(by_id.get(t) or [])
        if source_domains and target_domains and source_domains & target_domains:
            continue
        evidence = e.get("evidence")
        if evidence is not None and str(evidence).strip() != "":
            continue
        eid = e.get("id")
        findings.append((str(eid) if eid is not None else "", str(s), str(t)))
    return sorted(findings)


def _detect_top_level_discipline_label_as_prereq_source(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    canonical_labels: frozenset[str] = TOP_LEVEL_DISCIPLINE_LABELS,
    min_prereq_count: int = 3,
    min_distinct_target_domains: int = 2,
) -> list[tuple[str, str, int, int]]:
    """Return ``(node_id, label, prereq_count, distinct_target_domains)``
    for nodes whose label matches a canonical top-level discipline name
    AND that source >=``min_prereq_count`` prerequisite edges AND whose
    targets span >=``min_distinct_target_domains`` distinct domains.

    Per Issue #62 Proposal 2b (S-0122 audit input doc:40-58). Empirical
    basis: 3 corpus instances (philosophy_of_language, philosophy_of_science,
    political_philosophy) where a top-level discipline label sources
    foundation-spine prereq edges to its field's central topics — the
    "umbrella-as-prereq-source" shape. The fix posture per closeout is
    retain-with-explicit-umbrella-semantics; the soft-warn surfaces the
    pattern at validate time so authoring sessions record the umbrella
    framing in the node's ``teaching_notes``.

    The ``min_distinct_target_domains>=2`` predicate uses the targets'
    ``domain`` field cardinality to discriminate the foundation-spine
    fan-out shape from a single internal-coherence prereq (which is not
    the problem shape).
    """
    label_by_id: dict[str, str | None] = {
        n["id"]: n.get("label") for n in nodes if n.get("id") is not None
    }
    domains_by_id: dict[str, set[str]] = {
        n["id"]: set(n.get("domain") or []) for n in nodes if n.get("id") is not None
    }

    prereq_targets_by_source: dict[str, list[str]] = {}
    for e in edges:
        if e.get("edge_type") != PREREQUISITE_EDGE_TYPE:
            continue
        s = e.get("source_id")
        t = e.get("target_id")
        if s is None or t is None:
            continue
        prereq_targets_by_source.setdefault(s, []).append(t)

    findings: list[tuple[str, str, int, int]] = []
    for nid, label in label_by_id.items():
        if label is None or label not in canonical_labels:
            continue
        targets = prereq_targets_by_source.get(nid, [])
        if len(targets) < min_prereq_count:
            continue
        target_domain_set: set[str] = set()
        for t in targets:
            target_domain_set.update(domains_by_id.get(t, set()))
        if len(target_domain_set) < min_distinct_target_domains:
            continue
        findings.append((nid, label, len(targets), len(target_domain_set)))
    return sorted(findings)


def _label_to_prose_pattern(label: str) -> str:
    """Convert a snake_case node label into a regex fragment that matches
    its natural-language form in summary prose.

    Lowercases, splits on underscores, joins with ``\\s+``, and allows
    optional trailing ``s`` for plural-form occurrences. Each token is
    regex-escaped before joining. Word-boundary anchors are added by
    callers per the surrounding pattern shape.
    """
    tokens = [re.escape(t) for t in label.lower().split("_") if t]
    if not tokens:
        return ""
    return r"\s+".join(tokens) + r"s?"


def _detect_prereq_direction_summary_inconsistency(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    reversal_phrases: tuple[str, ...] = DIRECTION_REVERSAL_PHRASES,
) -> list[tuple[str, str, str, str]]:
    """Return ``(edge_id, source_id, target_id, matched_phrase)`` for
    cross-domain pedagogical-prerequisite edges whose target.summary
    contains a structural-dependency phrase pattern of shape
    ``<target.label> (is|are) ...<connecting-phrase>... <source.label>``.

    Per Issue #62 Proposal 3+5 merged (S-0122 audit input doc:60-77,
    98-108). Empirical basis: 5 cross-bridge reversal cases (CB-E-47,
    CB-E-63, CB-E-65, CB-E-69, CB-E-70) where the migration's own
    teaching prose contradicts the authored edge direction. Examples:

    - E-63 ``propositional_attitude → proposition``: proposition.summary
      says "propositions are the contents of propositional attitudes" —
      proposition supplies content to PA, so PA depends on proposition.
    - E-70 ``justice → morality``: morality.summary says "morality is
      the broader normative framework" — morality is broader; justice
      (specific) depends on morality (broader).

    Cross-bridges only — within-subdomain pairs share enough background
    vocabulary that the phrase-pattern produces too much noise. Phrase
    list anchored on the audit's documented cases (per
    DIRECTION_REVERSAL_PHRASES); Phase 6 self-correction can tune.
    """
    by_id: dict[str, dict[str, Any]] = {
        n["id"]: n for n in nodes if n.get("id") is not None
    }
    findings: list[tuple[str, str, str, str]] = []
    phrase_alternation = "|".join(re.escape(p) for p in reversal_phrases)
    for e in edges:
        if e.get("edge_type") != PREREQUISITE_EDGE_TYPE:
            continue
        s = e.get("source_id")
        t = e.get("target_id")
        if s is None or t is None:
            continue
        source = by_id.get(s)
        target = by_id.get(t)
        if source is None or target is None:
            continue
        source_domains = set(source.get("domain") or [])
        target_domains = set(target.get("domain") or [])
        if source_domains and target_domains and source_domains & target_domains:
            continue
        target_summary = target.get("summary")
        if not target_summary:
            continue
        source_label = source.get("label")
        target_label = target.get("label")
        if not source_label or not target_label:
            continue
        target_pattern = _label_to_prose_pattern(target_label)
        source_pattern = _label_to_prose_pattern(source_label)
        if not target_pattern or not source_pattern:
            continue
        # Target-noun-phrase ... is/are ... <phrase> ... source-noun-phrase
        # Same-sentence anchor: [^.;] excludes sentence-terminating
        # punctuation. The 80/120 budgets fit the audit-documented
        # cross-bridge reversals without over-bridging across clauses.
        regex = (
            r"\b"
            + target_pattern
            + r"\s+(?:is|are)\s+(?:[^.;]{0,80}?)(?:"
            + phrase_alternation
            + r")\b(?:[^.;]{0,120}?)\b"
            + source_pattern
            + r"\b"
        )
        match = re.search(regex, target_summary, flags=re.IGNORECASE)
        if match is None:
            continue
        # Recover the phrase fragment that fired so the soft-warn can
        # cite it.
        phrase_match = re.search(
            "(?:" + phrase_alternation + ")",
            match.group(0),
            flags=re.IGNORECASE,
        )
        matched_phrase = (
            phrase_match.group(0).lower() if phrase_match is not None else ""
        )
        eid = e.get("id")
        findings.append(
            (
                str(eid) if eid is not None else "",
                str(s),
                str(t),
                matched_phrase,
            )
        )
    return sorted(findings)


def _staged_paths_affect_graph() -> bool | None:
    """Return whether any staged path is graph-affecting (Issue #142).

    Disposition tri-state:
      * True  — at least one staged path matches
        ``GRAPH_AFFECTING_PATH_PREFIXES`` (proceed with audit).
      * False — staged paths exist and none are graph-affecting
        (caller may safely skip the connection attempt entirely).
      * None  — cannot determine (not in a git work tree, the git
        invocation failed, or zero staged paths). Likely a manual
        invocation of ``validate.py`` rather than the pre-commit
        hook; caller proceeds with normal audit logic.

    The 5-second subprocess timeout bounds the worst-case behaviour
    if the git environment itself misbehaves. ``check=False`` keeps
    a non-zero exit code (e.g., running outside a repo) from raising;
    we treat it as "cannot determine" instead.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None
    if result.returncode != 0:
        return None
    staged = [line for line in result.stdout.splitlines() if line.strip()]
    if not staged:
        return None
    for path in staged:
        for prefix in GRAPH_AFFECTING_PATH_PREFIXES:
            if path.startswith(prefix):
                return True
    return False


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
    cycles via Kosaraju SCC) plus ten soft-warn categories
    (undeclared_predicate, attribute_shape_inconsistency,
    missing_rigor_score, render_readiness_violation,
    synthetic_review_queue, orphan_leaf,
    suspicious_cross_domain_ratio, edge_evidence_empty,
    top_level_discipline_label_as_prereq_source,
    prereq_direction_summary_inconsistency), and returns a categorized
    result. The latter three landed at S-0146 from the S-0122 audit
    (Issue #62; per engine/build_readiness/phase_5_audit_system_input.md).

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

    # Path-aware skip per Issue #142: when running under the pre-commit
    # hook and the staged change set doesn't touch the graph, bypass
    # the connection attempt entirely. The S-0186 connect_timeout=10 +
    # S-0187 wall-clock watchdog cap connection establishment, but the
    # Supabase transaction-pool URL goes through pgbouncer which strips
    # session-level options=-c statement_timeout=... silently — so
    # psycopg.wait_c can hold past the cap under load. Skipping when
    # the audit isn't warranted is the cheapest mitigation per the
    # Issue's three-direction analysis. Manual invocations of
    # validate.py (no staged paths) and explicit ``connection_string``
    # overrides (test paths) are unaffected: the helper returns None
    # when staged paths cannot be enumerated.
    if connection_string is None:
        staged_affects = _staged_paths_affect_graph()
        if staged_affects is False:
            r.add_check("graph_audit_skipped_no_staged_graph_paths")
            return r

    try:
        nodes, edges = _read_graph_from_db(conn_str)
    except ImportError as exc:
        # psycopg unavailable. Pre-S-0049 this was a hard-fail because
        # SUPABASE_DB_URL was never set automatically — being set meant
        # the user committed to having psycopg. Post-S-0049, the walk-up
        # loader (engine/tools/load_env.py) auto-loads SUPABASE_DB_URL in
        # any context that has a reachable .env, including the pre-commit
        # hook running under system Python (which doesn't have psycopg).
        # The audit-skip path is the right disposition: non-seed-authoring
        # sessions (every commit besides Phase 5 task work) are not gated
        # on DB connectivity, and a missing psycopg is just one form of
        # "DB audit not applicable here". Print a stderr note so the user
        # still sees the gap if they intended to run the audit.
        print(
            f"[validate] graph_audit_skipped: psycopg unavailable "
            f"({exc!s}); install via venv per ADR 0050 to engage the audit",
            file=sys.stderr,
        )
        r.add_check("graph_audit_skipped")
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

    for eid, src, tgt in _detect_edge_evidence_empty(nodes, edges):
        r.soft_warn(
            "edge_evidence_empty",
            f"edge_id={eid!r} source={src!r} target={tgt!r}",
        )

    for (
        nid,
        label,
        prereq_count,
        distinct_domains,
    ) in _detect_top_level_discipline_label_as_prereq_source(nodes, edges):
        r.soft_warn(
            "top_level_discipline_label_as_prereq_source",
            f"node_id={nid!r} label={label!r} "
            f"prereq_count={prereq_count} distinct_target_domains={distinct_domains}",
        )

    for eid, src, tgt, phrase in _detect_prereq_direction_summary_inconsistency(
        nodes, edges
    ):
        r.soft_warn(
            "prereq_direction_summary_inconsistency",
            f"edge_id={eid!r} source={src!r} target={tgt!r} matched_phrase={phrase!r}",
        )

    return r


# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------


def validate_engine_memory_adoption() -> ValidationResult:
    """Adoption checks for the engine-memory substrate per ADR 0091.

    Covers the six-tool engine_memory MCP surface (ADR 0091 Decision
    5). Reads ``current.json``'s ``engine_memory_activity`` field
    (populated by ``scan_engine_memory_activity.py`` at shutdown step
    2 per ADR 0091). The sole adoption-check entry point for the
    engine-memory substrate.

    Categories:

    - ``engine_memory_boot_query_skipped`` (soft-warn) — no
      ``engine_memory_search`` call recorded.
    - ``engine_memory_diary_read_skipped`` (soft-warn) — no
      ``engine_memory_diary_read`` call recorded.
    - ``engine_memory_diary_write_skipped`` (HARD-FAIL, **engine mode
      only**) — no ``engine_memory_diary_write`` call AND no
      acknowledgement token ``engine_memory_unavailable_acknowledged:
      <reason>`` in ``outcome_summary``. Routine sessions emit
      ``engine_memory_diary_write_skipped_routine`` (soft-warn)
      instead — the user directive against routine-line halts on
      memory-substrate availability (per the S-0091 precedent carried
      forward) applies to the new substrate too.
    - ``engine_memory_diary_write_acknowledged_skip`` (soft-warn) —
      token present; hard-fail downgraded. Persistent skips fire the
      3-of-5 escalation per ADR 0042.
    - ``engine_memory_zero_citations_after_search`` (soft-warn) —
      ``search_calls > 0`` AND ``engine_memory_citations.total == 0``
      (closed-loop boot-search-effectiveness check; the citations
      block is populated by ``scan_engine_memory_citations.py`` per
      ADR 0091).

    No substrate-availability probe — engine_memory is a local SQLite
    file with no MCP-server-side intermittency to detect. The
    escape-hatch token surface still exists for legitimate edge
    cases (early-exit sessions with nothing meaningful to reflect on,
    filesystem-broken recovery).

    **Graceful no-op when ``engine_memory_activity`` is absent.** The
    field is the responsibility of ``scan_engine_memory_activity.py``;
    if it hasn't run (default-mode exploration session, or
    pre-shutdown commit), the validator skips silently. The
    structured-archive audit
    (``audit_archive_structured_fields.py``) hard-fails missing field
    at closing-commit time (since S-0192 per the
    ``REQUIRED_ARCHIVE_FIELDS`` row).

    Default-mode (exploration, non-build) sessions are exempt: when
    ``current.json`` is absent, the function returns a clean
    ValidationResult after recording one check.

    Gated by the ``--final-check`` CLI flag.
    """
    r = ValidationResult()
    r.add_check("validate_engine_memory_adoption")

    current_path = REPO_ROOT / "engine" / "session" / "current.json"
    if not current_path.is_file():
        return r

    try:
        current = json.loads(current_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return r

    activity = current.get("engine_memory_activity")
    if not isinstance(activity, dict):
        return r

    search_calls = int(activity.get("search_calls", 0))
    diary_read_calls = int(activity.get("diary_read_calls", 0))
    diary_write_calls = int(activity.get("diary_write_calls", 0))

    if search_calls == 0:
        r.soft_warn(
            "engine_memory_boot_query_skipped",
            "No engine_memory_search call recorded during this session. "
            "The boot-time engine-memory query (CLAUDE.md startup ceremony "
            "step 3 / session-build-lifecycle step 3 / "
            "routine-mode-lifecycle step 5.5) did not run, or its "
            "telemetry was not captured.",
        )

    if diary_read_calls == 0:
        r.soft_warn(
            "engine_memory_diary_read_skipped",
            "No engine_memory_diary_read call recorded during this "
            "session. The boot-time diary read "
            "(session-build-lifecycle step 3b / routine-mode-lifecycle "
            "step 5.6) did not run.",
        )

    mode_raw = current.get("mode")
    mode = mode_raw if isinstance(mode_raw, str) else "interactive"

    if diary_write_calls == 0:
        outcome_summary = current.get("outcome_summary") or ""
        if not isinstance(outcome_summary, str):
            outcome_summary = ""
        token_present = "engine_memory_unavailable_acknowledged:" in outcome_summary

        if token_present:
            r.soft_warn(
                "engine_memory_diary_write_acknowledged_skip",
                "⚠️  DIARY WRITE SKIPPED — DO NOT BURY THIS\n"
                "No engine_memory_diary_write call recorded; "
                "'engine_memory_unavailable_acknowledged:' token in "
                "outcome_summary. Hard-fail downgraded to soft-warn "
                "(token is honestly valid). Persistent acknowledged-"
                "skips fire the 3-of-5 escalation per ADR 0042. The "
                "single-session use is itself investigation-worthy: "
                "engine_memory is a local SQLite file with no MCP-"
                "server-side intermittency — substrate unavailability "
                "implies a filesystem issue or a deliberate early-exit "
                "session with nothing meaningful to reflect on. Address "
                "before the next session boot.",
            )
        elif mode == "routine":
            r.soft_warn(
                "engine_memory_diary_write_skipped_routine",
                "⚠️  ROUTINE DIARY DEFERRED — DO NOT BURY THIS\n"
                "No engine_memory_diary_write call recorded; no "
                "'engine_memory_unavailable_acknowledged:' token in "
                "outcome_summary. Routine mode does not hard-fail on "
                "memory-substrate availability (per the S-0091 "
                "precedent carried into engine_memory). Run "
                "engine_memory_diary_write at the next interactive "
                "session to capture the missing reflection.",
            )
        else:
            r.hard_fail(
                "engine_memory_diary_write_skipped: no "
                "engine_memory_diary_write call recorded during this "
                "engine session, and no "
                "'engine_memory_unavailable_acknowledged: <reason>' token "
                "in outcome_summary. Per ADR 0091: engine sessions must "
                "write a diary entry at close (the only first-person "
                "reflection layer). Either invoke engine_memory_diary_write "
                "now, or write the token + a one-line reason into "
                "outcome_summary and re-run validate.py --final-check."
            )

    citations_raw = activity.get("engine_memory_citations")
    citations: dict[str, Any] = citations_raw if isinstance(citations_raw, dict) else {}
    citations_total = int(citations.get("total", 0))

    if search_calls > 0 and citations_total == 0:
        r.soft_warn(
            "engine_memory_zero_citations_after_search",
            f"search_calls={search_calls} but "
            "engine_memory_citations.total=0. The session ran the "
            "engine-memory boot search but no drawer IDs, S-NNNN archive "
            "references, or tag-named drawer references appear in "
            "outcome_summary, the session's diary entry, or commit "
            "messages. Retrieval happened; observable behavior change "
            "did not. Citations are populated by "
            "scan_engine_memory_citations.py at shutdown step 12 per "
            "ADR 0091. Persistent firing across 3+ of last 5 sessions "
            "per ADR 0042 lifecycle indicates the boot-search "
            "effectiveness gap — tune the formulation set in "
            "engine/memory/boot_surface.py (FORMULATION_OPERATOR mapping "
            "or to_fts5_match logic) or escalate per "
            "engine/operations/soft-warn-lifecycle.md.",
        )

    return r


# ---------------------------------------------------------------------------
# Outcome-summary unhandled-defer detection (ADR 0049 Decision 6 / Issue #54)
# ---------------------------------------------------------------------------

# Hedge phrases drawn from the canonical S-0071 / S-0048 pushback
# instances now living as engine_memory `pushback`-room drawers.
# Conservative starting set per Issue #54; expand if false negatives
# surface. Patterns are matched case-insensitive and whitespace-tolerant.
_OUTCOME_SUMMARY_HEDGE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bfuture\s+session\b",
        r"\bnext\s+session\s+will\b",
        r"\bcorrectable\s+in\s+any\b",
        r"\bpreserved\s+for\s+manual\s+review\b",
        r"\bpicked\s+up\s+by\b",
        r"\bdefer\s+indefinitely\b",
        r"\brevisit\s+when\b",
    )
)

# Handle-string patterns. `#NN` matches Issue references (1+ digits); `S-NNNN`
# matches the canonical 4-digit session id.
_HANDLE_ISSUE_PATTERN = re.compile(r"^#(\d+)$")
_HANDLE_SESSION_PATTERN = re.compile(r"^S-(\d{4})$")


def _verify_issue_exists(issue_num: str) -> str | None:
    """Best-effort `gh issue view` check; returns None on success or unverifiable.

    Returns:
        - None on exit-0 (issue exists OR gh unavailable / network error /
          auth issue — anything that isn't a definitive "not found").
        - "not found" string on exit-1 with stderr matching the GitHub
          "Could not resolve to an Issue" / "not found" / "no issue or PR"
          shape — these are the only definitive negatives we treat as
          actionable. Any other error path suppresses to keep the validator
          offline-graceful per Issue #54's spirit ("don't block offline work").

    Spawned via `subprocess.run` with a 5-second timeout. The validator
    never raises on subprocess failure; verification is best-effort.
    """
    try:
        result = subprocess.run(
            ["gh", "issue", "view", issue_num, "--json", "state"],
            capture_output=True,
            text=True,
            timeout=5.0,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode == 0:
        return None
    err_lower = (result.stderr or "").lower()
    if "could not resolve" in err_lower or "no issue or pr" in err_lower:
        return "not found"
    if "not found" in err_lower and "issue" in err_lower:
        return "not found"
    return None


def validate_outcome_summary_unhandled_defer() -> ValidationResult:
    """Soft-warn defer-hedge prose without a declared handle per ADR 0049 Decision 6.

    Closes Issue #54 (Pushback Cluster A from the S-0097 audit). Two
    canonical instances captured as `[pushback]`-prefixed drawers in
    `paideia/problems`: S-0071 ("correctable in any future session via a
    JSON edit") and S-0048 ("preserved for manual review"). Both share the
    anti-pattern: deferral language that masks lack-of-resolution. The user
    adjudicated at S-0098 between brittle keyword-scan-only and structured
    archive-field requirement formulations, picking the latter. This audit
    operationalizes the structured-field approach.

    Reads engine/session/current.json's `outcome_summary` (string) and
    `next_session_handle` (str | None) fields. The `outcome_summary` is
    only populated at shutdown step 8, so mid-session pre-commit
    invocations are no-ops (the audit returns clean when `outcome_summary`
    is None).

    Disposition table (one positive primary category + three verification
    categories so failures are diagnosable):

        Hedge match in outcome_summary?  next_session_handle value      Action
        --------------------------------  -----------------------------  ------
        No                                (any)                          No-op
        Yes                               key absent from JSON           outcome_summary_unhandled_defer
        Yes                               null                           No-op (explicit "no defer")
        Yes                               "#<num>" + verified exists      No-op
        Yes                               "#<num>" + verified missing     next_session_handle_unknown_issue
        Yes                               "#<num>" + unverifiable        No-op (offline-graceful)
        Yes                               "S-<NNNN>" + archive exists    No-op
        Yes                               "S-<NNNN>" + matches next_id   No-op (next-claim-slot)
        Yes                               "S-<NNNN>" + neither           next_session_handle_unknown_session
        Yes                               other string                   next_session_handle_malformed

    Hedge regex set is conservative (7 patterns from Issue #54) — expand
    if false negatives surface in the first 5 sessions. Patterns are
    case-insensitive and whitespace-tolerant.

    Issue verification uses `gh issue view` with a 5-second timeout;
    suppresses on `gh` not installed, network failure, auth issue, or any
    non-definitive negative. Only the explicit "Could not resolve to an
    Issue" / "no issue or pr" responses fire the unknown-issue category.
    Per Issue #54 design intent: catch typos / stale references when
    online, don't block offline work.

    Session verification: an `S-<NNNN>` value is valid if either
    engine/session/archive/S-<NNNN>.json exists OR S-<NNNN> matches the
    next-claim slot in register_state.json (a session ID promised but not
    yet claimed). Anything else fires next_session_handle_unknown_session.

    Default-mode (exploration, non-build) sessions are exempt: when
    current.json is absent there is no formal session to audit.

    Gated by the `--final-check` CLI flag — pre-commit hook invocations
    (no flag) skip this validator so mid-session commits don't nag. The
    shutdown SKILL invokes `validate.py --final-check` at step 7 after
    `outcome_summary` and `next_session_handle` have been populated by the
    shutdown sequence's step 7b prompt + step 8 fill.
    """
    r = ValidationResult()
    r.add_check("validate_outcome_summary_unhandled_defer")

    current_path = REPO_ROOT / "engine" / "session" / "current.json"
    if not current_path.is_file():
        return r

    try:
        current = json.loads(current_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return r

    outcome_summary = current.get("outcome_summary")
    if not isinstance(outcome_summary, str) or not outcome_summary.strip():
        # Mid-session safety: outcome_summary is null until shutdown step 8.
        return r

    matched_patterns = [
        p.pattern for p in _OUTCOME_SUMMARY_HEDGE_PATTERNS if p.search(outcome_summary)
    ]
    if not matched_patterns:
        return r

    has_handle_key = "next_session_handle" in current
    handle_value = current.get("next_session_handle")

    if not has_handle_key:
        r.soft_warn(
            "outcome_summary_unhandled_defer",
            f"outcome_summary contains hedge-pattern phrasing "
            f"({', '.join(matched_patterns)}) but next_session_handle is "
            "absent from current.json. Per ADR 0049 Decision 6 (S-0100 "
            "amendment) / Issue #54, declare the handle as either "
            "'#<num>' (Issue), 'S-<NNNN>' (session), or null (when the "
            "phrasing is intentional forward-pointer prose, not a "
            "deferral). The structured-field requirement closes Pushback "
            "Cluster A from the S-0097 audit — defer-hedge language without "
            "a paired commitment is functionally identical to silence.",
        )
        return r

    if handle_value is None:
        return r

    if not isinstance(handle_value, str):
        r.soft_warn(
            "next_session_handle_malformed",
            f"next_session_handle has bad shape: expected str or null, got "
            f"{type(handle_value).__name__}. The audit_archive_structured_fields "
            "shape audit will hard-fail at closing-commit time; this soft-warn "
            "is the in-flight surface during the session.",
        )
        return r

    handle = handle_value.strip()

    issue_match = _HANDLE_ISSUE_PATTERN.match(handle)
    session_match = _HANDLE_SESSION_PATTERN.match(handle)

    if issue_match is not None:
        verdict = _verify_issue_exists(issue_match.group(1))
        if verdict == "not found":
            r.soft_warn(
                "next_session_handle_unknown_issue",
                f"next_session_handle={handle!r} but `gh issue view "
                f"{issue_match.group(1)}` reports the Issue does not exist. "
                "Either the Issue was closed/deleted or the number is a "
                "typo. Verify and update the handle, or change to null if "
                "the deferral is no longer applicable.",
            )
        return r

    if session_match is not None:
        session_num = int(session_match.group(1))
        archive_path = (
            REPO_ROOT / "engine" / "session" / "archive" / f"S-{session_num:04d}.json"
        )
        register_path = REPO_ROOT / "engine" / "session" / "register_state.json"
        next_id_int: int | None = None
        if register_path.is_file():
            try:
                register = json.loads(register_path.read_text(encoding="utf-8"))
                next_id_raw = register.get("next_id")
                if isinstance(next_id_raw, str) and next_id_raw.isdigit():
                    next_id_int = int(next_id_raw)
            except (json.JSONDecodeError, OSError):
                pass
        if archive_path.is_file():
            return r
        if next_id_int is not None and session_num == next_id_int:
            return r
        r.soft_warn(
            "next_session_handle_unknown_session",
            f"next_session_handle={handle!r} but no archive exists at "
            f"engine/session/archive/S-{session_num:04d}.json AND the "
            "session ID does not match the next-claim slot in "
            f"register_state.json (next_id={next_id_int!r}). The handle "
            "must reference either an existing archived session or the "
            "very next claim slot.",
        )
        return r

    r.soft_warn(
        "next_session_handle_malformed",
        f"next_session_handle={handle!r} does not match the required "
        "shape. Valid forms: '#<num>' (Issue reference), 'S-<NNNN>' "
        "(session reference, 4-digit), or null. Update the value to one "
        "of these, or remove the hedge-pattern phrasing from "
        "outcome_summary if the prose was unintentional.",
    )
    return r


# ---------------------------------------------------------------------------
# Timestamp helper bypass detection (ADR 0058 / Issue #33)
# ---------------------------------------------------------------------------

# Allowlisted source paths under engine/tools/ that may emit non-canonical
# timestamps without firing timestamp_helper_bypass. Each entry must be
# justified by an inline comment in the source file referencing ADR 0058.
_TIMESTAMP_HELPER_BYPASS_ALLOWLIST = frozenset(
    {
        "timestamps.py",  # the helper module itself defines the canonical shapes
        "apply_migration.py",  # legacy supabase schema_migrations.version contract
        "probe_push_gate.py",  # branch-name-safe compact-time form (no colons)
        "scan_dependabot_prs.py",  # gh wire-format timestamps (created_at parse + --simulate-age emit), not engine-canonical
    }
)


def validate_timestamp_helper_bypass() -> ValidationResult:
    """Soft-warn ad-hoc timestamp emission outside engine/tools/timestamps.py per ADR 0058.

    Walks each ``engine/tools/**/*.py`` source file with ``ast`` and
    detects ``Call`` nodes whose ``func.attr`` is ``"isoformat"``,
    ``"strftime"``, or ``"fromisoformat"``. Each detected callsite outside
    the allowlist fires a ``timestamp_helper_bypass`` soft-warn with
    file:line. The first two cover emit-site bypass; the third covers
    parse-site bypass (per the discipline contract: every site that reads
    a stored timestamp uses ``parse()``, not ``datetime.fromisoformat``
    directly, so the helper is the single point that knows about legacy
    shapes).

    Allowlist (no warn):
        - ``engine/tools/timestamps.py`` — the helper itself defines
          canonical shapes via ``strftime`` against ``CANONICAL_FORMAT`` /
          ``MICROS_FORMAT`` / ``DATE_FORMAT``.
        - ``engine/tools/apply_migration.py`` — the migration-version
          ``%Y%m%d%H%M%S`` shape is allowlisted as a legacy supabase
          contract per ADR 0058 Decision element 5.

    Excluded (no walk performed):
        - ``test_*.py`` — test fixtures legitimately carry timestamp
          string literals AND ``strftime``/``isoformat`` calls inside
          synthetic data construction. AST detection cannot distinguish
          a fixture string from a real emit site.

    Out of scope for the AST walk:
        - Shell scripts under ``engine/tools/hooks/*.sh`` — they emit
          canonical second precision via ``date -u +"%Y-%m-%dT%H:%M:%SZ"``,
          a separate runtime per ADR 0058 Decision element 4.
        - Non-Python files anywhere in the tree.

    Inputs: none (walks ``engine/tools/`` rooted at REPO_ROOT).
    Outputs: ``ValidationResult`` carrying ``timestamp_helper_bypass``
    soft-warn entries per offending callsite. Emits the
    ``timestamp_helper_bypass`` check name into ``checks_run``.
    Edge cases:
        - Files with syntax errors (cannot be parsed) emit a soft-warn at
          the file path; the walk continues for other files.
        - Files outside the engine/tools/ root are not walked.
    Non-responsibilities:
        - Does not enforce a particular emit shape — that's ADR 0058's
          contract layer. The check enforces *helper-routing*, leaving
          shape correctness to the helper itself.
        - Does not detect ``time.time()`` / ``time.monotonic()`` usage
          (stopwatch math is out of scope per ADR 0058 Decision element 6).
    """
    r = ValidationResult()
    r.add_check("timestamp_helper_bypass")

    tools_root = REPO_ROOT / "engine" / "tools"
    if not tools_root.is_dir():
        return r

    for py_path in sorted(tools_root.rglob("*.py")):
        name = py_path.name
        if name.startswith("test_"):
            continue
        if name in _TIMESTAMP_HELPER_BYPASS_ALLOWLIST:
            continue
        try:
            source = py_path.read_text(encoding="utf-8")
        except OSError as e:
            r.soft_warn(
                "timestamp_helper_bypass",
                f"{py_path.relative_to(REPO_ROOT)}: read failed ({e}); "
                "AST walk skipped, possible bypass not detected.",
            )
            continue
        # Path A pre-filter per S-0206 third-fire investigation (ADR 0063
        # readiness-note T1-B closure). A file that contains none of the
        # three keyword substrings cannot contain a matching Call node
        # below — substring presence is a superset of attribute-access
        # presence. Skipping the ast.parse + ast.walk on the ~93% of
        # engine/tools/*.py files that don't contain any of the keywords
        # cuts the dominant CPU cost (per-file AST construction) with no
        # false negatives. Assumes Python source does not split these
        # identifiers across `\` line-continuations — not present in current
        # corpus and forbidden by ruff format; the regression check would
        # surface the missed cost if this ever breaks.
        if not any(kw in source for kw in ("isoformat", "strftime", "fromisoformat")):
            continue
        try:
            tree = ast.parse(source, filename=str(py_path))
        except SyntaxError as e:
            r.soft_warn(
                "timestamp_helper_bypass",
                f"{py_path.relative_to(REPO_ROOT)}: parse failed ({e.msg} "
                f"at line {e.lineno}); AST walk skipped, possible bypass "
                "not detected.",
            )
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not isinstance(func, ast.Attribute):
                continue
            if func.attr not in ("isoformat", "strftime", "fromisoformat"):
                continue
            r.soft_warn(
                "timestamp_helper_bypass",
                f"{py_path.relative_to(REPO_ROOT)}:{node.lineno}: "
                f".{func.attr}(...) — ad-hoc timestamp emission. Per "
                "ADR 0058 + engine/operations/timestamp-discipline.md, "
                "route through engine/tools/timestamps.py "
                "(emit / emit_micros / parse / today). If this site has "
                "a legitimate non-canonical contract (e.g., a new legacy "
                "external system), add the path to "
                "_TIMESTAMP_HELPER_BYPASS_ALLOWLIST in validate.py with "
                "an inline comment naming the contract being preserved.",
            )

    return r


# Per-phase runtime targets per ADR 0063 (S-0126; four-phase model from S-0127
# Issue #90 fold).
# Structural phase: in-process file/regex checks only, no DB or subprocess.
# Health-probe phase: external-subprocess probes (repo state via
# probe_repo.py, session-dir via probe_session_dir.py, GitHub Issues
# via `gh issue list`). Bounded but slow and variable (network for gh).
# Extracted from structural phase at S-0127 — pre-extraction the
# external-subprocess probes dominated structural timing and surfaced
# the regression soft-warn that motivated the split;
# validate_issue_collisions was also moved here in the same fold
# because it shares the external-subprocess shape.
# Graph audit phase: live-DB consultation per ADR 0016.
# Total: sum of phases plus shutdown audits when --final-check is set; ~500ms
# buffer above phase sum for finalchecks + bookkeeping.
VALIDATOR_PHASE_TARGETS_MS: dict[str, float] = {
    # Structural target bumped 500 -> 700 at S-0206 (third regression fire,
    # Path C closure per ADR 0063 readiness-note T1-C). Post-Path-A
    # (validate_timestamp_helper_bypass keyword pre-filter at commit 78b439e)
    # structural pipeline median measured 811ms on n=5 warm iterations
    # (range 693-1097ms), with validate_adr_back_reference_orphan's intrinsic
    # file I/O across ~211 non-ADR md files as the dominant residual cost.
    # 700ms target -> 1050ms 1.5x threshold accommodates the measured warm
    # range without masking future algorithmic regressions in the
    # genuinely fast in-memory checks. Corpus has grown from 85 ADRs (S-0151
    # baseline) to 92 ADRs and the structural-phase function count from 7
    # to 10 (ADR 0089 skill-layer1 parity + ADR 0092 changelog entries /
    # README governance).
    "duration_structural_ms": 700.0,
    "duration_health_probe_ms": 5000.0,
    "duration_graph_audit_ms": 5000.0,
    "duration_total_ms": 11000.0,
}

# Governed-doc soft-warn thresholds per ADR 0062 (S-0126; Issue #87 part b).
# state_md_row_count: STATE.md baseline at S-0126 is 118 rows; threshold gives
# ~50% headroom before firing. Per-session prose belongs in archive + ENGINE_LOG.
STATE_MD_ROW_COUNT_THRESHOLD = 180
# handoff_long_resolved_sections: HANDOFF.md preamble commits to prune-on-resolve;
# total-count threshold + age-in-sessions threshold (per-section S-NNNN parse).
HANDOFF_RESOLVED_COUNT_THRESHOLD = 5
HANDOFF_RESOLVED_AGE_THRESHOLD_SESSIONS = 10
# Regex catching `**Resolved:**` lines that name a session (preamble prose uses
# the word "Resolved" without bold + session-id; this pattern only matches the
# actual section-marker shape).
_HANDOFF_RESOLVED_LINE_RE = re.compile(
    r"^\s*[-*]?\s*\*\*Resolved:\*\*\s*S-(\d{4})", re.MULTILINE
)
# Pattern for retired ADR-Consequences inline-amendment headers per ADR 0036
# + ADR 0062. Zero-tolerance — any `### Amendment` header in any ADR file fires.
_ADR_AMENDMENT_HEADER_RE = re.compile(r"^### Amendment", re.MULTILINE)

# Per ADR 0092 (S-0198): per-session changelog entry caps + governance README cap.
CHANGELOG_ENTRY_LINE_CAP_SOFT = 50
CHANGELOG_ENTRY_LINE_CAP_HARD = 70
CHANGELOG_README_LINE_CAP_SOFT = 50
CHANGELOG_README_LINE_CAP_HARD = 70
_CHANGELOG_ENTRY_FILENAME_RE = re.compile(r"^(S-\d{4})-(.+)\.md$")


def validate_changelog_entries(repo_root: Path | None = None) -> ValidationResult:
    """Validate per-session changelog entries under engine/changelog/<YYYY>/.

    Per ADR 0092 (S-0198). For each entry file:

    - Soft-warn ``changelog_entry_soft_cap`` if total line count exceeds
      ``CHANGELOG_ENTRY_LINE_CAP_SOFT`` (50).
    - Hard-fail ``changelog_entry_hard_cap`` if total line count exceeds
      ``CHANGELOG_ENTRY_LINE_CAP_HARD`` (70).
    - Hard-fail ``changelog_entry_no_frontmatter`` if the file lacks YAML
      frontmatter delimiters.
    - Hard-fail ``changelog_entry_schema_violation`` for each
      jsonschema.Draft202012Validator error against
      ``engine/schemas/changelog-entry.schema.json``.
    - Hard-fail ``changelog_entry_filename_mismatch`` if the filename's
      leading ``S-NNNN`` token does not match the frontmatter ``session_id``.

    Skips the ``_history/`` rollover directory; only walks active-year
    ``<YYYY>/`` subdirectories.

    Inputs:
        repo_root: Override the module-level REPO_ROOT. Test injection point.

    Returns:
        ValidationResult with ``changelog_entries`` registered as a check.
    """
    r = ValidationResult()
    r.add_check("changelog_entries")
    root = repo_root if repo_root is not None else REPO_ROOT
    changelog_root = root / "engine" / "changelog"
    schema_path = root / "engine" / "schemas" / "changelog-entry.schema.json"
    if not changelog_root.is_dir() or not schema_path.is_file():
        return r
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        r.hard_fail(f"engine/schemas/changelog-entry.schema.json unreadable: {exc}")
        return r
    try:
        import jsonschema as _js  # type: ignore[import-untyped]

        validator = _js.Draft202012Validator(schema)
    except Exception as exc:  # noqa: BLE001 — best-effort import; degrade gracefully
        r.soft_warn(
            "changelog_entries",
            f"jsonschema unavailable for changelog validation: {exc}",
        )
        return r
    for year_dir in sorted(changelog_root.iterdir()):
        if not year_dir.is_dir() or year_dir.name.startswith("_"):
            continue
        for entry_path in sorted(year_dir.glob("S-*.md")):
            if not entry_path.is_file():
                continue
            try:
                text = entry_path.read_text(encoding="utf-8")
            except OSError:
                continue
            rel = entry_path.relative_to(root)
            lines = text.splitlines()
            line_count = len(lines)
            if line_count > CHANGELOG_ENTRY_LINE_CAP_HARD:
                r.hard_fail(
                    f"{rel} is {line_count} lines (hard cap "
                    f"{CHANGELOG_ENTRY_LINE_CAP_HARD}); changelog entries "
                    f"must summarize via pointers, not narrate. Per ADR 0092."
                )
            elif line_count > CHANGELOG_ENTRY_LINE_CAP_SOFT:
                r.soft_warn(
                    "changelog_entry_soft_cap",
                    f"{rel} is {line_count} lines (soft cap "
                    f"{CHANGELOG_ENTRY_LINE_CAP_SOFT}); compress toward "
                    f"summary+pointers shape. Per ADR 0092.",
                )
            # Parse frontmatter inline (avoid cross-tool import for an
            # ~8-line parse). Matches changelog_aggregate.parse_frontmatter
            # contract: key: value, optional quoted values, no nesting.
            if not lines or lines[0].strip() != "---":
                r.hard_fail(
                    f"{rel}: missing opening --- frontmatter delimiter "
                    f"(changelog_entry_no_frontmatter). Per ADR 0092."
                )
                continue
            end = None
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    end = i
                    break
            if end is None:
                r.hard_fail(
                    f"{rel}: missing closing --- frontmatter delimiter "
                    f"(changelog_entry_no_frontmatter). Per ADR 0092."
                )
                continue
            fm: dict[str, str] = {}
            for raw in lines[1:end]:
                line = raw.rstrip()
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                if ":" not in line:
                    continue
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                fm[key] = value
            for err in validator.iter_errors(fm):
                r.hard_fail(
                    f"{rel}: schema violation "
                    f"(changelog_entry_schema_violation): {err.message}"
                )
            m = _CHANGELOG_ENTRY_FILENAME_RE.match(entry_path.name)
            if m:
                fname_sid = m.group(1)
                fm_sid = fm.get("session_id")
                if fm_sid is not None and fm_sid != fname_sid:
                    r.hard_fail(
                        f"{rel}: filename session_id {fname_sid} does not "
                        f"match frontmatter session_id {fm_sid} "
                        f"(changelog_entry_filename_mismatch). Per ADR 0092."
                    )
    return r


def validate_changelog_readme_governance(
    repo_root: Path | None = None,
) -> ValidationResult:
    """Soft-warn / hard-fail on engine/changelog/README.md line-cap breach.

    Per ADR 0092 (S-0198). The README declares ``governed: true`` in its HTML
    frontmatter with ``line_cap_soft: 50 / line_cap_hard: 70``. Standalone
    check (no governed_files.yaml apparatus; Paideia uses inline enforcement).

    Inputs:
        repo_root: Override the module-level REPO_ROOT.

    Returns:
        ValidationResult with ``changelog_readme_governance`` registered.
    """
    r = ValidationResult()
    r.add_check("changelog_readme_governance")
    root = repo_root if repo_root is not None else REPO_ROOT
    readme = root / "engine" / "changelog" / "README.md"
    if not readme.is_file():
        return r
    try:
        text = readme.read_text(encoding="utf-8")
    except OSError as exc:
        r.hard_fail(f"engine/changelog/README.md unreadable: {exc}")
        return r
    line_count = sum(1 for _ in text.splitlines())
    if line_count > CHANGELOG_README_LINE_CAP_HARD:
        r.hard_fail(
            f"engine/changelog/README.md is {line_count} lines (hard cap "
            f"{CHANGELOG_README_LINE_CAP_HARD}); declared `governed: true` "
            f"with `line_cap_hard: {CHANGELOG_README_LINE_CAP_HARD}` in its "
            f"HTML frontmatter. Per ADR 0092."
        )
    elif line_count > CHANGELOG_README_LINE_CAP_SOFT:
        r.soft_warn(
            "changelog_readme_governance",
            f"engine/changelog/README.md is {line_count} lines (soft cap "
            f"{CHANGELOG_README_LINE_CAP_SOFT}); declared "
            f"`line_cap_soft: {CHANGELOG_README_LINE_CAP_SOFT}` in its "
            f"HTML frontmatter. Per ADR 0092.",
        )
    return r


def validate_state_md_row_count(repo_root: Path | None = None) -> ValidationResult:
    """Soft-warn when engine/STATE.md exceeds STATE_MD_ROW_COUNT_THRESHOLD.

    Per ADR 0062 (S-0126; Issue #87). STATE.md committed at S-0121 to a
    scope-discipline preamble: present-state-only; per-session prose belongs
    in archive + ENGINE_LOG.md. This soft-warn mechanizes the boundary so
    accumulation re-surfacing fires the warn rather than waiting for the next
    cadence-fired audit.

    Inputs:
        repo_root: Override the module-level REPO_ROOT. Test injection point.

    Returns:
        ValidationResult with `state_md_row_count` registered as a check.
        Soft-warn fires when row count exceeds the threshold.
    """
    r = ValidationResult()
    r.add_check("state_md_row_count")
    root = repo_root if repo_root is not None else REPO_ROOT
    state_path = root / "engine" / "STATE.md"
    if not state_path.exists():
        return r
    row_count = sum(1 for _ in state_path.read_text(encoding="utf-8").splitlines())
    if row_count > STATE_MD_ROW_COUNT_THRESHOLD:
        r.soft_warn(
            "state_md_row_count",
            f"engine/STATE.md is {row_count} rows (threshold "
            f"{STATE_MD_ROW_COUNT_THRESHOLD}); per the file's preamble, "
            f"session-by-session prose belongs in engine/session/archive + "
            f"engine/changelog/<YYYY>/, not in STATE.md.",
        )
    return r


def validate_adr_consequences_amendment_headers(
    repo_root: Path | None = None,
) -> ValidationResult:
    """Soft-warn on any `### Amendment` header in ADR files.

    Per ADR 0036 + ADR 0062 (S-0126; Issue #87) + ADR 0092 (S-0198, layer-2
    surface mutation from monolithic ENGINE_LOG.md to engine/changelog/
    directory). ADR body content is present-truth declarative; authorship
    history, supersession narration, and per-session revision markers belong
    in engine/changelog/<YYYY>/ entries / engine_memory `decisions` room
    drawers / git blame. The 14 inline-amendment blocks retired at S-0126
    motivate this gate-time backstop against re-introduction.

    Inputs:
        repo_root: Override the module-level REPO_ROOT.

    Returns:
        ValidationResult with `adr_consequences_amendment_header` registered.
        One soft-warn per offending header (file:line pinpoints the surface).
    """
    r = ValidationResult()
    r.add_check("adr_consequences_amendment_header")
    root = repo_root if repo_root is not None else REPO_ROOT
    for adr_dir in [root / "engine" / "adr", root / "product" / "adr"]:
        if not adr_dir.exists():
            continue
        for adr_file in sorted(adr_dir.glob("*.md")):
            try:
                text = adr_file.read_text(encoding="utf-8")
            except OSError:
                continue
            for match in _ADR_AMENDMENT_HEADER_RE.finditer(text):
                line_no = text[: match.start()].count("\n") + 1
                rel_path = adr_file.relative_to(root)
                r.soft_warn(
                    "adr_consequences_amendment_header",
                    f"ADR {rel_path} carries `### Amendment` header at "
                    f"line {line_no}; per ADR 0036 + ADR 0062 + ADR 0092, "
                    f"authorship history belongs in engine/changelog/<YYYY>/ "
                    f"entries / engine_memory `decisions` room drawers / "
                    f"git, not in ADR body.",
                )
    return r


def validate_handoff_long_resolved_sections(
    repo_root: Path | None = None,
    current_session_id: str | None = None,
) -> ValidationResult:
    """Soft-warn when HANDOFF.md accumulates resolved sections.

    Per ADR 0062 (S-0126; Issue #87). HANDOFF.md's preamble commits to a
    prune-on-resolve discipline applied inline at the next interactive session
    that touches HANDOFF. This soft-warn mechanizes the boundary at two
    thresholds:

      1. Total-count: more than HANDOFF_RESOLVED_COUNT_THRESHOLD resolved
         sections present.
      2. Per-section age: any `**Resolved:** S-NNNN` line whose session id is
         more than HANDOFF_RESOLVED_AGE_THRESHOLD_SESSIONS older than the
         current session.

    Inputs:
        repo_root: Override the module-level REPO_ROOT.
        current_session_id: "S-NNNN" of the in-progress session. If absent or
            unparseable, the age check is skipped (count check still fires).

    Returns:
        ValidationResult with `handoff_long_resolved_sections` registered.
        Up to one count-warn + N age-warns.
    """
    r = ValidationResult()
    r.add_check("handoff_long_resolved_sections")
    root = repo_root if repo_root is not None else REPO_ROOT
    handoff_path = root / "HANDOFF.md"
    if not handoff_path.exists():
        return r
    try:
        text = handoff_path.read_text(encoding="utf-8")
    except OSError:
        return r

    matches = list(_HANDOFF_RESOLVED_LINE_RE.finditer(text))
    count = len(matches)
    if count > HANDOFF_RESOLVED_COUNT_THRESHOLD:
        r.soft_warn(
            "handoff_long_resolved_sections",
            f"HANDOFF.md has {count} resolved sections (threshold "
            f"{HANDOFF_RESOLVED_COUNT_THRESHOLD}); prune per the "
            f"prune-on-resolve discipline in the HANDOFF.md preamble.",
        )

    # Age check: requires a parseable current_session_id. The session id passes
    # through main() from session_id_from_current(); during pre-commit hook
    # invocations the current session is in-progress, so the id is available.
    if current_session_id and current_session_id.startswith("S-"):
        try:
            current_n = int(current_session_id[2:])
        except ValueError:
            current_n = None
        if current_n is not None:
            for m in matches:
                try:
                    resolved_n = int(m.group(1))
                except (ValueError, IndexError):
                    continue
                age = current_n - resolved_n
                if age > HANDOFF_RESOLVED_AGE_THRESHOLD_SESSIONS:
                    r.soft_warn(
                        "handoff_long_resolved_sections",
                        f"HANDOFF.md resolved section at S-{m.group(1)} is "
                        f"{age} sessions old (threshold "
                        f"{HANDOFF_RESOLVED_AGE_THRESHOLD_SESSIONS}); prune.",
                    )
    return r


# ---------------------------------------------------------------------------
# Skill ↔ Layer-1 procedure parity (per ADR 0089; Issue #129)
# ---------------------------------------------------------------------------


class _SkillDocPair(NamedTuple):
    """A recipe Skill paired with its Layer-1 ops doc, plus how to locate
    each side's procedure-step enumeration.

    ``doc_style`` selects the step-line grammar of the Layer-1 doc:
    ``"headings"`` for ``### N. Title`` / ``#### Na. Title`` headings,
    ``"list"`` for ``N. **Title.**`` paragraph-leading numbered-list items.
    All four recipe Skills use the headings grammar, so the Skill side is
    always ``"headings"`` and not configured. ``*_section`` is the literal
    procedure-section heading; ``*_section_end`` is the literal heading that
    terminates it (a level-2 ``## `` heading is the fallback bound when the
    marker is absent).
    """

    name: str
    skill_path: str
    skill_section: str
    skill_section_end: str
    doc_path: str
    doc_section: str
    doc_section_end: str
    doc_style: str


# The four recipe Skills (per ADR 0044's three + routine-mode-lifecycle per
# ADR 0051) and their Layer-1 ops docs. Each Skill body is the procedural form
# of its Layer-1 doc; ADR 0044 commits the two to enumerate the same steps.
_SKILL_LAYER1_PAIRS: tuple[_SkillDocPair, ...] = (
    _SkillDocPair(
        name="routine-mode-lifecycle",
        skill_path=".claude/skills/routine-mode-lifecycle/SKILL.md",
        skill_section="## Boot procedure (run in order)",
        skill_section_end="## Routine-mode posture (load-bearing)",
        doc_path="engine/operations/routine-mode-operations.md",
        doc_section="## Routine boot procedure",
        doc_section_end="### Concurrency control (per ADR 0082)",
        doc_style="list",
    ),
    _SkillDocPair(
        name="session-build-lifecycle",
        skill_path=".claude/skills/session-build-lifecycle/SKILL.md",
        skill_section="## Boot procedure (run in order)",
        skill_section_end="## In-session commit cadence",
        doc_path="engine/operations/session-build-lifecycle.md",
        doc_section="## Boot procedure (run in order)",
        doc_section_end="## Eager-claim ritual",
        doc_style="list",
    ),
    _SkillDocPair(
        name="session-shutdown-sequence",
        skill_path=".claude/skills/session-shutdown-sequence/SKILL.md",
        skill_section="## Sequence",
        skill_section_end="## Updating design docs during a session",
        doc_path="engine/operations/session-shutdown-sequence.md",
        doc_section="## Sequence",
        doc_section_end="## Updating design docs during a session",
        doc_style="headings",
    ),
    _SkillDocPair(
        name="build-readiness-gate",
        skill_path=".claude/skills/build-readiness-gate/SKILL.md",
        skill_section="## Procedure",
        skill_section_end="## Failure modes the gate prevents",
        doc_path="engine/operations/build-readiness-gate.md",
        doc_section="## Procedure",
        doc_section_end="## Build-readiness report template",
        doc_style="headings",
    ),
)

# Step-number tokens: a leading digit, optionally followed by sub-letters
# and/or a `.<minor>` part — matches `1`, `0a`, `5.5`, `7a`, `11`.
_PROCEDURE_STEP_HEADING_RE = re.compile(r"^#{3,4}\s+(\d[\da-z.]*)\.\s")
_PROCEDURE_STEP_LIST_RE = re.compile(r"^(\d[\da-z.]*)\.\s")


def _extract_procedure_section(
    text: str, section_start: str, section_end: str
) -> list[str] | None:
    """Return the body lines of the named procedure section, or None.

    The section runs from the line after ``section_start`` to (exclusive)
    the first of: a line equal to ``section_end``, or a level-2 ``## ``
    heading other than the start heading. Returns None when ``section_start``
    is not found.
    """
    lines = text.splitlines()
    start_idx: int | None = None
    for i, line in enumerate(lines):
        if line.strip() == section_start:
            start_idx = i
            break
    if start_idx is None:
        return None
    body: list[str] = []
    for line in lines[start_idx + 1 :]:
        stripped = line.strip()
        if stripped == section_end:
            break
        if stripped.startswith("## ") and stripped != section_start:
            break
        body.append(line)
    return body


def _extract_step_numbers(
    text: str, section_start: str, section_end: str, style: str
) -> set[str] | None:
    """Return the set of procedure step-number tokens for a procedure section.

    ``style`` is ``"headings"`` (``### N. Title`` lines) or ``"list"``
    (``N. **Title.**`` paragraph-leading list items). Returns None when the
    section cannot be located (heading text changed); an empty set means the
    section was found but no step lines parsed (step-line grammar changed).
    """
    body = _extract_procedure_section(text, section_start, section_end)
    if body is None:
        return None
    pattern = (
        _PROCEDURE_STEP_HEADING_RE if style == "headings" else _PROCEDURE_STEP_LIST_RE
    )
    steps: set[str] = set()
    for line in body:
        match = pattern.match(line)
        if match is not None:
            steps.add(match.group(1))
    return steps


def validate_skill_layer1_parity(repo_root: Path | None = None) -> ValidationResult:
    """Soft-warn when a recipe Skill's procedure step set diverges from its
    Layer-1 ops doc.

    Per ADR 0089 (Issue #129). The four recipe Skills (per ADR 0044's three
    plus routine-mode-lifecycle per ADR 0051) are the procedural form of their
    Layer-1 ops docs; ADR 0044 commits the two to enumerate the same procedure.
    The #122-#129 drift cluster falsified the "doc → skill only" sync
    assumption — drift ran skill↔skill (#125) and command↔skill (#123) with no
    mechanical surface to catch it.

    The check compares the *step-number set* of each side's procedure section
    (e.g. ``{0a, 1, 2, 5.5, ...}``), not step titles — skill voice and
    reference voice legitimately differ in wording per ADR 0044. A step
    present in one side but absent from the other is enumeration drift: the
    Skill grew a step the doc lacks, or the doc carries a step the Skill
    dropped. Either way a human reconciles.

    Soft-warn only — the legitimate-exception surface is non-empty (a future
    Skill may deliberately collapse or split a doc step) and a hard-fail would
    block unrelated commits on a stale procedure doc. One soft-warn per
    drifting pair, plus one per missing file or unlocatable section.

    Inputs:
        repo_root: Override the module-level REPO_ROOT (for testability).

    Returns:
        ValidationResult with ``skill_layer1_parity_drift`` registered.

    Non-responsibilities:
        - Does not compare step *titles* — wording divergence between skill
          voice and reference voice is expected, not drift.
        - Does not verify step *ordering* or intra-step content; it catches
          enumeration drift (a step present on one side only), not content
          drift within a shared step.
    """
    r = ValidationResult()
    r.add_check("skill_layer1_parity_drift")
    root = repo_root if repo_root is not None else REPO_ROOT

    for pair in _SKILL_LAYER1_PAIRS:
        skill_path = root / pair.skill_path
        doc_path = root / pair.doc_path

        missing: list[str] = []
        if not skill_path.is_file():
            missing.append(f"Skill {pair.skill_path}")
        if not doc_path.is_file():
            missing.append(f"Layer-1 doc {pair.doc_path}")
        if missing:
            r.soft_warn(
                "skill_layer1_parity_drift",
                f"{pair.name}: {' and '.join(missing)} missing — cannot verify "
                f"Skill↔Layer-1 procedure parity.",
            )
            continue

        try:
            skill_text = skill_path.read_text(encoding="utf-8")
            doc_text = doc_path.read_text(encoding="utf-8")
        except OSError:
            r.soft_warn(
                "skill_layer1_parity_drift",
                f"{pair.name}: could not read the Skill or Layer-1 doc — cannot "
                f"verify procedure parity.",
            )
            continue

        skill_steps = _extract_step_numbers(
            skill_text, pair.skill_section, pair.skill_section_end, "headings"
        )
        doc_steps = _extract_step_numbers(
            doc_text, pair.doc_section, pair.doc_section_end, pair.doc_style
        )

        unlocatable: list[str] = []
        if skill_steps is None:
            unlocatable.append(
                f"Skill section '{pair.skill_section}' in {pair.skill_path}"
            )
        if doc_steps is None:
            unlocatable.append(
                f"Layer-1 section '{pair.doc_section}' in {pair.doc_path}"
            )
        if unlocatable:
            r.soft_warn(
                "skill_layer1_parity_drift",
                f"{pair.name}: could not locate {' and '.join(unlocatable)} — the "
                f"procedure-section heading may have changed; reconcile the "
                f"parity-check config in validate.py.",
            )
            continue
        assert skill_steps is not None and doc_steps is not None

        if not skill_steps or not doc_steps:
            empty: list[str] = []
            if not skill_steps:
                empty.append(f"Skill {pair.skill_path}")
            if not doc_steps:
                empty.append(f"Layer-1 doc {pair.doc_path}")
            r.soft_warn(
                "skill_layer1_parity_drift",
                f"{pair.name}: no procedure steps parsed from "
                f"{' and '.join(empty)} — the step-line grammar may have "
                f"changed; reconcile the parity-check config in validate.py.",
            )
            continue

        only_skill = skill_steps - doc_steps
        only_doc = doc_steps - skill_steps
        if only_skill or only_doc:
            parts: list[str] = []
            if only_skill:
                parts.append(
                    f"steps only in Skill: {{{', '.join(sorted(only_skill))}}}"
                )
            if only_doc:
                parts.append(
                    f"steps only in Layer-1 doc: {{{', '.join(sorted(only_doc))}}}"
                )
            r.soft_warn(
                "skill_layer1_parity_drift",
                f"{pair.name}: Skill ({pair.skill_path}) and Layer-1 doc "
                f"({pair.doc_path}) enumerate divergent procedure steps — "
                f"{'; '.join(parts)}. Per ADR 0044 the two must carry the same "
                f"step set; reconcile (updates flow doc → skill).",
            )

    return r


_DEPENDABOT_PR_STALE_THRESHOLD_DAYS = 7


def validate_dependabot_pr_stale(
    now: datetime | None = None,
    repo: str | None = None,
    _scanner_module: Any = None,
) -> ValidationResult:
    """Soft-warn for each open Dependabot PR aged ≥ 7 days.

    Per ADR 0080 (engine), S-0147. Companion to the boot-time surface
    in ``scan_dependabot_prs.py``: this check records per-session counts
    into ``outcome_summary_soft_warns`` so the persistent-warn 3-of-5
    surface escalates if Dependabot PRs accumulate across sessions.

    Three no-op cases (return clean, no soft-warn registered as fired):

    - ``gh`` binary not on PATH (clone hasn't installed prerequisites).
    - ``gh pr list`` failure (auth, network).
    - No open Dependabot PRs.

    The soft-warn fires per stale PR with its number, age, and a
    next-action hint, sharing the per-PR formatting with
    ``scan_dependabot_prs.py``'s ``next_action_hint``.

    Inputs:
        now: Override datetime.now(UTC). Test injection point.
        repo: Pass-through to gh -R; production omits.
        _scanner_module: Test injection for the scanner module reference;
            production resolves via lazy import.

    Returns:
        ValidationResult with ``dependabot_pr_stale`` registered as a
        check. Soft-warn fires for each open PR ≥ 7 days old.
    """
    r = ValidationResult()
    r.add_check("dependabot_pr_stale")
    if shutil.which("gh") is None:
        return r

    if _scanner_module is None:
        try:
            import importlib

            _scanner_module = importlib.import_module("scan_dependabot_prs")
        except ImportError:
            return r

    prs = _scanner_module.fetch_open_prs(repo)
    if prs is None or not prs:
        return r

    threshold = _DEPENDABOT_PR_STALE_THRESHOLD_DAYS
    for pr in prs:
        days = _scanner_module.age_days(pr["createdAt"], now=now)
        if days >= threshold:
            num = pr.get("number", "?")
            title = pr.get("title", "(no title)")
            hint = _scanner_module.next_action_hint(pr)
            r.soft_warn(
                "dependabot_pr_stale",
                f"Dependabot PR #{num} open for {days} days "
                f"(threshold {threshold}d): {title}. → {hint}. "
                "Per engine/operations/dependency-discipline.md.",
            )
    return r


def validate_uv_lock_freshness(repo_root: Path | None = None) -> ValidationResult:
    """Soft-warn when ``uv.lock`` is out of date relative to ``pyproject.toml``.

    Per ADR 0064 (S-0127; Issue #65). The lockfile is committed; whenever
    ``pyproject.toml`` is edited, ``uv lock`` must be re-run to refresh
    transitive resolution. ``uv lock --check`` is the canonical staleness
    detector — it returns non-zero when the lock is out of date.

    Three no-op cases (return clean):

    - ``pyproject.toml`` is absent (project has not adopted the lockfile
      contract; pre-S-0127 clones).
    - ``uv.lock`` is absent (same case).
    - ``uv`` binary is not on PATH (clone has not installed prerequisites
      per ADR 0050; the missing-prereq surface is `engine/STATE.md`'s
      "Infrastructure pointers" section, not this gate).

    Inputs:
        repo_root: Override the module-level REPO_ROOT. Test injection point.

    Returns:
        ValidationResult with ``uv_lock_out_of_date`` registered as a check.
        Soft-warn fires when ``uv lock --check`` exits non-zero.
    """
    r = ValidationResult()
    r.add_check("uv_lock_out_of_date")
    root = repo_root if repo_root is not None else REPO_ROOT
    pyproject = root / "pyproject.toml"
    lockfile = root / "uv.lock"
    if not pyproject.exists() or not lockfile.exists():
        return r
    if shutil.which("uv") is None:
        return r
    try:
        proc = subprocess.run(
            ["uv", "lock", "--check"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
            env=scrubbed_env(),
        )
    except (subprocess.TimeoutExpired, OSError):
        return r
    if proc.returncode != 0:
        r.soft_warn(
            "uv_lock_out_of_date",
            "uv.lock is out of date relative to pyproject.toml. Run `uv lock` "
            "from the repo root and stage the updated uv.lock alongside the "
            "pyproject.toml change. Per engine/operations/dependency-discipline.md.",
        )
    return r


# Multiplier above the tiered target that must be sustained across this many
# consecutive entries before the regression soft-warn fires. Conservative:
# single-run noise won't trigger; only sustained breach will.
_REGRESSION_BREACH_MULTIPLIER = 1.5
_REGRESSION_RUN_WINDOW = 3


def validate_runtime_phase_regression(
    history_path: Path,
    tentative_entry: dict[str, float] | None = None,
) -> ValidationResult:
    """Check the last ``_REGRESSION_RUN_WINDOW`` history entries for sustained
    per-phase target breach; emit ``validator_runtime_phase_regression``
    soft-warn for any phase that breaches in all of them.

    Per ADR 0063 (S-0126; Issue #88). Four-phase model from S-0127 (Issue #90).
    Reads ``engine/tools/validate-history.jsonl``, filters to entries that
    carry every per-phase field declared in ``VALIDATOR_PHASE_TARGETS_MS``
    (skipping pre-S-0126 entries that only carry the prior ``duration_ms``
    and pre-S-0127 entries that lack ``duration_health_probe_ms``), and
    evaluates the rolling window against
    ``VALIDATOR_PHASE_TARGETS_MS * _REGRESSION_BREACH_MULTIPLIER``.

    When ``tentative_entry`` is provided, it represents the current run's
    timings (not yet appended to the JSONL). The function reads the last
    ``_REGRESSION_RUN_WINDOW - 1`` qualifying history entries and prepends
    them to ``[tentative_entry]`` so the current run participates in the
    window. This makes the soft-warn responsive (fires on the third
    sustained-breach run, not the run after it).

    Inputs:
        history_path: Path to ``validate-history.jsonl``. Absent file is fine
            — the check returns clean (insufficient data).
        tentative_entry: Optional dict carrying every key in
            ``VALIDATOR_PHASE_TARGETS_MS`` for the current run. When None,
            the function evaluates the last ``_REGRESSION_RUN_WINDOW``
            qualifying entries from history alone.

    Returns:
        ValidationResult with up to one soft-warn per phase when all entries
        in the window breach that phase's threshold.
    """
    r = ValidationResult()
    r.add_check("validator_runtime_phase_regression")

    qualifying: list[dict[str, float]] = []
    if history_path.is_file():
        try:
            text = history_path.read_text(encoding="utf-8")
        except OSError:
            text = ""
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(entry, dict):
                continue
            if all(
                isinstance(entry.get(phase), (int, float))
                for phase in VALIDATOR_PHASE_TARGETS_MS
            ):
                qualifying.append(
                    {phase: float(entry[phase]) for phase in VALIDATOR_PHASE_TARGETS_MS}
                )

    if tentative_entry is not None:
        # Use the last (window - 1) qualifying entries + the tentative.
        window_entries = qualifying[-(_REGRESSION_RUN_WINDOW - 1) :] + [tentative_entry]
    else:
        window_entries = qualifying[-_REGRESSION_RUN_WINDOW:]

    if len(window_entries) < _REGRESSION_RUN_WINDOW:
        return r

    for phase, target in VALIDATOR_PHASE_TARGETS_MS.items():
        threshold = target * _REGRESSION_BREACH_MULTIPLIER
        if all(e[phase] > threshold for e in window_entries):
            sorted_durations = sorted(e[phase] for e in window_entries)
            median = sorted_durations[len(sorted_durations) // 2]
            r.soft_warn(
                "validator_runtime_phase_regression",
                f"Validator phase `{phase}` exceeded "
                f"{_REGRESSION_BREACH_MULTIPLIER}x target "
                f"({threshold:.0f}ms) in last {_REGRESSION_RUN_WINDOW} runs; "
                f"median {median:.1f}ms, target {target:.0f}ms. "
                f"Investigate the phase's hot path or, with evidence the "
                f"steady-state has shifted legitimately, adjust the target "
                f"in VALIDATOR_PHASE_TARGETS_MS.",
            )
    return r


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
            ``checks_run``, ``hard_fails``, ``soft_warns``,
            ``duration_structural_ms``, ``duration_graph_audit_ms``,
            ``duration_total_ms``. Pre-S-0126 entries carry the prior
            ``duration_ms`` field instead.

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
    # Walk-up .env loader (per Issue #8 / S-0049). Routine sessions and
    # any worktree-launched invocation do not have a local .env; this
    # walks up to the main repo's .env so SUPABASE_DB_URL et al. become
    # visible without requiring the parent shell to source .env. Does
    # NOT override pre-set values, so explicit `KEY=value python3 ...`
    # invocations still win.
    from load_env import load_dotenv_walk_up

    load_dotenv_walk_up()

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
        help="Run only the shared-state health probes (git repo + "
        "session-dir). Used by the SessionStart hook for sub-second "
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
    parser.add_argument(
        "--final-check",
        action="store_true",
        help="Include shutdown-time audits that read fields populated only "
        "at shutdown. (1) Engine-memory adoption checks (boot-query / "
        "diary-read soft-warns; diary-write hard-fail with "
        "acknowledgement-token escape hatch) per ADR 0091. "
        "(2) Outcome-summary unhandled-defer detection per ADR 0049 "
        "Decision 6 (S-0100, Issue #54) — fires when outcome_summary "
        "contains hedge-pattern prose without a declared "
        "next_session_handle. Invoked by the shutdown SKILL at step 7 "
        "after scan_engine_memory_activity.py and the step 7b/8 prompts "
        "have populated their fields. Pre-commit hook does NOT pass this "
        "flag so mid-session commits are not nagged.",
    )
    args = parser.parse_args(argv)

    start = time.monotonic()
    overall = ValidationResult()
    duration_structural_ms: float = 0.0
    duration_health_probe_ms: float = 0.0
    duration_graph_audit_ms: float = 0.0

    if args.health_probe_only:
        overall.merge(validate_shared_state_health())
    elif args.code_gates:
        overall.merge(validate_code_gates(args.files))
    elif args.sql_gates:
        overall.merge(validate_sql_gates(args.files))
    elif args.export_snapshot is not None:
        overall.merge(validate_graph(export_snapshot=args.export_snapshot))
    else:
        # Structural phase: in-process file/regex checks; no DB consultation,
        # no subprocess probes. validate_shared_state_health and
        # validate_issue_collisions were here pre-S-0127 but moved to the
        # health-probe phase (Issue #90 / ADR 0063 fold) because both spawn
        # subprocesses to live external systems and dominated structural
        # timing.
        overall.merge(validate_repo_structure())
        overall.merge(validate_scope_discipline())
        overall.merge(validate_routine_mode())
        overall.merge(validate_timestamp_helper_bypass())
        # Governed-doc soft-warns per ADR 0062 (S-0126; Issue #87 part b).
        # File-only / in-process; belong in the structural phase.
        overall.merge(validate_state_md_row_count())
        overall.merge(validate_adr_consequences_amendment_headers())
        overall.merge(
            validate_handoff_long_resolved_sections(
                current_session_id=session_id_from_current()
            )
        )
        # Skill↔Layer-1 procedure parity per ADR 0089 (Issue #129). File-only /
        # in-process; belongs in the structural phase.
        overall.merge(validate_skill_layer1_parity())
        # Per-session changelog entry validation per ADR 0092 (S-0198; Issue #132).
        # File-only / in-process; bounded by directory walk + jsonschema validation.
        overall.merge(validate_changelog_entries())
        overall.merge(validate_changelog_readme_governance())
        t_structural_end = time.monotonic()
        duration_structural_ms = (t_structural_end - start) * 1000

        # Health-probe phase: external-subprocess probes (repo state
        # via probe_repo.py, session-dir via probe_session_dir.py,
        # GitHub Issues via `gh issue list`, lockfile freshness via
        # `uv lock --check`). Bounded but slow and variable (network
        # involved for the gh call); budgeted separately so the
        # in-memory structural target stays meaningful.
        overall.merge(validate_shared_state_health())
        overall.merge(validate_issue_collisions())
        # Lockfile-staleness check per ADR 0064 (S-0127; Issue #65). Fits
        # health_probe rather than structural because it shells out to `uv`.
        overall.merge(validate_uv_lock_freshness())
        # Stale Dependabot PR check per ADR 0080 engine (S-0147). Fits
        # health_probe — shells out to `gh pr list`.
        overall.merge(validate_dependabot_pr_stale())
        t_health_probe_end = time.monotonic()
        duration_health_probe_ms = (t_health_probe_end - t_structural_end) * 1000

        # Graph-audit phase: live-DB consultation per ADR 0016.
        overall.merge(validate_graph())
        t_graph_end = time.monotonic()
        duration_graph_audit_ms = (t_graph_end - t_health_probe_end) * 1000

        # Shutdown audits gated to --final-check; counted toward total but
        # not separately reported (per-phase target only covers the three
        # standing phases the audit at ADR 0063 names).
        if args.final_check:
            overall.merge(validate_engine_memory_adoption())
            overall.merge(validate_outcome_summary_unhandled_defer())

    duration_total_ms = (time.monotonic() - start) * 1000

    # Per-phase regression check (default-mode only — gate flags + health-probe
    # don't run the full pipeline, so their per-phase timings would be misleading
    # if compared against the tiered targets at ADR 0063).
    if (
        not args.health_probe_only
        and not args.code_gates
        and not args.sql_gates
        and args.export_snapshot is None
    ):
        tentative_entry = {
            "duration_structural_ms": round(duration_structural_ms, 2),
            "duration_health_probe_ms": round(duration_health_probe_ms, 2),
            "duration_graph_audit_ms": round(duration_graph_audit_ms, 2),
            "duration_total_ms": round(duration_total_ms, 2),
        }
        overall.merge(
            validate_runtime_phase_regression(
                history_path=HISTORY_FILE,
                tentative_entry=tentative_entry,
            )
        )

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

    # Telemetry — emit_micros() per ADR 0058 (microsecond precision matters here
    # for same-second event ordering across rapid-fire validate runs).
    record: dict[str, Any] = {
        "timestamp": emit_micros(),
        "session_id": session_id_from_current(),
        "checks_run": overall.checks_run,
        "hard_fails": len(overall.hard_fails),
        "soft_warns": {k: len(v) for k, v in overall.soft_warns.items()},
        "duration_total_ms": round(duration_total_ms, 2),
    }
    # Per-phase fields are only meaningful for the default-mode pipeline; gate
    # flags + health-probe + export-snapshot skip the structural/graph split.
    if (
        not args.health_probe_only
        and not args.code_gates
        and not args.sql_gates
        and args.export_snapshot is None
    ):
        record["duration_structural_ms"] = round(duration_structural_ms, 2)
        record["duration_health_probe_ms"] = round(duration_health_probe_ms, 2)
        record["duration_graph_audit_ms"] = round(duration_graph_audit_ms, 2)
    append_history(record)

    if overall.hard_fails:
        return 2
    if soft_total > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
