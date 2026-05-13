# ADR 0085 — Server-side mastery computation confirmed

- **Status:** Accepted
- **Date:** 2026-05-13
- **Deciders:** S-0152

## Context

[`product/docs/tensions.md`](../docs/tensions.md) carries OQ-DEC1-A ("Server-side mastery computation — confirm or revisit?") as decide-before-Phase-6, open since 2026-04-29 (S-0001). The current architectural commitment lives in [`product/docs/learner-model.md`](../docs/learner-model.md) under "Offline and Sync" (the section explicitly states *"No client-side mastery computation"*): mastery is computed server-side; native clients are thin event emitters and snapshot consumers. The original tension framing offered two revisit motivations — "richer offline UX" and "lower API cost" — and named Phase DEC.1 (between Phase 5 and Phase 6) as the natural moment to settle.

Two of those motivations have shifted under decisions that landed after the tension was filed:

1. **The "lower API cost" motivation does not survive [ADR 0065](0065-oss-pivot-and-byok-disposition.md)'s BYOK regime (S-0128).** Under OSS+BYOK, the user's Anthropic API key lives on-device and Paideia is out of the API path entirely (per ADR 0065 commitment 5 + commitment 8). The user pays Anthropic directly; Paideia has zero per-turn API cost to optimize against. The per-turn back-end-call surface that remains (mastery snapshot fetch, two-hop neighborhood fetch, prerequisite fetch) is against Paideia's own Supabase backend, not against Anthropic — moving mastery computation to the client would shift compute cost from server (Supabase, paid by the project per ADR 0046's structural-reference posture) to device, not reduce any user-facing API spend.

2. **ADR 0065 commitment 8 already pre-committed server-side mastery under post-BYOK reality.** That commitment reads: *"Mastery computation continues server-side via structured `learner_events` derived client-side from prompt + response, consistent with the transcript-non-persistence guarantee per [ADR 0026](0026-persistent-learner-storage-structural-not-substantive.md)."* The post-S-0128 architecture already binds against the OQ-DEC1-A revisit. This ADR makes the binding explicit as the decide-before-Phase-6 resolution.

The remaining substantive question — whether "richer offline UX" justifies moving mastery to the client — is answered by the existing offline-and-sync design in `learner-model.md:196-200`: the client holds a cached mastery snapshot from the last sync and queues events locally during disconnect. This satisfies offline routing-decision use cases without client-side computation. Mid-session routing without connectivity uses the cached snapshot plus locally queued events; the server reconciles on reconnect. The offline UX is not constrained by where mastery computes — it's constrained by whether the snapshot is fresh enough at session start, which is a sync-cadence question independent of compute location.

### Load-bearing premises

*Per the [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) extraction step. This ADR triggers the step under the "supersession of a load-bearing prior decision" class — it makes OQ-DEC1-A's explicit settlement, and `learner-model.md:202`'s "No client-side mastery computation" line gains an explicit ADR contract.*

1. **The mastery formula needs parameter-tunability without App Store deploy cycles.** *Falsifier:* if Phase 6/7 reveals the formula stabilizes early (decay parameters, floor constants, aggregation ceiling, backward-inference modulation, thresholds all converge within the first three Phase-6 sessions) and rarely retunes thereafter, then App Store deploy cycles for parameter changes become acceptable. *Test status:* unverifiable in-context — depends on future Phase 6/7 empirical signal. Named in Consequences as a known assumption with a Phase-7-review fallback trigger.

2. **A single source of truth on mastery state eliminates client-server disagreement.** *Falsifier:* if a Phase 6 use case surfaces where eventual-consistency client-side recomputation produces acceptable outcomes (e.g., approximation error < 5% on routing decisions, learner cannot observe the divergence), the single-source premise weakens. *Test status:* unverifiable in-context. Named in Consequences as a known assumption.

