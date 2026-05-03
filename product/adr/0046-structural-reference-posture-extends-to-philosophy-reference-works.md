# ADR 0046 — Structural-reference posture extends to philosophy reference works as a class

- **Status:** Accepted
- **Date:** 2026-05-03
- **Deciders:** S-0038 (Phase 4.5 input dataset survey)

## Context

The "SEP as Structural Reference, Not Content Source" subsection in [`docs/content-strategy.md`](../docs/content-strategy.md) settled a posture for the Stanford Encyclopedia of Philosophy specifically: SEP is consulted as a curated concept inventory and cross-reference source; no SEP prose is reproduced to learners; the licensing constraint that would otherwise gate commercial use is eliminated because what the project consumes from SEP is uncopyrightable structural fact (concept names and adjacency between concepts), per the project's reading of the idea/expression dichotomy and Feist v. Rural.

The Phase 4.5 input dataset survey ([ROADMAP §4.5](../../ROADMAP.md), [`build_plan/P_3_input_dataset_survey.md`](../../build_plan/P_3_input_dataset_survey.md)) surveyed cross-reference inventories useful as structural priors for Phase 5 seed authoring. The original ROADMAP §4.5 framing placed SEP, IEP, and Wikipedia in Tier 4 — "minimal on long-form prose references already parametrically accessible." That framing addressed only the content/prose value vector and missed a second, distinct value vector that the survey's evaluation made load-bearing.

Two value vectors are at stake when the project consults a curated reference work:

- **Content/prose value** — what an entry *says*. Sonnet/Opus already carry this from training; surveying a well-known reference for content adds no novel value.
- **Graph-shape value** — the cross-reference adjacency network between entries (entry A links to entries B, C, D in this order with this markup), the curated concept inventory (which ~1,500–1,800 concepts the editorial process selected as the discipline's structural backbone), and the entry-presupposition signals an editor's framing reveals. This vector does not survive model training: Sonnet/Opus can recall facts from SEP entries but cannot enumerate SEP's cross-reference adjacency matrix or reconstruct the editorial entry-selection. Graph-shape value is exactly the structural prior Phase 5 seed authoring for the home discipline (philosophy) consumes.

The graph-shape value extends beyond SEP to a class of similarly-curated philosophy reference works:

- **Internet Encyclopedia of Philosophy (IEP)** — ~900 peer-reviewed entries; 30 doctorate-holding editors; complementary coverage to SEP at the introductory tier
- **Routledge Encyclopedia of Philosophy** — ~1,500 peer-reviewed entries; broader on non-Western and historical-period coverage; subscription/institutional access
- **Oxford Reference (philosophy collection)** — Oxford Companion to Philosophy + Oxford Dictionary of Philosophy + Oxford Handbook series aggregated; subscription/institutional access
- **Wikipedia** — broader and uneven, but every article carries explicit cross-references and complementary structured-graph data exists in Wikidata; CC BY-SA 4.0

The same fact-shape argument that excludes SEP's structural extraction from copyright (Feist) extends naturally to these works. Three nuances bear on the extension:

1. **Source acquisition is separate from copyright posture.** Routledge and Oxford Reference are paywalled; the structural-extraction permission under copyright does not override DRM or subscription terms-of-service. Acquiring TXT-extractable copies for graph-shape mining requires legitimate channels (institutional library access, publisher subscription, per-volume purchase).
2. **EU sui generis database rights** apply more strictly than US copyright to *compilations*. Routledge and Oxford are UK-published; the editorial selection-and-arrangement carries compilation protection in EU/UK jurisdictions that US Feist does not extend. The structural extraction itself remains fact-shaped, but the bulk-extraction-and-republication threshold is lower.
3. **No content is hosted or reproduced.** [ADR 0011](0011-no-hosted-copyrighted-material.md) ("No hosted or distributed copyrighted material") is unchanged. The graph-shape extraction yields concept names and adjacency facts that inform a *generatively-authored* new graph; no source prose is copied, paraphrased, or surfaced to learners.

The Phase 4.5 survey records each candidate's graph-shape disposition separately from its content disposition, with the access-warrant tradeoff surfaced for paywalled candidates. The contract layer needs to settle the principle so per-candidate adoption decisions in Phase 5 sub-sessions can be made against a known posture rather than re-litigating the SEP precedent each time.

This ADR does not revise [Generative Graph Independence](../docs/business.md) — the graph remains generatively seeded by Claude with no licensed-dataset dependency for graph construction. Structural references are inputs to the generation pass, not the graph's substance. The posture this ADR formalizes is exactly the posture the existing SEP subsection establishes; the change is the explicit extension to a class.

## Decision

The structural-reference posture established for SEP extends to a class of curated philosophy reference works: **Internet Encyclopedia of Philosophy, Routledge Encyclopedia of Philosophy, Oxford Reference (philosophy collection), and Wikipedia.** The class is closed at the four named members plus SEP for now; admitting a new member is a decision in a consuming Phase 5 sub-session, recorded in that session's ADR if the addition involves a non-trivial tradeoff (e.g., a paywalled non-Western philosophy encyclopedia not in the named set).

**Two value vectors are recognized as distinct.** The graph-shape value (cross-reference adjacency network, concept-inventory curation, entry-presupposition signals) is what the project consumes from a structural reference. The content/prose value (entry text) is separately addressed by the no-hosted-copyrighted-material commitment in [ADR 0011](0011-no-hosted-copyrighted-material.md) — content is never hosted, redistributed, or surfaced to learners. The Phase 4.5 survey and downstream Phase 5 sub-sessions evaluate every candidate on the graph-shape vector independently of the content vector.

**Structural extraction is uncopyrightable per Feist.** Concept names are facts about the field; cross-reference adjacency between concepts is fact-shaped; the editorial selection-and-arrangement carries thin compilation copyright in US jurisdictions and stronger sui generis database protection in EU/UK jurisdictions. The project's extraction yields per-source-cited concept inventories and adjacency lists used as priors for generative authoring; no source prose is reproduced. The fair-use / transformative-use analysis is favorable for non-commercial personal-project use per [ADR 0032](0032-personal-project-disposition.md) (superseded by [ADR 0035](0035-multi-platform-apple-expansion.md) at the multi-platform scope; the personal-project disposition the cost-cap discipline rests on is preserved).

**Source acquisition is separate from copyright posture.** Paywalled members of the class (Routledge, Oxford) require legitimate-channel acquisition before structural extraction can proceed. The Phase 4.5 survey surfaces the access-warrant tradeoff per candidate; per-source acquisition decisions are made in the consuming Phase 5 sub-session. EU/UK compilation-protection is acknowledged at the contract layer; the project's bulk-extraction does not approach the threshold that would trigger sui generis database rights (the project derives a new structure from extracted fact-priors; it does not redistribute the source's compilation).

