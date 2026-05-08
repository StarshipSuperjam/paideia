"""Tests for parse_structural_reference.py.

Mirrors the test-class organization in test_validate.py:
- One TestClass per detector / adapter / emitter / orchestrator.
- One test per logical branch (empty, single match, multiple matches,
  edge case).
- Integration tests against the cached SEP fixtures in
  engine/tools/test_fixtures/sep/.
- CLI tests via subprocess.

The autouse `_scrub_git_env` fixture in engine/tools/conftest.py per
ADR 0045 applies to every test in this module without per-test wiring.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Match the project's per-test import convention (see test_validate.py:46-49):
# add engine/tools/ to sys.path and import the module by its bare name. This
# keeps mypy --strict from seeing the source file under two module names
# when the gate runs against multiple files in the same invocation.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parse_structural_reference import (  # noqa: E402
    ADAPTER_REGISTRY,
    CHARS_PER_WORD_APPROX,
    DOCUMENT_TYPE_REGISTRY,
    ENCYCLOPEDIA_CONFIG,
    PARSER_VERSION,
    PUBLICATION_NAME_PATTERN,
    PUBLICATION_NAME_PATTERN_CONCATENATED,
    PUBLICATION_NAME_SUFFIX_STRIPPER,
    AdapterOutput,
    Entry,
    FocusingBrief,
    HTMLInputAdapter,
    PDFInputAdapter,
    StructuralElement,
    compute_extraction_confidence,
    detect_cross_references,
    detect_entry_id,
    detect_section_path,
    detect_title,
    detect_word_count,
    emit_focusing_brief,
    extract_entries,
    extract_entry_from_partition,
    is_publication_name_shaped,
    main,
    partition_at_entry_boundaries,
    select_adapter,
    serialize_brief,
    slugify_title,
    strip_publication_name_suffix,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SEP_FIXTURE_DIR = REPO_ROOT / "engine" / "tools" / "test_fixtures" / "sep"
PARSER_PATH = REPO_ROOT / "engine" / "tools" / "parse_structural_reference.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_output(
    elements: list[StructuralElement],
    *,
    source_path: str = "/tmp/test.html",
    document_type: str = "encyclopedia",
    source_url: str | None = None,
    full_text: str = "",
) -> AdapterOutput:
    return AdapterOutput(
        source_path=source_path,
        document_type=document_type,
        elements=elements,
        source_url=source_url,
        full_text=full_text,
    )


def _heading(level: int, text: str, position: int) -> StructuralElement:
    return StructuralElement(
        kind="heading",
        text=text,
        attributes={"level": str(level)},
        position=position,
    )


def _anchor(href: str, text: str, position: int) -> StructuralElement:
    return StructuralElement(
        kind="anchor",
        text=text,
        attributes={"href": href},
        position=position,
    )


def _title(text: str, position: int) -> StructuralElement:
    return StructuralElement(kind="title", text=text, attributes={}, position=position)


def _paragraph(text: str, position: int) -> StructuralElement:
    return StructuralElement(
        kind="paragraph", text=text, attributes={}, position=position
    )


# ---------------------------------------------------------------------------
# Module-level constants and registry shape
# ---------------------------------------------------------------------------


class TestModuleConstants:
    def test_parser_version_is_semver_shaped(self) -> None:
        parts = PARSER_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_encyclopedia_config_carries_required_keys(self) -> None:
        # `title_suffix_strip_patterns` was removed at S-0103 per Issue #49 —
        # the structural PUBLICATION_NAME_SUFFIX_STRIPPER at module scope
        # subsumes the previously-enumerated per-publisher patterns. See the
        # source-identity anonymization block in parse_structural_reference.py
        # and the TestPublicationNamePattern test class below.
        for key in (
            "entry_boundary",
            "cross_reference_patterns",
            "section_path_source",
            "minimum_word_count_for_full_entry",
        ):
            assert key in ENCYCLOPEDIA_CONFIG
        assert "title_suffix_strip_patterns" not in ENCYCLOPEDIA_CONFIG

    def test_document_type_registry_includes_encyclopedia(self) -> None:
        assert "encyclopedia" in DOCUMENT_TYPE_REGISTRY
        assert DOCUMENT_TYPE_REGISTRY["encyclopedia"] is ENCYCLOPEDIA_CONFIG

    def test_adapter_registry_maps_html_extensions(self) -> None:
        assert ADAPTER_REGISTRY[".html"] is HTMLInputAdapter
        assert ADAPTER_REGISTRY[".htm"] is HTMLInputAdapter

    def test_chars_per_word_constant_is_positive(self) -> None:
        assert CHARS_PER_WORD_APPROX > 0


# ---------------------------------------------------------------------------
# slugify_title
# ---------------------------------------------------------------------------


class TestSlugifyTitle:
    def test_simple_lowercase_words_join_with_dash(self) -> None:
        assert slugify_title("Virtue Ethics") == "virtue-ethics"

    def test_punctuation_collapses_to_single_dash(self) -> None:
        assert slugify_title("Foo: Bar -- Baz!!") == "foo-bar-baz"

    def test_leading_and_trailing_punctuation_stripped(self) -> None:
        assert slugify_title("  -- hello -- ") == "hello"

    def test_empty_input_returns_empty(self) -> None:
        assert slugify_title("") == ""

    def test_only_punctuation_returns_empty(self) -> None:
        assert slugify_title("---!!!") == ""

    def test_unicode_lowered_and_replaced(self) -> None:
        assert slugify_title("Plato's Republic") == "plato-s-republic"


# ---------------------------------------------------------------------------
# detect_title
# ---------------------------------------------------------------------------


class TestDetectTitle:
    def test_returns_first_title_element(self) -> None:
        out = _make_output([_title("Epistemology", 0), _heading(1, "Heading", 1)])
        assert detect_title(out) == "Epistemology"

    def test_falls_back_to_first_h1_when_no_title(self) -> None:
        out = _make_output([_heading(1, "Some Heading", 0)])
        assert detect_title(out) == "Some Heading"

    def test_returns_none_when_no_title_or_h1(self) -> None:
        out = _make_output([_heading(2, "Sub", 0)])
        assert detect_title(out) is None

    def test_strips_sep_suffix_when_config_provides_pattern(self) -> None:
        out = _make_output(
            [_title("Epistemology (Stanford Encyclopedia of Philosophy)", 0)]
        )
        assert detect_title(out, ENCYCLOPEDIA_CONFIG) == "Epistemology"

    def test_strips_iep_suffix_when_config_provides_pattern(self) -> None:
        out = _make_output(
            [_title("Empiricism | Internet Encyclopedia of Philosophy", 0)]
        )
        assert detect_title(out, ENCYCLOPEDIA_CONFIG) == "Empiricism"

    def test_falls_through_to_h1_when_title_strips_to_empty(self) -> None:
        out = _make_output(
            [
                _title(" (Stanford Encyclopedia of Philosophy)", 0),
                _heading(1, "Fallback", 1),
            ]
        )
        assert detect_title(out, ENCYCLOPEDIA_CONFIG) == "Fallback"

    def test_ignores_empty_title(self) -> None:
        out = _make_output([_title("", 0), _heading(1, "From Heading", 1)])
        assert detect_title(out) == "From Heading"

    def test_ignores_non_h1_headings(self) -> None:
        out = _make_output([_heading(2, "Section", 0), _heading(3, "Sub", 1)])
        assert detect_title(out) is None


# ---------------------------------------------------------------------------
# detect_entry_id
# ---------------------------------------------------------------------------


class TestDetectEntryId:
    def test_extracts_slug_from_entries_url(self) -> None:
        out = _make_output(
            [], source_url="https://plato.stanford.edu/entries/epistemology/"
        )
        assert detect_entry_id(out, "Epistemology") == "epistemology"

    def test_extracts_slug_from_entries_url_with_fragment(self) -> None:
        out = _make_output(
            [], source_url="https://plato.stanford.edu/entries/kant/#1.2"
        )
        assert detect_entry_id(out, "Immanuel Kant") == "kant"

    def test_falls_back_to_iep_url_path_segment(self) -> None:
        out = _make_output([], source_url="https://iep.utm.edu/empiricism/")
        assert detect_entry_id(out, "Empiricism") == "empiricism"

    def test_falls_back_to_source_path_basename_when_no_url(self) -> None:
        out = _make_output(
            [],
            source_path="/some/dir/scientific-method.html",
            source_url=None,
        )
        assert detect_entry_id(out, "Scientific Method") == "scientific-method"

    def test_falls_back_to_slugified_title_when_basename_invalid(self) -> None:
        out = _make_output(
            [], source_path="/tmp/Some Random File.html", source_url=None
        )
        assert detect_entry_id(out, "Virtue Ethics") == "virtue-ethics"

    def test_returns_empty_string_when_all_signals_absent(self) -> None:
        out = _make_output([], source_path="", source_url=None)
        assert detect_entry_id(out, None) == ""


# ---------------------------------------------------------------------------
# detect_cross_references
# ---------------------------------------------------------------------------


class TestDetectCrossReferences:
    def test_matches_sep_sibling_relative_links(self) -> None:
        out = _make_output(
            [
                _anchor("../knowledge-analysis/", "analysis", 0),
                _anchor("../justification-epistemic/", "justification", 1),
            ]
        )
        refs = detect_cross_references(out, ENCYCLOPEDIA_CONFIG)
        assert refs == ["knowledge-analysis", "justification-epistemic"]

    def test_matches_sep_absolute_links(self) -> None:
        out = _make_output(
            [
                _anchor("https://plato.stanford.edu/entries/kant/", "Kant", 0),
            ]
        )
        refs = detect_cross_references(out, ENCYCLOPEDIA_CONFIG)
        assert refs == ["kant"]

    def test_matches_iep_absolute_links(self) -> None:
        out = _make_output(
            [_anchor("https://iep.utm.edu/empiricism/", "Empiricism (IEP)", 0)]
        )
        refs = detect_cross_references(out, ENCYCLOPEDIA_CONFIG)
        assert refs == ["empiricism"]

    def test_deduplicates_repeated_entry_ids(self) -> None:
        out = _make_output(
            [
                _anchor("../kant/", "Kant first", 0),
                _anchor("../kant/", "Kant second", 1),
                _anchor("../kant/#section-1", "Kant fragment", 2),
            ]
        )
        refs = detect_cross_references(out, ENCYCLOPEDIA_CONFIG)
        assert refs == ["kant"]

    def test_drops_non_matching_anchors(self) -> None:
        out = _make_output(
            [
                _anchor("../../about.html", "about", 0),
                _anchor("/contents.html", "contents", 1),
                _anchor("../kant/", "Kant", 2),
            ]
        )
        refs = detect_cross_references(out, ENCYCLOPEDIA_CONFIG)
        assert refs == ["kant"]

    def test_returns_empty_when_no_anchors(self) -> None:
        out = _make_output([])
        assert detect_cross_references(out, ENCYCLOPEDIA_CONFIG) == []

    def test_preserves_source_order(self) -> None:
        out = _make_output(
            [
                _anchor("../zeno/", "zeno", 0),
                _anchor("../aristotle/", "aristotle", 1),
                _anchor("../plato/", "plato", 2),
            ]
        )
        refs = detect_cross_references(out, ENCYCLOPEDIA_CONFIG)
        assert refs == ["zeno", "aristotle", "plato"]


# ---------------------------------------------------------------------------
# detect_section_path
# ---------------------------------------------------------------------------


class TestDetectSectionPath:
    def test_returns_first_h2_text(self) -> None:
        out = _make_output(
            [
                _heading(1, "Title", 0),
                _heading(2, "1. Introduction", 1),
                _heading(2, "2. History", 2),
            ]
        )
        assert detect_section_path(out) == "1. Introduction"

    def test_returns_none_when_no_h2(self) -> None:
        out = _make_output([_heading(1, "Title", 0), _heading(3, "Sub", 1)])
        assert detect_section_path(out) is None

    def test_skips_empty_h2(self) -> None:
        out = _make_output([_heading(2, "", 0), _heading(2, "Real Section", 1)])
        assert detect_section_path(out) == "Real Section"

    def test_returns_none_for_empty_elements(self) -> None:
        out = _make_output([])
        assert detect_section_path(out) is None


# ---------------------------------------------------------------------------
# detect_word_count
# ---------------------------------------------------------------------------


class TestDetectWordCount:
    def test_returns_zero_for_empty_text(self) -> None:
        out = _make_output([], full_text="")
        assert detect_word_count(out) == 0

    def test_divides_chars_by_constant(self) -> None:
        text = "x" * 100
        out = _make_output([], full_text=text)
        assert detect_word_count(out) == 100 // CHARS_PER_WORD_APPROX

    def test_handles_short_text(self) -> None:
        out = _make_output([], full_text="hi")
        assert detect_word_count(out) == 0  # 2 // 5 == 0


# ---------------------------------------------------------------------------
# compute_extraction_confidence
# ---------------------------------------------------------------------------


class TestComputeExtractionConfidence:
    def test_full_signal_yields_one(self) -> None:
        score = compute_extraction_confidence(
            title="Foo",
            entry_id="foo",
            cross_references=["bar"],
            section_path="1. Intro",
            word_count=500,
            document_type_config=ENCYCLOPEDIA_CONFIG,
        )
        assert score == 1.0

    def test_empty_signal_yields_zero(self) -> None:
        score = compute_extraction_confidence(
            title=None,
            entry_id="",
            cross_references=[],
            section_path=None,
            word_count=0,
            document_type_config=ENCYCLOPEDIA_CONFIG,
        )
        assert score == 0.0

    def test_partial_signal_below_one_above_zero(self) -> None:
        score = compute_extraction_confidence(
            title="Foo",
            entry_id="foo",
            cross_references=[],
            section_path=None,
            word_count=10,
            document_type_config=ENCYCLOPEDIA_CONFIG,
        )
        # title (0.30) + entry_id (0.20) = 0.50
        assert score == 0.50

    def test_word_count_threshold_consulted_from_config(self) -> None:
        score = compute_extraction_confidence(
            title=None,
            entry_id="",
            cross_references=[],
            section_path=None,
            word_count=ENCYCLOPEDIA_CONFIG["minimum_word_count_for_full_entry"],
            document_type_config=ENCYCLOPEDIA_CONFIG,
        )
        # Only word-count credit fires.
        assert score == 0.15

    def test_whitespace_only_title_does_not_credit(self) -> None:
        score = compute_extraction_confidence(
            title="   ",
            entry_id="foo",
            cross_references=[],
            section_path=None,
            word_count=0,
            document_type_config=ENCYCLOPEDIA_CONFIG,
        )
        assert score == 0.20  # entry_id only


# ---------------------------------------------------------------------------
# extract_entries (orchestrator)
# ---------------------------------------------------------------------------


class TestExtractEntries:
    def test_returns_empty_when_no_title(self) -> None:
        out = _make_output([_paragraph("Body text without heading", 0)])
        assert extract_entries(out, ENCYCLOPEDIA_CONFIG) == []

    def test_assembles_entry_from_full_signal(self) -> None:
        # Word count is computed per-partition from element text per ADR 0047
        # multi-entry partitioning landed at S-0096. The paragraph text drives
        # word_count; the document-level full_text is no longer consulted by
        # extract_entries because per-partition counts are more meaningful.
        # 1500 chars / 5 = 300 words > 200-word full-entry threshold, so
        # extraction_confidence still hits 1.0 when all five signals fire.
        out = _make_output(
            [
                _title("Epistemology (Stanford Encyclopedia of Philosophy)", 0),
                _heading(1, "Epistemology", 1),
                _heading(2, "1. Cognitive Success", 2),
                _anchor("../knowledge-analysis/", "analysis", 3),
                _anchor("../justification-epistemic/", "justification", 4),
                _paragraph("Body text " * 150, 5),
            ],
            source_path="/local/cache/epistemology.html",
            source_url="https://plato.stanford.edu/entries/epistemology/",
            full_text="x" * 5000,
        )
        entries = extract_entries(out, ENCYCLOPEDIA_CONFIG)
        assert len(entries) == 1
        e = entries[0]
        assert e.title == "Epistemology"
        assert e.entry_id == "epistemology"
        assert e.cross_references == [
            "knowledge-analysis",
            "justification-epistemic",
        ]
        assert e.section_path == "1. Cognitive Success"
        # Per-partition word_count from element text (paragraph dominates):
        # ~1500 / 5 ≈ 300 words.
        assert 200 <= e.word_count <= 400
        assert e.source_url == "https://plato.stanford.edu/entries/epistemology/"
        assert e.extraction_confidence == 1.0

    def test_drops_self_referential_cross_reference(self) -> None:
        out = _make_output(
            [
                _title("Kant", 0),
                _anchor("../kant/", "self", 1),
                _anchor("../categories/", "categories", 2),
            ],
            source_path="/local/kant.html",
        )
        entries = extract_entries(out, ENCYCLOPEDIA_CONFIG)
        assert entries[0].cross_references == ["categories"]

    def test_handles_zero_cross_references(self) -> None:
        out = _make_output(
            [_title("Solo", 0), _heading(1, "Solo", 1), _paragraph("body", 2)],
            source_path="/local/solo.html",
            full_text="body",
        )
        entries = extract_entries(out, ENCYCLOPEDIA_CONFIG)
        assert entries[0].cross_references == []


# ---------------------------------------------------------------------------
# emit_focusing_brief and serialize_brief
# ---------------------------------------------------------------------------


class TestFocusingBrief:
    def test_emit_carries_through_metadata(self) -> None:
        out = _make_output([], source_path="/p/x.html", document_type="encyclopedia")
        brief = emit_focusing_brief(out, [])
        assert brief.source_path == "/p/x.html"
        assert brief.document_type == "encyclopedia"
        assert brief.parser_version == PARSER_VERSION
        assert brief.entries == []
        # generated_at is a non-empty ISO-8601 UTC string.
        assert brief.generated_at.endswith("Z")
        assert "T" in brief.generated_at

    def test_serialize_produces_valid_json(self) -> None:
        brief = FocusingBrief(
            source_path="/p/x.html",
            document_type="encyclopedia",
            parser_version="0.1.0",
            generated_at="2026-05-03T22:00:00Z",
            entries=[
                Entry(
                    title="Foo",
                    entry_id="foo",
                    cross_references=["bar"],
                    section_path=None,
                    word_count=100,
                    source_url=None,
                    extraction_confidence=0.5,
                )
            ],
        )
        serialized = serialize_brief(brief)
        parsed = json.loads(serialized)
        assert parsed["entries"][0]["title"] == "Foo"
        assert parsed["entries"][0]["section_path"] is None
        # source_url stripped at serialization boundary per Issue #49 / S-0103
        # so the downstream LLM cannot infer source identity from URL fields.
        # The in-memory dataclass still carries the field for internal
        # consumers (detect_entry_id slug derivation).
        assert "source_url" not in parsed["entries"][0]
        assert "source_path" not in parsed
        assert parsed["entries"][0]["extraction_confidence"] == 0.5

    def test_serialize_round_trips_unicode(self) -> None:
        brief = FocusingBrief(
            source_path="/p/x.html",
            document_type="encyclopedia",
            parser_version="0.1.0",
            generated_at="2026-05-03T22:00:00Z",
            entries=[
                Entry(
                    title="Schopenhauer's Essence",
                    entry_id="schopenhauer",
                    cross_references=[],
                    section_path=None,
                    word_count=0,
                    source_url=None,
                    extraction_confidence=0.0,
                )
            ],
        )
        serialized = serialize_brief(brief)
        assert "Schopenhauer's Essence" in serialized


# ---------------------------------------------------------------------------
# TestSerializeBriefAnonymization — source-identity strip per Issue #49
# ---------------------------------------------------------------------------
#
# These tests target the serialization-boundary anonymization that
# preserves the ADR 0047 decision 4 parametric-knowledge boundary. The
# in-memory dataclasses retain source_path and source_url for internal
# consumers; the JSON output omits both so a downstream LLM consuming the
# brief cannot infer the publisher and bias its triage.


def _build_anonymization_test_brief() -> FocusingBrief:
    """Construct a FocusingBrief with non-null source_path and per-entry source_url."""
    return FocusingBrief(
        source_path="/path/that/should/not/leak/source.html",
        document_type="encyclopedia",
        parser_version="0.1.0",
        generated_at="2026-05-08T22:00:00Z",
        entries=[
            Entry(
                title="Foundationalism",
                entry_id="foundationalism",
                cross_references=["coherentism"],
                section_path="Epistemology",
                word_count=300,
                source_url="https://example.invalid/entries/foundationalism/",
                extraction_confidence=0.8,
            ),
            Entry(
                title="Coherentism",
                entry_id="coherentism",
                cross_references=["foundationalism"],
                section_path="Epistemology",
                word_count=250,
                source_url="https://example.invalid/entries/coherentism/",
                extraction_confidence=0.7,
            ),
        ],
    )


class TestSerializeBriefAnonymization:
    def test_serialize_brief_strips_top_level_source_path(self) -> None:
        brief = _build_anonymization_test_brief()
        parsed = json.loads(serialize_brief(brief))
        assert "source_path" not in parsed
        # The other top-level fields remain.
        assert parsed["document_type"] == "encyclopedia"
        assert parsed["parser_version"] == "0.1.0"
        assert parsed["generated_at"] == "2026-05-08T22:00:00Z"
        assert len(parsed["entries"]) == 2

    def test_serialize_brief_strips_per_entry_source_url(self) -> None:
        brief = _build_anonymization_test_brief()
        parsed = json.loads(serialize_brief(brief))
        for entry in parsed["entries"]:
            assert "source_url" not in entry
            # Per-entry payload otherwise intact.
            assert "title" in entry
            assert "entry_id" in entry
            assert "cross_references" in entry
            assert "section_path" in entry
            assert "word_count" in entry
            assert "extraction_confidence" in entry

    def test_serialize_brief_preserves_in_memory_dataclasses(self) -> None:
        # The strip happens on the asdict() copy — the in-memory dataclasses
        # remain unchanged because internal consumers (notably
        # detect_entry_id's URL-slug derivation) still need the fields.
        brief = _build_anonymization_test_brief()
        _ = serialize_brief(brief)
        assert brief.source_path == "/path/that/should/not/leak/source.html"
        for entry in brief.entries:
            assert entry.source_url is not None
            assert entry.source_url.startswith("https://example.invalid/")

    def test_serialize_brief_handles_brief_with_no_entries(self) -> None:
        # Empty entries list is the common shape for sources that produced
        # zero parseable entries; the top-level strip must still apply.
        brief = FocusingBrief(
            source_path="/empty.html",
            document_type="encyclopedia",
            parser_version="0.1.0",
            generated_at="2026-05-08T22:00:00Z",
            entries=[],
        )
        parsed = json.loads(serialize_brief(brief))
        assert "source_path" not in parsed
        assert parsed["entries"] == []

    def test_serialize_brief_handles_entry_with_null_source_url(self) -> None:
        # source_url is Optional in Entry; the strip must be safe against
        # already-None values (PDF entries typically lack a source_url).
        brief = FocusingBrief(
            source_path="/x.pdf",
            document_type="encyclopedia",
            parser_version="0.1.0",
            generated_at="2026-05-08T22:00:00Z",
            entries=[
                Entry(
                    title="Foo",
                    entry_id="foo",
                    cross_references=[],
                    section_path=None,
                    word_count=10,
                    source_url=None,
                    extraction_confidence=0.5,
                )
            ],
        )
        parsed = json.loads(serialize_brief(brief))
        assert "source_path" not in parsed
        assert "source_url" not in parsed["entries"][0]


# ---------------------------------------------------------------------------
# TestPublicationNamePattern — structural source-identity detection (Issue #49)
# ---------------------------------------------------------------------------
#
# These tests target the structural patterns and helpers that detect
# publication-name shapes without enumerating publisher tokens. Test data
# uses synthetic publisher tokens (Acme, Synthetic, FakeReference, etc.) —
# the structural pattern fires on the editorial-convention shape, not on
# the brand name. See the source-identity discipline in
# parse_structural_reference.py's anonymization-block doc comment.


class TestPublicationNamePattern:
    @pytest.mark.parametrize(
        "candidate",
        [
            "Acme Encyclopedia of Philosophy",
            "Synthetic Dictionary of History",
            "FakeReference Companion to Logic",
            "MockPublisher Handbook of Linguistics",
            "GenericSource Reference of Mathematics",
            "PlaceholderName Compendium of Astronomy",
            "The Great Acme Encyclopedia of Philosophy",
            "ACME ENCYCLOPEDIA OF PHILOSOPHY",  # all-caps
            "acme encyclopedia of philosophy",  # all-lowercase still matches IGNORECASE
        ],
    )
    def test_publication_name_pattern_matches_canonical_shapes(
        self, candidate: str
    ) -> None:
        assert PUBLICATION_NAME_PATTERN.match(candidate) is not None

    @pytest.mark.parametrize(
        "candidate",
        [
            "AcmeEncyclopediaofPhilosophy",
            "SyntheticDictionaryofHistory",
            "FakeReferenceCompaniontoLogic",
            "MockPublisherHandbookofLinguistics",
        ],
    )
    def test_publication_name_pattern_concatenated_matches_stripped_form(
        self, candidate: str
    ) -> None:
        assert PUBLICATION_NAME_PATTERN_CONCATENATED.search(candidate) is not None

    @pytest.mark.parametrize(
        "candidate",
        [
            "Acme Platonism",
            "Synthetic realism",
            "foundationalism",
            "Generic theory of knowledge",
            "compendium of arguments",  # lowercase noun phrase, not a title
            "encyclopedia",  # bare type token without preposition
            "of philosophy",  # bare prepositional phrase without subject
        ],
    )
    def test_publication_name_pattern_rejects_legitimate_entries(
        self, candidate: str
    ) -> None:
        # The structural pattern requires the editorial-convention shape:
        # a noun phrase + reference-work-type token + preposition + another
        # noun phrase. Bare body-context mentions of any individual word
        # do not match; this is the anti-false-positive guard for entries
        # that happen to mention reference-type words in their body prose.
        assert not is_publication_name_shaped(candidate), candidate

    def test_strip_publication_name_suffix_strips_em_dash_separator(self) -> None:
        result = strip_publication_name_suffix(
            "Foundationalism — Acme Encyclopedia of Philosophy"
        )
        assert result == "Foundationalism"

    def test_strip_publication_name_suffix_strips_hyphen_separator(self) -> None:
        result = strip_publication_name_suffix(
            "Foundationalism - Synthetic Dictionary of History"
        )
        assert result == "Foundationalism"

    def test_strip_publication_name_suffix_strips_pipe_separator(self) -> None:
        result = strip_publication_name_suffix(
            "Foundationalism | FakeReference Companion to Logic"
        )
        assert result == "Foundationalism"

    def test_strip_publication_name_suffix_strips_parenthesized_form(self) -> None:
        # Subsumes the previous SEP-style enumerated pattern structurally —
        # parens + publication-name shape + closing paren.
        result = strip_publication_name_suffix(
            "Foundationalism (MockPublisher Encyclopedia of Philosophy)"
        )
        assert result == "Foundationalism"

    def test_strip_publication_name_suffix_strips_colon_separator(self) -> None:
        result = strip_publication_name_suffix(
            "Foundationalism : GenericSource Reference of Mathematics"
        )
        assert result == "Foundationalism"

    def test_strip_publication_name_suffix_preserves_non_matching_titles(self) -> None:
        assert strip_publication_name_suffix("Foundationalism") == "Foundationalism"
        assert strip_publication_name_suffix("") == ""

    def test_strip_publication_name_suffix_preserves_legitimate_em_dash_titles(
        self,
    ) -> None:
        # Em-dash in title is common ("Foundationalism — A Brief History");
        # only the publication-name SHAPE after a separator triggers strip.
        assert (
            strip_publication_name_suffix("Foundationalism — A Brief History")
            == "Foundationalism — A Brief History"
        )

    def test_is_publication_name_shaped_helper_combines_both_patterns(self) -> None:
        # whole-form shape
        assert is_publication_name_shaped("Acme Encyclopedia of Philosophy")
        # concatenated shape
        assert is_publication_name_shaped("AcmeEncyclopediaofPhilosophy")
        # negative
        assert not is_publication_name_shaped("Foundationalism")
        # empty
        assert not is_publication_name_shaped("")

    def test_publication_name_as_whole_title_returns_none_in_detect_title(self) -> None:
        # When /Title metadata or first <title> is itself a publication name
        # (single-entry export of a book), detect_title must reject it and
        # fall through to the H1 chain.
        out = _make_output(
            [
                _title("Acme Encyclopedia of Philosophy", 0),
                _heading(1, "Foundationalism", 1),
            ]
        )
        assert detect_title(out) == "Foundationalism"

    def test_publication_name_as_h1_skipped_in_detect_title_fallback(self) -> None:
        # When the first H1 is a publication name (rare but possible when
        # an outline emits a book-cover heading), skip and continue.
        out = _make_output(
            [
                _heading(1, "Synthetic Dictionary of History", 0),
                _heading(1, "Causation", 1),
            ]
        )
        assert detect_title(out) == "Causation"

    def test_publication_name_suffix_stripper_is_compiled_regex(self) -> None:
        # Smoke test that the constant exposed at module scope is the
        # expected compiled pattern usable by external callers.
        assert (
            PUBLICATION_NAME_SUFFIX_STRIPPER.search(
                "Foo — Acme Encyclopedia of Philosophy"
            )
            is not None
        )


# ---------------------------------------------------------------------------
# select_adapter
# ---------------------------------------------------------------------------


class TestSelectAdapter:
    def test_resolves_html_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "x.html"
        f.write_text("<html></html>", encoding="utf-8")
        adapter = select_adapter(f)
        assert isinstance(adapter, HTMLInputAdapter)

    def test_resolves_htm_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "x.htm"
        f.write_text("<html></html>", encoding="utf-8")
        adapter = select_adapter(f)
        assert isinstance(adapter, HTMLInputAdapter)

    def test_extension_match_case_insensitive(self, tmp_path: Path) -> None:
        f = tmp_path / "x.HTML"
        f.write_text("<html></html>", encoding="utf-8")
        adapter = select_adapter(f)
        assert isinstance(adapter, HTMLInputAdapter)

    def test_override_with_dotted_form_works(self, tmp_path: Path) -> None:
        f = tmp_path / "x.txt"
        f.write_text("", encoding="utf-8")
        adapter = select_adapter(f, override=".html")
        assert isinstance(adapter, HTMLInputAdapter)

    def test_override_without_dot_works(self, tmp_path: Path) -> None:
        f = tmp_path / "x.txt"
        f.write_text("", encoding="utf-8")
        adapter = select_adapter(f, override="html")
        assert isinstance(adapter, HTMLInputAdapter)

    def test_unknown_extension_raises_value_error(self, tmp_path: Path) -> None:
        # .pdf added to ADAPTER_REGISTRY at S-0096 per Issue #34; use a
        # genuinely-unknown extension to exercise the unknown-extension path.
        f = tmp_path / "x.unknown"
        f.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="No adapter registered"):
            select_adapter(f)

    def test_unknown_override_raises_value_error(self, tmp_path: Path) -> None:
        f = tmp_path / "x.html"
        f.write_text("", encoding="utf-8")
        with pytest.raises(ValueError, match="No adapter registered"):
            select_adapter(f, override="unknown")


# ---------------------------------------------------------------------------
# HTMLInputAdapter
# ---------------------------------------------------------------------------


SYNTHETIC_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Test Entry</title>
  <link rel="canonical" href="https://example.org/entries/test/" />
</head>
<body>
  <h1>Test Entry</h1>
  <h2>1. First Section</h2>
  <p>Body paragraph one.</p>
  <p>See <a href="../other-entry/">other</a>,
     <a href="">empty href dropped</a>,
     <a href="#fragment">fragment dropped</a>,
     <a>no-href dropped</a>.</p>
  <ul>
    <li>List item one.</li>
  </ul>
</body>
</html>
"""


