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

A fourth responsibility (graph audit per ADR 0016) sits as a stub today;
Phase 4 fleshes it out. See validate_graph().

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
- No DB connectivity until Phase 4. validate_graph() is a stub.
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

Module contracts referenced:

- ADR 0016 — graph-construction live-validation contract; see validate_graph().
- ADR 0022 — periodic health-check telemetry contract; consumes the JSONL.
- ADR 0037 — engine/product partition; informs ENGINE_ADR_DIR / PRODUCT_ADR_DIR.
- ADR 0038 — code-discipline contract; see validate_code_gates().
- ADR 0039 — universal expression contract; the SQL/migrations row's Layer 2
  is implemented by validate_sql_gates().
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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
    r.add_check("code_gates_ruff_check")
    proc = subprocess.run(
        ["python3", "-m", "ruff", "check", *file_args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        r.hard_fail(f"ruff check failed:\n{proc.stdout}{proc.stderr}".rstrip())

    # Layer 2 gate 2: ruff format --check
    r.add_check("code_gates_ruff_format")
    proc = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", *file_args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        r.hard_fail(f"ruff format check failed:\n{proc.stdout}{proc.stderr}".rstrip())

    # Layer 2 gate 3: mypy --strict
    r.add_check("code_gates_mypy")
    proc = subprocess.run(
        ["python3", "-m", "mypy", "--strict", *file_args],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        r.hard_fail(f"mypy --strict failed:\n{proc.stdout}{proc.stderr}".rstrip())

    # Layer 2 gate 4: test presence — each non-test source file has a
    # corresponding test_<name>.py (sibling or in tests/ subdirectory).
    r.add_check("code_gates_test_presence")
    test_files: list[Path] = []
    for f in files:
        if f.name.startswith("test_") or "tests" in f.parts:
            # Test files themselves don't need their own tests
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

    Three invocation modes are mutually exclusive:

    - **Default (no flags)**: run validate_repo_structure + validate_graph.
      Aggregates results, prints summary to stdout, details to stderr,
      appends telemetry to the JSONL log.
    - **--code-gates --files <path>...**: run validate_code_gates against
      the named files. Useful for pre-commit hook integration where the
      hook passes the staged Python files. Skips repo-structure and graph
      checks; the structure run is invoked separately by the hook.
    - **--sql-gates --files <path>...**: run validate_sql_gates against
      the named SQL files. Useful for pre-commit hook integration where
      the hook passes staged migration files under
      product/seed-graph/migrations/. Mutually exclusive with --code-gates.

    Inputs:
        argv: optional argument list (for testability). When None, falls
            back to sys.argv[1:].

    Returns:
        Process exit code. 0 = clean, 1 = soft-warn only, 2 = hard-fail.

    Non-responsibilities:
        - Does not enforce mutual exclusion between --code-gates and
          --sql-gates beyond the dispatch precedence (--code-gates wins
          if both are set; the pre-commit hook invokes them in
          separate calls and never sets both).
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

    if args.code_gates:
        overall.merge(validate_code_gates(args.files))
    elif args.sql_gates:
        overall.merge(validate_sql_gates(args.files))
    else:
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
