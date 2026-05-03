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
- **Graph-audit hard-fails** — duplicate node IDs, dangling edge references, prerequisite cycles in the `pedagogical_prerequisite` subgraph (detected via Kosaraju SCC). Active when `SUPABASE_DB_URL` is set in the environment; absent env var records `graph_audit_skipped` and runs no DB query (non-seed-authoring sessions are not gated on DB connectivity). See [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md) for the full contract.

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

### `chromadb_palace_health`

The shared-state probe at [`engine/tools/probe_palace.py`](../tools/probe_palace.py) reported a level-1 (suspect) condition — palace path missing, no collections, or another anomaly that doesn't constitute outright corruption. Active from S-0035 onward per [ADR 0045](../adr/0045-shared-state-integrity-discipline.md). Probe runs at every `validate.py` invocation in the default check set and in the `--health-probe-only` mode used by the SessionStart hook.

The probe escalates to a **hard-fail** (not a soft-warn) when the palace is definitely broken — chromadb refuses to import, `PersistentClient` raises on open, `get_collection() / count()` raises, or the probe segfaults at SIGSEGV (the S-0034 chromadb_rust_bindings signature on a corrupt HNSW segment). Definite corruption blocks the commit so the build session must address it before proceeding; the soft-warn level is reserved for ambiguous states that don't yet warrant blocking.

Recoverable — `mempalace mine <dir>` to re-populate from source jsonl files; or move the suspect segment dir aside (`palace/<segment-uuid>.broken/`) and re-run the probe so chromadb rebuilds from SQLite-stored embeddings (the S-0034 recovery procedure).

### `health_check_overdue`

The cadence-aligned health-check audit slot has been consumed by other work and the audit slid past one full cadence. Active from S-0041 onward per [ADR 0022](../adr/0022-periodic-project-health-checks.md) Consequences amendment (overdue-catchup logic).

Fires when `(register_state.json.next_id - last_audit_session) > health_check_cadence`. The SessionStart hook (`engine/tools/hooks/session-start.sh`) surfaces both "due" (`slots_since == cadence`) and "overdue" (`slots_since > cadence`) at boot per the same amendment; this validator soft-warn is defense-in-depth so a silently-failing hook (the S-0033 / S-0034 vector pattern) cannot mask the slide. The validator stays silent at the natural-cadence slot — that case is the hook's "due" surface, not an overdue condition.

Skips quietly when `last_audit_session` is absent (legacy `register_state.json`, pre-S-0041); the `checks_run` field still records the attempt so cross-session telemetry distinguishes "field absent" from "check did not run."

Recoverable — run `engine/tools/health_check.py --session S-NNNN` (the report-emit bumps `last_audit_session`, clearing both the hook surface and this soft-warn) or document explicit deferral in `outcome_summary`.

### `repo_config_health`

The shared-state probe at [`engine/tools/probe_repo.py`](../tools/probe_repo.py) reported a level-1 (suspect) condition. Active from S-0035 onward per [ADR 0045](../adr/0045-shared-state-integrity-discipline.md). Currently no level-1 conditions are emitted (reserved for future calibration like dirty working tree or detached HEAD); all probe findings today reach hard-fail level.

The probe escalates to a **hard-fail** when `core.bare=true` is set on either the worktree's effective config or the parent clone's standalone `.git/config` (the S-0033 vector — masked by a worktree override but breaks parent-side boot operations like `merge --ff-only` and `push origin main`), or when HEAD does not resolve, or when basic `git rev-parse` queries fail.

Recoverable — the probe's stderr names the exact `git -C <repo> config --unset core.bare` command needed for the bare-misconfig case; HEAD-resolution failures are typically detached-HEAD or partial-checkout artifacts and are addressed by the appropriate `git checkout` or `git switch` operation.

### Graph-audit soft-warns (S-0037 onward, active when SUPABASE_DB_URL is set)

The seven categories ADR 0016 contracts. All seven register in `checks_run` even when zero findings fire, so cross-session telemetry distinguishes "category clean" from "category did not run" (the schema convention at [`session-shutdown-sequence.md`](session-shutdown-sequence.md)).

- `undeclared_predicate` — edge.type not in `product/seed-graph/migrations/PREDICATE_MANIFEST.md`. Recoverable: add the row to the registry in the same session that uses the predicate, paired with an ENGINE_LOG entry under `Added`. Per [`seed-chunked-authoring.md`](seed-chunked-authoring.md) step 5.
- `attribute_shape_inconsistency` — same-domain nodes with materially different attribute coverage. v1 metric: `teaching_notes` populated-vs-NULL split with the minority class above 30% within a domain tag. Phase 5 calibration is a [`engine/build_readiness/phase_4_graph_validation.md`](../build_readiness/phase_4_graph_validation.md) T3-C deferral.
- `missing_rigor_score` — node carries inbound `pedagogical_prerequisite` edges and `rigor_score_computed` is at the schema default `0.5` (per [`product/seed-graph/migrations/0002_nodes.sql`](../../product/seed-graph/migrations/0002_nodes.sql)). The architecture.md formula expects topology data; the warn fires on "could be computed but wasn't."
- `render_readiness_violation` — node label contains a scaffolding token (`service_node`, `synthetic`, `stub`). Per [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) applied to label authoring; recoverable by renaming the node before commit.
- `synthetic_review_queue` — node has `confidence_level = 'SYNTHETIC'` per [ADR 0030](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md). Not a defect — populates the Opus batch review consumer per [`product/docs/self-correction.md`](../../product/docs/self-correction.md).
- `orphan_leaf` — zero inbound + zero outbound `pedagogical_prerequisite` edges (other edge types do not count toward in/out degree for this category). Recoverable when downstream subdomains add edges that reach the leaf, or by re-evaluating whether the node belongs at the granularity principle.
- `suspicious_cross_domain_ratio` — subdomain (single domain tag) where >40% of inbound `pedagogical_prerequisite` edges originate from nodes carrying no overlap with that domain tag. Likely a missing service node on the inside of the subdomain; recoverable by introducing the service node and re-routing the cross-domain edges through it.

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
