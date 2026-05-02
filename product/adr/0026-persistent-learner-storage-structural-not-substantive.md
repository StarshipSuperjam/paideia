# ADR 0026 — Persistent learner storage is structural, not substantive

- **Status:** Accepted
- **Date:** 2026-04-29
- **Deciders:** S-0007 (privacy-posture deliberation, originating from off-system exploration carried into a build session)

## Context

Several existing decisions collectively shape Paideia's privacy posture. ADR 0014 (Sonnet teaches, Opus reviews) commits Opus to "aggregated patterns, not individual learner data" and bounds Sonnet's per-turn context to current concept + one-hop prerequisites + two-hop entity-resolution neighborhood. ADR 0015 (event-sourced learner model) establishes the durable representation as a structured event log, not transcripts. ADR 0024 (engagement-depth sub-signals stored raw) extends that discipline to engagement signals — three numeric columns, not prose. The common pattern: persistent state is structural evidence about engagement with concepts, not substantive content of what the learner said or believes.

Two surfaces remain underspecified.

**`tension_log.exchange_summary` is `TEXT NOT NULL`** (per the schema in [`docs/self-correction.md`](../docs/self-correction.md), Tension Log Schema). Sonnet writes prose here describing tension-generating exchanges, which Opus reads during batch review. The natural operational use looks like *"learner misapplied the categorical imperative across three exchanges; direct correction did not adhere; appears to be confusion at the formula vs. the meta-ethical grounding."* The drift surface — what we want to forbid — looks like *"learner argued from Catholic doctrine that all life is sacred, refused utilitarian framings."* The first is structural pedagogy; the second is substantive belief content. The schema does not currently distinguish.

**`learner_events.context` is described informally** in [`docs/learner-model.md`](../docs/learner-model.md) (Event-Sourced Architecture) as "the context in which it occurred (which learning path, which source text, which session)" — structural references. The Phase 3 schema has not yet been authored, and the natural failure mode is for `context` to absorb a JSONB grab-bag including substantive turn-by-turn content.

A third question is invisible in the existing design docs and worth surfacing now: **conversation transcripts**. Standard chat-AI architectures persist the dialog as the system-of-record. Paideia's architecture treats events as the system-of-record, but the persistence policy for the underlying turns has not been stated. If turns are persisted to a `conversations` table (even briefly, even for session-continuity), the privacy story is undermined. The strongest defensible posture is a deliberate non-persistence commitment with a bounded operational TTL.

The forcing function is **Phase 8 Apple App Store submission**. Apple's privacy nutrition labels and privacy questionnaire are non-negotiable. The 2–4 week Apple lead time noted in [`docs/business.md`](../docs/business.md) (Account Ownership and Transfer Path) means a settled privacy posture is not "before opening to general users" in some vague sense — it is a blocking artifact for Phase 8. A well-formed schema before Phase 3 ingestion is also far cheaper than a post-deployment retrofit.

A motivating substantive risk: philosophy as the V1 domain — and the cross-domain extension into religion, ethics, political theory committed to in [`docs/MISSION.md`](../docs/MISSION.md) (cross-domain porosity) — surfaces user views on GDPR Article 9 special-category data (philosophical beliefs, religious convictions, political opinions) during normal teaching. If those views land in `exchange_summary` or `context` in substantive form, Paideia is processing special-category data and assumes the corresponding compliance burden. If only structural evidence persists, the honest answer to "does Paideia process special-category data?" becomes: it processes structural evidence of engagement with concepts that touch special categories, but does not persist substantive beliefs. That answer is defensible because it is true at the schema level, or it is false — and the schema is what makes the difference.

## Decision

**Persistent learner storage is structural, not substantive.**

