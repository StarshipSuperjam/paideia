#!/usr/bin/env python3
"""Paideia project health-check audit producer.

Module contract — what this file is and is not.

This module aggregates audit data across five categories — the four
named in engine/operations/health-check.md (Fit, Gaps, Dead weight,
Bloat) plus MemPalace (added at S-0033 per the S-0032 MemPalace audit
plan, Improvement D) — and emits a populated markdown report at
docs/health-checks/S-NNNN.md. Per ADR 0022 (periodic project health
checks) and ADR 0042 (soft-warn lifecycle: archive is canon).

The script is invoked when the cadence trigger fires at session boot
(default cadence: 10 sessions as of S-0033, was 30 from S-0001 to S-0032
per ADR 0022 Consequences amendment; configurable in
engine/session/register_state.json via the health_check_cadence field).
It reads only committed sources for the structural audit categories;
the MemPalace audit category (added at S-0033) shells out to the local
mempalace CLI for drawer counts. Gitignored telemetry
(engine/tools/validate-history.jsonl) is consumed opportunistically when
present but the script does not depend on it.

Inputs (read):

- engine/session/archive/S-NNNN.json — per-session committed metadata.
  The new outcome_summary_soft_warns field (per ADR 0042) is the trend
  canon for Fit.
- engine/adr/*.md and product/adr/*.md — Status fields for Fit
  (Accepted / Superseded / Deprecated) and Dead-weight (long-Deprecated
  candidates).
- engine/ENGINE_LOG.md — entry counts by date for Fit fidelity check.
- product/docs/tensions.md — open tensions for Gaps; aged tensions
  (>TENSION_AGE_SESSIONS sessions open without movement) flagged.
- All .md files under REPO_ROOT (universal scan added at S-0041 per
  user direction; filesystem rglob with DEAD_WEIGHT_SKIP_PATH_PREFIXES
  + DEAD_WEIGHT_SKIP_NAMES filter) — read by audit_dead_weight (staleness
  per S-NNNN commit reference + inbound-citation count), audit_bloat
  (line counts > LARGE_DOC_LINES), audit_gaps (TBD/TODO/FIXME marker
  detection). The "scanned" set is filesystem-resident, NOT git-tracked
  — gitignored .md files are scanned too unless they fall under a
  skip-prefix.
- build_plan/*.md — read by audit_gaps for chunk-vs-archive cross-
  reference (universal scan added at S-0041).
- git log per scanned .md file — `_last_touched_session` extracts the
  highest S-NNNN reference from commit subjects + bodies for staleness
  computation.
- engine/tools/validate-history.jsonl — per-invocation telemetry for Fit
  validator-runtime drift (opportunistic; absent on fresh clones).

Outputs (written):

- docs/health-checks/S-NNNN.md — populated report following the shape
  in docs/health-checks/TEMPLATE.md, extended with the MemPalace
  section. Each of the five sections is non-empty.
- engine/session/register_state.json (non-dry-run only) —
  `bump_last_audit_session` writes the session_id to the
  `last_audit_session` field at report-emit time. Per ADR 0022
  Consequences amendment at S-0041, this field is the canonical "audit
  happened" anchor that the SessionStart hook (engine/tools/hooks/
  session-start.sh) and validate.py's `health_check_overdue` check both
  consume to compute overdue state. Best-effort: failures log to stderr
  but do not raise (the report on disk is the durable artifact; the
  field bump is advisory tracking).
- Stdout: progress messages and final report path.
- Exit code: 0 (report written), 2 (missing required input).

Edge cases:

- No archives yet (fresh repo). audit_fit reports "no trend data
  available; first audit defers calibration until structured archives
  accumulate." Report is still written; sections name the gap.
- ADR with malformed Status field. audit_fit lists it as a Fit gap;
  the validator's adr_missing_status soft-warn covers structural
  detection.
- validate-history.jsonl absent or empty. audit_fit emits "per-clone
  forensics not available in this environment" rather than failing.

Non-responsibilities:

- Does not modify any audited file. Only writes the report.
- Does not auto-commit. The session that ran the audit stages and
  commits the report per the standard session-shutdown sequence.
- Does not enforce action on findings. Reports observations and
  candidate corrective actions; the AI/user triages per
  health-check.md's three response paths (follow-on commit, next-session
  work item, new tension).

Output contract:

The written report follows docs/health-checks/TEMPLATE.md. Every section
has at least one bullet (or a "no findings" line). The Summary paragraph
is computed from the section findings — "no action across categories"
or "N findings, K corrective actions queued."

CLI invocation:

    python3 engine/tools/health_check.py --session S-0030
        Run all four audits, write docs/health-checks/S-0030.md.

    python3 engine/tools/health_check.py --session S-0030 --dry-run
        Same audits, but write to stdout instead of a file. Useful for
        manual iteration.

Module contracts referenced:

- ADR 0022 — periodic project health checks; this script is its first
  mechanical instantiation.
- ADR 0042 — soft-warn lifecycle; the trend canon this script reads.
- ADR 0041 — cascade-analysis discipline; the orphan and
  consequences-deliverable categories surface in Dead-weight and Gaps.
- ADR 0038 — code-discipline contract; this script is authored under
  the three-layer discipline.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from timestamps import parse, today  # noqa: E402  # ADR 0058


# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------

# Walk three levels up: health_check.py → tools/ → engine/ → repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

ARCHIVE_DIR = REPO_ROOT / "engine" / "session" / "archive"
ENGINE_ADR_DIR = REPO_ROOT / "engine" / "adr"
PRODUCT_ADR_DIR = REPO_ROOT / "product" / "adr"
ENGINE_LOG_PATH = REPO_ROOT / "engine" / "ENGINE_LOG.md"
TENSIONS_PATH = REPO_ROOT / "product" / "docs" / "tensions.md"
OPERATIONS_DIR = REPO_ROOT / "engine" / "operations"
VALIDATE_HISTORY_PATH = REPO_ROOT / "engine" / "tools" / "validate-history.jsonl"
REPORT_DIR = REPO_ROOT / "docs" / "health-checks"
BUILD_PLAN_DIR = REPO_ROOT / "build_plan"

# Tunable thresholds. Calibration changes are amendment-tracked under ADR 0042
# (soft-warn-lifecycle.md) for trend windows and ADR 0022 for audit thresholds.
SOFT_WARN_PERSISTENCE_BOOT_SURFACE = (3, 5)  # 3-of-last-5 archives surfaces
SOFT_WARN_PERSISTENCE_ESCALATION = 10  # consecutive archives → escalation
LARGE_DOC_LINES = 300  # >300 lines is a Bloat candidate per health-check.md
DEPRECATED_ADR_AGE_SESSIONS = 20  # Deprecated for >20 sessions without successor
TENSION_AGE_SESSIONS = 10  # Tension open >10 sessions without movement
PRODUCT_DOC_STALE_SESSIONS = 20  # tracked .md unmodified >20 sessions = stale candidate

# Universal-scan opt-out lists (per S-0041 user direction: the audit assesses
# the entire system; opt-out only when there's a structural reason). Path
# prefixes are matched against the REPO_ROOT-relative path of each .md
# file the filesystem scan returns; names are the file's basename.
DEAD_WEIGHT_SKIP_PATH_PREFIXES = (
    ".claude/",  # Claude Code harness state — not project artifacts
    "engine/tools/test_fixtures/",  # parser-tool test fixtures (per ADR 0047)
    "engine/session/archive/",  # per-session archives — staleness is by design
    "docs/health-checks/",  # historical audit reports
)
DEAD_WEIGHT_SKIP_NAMES: frozenset[str] = frozenset(
    {
        "LICENSE",
        "SECURITY.md",
        # Index files: cited but legitimately stable surface
        # (no skip — they should still surface citation count for sanity).
    }
)


# ---------------------------------------------------------------------------
# Result aggregator
# ---------------------------------------------------------------------------


@dataclass
class CategoryFindings:
    """Per-category audit findings.

    Each of the four health-check categories (Fit, Gaps, Dead weight, Bloat)
    aggregates into one CategoryFindings instance. Findings are paired with
    suggested corrective actions; the AI/user triages per health-check.md's
    response paths.

    Fields:
        observations: ordered list of (observation, action) tuples. Action
            is the suggested response or "no action" when the observation is
            informational only. Both strings render as one bullet in the
            report.
    """

    observations: list[tuple[str, str]] = field(default_factory=list)

    def add(self, observation: str, action: str = "no action") -> None:
        """Record an observation paired with a suggested action."""
        self.observations.append((observation, action))

    def is_empty(self) -> bool:
        """Return True if no observations were recorded."""
        return not self.observations


@dataclass
class HealthCheckReport:
    """Aggregator across the four audit categories.

    Mirrors the per-category structure of docs/health-checks/TEMPLATE.md.
    Each category's findings are independent; the script runs all four
    even if one returns no findings.

    Fields:
        session_id: the S-NNNN identifier the report is filed under.
        cadence: the cadence interval this audit ran against.
        last_check: previous health-check session id, or None if first.
        fit, gaps, dead_weight, bloat: per-category findings.

    Non-responsibilities:
        - Does not enforce report shape. The shape comes from
          docs/health-checks/TEMPLATE.md; emit_report is responsible
          for matching it.
    """

    session_id: str
    cadence: int = 10
    last_check: str | None = None
    fit: CategoryFindings = field(default_factory=CategoryFindings)
    gaps: CategoryFindings = field(default_factory=CategoryFindings)
    dead_weight: CategoryFindings = field(default_factory=CategoryFindings)
    bloat: CategoryFindings = field(default_factory=CategoryFindings)
    mempalace: CategoryFindings = field(default_factory=CategoryFindings)


# ---------------------------------------------------------------------------
# Archive readers
# ---------------------------------------------------------------------------


def list_archives() -> list[Path]:
    """Return all S-NNNN.json archives in numeric order.

    Returns empty list if the archive directory is absent (fresh repo
    before any session has closed).

    Non-responsibilities:
        - Does not validate archive content. read_archive is responsible
          for handling malformed JSON.
    """
    if not ARCHIVE_DIR.is_dir():
        return []
    return sorted(ARCHIVE_DIR.glob("S-[0-9][0-9][0-9][0-9].json"))


def read_archive(path: Path) -> dict[str, object]:
    """Parse a single archive file; return its dict.

    Returns an empty dict on JSON parse failure rather than raising;
    the caller's audit treats malformed archives as "data not available
    for this session" and continues.
    """
    try:
        loaded = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    if isinstance(loaded, dict):
        return loaded
    return {}


def soft_warns_from_archive(archive: Mapping[str, object]) -> dict[str, int]:
    """Extract the structured soft-warn counts from an archive dict.

    Returns the outcome_summary_soft_warns block per ADR 0042 if present,
    or an empty dict if the archive predates the structured field. Key
    type validation: only string keys with int values are returned.
    """
    block = archive.get("outcome_summary_soft_warns")
    if not isinstance(block, dict):
        return {}
    return {k: v for k, v in block.items() if isinstance(k, str) and isinstance(v, int)}


# ---------------------------------------------------------------------------
# Fit audit
# ---------------------------------------------------------------------------


def audit_fit(archives: list[Path]) -> CategoryFindings:
    """Audit machinery-vs-production alignment.

    Reads the last K archives (where K is bounded by the cadence interval
    or the available archive count, whichever is smaller) and reports:

    - Validate.py soft-warn distribution: which categories are firing
      most, which are persistent (per ADR 0042 boot-surface threshold).
    - ENGINE_LOG fidelity: every closed session in archive/ has a
      corresponding entry. (Lightweight check: looks for the session id
      string in ENGINE_LOG.md; misses can be intentional but signal
      drift if many.)
    - ADR statuses: counts of Accepted / Superseded / Deprecated; flags
      Accepted ADRs that are referenced by no doc (per ADR 0041
      adr_back_reference_orphan).
    - validate-history.jsonl runtime drift: opportunistic — if the file
      exists and parses, surfaces median runtime trend.

    Returns CategoryFindings with one observation per finding.

    Non-responsibilities:
        - Does not query MemPalace. The MemPalace-recall observation is
          a manual augmentation per docs/health-checks/README.md.
        - Does not parse archive prose outcome_summary. Only the
          structured outcome_summary_soft_warns field is mechanical
          input.
    """
    findings = CategoryFindings()

    # Soft-warn distribution across recent archives (per ADR 0042).
    # Walk archives in reverse-chronological order; bounded to a 30-archive
    # window (sufficient even under the cadence-10 default at S-0033 — three
    # full cycles of trend data per audit).
    recent = archives[-30:]
    if not recent:
        findings.add(
            "No closed sessions yet; no soft-warn trend data available.",
            "Defer Fit calibration until structured archives accumulate.",
        )
    else:
        category_persistence: Counter[str] = Counter()
        archives_with_structured_data = 0
        for archive_path in recent:
            archive = read_archive(archive_path)
            sw = soft_warns_from_archive(archive)
            if sw:
                archives_with_structured_data += 1
                for category, count in sw.items():
                    if count > 0:
                        category_persistence[category] += 1

        if archives_with_structured_data == 0:
            findings.add(
                f"None of the {len(recent)} recent archives carry the structured "
                "outcome_summary_soft_warns field (ADR 0042's canonical trend source).",
                "Pre-ADR-0042 archives lack the field by design; subsequent sessions "
                "populate it. Recheck after S-0040 or thereabouts.",
            )
        else:
            persistent_count = sum(
                1
                for cat, hits in category_persistence.items()
                if hits >= SOFT_WARN_PERSISTENCE_ESCALATION
            )
            for category, hits in category_persistence.most_common():
                if hits >= SOFT_WARN_PERSISTENCE_ESCALATION:
                    findings.add(
                        f"Soft-warn `{category}` persistent across {hits} of "
                        f"{archives_with_structured_data} structured archives "
                        f"(threshold: {SOFT_WARN_PERSISTENCE_ESCALATION} for escalation).",
                        "Escalate per soft-warn-lifecycle.md: promote to hard-fail, "
                        "accept and annotate, or address inline.",
                    )
                elif hits >= SOFT_WARN_PERSISTENCE_BOOT_SURFACE[0]:
                    findings.add(
                        f"Soft-warn `{category}` recurring across {hits} of "
                        f"{archives_with_structured_data} structured archives.",
                        "Watch — escalation criterion fires at "
                        f"{SOFT_WARN_PERSISTENCE_ESCALATION} consecutive.",
                    )
            if persistent_count == 0 and category_persistence:
                findings.add(
                    "No soft-warn categories have reached the escalation threshold; "
                    "current discipline is holding.",
                    "no action",
                )

    # ENGINE_LOG fidelity check.
    if not ENGINE_LOG_PATH.is_file():
        findings.add(
            "engine/ENGINE_LOG.md is absent.",
            "Author the file (validate.py engine_required check would "
            "hard-fail on this; surfacing as a Fit issue is redundant).",
        )
    else:
        engine_log_text = ENGINE_LOG_PATH.read_text()
        missing_session_entries: list[str] = []
        for archive_path in archives:
            sid = archive_path.stem  # "S-NNNN"
            if sid not in engine_log_text:
                missing_session_entries.append(sid)
        if missing_session_entries:
            sample = ", ".join(missing_session_entries[:5])
            findings.add(
                f"{len(missing_session_entries)} closed session(s) have no "
                f"reference in ENGINE_LOG.md (e.g., {sample}).",
                "Verify each: intentional omission (operational session, "
                "no material engine change) vs. drift (material change "
                "shipped without log entry).",
            )

    # ADR status distribution.
    adr_status_counts: Counter[str] = Counter()
    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if not adr_dir.is_dir():
            continue
        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            text = adr_file.read_text()
            match = re.search(r"^[\s*\-]*Status[\s*]*:[\s*]*(.+?)$", text, re.MULTILINE)
            if not match:
                continue
            status_text = re.sub(r"[*_`]", "", match.group(1)).strip().lower()
            for keyword in ("superseded", "deprecated", "accepted", "proposed"):
                if keyword in status_text:
                    adr_status_counts[keyword] += 1
                    break

    if adr_status_counts:
        summary = ", ".join(
            f"{count} {status}" for status, count in sorted(adr_status_counts.items())
        )
        findings.add(
            f"ADR collection: {summary}.",
            "no action",
        )

    # validate-history.jsonl runtime drift (opportunistic).
    if VALIDATE_HISTORY_PATH.is_file():
        try:
            lines = VALIDATE_HISTORY_PATH.read_text().splitlines()
            durations = []
            for line in lines:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(rec, dict) and isinstance(
                    rec.get("duration_ms"), (int, float)
                ):
                    durations.append(float(rec["duration_ms"]))
            if durations:
                median = sorted(durations)[len(durations) // 2]
                findings.add(
                    f"Validator runtime: median {median:.0f}ms across "
                    f"{len(durations)} per-clone invocations (validate-history.jsonl).",
                    "Phase-0+ structural-only checks should stay under ~500ms; "
                    "investigate if median exceeds.",
                )
        except OSError:
            pass

    if findings.is_empty():
        findings.add(
            "No Fit findings surfaced by mechanical audit. Augment with manual "
            "MemPalace-recall observation per docs/health-checks/README.md.",
            "no action",
        )
    return findings


# ---------------------------------------------------------------------------
# Gaps audit
# ---------------------------------------------------------------------------


def audit_gaps() -> CategoryFindings:
    """Audit what's missing that should be there.

    **Universal-scan extension at S-0041** per user direction (every audit
    category should assess the entire system, not opt-in subsets). The
    prior design only scanned tensions.md + ADR Consequences — the
    extended scan adds two universal signals:

    - **TBD/TODO/FIXME markers** in any tracked .md file. These mark
      author-acknowledged gaps that may have been forgotten.
    - **Unstarted build_plan/ chunks**: build_plan/*.md files that have
      not been referenced by any closed session's archive (per session_id
      mention in archive outcome_summary fields).

    Plus the existing tension and ADR-Consequences signals:
    - product/docs/tensions.md for tensions open >TENSION_AGE_SESSIONS
      sessions without movement (heuristic: counts session-id mentions;
      an "Updated:" or "Resolved:" line counts as movement).
    - ADR Consequences sections for promised-but-not-delivered work
      (mirrors validator's adr_consequences_deliverable_audit category).

    Returns CategoryFindings.
    """
    findings = CategoryFindings()

    # Aged tensions in product/docs/tensions.md.
    if TENSIONS_PATH.is_file():
        tensions_text = TENSIONS_PATH.read_text()
        # Find each "OQ-XXX" header. Heuristic: count it as aged if it
        # appears with an "Added at S-NNNN" marker more than TENSION_AGE_SESSIONS
        # sessions before the most recent archive, and no "Resolved:" or
        # "Updated:" line nearby.
        oq_pattern = re.compile(
            r"##\s*(OQ-[A-Z0-9-]+).*?(?=^##\s*OQ-|\Z)", re.MULTILINE | re.DOTALL
        )
        archives = list_archives()
        latest_session = 0
        if archives:
            latest_match = re.match(r"S-(\d{4})", archives[-1].stem)
            if latest_match:
                latest_session = int(latest_match.group(1))

        aged: list[str] = []
        for match in oq_pattern.finditer(tensions_text):
            oq_text = match.group(0)
            oq_id = match.group(1)
            added_match = re.search(r"[Aa]dded.*?S-(\d{4})", oq_text)
            if not added_match:
                continue
            added_session = int(added_match.group(1))
            age = latest_session - added_session
            if age <= TENSION_AGE_SESSIONS:
                continue
            if re.search(r"[Rr]esolved|[Uu]pdated|[Ww]ithdrawn|[Ss]ettled", oq_text):
                continue
            aged.append(f"{oq_id} (added S-{added_session:04d}, age {age} sessions)")

        if aged:
            findings.add(
                f"{len(aged)} aged tension(s) in product/docs/tensions.md: "
                + "; ".join(aged),
                "Per-tension: re-evaluate whether actionable now. If yes, queue "
                "as next session's work or absorb into a downstream doc.",
            )

    # ADR Consequences-deliverable audit (heuristic regex).
    deliverable_pattern = re.compile(
        r"(?:anticipated|lands?|expected|targeted)\s+"
        r"(?:around\s+|at\s+|in\s+)?S-(\d{4})",
        re.IGNORECASE,
    )
    archives_closed = {p.stem for p in list_archives()}
    promised_but_absent: list[str] = []
    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if not adr_dir.is_dir():
            continue
        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            text = adr_file.read_text()
            consequences_match = re.search(
                r"^##\s+Consequences\s*$.*?(?=^##\s+|\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )
            if not consequences_match:
                continue
            cons_text = consequences_match.group(0)
            for m in deliverable_pattern.finditer(cons_text):
                target_session = f"S-{m.group(1)}"
                if target_session not in archives_closed:
                    continue
                # The target session is closed. Check if any deliverable
                # path mentioned in the ADR text exists. Heuristic: look
                # for backtick-wrapped paths or markdown-link paths to .py
                # / .md / .sql files in the same line as the deliverable
                # mention.
                line = cons_text[
                    max(0, m.start() - 200) : min(len(cons_text), m.end() + 200)
                ]
                path_candidates = re.findall(r"`([\w./_-]+\.(?:py|md|sql|json))`", line)
                path_candidates += re.findall(
                    r"\]\(([\w./_-]+\.(?:py|md|sql|json))\)", line
                )
                # Resolve each path against both repo root AND the ADR file's
                # directory (relative-link convention in markdown). Mirrors
                # validate.py's validate_adr_consequences_deliverable_audit.
                missing_paths = []
                for p in path_candidates:
                    if (REPO_ROOT / p).exists():
                        continue
                    if (adr_file.parent / p).resolve().exists():
                        continue
                    missing_paths.append(p)
                if missing_paths:
                    rel = adr_file.relative_to(REPO_ROOT)
                    promised_but_absent.append(
                        f"{rel} promised {missing_paths} for {target_session} (closed)"
                    )

    if promised_but_absent:
        findings.add(
            f"{len(promised_but_absent)} ADR Consequences promise(s) not delivered: "
            + "; ".join(promised_but_absent[:5])
            + ("; ..." if len(promised_but_absent) > 5 else ""),
            "Per ADR: land the deliverable, amend the Consequences section to "
            "remove the promise, or document the deferral with a new expected "
            "session.",
        )

    # Universal scan: TBD / TODO / FIXME markers in tracked .md files.
    all_md = _list_scanned_md_files()
    marker_pattern = re.compile(r"\b(TBD|TODO|FIXME)\b")
    files_with_markers: list[tuple[str, int]] = []
    for md_path in all_md:
        if md_path.name in DEAD_WEIGHT_SKIP_NAMES:
            continue
        # Skip files where these tokens are part of the content's domain
        # (e.g., docs that describe the markers themselves). The S-0041
        # acceptable-list is files that reference the tokens definitionally
        # rather than as live gaps. Keep narrow to start.
        try:
            md_rel_str = str(md_path.relative_to(REPO_ROOT))
        except ValueError:
            continue
        if (
            md_rel_str
            in {
                "engine/operations/session-shutdown-sequence.md",  # describes the audit-side-discoveries marker list
                "HANDOFF.md",  # historical entries that include the marker tokens
                "engine/tools/test_audit_side_discoveries.py",  # not .md; defensive
                "engine/operations/expression-contract-instantiation.md",  # TBD is the convention's own decide-by-pattern marker
                "engine/ENGINE_LOG.md",  # historical narrative referring to the marker list as audit input
                "engine/adr/0043-hook-architecture.md",  # describes the post-state-edit hook's marker-detection list
            }
        ):
            continue
        try:
            text = md_path.read_text()
        except OSError:
            continue
        matches = marker_pattern.findall(text)
        if matches:
            files_with_markers.append((md_rel_str, len(matches)))
    if files_with_markers:
        files_with_markers.sort(key=lambda x: -x[1])
        listing = ", ".join(f"{p} ({n})" for p, n in files_with_markers[:8])
        more = (
            f"; +{len(files_with_markers) - 8} more"
            if len(files_with_markers) > 8
            else ""
        )
        findings.add(
            f"{len(files_with_markers)} tracked .md file(s) with TBD/TODO/FIXME "
            f"markers: {listing}{more}",
            "Per file: each marker is an author-acknowledged gap. Either close "
            'the gap inline (default per CLAUDE.md "Default to fix-in-context"), '
            "or replace the marker with an explicit decide-by trigger naming the "
            "phase or session that resolves it.",
        )

    # Universal scan: build_plan/ chunks not yet started.
    if BUILD_PLAN_DIR.is_dir():
        archives = list_archives()
        archive_text = " ".join(
            archive_path.read_text()
            for archive_path in archives
            if archive_path.is_file()
        )
        unreferenced_chunks: list[str] = []
        for chunk_file in sorted(BUILD_PLAN_DIR.glob("*.md")):
            if chunk_file.name in {"README.md", "MANIFEST.md"}:
                continue
            if chunk_file.name not in archive_text:
                unreferenced_chunks.append(chunk_file.name)
        if unreferenced_chunks:
            findings.add(
                f"{len(unreferenced_chunks)} build_plan/ chunk(s) not yet referenced "
                f"by any closed session's archive: {', '.join(unreferenced_chunks)}",
                "Per chunk: confirm phase sequencing per ROADMAP. Chunks for "
                "later phases are expected to be unreferenced; chunks whose "
                "phase has opened without consumption are gaps.",
            )

    # Cascade-discipline.md commitment: orphan-OK list audit at health-check
    # time. Mechanized at S-0099 per Issue #51 — the periodic-audit promise at
    # cascade-discipline.md:88 is now backed by mechanism rather than posture.
    orphan_ok_findings = audit_orphan_ok_list()
    findings.observations.extend(orphan_ok_findings.observations)

    if findings.is_empty():
        findings.add(
            "No Gaps surfaced by mechanical audit.",
            "no action",
        )
    return findings


def _resolve_current_session_id() -> str | None:
    """Return register_state.json's last_claimed S-NNNN, or None if unavailable.

    Returns None when the register file is missing, malformed, or carries a
    last_claimed value that is not a well-formed S-NNNN string. The orphan-OK
    audit treats None as "session-id triggers cannot be evaluated" and surfaces
    those triggers as informational findings rather than silently passing.
    """
    register_path = REPO_ROOT / "engine" / "session" / "register_state.json"
    try:
        register = json.loads(register_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    last_claimed = register.get("last_claimed") if isinstance(register, dict) else None
    if isinstance(last_claimed, str) and re.match(r"^S-\d{4}$", last_claimed):
        return last_claimed
    return None


def _resolve_current_phase_num() -> int | None:
    """Return the highest opened phase number per engine/STATE.md, or None.

    Parses the Current-phase row of STATE.md's headline table. Returns None
    when STATE.md is absent or the row cannot be parsed; the orphan-OK audit
    treats None as "phase triggers cannot be evaluated" and surfaces those
    triggers as informational findings.

    A phase is the "current" phase whether it is open or closed — closed
    phases have been reached. A trigger "revisit at Phase N" fires stale
    when the current phase number is >= N.
    """
    state_path = REPO_ROOT / "engine" / "STATE.md"
    try:
        text = state_path.read_text()
    except OSError:
        return None
    # Anchored to the headline-table "Current phase" row; the row's value cell
    # leads with `**Phase N — <description> (closed; ...)` per STATE.md
    # convention. The first match is canonical; downstream prose may mention
    # other phase numbers (Phase 6 master plan, Phase 8 cost-cap, etc.).
    match = re.search(
        r"\*\*Current phase\*\*\s*\|\s*\*\*Phase\s+(\d+)",
        text,
    )
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def audit_orphan_ok_list() -> CategoryFindings:
    """Audit ADR `Orphan-OK:` annotations for stale revisit-by triggers.

    Walks engine/adr/*.md and product/adr/*.md. For each Accepted ADR
    carrying an `- **Orphan-OK:** <reason>; revisit at <trigger>` annotation
    (per cascade-discipline.md convention), parses the trigger and surfaces
    findings when:

    - **Session-ID trigger** (`S-NNNN` shape): the trigger session has been
      reached or passed (compared against register_state.json:last_claimed).
    - **Phase trigger** (`Phase N` / `phase_N` shape): the named phase has
      been reached or passed (compared against engine/STATE.md's Current
      phase row).
    - **Malformed trigger**: the trigger string is neither shape; surfaced
      as an informational finding to nudge annotation repair.
    - **Cannot evaluate**: when register_state.json or STATE.md isn't
      parseable, surface an informational finding rather than silently
      passing — the audit's purpose is to prevent silent staleness.

    Cross-doc handshake closed: cascade-discipline.md line 88 commits the
    periodic health check to this audit; pre-S-0099 the commitment was
    posture-only and the S-0097 cold-context probe surfaced the gap.

    Pre-condition:
        ENGINE_ADR_DIR / PRODUCT_ADR_DIR exist on disk (or absent → empty
        findings — fresh repos before any ADR has been authored).

    Post-condition:
        Returns CategoryFindings with one observation per stale or malformed
        annotation. Empty findings when no Accepted ADR carries an
        `Orphan-OK:` line.

    Error modes:
        - ADR file unreadable (OSError): skipped silently (consistent with
          audit_gaps()'s existing OSError handling).
        - register_state.json / STATE.md unreadable: surfaced as
          "cannot evaluate" findings rather than raising.
        - Annotation regex mismatch: not surfaced (only well-formed
          annotations participate; malformed annotations that DO match the
          basic shape but carry an unrecognized trigger surface separately).

    Non-responsibilities:
        - Does not modify ADR files. Author repair is an out-of-band action
          surfaced by the finding's recommended action clause.
        - Does not enforce a "stale annotation that has not been
          re-annotated for >N cadence cycles" surface. cascade-discipline.md
          line 90 names this as a future criterion; one finding per stale
          annotation is sufficient for the first-exercise contract.
    """
    findings = CategoryFindings()

    # Trigger captures rest-of-line so multi-word forms like `Phase 6` are
    # caught alongside compact forms like `S-0050` or `phase_6`.
    annotation_re = re.compile(
        r"^\s*-\s*\*\*Orphan-OK:\*\*\s*(?P<reason>[^;]+);\s*"
        r"revisit at\s+(?P<trigger>[^\n]+?)\s*$",
        re.MULTILINE,
    )
    accepted_re = re.compile(
        r"^\s*-?\s*\*\*Status:\*\*\s*Accepted",
        re.MULTILINE | re.IGNORECASE,
    )
    session_trigger_re = re.compile(r"^S-(\d+)$")
    phase_trigger_re = re.compile(r"^[Pp]hase[\s_-]*(\d+)$")

    current_session_id = _resolve_current_session_id()
    current_phase_num = _resolve_current_phase_num()
    current_session_num: int | None = None
    if current_session_id is not None:
        try:
            current_session_num = int(current_session_id.split("-")[1])
        except (IndexError, ValueError):
            current_session_num = None

    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if not adr_dir.is_dir():
            continue
        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            try:
                content = adr_file.read_text()
            except OSError:
                continue
            if not accepted_re.search(content):
                continue
            for match in annotation_re.finditer(content):
                trigger = match.group("trigger").strip().rstrip(",.;:")
                reason = match.group("reason").strip()
                rel = adr_file.relative_to(REPO_ROOT)

                session_match = session_trigger_re.match(trigger)
                if session_match:
                    trigger_num = int(session_match.group(1))
                    if current_session_num is None:
                        findings.add(
                            f"{rel}: Orphan-OK trigger `{trigger}` cannot be "
                            "evaluated (register_state.json missing or "
                            "last_claimed malformed)",
                            "Investigate register_state.json; manual fallback "
                            "to verify the trigger.",
                        )
                    elif current_session_num >= trigger_num:
                        findings.add(
                            f"{rel}: Orphan-OK revisit-by trigger `{trigger}` "
                            f"has passed (current session: {current_session_id}). "
                            f"Reason: {reason}",
                            "Re-evaluate the ADR per cascade-discipline.md: "
                            "either remove the annotation, update the trigger, "
                            "or supersede/deprecate the ADR.",
                        )
                    continue

                phase_match = phase_trigger_re.match(trigger)
                if phase_match:
                    trigger_phase = int(phase_match.group(1))
                    if current_phase_num is None:
                        findings.add(
                            f"{rel}: Orphan-OK trigger `{trigger}` cannot be "
                            "evaluated (STATE.md Current-phase row not parseable)",
                            "Investigate STATE.md; manual fallback to verify "
                            "the trigger.",
                        )
                    elif current_phase_num >= trigger_phase:
                        findings.add(
                            f"{rel}: Orphan-OK revisit-by trigger `{trigger}` "
                            f"has been reached (current phase: "
                            f"{current_phase_num}). Reason: {reason}",
                            "Re-evaluate the ADR per cascade-discipline.md.",
                        )
                    continue

                findings.add(
                    f"{rel}: Orphan-OK trigger `{trigger}` is neither S-NNNN "
                    "nor Phase-N shape (malformed)",
                    "Repair the annotation per cascade-discipline.md "
                    "convention: `- **Orphan-OK:** <reason>; revisit at "
                    "<S-NNNN-or-Phase-N>`.",
                )

    return findings


# ---------------------------------------------------------------------------
# Dead-weight audit
# ---------------------------------------------------------------------------


def _list_scanned_md_files() -> list[Path]:
    """Return all .md files under REPO_ROOT in audit scope.

    Walks the filesystem under REPO_ROOT (not `git ls-files`, which would
    require a real git repo and break the synthetic-repo test fixtures).
    Filters out paths starting with DEAD_WEIGHT_SKIP_PATH_PREFIXES.

    Returns absolute paths; empty list on filesystem error.
    """
    paths: list[Path] = []
    try:
        for md_path in REPO_ROOT.rglob("*.md"):
            try:
                rel = str(md_path.relative_to(REPO_ROOT))
            except ValueError:
                continue
            if any(rel.startswith(p) for p in DEAD_WEIGHT_SKIP_PATH_PREFIXES):
                continue
            paths.append(md_path)
    except OSError:
        return []
    return sorted(paths)


def _last_touched_session(path: Path) -> int | None:
    """Return the highest S-NNNN session id from the file's git log, or None.

    Reads the full git log of the path (not just -1) and extracts every
    S-NNNN reference from commit subjects + bodies. The max is the most
    recent session that touched the file — even if the literal latest
    commit didn't carry an S-NNNN tag (a manual fixup commit, for example).

    Returns None when git fails or no S-NNNN reference appears in any
    commit touching the path.
    """
    try:
        rel = path.relative_to(REPO_ROOT)
    except ValueError:
        return None
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(REPO_ROOT),
                "log",
                "--format=%s%n%b%n----",
                "--",
                str(rel),
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    if result.returncode != 0:
        return None
    matches = re.findall(r"\bS-(\d{4})\b", result.stdout)
    if not matches:
        return None
    return max(int(m) for m in matches)


def _count_inbound_citations(path: Path, all_md_files: list[Path]) -> int:
    """Count distinct .md files (other than path itself) that mention path.name.

    Heuristic: filename match. False positives possible if two files share
    a basename in different directories; rare in this project (filenames
    are reasonably unique). False negatives possible if the file is cited
    by full-path-with-different-basename — also rare.

    Returns 0 if uncited.
    """
    name = path.name
    count = 0
    for other in all_md_files:
        if other == path:
            continue
        try:
            if name in other.read_text():
                count += 1
        except OSError:
            continue
    return count


def audit_dead_weight() -> CategoryFindings:
    """Audit what no longer earns its keep.

    **Universal-scan rewrite at S-0041** per user direction at the catch-up
    audit close (the prior opt-in design only scanned ADRs + operations docs
    + ideation.md, missing prep-paideia-prompt-pack.md which had been stale
    for 24 sessions in product/docs/). The new design scans every .md file
    found by filesystem walk under REPO_ROOT (with skip-prefix filter)
    and applies two signals universally — staleness (no S-NNNN
    commit reference newer than PRODUCT_DOC_STALE_SESSIONS sessions ago) and
    inbound-citation count (count of other .md files mentioning this file's
    name). Files that hit either signal land in the report; the AI/user
    triages at audit-read time. Opt-out via DEAD_WEIGHT_SKIP_PATH_PREFIXES
    + DEAD_WEIGHT_SKIP_NAMES below.

    Plus a Deprecated-ADR special-purpose check the prior design carried
    (kept because it applies category-specific semantics that universal
    scanning doesn't capture):

    - **Deprecated ADRs** (Status: Deprecated for >DEPRECATED_ADR_AGE_SESSIONS
      sessions without successor): structural archival candidates.

    (Pre-S-0083 there was a second special-purpose check for unconsumed
    ideation.md entries; ideation.md retired at S-0083 per Issue #29 and
    its function migrated to GitHub Issues per ADR 0048.)

    Returns CategoryFindings.

    Non-responsibilities:
        - Does not call git for stale-worktree detection. The
          `engine/tools/sweep_worktrees.sh` utility handles that on demand.
        - Does not enforce removal. Surfaces candidates; the AI/user
          decides per-finding.
        - Does not parse .py / .json / .yaml — staleness for non-.md
          artifacts is out of scope (would surface every test fixture).
    """
    findings = CategoryFindings()

    # Deprecated ADRs (special-purpose check; kept from pre-S-0041 design).
    deprecated: list[str] = []
    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if not adr_dir.is_dir():
            continue
        for adr_file in sorted(adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md")):
            text = adr_file.read_text()
            status_match = re.search(
                r"^[\s*\-]*Status[\s*]*:[\s*]*(.+?)$", text, re.MULTILINE
            )
            if not status_match:
                continue
            status = re.sub(r"[*_`]", "", status_match.group(1)).strip().lower()
            if status.startswith("deprecated"):
                deprecated.append(str(adr_file.relative_to(REPO_ROOT)))
    if deprecated:
        findings.add(
            f"{len(deprecated)} Deprecated ADR(s): " + ", ".join(deprecated),
            "Per ADR: confirm successor (if any) is in force; consider "
            "_archive/ move if reasoning is fully redistributed.",
        )

    # Universal scan over all tracked .md files.
    all_md = _list_scanned_md_files()
    archives = list_archives()
    latest_session_int = 0
    if archives:
        latest_match = re.match(r"S-(\d{4})", archives[-1].stem)
        if latest_match:
            latest_session_int = int(latest_match.group(1))

    stale_files: list[tuple[str, int]] = []
    uncited_files: list[str] = []
    for md_path in all_md:
        try:
            rel = str(md_path.relative_to(REPO_ROOT))
        except ValueError:
            continue
        if md_path.name in DEAD_WEIGHT_SKIP_NAMES:
            continue
        # Staleness: last-touched session per git log; >threshold = stale.
        if latest_session_int > 0:
            last_touched = _last_touched_session(md_path)
            if last_touched is not None:
                age = latest_session_int - last_touched
                if age > PRODUCT_DOC_STALE_SESSIONS:
                    stale_files.append((rel, age))
        # Inbound citations: count of OTHER .md files mentioning name.
        # Skip ADR files because the validator's adr_back_reference_orphan
        # check (per ADR 0041) covers the same ground with sharper semantics.
        if "/adr/" not in rel:
            citations = _count_inbound_citations(md_path, all_md)
            if citations == 0:
                uncited_files.append(rel)

    if stale_files:
        listing = "; ".join(f"{p} (age {n} sessions)" for p, n in stale_files)
        findings.add(
            f"{len(stale_files)} tracked .md file(s) with no S-NNNN commit "
            f"reference in >{PRODUCT_DOC_STALE_SESSIONS} sessions: {listing}",
            "Per file: confirm load-bearing (some files are legitimately "
            "stable — MISSION.md / LICENSE / older ADRs); retire stale ones "
            "with explicit disposition (mark historical with banner, or "
            "absorb into a current artifact). The S-0041 prep-paideia-prompt-"
            "pack disposition is the canonical pattern — close consumed "
            "sessions in-place with cross-refs, name explicit decide-by "
            "triggers for any genuinely-open prompts.",
        )

    if uncited_files:
        findings.add(
            f"{len(uncited_files)} tracked .md file(s) with zero inbound "
            f"citations from other .md files: {', '.join(uncited_files)}",
            "Per file: confirm load-bearing (some files are entry points "
            "that nothing else cites — README.md, MISSION.md); retire "
            "genuinely-orphaned content with explicit disposition.",
        )

    # (Unconsumed-ideation-entries check retired at S-0083 per Issue #29 —
    # ideation.md retired in the same session; ideas now go to GitHub Issues
    # with the `enhancement` label per ADR 0048.)

    if findings.is_empty():
        findings.add(
            "No Dead-weight surfaced by mechanical audit.",
            "no action",
        )
    return findings


# ---------------------------------------------------------------------------
# Bloat audit
# ---------------------------------------------------------------------------


def audit_bloat() -> CategoryFindings:
    """Audit what's grown past its purpose.

    **Universal-scan rewrite at S-0041** per user direction (the prior
    opt-in design only scanned engine/operations/, missing oversized files
    elsewhere). The new design scans every .md file under REPO_ROOT
    (filtered through DEAD_WEIGHT_SKIP_PATH_PREFIXES + DEAD_WEIGHT_SKIP_NAMES)
    and flags any over LARGE_DOC_LINES. The AI/user triages at audit-read
    time — ADRs over 300 lines often reflect a decision that became three;
    docs over 300 lines often reflect multiple concerns to split.

    Plus the existing duration-trend signal:
    - Recent archive durations (closed_at - started_at) for shutdown
      overhead; flags upward trend.

    Returns CategoryFindings.
    """
    findings = CategoryFindings()

    # Universal scan: every tracked .md file > LARGE_DOC_LINES.
    all_md = _list_scanned_md_files()
    large_docs: list[tuple[str, int]] = []
    for md_path in all_md:
        if md_path.name in DEAD_WEIGHT_SKIP_NAMES:
            continue
        try:
            line_count = len(md_path.read_text().splitlines())
        except OSError:
            continue
        if line_count > LARGE_DOC_LINES:
            try:
                rel = str(md_path.relative_to(REPO_ROOT))
            except ValueError:
                continue
            large_docs.append((rel, line_count))
    if large_docs:
        large_docs.sort(key=lambda x: -x[1])  # largest first
        listing = ", ".join(f"{name} ({n} lines)" for name, n in large_docs)
        findings.add(
            f"{len(large_docs)} tracked .md file(s) over {LARGE_DOC_LINES} lines: {listing}.",
            "Per doc: split if multiple concerns; accept if single coherent "
            "topic. ADRs over the threshold often reflect a single decision "
            "that became three; ops docs over the threshold often reflect "
            "multiple concerns ripe for splitting.",
        )

    # Session duration trend (recent archives).
    archives = list_archives()
    recent_durations: list[float] = []
    for archive_path in archives[-30:]:
        archive = read_archive(archive_path)
        started = archive.get("started_at")
        closed = archive.get("closed_at")
        if not (isinstance(started, str) and isinstance(closed, str)):
            continue
        try:
            # Smoking-gun fix per ADR 0058 — the helper concentrates the
            # legacy-shape knowledge that this site previously hand-rolled.
            t0 = parse(started)
            t1 = parse(closed)
        except ValueError:
            continue
        delta_minutes = (t1 - t0).total_seconds() / 60.0
        if 0 < delta_minutes < 24 * 60:  # plausible session length
            recent_durations.append(delta_minutes)

    if recent_durations:
        median = sorted(recent_durations)[len(recent_durations) // 2]
        findings.add(
            f"Recent session duration: median {median:.0f} minutes across "
            f"{len(recent_durations)} archives.",
            "Compare to productive-work share; investigate if shutdown overhead "
            "begins exceeding productive work.",
        )

    if findings.is_empty():
        findings.add(
            "No Bloat surfaced by mechanical audit.",
            "no action",
        )
    return findings


# ---------------------------------------------------------------------------
# MemPalace audit (added at S-0033 per the S-0032 MemPalace audit plan)
# ---------------------------------------------------------------------------


def _resolve_mempalace_binary() -> str | None:
    """Resolve the mempalace CLI binary path.

    Mirrors the resolution pattern in engine/tools/hooks/mempalace-hook-wrapper.sh
    and post-adr-write.sh (per ADR 0043): try PATH, fall back to the
    user-scope install at ~/Library/Python/3.9/bin/mempalace. Returns
    None if neither resolves.
    """
    on_path = shutil.which("mempalace")
    if on_path:
        return on_path
    fallback = Path.home() / "Library" / "Python" / "3.9" / "bin" / "mempalace"
    if fallback.is_file() and os.access(fallback, os.X_OK):
        return str(fallback)
    return None


def _run_mempalace(binary: str, *args: str) -> str | None:
    """Run mempalace CLI; return stdout or None on error.

    Captures stderr but discards it. Best-effort; the audit gracefully
    handles failures by returning None and the caller skips the
    corresponding finding. 30-second timeout — the CLI is fast against a
    local palace.
    """
    try:
        result = subprocess.run(
            [binary, *args],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.SubprocessError, OSError):
        pass
    return None


def _count_adrs() -> int:
    """Count ADR files across engine/adr/ and product/adr/."""
    count = 0
    for adr_dir in (ENGINE_ADR_DIR, PRODUCT_ADR_DIR):
        if adr_dir.is_dir():
            count += sum(1 for _ in adr_dir.glob("[0-9][0-9][0-9][0-9]-*.md"))
    return count


def audit_mempalace(archives: list[Path]) -> CategoryFindings:
    """Audit the project's MemPalace usage health.

    Added at S-0033 per the S-0032 MemPalace audit plan (Improvement D).
    Closes the loop from the audit's central finding: the project's
    MemPalace usage was previously evaluated only by manual observation,
    and the S-0030 audit's "1 decision drawer for 42 ADRs" headline was
    structurally wrong because it counted by room name only. This audit
    category provides a mechanical view of MemPalace state every cadence.

    Reports:

    - Decisions-room drawer count vs ADR count. Per the room-targeting
      conventions added at S-0032 (engine/operations/mempalace-tagging-conventions.md),
      ADR-companion drawers belong in the `decisions` room. A ratio
      significantly below 1.0 indicates two-layer-recording compliance
      drift even after the post-adr-write hook reminder (per ADR 0043).
    - `pushback`-tagged drawer count. Adoption metric for the convention
      added at S-0032. Zero or near-zero suggests the convention isn't
      being used in practice.
    - `lesson`-tagged drawer count. Same.
    - Diary discipline via `diary_skipped` soft-warn in recent archives.
      The shutdown-sequence step 6 (added at S-0032) emits this key in
      outcome_summary_soft_warns when a build session closes without a
      diary write.

    Returns CategoryFindings.

    Failure modes:
    - mempalace CLI not installed (PATH + fallback both miss). Records
      a single "CLI not available" finding and returns; downstream
      counts are skipped.
    - mempalace daemon down. Same handling.
    - mempalace status / search returns non-zero. Each call is
      independent; one failure doesn't suppress the others.
    """
    findings = CategoryFindings()

    binary = _resolve_mempalace_binary()
    if binary is None:
        findings.add(
            "MemPalace CLI not on PATH and not at ~/Library/Python/3.9/bin/mempalace",
            "Install per engine/operations/mempalace-operations.md, or document the "
            "absence (e.g., CI environment) so subsequent audits skip silently.",
        )
        return findings

    # Drawer counts per room (via `mempalace status`).
    status_text = _run_mempalace(binary, "status")
    if status_text is None:
        findings.add(
            "mempalace status returned no output; daemon may be down or palace path misconfigured",
            "Diagnose via `mempalace status` directly; check ~/.mempalace/config.json.",
        )
    else:
        room_counts: dict[str, int] = {}
        for m in re.finditer(r"ROOM:\s*(\S+)\s+(\d+)\s+drawers?", status_text):
            room_counts[m.group(1)] = int(m.group(2))
        adr_count = _count_adrs()
        decisions_count = room_counts.get("decisions", 0)
        if adr_count > 0:
            ratio = decisions_count / adr_count
            if ratio < 0.5:
                findings.add(
                    f"Decisions-room drawers ({decisions_count}) significantly below "
                    f"ADR count ({adr_count}); ratio {ratio:.2f}",
                    "Two-layer recording compliance gap. Audit which ADRs lack a "
                    "decision-tagged companion via the post-adr-write hook reminder log "
                    "(.claude/logs/post-adr-write.log) or ad-hoc mempalace_search per ADR.",
                )
            elif ratio < 0.9:
                findings.add(
                    f"Decisions-room drawers ({decisions_count}) modestly below "
                    f"ADR count ({adr_count}); ratio {ratio:.2f}",
                    "Watch — likely a small number of ADRs without companions. "
                    "Spot-check the most recent ADRs.",
                )
            else:
                findings.add(
                    f"Decisions-room drawers ({decisions_count}) approximate ADR count "
                    f"({adr_count}); ratio {ratio:.2f} — two-layer recording is healthy",
                    "no action",
                )
        # Per the room-targeting conventions, residual general/ should
        # shrink over time as classification cleanups land. Surface the
        # current count so the trend is visible across audits.
        general_count = room_counts.get("general", 0)
        if general_count > 0:
            findings.add(
                f"general-room drawer count: {general_count} "
                "(legacy mining content + auto-capture default)",
                "Trend-watch across audits — should shrink as classification cleanups "
                "land per engine/operations/mempalace-tagging-conventions.md "
                "Room-targeting conventions.",
            )

    # Adoption counts for `pushback` and `lesson` tags. The CLI search
    # returns full drawer bodies; raw match counts include false
    # positives (operations docs that *describe* the tags but aren't
    # tag-applied themselves). Two counting paths for the bifurcated
    # storage convention clarified at S-0098 in
    # mempalace-tagging-conventions.md:
    #
    # 1. Tags-line match: drawer body carries a `Tags:` line that
    #    includes the bare tag word (legacy convention; same heuristic
    #    as the post-adr-write hook's `decision`-tag check per ADR 0043).
    # 2. Content-prefix match: drawer body starts a line with
    #    `[<tag>]` (case-insensitive, optional leading whitespace).
    #    This catches drawers that lead their content with `[pushback]`
    #    or `[lesson]` rather than carrying the tag as metadata.
    #
    # A block matching BOTH counts once (per Issue #55 acceptance
    # criterion 4). Without this extension audit_mempalace() reported
    # "0 drawers tagged pushback" at S-0097 despite 3 substantive
    # `[pushback]`-prefixed drawers in paideia/problems (S-0005,
    # S-0048, S-0071).
    for tag in ("pushback", "lesson"):
        search_text = _run_mempalace(
            binary, "search", tag, "--wing", "paideia", "--results", "50"
        )
        if search_text is None:
            findings.add(
                f"mempalace search for `{tag}` returned no output",
                "Skip; diagnose CLI separately if persistent.",
            )
            continue
        # Each result is bracketed by a "[N] paideia / <room>" header.
        # Split on those headers and inspect each block's body for
        # either a Tags-line match or a [<tag>]-content-prefix line.
        blocks = re.split(
            r"^\s*\[\d+\]\s+paideia\s*/\s*\w+", search_text, flags=re.MULTILINE
        )
        tag_pattern = re.compile(rf"\*?\*?Tags:\*?\*?[^\n]*\b{re.escape(tag)}\b")
        prefix_pattern = re.compile(
            rf"^\s*\[{re.escape(tag)}\]", re.IGNORECASE | re.MULTILINE
        )
        tag_block_indices = {i for i, b in enumerate(blocks) if tag_pattern.search(b)}
        prefix_block_indices = {
            i for i, b in enumerate(blocks) if prefix_pattern.search(b)
        }
        combined_indices = tag_block_indices | prefix_block_indices
        tagged_count = len(combined_indices)
        tag_only_count = len(tag_block_indices)
        prefix_only_count = len(prefix_block_indices)
        if tagged_count == 0:
            findings.add(
                f"No drawers tagged `{tag}` found in MemPalace",
                f"Convention adoption gap. Either the {tag} convention isn't being "
                "used in practice (review at next session), or no qualifying moments "
                "have arisen since the convention was added at S-0032.",
            )
        else:
            findings.add(
                f"`{tag}`-tagged drawers in MemPalace: {tagged_count} confirmed "
                f"(via Tags-line match: {tag_only_count}; "
                f"via [{tag}]-content-prefix match: {prefix_only_count}; "
                "deduplicated)",
                "no action",
            )

    # Diary discipline via diary_skipped soft-warn in recent archives.
    diary_skipped_count = 0
    archives_with_diary_field = 0
    for archive_path in archives[-10:]:
        archive = read_archive(archive_path)
        sw = soft_warns_from_archive(archive)
        if "diary_skipped" in sw:
            archives_with_diary_field += 1
            diary_skipped_count += sw["diary_skipped"]

    if archives_with_diary_field == 0:
        findings.add(
            "No structured diary_skipped data in recent archives "
            "(field added at S-0033 — calibration window)",
            "Re-check after several post-S-0033 sessions accumulate.",
        )
    else:
        skip_rate = diary_skipped_count / archives_with_diary_field
        if skip_rate >= 0.5:
            findings.add(
                f"Diary skip rate: {diary_skipped_count}/{archives_with_diary_field} "
                f"recent archives ({skip_rate:.0%})",
                "Adoption gap. Per ADR 0042's 3-of-5 threshold, the persistent-warn "
                "surface should already be firing at boot. Investigate per "
                "engine/operations/session-shutdown-sequence.md step 6 — diary write "
                "is committed convention as of S-0033, not optional.",
            )
        else:
            findings.add(
                f"Diary discipline: {diary_skipped_count}/{archives_with_diary_field} "
                f"recent skips ({skip_rate:.0%})",
                "no action",
            )

    if findings.is_empty():
        findings.add(
            "No MemPalace observations surfaced.",
            "no action",
        )
    return findings


