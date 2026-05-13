"""Detect a halted-routine wedge and idempotently file Issue + HANDOFF.

Layer 1 contract per ADR 0060.

Purpose
-------
Issue #58 surfaced a class of routine-mode failure: S-0117 was
eager-claimed for AUDIT-HT and halted post-eager-claim mid-authoring,
leaving ``register_state.current_status: in_progress``,
``current.json.id: S-0117``, and ``auto_target.json[AUDIT-HT].status:
in_progress`` with no archive. The routine-mode-lifecycle skill body
had no recovery branch for this shape, so every subsequent hourly
fire of ``paideia-engine-loop`` ran through the boot, found no
eligible task at step 5, wrote a HANDOFF entry, and exited — producing
HANDOFF spam until a human paused the routine and adjudicated.

This tool runs at boot step ``0c``, between concurrency-lock acquire
(per ADR 0082) and target precondition (step 1). When the wedge shape
matches, it idempotently authors a single Issue (via ``gh issue
create``) and a single HANDOFF.md section, then exits 2 — the routine
boot reads exit 2 and exits cleanly without claiming. Subsequent fires
re-detect the wedge, see the existing Issue + HANDOFF section, skip
the author step, and exit cleanly. No spam.

Wedge shape (mechanical predicate, all conjuncts)
-------------------------------------------------
1. ``register_state.current_status == "in_progress"``.
2. ``current.json.id`` matches ``^S-\\d{4}$`` AND
   ``current.json.status == "in_progress"``.
3. No ``engine/session/archive/<current.id>.json`` at HEAD.
4. The routine lock is acquirable (no other routine holds it).
5. ``current.json`` names a ``task_id`` AND
   ``auto_target.json[task_id].status == "in_progress"``.
6. HEAD is at-or-behind ``origin/main`` with no local commits ahead.

ALL conjuncts hold → wedge → exit 2 (after authoring artifacts).
ANY conjunct fails → no wedge → exit 0 (boot proceeds).
Borderline / ambiguous shape → exit 3 (boot writes HANDOFF, exits).

Exit codes
----------
- ``0`` — no wedge detected; routine boot proceeds to step 1.
- ``2`` — wedge detected; Issue + HANDOFF authored (or already
  present); routine boot releases lock and exits without claiming.
- ``3`` — refusal due to ambiguous shape (e.g., HEAD ahead of
  origin/main with a non-eager-claim subject); routine boot writes
  HANDOFF "wedge detection refused: ambiguous state" and exits.
- ``5`` — generic failure (gh CLI error, file-system error); routine
  boot writes HANDOFF naming the failure and exits cleanly.

CLI
---
- ``routine_wedge_detect.py`` — runs the predicate, files artifacts on
  wedge.
- ``--repo-root PATH`` — override repo root (test fixtures).
- ``--remote NAME`` — override remote name (default: ``origin``).
- ``--target-branch NAME`` — override target branch (default: ``main``).
- ``--dry-run`` — run the predicate and report findings; do NOT file
  Issue or append HANDOFF. Used by tests + by humans investigating.
- ``--skip-gh`` — author HANDOFF only; skip ``gh issue create``. Used
  in test fixtures and offline contexts.

Out of scope
------------
- Recovery itself. The tool refuses to administratively close the
  wedged session — auto-close requires synthesizing the structured
  archive fields (``outcome_summary``, ``outcome_summary_soft_warns``,
  ``mempalace_activity``) without the halted session's input, which
  silently corrupts downstream telemetry. Recovery is interactive
  per ADR 0060 + ADR 0042.
- Cross-checkout wedge detection. The tool inspects the local
  repo's shared state. A wedge that lives only on origin/main but
  not the local checkout is a freshness-gate concern (ADR 0082),
  not this tool's concern.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

SESSION_ID_PATTERN = re.compile(r"^S-\d{4}$")

ISSUE_TITLE_TEMPLATE = (
    "Routine wedge: halted prior session leaves {task_id} in_progress "
    "with no recovery path"
)
HANDOFF_HEADING_TEMPLATE = "### Routine wedge detected ({session_id})"


def _run_git(args: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )


def get_head_subject(repo: Path) -> str | None:
    result = _run_git(["log", "--format=%s", "-n", "1", "HEAD"], repo)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_ahead_count(repo: Path, remote: str, target: str) -> int | None:
    ref = f"{remote}/{target}"
    result = _run_git(["rev-list", "--count", f"{ref}..HEAD"], repo)
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def archive_exists_at_head(repo: Path, session_id: str) -> bool:
    """Check whether engine/session/archive/<session_id>.json exists at HEAD."""
    rel = f"engine/session/archive/{session_id}.json"
    result = _run_git(["cat-file", "-e", f"HEAD:{rel}"], repo)
    return result.returncode == 0


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        loaded = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(loaded, dict):
        return None
    return loaded


def detect_wedge(
    repo: Path, remote: str = "origin", target: str = "main"
) -> tuple[str, str | None, dict[str, Any] | None]:
    """Run the wedge-shape predicate.

    Returns a tuple ``(disposition, reason, payload)`` where:
    - ``disposition`` is one of ``"wedge"``, ``"clean"``, ``"ambiguous"``.
    - ``reason`` is the cause when not a clean wedge (None on wedge or
      clean).
    - ``payload`` carries ``current.id``, ``current.task_id``,
      ``register_state``, and ``auto_target_task`` when disposition is
      ``"wedge"`` (None otherwise).
    """
    register_path = repo / "engine" / "session" / "register_state.json"
    current_path = repo / "engine" / "session" / "current.json"
    target_path = repo / "engine" / "session" / "auto_target.json"

    register = _read_json(register_path)
    if register is None:
        return "clean", "register_state.json absent or malformed", None
    if register.get("current_status") != "in_progress":
        return "clean", f"current_status={register.get('current_status')!r}", None

    current = _read_json(current_path)
    if current is None:
        # current_status: in_progress but current.json missing — that's
        # genuinely ambiguous (eager-claim wrote register but not current?
        # Or close already happened but didn't flip register?). Refuse.
        return "ambiguous", "register says in_progress but current.json absent", None

    session_id = current.get("id")
    if not isinstance(session_id, str) or not SESSION_ID_PATTERN.match(session_id):
        return (
            "ambiguous",
            f"current.json.id is not a valid S-NNNN: {session_id!r}",
            None,
        )
    if current.get("status") != "in_progress":
        return (
            "ambiguous",
            f"current.json.status={current.get('status')!r} but register says in_progress",
            None,
        )

    if archive_exists_at_head(repo, session_id):
        # Archive already exists — the close commit landed but
        # register/current somehow weren't cleaned up. That's a
        # different bug class than the wedge.
        return (
            "ambiguous",
            f"archive/{session_id}.json exists at HEAD but register/current still in_progress",
            None,
        )

    task_id = current.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        # Interactive sessions don't carry task_id. The wedge predicate
        # is routine-mode-specific (master-plan task tracking is the
        # signal). No task_id → not a routine wedge.
        return "clean", "current.json has no task_id (interactive session)", None

    target_doc = _read_json(target_path)
    if target_doc is None:
        return "ambiguous", "auto_target.json absent or malformed", None

    matched_task = next(
        (t for t in target_doc.get("tasks", []) if t.get("id") == task_id),
        None,
    )
    if matched_task is None:
        return (
            "ambiguous",
            f"current.task_id={task_id!r} not found in auto_target.json",
            None,
        )
    if matched_task.get("status") != "in_progress":
        return (
            "ambiguous",
            f"task {task_id!r} status={matched_task.get('status')!r} (expected in_progress)",
            None,
        )

    ahead = get_ahead_count(repo, remote, target)
    if ahead is None:
        return "ambiguous", "could not determine ahead count vs origin/main", None
    if ahead > 0:
        # HEAD has commits not yet on origin/main — the routine that
        # claimed the slot may still be running, or partial-shutdown
        # work hasn't pushed. Either way, not a clean wedge.
        return (
            "ambiguous",
            f"HEAD is {ahead} commits ahead of {remote}/{target}; not a wedge",
            None,
        )

    payload = {
        "session_id": session_id,
        "task_id": task_id,
        "register": register,
        "current": current,
        "auto_target_task": matched_task,
    }
    return "wedge", None, payload


def find_existing_issue(repo: Path, task_id: str) -> int | None:
    """Search GitHub for an open Issue matching the wedge title pattern.

    Uses ``gh issue list`` JSON output. Returns the issue number if a
    match exists; None otherwise. None is also returned on gh failure
    (no auth, network outage) — caller treats absent-issue and
    cannot-query-github as the same case (proceed to author).
    """
    if shutil.which("gh") is None:
        return None
    title_pattern = ISSUE_TITLE_TEMPLATE.format(task_id=task_id)
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--state",
            "open",
            "--search",
            title_pattern,
            "--json",
            "number,title",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    try:
        issues = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    for issue in issues:
        if issue.get("title", "").startswith(title_pattern):
            number = issue.get("number")
            if isinstance(number, int):
                return number
    return None


def create_issue(repo: Path, payload: dict[str, Any]) -> int | None:
    """File a new Issue. Returns the issue number on success; None on failure."""
    if shutil.which("gh") is None:
        return None
    title = ISSUE_TITLE_TEMPLATE.format(task_id=payload["task_id"])
    body = (
        f"## Symptom\n\n"
        f"Routine wedge detected at {payload['session_id']} boot per "
        f"`engine/tools/routine_wedge_detect.py`. The session "
        f"`{payload['session_id']}` was eager-claimed for task "
        f"`{payload['task_id']}` and halted post-eager-claim — "
        f"register_state.json shows `current_status: in_progress`, "
        f"current.json carries `id: {payload['session_id']}` with "
        f"`status: in_progress`, and `auto_target.json[{payload['task_id']}]"
        f".status: in_progress`. No archive exists at HEAD.\n\n"
        f"## Why this is a wedge\n\n"
        f"Per ADR 0060, the routine-mode-lifecycle boot step 5 "
        f"(eligibility) requires `status == pending`. With "
        f"`{payload['task_id']}` pinned at `in_progress`, no task is "
        f"eligible. Without the wedge-detect-and-pause step (this Issue's "
        f"author), every subsequent hourly fire would emit a HANDOFF "
        f"entry with no clearing mechanism. The detect-and-pause step "
        f"converts that to one Issue + one HANDOFF entry; this is that "
        f"Issue.\n\n"
        f"## Adjudication required (interactive)\n\n"
        f"Per ADR 0060, recovery requires master-plan-revision-class "
        f"judgment that routine mode defers. Pause `paideia-engine-loop` "
        f"and run an interactive `/start-engine` session to:\n\n"
        f"1. Decide AUDIT-HT-style disposition (reset to pending, "
        f"decompose, or deliver interactively).\n"
        f"2. Administratively close `{payload['session_id']}` per the "
        f"S-0117 → S-0118 worked example "
        f"([commit 48a6ac9](https://github.com/StarshipSuperjam/paideia/commit/48a6ac9)).\n"
        f"3. Re-enable the routine.\n\n"
        f"## References\n\n"
        f"- [ADR 0060](https://github.com/StarshipSuperjam/paideia/blob/main/engine/adr/0060-routine-wedge-detect-and-pause.md) — "
        f"wedge-detect-and-pause mechanism.\n"
        f"- [Issue #58](https://github.com/StarshipSuperjam/paideia/issues/58) — "
        f"original report (S-0117 wedge).\n"
    )
    result = subprocess.run(
        [
            "gh",
            "issue",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--label",
            "bug",
            "--label",
            "priority:urgent",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    # gh prints the URL; parse the number from the trailing path.
    url = result.stdout.strip()
    match = re.search(r"/issues/(\d+)$", url)
    if match:
        return int(match.group(1))
    return None


def handoff_section_exists(handoff_path: Path, session_id: str) -> bool:
    if not handoff_path.is_file():
        return False
    heading = HANDOFF_HEADING_TEMPLATE.format(session_id=session_id)
    return heading in handoff_path.read_text()


def author_handoff_section(
    handoff_path: Path, payload: dict[str, Any], issue_number: int | None
) -> None:
    """Append a wedge-detected section to HANDOFF.md.

    Caller has confirmed the section does not already exist.
    """
    heading = HANDOFF_HEADING_TEMPLATE.format(session_id=payload["session_id"])
    issue_ref = f"#{issue_number}" if issue_number is not None else "(gh-create-failed)"
    section = (
        f"\n{heading}\n\n"
        f"Routine boot at this fire detected a halted-routine wedge: "
        f"`{payload['session_id']}` was eager-claimed for task "
        f"`{payload['task_id']}` and halted post-eager-claim. "
        f"`register_state.current_status` and `current.json.status` and "
        f"`auto_target.json[{payload['task_id']}].status` all read "
        f"`in_progress` with no archive at HEAD.\n\n"
        f"Per ADR 0060, this routine fire authored an idempotent Issue "
        f"+ this HANDOFF entry, then exits without claiming. Subsequent "
        f"fires will detect the existing artifacts and skip-author. "
        f"Recovery requires interactive adjudication — see Issue "
        f"{issue_ref}.\n\n"
        f"**Disposition:** tracked-as-issue {issue_ref}\n"
    )
    if not handoff_path.is_file():
        handoff_path.write_text("# HANDOFF\n" + section)
        return
    existing = handoff_path.read_text()
    handoff_path.write_text(existing.rstrip() + "\n" + section)


def commit_handoff(repo: Path, session_id: str) -> bool:
    """Stage HANDOFF.md and create the wedge-detect commit. Returns success."""
    add = _run_git(["add", "HANDOFF.md"], repo)
    if add.returncode != 0:
        return False
    commit = _run_git(
        [
            "commit",
            "-m",
            f"chore(session): wedge-detect-and-pause for {session_id}",
        ],
        repo,
    )
    return commit.returncode == 0


def push_handoff(repo: Path, remote: str, target: str) -> tuple[bool, str]:
    """Push the wedge-detect commit to remote/target via subprocess.

    Routine sessions use the same subprocess-bypass pattern that
    routine_lifecycle_push.py uses to bypass the Default Branch Push gate
    (per ADR 0054). The push is required so subsequent routine fires
    (which create fresh worktrees) read the existing HANDOFF entry from
    origin/main rather than re-authoring locally.

    Returns (ok, reason).
    """
    refspec = f"HEAD:{target}"
    result = _run_git(["push", remote, refspec], repo)
    if result.returncode == 0:
        return True, "pushed"
    err = result.stderr.strip() or result.stdout.strip() or "unknown error"
    return False, err


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Detect a halted-routine wedge and idempotently file Issue + "
            "HANDOFF. Per ADR 0060."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repo root (default: script's repo).",
    )
    parser.add_argument(
        "--remote",
        type=str,
        default="origin",
        help="Remote name (default: origin).",
    )
    parser.add_argument(
        "--target-branch",
        type=str,
        default="main",
        help="Target branch (default: main).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the predicate; do not author Issue / HANDOFF.",
    )
    parser.add_argument(
        "--skip-gh",
        action="store_true",
        help="Skip gh issue create; HANDOFF only.",
    )
    parser.add_argument(
        "--skip-push",
        action="store_true",
        help=(
            "Skip pushing the wedge-detect commit to origin/main. "
            "Used in test fixtures and offline contexts. "
            "Production routine fires MUST push so cross-fire idempotency "
            "holds — fresh worktrees read HANDOFF from origin/main."
        ),
    )
    args = parser.parse_args(argv)

    repo: Path = args.repo_root

    # Idempotency short-circuit: if current.json names a session and the
    # HANDOFF section for that session already exists, skip the predicate
    # entirely. Catches the post-author-pre-push case where HEAD is 1
    # ahead with the wedge-detect commit — that would otherwise trip the
    # detect_wedge HEAD-ahead-vs-origin ambiguous branch and re-author
    # spuriously.
    current_path = repo / "engine" / "session" / "current.json"
    handoff_path = repo / "HANDOFF.md"
    early_current = _read_json(current_path)
    if isinstance(early_current, dict):
        early_session_id = early_current.get("id")
        if (
            isinstance(early_session_id, str)
            and SESSION_ID_PATTERN.match(early_session_id)
            and handoff_section_exists(handoff_path, early_session_id)
        ):
            print(
                f"[wedge-detect] idempotent: HANDOFF section already "
                f"present for {early_session_id}; routine boot exits "
                f"without re-authoring.",
                file=sys.stderr,
            )
            return 2

    disposition, reason, payload = detect_wedge(repo, args.remote, args.target_branch)

    if disposition == "clean":
        print(
            f"[wedge-detect] clean ({reason}); routine boot proceeds.",
            file=sys.stderr,
        )
        return 0

    if disposition == "ambiguous":
        print(
            f"[wedge-detect] AMBIGUOUS — refusing wedge call: {reason}",
            file=sys.stderr,
        )
        return 3

    assert disposition == "wedge" and payload is not None

    print(
        f"[wedge-detect] WEDGE detected: session={payload['session_id']} "
        f"task={payload['task_id']}",
        file=sys.stderr,
    )

    if args.dry_run:
        print(
            "[wedge-detect] dry-run: would author Issue + HANDOFF and exit 2.",
            file=sys.stderr,
        )
        return 2

    handoff_path = repo / "HANDOFF.md"
    # Short-circuit idempotency check: if the HANDOFF section already
    # exists for THIS wedged session_id (regardless of HEAD-ahead state
    # the predicate may flag), the artifacts are authored — exit 2.
    # Prevents the false-ambiguous trip when the wedge-detect commit is
    # locally present but unpushed (test fixture or post-author repeat).
    handoff_already_authored = handoff_section_exists(
        handoff_path, payload["session_id"]
    )

    issue_number: int | None = None
    if not args.skip_gh:
        issue_number = find_existing_issue(repo, payload["task_id"])
        if issue_number is None and not handoff_already_authored:
            # Only create an Issue on the first detection. Subsequent
            # fires either find the existing Issue (idempotent) or have
            # the HANDOFF entry as the indicator.
            issue_number = create_issue(repo, payload)

    if handoff_already_authored:
        print(
            f"[wedge-detect] HANDOFF section already present for "
            f"{payload['session_id']}; skip-author (idempotent).",
            file=sys.stderr,
        )
        return 2

    try:
        author_handoff_section(handoff_path, payload, issue_number)
    except OSError as exc:
        print(
            f"[wedge-detect] FAILED to author HANDOFF section: {exc}",
            file=sys.stderr,
        )
        return 5

    if not commit_handoff(repo, payload["session_id"]):
        print(
            "[wedge-detect] FAILED to commit HANDOFF entry",
            file=sys.stderr,
        )
        return 5

    if not args.skip_push:
        ok, reason = push_handoff(repo, args.remote, args.target_branch)
        if not ok:
            # Commit landed locally but push failed. The Issue is the
            # cross-fire signal of last resort; the local HANDOFF will
            # be lost when the worktree is swept. Surface the failure
            # but still return 2 (the immediate routine fire still
            # exits cleanly without claiming).
            print(
                f"[wedge-detect] commit landed locally but push FAILED "
                f"({reason}); cross-fire idempotency depends on the "
                f"Issue. Routine boot exits anyway.",
                file=sys.stderr,
            )

    print(
        f"[wedge-detect] authored HANDOFF section + Issue "
        f"{'#' + str(issue_number) if issue_number is not None else '(deferred)'}; "
        f"routine boot exits cleanly.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
