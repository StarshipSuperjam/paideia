paths_to_modify: ["product/seed-graph/migrations/0100_seed_political_philosophy_part1.sql", "product/seed-graph/migrations/ROUTING.md"]
criteria_addressed: [0, 1]

Routine task P5-05 (Political philosophy seed) of target T-PHASE-5. Eighth routine-mode session against `engine/session/auto_target.json`. P5-05's `depends_on: ["P5-01a"]` was satisfied at S-0050 (epistemology core). The routine eligibility walk picks P5-05 as the first pending task in walk order after P5-04b closed at S-0059.

Author `0100_seed_political_philosophy_part1.sql` with ~28 nodes + ~34 within-domain `pedagogical_prerequisite` edges covering the canonical political-philosophy curriculum:

- **Foundation (1):** political_philosophy.
- **Theories of justice (8):** justice (umbrella), distributive_justice, justice_as_fairness (Rawls 1971), libertarianism_political (Nozick 1974), communitarianism (MacIntyre/Sandel/Walzer), capability_approach (Sen/Nussbaum), luck_egalitarianism (Cohen/Arneson/Dworkin), desert_theory_political.
- **State, authority, legitimacy (6):** state_political, sovereignty (Bodin/Hobbes), political_authority, political_legitimacy, social_contract_theory (Hobbes/Locke/Rousseau), political_obligation.
- **Liberty, equality, rights (7):** liberty_political (Berlin 1958 negative-vs-positive), equality_political, human_rights, natural_rights (Locke), positive_rights, negative_rights, toleration (Locke/Mill/Rawls).
- **Government and political ideologies (6):** democracy, liberalism, republicanism (Pettit non-domination), conservatism (Burke), socialism, multiculturalism (Kymlicka group-differentiated rights).

Compose 100% INTERPRETED (mirrors P5-01a/P5-01b/P5-02a/P5-02b/P5-03/P5-04a/P5-04b distribution; well above 70% INTERPRETED floor per phase_5.md T2-B). 0% EXTRACTED (no SEP/IEP prose lifted per ADR 0011). 0% SYNTHETIC (every concept well-named in SEP/IEP entry inventory and contemporary analytic political-philosophy literature — Rawls, Nozick, Sen, Nussbaum, Cohen, Berlin, Locke, Hobbes, Rousseau, Mill, Burke, Pettit, MacIntyre, Sandel, Walzer, Kymlicka, Dworkin, Bodin, Marx).

All ~34 edges within-domain (every node tagged `political`); cross-domain bridges to ethics (contractualism→justice_as_fairness; deontology→natural_rights; consequentialism→utilitarian-democratic-theory), to epistemology (political_legitimacy→justification), to philosophy of language (consent→speech-act theory), to metaphysics (sovereignty→authority ontology), to philosophy of mind (rational agency→consent), and to philosophy of science (climate ethics → policy under uncertainty crosswalks) all defer to P5-11 cross-bridges per phase_5.md T2-G #1.

5- or 6-tier layered DAG; every edge from lower tier to higher tier so validate.py's Kosaraju SCC check confirms no-cycle post-apply across the cumulative subgraph (0011, 0016, 0030, 0036, 0090, 0020, 0026 + this).

PREDICATE_MANIFEST.md not edited (only `pedagogical_prerequisite` used; already in v1 registry). ROUTING.md per-session narrative entry appended documenting the cluster decomposition, edge structure, graph_version increment, cross-domain deferrals, and apply mechanics.

graph_version increment 8 → 9 honored per ROUTING.md "graph_version increment contract" (verify settings.graph_version = 8 at boot via Supabase MCP execute_sql; UPDATE settings to 9 in same transaction as 62 INSERTs; every node/edge carries graph_version_added = 9). Apply via Supabase MCP — chunked `execute_sql` (UPDATE settings; INSERT first half nodes; INSERT second half nodes; INSERT all edges) + final `apply_migration` marker call (no-op SELECT 1 body) recording the migration name in `supabase_migrations.schema_migrations` so the `check_target.py` `migration_applied` predicate passes — pattern continued from S-0058/S-0059.

Pre-apply SQL escape-bug sweep across non-comment lines via `awk '/^--/ {next} 1' | grep "[a-zA-Z]'[a-zA-Z]"` to catch unescaped single quotes inside SQL string literals (Mackie's-pattern bug from S-0058 caught and fixed pre-apply).

Verify with `python3 engine/tools/check_target.py --task-id P5-05` (both `migration_applied` and `validate_passes` criteria); run `python3 engine/tools/validate.py` with venv Python so live graph audit engages.

Two-commit pattern per S-0053/S-0054/S-0056/S-0057/S-0058/S-0059 procedural finding: deliverable commit (migration + ROUTING.md) split from auto_target.json status-flip commit so the staged scope-check engages on deliverables under the in_progress task.

End state: P5-05 status `complete` in auto_target.json; both criteria pass; graph_version 8→9; live totals 188 nodes / 240 edges → 216 nodes / 274 edges. Sub-range slots 0101-0109 left reserved (granularity principle achieved within 0100). Forward state: P5-06 Aesthetics next pending in walk order with `depends_on: ["P5-01a"]` already satisfied.

phase: P_5
