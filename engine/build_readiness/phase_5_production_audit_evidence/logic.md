# Phase 5 production audit evidence — logic (philosophical)

> Authored by S-0111 (routine session) per T-PHASE-5-AUDIT task AUDIT-LOG.
> SEP-anchored review per `engine/build_readiness/phase_5_production_audit.md`.
> Candidate findings only — disposition deferred to the closeout interactive session.

## Sample metadata

- Subdomain / scope: logic (philosophical) — modal logic, conditionals, semantic paradox, vagueness, paraconsistent, deontic, plus the propositional/predicate/classical foundation tier
- Edge population: 34 (all from `0090_seed_logic_part1.sql`; single-file seed per master-plan §T1-B P5-03 — no a/b split)
- Edge sample size: 12; sample density: 12/34 = 35.3%
- Sample selection: deterministic md5(seed='AUDIT-LOG' || source_id || '|' || target_id) ordering
- Node sample size: 8; selection: edge-anchored union (15 unique nodes from 12 sampled edges) ordered by md5(seed='AUDIT-LOG' || node_id), take first 8
- Generation date: 2026-05-10

## Sampled-edge candidate findings

### Finding E-1
EDGE: predicate_logic [domain=logic] → russell_paradox [domain=logic]
   edge_type = pedagogical_prerequisite, weight/confidence/evidence not surfaced (per master-plan §T2-E empty `evidence` field is graph-wide; not penalized in verdict)
SEP-ANCHORED REASONING: SEP entry on "Russell's Paradox" frames the 1901 paradox as arising when the unrestricted comprehension principle (∀φ. {x : φ(x)} is a set) of Frege's Grundgesetze is applied to the predicate "x is not a member of itself" — the construction R = {x : x ∉ x} and the derivation R ∈ R ↔ R ∉ R require the apparatus of predicate logic (variables ranging over individuals/sets, predicates with their extensions, the comprehension schema as an instance of the predicate-logic schema "for any predicate, there is a set of things satisfying it"). Without predicate logic in hand, the construction cannot be expressed. The migration's edge runs predicate_logic → russell_paradox in the canonical pedagogical-dependency direction: students learn predicates and quantifier syntax in the predicate-logic chapter, then encounter Russell's paradox as the foundational-crisis instance where naive comprehension breaks. SEP exposition follows this order.
VERDICT: sound
CONFIDENCE: high

