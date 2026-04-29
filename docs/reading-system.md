# Reading System

## Relationship to the Mastery Graph

The mastery graph is the primary teaching surface. It teaches concepts conversationally from the AI's parametric knowledge — no source text in context, no copyright dependency, no user-supplied materials required. The vast majority of learning happens here. The AI can teach transcendental idealism, the unreliable narrator, cognitive dissonance, or the French Revolution without quoting or displaying any copyrighted text, because the interaction method is conversational. The user engages with ideas through dialogue, not through guided page-turning.

Close reading is an **optional deep-dive mode** — a separate product surface that activates when the mastery graph's parametric teaching is insufficient for a particular concept or when the user's interest warrants sustained engagement with a primary text. The bar should be high. Many users will master difficult concepts through conversation alone. Some won't, and some will develop genuine intellectual interest that demands encountering the original argument in its own voice. Both are valid paths. The system respects the learner's judgment about which path to take, and the AI can signal when a concept genuinely benefits from close reading without making it a requirement.

## The Problem Close Reading Solves

Existing AI tools fail at deep reading because they drift into whatever seems locally salient instead of following the actual argument, every session starts from zero knowledge of the reader, they enumerate and summarize rather than teach, and they can't maintain interpretive continuity across a long text. The reading system solves all four problems: the outline prevents drift, the learner model provides persistence, the expression contract enforces teaching over summarizing, and the section-by-section architecture maintains continuity.

## Architecture: User-Supplied Text with AI-Generated Outline

The user acquires and uploads the text. The app never hosts, distributes, or embeds copyrighted material. All copyrighted content lives in a user-scoped personal corpus — the user's own purchased material, stored for their own use.

### Ingestion

The user uploads a file (EPUB, PDF, or plain text). The app chunks the text, embeds it via pgvector in Supabase, and stores it in the user's personal corpus. This is a one-time operation per text. Once ingested, the text is available for close reading sessions indefinitely. Storage cost is negligible — a typical ebook is 500KB-2MB as raw text; forty books with embeddings runs roughly 150MB per user. At Supabase pricing ($0.125/GB/month beyond included storage), even 1,000 users with 40 books each costs about $19/month in storage overage. The real cost of close reading is API compute per session, not storage.

### Outline Generation

At ingestion time, Opus generates an interpretive outline for the text. The outline is the session-by-session instruction that prevents AI drift and maintains interpretive continuity. It maps the text's argument structure, marks where the reader should be at each stage, and specifies which concept nodes in the mastery graph each section touches.

The outline is generated from two sources, one required and one optional:

**Parametric knowledge (always available).** Opus knows the scholarly traditions around major texts. It can generate an outline for the Phenomenology of Spirit that follows Pinkard's reading, or Stern's, or a synthetic account, without the commentary text in context. The outline quality depends on how well-represented the text is in the model's training data. For canonical works with extensive scholarly commentary, parametric outlines are strong. For obscure or very recent works, they're weaker. This is the baseline — every text gets at least this.

**User-supplied commentary (optional enhancement).** If the user uploads a scholarly commentary alongside the primary text, the outline generation incorporates it. This produces a more specific, more grounded outline — anchored in a particular interpretive framework rather than the model's blended knowledge. The commentary is ingested into the user's personal corpus alongside the primary text. This is the same "bring your own book" model: the user supplies it, the app never distributes it.

### Dialectical Text Handling

The outline must account for texts that undermine their own earlier framing on purpose. This is not only a Hegel problem — Kierkegaard, Nietzsche, Wittgenstein, and many literary works do versions of this. An outline entry for a self-undermining section is structurally different from a linear one. A linear entry says "this section establishes X." A dialectical entry encodes: "this section appears to establish X, but the argument's own logic will reveal X as inadequate by the end of the section — the reader should be led to see X as compelling *before* seeing why it fails, because experiencing the failure is the pedagogical point."

This connects directly to the expression contract's teaching modes. When the reader hits the first half of a dialectical reversal, the AI operates in mode 2 — leading the learner to see X's role in the argument. When the reversal arrives, the AI shifts to mode 3 — testing the learner's interpretation rather than explaining the reversal. "You just worked through Hegel's account of sense-certainty as immediate knowledge. What's the problem with it?" The outline entry encodes not just what happens argumentatively but which teaching mode the AI should be in at each stage.

The outline is what makes dialectical teaching possible. Without it, the AI has no way to know that the current section is the first half of a reversal. It would treat each section on its own terms and miss the dramatic structure entirely.

### Session-by-Session Reading

Each reading session loads: the relevant chunk of the primary text (retrieved from the user's personal corpus via the outline's section mapping), the corresponding outline entry, the expression contract, and the learner's recent event history on related concepts. Commentary chunks are loaded alongside if the user supplied commentary.

A chapter or major section of a text runs 5K-15K tokens. Commentary on that section runs similar. Add the outline entry (a few hundred tokens), expression contract, learner model context, and conversation history, and the total is comfortably within context limits for any current model. The full text never needs to be in context — only the current section.

## Domain-Specific Profiles

The close reading architecture is domain-agnostic in structure but the relationship between text, outline, and teaching varies by domain.

