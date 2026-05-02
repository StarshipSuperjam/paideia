# ADR 0028 — Input-side scope is structural, not prompt-policed

- **Status:** Accepted
- **Date:** 2026-04-29 (S-0016 sweep updated three residual globe-as-home-screen / globe-view references to the Discovery / Planning / Engagement triad)
- **Deciders:** S-0008 (exploration carried into the build session — sibling commitment to ADR 0027 rendering policy); S-0016 sweep updated stale UI-surface references per [ADR 0033](0033-mission-realignment-structured-guidance-for-self-learners.md) and [ADR 0034](0034-discovery-planning-engagement-triad.md). The structural input-scope commitment is unchanged; only the named navigation surfaces shift.

## Context

The naive answer to "how do you keep a teaching system from being used as a general assistant?" is to expose a chat input and ask the model in its system prompt to refuse off-topic requests. This is the wrong answer for Paideia for three reasons that compound.

**Prompt-level guardrails are leaky in both directions.** Asking a model to police user intent requires it to discriminate "this is a learning move" from "this is a redirect to a different task." The discrimination is contextual, judgment-laden, and the model gets it wrong both ways: refusing legitimate questions because they sound off-topic, accepting drift because it sounds engaged. Anthropic and others have published extensively on this; the failure mode is well-documented and not solvable by prompt iteration alone.

**Stay-on-topic prompts over-reject Mode 3.** The expression contract in [`docs/pedagogy.md`](../docs/pedagogy.md) explicitly invites the learner to "draw a connection" or "propose an interpretation" in Mode 3 (testing interpretation). [`docs/session-lifecycle.md`](../docs/session-lifecycle.md) elaborates: Mode 3 signals include "the learner makes a claim about what the text means," "the learner draws a connection." A learner studying Kantian autonomy who says "this is just like when my employer makes me work unpaid overtime" is doing exactly the work the system is designed to reward. A "stay on the concept" prompt would refuse this — the literal subject moved from philosophy to labor relations — even though the learner's purpose has not moved. The discipline the system needs is "stay on the *learning*," not "stay on the concept." That discipline is too subtle to prompt-encode robustly.

**Drift is gradual and unmonitored when the surface is open-ended.** A chat surface invites the user to discover that typing anything produces a response. Even without a single bad-actor moment, the equilibrium of long-term use is gradual expansion: a learner asks one off-topic question that gets answered, then another, then the system has become a general assistant by the slow road. The architecture wins or loses this on the first design choice — once the surface is open, no amount of prompt tightening reverses the equilibrium.

The forcing function is Phase 9 UI design. The Discovery / Planning / Engagement triad committed by [ADR 0034](0034-discovery-planning-engagement-triad.md) (per [`docs/ui-architecture.md`](../docs/ui-architecture.md) and [`docs/session-lifecycle.md`](../docs/session-lifecycle.md)) commits to a structured navigation surface composed of three primary surfaces with one-to-one correspondence to the structured-guidance-gap problems. What [`docs/session-lifecycle.md`](../docs/session-lifecycle.md) does not yet name explicitly is the *input-side* counterpart to that structure: the user has no chat input outside of bounded teaching contexts. Settling this before the UI prototype begins (Phase 9) prevents the chat-surface failure mode from being designed in by accident. *(Note: the original 2026-04-29 form of this paragraph referenced the globe-as-home-screen + concept-engagement-as-atomic-unit pair from the prior contract; updated at S-0016 to the triad per [ADR 0034](0034-discovery-planning-engagement-triad.md).)*

A complementary forcing function is [ADR 0027](0027-rendering-policy-prompt-layer-contract.md), which lands in the same session. [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) is the *output-side* prompt-layer contract for what tokens the agent emits. This ADR is the *input-side* structural contract for what surface the user has to emit through. The two together form the bidirectional contract for the teaching surface.

## Decision

**Input-side scope is structural, not prompt-policed.** The system does not expose a general chat input. Free-form input is available only inside bounded contexts where a clear pedagogical purpose already holds, and within those contexts the agent interprets input relative to the context, not by policing whether the input is "on topic."

Three bounded input contexts exist (V1):

1. **Concept engagement (Mode 2/3).** The atomic unit of teaching per [`docs/session-lifecycle.md`](../docs/session-lifecycle.md). The learner has entered a concept and is working through it. Free-form input arrives within an active concept-engagement thread. The agent classifies the input under the three teaching modes per [`docs/pedagogy.md`](../docs/pedagogy.md) and responds within the mode.
2. **Diagnostic conversation.** The cold-start probe per [`docs/pedagogy.md`](../docs/pedagogy.md) (Cold Start / Initial Calibration). Free-form input arrives in response to the agent's targeted prerequisite probes. The diagnostic context bounds the input semantically — the learner is answering a probe, not initiating a topic.
3. **Bring-your-own-book close reading.** Per [ADR 0011](0011-no-hosted-copyrighted-material.md). Free-form input arrives within a close-reading session against a specific text the learner has uploaded. The text and the current passage bound the conversational scope.

**Within bounded contexts, the discrimination line is purpose-not-topic.** A learner's input is "on task" when its speech act is *bringing material to the learning* — a connection, an example, a question about significance, an interpretation, a struggle. A learner's input is "off task" when its speech act is *redirecting the system to a different task* — "help me write a cover letter," "schedule my flight," "write a Python script for me." The literal subject matter of the input is not the discriminator; the speech act is. A connection from Kantian autonomy to a labor-relations example is on task. A request to *use* the agent to write a labor-relations document is off task.

The agent's response to a redirected-task input is constrained by [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) (rendering policy → scope discipline section): one sentence acknowledging the surface is for the concept engagement, an offer to step out via the exit affordance, no lecturing. The agent does not refuse harshly, does not argue, does not catalog the rules.