# ---------------------------------------------------------------------------
# Report emission
# ---------------------------------------------------------------------------


def render_section(title: str, findings: CategoryFindings, intro: str) -> str:
    """Render one report section as markdown.

    Format:

        ## <title>

        > <intro>

        - <observation>. <action>.
        - ...
    """
    bullets: list[str] = []
    for observation, action in findings.observations:
        # Ensure observation ends with a period before the action clause.
        obs = observation.rstrip(".")
        bullets.append(f"- {obs}. {action}.")
    body = "\n".join(bullets) if bullets else "- no findings. no action."
    return f"## {title}\n\n> {intro}\n\n{body}\n"


# ---------------------------------------------------------------------------
# Per-section emitters (one per docs/health-checks/TEMPLATE.md section,
# in TEMPLATE.md order, per ADR 0057 contract; refactor landed at S-0102
# per Issue #53).
#
# Three classes of emitter:
#
# - Data emitters (Fit / Gaps / Infrastructure-without-function / Bloat)
#   wrap audit_*()-collected CategoryFindings with the section's
#   adversarial prompt and reuse render_section() for bullet rendering.
#
# - Scaffolding emitters (Operative diagnostic / Forward-fit map /
#   Non-obvious finding(s) / Affirmative retire candidates /
#   Cold-context probe / User adjudication) emit the section header,
#   the intro blockquote (verbatim from TEMPLATE.md), and a placeholder
#   marker (e.g., `<observations>`, an empty 1-row table) for the
#   audit AI to populate at audit-time. Per ADR 0057 user-buffered
#   execution, User adjudication is left blank on arrival.
#
# - Mechanical / mixed emitters (Preamble / Freshness probes run /
#   Accumulated pushbacks and lessons / Cadence calibration / Summary)
#   produce some mechanical content (metadata, drawer counts, cadence
#   prose) and may carry placeholders for AI-judgment portions.
# ---------------------------------------------------------------------------


