# ADR 0059 — Audit-time fetching of public structural references for verdict fortification

- **Status:** Accepted
- **Date:** 2026-05-09
- **Deciders:** S-0106

## Context

[ADR 0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) settles the *authoring-time* posture for consuming a class of curated philosophy reference works (SEP, IEP, Routledge, Oxford Reference, Wikipedia) as graph-shape priors for Phase 5 seed authoring. [ADR 0047](0047-structural-reference-parser-tool-and-adversarial-triage-workflow.md) implements the operational mechanism: a standing engine tool, `parse_structural_reference.py`, with a deliberately tool-scoped *anti-fetch* contract — the user supplies a path to a source already acquired through legitimate channels; the parser does not crawl, scrape, or download. The S-0103 amendment to ADR 0047 adds source-identity anonymization at the serialization boundary so a downstream LLM consuming the focusing brief cannot infer the publisher and bias its triage. [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) settles the audit-time posture for health-check audits, with the principle "any external system the audit touches gets a fresh content probe at audit-time, not a citation of cached stats."

The Phase 5 production audit (master plan at [`engine/build_readiness/phase_5_production_audit.md`](../build_readiness/phase_5_production_audit.md), routine block resumed at S-0104) executes adversarial review of every graph entry against parametric SEP knowledge per [ADR 0057](0057-adversarial-stance-for-health-check-audits.md)'s posture for graph audits. S-0104's cross-bridge full-census produced a 35.2% substantive-defect rate across 71 cross-domain edges. Among the 71 verdicts, ~22 sit in a **medium-confidence band** where the parametric verdict implies a graph mutation (8 reversals, 14 historical-not-pedagogical retypings, 3 weak-edge removals) but the parametric reasoning lacks empirical structural evidence to corroborate. The S-0104 closeout flagged the ~22 medium-confidence verdicts as the band where empirical fortification would meaningfully reduce false-positive graph mutations.

The user adjudicated this question at S-0106 (transcript at [`~/.claude/plans/i-want-an-adversarial-toasty-storm.md`](../../../../.claude/plans/i-want-an-adversarial-toasty-storm.md)). The question: is the project's parametric-only stance strictly required for *audit-time* comparison/contrast use, distinct from authoring-time graph construction? After adversarial review against the parametric-only stance, Option A landed: a bounded ephemeral audit-time fetching carve-out.

Four dimensions warrant ADR-level commitment because each propagates to multiple downstream sessions and each has a substantive alternative the project might want to revisit:

1. **Authoring-time vs audit-time scope.** Seed authoring stays parametric per [ADR 0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md); only audit gets a carve-out. Mixing the carve-out into authoring would silently corrupt graph provenance — parametric integration across many sources during training has different epistemic properties than single-source ground-truthing.
2. **Source-identity bias.** A naive fetch-and-show-LLM workflow is strictly worse than parametric-only because the LLM treats "this is from SEP" as an authority signal that biases the comparison. The S-0103 anonymization mechanism extends to URL-fetched content as a load-bearing prerequisite. Without that extension, fetching is a regression on the parametric-knowledge boundary [ADR 0047](0047-structural-reference-parser-tool-and-adversarial-triage-workflow.md) decision 4 commits to.
3. **Procedural discipline.** Robots.txt, polite User-Agent, per-host rate-limit, ephemeral lifecycle, bounded fetch budget — design constraints, not blockers, but they have to be in the implementation rather than assumed.
4. **Aggregation under fair use.** One-off audit-time use is comfortably transformative non-commercial. A standing-capability fetcher (recurring crawler that becomes part of normal operation) is a separate ADR if and when use grows beyond audit fortification — fair use's four-factor balancing test shifts on factor 3 (amount used) and factor 4 (market effect) when bulk consumption replaces one-off comparison.

The user's initial framing leaned on a sidewalk-photo analogy ("if a person is on a public sidewalk I can take their photo"). That analogy is wrong-genre — privacy law and copyright law are different regimes and public viewability is necessary but not sufficient for any particular use. The defensible grounds are different: narrowly scoped non-commercial transformative comparison use, with mechanical bias prevention (anonymization extended) and bounded lifecycle (ephemeral). The carve-out below rests on those grounds, not on the analogy.

