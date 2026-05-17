# Timestamp discipline

> All timestamp emission across the engine apparatus uses one canonical format. All Python emission routes through one helper. Per [ADR 0058](../adr/0058-canonical-timestamp-format-and-helper.md). Adjunct to [`code-discipline.md`](code-discipline.md) (the Python/engine row's Layer 1 source-of-truth in [`expression-contract-instantiation.md`](expression-contract-instantiation.md)).

This document is the Layer 1 contract for the timestamp-emission pattern, in the sense of [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md). It is read at the moment a session is about to add a new timestamp emit-site or read a stored timestamp.

## Canonical format

`%Y-%m-%dT%H:%M:%SZ` — ISO 8601, UTC, second precision, `Z` suffix. Example: `2026-05-08T12:34:56Z`.

The format is shared across runtimes (Python, shell hooks, future Rust or TypeScript). The implementation is per-runtime: Python emits via `engine/tools/timestamps.py`; hooks emit via `date -u +"%Y-%m-%dT%H:%M:%SZ"`. Runtimes don't depend on each other; they depend on the format.

A microsecond-precision variant `%Y-%m-%dT%H:%M:%S.NNNNNNZ` is admitted for one specific use case — `validate.py`'s telemetry-history record where same-second event ordering matters. The variant is emitted by a distinct helper function and tolerated by the parser. Every other emit site uses second precision.

## Helper API (`engine/tools/timestamps.py`)

```python
def emit() -> str: ...              # canonical now-string, second precision
def emit_micros() -> str: ...       # microsecond now-string, sole legitimate caller is validate.py telemetry
def parse(s: str) -> datetime: ...  # tolerant parser, returns tz-aware UTC datetime
def today() -> str: ...             # date-only %Y-%m-%d, distinct intent (day-of-event, not event-time)
```

`parse()` accepts the canonical Z-suffix form, the legacy Python `+00:00` form (still present in pre-S-0095 archives per the back-compat clause below), the with-or-without microseconds form, and the compact-time `%Y%m%dT%H%M%SZ` form (legacy `probe_push_gate.py` shape). Raises bare `ValueError` on unrecognized shapes.

`today()` is distinct from `emit()[:10]` because the type-of-time intent is day-of-event, not event-time. Two callers — `health_check.py:1248` (audit-report header) and `scan_engine_memory_citations.py:178` (citation buckets keyed by day) — display dates that should be diff-stable across same-day re-runs.

## Emit-vs-parse boundary

Emit and parse are dual sides of the contract:

- **Emit:** every new timestamp surface uses `emit()` (or `emit_micros()` if the use case is the validator-telemetry shape). Authoring a new site that hand-rolls `strftime` or `.isoformat` is a contract violation.
- **Parse:** every site that reads a stored timestamp uses `parse()`. The helper is the single point that knows about legacy shapes — calling `datetime.fromisoformat` directly is a contract violation, even when the call works in practice for the data the caller observed today.

The contract is asymmetric in time: emission tightens forward (new sites use canonical), parsing stays tolerant indefinitely (archives carry the historical shapes per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)'s archive-as-canon claim). The asymmetry is documented in ADR 0058 as a one-way back-compat clause, not an ongoing dual-format policy.

## Hooks emit canonical via shell, not via the helper

The five hook scripts under `engine/tools/hooks/*.sh` already emit canonical second-precision via `date -u +"%Y-%m-%dT%H:%M:%SZ"`. They are NOT required to import the Python helper.

The format is shared; the implementation is per-runtime. Forcing hooks to shell into Python every time they emit a timestamp would slow boot/shutdown for no contract benefit.

If a future hook needs sub-second precision, it shells into the Python helper at that emit site only — but no current hook needs it, and macOS BSD `date` has no portable sub-second support, so the question is moot for the existing hook surface.

## Allowlists

The validator's `timestamp_helper_bypass` soft-warn excludes four file paths in `engine/tools/`. Each entry has a one-line rationale stored in `validate.py`'s `_TIMESTAMP_HELPER_BYPASS_ALLOWLIST` and a longer inline comment at the offending callsite that names the contract being preserved.

- **`apply_migration.py`** — migration-version emission `strftime("%Y%m%d%H%M%S")`. The format Supabase's `schema_migrations.version` column expects; touching it would require a coordinated migration of historical version values.
- **`probe_push_gate.py`** — branch-name timestamp `strftime("%Y%m%dT%H%M%SZ")`. Git's check-ref-format rejects colons in branch names; the canonical Z-suffix form `2026-05-08T12:34:56Z` would fail at branch creation. The compact-time form is the correct legacy shape for filename-safe contexts. The `parse()` helper accepts this form on read-back via the compact-time regex branch.
- **`audit_mempalace_attribution.py`** — `_parse_palace_dt(filed_at)` parses naive local-time strings written by MemPalace's storage layer (no timezone marker). Different concern from canonical UTC-emitted strings; `parse()` returns tz-aware UTC, which would silently misattribute palace-storage timestamps. The same file's `_parse_archive_dt` IS routed through `parse()` for cleanliness; allowlisting silences both, and the inline comments document the intent.
- **`scan_engine_memory_citations.py`** — `fetch_today_diary` matches palace diary `date` fields keyed by naive local date. Matching against UTC date would silently miss entries written near the UTC date boundary. Same semantic as `_parse_palace_dt` above, applied at the date level.

A future legacy contract (a new external system's stored timestamp shape, a new filename-safe constraint) adds a fifth entry to the allowlist with an inline comment naming what the helper would break if applied. The pattern is: allowlist with rationale, never silence by suppression.

## Non-goal: `time.time()` for stopwatch math

`mempalace_rebuild_hnsw.py:317,446` uses `time.time()` to measure `(end - start)` deltas during HNSW rebuilds. The float is never serialized, never compared across processes, never sorted across event types. It's stopwatch math, not timestamp emission.

ADR 0058 covers timestamp **emission** (a moment-in-time as a string) and **parsing** (a string back to a datetime). It does not cover duration measurement. The validator soft-warn does not fire on `time.time()` because the AST walk only catches `.isoformat` and `.strftime` attribute calls.

(`time.monotonic()` would be more correct than `time.time()` for stopwatch math, but that's a separate observation, not Issue #33's scope.)

## Mechanical enforcement

`engine/tools/validate.py` runs `validate_timestamp_helper_bypass()` every commit. The check parses each `engine/tools/**/*.py` source file with `ast`, walks for `Call` nodes whose `func.attr in {"isoformat", "strftime"}`, and emits soft-warn `timestamp_helper_bypass` with file:line per offense.

**Allowlist:** `engine/tools/timestamps.py` (the helper itself), `engine/tools/apply_migration.py` (legacy supabase contract, scope-excluded above).

**Excluded:** `engine/tools/test_*.py` (test fixtures legitimately carry timestamp literals; AST detection cannot distinguish a fixture string from a real emit site).

**Out of scope for the AST walk:** shell scripts (hooks emit canonical via `date -u`, separate runtime) and non-Python files.

The check is soft-warn — it surfaces drift without blocking. A new emit site that legitimately needs to bypass the helper (the next supabase-version-shaped legacy contract, the next non-emission stopwatch measurement) adds itself to the allowlist with an inline comment naming why; the check stays green.

Persistent firing of `timestamp_helper_bypass` across multiple sessions signals new ad-hoc emission slipping in — the 3-of-5-archives surface per [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md) is the escalation signal.

## Manual procedure when adding a new emit site

1. Read this document. Confirm the new site emits a moment-in-time as a string (use the helper) or a duration measurement (use `time.monotonic()` and don't import the helper at all).
2. If emission: import `from engine.tools.timestamps import emit` (or `emit_micros` for the validator-telemetry shape) and call. Do not hand-roll `strftime` or `.isoformat`.
3. If parsing a stored timestamp: import `from engine.tools.timestamps import parse` and call. Do not call `datetime.fromisoformat` directly even when the data observed today happens to round-trip.
4. If the new site genuinely needs a non-canonical shape (the next supabase-style legacy contract): add the path to the validator's allowlist with an inline comment naming the contract being preserved.
5. Run `python3 engine/tools/validate.py --final-check` locally before commit to confirm `timestamp_helper_bypass` is silent at the new site.

The procedure is mostly mechanical; the AST-walk soft-warn catches lapses at commit time. The procedure exists for the cases the AST walk cannot see — adding a new shell hook (emits via `date -u`, not Python), or extending a non-Python tool that needs to coordinate timestamps with Python tools.

## See also

- [ADR 0058](../adr/0058-canonical-timestamp-format-and-helper.md) — the citable contract this document operationalizes.
- [`code-discipline.md`](code-discipline.md) — Python/engine row's Layer 1 source-of-truth; this document is its sibling discipline doc.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — `timestamp_helper_bypass` soft-warn category interpretation.
- [`expression-contract-instantiation.md`](expression-contract-instantiation.md) — Python/engine row covers `engine/tools/**/*.py` Layer 1; this document is an adjunct, not a new pattern row.
- [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) — the archive-as-canon claim that motivates the parser's back-compat tolerance.
- [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md) — escalation discipline for persistent `timestamp_helper_bypass` firing.
