"""Tests for the env-pointer probe in engine/tools/hooks/session-start.sh.

Covers Issue #50 (S-0099): worktree-launched sessions must consult the
parent main repo's .env when the worktree has no .env (or no
SUPABASE_DB_URL line). Original Issue #7 / S-0048 contract preserved:
LOUD pointer still fires when neither location carries the URL.

Test isolation strategy
-----------------------
- ``tmp_path`` fixtures construct a real git repo + linked worktree per
  test so ``git rev-parse --git-common-dir`` returns the genuine value
  the production hook will see.
- Each test runs the actual session-start.sh script via subprocess and
  asserts on whether the LOUD ``.env onboarding pointer`` block appears
  in stderr. The full hook does many other things (validate, conflict-
  check, mempalace probes) and can exit at intermediate points in tmp-
  dir fixtures where downstream tools aren't installed; the LOUD block
  is emitted at line 274 — well before any of those failure points —
  so its presence/absence is the reliable surface.

Non-responsibilities
--------------------
- Does not test the LOUD-block prose verbatim. The LOUD block's wording
  belongs to Issue #7 / S-0048; this fix only changes the resolution.
- Does not exercise the auto_target.json gate. The probe is conditional
  on auto_target.json existing; tests construct it on every fixture.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / "engine" / "tools" / "hooks" / "session-start.sh"

LOUD_BLOCK_MARKER = "[session-start] .env onboarding pointer"

ENV_WITH_URL = "SUPABASE_DB_URL=postgresql://stub:stub@localhost/stub\n"


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _seed_repo_skeleton(repo_root: Path) -> None:
    """Create the minimum file skeleton session-start.sh expects.

    The hook reads register_state.json and walks engine/session/. Without
    these the hook would error out before reaching the env-pointer block.
    """
    (repo_root / "engine" / "session").mkdir(parents=True, exist_ok=True)
    (repo_root / "engine" / "session" / "register_state.json").write_text(
        '{"next_id": "0001", "last_claimed": null, "current_status": "closed",'
        ' "health_check_cadence": 20, "last_audit_session": "S-0001"}\n'
    )
    (repo_root / "engine" / "session" / "archive").mkdir(parents=True, exist_ok=True)
    (repo_root / "engine" / "session" / "auto_target.json").write_text(
        '{"target_id": "T-NONE", "tasks": []}\n'
    )
    (repo_root / "engine" / "tools").mkdir(parents=True, exist_ok=True)
    # An empty scrub_env.sh stub satisfies the source line in the hook.
    (repo_root / "engine" / "tools" / "scrub_env.sh").write_text(
        "#!/bin/bash\nscrub_git_env() { :; }\n"
    )


def _make_main_repo(tmp_path: Path, with_env_url: bool) -> Path:
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q", "-b", "main")
    _seed_repo_skeleton(main)
    _git(main, "add", "-A")
    _git(
        main, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init"
    )
    if with_env_url:
        (main / ".env").write_text(ENV_WITH_URL)
    return main


def _make_worktree(main: Path, with_env_url: bool) -> Path:
    wt = main / ".claude" / "worktrees" / "test_wt"
    (main / ".claude" / "worktrees").mkdir(parents=True, exist_ok=True)
    _git(main, "worktree", "add", "-q", str(wt), "-b", "test_branch")
    if with_env_url:
        (wt / ".env").write_text(ENV_WITH_URL)
    return wt


def _run_hook(cwd: Path) -> str:
    """Invoke session-start.sh in cwd; return combined stderr+stdout text.

    The hook may exit non-zero or hit unrelated failures in the tmp-dir
    fixture (mempalace probe, validator, etc.). We tolerate any exit code
    and rely on greping the env-pointer surface.
    """
    result = subprocess.run(
        ["bash", str(HOOK_SCRIPT)],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.stdout + result.stderr


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_loud_silent_when_parent_has_url_worktree_has_none(
    tmp_path: Path,
) -> None:
    """Issue #50 fix: parent has .env+URL, worktree has no .env. No LOUD."""
    main = _make_main_repo(tmp_path, with_env_url=True)
    wt = _make_worktree(main, with_env_url=False)
    output = _run_hook(wt)
    assert LOUD_BLOCK_MARKER not in output, output


def test_loud_fires_when_neither_has_url(tmp_path: Path) -> None:
    """Original Issue #7 / S-0048 contract: neither location has URL → LOUD."""
    main = _make_main_repo(tmp_path, with_env_url=False)
    wt = _make_worktree(main, with_env_url=False)
    output = _run_hook(wt)
    assert LOUD_BLOCK_MARKER in output, output


def test_loud_silent_when_worktree_has_url(tmp_path: Path) -> None:
    """Worktree's own .env carries the URL — fast path; parent ignored."""
    main = _make_main_repo(tmp_path, with_env_url=False)
    wt = _make_worktree(main, with_env_url=True)
    output = _run_hook(wt)
    assert LOUD_BLOCK_MARKER not in output, output


def test_loud_silent_when_main_repo_only_has_url(tmp_path: Path) -> None:
    """Non-worktree session with .env+URL — same-path fallback is idempotent."""
    main = _make_main_repo(tmp_path, with_env_url=True)
    output = _run_hook(main)
    assert LOUD_BLOCK_MARKER not in output, output


def test_loud_fires_when_main_repo_only_no_url(tmp_path: Path) -> None:
    """Non-worktree session with no .env — LOUD pointer (regression bar)."""
    main = _make_main_repo(tmp_path, with_env_url=False)
    output = _run_hook(main)
    assert LOUD_BLOCK_MARKER in output, output


def test_loud_silent_when_no_auto_target(tmp_path: Path) -> None:
    """Without auto_target.json, the probe block is skipped entirely."""
    main = _make_main_repo(tmp_path, with_env_url=False)
    (main / "engine" / "session" / "auto_target.json").unlink()
    output = _run_hook(main)
    assert LOUD_BLOCK_MARKER not in output, output


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
