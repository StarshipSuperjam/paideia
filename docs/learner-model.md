# Learner Model

## Persistent Learner Model

- Stored in Supabase (managed Postgres).
- Relational structure: tracks concept mastery, cross-concept connections, and what the learner hasn't yet encountered.
- Four mastery states: **not encountered** → **exposed** (user has prior reading history or library entry — signals interest and familiarity, never mastery) → **proficiency** (user proved understanding through meaningful interaction) → **mastery** (the concept can be wielded naturally in varied contexts; mastery of a downstream concept implies mastery of its prerequisites via backward inference). Only proficiency and mastery count as having understood a concept. Prior reading history and library contents set "exposed" status only. Mastery of a concept triggers backward inference through prerequisite edges. No forward inference ever. *(Revised: 2026-04-07)*
- **Initial population:** Three sources feed the empty model on first use. A diagnostic conversation probes prerequisite familiarity before path generation — the user's responses can set concepts to "exposed" or "proficiency" depending on depth. Optional library/reading-history import sets concepts to "exposed" only. Passive inference from engagement during the first session detects mastery from the sophistication of the user's questions. Full mechanism described in pedagogy.md under "Cold Start / Initial Calibration." *(Added: 2026-04-07)*
- Gives the AI a forward-looking teaching plan, not just a backward-looking record.
- Tracks across domains — a concept mastered in philosophy can scaffold learning in a related field.
- Planned: confidence weights on edges (hard requirement vs. helpful context).
- Planned: users self-report prior exposure to topics. Self-report sets "exposed" status only — never "demonstrated" or "mastered." The system uses exposure to adjust teaching mode (warmer entry, not a skip), then verifies understanding through interaction before advancing mastery state.

## Event-Sourced Architecture
**Added: 2026-04-07**

The learner model is event-sourced, not state-based. The source of truth is a log of interaction events — each recording what concept was engaged, at what depth, in what context, and when. Mastery states (not encountered / exposed / proficiency / mastery) are derived from this event history at query time, not stored as mutable columns.

This decision is forced by five requirements that a state table cannot serve: mastery decay over time (requires timestamps and engagement depth per event), false mastery detection (requires comparing current performance against earlier evidence), path efficiency tracking (requires knowing which path the user was on when they engaged a concept), source effectiveness (requires linking engagement events to the source material used), and cross-domain bridge discovery (requires logging freeform connections back to graph nodes). A mutable `mastery_level` column on a `user_concepts` table would be simpler to query but would foreclose all five.

Each event carries at minimum: user ID, concept node ID, timestamp, interaction type (direct teaching, assessment, callback reference, incidental mention, cross-domain connection), engagement depth (see below), the context in which it occurred (which learning path, which source text, which session), and a **graph_version counter** (see architecture.md, Node Versioning).

Mastery is computed by aggregating events for a given user-concept pair, applying temporal decay (see below), and returning a score that maps onto the four mastery states.

## Engagement Depth
**Added: 2026-04-07 | Revised: 2026-04-29 (S-0004 — aggregation settled per ADR 0023, storage shape per ADR 0024)**

Engagement depth is a composite variable derived from three sub-signals stored raw on each learner event (per ADR 0024 — sub-signals stored raw, composite derived). It determines how much the event contributes to mastery computation and how slowly it decays. Each sub-signal is on `[0, 1]` in **direct evidentiary direction** (higher = stronger evidence of depth):

**Generative ratio.** What proportion of the substantive content in the exchange was produced by the learner versus the AI? A response where the learner generates a novel explanation scores high (toward 1). A response where the learner confirms or paraphrases what the AI said scores low (toward 0). The AI estimates this per exchange.

**Scaffolding distance.** How detached the response is from recent AI scaffolding. A response produced moments after the AI's explanation has *low* scaffolding distance (low evidentiary weight). A spontaneous reference to the concept several exchanges or several concepts later has *high* scaffolding distance (high evidentiary weight). During mastery verification moments, the zero-scaffolding constraint locks `scaffolding_distance` at 1.0 — the maximum evidentiary weight. (This variable was named `scaffolding_proximity` pre-S-0004 with the inverse value/evidentiary direction; ADR 0023 renames it for direct composition into the formula. The pedagogical concept is unchanged.)

