# ADR 0045 — Shared-state integrity discipline: subprocess env scrubbing, atomic mempalace writes, boot-time health probes

- **Status:** Accepted
- **Date:** 2026-05-03
- **Deciders:** S-0035

## Context

Two consecutive sessions broke from the same class of failure — silent subprocess mutation of shared state with no post-condition validation:

- **S-0033** wrote `core.bare=true` to the parent repo's `.git/config` from inside a pytest subprocess invoked by the pre-commit hook. Root cause: `GIT_DIR` / `GIT_WORK_TREE` leaked from the pre-commit hook context into test subprocesses, which then ran `git config` against the wrong repository. The session patched its own worktree's `config.worktree` to override the bleed-through but did not pin the leak vector or repair the parent. The damage was discovered at the next session's boot when `git status` refused with "must be run in a work tree."

- **S-0034** corrupted the chromadb HNSW segment for the `mempalace_drawers` collection. The `mempalace_rust_bindings.abi3.so` segfaulted on every subsequent palace open until the corrupt segment dir was moved aside and chromadb rebuilt fresh structures from the SQLite-stored embeddings. The cause was not pinned with certainty (the corrupt segment's last-write timestamp predated S-0034's close), but the structural conditions match the same pattern as S-0033: a lifecycle hook (`Stop` / `PreCompact` invoking `mempalace-hook-wrapper.sh`) ran a subprocess (`mempalace hook run`) with no env scrubbing, no atomic-write discipline, and no post-mine integrity check. A mid-write kill or env-leak corruption would produce exactly the corrupt-on-disk-but-undetected state observed.

The common pattern across both: **lifecycle hook → subprocess → unscrubbed env or non-atomic write → silent corruption of cross-session shared state → only detected when the next session reads.**

The engine's existing infrastructure does not currently:

1. Scrub the environment of subprocess calls inside production hooks. The autouse `_scrub_git_env` fixture in [`engine/tools/test_audit_side_discoveries.py`](../tools/test_audit_side_discoveries.py) demonstrates the technique for tests but lives in only one test file; production hooks (`session-start.sh`, `post-state-edit.sh`, `post-adr-write.sh`, `mempalace-hook-wrapper.sh`) and the four subprocess calls in [`validate.py`](../tools/validate.py) (ruff, ruff format, mypy, pytest) all pass parent env unchanged.
2. Validate post-conditions after a hook writes to shared state. `mempalace-hook-wrapper.sh` invokes `mempalace hook run` and trusts its exit code; it does not re-open the palace afterward to confirm the segment files are usable.
3. Probe shared-state health at session boot. The `SessionStart` hook ([ADR 0043](0043-hook-architecture.md)) surfaces cadence and persistent-warns but does not open the palace or check parent-repo sanity. A latent corruption from one session's hook firing only manifests when the next session's first query hits the bad bytes.
4. Use atomic-write discipline for binary segment writes. ChromaDB's mine flow writes HNSW segments in-place via `upsert_closet_lines()`. A mid-write process kill or env-leak that misroutes a write produces a corrupt segment; the corruption is silent until the next read.

Any one of these four gaps would have caught one of the two breaks. The third gap (boot-time probe) would have caught both at boot rather than mid-flow. The CLAUDE.md "End-state-quality first-pass" rule applies to authored content; this ADR extends the same discipline to the engine apparatus's own integrity machinery.

## Decision

The project mechanizes four shared-state integrity rules. Each is non-blocking at the harness level (always exits 0 to avoid catch-22 boot-blocks) but visible to the AI through stderr surfacing and the soft-warn lifecycle.

### 1. Subprocess environment scrubbing (defense-in-depth across all hooks)

Two production helpers replicate the `_scrub_git_env` fixture's behavior outside pytest:

- [`engine/tools/scrub_env.py`](../tools/scrub_env.py) — `scrubbed_env(base=None)` returns a dict copy with every `GIT_*` key removed. Used by [`validate.py`](../tools/validate.py)'s four subprocess calls (ruff, ruff format, mypy, pytest) and by [`probe_repo.py`](../tools/probe_repo.py).
- [`engine/tools/scrub_env.sh`](../tools/scrub_env.sh) — `scrub_git_env` bash function that unsets every `GIT_*` variable in the current shell. Sourced by all four hook scripts before they shell out (`session-start.sh`, `post-state-edit.sh`, `post-adr-write.sh`, `mempalace-hook-wrapper.sh`).

The `_scrub_git_env` autouse fixture is also hoisted from `test_audit_side_discoveries.py` into a new [`engine/tools/conftest.py`](../tools/conftest.py) so the protection applies to every test in the suite, not just the side-discovery tests. The original fixture remains in place — both running is idempotent and removing the conftest would not silently regress.

