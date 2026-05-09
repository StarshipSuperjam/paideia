# Phase 5 graph production audit — master plan gate report

> Authored by S-0082 per the approved plan at `~/.claude/plans/exploration-session-phase-5-flickering-newell.md` and the S-0081 audit-warrant gate's PROCEED recommendation at [`phase_5_production_audit_gate.md`](phase_5_production_audit_gate.md). Pairs with the routine target file at [`engine/session/auto_target.json`](../session/auto_target.json) (T-PHASE-5-AUDIT). Read by the 12 routine evidence sessions at boot; consumed at closeout by the interactive disposition session.

## Scope and goal

Conduct an adversarial pedagogical-content audit of the 380-node / 536-edge Phase 5 knowledge graph using SEP-anchored review across a stratified, edge-anchored sample. Produce per-subdomain evidence files that the closeout disposition session triages into Issues, ADR memos, and validator soft-warn proposals.

**This is the project's first product-fitness audit.** The methodology piloted here is intended to be reusable for future phases (Phase 6 self-correction outputs, Phase 7+ teaching surfaces). Whether to formalize the pattern in an engine ADR is deferred to the closeout — one cross-cutting mechanism is now under exercise; ADR-warranting structure may not crystallize until findings are in hand.

## Anti-scope

- **Disposition.** Evidence sessions produce candidate findings only — no Issue filing, no ADR drafts, no soft-warn proposals authored as deliverables. Disposition is the closeout's interactive responsibility.
- **Migration changes.** Evidence sessions do not edit `product/seed-graph/migrations/`. Findings about edges or nodes are recorded in evidence files; corrections (if any) are authored in subsequent build sessions after closeout dispositioning.
- **Rigor calibration.** That's Phase 6.
- **Closeout reports themselves.** The production-audit final report and audit-system-input report land at the closeout, not during routine evidence gathering.

## Methodology — SEP-anchored review

### Per-edge prompt template (load-bearing — cross-session consistency depends on this)

For each sampled edge, the routine session applies the following structured prompt as in-thread reasoning. The prompt is fixed; deviation is the principal failure mode the gate session named (AI-generic philosophy paraphrase will dominate without the SEP anchor).

```
EDGE: <source_label> [<source_id>, domain=<source_domain>]
   → <target_label> [<target_id>, domain=<target_domain>]
   edge_type = pedagogical_prerequisite
   weight = <weight>, confidence = <confidence>, evidence = <evidence_text or NULL>

SEP-ANCHORED PROMPT:
1. Name the SEP entry (or entries) most directly relevant to source and target.
   Cite by entry title — e.g., "Stanford Encyclopedia of Philosophy entry on
   'The Analysis of Knowledge'" or "SEP entry on 'Modal Realism'".
2. Reference the SEP framing of the source-target relationship as you understand
   it from training: how does SEP describe the conceptual dependency direction,
   if any? What's the most proximate prerequisite SEP would name for the target,
   if any?
3. Verdict on the edge:
   (a) Sound — direction matches SEP framing; relationship is genuinely
       pedagogical-prerequisite-shaped.
   (b) Defensible — direction is not the canonical SEP framing, but the edge
       is supportable on alternative framing.
   (c) Reversed — pedagogical direction runs the opposite way of the edge.
   (d) Weak/redundant — direction is correct but a more proximate prereq
       exists in the graph; the edge is a long-distance shortcut.
   (e) Mis-typed: historical-not-pedagogical — the source is a historical
       movement, school, or thinker-framework whose relation to the target
       is influence, not prerequisite. The relation type is plausibly
       historical_influence (per PREDICATE_MANIFEST.md reserved-but-unused
       row), not pedagogical_prerequisite.
   (f) Mis-typed: thematic — the relation is co-discussed-in-philosophy
       rather than pedagogical-prerequisite.
   (g) Other — name the shape.
4. Reasoning — one short paragraph citing the SEP framing (no quoted prose
   per ADR 0011 / ADR 0046 — INTERPRETED-only posture).
5. Confidence in this verdict — high / medium / low.
```