**Novelty.** Did the learner apply the concept to something not present in the conversation? A cross-domain connection the AI didn't set up, an example the learner generated independently, or an objection the learner raised that the AI hadn't introduced — all score high on novelty (toward 1). Restating the concept in the terms the conversation already established scores low (toward 0).

### Aggregation
**Added: 2026-04-29 (S-0004 — per ADR 0023)**

The composite is a **floored weighted geometric mean**:

```
engagement_depth = max(
  0.05,
  scaffolding_distance^0.5 · generative_ratio^0.3 · novelty^0.2
)
```

The geometric form treats sub-signals as **complements** (a low signal pulls the composite down sharply) rather than substitutes (a high signal compensating for low ones). This is the design intent: a chatty paraphrase produced just-scaffolded should not read as deep mastery, even with a high generative ratio. The 0.5 weight on `scaffolding_distance` reflects ADR 0010's "scaffolding-proximity discount is the single most important calibration." The 0.05 floor prevents zero-collapse — without it, a sub-signal at 0 would zero out both `raw_strength` and `half_life` simultaneously, producing infinite decay rate.

Weights and floor are V1 defaults. Tuning is application-layer only; no schema migration required (per ADR 0024).

### Fixed engagement_depth for non-composite interaction types

Two interaction types bypass the composite (per ADR 0023):

- `backward_inference`: **fixed `engagement_depth = 0.5`**. Synthetic event; no learner exchange. The interaction-type weight already rigor-attenuates (`0.4 · (1 − rigor_score)`); composite would double-attenuate.
- `incidental_mention`: **fixed `engagement_depth = 0.3`**. Concept appeared but learner didn't engage. If the learner *did* engage, classify as `direct_teaching` or `callback_reference` instead.

For these events, the three sub-signal columns are NULL on the event row; the application layer substitutes the fixed value at compute time. NULL sub-signals on a composite-applicable interaction type are a data error.

## Interaction Types
**Added: 2026-04-07 | Revised: 2026-04-09**

The `interaction_type` field on learner events distinguishes the context in which the concept was engaged. This matters because different interaction types carry different evidentiary weight and feed different system behaviors.

**direct_teaching** — The concept was the focus of a concept engagement. The AI was actively teaching it. This is the primary event type during initial learning.

**assessment** — The concept was evaluated under the zero-scaffolding constraint during a mastery verification moment. These events carry full evidentiary weight: `scaffolding_distance` is locked at 1.0 by the zero-scaffolding constraint.

**callback_reference** — The concept was referenced by the AI while teaching a downstream concept. The learner engaged with the reference (not just acknowledged it). These events have moderate engagement depth and serve double duty: they are reinforcing encounters that suppress decay, and they are probes that feed mastery verification readiness.

**incidental_mention** — The concept appeared in conversation but was not the focus. The learner may have mentioned it in passing or the AI referenced it without probing. Low engagement depth. Provides weak decay suppression but little mastery evidence.

**cross_domain_connection** — The learner connected this concept to something in a different domain without the AI prompting the connection. High novelty, high scaffolding distance. These events are both strong mastery evidence and candidate signals for the cross-domain bridge discovery feedback loop.

**backward_inference** — A synthetic event generated on a concept's immediate prerequisites when the concept itself is verified at mastery. Not produced by a teaching interaction — the system generates it automatically. The event's raw strength is modulated by the prerequisite's rigor score: low-rigor prerequisites receive high-strength inference events (simple concepts are hard to route around), high-rigor prerequisites receive low-strength events (complex concepts may have been only partially engaged by the downstream work). These events enter the standard mastery computation and are defeasible — contradictory direct evidence from later interactions naturally outweighs them through the aggregation function. Backward inference propagates through immediate prerequisites only, not the full transitive closure; natural attenuation through rigor-score modulation prevents cascading inference from reaching concepts the learner may not actually own.

## Mastery Decay
**Added: 2026-04-07 | Revised: 2026-04-09**

Mastery degrades over time without reinforcing encounters. A concept understood deeply six months ago and never revisited is not the same as one used last week. The system must model this.

Decay is a property of individual evidence events, not a single timestamp on the learner-concept relationship. Each event has a strength (derived from engagement depth) and a timestamp. When computing current mastery, older events contribute less than recent ones, and shallow engagements decay faster than deep ones. This mirrors how memory actually works — deeper encoding resists forgetting longer.

