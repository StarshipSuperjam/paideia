# ADR 0053 — Mechanism-first-exercise gate for novel cross-cutting mechanisms

- **Status:** Accepted
- **Date:** 2026-05-04
- **Deciders:** S-0055

## Context

[Issue #12](https://github.com/StarshipSuperjam/paideia/issues/12) was filed by the S-0052 health-check audit (Finding A in `docs/health-checks/S-0052.md`). The case study: the routine-mode session pattern landed at S-0044 with [ADR 0051](0051-routine-mode-and-engine-loop.md) and six layers of anti-rogue defense, all authored at production quality. Then **five sessions in succession surfaced and closed routine-mode infrastructure gaps**, each filed as an Issue with `priority:urgent`:

| Slot | Issue | Symptom |
|---|---|---|
| S-0048 | [#7](https://github.com/StarshipSuperjam/paideia/issues/7) | Phase 5 routines cannot execute: `SUPABASE_DB_URL` missing from interactive `.env`. |
| would-be-S-0049 | [#8](https://github.com/StarshipSuperjam/paideia/issues/8) | `.env` not propagated to worktrees by `git worktree add`; tools read `os.environ.get` directly. |
| S-0050 | [#9](https://github.com/StarshipSuperjam/paideia/issues/9) | `check_target.py` queried `WHERE version = %s` but the auto_target.json `id` is the migration name. |
| S-0051 | [#10](https://github.com/StarshipSuperjam/paideia/issues/10) | Boot-time has no worktree-staleness check; AI sees stale shared-state files and proceeds on stale truth. |
| S-0055 | [#15](https://github.com/StarshipSuperjam/paideia/issues/15) | Routine boot doesn't mechanically act on the staleness warning; reads stale `register_state.json` and re-claims an already-taken slot. |

The composite reading: routine-mode wasn't actually ready for unattended dispatch at S-0044, even though the ADR was authored carefully. Five real prerequisites surfaced one-at-a-time as the routine fired against real DB state and concurrent worktrees. The build-readiness gate at S-0034 (per [ADR 0040](0040-build-readiness-gate-before-substantive-build-sessions.md)) was scoped to Phase 4 graph validation; the routine-mode session pattern got no equivalent pre-flight.

This isn't negligence — each gap is the kind of thing exhaustive a-priori analysis is unlikely to surface. The honest reading is: **for novel cross-cutting mechanisms, a brief first-use pre-flight exercise — fire the mechanism once interactively against real state, observe end-to-end, close gaps — is value-positive even though the gaps would have surfaced anyway in slow motion.** The cost of S-0048 → S-0055's serialized closure was five sessions of context, five Issue authoring rounds, and five routine pauses; a single first-use pre-flight at S-0045 would likely have caught all five.

The Issue's open-question list (trigger criterion, gate structure, where deliberation lives, cost calibration) is settled below.

## Decision

A new pre-flight gate fires before a *novel cross-cutting mechanism* is used unattended for the first time. Architecturally analogous to [ADR 0040](0040-build-readiness-gate-before-substantive-build-sessions.md)'s build-readiness gate, but triggered by introduction of a new cross-cutting mechanism rather than entry into a new build phase.

### Trigger criterion (resolves Issue #12 sub-question 1)

A mechanism qualifies as "novel cross-cutting" — and therefore requires a pre-flight gate session before unattended use — if it satisfies **any** of the following (disjunctive; one trigger suffices):

1. **Introduces a new session mode.** `build` / `exploration` / `routine` were the prior set; a fourth mode would qualify.
2. **Introduces a new validator soft-warn category** that depends on session-side discipline (i.e., the AI is responsible for resolving or annotating the warn). Discipline-dependent warns require validation that the discipline actually works against real session shape.
3. **Introduces a new state file the boot procedure reads** (joining `register_state.json`, `current.json`, `auto_target.json`, etc.).
4. **The authoring ADR's Consequences list spans ≥ 3 ops docs OR ≥ 5 tooling files.** A mechanism that touches that many surfaces is cross-cutting by reach, even if it doesn't satisfy 1–3.

The criterion is checked at ADR authoring time. Authoring sessions for cross-cutting ADRs must explicitly evaluate the trigger criterion in the ADR's own "Consequences" section — either declaring "qualifies; gate session needed before unattended use" with the mechanism named, or "does not qualify because [criterion check]" with the negative finding stated. Silent omission is the failure mode this ADR exists to prevent.

### Gate structure (resolves sub-question 2)

One pre-flight session per qualifying mechanism. Procedure:

1. **Fire the mechanism once interactively against real state.** This is the load-bearing step — not theoretical analysis, actual end-to-end execution. The session boots the mechanism, runs its operational loop, observes what happens.
2. **Observe and instrument.** What did the mechanism actually do? Where did it pause for input vs. proceed? What state did it read at each step? What did it write? Which tools did it invoke?
3. **File Tier 1 / Tier 2 / Tier 3 findings** (same triage rubric as the build-readiness gate per [ADR 0040](0040-build-readiness-gate-before-substantive-build-sessions.md)):
   - **Tier 1 — must close before unattended use.** The mechanism cannot run without human in the loop until this is fixed (e.g., environment dependency missing, tool returns wrong answer, boot procedure doesn't act on warning).
   - **Tier 2 — settle in advance and document.** The mechanism could improvise but doing so under unattended pressure produces compound drift (e.g., scope-lock convention not exercised, lockfile timeout not yet tested, recovery path untested).
   - **Tier 3 — name as deferred forward-pointer.** Genuine future-session concern (e.g., cadence tightening implications, multi-machine coordination).
4. **Resolve Tier 1 with the user**, conversationally, before unattended use. Gate session is *not auto-mode* — it surfaces judgment calls.

### Where the deliberation lives (resolves sub-question 3)

Three places, each playing a distinct role:

- **This ADR** — the *what* and *why* (the contract the gate instantiates).
- **[`engine/operations/mechanism-first-exercise-gate.md`](../operations/mechanism-first-exercise-gate.md)** — the *how* (Layer 1 source-of-truth procedure).
- **`engine/build_readiness/<mechanism>_first_exercise.md`** — the gate report itself (per-mechanism findings + resolutions). Parallel to existing `engine/build_readiness/<phase>_*.md` reports from the build-readiness gate.

### Cost calibration (resolves sub-question 4)

The gate fires **once per qualifying mechanism**, not per-phase or per-session. The routine-mode case had 5 missed prerequisites; one mechanism with that miss rate justifies the gate. Build-readiness exercises (per ADR 0040) remain phase-triggered and distinct — that gate is for *substantive build sessions* (schema, content, code), not *cross-cutting mechanisms*. The two gates can both apply to a single phase: a Phase N may have a build-readiness gate (for the substantive work) AND, if a new mechanism lands as part of that phase, a mechanism-first-exercise gate (for the mechanism). They're orthogonal triggers.

Estimated frequency: cross-cutting mechanisms land roughly every 1–2 phases (ADR 0044 routine-mode, ADR 0045 shared-state, ADR 0049 scope-lock, ADR 0050 venv, ADR 0051 routine-mode foundation, ADR 0082 routine-boot hardening — 6 in the last ~25 sessions). Of those, 2–3 would have qualified under the trigger criterion. Amortization rate: one gate session per ~10 build sessions. Acceptable.

## Consequences

**Positive:**
- Cross-cutting mechanisms get a structured first-use pre-flight before they're trusted unattended.
- The S-0048 → S-0055 serialized-Issue pattern is structurally avoidable for future mechanisms.
- Authoring sessions for cross-cutting ADRs are now required to evaluate the trigger criterion explicitly, which itself surfaces the question at authoring time.

**Cost:**
- One additional gate session per qualifying mechanism. ~1 session amortized per ~10 build sessions.
- Authoring overhead in the cross-cutting ADR template (the trigger-criterion evaluation block).
- The trigger criterion is judgment-dependent. The disjunctive form is intended to bias toward "trigger when in doubt" since the cost of a mistaken trigger (one extra gate session) is much smaller than the cost of a missed trigger (the S-0048 → S-0055 pattern).

**Out of scope:**
- **Back-port to existing cross-cutting ADRs** (ADR 0037, 0043, 0045, 0049, 0050, 0051, 0082). The trigger criterion applies to *new* ADRs only. Back-port lands on next-touch (when an existing ADR is amended, the amendment session adds the trigger-criterion evaluation block). No retroactive sweep.
- **Mechanism deprecation gate.** This ADR addresses adoption only. Removing or replacing a cross-cutting mechanism is a different shape of risk and gets its own future treatment if needed.
- **Gate report archive policy.** Reports live at `engine/build_readiness/<mechanism>_first_exercise.md` and persist; no rotation or archival logic. The reports are the canonical record of what was checked and decided.

## Cross-references

- [Issue #12](https://github.com/StarshipSuperjam/paideia/issues/12) — the open question this ADR resolves.
- [ADR 0040](0040-build-readiness-gate-before-substantive-build-sessions.md) — the architectural precursor (phase-triggered build-readiness gate).
- [ADR 0051](0051-routine-mode-and-engine-loop.md), [ADR 0082](0082-routine-boot-freshness-and-concurrency-defense.md) — the case study (routine-mode + corrected diagnosis).
- Issues [#7](https://github.com/StarshipSuperjam/paideia/issues/7), [#8](https://github.com/StarshipSuperjam/paideia/issues/8), [#9](https://github.com/StarshipSuperjam/paideia/issues/9), [#10](https://github.com/StarshipSuperjam/paideia/issues/10), [#15](https://github.com/StarshipSuperjam/paideia/issues/15) — the five routine-mode infrastructure gaps the case study draws from.
- `docs/health-checks/S-0052.md` Finding A — the audit finding that surfaced this question.
- [`engine/operations/mechanism-first-exercise-gate.md`](../operations/mechanism-first-exercise-gate.md) — Layer 1 procedure doc.
