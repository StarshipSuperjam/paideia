# Pedagogy

## The Expression Contract

The core teaching method. Not a personality — a *method*. Enforced through project instructions.

**Three teaching modes, triggered by the learner's type of confusion:**

1. **Sentence-level confusion** → Give the meaning directly. Don't Socratic-method someone who can't parse the sentence yet.
2. **Understands content but not significance** → Lead the learner to see its role in the argument. Ask questions. Build connections.
3. **Has an interpretation** → Test it against the text. Don't validate — show where the reading holds or breaks.

A good teacher switches between these unconsciously. The contract makes the AI do it deliberately.

## Layered Instruction Architecture

Each layer does one job cleanly:

| Layer | What it controls | Where it lives |
|-------|-----------------|----------------|
| **Style** | Surface: no lists, no hedging, prose that thinks out loud | Claude Style feature |
| **Project instruction** | Pedagogy: when to lead, explain, or test | Project system prompt |
| **Text-specific outline** | Interpretive spine for the current work | Project knowledge file (per text) |
| **Commentary** | Scholarly grounding and accuracy | Project knowledge file (per text) |
| **Learner model** | What the learner knows, connections made, forward plan | MCP filesystem |

## Assessment Rubric
**Added: 2026-04-07**

The AI continuously evaluates the learner's responses along three dimensions. These dimensions are universal — the same framework applies to every concept and every learner — but the threshold for what counts as "sufficient" scales contextually.

**Reconstruction.** Can the learner state the core of the concept without the AI having just said it? This distinguishes generated understanding from received understanding. A paraphrase immediately following the AI's explanation scores low on reconstruction; an unprompted restatement in the learner's own words scores high. The key question: did the learner produce the idea, or did they receive it?

**Application.** Can the learner deploy the concept against something not present in the current conversation? This is the difference between comprehension and ownership. A learner who can explain Transcendental Idealism but cannot see it operating in a passage they haven't encountered before has comprehension, not application. The AI looks for the learner using the concept as a tool, not describing it as a fact.

**Boundary awareness.** Does the learner see where the concept stops working — its limits, tensions with other ideas, the questions it opens but cannot answer? This is the hardest dimension and the one that most reliably separates proficiency from mastery. A learner who can reconstruct and apply eudaimonia but cannot articulate why someone might disagree with Aristotle's account of flourishing has not yet reached the edges of the concept.

### Scaffolding Proximity

Each exchange carries an implicit scaffolding proximity — a measure of how much the AI's recent output could have shaped the learner's response. A response produced moments after the AI explained the concept has high scaffolding proximity. A spontaneous cross-domain connection the learner makes unprompted has low scaffolding proximity. The AI treats high-scaffolding-proximity evidence as weaker than low-scaffolding-proximity evidence, even when the response itself is sophisticated.

This is why initial teaching almost never produces mastery-grade evidence. The entire conversation is scaffolded — the learner has the AI's reasoning visible in the thread, can pattern-match its analytical moves, and can reproduce them without owning them. The same three-dimensional evaluation applied in a boss encounter (where scaffolding is zero) carries full evidentiary weight.

### Rigor Score
**Added: 2026-04-07 | Revised: 2026-04-09**

The concept's rigor score (a continuous 0.0–1.0 value; see architecture.md) modulates assessment depth. The three assessment dimensions are always evaluated, but the rigor score determines how much evidence the AI demands before logging high-engagement events and how hard it probes during mastery verification.

**Low rigor score** (~0.0–0.3): Reconstruction plus basic application suffices for proficiency. Boundary awareness at this level is a bonus, not a requirement. These are entry-point concepts where a false proficiency costs a slightly rougher start on the next concept — recoverable in real time by the teaching AI.

**Mid-range rigor score** (~0.3–0.6): Reconstruction, application, and a lightweight boundary probe. The AI asks at least one question that pushes at the concept's limits. The learner doesn't need to resolve the tension, but they need to see it.

**High rigor score** (~0.6–1.0): All three dimensions required, and the boundary probe must be substantive. A false proficiency here cascades — the learner will hit a wall several concepts downstream, and backtracking is expensive.

The learner's demonstrated sophistication across prior engagements also calibrates the AI's expectations. A learner who has mastered several high-rigor concepts is held to a higher standard on low-rigor ones — not because the concept is different, but because the AI knows this learner operates at a level where lower expectations would be patronizing.

### What the Rigor Score Does Not Change

The three assessment dimensions are always present. The rigor score scales which dimensions must be *satisfied* for proficiency, not which dimensions are *evaluated*. The AI always tracks reconstruction, application, and boundary awareness. On a low-rigor concept, boundary awareness evidence is still logged even if it's not required — it feeds the mastery computation and enriches the learner model.

### Learner-Relative Assessment
**Added: 2026-04-09**

