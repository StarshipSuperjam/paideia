"""Probe the git repo for shared-state sanity.

Exit codes
----------
0
    Healthy. ``core.bare`` is false (worktree functions normally),
    HEAD resolves, no surprising parent-clone misconfig.
1
    Suspect. Cosmetic anomalies — dirty working tree, detached HEAD.
    (Currently no level-1 conditions; reserved for future calibration.)
2
    Hard-broken. ``core.bare=true`` on the worktree's effective config
    or the parent clone's config; HEAD does not resolve; basic
    ``git rev-parse`` queries fail.

Per ADR 0045 (engine). Run from the SessionStart hook (boot probe).
Sub-second on any clone size.

Motivating failure: S-0033 wrote ``core.bare=true`` to the parent
``.git/config`` from inside a pytest subprocess. The probe checks both
the worktree's effective ``core.bare`` (catches the bleed-through case)
and the parent's standalone config (catches the case where a worktree
override masks a still-broken parent — the boot procedure's parent-side
``git -C <parent> merge --ff-only`` and ``git -C <parent> push`` would
fail in that masked case even though the worktree itself works).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Local import — scrub_env lives next to this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrub_env import scrubbed_env  # noqa: E402


def _git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _emit(stream: str, line: str) -> None:
    target = sys.stderr if stream == "err" else sys.stdout
    print(line, file=target, flush=True)


def main() -> int:
    cwd = Path.cwd()

    # Resolve worktree top.
    rc, top, err = _git(["rev-parse", "--show-toplevel"], cwd)
    if rc != 0:
        _emit(
            "err",
            f"[probe-repo] hard-broken: rev-parse --show-toplevel failed: {err}",
        )
        return 2
    repo = Path(top)

    # Effective core.bare check. `git config --get` exits 1 when key
    # absent (defaults to false) — that's healthy. Exit 0 with value
    # 'true' is the bad case.
    rc, bare_val, _ = _git(["config", "--get", "core.bare"], repo)
    if rc == 0 and bare_val.strip().lower() == "true":
        _emit(
            "err",
            f"[probe-repo] hard-broken: core.bare=true on {repo}. "
            f"This blocks worktree git operations. "
            f"Run `git -C {repo} config --unset core.bare`.",
        )
        return 2

    # Parent clone direct check. For a worktree, the parent's config
    # may be misset even if the worktree's effective config is OK
    # (because a config.worktree override masks it). The boot
    # procedure's parent-side `merge --ff-only` and `push origin main`
    # would still fail.
    rc, common_dir_str, err = _git(["rev-parse", "--git-common-dir"], cwd)
    if rc == 0 and common_dir_str:
        # `git rev-parse --git-common-dir` may return either an absolute
        # path or a path relative to cwd. Resolve to absolute.
        common_dir = Path(common_dir_str)
        if not common_dir.is_absolute():
            common_dir = (cwd / common_dir).resolve()
        parent_config = common_dir / "config"
        if parent_config.is_file():
            rc2, parent_bare, _ = _git(
                ["config", "--file", str(parent_config), "--get", "core.bare"],
                cwd,
            )
            if rc2 == 0 and parent_bare.strip().lower() == "true":
                # Locate the parent repo for the user-facing recovery
                # command. common_dir is typically <parent>/.git, so the
                # parent repo dir is its parent.
                parent_repo = (
                    common_dir.parent if common_dir.name == ".git" else common_dir
                )
                _emit(
                    "err",
                    f"[probe-repo] hard-broken: core.bare=true on parent "
                    f"clone {parent_repo}. The worktree may function via a "
                    f"config.worktree override, but parent-side boot operations "
                    f"(merge --ff-only, push origin main) will fail. "
                    f"Run `git -C {parent_repo} config --unset core.bare`.",
                )
                return 2

    # HEAD resolution — basic sanity that we can reference HEAD.
    rc, head_sha, err = _git(["rev-parse", "HEAD"], cwd)
    if rc != 0:
        _emit("err", f"[probe-repo] hard-broken: HEAD does not resolve: {err}")
        return 2

    _emit("out", f"[probe-repo] healthy: {repo} HEAD={head_sha[:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