**Decay model: exponential with rigor-modulated parameters.** Each event's contribution decays as `strength * e^(-λt)` where λ (the decay rate) is modulated by both engagement depth and the concept's rigor score. The event log stores raw interaction data; the application layer applies the decay formula. This means the decay parameters can be tuned without recomputing or migrating stored data — only the computation layer changes.

**Rigor-score-modulated half-life.** Low-rigor concepts (structurally foundational, simple to hold) decay slowly. High-rigor concepts (internally complex, fragile without active use) decay faster. The half-life of any individual event is `base_half_life * engagement_depth_modifier * (1 / (0.5 + rigor_score))`. This produces the correct phenomenology: Cartesian dualism (rigor ~0.15) decays very slowly; transcendental idealism (rigor ~0.85) decays much faster — matching the observation that simple concepts persist once grasped while complex concepts require active maintenance.

**Decay floor.** Low-rigor concepts cannot decay below a floor. Once a concept has reached proficiency (the historical aggregate has crossed the proficiency threshold at least once), the floor activates: `decay_floor = max_floor * (1 - rigor_score)`. A concept with rigor 0.15 floors around 0.51 — it can lose immediacy but cannot fall below solid proficiency. A concept with rigor 0.85 floors near 0.09 — it can decay almost fully. A concept that was only ever "exposed" (never reached proficiency) receives no floor protection. This prevents the system from telling an active learner they've lost mastery of a genuinely simple concept they clearly still own, while allowing complex concepts to decay when genuinely abandoned.

### Active-Use Decay Suppression

Decay must not punish active users. A learner working steadily through a syllabus generates a continuous stream of callback reference and incidental mention events for upstream concepts. These events suppress decay on those concepts — not because the system ran a scheduled review, but because the learner is genuinely using the ideas as they move downstream.

This means decay only bites when a concept genuinely goes cold: no references, no callbacks, no downstream engagement touching it for an extended period. A user who studied Aristotle's ethics six months ago and hasn't touched anything related since — that is the case decay is designed for. A fervent user actively building on prior concepts should never experience the app as a maintenance sink where they're constantly refreshing ideas they clearly still own.

The design principle: **recovery from decay should feel like an appreciated reminder, never a pedantic chore.** When the AI re-engages a decayed concept, its tone should be reconnection — revisiting a place you haven't been in a while — not remediation. "It's been a while since we talked about eudaimonia, and it's going to matter for what we're heading into. Let me ask you something..." Not a quiz. A reorientation that respects the learner's prior engagement while checking whether the foundation is still there.

### Reinforcing Encounters

A reinforcing encounter is any interaction that touches the concept: direct teaching, assessment, callback reference, spontaneous cross-domain connection, or application in a novel context. The system must map freeform interactions back to graph nodes, which means every conversation with the AI teacher potentially resets or extends the decay clock on multiple concepts simultaneously. Different interaction types provide different reinforcement strength — a deep assessment event provides stronger reinforcement than an incidental mention — and the event log captures this distinction through engagement depth.

At current scale (n=1-3 users), live computation against the event log is fast enough that no caching or materialized mastery scores are needed. The performance optimization layer (materialized views, periodic refresh) should be deferred until user count demands it.

## Mastery Computation
**Added: 2026-04-09**

The mastery computation function takes all events for a user-concept pair and returns a score mapped to one of the four discrete mastery states. The function has four stages.

**Stage 1: Per-event decayed strength.** Each event has a raw strength derived from its interaction type base weight and engagement depth: `raw_strength = type_base_weight * engagement_depth`. The interaction type base weights encode the evidentiary hierarchy (assessment > cross_domain_connection > direct_teaching > callback_reference > backward_inference > incidental_mention). This raw strength then decays: `decayed_strength = raw_strength * e^(-λt)` where λ is modulated by the concept's rigor score and the event's engagement depth. Deep engagements on low-rigor concepts decay extremely slowly; shallow engagements on high-rigor concepts decay fast.

