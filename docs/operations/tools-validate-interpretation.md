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

- **Missing required top-level file** — README, LICENSE, CHANGELOG, SECURITY, STATE, ROADMAP, HANDOFF must all exist. If you're intentionally retiring one, that's an architectural decision; ADR it first.
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

### `changelog_format`

`CHANGELOG.md` missing the `[Unreleased]` section header. Always recoverable — add the header.

### `state_format`

`STATE.md` missing the "Current phase" field. Recoverable — restore the field. Indicates structural drift.

### `cross_reference_broken`

A markdown link in `docs/CROSS_REFERENCES.md` points at a `.md` file that doesn't exist. Recoverable — either the target path is wrong, or the target file was renamed/retired without updating CROSS_REFERENCES.md.

### `adr_missing_status`

An ADR file (matching `adr/NNNN-*.md`) doesn't contain a `Status:` line. Active from S-0003 onward. Recoverable — add a Status field per [`adr-authoring.md`](adr-authoring.md).

### `adr_index_inconsistent`

An ADR file in `adr/` either is not referenced from `adr/README.md`'s per-phase tables, or its `Status:` core keyword (Accepted / Superseded / Deprecated / Proposed) differs from the index's status column for that ADR. Active from S-0020 onward.

Recoverable — either add the missing index row (most common case: a new ADR was authored without the index update), or align the `Status:` field to match the index. The check normalizes around the four core status keywords; markdown-link decoration inside the status column is tolerated. False positives should refine the check rather than be papered over.

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

- **A soft-warn that recurs across multiple sessions** — indicates either a fix that keeps regressing (escalate to a structural change, not repeated patching) or a category that doesn't actually want to be zero (re-evaluate).
- **A new hard-fail in CI on a commit that passed locally** — clock skew on `validate-history.jsonl` writes is fine to ignore; everything else is a real divergence to investigate.
- **Validator runtime > 3s** — Phase 4 graph audit budget is 3s on a 100-node test seed. If the structural-only checks (Phase 0+) start exceeding ~500ms, they've grown beyond their scope.

## Telemetry

Every run appends a JSONL record to `tools/validate-history.jsonl` (gitignored — per-clone state). The health-check audit consumes this for trend analysis. See [`health-check.md`](health-check.md).

## See also

- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — where soft-warn counts get recorded.
- [`health-check.md`](health-check.md) — periodic audit consuming the JSONL telemetry.
- `tools/validate.py` — implementation.
