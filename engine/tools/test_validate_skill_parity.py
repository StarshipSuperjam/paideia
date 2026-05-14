"""Tests for engine/tools/validate.py's validate_skill_layer1_parity().

Per ADR 0089 / Issue #129. Covers step-number-set parity between each recipe
Skill and its Layer-1 ops doc: in-parity passes; a step present on one side
only fires the soft-warn; title wording is allowed to differ; both doc
grammars (``### N.`` headings and ``N. **Title.**`` numbered lists) parse;
sub-letter / minor steps (``0a``, ``5.5``) parse; section-end markers bound
the scan; missing files, unlocatable sections, and empty sections each emit a
soft-warn rather than crash. A smoke test runs against the real repo tree.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate  # noqa: E402
from validate import _SkillDocPair, validate_skill_layer1_parity  # noqa: E402

CATEGORY = "skill_layer1_parity_drift"


def _write_pair(
    repo_root: Path,
    *,
    skill_steps_md: str,
    doc_steps_md: str,
    doc_style: str = "headings",
    skill_section: str = "## Boot procedure",
    skill_section_end: str = "## Done",
    doc_section: str = "## Boot procedure",
    doc_section_end: str = "## Done",
    write_skill: bool = True,
    write_doc: bool = True,
    name: str = "test-pair",
) -> _SkillDocPair:
    """Write a Skill + Layer-1 doc into ``repo_root`` and return their pairing.

    ``skill_steps_md`` / ``doc_steps_md`` are the raw markdown bodies placed
    between the section heading and the section-end heading.
    """
    skill_rel = ".claude/skills/test-pair/SKILL.md"
    doc_rel = "engine/operations/test-pair.md"
    if write_skill:
        skill_path = repo_root / skill_rel
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            f"# Test Skill\n\n{skill_section}\n\n{skill_steps_md}\n\n"
            f"{skill_section_end}\n\nTail content.\n",
            encoding="utf-8",
        )
    if write_doc:
        doc_path = repo_root / doc_rel
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(
            f"# Test Doc\n\n{doc_section}\n\n{doc_steps_md}\n\n"
            f"{doc_section_end}\n\nTail content.\n",
            encoding="utf-8",
        )
    return _SkillDocPair(
        name=name,
        skill_path=skill_rel,
        skill_section=skill_section,
        skill_section_end=skill_section_end,
        doc_path=doc_rel,
        doc_section=doc_section,
        doc_section_end=doc_section_end,
        doc_style=doc_style,
    )


def _run(
    monkeypatch: pytest.MonkeyPatch, repo_root: Path, pair: _SkillDocPair
) -> list[str]:
    """Monkeypatch the pair list to ``pair`` only and return the soft-warns."""
    monkeypatch.setattr(validate, "_SKILL_LAYER1_PAIRS", (pair,))
    result = validate_skill_layer1_parity(repo_root=repo_root)
    assert result.checks_run == [CATEGORY]
    assert result.hard_fails == []
    return result.soft_warns.get(CATEGORY, [])


class TestValidateSkillLayer1Parity:
    def test_in_parity_no_warn(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Identical step-number sets produce no warn."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n\nBody.\n\n### 2. Beta\n\nBody.\n",
            doc_steps_md="### 1. Alpha\n\nBody.\n\n### 2. Beta\n\nBody.\n",
        )
        assert _run(monkeypatch, tmp_path, pair) == []

    def test_step_missing_from_skill_warns(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A step the doc carries but the Skill drops fires the warn."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n\nBody.\n",
            doc_steps_md="### 1. Alpha\n\nBody.\n\n### 2. Beta\n\nBody.\n",
        )
        warns = _run(monkeypatch, tmp_path, pair)
        assert len(warns) == 1
        assert "steps only in Layer-1 doc: {2}" in warns[0]
        assert "steps only in Skill" not in warns[0]

    def test_step_missing_from_doc_warns(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A step the Skill carries but the doc drops fires the warn."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n\nBody.\n\n### 2. Beta\n\nBody.\n",
            doc_steps_md="### 1. Alpha\n\nBody.\n",
        )
        warns = _run(monkeypatch, tmp_path, pair)
        assert len(warns) == 1
        assert "steps only in Skill: {2}" in warns[0]
        assert "steps only in Layer-1 doc" not in warns[0]

    def test_bidirectional_drift_warns(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Each side carrying a unique step fires one warn naming both."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n\n### 2b. Inserted\n",
            doc_steps_md="### 1. Alpha\n\n### 5b. Other\n",
        )
        warns = _run(monkeypatch, tmp_path, pair)
        assert len(warns) == 1
        assert "steps only in Skill: {2b}" in warns[0]
        assert "steps only in Layer-1 doc: {5b}" in warns[0]

    def test_title_wording_difference_no_warn(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Same step numbers with different titles is not drift (skill voice
        vs reference voice legitimately differ per ADR 0044)."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Eager-claim ritual\n\n### 2. Begin work\n",
            doc_steps_md="### 1. Claim slot\n\n### 2. Execute\n",
        )
        assert _run(monkeypatch, tmp_path, pair) == []

    def test_doc_list_style_parses(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The ``N. **Title.**`` numbered-list doc grammar parses to the same
        step numbers as the Skill's heading grammar."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n\n### 2. Beta\n",
            doc_steps_md="1. **Alpha.** Body.\n2. **Beta.** Body.\n",
            doc_style="list",
        )
        assert _run(monkeypatch, tmp_path, pair) == []

    def test_subletter_and_minor_steps_parse(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Sub-letter (``0a``) and minor (``5.5``) step tokens parse and
        compare correctly across both grammars."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md=(
                "### 0a. Pre\n\n### 1. Alpha\n\n### 5.5. Mid\n\n### 7b. Late\n"
            ),
            doc_steps_md=(
                "0a. **Pre.** Body.\n1. **Alpha.** Body.\n"
                "5.5. **Mid.** Body.\n7b. **Late.** Body.\n"
            ),
            doc_style="list",
        )
        assert _run(monkeypatch, tmp_path, pair) == []

    def test_subletter_drift_is_caught(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A sub-letter step present on one side only is caught (the #125
        shape: a ``5b`` collision-check step in the doc but not the Skill)."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n\n### 2. Beta\n",
            doc_steps_md="1. **Alpha.**\n2. **Beta.**\n5b. **Collision check.**\n",
            doc_style="list",
        )
        warns = _run(monkeypatch, tmp_path, pair)
        assert len(warns) == 1
        assert "steps only in Layer-1 doc: {5b}" in warns[0]

    def test_section_end_marker_bounds_the_scan(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Numbered lines after the section-end marker are not counted as
        steps (the routine-mode-operations.md shape — a ``### Concurrency
        control`` subsection with its own ``1. 2. 3.`` list)."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n\n### 2. Beta\n",
            doc_steps_md=(
                "1. **Alpha.**\n2. **Beta.**\n\n"
                "### Concurrency control\n\n"
                "1. **Decoy one.**\n2. **Decoy two.**\n3. **Decoy three.**\n"
            ),
            doc_style="list",
            doc_section_end="### Concurrency control",
        )
        assert _run(monkeypatch, tmp_path, pair) == []

    def test_level_two_heading_is_fallback_bound(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A level-2 ``## `` heading bounds the section even when the
        configured section-end marker is absent from the file."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n\n### 2. Beta\n",
            doc_steps_md="### 1. Alpha\n\n### 2. Beta\n",
            # The doc's real bound below is the auto-written "## Done"; point
            # the configured marker at a heading that does not exist.
            doc_section_end="## Nonexistent Marker",
        )
        assert _run(monkeypatch, tmp_path, pair) == []

    def test_missing_skill_file_warns(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An absent Skill file fires the warn rather than crashing."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="",
            doc_steps_md="### 1. Alpha\n",
            write_skill=False,
        )
        warns = _run(monkeypatch, tmp_path, pair)
        assert len(warns) == 1
        assert "Skill" in warns[0] and "missing" in warns[0]

    def test_missing_doc_file_warns(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An absent Layer-1 doc fires the warn rather than crashing."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n",
            doc_steps_md="",
            write_doc=False,
        )
        warns = _run(monkeypatch, tmp_path, pair)
        assert len(warns) == 1
        assert "Layer-1 doc" in warns[0] and "missing" in warns[0]

    def test_unlocatable_section_warns(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A section heading that does not appear in the file fires the warn.

        Written with the file carrying one heading but the pair configured to
        look for a different one — the parity-check config has drifted from the
        doc's actual structure.
        """
        skill_rel = ".claude/skills/test-pair/SKILL.md"
        doc_rel = "engine/operations/test-pair.md"
        skill_path = tmp_path / skill_rel
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            "# Skill\n\n## Boot procedure\n\n### 1. Alpha\n\n## Done\n",
            encoding="utf-8",
        )
        doc_path = tmp_path / doc_rel
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(
            "# Doc\n\n## Actual Heading\n\n### 1. Alpha\n\n## Done\n",
            encoding="utf-8",
        )
        pair = _SkillDocPair(
            name="test-pair",
            skill_path=skill_rel,
            skill_section="## Boot procedure",
            skill_section_end="## Done",
            doc_path=doc_rel,
            doc_section="## Heading That Is Not In The Doc",
            doc_section_end="## Done",
            doc_style="headings",
        )
        warns = _run(monkeypatch, tmp_path, pair)
        assert len(warns) == 1
        assert "could not locate" in warns[0]

    def test_empty_section_warns(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A located section with no parseable step lines fires the warn (the
        step-line grammar likely changed)."""
        pair = _write_pair(
            tmp_path,
            skill_steps_md="### 1. Alpha\n",
            doc_steps_md="Just prose, no numbered steps at all.\n",
        )
        warns = _run(monkeypatch, tmp_path, pair)
        assert len(warns) == 1
        assert "no procedure steps parsed" in warns[0]

    def test_real_repo_smoke(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Against the real repo tree the check runs without crashing, registers
        its category, and emits no hard-fails. (Soft-warn content is not asserted
        — the live repo may carry known open drift, e.g. Issue #125.)"""
        result = validate_skill_layer1_parity()
        assert result.checks_run == [CATEGORY]
        assert result.hard_fails == []