**Stage 2: Asymptotic aggregation.** Sum the decayed strengths, but through a concave function that prevents quantity from substituting for quality: `aggregate = ceiling * (1 - e^(-sum / ceiling))` where ceiling = 1.0. This ensures that fifty shallow mentions cannot outweigh three deep assessments. The aggregate asymptotically approaches 1.0 but cannot reach it through volume alone — only high-quality evidence pushes the score into the upper range.

**Stage 3: Decay floor.** Apply the conditional floor: `final_score = max(aggregate, decay_floor)` where `decay_floor = max_floor * (1 - rigor_score)` — but only if the concept's historical maximum aggregate has ever reached the proficiency threshold (0.3). If the concept has never been understood, no floor applies. The historical maximum aggregate is the asymptotic cap on cumulative undecayed raw strength over **substantive** interaction types (per ADR 0025 — see "Historical maximum tracking" below).

**Stage 4: State mapping.** Fixed thresholds map the continuous score to discrete states:
- **Not encountered:** score = 0 (no events exist)
- **Exposed:** 0 < score < 0.3 (events exist but evidence is thin — self-report, library import, shallow mentions, heavily decayed old evidence)
- **Proficiency:** 0.3 ≤ score < 0.7
- **Mastery:** score ≥ 0.7

These thresholds are fixed, not adaptive. The rigor score does its work upstream of the thresholds: it modulates the AI's assessment behavior (determining how hard the AI probes before logging high-engagement events), the decay rate (determining how quickly evidence weakens), and the decay floor (determining how far a concept can fall). Making the thresholds also rigor-dependent would double-count the parameter and make tuning intractable.

**Pseudocode:**
```
function compute_engagement_depth(event):
  // Fixed values for non-composite interaction types (per ADR 0023)
  if event.type == backward_inference: return 0.5
  if event.type == incidental_mention: return 0.3

  // Composite: floored weighted geometric mean (per ADR 0023)
  // Sub-signals stored raw on the event (per ADR 0024)
  return max(
    0.05,
    event.scaffolding_distance^0.5
    * event.generative_ratio^0.3
    * event.novelty^0.2
  )

function compute_mastery(events, rigor_score):
  if events is empty: return (0.0, NOT_ENCOUNTERED)

  type_weights = {
    assessment: 1.0,
    cross_domain_connection: 0.9,
    direct_teaching: 0.7,
    callback_reference: 0.5,
    backward_inference: 0.4 * (1 - rigor_score),  // attenuated by rigor
    incidental_mention: 0.2
  }

  // Substantive interaction types contribute to cumulative_substantive_raw
  // (per ADR 0025). incidental_mention and backward_inference are excluded —
  // neither represents "learner once genuinely engaged" evidence.
  substantive_types = { direct_teaching, callback_reference,
                        cross_domain_connection, assessment }

  sum = 0
  cumulative_substantive_raw = 0
  for event in events:
    depth = compute_engagement_depth(event)
    raw = type_weights[event.type] * depth
    if event.type in substantive_types:
      cumulative_substantive_raw += raw
    half_life = BASE_HALF_LIFE * depth * (1 / (0.5 + rigor_score))
    lambda = ln(2) / half_life
    decayed = raw * exp(-lambda * time_since(event.timestamp))
    sum += decayed

  aggregate = 1.0 * (1 - exp(-sum / 1.0))
  max_historical = 1.0 * (1 - exp(-cumulative_substantive_raw / 1.0))  // per ADR 0025

  floor = 0
  if max_historical >= 0.3:  // ever reached proficiency (per ADR 0025)
    floor = MAX_FLOOR * (1 - rigor_score)

  final = max(aggregate, floor)

  if final == 0: return (final, NOT_ENCOUNTERED)
  if final < 0.3: return (final, EXPOSED)
  if final < 0.7: return (final, PROFICIENCY)
  return (final, MASTERY)
```

**V1 parameter defaults** (tunable without schema changes per ADR 0024): `BASE_HALF_LIFE = 60 days`, `MAX_FLOOR = 0.6`. At these defaults, a deep `assessment` event on a low-rigor concept (rigor 0.15, `engagement_depth ≈ 0.95`) has a half-life of ~88 days and a floor of ~0.51. An `incidental_mention` event (`engagement_depth = 0.3` fixed) on a high-rigor concept (rigor 0.85) has a half-life of ~13 days and a floor of ~0.09.

