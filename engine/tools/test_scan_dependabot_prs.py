"""Tests for engine/tools/scan_dependabot_prs.py.

Tests are pure-function — gh subprocess is monkey-patched so the suite
runs without network or auth state.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_dependabot_prs import (  # noqa: E402
    LOUD_COUNT_THRESHOLD,
    STALE_AGE_DAYS,
    age_days,
    classify,
    fetch_open_prs,
    format_fyi,
    format_loud,
    main,
    next_action_hint,
)


def _now() -> datetime:
    """Pinned 'now' for deterministic age tests."""
    return datetime(2026, 5, 20, 0, 0, 0, tzinfo=timezone.utc)


def _pr(
    num: int,
    days_old: int,
    title: str = "chore(deps): bump foo from 1 to 2",
    head_ref: str = "dependabot/pip/foo",
    mergeable: str = "MERGEABLE",
) -> dict[str, Any]:
    """Build a fake PR dict with an age relative to _now()."""
    created = _now() - timedelta(days=days_old)
    return {
        "number": num,
        "title": title,
        "createdAt": created.isoformat().replace("+00:00", "Z"),
        "mergeable": mergeable,
        "headRefName": head_ref,
    }


# ---------------------------------------------------------------------------
# age_days
# ---------------------------------------------------------------------------


def test_age_days_zero_for_today() -> None:
    created = _now().isoformat().replace("+00:00", "Z")
    assert age_days(created, now=_now()) == 0


def test_age_days_seven_for_one_week_old() -> None:
    created = (_now() - timedelta(days=7)).isoformat().replace("+00:00", "Z")
    assert age_days(created, now=_now()) == 7


def test_age_days_handles_z_suffix() -> None:
    # Real gh output uses Z suffix; check the replace logic works.
    created = "2026-05-13T00:00:00Z"
    days = age_days(created, now=_now())
    assert days == 7


# ---------------------------------------------------------------------------
# next_action_hint
# ---------------------------------------------------------------------------


def test_next_action_hint_for_github_actions_pr() -> None:
    pr = _pr(1, 0, head_ref="dependabot/github_actions/actions/checkout-6")
    assert next_action_hint(pr) == "verify action release notes; merge"


def test_next_action_hint_for_pip_minor_patch() -> None:
    pr = _pr(1, 0, title="chore(deps): Update foo requirement (minor)")
    assert next_action_hint(pr) == "regenerate uv.lock and merge"


def test_next_action_hint_for_pip_major_default() -> None:
    pr = _pr(
        1, 0, title="chore(deps): Update chromadb requirement from >=0.5.0 to >=1.5.9"
    )
    assert (
        next_action_hint(pr)
        == "major bump — verify ADR 0069 contract; regenerate uv.lock"
    )


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------


def test_classify_empty_returns_quiet() -> None:
    result = classify([], now=_now())
    assert result["mode"] == "quiet"
    assert result["count"] == 0
    assert result["oldest_age"] == -1
    assert result["stale_prs"] == []


def test_classify_few_fresh_returns_fyi() -> None:
    prs = [_pr(1, 1), _pr(2, 3), _pr(3, 5)]
    result = classify(prs, now=_now())
    assert result["mode"] == "fyi"
    assert result["count"] == 3
    assert result["oldest_age"] == 5
    assert result["stale_prs"] == []


def test_classify_many_returns_loud_even_when_fresh() -> None:
    prs = [_pr(i, 1) for i in range(LOUD_COUNT_THRESHOLD)]
    result = classify(prs, now=_now())
    assert result["mode"] == "loud"
    assert result["count"] == LOUD_COUNT_THRESHOLD
    assert result["stale_prs"] == []


def test_classify_any_stale_returns_loud() -> None:
    prs = [_pr(1, 1), _pr(2, STALE_AGE_DAYS)]
    result = classify(prs, now=_now())
    assert result["mode"] == "loud"
    assert len(result["stale_prs"]) == 1
    assert result["stale_prs"][0]["number"] == 2


def test_classify_stale_threshold_boundary() -> None:
    """Exactly STALE_AGE_DAYS old IS stale (>= comparison)."""
    prs = [_pr(1, STALE_AGE_DAYS), _pr(2, STALE_AGE_DAYS - 1)]
    result = classify(prs, now=_now())
    assert len(result["stale_prs"]) == 1
    assert result["stale_prs"][0]["number"] == 1


def test_classify_sorts_oldest_first() -> None:
    prs = [_pr(1, 2), _pr(2, 10), _pr(3, 5)]
    result = classify(prs, now=_now())
    assert result["oldest_age"] == 10


# ---------------------------------------------------------------------------
# format_fyi / format_loud
# ---------------------------------------------------------------------------


def test_format_fyi_includes_count_and_age() -> None:
    scan = {"count": 3, "oldest_age": 4, "stale_prs": [], "mode": "fyi"}
    line = format_fyi(scan)
    assert "3 open" in line
    assert "4 day(s)" in line


def test_format_loud_lists_each_pr() -> None:
    prs = [_pr(1, 2), _pr(2, 8)]
    scan = classify(prs, now=_now())
    lines = format_loud(prs, scan, now=_now())
    blob = "\n".join(lines)
    assert "#1" in blob
    assert "#2" in blob
    assert "STALE" in blob  # PR #2 is 8 days old


def test_format_loud_orders_oldest_first() -> None:
    prs = [_pr(1, 2), _pr(2, 10), _pr(3, 5)]
    scan = classify(prs, now=_now())
    lines = format_loud(prs, scan, now=_now())
    blob = "\n".join(lines)
    idx1 = blob.find("#1")
    idx2 = blob.find("#2")
    idx3 = blob.find("#3")
    assert idx2 < idx3 < idx1  # 10d → 5d → 2d order


# ---------------------------------------------------------------------------
# fetch_open_prs — graceful gh failure
# ---------------------------------------------------------------------------


def test_fetch_open_prs_returns_none_on_gh_nonzero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When gh returns non-zero, fetch_open_prs returns None (caller surfaces stderr)."""
    import subprocess as _sp

    class FakeProc:
        returncode = 1
        stdout = ""

    monkeypatch.setattr(_sp, "run", lambda *a, **k: FakeProc())
    assert fetch_open_prs() is None


