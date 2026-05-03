"""Tests for engine/tools/audit_side_discoveries.py.

Covers each public surface of audit_side_discoveries.py with at least
one test per function and one test per logical branch within each
function.

Test isolation strategy
-----------------------
- Filesystem isolation via pytest's tmp_path fixture. Integration tests
  build synthetic git repos in tmp_path with hand-crafted commits.
- Subprocess invocations are real (the script shells out to git) but
  scoped to the tmp_path repo via the ``--repo-root`` flag.

Non-responsibilities
--------------------
- Does not test argparse beyond the documented flags.
- Does not test the script's behavior when git is unavailable on PATH.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_side_discoveries import (  # noqa: E402
    Disposition,
    Marker,
    find_eager_claim_sha,
    is_negated,
    load_dispositions,
    main,
    match_dispositions,
    scan_markers,
    session_range,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _scrub_git_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove GIT_* env vars from each test's process.

    Necessary so test subprocesses (and the script's own subprocess calls
    when exercised via main()) do not inherit GIT_DIR / GIT_WORK_TREE /
    GIT_INDEX_FILE from a parent invocation (e.g., when pytest runs inside
    a pre-commit hook), which would point git operations at the parent
    repo instead of the per-test tmp_path repo.
    """
    for key in list(os.environ.keys()):
        if key.startswith("GIT_"):
            monkeypatch.delenv(key, raising=False)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command in the given repo and return the result."""
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _init_repo(tmp_path: Path) -> Path:
    """Initialize an empty git repo with author/email configured."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "commit", "--allow-empty", "-q", "-m", "initial")
    return repo


def _commit(repo: Path, subject: str, body: str = "") -> str:
    """Create an empty commit with the given message; return its SHA."""
    message = subject if not body else f"{subject}\n\n{body}"
    _git(repo, "commit", "--allow-empty", "-q", "-m", message)
    out = _git(repo, "rev-parse", "HEAD")
    return out.stdout.strip()


def _write_current_json(
    path: Path, dispositions: list[dict[str, Any]] | None = None
) -> None:
    payload: dict[str, Any] = {"id": "S-9999", "status": "in_progress"}
    if dispositions is not None:
        payload["side_discoveries"] = dispositions
    path.write_text(json.dumps(payload))


# ---------------------------------------------------------------------------
# Unit tests — scan_markers
# ---------------------------------------------------------------------------


def test_scan_markers_basic_hit() -> None:
    commits = [("abc1234567", "fix: something. TODO: next step.")]
    markers = scan_markers(commits)
    assert len(markers) == 1
    assert markers[0].commit == "abc1234"
    assert markers[0].marker == "todo"


def test_scan_markers_case_insensitive() -> None:
    commits = [("abcdef1234", "lowercase todo and uppercase TODO present.")]
    markers = scan_markers(commits)
    assert {m.marker for m in markers} == {"todo"}
    assert len(markers) == 2


def test_scan_markers_negation_filter() -> None:
    """Markers preceded by no/not are skipped."""
    commits = [
        (
            "neg1234567",
            "no follow-up needed; not deferred; nothing pending here.",
        )
    ]
    markers = scan_markers(commits)
    assert markers == []


def test_scan_markers_distinct_phrases_in_one_commit() -> None:
    commits = [("multi12345", "TODO: thing. Also deferred until later. FIXME bar.")]
    markers = scan_markers(commits)
    assert {m.marker for m in markers} == {"todo", "deferred", "fixme"}


def test_scan_markers_hyphenated_vs_spaced_follow_up() -> None:
    """``follow-up`` and ``follow up`` yield distinct marker keys."""
    commits = [("hyphen1234", "follow-up here. follow up there.")]
    markers = scan_markers(commits)
    keys = {m.marker for m in markers}
    assert keys == {"follow-up", "follow up"}


def test_scan_markers_context_strips_newlines() -> None:
    commits = [("ctxabc1234", "first line\nTODO across line\nthird line")]
    markers = scan_markers(commits)
    assert len(markers) == 1
    assert "\n" not in markers[0].context


# ---------------------------------------------------------------------------
# Unit tests — is_negated
# ---------------------------------------------------------------------------


def test_is_negated_true_for_no_prefix() -> None:
    text = "no follow-up needed"
    pos = text.index("follow-up")
    assert is_negated(text, pos) is True


def test_is_negated_false_for_unrelated_word() -> None:
    text = "snore follow-up"
    pos = text.index("follow-up")
    assert is_negated(text, pos) is False


# ---------------------------------------------------------------------------
# Unit tests — match_dispositions
# ---------------------------------------------------------------------------


def test_match_dispositions_pairs_by_sha_prefix_and_marker() -> None:
    markers = [Marker(commit="abc1234", marker="todo", context="...")]
    dispositions = [
        Disposition(
            commit="abc1234",
            marker="todo",
            disposition_type="addressed_inline",
            disposition_ref="def5678",
            reasoning="",
        )
    ]
    assert match_dispositions(markers, dispositions) == []