## Decision

**Audit-time fetching of public Tier 4 structural references is permitted under bounded conditions.** The carve-out applies to Phase 5 production audit work (and any future audit work that extends the audit posture per [ADR 0057](0057-adversarial-stance-for-health-check-audits.md)) where parametrically-derived graph entries are compared against fetched structural skeletons for verdict fortification. Authoring-time posture under [ADR 0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) is unchanged; fetching is not a graph-construction shortcut.

**Four conditions are necessary and the union is sufficient:**

1. **Anonymization mandatory.** The S-0103 source-identity anonymization mechanism (`serialize_brief()` `dataclasses.asdict()` post-filter; `strip_publication_name_suffix()` and `is_publication_name_shaped()` defense-in-depth filters) MUST run on URL-fetched briefs before the LLM sees them. The recursive-walk invariant — "no source-identity strings at any depth in the brief" — is the load-bearing assertion. Tests assert this invariant against synthetic-publisher fixtures (`Acme`, `FakeReference`, `MockPublisher`) per the S-0103 implementation discipline.
2. **Bounded ephemeral lifecycle.** Fetched content lives in the audit session's process memory and dies with it. Storage is `tempfile.TemporaryDirectory` purged on context exit; no on-disk cache; no cross-session persistence. The graph remains parametric; only audit verdicts (which the audit was already authorized to produce) persist beyond the session.
3. **Polite-fetcher discipline.** Declared User-Agent identifying the project; robots.txt consulted via `urllib.robotparser` and refusal honored (exit code 2); per-host rate-limit (default 2.0 seconds between fetches); bounded fetch count per session (default 20). Robots.txt unavailable (4xx HTTP response) is treated as no-policy — proceed with rate-limit, no aggressive parallelism.
4. **Per-source policy.** [`product/docs/content-strategy.md`](../../product/docs/content-strategy.md) Tier 4 declares per-source authorization. Initial policy at S-0106: SEP / IEP / Wikipedia fetchable, polite, rate-limited; Routledge / Oxford Reference out of scope (paywalled — institutional-credential fetching is a different fair-use posture and warrants its own per-source ADR if pursued). Amendments to per-source policy are content-strategy.md amendments or per-source ADRs in the consuming session, not flags on this tool.

**The paired tool is `engine/tools/fetch_structural_reference.py`.** It composes the existing parser via the public API (`select_adapter` + `extract` + `extract_entries` + `emit_focusing_brief` + `serialize_brief`) after a fetch step. The parser's anti-fetch contract is preserved — `parse_structural_reference.py` itself is unchanged; its tool-scoped no-fetch rule is honored verbatim. The new tool is the URL-input counterpart that [ADR 0047](0047-structural-reference-parser-tool-and-adversarial-triage-workflow.md)'s "Open future ADRs" anticipated.

**Failure-mode discrimination via exit codes** matching the [`routine_lifecycle_push.py`](../tools/routine_lifecycle_push.py) and [`apply_migration.py`](../tools/apply_migration.py) wrapper pattern:

- 0 — success; brief printed to stdout (CLI mode) or returned (programmatic mode)
- 2 — robots.txt refused (per-source policy may need ADR amendment; HANDOFF; no retry)
- 3 — rate-limit / fetch-budget violation (caller exceeded session budget; investigate audit-loop shape)
- 4 — network failure (retried once after 5 seconds, then exit)
- 5 — generic fetch error
- 6 — anonymization invariant violation (load-bearing; signals tool bug or adversarial source content; HANDOFF immediately)

**The standing-capability fair-use ADR is deferred** until and unless audit fetching grows beyond one-off fortification. Per the four-factor fair use balancing test, one-off transformative non-commercial comparison use is comfortably within fair use; aggregation thresholds become live if the project starts running standing crawlers. The deferred-future-ADR clause is real, not a hedge — if standing fetching becomes warranted, that ADR must happen before the standing usage lands.

## Consequences

**[ADR 0011](../../product/adr/0011-no-hosted-copyrighted-material.md) ceiling is unchanged.** Fetched content is never hosted, redistributed, or surfaced to learners. The brief's structural skeleton informs verdict authoring; the brief itself dies with the session; only verdicts persist (and verdicts are graph-shape facts, not source prose). The graph remains parametric; ADR 0011's "zero copyright exposure in every domain, forever" clause holds.

