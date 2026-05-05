-- Migration: 0070_seed_language_part1
-- Purpose: Twelfth Phase 5 seed migration (the philosophy-of-language file) —
--   the analytic-tradition core of philosophy of language and within-domain
--   pedagogical_prerequisite edges. Authored in S-0071 against task P5-08
--   "Philosophy of language seed" of target T-PHASE-5 per
--   engine/build_readiness/phase_5.md (gate report) and
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md. P5-08 is
--   a single-task subdomain per phase_5.md T1-B (philosophy of language is
--   dominated by analytic-tradition core, well-bounded enough for a single
--   migration). Covers the eight coverage clusters identified at master-plan
--   time: foundation (the field umbrella, meaning, reference, the
--   Fregean sense/reference distinction, the proposition); reference and
--   names (proper names, descriptivist and causal theories of reference,
--   rigid designators, definite descriptions, Russell''s theory of
--   descriptions); meaning theories (truth-conditional semantics in
--   the Davidsonian tradition, the use theory of meaning in late
--   Wittgenstein, verificationism in the logical-positivist line,
--   semantic compositionality); speech acts and Gricean pragmatics
--   (Austin/Searle speech acts, performative utterances, the Gricean
--   maxims, conversational implicature, presupposition); externalism
--   about content (Putnam-Burge semantic externalism, the Twin Earth
--   thought experiment, narrow content as the internalist counterpoint);
--   indexicality and context (indexical expressions, Kaplan''s
--   character/content two-dimensional framework); truth in language
--   (deflationary theories of truth, Tarski''s T-schema as the technical
--   foundation Davidson''s program builds on); plus one adjacent edge
--   case (linguistic relativity, the Sapir-Whorf hypothesis as the
--   philosophically loaded interface between philosophy of language and
--   philosophy of mind/cognitive science). Within-domain edges span the
--   eight clusters with the pedagogical-prerequisite structure rooted at
--   philosophy_of_language. Cross-domain edges (causal_theory_of_
--   reference and semantic_externalism ↔ metaphysics on natural kinds and
--   Kripke-Putnam essentialism; semantic_externalism ↔ philosophy of mind
--   on content externalism, ↔ epistemology on the asymmetry of self-
--   knowledge; speech_act and conversational_implicature ↔ political
--   philosophy on hate-speech and silencing literatures; tarskis_t_schema
--   ↔ logic on formal theories of truth and the model-theoretic apparatus;
--   indexical ↔ philosophy of mind on de se attitudes; sense_and_reference
--   ↔ epistemology on the puzzle of cognitive significance; verificationism
--   ↔ philosophy of science on the logical-positivist criterion of
--   meaningfulness) remain P5-11''s exclusive surface.
-- Loads tables: public.nodes (28 INSERTs), public.edges (31 INSERTs),
--   public.settings (1 UPDATE incrementing graph_version 12 -> 13).
-- Preconditions:
--   * Phase 3 schema in place: public.nodes, public.edges, public.settings
--     all exist with the columns and CHECKs from 0002, 0003, 0004.
--   * settings.graph_version = 12 at session boot (post-S-0070 per
--     ROUTING.md narrative — most recent applied seed at this prefix
--     range was 0046_seed_mind_part1.sql which wrote 12).
--     The increment contract per
--     product/seed-graph/migrations/ROUTING.md is honored: all node/edge
--     INSERTs in this migration carry graph_version_added = 13 (the
--     post-increment value).
--   * No prior migrations under prefix 0070-0079; this is the first
--     philosophy-of-language seed file.
--   * P5-01a epistemology core applied (the only depends_on for P5-08).
--     No edge in this migration references epistemology nodes — within-
--     language seeding here; cross-domain bridges to epistemology
--     (sense_and_reference ↔ cognitive significance; semantic_externalism
--     ↔ self-knowledge; norm_of_assertion in P5-01b ↔ assertion-as-speech-
--     act here) land at P5-11 per phase_5.md T2-G #1.
-- Postconditions:
--   * 28 new nodes exist in public.nodes with id, label, summary,
--     teaching_notes, aliases, confidence_level=INTERPRETED,
--     domain[]={'language'}, status=active, graph_version_added=13.
--   * 31 new edges exist in public.edges with edge_type=
--     pedagogical_prerequisite, graph_version_added=13. All edges are
--     within-domain (source and target both tagged language); cross-
--     domain edges are P5-11''s exclusive responsibility. No edges
--     reference nodes outside this migration; the philosophy-of-language
--     subdomain is structurally self-contained at the analytic-tradition
--     core (the cross-domain reaches identified above are real but live
--     in P5-11).
--   * settings.graph_version = 13.
-- Invariants:
--   * Node IDs are slugified TEXT, lowercase, underscore-delimited
--     (architecture.md "Node Schema" + 0002_nodes.sql contract).
--   * Every edge satisfies the schema FK: source_id and target_id
--     reference public.nodes(id) values that this migration also inserts.
--   * No edge cycles in the pedagogical_prerequisite subgraph. Tier
--     assignment (relative to this migration''s nodes only — there are
--     no cross-migration endpoints): T0 philosophy_of_language; T1
--     meaning, reference; T2 sense_and_reference, proposition,
--     proper_name, definite_description, indexical, speech_act,
--     use_theory_of_meaning, verificationism, linguistic_relativity;
--     T3 descriptivism, causal_theory_of_reference,
--     russells_theory_of_descriptions, performative_utterance,
--     gricean_maxims, presupposition, truth_conditional_semantics,
--     deflationary_theory_of_truth; T4 rigid_designator,
--     conversational_implicature, compositionality_semantic,
--     character_and_content, semantic_externalism (deepened path via
--     causal_theory_of_reference even though reference also reaches it
--     directly), tarskis_t_schema; T5 twin_earth, narrow_content (under
--     semantic_externalism). Every edge points from a strictly
--     lower-tier node to a strictly higher-tier node — no edges point
--     back. SCC freedom holds; validate.py''s Kosaraju check confirms
--     post-apply.
--   * UNIQUE (source_id, target_id, edge_type) per 0003_edges.sql holds:
--     no triple in this migration duplicates any other triple (the 31
--     edges are pairwise distinct in (source_id, target_id) since
--     edge_type is uniformly pedagogical_prerequisite).
-- Non-responsibilities:
--   * Does not author cross-domain edges. Concepts authored here that
--     have cross-domain reach include: causal_theory_of_reference and
--     semantic_externalism bridge to metaphysics (P5-02a/b on natural
--     kinds and Kripke-Putnam essentialism); semantic_externalism
--     bridges to philosophy of mind (P5-07a on content externalism and
--     mental content individuation) and to epistemology (P5-01b on the
--     asymmetry of self-knowledge against externalist content);
--     speech_act and conversational_implicature bridge to political
--     philosophy (P5-05 on hate-speech and silencing literatures —
--     Langton, MacKinnon, McGowan); tarskis_t_schema bridges to logic
--     (P5-03 on formal theories of truth, the T-schema as the bridge
--     between syntax and model theory); indexical bridges to philosophy
--     of mind (P5-07a on de se attitudes and self-locating beliefs —
--     Perry, Lewis); sense_and_reference bridges to epistemology
--     (P5-01a/b on the cognitive significance puzzle that motivated
--     Frege''s 1892 distinction); verificationism bridges to philosophy
--     of science (P5-09 on the logical-positivist criterion of
--     meaningfulness and its post-Quinean rejection). Wait for P5-11''s
--     cross-bridges pass.
--   * Does not register any new edge predicates. Only
--     pedagogical_prerequisite is used (already in the v1 registry per
--     PREDICATE_MANIFEST.md).
--   * Does not seed any historical_influence edges.
--   * Does not author the additional sub-range slots (0071-0079).
--     Those slots remain reserved for any future Phase 6+ telemetry-
--     driven extensions to philosophy of language (e.g., specific
--     topics warranting follow-on seeding: pejoratives and slurs;
--     metaphor and figurative language; fictional discourse and
--     fictional names; generic statements; dynamic semantics; formal
--     pragmatics extensions; contextualism in semantics; expressivism
--     about evaluative discourse; truthmaker semantics); this seed
--     completes P5-08''s task at the granularity principle within the
--     0070 file.
-- Cross-cutting decisions:
--   * confidence_level distribution: 28/28 INTERPRETED (100%). Per
--     phase_5.md T2-B the floor is INTERPRETED >= 70%; the ceiling is
--     SYNTHETIC <= 20%. EXTRACTED is reserved for nodes whose definition
--     is directly lifted from a structural reference''s entry inventory;
--     this seed authors original pedagogical prose for every summary and
--     teaching_notes per ADR 0011 (no hosted copyrighted material) so
--     EXTRACTED is 0%. SYNTHETIC is also 0% because every concept here
--     is well-named in the SEP/IEP entry inventory and corresponds to a
--     concept the contemporary analytic philosophy-of-language
--     literature (Frege, Russell, Wittgenstein, Carnap, Quine, Davidson,
--     Kripke, Putnam, Burge, Kaplan, Lewis, Stalnaker, Grice, Austin,
--     Searle, Strawson, Tarski, Horwich) explicitly names. Mirrors the
--     eleven prior Phase 5 subject seeds (P5-01a/b epistemology,
--     P5-02a/b metaphysics, P5-03 logic, P5-04a/b ethics, P5-05
--     political philosophy, P5-06 aesthetics, P5-07a/b philosophy of
--     mind).
--   * domain[] cardinality: every node carries exactly one tag,
--     ''language''. Multiple cross-domain reaches exist (semantic
--     externalism intersects philosophy of mind and metaphysics;
--     speech_act intersects political philosophy; tarskis_t_schema
--     intersects logic; verificationism intersects philosophy of
--     science) but per phase_5.md T2-G #4 (domain-tag cardinality
--     explosions vector), cross-domain tagging belongs to P5-11. The
--     canonical home for each of these concepts in the analytic
--     literature is the philosophy-of-language sub-literature, so the
--     single ''language'' tag is correct here.
--   * provenance: ''ai-seed'' for every node and edge. Same as
--     P5-01a/b, P5-02a/b, P5-03, P5-04a/b, P5-05, P5-06, P5-07a/b.
--   * Node selection rationale: 28 concepts cover the eight core
--     analytic-tradition clusters at the granularity principle:
--     (1) foundation (5) [philosophy_of_language, meaning, reference,
--     sense_and_reference, proposition] — the field umbrella, the two
--     central explananda, Frege''s 1892 distinction that organizes
--     post-Fregean reference theory, and the proposition as the unit of
--     truth-evaluable content;
--     (2) reference and names (6) [proper_name, descriptivism,
--     causal_theory_of_reference, rigid_designator, definite_description,
--     russells_theory_of_descriptions] — the two competing theories of
--     name reference (Frege-Russell-Searle descriptivism vs. Kripke-
--     Putnam-Donnellan causal theory), Kripke''s rigid-designator
--     analysis as the core technical posit, definite descriptions as
--     the contrasting case where Russell''s 1905 paraphrase analysis
--     lives;
--     (3) meaning theories (4) [truth_conditional_semantics,
--     use_theory_of_meaning, verificationism, compositionality_semantic]
--     — the three major non-eliminativist theories of meaning
--     (Davidson''s truth-conditional program, late Wittgenstein''s use
--     theory, the logical-positivist verification criterion), plus
--     compositionality as the structural constraint any theory of
--     meaning must respect (Frege''s context principle in another
--     direction);
--     (4) speech acts and Gricean pragmatics (5) [speech_act,
--     performative_utterance, gricean_maxims, conversational_implicature,
--     presupposition] — Austin''s 1955 William James lectures and
--     Searle''s formalization, performatives as the seed case
--     (constatives vs. performatives), Grice''s 1975 Logic and
--     Conversation maxims as the central pragmatic machinery,
--     conversational implicature as Grice''s most influential
--     contribution, presupposition as the third pragmatic phenomenon
--     (Strawson 1950, Stalnaker''s common-ground formalization);
--     (5) externalism about content (3) [semantic_externalism,
--     twin_earth, narrow_content] — the Putnam-Burge thesis that meaning
--     ain''t in the head, Putnam''s 1975 Twin Earth thought experiment
--     as the canonical illustration, narrow_content as the internalist
--     attempt to recover a head-bounded notion of content (Fodor,
--     Loar);
--     (6) indexicality and context (2) [indexical, character_and_content]
--     — indexical expressions (I, here, now, this, that) as the
--     phenomenon, Kaplan''s 1989 Demonstratives two-dimensional
--     character/content framework as the standard analysis;
--     (7) truth in language (2) [deflationary_theory_of_truth,
--     tarskis_t_schema] — deflationary theories (Ramsey-Quine-Horwich
--     redundancy/disquotational/minimalism family) as the central post-
--     Tarskian alternative to substantive theories of truth (which were
--     largely covered in P5-01a''s truth_correspondence node), Tarski''s
--     1933 T-schema as the technical foundation Davidson built on;
--     (8) adjacent (1) [linguistic_relativity] — the Sapir-Whorf
--     hypothesis as the philosophically loaded interface where
--     philosophy of language meets philosophy of mind and cognitive
--     science (whether linguistic structure shapes thought) and where
--     contemporary work (Lera Boroditsky, Eric Pederson) keeps the
--     question empirically alive.
--   * Edge structure: 31 edges total, all pedagogical_prerequisite, all
--     within-domain. Foundation spine flows philosophy_of_language →
--     {meaning, reference}, with meaning branching into the proposition,
--     the Fregean sense_and_reference distinction (also reached from
--     reference — both meaning and reference depend on the
--     sense/reference apparatus), the three meaning-theory branches
--     (use, verificationism, truth-conditional via proposition),
--     speech_act, indexical, and linguistic_relativity. Reference
--     branches into proper_name (forking to descriptivism vs.
--     causal_theory_of_reference, with the causal theory leading to
--     rigid_designator and forming the cross-cluster bridge into
--     semantic_externalism), definite_description (into Russell''s
--     1905 theory), and semantic_externalism directly. Externalism
--     forks into twin_earth and narrow_content. The proposition leads
--     to truth_conditional_semantics and to deflationary_theory_of_
--     truth, with truth_conditional_semantics leading to
--     compositionality_semantic, character_and_content (Kaplan''s
--     framework presupposes the truth-conditional skeleton), and
--     tarskis_t_schema (Davidson''s program builds on Tarski). The
--     deflationary branch also leads to tarskis_t_schema (Tarski is
--     the technical foundation deflationists most often appeal to).
--     Indexical leads to character_and_content (Kaplan''s direct
--     elaboration). Speech_act forks into performative_utterance,
--     gricean_maxims (with conversational_implicature as the central
--     downstream phenomenon), and presupposition. Three cross-cluster
--     bridges: causal_theory_of_reference → semantic_externalism
--     (Putnam''s externalism developed directly from the causal-theoretic
--     framework); truth_conditional_semantics → tarskis_t_schema
--     (Davidson''s program is explicitly Tarskian); truth_conditional_
--     semantics → character_and_content (Kaplan''s two-dimensional
--     theory generalizes the truth-conditional framework to handle
--     indexicals).
-- Rollback: BEGIN; DELETE FROM public.edges WHERE graph_version_added
--   = 13; DELETE FROM public.nodes WHERE id IN (the 28 ids inserted
--   here); UPDATE public.settings SET value = ''12''::jsonb WHERE key =
--   ''graph_version''; COMMIT. The whole-migration BEGIN/COMMIT wrap
--   below means a single transaction failure rolls all 60 statements
--   atomically — manual rollback below applies to the post-commit
--   window only.
-- See also: engine/build_readiness/phase_5.md (gate report);
--   product/adr/0052-phase-5-philosophy-subdomain-decomposition.md;
--   engine/operations/seed-chunked-authoring.md (Layer 1 workflow);
--   engine/operations/migration-discipline.md (Layer 1 contract shape);
--   product/seed-graph/migrations/ROUTING.md (per-session narrative);
--   product/seed-graph/migrations/PREDICATE_MANIFEST.md (predicate
--   registry);
--   product/seed-graph/migrations/0046_seed_mind_part1.sql (P5-07b
--   philosophy-of-mind consciousness/specialized seed; pattern
--   reference for the most recent within-domain seeding);
--   product/seed-graph/migrations/0030_seed_metaphysics_part1.sql
--   (P5-02a metaphysics core; pattern reference);
--   engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md
--   (apply_migration.py wrapper used to apply this migration in
--   routine-mode);
--   product/docs/architecture.md (Node/Edge schema + Granularity
--   Principle).