class TestHTMLInputAdapter:
    def test_raises_filenotfound_for_missing_source(self, tmp_path: Path) -> None:
        adapter = HTMLInputAdapter()
        with pytest.raises(FileNotFoundError):
            adapter.extract(tmp_path / "missing.html", "encyclopedia")

    def test_extracts_title_element(self, tmp_path: Path) -> None:
        f = tmp_path / "x.html"
        f.write_text(SYNTHETIC_HTML, encoding="utf-8")
        out = HTMLInputAdapter().extract(f, "encyclopedia")
        titles = [e for e in out.elements if e.kind == "title"]
        assert len(titles) == 1
        assert titles[0].text == "Test Entry"

    def test_extracts_headings_with_levels(self, tmp_path: Path) -> None:
        f = tmp_path / "x.html"
        f.write_text(SYNTHETIC_HTML, encoding="utf-8")
        out = HTMLInputAdapter().extract(f, "encyclopedia")
        headings = [e for e in out.elements if e.kind == "heading"]
        levels = [h.attributes.get("level") for h in headings]
        assert "1" in levels
        assert "2" in levels

    def test_extracts_anchors_drops_empty_and_fragment(self, tmp_path: Path) -> None:
        f = tmp_path / "x.html"
        f.write_text(SYNTHETIC_HTML, encoding="utf-8")
        out = HTMLInputAdapter().extract(f, "encyclopedia")
        hrefs = [e.attributes.get("href") for e in out.elements if e.kind == "anchor"]
        assert hrefs == ["../other-entry/"]

    def test_extracts_canonical_url(self, tmp_path: Path) -> None:
        f = tmp_path / "x.html"
        f.write_text(SYNTHETIC_HTML, encoding="utf-8")
        out = HTMLInputAdapter().extract(f, "encyclopedia")
        assert out.source_url == "https://example.org/entries/test/"

    def test_falls_back_to_og_url_when_no_canonical(self, tmp_path: Path) -> None:
        html = (
            "<html><head><title>x</title>"
            '<meta property="og:url" content="https://og.example/path/" />'
            "</head><body><p>x</p></body></html>"
        )
        f = tmp_path / "x.html"
        f.write_text(html, encoding="utf-8")
        out = HTMLInputAdapter().extract(f, "encyclopedia")
        assert out.source_url == "https://og.example/path/"

    def test_returns_none_url_when_no_metadata(self, tmp_path: Path) -> None:
        html = "<html><head><title>x</title></head><body><p>x</p></body></html>"
        f = tmp_path / "x.html"
        f.write_text(html, encoding="utf-8")
        out = HTMLInputAdapter().extract(f, "encyclopedia")
        assert out.source_url is None

    def test_full_text_excludes_markup(self, tmp_path: Path) -> None:
        f = tmp_path / "x.html"
        f.write_text(SYNTHETIC_HTML, encoding="utf-8")
        out = HTMLInputAdapter().extract(f, "encyclopedia")
        assert "<h1>" not in out.full_text
        assert "Test Entry" in out.full_text

    def test_handles_empty_body(self, tmp_path: Path) -> None:
        html = "<html><head><title>t</title></head><body></body></html>"
        f = tmp_path / "x.html"
        f.write_text(html, encoding="utf-8")
        out = HTMLInputAdapter().extract(f, "encyclopedia")
        # Title element still present; body elements absent.
        kinds = {e.kind for e in out.elements}
        assert "title" in kinds
        assert "paragraph" not in kinds

    def test_propagates_document_type(self, tmp_path: Path) -> None:
        f = tmp_path / "x.html"
        f.write_text(SYNTHETIC_HTML, encoding="utf-8")
        out = HTMLInputAdapter().extract(f, "encyclopedia")
        assert out.document_type == "encyclopedia"