**[ADR 0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) authoring-time posture is unchanged.** The seed-authoring discipline (graph-shape value distinct from content/prose value, structural extraction at seed time only, no live fetching during authoring) holds. ADR 0046's class-boundary clause and access-warrant tradeoff remain intact. This ADR is *additive* — it adds an audit-time use case; it does not retreat from authoring-time discipline. A future Phase 6 (or beyond) authoring session that wanted to fetch live during authoring would need to amend ADR 0046, not cite this ADR.

**[ADR 0047](0047-structural-reference-parser-tool-and-adversarial-triage-workflow.md) is amended in Consequences (not superseded).** The amendment notes the paired URL-input tool's existence and back-references this ADR. The parser's own no-fetch contract is preserved in scope-clean separation: `parse_structural_reference.py` does not fetch; `fetch_structural_reference.py` composes a fetch step + the parser's public API. The S-0103 anonymization mechanism is shared via direct function reuse (no fork, no reimplementation). The "Open future ADRs" clause's per-source acquisition pointer is the conceptual ancestor of this ADR.

**[ADR 0057](0057-adversarial-stance-for-health-check-audits.md) "fresh content probe at audit-time" posture is operationalized for graph audits.** ADR 0057's principle was already established for health-check audits (audit external systems by fresh-probing, not by citing cached stats). This ADR extends the same logic to graph audits — the symmetry was implicit; this ADR makes it explicit at the contract layer. Audit posture and authoring posture were always meant to differ on this axis.

**[ADR 0053](0053-mechanism-first-exercise-gate.md) trigger criterion evaluation:**

- Trigger 1 (introduces a new session mode): NO — `fetch_structural_reference.py` is a tool, not a session mode.
- Trigger 2 (introduces a new validator soft-warn category): NO — no `validate.py` changes in this session.
- Trigger 3 (introduces a new state file the boot procedure reads): NO — ephemeral in-process cache; no boot integration.
- Trigger 4 (Consequences list spans ≥ 3 ops docs OR ≥ 5 tooling files): NO — 1 ops doc ([cross-references.md](../operations/cross-references.md)) + 2 tooling files (the new tool + tests) + 4 doc amendments.

**Strict trigger does not fire. Voluntary first-exercise readiness note authored anyway** at [`engine/build_readiness/fetch_structural_reference_first_exercise.md`](../build_readiness/fetch_structural_reference_first_exercise.md) because the master-plan amendment will route unattended routine-mode audit sessions to this tool, and the gate's spirit (catch S-0048-shape gaps before unattended use) applies despite the strict trigger not firing. Per ADR 0053's "trigger when in doubt" bias the cost of a voluntary gate (one note authored at landing time) is much smaller than the cost of a missed trigger (the S-0048 → S-0055 serialized-Issue pattern). The first exercise lands in an interactive session — the S-0104 medium-confidence-verdict fortification pass that the user runs at audit closeout.

**Per-source policy lives in [`product/docs/content-strategy.md`](../../product/docs/content-strategy.md), not in this ADR.** Initial policy lands at S-0106 in the same commit as this ADR (SEP / IEP / Wikipedia: fetchable, polite, rate-limited; Routledge / Oxford Reference: out of scope). Amendments to the per-source policy are content-strategy.md amendments or per-source ADRs in the consuming session — not amendments to this ADR. This ADR codifies the *contract*; the policy is the *parameter*.

**The Phase 5 audit methodology amendment** at [`engine/build_readiness/phase_5_production_audit.md`](../build_readiness/phase_5_production_audit.md) adds an optional empirical-fortification branch to the per-edge prompt template for medium-confidence verdicts that imply graph mutations. Routine-mode audit sessions running unattended SHOULD use the branch when verdict confidence is medium AND the verdict implies a graph mutation; the branch is OPTIONAL because high-confidence parametric verdicts don't justify the marginal cost. The first exercise of the branch lands in an interactive session per ADR 0053; subsequent routine fires use it freely.

