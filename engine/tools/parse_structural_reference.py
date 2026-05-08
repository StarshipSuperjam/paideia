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
        "source_path": "<absolute or relative path to source>",
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
                "source_url": "<URL>" | null,
                "extraction_confidence": <float 0.0-1.0>
            }
        ]
    }

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
    ],
    "section_path_source": "first_section_heading",
    "minimum_word_count_for_full_entry": 200,
    # Title-suffix patterns to strip from raw <title> text. SEP entries
    # use "<Entry> (Stanford Encyclopedia of Philosophy)"; IEP uses
    # "<Entry> | Internet Encyclopedia of Philosophy". Stripping yields
    # cleaner entry titles for the focusing brief.
    "title_suffix_strip_patterns": [
        r"\s*\(Stanford Encyclopedia of Philosophy\)\s*$",
        r"\s*\|\s*Internet Encyclopedia of Philosophy\s*$",
    ],
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


ADAPTER_REGISTRY: dict[str, type[InputAdapter]] = {
    ".html": HTMLInputAdapter,
    ".htm": HTMLInputAdapter,
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
      1. The first <title> element, with config-specified suffix patterns
         stripped (SEP / IEP suffixes). A non-empty stripped result wins;
         a result that strips to empty falls through.
      2. The first <h1> heading.
      3. None when neither is present.
    """
    suffix_patterns: list[str] = []
    if document_type_config is not None:
        suffix_patterns = document_type_config.get("title_suffix_strip_patterns", [])
    for element in adapter_output.elements:
        if element.kind == "title" and element.text:
            stripped = element.text
            for pattern in suffix_patterns:
                stripped = re.sub(pattern, "", stripped).strip()
            if stripped:
                return stripped
    for element in adapter_output.elements:
        if (
            element.kind == "heading"
            and element.attributes.get("level") == "1"
            and element.text
        ):
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


def extract_entries(
    adapter_output: AdapterOutput, document_type_config: dict[str, Any]
) -> list[Entry]:
    """Compose the detectors and return Entry records.

    SEP-shaped sources carry one entry per page; this orchestrator
    surfaces a single Entry per AdapterOutput. Future multi-entry source
    formats (a textbook chapter with N defined-term entries) will extend
    this to return a list of Entries by partitioning AdapterOutput at
    entry-boundary headings.

    Returns an empty list when no title can be detected (the entry-
    boundary signal absent — nothing to surface).
    """
    title = detect_title(adapter_output, document_type_config)
    if title is None:
        return []
    entry_id = detect_entry_id(adapter_output, title)
    cross_references = [
        ref
        for ref in detect_cross_references(adapter_output, document_type_config)
        if ref != entry_id
    ]
    section_path = detect_section_path(adapter_output)
    word_count = detect_word_count(adapter_output)
    confidence = compute_extraction_confidence(
        title=title,
        entry_id=entry_id,
        cross_references=cross_references,
        section_path=section_path,
        word_count=word_count,
        document_type_config=document_type_config,
    )
    return [
        Entry(
            title=title,
            entry_id=entry_id,
            cross_references=cross_references,
            section_path=section_path,
            word_count=word_count,
            source_url=adapter_output.source_url,
            extraction_confidence=confidence,
        )
    ]


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
    """Serialize the FocusingBrief to a JSON string with stable ordering."""
    return json.dumps(dataclasses.asdict(brief), indent=2, ensure_ascii=False)


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
    "StructuralElement",
    "AdapterOutput",
    "Entry",
    "FocusingBrief",
    "InputAdapter",
    "HTMLInputAdapter",
    "select_adapter",
    "detect_title",
    "slugify_title",
    "detect_entry_id",
    "detect_cross_references",
    "detect_section_path",
    "detect_word_count",
    "compute_extraction_confidence",
    "extract_entries",
    "emit_focusing_brief",
    "serialize_brief",
    "parse_args",
    "run",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())
