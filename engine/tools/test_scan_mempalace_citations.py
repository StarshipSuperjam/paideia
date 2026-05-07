"""Tests for engine/tools/scan_mempalace_citations.py — Issue #39 / ADR 0056 (S-0093)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import scan_mempalace_citations as scanner  # noqa: E402


def test_drawer_id_pattern_matches_canonical_forms() -> None:
    text = (
        "Saw drawer_paideia_a3d64680e953450f011e582f and "
        "drawer_wing_paideia_b7f3c2d1e4a5b6c789d012ef3 in the trace; "
        "also drawer_wing_claude_1a2b3c4d5e6f7890abcdef12 stood out."
    )
    counts = scanner.scan_text(text)
    assert counts["drawer_id_refs"] == 3


def test_drawer_id_pattern_ignores_short_hashes_and_non_drawer_prefixes() -> None:
    text = "drawer_short_abc and not_a_drawer_paideia_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    counts = scanner.scan_text(text)
    assert counts["drawer_id_refs"] == 0


def test_session_archive_pattern_matches_per_from_at() -> None:
    text = (
        "Per S-0091 the contract held; from S-0086 we learned scale-back. "
        "At S-0078 the mechanism landed."
    )
    counts = scanner.scan_text(text)
    assert counts["session_archive_refs"] == 3


def test_session_archive_pattern_matches_possessive_form() -> None:
    text = "S-0091's amendment dropped the differentiation."
    counts = scanner.scan_text(text)
    assert counts["session_archive_refs"] == 1


def test_session_archive_pattern_dedupes_within_source() -> None:
    text = "per S-0091 and again per S-0091 and S-0091's amendment"
    counts = scanner.scan_text(text)
    assert counts["session_archive_refs"] == 1


def test_tag_named_pattern_matches_three_kinds() -> None:
    text = (
        "Per pushback drawer the user ruled X out; "
        "per lesson drawer we know Y; "
        "per decision drawer the contract is Z."
    )
    counts = scanner.scan_text(text)
    assert counts["tag_named_refs"] == 3


def test_tag_named_pattern_case_insensitive() -> None:
    text = "Per Pushback Drawer captured at S-0061"
    counts = scanner.scan_text(text)
    assert counts["tag_named_refs"] == 1


def test_scan_empty_text_returns_zero_counts() -> None:
    counts = scanner.scan_text("")
    assert counts == {
        "drawer_id_refs": 0,
        "session_archive_refs": 0,
        "tag_named_refs": 0,
    }


def test_scan_unrelated_text_returns_zero_counts() -> None:
    text = "Just some prose with no drawer references whatsoever."
    counts = scanner.scan_text(text)
    assert counts == {
        "drawer_id_refs": 0,
        "session_archive_refs": 0,
        "tag_named_refs": 0,
    }


def test_session_archive_pattern_does_not_match_url_path_segment() -> None:
    text = "https://github.com/x/y/issues/S-0042/comments"
    counts = scanner.scan_text(text)
    assert counts["session_archive_refs"] == 0


def test_sum_counts_combines_sources_and_computes_total() -> None:
    sources = [
        {"drawer_id_refs": 2, "session_archive_refs": 1, "tag_named_refs": 0},
        {"drawer_id_refs": 0, "session_archive_refs": 4, "tag_named_refs": 1},
        {"drawer_id_refs": 1, "session_archive_refs": 0, "tag_named_refs": 0},
    ]
    summed = scanner._sum_counts(sources)
    assert summed == {
        "drawer_id_refs": 3,
        "session_archive_refs": 5,
        "tag_named_refs": 1,
        "total": 9,
    }


def test_fetch_today_diary_returns_empty_when_import_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Simulate ImportError by removing mempalace from sys.modules + import-block."""
    monkeypatch.delitem(sys.modules, "mempalace.mcp_server", raising=False)

    class _Blocker:
        def find_spec(
            self, fullname: str, path: object = None, target: object = None
        ) -> None:
            if fullname == "mempalace.mcp_server" or fullname.startswith(
                "mempalace.mcp_server."
            ):
                raise ImportError("simulated absent")
            return None

    blocker = _Blocker()
    monkeypatch.setattr(sys, "meta_path", [blocker, *sys.meta_path])
    assert scanner.fetch_today_diary() == ""