The scrub closes the S-0033 vector: pytest run inside the pre-commit hook now starts with no inherited `GIT_DIR` / `GIT_WORK_TREE` / `GIT_INDEX_FILE`, so any test that subprocesses `git config` against a tmp_path repo cannot bleed through to the parent's `.git/config`.

### 2. Boot-time shared-state health probes

Two probe scripts wrap chromadb and git checks so a native segfault terminates the probe (exit 139 = SIGSEGV) rather than crashing the validator that called it:

- [`engine/tools/probe_palace.py`](../tools/probe_palace.py) — opens chromadb `PersistentClient` at `~/.mempalace/palace`, lists collections, and calls `get_collection() + count()` on each. Sub-second on the 130 MB palace measured at S-0034. The `MEMPALACE_PROBE_PALACE_PATH` env var override exists for testing.
- [`engine/tools/probe_repo.py`](../tools/probe_repo.py) — checks the worktree's effective `core.bare`, the parent clone's standalone `.git/config` `core.bare` (catches the S-0033 worktree-override-masks-broken-parent case), and HEAD resolution.

Exit-code semantics: `0` healthy, `1` suspect (soft-warn), `2` hard-broken (hard-fail). `139` is treated as `2` by the wrapping validator function — for the palace probe this is the S-0034 chromadb_rust_bindings signature.

[`validate.py`](../tools/validate.py) gains `validate_shared_state_health()` which dispatches both probes as subprocesses (with scrubbed env), maps exit codes to `ValidationResult.soft_warn` / `hard_fail` calls, and is wired into the default check set so every pre-commit run includes it. A new `--health-probe-only` flag dispatches only the shared-state checks; the [`session-start.sh`](../tools/hooks/session-start.sh) hook calls `validate.py --health-probe-only` and surfaces findings to stderr at boot. Hard-broken findings emit a LOUD attention surface so the AI sees them at the top of the session context (the SessionStart hook still exits 0 — blocking the session would prevent the AI from diagnosing and repairing the very state the probe just flagged).

### 3. Atomic-write wrapper around `mempalace hook run`

[`engine/tools/hooks/mempalace-hook-wrapper.sh`](../tools/hooks/mempalace-hook-wrapper.sh) is extended with snapshot + probe + rollback discipline:

1. Pre-mine: `cp -a ~/.mempalace/palace ~/.mempalace/palace.pre-mine` (sub-200ms on 130 MB) and copy `~/.mempalace/knowledge_graph.sqlite3*` to a parallel snapshot dir.
2. Run `mempalace hook run` with scrubbed env via the sourced `scrub_env.sh` helper.
3. Post-mine: invoke `probe_palace.py`. On exit 0, rotate `palace.pre-mine` → `palace.last-good` (one snapshot retained for debugging). On exit 1, treat as suspect-but-success (no rollback). On exit 2 or 139, roll back: `rm -rf palace && mv palace.pre-mine palace`, restore the KG snapshot.

Rollback semantics: when triggered, the post-rollback palace is the exact pre-mine state. The hook's eventual `EXIT_CODE` for the log line is forced to non-zero so the next-session boot's reading of `.claude/logs/mempalace-hook.log` surfaces the rollback event.

Snapshot semantics: `cp -a` is byte-level, not transactional. If the long-running mempalace MCP server is mid-WAL-write to the chromadb sqlite at snapshot time, the snapshot may carry minor inconsistency. The trade is accepted because (a) chromadb uses WAL mode so reads don't block writes; (b) the snapshot is a recovery point, not a transactional baseline; (c) the cost of post-mine HNSW corruption (multi-session crash loop) dwarfs the cost of an imperfect rollback target.

### 4. Shutdown soft-warn aggregation across all session invocations

