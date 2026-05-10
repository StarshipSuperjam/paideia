paths_to_modify: ["engine/build_readiness/phase_5_production_audit_evidence/political.md"]
criteria_addressed: [0, 1]

S-0114 routine session executing T-PHASE-5-AUDIT task AUDIT-POL (political philosophy, ninth routine session in the post-cleanup-batch resumption block). Authors a single deliverable evidence file at `engine/build_readiness/phase_5_production_audit_evidence/political.md` per the schema in `engine/build_readiness/phase_5_production_audit.md` §"Evidence file schema (fixed)".

Sample plan:
- Edge population: 34 within-political pedagogical_prerequisite edges (entirely from `0100_seed_political_philosophy_part1.sql` — single-task P5-05 seed per master-plan §T1-B, no a/b split).
- Edge sample: 12 edges via md5(seed='AUDIT-POL' || source_id || '|' || target_id) ordering, take first 12 → 12/34 = 35.3% (≥35% per master-plan §"Sample-size policy").
- Node sample: 8 edge-anchored nodes via md5(seed='AUDIT-POL' || node_id) ordering of the 18-element edge-anchored union from the 12-edge sample.
- Per-edge prompt template applied verbatim from master-plan §"Per-edge prompt template" (load-bearing — cross-session consistency depends on this; SEVENTH within-subdomain audit applying it after EPI/ETH/MET/MIN/LOG/LAN/SCI).
- Per-node prompt template applied verbatim from master-plan §"Per-node prompt template".
- Routine-mode prohibition on the empirical-fortification branch holds (master-plan §"Empirical-fortification branch": routine sessions parametric-only until T1-A through T1-D close at the closeout interactive session per ADR 0053). S-0114 contributes any medium-confidence + mutation-implying verdicts to the closeout's fortification queue.

Verdict scope (candidate findings only — disposition deferred to closeout per master-plan §"Anti-scope"):
- No Issues filed at this routine layer for content findings (closeout's surface).
- No HANDOFF entries for content findings (closeout's surface).
- No ADR drafts (closeout's surface).
- No master-plan revision via this session (interactive-only per CLAUDE.md routine-mode posture).

Deliverable scope: single .md file under the named path. Operational allowlist (engine/session/current.json, current_plan.md, auto_target.json status fields, archive, ENGINE_LOG.md, register_state.json, HANDOFF.md, STATE.md) is permitted by routine-mode posture and check_routine_scope.py --staged at commit time.

Prior-context-from-diary surfaced via MemPalace boot search:
- AUDIT-CB (S-0104) cross-bridge baseline: 35.2% substantive-defect rate; reversal cluster B (within-philosophy bridges); 14 historical-not-pedagogical findings in service-domain history-terminator class.
- AUDIT-EPI (S-0105) within-subdomain baseline: 5.4% substantive-defect rate; 1 reversed (problem_of_induction → pyrrhonian_skepticism); 1 granularity-mismatch (bayesian_epistemology); 2 defensible (frameworks-vs-motivations dialectical-ordering pattern).
- AUDIT-ETH (S-0108) ethics: 16.7% defect; 1 reversal (animal_ethics → sentientism); 2 weak/redundant (parallel-edge species-shadowing-genus pattern); 2 granularity-mismatch (sub-discipline-label-with-content pattern).
- AUDIT-MET (S-0109) metaphysics: 14.3% defect; 1 weak/redundant (long-distance shortcut); 2 defensible (metaontological commitments); 2 granularity-mismatch (modality, mereology).
- AUDIT-MIN (S-0110) mind: 10.8% defect; 2 reversed (argument-vs-position directionality); 2 defensible; 1 granularity-mismatch (phenomenology school/movement).
- AUDIT-LOG (S-0111) logic: 5% defect (LOWEST so far); 1 defensible; zero reversals; zero granularity-mismatch — formal-systems hierarchy tightly determines pedagogical direction.
- AUDIT-LAN (S-0112) language: 21% defect (HIGHEST within-subdomain so far); 2 reversed (developmental-arc; tools-vs-position); 2 defensible; zero granularity-mismatch; discipline-label-as-prereq pattern flagged on philosophy_of_language foundation-spine edges.
- AUDIT-SCI (S-0113) science: 1 reversed (paradigm → theory_ladenness developmental-arc); discipline-label-as-prereq pattern flagged on philosophy_of_science foundation-spine edges; otherwise sound — methodology-anchored subdomain has objective sequencing.

Pattern shapes accumulated in routine block:
1. Pedagogical-direction reversal (S-0104, S-0105, S-0108, S-0110, S-0112, S-0113).
2. Parallel-edge weak/redundant (S-0108, S-0109).
3. Frameworks-vs-motivations / metaontological-commitment defensible (S-0105, S-0108, S-0109).
4. Tools-vs-topic ordering (S-0109, S-0110, S-0112).
5. Argument-vs-position directionality (S-0110, S-0113 PMI counterexample-direction-canonical).
6. Multi-prereq overdetermined (S-0111).
7. Developmental-arc reversal (S-0112, S-0113).
8. Cross-tradition prereq-strength defensible (S-0112).
9. Property-vs-mechanism prereq-strength defensible (S-0112).
10. Granularity-mismatch sub-discipline-label-with-content (S-0105, S-0108, S-0109).
11. School/movement granularity (S-0110).
12. Discipline-label-as-prereq foundation-spine pattern (S-0104, S-0112, S-0113).

Political-philosophy substantive prediction:
- Position-family-rich subdomain (liberalism, libertarianism, communitarianism, republicanism, conservatism, socialism, multiculturalism — seven competing political traditions in the seed). Position-family granularity is concept-level per S-0109 N-3 / S-0110 N-1 / S-0110 N-12 (analogous to physicalism, dualism in mind/metaphysics).
- Likely defect bands: position-vs-position direction questions (e.g., communitarianism is articulated as a critique of liberalism — is liberalism a prereq for communitarianism canonical, or is the dialectical relationship more symmetric?); discipline-label-as-prereq pattern on political_philosophy foundation-spine edges (mirrors S-0112 E-6 / S-0113 E-2/E-3 patterns); tools-vs-topic candidates (justice_as_fairness as Rawls's specific theory vs distributive_justice as the broader topic).
- Expected within-subdomain defect rate: somewhere in the moderate band (similar to S-0108 ethics at 16.7%, S-0109 metaphysics at 14.3%) — political philosophy has both objective historical-conceptual sequencing (state → sovereignty; natural rights → human rights; social contract authors in chronological order) and substantive philosophical contestation about position-family relations.