def emit_preamble(report: HealthCheckReport) -> str:
    """Render the report preamble — title, authoring blockquote, cadence line.

    Per docs/health-checks/TEMPLATE.md lines 1-7. The Last-check delta is
    computed as the integer difference of session ids when both are valid
    S-NNNN strings; absent (no parenthetical) when either id is malformed.
    """
    today_str = today()  # ADR 0058 — date-only display surface
    if report.last_check:
        delta_text = ""
        try:
            current_n = int(report.session_id.removeprefix("S-"))
            prior_n = int(report.last_check.removeprefix("S-"))
            delta_text = f" (Δ = {current_n - prior_n})"
        except ValueError:
            delta_text = ""
        last_check_clause = f"Last check: {report.last_check}{delta_text}."
    else:
        last_check_clause = "Last check: none (first check)."

    return (
        f"# Health Check {report.session_id} — {today_str}\n\n"
        f"> Authored by {report.session_id} against the cadence trigger "
        f"(or on-demand). Per [ADR 0022]"
        f"(../../engine/adr/0022-periodic-project-health-checks.md) and "
        f"[ADR 0057]"
        f"(../../engine/adr/0057-adversarial-stance-for-health-check-audits.md). "
        f"Producing script: "
        f"`python3 engine/tools/health_check.py --session {report.session_id}`. "
        f"Operational surface: [`engine/operations/health-check.md`]"
        f"(../../engine/operations/health-check.md).\n>\n"
        f"> **The audit is conversational by default — surface findings + "
        f"guidance suggestions to the user; the user adjudicates; downstream "
        f"sessions execute approved actions.** "
        f'The "User adjudication" subsection below is left **blank on arrival** '
        f"by the audit author. Do not pre-fill it. (Per ADR 0057 user-buffered "
        f"execution.)\n\n"
        f"**Cadence:** every {report.cadence} sessions. {last_check_clause}\n"
    )