The AI evaluates the learner's responses against what someone who has mastered the learner's current prerequisites — and nothing else — should be able to produce. The AI does not benchmark against its own knowledge of the field. A boundary awareness probe on Cartesian dualism does not look for Ryle's category mistake argument if the learner has not encountered Ryle. It looks for the learner to find *any* tension using the conceptual vocabulary they currently have.

This constraint interacts with the rigor score productively. A high-rigor concept deep in the graph means the learner has a large vocabulary of mastered prerequisites to draw on. The AI can legitimately expect more sophisticated responses there — not because it's comparing to the full field, but because the learner's own toolkit is richer. Assessment scales with the learner's demonstrated capability, not with the AI's encyclopedic knowledge.

The practical instruction to the teaching AI: "Evaluate the learner's response against what someone who has mastered these specific prerequisites and nothing else should be able to produce. A response that demonstrates genuine reasoning with the tools available to the learner is sufficient. Do not penalize the absence of ideas the learner has not yet encountered."

## Calibrating to Prior Exposure
**Added: 2026-04-07**

When the learner model shows a concept as "exposed" (the user has read about it before but hasn't demonstrated mastery), the teaching AI adjusts its entry point. It doesn't re-explain from scratch — it probes what the user retained, identifies gaps, and builds from there. But it does verify understanding before advancing. This connects directly to the three teaching modes: an exposed user is less likely to need mode 1 (sentence-level clarification) and more likely to need mode 3 (testing their existing interpretation against the text). The AI should not assume exposure means comprehension — it means a warmer start, not a skip.

Backward inference from demonstrated mastery works differently. If the user demonstrates mastery of a downstream concept, the system infers mastery of its antecedents and does not re-test them unless contradicted by a later interaction.

## Cold Start / Initial Calibration
**Added: 2026-04-07 | Revised: 2026-04-08**

The learner model is empty on first use. The system cannot assume the user knows nothing, everything, or anything specific in between. Three mechanisms work together to populate the model quickly, each feeding the persistent learner state so the cold-start problem only exists once.

**Diagnostic conversation.** Before generating a learning path, the system has a brief conversational exchange about the target topic's prerequisites — not a quiz, but a probe. ("When you think about Hegel's dialectic, does the concept of negation feel familiar, or is that new territory?") The user's responses set initial mastery states: substantive answers that demonstrate understanding can mark concepts as "proficiency"; signals of familiarity without depth mark concepts as "exposed"; no recognition leaves them as "not encountered." This front-loads the most valuable calibration before the user commits to a path.

**Adaptive pacing within the path.** Each step in the generated path opens with a brief orientation. If the user signals familiarity ("I've studied this"), that is self-report — it sets "exposed," never "demonstrated." The system does not skip the concept. Instead, it shifts teaching mode: rather than explaining from scratch (mode 1), it probes what the user retained and tests their interpretation (mode 2 or 3). The concept still gets touched; the entry point is warmer, not absent. Only when the interaction itself reveals genuine understanding does the concept move to "proficiency."

**Passive inference from engagement.** The system detects mastery from the sophistication of questions and comments the user makes without explicit testing. If someone asks about Heidegger's destruction of metaphysics in a way that presupposes understanding of Hegelian negation, the system can infer mastery of negation without ever having tested it directly. This is the same backward-inference mechanism described in architecture.md, applied in real time during conversation rather than only at formal assessment points.

### V1 Calibration Defaults
**Added: 2026-04-08**

The v1 default calibration assumes a learner encountering these ideas for the first time — a community college freshman, not an experienced autodidact. This means mode 1 (direct explanation of sentence-level confusion) frequency starts high, scaffolding proximity baselines assume the learner needs more support rather than less, and the diagnostic conversation probes rather than assumes prior knowledge.

This is the right default because the asymmetry of failure is directional. A freshman encountering content beyond their scope cannot proceed — and should not be made to feel inadequate for a gap they are specifically there to close. An autodidact encountering freshman-level calibration is mildly annoyed at worst, and the annoyance is short-lived: the diagnostic conversation and the first few exchanges generate enough signal to escalate rapidly. A system that starts at freshman defaults and ramps based on engagement quality is indistinguishable from a system "built for autodidacts" by the end of the first concept engagement.

The cold-start framing communicates that the system adapts to the quality of the learner's engagement. This simultaneously reassures the freshman (the system will meet them where they are) and activates the autodidact (they are being invited to demonstrate what they know). Neither audience needs to know the other exists. The expression contract's adaptive teaching modes do the work — the defaults only govern the starting posture before the system has data.

## AI-Initiated Awareness Introduction
**Added: 2026-04-07**

The system can proactively introduce a concept into the learner's awareness before they ask for it. This happens when a prerequisite concept is about to become relevant on the learning path, or when mastery of a current concept activates a cross-domain tendril. The AI does not wait to be asked — it surfaces the concept, gives a vivid framing that makes the learner want to engage, and ends with an open question the domain grapples with. This sets the concept to "exposed" in the learner model. It is the threshold act before teaching begins.

## Mastery Verification
**Added: 2026-04-07 | Revised: 2026-04-07**

The AI's greatest liability as a teacher is that it makes learners *feel* understood. A good tutor closes the gap between where the learner is and where they need to be — but that instinct is precisely what must be suppressed during mastery verification. If the AI helps the learner arrive at the answer, the win is empty. The learner echoed back what the AI scaffolded, not what they actually own.

This failure mode has a name: **immediate echoing as false mastery**. A learner can paraphrase Kant's synthetic a priori convincingly right after encountering it. That is not mastery — it is still warm in the working memory. Mastery means being able to reconstruct and *apply* the concept later, in a new context, without prompting.

### Structural Separation of Proficiency and Mastery

Initial teaching can grant proficiency but almost never grants mastery. This is not a policy choice — it is an evidentiary constraint. During a teaching conversation, the scaffolding proximity of every exchange is high. The learner has the AI's reasoning visible in the thread. Even a genuinely novel application produced in-session might be partly scaffolded by the conversational context. The system treats in-session evidence as inherently weaker than time-delayed evidence.

The exception exists: a learner who already owns a concept (the professor who has taught the allegory of the cave for twenty years) produces low-scaffolding, high-sophistication evidence from the first exchange. The system does not impose a minimum elapsed time before mastery — it imposes a minimum evidence quality, and that quality is almost impossible to reach within a scaffolded teaching session. The constraint is evidentiary, not temporal.

### Mastery Verification as Organic Escalation

Mastery verification does not interrupt a foreign syllabus. It happens within the syllabus the concept belongs to, as a natural escalation of downstream teaching.

The trajectory: the learner reaches proficiency on concept A and advances to concept B (which has A as a prerequisite). The AI teaching B naturally references A — because good teaching requires connecting new material to its foundations. These references are callback encounters: reinforcing events logged to the event stream that simultaneously probe whether the learner retained A. As the learner moves further downstream (concept C, concept D), the AI continues weaving A back in. Each callback produces a signal about how well A has been retained.

At some point — when enough distance and enough evidence have accumulated — the callbacks stop being references and become challenges. The AI stops scaffolding when it brings up concept A and instead asks the learner to do the work. "How does what we're seeing here connect back to what Kant was doing with the categories?" This is the mastery verification moment. It is not announced, labeled, or described to the user as a "boss encounter" or by any other name. It is a moment in a teaching conversation where the AI applies the zero-scaffolding constraint and evaluates the learner's response against the full three-dimensional rubric.

The system never names this mechanic to the user. The user experiences it as the AI asking a harder question than usual. If they succeed, mastery glow activates on the globe and tendrils become visible. If they don't, the AI continues teaching — no failure state is announced.

### The Zero-Scaffolding Constraint

During a mastery verification moment, the AI's behavioral rules change. It may only ask questions. It may not explain, scaffold, hint, or close the gap. It can probe and push back, but it cannot produce the understanding for the learner. This is the same three-dimensional rubric (reconstruction, application, boundary awareness) applied with scaffolding proximity set to zero. What the learner produces under this constraint is mastery-grade evidence.

The AI's tonal shift does the work of signaling the mode change. The constraint is legible through the AI's behavior — it becomes deliberately less helpful, more demanding — without the system ever labeling the moment. A subtle UI signal (a shift in background tone or header treatment) may reinforce this, but should be understated enough that a first-time user might not consciously notice it.

### Four Mechanisms That Create Genuine Struggle

**Socratic refusal.** The AI stops teaching entirely and only asks questions. The learner has to generate the understanding, not receive it.

**Time-delayed recall.** The mastery verification happens steps — and therefore days or weeks — downstream from the original teaching. What the learner can reconstruct at that distance is different in kind from what they can paraphrase while the session is still warm.

**Novel application.** The AI presents a context the learner has never seen and asks them to apply the concept there. This cannot be echoed. It must be used.

**Targeted exposure of weak points.** The learner model knows where the learner is shaky. The verification should probe exactly those points.

### After Mastery Verification

After a successful verification, mastery glow activates on the globe and cross-domain tendrils become visible. The AI's tone is recognition, not congratulation — it treats the user as someone who accomplished something real, not someone who needs a gold star. A brief note of what mastery of this concept opens up (new connections, new territory) serves as the reward. The reward is intrinsic to the system: new territory unlocked, not a badge earned.

After an unsuccessful verification, the AI continues teaching. It does not announce failure. The concept remains at proficiency and the system will organically create another verification opportunity further downstream.

Proficiency is quiet. Mastery is a moment.

## Key Pedagogical Principles

- Never enumerate what the author is doing. Instead, lead the learner to see it.
- Use analogies to things the learner already understands.
- When the learner is wrong, show where the reading went off track — don't just say "wrong."
- The outline prevents drift into locally salient tangents. It says "we're tracking this argument like this."
- The outline must account for dialectical texts that undermine their own earlier framing on purpose (e.g., Hegel).

---
*Last updated: 2026-04-09 (rigor score continuous; learner-relative assessment principle added)*