### Finding E-2
EDGE: propositional_logic [domain=logic] → predicate_logic [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entries on "Classical Logic" and "First-order Logic" treat first-order (predicate) logic as a strict extension of classical propositional logic — adding individual constants and variables, n-place predicates, and the universal/existential quantifiers to the propositional connectives. Every standard logic textbook (Mendelson, Enderton, van Dalen, Boolos-Burgess-Jeffrey) introduces propositional logic first (atomic letters, truth tables, validity, soundness/completeness for propositional calculus), then extends to predicate logic. The migration's prose explicitly notes "extends propositional logic with internal sentence structure," which matches the SEP framing. Pedagogical direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-3
EDGE: modal_logic [domain=logic] → kripke_semantics [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Modal Logic" presents the syntactic apparatus first — the necessity □ and possibility ◇ operators, the K axiom (□(P→Q) → (□P → □Q)), the necessitation rule, the standard system hierarchy K/T/B/S4/S5 — and then introduces Kripke semantics as the model-theoretic interpretation that vindicates each axiomatic system. The C.I. Lewis S1-S5 axiom systems (1918-1932) historically preceded Kripke's semantics (1959, 1963) by decades, and standard textbooks (Hughes-Cresswell, Chellas, Garson) follow the same order: first the modal language and its axiom systems, then the possible-worlds model theory that interprets them. The migration's edge runs modal_logic → kripke_semantics, matching the canonical SEP exposition order. The migration's teaching_notes for modal_logic explicitly says "Don't teach modal logic without teaching Kripke semantics" — but this is about co-teaching, not about reversing the dependency direction; you still introduce the modal language before the model theory that interprets it.
VERDICT: sound
CONFIDENCE: high

### Finding E-4
EDGE: semantic_paradox [domain=logic] → liar_paradox [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entries on "Liar Paradox" and "Self-Reference" treat the liar as the canonical and historically primary instance of the family of semantic paradoxes (the family also including Curry, Berry, Grelling-Nelson, and Richard paradoxes). The taxonomy of "semantic paradox" as a family (vs "set-theoretic paradox," following Ramsey's 1925 distinction) is a 20th-century systematization; the liar itself is much older (Eubulides, 4th c. BC). The pedagogical direction in the migration's edge runs umbrella → instance: introduce semantic paradox as the kind of phenomenon (paradoxes of self-referential semantic notions — truth, satisfaction, denotation), then study the liar as the simplest instance. SEP textbook exposition can go either way (instance-then-generalization, or umbrella-then-instances), and the migration's prose explicitly motivates the umbrella concept via "the family of paradoxes generated by self-referential or improperly stratified semantic notions." Edge is sound on the taxonomy-first reading. The alternative direction (liar_paradox → semantic_paradox) would be defensible too — historically the liar predates the family taxonomy — but the migration's chosen direction matches the systematic-then-particular structure of contemporary logic textbooks.
VERDICT: sound
CONFIDENCE: medium

### Finding E-5
EDGE: material_conditional [domain=logic] → curry_paradox [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Curry's Paradox" frames the 1942 paradox as depending on (a) self-reference, (b) the conditional/implication operator, and (c) contraction (the structural rule P → (P → Q) ⊢ P → Q). In classical propositional logic the conditional IS the material conditional, so material_conditional is a defensible prereq for the standard classical-logic formulation of Curry. The migration's gloss says "Curry's paradox crucially uses the material conditional's contraction-like inference." On strict reading SEP attributes the central role to *contraction* (a structural rule) rather than to the material conditional specifically, and Curry's contemporary interest derives largely from how it survives non-classical responses to the liar that revise negation but retain a contractive conditional (relevance logic, linear logic, and substructural logics drop contraction explicitly to block Curry). For the introductory classical-logic presentation, material_conditional → curry_paradox is fine; the more proximate prereq for the deeper diagnosis would be "contraction" or "deduction theorem," neither of which is a separate node. Edge is supportable on the introductory framing.
VERDICT: sound
CONFIDENCE: medium

### Finding E-6
EDGE: propositional_logic [domain=logic] → semantic_paradox [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entries on "Liar Paradox" and "Truth, axiomatic theories of" frame semantic paradoxes as arising from naive truth principles plus classical logical apparatus — formulating "this sentence is false" requires propositional connectives (the equivalence "λ ↔ ¬λ" uses biconditional + negation), and the derivation of contradiction uses standard classical-logic inference rules. Pedagogically you need propositional logic in hand before you can formulate the liar's structure or any of its semantic-paradox cousins. SEP exposition consistently presents propositional logic first, semantic paradoxes as a topic that exploits the classical-logic apparatus already familiar. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-7
EDGE: conditional_logic [domain=logic] → chisholm_paradox [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Deontic Logic" presents the Chisholm 1963 contrary-to-duty paradox as generated within Standard Deontic Logic (SDL) using natural-language conditionals (notably claim (3) ¬h → O¬t, a contrary-to-duty conditional whose antecedent is itself a violation of an obligation). The bare paradox can be stated and derived using just SDL apparatus + the classical material conditional + the deduction theorem; it does NOT centrally depend on Stalnaker-Lewis closest-world conditional logic. Conditional logic enters the topic in the *response* literature: Hansson's 1969 dyadic deontic logic introduces a conditional obligation operator O(t/¬h) inspired by closest-world structures; Belnap-Horty stit logic reformulates obligations as constraints on agency rather than truth-functional propositions. The migration's edge requires the student to grasp conditional logic before Chisholm. Given that deontic_logic → chisholm_paradox is also an edge in the seed (E-11 in this sample), this conditional_logic → chisholm_paradox edge is the multi-prereq overdetermined path: deontic_logic is the truly proximate prereq for the bare paradox; conditional_logic illuminates the response literature but isn't strictly required to formulate Chisholm. Direction is correct (you do need conditional logic to engage the post-1969 response literature) but the prereq is sharper than the bare paradox demands. Defensible on the response-literature reading; would be more accurate as conditional_logic → (a node representing the dyadic-deontic-logic response family) or just retired in favor of the deontic_logic → chisholm_paradox edge.
VERDICT: defensible
CONFIDENCE: medium

### Finding E-8
EDGE: propositional_logic [domain=logic] → classical_logic [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" frames classical logic as classical propositional logic + classical first-order (predicate) logic, characterized jointly by bivalence, the law of excluded middle, the law of non-contradiction, and the explosion principle. The migration's edge runs propositional_logic → classical_logic. Pedagogically you need propositional logic concepts (truth tables, the standard connectives, validity) before you can articulate the four characterizing commitments of "classical logic" as a system to which non-classical alternatives (intuitionism, paraconsistency, fuzzy logic) are contrasted. SEP exposition matches: propositional logic is introduced as a formal system, then "classical" is the label for the standard interpretation of that system + its first-order extension. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-9
EDGE: indicative_conditional [domain=logic] → counterfactual_conditional [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entries on "Indicative Conditionals" and "Counterfactuals" treat the indicative-vs-counterfactual distinction as a foundational philosophical-logic puzzle, anchored by Adams's 1970 example ("if Oswald didn't kill Kennedy, someone else did" vs "if Oswald hadn't killed Kennedy, someone else would have" — same antecedent and consequent, opposite truth values, so they cannot share truth conditions). Pedagogically the indicative is taught first as the everyday natural-language conditional (with the material+pragmatics, suppositional/probability, and closest-world analyses contrasted), and then counterfactuals are introduced as the subjunctive/contrary-to-fact variant that requires a closest-world treatment as the *standard* analysis (Stalnaker 1968, Lewis 1973). SEP exposition follows this order. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-10
EDGE: propositional_logic [domain=logic] → material_conditional [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" introduces the material conditional as one of the truth-functional connectives of classical propositional logic (defined by the truth table making P → Q false exactly when P is true and Q is false). The migration's edge runs propositional_logic → material_conditional. Pedagogically you need propositional logic in hand (the language, the truth-table semantics, validity) before "material conditional" can be discussed as a *philosophical* topic — namely, the so-called paradoxes of material implication and the mismatch with natural-language conditionals (which motivate the indicative_conditional and counterfactual_conditional concepts that follow). The migration's framing of material_conditional as a node distinct from propositional_logic emphasizes the philosophical questions about material implication, not the bare truth-table connective. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-11
EDGE: deontic_logic [domain=logic] → chisholm_paradox [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Deontic Logic" treats Chisholm's 1963 contrary-to-duty paradox as the canonical adequacy challenge for Standard Deontic Logic (SDL). The paradox's statement and derivation require SDL apparatus — the obligation operator O, the deontic seriality axiom D (Op → Pp), the deontic K axiom — and the four claims (1) Oh, (2) O(h → t), (3) ¬h → O¬t, (4) ¬h jointly entail SDL contradiction (Ot from (1)+(2); O¬t from (3)+(4); Ot ∧ O¬t violates D). Pedagogically you need deontic logic first; Chisholm is then the canonical instance demonstrating SDL's flat-propositional treatment of obligations is wrong. SEP exposition matches the migration's edge direction. Direction sound.
VERDICT: sound
CONFIDENCE: high

### Finding E-12
EDGE: liar_paradox [domain=logic] → curry_paradox [domain=logic]
   edge_type = pedagogical_prerequisite
SEP-ANCHORED REASONING: SEP entry on "Curry's Paradox" frames the 1942 paradox as a member of the same self-reference family as the liar — using diagonalization to construct a self-referential sentence — but distinct in not requiring negation. Curry historically postdates the liar (Eubulides, 4th c. BC) by over two millennia. Pedagogically the liar is the entry point to semantic paradoxes and the diagonalization machinery; once that machinery is in hand, Curry is the conditional-version successor (the sentence asserting "if I am true, then Q"). The crucial pedagogical *contrast* — Curry survives in non-classical responses to the liar that revise negation alone, because Curry uses no negation — is best taught after the liar's responses (Tarski's hierarchy, Kripke's fixed-point, Priest's dialetheism) are in view. SEP exposition presents the liar first and then Curry as the conditional-version successor that complicates the response space. Direction sound.
VERDICT: sound
CONFIDENCE: high

## Sampled-node candidate findings

### Finding N-1
NODE: conditional_logic [id=conditional_logic, domain=logic]
   summary = "The formal logic of counterfactual conditionals developed by Robert Stalnaker (1968) and David Lewis (1973). Treats the counterfactual operator □→ as a non-truth-functional binary connective, evaluated at a Kripke-style frame whose accessibility..."
SEP-ANCHORED REASONING: SEP entry on "The Logic of Conditionals" / "Counterfactuals" / "Conditionals" — Stalnaker (1968) "A Theory of Conditionals" and Lewis (1973) "Counterfactuals" are the canonical citations. Granularity: concept-level (a specific formal system within philosophical logic, not a discipline label). The migration's `_logic` suffix per its own discipline-disambiguation convention (the suffix used for nodes whose unsuffixed name is plausibly ambiguous outside the logic subdomain) is appropriate here. Summary reads as instructional voice with concept-grounded specificity (Stalnaker selection function f(w, P), Lewis similarity ordering, the negative results — failures of strengthening the antecedent, transitivity, contraposition). No granularity-mismatch concerns; no authenticity concerns.
VERDICT: sound
CONFIDENCE: high

### Finding N-2
NODE: predicate_logic [id=predicate_logic, domain=logic]
   summary = "Also called first-order logic. Extends propositional logic with internal sentence structure: individual constants and variables, predicates (one-place, two-place, n-place), and the universal (∀) and existential (∃) quantifiers binding variables..."
SEP-ANCHORED REASONING: SEP entries on "Classical Logic" and "First-order Logic" — predicate logic IS first-order logic; the aliases `first_order_logic`, `quantificational_logic`, `fol` map to canonical SEP terminology. Granularity: foundational formal-system concept, parallel to "classical_logic" — at appropriate granularity for foundation-level philosophical-logic teaching. Distinct in kind from the discipline-label-as-prereq pattern the per-node prompt warns about (e.g., "Political Philosophy", "Metaphysics"); predicate logic is not a discipline but a specific formal system whose syntax and semantics are precisely defined. Summary reads as instructional voice with the right technical content (variables, quantifiers, models M = ⟨D, I⟩, the soundness/completeness/compactness/Löwenheim-Skolem meta-theorems). No concerns.
VERDICT: sound
CONFIDENCE: high

### Finding N-3
NODE: counterfactual_conditional [id=counterfactual_conditional, domain=logic]
   summary = "The natural-language conditional in the subjunctive mood ('if it were raining, the streets would be wet'; 'if Oswald hadn't killed Kennedy, someone else would have'). Typically used to express what would have happened under a counter-to-fact supposition..."
SEP-ANCHORED REASONING: SEP entry on "Counterfactuals" — stand-alone canonical entry. Granularity: concept-level (a specific kind of natural-language conditional, evaluated by closest-world semantics). Summary reads as instructional voice with the canonical examples (Oswald, raining-streets-wet) and the standard logical theory citations (Stalnaker 1968, Lewis 1973), correctly identifying the closest-world semantic apparatus and the non-monotonicity that distinguishes counterfactuals from material conditionals. No concerns.
VERDICT: sound
CONFIDENCE: high

### Finding N-4
NODE: material_conditional [id=material_conditional, domain=logic]
   summary = "The truth-functional connective → in classical propositional logic, defined by the truth table that makes P → Q false exactly when P is true and Q is false (and true in all three other rows). Equivalent to ¬P ∨ Q. The standard formal rendering of 'if P then Q' in classical logic..."
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" — material implication is one of the standard truth-functional connectives. Granularity: concept-level (a specific connective with a specific truth-table semantics, with the philosophical interest located in the paradoxes of material implication and the mismatch with natural-language conditionals). Summary reads as instructional voice with the truth-table definition, the equivalence to ¬P ∨ Q, the paradoxes-of-material-implication framing, and the appropriate caveat that the mismatch with natural-language is the philosophical interest. No concerns.
VERDICT: sound
CONFIDENCE: high

### Finding N-5
NODE: indicative_conditional [id=indicative_conditional, domain=logic]
   summary = "The natural-language conditional in the indicative mood ('if Oswald didn't kill Kennedy, someone else did'), distinguished from the subjunctive / counterfactual ('if Oswald hadn't killed Kennedy, someone else would have'). The two famously differ in truth value..."
SEP-ANCHORED REASONING: SEP entry on "Indicative Conditionals" — stand-alone canonical entry. Granularity: concept-level (a specific kind of natural-language conditional). Summary reads as instructional voice with Adams's 1970 canonical example and the three dominant analyses (material+pragmatics with Grice and Jackson; suppositional/probability with Adams and Edgington; closest-world with Stalnaker). The Adams example is presented correctly with the appropriate "same antecedent same consequent opposite truth values" diagnosis. No concerns.
VERDICT: sound
CONFIDENCE: high

### Finding N-6
NODE: classical_logic [id=classical_logic, domain=logic]
   summary = "The orthodox logical system of mainstream mathematics and analytic philosophy: classical propositional logic plus classical first-order predicate logic. Characterized by bivalence (every proposition is either true or false, never both, never neither), the law of excluded middle..."
SEP-ANCHORED REASONING: SEP entry on "Classical Logic" — stand-alone canonical entry. Granularity: foundational system, parallel to predicate_logic in being a foundational formal-system concept. The four characterizing commitments (bivalence, LEM, non-contradiction, explosion) are SEP's standard list and are tightly coupled — rejecting bivalence typically requires rejecting at least one of the others, as the migration's teaching_notes correctly note. The role of classical_logic as the *default* against which non-classical alternatives are contrasted is also SEP-canonical. Distinct in kind from discipline-label patterns; "classical logic" is not a discipline but a specific system with a specific semantic interpretation. No concerns.
VERDICT: sound
CONFIDENCE: high

### Finding N-7
NODE: curry_paradox [id=curry_paradox, domain=logic]
   summary = "Haskell Curry's 1942 paradox: consider a sentence C asserting 'if C is true then Q' for any Q. Naive truth principles plus the deduction theorem and contraction yield Q for arbitrary Q, including absurdities. Distinct from the liar in not requiring negation; distinct from Russell's paradox in operating in propositional logic alone..."
SEP-ANCHORED REASONING: SEP entry on "Curry's Paradox" — stand-alone canonical entry. Granularity: concept-level (a specific paradox, with a specific construction and a specific structural-rule diagnosis). Summary reads as instructional voice with the canonical 1942 origin, the construction (no negation), the deduction-theorem-plus-contraction diagnosis, and the two key contrasts (vs liar — no negation; vs Russell — propositional logic alone, no set theory). The SEP-attributed crucial role of contraction and the relevance/linear/substructural-logic responses (drop contraction) are correctly identified in the teaching_notes. No concerns.
VERDICT: sound
CONFIDENCE: high

### Finding N-8
NODE: liar_paradox [id=liar_paradox, domain=logic]
   summary = "The paradox generated by a sentence asserting its own falsity — 'this sentence is false' (or, more carefully, λ: λ is false). Under naive truth principles, λ is true iff λ is false, contradicting bivalence (or generating absurdity classically). The Eubulides version (4th century BC) is the historical origin..."
SEP-ANCHORED REASONING: SEP entry on "Liar Paradox" — stand-alone canonical entry. Granularity: concept-level (a specific paradox). Summary reads as instructional voice with the Eubulides origin, the strengthened-liar formulation ("this sentence is not true" rather than "is false") to avoid Tarskian "neither true nor false" responses being immediate, and the canonical response landscape (Tarski 1933 hierarchy; Kripke 1975 fixed-point; Priest 1979 dialetheism; Field 2008 paracomplete). The diagnostic framing — any theory of truth committed to the T-schema + self-reference + classical logic faces the liar; relaxing any one is the choice point — is SEP-canonical. No concerns.
VERDICT: sound
CONFIDENCE: high

## Cross-cutting observations

- **Lowest within-subdomain defect rate of the routine block so far.** Edge-verdict tally: 11 sound, 1 defensible (E-7); node-verdict tally: 8 sound. Substantive-defect rate 1 of 20 sampled elements = 5%. Below the S-0105 epistemology baseline (5.4%) and S-0110 mind (10.8%); well below the S-0104 cross-bridge calibration baseline (35.2%); roughly tied with the lowest within-domain rate. The pattern fits the structural prediction that within-subdomain edges run cleaner than cross-domain bridges — and within-logic specifically runs cleanest among the within-subdomain audits because the formal-systems hierarchy (propositional ⊂ predicate ⊂ classical; modal as a propositional extension; deontic as a modal extension; conditionals as a propositional / modal question) tightly determines pedagogical direction in a way that contested philosophical concepts (e.g., the property-dualism / knowledge-argument relation in the mind seed) do not.
- **Half-sample defect rate (E-1 through E-6) was 0/6 = 0%.** The mid-sample expansion trigger (>60% at half-sample → expand to 50% density) was nowhere near firing; standard 35% density held. The single defensible verdict (E-7) falls in the second half.
- **The single defensible verdict (E-7 conditional_logic → chisholm_paradox) is a multi-prereq overdetermined-edge pattern.** The bare Chisholm paradox can be stated and derived using just SDL apparatus + the classical material conditional + the deduction theorem (deontic_logic → chisholm_paradox is also a seed edge — E-11 in this sample); conditional_logic illuminates the response literature (Hansson 1969 dyadic deontic, Belnap-Horty stit) but isn't strictly required for the bare paradox. Distinct in shape from the mind seed's argument-vs-position directionality reversals (S-0110 E-14 hard_problem→explanatory_gap, E-17 property_dualism→knowledge_argument, both reversed-medium-confidence) and from the metaphysics seed's tools-vs-topic ordering pattern (S-0109 E-3) — this is overdetermined-multi-prereq, not direction-reversal. Closeout disposition: either retire E-7 (deontic_logic → chisholm_paradox is enough) OR retain it as illuminating-the-response-literature with no graph-mutation needed (the migration permits multi-prereq).
- **Zero direction reversals.** All 12 sampled edges run in the canonical SEP-exposition direction. Distinct from the mind seed (2 reversals in 25 edges = 8%); the logic seed's tightly-determined formal-systems hierarchy makes direction-reversal less likely than in seeds with contested philosophical positions / arguments.
- **Zero granularity-mismatch verdicts.** All 8 sampled nodes are at appropriate concept granularity. The two foundation-level formal-system nodes (predicate_logic, classical_logic) are *not* discipline labels in the per-node prompt's warning sense (the prompt names "Political Philosophy", "Metaphysics", "Ontology" as discipline-name examples; "classical logic" and "predicate logic" are specific formal systems with precisely-defined syntax/semantics, parallel in granularity to "modal_logic" or "deontic_logic"). Distinct in kind from the school/movement granularity surfaced at S-0110 N-2 phenomenology and the sub-discipline-label-with-content pattern at S-0105 N-8 + S-0108 N-4/N-9 + S-0109 N-4/N-6.
- **Zero authenticity concerns.** All 8 sampled nodes' summaries read as instructional voice with concept-grounded specificity (canonical citations, technical apparatus, the right level of detail for the granularity). No model-generic philosophy paraphrase.
- **Empty `evidence` field uniform null across all 34 within-logic edges** (master-plan §T2-E pre-listed; confirmed graph-wide again — sixth session in a row with this pattern, after AUDIT-CB / AUDIT-EPI / AUDIT-ETH / AUDIT-MET / AUDIT-MIN).
- **No new gate-feasible audit-system-input class authored as deliverable.** The four pre-listed master-plan proposals plus the cross-bridge-specific candidate from S-0104 were not extended; within-logic data did not corroborate any new pattern beyond the audit-system-inputs already identified. The S-0110 candidate (argument-vs-position directionality validator soft-warn) is not corroborated by within-logic data — the logic seed has zero argument-vs-position-style reversals because its node taxonomy doesn't include "arguments" and "positions" in the philosophy-of-mind sense (the closest analogue would be "paradoxes" and "responses-to-paradoxes," but the seed's edges run paradox → response in the canonical exposition order, with no reversals).

## SEP citations consulted

- SEP entry on "Classical Logic" (E-2, E-8, N-2, N-4, N-6)
- SEP entry on "First-order Logic" / "Logic, Classical Predicate" (E-2, N-2)
- SEP entry on "Russell's Paradox" / "Set Theory" (E-1)
- SEP entry on "Modal Logic" (E-3)
- SEP entry on "Liar Paradox" (E-4, E-6, E-12, N-8)
- SEP entry on "Curry's Paradox" (E-5, E-12, N-7)
- SEP entry on "Self-Reference" / "Truth, axiomatic theories of" (E-4, E-6, N-8)
- SEP entry on "Deontic Logic" (E-7, E-11)
- SEP entry on "The Logic of Conditionals" / "Conditionals" / "Counterfactuals" (E-7, E-9, N-1, N-3)
- SEP entry on "Indicative Conditionals" (E-9, N-5)