def emit_freshness_probes_run() -> str:
    """Emit the Freshness probes run section — TEMPLATE.md scaffolding.

    Per docs/health-checks/TEMPLATE.md lines 9-17 and ADR 0057 element 3
    (stats-as-proxy-for-function): each external system gets a fresh
    content probe at audit-time. The script supplies the section
    scaffolding; the audit AI runs the probes and replaces the
    `<observation>` placeholders.
    """
    return (
        "## Freshness probes run\n\n"
        "> Per [ADR 0057]"
        "(../../engine/adr/0057-adversarial-stance-for-health-check-audits.md) "
        "stats-as-proxy-for-function. Each external system the audit "
        "references gets a fresh content probe at audit-time. Counts and "
        "existence checks alone do not satisfy this section.\n\n"
        "- **MemPalace.** `mempalace search` against ≥3 representative recent "
        "terms (derived from last sessions' `working_on` / `outcome_summary`). "
        "Result: <observation about content quality, not just drawer count>.\n"
        "- **Validator.** Acted-on rate of soft-warns across the audit window "
        "(`git log --grep` per persistent category vs. archive "
        "`outcome_summary_soft_warns` deltas). Result: <observation>.\n"
        "- **Supabase.** Most-recent migration's empirical effect (sample row "
        "counts, predicate distribution, schema shape vs. contract header). "
        "Result: <observation>.\n"
        "- **Hooks.** `.claude/logs/*-hook.log` tail across the audit window — "
        "verify recent fires show `OK exit=0`. Result: <observation per hook>.\n"
        "- **Registries.** Capture rate per register (`tensions.md`, "
        "dead-weight scanner output, `auto_target.json`, `HANDOFF.md`) — "
        "`git log --since` + content read. Result: <observation per register>.\n"
    )