**Philosophy.** Cleanest case. Primary texts (ancient and early modern) are often public domain. Modern translations are copyrighted but the user can supply them. Commentary serves a distinct grounding function — a separate layer from the primary text. The outline tracks the argument through the primary text, informed by commentary. Two-layer architecture: primary text + commentary is the fullest version; primary text + parametric outline is the minimum.

**Literature.** The primary text IS the copyrighted thing. Close reading of Beloved or Blood Meridian requires the text in context, and sentence-level work ("look at how Morrison uses the passive voice here") requires the passage. The "bring your own book" model applies directly — the user uploads their purchased copy. No separate commentary layer is needed in most cases; the outline tracks the narrative argument and key passages, and the AI's literary-critical knowledge provides the interpretive framework. When literary criticism is useful as grounding (e.g., reading Joyce alongside Stuart Gilbert), the user can supply it as optional commentary.

**History.** Every work is a commentary — there is no clean primary/secondary split. A learner studying the French Revolution reads Schama, or Furet, or Lefebvre, each of which IS the interpretive argument. The historian's book is simultaneously the text being read and the interpretive framework. The outline tracks the historian's argument and methodology — their thesis, their use of evidence, their biases, the historiographical tradition they're responding to. One-layer architecture: the book itself is the argument, and the outline maps its structure. The AI helps the learner track the argument, identify methodology, and connect claims to what they know from the mastery graph.

**Psychology / Sciences.** Foundational texts have varying copyright status. The real teaching material is often modern — textbooks, meta-analyses, empirical studies. For conceptual teaching, the mastery graph handles this parametrically without close reading. Close reading activates when a user wants to engage with a specific study, a specific theoretical text (Freud's case studies, James's Principles), or a specific methodological argument. The outline tracks the author's reasoning and evidence structure. The AI's role is to help the learner evaluate the argument, not just understand it.

## Event Emission to the Learner Model

Close reading sessions emit events to the learner model through the same event stream as mastery graph teaching. Each exchange about a concept generates a learner event with its actual engagement depth.

Close reading events carry inherently low scaffolding distance — the text is in context, the outline is guiding, the AI is walking the reader through the argument. This is by design, not a flaw. The events reliably move concepts from "not encountered" to "exposed" and frequently to "proficiency." They rarely produce mastery-grade evidence, because mastery requires high-scaffolding-distance demonstration in a new context.

Mastery comes later, in the mastery graph. When concepts from a close reading appear in downstream teaching — in a different text, a different domain, a different conversation — the learner must wield them without the original text propping them up. A learner who did a close reading of the Phenomenology and later encounters negation in a Kierkegaard context gets a callback reference with high scaffolding distance and high novelty. That's mastery-grade evidence. The two systems talk through the event stream; no special interface is needed.

The reading system also emits `source_ineffective` tension records when a text isn't working for a learner on a given concept — the same self-correction mechanism used throughout the mastery graph.

## AI-Initiated Reading Recommendations

The teaching AI can signal that a concept genuinely benefits from close reading — either because the parametric teaching is hitting limits or because the learner's engagement pattern suggests deep interest. The recommendation includes: which text to read (specific edition, translation, or commentary), why this text rather than alternatives, and what the user should expect from the close reading that the conversational teaching can't provide.

This connects to the commerce layer in content-strategy.md. The AI's text recommendation links to acquisition channels (Amazon Associates, library systems, publisher direct) so the user can move from "the AI says I should read this" to "I own it and can upload it" with minimal friction.

## Repeatable Setup Process Per Text

1. **User acquires the text.** The AI has recommended a specific edition or translation. The user purchases or obtains it.
2. **User uploads the file.** One-time action. The app chunks, embeds, and stores it in the user's personal corpus.
3. **Opus generates the outline.** Automatic at ingestion. Uses parametric knowledge of the scholarly tradition, plus the uploaded commentary if the user supplied one. The outline maps sections to argument stages, marks dialectical reversals, specifies teaching modes, and identifies which mastery graph concepts each section touches.
4. **User reviews the outline.** Not for scholarly accuracy — the user isn't expected to evaluate whether the outline correctly represents Pinkard's reading. The review is for coherence: does the outline read as a sensible guide? Can the user follow what it claims the argument does? If the outline is opaque at this stage, it won't help during reading.
5. **Expression contract loads.** A reusable template with per-text calibration. The mode 1/2/3 ratio adjusts based on text difficulty (estimable from the domain and the user's mastery states on related concepts). Hegel is mode-1-heavy. Descartes is mode-2/3-heavy. The system can estimate this; the user can override.
6. **Reading begins.** Session-by-session, section-by-section, with the outline maintaining continuity across sessions.

Manual work per text: acquire it, upload it, review the outline. Everything else is automated.

## Prototype Plan

The minimum viable test: a single major section of a single text. Sense-Certainty through Perception in Hegel's Phenomenology — short, well-commented, dialectical. Generate a parametric-only outline (no commentary uploaded). Use that outline to read the primary text with Sonnet as the teaching AI. The evaluation criterion: did the outline prevent the AI from drifting, and did the reading feel like following an argument rather than receiving a series of disconnected explanations? If yes, the architecture is validated. If no, the failure point reveals whether the problem is outline quality or teaching behavior — which determines whether to invest in better outline generation or better expression contract tuning.

---
*Last updated: 2026-04-08 (full rewrite: general architecture replacing Hegel-specific case study; domain profiles; copyright resolution via bring-your-own-book model; event emission to learner model; storage economics)*
