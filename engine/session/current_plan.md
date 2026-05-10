paths_to_modify: ["engine/build_readiness/phase_5_production_audit_evidence/science.md"]
criteria_addressed: [0, 1]

S-0113 routine session executing T-PHASE-5-AUDIT task AUDIT-SCI (philosophy of science, eighth routine session in the post-cleanup-batch resumption block). Authors a single deliverable evidence file at `engine/build_readiness/phase_5_production_audit_evidence/science.md` per the schema in `engine/build_readiness/phase_5_production_audit.md` §"Evidence file schema (fixed)".

Sample plan:
- Edge population: 30 within-science pedagogical_prerequisite edges (entirely from `0080_seed_science_part1.sql` — single-file P5-09 seed per master-plan §T1-B, no a/b split).
- Edge sample: 11 edges via md5(seed='AUDIT-SCI' || source_id || '|' || target_id) ordering, take first 11 → 11/30 = 36.7% (≥35% per master-plan §"Sample-size policy").
- Node sample: 8 edge-anchored nodes via md5(seed='AUDIT-SCI' || node_id) ordering of the 14-element edge-anchored union from the 11-edge sample.
- Per-edge prompt template applied verbatim from master-plan §"Per-edge prompt template" (load-bearing — cross-session consistency depends on this; SIXTH within-subdomain audit applying it).
- Per-node prompt template applied verbatim from master-plan §"Per-node prompt template".
- Routine-mode prohibition on the empirical-fortification branch holds (master-plan §"Empirical-fortification branch": routine sessions parametric-only until T1-A through T1-D close at the closeout interactive session per ADR 0053). S-0113 contributes any medium-confidence + mutation-implying verdicts to the closeout's fortification queue.

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
- AUDIT-MET (S-0109) metaphysics: 14.3% defect; 1 weak/redundant (long-distance shortcut time → mctaggarts_paradox); 2 defensible (metaontological commitments — modality → essence_metaphysical, abstract_object → possible_worlds); 2 granularity-mismatch (modality, mereology).
- AUDIT-MIN (S-0110) mind: 10.8% defect; 2 reversed (hard_problem → explanatory_gap, property_dualism → knowledge_argument — argument-vs-position directionality); 2 defensible (E-12 tools-vs-topic, E-23 school-as-target); 1 granularity-mismatch (phenomenology school/movement — first instance of school-name flag).
- AUDIT-LOG (S-0111) logic: 5% defect (LOWEST so far); 1 defensible (E-7 multi-prereq overdetermined); zero reversals; zero granularity-mismatch — formal-systems hierarchy tightly determines pedagogical direction.
- AUDIT-LAN (S-0112) language: 21% defect (HIGHEST within-subdomain so far); 2 reversed (E-2 speech_act → performative_utterance developmental-arc, E-10 deflationary_theory_of_truth → tarskis_t_schema tools-vs-position); 2 defensible (E-3 cross-tradition, E-5 property-vs-mechanism); zero granularity-mismatch.

Pattern shapes accumulated in routine block:
1. Pedagogical-direction reversal (S-0104, S-0105, S-0108, S-0110, S-0112).
2. Parallel-edge weak/redundant (S-0108, S-0109).
3. Frameworks-vs-motivations / metaontological-commitment defensible (S-0105, S-0108, S-0109).
4. Tools-vs-topic ordering (S-0109, S-0110, S-0112).
5. Argument-vs-position directionality (S-0110).
6. Multi-prereq overdetermined (S-0111).
7. Developmental-arc reversal (S-0112 NEW shape).
8. Cross-tradition prereq-strength defensible (S-0112 NEW shape).
9. Property-vs-mechanism prereq-strength defensible (S-0112 NEW shape).
10. Granularity-mismatch sub-discipline-label-with-content (S-0105, S-0108, S-0109).
11. School/movement granularity (S-0110).
12. Discipline-label-as-prereq foundation-spine pattern (S-0104, S-0112).

Philosophy-of-science substantive prediction:
- Methodology-anchored subdomain with tightly-coupled internal structure (foundation: philosophy_of_science → {method, theory, explanation}; confirmation cluster; demarcation cluster; realism cluster; etc.).
- Likely defect bands: tools-vs-position reversals (e.g., DN model is tool deflationism-of-explanation exploits); paradigm/research_programme/falsificationism cross-references where Lakatos's framework synthesizes Popper + Kuhn; reductionism vs multiple-realizability where the latter is canonically argued AGAINST the former (could be a reversal candidate). Discipline-label `philosophy_of_science` as foundation-spine source mirrors S-0112 E-6 / S-0104 patterns.
- Expected within-subdomain defect rate: somewhere between S-0111 logic 5% (formal-systems tight) and S-0112 language 21% (philosophical contestation high) — philosophy of science is methodology-anchored with some objective methodological-historical sequencing but also contested foundational positions (realism debate, demarcation debate).