**Generative Graph Independence remains intact.** The graph is generatively seeded by Claude. Structural references provide priors that improve the generation pass; they are not the graph's substance. No member of the structural-reference class becomes a corpus dependency or a reproduction surface.

## Consequences

- **Phase 4.5 survey records the posture concretely.** The "Cross-Domain Reference Inventories — Survey" section in [`docs/content-strategy.md`](../docs/content-strategy.md) lands per-candidate Tier 4 assessments evaluating graph-shape value distinctly from content value, with access-warrant disposition per source. The survey's Tier 4 reframing supersedes the original ROADMAP §4.5 "minimal on long-form prose" framing as applied to philosophy reference works specifically.
- **Phase 5 sub-sessions inherit a settled framing.** Every Phase 5 subdomain session (epistemology, ethics, metaphysics, philosophy of mind, philosophy of language, philosophy of science, plus service nodes and cross-domain edges) consults the structural-reference class at boot. The session does not re-decide whether SEP / IEP / Routledge / Oxford / Wikipedia structural extraction is permitted; it inherits this ADR. Per-source adoption decisions (e.g., "this session pursues Routledge institutional access for non-Western coverage") land as ADRs in the consuming session.
- **The "SEP as Structural Reference, Not Content Source" subsection in [`docs/content-strategy.md`](../docs/content-strategy.md) is extended in place** with a cross-link to this ADR and a one-paragraph extension naming the broader class. The original SEP-specific framing is preserved; the extension is additive.
- **Source-acquisition decisions remain per-session.** Routledge subscription cost, Oxford Reference institutional-vs-personal access, EU/UK jurisdiction considerations — these are operational decisions the consuming Phase 5 sub-session makes against the contract this ADR provides. The contract is the principle; the operational question is "should we acquire this source for this sub-session?"
- **[ADR 0011](0011-no-hosted-copyrighted-material.md) is unchanged.** No hosted or distributed copyrighted material remains binding. Structural extraction yields fact-priors that inform generation; no source prose is hosted, redistributed, or surfaced to learners.
- **Generative Graph Independence in [`docs/business.md`](../docs/business.md) is unchanged.** The graph remains generatively seeded; structural references are inputs to the generation pass, not the graph's substance.
- **Class boundary admits supersession.** A future Phase 5 sub-session may surface a structural reference outside the named five (e.g., a non-Western philosophy encyclopedia, a curated history-of-ideas database) whose graph-shape value warrants admitting it to the class. That admission lands as an ADR in the consuming session with a brief rationale; the precedent this ADR sets is the criterion (graph-shape value distinct from content value, structural extraction fact-shaped per Feist, no hosted prose).
- **Open future ADRs.** None forced. The first Phase 5 sub-session that pursues Routledge or Oxford acquisition will likely author a small operational ADR documenting the chosen access path and the budget-impact disposition. The class is not closed in principle; it is closed at the named five for now.

## See also

- [`docs/content-strategy.md`](../docs/content-strategy.md) — "SEP as Structural Reference, Not Content Source" (extended in place at S-0038); "Cross-Domain Reference Inventories — Survey" (Tier 4 reframed at S-0038).
- [ADR 0011](0011-no-hosted-copyrighted-material.md) — no hosted or distributed copyrighted material; unchanged.
- [`docs/business.md`](../docs/business.md) — Generative Graph Independence (referenced in `content-strategy.md`); unchanged.
- [`build_plan/P_3_input_dataset_survey.md`](../../build_plan/P_3_input_dataset_survey.md) — Phase 4.5 chunk file mandating that survey findings revising the SEP-structural-reference posture land as ADRs in-session.
- [ROADMAP §4.5](../../ROADMAP.md) — Phase 4.5 input dataset survey scope; this ADR's authoring is the survey-finding-revision the chunk file anticipates.
