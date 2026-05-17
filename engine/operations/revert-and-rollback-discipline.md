# Revert and rollback discipline

> Procedure for undoing a landed commit. Sibling to [`code-discipline.md`](code-discipline.md) and [`migration-discipline.md`](migration-discipline.md); kindred surface to [`escalation-criteria.md`](escalation-criteria.md)'s destructive-action rule. The constructive alternative when the destructive shortcut (`git reset --hard`, force-push, amend) is foreclosed.

Per [ADR 0078](../adr/0078-revert-and-rollback-discipline.md). The destructive-action rule in [`../../CLAUDE.md`](../../CLAUDE.md) forbids `git reset --hard` and amend as shortcuts; this doc names the constructive path forward when a commit on `main` needs to be undone.

## When to revert vs forward-fix

Forward-fix is the default. Revert is sparing.

| Choose | When |
|---|---|
| **Forward-fix** | The bug is small. The fix is well-understood. CI can be made green by a follow-up `fix:` commit. The bad commit's content is mostly correct; the defect is localized. |
| **Revert** | The bug is structural. The fix is not yet known. The bad commit must be removed from history *now* to unblock other work. The content as a whole is wrong-shaped, not a localized typo. |

Both paths preserve history — neither rewrites published commits. The choice is about whether the *fix* is forward (a new commit fixing the bug) or backward (a new commit undoing the bad commit). Amending a published commit, force-pushing over it, or `git reset --hard`-ing it out are not options; the destructive-action rule binds.

## Procedure

A revert is a normal commit authored on a working branch and merged through the standard PR flow:

