# Handoff Log

> Running log of items deferred to a future *next-session-must-resolve* transition. Not a contract; a convenience so transition sessions don't re-solve already-solved problems. Add entries here ONLY when the next session must pick up the item immediately AND it doesn't belong in a per-session changelog entry (per ADR 0092), an ADR, or a GitHub Issue (per [ADR 0048](engine/adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — cross-session deferrals route to Issues by default; HANDOFF.md is reserved for session-internal handoffs).
>
> **Disposition discipline (added at S-0036, retroactively applied to live entries at S-0041).** Every section carries a `**Disposition:**` line in one of five forms: `fixed-in-session @ <SHA>`, `deferred-with-user-confirmation`, `out-of-scope`, `not-actionable`, or `tracked-as-issue #<num>`. For resolved entries, a `**Resolved:**` line names the session and downstream artifact (ADR, per-session changelog entry, ops-doc edit, commit SHA). The `engine/tools/audit_handoff_dispositions.py` script audits new sections at session shutdown.
>
> **Prune-on-resolve discipline (added at S-0121 audit inline cleanup).** Resolved sections are pruned at the next interactive session that touches HANDOFF.md. The eight resolved sections from S-0002 / S-0033 / S-0035 / S-0041 / S-0049 / S-0051 / S-0062 / S-0064 retired at S-0121 — content preserved in git history (each section's `**Resolved:**` line named the downstream artifact: ADRs 0045 / 0055, commits `21285f8` / `ae85e20` / `6b7999c` / `2609aaf` / `ca36c17`, Issues #8 / #9 / #17 / #18, and tooling at `engine/tools/scrub_env.sh` / `load_env.py` / `apply_migration.py` / `routine_lifecycle_push.py` — all verified extant at prune time). The S-0121 audit report's User adjudication subsection carries the recommendation for an automated prune-discipline posture rule (extending `audit_handoff_dispositions.py` to flag long-resolved sections for the next interactive HANDOFF touch); downstream session executes if approved.
>
> **Scope discipline.** Add an entry here ONLY when the next session must pick up the item immediately. Cross-session deferrals (bugs, tech-debt, cleanup, enhancements, doc work, open questions, health-check findings) route to GitHub Issues with appropriate labels per ADR 0048. Resolved entries leave under the prune-on-resolve discipline above.

---

## PDG papers extraction — pre-phase deliberation plan ready for interactive pickup

**Disposition:** deferred-with-user-confirmation

**Authored:** 2026-05-14 (non-claimed interactive worktree `claude/quizzical-northcutt-91ea60`)

**Pickup target:** next interactive session (user direction: "pick this up tomorrow during interactive sessions")

**Worktree path containing artifacts (now at HEAD per S-0199):** `engine/build_readiness/pdg_papers_extraction/` (11 substantive files committed at commit `e5c34a2`; the original `quizzical-northcutt-91ea60` worktree has been removed). Session α deliverable `adr_cross_reference_map.md` added at S-0199 (commit `66d9a73`).

**Summary.** Deep extraction of two academic papers on pedagogical dependency graphs (PDGs) is complete. 12 durable artifacts in `engine/build_readiness/pdg_papers_extraction/` (all committed at HEAD as of S-0199). Plan file at [`~/.claude/plans/there-are-two-papers-parsed-aho.md`](~/.claude/plans/there-are-two-papers-parsed-aho.md) (committed to per-user plan directory, durable across sessions). MemPalace drawers migrated to engine_memory substrate at S-0193 per ADR 0091.

**Top finding (user-confirmed):** the current Paideia graph (380 nodes / 533 edges / 2 edge types) is materially under-modeled at the substrate level. 8 substrate gaps named; 17 integrated clusters of work emerged; 22 adversarial findings (3 critical landed inline in synthesis, 19 carried into Issue bodies).

**Posture — quality over speed.** User has no deadline pressure and explicitly directed `set the stage fully before stepping into the next stage`. **Do NOT fire any of the 17 Issues yet.** Run the 6-session pre-phase plan first (Sessions α-ζ described below).

**Pre-phase session sequence (interactive, in order):**

1. **Session α — Cross-reference audit** against existing 89 ADRs. Map each proposed cluster against intersecting/conflicting/extending ADRs. Output: `adr_cross_reference_map.md` in `engine/build_readiness/pdg_papers_extraction/`.
2. **Session β — Kant/phenomenology walk-through** against actual Paideia data. Walk each node and edge in the current phenomenology subgraph through the proposed schema. Output: `kant_walkthrough.md`.
3. **Session γ — Foundational reading** (Meyer & Land / Middendorf & Pace / Spiro / Falmagne et al.). Optional but high-value. Output: `foundations.md`.
4. **Session δ — Four foundational ADRs:** Phase 6 scope (4 options: A expand / B narrow / C halt / D rescope); tool-stack decision (Postgres+JSONB vs Neo4j vs other — per adversarial E.10.3 must settle before any Tier A migration); learning-outcome taxonomy; product trajectory commitment (already settled this session — Paideia is learner-facing + OSS-forkable; NO LMS-integrated tooling). Likely 2 sessions per ADR 0084 extraction-step discipline.
5. **Session ε — Adversarial residue adjudication.** User adjudicates 19 deferred findings (incorporate / escalate to own ADR / reject).
6. **Session ζ — Synthesis revision + Issue-draft revision.** Issue drafts are ready to file only after this.

**Decisions already settled in this session** (MemPalace decision drawers written for each; ADR'd progressively):

1. **Paideia product trajectory** — learner-facing + open-source/forkable; **NO LMS-integrated tooling** on projects user is directly involved with (third-party LMS integrations of the OSS graph not foreclosed). **ADR'd at S-0202 as [`product/adr/0093`](product/adr/0093-phase-6-product-trajectory-formalization.md)** with four binding commitments specialized for Phase 6 substrate work.
2. **Two-bias-surface partition** — graph-topology bias (currently uncovered) distinct from LLM-mediated bias (existing anti-bias mechanism covers a subset of input-side). Both surfaces require parallel mechanisms. (Pending ADR — likely Cluster 8 product ADR in Phase 7+ per ADR 0094 Tier-C deferral.)
3. **Contestability is atomic** — confidence (3-source) + provenance (5-field) + counterexamples + version history land as a unit; adding any one without the others produces unmoored data. (Pending ADR — Cluster 1 product ADR in Session δ₂+ per ADR 0094 Tier-A dependency order 1→2→4→3→5.)
4. **Mass-retyping default reversed** — 516 existing `pedagogical_prerequisite` edges retype to `soft_prerequisite` (NOT `hard_prerequisite`) per `paper_1:L162` expert overconfidence finding. Upgrades only after SQA validation with learner-trace evidence. (Pending ADR — Cluster 2 product ADR in Session δ₂+ per ADR 0094 dependency order.)
5. **Quality-first deliberation posture** — no Issues fire before Session ζ. (Posture, not ADR — applies through the remainder of the pre-phase sessions per pushback drawer 1dc03200.)

**Commit posture (post-S-0199 update).** All artifacts committed at HEAD; `engine/HANDOFF.md` duplicate previously deleted; engine_memory drawers (post-S-0193 migration per ADR 0091) carry the conversational substrate. The Session α deliverable lives at [`engine/build_readiness/pdg_papers_extraction/adr_cross_reference_map.md`](engine/build_readiness/pdg_papers_extraction/adr_cross_reference_map.md).

**Pre-phase progress:**

- ✅ Session α (S-0199) — cross-reference audit complete; `adr_cross_reference_map.md` authored.
- ✅ Session β (S-0200) — Kant/phenomenology walkthrough complete; `kant_walkthrough.md` authored (601 lines; 8 D1-D8 adjudication items + 4 F1-F4 reading items).
- ✅ Session γ (S-0201) — Foundational reading complete; `foundations.md` authored (473 lines; F1-F4 answered with explicit evidence-tier markers).
- 🟡 **Session δ₁ (S-0202) PARTIAL** — Two of four foundational ADRs landed: [`product/adr/0093`](product/adr/0093-phase-6-product-trajectory-formalization.md) (Product Trajectory formalization) + [`product/adr/0094`](product/adr/0094-phase-6-scope.md) (Phase 6 Scope: expand to include Tier-A substrate Clusters 1-5 before SEP/embedding self-correction). The HANDOFF "four options" framing (A expand-all-17 / B narrow-to-Tier-A / C halt / D rescope) reduced after foreclosing C (per ADR 0093 commitment b) and dropping D (underspecified); synthesis.md §"Phase 6 master-plan-input subsection" supplied the empirically-grounded binary; Option α chosen.
- 🟡 **Session δ₂ (S-0203) IN PROGRESS** — Both remaining foundational ADRs landed: [`product/adr/0095`](product/adr/0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md) (tool-stack: Postgres+JSONB+recursive CTEs confirmed; OSS Apache-2.0 + cost-priced posture raises revisit bar; amends ADR 0017) + [`product/adr/0096`](product/adr/0096-phase-6-learning-outcome-taxonomy.md) (learning-outcome taxonomy: 3-level depth + Decoding-the-Disciplines bottleneck moves as (depth_level, bottleneck_move) tuple). All four Session δ foundational ADRs (0093 + 0094 + 0095 + 0096) now landed. Q/D adjudications in progress this session (see "Session δ₂ Q/D settlements" subsection below).
- ⏳ Session δ₃+ — First Tier-A cluster-implementation ADRs (likely Cluster 1 Contestability substrate first per dependency order 1→2→4→3→5). Any remaining D-items not settled in δ₂ defer to the relevant Cluster cluster-implementation ADR author.
- ⏳ Session ε — Adversarial residue adjudication (19 deferred findings).
- ⏳ Session ζ — Synthesis revision + Issue-draft revision. Issues fire only after Session ζ.

**Session δ₂ Q/D settlements (S-0203):** captured here as a sub-list of the PDG entry (not as new HANDOFF sections — these are work-item ownership transfers to the Cluster-ADR sessions in δ₃+; cluster-ADR-authors cite the paired engine_memory `decisions`-room drawers). Each settlement closes one or more Session-α coordination questions + Session-β D-items.

- **Q1 + D1 + D2 (settled at S-0203):** `node_type` enum scope = **concept-level only** (interpretation (a) wins per ADR 0008 compatibility); `historical_context` enum value names *concept-level teaching units about historical context*, not period/tradition nodes; `node_type` is **multi-valued** (Postgres array column or JSONB array per ADR 0095 substrate). Settles Q1 (Session α / `adr_cross_reference_map.md`) + D1 + D2 (Session β / `kant_walkthrough.md` §6.7). Decisions drawer `6a55cc2a`. Downstream: Cluster 4 cluster-implementation ADR commits `nodes.node_type` as multi-valued with CHECK constraint over the concept-level enum; Cluster 5 + 8 ADRs inherit concept-level scope.
- **Q2 (settled at S-0203):** Institutional vs individual scope partition = **shipped Paideia binary stays individual-only** (ADR 0031 honored without supersession; ADR 0065 commitment 4 + ADR 0093 commitment 2 binding). OSS deployers may fork to layer institutional features on for non-Paideia-release forks per ADR 0093 commitment 2's third-party-OSS-forks-not-foreclosed framing. Settles Q2 (Session α / `adr_cross_reference_map.md`). Decisions drawer `e464bf2d`. Downstream: Cluster 15 (privacy/FERPA/NIST + override logging) drops FERPA framing and cluster-randomized-experiment shapes for Paideia release; Cluster 16 (learner-outcome evaluation infrastructure) drops `subgroup_routing_discrepancies` and per-cohort aggregations; Cluster 17 (anomalous routing detection) drops `cohort_id`-based framings. Cluster 15-17 ADRs commit narrower-but-honest individual-only shapes; OSS fork ADRs may re-introduce the dropped framings for institutional deployers.
- **Q3 (settled at S-0203):** BYOK execution-surface partition for Clusters 8, 10, 11, 14, 15 = **client-side BYOK default per ADR 0093 commitment 3 (iOS Keychain v1; web visualizer deferred to Phase 8/9)**; exceptions named per cluster. Per-cluster table: C8 (graph-topology bias mitigation) = **maintainer-side build-time + audit-time** (graph-quality audit, not learner-facing); C10 (prompt-template versioning + content store) = **maintainer-side template store + client-side BYOK invocation**; C11 (workflow instantiation) = **client-side BYOK** (per-turn LLM calls); C14 (LLM-mediated output-side bias auditing) = **client-side BYOK; opt-in toggle** (N× cost-surface multiplier; default-off per freshman-defaults posture); C15 (privacy + override logging, narrowed per Q2) = **client-side BYOK invocation + client-side or per-user-cloud-synced log storage**. Settles Q3 (Session α / `adr_cross_reference_map.md`). Decisions drawer `37ef1613`. Downstream: Cluster 8/10/11/14/15 cluster-implementation ADRs (Phase 7+) cite the per-cluster execution-surface row + cost-attribution rationale.

**Routine work unchanged.** SQA census (8 of 20 tasks done) continues firing tonight; SQA-09 next. Routine work and PDG-papers work are independent streams.

**Cross-references:**
- Plan file: [`~/.claude/plans/there-are-two-papers-parsed-aho.md`](~/.claude/plans/there-are-two-papers-parsed-aho.md)
- Worktree artifacts (uncommitted): `.claude/worktrees/quizzical-northcutt-91ea60/engine/build_readiness/pdg_papers_extraction/`
- MemPalace drawers (decisions wing): drawer IDs prefixed `drawer_paideia_decisions_` (6 written this session) + `drawer_paideia_lessons_` (2) + `drawer_paideia_pushback_` (1) + `drawer_paideia_project_` (1)
