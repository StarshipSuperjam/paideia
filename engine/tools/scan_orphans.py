"""Multi-axis dead-weight scanner for the project health-check.

Layer 1 contract per ADR 0048 + ADR 0049 (the cross-cutting telemetry
addition motivates this tool's framing — health-check sessions need
mechanical input that surfaces "is this file doing the work it was
created to do?" candidates beyond pure-reference-count).

Five independent axes
---------------------
Each axis emits zero or more ``OrphanCandidate`` records. The audit
session walks the aggregated output top-to-bottom and judges each
candidate against the operative diagnostic question.

1. **Reference-count.** Walk tracked Markdown files in semantic
   directories (product/docs/, engine/operations/, engine/adr/,
   product/adr/, root-level *.md). For each, count inbound references
   (basename mentions in other tracked files, excluding self-mentions
   and the file's own README index entry). Files with < 3 references
   are candidates. Catches the classic "anyone pointing at this?" case.

2. **Last-substantive-modification age.** For each tracked file, find
   the last commit that touched it. Skip commits whose subject contains
   sweep markers ("partition migration", "ruff format", "format only",
   "format-only"). Files unchanged for N+ sessions despite the system
   being active are candidates. Threshold defaults to 20 sessions.

3. **Register-emptiness.** Files with detectable "register / log /
   queue" patterns (markdown tables with header rows but no data rows,
   or known register filenames with no captured entries). Pre-S-0083
   the canonical example was ``ideation.md`` (17 inbound references but
   no captured entries across S-0001..S-0077, retired at S-0083 per
   Issue #29 — the function migrated to GitHub Issues with the
   ``enhancement`` label per ADR 0048).

4. **Ops-doc-uncited.** For each engine/operations/*.md, flag the doc
   if it has fewer than ``OPS_DOC_UNCITED_REF_THRESHOLD`` (default 5)
   unique inbound file references AND it is unreachable from the
   boot-surface link graph (BFS from CLAUDE.md + engine/STATE.md,
   treating operations/README.md as a visit-but-don't-traverse leaf).
   Refined at S-0126 per Issue #89 / ADR 0062 from the prior
   archive-text-substring predicate, which had a high false-positive
   rate against foundational ops docs consumed by behavior but rarely
   cited verbatim in outcome_summary prose.

5. **Stale-pending-marker.** Files carrying pending decision markers
   (e.g., "decide-trigger", "decide-before", "open decide-by") whose
   pinned phase has passed or whose marker has been pending for many
   sessions. Catches the unfired decide-trigger pattern in
   ``prep-paideia-prompt-pack.md``.

Output
------
JSON (``--json``) for machine consumption, or markdown (default)
suitable for ``engine/health_check/dead_weight_candidates_<session>.md``.

Exit codes
----------
- ``0`` — scan completed (regardless of how many candidates surface).
- ``1`` — reserved; not currently used. The scanner is informational.

CLI
---
- ``scan_orphans.py`` — default; emit markdown to stdout.
- ``scan_orphans.py --json`` — emit JSON to stdout.
- ``scan_orphans.py --repo-root PATH`` — override repo root.
- ``scan_orphans.py --age-threshold N`` — sessions threshold for
  axes 2 and 5 (default 20).
- ``scan_orphans.py --output PATH`` — write to PATH instead of stdout.
- ``scan_orphans.py --axis NAME`` — restrict to one axis (for
  per-axis unit testing).

Out of scope
------------
- No automatic deletion or modification of any flagged file.
- No judgment on whether a candidate should be retired; surfaces only.
- Canonical-file allowlist not maintained inside this tool. Files like
  HANDOFF.md, MISSION.md, README.md are simply low-noise candidates
  that the audit recognizes as load-bearing on read.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Local import — scrub_env lives next to this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrub_env import scrubbed_env  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[2]

# Directories to walk for axes 1 + 2. Other directories are scoped out.
SEMANTIC_DIRS = (
    Path("product/docs"),
    Path("engine/operations"),
    Path("engine/adr"),
    Path("product/adr"),
)

# Reference-count threshold below which a file is flagged as low-reference.
REFERENCE_COUNT_THRESHOLD = 3

# Age-in-sessions threshold for axes 2 + 5 (default; CLI override exists).
DEFAULT_AGE_THRESHOLD_SESSIONS = 20

# Commit-subject markers that indicate sweep commits (excluded from
# "substantive modification" detection).
_SWEEP_MARKERS = (
    "partition migration",
    "ruff format",
    "format only",
    "format-only",
    "deps bump",
    "dependency bump",
)

# Filename suffixes / paths that match the "register / log / queue" pattern
# and are scanned by axis 3. (ideation.md was in this list pre-S-0083;
# retired per Issue #29 — function migrated to GitHub Issues with the
# `enhancement` label per ADR 0048.)
_REGISTER_FILE_NAMES = (
    "tensions.md",  # has structural patterns; skip if entries present
)

# Markers that indicate a pending decision in axis 5.
_PENDING_MARKERS = (
    "decide-trigger",
    "decide-before",
    "open decide-by",
)

# Forward-pin trigger vocabulary (per S-0143 / Issue #111). Markers carrying
# any of these annotations point at a FUTURE phase / session / external
# condition; the marker is deliberately deferred and not stale. The
# classifier `is_marker_line_back_pinned()` parses each marker line for these
# patterns and returns False (forward-pinned, skip) when found pointing at a
# future trigger, True (back-pinned or unannotated, flag) otherwise.
#
# Patterns:
#   - `decide-before Phase N` — forward-pinned if N > current_phase
#   - `decide-by S-NNNN` — forward-pinned if NNNN > current_session
#   - `[TRIGGER: <condition>]` — forward-pinned (gated on external trigger)
#   - `Phase N+` — forward-pinned if N > current_phase
#   - `OQ-XXXXX` reference — forward-pinned (the open question is unresolved;
#     if it had been resolved, the marker would have been removed)
_DECIDE_BEFORE_PHASE_RE = re.compile(r"decide-before\s+Phase\s+(\d+)", re.IGNORECASE)
_DECIDE_BY_SESSION_RE = re.compile(r"decide-by\s+S-(\d{4})", re.IGNORECASE)
_TRIGGER_BRACKET_RE = re.compile(r"\[TRIGGER:\s")
_PHASE_PLUS_RE = re.compile(r"Phase\s+(\d+)\+", re.IGNORECASE)
_OQ_REFERENCE_RE = re.compile(r"\bOQ-[A-Z][A-Z0-9-]+", re.IGNORECASE)


def get_current_phase(repo_root: Path) -> int:
    """Parse the current phase number from engine/STATE.md.

    Returns 0 when STATE.md is missing or no "Phase N" reference parseable.
    """
    state = repo_root / "engine" / "STATE.md"
    if not state.is_file():
        return 0
    try:
        text = state.read_text()
    except OSError:
        return 0
    # Match the **Current phase** row: "**Phase N — ...**" or "Phase N —".
    m = re.search(
        r"\*\*Current phase\*\*\s*\|\s*\*?\*?Phase\s+(\d+)", text, re.IGNORECASE
    )
    if m:
        return int(m.group(1))
    return 0


def get_current_session(repo_root: Path) -> int:
    """Parse the current session counter from engine/session/register_state.json.

    Returns the integer suffix of `next_id` (e.g., 143 for "S-0143"); 0 on any
    failure.
    """
    register = repo_root / "engine" / "session" / "register_state.json"
    if not register.is_file():
        return 0
    try:
        data = json.loads(register.read_text())
    except (OSError, json.JSONDecodeError):
        return 0
    next_id = data.get("next_id", "")
    if isinstance(next_id, str) and next_id:
        try:
            return int(next_id)
        except ValueError:
            return 0
    return 0


def is_marker_line_back_pinned(
    line: str, current_phase: int, current_session: int
) -> bool:
    """Classify a single marker line as back-pinned (flag) or forward-pinned (skip).

    Returns True (back-pinned, flag) when the line:
      - has no trigger annotation at all (unannotated marker), OR
      - carries a `decide-before Phase N` with N <= current_phase (overdue), OR
      - carries a `decide-by S-NNNN` with NNNN <= current_session (overdue), OR
      - carries a `Phase N+` with N <= current_phase (overdue).

    Returns False (forward-pinned, skip) when any of:
      - `decide-before Phase N` with N > current_phase,
      - `decide-by S-NNNN` with NNNN > current_session,
      - `Phase N+` with N > current_phase,
      - `[TRIGGER: ...]` literal,
      - `OQ-XXXXX` reference (open question, treat as forward-pinned).

    The function answers "is this marker stale?"; the caller decides whether
    to flag the containing file based on whether ANY of its marker lines
    return True.
    """
    # Explicit phase-future triggers (highest priority).
    m = _DECIDE_BEFORE_PHASE_RE.search(line)
    if m:
        phase = int(m.group(1))
        return phase <= current_phase  # overdue → back-pinned

    m = _DECIDE_BY_SESSION_RE.search(line)
    if m:
        session = int(m.group(1))
        return session <= current_session  # overdue → back-pinned

    m = _PHASE_PLUS_RE.search(line)
    if m:
        phase = int(m.group(1))
        return phase <= current_phase  # overdue → back-pinned

    if _TRIGGER_BRACKET_RE.search(line):
        return False  # [TRIGGER: ...] is always forward-pinned

    if _OQ_REFERENCE_RE.search(line):
        return False  # OQ-XXXXX open question reference is forward-pinned

    # No trigger annotation found — unannotated marker, classify as back-pinned
    # (the marker has no deferral justification, so it's stale by default).
    return True


@dataclass(frozen=True)
class OrphanCandidate:
    """One file flagged by one axis as a dead-weight candidate."""

    path: str  # repo-relative
    axis: str
    signal: str
    last_substantive_change: str
    inbound_references: int


def _git(args: list[str], cwd: Path) -> tuple[int, str]:
    """Run a git command; return (exit_code, stdout)."""
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    return proc.returncode, proc.stdout


def tracked_md_files(
    repo_root: Path, dirs: tuple[Path, ...] = SEMANTIC_DIRS
) -> list[Path]:
    """Return tracked .md files under the given semantic directories.

    Falls back to a filesystem walk if git ls-files fails.
    """
    files: list[Path] = []
    for d in dirs:
        target = repo_root / d
        if not target.is_dir():
            continue
        rc, out = _git(["ls-files", "--", f"{d}/*.md"], repo_root)
        if rc == 0:
            for line in out.splitlines():
                line = line.strip()
                if line:
                    files.append(repo_root / line)
        else:
            files.extend(target.rglob("*.md"))
    # Also include root-level .md files (CLAUDE.md, ROADMAP.md, etc.).
    rc, out = _git(["ls-files", "--", "*.md"], repo_root)
    if rc == 0:
        for line in out.splitlines():
            line = line.strip()
            if line and "/" not in line:
                files.append(repo_root / line)
    return files


def count_inbound_references(repo_root: Path, target_path: Path) -> int:
    """Count tracked-file mentions of target_path's basename, excluding
    the file itself and trivial index-only mentions (operations/README.md
    indexes every operations doc by basename — counted as 0, not 1).
    """
    name = target_path.name
    # grep-l returns filenames containing the basename; -F is fixed-string.
    rc, out = _git(
        [
            "grep",
            "-l",
            "-F",
            "--",
            name,
            "*",
        ],
        repo_root,
    )
    if rc != 0 and rc != 1:
        # rc 1 from git grep is "no matches" — fine. Other rcs are errors.
        return 0
    refs: set[Path] = set()
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        candidate = repo_root / line
        if candidate == target_path:
            continue
        # Discount the operations/README.md index entry (axis 4 handles
        # that pattern explicitly).
        if (
            line == "engine/operations/README.md"
            and target_path.parent.name == "operations"
        ):
            continue
        refs.add(candidate)
    return len(refs)


def axis_reference_count(repo_root: Path) -> list[OrphanCandidate]:
    """Axis 1 — files with < REFERENCE_COUNT_THRESHOLD inbound references."""
    candidates: list[OrphanCandidate] = []
    files = tracked_md_files(repo_root)
    for f in files:
        refs = count_inbound_references(repo_root, f)
        if refs < REFERENCE_COUNT_THRESHOLD:
            rel = str(f.relative_to(repo_root))
            sig = f"{refs} inbound reference(s) (threshold {REFERENCE_COUNT_THRESHOLD})"
            last_change = last_substantive_change(repo_root, f)
            candidates.append(
                OrphanCandidate(
                    path=rel,
                    axis="reference-count",
                    signal=sig,
                    last_substantive_change=last_change,
                    inbound_references=refs,
                )
            )
    return candidates


def last_substantive_change(repo_root: Path, target: Path) -> str:
    """Return ``<sha> <date>`` for the last non-sweep commit touching
    target, or ``(no substantive changes)`` when only sweep commits found.
    """
    rel = str(target.relative_to(repo_root))
    rc, out = _git(
        ["log", "--format=%H|%ad|%s", "--date=short", "--", rel],
        repo_root,
    )
    if rc != 0 or not out.strip():
        return "(no commits)"
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        sha, date, subject = parts
        if any(marker in subject.lower() for marker in _SWEEP_MARKERS):
            continue
        return f"{sha[:8]} {date}"
    return "(only sweep commits)"


def _commits_count_for_path(repo_root: Path, target: Path) -> int:
    """Return number of substantive commits touching target."""
    rel = str(target.relative_to(repo_root))
    rc, out = _git(
        ["log", "--format=%s", "--", rel],
        repo_root,
    )
    if rc != 0:
        return 0
    count = 0
    for subject in out.splitlines():
        if any(marker in subject.lower() for marker in _SWEEP_MARKERS):
            continue
        count += 1
    return count


# Axis 2 only flags when low modification rate combines with low
# reference count. A frequently-cited foundation document with no
# substantive edits is doing its job (being a stable reference); it is
# not dead weight. The combined signal is stronger than either alone.
_AXIS_2_REFERENCE_CEILING = 5


def axis_last_mod_age(
    repo_root: Path,
    threshold_sessions: int = DEFAULT_AGE_THRESHOLD_SESSIONS,
) -> list[OrphanCandidate]:
    """Axis 2 — files unchanged for threshold+ sessions AND low-referenced.

    Approximation: if the file's substantive-commit count is 1 (initial
    commit only) AND the project has accumulated more than threshold
    archived sessions since AND inbound references are below
    ``_AXIS_2_REFERENCE_CEILING``, the file is a candidate. The dual
    filter prevents foundation reference docs (high-ref, stable) from
    surfacing — those are doing their job by existing.
    """
    candidates: list[OrphanCandidate] = []
    archive_dir = repo_root / "engine" / "session" / "archive"
    if not archive_dir.is_dir():
        return candidates
    archived_sessions = sorted(archive_dir.glob("S-[0-9][0-9][0-9][0-9].json"))
    total_sessions = len(archived_sessions)
    if total_sessions < threshold_sessions:
        return candidates  # Not enough history to judge.

    files = tracked_md_files(repo_root)
    for f in files:
        substantive_commits = _commits_count_for_path(repo_root, f)
        if substantive_commits > 1:
            continue
        refs = count_inbound_references(repo_root, f)
        if refs >= _AXIS_2_REFERENCE_CEILING:
            # Foundation document doing its job — surface only via
            # other axes if at all.
            continue
        rel = str(f.relative_to(repo_root))
        last_change = last_substantive_change(repo_root, f)
        sig = (
            f"only {substantive_commits} substantive commit(s) across "
            f"{total_sessions} sessions; {refs} inbound reference(s) "
            f"(below {_AXIS_2_REFERENCE_CEILING}-ref ceiling)"
        )
        candidates.append(
            OrphanCandidate(
                path=rel,
                axis="last-mod-age",
                signal=sig,
                last_substantive_change=last_change,
                inbound_references=refs,
            )
        )
    return candidates


_TABLE_SEP_RE = re.compile(r"^\|[\s|:-]+\|\s*$")


def _table_emptiness(text: str) -> tuple[int, int]:
    """Return (header_count, data_count) across all markdown tables.

    A "data row" is any pipe-row appearing after a separator row whose
    cells contain at least one non-whitespace character between pipes.
    Header rows and separator rows do not count as data.
    """
    header_count = 0
    data_count = 0
    saw_separator = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.startswith("|"):
            saw_separator = False
            continue
        if _TABLE_SEP_RE.match(line):
            saw_separator = True
            continue
        if not saw_separator:
            # First pipe-row in a table is the header.
            header_count += 1
            continue
        # Data row candidate.
        cells = line.strip("|").split("|")
        # Empty cells are all-whitespace; a real data row has at least
        # one non-whitespace character somewhere.
        if any(cell.strip() for cell in cells):
            data_count += 1
    return header_count, data_count


def axis_register_emptiness(repo_root: Path) -> list[OrphanCandidate]:
    """Axis 3 — register/log/queue files with no captured entries."""
    candidates: list[OrphanCandidate] = []
    for name in _REGISTER_FILE_NAMES:
        # Search common register locations.
        for loc in (repo_root / "product" / "docs", repo_root):
            target = loc / name
            if not target.is_file():
                continue
            text = target.read_text()
            header_count, data_count = _table_emptiness(text)
            if header_count and data_count == 0:
                rel = str(target.relative_to(repo_root))
                refs = count_inbound_references(repo_root, target)
                last_change = last_substantive_change(repo_root, target)
                sig = (
                    f"register table present ({header_count} header "
                    f"row(s)) but no data rows captured"
                )
                candidates.append(
                    OrphanCandidate(
                        path=rel,
                        axis="register-empty",
                        signal=sig,
                        last_substantive_change=last_change,
                        inbound_references=refs,
                    )
                )
    return candidates


# Threshold for ops-doc-uncited axis: minimum unique inbound file references
# (per count_inbound_references, which already discounts the operations/README.md
# index entry). An ops doc with fewer than this many unique inbound references
# AND unreachable from the boot-surface link graph is a candidate.
OPS_DOC_UNCITED_REF_THRESHOLD = 5

# Boot-surface seeds for axis 4. operations/README.md is intentionally NOT a
# seed — README.md is the ops-doc index, so seeding from it would make every
# ops doc trivially reachable, collapsing the axis. The BFS treats README.md as
# a "visited but not traversed" leaf when reached transitively.
_BOOT_SURFACE_SEEDS = (
    Path("engine/STATE.md"),
    Path("CLAUDE.md"),
)
_BOOT_SURFACE_LEAF_NAMES = ("README.md",)

_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _build_boot_surface_reachable_set(repo_root: Path) -> set[Path]:
    """BFS over markdown links starting from CLAUDE.md + engine/STATE.md.

    README.md files are visited as leaves (added to the reachable set) but not
    traversed into. This is because operations/README.md indexes every ops doc;
    seeding or traversing into it would make every ops doc reachable, defeating
    the axis. Docs are reachable iff some non-index doc links to them.

    Returns a set of resolved (canonical) Paths.
    """
    reachable: set[Path] = set()
    seeds: list[Path] = []
    for seed in _BOOT_SURFACE_SEEDS:
        seed_path = (repo_root / seed).resolve()
        if seed_path.exists():
            seeds.append(seed_path)
    repo_root_resolved = repo_root.resolve()
    queue: list[Path] = list(seeds)
    while queue:
        cur = queue.pop()
        if cur in reachable:
            continue
        reachable.add(cur)
        # Visit-but-don't-traverse for README.md leaves.
        if cur.name in _BOOT_SURFACE_LEAF_NAMES:
            continue
        try:
            text = cur.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in _MD_LINK_RE.finditer(text):
            target_raw = m.group(1).split("#", 1)[0].strip()
            if not target_raw or target_raw.startswith(
                ("http://", "https://", "mailto:")
            ):
                continue
            try:
                target_path = (cur.parent / target_raw).resolve()
            except OSError:
                continue
            try:
                target_path.relative_to(repo_root_resolved)
            except ValueError:
                continue
            if (
                target_path.exists()
                and target_path.is_file()
                and target_path.suffix == ".md"
            ):
                queue.append(target_path)
    return reachable


def axis_ops_doc_uncited(
    repo_root: Path, archives_to_check: int = 20
) -> list[OrphanCandidate]:
    """Axis 4 — operations docs that are BOTH low-referenced AND
    unreachable from the boot-surface link graph.

    Refined at S-0126 per Issue #89 / ADR 0062's audit-driven scope.
    The pre-S-0126 axis flagged ops docs whose basename did not appear in
    the concatenated text of the last N session archives — high
    false-positive rate against foundational ops docs that are consumed
    by behavior (e.g. session-build-lifecycle.md is read at every boot by
    the build SKILL) but rarely cited verbatim by name in outcome_summary
    prose. The refined axis combines two independent predicates with AND
    so a doc must fail BOTH signals before flagging.

    The ``archives_to_check`` parameter is retained for backward
    compatibility with the CLI but is unused by the refined predicate.
    """
    del archives_to_check  # retained for CLI compat; no longer consumed
    candidates: list[OrphanCandidate] = []
    ops_dir = repo_root / "engine" / "operations"
    if not ops_dir.is_dir():
        return candidates

    reachable = _build_boot_surface_reachable_set(repo_root)

    for ops_doc in sorted(ops_dir.glob("*.md")):
        if ops_doc.name == "README.md":
            continue
        refs = count_inbound_references(repo_root, ops_doc)
        is_reachable = ops_doc.resolve() in reachable
        if refs < OPS_DOC_UNCITED_REF_THRESHOLD and not is_reachable:
            rel = str(ops_doc.relative_to(repo_root))
            last_change = last_substantive_change(repo_root, ops_doc)
            sig = (
                f"{refs} unique inbound file reference(s) (threshold "
                f"{OPS_DOC_UNCITED_REF_THRESHOLD}) AND unreachable from "
                f"boot-surface link graph (CLAUDE.md / engine/STATE.md)"
            )
            candidates.append(
                OrphanCandidate(
                    path=rel,
                    axis="ops-doc-uncited",
                    signal=sig,
                    last_substantive_change=last_change,
                    inbound_references=refs,
                )
            )
    return candidates


def axis_stale_marker(
    repo_root: Path,
    threshold_sessions: int = DEFAULT_AGE_THRESHOLD_SESSIONS,
) -> list[OrphanCandidate]:
    """Axis 5 — files with pending-decision markers whose pinned trigger has
    passed (overdue) OR which carry no trigger annotation at all.

    Per S-0143 / Issue #111 the axis classifies each marker line via
    `is_marker_line_back_pinned()` and only counts back-pinned (overdue or
    unannotated) lines as stale. Markers explicitly forward-pinned to a
    future phase/session/OQ/external-trigger are deliberately deferred and
    do not produce false-positive findings — pre-S-0143 the axis flagged
    `expression-contract-instantiation.md`'s correctly-deferred Phase 7+
    TBDs at every cadence audit (S-0141 audit Cold-context probe finding).
    """
    candidates: list[OrphanCandidate] = []
    files = tracked_md_files(repo_root)
    archive_dir = repo_root / "engine" / "session" / "archive"
    if not archive_dir.is_dir():
        return candidates
    total_sessions = len(list(archive_dir.glob("S-[0-9][0-9][0-9][0-9].json")))

    current_phase = get_current_phase(repo_root)
    current_session = get_current_session(repo_root)

    for f in files:
        try:
            text = f.read_text()
        except OSError:
            continue
        # Find pending-marker lines AND classify each as back-pinned or
        # forward-pinned. Only back-pinned lines contribute to the flag.
        back_pinned_lines: list[str] = []
        forward_pinned_count = 0
        for line in text.splitlines():
            lower = line.lower()
            if not any(m in lower for m in _PENDING_MARKERS):
                continue
            if is_marker_line_back_pinned(line, current_phase, current_session):
                back_pinned_lines.append(line.strip())
            else:
                forward_pinned_count += 1

        if not back_pinned_lines:
            continue

        # Compute the file's age in sessions: total_sessions minus
        # the session count at the file's last substantive commit.
        substantive_commits = _commits_count_for_path(repo_root, f)
        if substantive_commits == 0:
            continue
        # Approximation: if the file has only 1-2 substantive commits but
        # has been on the books for many sessions with back-pinned markers,
        # the markers are stale candidates.
        if substantive_commits <= 2 and total_sessions >= threshold_sessions:
            rel = str(f.relative_to(repo_root))
            refs = count_inbound_references(repo_root, f)
            last_change = last_substantive_change(repo_root, f)
            preview = "; ".join(back_pinned_lines[:2])
            if len(back_pinned_lines) > 2:
                preview += f"; ... (+{len(back_pinned_lines) - 2} more)"
            forward_note = (
                f"; {forward_pinned_count} forward-pinned marker(s) skipped"
                if forward_pinned_count > 0
                else ""
            )
            sig = (
                f"{len(back_pinned_lines)} back-pinned marker(s) present, "
                f"file has only {substantive_commits} substantive commit(s) "
                f"across {total_sessions} sessions{forward_note}: {preview}"
            )
            candidates.append(
                OrphanCandidate(
                    path=rel,
                    axis="stale-marker",
                    signal=sig,
                    last_substantive_change=last_change,
                    inbound_references=refs,
                )
            )
    return candidates


def aggregate_candidates(
    repo_root: Path,
    age_threshold: int = DEFAULT_AGE_THRESHOLD_SESSIONS,
) -> list[OrphanCandidate]:
    """Run all five axes; return the concatenated candidate list.

    Each axis runs independently. A file may surface in multiple axes;
    the audit reads the per-axis annotations to triage.
    """
    out: list[OrphanCandidate] = []
    out.extend(axis_reference_count(repo_root))
    out.extend(axis_last_mod_age(repo_root, age_threshold))
    out.extend(axis_register_emptiness(repo_root))
    out.extend(axis_ops_doc_uncited(repo_root))
    out.extend(axis_stale_marker(repo_root, age_threshold))
    return out


def render_markdown(candidates: list[OrphanCandidate], session_id: str) -> str:
    """Render the candidate list as the dead-weight report markdown."""
    lines: list[str] = []
    lines.append(f"# Dead-weight candidates — {session_id}")
    lines.append("")
    lines.append(
        "> Auto-generated by `engine/tools/scan_orphans.py`. The audit "
        "session walks each candidate and judges against the operative "
        "diagnostic question: *Is this file doing the work it was created "
        "to do, or is it plumbing waiting for a function that never arrived?*"
    )
    lines.append("")
    lines.append(
        f"**{len(candidates)} candidate(s) flagged across 5 axes.** A file "
        f"may surface in multiple axes; that's a stronger dead-weight signal."
    )
    lines.append("")

    # Group by path so multi-axis candidates show their axes together.
    by_path: dict[str, list[OrphanCandidate]] = {}
    for c in candidates:
        by_path.setdefault(c.path, []).append(c)

    for path in sorted(by_path):
        entries = by_path[path]
        lines.append(f"### `{path}`")
        lines.append("")
        for c in entries:
            lines.append(f"- **Axis:** {c.axis}")
            lines.append(f"- **Signal:** {c.signal}")
            lines.append(f"- **Last substantive change:** {c.last_substantive_change}")
            lines.append(f"- **Inbound references:** {c.inbound_references}")
            lines.append("")
    return "\n".join(lines)


def render_json(candidates: list[OrphanCandidate]) -> str:
    """Render candidate list as JSON for machine consumers."""
    payload: list[dict[str, Any]] = [
        {
            "path": c.path,
            "axis": c.axis,
            "signal": c.signal,
            "last_substantive_change": c.last_substantive_change,
            "inbound_references": c.inbound_references,
        }
        for c in candidates
    ]
    return json.dumps(payload, indent=2)


_AXIS_DISPATCH = {
    "reference-count": lambda root, age: axis_reference_count(root),
    "last-mod-age": lambda root, age: axis_last_mod_age(root, age),
    "register-empty": lambda root, age: axis_register_emptiness(root),
    "ops-doc-uncited": lambda root, age: axis_ops_doc_uncited(root),
    "stale-marker": lambda root, age: axis_stale_marker(root, age),
}


def _detect_session_id(repo_root: Path) -> str:
    """Read engine/session/current.json's id, or return a placeholder."""
    current = repo_root / "engine" / "session" / "current.json"
    if not current.is_file():
        return "S-XXXX"
    try:
        data = json.loads(current.read_text())
    except (OSError, json.JSONDecodeError):
        return "S-XXXX"
    sid = data.get("id")
    return sid if isinstance(sid, str) else "S-XXXX"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Multi-axis dead-weight scanner for the project health-check. "
            "Surfaces candidates the audit triages against 'is this file "
            "doing the work it was created to do?'"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of markdown.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root (defaults to script's repo).",
    )
    parser.add_argument(
        "--age-threshold",
        type=int,
        default=DEFAULT_AGE_THRESHOLD_SESSIONS,
        help=(
            f"Sessions threshold for last-mod-age and stale-marker axes "
            f"(default {DEFAULT_AGE_THRESHOLD_SESSIONS})."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write to this path instead of stdout.",
    )
    parser.add_argument(
        "--axis",
        choices=sorted(_AXIS_DISPATCH.keys()),
        default=None,
        help="Restrict scan to one axis (for per-axis testing).",
    )
    args = parser.parse_args(argv)

    repo_root: Path = args.repo_root

    if args.axis:
        candidates = _AXIS_DISPATCH[args.axis](repo_root, args.age_threshold)
    else:
        candidates = aggregate_candidates(repo_root, args.age_threshold)

    if args.json:
        body = render_json(candidates)
    else:
        session_id = _detect_session_id(repo_root)
        body = render_markdown(candidates, session_id)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body)
        print(
            f"[scan-orphans] wrote {len(candidates)} candidate(s) to {args.output}",
            flush=True,
        )
    else:
        print(body, flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