**An exit affordance is a UI primitive.** The user has a visible, intentional way to step out of the current context and return to one of the triad's primary surfaces per [ADR 0034](0034-discovery-planning-engagement-triad.md) — Planning surface (the typical exit destination from a concept engagement; the user returns to their active syllabus set), Discovery surface (the typical exit destination from a diagnostic; the user returns to target identification), or another bounded engagement context. The affordance is labeled and reachable in one action from any teaching context. This is the structural alternative to "general chat": the user who wants to do something else takes the exit and enters a different bounded context (or leaves the app), rather than drifting the current one.

**Prompt-level off-topic refusal language is forbidden.** [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) (`AGENT_INSTRUCTIONS.md`) does not contain "refuse off-topic questions" or "stay strictly on the current concept" framing, because both formulations would over-reject the Mode 3 cross-context connections the design depends on. The agent's scope discipline is positive (engage with what is adjacent and serves the learning) and structural (decline redirected tasks via the exit affordance), not list-of-forbidden-topics.

## Consequences

- **Phase 9 UI prototype must implement the exit affordance as a first-class primitive.** A single visible control, reachable in one action from any concept engagement / diagnostic / close-reading surface, that returns the user to graph navigation. Specification belongs in [`docs/ui-architecture.md`](../docs/ui-architecture.md) at Phase 9 authoring.

- **A "general chat" feature is foreclosed without a superseding ADR.** Adding a free-form input that does not live inside a bounded context — a "ask Paideia anything" surface, a free-text help bot, a generic prompt input — requires an explicit superseding decision. This is the structural commitment that prevents the gradual-drift equilibrium.

- **The agent's scope-discipline behavior is bounded by [ADR 0027](0027-rendering-policy-prompt-layer-contract.md).** Redirected-task requests are answered with the exit-affordance pattern (one sentence + offer to step out), not with refusal lectures or list-of-rules recitations. This protects the learner experience in the rare case where a redirected request does land — the agent's response does not feel like a slap.

- **The freshman-default audience commitment ([ADR 0012](0012-freshman-defaults-autodidact-ceiling.md)) is structurally protected.** A freshman who types "wait, can you also help me with my math homework?" experiences a brief "this surface is for working through this concept; you can step out from the menu" — not a lecture about scope. The relationship survives the moment.

- **Mode 3 cross-context connections are preserved.** The discipline of "engage with what is adjacent and serves the learning" is the explicit, positive instruction. The agent does not have a forbidden-topic list that would catch labor-relations analogies to Kant or evolutionary-biology applications of Aristotelian *energeia*.

- **The discrimination line is recorded and citable.** Future feature design that touches input surfaces (a syllabus-upload chat, a close-reading question box, a search-the-graph input) inherits the purpose-not-topic test. The test is: does the input's speech act *bring material* or *redirect the task*? If the surface invites bringing material in some bounded sense, it is consistent with this ADR. If the surface invites redirection, it is a "general chat" surface and requires superseding this ADR.

- **The architectural-constraint-beats-prompt-guardrail principle is recorded as a citable commitment.** This generalizes beyond the input-scope question to the broader pattern: when a behavior matters, prefer a structural enforcement (a UI surface that doesn't expose the bad path) over a prompt enforcement (a model asked to refuse the bad path). Future design choices about safety, content-policy, and learner protection inherit this preference. It does not commit to "no prompt-level enforcement ever" — some contracts (like the rendering policy in [ADR 0027](0027-rendering-policy-prompt-layer-contract.md)) are necessarily prompt-layer; the principle says "prefer structural where structural is available."

- **No infrastructure cost.** The decision is a UI design constraint and a prompt-layer constraint (in [ADR 0027](0027-rendering-policy-prompt-layer-contract.md)). It does not require database schema, API endpoints, or new services.

- **Pairs with [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) as input-output contract.** [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) commits that output-side rendering is the prompt-layer contract: the prompt bounds what the agent emits. This ADR commits that input-side scope is the structural contract: the surface bounds what the user can ask. Together they form the bidirectional contract for the teaching surface — neither is sufficient alone.

## See also

- [ADR 0027](0027-rendering-policy-prompt-layer-contract.md) — output-side prompt-layer contract (sibling).
- [ADR 0012](0012-freshman-defaults-autodidact-ceiling.md) — audience commitment this ADR protects.
- [ADR 0014](0014-sonnet-teaches-opus-reviews.md) — teaching role this ADR scopes the input surface for.
- [ADR 0011](0011-no-hosted-copyrighted-material.md) — bring-your-own-book close-reading mode (one of the three bounded input contexts).
- [`docs/pedagogy.md`](../docs/pedagogy.md) — three teaching modes; cold-start diagnostic conversation.
- [`docs/session-lifecycle.md`](../docs/session-lifecycle.md) — concept engagement as atomic unit; mode transitions; routing after concept completion (substantially rewritten at S-0014 against the Discovery / Planning / Engagement triad per [ADR 0034](0034-discovery-planning-engagement-triad.md)).
- [ADR 0034](0034-discovery-planning-engagement-triad.md) — Discovery / Planning / Engagement triad as primary product structure; the navigation surfaces this ADR's exit affordance returns the user to.
- [`AGENT_INSTRUCTIONS.md`](../AGENT_INSTRUCTIONS.md) — scope discipline section operationalizing this ADR's purpose-not-topic discrimination.
- [`docs/ui-architecture.md`](../docs/ui-architecture.md) — Phase 9 UI prototype (exit affordance specification target).
- [`ROADMAP.md`](../ROADMAP.md) — Phase 9 UI prototype.