def emit_operative_diagnostic_applied() -> str:
    """Emit the Operative diagnostic applied section — scaffolding for AI judgment.

    Per docs/health-checks/TEMPLATE.md lines 19-23. The dead-weight scanner
    output goes here as evidence; the audit's *judgment* of candidates
    against "is this thing doing the work it was created to do, or is it
    plumbing waiting for a function that never arrived?" is what makes
    this section non-trivial.
    """
    return (
        "## Operative diagnostic applied\n\n"
        "> Brief restatement: which files / categories / rules surfaced as "
        'candidates against "is this thing doing the work it was created to '
        'do, or is it plumbing waiting for a function that never arrived?" '
        "The dead-weight scanner output "
        "([`engine/health_check/dead_weight_candidates_S-NNNN.md`]"
        "(../../engine/health_check/dead_weight_candidates_S-NNNN.md)) goes "
        "here as evidence; the audit's judgment is what makes this section "
        "non-trivial.\n\n"
        "<observations>\n"
    )


def emit_forward_fit_map() -> str:
    """Emit the Forward-fit map section — scaffolding 1-row table for AI population.

    Per docs/health-checks/TEMPLATE.md lines 25-41. ADR 0057 dual-temporal-frame
    discipline (Issue #44 + S-0086 audit lesson). Adversarial audits weigh
    BOTH historical fit AND fit-to-CONTINUE.
    """
    return (
        "## Forward-fit map\n\n"
        "> Required alongside historical-evidence reading per the "
        "dual-temporal-frame discipline ([`engine/operations/health-check.md`]"
        '(../../engine/operations/health-check.md) "Forward-fit map" + '
        "[Issue #44](https://github.com/StarshipSuperjam/paideia/issues/44) + "
        "S-0086 audit lesson). Adversarial audits weigh BOTH historical fit "
        "AND fit-to-CONTINUE; either alone produces a muddled or "
        "too-charitable verdict. Apply to any internal subsystem under audit "
        "(or any artifact whose value depends on continued use).\n\n"
        "For each upcoming phase / committed-future-need, name the "
        "system-under-audit's role:\n\n"
        "- **Load-bearing forward** — system is committed to play a specific "
        "role in the next phase or open-question settlement.\n"
        "- **Candidate-among-substrates** — system *could* play a role; "
        "alternatives exist; commitment not yet made.\n"
        "- **No role** — forward state needs are met by other substrates; "
        "system has no called-out role.\n\n"
        "Map state-needs to candidate substrates (Postgres + pgvector / "
        "MemPalace / ADR + ENGINE_LOG / STATE.md / new). The forward-fit map "
        "informs every retire/preserve/scale-back recommendation alongside "
        "the historical-evidence section that follows.\n\n"
        "| Forward state need | System-under-audit role | "
        "Alternative substrate |\n"
        "|---|---|---|\n"
        "| <upcoming phase or OQ> | <load-bearing / candidate / no-role> | "
        "<Postgres / ADR / etc.> |\n\n"
        "<Add rows per upcoming phase / OQ / committed-future-need. The "
        "dual-frame produces the most decisive recommendations when "
        "historical and forward signals point opposite directions.>\n"
    )