# ---------------------------------------------------------------------------
# Integration tests — real SEP fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def sep_fixtures() -> list[Path]:
    return sorted(SEP_FIXTURE_DIR.glob("*.html"))


class TestSEPFixtureIntegration:
    """End-to-end runs against cached SEP entries.

    The fixtures live in engine/tools/test_fixtures/sep/ and are real
    SEP HTML acquired under SEP's crawl-for-indexing permission per
    content-strategy.md Tier 4. They exist only as parser test inputs
    and never reach the production graph or any user-facing surface
    per ADR 0011 (unchanged).
    """

    def test_fixtures_directory_populated(self, sep_fixtures: list[Path]) -> None:
        assert len(sep_fixtures) >= 5, (
            "Expected at least 5 SEP fixtures for diversity coverage; "
            f"found {len(sep_fixtures)}: {[f.name for f in sep_fixtures]}"
        )

    def test_every_fixture_yields_one_entry(self, sep_fixtures: list[Path]) -> None:
        adapter = HTMLInputAdapter()
        for fx in sep_fixtures:
            out = adapter.extract(fx, "encyclopedia")
            entries = extract_entries(out, ENCYCLOPEDIA_CONFIG)
            assert len(entries) == 1, (
                f"Expected exactly one entry from {fx.name}; got {len(entries)}"
            )

    def test_every_entry_has_clean_title_and_id(self, sep_fixtures: list[Path]) -> None:
        adapter = HTMLInputAdapter()
        for fx in sep_fixtures:
            out = adapter.extract(fx, "encyclopedia")
            entry = extract_entries(out, ENCYCLOPEDIA_CONFIG)[0]
            assert entry.title, f"{fx.name}: empty title"
            assert "Stanford Encyclopedia of Philosophy" not in entry.title, (
                f"{fx.name}: SEP suffix not stripped"
            )
            assert entry.entry_id == fx.stem, (
                f"{fx.name}: entry_id={entry.entry_id!r} did not match stem"
            )

    def test_every_entry_has_at_least_some_cross_references(
        self, sep_fixtures: list[Path]
    ) -> None:
        adapter = HTMLInputAdapter()
        for fx in sep_fixtures:
            out = adapter.extract(fx, "encyclopedia")
            entry = extract_entries(out, ENCYCLOPEDIA_CONFIG)[0]
            assert len(entry.cross_references) >= 1, (
                f"{fx.name}: zero cross-references — parser regression?"
            )

    def test_every_entry_has_full_extraction_confidence(
        self, sep_fixtures: list[Path]
    ) -> None:
        adapter = HTMLInputAdapter()
        for fx in sep_fixtures:
            out = adapter.extract(fx, "encyclopedia")
            entry = extract_entries(out, ENCYCLOPEDIA_CONFIG)[0]
            assert entry.extraction_confidence == 1.0, (
                f"{fx.name}: confidence={entry.extraction_confidence}"
            )

    def test_no_self_reference_in_cross_references(
        self, sep_fixtures: list[Path]
    ) -> None:
        adapter = HTMLInputAdapter()
        for fx in sep_fixtures:
            out = adapter.extract(fx, "encyclopedia")
            entry = extract_entries(out, ENCYCLOPEDIA_CONFIG)[0]
            assert entry.entry_id not in entry.cross_references, (
                f"{fx.name}: self-reference {entry.entry_id} in cross_references"
            )


