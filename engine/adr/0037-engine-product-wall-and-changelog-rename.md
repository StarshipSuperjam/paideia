# ADR 0037 — Engine / product wall; CHANGELOG.md renames to ENGINE_LOG.md

- **Status:** Superseded in part by [ADR 0092](0092-per-session-changelog-directory.md) (ENGINE_LOG-naming/structure clauses only; the engine/product wall partition remains Accepted)
- **Date:** 2026-05-01
- **Deciders:** S-0022 (Phase 1.5 → Phase 2 bridge — engine/product wall commitment)

## Context

The repository carries two concerns that share a single tree: the **engine** — the AI build apparatus the user and Claude run together to construct Paideia (session lifecycle, validators, hooks, MemPalace integration, operations docs, ADRs about how the AI works) — and the **product** — Paideia itself (curriculum content, pedagogical commitments, the eventual app). The engine exists to build the product; the two are not the same thing.

Top-level repo structure does not visually separate them. `.claude/`, `session/`, `tools/`, `docs/operations/`, `STATE.md`, `CLAUDE.md` are engine artifacts; `docs/MISSION.md`, `docs/pedagogy.md`, `docs/architecture.md`, `docs/business.md`, `docs/learner-model.md`, `docs/content-strategy.md`, the pedagogy ADRs (0001–0012) are product artifacts; `ROADMAP.md`, the `adr/` collection, the existing `CHANGELOG.md`, and `docs/` itself are mixed. A reader walking up cold cannot tell at a glance which file is which kind.

The most acute instance of the conflation is `CHANGELOG.md`. Software convention (Keep a Changelog) treats `CHANGELOG.md` as a versioned product release log. The current file contains zero product release entries and is filled with session-by-session engine work — ROADMAP cleanups, validator extensions, hook wrappers, ADR authoring, voice-contract sweeps. The file's preamble already deviates from convention by scoping itself to "state-of-record" engine artifacts, but the filename keeps the product-release promise the contents do not deliver. [ADR 0036](0036-expression-contract-for-inward-documents.md) names a four-layer trace system (ADRs / CHANGELOG / MemPalace / git) as load-bearing precondition for the inward-voice contract; in that system, the `CHANGELOG` layer carries dated narrative for material engine changes, complementary to MemPalace's conversational story and ADR-as-contract.

Two specific futures make the conflation costly to leave in place. First, Phase 9 product launch requires a learner-visible release log (App Store / TestFlight reality), and the existing `CHANGELOG.md` cannot be it — it carries hundreds of engine entries no learner should see. Second, Phase 2 (Build Plan Scaffolding) opens at S-0023 with the original Phase 2 work resequenced from S-0022, and authors per-phase `build_plan/P_*.md` chunks for Phases 3–9; every chunk references file paths, and if Phase 2 authors against a flat unpartitioned tree, every build_plan path migrates when the engine/product partition lands later — the cost compounds across 13+ build_plan files plus their downstream cross-references.

The folder hard wall (a structural partition of the tree into `engine/` and `product/` subtrees) is correct eventually but cannot be designed well now. The partition criterion (which ADR is engine, which is product, where ADR 0027 — rendering policy, *about* how the AI talks to learners — sits) is genuinely hard, and the reason it is hard is that there is no product content yet to load-test the partition against. Phase 5 (Seed Graph Build) is when the first product artifact at scale lands. Authoring the partition before Phase 5 means guessing at boundaries that should be content-tested; doing it after Phase 5 lets real product authoring grade the criteria.

## Decision

The project commits to two coupled changes, sequenced across three execution windows.

**Rename, now (S-0022).** `CHANGELOG.md` → `ENGINE_LOG.md`. The renamed file carries the same role under an honest name: dated narrative for material engine changes, the third layer in [ADR 0036](0036-expression-contract-for-inward-documents.md)'s four-layer trace system. The filename `CHANGELOG.md` is reserved for the future learner-visible product release log; the first entry lands at Phase 9 release prep. Until then the filename does not exist in the tree — the absence is the signal.

**Engine / product partition, committed now, executed after Phase 2.** The repo restructures into `engine/` and `product/` subtrees per the shape below. The commitment lands in this ADR so Phase 2's build_plan chunks (S-0023 onward) author against partition-aware paths from the start. The mechanical migration executes between Phase 2 close and Phase 5 open, in one or two dedicated sessions. Phase 5 seed-graph authoring is the partition's first content load-test; if criteria need refinement, the supersession path runs through this ADR.

Proposed shape:

