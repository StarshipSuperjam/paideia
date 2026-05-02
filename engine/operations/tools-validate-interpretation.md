# Interpreting `tools/validate.py` output

> The validator is the project's structural conscience. It runs in the pre-commit hook on every commit and on demand. This file documents what each output category means and the response posture for each.

## Exit codes

| Exit | Meaning | Response |
|---|---|---|
| `0` | Clean — no hard-fails, no soft-warns | Proceed. |
| `1` | Soft-warns only — no hard-fails | Allowed by hook (configurable via env), but every soft-warn must be acknowledged in `outcome_summary` at session close. |
| `2` | At least one hard-fail | Blocking. Pre-commit hook rejects the commit. Fix and retry. |

## Hard-fails (always blocking)

Hard-fails are structural mistakes that, if committed, would degrade the project's machinery. Always fix before the commit lands.

Categories:

- **Missing required top-level file** — README, LICENSE, ENGINE_LOG, SECURITY, STATE, ROADMAP, HANDOFF must all exist. If you're intentionally retiring one, that's an architectural decision; ADR it first. (`ENGINE_LOG.md` was named `CHANGELOG.md` before [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md); the `CHANGELOG.md` filename is now reserved for the future learner-visible product release log.)
- **`session/register_state.json` missing or malformed** — required keys: `next_id`, `last_claimed`, `current_status`. Format must parse as JSON.
- **`session/current.json` missing keys** — when present (during an in-progress session), must have `id`, `started_at`, `status`, `working_on`. `id` must match `^S-\d{4}$`.
- **Graph-audit hard-fails** (Phase 4+, currently stubbed) — duplicate node IDs, dangling edges, prerequisite cycles. See ADR 0016 for the full Phase 4 contract.

If a hard-fail blocks a commit and the fix is non-obvious, escalate per [`escalation-criteria.md`](escalation-criteria.md). Don't bypass the hook (`--no-verify`) — investigate the root cause.

## Soft-warns (signal, not blocker)

Soft-warns indicate slipping discipline or expected gaps. Each one rolls up into a category count recorded in `outcome_summary` at session close. Trend analysis (per [`health-check.md`](health-check.md)) consumes the per-category counts to detect drift.

Categories and meaning:

### `expected_future_file_missing`

A file expected to exist in a future session (per `EXPECTED_FROM_S0002` in `validate.py`) hasn't been authored yet. Expected during the session that's *about to* author it; should drop to zero after that session closes.

Example: during S-0001 the warns for `CLAUDE.md`, `docs/MISSION.md`, `docs/CROSS_REFERENCES.md`, `docs/operations/README.md` are expected. After S-0002 closes, all four should resolve.

If still warning after the session that was supposed to author the file: investigate. Either the file got missed or the file's authored but at a different path than expected.

### `engine_log_format`

`ENGINE_LOG.md` missing the `[Unreleased]` section header. Always recoverable — add the header. (Named `changelog_format` before [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md) renamed `CHANGELOG.md` → `ENGINE_LOG.md`.)

### `state_format`

`STATE.md` missing the "Current phase" field. Recoverable — restore the field. Indicates structural drift.

### `cross_reference_broken`

A markdown link in `docs/CROSS_REFERENCES.md` points at a `.md` file that doesn't exist. Recoverable — either the target path is wrong, or the target file was renamed/retired without updating CROSS_REFERENCES.md.

### `adr_missing_status`

An ADR file (matching `adr/NNNN-*.md`) doesn't contain a `Status:` line. Active from S-0003 onward. Recoverable — add a Status field per [`adr-authoring.md`](adr-authoring.md).

### `adr_index_inconsistent`

An ADR file in `adr/` either is not referenced from `adr/README.md`'s per-phase tables, or its `Status:` core keyword (Accepted / Superseded / Deprecated / Proposed) differs from the index's status column for that ADR. Active from S-0020 onward.

Recoverable — either add the missing index row (most common case: a new ADR was authored without the index update), or align the `Status:` field to match the index. The check normalizes around the four core status keywords; markdown-link decoration inside the status column is tolerated. False positives should refine the check rather than be papered over.

### `superseded_adr_currency`