# ---------------------------------------------------------------------------
# CLI tests via subprocess
# ---------------------------------------------------------------------------


class TestCLI:
    def test_help_runs_clean(self) -> None:
        result = subprocess.run(
            [sys.executable, str(PARSER_PATH), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert "--source" in result.stdout
        assert "--document-type" in result.stdout

    def test_run_against_fixture_writes_to_stdout(self) -> None:
        fixture = SEP_FIXTURE_DIR / "epistemology.html"
        if not fixture.exists():
            pytest.skip("epistemology.html fixture not present")
        result = subprocess.run(
            [
                sys.executable,
                str(PARSER_PATH),
                "--source",
                str(fixture),
                "--document-type",
                "encyclopedia",
                "--output",
                "-",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        parsed = json.loads(result.stdout)
        assert parsed["document_type"] == "encyclopedia"
        assert parsed["parser_version"] == PARSER_VERSION
        assert len(parsed["entries"]) == 1
        assert parsed["entries"][0]["entry_id"] == "epistemology"

    def test_run_against_fixture_writes_to_file(self, tmp_path: Path) -> None:
        fixture = SEP_FIXTURE_DIR / "epistemology.html"
        if not fixture.exists():
            pytest.skip("epistemology.html fixture not present")
        out_path = tmp_path / "brief.json"
        result = subprocess.run(
            [
                sys.executable,
                str(PARSER_PATH),
                "--source",
                str(fixture),
                "--document-type",
                "encyclopedia",
                "--output",
                str(out_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        parsed = json.loads(out_path.read_text(encoding="utf-8"))
        assert parsed["entries"][0]["entry_id"] == "epistemology"

    def test_unknown_document_type_rejected_by_argparse(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(PARSER_PATH),
                "--source",
                "/tmp/x.html",
                "--document-type",
                "unknown-type",
                "--output",
                "-",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
        assert "invalid choice" in result.stderr or "unknown-type" in result.stderr


# ---------------------------------------------------------------------------
# main() in-process tests
# ---------------------------------------------------------------------------


class TestMainEntryPoint:
    def test_main_writes_to_stdout_dash(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        fixture = tmp_path / "test.html"
        fixture.write_text(SYNTHETIC_HTML, encoding="utf-8")
        rc = main(
            [
                "--source",
                str(fixture),
                "--document-type",
                "encyclopedia",
                "--output",
                "-",
            ]
        )
        assert rc == 0
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["entries"][0]["title"] == "Test Entry"

    def test_main_writes_to_file(self, tmp_path: Path) -> None:
        fixture = tmp_path / "test.html"
        fixture.write_text(SYNTHETIC_HTML, encoding="utf-8")
        out_path = tmp_path / "brief.json"
        rc = main(
            [
                "--source",
                str(fixture),
                "--document-type",
                "encyclopedia",
                "--output",
                str(out_path),
            ]
        )
        assert rc == 0
        parsed = json.loads(out_path.read_text(encoding="utf-8"))
        assert parsed["entries"][0]["entry_id"] == "test"

    def test_main_propagates_filenotfound(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            main(
                [
                    "--source",
                    str(tmp_path / "missing.html"),
                    "--document-type",
                    "encyclopedia",
                    "--output",
                    "-",
                ]
            )


# ---------------------------------------------------------------------------
# PDF synthesis helpers (reportlab) — keeps the licensing posture clean
# (no committed third-party PDF blobs) and makes tests self-contained.
# ---------------------------------------------------------------------------


def _build_synthetic_pdf(
    path: Path,
    *,
    entries: list[tuple[str, str]] | None = None,
    title_metadata: str | None = "Synthetic Encyclopedia",
    body_size: int = 10,
    heading_size: int = 18,
    add_outline: bool = True,
    body_lines_per_entry: int = 4,
    crossref_text: str | None = None,
) -> Path:
    """Build a small multi-entry encyclopedia-shaped PDF for testing.

    The synthesized PDF carries:
    - /Title metadata (None to omit)
    - One outline entry per (entry_title, entry_id) tuple if add_outline=True
    - One page per entry: heading at heading_size, body lines at body_size
    - Optional crossref_text spliced into each entry's body for textual
      cross-reference detection tests
    """
    try:
        from reportlab.lib.pagesizes import letter  # type: ignore[import-untyped,unused-ignore]
        from reportlab.pdfgen import canvas as rl_canvas  # type: ignore[import-untyped,unused-ignore]
    except ImportError:
        pytest.skip("reportlab not available")

    if entries is None:
        entries = [("Alpha", "alpha"), ("Beta", "beta"), ("Gamma", "gamma")]

    c = rl_canvas.Canvas(str(path), pagesize=letter)
    # reportlab defaults /Title to "untitled" when setTitle() is not called.
    # When the test wants no metadata, set it to empty so the adapter's
    # junk-filter (which rejects empty/short titles) falls through to the
    # font-size heading fallback.
    c.setTitle(title_metadata if title_metadata is not None else "")
    for entry_title, entry_id in entries:
        c.setFont("Helvetica-Bold", heading_size)
        c.drawString(72, 720, entry_title)
        c.setFont("Helvetica", body_size)
        y = 700
        for i in range(body_lines_per_entry):
            c.drawString(72, y, f"This is body line {i + 1} of {entry_title}.")
            y -= 14
        if crossref_text is not None:
            # Each \n-separated segment becomes its own drawString — reportlab
            # drawString is single-line, so we splice the segments onto
            # successive y positions so pypdfium2's text extractor returns
            # them on separate lines.
            for segment in crossref_text.split("\n"):
                c.drawString(72, y, segment)
                y -= 14
        if add_outline:
            c.bookmarkPage(entry_id)
            c.addOutlineEntry(entry_title, entry_id, level=0)
        c.showPage()
    c.save()
    return path


def _build_body_font_page_header_pdf(
    path: Path,
    *,
    page_runners: list[str],
    body_font_size: int = 10,
    book_section_outline: list[tuple[str, str]] | None = None,
    body_phrase: str | None = None,
) -> Path:
    """Build a PDF for the body-font-entry / page-header-runner class.

    Synthesizes:
      - Optional small outline (book sections only — under threshold-50 so
        the page-header tier is gated-in). Default: ["Cover", "Title Page",
        "Index"]. Set to [] to omit outline entirely.
      - Each page: page-header runner as the FIRST line at body font size
        (no large headings). Body phrase below.
      - body_phrase: optional sentence-case body content placed below
        the runner. Used to verify body content is NOT filtered.

    Per the source-identity discipline, all test publisher tokens used by
    callers should be SYNTHETIC (Acme, Synthetic, FakeReference, etc.).
    """
    try:
        from reportlab.lib.pagesizes import letter  # type: ignore[import-untyped,unused-ignore]
        from reportlab.pdfgen import canvas as rl_canvas  # type: ignore[import-untyped,unused-ignore]
    except ImportError:
        pytest.skip("reportlab not available")

    if book_section_outline is None:
        book_section_outline = [
            ("Cover", "cover"),
            ("Title Page", "title-page"),
            ("Index", "index"),
        ]

    c = rl_canvas.Canvas(str(path), pagesize=letter)
    c.setTitle("")  # /Title metadata absent; structural detection drives titles

    # Optional first page that anchors the outline bookmarks. Without a
    # bookmarkPage call before addOutlineEntry, reportlab drops the entry.
    if book_section_outline:
        c.setFont("Helvetica", body_font_size)
        c.drawString(72, 720, "Front matter")
        for section_title, section_id in book_section_outline:
            c.bookmarkPage(section_id)
            c.addOutlineEntry(section_title, section_id, level=0)
        c.showPage()

    for runner in page_runners:
        c.setFont("Helvetica", body_font_size)
        # Runner sits at body font size — font-size analysis must NOT
        # extract these. Place at top of page so it becomes the first
        # line of pages_text per pypdfium2 reading order.
        c.drawString(72, 740, runner)
        if body_phrase is not None:
            y = 720
            for segment in body_phrase.split("\n"):
                c.drawString(72, y, segment)
                y -= 14
        else:
            c.drawString(72, 720, "Body content for the page below the runner line.")
        c.showPage()
    c.save()
    return path


# ---------------------------------------------------------------------------
# TestPDFInputAdapter — exercises the multi-fallback PDF adapter against
# reportlab-synthesized fixtures. Each test exercises one fallback layer.
# ---------------------------------------------------------------------------


class TestPDFInputAdapter:
    def test_raises_filenotfound_for_missing_source(self, tmp_path: Path) -> None:
        adapter = PDFInputAdapter()
        with pytest.raises(FileNotFoundError):
            adapter.extract(tmp_path / "missing.pdf", "encyclopedia")

    def test_extracts_title_from_metadata(self, tmp_path: Path) -> None:
        f = _build_synthetic_pdf(
            tmp_path / "x.pdf",
            title_metadata="My Test Encyclopedia",
            entries=[("Alpha", "alpha")],
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        titles = [e for e in out.elements if e.kind == "title"]
        assert len(titles) == 1
        assert titles[0].text == "My Test Encyclopedia"

    def test_falls_back_to_largest_font_when_metadata_absent(
        self, tmp_path: Path
    ) -> None:
        f = _build_synthetic_pdf(
            tmp_path / "x.pdf",
            title_metadata=None,
            entries=[("Foundationalism", "foundationalism")],
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        titles = [e for e in out.elements if e.kind == "title"]
        # First-page largest-font run — synthetic PDF puts the heading at
        # heading_size which is larger than body, so the title falls
        # through to that text.
        assert len(titles) == 1
        assert "Foundationalism" in titles[0].text

    def test_extracts_outline_headings_with_levels(self, tmp_path: Path) -> None:
        f = _build_synthetic_pdf(
            tmp_path / "x.pdf",
            entries=[("Alpha", "alpha"), ("Beta", "beta"), ("Gamma", "gamma")],
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        headings = [e for e in out.elements if e.kind == "heading"]
        # Outline entries are at level 0 in pypdfium2 → mapped to L1 here.
        l1_titles = {h.text for h in headings if h.attributes.get("level") == "1"}
        assert "Alpha" in l1_titles
        assert "Beta" in l1_titles
        assert "Gamma" in l1_titles

    def test_extracts_textual_crossref_anchors(self, tmp_path: Path) -> None:
        f = _build_synthetic_pdf(
            tmp_path / "x.pdf",
            entries=[("Alpha", "alpha")],
            crossref_text="See also: Beta, Gamma, Delta.",
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        anchors = [e for e in out.elements if e.kind == "anchor"]
        hrefs = {a.attributes.get("href") for a in anchors}
        # All three "See also" targets should appear as canonical
        # internal:<slug> hrefs.
        assert "internal:beta" in hrefs
        assert "internal:gamma" in hrefs
        assert "internal:delta" in hrefs

    def test_textual_crossref_splits_on_commas_and_and(self, tmp_path: Path) -> None:
        f = _build_synthetic_pdf(
            tmp_path / "x.pdf",
            entries=[("Alpha", "alpha")],
            crossref_text="See: foo, bar and baz.",
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        slugs = {a.attributes.get("href") for a in out.elements if a.kind == "anchor"}
        assert "internal:foo" in slugs
        assert "internal:bar" in slugs
        assert "internal:baz" in slugs

    def test_textual_crossref_rejects_numeric_and_positional_slugs(
        self, tmp_path: Path
    ) -> None:
        f = _build_synthetic_pdf(
            tmp_path / "x.pdf",
            entries=[("Alpha", "alpha")],
            crossref_text="See: above, 14, below, ibid.",
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        hrefs = {a.attributes.get("href") for a in out.elements if a.kind == "anchor"}
        # Pure-numeric and editorial-positional slugs should NOT survive
        # the crossref filter.
        assert "internal:above" not in hrefs
        assert "internal:below" not in hrefs
        assert "internal:14" not in hrefs
        assert "internal:ibid" not in hrefs

    def test_full_text_concatenates_pages(self, tmp_path: Path) -> None:
        f = _build_synthetic_pdf(
            tmp_path / "x.pdf",
            entries=[("Alpha", "alpha"), ("Beta", "beta")],
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        assert "Alpha" in out.full_text
        assert "Beta" in out.full_text
        assert "body line" in out.full_text

    def test_propagates_document_type(self, tmp_path: Path) -> None:
        f = _build_synthetic_pdf(tmp_path / "x.pdf", entries=[("Alpha", "alpha")])
        out = PDFInputAdapter().extract(f, "encyclopedia")
        assert out.document_type == "encyclopedia"

    def test_returns_none_url_when_subject_metadata_absent(
        self, tmp_path: Path
    ) -> None:
        f = _build_synthetic_pdf(tmp_path / "x.pdf", entries=[("Alpha", "alpha")])
        out = PDFInputAdapter().extract(f, "encyclopedia")
        assert out.source_url is None

    def test_text_pattern_chapter_heading_caught(self, tmp_path: Path) -> None:
        # Chapter regex requires short line + <=8 words. "Chapter 1: Intro"
        # passes; "Chapter 14 of his Proslogion" should NOT.
        f = _build_synthetic_pdf(
            tmp_path / "x.pdf",
            entries=[("Section A", "section-a")],
            crossref_text="Chapter 1: Intro\nChapter 14 of his Proslogion in 1078",
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        heading_texts = {e.text for e in out.elements if e.kind == "heading"}
        assert "Chapter 1: Intro" in heading_texts
        # Body-prose Chapter mention should NOT be emitted as a heading.
        assert "Chapter 14 of his Proslogion in 1078" not in heading_texts


# ---------------------------------------------------------------------------
# TestMultiEntryPartitioning — exercises partition_at_entry_boundaries() and
# extract_entries()'s multi-entry path. The SEP integration tests above are
# the load-bearing regression bar; these tests exercise the new code paths
# directly with synthetic fixtures.
# ---------------------------------------------------------------------------


class TestMultiEntryPartitioning:
    def test_partition_at_h1_boundaries_yields_n_partitions(self) -> None:
        out = _make_output(
            [
                _heading(1, "Alpha", 0),
                _paragraph("Alpha body", 1),
                _heading(1, "Beta", 2),
                _paragraph("Beta body", 3),
                _heading(1, "Gamma", 4),
            ]
        )
        partitions = partition_at_entry_boundaries(out, ENCYCLOPEDIA_CONFIG)
        assert len(partitions) == 3
        assert partitions[0][0].text == "Alpha"
        assert partitions[1][0].text == "Beta"
        assert partitions[2][0].text == "Gamma"

    def test_zero_boundaries_yields_single_partition(self) -> None:
        # No h1 headings; whole-document fallback partition kicks in.
        out = _make_output(
            [
                _title("Whole doc title", 0),
                _paragraph("body", 1),
            ]
        )
        partitions = partition_at_entry_boundaries(out, ENCYCLOPEDIA_CONFIG)
        assert len(partitions) == 1
        # Fallback partition contains the title + paragraph.
        assert any(e.kind == "title" for e in partitions[0])

    def test_preamble_before_first_boundary_dropped(self) -> None:
        out = _make_output(
            [
                _title("Preamble title", 0),
                _heading(2, "Subheading before first h1", 1),
                _heading(1, "First Entry", 2),
                _paragraph("first body", 3),
                _heading(1, "Second Entry", 4),
            ]
        )
        partitions = partition_at_entry_boundaries(out, ENCYCLOPEDIA_CONFIG)
        # Two partitions, preamble (title + h2) dropped.
        assert len(partitions) == 2
        assert partitions[0][0].text == "First Entry"
        assert partitions[1][0].text == "Second Entry"
        # The preamble title should NOT appear in any partition.
        all_partition_texts = {e.text for p in partitions for e in p}
        assert "Preamble title" not in all_partition_texts

    def test_extract_entries_returns_n_entries_for_n_h1_doc(self) -> None:
        out = _make_output(
            [
                _heading(1, "Alpha", 0),
                _anchor("internal:beta", "Beta", 1),
                _heading(1, "Beta", 2),
                _anchor("internal:gamma", "Gamma", 3),
                _heading(1, "Gamma", 4),
            ]
        )
        entries = extract_entries(out, ENCYCLOPEDIA_CONFIG)
        assert len(entries) == 3
        assert [e.title for e in entries] == ["Alpha", "Beta", "Gamma"]

    def test_extract_entries_returns_one_entry_for_zero_boundary_doc(self) -> None:
        # Whole-document fallback: title element + no boundary headings.
        out = _make_output(
            [
                _title("Sole Entry", 0),
                _paragraph("body", 1),
            ]
        )
        entries = extract_entries(out, ENCYCLOPEDIA_CONFIG)
        assert len(entries) == 1
        assert entries[0].title == "Sole Entry"

    def test_partition_skipped_when_no_title_detectable(self) -> None:
        # Whitespace-only heading text → partition exists but no title detectable
        # → entry filtered out.
        out = _make_output(
            [
                _heading(1, "  ", 0),
                _anchor("internal:foo", "foo", 1),
                _heading(1, "Real Entry", 2),
                _anchor("internal:bar", "bar", 3),
            ]
        )
        entries = extract_entries(out, ENCYCLOPEDIA_CONFIG)
        # First partition's heading is whitespace; detect_title returns None
        # under whitespace-only conditions; partition skipped per
        # extract_entry_from_partition's None return.
        titles = [e.title for e in entries]
        assert "Real Entry" in titles

    def test_per_partition_cross_references_distributed(self) -> None:
        # Cross-references should land in their containing partition based on
        # element list order — this is the fix for the Routledge bug where all
        # anchors landed in the last partition before the reorder pass.
        out = _make_output(
            [
                _heading(1, "First", 0),
                _anchor("internal:first-ref", "first-ref", 1),
                _heading(1, "Second", 2),
                _anchor("internal:second-ref", "second-ref", 3),
                _heading(1, "Third", 4),
                _anchor("internal:third-ref", "third-ref", 5),
            ]
        )
        entries = extract_entries(out, ENCYCLOPEDIA_CONFIG)
        assert len(entries) == 3
        assert entries[0].cross_references == ["first-ref"]
        assert entries[1].cross_references == ["second-ref"]
        assert entries[2].cross_references == ["third-ref"]

    def test_extract_entry_from_partition_returns_none_without_title(self) -> None:
        partition_elements = [
            _anchor("internal:foo", "foo", 0),
            _paragraph("body", 1),
        ]
        out = _make_output(partition_elements)
        result = extract_entry_from_partition(
            partition_elements, out, ENCYCLOPEDIA_CONFIG
        )
        assert result is None


# ---------------------------------------------------------------------------
# TestPageHeaderEntryIndicator — third-tier PDF detector for body-font/page-
# header-runner class per Issue #48. Synthetic publisher tokens throughout.
# ---------------------------------------------------------------------------


class TestPageHeaderEntryIndicator:
    def test_synthetic_body_font_pdf_emits_entries_via_page_header_path(
        self, tmp_path: Path
    ) -> None:
        f = _build_body_font_page_header_pdf(
            tmp_path / "x.pdf",
            page_runners=[
                "Foundationalism Coherentism",
                "Coherentism Externalism",
                "Externalism Internalism",
            ],
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        heading_texts = [e.text for e in out.elements if e.kind == "heading"]
        # Each runner contributes both tokens; tokens are deduped at emit-time.
        assert "Foundationalism" in heading_texts
        assert "Coherentism" in heading_texts
        assert "Externalism" in heading_texts
        assert "Internalism" in heading_texts

    def test_page_header_path_gated_off_when_outline_count_above_50(
        self, tmp_path: Path
    ) -> None:
        # Synthesize a PDF whose outline already supplies >= 50 headings so
        # the page-header tier returns early. Page-header runners on body
        # pages must not produce additional level-1 headings.
        many_outline = [(f"OutlineEntry{i}", f"outline-{i}") for i in range(60)]
        f = _build_body_font_page_header_pdf(
            tmp_path / "x.pdf",
            page_runners=["RunnerAlpha RunnerBeta"],
            book_section_outline=many_outline,
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        heading_texts = [e.text for e in out.elements if e.kind == "heading"]
        # Outline entries present.
        assert any(t.startswith("OutlineEntry") for t in heading_texts)
        # Page-header tokens NOT emitted because outline >= 50 short-circuits.
        assert "RunnerAlpha" not in heading_texts
        assert "RunnerBeta" not in heading_texts

    def test_page_header_path_handles_concatenated_tokens(self, tmp_path: Path) -> None:
        # Sources that strip whitespace from runners produce concatenated
        # forms; the case-transition split helper must recover the tokens.
        f = _build_body_font_page_header_pdf(
            tmp_path / "x.pdf",
            page_runners=["FoundationalismCoherentism"],
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        heading_texts = [e.text for e in out.elements if e.kind == "heading"]
        assert "Foundationalism" in heading_texts
        assert "Coherentism" in heading_texts

    def test_is_page_header_shaped_rejects_body_lines(self) -> None:
        adapter = PDFInputAdapter()
        # Sentence-case body line with terminal punctuation — rejected.
        assert not adapter._is_page_header_shaped(
            "This is a regular body sentence.", ""
        )

    def test_is_page_header_shaped_rejects_terminal_punctuation(self) -> None:
        adapter = PDFInputAdapter()
        assert not adapter._is_page_header_shaped("This is a sentence.", "")
        assert not adapter._is_page_header_shaped("Question?", "")
        assert not adapter._is_page_header_shaped("Exclamation!", "")

    def test_is_page_header_shaped_rejects_overly_long_lines(self) -> None:
        adapter = PDFInputAdapter()
        # Lines over 80 chars are unlikely to be runners (paragraph wrapped
        # body content reaching the first-line position).
        assert not adapter._is_page_header_shaped("A " * 50, "")

    def test_is_page_header_shaped_rejects_pure_lowercase(self) -> None:
        adapter = PDFInputAdapter()
        assert not adapter._is_page_header_shaped("all lowercase no caps", "")

    def test_is_page_header_shaped_accepts_title_case(self) -> None:
        adapter = PDFInputAdapter()
        assert adapter._is_page_header_shaped(
            "Foundationalism Coherentism",
            "Body content goes here without the runner",
        )

    def test_is_page_header_shaped_accepts_all_caps(self) -> None:
        adapter = PDFInputAdapter()
        assert adapter._is_page_header_shaped(
            "FOUNDATIONALISM COHERENTISM",
            "Body content here",
        )

    def test_split_camel_concat_recovers_tokens_at_lowercase_to_upper(
        self,
    ) -> None:
        adapter = PDFInputAdapter()
        assert adapter._split_camel_concat("FooBar") == ["Foo", "Bar"]
        assert adapter._split_camel_concat("FoundationalismCoherentism") == [
            "Foundationalism",
            "Coherentism",
        ]

    def test_split_camel_concat_returns_singleton_when_no_boundary(self) -> None:
        adapter = PDFInputAdapter()
        # All-uppercase or all-lowercase have no case-transition boundary;
        # fall through to the original string.
        assert adapter._split_camel_concat("FOUNDATIONALISM") == ["FOUNDATIONALISM"]
        assert adapter._split_camel_concat("foundationalism") == ["foundationalism"]
        assert adapter._split_camel_concat("Foundationalism") == ["Foundationalism"]

    def test_split_camel_concat_handles_uppercase_run_to_titlecase(self) -> None:
        adapter = PDFInputAdapter()
        # "ABCFoo" — uppercase run "ABC" transitions to a Title-cased word
        # "Foo" at index 3 because text[2]='C' upper, text[3]='F' upper,
        # text[4]='o' lower. Tokens: ["ABC", "Foo"].
        result = adapter._split_camel_concat("ABCFoo")
        assert result == ["ABC", "Foo"]

    def test_split_camel_concat_empty_input(self) -> None:
        adapter = PDFInputAdapter()
        assert adapter._split_camel_concat("") == []


# ---------------------------------------------------------------------------
# TestPageHeaderAnonymizationInvariant — cross-deliverable invariant gate
# (Issue #48 + Issue #49). Adversarial fixtures with synthetic publisher
# tokens to exercise the publication-name filter at every layer.
# ---------------------------------------------------------------------------


class TestPageHeaderAnonymizationInvariant:
    def test_publication_name_page_header_runner_filtered_out(
        self, tmp_path: Path
    ) -> None:
        # When every page's first line is a publication name, zero level-1
        # headings should be emitted by the page-header detector. The
        # outline supplies its small set of book-section headings only.
        f = _build_body_font_page_header_pdf(
            tmp_path / "x.pdf",
            page_runners=[
                "The Acme Dictionary of Philosophy",
                "The Acme Dictionary of Philosophy",
                "The Acme Dictionary of Philosophy",
            ],
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        heading_texts = [e.text for e in out.elements if e.kind == "heading"]
        # No heading should carry the publication name (or its tokens).
        for t in heading_texts:
            assert not is_publication_name_shaped(t), t
            assert "Acme" not in t or "Dictionary" not in t

    def test_concatenated_publication_name_page_header_filtered_out(
        self, tmp_path: Path
    ) -> None:
        f = _build_body_font_page_header_pdf(
            tmp_path / "x.pdf",
            page_runners=[
                "TheAcmeDictionaryofPhilosophy",
                "TheAcmeDictionaryofPhilosophy",
            ],
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        heading_texts = [e.text for e in out.elements if e.kind == "heading"]
        for t in heading_texts:
            assert not is_publication_name_shaped(t), t

    def test_alternating_publication_name_and_entry_pair_runners(
        self, tmp_path: Path
    ) -> None:
        # Even pages carry the publication name (book-title typography);
        # odd pages carry entry-pair runners. Only entry-pair tokens
        # should survive the anonymization filter.
        f = _build_body_font_page_header_pdf(
            tmp_path / "x.pdf",
            page_runners=[
                "Foundationalism Coherentism",
                "The Acme Dictionary of Philosophy",
                "Externalism Internalism",
                "The Acme Dictionary of Philosophy",
                "Reliabilism Skepticism",
                "The Acme Dictionary of Philosophy",
            ],
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        heading_texts = [e.text for e in out.elements if e.kind == "heading"]
        # Entry-pair tokens emitted.
        for expected in [
            "Foundationalism",
            "Coherentism",
            "Externalism",
            "Internalism",
            "Reliabilism",
            "Skepticism",
        ]:
            assert expected in heading_texts, f"missing {expected}"
        # Publication-name shape NOT in any heading.
        for t in heading_texts:
            assert not is_publication_name_shaped(t), t

    def test_recursive_brief_grep_for_publication_name_shape(
        self, tmp_path: Path
    ) -> None:
        # Full pipeline: synthesize, parse, emit brief, serialize. Recursive
        # walk over the JSON dict asserts no string field at any depth
        # matches PUBLICATION_NAME_PATTERN or PUBLICATION_NAME_PATTERN_CONCATENATED.
        f = _build_body_font_page_header_pdf(
            tmp_path / "x.pdf",
            page_runners=[
                "Foundationalism Coherentism",
                "The Acme Dictionary of Philosophy",
                "Externalism Internalism",
            ],
        )
        adapter_output = PDFInputAdapter().extract(f, "encyclopedia")
        entries = extract_entries(adapter_output, ENCYCLOPEDIA_CONFIG)
        brief = emit_focusing_brief(adapter_output, entries)
        parsed = json.loads(serialize_brief(brief))

        leaks: list[tuple[str, str]] = []

        def walk(obj: object, path: str) -> None:
            if isinstance(obj, str):
                if PUBLICATION_NAME_PATTERN.match(obj.strip()):
                    leaks.append((path, obj))
                if PUBLICATION_NAME_PATTERN_CONCATENATED.search(obj):
                    leaks.append((path, obj))
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    walk(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    walk(v, f"{path}[{i}]")

        walk(parsed, "root")
        assert leaks == [], f"publication-name shape leaked: {leaks}"

    def test_legitimate_body_publisher_phrase_preserved(self, tmp_path: Path) -> None:
        # Body-context phrase containing reference-type words should NOT be
        # filtered — the structural pattern catches the editorial-convention
        # title shape, not bare body mentions.
        f = _build_body_font_page_header_pdf(
            tmp_path / "x.pdf",
            page_runners=["Foundationalism Coherentism"],
            body_phrase=(
                "Acme Platonism is a hypothetical movement in epistemology. "
                "It draws on a compendium of arguments from earlier traditions."
            ),
        )
        out = PDFInputAdapter().extract(f, "encyclopedia")
        # The body phrase appears in full_text intact (the page-header
        # detector touched only the first-line tokens).
        assert "Acme Platonism" in out.full_text
        assert "compendium of arguments" in out.full_text

    def test_extract_entries_drops_partition_with_publication_name_first_heading(
        self,
    ) -> None:
        # Defense-in-depth at the partition layer: even if a heading
        # element with a publication-name shape arrives via some emit
        # path, extract_entries drops the partition before producing
        # an Entry record.
        out = _make_output(
            [
                _heading(1, "Acme Encyclopedia of Philosophy", 0),
                _paragraph("This partition should be dropped entirely.", 1),
                _heading(1, "Foundationalism", 2),
                _paragraph(
                    "This partition is preserved (legitimate philosophy entry).",
                    3,
                ),
            ]
        )
        entries = extract_entries(out, ENCYCLOPEDIA_CONFIG)
        assert len(entries) == 1
        assert entries[0].title == "Foundationalism"
