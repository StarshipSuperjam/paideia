# Project health checks

> Periodic audits of the project's own machinery — the artifacts each session produces, one per cadence trigger. Per [ADR 0022](../../engine/adr/0022-periodic-project-health-checks.md). Procedure at [`engine/operations/health-check.md`](../../engine/operations/health-check.md). Producing script at [`engine/tools/health_check.py`](../../engine/tools/health_check.py).

## What lives here

One markdown file per audit, named `S-NNNN.md` after the session that produced it. The first audit is expected at S-0030 (cadence trigger fires when `last_claimed mod 30 == 0`).

Each report carries the four-section structure from [`TEMPLATE.md`](TEMPLATE.md): Fit, Gaps, Dead weight, Bloat — each with observations and corrective actions or "no action."

## How a report gets produced

The cadence trigger fires at session boot (per [`engine/operations/session-build-lifecycle.md`](../../engine/operations/session-build-lifecycle.md)). When the user accepts the audit:

1. Run `python3 engine/tools/health_check.py --session S-NNNN` from the repo root. The script reads `engine/session/archive/*.json` (per [ADR 0042](../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md), the trend canon for soft-warns), the ADR collection, ENGINE_LOG entries, tensions and ideation files, and `engine/tools/validate-history.jsonl` if present. It writes a populated report at `docs/health-checks/S-NNNN.md`.

2. Append the MemPalace-recall observation manually. The script does not query MemPalace (the MCP-only access path is not reliably reachable from a CLI script); the AI augments the Fit section with `mempalace_search` results — drawer growth, room balance, recall quality on representative recent queries.

3. Triage findings into the three response paths named in [`engine/operations/health-check.md`](../../engine/operations/health-check.md): land as a follow-on commit (small fixes), become the next session's work item in `engine/STATE.md` (large items), or become a new tension in [`product/docs/tensions.md`](../../product/docs/tensions.md) (not yet actionable).

## Cadence

Default: every 30 sessions. Configurable in `engine/session/register_state.json` as the optional key `health_check_cadence`. Re-evaluation per [`engine/operations/health-check.md`](../../engine/operations/health-check.md) cadence policy — raise when audits consistently produce no action; lower when they consistently produce large finding lists.

## Why at repo root, not under engine/ or product/

The audit covers both sides of the engine/product partition (per [ADR 0037](../../engine/adr/0037-engine-product-wall-and-changelog-rename.md)). The artifact straddles the wall — same edge case as `CLAUDE.md` and `HANDOFF.md` at root. Each report names which findings belong to which subtree.

## See also

- [ADR 0022](../../engine/adr/0022-periodic-project-health-checks.md) — the citable contract.
- [ADR 0042](../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md) — the soft-warn lifecycle the script's Fit-section reading consumes.
- [`engine/operations/health-check.md`](../../engine/operations/health-check.md) — the audit categories and response paths.
- [`engine/tools/health_check.py`](../../engine/tools/health_check.py) — the producing script.
- [`TEMPLATE.md`](TEMPLATE.md) — the report shape.