3. **The BYOK regime under ADR 0065 forecloses "lower API cost" as a revisit motivation.** *Falsifier:* identify a per-turn back-end call that mastery-side computation could eliminate AND that produces user-facing Anthropic API spend (not Paideia Supabase compute). *Test status (run in-context S-0152):* surveyed the per-turn back-end-call surface. Three call types per turn: (a) mastery snapshot fetch (Paideia → Supabase, no Anthropic), (b) two-hop neighborhood fetch (Paideia → Supabase, no Anthropic), (c) prerequisite fetch (Paideia → Supabase, no Anthropic). None of the three would shrink as user-facing Anthropic spend if mastery moved to the client — they all hit Paideia's own infrastructure. **Premise verified.**

4. **ADR 0065 commitment 8 already binds server-side mastery under post-S-0128 reality.** *Falsifier:* the commitment 8 text would have to read differently than verified. *Test status (run in-context S-0152):* re-read [`product/docs/business.md:18`](../docs/business.md:18) and confirmed *"Mastery computation continues server-side via structured `learner_events` derived client-side from prompt + response, consistent with the transcript-non-persistence guarantee per ADR 0026."* **Premise verified.** The OQ-DEC1-A revisit was already pre-foreclosed; this ADR records the binding explicitly rather than authoring a new architectural commitment.

## Decision

Mastery computation runs server-side. The mastery computation function (per [`product/docs/learner-model.md`](../docs/learner-model.md) "Mastery Computation" section) executes against the `learner_events` log on Paideia's Supabase backend; results land in `mastery_snapshots` as derived state. Native clients are thin: they emit events and consume snapshots. The client never runs the mastery function. This makes explicit the architectural commitment already in `learner-model.md:202` ("No client-side mastery computation") and the post-BYOK reaffirmation in [ADR 0065](0065-oss-pivot-and-byok-disposition.md) commitment 8.

## Alternatives Considered

### Confirm server-side via this ADR (chosen)

- **What:** Author this ADR to make the `learner-model.md:202` commitment + ADR 0065 commitment 8 explicit as the decide-before-Phase-6 settlement of OQ-DEC1-A.
- **Pros:** Phase 6 entry proceeds against an explicit contract. Future sessions querying "is server-side mastery settled?" find a single citable ADR. The BYOK-driven shift in the revisit motivation is recorded.
- **Cons:** Records a decision that ADR 0065 commitment 8 already implicitly bound; mild redundancy with the existing surface.
- **Rejected because:** not rejected — chosen.

### Revisit toward client-side mastery