def emit_non_obvious_findings() -> str:
    """Emit the Non-obvious finding(s) section — scaffolding for AI judgment.

    Per docs/health-checks/TEMPLATE.md lines 43-49. ≥1 required per the
    operative diagnostic; the audit's own observation that no mechanical
    scanner would catch.
    """
    return (
        "## Non-obvious finding(s)\n\n"
        "> ≥1 required, per [`engine/operations/health-check.md`]"
        "(../../engine/operations/health-check.md). Not on any mechanical "
        "scanner's output. The audit's own observation — what the AI/user "
        "noticed that no rule would catch.\n\n"
        "### Non-obvious finding A — <title>\n\n"
        "<observation + recommendation, routed through User adjudication "
        "below>\n"
    )


def emit_fit(findings: CategoryFindings) -> str:
    """Emit the Fit section — adversarial prompt + audit_fit() data.

    Per docs/health-checks/TEMPLATE.md lines 51-59. Adversarial prompt per
    ADR 0057 element 2.
    """
    intro = (
        "**Adversarial prompt:** *what machinery is silently ignored, what "
        "telemetry is being treated as load-bearing without anyone acting on "
        "it, and what category is firing 30+ times per session that no one "
        "reads?*"
    )
    return render_section("Fit", findings, intro)


def emit_gaps(findings: CategoryFindings) -> str:
    """Emit the Gaps section — adversarial prompt + audit_gaps() data.

    Per docs/health-checks/TEMPLATE.md lines 61-70. audit_gaps() integrates
    audit_orphan_ok_list() per S-0099 (Issue #51); its findings flow
    through this emitter unchanged.
    """
    intro = (
        "**Adversarial prompt:** *if a new collaborator joined the project "
        "tomorrow and tried to do work, what would they discover is missing "
        "only by tripping over it?*"
    )
    return render_section("Gaps", findings, intro)