```
(repo root)
├── engine/                     ← the AI build apparatus
│   ├── operations/             ← was docs/operations/
│   ├── tools/                  ← validators, hooks
│   ├── session/                ← session register + archive
│   ├── adr/                    ← engine ADRs
│   ├── ENGINE_LOG.md           ← was CHANGELOG.md
│   └── STATE.md                ← session state
├── product/                    ← Paideia content
│   ├── adr/                    ← pedagogy + product-architecture ADRs
│   ├── docs/                   ← MISSION, pedagogy, architecture, learner-model, content-strategy, business
│   ├── seed-graph/             ← Phase 5 onward
│   ├── AGENT_INSTRUCTIONS.md   ← rendering policy (product-facing)
│   └── CHANGELOG.md            ← reserved, first entry Phase 9
├── CLAUDE.md                   ← stays at root (edge-case; see below)
├── ROADMAP.md                  ← stays at root with [ENGINE] / [PRODUCT] phase markers
└── README.md                   ← stays at root; orients to both subtrees
```

Edge-case resolutions: (a) ADRs that bridge engine and product — `AGENT_INSTRUCTIONS.md` and [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) (rendering policy) are *about* how the engine talks to learners; their consumer-of-record is learner-facing prose, so they file under `product/`. The engine side cross-references. (b) `ROADMAP.md` and `README.md` stay at root as orientation surfaces — they speak to both subtrees. (c) `.claude/` and `CLAUDE.md` stay at root because Claude Code expects them there. `.claude/` is the harness's settings/commands/hooks tree; `CLAUDE.md` is the project-orientation file Claude Code auto-loads only by walking ancestor directories from cwd — a subdirectory `engine/CLAUDE.md` would not auto-load at session start (subdirectory `CLAUDE.md` files load lazily, only when files inside that subtree are touched), which would break the load-bearing boot ceremony. The wall this ADR commits to is conceptual — partition by what kind of artifact, not a physical-purity test that every engine artifact must live under `engine/`. `CLAUDE.md`'s content is engine-side; its location is determined by the harness's expectations, identical to `.claude/`'s rationale. The light-revision settling this folds into edge-case (c) at S-0024 (the migration session).

The naming choice — `ENGINE_LOG.md` over `MACHINERY_LOG.md` — matches the project's existing `/start-engine` build-mode command vocabulary directly; "machinery" is a separate posture-discipline term in [`CLAUDE.md`](../../CLAUDE.md) (`### Posture vs machinery` distinguishes rules-held-by-judgment from rules-enforced-by-validators) and overloading it onto the file would conflate two distinct concepts the project keeps separate.

## Consequences

- **The four-layer trace system survives under a renamed layer.** [ADR 0036](0036-expression-contract-for-inward-documents.md)'s posture — that governed body prose does not duplicate the trace because four redundant layers carry it — depends on the `CHANGELOG` layer continuing to function. The rename preserves the function; the layer is now `ENGINE_LOG.md` in citations. ADR 0036 light-revises in this commit to update the four-layer-system reference; its Status remains `Accepted` and a new bullet in its Consequences cites this ADR.

- **Phase 2 (Build Plan Scaffolding, opening at S-0023) authors against the committed partition shape.** `build_plan/P_*.md` chunks reference partition-aware paths: `product/seed-graph/...` for Phase 5 outputs, `engine/tools/validate.py` for validator references, `engine/operations/...` for operations docs. The partition itself does not yet exist when Phase 2 runs; the chunks anticipate it so when the migration lands the chunks need zero edits. STATE.md's S-0023 work item brief carries this constraint.

- **The migration executes after Phase 2 closes and before Phase 5 opens.** One or two sessions of mechanical `git mv` plus cross-reference updates per the shape above. `tools/validate.py` runs clean after each session. `git mv` preserves history per file. The Phase 5 seed-graph authoring is the partition's first real content load-test — if criteria need refinement, the supersession path runs through a new ADR; if the partition holds, the wall is settled before Phase 9.