[`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) step 8 changes from "compute `outcome_summary_soft_warns` from validate.py's final-run output" to "aggregate across every validate.py invocation in this session's `validate-history.jsonl` entries — per-category max-count." The corresponding skill mirror at [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md) is updated in the same shape.

This closes a gap that would otherwise blunt the new boot-time probes: a probe that fires soft-warn at boot (e.g., `chromadb_palace_health` under suspicion-level corruption) but resolves before shutdown would be dropped from the archive, defeating the cross-session 3-of-5 surface per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md). Aggregating across all session invocations means boot-only firings still accumulate into the archive's `outcome_summary_soft_warns` field and contribute to persistent-warn detection.

## Consequences

The deliverables this ADR commits to all land at S-0035:

- New: [`engine/tools/scrub_env.py`](../tools/scrub_env.py), [`engine/tools/scrub_env.sh`](../tools/scrub_env.sh), [`engine/tools/probe_palace.py`](../tools/probe_palace.py), [`engine/tools/probe_repo.py`](../tools/probe_repo.py), [`engine/tools/conftest.py`](../tools/conftest.py), [`engine/tools/test_scrub_env.py`](../tools/test_scrub_env.py), [`engine/tools/test_probe_palace.py`](../tools/test_probe_palace.py), [`engine/tools/test_probe_repo.py`](../tools/test_probe_repo.py).
- Modified: [`engine/tools/validate.py`](../tools/validate.py) (env scrub on 4 subprocess calls; new `validate_shared_state_health()`; new `--health-probe-only` flag; default check set includes shared-state probes); [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh), [`engine/tools/hooks/post-state-edit.sh`](../tools/hooks/post-state-edit.sh), [`engine/tools/hooks/post-adr-write.sh`](../tools/hooks/post-adr-write.sh), [`engine/tools/hooks/mempalace-hook-wrapper.sh`](../tools/hooks/mempalace-hook-wrapper.sh) (sourced env scrub; the wrapper additionally gains snapshot + probe + rollback); [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) and [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md) (aggregation change); [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) (new `chromadb_palace_health` and `repo_config_health` categories).

CLAUDE.md's "Posture vs machinery" section narrows further: subprocess env scrubbing across hooks moves from posture (carried by the autouse fixture in one test file) to machinery (production helpers applied at every hook entry); palace atomic-write moves from posture (mining trusted to be self-healing) to machinery (snapshot + verify + rollback); shared-state probes at boot move from posture (next session reads broken state and discovers it) to machinery (probes fire at boot and surface findings before substantive work).

The validator's check count rises from 14 to 16 (`shared_state_palace`, `shared_state_repo`). Default-mode runtime gains the cost of two subprocess fires plus chromadb open (~0.3s on a 130 MB palace) — comfortably within the 3s pre-commit budget.

Trade-offs accepted:

- **Boot probe is non-blocking.** A hard-broken palace at boot emits a LOUD stderr surface but the SessionStart hook still exits 0, allowing the session to start. Blocking the boot would catch-22 the AI: the broken state is fixable from within a session, but only if a session can start. Soft surfacing relies on the AI reading the boot output and addressing the finding before substantive work — this is enforced by AI discipline, not mechanism.
- **Pre-commit hard-fail on hard-broken probe.** The default `validate.py` mode now hard-fails on definite corruption. Every commit is blocked until the corruption is repaired. This is correct — a session should not commit work on top of a broken palace or misset parent config — but it changes the failure surface: previously, hard-fails came only from repo-structure or code-discipline gates; now they can come from external state the session may not have caused. Mitigation: the probe's stderr names the exact recovery command for the bare-misconfig case and points at this ADR for the palace recovery procedure.
- **Snapshot disk overhead.** `palace.last-good` retains a copy of the pre-mine state; `palace.pre-mine` exists only mid-hook. Total: ~250 MB during a hook firing, ~130 MB between hooks, on a 130 MB palace. Negligible on modern disks; the rotation discipline caps retention at one. Disk-pressure is not currently checked — the wrapper doesn't refuse mining if free space is low. Future enhancement if the palace grows materially.
- **`cp -a` snapshot inconsistency window.** As noted under Decision 3, the snapshot may carry minor byte-level inconsistency if the MCP server is mid-write. Accepted for the cost-benefit reasoning above; using `sqlite3 .backup` or VACUUM INTO on the chroma sqlite would be more correct but adds complexity that the corruption-recovery use case does not demand.
- **`probe_palace.py` could itself segfault.** The probe imports chromadb and opens a `PersistentClient`. If the wheel is broken (the S-0034 chromadb 1.5.8 condition that crashed even in isolation pre-fix), the probe inherits the same fate. The wrapper handles this by treating exit 139 as hard-broken — the rollback path runs even though the probe didn't return cleanly. The validator's `validate_shared_state_health()` does the same, mapping 139 to a hard-fail with a body that names "the S-0034 corruption signature." Both paths are correct; both rely on the operating system's segfault → exit 139 invariant, which is reliable.
- **Soft enforcement leaves drift possible.** Like ADR 0043's hooks, these soft surfaces can be ignored. The first 3-of-5 surface for `chromadb_palace_health` or `repo_config_health` would fire at the third session in which the suspect/hard-broken state persisted; the 10-consecutive-archive escalation per ADR 0042 forces a resolution at that point. Earlier resolution is AI-discipline-driven.

The boot procedure's parent-side `git -C <parent> merge --ff-only` and `git -C <parent> push origin main` operations were the eventual victims of S-0033's `core.bare=true`; the new `probe_repo.py` checks that surface specifically (the parent's standalone config, not just the worktree's effective config), so a recurrence would surface at boot rather than mid-shutdown.

### Amendment (S-0084) — HNSW divergence detection wiring + non-destructive restoration tool

S-0084 wires `probe_palace.py` to upstream's `mempalace repair-status` (read-only; never opens a chromadb client) for divergence detection — replacing the from-scratch probe initially considered. The upstream subcommand was discovered during planning to already exist; building one from scratch was unnecessary reinvention. The probe emits a new stderr line — `[probe-palace] divergence: HNSW=N1 SQLite=N2 (P%)` — when the upstream tool is available and parseable; the existing exit-code semantics (0 healthy / 1 suspect / 2 hard-broken / 139 segfault) are preserved with the addition that divergence ≥ 10% promotes a previously-clean exit code from 0 to 1. `validate.py`'s `validate_shared_state_health()` parses the divergence line and emits a new soft-warn category `mempalace_hnsw_divergence` at ≥ 10%, with a LOUD-attention escalation body at ≥ 30% that includes the destructive-repair carve-out warning verbatim.

For restoration, S-0084 introduces [`engine/tools/mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) — a direct chromadb rebuild that bypasses `mempalace repair --mode legacy` (which S-0078 confirmed destroys SQLite embedding rows; see `engine/operations/mempalace-operations.md` "Known issues"). The tool reads `(embedding_id, document, metadata)` tuples directly from `chroma.sqlite3` for every drawer in the METADATA segment, deletes the collection preserving its `metadata` (e.g., `hnsw:space: cosine`), recreates, and re-adds via `collection.add(ids, documents, metadatas)` WITHOUT explicit embeddings — chromadb re-computes via the registered default embedding function and writes both SQLite metadata segment and HNSW vector segment in sync. This shape is forced by the operative case: on a divergent palace, chromadb's `get(include=["embeddings"])` raises `InternalError: Error finding id` for the divergent rows because their vectors are genuinely missing from HNSW; SQLite-direct extraction sidesteps that failure mode. Trade-off accepted: the rebuilt vectors are not byte-identical to the originals (current default embedding function may have shifted from when the originals were embedded) — but the alternative is to lose the divergent rows' data entirely.

