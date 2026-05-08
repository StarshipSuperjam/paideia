# ADR 0058 — Canonical timestamp format and shared timestamps.py helper

- **Status:** Accepted
- **Date:** 2026-05-08
- **Deciders:** S-0095 (issue close-out campaign session C6; closes [Issue #33](https://github.com/StarshipSuperjam/paideia/issues/33))

## Context

The engine apparatus emits timestamps from at least 15 sites across shell hooks, Python tools, JSON archives, and the migrations table. There has been **zero prescribed standard** — no ADR, no operations doc, no shared helper module — and at least five distinct formats coexist:

1. ISO-8601 UTC second-precision Z-suffix `%Y-%m-%dT%H:%M:%SZ` (5 hook scripts plus `parse_structural_reference.py`).
2. Python `.isoformat()` with microseconds and `+00:00` offset (`validate.py:3301` telemetry record, `routine_lock.py:111`).
3. Compact `%Y%m%d%H%M%S` (no separators) for `apply_migration.py`'s supabase migration version.
4. Compact-time `%Y%m%dT%H%M%SZ` (T separator, no colons in the time portion) for `probe_push_gate.py`.
5. Day-only `%Y-%m-%d` for `health_check.py:1248` audit-report header and `scan_mempalace_citations.py:178` citation buckets.

The cost is per-emitter format-knowledge sprawl in every parser site. `health_check.py:960-961` already pays this tax — `datetime.fromisoformat(started.replace("Z", "+00:00"))` — to bridge formats #1 and #2 on a same-archive read. The `.replace("Z", "+00:00")` is the smoking gun: every parser site is responsible for knowing which emitter wrote which field, and patching the format before parsing. Adding a new emitter that uses format #2 keeps this code working accidentally; adding one that uses format #4 silently breaks it.

Audits and telemetry that span sites become unreliable in concrete ways:

- **Migration ↔ session correlation.** No automated audit can match "migration applied at T1" (format #3) to "session active at T2" (format #1) without per-join format conversion.
- **Archive timestamp comparison.** `started_at` (hook-written, format #1) and `timestamp` (`validate.py`-written, format #2) live in the same archive JSON. Sorting or arithmetic across them requires per-field format awareness.
- **Future validators.** Any new validator that wants to read timestamps across the system replicates per-emitter format knowledge in its own parsing layer. Format-knowledge sprawls instead of concentrating.

The structural diagnosis matches the **scattered-knowledge** mode that one-helper-per-concern designs are meant to prevent: knowledge about format coexistence belongs in *one* place — the helper — so that adding a new emitter or reader is a single import, not a library survey.

## Decision

The project commits to a canonical timestamp format and a shared Python helper that all `engine/tools/**/*.py` emission and parsing routes through. The operational surface is [`../operations/timestamp-discipline.md`](../operations/timestamp-discipline.md). This ADR is the citable contract.

The contract carries six elements:

**1. Canonical format.** ISO-8601 UTC second-precision Z-suffix `%Y-%m-%dT%H:%M:%SZ`. Example: `2026-05-08T12:34:56Z`. The format is shared across runtimes (Python, shell hooks, future runtimes); the implementation is per-runtime. Hooks emit canonical via `date -u +"%Y-%m-%dT%H:%M:%SZ"`; Python emits via the helper.

**2. All Python emission routes through `engine/tools/timestamps.py`.** The helper exposes four functions: `emit()` (canonical second-precision now-string), `emit_micros()` (microsecond now-string for the validator-telemetry shape only), `parse(s) -> datetime` (tolerant parser), `today() -> str` (date-only for day-of-event surfaces distinct from event-time emission). Authoring a new site that hand-rolls `strftime("%Y-%m-%dT%H:%M:%SZ")` or `.isoformat()` is a contract violation, mechanically detected by `validate.py`'s `timestamp_helper_bypass` AST-walk soft-warn over `engine/tools/**/*.py`.

**3. Parser tolerance is one-way back-compat.** `parse()` accepts the canonical Z-suffix form, the legacy Python `+00:00` form (still present in pre-S-0095 archives per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md)'s archive-as-canon claim), with-or-without microseconds, and the compact-time `%Y%m%dT%H%M%SZ` form (legacy `probe_push_gate.py` shape). The contract is asymmetric in time: emission tightens forward, parsing stays tolerant indefinitely. The asymmetry is *not* a dual-format policy — it is a one-way back-compat clause documented as such so a future reader does not interpret the parser's tolerance as license to emit non-canonical shapes from new sites.

**4. Hooks emit canonical via shell, not via the helper.** The five hook scripts under `engine/tools/hooks/*.sh` already emit canonical second-precision via `date -u +"%Y-%m-%dT%H:%M:%SZ"`. They are NOT required to import the Python helper. The format is shared; the implementation is per-runtime. Forcing hooks to shell into Python at every emit site would slow boot/shutdown for no contract benefit.

**5. Allowlisted bypasses cover legitimate non-canonical contracts.** Four files under `engine/tools/` emit or parse non-canonical shapes for reasons external to the helper's contract: `apply_migration.py` (legacy supabase `schema_migrations.version` column shape `%Y%m%d%H%M%S`), `probe_push_gate.py` (branch-name-safe compact-time form `%Y%m%dT%H%M%SZ` — Git's check-ref-format rejects colons), `audit_mempalace_attribution.py` (palace-storage naive local-time strings, different concern from canonical UTC emission), and `scan_mempalace_citations.py` (palace diary entries keyed by naive local date). The validator's `timestamp_helper_bypass` check excludes these by path; each carries an inline comment cross-referencing this ADR and naming what the helper would break if applied. The full per-file rationale is documented in [`../operations/timestamp-discipline.md`](../operations/timestamp-discipline.md) "Allowlists." Adding a fifth allowlist entry follows the same pattern: allowlist with rationale, never silence by suppression.

**6. Non-goal: stopwatch math.** `time.time()` for `(end - start)` deltas (currently `mempalace_rebuild_hnsw.py:317,446`) is out of scope. The ADR covers timestamp **emission** (a moment-in-time as a string) and **parsing** (a string back to a datetime). It does not cover duration measurement. The validator soft-warn does not fire on `time.time()` because the AST walk only catches `.isoformat` and `.strftime` attribute calls.

The contract's **amendment discipline**: refinements to the helper (adding a fifth function the contract anticipates, sharpening the parser's tolerance, adding an allowlist entry with an inline rationale comment) are ENGINE_LOG-tracked refinements to [`../operations/timestamp-discipline.md`](../operations/timestamp-discipline.md). Posture changes — abandoning the canonical-format claim, dropping the helper-routes-emission principle, removing the back-compat tolerance — require a superseding ADR.

## Consequences

- **The operational document is the working surface; this ADR is the citable contract.** [`../operations/timestamp-discipline.md`](../operations/timestamp-discipline.md) carries the helper API description, the emit-vs-parse boundary, the hooks-stay-shell rationale, the allowlist documentation, the non-goal definition, the mechanical-enforcement description, and the manual procedure for adding new emit sites. Refinements land there under ENGINE_LOG tracking; posture changes require superseding this ADR. Same separation [ADR 0036](0036-expression-contract-for-inward-documents.md), [ADR 0038](0038-expression-contract-for-ai-authored-code.md), [ADR 0039](0039-universal-expression-contract-across-ai-authoring-patterns.md), and [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) maintain between themselves and their operational surfaces.

- **No new pattern row in [`../operations/expression-contract-instantiation.md`](../operations/expression-contract-instantiation.md).** Timestamp emission is a sub-discipline within the existing Python/engine pattern row, the same shape as [`../operations/cascade-discipline.md`](../operations/cascade-discipline.md) (an adjunct to `code-discipline.md` that does not add a row to the table). The Python/engine row's Layer 2 gate (the `validate.py` check stack) gains one new check; its Layer 1 source-of-truth gains a sibling discipline doc. The pattern itself is unchanged.

- **`timestamp_helper_bypass` soft-warn fires on first commit if any emit site is missed.** The check is registered in [`../operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md). Persistent firing across sessions per [`../operations/soft-warn-lifecycle.md`](../operations/soft-warn-lifecycle.md)'s 3-of-5-archives surface signals new ad-hoc emission slipping in.

- **Backfill of historical archives is not undertaken.** [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) names archives as load-bearing canon; mutating ~95 archives via a migration script is a far bigger blast radius than the inconsistency it removes, and would break `git blame` semantics on session evidence. New emissions land canonical (Z-suffix); `parse()` accepts both Z and `+00:00` indefinitely. The asymmetry is documented in element 3 of the Decision.

- **`probe_push_gate.py` branch-naming docstring updates.** The current `_utc_timestamp()` docstring claims "compact UTC timestamp suitable for branch names" but the actual caller is a commit-message body, not a branch name. The migration to `emit()` (canonical Z-suffix with colons) preserves correctness because colons are legal in commit messages. The docstring revision lands as part of this ADR's first-exercise migration.

- **First-exercise readiness per [ADR 0053](0053-mechanism-first-exercise-gate.md).** Trigger-criterion evaluation: this contract is *single-runtime* (Python `engine/tools/`) and *non-cross-cutting* (a single discipline-doc + helper module + validator check, no harness coordination, no external system contract). It does **not** meet ADR 0053's cross-cutting first-exercise threshold; the helper's first exercise is its own immediate use within the S-0095 migration commits, mechanically gated by the new soft-warn at every commit. No separate first-exercise readiness note is required.

- **No retroactive grandfathering.** The contract takes force at acceptance. Pre-S-0095 archive timestamps in format #2 stay in their original shape per the back-compat tolerance; pre-S-0095 hook-emitted timestamps in format #1 were already canonical. The contract applies forward from the S-0095 close commit.

## See also

- [`../operations/timestamp-discipline.md`](../operations/timestamp-discipline.md) — Layer 1 source-of-truth.
- [`../operations/code-discipline.md`](../operations/code-discipline.md) — Python/engine Layer 1 source-of-truth this discipline is a sibling to.
- [`../operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — `timestamp_helper_bypass` soft-warn category interpretation.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — archive-as-canon claim that motivates the parser's back-compat tolerance.
- [ADR 0039](0039-universal-expression-contract-across-ai-authoring-patterns.md) — the umbrella expression-contract framing this ADR's helper-routing claim instantiates.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise gate; trigger-criterion evaluation in Consequences above.
