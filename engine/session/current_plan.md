paths_to_modify: ["product/seed-graph/migrations/0070_seed_language_part1.sql", "product/seed-graph/migrations/ROUTING.md"]
criteria_addressed: [0, 1]

# Plan: P5-08 Philosophy of language seed (T-PHASE-5)

## Why these paths address these criteria

The task `P5-08` has criteria `[migration_applied: 0070_seed_language_part1, validate_passes]`. Both criteria are objective and runnable per `engine/build_readiness/phase_5.md` T2-E: migration-applied + validate-passes is the universal subdomain-task gate. Authoring the migration file in the assigned `0070-0079` sub-range and applying it via `engine/tools/apply_migration.py` (per ADR 0055) records the row in `supabase_migrations.schema_migrations` that `check_target.py --task-id P5-08` reads to satisfy criterion 0; criterion 1 (`validate_passes`) is the standard expectation for any clean Phase 5 commit. The ROUTING.md per-session-narrative entry is the per-session audit trail per the contract at the top of `product/seed-graph/migrations/ROUTING.md`. PREDICATE_MANIFEST.md is in `scope_lock` but will not be edited — only `pedagogical_prerequisite` is used (already in v1 registry per phase_4_graph_validation.md T2-G). Sub-range slots `0071-0079` left reserved for any future Phase 6+ extension; this seed completes P5-08 at the granularity principle within the single 0070 file (philosophy of language is dominated by analytic-tradition core per phase_5.md T1-B rationale and is a single-task subdomain).

## Deliverable shape

`0070_seed_language_part1.sql` — one Phase 5 seed migration following `0046_seed_mind_part1.sql` and `0030_seed_metaphysics_part1.sql` as structural references. ~28 nodes covering the analytic-tradition core of philosophy of language at the granularity principle, organized into eight coverage clusters:

- **Foundation (5)**: philosophy_of_language, meaning, reference, sense_and_reference (Frege 1892), proposition.
- **Reference and names (6)**: proper_name, descriptivism, causal_theory_of_reference (Kripke 1972 / Putnam 1975), rigid_designator (Kripke), definite_description, russells_theory_of_descriptions (Russell 1905).
- **Meaning theories (4)**: truth_conditional_semantics (Davidson 1967), use_theory_of_meaning (Wittgenstein PI), verificationism (logical-positivist criterion of meaning), compositionality_semantic (Frege; Davidson).
- **Speech acts & Gricean pragmatics (5)**: speech_act (Austin / Searle), performative_utterance (Austin 1955), gricean_maxims (Grice 1975), conversational_implicature (Grice), presupposition (Strawson 1950 / Stalnaker).
- **Externalism (3)**: semantic_externalism (Putnam 1975 / Burge 1979), twin_earth (Putnam's thought experiment), narrow_content.
- **Indexicality & context (2)**: indexical, character_and_content (Kaplan 1989 two-dimensional semantics).
- **Truth in language (2)**: deflationary_theory_of_truth (Ramsey / Quine / Horwich), tarskis_t_schema (Tarski 1933).
- **Adjacent (1)**: linguistic_relativity (Sapir-Whorf hypothesis as the philosophically loaded edge case where philosophy of language meets philosophy of mind / cognitive science).

~35 within-domain `pedagogical_prerequisite` edges in a layered DAG rooted at philosophy_of_language → meaning, reference. Cross-domain edges deferred to P5-11 per phase_5.md T2-G #1 (concepts that bridge: causal_theory_of_reference ↔ metaphysics on natural kinds; semantic_externalism ↔ philosophy of mind on content externalism, and ↔ epistemology on the asymmetry of self-knowledge; speech_act / conversational_implicature ↔ political philosophy on hate-speech and silencing; tarskis_t_schema ↔ logic; indexical ↔ philosophy of mind on de se attitudes).

`ROUTING.md` — append one per-session narrative entry under the existing chronological sequence (the entry preceding will be S-0070 / 0046_seed_mind_part1.sql). Entry documents the cluster inventory, edge structure, `graph_version` increment (12 → 13), `confidence_level` distribution (28/28 INTERPRETED), cross-domain deferrals, and forward-pointer to remaining pending P5-09 (Philosophy of science), P5-10 (Service nodes), P5-11 (Cross-bridges), P5-12 (Closeout).

## Execution shape

1. Eager-claim S-0071 (this routine session).
2. Author the migration file with the `engine/operations/migration-discipline.md` contract block (Purpose / Loads / Preconditions / Postconditions / Invariants / Non-responsibilities / Cross-cutting decisions / Rollback / See also) preceding `BEGIN; ... COMMIT;`.
3. Append ROUTING.md per-session narrative.
4. Stage the migration + ROUTING.md and commit (deliverable commit; two-commit pattern per S-0054 procedural finding).
5. Apply the migration via `engine/tools/apply_migration.py product/seed-graph/migrations/0070_seed_language_part1.sql` per ADR 0055 (third post-S-0066 routine-mode load-bearing exercise of the wrapper; first P5-07a/S-0066, second P5-06/S-0068, third P5-07b/S-0070, this fourth).
6. Run `python3 engine/tools/check_target.py --task-id P5-08`; both criteria expected to pass.
7. Mark P5-08 `complete` in `auto_target.json` (status-flip commit).
8. Run `python3 engine/tools/validate.py` for telemetry.
9. Standard shutdown sequence: STATE.md update, ENGINE_LOG entry, archive S-0071 to `engine/session/archive/S-0071.json`, final commit + push.

## Confidence_level composition target

100% INTERPRETED (28/28). Per phase_5.md T2-B the floor is INTERPRETED ≥ 70%; the ceiling is SYNTHETIC ≤ 20%. EXTRACTED is reserved for nodes whose definition is directly lifted from a structural reference's entry inventory; this seed authors original pedagogical prose for every summary and teaching_notes per ADR 0011 so EXTRACTED is 0%. SYNTHETIC is also 0% because every concept here is well-named in the SEP/IEP entry inventory and corresponds to a concept the contemporary analytic philosophy-of-language literature explicitly names. Mirrors the eleven prior Phase 5 subject seeds.

## Sub-range slots reserved

`0071-0079` left available for Phase 6+ telemetry-driven extensions (e.g., specific topics in philosophy of language warranting follow-on seeding: pejoratives and slurs, metaphor and figurative language, fictional discourse, generic statements, dynamic semantics, formal pragmatics extensions, contextualism in semantics).

## End state

- `0070_seed_language_part1.sql` applied; `supabase_migrations.schema_migrations` carries the row.
- `auto_target.json[tasks][P5-08].status == "complete"`.
- `check_target.py --task-id P5-08` exit 0 with both criteria pass.
- `graph_version` incremented 12 → 13.
- ROUTING.md narrative section grown by one entry.
- `S-0071.json` archived; register_state.json reflects `last_claimed: S-0071, current_status: closed`.
- Eligible-task tier remaining: P5-09 Philosophy of science, P5-10 Service nodes (still parallel-eligible after P5-01a). P5-11 Cross-bridges and P5-12 Closeout remain blocked on their dep chains.