### Per-node prompt template

For each sampled node:

```
NODE: <label> [<id>, domain=<domain>]
   summary = <first 200 chars of summary>

SEP-ANCHORED PROMPT:
1. Name the SEP entry most directly relevant to this concept.
2. Granularity check: is this concept at concept-level granularity per ADR 0008
   (atomic mastery unit, not a thinker / school / discipline label)? If the
   label is a discipline name (e.g., "Political Philosophy", "Metaphysics",
   "Ontology") or a school name (e.g., "Vienna Circle", "Scholasticism") or a
   thinker-framework name (e.g., "Aristotelian Four Causes"), flag for
   granularity-mismatch review.
3. Summary authenticity: does the summary read as instructional voice with
   concept-grounded specificity, or as model-generic philosophy paraphrase?
4. Verdict + reasoning + confidence (same shape as edge verdict).
```

### Optional empirical-fortification branch (added at S-0106 per ADR 0059)

For verdicts whose **confidence is "medium"** AND **whose verdict implies a graph mutation** (reversed, weak/redundant, mis-typed: historical-not-pedagogical, mis-typed: thematic, granularity-mismatch on a node), the routine session SHOULD invoke the empirical-fortification branch using [`engine/tools/fetch_structural_reference.py`](../tools/fetch_structural_reference.py) per [ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md). For high-confidence verdicts (parametric reasoning corroborated by a clear SEP framing) the branch is *not* used — the marginal cost of fetching does not justify the additional confidence gain.

The branch is OPTIONAL because:

- High-confidence parametric verdicts (sound, with clear SEP corroboration) don't need fortification; routine sessions skip the branch.
- Low-confidence verdicts that don't imply a graph mutation are recorded as candidate findings without fortification (the closeout adjudicates whether to fortify or to leave as low-confidence in the audit record).
- Medium-confidence verdicts that DO imply a graph mutation are exactly the band where the branch reduces false-positive graph mutations the closeout would otherwise have to triage.

Procedure (per-verdict):

```
EMPIRICAL-FORTIFICATION BRANCH (optional; medium-confidence + mutation-implying verdicts):

1. Identify the canonical public Tier 4 URL for the source entry (per
   product/docs/content-strategy.md Tier 4 fetch-policy column). Routine
   sessions running unattended use only Tier 4 hosts authorized as
   "fetchable, polite, rate-limited."

2. Within an audit-session FetchSession (ephemeral lifecycle), invoke
   fetch_structural_reference.fetch_and_parse(url, "encyclopedia",
   session=session). The session bounds budget to 20 fetches by default
   and rate-limits to 2.0s per host; unattended sessions adjust via CLI
   flags only when the audit's per-task scope justifies it.

3. Read the resulting FocusingBrief — note that source-identity has been
   stripped (the brief reads as "from a public reference work," not as
   "from <publisher>"). The recursive-walk anonymization invariant
   already gated the brief; if it had failed, the tool would have raised
   AnonymizationViolation and the verdict path would HANDOFF.

4. Compare structural framing against the parametric verdict:
   - Cross-reference adjacency: does the entry link source→target as the
     parametric verdict claims, or the other direction? Cross-reference
     direction is direct evidence of the conceptual dependency the verdict
     classifies.
   - Section path: does the link sit under "Historical background" /
     "Pre-modern" / "Origins" (suggesting historical_influence) vs
     "Current theories" / "Contemporary debates" (suggesting
     pedagogical_prerequisite)?
   - Word-count and extraction confidence: high-mass linked entries vs
     incidental mentions inform whether the relationship is structural
     or peripheral.

5. Update the verdict's confidence level (now "high" if the brief
   corroborates) OR update the verdict itself (now "fortified-changed"
   if the brief contradicts; record the original parametric verdict
   alongside the post-fortification verdict for closeout adjudication).

6. The evidence file's per-edge or per-node entry records both the
   parametric verdict and the fortification result, including which
   structural cues drove the change. The brief itself is NOT persisted
   anywhere — it dies with the FetchSession's tmpdir on context exit.
```

