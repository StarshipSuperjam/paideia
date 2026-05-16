# ADR 0079 — HNSW sync_threshold tuning for cross-session metadata persistence

- **Status:** Superseded by [ADR 0091](0091-engine-memory-substrate-sqlite-fts5.md)
- **Date:** 2026-05-13
- **Deciders:** S-0145
- **Superseded at:** S-0188 (2026-05-16) — HNSW persist concerns retire with chromadb. ADR 0091 replaces the substrate with SQLite + FTS5; the WAL-mode + atomic-commit + foreign-keys discipline of stdlib `sqlite3` is the new durability story. The S-0187 in-rebuild `sync_threshold=3` amendment + the S-0186 `psycopg.connect_timeout` watchdog work surface decoupled from the substrate decision (watchdog survives in `validate.py`; sync_threshold logic deletes with `mempalace_set_sync_threshold.py` at S-0193). Removal lands at S-0193 per ADR 0091 Consequences.

## Context

Two destructive MemPalace HNSW rebuild events in 144 sessions (S-0078 at session 78, S-0144 at session 144 — an interval of ~66 sessions) traced to chromadb's lazy-persist design intersecting with mempalace's intentional anti-bloat tuning.

**The recurrence mechanism (verified empirically at S-0145 Phase 1.5).** chromadb's `PersistentLocalHnswSegment._apply_batch` (`chromadb/segment/impl/vector/local_persistent_hnsw.py:278-280` at chromadb 1.5.9) only calls `_persist()` (writes `index_metadata.pickle`) when `_num_log_records_since_last_persist >= self._sync_threshold`. `_persist()` is the function whose absence triggers the "HNSW segment has never flushed metadata" state that S-0078 and S-0144 forensic-rebuilt against. `Client.close()` (`chromadb/api/client.py:590-625`) does NOT call `_persist()`; it only releases the shared system reference. There is no public flush primitive on the chromadb client surface.

**The 50_000 threshold is mempalace's deliberate choice, not an oversight.** Mempalace `backends/chroma.py:52` (3.3.5; was `:54` at 3.3.4) defines `_HNSW_BLOAT_GUARD = {"hnsw:batch_size": 50_000, "hnsw:sync_threshold": 50_000}` and applies it to every `client.create_collection` call (`mcp_server.py:298-302`, `repair.py:411`). The rationale, from the file's own comment:

> *"HNSW tuning to prevent link_lists.bin bloat on large mines (#344). With default params (batch_size=100, sync_threshold=1000, initial capacity 1000), inserting tens of thousands of drawers triggers ~30 index resizes and hundreds of persistDirty() calls. persistDirty uses relative seek positioning in link_lists.bin; accumulated seek drift across resize cycles causes the OS to extend the sparse file with zero-filled regions, each cycle compounding the next. Result: link_lists.bin grows into hundreds of GB sparse, after which `status`/`search`/`repair` segfault."*

Mempalace's choice optimizes for high-volume bulk-mining workloads. For the project's low-volume MCP-mode auto-capture pattern (1–3 drawers per session), the 50_000 threshold is rarely reached — the in-memory metadata is dropped on process exit, the next session's HNSW open sees the missing pickle, and the recurrence vector fires.

**Issue #113 premise correction.** The originally-filed Issue #113 framed this as "default `sync_threshold = 1000` not reached." That was wrong-of-mechanism — chromadb's default is 1000, but mempalace overrides to 50_000 at creation. Issue #113 also labeled the S-0144 investigation as reading "mempalace v3.3.5 source" — actually the venv ran 3.3.4 at S-0144. The technical claim about the never-flushed-metadata state was correct in symptom; the version labels and the "default 1000" framing were wrong. The Issue #113 correction comment posted at S-0145 records these three layers of premise correction (mechanism + version + line numbers) and links here for the canonical disposition.