def emit_infrastructure_without_function(findings: CategoryFindings) -> str:
    """Emit the Infrastructure-without-function (dead weight) section.

    Per docs/health-checks/TEMPLATE.md lines 72-82. Adversarial prompt per
    ADR 0057 element 2; disposition labels per element 4 (recommend retire
    / convert / preserve-with-affirmative-case). Header rename only —
    audit_dead_weight() data feeds unchanged.
    """
    intro = (
        "**Adversarial prompt:** *argue this candidate's retirement. What's "
        "the affirmative case for keeping it? If the case is "
        '"inbound references" alone, the references are themselves '
        "candidates for retirement.*"
    )
    return render_section(
        "Infrastructure-without-function (dead weight)", findings, intro
    )


def emit_bloat(findings: CategoryFindings) -> str:
    """Emit the Bloat section — adversarial prompt + audit_bloat() data.

    Per docs/health-checks/TEMPLATE.md lines 84-92.
    """
    intro = (
        "**Adversarial prompt:** *if the project's machinery were forced to "
        "halve in size, what would go first?*"
    )
    return render_section("Bloat", findings, intro)


def emit_accumulated_pushbacks_and_lessons(findings: CategoryFindings) -> str:
    """Emit the Accumulated pushbacks and lessons section.

    Per docs/health-checks/TEMPLATE.md lines 94-106 and ADR 0057 element 3
    + Issue #36: the audit reads `pushback`-tagged and `lesson`-tagged
    drawer content (not just count) since `last_audit_session`. The script
    surfaces audit_mempalace's mechanical observations (drawer counts via
    the S-0099 content-prefix-extension); cluster prose is AI-judgment
    work surfaced via scaffolding.
    """
    out: list[str] = ["## Accumulated pushbacks and lessons\n\n"]
    out.append(
        "> Per [Issue #36]"
        "(https://github.com/StarshipSuperjam/paideia/issues/36) and "
        "[ADR 0057]"
        "(../../engine/adr/0057-adversarial-stance-for-health-check-audits.md). "
        "The audit reads `pushback`-tagged and `lesson`-tagged drawer content "
        "(not just count) since `last_audit_session`, surfaces clusters, "
        "recommends posture rules for mechanization when clusters appear.\n"
    )
    if findings.observations:
        out.append("\nMechanical observations from `audit_mempalace()`:\n\n")
        bullets: list[str] = []
        for observation, action in findings.observations:
            obs = observation.rstrip(".")
            bullets.append(f"- {obs}. {action}.")
        out.append("\n".join(bullets) + "\n")
    out.append(
        "\n### Pushback clusters\n\n"
        "<For each cluster of pushbacks against the same risk-class, name "
        "the cluster and recommend whether the posture rule should be "
        "mechanized (new ADR, validator soft-warn, hook gate). If zero "
        "clusters or zero captures, name the signal explicitly — was the "
        "posture not exercised, or is the capture surface failing silently?>\n\n"
        "### Lesson clusters\n\n"
        "<Same shape: cluster of lessons against the same workflow → "
        "recommendation for ops-doc update, validator addition, or new "
        "ADR.>\n"
    )
    return "".join(out)


def emit_affirmative_retire_candidates() -> str:
    """Emit the Affirmative retire candidates section — scaffolding for AI judgment.

    Per docs/health-checks/TEMPLATE.md lines 108-120 and ADR 0057 element 4:
    ≥1 retire-candidate-with-reasoning OR an explicit "no retire candidates
    this audit" subsection adversarially scrutinizing its own claim.
    """
    return (
        "## Affirmative retire candidates\n\n"
        "> Per [ADR 0057]"
        "(../../engine/adr/0057-adversarial-stance-for-health-check-audits.md): "
        '≥1 retire-candidate-with-reasoning OR an explicit "no retire '
        'candidates this audit" subsection adversarially scrutinizing its own '
        "claim. Recommendations route through User adjudication below.\n\n"
        "### Retire candidate A — <title>\n\n"
        "<artifact + affirmative argument for retirement + what would be "
        "lost>\n\n"
        "<OR, if no candidates surfaced:>\n\n"
        "### No retire candidates this audit\n\n"
        '<Adversarial scrutiny of the claim: "I argue no retire candidates '
        'because X; if X were false, Y would be a candidate.">\n'
    )


def emit_cold_context_probe() -> str:
    """Emit the Cold-context probe section — scaffolding for AI judgment.

    Per docs/health-checks/TEMPLATE.md lines 122-130 and ADR 0057 element 5:
    audit reads ≥1 randomly-selected artifact as if it had no project
    context.
    """
    return (
        "## Cold-context probe\n\n"
        "> Per [ADR 0057]"
        "(../../engine/adr/0057-adversarial-stance-for-health-check-audits.md): "
        "the audit reads ≥1 randomly-selected artifact as if it had no project "
        "context. Surfaces compound drift in artifacts the warm-context audit "
        "can't see.\n\n"
        "**Artifact selected (random):** <path>. <Random-pick procedure: "
        "e.g., `find` filter + `shuf -n 1` against operations docs, ADRs, "
        "registers, build-plan chunks, hook scripts.>\n\n"
        "**Cold-read findings:** Do cross-references resolve? Does the prose "
        "tell a future cold consumer how to *use* this artifact? Does the "
        "artifact name a sibling that no longer exists? Does it carry a rule "
        "whose successor superseded it without a back-reference?\n\n"
        "<observations + recommendations>\n"
    )