1. Identify the SHA to revert. Confirm it is the *exact* commit (not a merge commit; not an adjacent commit).
2. Create a working branch: `git checkout -b revert/<short-desc>`.
3. `git revert <sha> --no-edit` — produces a revert commit on the working branch with auto-generated message.
4. Amend the commit message to the Conventional Commits form: `revert: <original subject> [reverts <sha>]`. The `revert:` prefix is the Conventional Commits standard for revert commits.
5. Push the branch and open a PR. Branch protection on `main` (per [Issue #69](https://github.com/StarshipSuperjam/paideia/issues/69)) requires the PR flow; CI runs against the revert (per [Issue #68](https://github.com/StarshipSuperjam/paideia/issues/68)) and merges after green.

The revert does NOT route through [`engine/tools/build_lifecycle_push.py`](../tools/build_lifecycle_push.py) or [`engine/tools/routine_lifecycle_push.py`](../tools/routine_lifecycle_push.py). Those wrappers verify lifecycle-shape commits (`chore(session): eager-claim ...`, `chore(session): close ...`, in-session deliverables); a revert is none of those.

## Interactions with project mechanisms

The revert procedure interacts with five Paideia-specific surfaces. Each interaction has a stable, verified shape.

### Lifecycle-push wrappers

[`engine/tools/routine_lifecycle_push.py`](../tools/routine_lifecycle_push.py) and [`engine/tools/build_lifecycle_push.py`](../tools/build_lifecycle_push.py) refuse `revert:` subjects in deliverable mode. The deliverable-shape regex is `^(feat|fix|docs|refactor|chore|test|ci|perf)(\([^)]+\))?: ` ([`routine_lifecycle_push.py:99`](../tools/routine_lifecycle_push.py)). The `revert:` prefix is intentionally absent.

This is correct behavior. Reverts are not lifecycle deliverables — they undo prior work rather than advance the session's named scope. The PR flow is the right surface for reverts; the lifecycle wrappers are the right surface for the three-step session ritual (eager-claim, deliverable, close).

Do not add `revert:` to `DELIVERABLE_SUBJECT_RE`. ADR 0078 records the rejection.

### Eager-claim recovery script

[`engine/tools/routine_eager_claim_recovery.py`](../tools/routine_eager_claim_recovery.py) is mechanically narrow. It activates only when HEAD-vs-`origin/main` matches the eager-claim-race shape: HEAD exactly one commit ahead of `origin/main`, HEAD subject matching `^chore\(session\): eager-claim S-\d{4}\b` ([`routine_eager_claim_recovery.py:81`](../tools/routine_eager_claim_recovery.py)), `origin/main` HEAD also carrying an eager-claim for the same slot.

A `revert:`-prefixed subject does not match the eager-claim regex. The recovery script refuses outside the verified shape; a recent revert at HEAD cannot false-trigger the script's narrow `git reset --hard origin/main` recovery. Verified shape, no code change needed.

### Migration apply wrapper

[`engine/tools/apply_migration.py`](../tools/apply_migration.py) executes migration bodies under a BEGIN/COMMIT wrap. SQL errors trigger atomic rollback (exit 3); no partial state lands; `supabase_migrations.schema_migrations` records nothing; retry is cheap. The in-flight rollback path is handled.

Reverting a migration *file* on a SUCCESSFUL apply is a different concern. The DB write already committed; deleting or reverting the SQL file does not undo the row inserts, schema changes, or settings updates the body produced. The constructive path is a separate **rollback migration**: a new `NNNN_rollback_<reason>_partN.sql` file authored under the same contract as the forward migration, applied via `apply_migration.py`, with Layer 2.5 postcondition assertions verifying the rollback effect (row counts decreased, schema reverted).

Rollback-migration authorship is documented in [`migration-discipline.md`](migration-discipline.md) ("Rollback authorship" section). The contract there is the source of truth — every up-migration carries a tested down-migration, either as a Supabase `down` step or a sibling `NNNN_<purpose>_rollback.sql` file. Living precedent: [`product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql`](../../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) (the S-0123 production-audit follow-up). The pattern is in use; this doc cross-references, it does not duplicate.

### ADR supersession

Reverting an ADR's contract is not a `git revert` operation against the ADR file. Per [`adr-authoring.md`](adr-authoring.md) status conventions, the path is:

1. Author a successor ADR carrying the new contract.
2. Mark the older ADR `Status: Superseded by ADR NNNN`. The older ADR remains in `engine/adr/` (or `product/adr/`) — its prose carries the historical reasoning.
3. The validator's `superseded_adr_currency` soft-warn (per [`cascade-discipline.md`](cascade-discipline.md)) catches downstream prose still citing the superseded ADR without a historical marker; fix the citations as part of the supersession landing.

Deleting a file from history (the destructive shortcut) is foreclosed. The decision-record substrate's value is durability — every settled position is recoverable, even after replacement.

If the revert intent is *also* to undo the ADR file itself (rare — usually only when an ADR landed within seconds of an immediate-rejection signal), use a `git revert` of the commit that introduced the ADR file, and still author a brief replacement ADR (or a `Status: Deprecated` marker per `adr-authoring.md`) explaining what happened. Pure deletion-via-revert leaves the decision record incoherent.

### engine_memory decisions-room drawers

engine_memory `decisions`-room drawers (per [`engine-memory-conventions.md`](mempalace-tagging-conventions.md)) are immutable. They capture the conversation that produced a decision; rewriting them would falsify the historical record.

When a decision is reverted, author a NEW `decision` drawer capturing the revert rationale. The original drawer remains. The recall-by-similarity surface naturally returns both — a future similarity search for "have we considered X?" surfaces the original decision AND the revert, giving the future session the full arc.

The `decision`-drawer-on-ADR-write hook ([`engine/tools/hooks/post-adr-write.sh`](../tools/hooks/post-adr-write.sh) per [ADR 0043](../adr/0043-hook-architecture.md)) reminds when a new ADR lands without a matching drawer; the same reminder applies to a supersession ADR — author the drawer capturing the revert deliberation.

## Hotfix flow

A critical production bug that cannot wait for the session-ritual ceremony (eager-claim → deliverable → close) routes through a hotfix branch:

1. `git checkout -b hotfix/<short-desc>` from `main`.
2. Author the fix as a `fix:` Conventional Commits subject. The fix may also be a `revert:` if the right path is to back out the bad commit rather than patch forward.
3. Open a PR with the `priority:urgent` label (per [Issue #72](https://github.com/StarshipSuperjam/paideia/issues/72) issue templates and [`issue-discipline.md`](issue-discipline.md) label taxonomy).
4. Merge after CI green. **Do not skip CI** — the hotfix branch runs the same gates as any other branch. Skipping introduces the failure mode the gates exist to catch.
5. Post-hotfix:
   - If the hotfix changed a contract surface (ADR-citable behavior, public API shape, schema), author an ADR documenting the change.
   - Otherwise, close the loop with an `engine/ENGINE_LOG.md` `[Unreleased]` entry under `Changed` or `Fixed`.

Hotfix flow bypasses the session-slot mechanism (no eager-claim, no `current.json`, no archive entry). It does not bypass the discipline that follows the fix — ADR/ENGINE_LOG accountability is preserved.

## What does NOT change for reverts

Per the ADR 0078 disposition:

- **`engine/tools/validate.py`** does not validate commit subjects. The `revert:` prefix question is moot at the validator surface; nothing there enumerates allowed Conventional Commits types.
- **The lifecycle wrappers' `DELIVERABLE_SUBJECT_RE`** stays strict. Reverts route through PR flow, not through the wrapper.
- **`routine_eager_claim_recovery.py`'s HEAD-shape check** stays narrow. Conservative by design.
- **`apply_migration.py`** has the BEGIN/COMMIT rollback path for in-flight SQL errors. Already-committed migrations require a rollback migration, not a file revert.

These are recorded here so a future session does not re-propose the changes. ADR 0078's "Alternatives Considered" section enumerates the rejected proposals with rationale.

## See also

- [ADR 0078](../adr/0078-revert-and-rollback-discipline.md) — the citable contract this doc operationalizes.
- [`adr-authoring.md`](adr-authoring.md) — Status conventions, supersession chain.
- [`migration-discipline.md`](migration-discipline.md) — rollback-migration authorship (the SQL surface of revert).
- [`code-discipline.md`](code-discipline.md) — sibling sub-discipline within engine/.
- [`escalation-criteria.md`](escalation-criteria.md) — destructive-action rule (the rule the constructive procedure here exists to satisfy).
- [`session-build-lifecycle.md`](session-build-lifecycle.md) — push policy; lifecycle commits route through the wrappers.
- [`issue-discipline.md`](issue-discipline.md) — HANDOFF.md vs GitHub Issues split for revert follow-ups.
- [`engine-memory-conventions.md`](mempalace-tagging-conventions.md) — `decision` drawer immutability.
- [`cascade-discipline.md`](cascade-discipline.md) — `superseded_adr_currency` soft-warn catches lingering citations.