def test_match_dispositions_returns_undispositioned_only() -> None:
    markers = [
        Marker(commit="aaa1234", marker="todo", context="x"),
        Marker(commit="bbb5678", marker="deferred", context="y"),
    ]
    dispositions = [
        Disposition(
            commit="aaa1234",
            marker="todo",
            disposition_type="acceptable_no_action",
            disposition_ref="",
            reasoning="false positive",
        )
    ]
    undisp = match_dispositions(markers, dispositions)
    assert [m.marker for m in undisp] == ["deferred"]


def test_match_dispositions_extra_dispositions_ignored() -> None:
    """Dispositions for nonexistent markers do not error."""
    markers: list[Marker] = []
    dispositions = [
        Disposition(
            commit="ccc9999",
            marker="todo",
            disposition_type="addressed_inline",
            disposition_ref="",
            reasoning="",
        )
    ]
    assert match_dispositions(markers, dispositions) == []


# ---------------------------------------------------------------------------
# Unit tests — load_dispositions
# ---------------------------------------------------------------------------


def test_load_dispositions_missing_file_returns_empty(tmp_path: Path) -> None:
    assert load_dispositions(tmp_path / "no.json") == []


def test_load_dispositions_no_field_returns_empty(tmp_path: Path) -> None:
    p = tmp_path / "current.json"
    p.write_text(json.dumps({"id": "S-9999"}))
    assert load_dispositions(p) == []


def test_load_dispositions_normalizes_marker_text(tmp_path: Path) -> None:
    p = tmp_path / "current.json"
    _write_current_json(
        p,
        [
            {
                "commit": "ABCDEF1XX",
                "marker": "  Follow-Up  ",
                "disposition_type": "addressed_inline",
                "disposition_ref": "fixsha1",
            }
        ],
    )
    [d] = load_dispositions(p)
    assert d.commit == "abcdef1"
    assert d.marker == "follow-up"


def test_load_dispositions_rejects_non_list_field(tmp_path: Path) -> None:
    p = tmp_path / "current.json"
    p.write_text(json.dumps({"side_discoveries": {"not": "a list"}}))
    with pytest.raises(ValueError, match="must be a list"):
        load_dispositions(p)


# ---------------------------------------------------------------------------
# Integration tests — end-to-end via main()
# ---------------------------------------------------------------------------


def test_main_no_markers_exits_zero(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit(repo, "chore(session): eager-claim S-0099 — test")
    _commit(repo, "feat: add a thing", body="No interesting markers in this body.")
    current = tmp_path / "current.json"
    _write_current_json(current, [])
    rc = main(
        [
            "--repo-root",
            str(repo),
            "--dispositions",
            str(current),
        ]
    )
    assert rc == 0


def test_main_undispositioned_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo(tmp_path)
    _commit(repo, "chore(session): eager-claim S-0099 — test")
    _commit(repo, "feat: thing", body="TODO: revisit this later.")
    current = tmp_path / "current.json"
    _write_current_json(current, [])
    rc = main(
        [
            "--repo-root",
            str(repo),
            "--dispositions",
            str(current),
        ]
    )
    assert rc == 2
    err = capsys.readouterr().err
    assert "undispositioned" in err
    assert "todo" in err


def test_main_all_dispositioned_exits_zero(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit(repo, "chore(session): eager-claim S-0099 — test")
    target_sha = _commit(repo, "feat: thing", body="TODO: revisit this later.")
    current = tmp_path / "current.json"
    _write_current_json(
        current,
        [
            {
                "commit": target_sha[:7],
                "marker": "todo",
                "disposition_type": "addressed_inline",
                "disposition_ref": target_sha[:7],
                "reasoning": "",
            }
        ],
    )
    rc = main(
        [
            "--repo-root",
            str(repo),
            "--dispositions",
            str(current),
        ]
    )
    assert rc == 0


def test_main_list_flag_dry_runs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo(tmp_path)
    _commit(repo, "chore(session): eager-claim S-0099 — test")
    _commit(repo, "feat: thing", body="TODO: revisit this later.")
    current = tmp_path / "current.json"
    _write_current_json(current, [])
    rc = main(
        [
            "--repo-root",
            str(repo),
            "--dispositions",
            str(current),
            "--list",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "todo" in out


def test_main_range_override(tmp_path: Path) -> None:
    """``--range`` skips the eager-claim auto-detection."""
    repo = _init_repo(tmp_path)
    _commit(repo, "feat: pre-claim work that should be excluded")
    base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _commit(repo, "feat: thing", body="TODO: revisit later.")
    current = tmp_path / "current.json"
    _write_current_json(current, [])
    rc = main(
        [
            "--repo-root",
            str(repo),
            "--range",
            f"{base}..HEAD",
            "--dispositions",
            str(current),
        ]
    )
    assert rc == 2  # the TODO is undispositioned


# ---------------------------------------------------------------------------
# Unit tests — find_eager_claim_sha / session_range
# ---------------------------------------------------------------------------


def test_find_eager_claim_sha_returns_match(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    claim_sha = _commit(repo, "chore(session): eager-claim S-0099 — test")
    _commit(repo, "feat: subsequent work")
    found = find_eager_claim_sha(repo)
    assert found == claim_sha


def test_session_range_raises_when_no_claim(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit(repo, "feat: ordinary work")
    with pytest.raises(RuntimeError, match="No eager-claim commit found"):
        session_range(repo)