Always run against a scratch palace copy first; atomic-rename swap to live gated on `mempalace repair-status` reporting < 1% divergence post-rebuild. The pre-S-0084 backup at `~/.mempalace/palace.S-0084-pre` is the canonical safety anchor. If chromadb's add() is mid-flight when the process is killed, the collection is in a "deleted-but-not-fully-readded" state — exit code 2 documents this; recovery is to restore from the pre-rebuild snapshot.

The validator's check count rises from 16 to 17 (`mempalace_hnsw_divergence` is the new category). Default-mode runtime gains the cost of one `mempalace repair-status` subprocess per probe invocation — 5-15s on the live ~450 MB palace; the probe's existing chromadb-open is unchanged.

The rebuild tool is project-internal. It duplicates capability that ought to live in upstream's `mempalace repair`. The S-0084 upstream tracker [MemPalace/mempalace#1394](https://github.com/MemPalace/mempalace/issues/1394) tracks the destructive-repair pattern; if upstream lands a non-destructive `mempalace repair` mode, `mempalace_rebuild_hnsw.py` becomes vestigial and should retire.

## See also

- [ADR 0033](0033-validator-as-the-discipline-spine.md) — the discipline spine `validate.py` extends.
- [ADR 0038](0038-expression-contract-for-ai-authored-code.md) — the Layer 2 code-gates the env scrub now applies to.
- [ADR 0041](0041-cascade-analysis-discipline.md) — sibling cascade-discipline soft-warn machinery.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — the archive-canon trend mechanism the new categories plug into; aggregation change in Decision 4 closes a gap in this lifecycle for boot-only firings.
- [ADR 0043](0043-hook-architecture.md) — sibling structural decision: this ADR's helpers are sourced by the hook scripts ADR 0043 introduced. The new probe step in `session-start.sh` is an in-place extension of the hook ADR 0043 commits to.
- [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) — step 8 amended for the aggregation change.
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — new `chromadb_palace_health` and `repo_config_health` category entries.
- [`engine/tools/test_audit_side_discoveries.py`](../tools/test_audit_side_discoveries.py) — the autouse fixture this ADR's production helpers replicate.
- HANDOFF.md S-0033→S-0034 entry: "Stale-checkout vs halted-shutdown — Recovery section needs a sanity check" — the open recovery-procedure thread that frames this hardening's broader context.
