"""Routine-mode scope-check and master-plan-integrity tool.

Layer 1 contract per ADR 0051. Two enforcement points wired by the
pre-commit hook (and one boot-time check called by the routine-mode
boot procedure):

1. **Plan-vs-scope** (boot-time, ``--plan``): the routine session writes
   a session plan to ``engine/session/current_plan.md`` describing the
   files it intends to touch and which criteria it intends to address.
   This tool verifies the plan's ``paths_to_modify`` are all within the
   active task's ``scope_lock.allowed_paths`` (∪ the operational
   allowlist) AND that the plan references at least one criterion.

2. **Staged-vs-scope** (commit-time, ``--staged``): pre-commit invokes
   this against the currently staged file set. Same matcher, same
   allowlist. A staged file outside scope hard-fails the commit.

3. **Master-plan integrity** (commit-time, automatic when ``--staged``
   AND ``engine/session/auto_target.json`` is in the staged set): the
   diff is parsed; only ``tasks[*].status`` and ``tasks[*].blocked_reason``
   field changes are permitted in routine-mode commits. Any other key
   change hard-fails. Authoring/revising the master plan happens in
   interactive (non-routine) sessions only.

Routine-mode detection
----------------------
Routine mode is active when **all three** are true:

- ``engine/session/auto_target.json`` exists in the working tree.
- ``engine/session/current_plan.md`` exists (the routine boot procedure
  wrote it before any work).
- At least one task in the target file has ``status == "in_progress"``.

When any of these is false, the tool emits ``not in routine mode`` to
stderr and exits 0 (the pre-commit hook then takes the interactive
path, no scope-check applied).

Operational allowlist
---------------------
Always-permitted paths regardless of which task is active. The session
apparatus the routine itself runs on:

- ``engine/session/current.json``
- ``engine/session/current_plan.md``
- ``engine/session/auto_target.json`` (status field updates only —
  master-plan-integrity hook enforces this separately)
- ``engine/session/archive/S-*.json``
- ``engine/session/register_state.json``
- ``engine/session/diary_pending_index.json`` (per ADR 0056 — routine
  sessions that skip the engine_memory diary write at close append
  to this index so the next boot surfaces the deferred-diary count;
  the close commit must include this update or the entry is lost)
- ``engine/ENGINE_LOG.md`` (legacy; file moved to
  ``engine/changelog/_history/`` at S-0198 per ADR 0092 — entry is
  harmless dead code per ADR 0091 Option B residue acceptance)
- ``engine/changelog/**/*.md`` (per ADR 0092 — per-session changelog
  entries written at close in lieu of the retired monolithic ENGINE_LOG.md)
- ``HANDOFF.md``

Exit codes
----------
- ``0`` — pass (or not in routine mode → no-op).
- ``1`` — at least one violation found (per-violation detail to stderr).
- ``2`` — usage error (missing required args, malformed plan/target).

CLI
---
- ``check_routine_scope.py --plan PATH`` — check a plan file.
- ``check_routine_scope.py --staged`` — check staged files (and run
  master-plan-integrity automatically when applicable).
- ``check_routine_scope.py --task-id ID`` — override active task
  auto-detect; defaults to first ``in_progress`` task in the target.
- ``check_routine_scope.py --target PATH`` — override target file
  location (default: ``engine/session/auto_target.json``).
- ``check_routine_scope.py --repo-root PATH`` — override repo root
  for git invocations (test fixture support).

Out of scope
------------
- No correctness verification of the plan beyond scope/criteria coverage.
- No file mutation. Status writes happen elsewhere.
- No automatic recovery. Violations are reported; the caller decides.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# Local helper at engine/tools/scrub_env.py — see ADR 0045.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrub_env import scrubbed_env  # noqa: E402


# ---------------------------------------------------------------------------
# Operational allowlist — always-permitted paths in routine mode
# ---------------------------------------------------------------------------

OPERATIONAL_ALLOWLIST: tuple[str, ...] = (
    "engine/session/current.json",
    "engine/session/current_plan.md",
    "engine/session/auto_target.json",
    "engine/session/archive/S-*.json",
    "engine/session/register_state.json",
    # Per ADR 0056 (S-0091 routine-protection refinement). Routine sessions
    # whose mempalace diary write is skipped at close append an entry here
    # so the next boot can surface the deferred-diary count + IDs. This
    # write happens inside validate.py --final-check at shutdown step 1,
    # and the closing-commit must include the index update or the entry
    # is lost. Operational allowlist makes the write commit-able from
    # any routine task regardless of the active scope_lock.
    "engine/session/diary_pending_index.json",
    "engine/ENGINE_LOG.md",
    # Per ADR 0092 (S-0198 cutover; #147 closure at S-0200). Per-session
    # changelog entries at engine/changelog/<YYYY>/S-NNNN-<slug>.md replaced
    # the monolithic ENGINE_LOG.md. The close commit writes the entry
    # alongside STATE.md and archive; both routine and interactive build
    # sessions need this glob in the close-mode verifier (downstream
    # CLOSE_ALLOWED_GLOBS spreads from this tuple in both lifecycle wrappers).
    "engine/changelog/**/*.md",
    "HANDOFF.md",
)


# ---------------------------------------------------------------------------
# Path matching with proper / segmentation
# ---------------------------------------------------------------------------


def path_matches(path: str, pattern: str) -> bool:
    """Match a path against a glob pattern with /-aware segmentation.

    - ``*`` matches any non-``/`` characters within a single segment.
    - ``**`` matches zero or more whole segments.
    - Other fnmatch metacharacters (``?``, ``[seq]``) are honored
      per-segment.

    Examples
    --------
    >>> path_matches("engine/migrations/0042_x.sql", "engine/migrations/0042_*")
    True
    >>> path_matches("engine/migrations/0042/x.sql", "engine/migrations/0042_*")
    False
    >>> path_matches("a/b/c/d.md", "a/**/d.md")
    True
    """
    return _match_parts(path.split("/"), pattern.split("/"))


def _match_parts(path_parts: list[str], pat_parts: list[str]) -> bool:
    if not pat_parts:
        return not path_parts
    head = pat_parts[0]
    rest = pat_parts[1:]
    if head == "**":
        # ** matches zero or more whole segments.
        if not rest:
            return True
        for i in range(len(path_parts) + 1):
            if _match_parts(path_parts[i:], rest):
                return True
        return False
    if not path_parts:
        return False
    if "*" in head or "?" in head or "[" in head:
        if not fnmatch.fnmatchcase(path_parts[0], head):
            return False
    elif path_parts[0] != head:
        return False
    return _match_parts(path_parts[1:], rest)


def matches_any(path: str, patterns: list[str] | tuple[str, ...]) -> bool:
    return any(path_matches(path, p) for p in patterns)


# ---------------------------------------------------------------------------
# Routine-mode detection
# ---------------------------------------------------------------------------


@dataclass
class ModeContext:
    in_routine_mode: bool
    target_path: Path
    plan_path: Path
    target_data: dict[str, Any] | None
    active_task: dict[str, Any] | None
    reason_not_routine: str = ""


def detect_mode(repo_root: Path, target_override: Path | None = None) -> ModeContext:
    target_path = (
        target_override or repo_root / "engine" / "session" / "auto_target.json"
    )
    plan_path = repo_root / "engine" / "session" / "current_plan.md"

    if not target_path.exists():
        return ModeContext(
            False, target_path, plan_path, None, None, "auto_target.json absent"
        )
    if not plan_path.exists():
        return ModeContext(
            False, target_path, plan_path, None, None, "current_plan.md absent"
        )

    try:
        target_data = json.loads(target_path.read_text())
    except json.JSONDecodeError as exc:
        return ModeContext(
            False, target_path, plan_path, None, None, f"target malformed: {exc!s}"
        )

    active_task = next(
        (t for t in target_data.get("tasks", []) if t.get("status") == "in_progress"),
        None,
    )
    if active_task is None:
        return ModeContext(
            False, target_path, plan_path, target_data, None, "no in_progress task"
        )

    return ModeContext(True, target_path, plan_path, target_data, active_task)


# ---------------------------------------------------------------------------
# Plan parsing
# ---------------------------------------------------------------------------


_PATHS_RE = re.compile(
    r"^paths_to_modify:\s*\[(?P<body>.*?)\]\s*$", re.MULTILINE | re.DOTALL
)
_CRITERIA_RE = re.compile(
    r"^criteria_addressed:\s*\[(?P<body>.*?)\]\s*$", re.MULTILINE | re.DOTALL
)


@dataclass
class PlanContents:
    paths_to_modify: list[str]
    criteria_addressed: list[str]


def parse_plan(text: str) -> PlanContents:
    """Parse a session plan markdown file.

    Required fields (one each, anywhere in the body):
    - ``paths_to_modify: [<comma-separated quoted strings>]``
    - ``criteria_addressed: [<comma-separated quoted strings or ints>]``

    The fields may appear inside fenced code blocks or as top-level
    lines; the regex matches either. Extra text (rationale prose) is
    preserved/ignored.
    """
    paths_match = _PATHS_RE.search(text)
    criteria_match = _CRITERIA_RE.search(text)
    paths = _parse_list(paths_match.group("body")) if paths_match else []
    criteria = _parse_list(criteria_match.group("body")) if criteria_match else []
    return PlanContents(paths_to_modify=paths, criteria_addressed=criteria)


def _parse_list(body: str) -> list[str]:
    """Parse a comma-separated list of quoted strings or bare tokens."""
    body = body.strip()
    if not body:
        return []
    items: list[str] = []
    for raw in body.split(","):
        item = raw.strip().strip('"').strip("'")
        if item:
            items.append(item)
    return items


# ---------------------------------------------------------------------------
# Violation reporting
# ---------------------------------------------------------------------------


@dataclass
class Violation:
    kind: str  # "out_of_scope" | "no_criteria_addressed" | "master_plan_non_status"
    detail: str


def _allowed_patterns_for(task: dict[str, Any]) -> list[str]:
    scope = task.get("scope_lock") or {}
    return list(scope.get("allowed_paths", [])) + list(OPERATIONAL_ALLOWLIST)


# ---------------------------------------------------------------------------
# Plan check
# ---------------------------------------------------------------------------


def check_plan(plan: PlanContents, task: dict[str, Any]) -> list[Violation]:
    violations: list[Violation] = []
    allowed = _allowed_patterns_for(task)
    for path in plan.paths_to_modify:
        if not matches_any(path, allowed):
            violations.append(
                Violation(
                    "out_of_scope",
                    f"plan path '{path}' not in scope_lock or operational allowlist",
                )
            )
    if not plan.criteria_addressed:
        violations.append(
            Violation(
                "no_criteria_addressed", "plan must reference at least one criterion"
            )
        )
    return violations


# ---------------------------------------------------------------------------
# Staged check
# ---------------------------------------------------------------------------


def get_staged_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=scrubbed_env(),
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def check_staged(staged: list[str], task: dict[str, Any]) -> list[Violation]:
    violations: list[Violation] = []
    allowed = _allowed_patterns_for(task)
    for path in staged:
        if not matches_any(path, allowed):
            violations.append(
                Violation(
                    "out_of_scope",
                    f"staged file '{path}' not in scope_lock or operational allowlist",
                )
            )
    return violations


# ---------------------------------------------------------------------------
# Master-plan integrity check
# ---------------------------------------------------------------------------


def get_target_diff(
    repo_root: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Return (head_target, staged_target) — pre- and post-images of auto_target.json.

    Returns (None, None) when auto_target.json isn't staged or HEAD has no version.
    """
    head_target: dict[str, Any] | None = None
    staged_target: dict[str, Any] | None = None

    head_result = subprocess.run(
        ["git", "show", "HEAD:engine/session/auto_target.json"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    if head_result.returncode == 0:
        try:
            head_target = json.loads(head_result.stdout)
        except json.JSONDecodeError:
            head_target = None

    staged_result = subprocess.run(
        ["git", "diff", "--cached", "--", "engine/session/auto_target.json"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    if not staged_result.stdout.strip():
        return head_target, None  # not staged

    # Read the staged content via `git show :auto_target.json`
    show_result = subprocess.run(
        ["git", "show", ":engine/session/auto_target.json"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    if show_result.returncode == 0:
        try:
            staged_target = json.loads(show_result.stdout)
        except json.JSONDecodeError:
            staged_target = None

    return head_target, staged_target


_STATUS_FIELDS: tuple[str, ...] = ("status", "blocked_reason")


def check_master_plan_integrity(
    head_target: dict[str, Any] | None, staged_target: dict[str, Any] | None
) -> list[Violation]:
    """Return violations for non-status changes to auto_target.json."""
    violations: list[Violation] = []
    if head_target is None or staged_target is None:
        # First introduction of auto_target.json (HEAD has none) is
        # always an interactive-session act, not a routine commit. The
        # mode-detection in main() already gates on routine-mode being
        # active; if we got here, the diff is meaningful.
        if head_target is None and staged_target is not None:
            # Routine session committing the first auto_target.json — should never
            # happen because routine mode requires an in_progress task, which
            # requires a pre-existing target. Treat as violation.
            violations.append(
                Violation(
                    "master_plan_non_status",
                    "auto_target.json being newly added in a routine commit (master plan must be authored in interactive sessions)",
                )
            )
        return violations

    # Top-level keys other than 'tasks' must be unchanged.
    for key in set(head_target.keys()) | set(staged_target.keys()):
        if key == "tasks":
            continue
        if head_target.get(key) != staged_target.get(key):
            violations.append(
                Violation(
                    "master_plan_non_status",
                    f"top-level key '{key}' changed in routine commit",
                )
            )

    # Walk tasks pairwise by id and compare each field.
    head_tasks = {t.get("id"): t for t in head_target.get("tasks", [])}
    staged_tasks = {t.get("id"): t for t in staged_target.get("tasks", [])}

    if set(head_tasks.keys()) != set(staged_tasks.keys()):
        violations.append(
            Violation(
                "master_plan_non_status",
                f"task id set changed (head: {sorted(head_tasks.keys())}, staged: {sorted(staged_tasks.keys())})",
            )
        )

    for tid in set(head_tasks.keys()) & set(staged_tasks.keys()):
        h, s = head_tasks[tid], staged_tasks[tid]
        for field in set(h.keys()) | set(s.keys()):
            if field in _STATUS_FIELDS:
                continue
            if h.get(field) != s.get(field):
                violations.append(
                    Violation(
                        "master_plan_non_status",
                        f"task '{tid}' field '{field}' changed in routine commit",
                    )
                )

    return violations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _select_task(target: dict[str, Any], task_id: str | None) -> dict[str, Any] | None:
    if task_id:
        return next(
            (t for t in target.get("tasks", []) if t.get("id") == task_id), None
        )
    return next(
        (t for t in target.get("tasks", []) if t.get("status") == "in_progress"), None
    )


def _emit_violations(violations: list[Violation]) -> None:
    for v in violations:
        print(f"  [{v.kind}] {v.detail}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Routine-mode scope-check and master-plan-integrity"
    )
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--plan",
        metavar="PATH",
        help="Check a plan file's paths_to_modify and criteria_addressed",
    )
    mode.add_argument(
        "--staged",
        action="store_true",
        help="Check staged files (and master-plan integrity)",
    )
    ap.add_argument("--task-id", help="Override active-task auto-detect")
    ap.add_argument("--target", help="Override target file path")
    ap.add_argument("--repo-root", help="Override repo root")
    args = ap.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT
    target_override = Path(args.target) if args.target else None

    ctx = detect_mode(repo_root, target_override)
    if not ctx.in_routine_mode:
        print(
            f"not in routine mode ({ctx.reason_not_routine}); skipping scope-check",
            file=sys.stderr,
        )
        return 0

    assert ctx.target_data is not None
    task = _select_task(ctx.target_data, args.task_id)
    if task is None:
        print(f"no eligible task found (task_id={args.task_id})", file=sys.stderr)
        return 2

    violations: list[Violation] = []

    if args.plan:
        plan_path = Path(args.plan)
        if not plan_path.exists():
            print(f"plan file not found: {plan_path}", file=sys.stderr)
            return 2
        plan = parse_plan(plan_path.read_text())
        violations.extend(check_plan(plan, task))
    else:
        # --staged
        try:
            staged = get_staged_files(repo_root)
        except subprocess.CalledProcessError as exc:
            print(f"git diff failed: {exc!s}", file=sys.stderr)
            return 2
        violations.extend(check_staged(staged, task))

        if "engine/session/auto_target.json" in staged:
            head_target, staged_target = get_target_diff(repo_root)
            violations.extend(check_master_plan_integrity(head_target, staged_target))

    if violations:
        print(
            f"check_routine_scope: {len(violations)} violation(s) for task '{task.get('id')}':",
            file=sys.stderr,
        )
        _emit_violations(violations)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
