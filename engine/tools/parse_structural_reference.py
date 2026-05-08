#!/usr/bin/env python3
"""Structural-reference parser — extract graph-shape signal from a source.

Module contract — what this file is and is not.

This module is a standing engine tool that extracts graph-shape signal
from a structural-reference source (encyclopedia, dictionary, textbook)
the user has acquired through legitimate channels per ADR 0046. The
graph-shape signal — entry inventory, cross-reference adjacency,
section/topic tags, per-entry word counts and URLs — is emitted as a
JSON focusing brief consumed by an adversarial-triage LLM prompt
against current graph state and parametric knowledge of the concepts.
The brief is then discarded; the graph is the only durable artifact.

The full operational contract lives in ADR 0047
(engine/adr/0047-structural-reference-parser-tool-and-adversarial-
triage-workflow.md). This docstring summarizes the load-bearing claims
the implementation honors.

Three responsibility families live here:

1. Input adaptation — convert a source file (HTML, future PDF / plaintext)
   into a uniform AdapterOutput carrying StructuralElement records.
   Concrete adapter shipped: HTMLInputAdapter for SEP-shaped HTML.
   PDF and plaintext adapters are deferred per ADR 0047 to first-source-
   acquisition. The adapter interface is in place; new adapters subclass
   InputAdapter and are registered in ADAPTER_REGISTRY.

2. Structural detection — pure functions consuming AdapterOutput and
   producing Entry records. Detectors are deliberately recall-prioritized
   over precision per ADR 0047 (section 3): a parser that finds 60% of
   real cross-references with some noise is useful; the LLM's parametric
   knowledge does final triage. Detectors do no I/O; they are testable
   without filesystem or network.

3. Focusing-brief emission — assemble Entry records into a JSON-
   serializable FocusingBrief and write it to a file or stdout.

Invariants this module preserves:

- Read-only with respect to the source. The parser reads source files
  via the adapter; it never writes to or modifies the source. Outputs
  are written only to the path the caller names (or stdout when --output
  is "-").
- Deterministic for a given source. Two parser runs against the same
  bytes produce the same FocusingBrief modulo the generated_at timestamp.
- No persistence beyond the named output. There is no parser_findings/
  directory, no cross-source corroboration index, no aging policy
  per ADR 0047 (decision 3). Re-running the parser against the same
  source produces a fresh focusing brief; same-source re-runs are
  indistinguishable from independent extractions for credibility
  purposes — that is the deliberate posture, not an oversight.
- Recall over precision. The structural detectors err toward surfacing
  more candidates, not fewer; the LLM triage filters noise via the
  parametric-knowledge boundary (ADR 0047 decision 4).

Non-responsibilities:

- No source acquisition. The user supplies the source path; legitimate-
  channel acquisition is the user's responsibility per ADR 0046. The
  parser does not crawl, scrape, download, or otherwise fetch sources.
- No graph mutation. The parser never writes to the Supabase graph or
  to engine/STATE.md or to any committed artifact other than the focusing-
  brief output the caller named.
- No LLM invocation. The triage step that consumes the focusing brief is
  out-of-process; this module produces the brief and exits.
- No content reproduction. The brief carries graph-shape facts (titles,
  identifiers, cross-reference adjacency, URLs, word-counts). It does
  not carry source prose. Source-prose passages are not loaded into
  Entry records, not written to output, not surfaced anywhere. ADR 0011
  remains unchanged operationally.
- No correctness guarantees. Cross-reference detection is heuristic;
  per-document-type configs cover canonical cases; idiosyncratic source
  formatting may be missed. Same outcome as the LLM rejecting the
  candidate downstream — the parametric-knowledge boundary covers
  parser misses.

Output schema (FocusingBrief, JSON-serialized):

    {
        "document_type": "encyclopedia" | "dictionary" | "textbook",
        "parser_version": "<PARSER_VERSION constant>",
        "generated_at": "<ISO-8601 UTC>",
        "entries": [
            {
                "title": "<entry title>",
                "entry_id": "<slug or identifier>",
                "cross_references": ["<entry_id>", ...],
                "section_path": "<topical category>" | null,
                "word_count": <int>,
                "extraction_confidence": <float 0.0-1.0>
            }
        ]
    }

Source identity is anonymized at the serialization boundary per ADR 0047
decision 4 — the JSON omits top-level `source_path` and per-entry
`source_url` so a downstream LLM consuming the brief cannot infer the
publisher and bias its triage. The in-memory `FocusingBrief` and `Entry`
dataclasses retain those fields for internal consumers (notably
`detect_entry_id` slug derivation); only `serialize_brief()` strips them.
Title detection additionally strips structurally-shaped publication-name
suffixes via `strip_publication_name_suffix()` so titles arriving from
`/Title` metadata or `<title>` tags don't carry the publication name
into the brief.

CLI invocation:

    python3 engine/tools/parse_structural_reference.py \\
        --source <path> \\
        --document-type encyclopedia \\
        --output <path-or-dash>

    --source         Path to the source file the adapter reads.
    --document-type  One of DOCUMENT_TYPE_REGISTRY keys (currently
                     "encyclopedia"). Selects per-type heuristic config.
    --output         Output path. "-" writes to stdout.
    --adapter        Optional explicit adapter selection (default: inferred
                     from file extension via ADAPTER_REGISTRY).

Module contracts referenced:

- ADR 0047 — operational contract for this tool; parser is standing,
  document-agnostic, ephemeral-output, adversarial-triage downstream.
- ADR 0046 — structural-reference posture; class boundary; source-
  acquisition discipline.
- ADR 0011 — no hosted or distributed copyrighted material; the brief
  carries facts not prose.
- ADR 0030 — accepted candidates land as INTERPRETED nodes after triage.
- ADR 0001 — pedagogical-prerequisite framing; the third triage rejection
  filter applies this.
- ADR 0038 — code-discipline contract; this module authors under it.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from timestamps import emit  # noqa: E402  # ADR 0058

PARSER_VERSION = "0.1.0"

# --------------------------------------------------------------------------
# Per-document-type heuristic configs
# --------------------------------------------------------------------------
#
# Each config names the structural cues a document of that type carries.
# Configs are declarative dicts at module top so adding a new document
# type is a single-table edit. Per ADR 0047 (decision 2) the configs name
# document type, not source — SEP and IEP are both "encyclopedia"; both
# share the encyclopedia config; per-source idiosyncrasies are absorbed
# by the LLM's adversarial triage downstream, not by per-source code.

ENCYCLOPEDIA_CONFIG: dict[str, Any] = {
    "entry_boundary": "h1",
    "cross_reference_patterns": [
        # SEP sibling-entry convention as actually rendered in published
        # entry HTML: ../<slug>/ resolved from .../entries/<this-entry>/.
        # The leading ../ jumps to /entries/ and lands on the sibling.
        r"^\.\./([a-z][a-z0-9\-]*)/?(?:#.*)?$",
        # Less-common nested-entries form (occurs in some legacy / staging
        # contexts and in the SEP archives subtree): entries/<slug>/.
        r"^(?:\.\.?/)*entries/([a-z0-9][a-z0-9\-]*)/?(?:#.*)?$",
        # SEP absolute cross-links: https://plato.stanford.edu/entries/<slug>/
        r"^https?://plato\.stanford\.edu/entries/([a-z0-9][a-z0-9\-]*)/?(?:#.*)?$",
        # IEP cross-link convention: https://iep.utm.edu/<slug>/
        r"^https?://iep\.utm\.edu/([a-z0-9][a-z0-9\-]*)/?(?:#.*)?$",
        # Canonical PDF-emitted form (added at S-0096 per ADR 0047 + Issue #34).
        # PDFInputAdapter slugifies both link-annotation targets and textual
        # editorial-marker cross-refs into "internal:<slug>" hrefs. The pattern
        # is appended last so the more-specific HTML patterns above win when
        # HTML hrefs happen to be slug-shaped.
        r"^internal:([a-z0-9][a-z0-9\-]*)$",
    ],
    "section_path_source": "first_section_heading",
    "minimum_word_count_for_full_entry": 200,
    # Title-suffix anonymization moved to the structural stripper at
    # module scope (PUBLICATION_NAME_SUFFIX_STRIPPER + helpers below).
    # The previous enumerated patterns (per-publisher suffixes) were
    # subsumed at S-0103 per ADR 0047 decision 4: the structural pattern
    # matches any "<X> Encyclopedia/Dictionary/Companion/Handbook/Reference/
    # Compendium of/to <Y>" suffix without enumerating publisher names,
    # preserving the parametric-knowledge boundary at the project's own
    # config layer (no source-identity tokens embedded in code).
}

DOCUMENT_TYPE_REGISTRY: dict[str, dict[str, Any]] = {
    "encyclopedia": ENCYCLOPEDIA_CONFIG,
}

# Approximate characters-per-word for stripped prose word-count estimation.
# Calibrated against English academic prose; coarse but adequate for the
# graph-shape signal the brief carries (the LLM does not consume
# word_count for fine-grained decisions).
CHARS_PER_WORD_APPROX = 5

# --------------------------------------------------------------------------
# PDFInputAdapter constants — source-agnostic posture per ADR 0047 + Issue #34
# --------------------------------------------------------------------------
#
# These constants tune the multi-fallback heuristics PDFInputAdapter relies
# on. None of them encode per-source assumptions; the values are calibrated
# to span editorial conventions broadly shared across published reference
# works (Routledge, Oxford, Cambridge, and similar). Per ADR 0047 decision 3
# the adapter is recall-prioritized — false positives are absorbed by the
# downstream LLM triage; the only structural failure is producing nothing.

# Top-N font-size buckets become heading levels 1..N when the outline
# fallback fires. 3 is enough to distinguish entry-level / section-level /
# subsection-level for typical encyclopedia typography; the LLM filters
# false-positive runs.
PDF_HEADING_FONT_BUCKET_COUNT = 3

# Minimum char count of a font-size bucket before it qualifies as a heading
# bucket. Smaller buckets are likely typographic accents (drop-caps, single
# emphasis runs) rather than systematic heading-level signals.
PDF_HEADING_FONT_MIN_BUCKET_CHARS = 5

# Universal editorial-convention regex patterns for textual cross-reference
# detection. Editorial conventions broadly shared across reference works:
# "See: X", "See also: A, B, C", parenthetical "(see X)", arrow "→ X",
# scholarly "Cf. X". Patterns capture the cross-reference target text up
# to terminal punctuation; the captured group is then comma-split and each
# segment slugified. NO per-source patterns — this set must work across
# any reference PDF format the user feeds in.
PDF_TEXT_CROSSREF_PATTERNS = [
    r"\bSee:\s+([^.\n;:()]+)",
    r"\bSee also:\s+([^.\n;:()]+)",
    r"\(see\s+([^).\n;:]+)\)",
    r"\(see also\s+([^).\n;:]+)\)",
    r"→\s+([^.\n;:()]+)",
    r"\bCf\.\s+([^.\n;:()]+)",
]

# --------------------------------------------------------------------------
# Source-identity anonymization — structural patterns per ADR 0047 + Issue #49
# --------------------------------------------------------------------------
#
# These patterns detect the editorial-convention shape that publishers use
# to brand their reference works. The alternation tokens (Encyclopedia,
# Dictionary, Companion, Handbook, Reference, Compendium) are descriptors
# of reference-work TYPES — not publisher names. The patterns fire on the
# structural shape, never on enumerated publisher tokens. This preserves
# the ADR 0047 decision 4 parametric-knowledge boundary at the project's
# own config / code layer: no source-identity tokens are embedded here.
#
# Three primitives:
#
# 1. PUBLICATION_NAME_PATTERN — matches a whole title that IS a publication
#    name (e.g., the candidate "<Publisher> Encyclopedia of <Domain>"
#    arriving from /Title metadata when the source was a single-entry
#    export of a book). detect_title rejects matches and falls through to
#    the heading chain.
#
# 2. PUBLICATION_NAME_PATTERN_CONCATENATED — sibling pattern that catches
#    the same shape when source typography strips whitespace from page-
#    header runners (the pattern ingests PDFs that emit "FoobarDictionaryof
#    Philosophy"-style concatenated forms in their first-line page headers).
#    Used by the heading-emit anonymization filter and by the partition-
#    layer defense-in-depth filter.
#
# 3. PUBLICATION_NAME_SUFFIX_STRIPPER — strips a trailing publication-name
#    suffix from a title (e.g., "Foundationalism — Acme Encyclopedia of
#    Philosophy" -> "Foundationalism"). Subsumes the previously-enumerated
#    per-publisher patterns in ENCYCLOPEDIA_CONFIG. Recognized separators:
#    parentheses, pipes, hyphens, em-dashes, colons.

_PUBLICATION_TYPE_TOKENS = (
    r"(?:Encyclopedia|Dictionary|Companion|Handbook|Reference|Compendium)"
)
_PUBLICATION_PREPOSITION = r"(?:of|to)"

PUBLICATION_NAME_PATTERN = re.compile(
    rf"^(.+?)\s+{_PUBLICATION_TYPE_TOKENS}\s+{_PUBLICATION_PREPOSITION}\s+(.+)$",
    re.IGNORECASE,
)

PUBLICATION_NAME_PATTERN_CONCATENATED = re.compile(
    rf"{_PUBLICATION_TYPE_TOKENS}{_PUBLICATION_PREPOSITION}",
    re.IGNORECASE,
)

PUBLICATION_NAME_SUFFIX_STRIPPER = re.compile(
    rf"\s*[\(\|\-—:]+\s*[^()|\-—:]+?\s+{_PUBLICATION_TYPE_TOKENS}"
    rf"\s+{_PUBLICATION_PREPOSITION}\s+[^()|]+\)?\s*$",
    re.IGNORECASE,
)


def is_publication_name_shaped(text: str) -> bool:
    """Return True when text matches the publication-name structural shape.

    Tests against both the whole-line pattern (for properly-spaced
    candidates) and the concatenated-form sibling (for sources whose
    page-header runners or metadata strip whitespace). Either match
    returns True.

    The function is the gate used by:
      - detect_title (rejects the candidate and falls through)
      - PDFInputAdapter._emit_page_header_headings (skips the page)
      - extract_entries via partition filter (drops the partition)

    Anti-false-positive: matches the EDITORIAL-CONVENTION shape (a
    capitalized noun phrase + reference-work type token + preposition +
    another noun phrase). Bare body-context mentions like "Acme Platonism"
    or "compendium of arguments" do not match because the structural
    pattern requires the type token to be capitalized AND surrounded by
    the editorial preposition shape; the lowercase "compendium of" form
    is rejected by the title-shape regex.
    """
    if not text:
        return False
    if PUBLICATION_NAME_PATTERN.match(text.strip()):
        return True
    if PUBLICATION_NAME_PATTERN_CONCATENATED.search(text):
        return True
    return False


def strip_publication_name_suffix(title: str) -> str:
    """Return title with any trailing publication-name suffix removed.

    Applies PUBLICATION_NAME_SUFFIX_STRIPPER against title; returns the
    title with the matched suffix (and its preceding separator) stripped.
    Returns the title unchanged when no match.

    Examples:
      "Foundationalism — Acme Encyclopedia of Philosophy" -> "Foundationalism"
      "Foundationalism (Synthetic Encyclopedia of History)" -> "Foundationalism"
      "Foundationalism | Generic Dictionary of Logic" -> "Foundationalism"
      "Foundationalism" -> "Foundationalism"
    """
    if not title:
        return title
    match = PUBLICATION_NAME_SUFFIX_STRIPPER.search(title)
    if match is None:
        return title
    return title[: match.start()].rstrip()


# Lines repeated identically across at least N pages are treated as page
# headers/footers and stripped from extracted text. 3 is conservative —
# legitimate body text rarely repeats verbatim across 3+ pages, while
# page boilerplate ("page N entry-name", copyright lines) is highly
# recurrent. Recall-prioritized: when in doubt, leave in.
PDF_PAGEHEADER_REPETITION_THRESHOLD = 3

# Junk-filter floor for /Title metadata. Titles shorter than this are
# almost always artifacts (empty strings, single chars), not editorial.
PDF_TITLE_MIN_LENGTH = 3

# Reject slugs that are pure-numeric or positional pointers — textual
# cross-reference markers like "See: above" or "See also: 12, 14" are
# editorial conveniences that slugify into useless graph signal. The
# slug-quality filter rejects them at emission time so the brief carries
# only candidate entry IDs the LLM might recognize.
PDF_CROSSREF_SLUG_REJECT = frozenset(
    {
        "above",
        "below",
        "supra",
        "infra",
        "ibid",
        "id",
        "idem",
        "loc",
        "op",
        "cit",
        "ff",
        "et",
        "al",
        "see",
        "also",
    }
)

# Page-count caps for the slow per-page operations. PDFInputAdapter walks
# pages for char-level metadata (font-size analysis) and link annotations.
# Encyclopedia-scale PDFs (Routledge: 9169 pages, Cambridge: 1210, Oxford:
# 1076) make unbounded walks prohibitively slow under pdfplumber's pdfminer
# backend. The caps below are calibrated empirically: 30 sample pages
# starting after the front-matter establishes a stable body-vs-heading
# typography signal in well-edited reference works (which is what the
# class-boundary in ADR 0046 selects for); 500 pages of annotation walk
# captures editorial cross-link inventories that, in published volumes,
# concentrate near the document's TOC/index rather than spreading evenly.
# Both caps trade some recall for tractability — false negatives surface
# as fewer cross-references in late-document entries, which the LLM triage
# absorbs via its parametric-knowledge boundary per ADR 0047 decision 4.
PDF_FONT_SAMPLE_PAGE_COUNT = 30
PDF_FONT_SAMPLE_SKIP_FRONT = 10
PDF_ANNOT_PAGE_CAP = 500

# Hard cap on the per-page char walks during font-size heading emission.
# Without this, encyclopedia-scale PDFs (Cambridge: 1210 pages, Oxford:
# 1076 pages) take 3-5 minutes per extraction. The cap balances coverage
# (most reference PDFs have entries within the first ~1500 content pages)
# against iteration speed. Routledge avoids this entirely via the outline
# short-circuit (outline_count >= 50 returns before font-size analysis runs).
PDF_FONT_EMIT_PAGE_CAP = 500

# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class StructuralElement:
    """Adapter-normalized representation of one structural element.

    Adapters convert source-format-specific markup into StructuralElement
    records the structural detectors consume. Detectors operate on lists
    of these records, not on raw markup; this is what keeps the detectors
    pure and source-format-agnostic.

    Fields:
        kind: One of {"heading", "anchor", "paragraph", "list_item",
            "title"}. Kinds the detectors recognize.
        text: Stripped text content of the element.
        attributes: Element-specific attributes — href for anchors,
            level (1-6) for headings, etc. Stored as str-keyed str values
            for JSON-roundtripping ease.
        position: Zero-indexed ordinal position in source order. Used
            for adjacency reasoning by the section-path detector.
    """

    kind: str
    text: str
    attributes: dict[str, str]
    position: int


@dataclass(frozen=True)
class AdapterOutput:
    """Adapter-produced normalized representation of a source document.

    Adapters return AdapterOutput; structural detectors consume it.
    The shape decouples source-format parsing (in adapters) from
    structural reasoning (in detectors), so a new source format requires
    only a new adapter, not detector changes.

    Fields:
        source_path: The path the caller passed, retained for the brief.
        document_type: The DOCUMENT_TYPE_REGISTRY key in force for this
            run, retained for the brief.
        elements: Source-order list of StructuralElement records.
        source_url: Canonical URL of the source if known (extracted by
            the adapter from <link rel="canonical"> or similar). None
            if the adapter cannot determine it.
        full_text: Stripped concatenated text from the source, used for
            word-count estimation. Adapters strip markup; detectors do
            not need to.
    """

    source_path: str
    document_type: str
    elements: list[StructuralElement]
    source_url: str | None
    full_text: str


@dataclass(frozen=True)
class Entry:
    """One entry surfaced from a structural reference.

    An Entry is one row in the focusing brief. The fields are the
    graph-shape signal the LLM triage consumes; source prose is
    deliberately not represented here per ADR 0047 (section
    "Non-responsibilities" above) and ADR 0011.

    Fields:
        title: The entry's title (extracted by the title detector).
        entry_id: A slug or identifier derived from the title or URL,
            used to key cross-reference adjacency.
        cross_references: Other entry_ids the entry cross-references.
            Recall-prioritized: the parser surfaces all candidate
            cross-references; the LLM triage rejects ones not in
            parametric knowledge.
        section_path: Topical category from the source's TOC ancestry
            if available; None when the adapter cannot determine it.
        word_count: Approximate word count of the entry's prose,
            estimated from CHARS_PER_WORD_APPROX.
        source_url: Canonical URL of the entry if known.
        extraction_confidence: Coarse 0.0–1.0 score reflecting how many
            of the expected structural cues the parser found. The LLM
            triage uses this as a tiebreaker, not as a primary signal.
    """

    title: str
    entry_id: str
    cross_references: list[str]
    section_path: str | None
    word_count: int
    source_url: str | None
    extraction_confidence: float


@dataclass(frozen=True)
class FocusingBrief:
    """JSON-serializable focusing brief — the parser's output artifact.

    A FocusingBrief is what the LLM triage prompt consumes per ADR 0047.
    The brief is deliberately small (~one entry per source page in the
    SEP / IEP shape) and carries graph-shape facts only. The brief is
    discarded after triage; persistence beyond the named output path is
    explicitly out-of-scope per ADR 0047.

    Fields:
        source_path: Echoes the AdapterOutput field for traceability.
        document_type: Echoes the AdapterOutput field.
        parser_version: PARSER_VERSION constant in force at generation.
        generated_at: ISO-8601 UTC timestamp of brief generation. The
            only non-deterministic field; two runs against identical
            source bytes produce identical briefs modulo this field.
        entries: List of Entry records.
    """

    source_path: str
    document_type: str
    parser_version: str
    generated_at: str
    entries: list[Entry]


# --------------------------------------------------------------------------
# InputAdapter interface and HTMLInputAdapter implementation
# --------------------------------------------------------------------------


class InputAdapter(ABC):
    """Abstract input adapter — converts a source file to AdapterOutput.

    Concrete adapters subclass this and implement extract(). New source
    formats add a subclass and register in ADAPTER_REGISTRY. Per ADR 0047
    (decision 2), the architecture is one parser, multiple adapters
    sharing the structural-detector layer.

    Subclass responsibilities:
        - Read the source file at the given path.
        - Strip source-format-specific markup.
        - Produce StructuralElement records in source order.
        - Extract canonical URL if the format supports it.
        - Produce stripped full_text for word-count estimation.
        - Raise FileNotFoundError if the path does not exist.
        - Raise ValueError if the source is malformed beyond recovery.
    """

    @abstractmethod
    def extract(self, source_path: Path, document_type: str) -> AdapterOutput:
        """Extract AdapterOutput from the source at source_path."""


class HTMLInputAdapter(InputAdapter):
    """HTML input adapter — handles SEP- and IEP-shaped HTML.

    Uses BeautifulSoup4 (bs4) for HTML parsing. The adapter normalizes
    HTML markup into StructuralElement records:

    - <title> → StructuralElement(kind="title", ...)
    - <h1>..<h6> → StructuralElement(kind="heading",
        attributes={"level": "1"}, ...)
    - <a href="..."> → StructuralElement(kind="anchor",
        attributes={"href": ...}, ...)
    - <p> → StructuralElement(kind="paragraph", ...)
    - <li> → StructuralElement(kind="list_item", ...)

    Canonical URL extraction: looks for <link rel="canonical" href="...">
    in <head>, then <meta property="og:url" content="...">, then None.

    Edge cases handled:
        - HTML with multiple <h1> elements: all returned; the first is
          the entry's primary title.
        - HTML with no <title>: handled — the title detector falls back
          to the first <h1>.
        - Anchors with no href or empty href: dropped (not surfaced as
          cross-references).
        - Anchors whose href is a fragment-only reference (#section):
          dropped.
        - Empty body: returns AdapterOutput with empty elements list and
          empty full_text (the entry detector then surfaces no entries).

    Non-responsibilities:
        - No JavaScript execution. Server-rendered HTML only.
        - No external-resource fetching. The adapter does not follow
          links or load images.
        - No HTML repair beyond what bs4's html.parser does. Malformed
          HTML beyond bs4's recovery raises ValueError.
    """

    def extract(self, source_path: Path, document_type: str) -> AdapterOutput:
        if not source_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {source_path}")

        try:
            from bs4 import BeautifulSoup
        except ImportError as exc:
            raise ImportError(
                "beautifulsoup4 is required for HTMLInputAdapter; "
                "run `pip install -r engine/tools/requirements.txt`"
            ) from exc

        html_bytes = source_path.read_bytes()
        soup = BeautifulSoup(html_bytes, "html.parser")

        elements: list[StructuralElement] = []
        position = 0

        title_tag = soup.find("title")
        if title_tag is not None and title_tag.string is not None:
            elements.append(
                StructuralElement(
                    kind="title",
                    text=title_tag.get_text(strip=True),
                    attributes={},
                    position=position,
                )
            )
            position += 1

        body = soup.find("body") or soup
        for tag in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "a", "p", "li"]):
            tag_name = tag.name
            text = tag.get_text(strip=True)
            attrs: dict[str, str] = {}
            if tag_name and tag_name.startswith("h") and len(tag_name) == 2:
                kind = "heading"
                attrs["level"] = tag_name[1]
            elif tag_name == "a":
                kind = "anchor"
                href_value = tag.get("href")
                if not href_value or not isinstance(href_value, str):
                    continue
                href_stripped = href_value.strip()
                if not href_stripped or href_stripped.startswith("#"):
                    continue
                attrs["href"] = href_stripped
            elif tag_name == "p":
                kind = "paragraph"
            elif tag_name == "li":
                kind = "list_item"
            else:
                continue
            elements.append(
                StructuralElement(
                    kind=kind, text=text, attributes=attrs, position=position
                )
            )
            position += 1

        source_url: str | None = None
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if canonical is not None:
            href_value = canonical.get("href")
            if isinstance(href_value, str) and href_value.strip():
                source_url = href_value.strip()
        if source_url is None:
            og_url = soup.find("meta", attrs={"property": "og:url"})
            if og_url is not None:
                content_value = og_url.get("content")
                if isinstance(content_value, str) and content_value.strip():
                    source_url = content_value.strip()

        full_text = soup.get_text(separator=" ", strip=True)

        return AdapterOutput(
            source_path=str(source_path),
            document_type=document_type,
            elements=elements,
            source_url=source_url,
            full_text=full_text,
        )


class PDFInputAdapter(InputAdapter):
    """PDF input adapter — source-agnostic, multi-fallback per ADR 0047 + Issue #34.

    Authored under the source-agnostic posture: no per-source code branches.
    Every PDF the user feeds in is parsed by the same code path; per-source
    idiosyncrasies (Routledge's outline-as-entry-inventory shape, Cambridge's
    book-section-only outline + font-size-driven entries, Oxford's letter-
    section outline + font-size-driven entries) are absorbed by multi-layer
    fallbacks below, not by branching.

    Detector contract (mirrors HTMLInputAdapter; only title/heading/anchor
    element kinds are produced because the downstream detector layer at
    lines 509+ consumes only those three):

    - title elements: at most one. (1) /Title metadata if non-empty and
      passes the junk-filter (>=PDF_TITLE_MIN_LENGTH chars, not all-digits).
      (2) First-page largest-font contiguous text run.
    - heading elements: union of three layers, recall-prioritized.
      (1) Outline tree via pdf.doc.get_outlines() — yields (level, title)
          tuples; emit one heading per outline entry with attributes.level
          set to str(level). The outline fragments below the document root
          are 1-indexed.
      (2) Font-size buckets when outline is empty / shallow / single-level.
          Bucket all chars by (rounded-size, fontname); rank descending by
          char-count is wrong here — rank by SIZE (largest first); top-N
          buckets become levels 1..N. Within each bucket, contiguous
          per-page char runs become heading elements.
      (3) Text-pattern heuristics layered on top: lines matching
          ^(Chapter|Section|Part|Article)\\s+[\\dIVX]+ or all-caps single
          lines 5..80 chars long get emitted as level-1 headings. Layer
          (3) is purely additive over (1) + (2); duplicates are tolerated
          because the downstream partition logic deduplicates by text.
    - anchor elements: union of two paths, both emitting hrefs in the
      canonical form internal:<slug>.
      (a) Link annotations via page.annots — Link-subtype annotations
          with URI or GoTo named-destination actions.
      (b) Textual editorial-convention markers via PDF_TEXT_CROSSREF_PATTERNS
          regex-scanned over full_text.
      Both paths emit href="internal:<slug>" so the universal pattern
      r"^internal:([a-z0-9][a-z0-9\\-]*)$" added to ENCYCLOPEDIA_CONFIG
      picks up cross-references uniformly.
    - source_url: pdf.metadata["Subject"] if URL-shaped; else None.
    - full_text: concatenated page.extract_text() across all pages, with
      page-header/footer stripping (lines repeated identically across
      >=PDF_PAGEHEADER_REPETITION_THRESHOLD pages removed).

    Failure modes:
        - Source path missing: FileNotFoundError.
        - Image-only / scanned PDF (zero text extracted): ValueError —
          fail loud rather than silently produce a zero-entry brief.
          OCR is the user's prep responsibility.
        - Malformed PDF beyond pdfplumber recovery: ValueError.
    """

    def extract(self, source_path: Path, document_type: str) -> AdapterOutput:
        if not source_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {source_path}")

        try:
            import pdfplumber  # type: ignore[import-not-found,unused-ignore]
            import pypdfium2 as pdfium  # type: ignore[import-untyped,import-not-found,unused-ignore]
        except ImportError as exc:
            raise ImportError(
                "pdfplumber and pypdfium2 are required for PDFInputAdapter; "
                "run `pip install -r engine/tools/requirements.txt`"
            ) from exc

        # Bulk text extraction via pypdfium2 — empirically ~30x faster than
        # pdfplumber's pdfminer-backed extract_text() at encyclopedia scale
        # (Routledge 9169 pages: ~75s vs many minutes).
        try:
            pdfium_doc = pdfium.PdfDocument(source_path)
        except Exception as exc:
            raise ValueError(
                f"Failed to open PDF {source_path} via pypdfium2: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        try:
            pages_text = self._extract_per_page_text_pypdfium(pdfium_doc)
            outline_entries = self._collect_pypdfium_outline(pdfium_doc)
        finally:
            pdfium_doc.close()

        pages_text = self._strip_repeating_page_boilerplate(pages_text)
        full_text = " ".join(t for t in pages_text if t)

        if not full_text.strip():
            raise ValueError(
                f"PDF {source_path} has no extractable text layer; "
                "OCR required before parsing"
            )

        # Structural metadata (outline, chars, annotations, doc metadata)
        # via pdfplumber — pypdfium2 doesn't expose these in the same way.
        try:
            pdf_ctx = pdfplumber.open(source_path)
        except Exception as exc:
            raise ValueError(
                f"Failed to open PDF {source_path} via pdfplumber: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        with pdf_ctx as pdf:
            elements: list[StructuralElement] = []
            position_counter = [0]

            self._emit_title_element(pdf, elements, position_counter)
            self._emit_outline_headings_from_toc(
                outline_entries, elements, position_counter
            )
            self._emit_font_size_headings(pdf, elements, position_counter)
            # Third-tier detector — fires only when outline tree is sparse
            # (< 50 headings) AND font-size analysis didn't supply enough
            # heading inventory to characterize the source. Source-agnostic
            # by structural shape; anonymization filter applied at emit-
            # time so publication-name-shaped runners cannot leak through.
            self._emit_page_header_headings(pages_text, elements, position_counter)
            self._emit_text_pattern_headings(full_text, elements, position_counter)
            self._emit_link_annotation_anchors(pdf, elements, position_counter)
            self._emit_textual_crossref_anchors(full_text, elements, position_counter)

            source_url = self._extract_source_url(pdf)

        # Reorder elements by document position. Heading and anchor emitters
        # write to disjoint position ranges (headings first, anchors last)
        # because they're invoked sequentially. That ordering would partition
        # all cross-references into the last entry — every entry except the
        # final one would have zero cross_references. Reordering by where
        # each element appears in full_text restores source-order interleaving
        # so partition_at_entry_boundaries() distributes cross-refs correctly.
        elements = self._reorder_elements_by_full_text_offset(elements, full_text)

        return AdapterOutput(
            source_path=str(source_path),
            document_type=document_type,
            elements=elements,
            source_url=source_url,
            full_text=full_text,
        )

    @staticmethod
    def _extract_per_page_text_pypdfium(pdfium_doc: Any) -> list[str]:
        out: list[str] = []
        for page in pdfium_doc:
            try:
                textpage = page.get_textpage()
                text = textpage.get_text_range() or ""
                textpage.close()
            except Exception:
                text = ""
            finally:
                page.close()
            out.append(text)
        return out

    @staticmethod
    def _collect_pypdfium_outline(pdfium_doc: Any) -> list[tuple[int, str]]:
        """Return [(level, title), ...] from the PDF outline tree.

        Uses pypdfium2's get_toc() which is non-recursive — pdfminer's
        get_outlines() recurses sibling-by-sibling and blows the default
        1000-deep recursion limit on encyclopedia-scale outlines (Routledge:
        2041 entries). Levels are 0-indexed at the root in pypdfium2; we
        bump by one so the heading-level model (1-indexed, 1..6) lines up
        with HTML's h1..h6 abstraction.
        """
        out: list[tuple[int, str]] = []
        try:
            for bookmark in pdfium_doc.get_toc():
                try:
                    title = bookmark.get_title() or ""
                except Exception:
                    continue
                level = max(1, min(6, int(getattr(bookmark, "level", 0)) + 1))
                if title:
                    out.append((level, title))
        except Exception:
            pass
        return out

    @staticmethod
    def _strip_repeating_page_boilerplate(pages_text: list[str]) -> list[str]:
        if len(pages_text) < PDF_PAGEHEADER_REPETITION_THRESHOLD:
            return pages_text
        line_page_counts: dict[str, int] = {}
        per_page_lines: list[list[str]] = []
        for txt in pages_text:
            lines = [ln.strip() for ln in txt.split("\n") if ln.strip()]
            per_page_lines.append(lines)
            for ln in set(lines):
                line_page_counts[ln] = line_page_counts.get(ln, 0) + 1
        boilerplate = {
            ln
            for ln, count in line_page_counts.items()
            if count >= PDF_PAGEHEADER_REPETITION_THRESHOLD
        }
        if not boilerplate:
            return pages_text
        cleaned: list[str] = []
        for lines in per_page_lines:
            kept = [ln for ln in lines if ln not in boilerplate]
            cleaned.append("\n".join(kept))
        return cleaned

    @staticmethod
    def _emit_title_element(
        pdf: Any, elements: list[StructuralElement], pos: list[int]
    ) -> None:
        meta = pdf.metadata or {}
        title_raw = meta.get("Title")
        if isinstance(title_raw, bytes):
            try:
                title_raw = title_raw.decode("utf-8", errors="replace")
            except Exception:
                title_raw = ""
        title_str = (title_raw or "").strip() if isinstance(title_raw, str) else ""
        if (
            title_str
            and len(title_str) >= PDF_TITLE_MIN_LENGTH
            and not title_str.isdigit()
            and not re.search(r"\.(indd|docx|pdf|tex)$", title_str, re.IGNORECASE)
        ):
            elements.append(
                StructuralElement(
                    kind="title", text=title_str, attributes={}, position=pos[0]
                )
            )
            pos[0] += 1
            return

        if not pdf.pages:
            return
        # Walk first few pages until we find one with chars — some PDFs
        # have an image-only cover page, then content begins on later pages.
        chars: list[Any] = []
        for page in pdf.pages[:5]:
            try:
                page_chars = list(page.chars[:5000])
            except Exception:
                continue
            if page_chars:
                chars = page_chars
                break
        if not chars:
            return
        size_groups: dict[float, list[Any]] = {}
        for ch in chars:
            size = round(ch.get("size", 0), 1)
            size_groups.setdefault(size, []).append(ch)
        if not size_groups:
            return
        largest_size = max(size_groups.keys())
        largest_chars = size_groups[largest_size]
        text_run = "".join(ch.get("text", "") for ch in largest_chars[:200]).strip()
        if text_run and len(text_run) >= PDF_TITLE_MIN_LENGTH:
            elements.append(
                StructuralElement(
                    kind="title",
                    text=text_run[:200],
                    attributes={},
                    position=pos[0],
                )
            )
            pos[0] += 1

    @staticmethod
    def _emit_outline_headings_from_toc(
        outline_entries: list[tuple[int, str]],
        elements: list[StructuralElement],
        pos: list[int],
    ) -> None:
        for level, title in outline_entries:
            cleaned = title.strip()
            cleaned = re.sub(
                r"\.(pdf|html?|txt|docx?)$", "", cleaned, flags=re.IGNORECASE
            )
            cleaned = cleaned.strip()
            if not cleaned:
                continue
            elements.append(
                StructuralElement(
                    kind="heading",
                    text=cleaned,
                    attributes={"level": str(level)},
                    position=pos[0],
                )
            )
            pos[0] += 1

    @staticmethod
    def _emit_font_size_headings(
        pdf: Any, elements: list[StructuralElement], pos: list[int]
    ) -> None:
        # Skip font-size analysis when the outline already provides ample
        # heading inventory. The threshold (50) is conservative: outlines with
        # only book sections (Cambridge: 12 entries) still trigger font-size
        # analysis to find the actual entry-level headings.
        outline_count = sum(1 for e in elements if e.kind == "heading")
        if outline_count >= 50:
            return

        # Phase 1: bucket fonts on a sample of pages — typography is consistent
        # across well-edited reference works, so a sample suffices to identify
        # which (rounded-size) buckets are heading-sized vs body-sized.
        size_char_counts: dict[float, int] = {}
        skip = PDF_FONT_SAMPLE_SKIP_FRONT
        end = skip + PDF_FONT_SAMPLE_PAGE_COUNT
        sample_pages = pdf.pages[skip:end] if len(pdf.pages) > end else pdf.pages[skip:]
        if len(sample_pages) < 3:
            sample_pages = pdf.pages[: min(len(pdf.pages), PDF_FONT_SAMPLE_PAGE_COUNT)]
        for page in sample_pages:
            try:
                for ch in page.chars[:5000]:
                    size = round(ch.get("size", 0), 1)
                    size_char_counts[size] = size_char_counts.get(size, 0) + 1
            except Exception:
                continue
        if not size_char_counts:
            return

        ranked_sizes = sorted(
            (
                s
                for s, n in size_char_counts.items()
                if n >= PDF_HEADING_FONT_MIN_BUCKET_CHARS
            ),
            reverse=True,
        )
        if len(ranked_sizes) <= 1:
            return
        body_size = max(size_char_counts.items(), key=lambda kv: kv[1])[0]
        heading_sizes = [s for s in ranked_sizes if s > body_size][
            :PDF_HEADING_FONT_BUCKET_COUNT
        ]
        if not heading_sizes:
            return
        size_to_level = {s: i + 1 for i, s in enumerate(heading_sizes)}

        # Phase 2: emit headings by walking pages within the cap. Cambridge's
        # entries start mid-volume; sample-only emission would miss them, so
        # we walk further than the bucketing sample, but not unboundedly —
        # encyclopedia-scale PDFs without per-source caps take 3-5 minutes.
        # Routledge avoids this path entirely via the outline short-circuit.
        emit_pages = (
            pdf.pages[:PDF_FONT_EMIT_PAGE_CAP]
            if len(pdf.pages) > PDF_FONT_EMIT_PAGE_CAP
            else pdf.pages
        )
        for page in emit_pages:
            try:
                chars = page.chars
            except Exception:
                continue
            current_run_chars: list[str] = []
            current_run_size: float | None = None
            for ch in chars:
                size = round(ch.get("size", 0), 1)
                text_ch = ch.get("text", "")
                if size in size_to_level:
                    if size != current_run_size and current_run_chars:
                        PDFInputAdapter._flush_heading_run(
                            current_run_chars,
                            current_run_size,
                            size_to_level,
                            elements,
                            pos,
                        )
                        current_run_chars = []
                    current_run_size = size
                    current_run_chars.append(text_ch)
                else:
                    if current_run_chars:
                        PDFInputAdapter._flush_heading_run(
                            current_run_chars,
                            current_run_size,
                            size_to_level,
                            elements,
                            pos,
                        )
                        current_run_chars = []
                        current_run_size = None
            if current_run_chars:
                PDFInputAdapter._flush_heading_run(
                    current_run_chars,
                    current_run_size,
                    size_to_level,
                    elements,
                    pos,
                )

    @staticmethod
    def _flush_heading_run(
        chars: list[str],
        size: float | None,
        size_to_level: dict[float, int],
        elements: list[StructuralElement],
        pos: list[int],
    ) -> None:
        if size is None or size not in size_to_level:
            return
        text = "".join(chars).strip()
        if len(text) < 3 or len(text) > 200:
            return
        level = size_to_level[size]
        elements.append(
            StructuralElement(
                kind="heading",
                text=text,
                attributes={"level": str(level)},
                position=pos[0],
            )
        )
        pos[0] += 1

    @staticmethod
    def _emit_page_header_headings(
        pages_text: list[str],
        elements: list[StructuralElement],
        pos: list[int],
    ) -> None:
        """Emit headings derived from page-header runners.

        Third-tier detector for the structural class characterized by body-
        font entries with page-header runners as the only entry indicator
        (entries do not stand out in the outline tree, do not stand out in
        font-size analysis, but consistently appear in each page's first
        non-empty line as "<first-entry-on-page> <last-entry-on-page>" or
        a concatenated form). Per ADR 0047 decision 1 the path is source-
        agnostic — gating decisions and shape predicates fire on structural
        signals alone.

        Anonymization filter (load-bearing per Issue #49 + Issue #48 cross-
        deliverable invariant): page-header runners commonly carry the
        publication name on alternating pages (standard typography). Lines
        matching `is_publication_name_shaped()` are skipped entirely so
        they cannot leak through to entry titles via the partitioning
        path. Per-token re-check after splitting catches the case where
        the whole-line match misses but a token preserves the
        concatenated-shape signature.

        Outline-count gating mirrors `_emit_font_size_headings()`: when
        the outline tree already supplies ample heading inventory
        (>= 50 entries, the same threshold), this path returns early
        because the outline is authoritative.

        Page-header-shape predicate: line is short (under 80 chars), all-
        caps OR title-case, lacks terminal punctuation, distinct from
        body content. Concatenated-token sources fall through to a case-
        transition-based split helper.
        """
        outline_count = sum(1 for e in elements if e.kind == "heading")
        if outline_count >= 50:
            return
        seen_text: set[str] = {e.text for e in elements if e.kind == "heading"}
        for page_text in pages_text:
            if not page_text:
                continue
            stripped_page = page_text.strip()
            if not stripped_page:
                continue
            first_line = stripped_page.split("\n", 1)[0].strip()
            if not first_line:
                continue
            if is_publication_name_shaped(first_line):
                continue
            if not PDFInputAdapter._is_page_header_shaped(first_line, page_text):
                continue
            tokens = first_line.split()
            if len(tokens) == 1:
                tokens = PDFInputAdapter._split_camel_concat(first_line)
            tokens = [t.strip() for t in tokens if t.strip()]
            if not tokens:
                continue
            if any(is_publication_name_shaped(t) for t in tokens):
                continue
            for token in tokens:
                if len(token) < 2 or len(token) > 80:
                    continue
                if token in seen_text:
                    continue
                seen_text.add(token)
                elements.append(
                    StructuralElement(
                        kind="heading",
                        text=token,
                        attributes={"level": "1"},
                        position=pos[0],
                    )
                )
                pos[0] += 1

    @staticmethod
    def _is_page_header_shaped(line: str, page_text: str) -> bool:
        """Return True when line shape is consistent with a page-header runner.

        Page-header runners are short, capitalized, free of terminal
        sentence punctuation, and distinct from body content. The
        predicate is recall-prioritized — it accepts any line that
        could plausibly be a runner; downstream filtering (publication-
        name structural patterns, partition-layer rejection) handles
        false positives.
        """
        if not line:
            return False
        if len(line) > 80:
            return False
        if line[-1:] in {".", "?", "!", ","}:
            return False
        # Reject if the line is purely lowercase (sentence-case body lines).
        # Allow all-uppercase OR mixed-case-with-uppercase-anywhere; reject
        # purely-lowercase noise. Title-case detection is handled by the
        # presence of any uppercase letter.
        if not any(c.isupper() for c in line):
            return False
        # Reject pure digits / pure punctuation lines.
        if not any(c.isalpha() for c in line):
            return False
        # Distinct from body content: the line should not appear verbatim
        # later in the same page's body (which would suggest it is body
        # text repeated rather than a header runner).
        page_body = page_text.split("\n", 1)[1] if "\n" in page_text else ""
        if page_body and line in page_body:
            return False
        return True

    @staticmethod
    def _split_camel_concat(text: str) -> list[str]:
        """Split a concatenated-token string on case-transition boundaries.

        Sources that strip whitespace from page-header runners produce
        forms like "FoundationalismCoherentism" or "AbrabanelJudahabstractentity".
        The split heuristic recovers tokens by inserting a boundary
        wherever a lowercase character is followed by an uppercase, and
        wherever an uppercase run transitions to a Title-cased word.

        Returns the list of recovered tokens; falls back to [text] when
        no case-transition boundary is found.
        """
        if not text:
            return []
        boundaries: list[int] = [0]
        for i in range(1, len(text)):
            prev = text[i - 1]
            cur = text[i]
            if prev.islower() and cur.isupper():
                boundaries.append(i)
            elif (
                prev.isupper()
                and cur.isupper()
                and i + 1 < len(text)
                and text[i + 1].islower()
            ):
                boundaries.append(i)
        boundaries.append(len(text))
        tokens: list[str] = []
        for j in range(len(boundaries) - 1):
            chunk = text[boundaries[j] : boundaries[j + 1]]
            if chunk:
                tokens.append(chunk)
        return tokens or [text]

    @staticmethod
    def _emit_text_pattern_headings(
        full_text: str, elements: list[StructuralElement], pos: list[int]
    ) -> None:
        """Emit explicit Chapter / Section / Part / Article markers as headings.

        Recall-prioritized but precision-bounded: only matches editorial
        conventions that are unambiguously chapter markers. Earlier
        iterations included an all-caps detector for "BIBLIOGRAPHY" /
        "PRELIMINARIES" style headings, but that turned out to be noise-
        dominant on real reference works — author bylines like "DANIEL B.
        STEVENSON" or "BARRY HALLEN" are syntactically indistinguishable
        from section headings without semantic knowledge. PDFs that
        genuinely lack outline AND distinct font sizes for headings will
        produce empty heading lists from this layer; the LLM triage's
        parametric-knowledge boundary handles the recall gap.
        """
        existing_heading_texts = {e.text for e in elements if e.kind == "heading"}
        for line in full_text.split("\n"):
            ln = line.strip()
            if not ln or ln in existing_heading_texts:
                continue
            # Real chapter headings are short and self-contained; body prose
            # like "Article 17 points out the need..." or "Chapter 14 of his
            # Proslogion in 1078" matches the pattern syntactically but is
            # mid-paragraph. Three filters: <=8 words, <=80 chars, AND the
            # word right after the chapter number is NOT a common prose
            # connector. Together they catch "Chapter 14: The Prerequisites
            # of Theory" (~6 words, ~38 chars, connector "The" follows ":")
            # while rejecting prose runs.
            if (
                len(ln) <= 80
                and len(ln.split()) <= 8
                and re.match(r"^(Chapter|Section|Part|Article)\s+[\dIVXLC]+\b", ln)
                and not re.search(
                    r"^(Chapter|Section|Part|Article)\s+[\dIVXLC]+\s+"
                    r"(of|in|on|by|to|from|with|points|says|argues|holds|notes)\b",
                    ln,
                    re.IGNORECASE,
                )
            ):
                elements.append(
                    StructuralElement(
                        kind="heading",
                        text=ln,
                        attributes={"level": "1"},
                        position=pos[0],
                    )
                )
                pos[0] += 1

    @staticmethod
    def _emit_link_annotation_anchors(
        pdf: Any, elements: list[StructuralElement], pos: list[int]
    ) -> None:
        cap = PDF_ANNOT_PAGE_CAP
        pages_to_walk = pdf.pages[:cap] if len(pdf.pages) > cap else pdf.pages
        for page in pages_to_walk:
            try:
                annots = page.annots or []
            except Exception:
                continue
            for annot in annots:
                data = annot.get("data") or {}
                if data.get("Subtype") != "Link":
                    continue
                a_action = data.get("A") or {}
                if not isinstance(a_action, dict):
                    continue
                slug: str | None = None
                action_kind = a_action.get("S")
                if action_kind == "URI":
                    uri = a_action.get("URI", "")
                    if isinstance(uri, bytes):
                        try:
                            uri = uri.decode("utf-8", errors="replace")
                        except Exception:
                            uri = ""
                    if isinstance(uri, str) and uri.strip():
                        url_match = re.search(
                            r"/([a-z0-9][a-z0-9\-_]+)/?(?:#.*)?$",
                            uri.rstrip("/"),
                            re.IGNORECASE,
                        )
                        if url_match is not None:
                            slug = slugify_title(url_match.group(1))
                elif action_kind == "GoTo":
                    dest = a_action.get("D")
                    if isinstance(dest, bytes):
                        try:
                            dest = dest.decode("utf-8", errors="replace")
                        except Exception:
                            dest = ""
                    if isinstance(dest, list) and dest:
                        dest = dest[0]
                        if isinstance(dest, bytes):
                            try:
                                dest = dest.decode("utf-8", errors="replace")
                            except Exception:
                                dest = ""
                    if isinstance(dest, str) and dest.strip():
                        slug = slugify_title(dest)
                if slug:
                    elements.append(
                        StructuralElement(
                            kind="anchor",
                            text="",
                            attributes={"href": f"internal:{slug}"},
                            position=pos[0],
                        )
                    )
                    pos[0] += 1

    @staticmethod
    def _emit_textual_crossref_anchors(
        full_text: str, elements: list[StructuralElement], pos: list[int]
    ) -> None:
        for pattern in PDF_TEXT_CROSSREF_PATTERNS:
            for match in re.finditer(pattern, full_text, re.IGNORECASE):
                captured = match.group(1)
                # Capture match start so the post-emission reorder pass can
                # interleave anchors with headings by document position.
                match_start = match.start()
                for segment in re.split(r"\s*,\s*|\s+and\s+", captured):
                    segment = segment.strip()
                    if not segment:
                        continue
                    slug = slugify_title(segment)
                    if not PDFInputAdapter._is_useful_crossref_slug(slug):
                        continue
                    elements.append(
                        StructuralElement(
                            kind="anchor",
                            text=segment,
                            attributes={
                                "href": f"internal:{slug}",
                                "_text_offset": str(match_start),
                            },
                            position=pos[0],
                        )
                    )
                    pos[0] += 1

    @staticmethod
    def _is_useful_crossref_slug(slug: str) -> bool:
        """Return True if the slug looks like a candidate concept identifier.

        Filters slugs that are pure-numeric, single-char, all-positional
        ("above" / "below"), or in the editorial-convenience reject set
        (PDF_CROSSREF_SLUG_REJECT). These end up in textual crossref captures
        from "See: above" / "(see 14)" / similar editorial references that
        carry no concept-identity signal.
        """
        if not slug or len(slug) < 2:
            return False
        if slug in PDF_CROSSREF_SLUG_REJECT:
            return False
        # Pure-numeric (after slugification, "14" stays "14", "12.3" → "12-3").
        # Reject slugs whose alpha-removed form equals the slug — meaning no
        # alphabetical content survives.
        alpha_removed = re.sub(r"[a-z]", "", slug)
        if alpha_removed == slug:
            return False
        return True

    @staticmethod
    def _reorder_elements_by_full_text_offset(
        elements: list[StructuralElement], full_text: str
    ) -> list[StructuralElement]:
        """Sort elements by their first-occurrence offset in full_text.

        Headings and anchors are emitted by separate phases that don't share
        a position scale; without this pass, all anchors land at the end and
        partition_at_entry_boundaries() concentrates them into the final
        entry. The reorder uses:

        - title element: offset 0 (always at the document start)
        - heading element: first occurrence of e.text in full_text, scanned
          forward from a monotonically-advancing pointer so consecutive
          headings (which arrive in document order from outline / font-size
          / text-pattern phases) stay in document order
        - anchor element: the regex match.start() captured during textual
          crossref emission; link-annotation anchors lack a full_text offset
          and fall back to a placeholder near the end (acceptable because
          link annotations were absent in all three S-0096 test PDFs and
          the architecture treats the textual path as primary)
        """
        if not elements:
            return elements

        offsets: list[int] = []
        heading_pointer = 0
        for element in elements:
            if element.kind == "title":
                offsets.append(0)
                continue
            if element.kind == "heading":
                if not element.text:
                    offsets.append(heading_pointer)
                    continue
                idx = full_text.find(element.text, heading_pointer)
                if idx == -1:
                    # Heading text not found from current pointer onward;
                    # fall back to a global search before giving up. If the
                    # document orders match (typical for outline-driven
                    # encyclopedias), this branch is rarely entered.
                    idx = full_text.find(element.text)
                    if idx == -1:
                        offsets.append(heading_pointer)
                        continue
                offsets.append(idx)
                heading_pointer = idx + len(element.text)
                continue
            if element.kind == "anchor":
                offset_str = element.attributes.get("_text_offset", "")
                try:
                    offsets.append(int(offset_str))
                except (TypeError, ValueError):
                    offsets.append(len(full_text))
                continue
            offsets.append(heading_pointer)

        # Stable sort preserves emission order within ties (e.g., multiple
        # anchors at the same match.start() from a comma-separated list).
        indexed = sorted(
            enumerate(elements),
            key=lambda pair: (offsets[pair[0]], pair[0]),
        )
        # Strip the internal _text_offset attribute and renumber positions
        # so the returned elements match the public StructuralElement
        # contract (positions are sequential ordinals; attributes carry
        # only public keys like href / level).
        cleaned: list[StructuralElement] = []
        for new_pos, (_orig_idx, element) in enumerate(indexed):
            attrs = {
                k: v for k, v in element.attributes.items() if not k.startswith("_")
            }
            cleaned.append(
                StructuralElement(
                    kind=element.kind,
                    text=element.text,
                    attributes=attrs,
                    position=new_pos,
                )
            )
        return cleaned

    @staticmethod
    def _extract_source_url(pdf: Any) -> str | None:
        meta = pdf.metadata or {}
        subject = meta.get("Subject", "")
        if isinstance(subject, bytes):
            try:
                subject = subject.decode("utf-8", errors="replace")
            except Exception:
                subject = ""
        if isinstance(subject, str) and re.match(r"^https?://", subject.strip()):
            return subject.strip()
        return None


ADAPTER_REGISTRY: dict[str, type[InputAdapter]] = {
    ".html": HTMLInputAdapter,
    ".htm": HTMLInputAdapter,
    ".pdf": PDFInputAdapter,
}


def select_adapter(source_path: Path, override: str | None = None) -> InputAdapter:
    """Return the adapter for source_path, optionally forced by override.

    Resolves an InputAdapter subclass from ADAPTER_REGISTRY by file
    extension, or from override (an extension key like "html") if given.
    Instantiates and returns the adapter.

    Raises ValueError if no adapter matches.
    """
    if override is not None:
        key = override if override.startswith(".") else f".{override}"
        adapter_cls = ADAPTER_REGISTRY.get(key.lower())
        if adapter_cls is None:
            raise ValueError(
                f"No adapter registered for override={override!r}; "
                f"known: {sorted(ADAPTER_REGISTRY.keys())}"
            )
        return adapter_cls()
    suffix = source_path.suffix.lower()
    adapter_cls = ADAPTER_REGISTRY.get(suffix)
    if adapter_cls is None:
        raise ValueError(
            f"No adapter registered for extension {suffix!r}; "
            f"known: {sorted(ADAPTER_REGISTRY.keys())}"
        )
    return adapter_cls()


# --------------------------------------------------------------------------
# Pure structural detectors
# --------------------------------------------------------------------------
#
# Detectors consume AdapterOutput and produce structured findings. All
# detectors are pure functions: no I/O, deterministic, recall-prioritized
# per ADR 0047 (decision 3). Each detector handles one logical aspect of
# the entry-extraction task; the orchestrating extract_entries() composes
# them.


def detect_title(
    adapter_output: AdapterOutput, document_type_config: dict[str, Any] | None = None
) -> str | None:
    """Return the entry's primary title, or None if not detectable.

    Order of preference:
      1. The first <title> element, with structurally-detected
         publication-name suffix stripped via
         `strip_publication_name_suffix()` (e.g.,
         "Foundationalism — Acme Encyclopedia of Philosophy" yields
         "Foundationalism"). A non-empty stripped result wins; a result
         that strips to empty (the title was a bare publication name)
         falls through. A title that is itself a publication name
         (no separable suffix; the entire candidate matches
         `is_publication_name_shaped`) also falls through.
      2. The first <h1> heading.
      3. None when neither is present.

    The publication-name detection is structural — see the
    PUBLICATION_NAME_PATTERN family at module scope. The previous
    enumerated SEP / IEP per-publisher suffix patterns in
    ENCYCLOPEDIA_CONFIG were subsumed by the structural stripper at
    S-0103 per ADR 0047 decision 4 (Issue #49) so the project's own
    config layer holds the same parametric-knowledge boundary the brief
    output does. The `document_type_config` argument is preserved for
    interface compatibility with future per-type extensions.
    """
    del document_type_config  # accepted for interface compatibility; unused
    for element in adapter_output.elements:
        if element.kind == "title" and element.text:
            stripped = strip_publication_name_suffix(element.text).strip()
            if stripped and not is_publication_name_shaped(stripped):
                return stripped
    for element in adapter_output.elements:
        if (
            element.kind == "heading"
            and element.attributes.get("level") == "1"
            and element.text
        ):
            if is_publication_name_shaped(element.text):
                continue
            return element.text
    return None


def slugify_title(title: str) -> str:
    """Return a filesystem-safe slug for an entry title.

    Lowercases, replaces non-alphanumeric runs with single dashes,
    strips leading/trailing dashes. Used as the entry_id when the
    source URL does not provide one.

    Edge cases:
        - Empty input returns the empty string.
        - Inputs of only punctuation collapse to the empty string.
    """
    lowered = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug


def detect_entry_id(adapter_output: AdapterOutput, title: str | None) -> str:
    """Return a stable entry identifier.

    Order of preference:
      1. The slug from the source_url path (preferred — matches the
         source's own canonical identifier).
      2. The source_path file basename minus its extension (the natural
         convention when a user caches an entry as <slug>.html locally).
      3. The slugified title.
      4. The empty string (entry_id is best-effort; the title carries
         the human-readable signal).
    """
    if adapter_output.source_url is not None:
        url_match = re.search(
            r"/entries/([a-z0-9][a-z0-9\-]*)/?",
            adapter_output.source_url,
        )
        if url_match is not None:
            return url_match.group(1)
        url_match = re.search(
            r"/([a-z0-9][a-z0-9\-]*)/?$",
            adapter_output.source_url.rstrip("/"),
        )
        if url_match is not None:
            return url_match.group(1)
    if adapter_output.source_path:
        stem = Path(adapter_output.source_path).stem
        if stem and re.match(r"^[a-z][a-z0-9\-]*$", stem):
            return stem
    if title is not None:
        return slugify_title(title)
    return ""


def detect_cross_references(
    adapter_output: AdapterOutput, document_type_config: dict[str, Any]
) -> list[str]:
    """Return cross-reference entry_ids in source order, deduplicated.

    Walks all anchor elements and applies each cross_reference_pattern
    in the document-type config. The first matching pattern's capture
    group becomes the cross-reference entry_id.

    Recall-prioritized: matches all anchors against all patterns; the
    LLM triage downstream rejects entries it does not recognize.

    Edge cases:
        - Anchors with no matching pattern are dropped.
        - The same entry_id appearing multiple times is included once
          (first occurrence wins; subsequent are deduplicated).
        - Self-references (anchor pointing to the entry's own id) are
          included; deduplication occurs against the page's own
          entry_id by the orchestrator, not here.
    """
    patterns: list[re.Pattern[str]] = [
        re.compile(p) for p in document_type_config["cross_reference_patterns"]
    ]
    seen: set[str] = set()
    refs: list[str] = []
    for element in adapter_output.elements:
        if element.kind != "anchor":
            continue
        href = element.attributes.get("href", "")
        if not href:
            continue
        for pattern in patterns:
            match = pattern.match(href)
            if match is None:
                continue
            ref_id = match.group(1)
            if ref_id and ref_id not in seen:
                seen.add(ref_id)
                refs.append(ref_id)
            break
    return refs


def detect_section_path(adapter_output: AdapterOutput) -> str | None:
    """Return the entry's first major-section heading, or None.

    Heuristic: returns the text of the first level-2 heading in source
    order. SEP entries number their major sections (e.g.,
    "1. The Varieties of Cognitive Success"); textbook chapters use
    the same shape. The first such heading is a coarse but useful
    section pointer for the focusing brief.

    Returns None when no level-2 heading is present.
    """
    for element in adapter_output.elements:
        if element.kind == "heading" and element.attributes.get("level") == "2":
            text = element.text.strip()
            if text:
                return text
    return None


def detect_word_count(adapter_output: AdapterOutput) -> int:
    """Return an approximate word count for the entry.

    Uses character-count divided by CHARS_PER_WORD_APPROX. Coarse but
    adequate for the focusing brief — the word_count is a relative-
    magnitude signal (stub vs. full-length entry), not a precise
    measurement.

    Returns 0 for empty source.
    """
    if not adapter_output.full_text:
        return 0
    return len(adapter_output.full_text) // CHARS_PER_WORD_APPROX


def compute_extraction_confidence(
    title: str | None,
    entry_id: str,
    cross_references: list[str],
    section_path: str | None,
    word_count: int,
    document_type_config: dict[str, Any],
) -> float:
    """Return a coarse 0.0–1.0 extraction-confidence score.

    Heuristic combining presence of structural cues:
      - +0.30 if title detected
      - +0.20 if entry_id non-empty
      - +0.20 if any cross_references found
      - +0.15 if section_path detected
      - +0.15 if word_count >= minimum_word_count_for_full_entry

    The LLM triage uses this as a tiebreaker only; the parametric-
    knowledge boundary remains the primary credibility signal.
    """
    score = 0.0
    if title is not None and title.strip():
        score += 0.30
    if entry_id:
        score += 0.20
    if cross_references:
        score += 0.20
    if section_path is not None and section_path.strip():
        score += 0.15
    if word_count >= document_type_config["minimum_word_count_for_full_entry"]:
        score += 0.15
    return round(score, 3)


# --------------------------------------------------------------------------
# Orchestrator and emitter
# --------------------------------------------------------------------------


def partition_at_entry_boundaries(
    adapter_output: AdapterOutput, document_type_config: dict[str, Any]
) -> list[list[StructuralElement]]:
    """Partition adapter_output.elements at entry-boundary headings.

    The boundary signal is `document_type_config["entry_boundary"]`, which
    encodes the heading "level" that delimits an entry. The HTML config
    sets this to "h1"; the function maps that to level="1" on heading
    elements. PDFInputAdapter emits outline-derived headings with the same
    level scheme, so the same boundary contract works uniformly across
    HTML and PDF.

    Returns a list of element-lists, one per partition (= one per entry).
    Edge cases:

    - Elements before the first boundary heading attach to a "preamble"
      partition that is dropped (matches the SEP HTML expectation that
      content before <h1> is metadata/nav, not entry content).
    - Zero boundary headings → entire document is one partition. This
      preserves single-entry HTML behavior (test_extract_entries_returns_
      one_entry_for_zero_boundary_doc regression bar).
    - The title element (kind="title", before any heading) is preserved
      in the preamble and dropped with it; per-partition title comes from
      the partition's first heading via `detect_title`'s h1 fallback.
    """
    boundary_level = _resolve_entry_boundary_level(
        document_type_config.get("entry_boundary", "h1")
    )
    partitions: list[list[StructuralElement]] = []
    current: list[StructuralElement] = []
    started = False
    for element in adapter_output.elements:
        if (
            element.kind == "heading"
            and element.attributes.get("level") == boundary_level
        ):
            if started and current:
                partitions.append(current)
            current = [element]
            started = True
        else:
            if started:
                current.append(element)
    if started and current:
        partitions.append(current)
    if not started and adapter_output.elements:
        partitions.append(list(adapter_output.elements))
    return partitions


def _resolve_entry_boundary_level(boundary: str) -> str:
    """Map an entry_boundary config value to a level attribute string.

    The historical HTML config uses "h1" / "h2" forms; PDFInputAdapter
    emits headings with attributes {"level": "1"}. This helper bridges
    them so the partitioner stays agnostic to the config surface.
    """
    match = re.match(r"^h(\d+)$", boundary, re.IGNORECASE)
    if match is not None:
        return match.group(1)
    return boundary


def extract_entry_from_partition(
    partition_elements: list[StructuralElement],
    adapter_output: AdapterOutput,
    document_type_config: dict[str, Any],
) -> Entry | None:
    """Run the detector pipeline against a single partition.

    Returns None when no title detectable in the partition. Used by
    extract_entries() in the multi-entry partitioning path; mirrors the
    single-entry orchestrator body but operates on a scoped element list
    rather than the full AdapterOutput.

    word_count is computed from the partition's text (not the document-
    wide full_text) so per-entry word counts in multi-entry sources are
    meaningful. entry_id falls through URL-slug → source-path stem →
    slugified title; for multi-entry PDFs the URL path is typically
    absent and the slug derives from the partition's title.
    """
    partition_view = AdapterOutput(
        source_path=adapter_output.source_path,
        document_type=adapter_output.document_type,
        elements=partition_elements,
        source_url=adapter_output.source_url,
        full_text=_partition_text(partition_elements),
    )
    title = detect_title(partition_view, document_type_config)
    if title is None:
        return None
    entry_id = detect_entry_id(partition_view, title)
    cross_references = [
        ref
        for ref in detect_cross_references(partition_view, document_type_config)
        if ref != entry_id
    ]
    section_path = detect_section_path(partition_view)
    word_count = detect_word_count(partition_view)
    confidence = compute_extraction_confidence(
        title=title,
        entry_id=entry_id,
        cross_references=cross_references,
        section_path=section_path,
        word_count=word_count,
        document_type_config=document_type_config,
    )
    return Entry(
        title=title,
        entry_id=entry_id,
        cross_references=cross_references,
        section_path=section_path,
        word_count=word_count,
        source_url=partition_view.source_url,
        extraction_confidence=confidence,
    )


def _partition_text(partition_elements: list[StructuralElement]) -> str:
    """Join partition element texts for word-count estimation.

    Used by extract_entry_from_partition() when computing per-entry
    word counts. The joined text is approximate (the element list
    contains headings + anchors + a title at most; body paragraphs
    are not collected by either adapter), but coarse word counts
    suffice for the brief's tiebreak signal per ADR 0047.
    """
    return " ".join(e.text for e in partition_elements if e.text)


def extract_entries(
    adapter_output: AdapterOutput, document_type_config: dict[str, Any]
) -> list[Entry]:
    """Compose the detectors and return Entry records.

    Multi-entry partitioning landed at S-0096 per Issue #34: the
    orchestrator partitions adapter_output.elements at entry-boundary
    headings (per `document_type_config["entry_boundary"]`) and runs
    the detector pipeline against each partition. Single-entry sources
    (SEP HTML pages — one <h1> per page) yield exactly one Entry,
    preserving pre-S-0096 behavior. Multi-entry sources (Routledge PDF —
    2041 outline entries) yield N Entries.

    Returns an empty list when no entry is detectable (no boundary
    headings AND the orchestrator's no-boundary fallback partition
    yields no detectable title).

    Defense-in-depth anonymization filter (Issue #49 + Issue #48 cross-
    deliverable invariant): partitions whose first heading text matches
    `is_publication_name_shaped()` are dropped before becoming Entry
    records. Catches publication-name leakage from any emit path
    (outline, font-size, page-header, text-pattern) — not only the new
    third-tier detector. Pairs with the emit-time filter in
    `PDFInputAdapter._emit_page_header_headings()` and the title-detection
    filter in `detect_title()` for layered protection of the
    parametric-knowledge boundary committed in ADR 0047 decision 4.
    """
    partitions = partition_at_entry_boundaries(adapter_output, document_type_config)
    entries: list[Entry] = []
    for partition in partitions:
        first_heading = next(
            (e for e in partition if e.kind == "heading"),
            None,
        )
        if (
            first_heading is not None
            and first_heading.text
            and is_publication_name_shaped(first_heading.text)
        ):
            continue
        entry = extract_entry_from_partition(
            partition, adapter_output, document_type_config
        )
        if entry is not None:
            entries.append(entry)
    return entries


def emit_focusing_brief(
    adapter_output: AdapterOutput, entries: list[Entry]
) -> FocusingBrief:
    """Assemble the final FocusingBrief from AdapterOutput + entries."""
    return FocusingBrief(
        source_path=adapter_output.source_path,
        document_type=adapter_output.document_type,
        parser_version=PARSER_VERSION,
        generated_at=emit(),  # ADR 0058 canonical
        entries=entries,
    )


def serialize_brief(brief: FocusingBrief) -> str:
    """Serialize the FocusingBrief to a JSON string with stable ordering.

    Source identity is anonymized at this boundary per ADR 0047 decision 4
    so the downstream adversarial-triage LLM cannot infer the publisher and
    bias its candidate evaluation. The strip targets:

      - `source_path` at the top level
      - `source_url` on every entry

    The in-memory dataclasses are NOT mutated — internal consumers (notably
    `detect_entry_id`'s URL-slug derivation) still need the fields. The
    strip happens only on the dict copy produced by `dataclasses.asdict`.

    The publication-name structural pattern that strips publisher
    signatures from entry titles is applied earlier (in `detect_title`),
    so titles arriving here are already anonymized; this function's
    responsibility is the URL/path layer.
    """
    data = dataclasses.asdict(brief)
    data.pop("source_path", None)
    for entry_dict in data.get("entries", []):
        entry_dict.pop("source_url", None)
    return json.dumps(data, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments into a Namespace."""
    parser = argparse.ArgumentParser(
        prog="parse_structural_reference",
        description=(
            "Extract graph-shape signal from a structural-reference source "
            "(see ADR 0047)."
        ),
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the source file the adapter reads.",
    )
    parser.add_argument(
        "--document-type",
        choices=sorted(DOCUMENT_TYPE_REGISTRY.keys()),
        required=True,
        help="Document type for heuristic config selection.",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output path. Use '-' to write the brief to stdout.",
    )
    parser.add_argument(
        "--adapter",
        type=str,
        default=None,
        help=(
            "Optional explicit adapter selection; default is inferred from "
            "the source file extension."
        ),
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> int:
    """Execute the parse run; return process exit code."""
    config = DOCUMENT_TYPE_REGISTRY[args.document_type]
    adapter = select_adapter(args.source, override=args.adapter)
    adapter_output = adapter.extract(args.source, args.document_type)
    entries = extract_entries(adapter_output, config)
    brief = emit_focusing_brief(adapter_output, entries)
    serialized = serialize_brief(brief)
    if args.output == "-":
        sys.stdout.write(serialized)
        sys.stdout.write("\n")
    else:
        Path(args.output).write_text(serialized + "\n", encoding="utf-8")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point. argv defaults to sys.argv[1:]."""
    args = parse_args(argv if argv is not None else sys.argv[1:])
    return run(args)


# Module-level constant intentionally re-exported for tests; field()
# default factory not used because the dataclasses above are frozen.
__all__ = [
    "PARSER_VERSION",
    "ENCYCLOPEDIA_CONFIG",
    "DOCUMENT_TYPE_REGISTRY",
    "ADAPTER_REGISTRY",
    "CHARS_PER_WORD_APPROX",
    "PDF_HEADING_FONT_BUCKET_COUNT",
    "PDF_HEADING_FONT_MIN_BUCKET_CHARS",
    "PDF_TEXT_CROSSREF_PATTERNS",
    "PDF_PAGEHEADER_REPETITION_THRESHOLD",
    "PDF_TITLE_MIN_LENGTH",
    "PDF_CROSSREF_SLUG_REJECT",
    "PDF_FONT_SAMPLE_PAGE_COUNT",
    "PDF_FONT_SAMPLE_SKIP_FRONT",
    "PDF_ANNOT_PAGE_CAP",
    "PDF_FONT_EMIT_PAGE_CAP",
    "StructuralElement",
    "AdapterOutput",
    "Entry",
    "FocusingBrief",
    "InputAdapter",
    "HTMLInputAdapter",
    "PDFInputAdapter",
    "select_adapter",
    "detect_title",
    "slugify_title",
    "detect_entry_id",
    "detect_cross_references",
    "detect_section_path",
    "detect_word_count",
    "compute_extraction_confidence",
    "partition_at_entry_boundaries",
    "extract_entry_from_partition",
    "extract_entries",
    "emit_focusing_brief",
    "serialize_brief",
    "parse_args",
    "run",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())