- **`CHANGELOG.md` does not exist in the tree until Phase 9.** The empty filename is a deliberate signal: the product has not released anything yet. Phase 9 release prep authors the file with the v1.0.0 entry. The intermediate decision of which expression contract governs learner-visible CHANGELOG entries lands under [`OQ-OUTWARD-VOICE`](../../product/docs/tensions.md) (added S-0019), the third expression-contract gap to be settled before Phase 7 — outward product surfaces (UI labels, button text, error messages, learner-facing help, public README, App Store description, learner-visible CHANGELOG entries) need their own contract that neither [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) (Sonnet's teaching prose) nor [ADR 0036](0036-expression-contract-for-inward-documents.md) (inward documentation) covers.

- **`tools/validate.py`'s CHANGELOG check renames to `engine_log_format`.** The lightweight `[Unreleased]` header check fires on `ENGINE_LOG.md` rather than the now-missing `CHANGELOG.md`. The check's category name in `outcome_summary` rolls forward.

- **Engine procedural docs update their `CHANGELOG` references in this commit.** [`docs/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) step 4 ("Update CHANGELOG.md") becomes "Update ENGINE_LOG.md"; [`docs/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md), [`docs/operations/adr-authoring.md`](../operations/adr-authoring.md) (the ADR-vs-CHANGELOG-vs-MemPalace boundary table), [`docs/operations/mempalace-tagging-conventions.md`](../operations/mempalace-tagging-conventions.md) all update their references in the same commit.

- **`ROADMAP.md` gains explicit `[ENGINE]` / `[PRODUCT]` markers on phase headings.** Phases 0, 1, 1.5, 2 mark `[ENGINE]`; Phases 3–9 mark `[PRODUCT]` (with mixed sub-phases noted in their headings). The marker is the first installment of the partition; it makes the engine/product distinction legible at root level for the document a future session reads cold. The full structural restructure is the post-Phase-2 migration.

- **`STATE.md`, `CLAUDE.md` update their references and `STATE.md` resequences.** `STATE.md:11` four-layer reference updates. `CLAUDE.md`'s `### Two-layer decision recording`, `### Commit conventions`, and `### Posture vs machinery` sections update their CHANGELOG references. `STATE.md`'s next-session work item shifts from the original S-0022 brief (which was Phase 2 Build Plan Scaffolding) to S-0023 — Phase 2 with the constraint that build_plan chunks reference partition-aware paths.

- **MemPalace `decision` drawer pairs with this ADR.** Per the two-layer decision recording discipline, the conversational reasoning behind this decision (the user's CHANGELOG-as-conflation diagnosis, the four-layer-system pushback, the cost-projection at Phase 9, the sequenced-execution rationale, the filename defense, the Engine-over-Machinery vocabulary correction) lands as a verbatim drawer alongside this contract.

- **The folder migration's reversal cost is bounded.** If Phase 5 content reveals partition criteria the pre-content design missed, the supersession path is a new ADR plus a second `git mv` pass. The cost is one extra migration, paid against real content rather than guesses; this is preferable to designing the partition without content and discovering the same criterion-failure later under more expensive conditions.

## Supersession Amendment (S-0198 per ADR 0092)

The ENGINE_LOG-naming/structure clauses of this ADR (Decision's "Rename, now" paragraph + the `engine/ENGINE_LOG.md` row of the proposed shape + the Consequences paragraphs about `tools/validate.py`'s `engine_log_format` check + ENGINE_LOG-references-in-procedural-docs) are superseded by [ADR 0092](0092-per-session-changelog-directory.md). The single monolithic `engine/ENGINE_LOG.md` file replaces with a per-session changelog directory at `engine/changelog/<YYYY>/<S-NNNN>-<slug>.md` (schema-validated frontmatter + 50/70-line cap + aggregator-driven `[Unreleased]` synthesis). The historical 2,799-line file moves verbatim to `engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md`. The first engine-side release tag `engine-v0.1.0` cuts at S-0198.

The **engine/product wall partition** (Decision part 2 — the `engine/` / `product/` subtree shape + edge-case resolutions) **remains Accepted**. ADR 0091's wall-violation rejection of the A4 Postgres-in-Paideia-DB alternative was an independent empirical test of the wall principle that stands unmodified. The CHANGELOG.md filename reservation for Phase 9 learner-visible product release log is also unchanged — the new engine-side directory pattern does not occupy that filename.

## See also

- [ADR 0036](0036-expression-contract-for-inward-documents.md) — Expression contract for inward-facing documentation. Light-revised in this commit to update the four-layer-system reference.
- [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) — Rendering policy; the project's outward-facing expression contract. Files under `product/` in the post-Phase-2 partition because its consumer-of-record is learner-facing.
- [`docs/operations/adr-authoring.md`](../operations/adr-authoring.md) — Nygard template; ADR-vs-CHANGELOG-vs-MemPalace boundary table. Light-revised in this commit.
- [`docs/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) — Step 4 ("Update CHANGELOG.md") light-revised in this commit.
- [`docs/operations/document-voice.md`](../operations/document-voice.md) — The operational surface for [ADR 0036](0036-expression-contract-for-inward-documents.md); its four-layer-system reference in the where-the-trace-lives section is among those updated.
- [`docs/tensions.md`](../../product/docs/tensions.md) — Carries OQ-OUTWARD-VOICE (the third expression-contract gap), which governs learner-visible CHANGELOG entries when the reserved `CHANGELOG.md` filename gets its first content at Phase 9.
- [ADR 0091](0091-engine-memory-substrate-sqlite-fts5.md) — S-0188 substrate replacement empirically tests the wall principle. The MemPalace substrate replacement was scoped to live entirely under `engine/.memory/` + `engine/memory/` (gitignored SQLite file; stdlib `sqlite3`; no coupling to `paideia-dev` Supabase project) precisely because allowing engine state into the product database would have violated the wall. ADR 0091 explicitly rejected a Postgres-in-Paideia-DB alternative (A4) on wall-violation grounds.
- [ADR 0092](0092-per-session-changelog-directory.md) — S-0198. Supersedes the ENGINE_LOG-naming/structure clauses of this ADR (Supersession Amendment subsection above). Replaces the monolithic `engine/ENGINE_LOG.md` with a per-session changelog directory at `engine/changelog/<YYYY>/<S-NNNN>-<slug>.md`. The engine/product wall partition (Decision part 2) and the CHANGELOG.md filename reservation for Phase 9 remain Accepted.