The system persists structural signals about learner engagement: concept references (node IDs), interaction types, sub-signal scores (per ADR 0024), timestamps, graph_version counter, bounded structural context references (path ID, source text ID, session ID, cohort ID), and structured tension records describing pedagogical pattern-shape. The system does not persist substantive content (the learner's beliefs, doctrinal positions, political or religious views, first-person claims, quoted reasoning) in free-text form on any durable table.

This commitment has three operational sub-decisions.

**(1) `tension_log.exchange_summary` becomes structured, not free-text.** The Phase 3 schema for `tension_log` replaces `exchange_summary TEXT NOT NULL` with a JSONB column carrying a constrained shape with named fields. The required semantic fields (whether stored inside the JSONB column or hoisted to top-level columns for query efficiency):

- `teaching_moves_tried` — array of enum values from a constrained vocabulary
- `friction_type` — enum value, more granular than the existing top-level `tension_type`
- `pattern_observed` — bounded-length structural description; third-person; descriptive, not quotational
- `suggested_review_focus` — enum value or null
- `unresolved_reference` — string or null, used when `tension_type = spontaneous_connection` and the reference did not resolve to a graph node

The existing top-level columns `concept_id` and `learner_reference_node_id` already capture the source-and-target concept pair as foreign-key references; the JSONB column does not duplicate them. The constrained enum vocabularies (`teaching_moves_tried`, `friction_type`, `suggested_review_focus`) are authored alongside the Phase 3 schema migration; this ADR commits the principle, not the specific vocabulary.

`pattern_observed` is the only free-text field; it is bounded in length (target ~280 characters, hard cap ~600), constrained by Sonnet's writing policy to describe pedagogical pattern-shape (where the friction occurred, what teaching moves were tried, what the structure of the difficulty is), and explicitly forbidden from carrying first-person learner claims, contested doctrinal positions, or political/religious framings as substantive content. Sonnet's emission policy enforces this at write-time; `tools/validate.py`'s Phase 4 extension audits it on a periodic-batch cadence.

**(2) `learner_events.context` is schematized as a fixed structured shape, not a JSONB grab-bag.** The Phase 3 schema for `learner_events` declares `context` as a structured set of nullable foreign-key references and enum-typed fields: `path_id` (FK to a constrained_paths table), `source_text_id` (FK to a sources table), `session_id` (UUID, opaque), `cohort_id` (per the institutional schema provisions in [`docs/architecture.md`](../docs/architecture.md), defaults to NULL). No free-text columns. No JSONB column for "extras" — extension requires a schema migration with explicit privacy review at the same gate as this ADR.

**(3) Conversation transcripts are not persisted as system-of-record data.** Raw turn-by-turn dialog between learner and teaching agent is operational state, not a durable record. The application MAY retain in-flight turns for the duration of an active teaching session to support context continuity within that session, with retention bounded by session close. Default TTL: session-end (in-memory or session-scoped store, deleted on session close). Absolute hard cap: 24 hours from the last turn (covers session-resume across a single sleep cycle without becoming a durable transcript log). On expiry, retained turns are deleted. Cross-session continuity is supported through the structured event log and `mastery_snapshots`, not through transcript replay. Sonnet's per-turn context budget — the slice loaded into the model — may include the most recent in-session turns plus the structured learner state; it does not include cross-session transcript history.

This third sub-decision is the largest gap closed by this ADR. Existing decisions implied transcript non-persistence; this ADR makes it explicit and bounds the operational exception.

## Consequences

- **The honest answer to "does Paideia process GDPR Article 9 special-category data?" is well-formed.** It processes structural evidence of engagement with concepts that touch special categories (a learner spent six events on Kantian ethics; another spent four events on Aquinas's natural law). It does not persist substantive beliefs (what the learner thinks about Kantian vs. natural-law ethics). The schema is the proof. The privacy policy a lawyer eventually drafts at Phase 8 can rely on this distinction without it being a fiction.

- **Phase 3 SQL schema authoring is constrained accordingly.** When the `tension_log` and `learner_events` migrations land in Phase 3, they implement the JSONB-with-named-fields shape for `exchange_summary` (replacing the original `TEXT NOT NULL` shape) and the structured-columns shape for `context`. The `tension_log` schema in [`docs/self-correction.md`](../docs/self-correction.md) is updated in this session to reflect the new shape.

- **Phase 4 `tools/validate.py` gains a privacy-audit category.** A periodic-batch soft-warn extension scans `tension_log.exchange_summary.pattern_observed` for substantive-content markers: contested-doctrine proper nouns in declarative voice ("the learner argued the Trinity is..."), first-person quotational structure, political/religious framing as substantive claim. False positives are expected and acceptable — the audit surfaces candidates for human review, not auto-edit. This sits alongside the existing soft-warn categories specified in [`ROADMAP.md`](../../ROADMAP.md) Phase 4 and is wired during the Phase 4 graph-validation utility build (per ADR 0016).

- **Phase 8 App Store privacy questionnaire alignment becomes tractable.** With the persistence shape committed, the questionnaire's "what data do you collect?" answers are constrained to structural categories (engagement events, derived mastery state, structured tension records, bounded session-scoped operational state). The privacy policy a lawyer drafts at Phase 8 can be aligned with the schema rather than aspirational. ROADMAP.md Phase 8 success criteria gains a corresponding bullet in this session.

- **FERPA bolt-on path stays clean** (per ADR 0012's "freshman defaults, autodidact ceiling" commitment to deferring institutional features). Cohort-bound events under a future institutional regime can layer additional constraints on top of the structural baseline; they do not have to retroactively strip substantive content, because none was persisted in the first place.

- **Two open questions are surfaced and tracked in [`docs/tensions.md`](../docs/tensions.md)** (added in this session): OQ-PRIVACY-A (erasure mechanism — crypto-shredding vs. hard-delete-with-cascade vs. anonymize-and-aggregate; decide before Phase 3 schema authoring because the choice shapes whether `learner_events` needs an `encrypted_user_data_key` column or a nullable `user_id`); OQ-PRIVACY-B (institutional vs. individual data regime — direction-neutral; decide before Phase 3 to reserve any required columns; policy specification deferred to Phase 8 alongside actual institutional partner conversations).

- **The transcript non-persistence commitment constrains future feature design.** Features that would require persisted transcript history — full conversation-history search, cross-session quotation, transcript-based fine-tuning of a session-specific model — are foreclosed without a superseding ADR. The "internal fine-tuning from session data" mention in [`docs/business.md`](../docs/business.md) (Revenue Mechanisms Explored), already flagged as raising "privacy/consent problems," is constrained by this ADR: any fine-tuning use draws on the structured event log and structured tension records, not on raw transcripts.

- **Operational implementation freedom is preserved within the bound.** The 24-hour absolute hard cap is permissive enough for most reasonable session-resume patterns (a learner who closes the app and returns within a day) while bounding the privacy exposure. If operational reality requires longer retention for a specific feature, that requires a superseding ADR and a corresponding privacy-policy revision — a deliberate decision, not drift.

- **This commitment does not rise to the strong-working-commitments list in [`docs/MISSION.md`](../docs/MISSION.md).** That list is the audience-facing summary of pedagogical commitments — what makes Paideia different as a teaching tool. The privacy posture is architectural discipline that supports the institutional and App Store paths but does not directly shape teaching. Cross-references from [`docs/architecture.md`](../docs/architecture.md), [`docs/business.md`](../docs/business.md), and the Phase 3 / Phase 8 entries in [`ROADMAP.md`](../../ROADMAP.md) are sufficient.

- **Phase ordering note.** This ADR is a Phase 1 insertion ahead of Phase 1.2 (rendering policy, now S-0008 with ADR 0027). Phase 1.1 closed cleanly at S-0006; Phase 1.2 and 1.3 are unaffected in scope, only renumbered in session order. Phase 3 schema authoring inherits this ADR as a constraint; Phase 8 inherits the privacy-policy/questionnaire bullet as a success criterion.

## See also

- ADR 0014 — Sonnet teaches, Opus reviews (the "Opus operates on aggregated patterns, not on individual learner data" sentence this ADR extends).
- ADR 0015 — Event-sourced learner model (the storage discipline this ADR extends to substantive-vs-structural).
- ADR 0024 — Engagement-depth sub-signals stored raw (the same structural-not-substantive discipline applied at the engagement-signal layer).
- ADR 0012 — Freshman defaults, autodidact ceiling (the FERPA-deferred-as-bolt-on commitment that this ADR keeps clean).
- ADR 0011 — No hosted or distributed copyrighted material (a related but separate operational commitment; copyright governs what the system shows the learner, this ADR governs what the system stores about the learner).
- [`docs/self-correction.md`](../docs/self-correction.md) — Tension Log Schema (updated in this session to reflect the JSONB shape).
- [`docs/learner-model.md`](../docs/learner-model.md) — Event-Sourced Architecture (the `context` field schematization target for Phase 3).
- [`docs/architecture.md`](../docs/architecture.md) — Institutional Schema Provisions (the cohort-bound regime context for OQ-PRIVACY-B).
- [`docs/business.md`](../docs/business.md) — Internal fine-tuning from session data (the prior privacy/consent flag this ADR constrains); Account Ownership and Transfer Path (the data-ownership-clarity requirement this ADR partially answers).
- [`docs/tensions.md`](../docs/tensions.md) — OQ-PRIVACY-A, OQ-PRIVACY-B (added in this session).
- [`ROADMAP.md`](../../ROADMAP.md) — Phase 3 schema authoring (constrained by this ADR); Phase 8 App Store success criteria (privacy-policy bullet added in this session).
