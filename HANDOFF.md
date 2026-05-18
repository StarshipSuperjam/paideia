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

**Decisions already settled in this session** (will be ADR'd in Session δ; MemPalace decision drawers written for each):

1. **Paideia product trajectory** — learner-facing + open-source/forkable; **NO LMS-integrated tooling** on projects user is directly involved with (third-party LMS integrations of the OSS graph not foreclosed).
2. **Two-bias-surface partition** — graph-topology bias (currently uncovered) distinct from LLM-mediated bias (existing anti-bias mechanism covers a subset of input-side). Both surfaces require parallel mechanisms.
3. **Contestability is atomic** — confidence (3-source) + provenance (5-field) + counterexamples + version history land as a unit; adding any one without the others produces unmoored data.
4. **Mass-retyping default reversed** — 516 existing `pedagogical_prerequisite` edges retype to `soft_prerequisite` (NOT `hard_prerequisite`) per `paper_1:L162` expert overconfidence finding. Upgrades only after SQA validation with learner-trace evidence.
5. **Quality-first deliberation posture** — no Issues fire before Session ζ.

**Commit posture (post-S-0199 update).** All artifacts committed at HEAD; `engine/HANDOFF.md` duplicate previously deleted; engine_memory drawers (post-S-0193 migration per ADR 0091) carry the conversational substrate. The Session α deliverable lives at [`engine/build_readiness/pdg_papers_extraction/adr_cross_reference_map.md`](engine/build_readiness/pdg_papers_extraction/adr_cross_reference_map.md).

**Pre-phase progress:**

- ✅ Session α (S-0199) — cross-reference audit complete; `adr_cross_reference_map.md` authored.
- ⏳ Session β — Kant/phenomenology walk-through against actual Paideia data → `kant_walkthrough.md`.
- ⏳ Session γ — Foundational reading (Meyer & Land / Middendorf & Pace / Spiro / Falmagne et al.) → `foundations.md`.
- ⏳ Session δ — Four foundational ADRs (Phase 6 scope; tool-stack; learning-outcome taxonomy; product trajectory confirmation). Per Session α adversarial findings, Session δ must adjudicate three coordination questions BEFORE drafting individual ADRs: `node_type` enum compatibility with ADR 0008 (spans C4/C5/C8); institutional-vs-individual scope under ADR 0065 OSS pivot (spans C15/C16/C17); BYOK execution-surface per cluster (spans C8/C10/C11/C14/C15).
- ⏳ Session ε — Adversarial residue adjudication (19 deferred findings).
- ⏳ Session ζ — Synthesis revision + Issue-draft revision. Issues fire only after Session ζ.

**Routine work unchanged.** SQA census (8 of 20 tasks done) continues firing tonight; SQA-09 next. Routine work and PDG-papers work are independent streams.

**Cross-references:**
- Plan file: [`~/.claude/plans/there-are-two-papers-parsed-aho.md`](~/.claude/plans/there-are-two-papers-parsed-aho.md)
- Worktree artifacts (uncommitted): `.claude/worktrees/quizzical-northcutt-91ea60/engine/build_readiness/pdg_papers_extraction/`
- MemPalace drawers (decisions wing): drawer IDs prefixed `drawer_paideia_decisions_` (6 written this session) + `drawer_paideia_lessons_` (2) + `drawer_paideia_pushback_` (1) + `drawer_paideia_project_` (1)
