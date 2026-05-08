-- Migration: 0100_seed_political_philosophy_part1
-- Purpose: Eighth Phase 5 seed migration (first political-philosophy file) —
--   political-philosophy concepts and within-domain pedagogical_prerequisite
--   edges. Authored in S-0061 against task P5-05 "Political philosophy
--   seed" of target T-PHASE-5 per engine/build_readiness/phase_5.md (gate
--   report) and product/adr/0052-phase-5-philosophy-subdomain-decomposition.md.
--   Covers four clusters that span the canonical analytic political-
--   philosophy curriculum: theories of justice (Rawls 1971 / Nozick 1974
--   / Sen 1980 - Nussbaum 2000 / Cohen-Arneson-Dworkin luck-egalitarian
--   refinement / MacIntyre-Sandel-Walzer-Taylor communitarian critique /
--   Miller 1999 desert), state and authority (Bodin 1576 / Hobbes 1651
--   sovereignty; political authority and its companion concepts of
--   legitimacy and obligation; the social-contract tradition through
--   Hobbes-Locke-Rousseau and Rawls's modern resuscitation), liberty
--   and rights (Berlin 1958 negative-vs-positive liberty; the
--   distinction between negative-and-positive rights; Lockean natural
--   rights extending into the modern human-rights framework; Locke 1689
--   / Mill 1859 / Rawls 1993 toleration), and forms of government and
--   political ideologies (democracy as popular self-government;
--   liberalism as the canonical commitment to individual liberty and
--   limited government; Pettit 1997 republicanism as freedom-as-non-
--   domination; Burke 1790 conservatism as traditional authority and
--   organic society; socialism as collective ownership for distributive
--   equality; Kymlicka 1995 multiculturalism as group-differentiated
--   rights and recognition). P5-05 is single-task (not pre-split a/b)
--   per phase_5.md T1-B; the entire political-philosophy subdomain seed
--   lands in this one migration.
-- Loads tables: public.nodes (28 INSERTs), public.edges (34 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 8 -> 9).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 8 at session boot (post-S-0059; verified
--     via Supabase MCP execute_sql at S-0061 boot before authoring this
--     migration). The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 9 (the
--     post-increment value).
--   * P5-01a epistemology core seed applied (0011) — depends_on
--     dependency satisfied since S-0050. P5-05 has no other Phase 5
--     dependencies; political-philosophy concepts are introduced de novo
--     in this seed, independent of metaphysics, ethics, mind, language,
--     or science inventories. Cross-domain bridges into ethics
--     (contractualism → justice_as_fairness; deontology → natural_rights;
--     utilitarianism → distributive_justice via welfare-maximization
--     theories of distribution; supererogation → political_obligation),
--     into logic (deontic_logic → political_authority on the formal
--     logic of obligation; conditional_logic → political_obligation
--     for nested duty-bearing claims), into epistemology (knowledge,
--     justification → political_legitimacy on epistemic theories of
--     democracy; testimony → multiculturalism on epistemic
--     marginalization), into philosophy of language (speech-act theory
--     → consent-grounding of political_obligation; performatives →
--     declarations of independence and constitution-making), into
--     metaphysics (sovereignty → authority ontology; group_agency →
--     multiculturalism on collective rights-bearers), and into
--     philosophy of mind (rational_agency → consent; collective_
--     intentionality → social_contract_theory) all defer to P5-11
--     cross-bridges per phase_5.md T2-G #1.
--   * No prior migrations under prefix 0100-0109; this is the first
--     political-philosophy seed file.
-- Postconditions:
--   * 28 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'political'}, status=active, graph_version_added=9.
--   * 34 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=9. All edges are
--     within-domain (source and target both tagged political);
--     cross-domain edges are P5-11's exclusive responsibility.
--   * settings.graph_version = 9.
-- Postcondition-Assertions:
--   (Layer 2.5 per ADR 0039 amendment landed at S-0094 / Issue #23.
--   Empirical verification of the prose Postconditions above against
--   the live DB after body apply. ON CONFLICT skip / partial INSERT /
--   silent FK rollback would surface as exit 8.)
--   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = 9 AND 'political' = ANY(domain) :: 28
--   SELECT count(*)::int FROM public.edges WHERE graph_version_added = 9 AND edge_type = 'pedagogical_prerequisite' :: 34
--   SELECT graph_version FROM public.settings WHERE id = 1 :: 9
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract). The
--     `_political` suffix is used for nodes whose unsuffixed name is
--     plausibly ambiguous outside the political-philosophy subdomain
--     (state_political — already taken by U.S. state government /
--     ontological state in metaphysics; liberty_political — Frankfurt-
--     style mental-liberty in philosophy of mind; equality_political —
--     mathematical equality / metaphysical identity; libertarianism_
--     political — distinct from libertarianism about free will in
--     metaphysics; political_authority and political_legitimacy and
--     political_obligation and political_philosophy carry the prefix
--     for clarity in cross-domain disambiguation; desert_theory_
--     political — distinct from desert in epistemology;
--     justice_bioethical — already in P5-04b for medical-ethics
--     allocation, so the bare `justice` here disambiguates to political-
--     philosophy distributive justice; autonomy_bioethical — already
--     in P5-04b for medical-ethics consent, so political-philosophy
--     autonomy themes route through liberty_political and natural_rights
--     here). Bare nodes (justice, sovereignty, democracy, liberalism,
--     republicanism, conservatism, socialism, multiculturalism,
--     toleration, communitarianism, capability_approach, luck_
--     egalitarianism, justice_as_fairness, social_contract_theory,
--     positive_rights, negative_rights, natural_rights, human_rights,
--     distributive_justice) are unambiguous because no other subdomain
--     claims those concepts at this seed phase. Note: the bare
--     `liberalism` here is the political-philosophy doctrine; the
--     epistemic / pragmatic / methodological uses of "liberalism"
--     elsewhere in philosophy are not inventoried as separate concepts
--     in any prior P5 seed.
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also
--     inserts. Like P5-03 (logic), P5-05 has no a/b split and is
--     internally self-contained — every prerequisite edge resolves
--     within the 28 nodes inserted here.
--   * No edge cycles in the pedagogical_prerequisite subgraph. The
--     dependency graph is layered into 6 tiers:
--     T0: political_philosophy.
--     T1: justice, state_political, liberty_political, equality_
--       political, social_contract_theory.
--     T2: distributive_justice, sovereignty, political_authority,
--       negative_rights, positive_rights, natural_rights, liberalism,
--       republicanism.
--     T3: justice_as_fairness, libertarianism_political,
--       communitarianism, capability_approach, desert_theory_political,
--       democracy, political_legitimacy, political_obligation,
--       human_rights, toleration, socialism.
--     T4: luck_egalitarianism, conservatism, multiculturalism.
--     Every edge below points from a lower-tier source to a higher-
--     tier target. validate.py's Kosaraju SCC check confirms post-apply
--     that the pedagogical_prerequisite subgraph remains acyclic
--     globally (the 0011 / 0016 / 0030 / 0036 / 0090 / 0020 / 0026
--     prior seeds plus this one's 34 edges, all together).
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds
--     trivially (no duplicate triples in the INSERT block).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach include: justice_as_fairness bridges to
--     ethics (P5-04a's contractualism is the interpersonal-ethics
--     counterpart Scanlon 1998 develops; Rawls 1971 explicitly uses
--     contractualist apparatus in the political domain); political_
--     legitimacy and political_obligation bridge to ethics (the
--     normative grounding of authority depends on first-order moral
--     theory — consequentialist legitimation through beneficial
--     consequences, deontological legitimation through respect-for-
--     persons, virtue-theoretic through enabling civic flourishing);
--     natural_rights bridges to ethics (deontology's agent-centered
--     restrictions are often grounded in natural-rights metaphysics);
--     political_authority and political_obligation bridge to logic
--     (P5-03's deontic_logic is the formal apparatus for ought-claims
--     about political duties; Chisholm's contrary-to-duty paradox bears
--     on conflicts between political and moral obligations); social_
--     contract_theory bridges to philosophy of mind (P5-07's collective_
--     intentionality and joint_action will treat the metaphysics of
--     contract-formation by groups); social_contract_theory bridges to
--     philosophy of language (P5-08 will house speech-act theory of
--     promises and consent that grounds contractarian models);
--     sovereignty bridges to metaphysics (P5-02b on the ontology of
--     authority-bearing collectives); democracy bridges to epistemology
--     (P5-01a/b on epistemic theories of democracy — democracy as a
--     truth-tracking institution per Estlund 2008, Anderson 2006); human_
--     rights bridges to ethics (P5-04a/b on the universalist moral
--     foundations and contestation thereof); multiculturalism bridges
--     to epistemology (testimony, hermeneutical injustice per Fricker
--     2007), to ethics (recognition as a moral-political concept per
--     Taylor 1992, Honneth 1995), and to philosophy of language (group-
--     identity terms and their semantic stability); republicanism
--     bridges to philosophy of mind (rational-agency conceptions of
--     non-domination); equality_political bridges to ethics (P5-04a's
--     normative theories all take positions on the moral significance
--     of equality). All of these defer to P5-11 cross-bridges.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md). The historical_influence predicate is
--     not used here either; political philosophy's intellectual history
--     (Plato → Aristotle → Augustine → Aquinas → Hobbes → Locke →
--     Rousseau → Kant → Hegel → Marx → Mill → Rawls → Nozick) is rich
--     but the historical-influence pass is deferred to a later phase
--     (display-only edges per PREDICATE_MANIFEST.md "historical_
--     influence" row; not part of P5-05's pedagogical-prerequisite
--     scope).
--   * Does not seed any historical_influence edges.
--   * Does not author the additional sub-range slots (0101-0109). Those
--     slots remain reserved for future political-philosophy extension
--     if Phase 6+ telemetry warrants additional concepts (further
--     subfields like cosmopolitanism, global justice, just war theory
--     restored to political philosophy from ethics-applied placement,
--     deliberative democracy specifications, recognition vs
--     redistribution debates, theories of representation, populism,
--     authoritarianism, fascism, theories of revolution, theories of
--     federalism, theories of secession, the political turn in the
--     analytic-philosophy literature post-2000). This seed completes
--     P5-05's task at the granularity principle within the 0100 file:
--     28 nodes covering the four explicitly-named clusters at the
--     umbrella-plus-canonical-positions density that prior P5 sessions
--     established. Political philosophy is structurally similar to
--     ethics in concept density — many canonical isms competing across
--     overlapping concept axes — and 28 nodes captures the contemporary
--     core of the analytic political-philosophy curriculum at the
--     same granularity as ethics metaethics+normative (P5-04a).
-- Cross-cutting decisions:
--   * confidence_level distribution: 28/28 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose
--     definition is directly lifted from a structural reference's
--     entry inventory; this seed authors original pedagogical prose
--     for every summary and teaching_notes per ADR 0011 (no hosted
--     copyrighted material) so EXTRACTED is 0%. SYNTHETIC is also 0%
--     because every concept here is well-named in the SEP/IEP entry
--     inventory and corresponds to a concept the contemporary analytic
--     political-philosophy literature (Rawls, Nozick, Sen, Nussbaum,
--     Cohen, Arneson, Dworkin, Berlin, Locke, Hobbes, Rousseau, Mill,
--     Burke, Pettit, MacIntyre, Sandel, Walzer, Taylor, Kymlicka, Marx,
--     Bodin, Bentham, Miller) explicitly names. Mirrors P5-01a / P5-01b
--     / P5-02a / P5-02b / P5-03 / P5-04a / P5-04b distribution.
--   * domain[] cardinality: every node carries exactly one tag,
--     'political'. Multiple cross-domain reaches exist (justice_as_
--     fairness into ethics; political_authority into logic; democracy
--     into epistemology; social_contract_theory into philosophy of
--     language; sovereignty into metaphysics; multiculturalism into
--     epistemology and ethics) but per phase_5.md T2-G #1, cross-domain
--     tagging belongs to P5-11. The canonical home for each of these
--     concepts in the analytic literature is political philosophy
--     (with Rawls and Nozick organizing the contemporary distributive-
--     justice debate; Berlin organizing the liberty-axis debate; Bodin
--     and Hobbes organizing the sovereignty-and-authority axis; Locke
--     organizing the natural-rights and consent-theory axes; Mill
--     organizing the toleration-and-democracy axes; Pettit organizing
--     the republican counter-tradition), so the single tag is correct
--     here. The borderline cases are toleration (which has religious-
--     studies and historical-philosophy contexts but the contemporary
--     analytic locus is Lockean and Millian political philosophy) and
--     human_rights (which has moral-philosophy and international-law
--     contexts but the contemporary analytic locus that grounds the
--     concept is political philosophy via Rawls's Law of Peoples and
--     Beitz's Idea of Human Rights tradition); both are tagged
--     political here.
--   * provenance: 'ai-seed' for every node and edge.
--   * Node selection rationale: 28 concepts cover the four clusters at
--     the granularity principle. Foundation (1): political_philosophy
--     (the subdomain umbrella, framing the inquiry into the legitimate
--     uses of collective coercive power). Theories of justice (8):
--     justice (the central cross-cluster concept, distinguishing
--     distributive justice from procedural and corrective justice and
--     anchoring the Aristotelian-Rawlsian tradition), distributive_
--     justice (the modern reframing of justice as a question about the
--     fair distribution of advantages and burdens), justice_as_fairness
--     (Rawls 1971 A THEORY OF JUSTICE — the original position behind a
--     veil of ignorance; the two principles of justice; the difference
--     principle that inequalities must benefit the worst off), libertarian-
--     ism_political (Nozick 1974 ANARCHY, STATE, AND UTOPIA — the
--     entitlement theory of justice in holdings; the night-watchman
--     state; the Wilt Chamberlain argument that distributive patterns
--     conflict with liberty), communitarianism (MacIntyre 1981 AFTER
--     VIRTUE / Sandel 1982 LIBERALISM AND THE LIMITS OF JUSTICE / Walzer
--     1983 SPHERES OF JUSTICE / Taylor — the critique that liberal
--     justice presupposes an unsituated self abstracted from community
--     traditions and roles), capability_approach (Sen 1980 / Nussbaum
--     2000 WOMEN AND HUMAN DEVELOPMENT — the alternative metric of
--     justice as substantive freedoms or capabilities to function rather
--     than primary goods or welfare), luck_egalitarianism (Cohen 1989
--     ON THE CURRENCY OF EGALITARIAN JUSTICE / Arneson 1989 / Dworkin
--     1981 — the choice/circumstance distinction as the touchstone for
--     egalitarian distribution), desert_theory_political (Miller 1999
--     PRINCIPLES OF SOCIAL JUSTICE — the partial revival of pre-
--     Rawlsian desert-based distribution against luck-egalitarian
--     hostility to desert claims). State and authority (6): state_
--     political (the modern political state as the territorial
--     organization claiming legitimate monopoly on coercive force per
--     Weber 1919), sovereignty (Bodin 1576 SIX BOOKS OF THE COMMONWEALTH
--     — supreme political authority within a territory; Hobbes's modern
--     development; Westphalian state sovereignty in international
--     relations), political_authority (the right to rule and be obeyed,
--     distinguished from mere power and from moral authority), political_
--     legitimacy (the normative property a political order has when its
--     authority is morally justified — through consent, fairness,
--     beneficial consequences, or democratic process), social_contract_
--     theory (the tradition grounding political authority in actual or
--     hypothetical agreement among the governed: Hobbes 1651 LEVIATHAN
--     / Locke 1689 SECOND TREATISE / Rousseau 1762 SOCIAL CONTRACT /
--     Rawls 1971 hypothetical-consent restatement), political_obligation
--     (the moral duty to obey the law and support political institutions
--     — fair-play theories per Hart 1955 and Rawls; gratitude theories;
--     consent theories; natural-duty theories; associative-obligations
--     theories per Dworkin 1986). Liberty, equality, rights (7): liberty_
--     political (Berlin 1958 TWO CONCEPTS OF LIBERTY — the negative-
--     versus-positive liberty distinction; the related Constant 1819
--     ancients-versus-moderns liberty distinction; the contemporary
--     republican challenge to the negative-positive dichotomy), equality_
--     political (the family of egalitarian commitments — formal equality
--     of treatment, equality of opportunity, equality of outcome,
--     relational equality per Anderson 1999, equal moral worth as the
--     foundational assumption), human_rights (the contemporary
--     framework of universal moral entitlements held by all persons
--     in virtue of their humanity, codified in UDHR 1948 and the major
--     covenants; political-conception per Rawls / Beitz; moral-conception
--     per Griffin 2008), natural_rights (the Lockean tradition of pre-
--     political moral entitlements grounded in the natural law and
--     equal moral status — life, liberty, property; the foundational
--     vocabulary on which modern human-rights discourse builds),
--     positive_rights (rights requiring positive action by others or
--     the state to provide goods or services — welfare, healthcare,
--     education), negative_rights (rights requiring only forbearance
--     from interference — non-coercion, non-discrimination), toleration
--     (the political stance of refraining from suppressing beliefs and
--     practices one disapproves of — Locke 1689 LETTER CONCERNING
--     TOLERATION / Mill 1859 ON LIBERTY / Rawls 1993 POLITICAL
--     LIBERALISM and the doctrine of public reason; toleration as
--     the precondition for stable diversity within a single polity).
--     Government and political ideologies (6): democracy (rule by the
--     people — direct vs representative; aggregative vs deliberative
--     per Habermas / Cohen / Estlund; majoritarian vs constitutional;
--     the epistemic theories of democracy as truth-tracking
--     institutions), liberalism (the dominant tradition of post-
--     Enlightenment political thought — individual liberty, rule of
--     law, limited government, equal moral worth, religious toleration;
--     classical-liberal vs egalitarian-liberal vs political-liberal
--     strands), republicanism (Pettit 1997 REPUBLICANISM — the neo-
--     republican revival; freedom as non-domination distinguished from
--     freedom as non-interference; the connection to Cicero, Machiavelli,
--     and the American founding; civic virtue as the political-
--     psychological basis of non-domination), conservatism (Burke 1790
--     REFLECTIONS ON THE REVOLUTION IN FRANCE — the founding modern
--     statement; tradition as accumulated practical wisdom; organic
--     view of society against rationalist reform; prudence as cardinal
--     political virtue; Oakeshott 1962 RATIONALISM IN POLITICS),
--     socialism (the family of doctrines committing to collective or
--     social ownership of the means of production for the sake of
--     economic equality and democratic self-determination — Marx 1867
--     CAPITAL on the structural critique of capitalist exploitation;
--     market socialism per Roemer 1994; democratic socialism;
--     contemporary debates between socialist and social-democratic
--     framings), multiculturalism (Kymlicka 1995 MULTICULTURAL
--     CITIZENSHIP — group-differentiated rights; the distinction
--     between national minorities and immigrant groups; recognition
--     per Taylor 1992 / Honneth 1995; the redistribution-vs-recognition
--     debate per Fraser 1995, 2000; the limits-of-toleration question
--     for cultural practices that conflict with individual rights).
--   * Edge structure: 34 edges total, all pedagogical_prerequisite, all
--     within-domain. Foundation tier (5) wires the umbrella into the
--     five subdomain anchors: political_philosophy → {justice, state_
--     political, liberty_political, equality_political, social_contract_
--     theory}. Justice tier (1) wires justice → distributive_justice
--     (the modern reframing). State tier (2) wires state_political →
--     {sovereignty, political_authority}. Liberty tier (5) wires
--     liberty_political → {negative_rights, positive_rights, natural_
--     rights, liberalism, republicanism}. Authority tier (3) wires
--     political_authority → {political_legitimacy, political_obligation,
--     democracy} — democracy presupposes the prior conceptualization of
--     political authority as the right against which popular self-rule
--     is the answer; legitimacy and obligation are the two normative
--     concepts internal to the authority relation. Social contract
--     tier (3) wires social_contract_theory → {justice_as_fairness,
--     political_legitimacy, political_obligation} — Rawls's hypothetical
--     contract apparatus extends the social contract into the
--     distributive-justice question; the contract tradition grounds
--     legitimacy and obligation in actual or hypothetical agreement.
--     Distributive justice tier (6) wires distributive_justice → the
--     six positions on the distributive landscape: justice_as_fairness,
--     libertarianism_political, communitarianism, capability_approach,
--     desert_theory_political, socialism. Equality tier (1) wires
--     equality_political → capability_approach (the capability metric
--     is fundamentally an egalitarian metric of substantive equality).
--     Natural rights tier (2) wires natural_rights → {libertarianism_
--     political, human_rights} — Nozickian libertarianism is built on
--     a natural-rights foundation against pattern-based distribution;
--     the contemporary human-rights framework is the natural-rights
--     tradition's modern descendant. Liberalism tier (3) wires
--     liberalism → {communitarianism, toleration, multiculturalism} —
--     communitarianism is the canonical critic; toleration is the
--     definitional liberal commitment; multiculturalism extends and
--     contests liberal individualism in the direction of group rights.
--     Justice as fairness tier (1) wires justice_as_fairness → luck_
--     egalitarianism (luck-egalitarianism extends Rawlsian fairness
--     by sharpening the choice-versus-circumstance distinction).
--     Communitarianism tier (1) wires communitarianism → multiculturalism
--     (multiculturalism is the most successful contemporary
--     communitarian-influenced political position). Political obligation
--     tier (1) wires political_obligation → conservatism (Burkean
--     conservatism centers the duty of obedience to traditional
--     authority as the political virtue par excellence).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 9; DELETE FROM public.nodes WHERE id IN (the 28 ids inserted
--   here); UPDATE public.settings SET value = '8'::jsonb WHERE key =
--   'graph_version'; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 63 statements
--   atomically — manual rollback above applies to the post-commit
--   window only. The 28 ids: political_philosophy, justice, state_
--   political, liberty_political, equality_political, social_contract_
--   theory, distributive_justice, sovereignty, political_authority,
--   negative_rights, positive_rights, natural_rights, liberalism,
--   republicanism, justice_as_fairness, libertarianism_political,
--   communitarianism, capability_approach, desert_theory_political,
--   democracy, political_legitimacy, political_obligation, human_rights,
--   toleration, socialism, luck_egalitarianism, conservatism,
--   multiculturalism.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry); product/seed-graph/migrations/0011_seed_epistemology_
--   part1.sql (P5-01a foundational seed; pattern reference);
--   product/seed-graph/migrations/0026_seed_ethics_part1.sql (P5-04b
--   applied ethics; immediate-prior pattern reference; just_war_theory
--   resides in P5-04b ethics-applied rather than political-philosophy
--   here per phase_5.md T1-B's allocation choice — political-philosophy
--   inherits the moral-foundations of just war but doesn't re-author
--   the concept); product/docs/architecture.md (Node/Edge schema +
--   Granularity Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 8 at session boot (post-S-0059 state); write 9 here;
-- every node/edge below carries graph_version_added = 9.
UPDATE public.settings
  SET value = '9'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 28 INSERTs across the four political-philosophy clusters plus the foundation tier.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'political_philosophy',
    'Political Philosophy',
    ARRAY['political'],
    'The branch of philosophy concerned with the legitimate uses of collective coercive power, the moral foundations of political institutions, and the principles that should govern social life. Distinguishes itself from political science (which describes how political institutions actually work) by asking how they ought to work. Central questions: when, if ever, is the state morally justified in coercing its subjects; what distribution of advantages and burdens across persons is just; what political liberties and rights persons have and how they constrain collective action; what forms of government are best.',
    'Teach political philosophy as the inquiry into the moral foundations of political life. Open with the question of authority: under what conditions, if any, may one person or institution legitimately command another? Move through the canonical distinctions: justice vs other political values (liberty, equality, security, prosperity, community); the state vs other institutions (family, church, market, voluntary association); rights vs interests vs preferences; ideal theory (what would a just society look like?) vs nonideal theory (what should we do given existing injustice?). Establish the three traditions students will see throughout: the social-contract tradition grounding authority in agreement, the natural-law tradition grounding it in objective moral order, and the consequentialist tradition grounding it in beneficial outcomes. Note that political philosophy operates in close relation to ethics (the moral foundations are first-order ethical commitments) but distinguishes itself by attending specifically to the structural and institutional level — what laws should we have, what institutions should we build, not what should I as an individual do.',
    ARRAY['politics_philosophy', 'political_theory_philosophical', 'normative_political_theory'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'justice',
    'Justice',
    ARRAY['political'],
    'The central evaluative concept of political philosophy: the property a society has when its institutions distribute benefits and burdens, recognize claims, and respond to wrongs in the morally appropriate way. Aristotle distinguished distributive justice (the proper division of goods among persons), corrective justice (the proper response to wrongs), and procedural justice (the propriety of the methods by which decisions are made). Modern political philosophy has been organized largely around distributive justice since Rawls 1971 reframed the central question as: what principles for the basic structure of society would free and equal persons agree to under fair conditions of choice?',
    'Teach justice as the master concept students will see organize the rest of the political-philosophy curriculum. Open with Aristotle''s tripartite division (distributive, corrective, procedural) so students can locate later authors within or against this framework. Note that contemporary analytic political philosophy is organized around distributive justice — the question of how the social product should be divided — to a degree that can mask the prior questions of corrective and procedural justice. Two methodological approaches are visible across the literature: top-down (start with abstract principles and derive distributive consequences — Rawls, Nozick, Cohen) and bottom-up (start with our considered judgments about specific cases and articulate the principles implicit in them — Walzer 1983, Miller 1999). The reflective-equilibrium method per Rawls 1971 is an attempt to combine both. Distinguish justice from related concepts: legitimacy (which can attach to unjust orders), obligation (the duty to obey law in unjust circumstances), and ethics generally (the moral life is wider than what justice demands).',
    ARRAY['political_justice', 'social_justice_general', 'fairness_political'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'state_political',
    'State (Political)',
    ARRAY['political'],
    'The modern political state: the territorial organization that successfully claims a monopoly on the legitimate use of physical force within a given territory (Weber 1919 POLITIK ALS BERUF). Distinguished from earlier forms of political organization (city-state, empire, feudal lordship) by territorial sovereignty, centralized administration, formal legal codification, professional bureaucracy, and a standing military. The unit of contemporary international relations and the locus of most political-philosophy theorizing about authority, legitimacy, and obligation.',
    'Teach the modern state as a specific historical and conceptual entity that students should distinguish from political organization in general. Open with the Weberian definition (territorial monopoly on legitimate violence) and unpack each element: territorial (bounded geographical extent), monopoly (claims authority against rival violence), legitimate (claims moral and not just factual authority), force (physical coercion as the ultimate sanction). Locate the state historically: emerging in early-modern Europe through the displacement of feudal personal authority by centralized territorial authority, codified at Westphalia 1648, and globalized through European colonial expansion and 20th-century decolonization producing the contemporary system of nation-states. Note three contemporary debates about the state: against the state (anarchism — the state is necessarily illegitimate; Wolff 1970 IN DEFENSE OF ANARCHISM); about the right kind of state (the bulk of contemporary political philosophy); and about the future of the state (cosmopolitanism, global governance, post-Westphalian theorizing — does globalization render the territorial state obsolete?).',
    ARRAY['modern_state', 'territorial_state', 'westphalian_state', 'nation_state'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'liberty_political',
    'Liberty (Political)',
    ARRAY['political'],
    'The political concept of freedom: the absence of constraints on a person''s ability to do or be what they have reason to value. Berlin 1958 TWO CONCEPTS OF LIBERTY drew the canonical contemporary distinction: negative liberty (freedom from interference by others) and positive liberty (freedom to be one''s own master, to pursue self-realization). The negative-positive distinction maps imperfectly onto an older distinction Constant 1819 drew between the liberty of the moderns (private rights against the state) and the liberty of the ancients (active participation in collective self-government). Pettit 1997 has argued the negative-positive dichotomy obscures a third concept — freedom as non-domination — that organizes the republican tradition.',
    'Teach political liberty as the home of three distinct concepts students should keep separate: negative liberty (non-interference; the absence of external obstacles), positive liberty (self-mastery; the conditions of effective self-direction), and republican liberty (non-domination; the absence of arbitrary power that could interfere even if it does not). Berlin 1958 worried that positive-liberty theories slide easily into the legitimation of paternalistic and totalitarian coercion (one is forced to be free in pursuit of one''s "true" self), and defended a primarily negative conception. Critics argue that bare non-interference is too thin (a slave with a permissive master is not free); positive-liberty theorists develop conceptions of autonomy and capability; republican-liberty theorists like Pettit argue freedom requires the absence of arbitrary power, not merely the absence of actual interference. Note that the value of liberty is itself contested: instrumentalists value it for what it enables, intrinsicists value it as constitutive of personhood. The taxonomy of liberty interacts with every other political-philosophy concept — equality, rights, democracy, justice — and is the structural fault line dividing liberal, libertarian, republican, and communitarian political theories.',
    ARRAY['freedom_political', 'political_freedom', 'civil_liberty'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'equality_political',
    'Equality (Political)',
    ARRAY['political'],
    'The family of political-philosophy commitments to treating persons as equals or to equalizing some morally relevant dimension across persons. Includes formal equality (equal treatment under the law), equality of opportunity (equal chances at advantages whose distribution is then permitted to vary by choice or merit), equality of outcome (equal final shares of relevant goods), relational equality (Anderson 1999 — equality as a feature of social relationships, not a pattern of distribution), and equal moral worth (the foundational assumption that all persons count equally morally). Most contemporary political philosophers accept some form of equal moral worth as foundational while disagreeing about which further egalitarian commitments follow.',
    'Teach political equality as a multi-dimensional commitment students should not collapse into a single demand for equal shares. Open with the foundational claim of equal moral worth — the proposition that no person is intrinsically more important than any other — and note that virtually every contemporary political philosophy accepts this in some form (Dworkin 2000 calls the foundational principle "equal concern and respect"; Rawls 1971 builds it into the original position''s symmetry conditions). Distinguish four dimensions of more substantive egalitarian commitment: formal equality (equal treatment under existing rules), opportunity-equality (equal access to positions the rules allocate competitively), outcome-equality (equal final shares of advantage), relational equality (equality as a feature of how persons stand to each other in social relations, against hierarchy and domination, per Anderson 1999 and the relational-egalitarian tradition). The choice among these is consequential. Note that the equality-vs-liberty tradeoff (a stock theme in political-theory teaching) is partially a misframing — many contemporary theories (Rawls, the capability approach, relational egalitarianism) treat liberty and equality as interconnected rather than rivalrous. Also note the leveling-down objection (Parfit 1995): if equality is good in itself, would it be better to make everyone worse off than to leave some better off than others? Different egalitarian theories answer differently.',
    ARRAY['political_equality', 'egalitarianism_political', 'equal_treatment'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'social_contract_theory',
    'Social Contract Theory',
    ARRAY['political'],
    'The tradition of grounding political authority and political obligation in actual or hypothetical agreement among the governed. Hobbes 1651 LEVIATHAN argued that to escape the state of nature (a war of all against all), rational persons would agree to authorize an absolute sovereign. Locke 1689 SECOND TREATISE argued that persons in the state of nature, possessing natural rights, would consent to a limited government instituted to protect those rights. Rousseau 1762 SOCIAL CONTRACT argued that the contract creates the general will and a form of moral freedom unavailable to pre-political individuals. Rawls 1971 A THEORY OF JUSTICE updated the tradition by replacing actual consent with hypothetical consent in the original position behind a veil of ignorance.',
    'Teach the social-contract tradition as a master strategy in political philosophy: ground the legitimacy of political authority in something the governed have, would have, or could have agreed to. Open with the canonical historical sequence — Hobbes (sovereign protects against state-of-nature violence), Locke (sovereign protects pre-existing natural rights), Rousseau (the general will makes the citizen morally free) — and note the structural variations: actual vs hypothetical consent (most classical theorists invoke actual consent in some attenuated form; Rawls switches decisively to hypothetical consent); state of nature as descriptive vs heuristic (Hobbes treats it as a real state into which order can collapse; Locke treats it as a partly historical, partly heuristic baseline; Rawls discards it); the form of agreement (unanimous vs majoritarian; one-shot vs ongoing; tacit vs express). Distinguish the historical-political contract (the legitimacy-grounding agreement at the foundation of the state) from the moral contract (the principles of justice that would be agreed to under fair conditions — Scanlon 1998''s ethical contractualism is this kind in the moral domain). Note the standard objections: the state of nature is a fiction; tacit consent is empty (Hume 1748 OF THE ORIGINAL CONTRACT); hypothetical consent does not bind real persons (Dworkin 1973). The replies have spawned an enormous literature; Rawls''s hypothetical-consent strategy remains the most influential contemporary form.',
    ARRAY['contractarianism_political', 'social_contract', 'contract_theory_political'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'distributive_justice',
    'Distributive Justice',
    ARRAY['political'],
    'The branch of justice concerned with the proper distribution of advantages and burdens across persons within a society. Modern political philosophy has been organized around the distributive question since Rawls 1971: what principles should govern the basic structure of society in its allocation of primary goods (rights, liberties, opportunities, income, wealth, the social bases of self-respect)? Competing answers include strict equality, Rawlsian justice as fairness with the difference principle, libertarian entitlement theories that reject patterned distribution entirely, capability-approach metrics of substantive freedom, luck-egalitarian distinctions between choice and circumstance, and desert-based distributions tracking productive contribution.',
    'Teach distributive justice as the theme that organizes most contemporary political-philosophy debate. Open with the contrast between patterned and historical theories of distributive justice (Nozick 1974''s framing): patterned theories (Rawls, capability approach, luck-egalitarianism) specify a preferred end-state distribution and evaluate institutions by how well they achieve it; historical theories (Nozick''s entitlement theory) evaluate distributions by the propriety of the process by which they came about. The Wilt Chamberlain argument illustrates Nozick''s thought: any preferred patterned distribution will be upset by free voluntary exchanges (people pay to watch Chamberlain play basketball; he becomes wealthy; the original pattern is disturbed) — so maintaining the pattern requires continuous interference with liberty. Patterned theorists reply that liberty itself is constrained by the resources persons have, so the pattern is not opposed to liberty but constitutive of its conditions. Note four further dimensions students should track across positions: the metric (what is distributed — primary goods, welfare, capabilities, resources), the rule (what pattern — equality, sufficiency, priority to worst-off, desert), the site (the basic structure vs personal ethics — Cohen 2008 RESCUING JUSTICE AND EQUALITY presses the question), the scope (one society vs global — Pogge 2002, cosmopolitan critiques of methodologically nationalist distributive theory).',
    ARRAY['distributive_fairness', 'distribution_justice', 'distributive_principles'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'sovereignty',
    'Sovereignty',
    ARRAY['political'],
    'Supreme political authority within a defined territory or population. Bodin 1576 SIX BOOKS OF THE COMMONWEALTH gave the canonical modern formulation: sovereignty is the absolute and perpetual power of a commonwealth, indivisible, unaccountable to any superior, and the source of law (princeps legibus solutus est — the sovereign is not bound by the laws). Hobbes 1651 developed the concept further as the precondition of civil society. The Westphalian settlement of 1648 institutionalized sovereignty as the organizing principle of international relations: each territorial state has supreme authority within its borders and recognizes others'' equal authority within theirs.',
    'Teach sovereignty as a foundational concept students need to understand even as contemporary political theory increasingly contests it. Open with the Bodinian definition (supreme, perpetual, indivisible authority) and unpack each property: supreme (no higher authority within the territory), perpetual (not delegated for a fixed term), indivisible (the locus of sovereignty is one — though sovereignty can be exercised through delegated agents). Note the canonical distinctions: internal vs external sovereignty (supremacy within the state vs independence from external states); de jure vs de facto sovereignty (the legal claim vs the actual capacity to exercise authority); popular vs monarchical sovereignty (the people as ultimate source per Rousseau vs the prince per Bodin); legal vs political sovereignty (Dicey 1885 — the legal sovereign whose enactments courts will enforce vs the political sovereign whose will determines what those enactments are). Contemporary contestation: globalization, supranational institutions (EU, UN, WTO), transnational corporate power, climate-change governance, humanitarian intervention, R2P (responsibility to protect), all pressure the Westphalian model. Some theorists argue sovereignty is being unbundled (Krasner 1999) into territorial, interdependence, domestic-authority, and international-legal components; others argue cosmopolitan governance should supersede territorial sovereignty entirely.',
    ARRAY['supreme_authority', 'state_sovereignty', 'westphalian_sovereignty'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'political_authority',
    'Political Authority',
    ARRAY['political'],
    'The right to rule and be obeyed: the moral or legal property in virtue of which a person or institution can issue commands that subjects are bound to obey. Distinguished from mere power (the ability to coerce) and from moral expertise (knowledge of what should be done); authority is a deontic relation that creates duties of obedience without requiring the subject''s own assessment of the merits of each command. Whether genuine political authority exists is itself contested — philosophical anarchism (Wolff 1970 IN DEFENSE OF ANARCHISM) argues no political institution can have authority over autonomous persons; defenders of authority argue it is justified instrumentally (by the goods it produces) or intrinsically (through consent, fair play, or natural duty).',
    'Teach political authority as a concept students should distinguish sharply from related notions: power (causal capacity to coerce), influence (causal capacity to shape behavior without coercion), legitimacy (the normative property of having authority justifiably), and obligation (the corresponding duty to obey). Authority is the right; legitimacy is what makes it morally rightful; obligation is the duty correlative to it. Raz 1986 THE MORALITY OF FREEDOM developed the canonical contemporary account: authority is justified when subjects do better at acting in accordance with the reasons that already apply to them by following the authority''s directives than by deciding case-by-case (the service conception or normal justification thesis). The dependence thesis (the authority''s directives must be based on the reasons that already apply to subjects) and the preemption thesis (the directives replace the underlying reasons in subjects'' deliberation) complete the account. Alternative accounts ground authority in consent (Locke), fair play (Hart 1955), associative obligations (Dworkin 1986), or natural duty (Rawls 1971). Note the philosophical-anarchist challenge: if subjects retain their autonomy, every directive must still be assessed by their own judgment, in which case the authority is doing no normative work. The replies typically distinguish autonomous judgment from autonomous action and argue that delegating decision-making to better-positioned authorities is itself a rational exercise of autonomy.',
    ARRAY['authority_political', 'right_to_rule', 'political_command'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'negative_rights',
    'Negative Rights',
    ARRAY['political'],
    'Rights that require only forbearance from others — duties of non-interference. Examples: the right not to be killed, not to be assaulted, not to have one''s property taken, not to be coerced into religious practice, not to be discriminated against. Contrasted with positive rights, which require positive action (provision of goods or services). The negative-positive distinction maps roughly onto Berlin''s negative-positive liberty distinction and onto the libertarian-liberal-egalitarian dispute about which rights are fundamental: classical liberals and libertarians treat negative rights as primary; egalitarian liberals and socialists argue positive rights are equally fundamental.',
    'Teach negative rights as a concept students should be able to wield carefully. Open with the conceptual distinction (negative rights = correlative duties of non-interference; positive rights = correlative duties of provision) and the two stock arguments for negative-rights priority: enforceability (negative duties can in principle be discharged by all addressees simultaneously without resource constraints; positive duties cannot — only some can provide healthcare, education, housing) and demandingness (positive duties are more onerous and intrude further into the lives of duty-bearers). Note the canonical objections: the asymmetry is overstated (rights against violence presuppose police, courts, prisons — substantial provision; rights to private property presuppose enforcement of property law — substantial provision); positive-negative is a continuum, not a sharp distinction (the right to a fair trial is partly negative, partly positive); the priority claim begs the question (whether negative rights are more fundamental is what is at issue, not what is established by the conceptual distinction). Note that the human-rights instruments codify both kinds (ICCPR primarily negative; ICESCR primarily positive) — the legal-political consensus is that both are genuine rights, with the priority question contested. The negative-rights framework remains the spine of libertarian and classical-liberal political theory; positive rights are increasingly central to contemporary egalitarian and capability-approach theorizing.',
    ARRAY['liberty_rights', 'noninterference_rights', 'forbearance_rights'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'positive_rights',
    'Positive Rights',
    ARRAY['political'],
    'Rights that require positive action by others or by the state to provide goods or services. Examples: the right to education, healthcare, adequate housing, social security, legal counsel in criminal proceedings. Contrasted with negative rights (duties of forbearance only). Codified extensively in the International Covenant on Economic, Social and Cultural Rights (ICESCR, 1966) and in many national constitutions. Their status as genuine rights (vs aspirational goals or political demands) is contested between libertarians (who deny they are rights properly so called) and most other contemporary positions (who affirm them).',
    'Teach positive rights as the conceptual counterpart to negative rights and the locus of substantial contemporary disagreement. Open with the conceptual distinction (positive rights = correlative duties of positive provision; negative rights = duties of forbearance) and the canonical objections to positive-rights status: enforceability is uneven (we can simultaneously refrain from killing everyone but cannot simultaneously provide healthcare to everyone); positive rights generate conflicts (right to healthcare conflicts with right to keep one''s earnings); positive rights confuse rights with desirable goals. Note the standard replies: rights generate priorities and tradeoffs anyway (negative rights conflict with each other — speech vs reputation, property vs equality); the goal-vs-right distinction does not track the negative-positive distinction (positive rights can be highly stringent — the right to legal counsel in criminal proceedings is robustly enforceable in modern legal systems); the conceptual asymmetry is overstated (negative rights presuppose enforcement provision). Note the socialist and capability-approach traditions that treat the negative-positive distinction as an artifact of the liberal-capitalist economic settlement rather than a deep conceptual divide. Marshall 1950 CITIZENSHIP AND SOCIAL CLASS placed civil rights, political rights, and social rights as a developmental sequence with social (largely positive) rights as the modern completion of citizenship; this framework remains influential in social-democratic theorizing.',
    ARRAY['welfare_rights', 'social_rights', 'provision_rights', 'economic_rights'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'natural_rights',
    'Natural Rights',
    ARRAY['political'],
    'Pre-political moral entitlements held by all persons in virtue of their nature as rational beings or as creatures of God. The Lockean tradition is canonical: Locke 1689 SECOND TREATISE OF GOVERNMENT identifies the natural rights of life, liberty, and property as held by persons in the state of nature, prior to any political authority and constraining what political authority can permissibly do. Earlier formulations in Aquinas, Suarez, and Grotius developed the medieval and early-modern natural-law tradition; the Declaration of Independence 1776 ("endowed by their Creator with certain unalienable Rights") and the French Declaration of the Rights of Man 1789 institutionalized the natural-rights vocabulary as the foundation of modern liberal constitutionalism.',
    'Teach natural rights as the conceptual ancestor of contemporary human rights and as the foundation Locke supplies for liberal political philosophy. Open with the Lockean argument: in the state of nature, persons are free and equal, possess rights to life, liberty, and property, and have a natural duty not to harm others in their life, health, liberty, or possessions. The state is instituted by consent to better protect these natural rights; its authority is limited by them; a government that systematically violates them forfeits its authority and may be resisted. Note the foundational question: what grounds natural rights? Locke''s argument depends on theistic premises (we are God''s property and so cannot destroy ourselves or others); secular reformulations (Nozick 1974) ground rights in the Kantian principle of treating persons as ends and not merely as means, but the foundation remains contested. Note the canonical critiques: Bentham 1843 ANARCHICAL FALLACIES called natural rights "nonsense upon stilts"; Marx 1843 ON THE JEWISH QUESTION argued that the rights-of-man framework presupposes a possessive-individualist conception of the person; communitarians (MacIntyre 1981) argue natural-rights talk is intelligible only against a backdrop of substantive moral tradition. Note the connection to contemporary human rights: human rights inherit the natural-rights structure (universal, pre-institutional, constraining government) but typically secularize the foundation. The political conception of human rights per Rawls 1999 LAW OF PEOPLES and Beitz 2009 THE IDEA OF HUMAN RIGHTS attempts to ground human-rights claims in the practical role they play in international politics rather than in a metaphysical natural-rights foundation.',
    ARRAY['lockean_rights', 'natural_law_rights', 'pre_political_rights'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'liberalism',
    'Liberalism',
    ARRAY['political'],
    'The dominant tradition of post-Enlightenment political thought, organized around individual liberty, the rule of law, limited and accountable government, equal moral worth of persons, and toleration of diverse views about the good life. Encompasses several internally diverse strands: classical liberalism (Locke, Smith, Mill — emphasis on negative liberty, limited state, free markets), egalitarian liberalism (Rawls, Dworkin — emphasis on substantive equality and the welfare state alongside individual liberty), and political liberalism (Rawls 1993 POLITICAL LIBERALISM — emphasis on the conditions for stable cooperation among reasonable persons who disagree about the good).',
    'Teach liberalism as the structurally hegemonic political tradition of the contemporary West and as a tradition with substantive internal disagreement that students should not collapse into a single position. Open with the foundational commitments shared across liberal positions: individual moral worth and dignity, individual liberty as a primary political value, the rule of law against arbitrary government, religious toleration and broader pluralism about conceptions of the good, and constitutional government with limits on state power. Note the principal internal divides: the libertarian-egalitarian divide (negative liberty alone vs negative liberty plus substantive equality and welfare provision); the comprehensive-political divide (Mill''s liberalism rests on a substantive doctrine about human flourishing and individuality; Rawls''s political liberalism deliberately avoids reliance on any comprehensive doctrine); the perfectionist-neutralist divide (whether the state may permissibly promote particular conceptions of the good or must be neutral among them). Note the principal critics: communitarians (Sandel, MacIntyre, Taylor, Walzer) argue liberalism presupposes an unsituated self and undervalues the constitutive role of community; libertarians argue liberalism (in its egalitarian form) sacrifices liberty to redistribution; Marxists argue liberalism legitimates capitalist exploitation; multiculturalists argue liberalism is insufficiently attentive to group identity; feminists argue liberalism''s public-private distinction insulates patriarchal social relations from political critique. Liberal traditions have responded to each, generating internal refinement (political liberalism, perfectionist liberalism, multicultural liberalism, feminist liberalism).',
    ARRAY['political_liberalism', 'liberal_tradition', 'liberal_political_theory'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'republicanism',
    'Republicanism',
    ARRAY['political'],
    'A political tradition centering on civic self-government, civic virtue, and freedom understood as the absence of arbitrary power (non-domination). The historical tradition runs from the Roman Republic through Machiavelli, Harrington, Montesquieu, and the American founders; the contemporary neo-republican revival (Pettit 1997 REPUBLICANISM, Skinner 1998 LIBERTY BEFORE LIBERALISM) reconstructs the tradition as a third position alongside liberalism and communitarianism. The defining commitment is freedom-as-non-domination: a person is free not when nobody actually interferes with them but when nobody has the arbitrary capacity to interfere.',
    'Teach contemporary republicanism as a third political-philosophy alternative students should understand alongside liberalism and communitarianism. Open with Pettit''s freedom-as-non-domination definition and contrast it with both Berlinian liberty concepts: against negative liberty (non-interference), republicans argue that a slave with a lenient master enjoys non-interference but is unfree because the master could interfere arbitrarily — so freedom requires the absence of arbitrary power, not merely the absence of actual interference; against positive liberty (self-mastery), republicans argue freedom is fundamentally a relational property (about how persons stand to each other in social relations) rather than a property of the inner life. Note the practical political implications: republican liberty justifies extensive state action (against private domination by employers, spouses, creditors) that classical liberals would resist; it grounds a strong commitment to democratic accountability (so the state does not become the arbitrary dominator); it values civic virtue and active participation as preconditions of non-domination. Distinguish from Aristotelian republicanism (the older tradition emphasizing positive participation as constitutive of human flourishing; civic humanist tradition per Pocock 1975) which contemporary neo-republicans treat as an alternative version of positive liberty rather than the core of the tradition. Note the connections to feminist political philosophy (the family as a domain of potential domination), to labor and socialist theory (the workplace as a domain of domination), and to international theory (small states as dominated by great powers).',
    ARRAY['neo_republicanism', 'civic_republicanism', 'pettit_republicanism'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'justice_as_fairness',
    'Justice as Fairness (Rawls)',
    ARRAY['political'],
    'Rawls 1971 A THEORY OF JUSTICE''s account of justice for the basic structure of society. Justice as fairness derives two principles of justice from a hypothetical contract behind a veil of ignorance: first, each person has equal claim to the most extensive scheme of basic liberties compatible with the like liberty of others; second, social and economic inequalities are to be arranged so that they are (a) attached to positions and offices open to all under conditions of fair equality of opportunity, and (b) to the greatest benefit of the least advantaged members of society (the difference principle). The first principle has lexical priority over the second; fair equality of opportunity has lexical priority over the difference principle.',
    'Teach Rawls''s justice as fairness as the centerpiece of contemporary distributive-justice theorizing — every other position in the literature is articulated partly in relation to it. Open with the methodology: the original position is a heuristic device for selecting principles of justice — rational agents behind a veil of ignorance (not knowing their own talents, social position, conception of the good) choose principles to govern the basic structure of the society they will then inhabit. Walk through the argument that they would choose the two principles: the maximin reasoning (in conditions of profound uncertainty, choose the principle that maximizes the position of the worst off — the difference principle); the lexical priority of liberty (basic liberties cannot be traded for material gains because the loss of liberty would compromise the conditions of agency itself). Note the principal critiques: Nozick 1974 (any pattern is upset by free transactions; the difference principle is incompatible with self-ownership); Sen 1980 (primary goods is the wrong metric — capabilities matter); Cohen 1989 ("incentive payments" presupposed by the difference principle conflict with the egalitarian ethos that should also govern individual action); communitarian critiques (the unsituated self of the original position presupposes a thin conception of the person); feminist critiques (the original position abstracts from gender and the family). Distinguish A Theory of Justice (1971; comprehensive doctrine) from Political Liberalism (1993; political conception); Rawls in his later work argued the comprehensive doctrine cannot be the public basis of justification for citizens with diverse comprehensive views, and reformulated justice as fairness as a free-standing political conception.',
    ARRAY['rawlsian_justice', 'rawls_justice', 'difference_principle_theory'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'libertarianism_political',
    'Libertarianism (Political)',
    ARRAY['political'],
    'The political philosophy that takes individual liberty (in the negative sense) and natural rights (especially property rights) as primary, and accordingly endorses minimal state authority. Nozick 1974 ANARCHY, STATE, AND UTOPIA is the canonical contemporary statement: starting from Lockean self-ownership and natural rights, Nozick derives an entitlement theory of justice in holdings (a distribution is just if it arose from just original acquisition through a series of just transfers; just rectifications correct past injustice) and the night-watchman state (the only state compatible with rights protects against force, theft, fraud, and breach of contract — anything more extensive violates rights). Distinguished from libertarianism about free will in metaphysics.',
    'Teach political libertarianism as the principal contemporary alternative to Rawlsian distributive theory. Open with the foundational commitments: self-ownership (each person owns themselves and their natural talents); natural rights to property in the products of one''s labor; the moral inviolability of voluntary transactions among consenting persons. Walk through Nozick''s entitlement theory (just acquisition, just transfer, just rectification) and the Wilt Chamberlain argument: any patterned distribution of holdings will be upset by voluntary exchanges (people pay to watch Chamberlain play; he becomes wealthy; the original pattern dissolves) — so maintaining the pattern requires continuous interference with liberty. Note the implications: redistributive taxation is on a par with forced labor (some hours of work are appropriated for state-determined ends); the welfare state is illegitimate; the night-watchman state is the maximum justifiable government. Distinguish right-libertarianism (Nozick — full self-ownership including ownership of natural talents and resources acquired) from left-libertarianism (Steiner, Otsuka, Vallentyne — self-ownership but equal claim to natural resources, supporting substantial redistribution of unearned advantages). Note the principal objections: the Lockean proviso (acquisition is just only if "enough and as good is left for others") is hard to satisfy in a finite world; self-ownership of natural talents is contestable (talents are partly the product of luck, social investment, others'' contributions); the distribution-process disjunction is overstated (background conditions of acquisition affect the justice of subsequent transactions). Cohen 1995 SELF-OWNERSHIP, FREEDOM, AND EQUALITY develops the most detailed contemporary critique.',
    ARRAY['nozick_libertarianism', 'minarchism', 'night_watchman_state'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'communitarianism',
    'Communitarianism',
    ARRAY['political'],
    'A family of political-philosophy positions that critiques the abstract individualism of liberal political theory and emphasizes the constitutive role of community, tradition, and shared social meanings in political life. Canonical contemporary texts: MacIntyre 1981 AFTER VIRTUE (the modern moral and political vocabulary is fragmented and unintelligible without recovery of an Aristotelian tradition); Sandel 1982 LIBERALISM AND THE LIMITS OF JUSTICE (the unencumbered self of Rawlsian liberalism is metaphysically incoherent); Walzer 1983 SPHERES OF JUSTICE (different distributive principles govern different social goods, depending on their shared meanings within the community); Taylor 1989 SOURCES OF THE SELF (the modern self is constituted by historically-situated frameworks of meaning).',
    'Teach communitarianism as the most influential late-20th-century critique of the liberal tradition and as a position students should distinguish from conservatism (with which it is sometimes confused). Open with the foundational claim: persons are not the unencumbered, prior-to-attachment selves of liberal theory but are partly constituted by their roles, traditions, and communities — and political philosophy that ignores this is descriptively false and normatively distorted. Walk through three principal lines of critique. Sandel''s metaphysical critique: the original position presupposes a self that exists prior to its ends and attachments, but no such self exists; persons are "encumbered" by constitutive attachments. MacIntyre''s historical critique: the modern moral and political vocabulary (rights, utility, duties) consists of fragments of an older Aristotelian tradition cut loose from their original framework; political-philosophy disagreement is interminable because we lack the shared tradition needed to settle it. Walzer''s methodological critique: distributive principles cannot be derived from a universal account; they must be discovered in the shared social meanings of particular communities (different goods belong to different "spheres" with different distributive logics — money does not buy political power, love, or friendship). Note the standard liberal replies: communitarianism conflates metaphysical and political theses (a metaphysically constituted self can still be the political-philosophy bearer of rights); shared meanings are themselves contested; communitarian arguments often presuppose universal moral premises they officially reject. Note the practical-political implications: communitarianism is politically heterogeneous (left, right, and centrist variants exist) and has fed both contemporary multiculturalism and contemporary religious-political theory.',
    ARRAY['communitarian_political_theory', 'communitarian_critique', 'situated_self_theory'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'capability_approach',
    'Capability Approach',
    ARRAY['political'],
    'Sen 1980 / Nussbaum 2000 WOMEN AND HUMAN DEVELOPMENT''s alternative metric for justice and human development: not primary goods (Rawls) and not subjective welfare (utilitarianism) but capabilities — the substantive freedoms persons have to achieve various functionings (states of being and doing they have reason to value). Sen developed the approach in critique of welfarist development economics; Nussbaum developed the philosophical foundations and produced a list of central human capabilities (life, bodily health, bodily integrity, senses-imagination-thought, emotions, practical reason, affiliation, other species, play, control over one''s environment) as the focus of political concern.',
    'Teach the capability approach as a major alternative to both Rawlsian primary-goods and utilitarian welfarist metrics. Open with Sen''s critique of competing metrics: primary goods (Rawls) are means rather than ends — what matters is what persons can do and be with their primary goods, not the goods themselves; persons differ in their capacity to convert resources into achievements (a person with a disability needs more resources to achieve mobility than a non-disabled person), so equal resources do not produce equal substantive freedom. Welfarist utilitarianism is also inadequate: subjective preferences are adaptive (persons in deprivation may report being satisfied), so welfare is the wrong metric; what matters is the capability to function, not the achieved satisfaction. Walk through the conceptual architecture: functionings (the various states of being and doing — being well-nourished, being literate, participating in community life), capabilities (the freedoms or substantive opportunities to achieve various functioning combinations). Note the disagreement between Sen and Nussbaum: Sen resists specifying a definitive list of capabilities (the list is to be settled by democratic deliberation in each society); Nussbaum produces a definitive list of central human capabilities grounded in an Aristotelian conception of human flourishing. Note the practical influence: the UN Human Development Index (Sen contributed to its design) operationalizes capability-approach insights in development measurement; the approach has shaped contemporary work on disability, gender, and development ethics. The approach connects to political-philosophy debates about the metric of justice, to ethics debates about welfare and well-being, and to philosophy-of-economics debates about the foundations of welfare measurement.',
    ARRAY['capabilities_approach', 'sen_nussbaum_capabilities', 'human_capabilities_theory'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'desert_theory_political',
    'Desert Theory (Political)',
    ARRAY['political'],
    'The view that the just distribution of advantages and burdens is the one that tracks desert: persons should receive what they deserve in light of their productive contributions, efforts, virtues, or responsible choices. Pre-Rawlsian distributive theory took desert seriously; Rawls 1971 famously argued that the distribution of natural talents is morally arbitrary and therefore cannot ground desert claims, and contemporary egalitarian theory has been largely hostile to desert. Miller 1999 PRINCIPLES OF SOCIAL JUSTICE has led the partial revival of desert as one principle of justice (operating in market contexts, alongside other principles operating in solidaristic and procedural contexts).',
    'Teach desert-theory as a position students should understand both for its pre-Rawlsian importance and for its partial contemporary revival. Open with the basic structure of desert claims: a person deserves X in virtue of some desert basis Y (productive contribution, effort, virtue, responsible choice) where Y has the appropriate connection to X. Note the four standard desert bases in distributive contexts: contribution (one deserves a share proportional to what one contributes to the social product), effort (one deserves a share proportional to one''s effort, regardless of differential productivity), virtue (one deserves rewards in proportion to one''s moral character), and responsible choice (one deserves the foreseeable consequences of one''s voluntary choices — a basis luck-egalitarianism partly takes over). Walk through Rawls''s critique: the natural distribution of talents is "morally arbitrary" — no one deserves their starting endowment of capacity to make productive contributions — so productive-contribution desert cannot ground distributive principles. The argument extends to character: even effort and conscientiousness depend on developmentally-formed traits, themselves the product of factors outside the agent''s control. Note the standard replies: the "deep" causal-determinism objection proves too much (it would undermine moral responsibility entirely); desert can be grounded in the institutional rules under which contributions are recognized, not in metaphysical facts about agency; common-sense moral practice deeply embeds desert claims that political philosophy should accommodate. Note the contemporary partial-revival positions: Miller 1999 distinguishes spheres of justice (markets reward desert; solidaristic associations distribute by need; democratic procedures distribute by equality) and gives desert an enduring role in market contexts; Olsaretti 2004 LIBERTY, DESERT AND THE MARKET defends a market-grounded desert account.',
    ARRAY['desert_based_distribution', 'desert_egalitarianism', 'meritocratic_justice'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'democracy',
    'Democracy',
    ARRAY['political'],
    'The form of government in which political authority ultimately derives from the people governed. Contemporary democratic theory addresses both institutional questions (direct vs representative; majoritarian vs constitutional; presidential vs parliamentary; deliberative vs aggregative) and normative questions (what justifies democracy — intrinsic value of self-government, instrumental value in producing good outcomes, epistemic value in tracking the truth, or some combination). Major contemporary positions: aggregative democracy (democracy as the fair aggregation of pre-political preferences); deliberative democracy (Habermas, Cohen — democracy as the institutionalization of public reason); epistemic democracy (Estlund 2008, Anderson 2006 — democracy as a truth-tracking institution).',
    'Teach democracy as both an institutional concept and a normative-philosophical concept students should be careful to keep distinct. Open with the institutional taxonomy (direct, representative, deliberative; majoritarian, constitutional; presidential, parliamentary; first-past-the-post, proportional; etc.) so students can locate later normative discussions appropriately. Move to the normative question: what makes democracy valuable? Three principal answers. Intrinsic theories (Christiano 2008, Kolodny 2014) hold that democracy is valuable as the institutional realization of equal status of citizens — non-democratic government inherently treats some as more authoritative than others. Instrumental theories (Mill, contemporary economic-democracy theorists) hold that democracy is valuable because it tends to produce better outcomes (information aggregation, accountability, peaceful conflict resolution). Epistemic theories (Estlund 2008 DEMOCRATIC AUTHORITY, Anderson 2006, Landemore 2013) hold that democracy is a truth-tracking institution under suitable conditions (Condorcet jury theorem; cognitive diversity advantages over expertise). Note the distinctive challenges to each: intrinsic theories have to explain why minority rule (rotation, lottery) does not equally realize equal status; instrumental theories have to defend the empirical claims (against authoritarian-meritocracy challenges, against jury-theorem-failure conditions); epistemic theories have to handle persistent failures (climate science denial, conspiracy theories, media-environment degradation). Note the principal contemporary critiques: epistocratic challenge per Brennan 2016 AGAINST DEMOCRACY (informed minority should rule); deliberative-democracy critiques of aggregative shallow democracy (preferences are formed in deliberation, not given prior to it); republican concerns about elite capture (democratic procedures can mask substantive domination). Distinguish democratic theory (about regime form) from theories of democratic authority (about the obligations citizens have under democratic regimes).',
    ARRAY['democratic_government', 'democratic_theory', 'rule_of_the_people'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'political_legitimacy',
    'Political Legitimacy',
    ARRAY['political'],
    'The normative property a political order has when its claim to authority is morally justified. Distinguished from political authority itself (legitimacy is what makes authority morally rightful); from descriptive sociological legitimacy (Weber — what subjects believe makes the order rightful); and from justice (a legitimate political order need not be perfectly just, and a perfectly just order may not be legitimate if it lacks the relevant authority-grounding properties). Major theories ground legitimacy in actual or hypothetical consent of the governed (Locke; Rawls), in fair-play obligations created by participation in beneficial cooperative schemes (Hart 1955), in democratic procedure (Habermas; Cohen), in beneficial consequences (welfare-instrumentalist accounts), or in some combination.',
    'Teach political legitimacy as a normative-philosophical concept students should distinguish carefully from related concepts. Open with the canonical distinctions: legitimacy vs power (legitimacy is normative, not causal); legitimacy vs authority (legitimacy makes authority morally justified; an unauthorized claimant might yet be powerful and accepted); legitimacy vs justice (legitimacy can attach to imperfectly just orders; perfect justice does not entail legitimacy); legitimacy vs sociological-Weberian acceptance (the question is whether the order is rightfully accepted, not whether it is in fact accepted). Walk through the major theories. Consent theories: Locke 1689 grounds legitimacy in actual or tacit consent — the difficulties (most subjects never expressly consent; tacit consent through residence is too weak — Hume 1748) lead to hypothetical-consent theories (Rawls — legitimate orders are those that would be agreed to under fair conditions; Scanlon 1998''s contractualism in the moral domain has the analogous structure). Fair-play theories: Hart 1955 grounds legitimacy in the fair-play obligation participants in beneficial cooperative schemes have to bear their share of the costs. Democratic theories (Habermas, Cohen): legitimacy depends on the order''s institutional realization of public deliberative reason among free and equal citizens. Welfare-instrumentalist theories: legitimacy attaches to orders that successfully promote subjects'' welfare or other valuable outcomes. Mixed theories combine consent, fair-play, and instrumental considerations (Rawls 1993; Estlund 2008). Note the standard challenges: the problem of "tacit consent" (born into a state, no genuine option to refuse); the variance across regimes (most actual states fall short of any plausible legitimacy standard yet command obedience); the relation to political obligation (does legitimacy entail an obligation to obey?).',
    ARRAY['legitimacy_political', 'legitimate_authority', 'legitimate_government'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'political_obligation',
    'Political Obligation',
    ARRAY['political'],
    'The moral duty (if there is one) to obey the law and support the institutions of one''s political community. Distinguished from political legitimacy (the property the institutions have) by being the correlative property of subjects: legitimacy is the right to rule, obligation is the duty to obey. Major theories: consent theories (Locke — obligation arises from express or tacit consent); fair-play theories (Hart 1955, Rawls 1971 — obligation arises from receiving benefits from the cooperative scheme of social institutions); gratitude theories (we owe the state for benefits received); natural-duty theories (Rawls 1971 — duty to support just institutions independent of consent); associative-obligation theories (Dworkin 1986 — special obligations to one''s political community akin to obligations to family or friends).',
    'Teach political obligation as a contested concept that students should approach with caution about its existence. Open with the distinction from related concepts: obligation (morally required action) vs duty (general moral requirement) vs reasons (considerations that count in favor of action). Political obligation, properly so called, is content-independent and exclusionary — one is bound to obey because the law requires, not because one has independently judged the action right; the law''s directive replaces ordinary moral deliberation. The philosophical-anarchist position (Wolff 1970, Simmons 1979 MORAL PRINCIPLES AND POLITICAL OBLIGATIONS, Smith 1973) holds that there is no general political obligation: theories purporting to ground it all fail. Walk through the major theories and their objections. Consent theories: most subjects never expressly consent; tacit consent is too weak; hypothetical consent does not bind. Fair-play theories: only voluntary acceptance of benefits creates obligation, but most political benefits are received non-voluntarily (Nozick 1974''s "thrown into the air" critique). Gratitude theories: confuse owing thanks with owing obedience. Natural-duty theories: the duty to support just institutions does not generate a particular obligation to one''s own state rather than the closest just one. Associative-obligation theories: the analogy to family is contested; political community is too large and impersonal to ground genuinely associative obligations. Note the practical-political implications: if there is no political obligation, individual disobedience is not (per se) wrong; civil disobedience and conscientious refusal need not be defended as exceptions to a general duty to obey but can be assessed on their first-order moral merits. Most contemporary theorists accept some form of weak or partial obligation while rejecting the strong consent-based account.',
    ARRAY['obligation_to_obey', 'duty_of_obedience', 'civil_obligation'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'human_rights',
    'Human Rights',
    ARRAY['political'],
    'Universal moral entitlements held by all persons in virtue of their humanity, codified in the Universal Declaration of Human Rights 1948 and the major international covenants (ICCPR 1966 on civil and political rights; ICESCR 1966 on economic, social, and cultural rights). Distinguished from natural rights by their typically secularized foundations and their institutional-international codification, but inheriting the natural-rights structure (universal, pre-institutional, constraining government). Two principal contemporary theoretical orientations: moral conceptions (Griffin 2008 ON HUMAN RIGHTS — human rights protect normative agency; Gewirth — they derive from agency''s necessary preconditions) and political conceptions (Rawls 1999 LAW OF PEOPLES; Beitz 2009 THE IDEA OF HUMAN RIGHTS — human rights are defined by their practical role in international politics).',
    'Teach human rights as the dominant contemporary international-moral framework and as the locus of substantial recent philosophical disagreement. Open with the institutional context (UDHR, ICCPR, ICESCR, regional human-rights instruments — European Convention, African Charter, American Convention) so students see human rights as a working international vocabulary, not just a philosophical concept. Walk through the structural features: universality (held by all persons), inalienability (cannot be forfeited), pre-institutional grounding (logically prior to any particular legal recognition), and (controversial) interpretive-priority over conflicting domestic law. Note the canonical taxonomic distinctions: civil and political rights (largely negative — non-interference: against torture, arbitrary detention, discrimination; for free speech, association, religion, fair trial, political participation) vs economic, social, and cultural rights (largely positive — provision: education, healthcare, adequate standard of living, work, social security). Walk through the two principal theoretical orientations. Moral conceptions ground human rights in moral premises about human nature (Griffin 2008 — protection of normative agency; Gewirth 1978 — necessary conditions of action). Political conceptions ground them in their practical role: Rawls 1999 holds human rights are the rights whose violation by a state warrants international intervention or sanctions in the international community of peoples; Beitz 2009 develops the political conception in detail, treating human rights as standards governing the international evaluation of state conduct. Note the principal contestation: cultural-relativist objections (whose human rights — Western-liberal? Are they cross-culturally legitimate?); the proliferation problem (the rights enumeration has expanded — Are all these really rights?); the negative-positive question (Are economic rights genuinely rights?); the foundations question (Without religious or natural-law backing, what grounds them?). Despite contestation, the human-rights framework remains the dominant international-moral vocabulary.',
    ARRAY['universal_human_rights', 'international_human_rights', 'rights_of_man'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'toleration',
    'Toleration',
    ARRAY['political'],
    'The political stance of refraining from suppressing beliefs and practices one disapproves of, particularly in matters of religion and conscience but extending to broader pluralism about conceptions of the good life. Locke 1689 LETTER CONCERNING TOLERATION argued the state has no authority to coerce religious belief because such belief cannot be produced by coercion and falls outside the scope of legitimate political concern. Mill 1859 ON LIBERTY developed a broader argument for toleration of dissenting opinion grounded in the value of free inquiry, individual self-development, and the conditions of progress. Rawls 1993 POLITICAL LIBERALISM extended toleration into the doctrine of public reason: in a democratic society characterized by reasonable pluralism, the political conception of justice should not depend on contested comprehensive views.',
    'Teach toleration as a foundational political concept for liberal political theory and as a continuing site of contemporary philosophical debate. Open with the conceptual structure: toleration is not endorsement; the tolerator has the standing to suppress (legal authority, social power, parental control) and refrains from exercising it; the toleration-paradox arises because endorsement is too weak (you do not tolerate what you approve) but power-with-distaste is the structural condition. Walk through the canonical historical arguments: Locke''s religious-toleration argument (state authority over conscience is both impossible — coercion cannot produce belief — and illegitimate — religion lies outside the political domain); Mill''s broader argument from individuality and the conditions of intellectual progress (truth emerges from open contestation; conformity and silenced dissent both impoverish individual development). Walk through the contemporary developments: Rawls''s political liberalism extends toleration into the principle of public reason (constitutional essentials should be defensible by considerations not dependent on contested comprehensive doctrines); the "limits of toleration" question (can a tolerant society tolerate the intolerant — Popper 1945 paradox); the relation to multiculturalism (toleration of practices vs recognition of cultures). Note the standard objections to liberal toleration as currently formulated: that it presupposes a public-private distinction (suppressed and historically contested by feminist political theory); that it treats only certain pluralisms (those compatible with liberal background commitments) as candidates for toleration (Connolly''s critique of Rawls''s reasonable-pluralism formulation); that it underestimates the demands of recognition (mere toleration insufficiently respects identities at stake — Honneth 1995). The toleration-recognition distinction is central to contemporary multiculturalism debates.',
    ARRAY['religious_toleration', 'political_toleration', 'tolerance_political'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'socialism',
    'Socialism',
    ARRAY['political'],
    'The family of political-economic doctrines committing to collective or social ownership of the means of production, motivated by commitments to economic equality, democratic self-determination, and the abolition or substantial mitigation of class-based exploitation. Marx 1867 CAPITAL provides the canonical structural critique of capitalist exploitation through the labor theory of value and the appropriation of surplus value; subsequent socialist theory has split between revolutionary and reformist strategies, between centralized-planning and market-socialist economic organizations, and between liberty-prioritizing and equality-prioritizing normative emphases. Contemporary academic socialism is largely democratic-socialist (Cohen 2009 WHY NOT SOCIALISM?; Wright 2010 ENVISIONING REAL UTOPIAS; market-socialist proposals per Roemer 1994).',
    'Teach socialism as both a critical analysis of capitalist political economy and a positive political-economic vision students should be able to discuss without conflating its many internal varieties. Open with the foundational normative commitments shared across socialist positions: economic equality (against the systemic inequalities capitalism produces), democratic control of economic life (against the rule of private capital), and the elimination of exploitative class relations. Walk through the Marxian analytical framework: the labor theory of value (in classical Marxism — workers produce value but capitalists appropriate the surplus); the structural critique of capitalism (concentration, crisis, alienation, commodification of labor); the historical-materialist account of social-political change. Walk through the contemporary normative arguments per Cohen 2009 (the camping-trip thought experiment — among friends on a camping trip, market-capitalist relations would be inappropriate; this suggests the moral basis of socialist commitments). Walk through the major internal divisions: revolutionary vs reformist strategies (the 19th-century Marxist-Bernsteinian split); centrally-planned vs market socialism (Hayek-Mises socialist-calculation debate; Roemer 1994 A FUTURE FOR SOCIALISM defending market-socialist coupon-economy proposals); democratic socialism vs social democracy (the former targets fundamental economic restructuring; the latter accepts capitalist ownership while extensively regulating and taxing it for egalitarian ends). Note the distinctively socialist concepts: alienation (Marx 1844 — workers separated from the products and process of their labor); exploitation (technical Marxian sense — appropriation of surplus value; or moral sense — taking unfair advantage of asymmetric power); class consciousness (the political-psychological precondition of collective action). Note the standard liberal objections (incentive problems with non-market allocation; planning impossibility; freedom-restriction in collective ownership) and the standard socialist replies (markets generate greater unfreedom than they avoid; planning is feasible with adequate information technology; collective ownership expands genuine freedom).',
    ARRAY['socialist_political_theory', 'democratic_socialism', 'collective_ownership_doctrine'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'luck_egalitarianism',
    'Luck Egalitarianism',
    ARRAY['political'],
    'The view that the just distribution of advantages and burdens is one in which no one is worse off than another due to factors outside their responsible control (brute luck), but inequalities arising from responsible choices (option luck) are permissible. Cohen 1989 ON THE CURRENCY OF EGALITARIAN JUSTICE, Arneson 1989 EQUALITY AND EQUAL OPPORTUNITY FOR WELFARE, and Dworkin 1981 WHAT IS EQUALITY? developed the position from somewhat different starting points — Dworkin from equality of resources, Arneson from equality of opportunity for welfare, Cohen from equality of access to advantage. Anderson 1999 WHAT IS THE POINT OF EQUALITY? launched the principal contemporary critique, contrasting luck-egalitarianism with relational equality.',
    'Teach luck-egalitarianism as the dominant late-20th-century refinement of Rawlsian egalitarian theory and as the position contemporary relational-egalitarian theory positions itself against. Open with the foundational distinction between brute luck (outcomes outside the agent''s control — natural endowments, accidents, gambles one had no reason to anticipate) and option luck (outcomes flowing from the agent''s deliberate choices — investments, risks one chose to run). Luck egalitarianism takes brute-luck inequalities to be unjust and option-luck inequalities to be permissible. Walk through the principal variants. Cohen''s equality of access to advantage: equalize whatever causes shortfalls in well-being for which the agent is not responsible; well-being itself is composite (welfare, resources, capabilities). Arneson''s equality of opportunity for welfare: equalize the prospects, evaluated under counterfactual rationality, for achieving valued ends. Dworkin''s equality of resources: equalize starting endowments through a hypothetical-auction mechanism that internalizes the costs persons impose on others through the choice of expensive tastes. Walk through Anderson''s critique: luck-egalitarianism is too harsh in its treatment of persons whose choices led to bad outcomes (the "abandonment of the imprudent"); too disrespectful in its requirement that persons document their misfortune to claim assistance; misses the point of egalitarianism, which should be about social-relational equality (against hierarchy and oppression) rather than distributional equality across choice-circumstance lines. Note the principal contemporary positions: relational egalitarianism (Anderson, Scheffler 2003) treats equality as a feature of social relationships rather than a pattern of distribution; sufficientarianism (Frankfurt 1987) holds the relevant moral concern is not equality but having enough; prioritarianism (Parfit 1991) holds priority should go to the worst-off without committing to equality per se.',
    ARRAY['luck_egalitarian_theory', 'choice_circumstance_egalitarianism', 'cohen_arneson_dworkin'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'conservatism',
    'Conservatism',
    ARRAY['political'],
    'A political tradition emphasizing tradition, prudence, gradualism, the organic interconnection of social institutions, and skepticism about the rationalist reform of political life. Burke 1790 REFLECTIONS ON THE REVOLUTION IN FRANCE provided the founding modern statement, criticizing the French revolutionaries'' attempt to remake society from abstract principle and defending the accumulated practical wisdom of inherited institutions. Subsequent conservative thought develops several strands: traditionalist conservatism (Burke, Oakeshott 1962 RATIONALISM IN POLITICS, Scruton); religious conservatism (T.S. Eliot, contemporary Catholic and Orthodox traditions); fusionist conservatism (the late-20th-century American conservative synthesis of traditionalism and free-market commitments).',
    'Teach conservatism as a distinct political-philosophy tradition students should not confuse with right-wing political alignment in any particular contemporary setting. Open with the foundational commitments: tradition as accumulated practical wisdom (institutions that have endured embody knowledge that explicit theorizing cannot capture); prudence as the cardinal political virtue (slow change, attention to unintended consequences, distrust of comprehensive reform); the organic conception of society (institutions are interconnected; reform of one part disturbs the others); skepticism about rationalist political design (abstract principle is no substitute for the wisdom embedded in practice). Walk through the canonical Burkean argument: the French revolutionaries attempted to remake society from abstract principle (the Rights of Man, popular sovereignty, the cult of Reason); the result was terror, war, and ultimately Napoleonic dictatorship. The English settlement, by contrast, evolved through gradual reform within continuous institutional traditions. Walk through Oakeshott 1962 RATIONALISM IN POLITICS: rationalism in politics — the application of explicit theory to comprehensive political reform — is structurally unsuited to political life, which is a practice transmitted through participation rather than a problem solvable by reason alone. Note the principal internal varieties. Traditionalist conservatism (Burke, Oakeshott, Scruton) emphasizes institutional continuity and the limits of reason. Religious conservatism (Eliot, contemporary Catholic and Orthodox political thought) grounds the political order in religious moral foundations. Fusionist conservatism (American post-1950s) couples traditional cultural-religious commitments with classical-liberal economic commitments — a synthesis Frank Meyer attempted to defend philosophically; subsequent strain points (libertarian-communitarian; populist-elitist) have been considerable. Distinguish from libertarianism (which is rationalist and individualist), from fascism and authoritarianism (which involve mobilization of state power for transformative ends conservatives would oppose), and from reactionary politics (which seeks to restore an earlier social order; conservatism is meliorist within the present, not restorationist).',
    ARRAY['burkean_conservatism', 'traditionalist_conservatism', 'oakeshott_conservatism'],
    'INTERPRETED',
    'ai-seed',
    9
  ),
  (
    'multiculturalism',
    'Multiculturalism',
    ARRAY['political'],
    'The political-philosophy position holding that liberal-democratic societies should accommodate the cultural and group identities of their members through group-differentiated rights, recognition of distinctive cultural practices, and institutional adjustments to background majority norms. Kymlicka 1995 MULTICULTURAL CITIZENSHIP provided the canonical contemporary statement, distinguishing national minorities (whose societal cultures merit self-government rights) from immigrant groups (whose cultural-difference accommodation merits polyethnic rights). The recognition tradition (Taylor 1992 MULTICULTURALISM AND THE POLITICS OF RECOGNITION; Honneth 1995 THE STRUGGLE FOR RECOGNITION) provides the philosophical-anthropological grounding for treating recognition as a fundamental human need.',
    'Teach multiculturalism as a major contemporary political-philosophy position with roots in both communitarian critique and liberal political theory, and as a position with serious internal tensions students should appreciate. Open with the central claim: justice in pluralistic societies requires not merely individual rights and equal treatment but also recognition of group identities and group-differentiated provision (sometimes including special rights or institutional accommodation). Walk through the Kymlicka framework: the distinction between national minorities (sub-state national groups — Quebecois, Catalans, indigenous peoples — whose claims to societal-cultural integrity warrant self-government rights) and immigrant groups (immigrant communities whose cultural-distinctness claims warrant polyethnic accommodations — religious holidays, dress codes, language services). Walk through Taylor 1992: recognition is a vital human need; misrecognition (being represented in distorting and demeaning ways) is a form of harm; political institutions should provide the conditions for authentic recognition. Walk through Honneth 1995: recognition is the foundational structure of social life, with three principal forms (love in the intimate sphere, respect in the legal-political sphere, esteem in the social-economic sphere). Note the principal internal tensions. The redistribution-recognition debate per Fraser 1995, 2000: are claims of cultural recognition complementary to or in tension with claims of economic redistribution? Fraser argues both axes are independent; Honneth argues recognition is foundational and redistribution-claims can be reconstructed in recognition terms. The minorities-within-minorities problem per Okin 1999 IS MULTICULTURALISM BAD FOR WOMEN?: cultural-group accommodation can shelter intra-group oppression of women, dissenters, religious minorities, etc. — multiculturalism risks freezing group boundaries and authorizing group leaders to speak for all members. The toleration-recognition distinction (mere toleration treats minority cultures as objects to be put up with; recognition treats them as deserving substantive valuation). Note the contemporary critiques from both liberal universalists (rights are individual; group-differentiated rights compromise equal citizenship) and from communitarians (multicultural accommodation typically still presupposes liberal-individualist background commitments).',
    ARRAY['multicultural_political_theory', 'multicultural_citizenship', 'group_differentiated_rights'],
    'INTERPRETED',
    'ai-seed',
    9
  );

-- Edges: 34 within-domain pedagogical_prerequisite INSERTs.
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  ('political_philosophy', 'justice', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('political_philosophy', 'state_political', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('political_philosophy', 'liberty_political', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('political_philosophy', 'equality_political', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('political_philosophy', 'social_contract_theory', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('justice', 'distributive_justice', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('state_political', 'sovereignty', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('state_political', 'political_authority', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('liberty_political', 'negative_rights', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('liberty_political', 'positive_rights', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('liberty_political', 'natural_rights', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('liberty_political', 'liberalism', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('liberty_political', 'republicanism', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('political_authority', 'democracy', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('political_authority', 'political_legitimacy', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('political_authority', 'political_obligation', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('social_contract_theory', 'justice_as_fairness', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('social_contract_theory', 'political_legitimacy', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('social_contract_theory', 'political_obligation', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('distributive_justice', 'justice_as_fairness', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('distributive_justice', 'libertarianism_political', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('distributive_justice', 'communitarianism', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('distributive_justice', 'capability_approach', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('distributive_justice', 'desert_theory_political', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('distributive_justice', 'socialism', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('equality_political', 'capability_approach', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('natural_rights', 'libertarianism_political', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('natural_rights', 'human_rights', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('liberalism', 'communitarianism', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('liberalism', 'toleration', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('liberalism', 'multiculturalism', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('justice_as_fairness', 'luck_egalitarianism', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('communitarianism', 'multiculturalism', 'pedagogical_prerequisite', 'ai-seed', 9),
  ('political_obligation', 'conservatism', 'pedagogical_prerequisite', 'ai-seed', 9);

COMMIT;