def test_fetch_open_prs_returns_none_on_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import subprocess as _sp

    class FakeProc:
        returncode = 0
        stdout = "not json"

    monkeypatch.setattr(_sp, "run", lambda *a, **k: FakeProc())
    assert fetch_open_prs() is None


# ---------------------------------------------------------------------------
# main CLI
# ---------------------------------------------------------------------------


def test_main_emits_nothing_on_zero_prs(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import scan_dependabot_prs

    monkeypatch.setattr(scan_dependabot_prs, "fetch_open_prs", lambda repo=None: [])
    rc = main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert out == ""


def test_main_emits_fyi_line_for_few_fresh(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import scan_dependabot_prs

    monkeypatch.setattr(
        scan_dependabot_prs,
        "fetch_open_prs",
        lambda repo=None: [_pr(1, 0), _pr(2, 1)],
    )
    rc = main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "[session-start] Dependabot PRs:" in out
    assert "2 open" in out


def test_main_emits_loud_block_at_threshold(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import scan_dependabot_prs

    prs = [_pr(i, 1) for i in range(LOUD_COUNT_THRESHOLD)]
    monkeypatch.setattr(scan_dependabot_prs, "fetch_open_prs", lambda repo=None: prs)
    rc = main([])
    assert rc == 0
    out = capsys.readouterr().out
    assert "=" * 72 in out
    assert f"{LOUD_COUNT_THRESHOLD} open" in out


def test_main_json_mode_emits_structured_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Use real-time ages: createdAt 8 days before real datetime.now() so
    main()'s default `now` (real now) sees it as stale."""
    import scan_dependabot_prs

    real_now = datetime.now(timezone.utc)
    fresh = (real_now - timedelta(days=3)).isoformat().replace("+00:00", "Z")
    stale = (real_now - timedelta(days=8)).isoformat().replace("+00:00", "Z")
    prs = [
        {
            "number": 1,
            "title": "t1",
            "createdAt": fresh,
            "mergeable": "M",
            "headRefName": "dependabot/pip/foo",
        },
        {
            "number": 2,
            "title": "t2",
            "createdAt": stale,
            "mergeable": "M",
            "headRefName": "dependabot/pip/bar",
        },
    ]
    monkeypatch.setattr(scan_dependabot_prs, "fetch_open_prs", lambda repo=None: prs)
    rc = main(["--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["count"] == 2
    assert data["mode"] == "loud"  # one is ≥7d
    assert data["stale_prs_count"] == 1
    assert len(data["prs"]) == 2


def test_main_simulate_age_overrides_for_loud(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """--simulate-age 10 ages 1-PR backlog past STALE_AGE_DAYS so LOUD fires."""
    import scan_dependabot_prs

    monkeypatch.setattr(
        scan_dependabot_prs, "fetch_open_prs", lambda repo=None: [_pr(1, 0)]
    )
    rc = main(["--simulate-age", "10"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "STALE" in out


def test_main_gh_failure_returns_zero_with_stderr_note(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """When gh fails entirely, the scanner is non-blocking."""
    import scan_dependabot_prs

    monkeypatch.setattr(scan_dependabot_prs, "fetch_open_prs", lambda repo=None: None)
    rc = main([])
    assert rc == 0
    err = capsys.readouterr().err
    assert "gh pr list failed" in err