def emit_user_adjudication() -> str:
    """Emit the User adjudication section — left blank on arrival.

    Per docs/health-checks/TEMPLATE.md lines 132-142 and ADR 0057 element 1
    (user-buffered execution). The user (or the next interactive session)
    populates this subsection with accept/reject/modify dispositions. The
    script ships the placeholder marker so audit recommendations are
    *surfaced*, not *executed*.
    """
    return (
        "## User adjudication\n\n"
        "> **Left blank on arrival.** Per [ADR 0057]"
        "(../../engine/adr/0057-adversarial-stance-for-health-check-audits.md) "
        "user-buffered execution. The user (or the next interactive session "
        "that picks up the audit's recommendations) populates this subsection "
        "with accept/reject/modify dispositions per recommendation. The audit "
        "closes with recommendations *surfaced*, not *executed*.\n>\n"
        "> Recommendations route to one of four execution lanes per [ADR 0048]"
        "(../../engine/adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md):\n"
        "> - **Inline trivial cleanup** (typos, broken cross-refs noticed in "
        "passing) — only for fix-in-context items, NOT adversarial "
        "recommendations.\n"
        "> - **Next-session work item in `engine/STATE.md`** — large items "
        "requiring substantial scope.\n"
        "> - **New GitHub Issue** with `health-check-finding` label — default "
        "lane for adversarial recommendations.\n"
        "> - **New tension in `product/docs/tensions.md`** — if not yet "
        "actionable.\n\n"
        "<populated post-audit by the user>\n"
    )


def emit_cadence_calibration(report: HealthCheckReport) -> str:
    """Emit the Cadence calibration section — TEMPLATE.md prose with the report's cadence.

    Per docs/health-checks/TEMPLATE.md lines 144-152.
    """
    return (
        "## Cadence calibration\n\n"
        f"Is the current cadence ({report.cadence} sessions) right for "
        "current project velocity?\n\n"
        "- If consistently no-action: raise (e.g., 10 → 20).\n"
        "- If consistently large action lists: lower (e.g., 10 → 5).\n"
        "- During phase transitions: consider one-off audit at the boundary, "
        "independent of the cadence.\n\n"
        f"This audit's recommendation: <keep at {report.cadence} | raise to "
        "M | lower to M> — routed through User adjudication above.\n"
    )


def emit_summary(report: HealthCheckReport) -> str:
    """Emit the Summary section — scaffolding + observation-count footer.

    Per docs/health-checks/TEMPLATE.md lines 154-156. The script appends
    the mechanical observation count from the data sections as an aid;
    the AI fills the narrative.
    """
    total_findings = (
        len(report.fit.observations)
        + len(report.gaps.observations)
        + len(report.dead_weight.observations)
        + len(report.bloat.observations)
        + len(report.mempalace.observations)
    )
    return (
        "## Summary\n\n"
        "<One paragraph: what the project's discipline looks like now vs. "
        "last check, and what's queued for next session as a result of this "
        "audit's recommendations once user adjudication completes.>\n\n"
        f"_Mechanical-data baseline (script-emitted): {total_findings} "
        "observation(s) across the data sections (Fit / Gaps / "
        "Infrastructure-without-function / Bloat / Accumulated "
        "pushbacks-and-lessons mechanical bullets)._\n"
    )


def render_report(report: HealthCheckReport) -> str:
    """Render the full report as markdown matching docs/health-checks/TEMPLATE.md.

    Chains the per-section emitters in TEMPLATE.md order. The script's
    contract: produce the canonical 14-body-section shape per ADR 0057
    (engine/adr/0057-adversarial-stance-for-health-check-audits.md). The
    audit AI's contract at audit-time: replace `<observation>` /
    `<observations>` placeholders with content-probe findings + adversarial
    judgment per the section's adversarial prompt.

    Per Issue #53 (closed at S-0102): refactor moved prose-emission from
    the prior 5-section ad-hoc layout (Fit / Gaps / Dead weight / Bloat /
    MemPalace + Cadence + Summary) to the 14-body-section TEMPLATE.md
    shape. The audit_*() data-gathering functions are unchanged; their
    outputs feed the four data-section emitters (emit_fit / emit_gaps /
    emit_infrastructure_without_function / emit_bloat) plus
    emit_accumulated_pushbacks_and_lessons.
    """
    return (
        f"{emit_preamble(report)}\n"
        f"{emit_freshness_probes_run()}\n"
        f"{emit_operative_diagnostic_applied()}\n"
        f"{emit_forward_fit_map()}\n"
        f"{emit_non_obvious_findings()}\n"
        f"{emit_fit(report.fit)}\n"
        f"{emit_gaps(report.gaps)}\n"
        f"{emit_infrastructure_without_function(report.dead_weight)}\n"
        f"{emit_bloat(report.bloat)}\n"
        f"{emit_accumulated_pushbacks_and_lessons(report.mempalace)}\n"
        f"{emit_affirmative_retire_candidates()}\n"
        f"{emit_cold_context_probe()}\n"
        f"{emit_user_adjudication()}\n"
        f"{emit_cadence_calibration(report)}\n"
        f"{emit_summary(report)}"
    )


def emit_report(report: HealthCheckReport, dry_run: bool = False) -> Path | None:
    """Write the rendered report to docs/health-checks/<session>.md.

    If dry_run is True, write to stdout instead and return None.

    Returns the written path on success.

    Side effect (non-dry-run): bumps engine/session/register_state.json's
    `last_audit_session` field to report.session_id. The bump anchors the
    overdue-catchup cadence trigger introduced at S-0041 (per ADR 0022
    Consequences amendment): the SessionStart hook and validate.py's
    `health_check_overdue` check both read this field. Best-effort —
    register-state write failures do not poison the audit (the report is
    the durable artifact; the field bump is advisory tracking).
    """
    rendered = render_report(report)
    if dry_run:
        sys.stdout.write(rendered)
        return None
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / f"{report.session_id}.md"
    out_path.write_text(rendered)
    bump_last_audit_session(report.session_id)
    return out_path


def bump_last_audit_session(session_id: str) -> None:
    """Update register_state.json's `last_audit_session` to session_id.

    Per ADR 0022 Consequences amendment at S-0041. The SessionStart hook
    and validate.py's `health_check_overdue` check both consume this field
    to compute overdue state; the audit script is the canonical "audit
    happened" producer and so owns the field bump.

    Best-effort: failures are logged to stderr but do not raise. The audit
    report is the durable artifact; a missed field bump produces a
    spurious overdue surface at the next session boot, which is recoverable
    by manual edit.
    """
    register_path = REPO_ROOT / "engine" / "session" / "register_state.json"
    if not register_path.is_file():
        sys.stderr.write(
            f"warning: register_state.json absent; cannot bump "
            f"last_audit_session to {session_id}\n"
        )
        return
    try:
        register = json.loads(register_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write(
            f"warning: register_state.json unreadable ({e}); "
            f"cannot bump last_audit_session to {session_id}\n"
        )
        return
    if not isinstance(register, dict):
        sys.stderr.write(
            f"warning: register_state.json not an object; "
            f"cannot bump last_audit_session to {session_id}\n"
        )
        return
    register["last_audit_session"] = session_id
    try:
        register_path.write_text(json.dumps(register, indent=2) + "\n")
    except OSError as e:
        sys.stderr.write(
            f"warning: register_state.json write failed ({e}); "
            f"last_audit_session not bumped to {session_id}\n"
        )


# ---------------------------------------------------------------------------
# Cadence detection
# ---------------------------------------------------------------------------


def detect_cadence() -> int:
    """Return the cadence interval from register_state.json or default 10.

    Looks for the optional `health_check_cadence` key. Defaults to 10 if
    absent or malformed (was 30 from S-0001 to S-0032; tightened to 10 at
    S-0033 by user direction per ADR 0022 Consequences amendment).
    """
    register_path = REPO_ROOT / "engine" / "session" / "register_state.json"
    if not register_path.is_file():
        return 10
    try:
        register = json.loads(register_path.read_text())
    except (OSError, json.JSONDecodeError):
        return 10
    if isinstance(register, dict):
        cadence = register.get("health_check_cadence", 10)
        if isinstance(cadence, int) and cadence > 0:
            return cadence
    return 10


def detect_last_check() -> str | None:
    """Return the most-recent prior health-check session id or None.

    Scans docs/health-checks/ for files matching S-NNNN.md (excluding
    README.md and TEMPLATE.md) and returns the highest-numbered.
    """
    if not REPORT_DIR.is_dir():
        return None
    candidates = sorted(REPORT_DIR.glob("S-[0-9][0-9][0-9][0-9].md"))
    if not candidates:
        return None
    return candidates[-1].stem


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI entry. Returns process exit code.

    Args:
        argv: optional argument list (default sys.argv[1:]). Allows
            programmatic invocation from tests.

    Exit codes:
        0 — report written (or dry-run printed) successfully.
        2 — required input missing (e.g., --session not provided).
    """
    parser = argparse.ArgumentParser(
        description="Produce a project health-check report per ADR 0022.",
    )
    parser.add_argument(
        "--session",
        required=True,
        help="Session id (S-NNNN) the report is filed under.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the rendered report to stdout instead of writing a file.",
    )
    args = parser.parse_args(argv)

    if not re.match(r"^S-\d{4}$", args.session):
        sys.stderr.write(f"--session must match S-NNNN format; got {args.session!r}\n")
        return 2

    archives = list_archives()
    cadence = detect_cadence()
    last_check = detect_last_check()

    report = HealthCheckReport(
        session_id=args.session,
        cadence=cadence,
        last_check=last_check,
    )
    report.fit = audit_fit(archives)
    report.gaps = audit_gaps()
    report.dead_weight = audit_dead_weight()
    report.bloat = audit_bloat()
    report.mempalace = audit_mempalace(archives)

    out_path = emit_report(report, dry_run=args.dry_run)
    if out_path is not None:
        sys.stdout.write(f"Wrote {out_path.relative_to(REPO_ROOT)}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
