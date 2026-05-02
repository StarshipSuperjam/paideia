# ADR 0022 — Periodic project health checks

- **Status:** Accepted
- **Date:** 2026-04-29
- **Deciders:** S-0001 plan conversation; formalized in S-0003

## Context

A project's machinery accumulates drift. Soft-warn categories trend upward; documentation sections grow stale; conventions diverge between what `CLAUDE.md` says and what sessions actually do; tools added for one purpose linger after that purpose ends. The accumulation is invisible turn-by-turn — no single session is responsible — but compounds across many sessions into structural debt that is expensive to repay later.

Two approaches are available. **Reactive** — fix things when they're noticed in the course of other work. This is what most projects do; it produces uneven coverage (busy areas get attention; quiet areas drift). **Periodic** — schedule explicit audit sessions whose job is to assess fit, gaps, dead weight, and bloat across the whole machinery, on a known cadence.

Periodic audits exploit two facts. First, they have a different posture than feature work — looking *for* problems rather than *at* them in passing. Second, they consume telemetry that's been quietly accumulating: `tools/validate-history.jsonl` (per-category soft-warn trends), `session/archive/S-NNNN.json` (per-session outcome summaries), ADR status field (counts of Accepted / Deprecated / Superseded over time), ENGINE_LOG entries (categorized engine changes by date), MemPalace `exploration` and `decision` tags (semantic memory of every conversation). The telemetry exists to be consumed; without a scheduled consumer, it accumulates without surfacing signal.

## Decision

The project runs **periodic health checks** at a configurable cadence (default every 30 sessions). The cadence trigger fires automatically at session boot when `last_claimed mod health_check_cadence == 0`; the user accepts (the session's work is the audit, per `docs/operations/health-check.md`) or defers (proceed with planned work; trigger fires again next time the modulus is satisfied).

Health checks are not phase-anchored. They fall wherever the modulus lands; the audit consumes whatever telemetry has accumulated since the last check.

## Consequences

- The cadence machinery is built in S-0001 (`session/register_state.json` carries `health_check_cadence`; the boot procedure computes the modulus). The health-check session itself runs from `docs/operations/health-check.md` (categories, report template).
- `tools/health_check.py` is anticipated to land around S-0025 (one of the pre-first-check sessions); the pre-first-check window allows the script to be authored against telemetry that has accumulated rather than against an empty data set. **First check expected around S-0030.**
- Audit categories (per `docs/operations/health-check.md`): soft-warn trend analysis, ADR status drift, ENGINE_LOG cadence, doc/code consistency, MemPalace coverage gaps, `tensions.md` aging, file-size and complexity heuristics.
- Defer is a first-class option. If the cadence fires during a busy phase (e.g., mid-Phase 5 seed authoring with 6+ subdomain sessions in flight), the user defers; the trigger re-fires at the next satisfied modulus. Audits are not blocking.
- The audit produces a report (template in `docs/operations/health-check.md`) and one or more ENGINE_LOG entries (`Changed`/`Removed`/`Added`) for any cleanups landed in the audit session. Findings that warrant follow-up become explicit work items in `STATE.md`.
- The cadence is **configurable**, not hardcoded. As the project matures, the right cadence may change (longer interval as machinery stabilizes; shorter interval if telemetry shows fast drift).
- Deferring health checks indefinitely is a self-inflicted cost. The cadence trigger is an interrupt, not a request — the user should accept it unless there's an active reason to defer.

## See also

- [`docs/operations/health-check.md`](../operations/health-check.md) — audit categories, report template, cadence policy.
- [`session/register_state.json`](../session/register_state.json) — `health_check_cadence` field (when present).
- [`tools/validate.py`](../tools/validate.py) — emits `tools/validate-history.jsonl` consumed by health checks.
- [`ROADMAP.md`](../../ROADMAP.md) — Recurring section: health-check telemetry hooks.
- ADR 0016 — Graph construction needs live validation (telemetry source).
- `.claude/commands/start-engine.md` — boot procedure that fires the cadence trigger.