- **What:** Move the mastery computation function to the native client; clients become authoritative on mastery state; the server stores events and acts as a sync substrate but does not compute.
- **Pros:** Eliminates per-turn back-end calls for mastery (though under BYOK these aren't user-facing API costs — see premise 3 above). Marginally reduces Paideia's Supabase compute cost. Could enable richer offline UX *if* the formula were stable enough that "client computes, server reconciles" doesn't surface disagreements.
- **Cons:** Versioning complexity — formula tuning between releases would require coordinated client + server updates; mismatched client builds would compute differently against the same event log. App Store review cycle adds 1-7 days to any formula adjustment that today is a deploy. Single-source-of-truth lost; client-server disagreement on mastery becomes a possible failure mode. ADR 0065 commitment 8 would need supersession.
- **Rejected because:** the "lower API cost" motivation evaporates under BYOK (premise 3 verified); the "richer offline UX" motivation is met by the existing snapshot-cache + event-queue offline design (`learner-model.md:196-200`) without moving the computation; ADR 0065 commitment 8 already pre-foreclosed this path.

### Hybrid (client-side approximate, server-side authoritative)

- **What:** Client computes mastery approximately from the cached snapshot + locally queued events; server-side recomputation on reconnect is authoritative. The two computations may diverge mid-session.
- **Pros:** Offline routing decisions don't wait for sync. Marginally smoother UX during disconnect.
- **Cons:** This is **already what `learner-model.md:200` describes** — *"the client uses the cached mastery snapshot plus locally queued events to make an approximate routing decision."* But the approximation is *not* a client-side run of the mastery function; it's snapshot-plus-event-state extrapolation. Calling that "client-side mastery computation" muddles vocabulary without changing architecture. A true hybrid that runs the formula client-side adds the versioning and disagreement risks of pure client-side without their full benefit.
- **Rejected because:** the architecture's offline behavior is already a soft hybrid (cached snapshot + local events); promoting that to a full client-side computation run adds versioning cost without buying additional offline capability.

### Defer (leave OQ-DEC1-A open)

- **What:** Treat OQ-DEC1-A as not-yet-settled; Phase 6 entry proceeds without an explicit ADR; revisit at a later trigger.
- **Pros:** Preserves optionality if Phase 6 reveals a use case that flips the choice.
- **Cons:** OQ-DEC1-A is explicitly *decide-before-Phase-6*. Deferral past Phase 6 entry violates the constraint the tension itself imposed. The optionality is illusory — ADR 0065 commitment 8 already binds the choice; "not yet settled" is fiction.
- **Rejected because:** the tension's own decide-before-Phase-6 framing forecloses indefinite deferral; the ADR 0065 binding makes the deferral fictional.

## Consequences

- **Phase 6 entry can proceed against an explicit server-side mastery contract.** Self-correction infrastructure (per [ADR 0014](0014-sonnet-teaches-opus-reviews.md)) consumes the `learner_events` table server-side; the mastery computation function operates against it on Paideia's Supabase backend. No client-side rework required.

- **Phase 7 formula-stability review is the post-deploy verification trigger for premise 1.** If the mastery formula has retuned ≥3 times in Phase 6 across distinct sessions (decay parameters, floor constants, thresholds), the server-side commitment is empirically validated against the falsifier. If the formula stabilizes within the first three Phase 6 sessions, the falsifier surfaces and a future ADR may amend toward bundled client-side parameter packs. Recorded as a known assumption with a Phase-7-review fallback per ADR 0084's "untestable premise" guidance.

- **`product/docs/tensions.md` OQ-DEC1-A section flips from "Open" to "Resolved by ADR 0085"** in the same commit as this ADR.

- **No supersession.** [ADR 0015](0015-event-sourced-learner-model.md) (event-sourced learner model), ADR 0014 (Sonnet teaches / Opus reviews), and ADR 0065 (OSS+BYOK) all remain Accepted; ADR 0085 makes explicit the server-side-mastery commitment those ADRs already imply.

- **No cascade beyond `tensions.md` + ADR 0085's own commit.** `learner-model.md:202`'s "No client-side mastery computation" line gains a back-reference to ADR 0085 in the See-also of this ADR, but the doc text remains substantively unchanged.

- **The OQ-DEC1-A entry no longer counts against the Phase-6-blocker set in [`engine/STATE.md`](../../engine/STATE.md).** Three OQ-DEC1 entries remain (B, C, D) to settle before Phase 6 opens; this session settles them in subsequent ADRs.

- **Cost of supersession if Phase 7 review surfaces the falsifier:** modest. A future ADR amends or supersedes ADR 0066 without retrofitting Phase 6 work — the client-side rework is the substantive cost, paid only if and when the falsifier fires.

## See also

- [ADR 0014](0014-sonnet-teaches-opus-reviews.md) — Sonnet teaches, Opus reviews; consumes the event log for batch tension analysis.
- [ADR 0015](0015-event-sourced-learner-model.md) — Event-sourced learner model; mastery is derived state.
- [ADR 0025](0025-mastery-historical-maximum-tracking.md) — Mastery historical-maximum tracking; formula extension that exemplifies the kind of tuning server-side computation accommodates.
- [ADR 0026](0026-persistent-learner-storage-structural-not-substantive.md) — Persistent learner storage as structural-only; underpins the events-on-server / transcript-not-on-server split.
- [ADR 0065](0065-oss-pivot-and-byok-disposition.md) — OSS pivot + BYOK; commitment 8 pre-committed server-side mastery under post-BYOK reality.
- [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — Extraction step (first natural exercise: this ADR + 0086 + 0087 + 0088).
- [`product/docs/learner-model.md`](../docs/learner-model.md) "Offline and Sync" — original commitment now ADR-cited.
- [`product/docs/tensions.md`](../docs/tensions.md) OQ-DEC1-A — resolved by this ADR.