The first exercise of this branch lands in an interactive session per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — see [`engine/build_readiness/fetch_structural_reference_first_exercise.md`](fetch_structural_reference_first_exercise.md). Subsequent routine fires use the branch freely once the gate report's Tier 1 findings are resolved.

The pre-S-0106 audit cadence (S-0104, S-0105) used parametric reasoning only and did not invoke this branch; those evidence files remain valid as parametric-only baselines, and the closeout adjudication may revisit specific medium-confidence verdicts using this branch if the user judges the cost-benefit favorable.

### Evidence file schema (fixed)

Each per-task evidence file under `engine/build_readiness/phase_5_production_audit_evidence/<task>.md` follows this shape:

```markdown
# Phase 5 production audit evidence — <subdomain or scope>

> Authored by S-XXXX (routine session) per T-PHASE-5-AUDIT task <TASK-ID>.
> SEP-anchored review per `engine/build_readiness/phase_5_production_audit.md`.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Sample metadata

- Subdomain / scope: <name>
- Edge population: <N total>
- Edge sample size: <k>; sample density: <k/N %>
- Sample selection: deterministic md5(seed='<task-id>' || source_id || '|' || target_id) ordering
- Node sample size: <m>; selection: edge-anchored union plus <p> leaf-shaped
  random nodes drawn separately
- Generation date: <ISO date>

## Sampled-edge candidate findings

### Finding E-1
EDGE: ...
SEP-ANCHORED REASONING: ...
VERDICT: <one of sound | defensible | reversed | weak | historical | thematic | other>
CONFIDENCE: <high | medium | low>
NOTES: <optional pointer to related findings, structural patterns, etc.>

### Finding E-2
...

## Sampled-node candidate findings

### Finding N-1
NODE: ...
SEP-ANCHORED REASONING: ...
VERDICT: <one of sound | granularity-mismatch | authenticity | other>
CONFIDENCE: ...
NOTES: ...

## Cross-cutting observations (optional)

Any patterns across edges/nodes in this subdomain. Treat sparingly — aggregate
patterns are the closeout's synthesis surface, not the evidence session's.

## SEP citations consulted

(Optional; useful for closeout spot-check)
- SEP entry: <title>
- SEP entry: <title>
```

The schema is intentionally simple. The routine session's job is to populate verdict + reasoning + citation fields honestly; the closeout adjudicates dispositions and synthesizes patterns.

## Sample-size policy (calibrated by S-0081 gate findings)

The S-0081 gate sampled 15 of 71 cross-bridges and found 8 substantive findings (53%). Per the approved plan's stopping rule (cross-bridge defect rate >15% triggers density expansion), per-subdomain sampling is set to **35%** for this audit, not the 25–30% baseline.

| Task | Sample (edges) | Population | Density | Node sample (edge-anchored) |
|---|---|---|---|---|
| AUDIT-CB | 71 (full census) | 71 | 100% | N/A — cross-bridges have no nodes; node coverage is via the subdomain tasks |
| AUDIT-EPI (epistemology) | 25 | 72 | 35% | ~12 |
| AUDIT-ETH (ethics) | 24 | 68 | 35% | ~12 |
| AUDIT-MET (metaphysics) | 23 | 66 | 35% | ~12 |
| AUDIT-MIN (philosophy of mind) | 25 | 70 | 35% | ~12 |
| AUDIT-LOG (logic) | 12 | 34 | 35% | ~8 |
| AUDIT-LAN (philosophy of language) | 11 | 31 | 35% | ~8 |
| AUDIT-SCI (philosophy of science) | 11 | 30 | 35% | ~8 |
| AUDIT-POL (political philosophy) | 12 | 34 | 35% | ~8 |
| AUDIT-AES (aesthetics) | 11 | 32 | 35% | ~8 |
| AUDIT-SVC (service nodes) | 10 | 28 | 35% | ~8 |
| AUDIT-HT (hubs + traces) | top-10 hubs full + 3 syllabus traces | 10 hubs + 3 targets | N/A | the 10 hub nodes themselves |

