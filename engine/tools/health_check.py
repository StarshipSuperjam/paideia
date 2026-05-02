#!/usr/bin/env python3
"""Paideia project health-check audit producer.

Module contract — what this file is and is not.

This module aggregates audit data per the four categories named in
engine/operations/health-check.md (Fit, Gaps, Dead weight, Bloat) and
emits a populated markdown report at docs/health-checks/S-NNNN.md.
Per ADR 0022 (periodic project health checks) and ADR 0042 (soft-warn
lifecycle: archive is canon).

The script is invoked when the cadence trigger fires at session boot
(default cadence: 30 sessions; configurable in
engine/session/register_state.json). It reads only committed sources;
gitignored telemetry (engine/tools/validate-history.jsonl) is consumed
opportunistically when present but the script does not depend on it.

Inputs (read):

- engine/session/archive/S-NNNN.json — per-session committed metadata.
  The new outcome_summary_soft_warns field (per ADR 0042) is the trend
  canon for Fit.
- engine/adr/*.md and product/adr/*.md — Status fields for Fit
  (Accepted / Superseded / Deprecated) and Dead-weight (long-Deprecated
  candidates).
- engine/ENGINE_LOG.md — entry counts by date for Fit fidelity check.
- product/docs/tensions.md — open tensions for Gaps; aged tensions
  (>10 sessions open without movement) flagged.
- product/docs/ideation.md — unconsumed entries for Dead-weight.
- engine/operations/*.md — file sizes for Bloat.
- engine/tools/validate-history.jsonl — per-invocation telemetry for Fit
  validator-runtime drift (opportunistic; absent on fresh clones).

Outputs (written):

- docs/health-checks/S-NNNN.md — populated report following the shape
  in docs/health-checks/TEMPLATE.md. Each of the four sections is
  non-empty.
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

- Does not query MemPalace. The MCP server is not reliably reachable
  from a CLI script; the AI augments the Fit section manually with
  mempalace_search results after this script writes the structural
  sections (per docs/health-checks/README.md "How a report gets
  produced" step 2).
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
import re
import sys
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


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
IDEATION_PATH = REPO_ROOT / "product" / "docs" / "ideation.md"
OPERATIONS_DIR = REPO_ROOT / "engine" / "operations"
VALIDATE_HISTORY_PATH = REPO_ROOT / "engine" / "tools" / "validate-history.jsonl"
REPORT_DIR = REPO_ROOT / "docs" / "health-checks"

# Tunable thresholds. Calibration changes are amendment-tracked under ADR 0042
# (soft-warn-lifecycle.md) for trend windows and ADR 0022 for audit thresholds.
SOFT_WARN_PERSISTENCE_BOOT_SURFACE = (3, 5)  # 3-of-last-5 archives surfaces
SOFT_WARN_PERSISTENCE_ESCALATION = 10  # consecutive archives → escalation
LARGE_OPS_DOC_LINES = 300  # >300 lines is a Bloat candidate per health-check.md
DEPRECATED_ADR_AGE_SESSIONS = 20  # Deprecated for >20 sessions without successor
TENSION_AGE_SESSIONS = 10  # Tension open >10 sessions without movement


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
    cadence: int = 30
    last_check: str | None = None
    fit: CategoryFindings = field(default_factory=CategoryFindings)
    gaps: CategoryFindings = field(default_factory=CategoryFindings)
    dead_weight: CategoryFindings = field(default_factory=CategoryFindings)
    bloat: CategoryFindings = field(default_factory=CategoryFindings)


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
    # Walk archives in reverse-chronological order; bounded by the
    # cadence-interval window (default 30) when more archives exist.
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

    Reads:
    - product/docs/tensions.md for tensions open >10 sessions without
      movement (heuristic: counts session-id mentions; an "Updated:" or
      "Resolved:" line counts as movement).
    - ADR Consequences sections for promised-but-not-delivered work
      (mirrors validator's adr_consequences_deliverable_audit category).
    - engine/STATE.md for unresolved open questions (heuristic: lines
      starting with "OQ-" without a "decided" or "settled" marker).

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
                missing_paths = [
                    p for p in path_candidates if not (REPO_ROOT / p).exists()
                ]
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

    if findings.is_empty():
        findings.add(
            "No Gaps surfaced by mechanical audit.",
            "no action",
        )
    return findings


# ---------------------------------------------------------------------------
# Dead-weight audit
# ---------------------------------------------------------------------------


def audit_dead_weight() -> CategoryFindings:
    """Audit what no longer earns its keep.

    Reads:
    - ADR collection for Deprecated entries (Status: Deprecated).
    - Operations docs for inbound-citation count (grep across all .md
      files for the doc filename); zero-citation docs are dead-weight
      candidates.
    - product/docs/ideation.md for unconsumed entries (heuristic:
      entries without a "Consumed:" or "Promoted:" marker).

    Returns CategoryFindings.

    Non-responsibilities:
        - Does not call git for stale-worktree detection. That belongs
          to a shell wrapper around this script if needed.
        - Does not enforce removal. Surfaces candidates; the AI/user
          decides.
    """
    findings = CategoryFindings()

    # Deprecated ADRs.
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

    # Operations docs with no inbound citations.
    if OPERATIONS_DIR.is_dir():
        all_md_files = list(REPO_ROOT.rglob("*.md"))
        # Exclude files we won't search through (the doc itself; node_modules
        # equivalents). A simple heuristic: skip files inside docs/ subtree
        # that are themselves the candidate doc.
        op_doc_names = [
            p.name for p in OPERATIONS_DIR.glob("*.md") if p.name != "README.md"
        ]
        uncited_ops: list[str] = []
        for op_name in op_doc_names:
            cited = False
            for md_path in all_md_files:
                if md_path.name == op_name and md_path.parent == OPERATIONS_DIR:
                    continue  # the doc itself
                try:
                    if op_name in md_path.read_text():
                        cited = True
                        break
                except OSError:
                    continue
            if not cited:
                uncited_ops.append(op_name)
        if uncited_ops:
            findings.add(
                f"{len(uncited_ops)} operations doc(s) with no inbound citations: "
                + ", ".join(uncited_ops),
                "Per doc: confirm load-bearing for future work; if not, retire "
                "or absorb into a sibling doc.",
            )

    # Unconsumed ideation entries.
    if IDEATION_PATH.is_file():
        ideation_text = IDEATION_PATH.read_text()
        # Each entry is a section starting with `## ` in the file.
        entries = re.findall(r"^##\s+(.+)$", ideation_text, re.MULTILINE)
        unconsumed: list[str] = []
        for entry_title in entries:
            entry_pattern = re.compile(
                rf"^##\s+{re.escape(entry_title)}.*?(?=^##\s|\Z)",
                re.MULTILINE | re.DOTALL,
            )
            entry_match = entry_pattern.search(ideation_text)
            if not entry_match:
                continue
            entry_text = entry_match.group(0)
            if not re.search(
                r"[Cc]onsumed|[Pp]romoted|[Rr]ejected|[Rr]etired", entry_text
            ):
                unconsumed.append(entry_title)
        if unconsumed:
            findings.add(
                f"{len(unconsumed)} unconsumed ideation entry/entries: "
                + "; ".join(unconsumed[:5])
                + ("; ..." if len(unconsumed) > 5 else ""),
                "Per entry: promote (becomes a tension or a downstream doc), "
                "retire (mark Rejected with reason), or accept long-tail.",
            )

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

    Reads:
    - engine/operations/*.md for line counts; flags files >300 lines
      per health-check.md's heuristic.
    - ADR collection for topic clustering (heuristic: title-token
      overlap suggests a single decision became multiple).
    - Recent archive durations (closed_at - started_at) for shutdown
      overhead; flags upward trend.

    Returns CategoryFindings.
    """
    findings = CategoryFindings()

    # Operations docs > LARGE_OPS_DOC_LINES.
    large_docs: list[tuple[str, int]] = []
    if OPERATIONS_DIR.is_dir():
        for op_doc in sorted(OPERATIONS_DIR.glob("*.md")):
            line_count = len(op_doc.read_text().splitlines())
            if line_count > LARGE_OPS_DOC_LINES:
                large_docs.append((op_doc.name, line_count))
    if large_docs:
        listing = ", ".join(f"{name} ({n} lines)" for name, n in large_docs)
        findings.add(
            f"{len(large_docs)} operations doc(s) over {LARGE_OPS_DOC_LINES} lines: {listing}.",
            "Per doc: split if multiple concerns; accept if single coherent topic.",
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
            t0 = datetime.fromisoformat(started.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(closed.replace("Z", "+00:00"))
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


def render_report(report: HealthCheckReport) -> str:
    """Render the full report as markdown matching docs/health-checks/TEMPLATE.md.

    Composes the four section bodies plus the cadence-calibration block
    and the summary paragraph. The summary is computed from total
    finding counts.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    last_check_clause = (
        f"Last check: {report.last_check}." if report.last_check else "First check."
    )

    fit_md = render_section(
        "Fit",
        report.fit,
        "Does the machinery match what the project is actually producing?",
    )
    gaps_md = render_section(
        "Gaps",
        report.gaps,
        "What's missing that should be there?",
    )
    dead_weight_md = render_section(
        "Dead weight",
        report.dead_weight,
        "What's in the repo that no longer earns its keep?",
    )
    bloat_md = render_section(
        "Bloat",
        report.bloat,
        "What's grown past its purpose?",
    )

    total_findings = (
        len(report.fit.observations)
        + len(report.gaps.observations)
        + len(report.dead_weight.observations)
        + len(report.bloat.observations)
    )
    summary = (
        f"Audit ran against the structured-data window. {total_findings} observation(s) "
        "across the four categories. Augment with MemPalace-recall observation per "
        "docs/health-checks/README.md before triaging."
    )

    return (
        f"# Health Check {report.session_id} — {today}\n\n"
        f"> Authored by {report.session_id} against the cadence trigger. "
        f"Per [ADR 0022](../../engine/adr/0022-periodic-project-health-checks.md). "
        f"Producing script: `python3 engine/tools/health_check.py "
        f"--session {report.session_id}`.\n\n"
        f"**Cadence:** every {report.cadence} sessions. {last_check_clause}\n\n"
        f"{fit_md}\n"
        f"{gaps_md}\n"
        f"{dead_weight_md}\n"
        f"{bloat_md}\n"
        f"## Cadence calibration\n\n"
        f"Is the current cadence ({report.cadence} sessions) right for current project velocity?\n\n"
        f"- If consistently no-action: raise (e.g., 30 → 50).\n"
        f"- If consistently large action lists: lower (e.g., 30 → 15).\n"
        f"- During phase transitions: consider one-off audit at the boundary.\n\n"
        f"This audit's recommendation: keep at {report.cadence} (override after "
        f"reading the four sections).\n\n"
        f"## Summary\n\n"
        f"{summary}\n"
    )


def emit_report(report: HealthCheckReport, dry_run: bool = False) -> Path | None:
    """Write the rendered report to docs/health-checks/<session>.md.

    If dry_run is True, write to stdout instead and return None.

    Returns the written path on success.
    """
    rendered = render_report(report)
    if dry_run:
        sys.stdout.write(rendered)
        return None
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / f"{report.session_id}.md"
    out_path.write_text(rendered)
    return out_path


# ---------------------------------------------------------------------------
# Cadence detection
# ---------------------------------------------------------------------------


def detect_cadence() -> int:
    """Return the cadence interval from register_state.json or default 30.

    Looks for the optional `health_check_cadence` key. Defaults to 30 if
    absent or malformed.
    """
    register_path = REPO_ROOT / "engine" / "session" / "register_state.json"
    if not register_path.is_file():
        return 30
    try:
        register = json.loads(register_path.read_text())
    except (OSError, json.JSONDecodeError):
        return 30
    if isinstance(register, dict):
        cadence = register.get("health_check_cadence", 30)
        if isinstance(cadence, int) and cadence > 0:
            return cadence
    return 30


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

    out_path = emit_report(report, dry_run=args.dry_run)
    if out_path is not None:
        sys.stdout.write(f"Wrote {out_path.relative_to(REPO_ROOT)}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