def test_fetch_today_diary_returns_today_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub mempalace.mcp_server.tool_diary_read with a today entry."""
    import datetime as dt
    import types

    today = dt.date.today().isoformat()

    def fake_tool_diary_read(
        agent_name: str, last_n: int = 10, wing: str = ""
    ) -> dict[str, object]:
        return {
            "agent": agent_name,
            "entries": [
                {"date": "2020-01-01", "content": "ancient", "topic": "old"},
                {
                    "date": today,
                    "content": "today's reflection content",
                    "topic": "S-0093",
                },
            ],
        }

    fake_module = types.SimpleNamespace(tool_diary_read=fake_tool_diary_read)
    monkeypatch.setitem(sys.modules, "mempalace.mcp_server", fake_module)
    assert scanner.fetch_today_diary() == "today's reflection content"


def test_fetch_today_diary_returns_empty_when_no_today_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types

    def fake_tool_diary_read(
        agent_name: str, last_n: int = 10, wing: str = ""
    ) -> dict[str, object]:
        return {"entries": [{"date": "2020-01-01", "content": "old", "topic": "x"}]}

    fake_module = types.SimpleNamespace(tool_diary_read=fake_tool_diary_read)
    monkeypatch.setitem(sys.modules, "mempalace.mcp_server", fake_module)
    assert scanner.fetch_today_diary() == ""


def test_fetch_session_commit_messages_returns_empty_when_no_eager_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_log = "abc123\nfeat: x\n\nbody1\n--END--\ndef456\nfix: y\n\nbody2\n--END--\n"

    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout=fake_log, stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert scanner.fetch_session_commit_messages(tmp_path) == ""


def test_fetch_session_commit_messages_collects_pre_eager_claim_commits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_log = (
        "ccc\nfeat(x): bar\n\nthird body\n--END--\n"
        "bbb\nfeat(y): foo\n\nsecond body per S-0091\n--END--\n"
        "aaa\nchore(session): eager-claim S-0093 — campaign C4\n\neager body\n--END--\n"
        "old\nfeat(z): older\n\nolder body\n--END--\n"
    )

    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout=fake_log, stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    text = scanner.fetch_session_commit_messages(tmp_path)
    assert "third body" in text
    assert "second body per S-0091" in text
    assert "eager body" not in text
    assert "older body" not in text


def test_fetch_session_commit_messages_handles_git_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(returncode=128, cmd=["git"])

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert scanner.fetch_session_commit_messages(tmp_path) == ""


def test_write_citations_to_current_creates_nested_block(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0093",
                "mempalace_activity": {
                    "search_calls": 3,
                    "diary_read_calls": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    citations = {
        "drawer_id_refs": 1,
        "session_archive_refs": 4,
        "tag_named_refs": 0,
        "total": 5,
    }
    scanner.write_citations_to_current(current, citations)
    data = json.loads(current.read_text(encoding="utf-8"))
    assert data["mempalace_activity"]["mempalace_citations"] == citations
    assert data["mempalace_activity"]["search_calls"] == 3
    assert data["mempalace_activity"]["diary_read_calls"] == 1


def test_write_citations_to_current_creates_activity_when_absent(
    tmp_path: Path,
) -> None:
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"id": "S-0093"}), encoding="utf-8")
    citations = {
        "drawer_id_refs": 0,
        "session_archive_refs": 1,
        "tag_named_refs": 0,
        "total": 1,
    }
    scanner.write_citations_to_current(current, citations)
    data = json.loads(current.read_text(encoding="utf-8"))
    assert data["mempalace_activity"]["mempalace_citations"] == citations


def test_write_citations_to_current_idempotent_overwrites(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    current.write_text(json.dumps({"id": "S-0093"}), encoding="utf-8")
    scanner.write_citations_to_current(
        current,
        {
            "drawer_id_refs": 5,
            "session_archive_refs": 0,
            "tag_named_refs": 0,
            "total": 5,
        },
    )
    scanner.write_citations_to_current(
        current,
        {
            "drawer_id_refs": 0,
            "session_archive_refs": 0,
            "tag_named_refs": 0,
            "total": 0,
        },
    )
    data = json.loads(current.read_text(encoding="utf-8"))
    assert data["mempalace_activity"]["mempalace_citations"]["total"] == 0


def test_write_citations_to_current_raises_when_current_absent(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    with pytest.raises(FileNotFoundError):
        scanner.write_citations_to_current(
            current,
            {
                "drawer_id_refs": 0,
                "session_archive_refs": 0,
                "tag_named_refs": 0,
                "total": 0,
            },
        )


def test_main_no_current_returns_0(tmp_path: Path) -> None:
    rc = scanner.main(
        [
            "--current-path",
            str(tmp_path / "current.json"),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0


def test_main_dry_run_does_not_modify_current(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0093",
                "outcome_summary": "Fixed via S-0091's amendment per pushback drawer.",
                "mempalace_activity": {"search_calls": 1},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(scanner, "fetch_today_diary", lambda agent_name="claude": "")
    monkeypatch.setattr(scanner, "fetch_session_commit_messages", lambda repo_root: "")

    rc = scanner.main(
        [
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),
            "--dry-run",
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text(encoding="utf-8"))
    assert "mempalace_citations" not in data["mempalace_activity"]


def test_main_writes_citations_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0093",
                "outcome_summary": "Per S-0091 the body is uniform; see S-0086 for context.",
                "mempalace_activity": {"search_calls": 2},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        scanner,
        "fetch_today_diary",
        lambda agent_name="claude": "Per pushback drawer this was anticipated.",
    )
    monkeypatch.setattr(
        scanner,
        "fetch_session_commit_messages",
        lambda repo_root: "feat: extend per S-0078 contract",
    )

    rc = scanner.main(
        [
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text(encoding="utf-8"))
    citations = data["mempalace_activity"]["mempalace_citations"]
    assert citations["session_archive_refs"] >= 2
    assert citations["tag_named_refs"] == 1
    assert citations["total"] == (
        citations["drawer_id_refs"]
        + citations["session_archive_refs"]
        + citations["tag_named_refs"]
    )


def test_main_handles_non_string_outcome_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0093",
                "outcome_summary": None,
                "mempalace_activity": {"search_calls": 1},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(scanner, "fetch_today_diary", lambda agent_name="claude": "")
    monkeypatch.setattr(scanner, "fetch_session_commit_messages", lambda repo_root: "")

    rc = scanner.main(
        [
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text(encoding="utf-8"))
    assert data["mempalace_activity"]["mempalace_citations"]["total"] == 0


def test_main_multi_source_aggregation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """outcome + diary + git all contribute; per-source dedup but cross-source sums."""
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps(
            {
                "id": "S-0093",
                "outcome_summary": "per S-0091 (1).",
                "mempalace_activity": {"search_calls": 1},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        scanner,
        "fetch_today_diary",
        lambda agent_name="claude": "from S-0086 (2).",
    )
    monkeypatch.setattr(
        scanner,
        "fetch_session_commit_messages",
        lambda repo_root: "per S-0078 (3) and per S-0078 (4 dup).",
    )

    rc = scanner.main(
        [
            "--current-path",
            str(current),
            "--repo-root",
            str(tmp_path),
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text(encoding="utf-8"))
    citations = data["mempalace_activity"]["mempalace_citations"]
    assert citations["session_archive_refs"] == 3


def test_eager_claim_pattern_matches_canonical_subject() -> None:
    assert scanner.EAGER_CLAIM_PATTERN.search(
        "chore(session): eager-claim S-0093 — campaign C4"
    )
    assert not scanner.EAGER_CLAIM_PATTERN.search("feat: not an eager claim")