A doc cites an ADR whose `Status:` is now `Superseded by ADR NNNN`, and the citation does not mark itself as historical. Active from S-0029 onward per [ADR 0041](../adr/0041-cascade-analysis-discipline.md). Recoverable — re-point the citation to the new ADR, or add a `(superseded by ADR NNNN)` qualifier if the reference is intentionally historical, or rewrite the surrounding paragraph if the supersession changes substance. The check excludes `*/adr/*.md` and `engine/ENGINE_LOG.md`.

False positives: a superseded-ADR mention that legitimately reads as historical context but the surrounding 50 chars do not include "superseded" or the new ADR id. Suppress by adding the qualifier or by widening the surrounding context to include the marker.

### `adr_back_reference_orphan`

An ADR with `Status: Accepted` has zero citations from `.md` files outside `*/adr/*`. Active from S-0029 onward per [ADR 0041](../adr/0041-cascade-analysis-discipline.md). The warn names a question, not a defect: is this ADR load-bearing for future work, or is it dead weight?

Suppress with the `Orphan-OK` annotation per [`cascade-discipline.md`](cascade-discipline.md):

```markdown
- **Orphan-OK:** <reason>; revisit at <session-id-or-phase>
```

The annotation is a deferral, not a permanent exemption. The periodic health check audits the orphan-OK list.

### `adr_consequences_deliverable_audit`

An ADR's Consequences section anticipated a deliverable "around S-NNNN," that session is closed (per `engine/session/archive/`), and a deliverable file path also named in the ADR text is absent on disk. Active from S-0029 onward per [ADR 0041](../adr/0041-cascade-analysis-discipline.md). Heuristic regex: catches the literal "tools/foo.py around S-0025" shape; does not catch promises in different prose forms.

Recoverable — either land the deliverable (with closing-commit handshake per [`cascade-discipline.md`](cascade-discipline.md): cite the ADR id in the commit message), or amend the ADR's Consequences section to remove the now-obsolete promise, or document the deferral with a new expected session.

### Phase-4-specific (stubbed today)

When Phase 4 fleshes out the graph audit, additional categories appear:

- `undeclared_predicate` — edge.type not in `supabase/migrations/PREDICATE_MANIFEST.md`.
- `attribute_shape_inconsistency` — same-domain nodes with materially different attribute coverage.
- `missing_rigor_score` — `rigor_score_computed` null when topology data is sufficient.
- `render_readiness_violation` — node label contains scaffolding tokens (`service_node`, `synthetic`, `stub`).
- `synthetic_review_queue` — `confidence_level: SYNTHETIC` nodes flagged for review.
- `orphan_leaf` — zero inbound + zero outbound prerequisite edges.
- `suspicious_cross_domain_ratio` — subdomain with > 40% cross-domain inbound edges (likely missing service node).

Each Phase-4 category has a recoverable fix per ADR 0016 and the seed-chunked-authoring workflow.

## Response posture

- **A soft-warn that recurs across multiple sessions** — formalized into a discipline per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). The boot-time persistent-warn surface flags categories firing in 3-or-more of the last 5 archives; categories firing in 10 consecutive archives reach the escalation criterion (promote to hard-fail, accept and annotate, or address inline) per [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md).
- **A new hard-fail in CI on a commit that passed locally** — clock skew on `validate-history.jsonl` writes is fine to ignore; everything else is a real divergence to investigate.
- **Validator runtime > 3s** — Phase 4 graph audit budget is 3s on a 100-node test seed. If the structural-only checks (Phase 0+) start exceeding ~500ms, they've grown beyond their scope.

## Persistent-warn annotation

When the escalation criterion ([`soft-warn-lifecycle.md`](soft-warn-lifecycle.md), 10 consecutive archives) lands on "accept and annotate," the category gets an entry below explaining why the persistence is expected and what condition would resolve it. The boot surface respects the annotation by suppressing the surface for sessions that match the named condition.

*(No annotated categories yet — first annotations expected when the structured-data window matures.)*

## Telemetry

Trend canon: committed `engine/session/archive/S-NNNN.json` field `outcome_summary_soft_warns` per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). Read by `engine/tools/health_check.py` and the `/start-engine` boot procedure.

Per-invocation forensics: `engine/tools/validate-history.jsonl` (gitignored, per-clone). Useful for "when did this warn first appear" / "which commit introduced it" / "validator runtime drift."

## See also

- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — where soft-warn counts get recorded.
- [`health-check.md`](health-check.md) — periodic audit consuming the JSONL telemetry.
- `tools/validate.py` — implementation.
