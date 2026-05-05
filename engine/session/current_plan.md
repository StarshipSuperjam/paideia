paths_to_modify: ["product/seed-graph/migrations/0036_*.sql", "product/seed-graph/migrations/ROUTING.md"]
criteria_addressed: [0, 1]

Author `product/seed-graph/migrations/0036_seed_metaphysics_part1.sql` for task P5-02b "Metaphysics specialized seed" of target T-PHASE-5 per `engine/build_readiness/phase_5.md` T1-B (the b-half of the metaphysics pre-split). The four specialized clusters phase_5.md T1-B explicitly defers to P5-02b are: modality (with possible-worlds machinery), free will, properties/universals, and mereology. Targeting ~25 nodes + ~35 within-domain `pedagogical_prerequisite` edges at the granularity principle, mirroring the density of the analog b-half P5-01b (26 nodes / 38 edges; 21 cross-references from a-half + 17 within-cluster).

Cluster decomposition (within scope_lock):

- **Modality (~7 nodes):** `modality`, `possible_worlds`, `modal_realism`, `ersatz_modal_realism`, `essence_metaphysical`, `haecceity`, `counterpart_theory`. Anchors: Lewis's *On the Plurality of Worlds*, Plantinga / Stalnaker ersatzism, Fine 1994 essence-as-non-modal, Lewis's counterpart theory replacing transworld identity.
- **Free will (~7 nodes):** `free_will`, `determinism`, `compatibilism`, `incompatibilism`, `libertarianism_metaphysical` (the metaphysical position, not the political one), `moral_responsibility`, `principle_of_alternative_possibilities`. Anchors: classical compatibilism (Hume / Frankfurt / Wolf / Fischer), incompatibilist libertarianism (Kane / O'Connor), PAP and Frankfurt-style cases.
- **Properties / Universals (~5 nodes):** `universals`, `realism_about_universals`, `nominalism`, `tropes`, `bundle_theory`. Anchors: Plato + Armstrong realism, Williams 1953 + Campbell tropes, class/predicate nominalism, bundle theory as the substance-rejecting alternative.
- **Mereology (~6 nodes):** `mereology`, `composition_mereological`, `simples`, `gunk`, `mereological_universalism`, `mereological_nihilism`. Anchors: classical extensional mereology, Lewis / Sider universalism, van Inwagen's "Material Beings" near-nihilism.

Edge structure (~35 edges, all `pedagogical_prerequisite`, all within-domain):

- Within-cluster forward edges (~21): modality → possible_worlds; possible_worlds → modal_realism / ersatz_modal_realism / counterpart_theory / haecceity; modality → essence_metaphysical; free_will → determinism / compatibilism / incompatibilism / moral_responsibility / principle_of_alternative_possibilities; incompatibilism → libertarianism_metaphysical; universals → realism_about_universals / nominalism / tropes; tropes → bundle_theory; mereology → composition_mereological; composition_mereological → simples / gunk / mereological_universalism / mereological_nihilism.
- Cross-references from P5-02a (~14): existence → modality (modality is about modes of being); abstract_object → possible_worlds (one canonical analysis); numerical_identity → counterpart_theory + haecceity (transworld identity question); causation → free_will + determinism (free will is grounded in causal structure); property → universals + realism_about_universals + nominalism + tropes; substance → bundle_theory (bundle theory denies substance); concrete_object → mereology + composition_mereological; temporal_parts → mereology (temporal parts are mereological); numerical_identity → mereology (composition-as-identity).

All edges flow forward (P5-02a → P5-02b, never P5-02b → P5-02a). Within-cluster edges are tree-shaped per cluster. No cycles by construction; validate.py's Kosaraju SCC check confirms post-apply.

Cross-cutting decisions (mirroring S-0054 P5-02a):

- `confidence_level`: 100% INTERPRETED (well above the 70% INTERPRETED floor per phase_5.md T2-B). EXTRACTED 0% (no SEP/IEP prose lifted per ADR 0011); SYNTHETIC 0% (every concept is well-named in SEP/IEP entry inventory and contemporary analytic literature explicitly names each).
- `domain[]` cardinality 1 ('metaphysics') for all 25 nodes per phase_5.md T2-G #4. Cross-domain reach (modality → modal logic in P5-03; possible_worlds → philosophy of language P5-08 on Kripke semantics; free_will → ethics P5-04a on moral responsibility; mereology → philosophy of science P5-09 on composition in physics) lands at P5-11 cross-bridges per phase_5.md T2-G #1.
- `provenance`: 'ai-seed' for all nodes and edges.
- `graph_version`: read at session boot (expected 4 post-S-0054; verify via Supabase MCP `execute_sql` on `public.settings` before authoring); UPDATE writes 5 in the same transaction; every node and edge carries `graph_version_added = 5` per ROUTING.md "graph_version increment contract".
- `PREDICATE_MANIFEST.md` not edited (only `pedagogical_prerequisite` used; already in v1 registry per phase_4_graph_validation.md T2-G).

Append ROUTING.md per-session narrative entry under the existing S-0054 entry (the operational allowlist permits ROUTING.md edits via the task scope_lock; the narrative is the long-form audit trail per ROUTING.md "Per-session narrative").

Apply the migration via Supabase MCP `apply_migration` (the canonical seed-chunked-authoring workflow per `engine/operations/seed-chunked-authoring.md` step 6). Run `engine/tools/validate.py` with venv Python (per Issue #14's auto-reexec fix at commit 983ff7d) so the live graph audit engages. Verify both criteria pass via `python3 engine/tools/check_target.py --task-id P5-02b`.

Two-commit pattern per S-0053 procedural finding adopted at S-0054: deliverable commit (0036_*.sql + ROUTING.md narrative) lands separate from the auto_target.json status-flip commit so the staged scope-check engages on deliverables under the in_progress task.

Criteria mapping:

- Criterion 0 (`migration_applied: 0036_seed_metaphysics_part1`): satisfied by Supabase MCP `apply_migration` writing to `supabase_migrations.schema_migrations.name`.
- Criterion 1 (`validate_passes`): satisfied by `engine/tools/validate.py` returning zero hard-fails. Soft-warns expected (missing_rigor_score for the partial-seed shape; issue_collision carryover from #1, #2 upstream + open project Issues; orphan_leaf may fire if any leaf in the new seed is genuinely terminal — likely zero given heavy cross-references) recorded in `outcome_summary_soft_warns`.

Out of scope (deferred):

- Cross-domain edges (P5-11 cross-bridges).
- Specialized concepts beyond the four clusters phase_5.md T1-B names — e.g., dispositions (already touched by causal_powers in P5-02a; deeper unfolding into Bird / Mumford-Anjum is not warranted here), structural realism (philosophy of science territory), four-categories ontology (deeper Lowe metaphysics — not at the canonical-coverage layer).
- PREDICATE_MANIFEST.md edits (no new predicate types used).
- 0037-0039 sub-range slots (granularity principle achieved within 0036; sub-range remains reserved for future Phase 6+ extension if telemetry warrants).
- Master plan revisions, rogue scope expansion, destructive operations.