**Mempalace 3.3.5 (released 2026-05-10) improves the failure surface but does not address the cause.** Three relevant 3.3.5 fixes — `#1342` quarantine_stale_hnsw (detects missing-metadata + non-trivial-data state and renames bad segments aside before chromadb opens the native HNSW reader), `#1396` tool_search retry (cache-bust + 2s sleep + retry on "Error finding id" during the post-mine flush window; release notes explicitly call this a "partial fix"), `#1322` quarantine_stale_hnsw wired into `_client()` more broadly. None of these change chromadb's lazy-persist mechanism or mempalace's 50_000 default. The S-0144 recurrence vector is unchanged across 3.3.4 → 3.3.5. The two work streams are complementary, not redundant: 3.3.5 makes the failure cleaner when it happens; this ADR prevents it from happening.

[ADR 0045](0045-shared-state-integrity-discipline.md) already detects the divergence via the `mempalace_hnsw_divergence` boot probe and offers non-destructive recovery via [`mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py). What it does not do is prevent the recurrence. This ADR extends ADR 0045's detection posture with a prevention layer.

## Decision

S-0145 lands a hybrid posture honoring both failure modes (never-flushed-metadata and link_lists.bin sparse-file bloat):

**Steady-state: project-tuned `hnsw:sync_threshold = 100` on the live palace.** A new tool [`engine/tools/mempalace_set_sync_threshold.py`](../tools/mempalace_set_sync_threshold.py) reads from and writes to chromadb's `configuration` channel (the authoritative runtime source per chromadb 1.5.x — empirically verified that `collection.modify(metadata={...})` rejects payloads including `hnsw:space` as a distance-function change; `collection.modify(configuration={"hnsw": {"sync_threshold": N}})` is the supported retrofit path). The tool reads via `configuration.hnsw.sync_threshold` because the metadata channel is a creation-time advisory that does not reflect post-modify updates.

**Bulk rebuilds: mempalace's 50_000 default preserved.** [`mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) operates against a fresh scratch palace; chromadb collection creation in that scratch inherits mempalace's `_HNSW_BLOAT_GUARD` (50_000), so the anti-bloat protection applies during the bulk `add()` loop. After the scratch-then-swap completes, a forward-pointer in the rebuild tool's stderr names the next step: invoke `mempalace_set_sync_threshold.py --threshold 100 --backup-dir <path>` against the live palace.

**Threshold value: 100.** Defensible against the three named trade-off points:

- vs. **`threshold = 5` (the original Issue #113 suggestion)**: at threshold=5 a 16K-record forensic rebuild would trigger ~3,355 persistDirty() calls under the resize-feedback-loop. Empirical evidence from upstream PR #344 is that 39K-drawer rebuilds at low thresholds triggered the link_lists.bin bloat that compounds into multi-GB sparse files and segfault. Threshold=5 trades one corruption class for another.
- vs. **`threshold = 1000` (chromadb's untuned default)**: at typical 1–3-drawers-per-session, the chromadb default persists every ~300+ sessions; the recurrence vector is not closed in any reasonable horizon.
- vs. **`threshold = 50_000` (status quo, mempalace's default)**: the recurrence vector we're explicitly trying to escape. S-0078 + S-0144 empirical record names the ~66-session-per-rebuild recurrence interval.

At threshold=100, a forensic rebuild triggers ~160 persistDirty() calls (16K records / 100 per persist) — comparable in scale to chromadb's untuned default workload, well below the resize-feedback-loop pattern PR #344 was designed to prevent. Day-to-day low-volume writes persist every ~33 typical sessions (1–3 drawers per session); even worst-case process exit between persists loses less than one cadence of writes (recoverable from the SQLite source-of-truth via the existing rebuild tool).

**Tunability via `--threshold N`.** Future ADR amendments can adjust the value without re-authoring the tool. Chromadb's `hnsw_params.py:22` validator floors at `int > 2`, so the minimum is 3.

**User-directed safeguards.** Mandatory pre-switch backup via `--backup-dir PATH` (`cp -a`-equivalent through `shutil.copytree(copy_function=shutil.copy2)`); pre-switch state capture; post-switch verification via fresh-client re-read (mismatch is exit 4 with explicit RESTORE-FROM-BACKUP guidance); palace health probe via `probe_palace.py` subprocess (non-zero probe is exit 6, soft-warn-but-success).

**Three wiring points.**

1. **Boot ceremony** (`engine/tools/hooks/session-start.sh`): invokes the tool with `--verify-only` after the existing `probe_palace.py` line. Verify-only is read-only and never modifies state. If the boot probe surfaces divergence (one collection at 100, the other at 50_000 — likely a fresh-rebuild-without-post-swap state), it emits a LOUD attention block naming the corrective command. Apply is NEVER auto-invoked at boot per the user-directed safeguard (the modification requires its own explicit backup-dir).
2. **Rebuild tool** ([`mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py)): emits a forward-pointer at the end of a successful rebuild + divergence-verify path, naming the threshold-set command + backup-dir convention. Does NOT auto-apply (the swap from scratch to live is manual; the threshold-switch is a separate operation with its own backup).
3. **MCP search reliability**: indirectly. Steady-state threshold=100 keeps `index_metadata.pickle` fresh enough that the next session's HNSW open finds it, eliminating the "Error finding id" surface that 3.3.5 #1396 partially mitigates. The two layers are complementary.

**Upstream filing.** A new Issue on MemPalace/mempalace (not a comment on closed #1315; not the off-topic #1394) frames the low-volume-MCP gap in `_HNSW_BLOAT_GUARD`'s anti-bloat posture and proposes a `--hnsw-sync-threshold N` flag on `mempalace init` and `mempalace repair --mode from-sqlite`, or a dynamic-threshold mechanism that scales down once a collection's growth slows. If upstream lands either, the project-side tool retires as vestigial — same disposition as `mempalace_rebuild_hnsw.py` carries vis-à-vis MemPalace/mempalace#1394.

## Alternatives Considered

This ADR dogfoods the canonical "Alternatives Considered" section per [ADR 0077](0077-adr-template-alternatives-considered-section.md).

### `threshold = 5` (the original Issue #113 suggestion)

- **What:** Set `hnsw:sync_threshold = 5` to force a persist after almost every write. Issue #113 explicitly suggested 5–10 as the right band.
- **Pros:** Maximum durability — every session boundary's writes flush before process exit. Sealed the recurrence vector at the strictest possible setting (`int > 2` per chromadb's validator floor).
- **Cons:** Phase 1.5a discovery surfaced the trade-off the Issue #113 author hadn't anticipated: at threshold=5 a 16K-record forensic rebuild triggers ~3,355 persistDirty() calls. Upstream PR #344 documents empirically that low thresholds during bulk inserts trigger seek-drift accumulation in `link_lists.bin`, compounding into multi-GB sparse files and SIGSEGV during `status`/`search`/`repair`. We'd trade the never-flushed-metadata failure (recoverable via the existing rebuild tool) for the bloat failure (recoverable only via a fresh mine per the upstream comment — "once link_lists.bin has bloated, the index is already corrupt").
- **Rejected because:** the failure mode being introduced is strictly worse than the failure mode being prevented. The rebuild-tool-recovery path for never-flushed-metadata is well-trodden (S-0078, S-0144); the fresh-mine recovery path for bloat-corruption is destructive at the highest level.

### `threshold = 1000` (chromadb's untuned default)

- **What:** Override mempalace's 50_000 down to chromadb's library default of 1000 (per `hnsw_params.py:80`).
- **Pros:** Matches what every other chromadb-using project gets out of the box; arguably the lowest-friction value to defend in an upstream discussion ("we just want chromadb's own default, not mempalace's override").
- **Cons:** At typical 1–3-drawers-per-session, persists every ~300+ sessions. The recurrence vector closes at roughly the same interval the rebuild interval already runs (S-0078 → S-0144 was ~66 sessions; threshold=1000 would extend that to maybe ~200 sessions before rebuild is needed). Not a meaningful improvement; the rebuild-every-66-sessions pain becomes rebuild-every-200-sessions pain.
- **Rejected because:** does not deliver the durability the user-pushback at S-0144 was asking for ("can it be prevented?"). 200-session recurrence is reduction, not prevention.

### Upstream-only (no project-side tool)

- **What:** File the finding upstream and wait for mempalace to land a fix; ship no project-side mitigation.
- **Pros:** Cleanest long-term architecture — the fix lives where the choice is made; no project-side wrapper to retire when upstream lands the API. Avoids the dual-channel complexity of project tool + upstream tool.
- **Cons:** Upstream timelines are out of project control. The recurring rebuild was empirically observed at ~66-session interval; another rebuild between filing-time and upstream-fix-time is likely. The project-side wrapper has zero coupling cost — it lives in `engine/tools/` and retires cleanly when upstream's flag lands (same disposition as [`mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) carries vis-à-vis MemPalace/mempalace#1394).
- **Rejected because:** the S-0084 precedent (ADR 0045 amendment) for `mempalace_rebuild_hnsw.py` established the pattern of project-side mitigation when upstream timelines are uncertain. Same shape applies here. AND we do file upstream — the project tool is not in lieu of upstream filing, it's the bridge between filing and upstream landing.

### Pre-init wrapper around `mempalace init` / `mempalace repair`

- **What:** Intercept mempalace's CLI invocations at the project edge (e.g., a bash wrapper script around `mempalace init`) and inject `hnsw:sync_threshold = 100` into the metadata that the underlying collection creation will use.
- **Pros:** Closes the gap at collection creation time rather than retrofitting after. Avoids the read-modify-write cycle entirely.
- **Cons:** Far more invasive surface — the project would need to wrap every mempalace command that creates collections (init, repair, possibly future commands). Coupling tightens to mempalace's CLI surface. The retrofit approach via `collection.modify(configuration={...})` is version-portable across mempalace upgrades — `init` / `repair` may shift, but the chromadb collection-modify API is stable.
- **Rejected because:** deeper invasive surface than needed; `collection.modify()` post-hoc is sufficient and version-portable.

## Consequences

The deliverables this ADR commits to all land at S-0145:

- New: [`engine/tools/mempalace_set_sync_threshold.py`](../tools/mempalace_set_sync_threshold.py) — CLI wrapper with `--threshold N` / `--palace-path PATH` / `--verify-only` / `--backup-dir PATH` / `--no-backup` / `--skip-probe` flags; exit codes 0/1/2/3/4/5/6 (success / divergent-verify-only / pre-flight-refused / chromadb-modify-error / post-switch-verification-failed / generic-pre-flight-error / probe-finding-but-modify-succeeded).
- New: [`engine/tools/test_mempalace_set_sync_threshold.py`](../tools/test_mempalace_set_sync_threshold.py) — 27 pytests covering every exit-code path + backup discipline + configuration-vs-metadata channel + verify-only + apply + idempotency + production-path safety.
- Modified: [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) — new "MemPalace HNSW sync_threshold consistency probe" section. Always-verify-only, never auto-apply. Surfaces divergence with a LOUD attention block naming the corrective command.
- Modified: [`engine/tools/mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) — forward-pointer at successful-rebuild completion naming the threshold-set step + backup-dir convention.
- Modified: [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) — new "Persist-threshold tuning" subsection under "Maintenance probes" cross-referencing this ADR, the new tool, the Issue #113 trace, and the upstream Issue.
- Modified: [`pyproject.toml`](../../pyproject.toml) + [`uv.lock`](../../uv.lock) — mempalace pin bumped 3.3.4 → 3.3.5 (subsumes the stale Dependabot PR #104; closed in-session). `uv sync` brought the venv to mempalace 3.3.5 + chromadb 1.5.9 transitively.

The hybrid posture trades roughly:

- **Reduced**: never-flushed-metadata recurrence interval (was ~66 sessions empirically; expected ≥150+ sessions at threshold=100).
- **Added**: ~160 extra persistDirty() calls during a 16K-record forensic rebuild (vs. ~0 at the original 50_000; vs. ~3,355 at threshold=5). On a modern SSD, sub-second total cost.
- **Operational**: every threshold modification requires a backup. The S-0145 first-exercise backup is at `~/.mempalace/palace.S-0145-pre-threshold-switch` (130 MB); rotation discipline applies on subsequent modifications (caller picks a unique path).

**ADR 0053 first-exercise readiness criterion: NO (0/4 satisfied).** No new session mode; no new validator soft-warn category; no new state file; 1 ops-doc + 1 ADR + 1 new tool + 1 new test below the ≥3-ops-docs OR ≥5-tooling-files threshold. **10th consecutive negative finding** for ADR 0053 (mirrors ADRs 0069 / 0070 / 0071 / 0072 / 0073 / 0075 / 0077 / 0078 + the S-0143 ADR 0076 Amendment v2). The pattern is now firmly entrenched as the standard ADR shape.

**Issue #113 will be corrected (mechanism + version + line numbers) then closed at S-0145**, naming this ADR + the new tool + the new upstream Issue + the S-0145 archive ID.

**Versions at decision time**: mempalace 3.3.5; chromadb 1.5.9 (transitive). S-0144 investigation was against mempalace 3.3.4 + chromadb 1.5.8 (also a transitive at the time). The chromadb line numbers shifted across 1.5.8 → 1.5.9 (e.g., `_apply_batch` 286→278; `close_persistent_index` 540→511; `Client.close()` 596→590); the mempalace line numbers are mostly stable except `_HNSW_BLOAT_GUARD` (54 → 52). Mechanism is identical across all four version pairs.

## Amendment (S-0187): in-rebuild threshold override

The S-0145 deliverables shipped working but the **≥150-session recurrence-interval premise was falsified at 39 sessions** by the S-0184 audit. [ADR 0090](0090-phase-6-recall-substrate-decision.md) commitment 4 committed to investigating why. The S-0186 audit ([`engine/docs/audits/mempalace_state_S-0186.md`](../docs/audits/mempalace_state_S-0186.md)) named the root cause; this amendment (S-0187) lands the actionable mechanism.

### What was falsified

ADR 0079's "≥150-session recurrence at threshold=100" assumed that the post-S-0145 retrofit (`mempalace_set_sync_threshold.py --threshold 100` on the live palace, post-rebuild) made the persist mechanism reliable. S-0184 observed HNSW UNKNOWN at 39 sessions — far under the predicted window.

### Mechanism-level explanation (per S-0186 audit + S-0187 forensic re-verification)

Two coupled gaps in the S-0145 design:

1. **Rebuild-time threshold inheritance.** `mempalace_rebuild_hnsw.py` (S-0084) recreates collections via `client.create_collection(name=..., metadata=metadata)` where `metadata = dict(col.metadata or {})` — copying mempalace's `_HNSW_BLOAT_GUARD` `hnsw:sync_threshold=50_000` from the existing collection. chromadb's `PersistentLocalHnswSegment._sync_threshold` is set from this metadata at creation time. The rebuild's `collection.add()` calls per pagination batch never accumulate 50_000 records in a single batch (the rebuild uses batches of 5K), so `_apply_batch._persist()` (line 280 in chromadb 1.5.9 `local_persistent_hnsw.py`) never fires during the rebuild. `link_lists.bin` stays 0 bytes; `index_metadata.pickle` is never written.

2. **Retroactive threshold updates don't flush in-memory state.** The S-0145 `mempalace_set_sync_threshold.py` retrofit operates against the *live* palace via `collection.modify(configuration={'hnsw': {'sync_threshold': 100}})`. This affects FUTURE writes only — it doesn't trigger a flush of the un-persisted in-memory state from the rebuild. The post-rebuild palace was thus in the broken state from creation; subsequent normal-load writes accumulated against the threshold-100 ceiling but the original un-flushed state never went away.

The S-0187 forensic re-verification confirmed the empirical signature on the live palace 8 hours after S-0186's own rebuild:

- `~/.mempalace/palace/<drawers-seg-uuid>/link_lists.bin = 0 bytes`
- `~/.mempalace/palace/<closets-seg-uuid>/link_lists.bin = 0 bytes`
- Neither active segment carries `index_metadata.pickle`
- 49 quarantine directories (13 `.drift-*` + 36 `.corrupt-*`) — upstream `quarantine_stale_hnsw` (mempalace 3.3.5 chroma.py:105-108) firing on every open against the un-flushed shape, replacing each "bad" segment with a fresh-empty placeholder the next open also quarantines

### The mechanism this amendment lands

`mempalace_rebuild_hnsw.py` now overrides `hnsw:sync_threshold` at the rebuild's create-collection call:

- **Create-time:** metadata passed to `client.create_collection()` includes `"hnsw:sync_threshold": REBUILD_SYNC_THRESHOLD` (= 3, the chromadb `int > 2` validator floor). Each pagination batch crosses the threshold; `_persist()` fires per batch; `link_lists.bin` + `index_metadata.pickle` actually land on disk during the rebuild.
- **Post-adds:** after `_add_paginated()` completes and the count check passes, the tool calls `new_col.modify(configuration={"hnsw": {"sync_threshold": STEADY_STATE_SYNC_THRESHOLD}})` (= 100, the project steady-state). This is chromadb 1.5.x's authoritative runtime channel.
- **`hnsw:batch_size`** is left at the inherited 50_000 — that's the anti-bloat protection PR #344 designed; it controls HNSW *index resize* cadence (independent of persist cadence). Unaffected.

### Deliverables (S-0187)

- Modified: [`engine/tools/mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) — new `REBUILD_SYNC_THRESHOLD` (= 3) and `STEADY_STATE_SYNC_THRESHOLD` (= 100) constants; create-collection metadata override; post-adds `collection.modify` raise; post-rebuild forward-pointer updated to reflect that the rebuild self-applies the threshold (the prior pointer to `mempalace_set_sync_threshold.py` is no longer needed in the rebuild path; the standalone tool retains a narrower role for live-palace retrofit outside a rebuild context).
- Modified: [`engine/tools/test_mempalace_rebuild_hnsw.py`](../tools/test_mempalace_rebuild_hnsw.py) — two new regression guards (`test_rebuild_sets_steady_state_sync_threshold_post_adds`, `test_rebuild_uses_rebuild_threshold_at_create_collection`); existing `test_rebuild_against_synthetic_palace_preserves_count_and_metadata` updated to reflect intentional metadata mutation.
- Empirical re-verification record at [`engine/docs/audits/mempalace_regression_S-0187.md`](../docs/audits/mempalace_regression_S-0187.md) — the S-0187 diagnostic findings; Probes 1–6 + classifier-bug discovery (separate from this amendment but discovered in the same session).

### Scheduled-rebuild cadence decision (ADR 0090 commitment 2a)

ADR 0090 commitment 2a deferred the cadence question pending the recurrence-interval investigation outcome. With the S-0187 amendment landed:

**Decision: no scheduled rebuild at this time.** The rebuild-tool amendment (this section) addresses the recurrence root cause directly; the defensive post-hook prune (S-0186; S-0187 field-name fix) prevents the wing-scatter compounding factor. The combined posture should make the recurrence interval much longer than the falsified 39 sessions; absent empirical evidence that the new mechanism is itself insufficient, scheduled-rebuild machinery would be premature.

**Re-evaluation triggers (named so this is not silent deferral):**

- HNSW UNKNOWN status surfaces in any health-check audit between S-0187 and the next cadence-20 audit (S-0204) → escalate to scheduled-rebuild ADR.
- ≥1 instance of `mempalace_hnsw_status_suspect` soft-warn fires in the next 30 sessions → reconsider.
- Any future `mempalace_hnsw_divergence` soft-warn ≥10% pre-S-0204 → reconsider.
- If S-0204 audit (cadence-20) and S-0224 audit both surface MemPalace-substrate findings related to this mechanism → fire ADR 0090 commitment 6 reconsideration trigger.

The re-evaluation surface is monitored via the existing `validate.py` soft-warn telemetry (`mempalace_hnsw_status_suspect`, `mempalace_hnsw_divergence`, `mempalace_quarantine_accumulation`) — no new mechanism needed to detect.

### ADR 0053 first-exercise readiness criterion: NO (0/4 satisfied)

No new session mode; no new validator soft-warn category; no new state file; this amendment + the related field-name fix touch [`mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) + [`test_mempalace_rebuild_hnsw.py`](../tools/test_mempalace_rebuild_hnsw.py) + [`mempalace_post_hook_prune.py`](../tools/mempalace_post_hook_prune.py) + [`test_mempalace_post_hook_prune.py`](../tools/test_mempalace_post_hook_prune.py) + this ADR + the findings report — 6 files total, of which 4 are tooling. ≥5 tooling-files threshold is borderline; the rebuild + classifier are tightly coupled subjects, not cross-cutting. Treated as a single mechanism's amendment, not a new mechanism. **11th consecutive negative finding** for ADR 0053.

### Versions at amendment time

mempalace 3.3.5; chromadb 1.5.9 (unchanged from S-0145).

## See also

- [ADR 0045](0045-shared-state-integrity-discipline.md) — the detection-side spine this ADR extends with prevention.
- [ADR 0050](0050-project-venv-and-hook-path-wiring.md) — the venv-PATH wiring that makes the session-start.sh hook reach the venv-installed mempalace + the project tool.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — the readiness-note rubric the negative-finding block above evaluates against.
- [ADR 0077](0077-adr-template-alternatives-considered-section.md) — the Alternatives Considered template this ADR dogfoods.
- [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) "Persist-threshold tuning" subsection — the operational orientation.
- [`engine/tools/mempalace_set_sync_threshold.py`](../tools/mempalace_set_sync_threshold.py) — the wrapper tool.
- [`engine/tools/mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) — the sibling forensic-rebuild tool whose post-rebuild forward-pointer names this ADR.
- [Issue #113](https://github.com/StarshipSuperjam/paideia/issues/113) — the filing this ADR resolves; correction comment posted at S-0145 records the three layers of premise correction.
- Upstream [MemPalace/mempalace#1315](https://github.com/MemPalace/mempalace/issues/1315) — CLOSED; symptom-side fix via #1342 + #1396 (release notes self-described as "partial fix"). Not the upstream-filing target.
- Upstream [MemPalace/mempalace#1394](https://github.com/MemPalace/mempalace/issues/1394) — S-0084 destructive-repair filing; distinct concern.
- New upstream Issue on MemPalace/mempalace — proposes `--hnsw-sync-threshold N` flag on `init` / `repair`; named in the Phase 5 step 9 close comment on Issue #113.
- [ADR 0090](0090-phase-6-recall-substrate-decision.md) — back-pointer per [ADR 0041](0041-cascade-analysis-discipline.md) cascade discipline. The S-0184 audit found this ADR's "≥150-session recurrence interval" expectation falsified empirically (HNSW UNKNOWN at 39 sessions post-rebuild). ADR 0090 commitment 4 commits to investigating why; commitment 2a commits to scheduled rebuild as the bridge until upstream Issue #1489 lands.