**Verified at S-0005 (2026-04-29)** against five realistic trajectory scenarios (active low-rigor, active high-rigor, abandoned mid-rigor, mastery verification, backward inference) using the engagement-depth distribution settled in ADR 0023. All scenarios match design intent; no parameter revisions warranted. See the S-0005 entry in `ENGINE_LOG.md` for the verification summary. Notes from the run: a single `direct_teaching` event at `engagement_depth = 0.6` on a low-rigor concept already crosses the 0.3 proficiency threshold (aggregate 0.343) and activates the floor — consistent with the design ("simple concepts stick once grasped") but more permissive than a colloquial reading might suggest. Mastery on high-rigor concepts is unreachable through `callback_reference` events alone at typical depth (~0.4); it requires an `assessment` event or sustained callbacks at depth ≥ 0.5 — also matching design intent (high-rigor demands verified understanding, not passive reinforcement). The mid-rigor floor (0.30) sits exactly at the proficiency threshold, so an abandoned mid-rigor concept stays technically `PROFICIENCY` by the inclusive `≥ 0.3` boundary; the continuous score, not the discrete state, is the signal of fading.

**Historical maximum tracking.** The decay floor's proficiency precondition is tracked via a `max_historical_score` column (`NUMERIC(3,2) NOT NULL DEFAULT 0`) on the existing `mastery_snapshots` table (per ADR 0025). The historical maximum aggregate is the asymptotic cap on the cumulative undecayed raw strength of **substantive** interaction types: `max_historical_score = 1 − exp(−Σ_e raw_strength(e) / 1.0)` where the sum runs over events `e` with `e.interaction_type ∈ {direct_teaching, callback_reference, cross_domain_connection, assessment}`. `incidental_mention` and `backward_inference` are excluded — neither represents the "learner once genuinely engaged" evidence the floor is intended to protect, and the substantive set matches the interaction types where the engagement-depth composite applies (per ADR 0023). The value is monotonically non-decreasing under event ingest; the closed-form incremental update is `max_new = 1 − (1 − max_old) · exp(−raw_new)` for substantive events, `max_new = max_old` otherwise. Offline-sync clients receive `max_historical_score` in the cached snapshot and derive `floor_active = max_historical_score ≥ 0.3` locally (per ADR 0015's no-client-side-mastery-computation principle).

## Offline and Sync
**Added: 2026-04-09**

Mastery computation runs server-side. Native clients are thin: they emit events and consume mastery snapshots. This split exists because the mastery computation function will change — the decay parameters, floor constants, aggregation ceiling, and backward inference modulation are all tunable, and pushing parameter changes to a server is a deploy while pushing them to native apps is an App Store review cycle.

**Offline behavior.** The client queues events locally during a disconnected session using append-only local storage. It holds a cached mastery snapshot from the last sync — stale but usable for routing decisions (which concept to teach next, what the Planning surface displays per [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md)). The teaching AI does not need real-time mastery scores during a session; it needs the learner's state at session start (available from cache) and the events generated within the current session (available locally).

**Reconnection.** When connectivity returns, the client flushes queued events to the server. The server recomputes mastery for all affected concepts (those touched by the new events plus their immediate prerequisites, for backward inference). The updated mastery snapshot is pushed back to the client.

**Mid-session routing without connectivity.** If a learner completes a concept engagement offline and the app needs to route them to the next concept, the client uses the cached mastery snapshot plus locally queued events to make an approximate routing decision. The approximation may occasionally be suboptimal (a prerequisite might have tipped to mastery and unlocked a shortcut that the client doesn't know about), but the cost is a slightly longer path, not a broken experience. The server reconciles on reconnect.

**No client-side mastery computation.** The client never runs the mastery function. This eliminates versioning headaches (different client builds computing differently), prevents client-server disagreement on mastery state, and keeps the native app's logic minimal. The client is an event emitter and a snapshot consumer; the server is the source of truth.

---
*Last updated: 2026-04-29 (S-0006 — historical maximum tracking settled per ADR 0025; Stage 3 floor precondition formalized as the asymptotic cap on cumulative undecayed raw strength over substantive interaction types; pseudocode updated. Prior: S-0005 — V1 decay parameters verified; S-0004 — engagement-depth aggregation per ADR 0023; sub-signals stored raw per ADR 0024.)*