Total reviewed across all 12 evidence sessions: **71 + 164 + 30 syllabus-trace-node coverage ≈ 265 edges**, **~96 nodes**, plus the 10 hubs. Roughly **300 graph elements** under SEP-anchored review (vs the gate's 20 + topology pass).

**Sample expansion rule (within an evidence session)**: if a session's defect rate at half-sample (after first half of sampled edges reviewed) exceeds 60%, expand to 50% density rather than the baseline 35% before commit. Halt expansion at 50% to keep within session budget.

## Three diagnostic syllabus traces

Free speech is absent from the graph (S-0081 gate finding). Substituted target list:

1. **"Understand Gettier counterexamples to JTB"** (target = `gettier_problem`, epistemology). 10 unique prereq nodes / max depth 4 per gate's trace. Re-run with full edge-by-edge SEP review, recording any depth-1 prereq the trace would naturally name that's missing.
2. **"Understand modal realism"** (target = `modal_realism`, metaphysics). 7 unique prereq nodes / max depth 5 per gate's trace. Stresses 2-hop bridge resolution to set theory (service domain).
3. **"Understand the social contract"** (target = `social_contract_theory`, political). **Substitute for absent `free_speech`.** Tests cross-bridges to ethics + service-node priors. The S-0081 gate traced `justice` (1 prereq, too sparse); social_contract_theory has more upstream branching and is a richer diagnostic target. Falls within AUDIT-HT scope.

For each: re-pull the topo-sort prereq tree from live Supabase, list every node by depth, apply the SEP-anchored prompt to the chain, record:

- Syllabus length (unique nodes)
- Max depth + median depth
- Cross-domain hops along any shortest path
- Any node in the chain whose presence as prereq is questionable (cite SEP)
- Any obvious missing prereq the chain skips (cite SEP)
- Verdict on overall trace coherence

## Tier 1 / Tier 2 / Tier 3 triage

Adversarial reconnaissance per [`engine/operations/build-readiness-gate.md`](../operations/build-readiness-gate.md).

### Tier 1 — must resolve before evidence sessions begin

- **T1-A — SEP-anchored prompt template is fixed.** Verbatim in this gate report (above). Routine sessions copy-paste, do not paraphrase. Resolved at this gate.
- **T1-B — Evidence file schema is fixed.** Verbatim in this gate report (above). Routine sessions populate the named sections. Resolved at this gate.
- **T1-C — Per-subdomain sample density is 35%.** Calibrated from S-0081 gate findings. Routine sessions follow the table in §"Sample-size policy" without per-session re-decision (the within-session expansion rule is the only on-the-fly judgment). Resolved at this gate.
- **T1-D — Diagnostic-target list locked.** Gettier, modal realism, social contract theory. Free speech withdrawn (absent from graph; coverage finding recorded by gate). Routine session AUDIT-HT runs these three. Resolved at this gate.
- **T1-E — Cross-bridges run first to calibrate density.** The dependency `depends_on: [AUDIT-CB]` for all 10 subdomain tasks enforces this. AUDIT-CB's defect rate calibrates whether the per-subdomain expansion rule fires. Resolved.
- **T1-F — Closeout is interactive, not routine.** The 12 evidence tasks produce candidate findings only. Disposition (Issue filing, ADR memos, soft-warn proposals, structural-reopen memo authoring, both final reports) is the closeout's interactive scope. The routine target ends at AUDIT-HT; routines exit at step 3 thereafter. The user runs `/start-engine` for the closeout. Resolved.

### Tier 2 — within-session decision criteria the gate report bounds

- **T2-A — Within-session sample expansion rule** (`>60% mid-sample defect rate → expand to 50%, halt at 50%`). Codified above.
- **T2-B — Verdict taxonomy** (sound / defensible / reversed / weak / historical / thematic / other). Codified in the prompt template. New verdict shapes that arise at evidence-session time → record under "other" with a free-form NOTES; the closeout decides whether to add a new category for the disposition matrix.
- **T2-C — Confidence in each verdict** (high / medium / low). Codified. The closeout's user spot-check focuses on `low`-confidence findings first.
- **T2-D — Cross-cutting observations are optional.** Routine sessions write them sparingly; aggregate pattern recognition is the closeout's surface, not per-session.
- **T2-E — Empty `evidence` field on edges is graph-wide** (S-0081 finding: 0/536). Evidence sessions do NOT call this out per-edge — it's a known graph-wide gap, pre-listed in §"Audit-system-input proposals" below. Per-edge prompt does not penalize empty evidence in the verdict; the verdict is about the prerequisite claim, not the populated-evidence-text.

### Tier 3 — deferred to closeout

- **T3-A — Disposition matrix** (Issue, ADR memo, soft-warn proposal, "no action — recorded"). Plan-defined; closeout applies.
- **T3-B — Audit-system implication labels** (`gate-feasible` / `post-build-only` / `already-covered-but-missed`). Plan-defined; closeout applies. 4 pre-listed proposals (§ below) are exempt — those are already known.
- **T3-C — Structural reopens** (cross_domain_dependency / historical_influence; philosophy of religion). Plan-defined; closeout authors memos.
- **T3-D — Both final reports** (production audit + audit-system input). Closeout authors.
- **T3-E — README multi-class restructure** (Issue #26 closure). Closeout's companion edit.
- **T3-F — Optional engine ADR for the post-phase production-audit pattern**. Closeout judges whether the pattern crystallizes enough to warrant an ADR. If yes, drafts in the same session.

## Audit-system-input proposals (pre-listed; routine sessions do NOT re-derive)

Per S-0081 gate findings, four `gate-feasible` audit-system-input proposals are already known. The closeout's audit-system-input report lists these with concrete rationale; routine evidence sessions skip them — focus on subdomain content.

1. **`edge_evidence_empty` validator soft-warn.** Fires per-edge when `evidence IS NULL` and the edge is cross-domain. Universal empty across all 536 edges currently; the soft-warn would trigger Phase 6+ discipline to populate evidence on cross-bridges going forward.
2. **`discipline_label_node_at_root` validator soft-warn.** Fires when a node whose label matches a canonical subdomain name (Political Philosophy, Metaphysics, Ontology, etc.) has zero in-edges and serves as a prereq to multiple subdomain concepts. Mitigation: split or re-categorize the discipline-label-as-prereq pattern.
3. **`prereq_direction_summary_inconsistency` validator soft-warn (NLP-flagged; possibly defer).** Fires when a target node's summary mentions the source node as antecedent ("X depends on Y" pattern in source's summary). Implementation harder; closeout assesses cost-benefit.
4. **`historical_node_as_prereq_source` validator soft-warn.** Fires when a node tagged in the "history terminator" sub-class of the service subdomain (per ADR 0052 product) sources a `pedagogical_prerequisite` edge to a non-service-domain concept. Requires sub-class tagging in node schema first; concrete recommendation contingent on schema extension.

If evidence sessions surface a NEW gate-feasible class beyond these four, record it as an "other" verdict-NOTES finding; the closeout's audit-system-input synthesis incorporates.

## Structural reopen pre-flag

S-0081 gate found 4 of 15 sampled cross-bridges historical-not-pedagogical (extrapolating to ~19 of 71 — exceeds the ≥10 ADR-warranting threshold from the approved plan). Routine session AUDIT-CB will produce the full census; the closeout adjudicates with the complete data.

**Expected closeout disposition.** A fresh ADR memo proposing **activation of the reserved-but-unused `historical_influence` predicate** (per [`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md)) for cross-bridges of historical shape, with retyping of the ~19 affected edges. Likely lands as a product ADR, not engine ADR.

**Alternative dispositions** the closeout may consider:
- Maintain the S-0075 rejection of `cross_domain_dependency` AND keep the historical edges typed as `pedagogical_prerequisite` — defer the predicate refactor to Phase 6+ alongside thinker-overlay work.
- Activate `historical_influence` AND retain the historical edges in `pedagogical_prerequisite` (dual-typing is permitted by the schema). Closeout judges.

The pre-flag is recorded so AUDIT-CB's evidence session knows the cross-bridge census is the load-bearing input to this decision; the routine session does NOT propose the predicate decision itself (that's interactive judgment).

## Forward pointers to closeout

The closeout interactive session reads:

- All 12 evidence files under `engine/build_readiness/phase_5_production_audit_evidence/`
- This gate report (the methodology and pre-listings)
- [`phase_5_production_audit_gate.md`](phase_5_production_audit_gate.md) (the warrant gate's findings as input)
- [`phase_5_closeout.md`](phase_5_closeout.md) (Phase 5 build closeout — what was built)
- [ADR 0046 product](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md), [ADR 0052 product](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md), [PREDICATE_MANIFEST.md](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md)
- [`product/docs/architecture.md`](../../product/docs/architecture.md), [`product/docs/learner-model.md`](../../product/docs/learner-model.md), [`product/docs/self-correction.md`](../../product/docs/self-correction.md)
- [`engine/tools/validate.py`](../tools/validate.py) (for gate-by-gate audit-system-input synthesis)

The closeout produces:

- `engine/build_readiness/phase_5_production_audit.md` (final report — REPLACES this gate report at closeout, OR sits alongside it as a sibling; closeout decides naming)
- `engine/build_readiness/phase_5_audit_system_input.md` (audit-system synthesis)
- Issues for `bug` / `enhancement` / `tech-debt` dispositions
- Possibly: a fresh ADR memo (cross_domain_dependency / historical_influence)
- Possibly: a fresh ADR memo (philosophy of religion readmission criterion refinement)
- Possibly: a new engine ADR formalizing the post-phase production-audit pattern (T3-F)
- README index update (Issue #26 multi-class closure)

**Naming note for the closeout report**: the closeout's final production-audit report should NOT overwrite this gate report. Two options the closeout adjudicates:

- **(a)** Rename this gate report to `phase_5_production_audit_gate_for_master_plan.md` and have the closeout author `phase_5_production_audit.md` as the consolidated final report.
- **(b)** Keep this gate report as `phase_5_production_audit.md` (since it IS the master plan); the closeout authors `phase_5_production_audit_findings.md` or `phase_5_production_audit_closeout.md`.

Default recommendation: **(a)** — the term "production audit" should refer to the executed audit and its findings, not the master plan setup. But the rename touches `phase_5_production_audit.md` references; the closeout adjudicates whether the cost is worth the clarity.

## Verification (master-plan session)

Mechanical:
- This gate report committed to `engine/build_readiness/phase_5_production_audit.md`.
- `engine/session/auto_target.json` replaced with T-PHASE-5-AUDIT (12 tasks, max_sessions 14).
- Validator passes on commit (zero hard-fails; soft-warns annotated).
- STATE.md and ENGINE_LOG.md updated.

Editorial (user, on review):
- Sample-size policy table is correct (35% per-subdomain density).
- Diagnostic-target list (Gettier, modal realism, social contract) substitutes free_speech adequately.
- 4 pre-listed audit-system-input proposals capture S-0081 gate's `gate-feasible` findings.
- Tier 1/2/3 triage is honest about what's locked-at-master-plan vs deferred-to-closeout.
- The 12-task partition produces session-sized tasks (~1 hour wall-clock per the schema's authoring conventions).

If user adjudication redirects any of these (e.g., different density, different diagnostic targets, different verdict taxonomy), this gate report is amended and the auto_target.json is regenerated in a follow-up commit before the first routine evidence session fires.
