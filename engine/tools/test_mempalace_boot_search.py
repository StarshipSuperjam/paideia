"""Tests for engine/tools/mempalace_boot_search.py — Issue #38 / ADR 0056 (S-0093)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mempalace_boot_search as orchestrator  # noqa: E402


def _stub_drawers(
    monkeypatch: pytest.MonkeyPatch,
    drawers_by_query: dict[str, list[dict[str, Any]] | None] | None = None,
) -> list[tuple[str, float, int]]:
    """Replace fetch_drawers with a stub. Returns a call-log list."""
    calls: list[tuple[str, float, int]] = []

    def fake_fetch(
        query: str, min_similarity: float, limit: int
    ) -> list[dict[str, Any]] | None:
        calls.append((query, min_similarity, limit))
        if drawers_by_query is None:
            return []
        for substring, value in drawers_by_query.items():
            if substring in query:
                return value
        return []

    monkeypatch.setattr(orchestrator, "fetch_drawers", fake_fetch)
    return calls


def test_normalize_query_lowercases_strips_punctuation() -> None:
    assert (
        orchestrator._normalize_query("Hello, World! Foo-Bar.") == "hello world foo-bar"
    )


def test_normalize_query_truncates_to_max_chars() -> None:
    long = "x" * 400
    assert len(orchestrator._normalize_query(long)) == orchestrator.MAX_QUERY_CHARS


def test_extract_keywords_drops_stopwords_and_short_tokens() -> None:
    text = "The quick brown fox jumps over the lazy dog into a hole"
    keywords = orchestrator._extract_keywords(text, max_n=10)
    assert "the" not in keywords
    assert "into" not in keywords
    assert "a" not in keywords
    assert "quick" in keywords
    assert "brown" in keywords


def test_extract_keywords_dedupes_preserving_order() -> None:
    text = "search search retrieval search drawer drawer"
    keywords = orchestrator._extract_keywords(text)
    assert keywords == ["search", "retrieval", "drawer"]


def test_extract_keywords_caps_at_max_n() -> None:
    text = " ".join(f"keyword{i}" for i in range(20))
    assert len(orchestrator._extract_keywords(text, max_n=4)) == 4


def test_generate_formulations_returns_three_labeled_queries() -> None:
    work_item = "Mechanize MemPalace boot search with three formulations"
    formulations = orchestrator.generate_formulations(work_item)
    labels = [label for label, _ in formulations]
    assert labels == ["literal", "conceptual", "adjacent"]
    for _, query in formulations:
        assert query
        assert len(query) <= orchestrator.MAX_QUERY_CHARS


def test_generate_formulations_deterministic() -> None:
    work_item = "Boot search drawer telemetry"
    a = orchestrator.generate_formulations(work_item)
    b = orchestrator.generate_formulations(work_item)
    assert a == b


def test_generate_formulations_adjacent_carries_lessons_pushback() -> None:
    formulations = orchestrator.generate_formulations("Test phrase")
    adjacent = dict(formulations)["adjacent"]
    assert "lessons" in adjacent
    assert "pushback" in adjacent


def test_generate_formulations_empty_keywords_falls_back_to_literal_for_conceptual() -> (
    None
):
    work_item = "the a an it of on in"
    formulations = orchestrator.generate_formulations(work_item)
    conceptual = dict(formulations)["conceptual"]
    assert conceptual == orchestrator._normalize_query(work_item)


def test_render_section_with_drawers() -> None:
    drawers = [
        {
            "wing": "paideia",
            "room": "decisions",
            "source_file": "x.txt",
            "similarity": 0.74,
            "text": "This is a sample drawer text",
        }
    ]
    body = orchestrator.render_section(
        [
            ("literal", "test", drawers),
            ("conceptual", "test other", []),
            ("adjacent", "test lessons pushback", drawers),
        ],
        ts="2026-05-07T22:00:00Z",
        threshold=0.6,
        substrate_unreachable=False,
    )
    assert "## Prior context (MemPalace boot search)" in body
    assert "Three formulations × similarity ≥0.60 = 2 drawers" in body
    assert "### Literal — `test`" in body
    assert "### Conceptual — `test other`" in body
    assert "### Adjacent — `test lessons pushback`" in body
    assert "_no drawers above threshold_" in body
    assert "paideia/decisions" in body
    assert "sim: 0.74" in body


def test_render_section_substrate_unreachable() -> None:
    body = orchestrator.render_section(
        [], ts="2026-05-07T22:00:00Z", threshold=0.6, substrate_unreachable=True
    )
    assert "MemPalace substrate unreachable at boot" in body
    assert "Three formulations" not in body


def test_write_section_creates_new_plan_file(tmp_path: Path) -> None:
    plan = tmp_path / "current_plan.md"
    body = "## Prior context (MemPalace boot search)\n\nbody contents"
    orchestrator.write_section(plan, body)
    content = plan.read_text(encoding="utf-8")
    assert content.startswith("## Prior context (MemPalace boot search)")
    assert "body contents" in content


def test_write_section_replaces_existing_section_idempotent(tmp_path: Path) -> None:
    plan = tmp_path / "current_plan.md"
    plan.write_text(
        "## Prior context (MemPalace boot search)\n\nold body\n\n"
        "## Other section\n\nother body\n",
        encoding="utf-8",
    )
    new_body = "## Prior context (MemPalace boot search)\n\nnew body"
    orchestrator.write_section(plan, new_body)
    content = plan.read_text(encoding="utf-8")
    assert "old body" not in content
    assert "new body" in content
    assert "## Other section" in content
    assert "other body" in content


def test_write_section_idempotent_re_run_replaces(tmp_path: Path) -> None:
    plan = tmp_path / "current_plan.md"
    body_v1 = "## Prior context (MemPalace boot search)\n\nv1 body"
    body_v2 = "## Prior context (MemPalace boot search)\n\nv2 body"
    orchestrator.write_section(plan, body_v1)
    orchestrator.write_section(plan, body_v2)
    content = plan.read_text(encoding="utf-8")
    assert "v1 body" not in content
    assert "v2 body" in content
    assert content.count("## Prior context (MemPalace boot search)") == 1


def test_write_section_appends_when_other_content_exists(tmp_path: Path) -> None:
    plan = tmp_path / "current_plan.md"
    plan.write_text("## Other\n\nfoo\n", encoding="utf-8")
    body = "## Prior context (MemPalace boot search)\n\nnew"
    orchestrator.write_section(plan, body)
    content = plan.read_text(encoding="utf-8")
    assert "## Other" in content
    assert "## Prior context (MemPalace boot search)" in content
    assert "new" in content


def test_append_telemetry_writes_three_lines(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_mempalace.jsonl"
    formulations = [("literal", "abc"), ("conceptual", "def"), ("adjacent", "ghi")]
    orchestrator.append_telemetry(jsonl, formulations, ts="2026-05-07T22:00:00Z")
    lines = jsonl.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 3
    for line, (label, query) in zip(lines, formulations):
        entry = json.loads(line)
        assert entry["tool"] == "mcp__mempalace__mempalace_search"
        assert entry["ts"] == "2026-05-07T22:00:00Z"
        assert entry["args_summary"] == f"boot-search:{label}:{query}"


def test_append_telemetry_appends_not_truncates(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_mempalace.jsonl"
    jsonl.write_text('{"existing": "line"}\n', encoding="utf-8")
    orchestrator.append_telemetry(jsonl, [("literal", "x")], ts="2026-05-07T22:00:00Z")
    lines = jsonl.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"existing": "line"}


def test_append_telemetry_truncates_long_query_summary(tmp_path: Path) -> None:
    jsonl = tmp_path / "current_mempalace.jsonl"
    long_query = "x" * 400
    orchestrator.append_telemetry(
        jsonl, [("literal", long_query)], ts="2026-05-07T22:00:00Z"
    )
    entry = json.loads(jsonl.read_text(encoding="utf-8").strip())
    assert len(entry["args_summary"]) <= len("boot-search:literal:") + 160


def test_resolve_work_item_prefers_current_json_working_on(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps({"id": "S-0093", "working_on": "from current.json"}),
        encoding="utf-8",
    )
    state = tmp_path / "STATE.md"
    state.write_text("## Next session work item\n\nfrom STATE.md\n", encoding="utf-8")
    auto_target = tmp_path / "auto_target.json"
    auto_target.write_text(
        json.dumps({"tasks": [{"status": "pending", "name": "from auto_target"}]}),
        encoding="utf-8",
    )
    assert (
        orchestrator.resolve_work_item(current, state, auto_target)
        == "from current.json"
    )


def test_resolve_work_item_falls_back_to_auto_target(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    state = tmp_path / "STATE.md"
    state.write_text("## Next session work item\n\nfrom STATE.md\n", encoding="utf-8")
    auto_target = tmp_path / "auto_target.json"
    auto_target.write_text(
        json.dumps(
            {
                "paused": False,
                "tasks": [
                    {"status": "complete", "name": "old task"},
                    {"status": "pending", "name": "from auto_target"},
                ],
            }
        ),
        encoding="utf-8",
    )
    assert (
        orchestrator.resolve_work_item(current, state, auto_target)
        == "from auto_target"
    )


def test_resolve_work_item_skips_paused_auto_target(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    state = tmp_path / "STATE.md"
    state.write_text(
        "## Next session work item\n\nfrom STATE.md prose\n", encoding="utf-8"
    )
    auto_target = tmp_path / "auto_target.json"
    auto_target.write_text(
        json.dumps(
            {
                "paused": True,
                "tasks": [{"status": "pending", "name": "from auto_target"}],
            }
        ),
        encoding="utf-8",
    )
    assert (
        orchestrator.resolve_work_item(current, state, auto_target)
        == "from STATE.md prose"
    )


def test_resolve_work_item_returns_none_when_all_sources_empty(tmp_path: Path) -> None:
    current = tmp_path / "current.json"
    state = tmp_path / "STATE.md"
    auto_target = tmp_path / "auto_target.json"
    assert orchestrator.resolve_work_item(current, state, auto_target) is None


def test_main_dry_run_no_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps({"id": "S-0093", "working_on": "test work item"}),
        encoding="utf-8",
    )
    plan = tmp_path / "current_plan.md"
    jsonl = tmp_path / "current_mempalace.jsonl"
    _stub_drawers(monkeypatch)

    rc = orchestrator.main(
        [
            "--current-path",
            str(current),
            "--state-path",
            str(tmp_path / "STATE.md"),
            "--auto-target-path",
            str(tmp_path / "auto_target.json"),
            "--plan-path",
            str(plan),
            "--jsonl-path",
            str(jsonl),
            "--dry-run",
        ]
    )
    assert rc == 0
    assert not plan.exists()
    assert not jsonl.exists()
    captured = capsys.readouterr()
    assert "## Prior context (MemPalace boot search)" in captured.out


def test_main_writes_plan_and_telemetry_on_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps({"id": "S-0093", "working_on": "boot search test"}),
        encoding="utf-8",
    )
    plan = tmp_path / "current_plan.md"
    jsonl = tmp_path / "current_mempalace.jsonl"
    _stub_drawers(
        monkeypatch,
        {
            "boot search test": [
                {
                    "wing": "paideia",
                    "room": "decisions",
                    "source_file": "x.txt",
                    "similarity": 0.7,
                    "text": "found drawer",
                }
            ]
        },
    )

    rc = orchestrator.main(
        [
            "--current-path",
            str(current),
            "--state-path",
            str(tmp_path / "STATE.md"),
            "--auto-target-path",
            str(tmp_path / "auto_target.json"),
            "--plan-path",
            str(plan),
            "--jsonl-path",
            str(jsonl),
        ]
    )
    assert rc == 0
    assert plan.exists()
    assert "found drawer" in plan.read_text(encoding="utf-8")
    assert jsonl.exists()
    lines = jsonl.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 3


def test_main_substrate_unreachable_writes_section_skips_telemetry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps({"id": "S-0093", "working_on": "any work"}), encoding="utf-8"
    )
    plan = tmp_path / "current_plan.md"
    jsonl = tmp_path / "current_mempalace.jsonl"
    monkeypatch.setattr(orchestrator, "fetch_drawers", lambda **kwargs: None)
    rc = orchestrator.main(
        [
            "--current-path",
            str(current),
            "--state-path",
            str(tmp_path / "STATE.md"),
            "--auto-target-path",
            str(tmp_path / "auto_target.json"),
            "--plan-path",
            str(plan),
            "--jsonl-path",
            str(jsonl),
        ]
    )
    assert rc == 2
    assert plan.exists()
    assert "MemPalace substrate unreachable" in plan.read_text(encoding="utf-8")
    assert not jsonl.exists()


def test_main_returns_1_when_work_item_unresolvable(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    current = tmp_path / "current.json"
    state = tmp_path / "STATE.md"
    auto_target = tmp_path / "auto_target.json"
    rc = orchestrator.main(
        [
            "--current-path",
            str(current),
            "--state-path",
            str(state),
            "--auto-target-path",
            str(auto_target),
            "--plan-path",
            str(tmp_path / "plan.md"),
            "--jsonl-path",
            str(tmp_path / "current_mempalace.jsonl"),
        ]
    )
    assert rc == 1
    captured = capsys.readouterr()
    assert "could not resolve work-item phrase" in captured.err


def test_main_explicit_work_item_overrides_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current = tmp_path / "current.json"
    current.write_text(
        json.dumps({"working_on": "from current.json"}), encoding="utf-8"
    )
    plan = tmp_path / "current_plan.md"
    jsonl = tmp_path / "current_mempalace.jsonl"
    calls = _stub_drawers(monkeypatch)
    rc = orchestrator.main(
        [
            "--current-path",
            str(current),
            "--state-path",
            str(tmp_path / "STATE.md"),
            "--auto-target-path",
            str(tmp_path / "auto_target.json"),
            "--plan-path",
            str(plan),
            "--jsonl-path",
            str(jsonl),
            "--work-item",
            "explicit override phrase",
        ]
    )
    assert rc == 0
    assert any("explicit override phrase" in q for q, _, _ in calls)
    assert not any("from current.json" in q for q, _, _ in calls)