**Validator unchanged.** No new soft-warn category is introduced in this session. A future session may add a `fetch_budget_exceeded_session` category if the routine block produces evidence that the budget is being silently exhausted; that's an [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) soft-warn-lifecycle decision the consuming session makes against real telemetry. Adding it speculatively now would violate "don't add features beyond what the task requires."

**Test coverage at S-0106:**

- `TestFetchSession` — context-manager lifecycle; ephemeral tmpdir purge on `__exit__`; max-fetches budget enforcement (exit code 3); per-host rate-limit enforcement (exit code 3 if violated; sleep-and-proceed otherwise).
- `TestRobotsTxtCompliance` — disallowed URL refused with exit code 2; allowed URL proceeds; robots-unavailable (4xx) proceeds conservatively; robots fetch error itself does not crash the tool.
- `TestAnonymizationInvariant` — recursive walk over the URL-fetched brief asserts no source-identity strings at any depth; adversarial fixtures use synthetic-publisher tokens (`Acme`, `FakeReference`, `MockPublisher`) per S-0103 implementation discipline.
- `TestComposition` — synthetic SEP-shaped HTML round-trips through the parser via the fetch path and produces a `FocusingBrief` with entries and cross-references.
- `TestExitCodes` — each of exit codes 0/2/3/4/5/6 is reachable via a synthetic stub; argparse CLI mode emits the correct code.

**The aggregation / fair-use concern is bounded for one-off audit use** but not eliminated. If audit work grows to systematically fetch every Tier 4 structural reference corresponding to every graph node on a recurring schedule, the aggregation analysis under fair use shifts. The standing-capability ADR mentioned in the Decision section is the future hook for that escalation. As of S-0106 the carve-out is for one-off audit fortification, comfortably within transformative non-commercial fair use.

**No `engine/tools/requirements.txt` addition required.** The tool uses only `urllib.request`, `urllib.robotparser`, `tempfile`, `pathlib`, `time`, `dataclasses`, `re`, `argparse`, plus the existing parser module. All standard-library; no new third-party dependencies. The existing `beautifulsoup4` (HTML adapter) and PDF stack are already pinned.

**ENGINE_LOG entry under [Unreleased] / Added** records the contract landing. Subsequent sessions consuming the carve-out reference this ADR.

**Open future ADRs:**

- A standing-capability fair-use ADR if/when audit fetching grows beyond one-off fortification (named explicitly above; deferral is real, not a hedge).
- A per-source acquisition ADR for paywalled members of the Tier 4 class (Routledge, Oxford Reference) if a session pursues institutional-credential fetching — distinct fair-use posture from public-source fetching.
- A `fetch_budget_exceeded_session` validator soft-warn ADR if routine-block telemetry shows the budget is being silently exhausted ([ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) lifecycle).

## See also

- [ADR 0011](../../product/adr/0011-no-hosted-copyrighted-material.md) — no hosted or distributed copyrighted material; ceiling, unchanged.
- [ADR 0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) — structural-reference posture for seed authoring; authoring-time posture, unchanged.
- [ADR 0047](0047-structural-reference-parser-tool-and-adversarial-triage-workflow.md) — `parse_structural_reference.py` operational mechanism; amended in Consequences with paired-tool back-pointer.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — mechanism-first-exercise gate; voluntary application despite strict trigger not firing.
- [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) — adversarial stance for audits; audit-time fresh-probe posture extended from health-check audits to graph audits.
- [`engine/tools/fetch_structural_reference.py`](../tools/fetch_structural_reference.py) — the paired URL-input tool implementing this ADR.
- [`engine/build_readiness/phase_5_production_audit.md`](../build_readiness/phase_5_production_audit.md) — Phase 5 production audit methodology; amended at S-0106 with the optional empirical-fortification branch.
- [`engine/build_readiness/fetch_structural_reference_first_exercise.md`](../build_readiness/fetch_structural_reference_first_exercise.md) — first-exercise readiness note; closes when an interactive audit-closeout session executes the fortification pass against medium-confidence verdicts.
- [`product/docs/content-strategy.md`](../../product/docs/content-strategy.md) — Tier 4 fetch-policy column declaring per-source authorization (added at S-0106).
- [`engine/operations/cross-references.md`](../operations/cross-references.md) — engine-side dependency map.