BEGIN;

-- Increment graph_version per ROUTING.md "graph_version increment
-- contract". Read 12 at session boot (post-S-0070 state per ROUTING.md
-- narrative); write 13 here; every node/edge below carries
-- graph_version_added = 13.
UPDATE public.settings
  SET value = '13'::jsonb
  WHERE key = 'graph_version';

-- Nodes: 28 INSERTs covering the eight philosophy-of-language clusters.
INSERT INTO public.nodes (id, label, domain, summary, teaching_notes, aliases, confidence_level, provenance, graph_version_added) VALUES
  (
    'philosophy_of_language',
    'Philosophy of Language',
    ARRAY['language'],
    'The philosophical study of language as a representational and communicative phenomenon: how words and sentences come to have meaning, how speakers refer to things in the world with them, what propositions are, how speech acts perform actions in addition to conveying content, and how context shapes interpretation. The analytic tradition since Frege treats philosophy of language as a propaedeutic to other inquiries (since philosophical questions are often about how concepts are best understood, the structure of meaning is foundational), while the continental tradition treats language as constitutive of human existence (Heidegger, Gadamer).',
    'Frame the field for students by its central questions: (1) the meaning question — what is it for an expression to mean what it does? (2) the reference question — how do words latch onto things in the world? (3) the proposition question — what are the truth-evaluable contents that sentences express? (4) the use question — what do speakers do with language beyond stating things? (5) the context question — how does what an utterance means depend on who, when, and where? Each question has a canonical literature and a small number of canonical positions. The field is dominated by analytic philosophy of language because the questions are paradigmatically analytic — they invite formal-semantic, conceptual, and broadly Fregean analysis — but the continental tradition offers complementary framings that surface in pragmatist (Brandom) and ordinary-language (later Wittgenstein, Austin) work. For this seed, focus is on the analytic surface; cross-bridges to the continental tradition (where they reach hermeneutics, philosophical anthropology, and post-Heideggerian thought) are out of scope.',
    ARRAY['philosophy_language', 'phil_language'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'meaning',
    'Meaning (Linguistic)',
    ARRAY['language'],
    'The property in virtue of which a linguistic expression — a word, phrase, sentence, or utterance — represents, communicates, or is about something. The central explanandum of philosophy of language: any complete theory of language must say what meaning is, what determines it, what role it plays in communication, and how it relates to truth, reference, use, and context. Meaning is contested at every level — what it consists in, where it is located (head, community, the world), and whether the term picks out one phenomenon or several.',
    'Help students see that "what does X mean?" is several questions at once. Distinguish: (1) speaker meaning (what someone meant by saying it on this occasion — Grice''s notion); (2) sentence meaning (what the sentence means in the language, abstracted from any utterance); (3) word meaning (the conventional meaning of a lexical item); (4) referential meaning (what an expression picks out in the world); (5) sense or descriptive meaning (what one would have to know to use the expression correctly); (6) the broader pragmatic meaning that includes implicature, presupposition, and conventional force. Different theories of meaning prioritize different layers — truth-conditional semantics treats sentence-level truth conditions as central; use theories treat patterns of use; verificationism treats verification conditions. The disputes are not merely about which is the right "theory of meaning" but about which question philosophical theorizing is answering. For pedagogy, surface this layering early: a single question "what is meaning?" is a family of questions.',
    ARRAY['linguistic_meaning', 'semantic_meaning'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'reference',
    'Reference',
    ARRAY['language'],
    'The relation between linguistic expressions and the things in the world they pick out: between proper names and individuals, between predicates and properties or sets, between definite descriptions and the objects (if any) that uniquely satisfy them. Reference is the second central explanandum of philosophy of language alongside meaning. The dominant question post-Frege has been how reference is determined: by descriptive content the speaker associates with the term (descriptivism), by causal-historical chains running from initial baptisms to current uses (causal theory), or by some combination.',
    'Use Frege''s 1892 puzzle to motivate the topic: "Hesperus is Phosphorus" is informative, but if both names refer to Venus and meaning is just reference, both names mean the same thing and the identity should be trivial. Something more than reference must distinguish them — that something is sense (Sinn), the mode of presentation. Frege''s solution introduced the sense/reference distinction that organizes most subsequent discussion. The descriptivist tradition (early Russell, late Frege, Searle) treats names as abbreviated descriptions; the causal theory (Kripke 1972, Putnam, Donnellan) reverses this, treating reference as fixed by causal chains independent of any descriptions speakers happen to associate. The disputes here are not trivial — they have downstream consequences for the philosophy of natural kinds, the metaphysics of essential properties, and the philosophy of mind on the externalist view of content. Treat reference as the cluster where philosophical-of-language analyses bear most directly on metaphysics and epistemology.',
    ARRAY['linguistic_reference', 'reference_relation'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'sense_and_reference',
    'Sense and Reference (Sinn und Bedeutung)',
    ARRAY['language'],
    'Frege''s 1892 distinction between the sense (Sinn) of an expression and its reference (Bedeutung). The sense is the mode of presentation — the cognitive content one grasps when one understands the expression — while the reference is what the expression picks out in the world. Frege introduced the distinction to resolve the puzzle of cognitive significance: identity statements like "Hesperus is Phosphorus" can be informative even when both names refer to the same thing because the senses differ. The distinction organizes most subsequent reference theory.',
    'Make the puzzle vivid for students with Frege''s own example: an astronomer who already knows that Venus is sometimes the morning star (Phosphorus) learns that Venus is also the evening star (Hesperus). This is genuine information — knowledge that improves understanding of the heavens. But on a pure-reference theory of meaning, "Hesperus = Phosphorus" should mean the same as "Venus = Venus" — trivial. Frege diagnosed the puzzle: the names "Hesperus" and "Phosphorus" share a reference (Venus) but differ in sense (the modes of presentation "the brightest celestial object visible at dusk" vs. "the brightest celestial object visible at dawn"). Once the sense/reference apparatus is in place, related puzzles fall into line: why substitution of co-referring expressions in propositional-attitude contexts can change truth-value (Lois Lane believes Superman is brave but does not believe Clark Kent is brave); why empty names like "Pegasus" still seem meaningful despite lacking reference. The distinction is the foundational technical move philosophy-of-language students need to internalize before tackling any post-Fregean theory.',
    ARRAY['fregean_sense', 'sinn_und_bedeutung', 'frege_sense_reference'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'proposition',
    'Proposition',
    ARRAY['language'],
    'The truth-evaluable content expressed by a declarative sentence: what is asserted when one asserts, believed when one believes, doubted when one doubts. Propositions are the typical relata of propositional attitudes (belief that p, hope that p) and the typical bearers of truth-value. What propositions are metaphysically — sets of possible worlds, structured complexes of constituents, Fregean thoughts, or something else — is contested; that there are propositions in some sense is broadly accepted in analytic philosophy of language as a working posit.',
    'Distinguish propositions from sentences and utterances: the same proposition can be expressed by different sentences ("It is raining" / "Es regnet" / "Il pleut"), and the same sentence can express different propositions on different occasions (an indexical-bearing sentence like "I am hungry" expresses different propositions when uttered by different speakers). The proposition is the abstract content that is the same across these. Three main metaphysical accounts: (1) Russellian structured propositions (sequences of objects, properties, and relations — the proposition that Mary loves John has Mary, John, and the loving-relation as constituents); (2) Fregean structured propositions (sequences of senses rather than referents); (3) sets-of-possible-worlds accounts (the proposition that p is the set of worlds at which p is true — Stalnaker, Lewis). Each has costs: Russellian propositions have trouble with empty-name and indexical cases; Fregean propositions multiply senses; sets-of-worlds propositions identify all necessary truths (since they are true at all worlds), which is implausible for mathematics and metaphysics.',
    ARRAY['proposition_content', 'truth_evaluable_content'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'proper_name',
    'Proper Name',
    ARRAY['language'],
    'A linguistic expression that refers to a particular individual: "Aristotle", "Venus", "Mount Everest". The locus of the central reference debate in twentieth-century philosophy of language: whether proper names refer via descriptions associated with them (descriptivism) or via causal-historical chains independent of any descriptive content (the causal theory of reference). Kripke''s 1972 Naming and Necessity is the central inflection point; the contemporary literature is largely post-Kripkean.',
    'Set up the dispute for students with the question: how does the name "Aristotle" pick out Aristotle? Descriptivism (early Russell, late Frege, Searle): "Aristotle" abbreviates a description like "the teacher of Alexander the Great who wrote the Metaphysics" — to use the name is to deploy the description, and the name refers to whoever uniquely satisfies it. The causal theory (Kripke, Putnam, Donnellan): "Aristotle" was bequeathed to its bearer by an initial baptism (his parents naming him), and subsequent uses inherit reference by causal chains running back to that baptism — speakers need not know any individuating descriptions. Kripke''s arguments against descriptivism work on three fronts: the modal argument (if "Aristotle" abbreviated "the teacher of Alexander", "Aristotle taught Alexander" would be necessary, but it is contingent — Aristotle might have not been a teacher); the epistemic argument (we know who Aristotle is even when our descriptions are wrong); the semantic argument (a community can refer to Aristotle through a name they associate with no individuating description, by deference to other speakers). The causal theory has become the dominant view but has its own difficulties (the qua-problem: which thing in the baptism-chain is being referred to?).',
    ARRAY['proper_names', 'name_proper'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'descriptivism',
    'Descriptivism (Theory of Reference)',
    ARRAY['language'],
    'The view that proper names refer to whatever uniquely satisfies a description (or cluster of descriptions) the speaker or community associates with the name. Held in different forms by early Russell ("Aristotle" abbreviates "the teacher of Alexander..."), late Frege (the sense of a proper name is a description), and Searle (a cluster of descriptions, weighted, with reference going to whatever satisfies enough of them). Largely supplanted by the causal theory of reference after Kripke 1972 but still defended in modified forms (descriptive metalinguistic theories; rigidified-description views).',
    'Help students see why descriptivism was attractive before Kripke: it explains how a speaker who does not know much about Aristotle can still refer to him (by knowing some descriptions), explains the cognitive significance of identity statements (sense/reference machinery transposed onto names), explains how empty names like "Vulcan" can be meaningful (an empty description), and explains how reference can shift if the original individual turns out to fail key descriptions (the man we have been calling Aristotle was actually two people — descriptivism predicts the name partially fails to refer). Kripke''s arguments turn each of these features against the theory: the modal argument shows descriptions are too rigid (descriptions vary across worlds — the description-satisfier varies — but names don''t); the epistemic argument shows speakers can refer without descriptions; the qua-historical-deference cases show the social structure of naming is too rich for individual descriptions to capture. The contemporary defense of descriptivism (Jackson, Lewis, Stanley) treats descriptions as semantic but not as what speakers need to know — a more sophisticated descriptivism that absorbs Kripkean lessons.',
    ARRAY['descriptive_theory_reference', 'description_theory_names'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'causal_theory_of_reference',
    'Causal Theory of Reference',
    ARRAY['language'],
    'The view that proper names (and natural-kind terms) refer to their bearers via causal-historical chains: an initial baptism (or dubbing) establishes the reference, and subsequent uses inherit reference by causal chains running back to that baptism. Developed by Kripke (1972, Naming and Necessity), Putnam (1975, "The Meaning of `Meaning''"), and Donnellan (1970), the causal theory replaced descriptivism as the dominant view of how proper names refer, with extensions to natural-kind terms (Putnam) and theoretical terms.',
    'Walk students through Kripke''s setup: imagine a child being named Aristotle by his parents — that is the initial baptism. Subsequent speakers learn the name from those who learned it from those who learned it... back to the baptism. To use the name is to inherit reference along that chain. No description need be in the speaker''s head — a speaker who knows almost nothing about Aristotle still refers to him through the chain. The causal theory explains Kripkean cases descriptivism struggles with: the "semantic" case (a community refers to Gödel even after they all believe descriptions that turn out to be about Schmidt — they still refer to Gödel via the chain); the "modal" case (Aristotle would be Aristotle even if he had been a fisherman with no philosophical interests — the name picks out him, not whoever happens to satisfy descriptions). The theory has been extended: Putnam''s account of natural-kind terms ("water" refers to H2O via causal chains running through scientific investigations of the substance — even speakers who cannot distinguish water from XYZ refer to water on Earth); Donnellan''s referential/attributive distinction for definite descriptions adds a parallel story for descriptions used referentially. Difficulties: the qua-problem (in the baptism, we point at a thing — but which thing is being baptized? An individual? A species? A stage?); cases where chains break or fork.',
    ARRAY['causal_reference', 'historical_chain_reference', 'kripke_putnam_reference'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'rigid_designator',
    'Rigid Designator',
    ARRAY['language'],
    'Kripke''s technical term for an expression that designates the same object in every possible world in which that object exists. Proper names are rigid designators on Kripke''s analysis ("Aristotle" picks out the same person — Aristotle — in every world where he exists), while definite descriptions are typically non-rigid ("the teacher of Alexander" picks out different people in different worlds, depending on who teaches Alexander there). The rigid/non-rigid distinction is the technical core of Kripke''s argument against descriptivism and a central tool of contemporary modal semantics.',
    'Make rigidity vivid with the modal argument against descriptivism. If "Aristotle" abbreviated "the teacher of Alexander", then "Aristotle taught Alexander" should be a necessary truth — it would just say "the teacher of Alexander taught Alexander". But the sentence is intuitively contingent: Aristotle might not have taught Alexander; the world in which he had a different career is a world in which he is still Aristotle. The diagnosis: "Aristotle" rigidly designates Aristotle (the man), while "the teacher of Alexander" non-rigidly designates whoever teaches Alexander in the world being evaluated. Identity statements between rigid designators ("Hesperus is Phosphorus", "water is H2O") are necessary if true — there is no world in which Hesperus is anything other than Phosphorus, since both rigidly designate Venus. This cuts apart the necessary/a priori distinction (Hesperus = Phosphorus is necessary but a posteriori) and is the technical machinery behind Kripkean essentialism: if "water is H2O" is necessary, water has its molecular composition essentially. Rigid designators are the bridge from philosophy of language to metaphysics of natural kinds (P5-02b territory) and to the modal logic of essential properties.',
    ARRAY['rigid_designation', 'kripke_rigid_designator'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'definite_description',
    'Definite Description',
    ARRAY['language'],
    'A noun phrase of the form "the F" that purports to designate a unique satisfier of the property F: "the king of France", "the tallest mountain", "the author of Waverley". Definite descriptions are the parade case for Russell''s 1905 theory of descriptions and a continuing focus of philosophy of language because they raise puzzles about empty reference, scope, and the referential/attributive distinction. The contrast with proper names (which are rigid) and indefinite descriptions ("a king of France") helps locate them in the wider semantic landscape.',
    'Walk students through the puzzle Russell aimed to solve: "The king of France is bald" — there is no king of France, but the sentence does not seem meaningless. On the naive view that "the king of France" refers, the sentence has no truth-value (it is neither true nor false), violating the law of excluded middle. Russell''s 1905 paraphrase: "The king of France is bald" means "there is one and only one thing that is king of France, and that thing is bald" — a quantified statement that is straightforwardly false (because there is no king of France). The empty-reference puzzle dissolves: there is no problem with reference, because on Russell''s analysis "the king of France" is not a referring expression at all. Strawson''s 1950 reply ("On Referring") objects: ordinary speakers do not feel that "the king of France is bald" is straightforwardly false; rather, the question of its truth-value does not arise because the presupposition of unique reference fails. This presuppositional account has subsequent influence (Stalnaker''s common-ground theory). Donnellan''s 1966 "referential vs. attributive" distinction adds a third option: a speaker can use "the king of France" to refer to a particular person (the man at the table, mistakenly thought to be king) or attributively (whoever uniquely satisfies "king of France").',
    ARRAY['definite_descriptions', 'description_definite'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'russells_theory_of_descriptions',
    'Russell''s Theory of Descriptions',
    ARRAY['language'],
    'Bertrand Russell''s 1905 ("On Denoting") logical analysis of definite descriptions as quantified expressions rather than referring expressions. "The F is G" is paraphrased as: there is one and only one thing that is F, and that thing is G. The theory dissolves Meinongian puzzles about non-existent objects (since "the king of France is bald" no longer requires a referent for "the king of France"), handles empty descriptions cleanly, and was Russell''s paradigm of "logical analysis" — replacing apparent grammatical structure with underlying logical structure.',
    'Pedagogically, the theory of descriptions is a textbook case of philosophical logical analysis. Russell''s motivation was multiple: (1) to dissolve Meinong''s puzzle about non-existent objects (Meinong held that "the round square does not exist" requires a non-existent object to refer to, generating a populated realm of non-existents); (2) to avoid violations of the law of excluded middle for sentences with empty descriptions ("the king of France is bald" should be either true or false, but neither seems right on the naive view); (3) to explain the substitution-failure puzzle (in "George IV wished to know whether Scott was the author of Waverley", you cannot substitute "Scott" for "the author of Waverley" without absurdity). Russell''s paraphrase handles each case by showing that descriptions interact with other operators (negation, modal operators, propositional-attitude verbs) at different scopes. The wide-scope/narrow-scope distinction Russell introduced is now standard in formal semantics. The theory remains influential — a central tool of philosophical logical analysis — even where contemporary philosophers diverge from Russell on details (e.g., dynamic-semantics treatments of definites; presuppositional accounts in the Strawson-Stalnaker line).',
    ARRAY['russell_descriptions', 'theory_of_descriptions'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'truth_conditional_semantics',
    'Truth-Conditional Semantics',
    ARRAY['language'],
    'The program in semantics, originating with Frege and developed systematically by Donald Davidson (especially "Truth and Meaning", 1967), of identifying the meaning of a sentence with its truth conditions: to know the meaning of a sentence is to know what the world would have to be like for the sentence to be true. Davidson''s specific proposal applies Tarski''s 1933 T-schema (snow is white iff snow is white) recursively to natural-language sentences, treating a Tarskian truth theory for a language as a theory of meaning for that language.',
    'Help students see why truth-conditional semantics has been so dominant in formal semantics. The strategy: take any declarative sentence "S"; identify the conditions under which S is true; that is what S means. The strategy is recursive — the truth conditions of complex sentences are computed from the truth conditions of their parts plus the contributions of logical connectives, quantifiers, modal operators, etc. Davidson''s 1967 insight: Tarski''s mathematical apparatus for defining truth in formal languages can be repurposed as a semantic theory for natural language. A Tarskian theory of truth for English (a recursive specification of the truth conditions of every English sentence in terms of its parts) gives a compositional theory of meaning. The program has prospered: contemporary formal semantics (Heim, Kratzer, Kaplan-style two-dimensional theories) lives within the truth-conditional tradition. Limits: the theory works best for declarative sentences and has trouble with non-truth-evaluable utterances (questions, commands, performatives — though extensions to dynamic semantics aim to cover these); use theorists object that knowing truth conditions is not enough for understanding (the manual translation case of Quine''s "Two Dogmas"); presupposition and conventional implicature do not fit neatly into a truth-conditional framework. Despite these limits, truth-conditional semantics remains the standard framework — the program is incomplete rather than rejected.',
    ARRAY['davidsonian_semantics', 'truth_conditional_meaning'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'use_theory_of_meaning',
    'Use Theory of Meaning',
    ARRAY['language'],
    'The view, associated paradigmatically with the later Wittgenstein (Philosophical Investigations §43: "the meaning of a word is its use in the language"), that the meaning of a linguistic expression is determined by the patterns of its use in the linguistic community: how it is taught, how it is corrected, what one says with it, what counts as a proper or improper deployment. Contrasts with truth-conditional, verificationist, and reference-theoretic accounts that locate meaning in conditions or relations external to use.',
    'Make the contrast vivid for students. Consider the word "thanks." On a truth-conditional account, "thanks" is hard to fit — it does not have truth conditions; it is not used to state things. On a referential account, what does "thanks" refer to? On Wittgenstein''s use account, the meaning of "thanks" is its role in a complex social practice: one says it when receiving help, the typical response is "you''re welcome", failure to say it is rude, sarcastic uses are recognizable as sarcasm because they violate the conventional pattern, etc. The meaning is the pattern of use itself, not anything beyond it. The use theory dissolves several puzzles that plague representational theories: the meaning of expressives (interjections, ethical terms on expressivist construals, attitude markers); the meaning of social-coordination expressions; the meaning of expressions whose role is performative rather than descriptive. Inferentialism (Brandom''s contemporary heir to the use tradition) makes the program more precise: the meaning of an expression is its inferential role — what one is committed to by using it, what entitles one to use it, what one denies by denying it. The use tradition has been most successful as a framework for thinking about non-fact-stating uses of language and as a corrective against treating every linguistic expression as a description in disguise.',
    ARRAY['wittgenstein_use_theory', 'meaning_as_use'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'verificationism',
    'Verificationism',
    ARRAY['language'],
    'The logical-positivist view that the meaning of a (non-analytic) sentence is its method of empirical verification: to know what a sentence means is to know what observations would confirm it. Associated with the Vienna Circle (Schlick, Carnap, Ayer) and crystallized in the verification principle: a sentence is meaningful iff it is either analytically true (a tautology) or empirically verifiable. The view aimed to demarcate science from metaphysics by ruling unverifiable metaphysical claims meaningless. Largely abandoned after Quine''s "Two Dogmas of Empiricism" (1951) and the recognition that the verification principle is itself unverifiable.',
    'Verificationism is best understood as a programmatic attempt to make philosophy more like science by tying meaning to empirical content. The slogan: a difference that makes no observable difference is no difference at all. Apparent metaphysical claims that no observation could confirm or refute (the world began five minutes ago with all evidence in place; there is a substance underlying the appearances) are, on the verificationist view, not false but meaningless. The view''s appeal was real: it offered a sharp criterion for cognitive significance that vindicated empirical science and dismissed traditional metaphysics. Multiple problems sank it: (1) the verification principle does not verify itself; (2) Quine''s "Two Dogmas" undermined the analytic/synthetic distinction the principle relied on; (3) holism — observation does not bear on individual sentences but on the theoretical web (Duhem-Quine); (4) successful theoretical sentences (about quarks, electrons, distant galaxies) are not directly verifiable but are clearly meaningful and clearly central to science. Successor views: Carnap''s shift toward confirmation theory; the "verificationism is dead, long live verificationism" of contemporary anti-realist semantics (Dummett); Putnam''s pragmatic realism. The historical importance is enormous; the contemporary defense is rare.',
    ARRAY['verification_principle', 'logical_positivist_verificationism'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'compositionality_semantic',
    'Compositionality (Semantic)',
    ARRAY['language'],
    'The principle that the meaning of a complex expression is determined by the meanings of its parts plus the way they are combined. Often called Frege''s context principle in the converse direction (Frege''s slogan was that words have meaning only in the context of a sentence). Compositionality is a central structural constraint on theories of meaning: any account that makes meaning unsystematic, or that fails to derive the meaning of complex expressions from the meanings of their parts, faces the productivity argument (we understand novel sentences whose meanings we have never been told — only systematic composition explains this).',
    'Frame the compositionality principle for students as the answer to a foundational question: how is it that we can understand sentences we have never encountered before? "The blue elephant who graduated from Yale ate my taxes" is novel but immediately understood — we did not learn it from anyone. Compositional explanation: we learned the words individually, learned the syntactic rules of combination, and the meaning of the novel sentence is computed from these. Without compositionality, a language with finite vocabulary and finite syntactic rules could not produce the unbounded productive understanding that is characteristic of natural language. The principle has formal force in contemporary semantics: every well-developed semantic theory has a compositionality result — a recursive specification of how the meaning of a complex expression depends on the meanings of its parts. Apparent counterexamples (idioms like "kick the bucket"; opaque-context substitution failures; metaphors) are typically handled by treating idioms as lexical units, distinguishing referential and ungerade-sense modes, and treating metaphor as a pragmatic phenomenon. The principle sets a high bar: any theory of meaning that fails compositionality has explanatory work to do.',
    ARRAY['compositionality_principle', 'frege_compositionality'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'speech_act',
    'Speech Act',
    ARRAY['language'],
    'A linguistic act performed in uttering a sentence: stating, asking, promising, ordering, apologizing, naming, baptizing, marrying. The notion was developed by J. L. Austin (How to Do Things with Words, 1962, the William James lectures of 1955) and systematized by John Searle (Speech Acts, 1969). Austin distinguished three aspects of any utterance: locutionary (the act of saying something with a certain meaning), illocutionary (the act performed in saying it — promising, asserting), and perlocutionary (the effect produced — convincing, frightening). The illocutionary act is the central object of speech-act theory.',
    'Help students see the philosophical move Austin made. The picture before Austin: language is fundamentally for stating things — declarative sentences expressing propositions that are true or false. Austin''s 1955 lectures challenged this in three steps. First, he identified performative utterances ("I promise...", "I name this ship...", "I bequeath...") that do not state things and are not true or false but rather perform actions in being uttered. Second, he showed the distinction between performatives and constatives breaks down: even constatives ("It is raining") are themselves a kind of speech act — namely, asserting. Third, he generalized: every utterance has an illocutionary force (asserting, asking, promising, ordering, etc.) on top of its propositional content. Searle''s formalization: an illocutionary act consists of a force F applied to a content P; F(P) where F is the force (promising, asserting, etc.) and P is the propositional content. The classification of forces: assertives (asserting), directives (commanding), commissives (promising), expressives (apologizing), declarations (baptizing). Speech-act theory has had wide influence: in pragmatics (Grice''s implicature theory builds on it), in legal philosophy (the speech-act structure of legal pronouncements), in feminist philosophy (the speech-act analysis of pornography and silencing — Langton, MacKinnon).',
    ARRAY['speech_acts', 'illocutionary_act', 'austin_speech_act'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'performative_utterance',
    'Performative Utterance',
    ARRAY['language'],
    'A class of utterances Austin identified that do not state facts but perform actions: "I promise to be there" is not a description of an inner mental act of promising — uttering it (under appropriate conditions) constitutes the promising. Other paradigm cases: "I now pronounce you husband and wife", "I name this ship the Queen Elizabeth", "I bet you ten dollars". Austin''s 1955 lectures took these as the seed for a general theory of speech acts after the constative/performative distinction was found to be unstable.',
    'Walk students through the felicity conditions Austin identified for performatives — the conditions a performative must satisfy to come off rather than misfire. To "I promise to be there" succeed in promising, several things must obtain: the speaker must have the appropriate authority/standing (the speaker can promise their own actions, not someone else''s); the conventions must be right (saying it as a joke, on stage, or in quotation does not count); the speaker must intend to be bound; the audience must take it up appropriately. When these conditions fail, the performative misfires (Austin''s technical term) — it is not false, but rather null, void, infelicitous, hollow, etc. Performatives split into three categories Austin proposed: explicit performatives ("I hereby promise..." with the performative verb in first-person present tense — the canonical form); primary performatives (informal versions: "I''ll be there" said in a promising context — the promising force is implicit); and the broader category once Austin generalized to speech acts (every utterance has illocutionary force, so the constative/performative distinction collapses into the more general locutionary/illocutionary/perlocutionary distinction). Pedagogically, performatives are the easiest entry to speech-act theory because the action-performing nature of the utterance is overt.',
    ARRAY['performatives', 'performative_speech_act'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'gricean_maxims',
    'Gricean Maxims (Cooperative Principle)',
    ARRAY['language'],
    'Paul Grice''s 1975 ("Logic and Conversation") set of conversational norms speakers and hearers tacitly observe to make conversation efficient and rational. The cooperative principle: make your contribution such as is required, at the stage at which it occurs, by the accepted purpose or direction of the talk exchange. Four maxim categories: Quantity (be informative — but not over-informative), Quality (be truthful), Relation (be relevant), Manner (be clear, brief, orderly). Speakers can flout the maxims while still being cooperative — flouting generates conversational implicatures.',
    'Grice''s framework illuminates the gap between what sentences literally mean and what speakers are usually understood to communicate. Consider: A says "Smith does not have a girlfriend these days." B replies "He has been visiting New York a lot lately." B''s utterance literally just reports Smith''s travel; but A correctly infers from B''s remark that Smith may have a romantic interest in New York. How? On the assumption that B is being cooperative — that B''s reply is relevant to A''s claim — A can infer that B''s mention of New York must somehow bear on the girlfriend question. The mechanism is implicature: B has not said Smith has a girlfriend in New York, but has implicated it. Grice''s maxims are the structural assumptions hearers make about cooperative conversation: speakers are presumed to obey them by default, and apparent violations either constitute hedged violations (tactfulness, politeness), unobtrusive violations (white lies), or are flouts that signal a conversational implicature. The framework is the foundation of contemporary linguistic pragmatics. Pedagogically, contrast Grice with strict-content theories: the cooperative-principle structure says rational conversation depends on assumptions speakers make about each other''s cooperation, not on encoded conventions of meaning alone.',
    ARRAY['grice_maxims', 'cooperative_principle', 'conversational_maxims'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'conversational_implicature',
    'Conversational Implicature',
    ARRAY['language'],
    'Paul Grice''s technical term for what is communicated by an utterance but not strictly said by it: a hearer derives the implicature from the literal content plus assumptions about cooperation (the Gricean maxims) plus contextual information. "Some students passed" implicates that not all did (Quantity); "Where can I get gas?" "There''s a station around the corner" implicates the station is open and selling gas (Relation). Implicatures are calculable, cancelable, non-detachable, and non-conventional — distinguishing them from semantic content and from conventional implicature.',
    'Help students apply Grice''s tests for distinguishing implicature from said-content. Cancelability: an implicature can be cancelled with appropriate further content ("Some students passed — in fact, all of them did" — the implicature that not-all-did is cancelled without contradiction). Calculability: the hearer can reconstruct why the implicature holds by reasoning from the said content plus cooperative assumptions. Non-detachability: the implicature attaches to the proposition expressed, not to the specific words used (a paraphrase generally generates the same implicature). Non-conventionality: the implicature is not part of the conventional meaning of the words but is a derived consequence of using those words in a cooperative context. Use these tests with the canonical examples: scalar implicatures ("some" implicating "not all"); relevance-based ("the station is open" from the gas-directions example); manner-based ("she produced a sequence of sounds corresponding to the score" implicating she did not really sing well — a more roundabout description suggests something amiss). The framework explains a vast amount of linguistic communication that strict content-only theories cannot: politeness phenomena, indirect requests, irony, hedging. Limits: the calculation procedure for deriving implicatures is not fully formalized; some implicatures (especially scalar ones) are conventionalized to a degree that strains Grice''s purity claim.',
    ARRAY['gricean_implicature', 'implicature_conversational'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'presupposition',
    'Presupposition',
    ARRAY['language'],
    'Information that an utterance takes for granted rather than asserts. "The king of France is bald" presupposes there is a king of France; "John stopped smoking" presupposes John used to smoke; "It was Mary who broke the window" presupposes someone broke the window. Presupposition is distinguished from assertion by behavior under negation: a sentence and its negation typically share their presuppositions ("John did not stop smoking" still presupposes John used to smoke). Strawson 1950 ("On Referring") gave a presuppositional alternative to Russell''s theory of descriptions; Stalnaker formalized presupposition as common-ground content speakers treat as already accepted.',
    'Help students see what presupposition contributes that assertion does not. The classic Strawson move against Russell: when someone says "the king of France is bald" today, they are not asserting that there is a king of France (so as to be straightforwardly false); they are presupposing it, and the presupposition failure means the question of bald-vs-not-bald does not arise — the sentence is not assertable rather than false. The behavior under embedding is the technical signature: presuppositions project through negation, questions, and modal operators ("Does John know it is raining?" still presupposes it is raining; "Maybe John stopped smoking" still presupposes he used to smoke), while truth-conditional content does not. Stalnaker''s common-ground formalization: presuppositions are propositions speakers treat as part of the conversational common ground — already accepted by all conversationally relevant parties. An assertion''s job is to add to the common ground; a presupposition''s job is to be in the common ground already (or to be accommodated by the hearer when the speaker proceeds as if it were). The taxonomy of presupposition triggers (definite descriptions, factive verbs, change-of-state verbs, cleft constructions, focus-sensitive operators) is a core topic in formal pragmatics. Presupposition failure is also pedagogically rich: how do speakers and hearers manage failed presuppositions? Repair strategies, accommodation, common-ground revision.',
    ARRAY['linguistic_presupposition', 'pragmatic_presupposition'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'semantic_externalism',
    'Semantic Externalism',
    ARRAY['language'],
    'The thesis that the contents of (some) thoughts and meanings of (some) words depend on factors outside the head of the thinker or speaker — typically features of the physical, social, or causal-historical environment. Putnam''s 1975 ("The Meaning of `Meaning''") slogan: "meaning ain''t in the head". Burge''s 1979 ("Individualism and the Mental") argued for social externalism: a community''s usage partly fixes what the individual''s words and thoughts mean. Externalism has profound consequences for the philosophy of mind (content externalism), epistemology (asymmetry of self-knowledge), and metaphysics (Kripkean essentialism follows naturally).',
    'Walk students through Putnam''s Twin Earth thought experiment as the canonical externalist illustration: imagine a planet (Twin Earth) just like Earth except the substance there called "water" is XYZ (chemically distinct from H2O) but indistinguishable to ordinary speakers. An Earth-Oscar and Twin-Earth-Oscar are intrinsically identical (same brain states, same dispositions, same history of causal interactions with their respective environments). Question: when each says "water", do they mean the same thing? Putnam: no — Earth-Oscar refers to H2O via causal-historical chains running back to Earth''s actual liquid; Twin-Oscar refers to XYZ. They mean different things by "water" despite being intrinsically identical. So meaning is not a function of internal states alone. The externalist view extends: natural-kind terms generally have externally-determined extensions; social externalism (Burge''s arthritis case: someone who incorrectly believes that "arthritis" can apply to thigh ailments still means what their community means by it, partly fixed by expert deference); content externalism in philosophy of mind (the contents of beliefs depend on environmental factors). Implications students should see: anti-individualism about the mental; first-person authority puzzles (how can I know what I am thinking if its content is partly external?); the bridge to Kripkean essentialism (if "water" rigidly designates H2O, water is essentially H2O).',
    ARRAY['content_externalism', 'putnam_externalism', 'externalism_meaning'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'twin_earth',
    'Twin Earth',
    ARRAY['language'],
    'Hilary Putnam''s 1975 thought experiment central to the case for semantic externalism. Imagine a planet just like Earth (Twin Earth) except that the colorless, odorless, tasteless liquid the inhabitants call "water" has the chemical composition XYZ rather than H2O. The substance is indistinguishable to ordinary speakers. The thought experiment: what do Earth-speakers and Twin-Earth-speakers each refer to when they say "water"? Putnam''s answer: each refers to the local liquid (Earth-speakers to H2O, Twin-speakers to XYZ), even though they are intrinsically identical. The conclusion: meaning is partly determined by external environment, not just internal mental states.',
    'Twin Earth is the canonical externalist setup for a reason — it isolates the philosophical question with surgical precision. Imagine identical twins — Oscar on Earth and Twin-Oscar on Twin Earth — both pre-1750 (before any chemical analysis of water existed). They are intrinsically identical: same neurons firing in the same patterns, same history of touching/drinking/swimming-in the local liquid, same dispositions to use the word "water" the same way. They differ only in the world they inhabit. Question: do they mean the same by "water"? The externalist intuition: no — Oscar refers to H2O (which is the local liquid) and Twin-Oscar refers to XYZ. The reference is partly fixed by the environment, not by their intrinsic mental states. Internalist replies: they mean the same — what differs is just what their meaning extends to in the actual world; or they each mean a more general property like "watery stuff". The dialectic has been intricate, but Twin Earth has remained the touchstone scenario for the externalist thesis. Variants: arthritis (Burge''s social externalism — someone who applies "arthritis" to thigh ailments still means what their community means); Kripke''s "Aristotle" cases for proper names. Twin Earth''s pedagogical strength is its concreteness: the philosophical thesis follows directly from a vivid scenario rather than from technical machinery.',
    ARRAY['putnam_twin_earth', 'twin_earth_thought_experiment'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'narrow_content',
    'Narrow Content',
    ARRAY['language'],
    'A notion of mental or linguistic content that depends only on the intrinsic properties of the thinker or speaker — what would be shared between intrinsic duplicates regardless of their external environments. The internalist counterpoint to externalist wide content: where wide content varies across Putnam''s Twin Earth pair (Earth-Oscar means H2O; Twin-Oscar means XYZ), narrow content is invariant. Defended in different forms by Fodor (early), Loar, and others as a notion of content useful for psychological explanation; criticized by externalists as either trivial (logic-of-discrimination only) or impossible to specify.',
    'Help students see the appeal and the difficulty of narrow content. The appeal: psychological explanation seems to need a content notion that supervenes on the thinker''s intrinsic states. If two intrinsic duplicates would behave identically in identical situations, their psychological states ought to count as having the same content for explanatory purposes. Wide content (which varies between the duplicates) cannot fill this role; narrow content can. The Fodor-Loar program in the 1980s aimed to specify narrow content — the contribution to content that supervenes on the head — alongside wide content for full theoretical accounts. Difficulties: the notion is hard to specify in a non-question-begging way. If narrow content is just the function from external environment to wide content, it is a relational property after all. If narrow content is what is in common between the Twin Earth duplicates, that may turn out to be very thin — perhaps just dispositional patterns of inferential behavior. Externalist replies: psychological explanation may not need narrow content; the wide content is enough together with information about the environment. The contemporary disposition: narrow content is a contested notion that has lost ground but still plays a role in certain psychological-explanation programs (e.g., conceptual role semantics; some functionalist accounts).',
    ARRAY['internalist_content', 'narrow_psychological_content'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'indexical',
    'Indexical Expression',
    ARRAY['language'],
    'A linguistic expression whose reference shifts systematically with context: "I" refers to the speaker, "you" to the addressee, "here" to the place of utterance, "now" to the time of utterance, "this" / "that" / "today" / "yesterday" to context-dependent items. Indexicals (also called deictic expressions) are pervasive in natural language and pose central challenges to truth-conditional semantics: the same indexical-bearing sentence expresses different propositions in different contexts, requiring a layered semantic theory to handle the context-sensitivity systematically.',
    'Walk students through the puzzle indexicals raise. "I am hungry" is true when uttered by a hungry speaker, false when uttered by a sated one. The same sentence, different propositions expressed depending on who utters it. A truth-conditional theory cannot treat sentences as straightforwardly mapped to propositions — context intervenes. Kaplan''s 1989 "Demonstratives" gave the standard solution: distinguish two layers of meaning, character (the linguistic rule that maps contexts to propositional contents — "I" has the character "the speaker of the context") and content (the proposition expressed in a given context). Character is fixed by the language, invariant across contexts; content varies with context but is a definite proposition once a context is supplied. The two-dimensional structure handles both: the same indexical-bearing sentence has constant character and varying content. Indexicals are a category — pure indexicals (I, here, now) whose referent is fixed by context purely; demonstratives (this, that) which require an accompanying demonstration; tense markers; aspectual indexicals. The philosophy-of-mind side: indexicals are central to the "essential indexical" puzzle (Perry 1979, Castañeda) — beliefs expressed with "I" cannot be replaced by their third-person counterparts without explanatory loss; this is the de se attitude problem and bridges to philosophy of mind (P5-07a personal identity territory).',
    ARRAY['deictic_expression', 'indexical_term'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'character_and_content',
    'Character and Content (Two-Dimensional Semantics)',
    ARRAY['language'],
    'David Kaplan''s 1989 ("Demonstratives") two-dimensional framework for handling indexical and demonstrative expressions. Character: the linguistic rule that determines, for any context, what content (propositional content) the expression contributes. Content: the proposition expressed once a context is fixed. "I" has a constant character (the speaker of the context) and contents that vary across contexts (each utterance contributes the speaker as content). The two-dimensional structure became the standard treatment of indexicals in formal semantics and inspired further two-dimensional applications in modal and epistemic semantics.',
    'Walk students through Kaplan''s setup: a sentence''s meaning is computed in two stages. Stage 1: the language fixes the character of every indexical — a function from contexts to contents. "I" has the character: for any context c, the content of "I" in c is the speaker of c. Stage 2: a context is supplied (a particular utterance situation: speaker, addressee, place, time, etc.), and the character is applied to that context to yield the content (a definite proposition). Kaplan''s formal apparatus: for a sentence S in context c, [[S]]^c is the proposition expressed; this proposition then has a truth-value at a circumstance of evaluation (a possible world, a time). Two key formal results: (1) indexicals are directly referential — once content is fixed, the indexical contributes its referent to the proposition (not a description); (2) the framework predicts the rigidity of indexicals correctly (in the modal evaluation, "I" still picks out the actual speaker, not whoever happens to be speaking in the world being considered). Two-dimensional semantics has had broader impact: extension to natural-kind terms (Chalmers, Jackson on the bridge to apriori-vs-aposteriori), to epistemic content, to varieties of conceivability — but the canonical use is for indexical and demonstrative expressions. Pedagogically, present Kaplan''s framework as the answer to: how do truth-conditional semantics and indexicality coexist?',
    ARRAY['kaplan_two_dimensional', 'character_content_kaplan'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'deflationary_theory_of_truth',
    'Deflationary Theory of Truth',
    ARRAY['language'],
    'A family of views that hold the predicate "is true" has no substantive philosophical analysis: it is a logical or quasi-logical device, not a name for a metaphysically loaded property. Deflationism stands against substantive theories (correspondence, coherence, pragmatist) that aim to analyze truth as a real relation between sentences and the world (or sentences and other sentences, or sentences and their utility). Versions: the redundancy theory (Ramsey, early); the disquotational theory (Quine); the prosentential theory (Grover, Camp, Belnap); minimalism (Horwich). All share the thought that "S is true" is, philosophically, no more than what S already says.',
    'Help students see the deflationist''s minimalist move. Consider Ramsey''s 1927 observation: "It is true that snow is white" says no more than "snow is white". The truth predicate seems to add a redundant layer. Quine''s 1970 disquotational story makes this precise: "S is true" iff S, where S is any declarative sentence. The truth predicate is a useful generalization device — it lets us say things like "everything Aristotle said about logic is true" (which would otherwise require an infinite conjunction) and "if what John said is true, then we should believe it" (which lets us hypothesize about truth without specifying which sentence). But the predicate has no substantive philosophical content beyond this generalizing role. Horwich''s minimalism (1990, 1998) is the most-developed contemporary version: the meaning of the truth predicate is given by the schema "the proposition that p is true iff p", and there is no further philosophical analysis to be given of truth itself. Critics object: the schema commits to the existence of propositions; the schema does not handle paradoxes (the liar, Curry); the schema does not explain the role of truth in semantic theorizing (truth-conditional semantics seems to need a substantive notion). Defenders reply that the schema is enough for the work truth needs to do — the rest is philosophical inflation.',
    ARRAY['deflationism_truth', 'horwich_minimalism', 'disquotational_truth'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'tarskis_t_schema',
    'Tarski''s T-Schema',
    ARRAY['language'],
    'Alfred Tarski''s 1933 ("The Concept of Truth in Formalized Languages") formal schema for defining truth in a formal language: T(S) iff p, where T is the truth predicate, S is a name (or structural description) of a sentence, and p is a translation of S into the metalanguage. The instance "snow is white" is true iff snow is white — the trivial-looking but technically powerful schema that any acceptable definition of truth in a language must yield. Tarski''s definition was original to the formal-language case (he held natural languages were unsuited because of self-reference paradoxes); Davidson 1967 reapplied the apparatus to natural language as the foundation of truth-conditional semantics.',
    'Help students see what Tarski achieved. Pre-Tarski, semantic notions like "true" and "refers" seemed metaphysically dubious — they appeared to require a relation between language and reality that was hard to make precise. Tarski showed how, for a formal language with strict structural rules, one could give a recursive definition of "true-in-L" that referred only to the syntactic structure of sentences plus a satisfaction relation between sentences and sequences of objects. The definition handles complex sentences by recursion: a sentence with a logical connective (P and Q) is true iff the components meet the recursive condition. The base cases handle atomic predicates (Px is true iff x has property P). The result: a definition of truth-in-L that is materially adequate (yields all instances of the T-schema) and is itself defined in terms that do not include a primitive truth predicate. Davidson''s 1967 insight: a Tarskian truth theory for a natural language, treating each natural-language sentence as paired with its truth conditions, is itself a theory of meaning. Tarski''s technical results structure most contemporary formal semantics. Pedagogically, the T-schema looks trivial ("snow is white" is true iff snow is white) but is the linchpin of a sophisticated technical apparatus — students should see both the appearance and the underlying machinery.',
    ARRAY['tarski_truth', 't_schema', 'tarskian_truth_definition'],
    'INTERPRETED',
    'ai-seed',
    13
  ),
  (
    'linguistic_relativity',
    'Linguistic Relativity (Sapir-Whorf Hypothesis)',
    ARRAY['language'],
    'The thesis that the structure of a language influences the cognition or worldview of its speakers: that what we can think (or what we can think easily) depends on the linguistic resources we have. Associated paradigmatically with Edward Sapir (1921) and Benjamin Lee Whorf (1940s), the Sapir-Whorf hypothesis comes in strong form (language determines thought) and weak form (language influences thought). The strong form is largely rejected by contemporary linguists; the weak form remains empirically active in cognitive linguistics and psychology (Lera Boroditsky, Eric Pederson, John Lucy).',
    'Frame the topic for students as the philosophically loaded question of whether language shapes thought, distinguishing the strong and weak claims. The strong claim — language determines what is thinkable — was held by Whorf (color terminology, time, motion) and influenced anthropology mid-twentieth century. It largely fell to two lines of evidence: the universal cognitive abilities documented by cross-linguistic research (basic color discrimination, basic spatial reasoning, basic numerical cognition appear universal regardless of linguistic resources); the obvious fact that bilinguals can think things in one language they could not have thought before they learned it (refuting the determinist version). The weak claim — language influences thought, making some patterns easier and others harder — has stronger empirical support: Boroditsky on Russian color discrimination (Russians categorize blue more finely and discriminate blue shades faster); Pederson on absolute vs. relative spatial frames of reference; the ongoing empirical work in cognitive linguistics and psycholinguistics. Philosophically, the topic interfaces with philosophy of mind (the language-of-thought debate; whether we think in a natural language or in a structured representational system independent of natural language) and philosophy of science (the underdetermination question for cross-cultural translation; Kuhn-Whorf parallels). Place this node in the seed for its bridging function: it is where philosophy of language meets philosophy of mind and cognitive science.',
    ARRAY['sapir_whorf_hypothesis', 'whorfian_relativity'],
    'INTERPRETED',
    'ai-seed',
    13
  );

-- Edges: 31 INSERTs, all pedagogical_prerequisite, all within-domain
-- (both endpoints tagged 'language'). Cross-domain edges (semantic
-- externalism ↔ philosophy of mind on content; speech_act ↔ political
-- philosophy on hate-speech; tarskis_t_schema ↔ logic on formal truth
-- theories; sense_and_reference ↔ epistemology on cognitive
-- significance) are P5-11''s exclusive surface.
INSERT INTO public.edges (source_id, target_id, edge_type, provenance, graph_version_added) VALUES
  -- Foundation spine: philosophy_of_language → meaning, reference; meaning/reference → sense_and_reference, proposition, proper_name
  ('philosophy_of_language', 'meaning', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('philosophy_of_language', 'reference', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('meaning', 'sense_and_reference', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('reference', 'sense_and_reference', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('meaning', 'proposition', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('reference', 'proper_name', 'pedagogical_prerequisite', 'ai-seed', 13),
  -- Reference and names cluster
  ('reference', 'definite_description', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('proper_name', 'descriptivism', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('proper_name', 'causal_theory_of_reference', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('causal_theory_of_reference', 'rigid_designator', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('definite_description', 'russells_theory_of_descriptions', 'pedagogical_prerequisite', 'ai-seed', 13),
  -- Meaning theories cluster
  ('proposition', 'truth_conditional_semantics', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('truth_conditional_semantics', 'compositionality_semantic', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('meaning', 'use_theory_of_meaning', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('meaning', 'verificationism', 'pedagogical_prerequisite', 'ai-seed', 13),
  -- Speech acts and Gricean pragmatics cluster
  ('meaning', 'speech_act', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('speech_act', 'performative_utterance', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('speech_act', 'gricean_maxims', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('gricean_maxims', 'conversational_implicature', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('speech_act', 'presupposition', 'pedagogical_prerequisite', 'ai-seed', 13),
  -- Externalism cluster (with cross-cluster bridge from causal_theory_of_reference)
  ('reference', 'semantic_externalism', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('causal_theory_of_reference', 'semantic_externalism', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('semantic_externalism', 'twin_earth', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('semantic_externalism', 'narrow_content', 'pedagogical_prerequisite', 'ai-seed', 13),
  -- Indexicality and context cluster (with cross-cluster bridge from truth_conditional_semantics)
  ('meaning', 'indexical', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('indexical', 'character_and_content', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('truth_conditional_semantics', 'character_and_content', 'pedagogical_prerequisite', 'ai-seed', 13),
  -- Truth in language cluster (with cross-cluster bridge from truth_conditional_semantics)
  ('proposition', 'deflationary_theory_of_truth', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('deflationary_theory_of_truth', 'tarskis_t_schema', 'pedagogical_prerequisite', 'ai-seed', 13),
  ('truth_conditional_semantics', 'tarskis_t_schema', 'pedagogical_prerequisite', 'ai-seed', 13),
  -- Adjacent: linguistic_relativity bridges philosophy of language to philosophy of mind / cognitive science
  ('meaning', 'linguistic_relativity', 'pedagogical_prerequisite', 'ai-seed', 13);

COMMIT;
