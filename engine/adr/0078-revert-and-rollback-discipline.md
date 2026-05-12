# ADR 0078 — Revert and rollback discipline

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0140

## Context

Paideia's destructive-action rule in [`../../CLAUDE.md`](../../CLAUDE.md) forbids `git reset --hard`, force-push, and amend as shortcuts for undoing a landed commit. The constructive alternative — a revert commit on a working branch merged via PR — is well-known in general git practice but interacts with five Paideia-specific surfaces in non-obvious ways:

1. **The lifecycle-push wrappers** ([`build_lifecycle_push.py`](../tools/build_lifecycle_push.py) per [ADR 0076](0076-build-mode-lifecycle-push-wrapping.md), [`routine_lifecycle_push.py`](../tools/routine_lifecycle_push.py) per [ADR 0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md)) shape-verify HEAD subjects against a strict regex. A `revert:` prefix is not in that regex.
2. **The eager-claim recovery script** ([`routine_eager_claim_recovery.py`](../tools/routine_eager_claim_recovery.py) per [ADR 0052](0052-routine-boot-freshness-and-concurrency-defense.md)) performs a narrow `git reset --hard origin/main` only when HEAD matches a very specific eager-claim race shape. A `revert:` commit at HEAD might or might not perturb that judgment.
3. **The migration apply wrapper** ([`apply_migration.py`](../tools/apply_migration.py) per [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md)) wraps body apply under BEGIN/COMMIT; SQL errors trigger atomic in-flight rollback. Reverting a migration *file* after a successful apply does not undo the DB write — a separate rollback migration is required (rule exists in [`migration-discipline.md`](../operations/migration-discipline.md) but is not connected to the revert procedure).
4. **ADR supersession** has its own status-conventions discipline ([`adr-authoring.md`](../operations/adr-authoring.md)) that forecloses simple file deletion.
5. **MemPalace `decision` drawers** are immutable per [`mempalace-tagging-conventions.md`](../operations/mempalace-tagging-conventions.md).

[Issue #86](https://github.com/StarshipSuperjam/paideia/issues/86) (analysis-outcome from cross-check of `addyosmani/agent-skills` against Paideia practice) surfaced the gap: there is no Layer-1 ops doc consolidating the revert procedure and naming the five interactions. The Issue body also proposed a `validate.py` allowed-Conventional-Commits-types extension, but on inspection `validate.py` does not validate commit subjects — that gate lives in the lifecycle wrappers, not the validator.

## Decision

S-0140 lands a new Layer-1 ops doc [`engine/operations/revert-and-rollback-discipline.md`](../operations/revert-and-rollback-discipline.md) consolidating the revert procedure and naming each of the five interactions with concrete stable behavior. No code changes ride alongside; each of the five mechanisms already has the correct shape:

- The lifecycle wrappers refuse `revert:` subjects in deliverable mode by design. Reverts route through PR flow (per [Issue #69](https://github.com/StarshipSuperjam/paideia/issues/69) branch protection + [Issue #68](https://github.com/StarshipSuperjam/paideia/issues/68) CI), not through the wrappers.
- The eager-claim recovery script's HEAD-shape check matches only `^chore\(session\): eager-claim S-\d{4}\b`; a `revert:` subject does not match and cannot false-trigger the script.
- `apply_migration.py`'s BEGIN/COMMIT body wrap handles in-flight SQL errors; already-committed migrations require a separate rollback migration whose authorship is documented in [`migration-discipline.md`](../operations/migration-discipline.md) (the new ops doc cross-references, does not duplicate). Living precedent: [`product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql`](../../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql).
- ADR supersession follows the existing status-conventions chain (Status: `Superseded by ADR NNNN`); the older ADR remains in place.
- MemPalace handles reverts by authoring a new `decision`-tagged drawer alongside the original; the recall-by-similarity surface returns both.

A hotfix flow for critical production bugs that cannot wait for the session-ritual ceremony is documented in the new ops doc: `hotfix/<short-desc>` branch + `fix:` (or `revert:`) Conventional Commits subject + PR with `priority:urgent` label + standard CI gates (no skip). Post-hotfix accountability via ADR (if a contract surface changed) or `engine/ENGINE_LOG.md` `[Unreleased]`.

## Alternatives Considered

This ADR dogfoods the canonical "Alternatives Considered" section per [ADR 0077](0077-adr-template-alternatives-considered-section.md).

### Extend `code-discipline.md` with a "revert" section rather than authoring a new ops doc

- **What:** Add a "Revert and rollback" section to [`code-discipline.md`](../operations/code-discipline.md) (the expression contract for AI-authored code), keeping all revert-related guidance under one document.
- **Pros:** Fewer ops-doc files; co-locates revert with the broader code-discipline contract; a session reading code-discipline for the first time naturally encounters revert procedure as a "see also" within the same surface.
- **Cons:** Conflates two different concerns. `code-discipline.md` is an *expression contract* for code — what code looks like at authoring time (contract blocks, mechanical gates, cold-review). Revert/rollback is a *procedural* concern — what to do after a commit lands. Mixing them makes both harder to find and harder to maintain (changes to one surface risk churning the other). [`migration-discipline.md`](../operations/migration-discipline.md) already operates as a separate ops doc rather than a section within code-discipline; the same partitioning applies here.
- **Rejected because:** the [`engine/operations/README.md`](../operations/README.md) "one concern per file" convention is load-bearing. The new ops doc is a sibling, not a section.

### Add `revert:` to `DELIVERABLE_SUBJECT_RE` in the lifecycle wrappers

- **What:** Extend the regex at [`routine_lifecycle_push.py:99`](../tools/routine_lifecycle_push.py) from `^(feat|fix|docs|refactor|chore|test|ci|perf)(\([^)]+\))?: ` to include `revert` — making revert commits acceptable as in-session deliverables pushable through the wrapper.
- **Pros:** A session that authors a revert mid-work could push it through the same lifecycle wrapper used for other deliverable commits, without having to leave session ritual for PR flow.
- **Cons:** Reverts are not lifecycle deliverables. The wrapper exists to verify the three-step session ritual (eager-claim, deliverable, close); a revert undoes prior work rather than advances the session's named scope. Adding `revert:` to the regex would permit a session to land a revert directly to `main` without PR review — sidestepping branch protection's review-required posture for changes that, almost by definition, address something the original review process missed. The PR flow is the correct surface for revert oversight.
- **Rejected because:** scope mismatch (reverts are not session deliverables) combined with review-bypass risk. The wrapper's strict regex is correct behavior.

### Author a separate ADR specifically for migration rollback

- **What:** Author ADR 0078 for revert (git-history surface) and a separate companion ADR for migration rollback (DB-state surface) — two ADRs covering two distinct domains.
- **Pros:** Sharper scoping per ADR; future readers grep-find each domain independently; the migration-rollback ADR could pair naturally with [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md) and [`migration-discipline.md`](../operations/migration-discipline.md).
- **Cons:** Migration rollback authorship is *already* documented in [`migration-discipline.md`](../operations/migration-discipline.md) (search "rollback"); the rule exists and has been exercised (precedent: [`0062_seed_direction_flips_revert_part1.sql`](../../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql)). A new ADR would duplicate the contract rather than extend it. The right move is to cross-reference from the new ops doc, not to author a redundant ADR.
- **Rejected because:** the migration-rollback contract already exists. The cross-reference pattern from `revert-and-rollback-discipline.md` to `migration-discipline.md` is the structurally correct response. ADRs commit to *new* contracts; this is not a new contract.

### Defer the ops doc and address each revert/rollback case as it arises

- **What:** Close [Issue #86](https://github.com/StarshipSuperjam/paideia/issues/86) as `wontfix` or "trigger-gated"; document the procedure ad-hoc when the first revert situation actually occurs.
- **Pros:** No work now; smaller corpus.
- **Cons:** Per `feedback_no_pilot_wait_and_see.md` and `feedback_no_preemptive_deferral.md`: deferral-without-mechanism is silent indefinite deferral. The first revert situation will be under time pressure (production bug, broken CI, stale `main`) — the worst moment to also be deciding procedure cold. The cost of authoring the doc now is one session; the cost of authoring it during an incident is multiplied by stress + interrupting incident response. The five interactions are non-obvious; documenting them in advance removes a class of mistake.
- **Rejected because:** standing memory rules out the deferral framing. The doc lands in the same session as the surface it documents.

## Consequences

- New Layer-1 ops doc [`engine/operations/revert-and-rollback-discipline.md`](../operations/revert-and-rollback-discipline.md) consolidates revert procedure + five interaction shapes + hotfix flow. Future revert/rollback work has one document to consult.
- The "Alternatives Considered" section of this ADR records the explicit rejection of adding `revert:` to `DELIVERABLE_SUBJECT_RE`. A future session re-encountering the question has a citable answer; the re-litigation surface is closed.
- Cascade per [ADR 0041](0041-cascade-discipline-three-validator-checks-plus-manual-procedures.md): future changes to `DELIVERABLE_SUBJECT_RE` (in either lifecycle wrapper) or to `routine_eager_claim_recovery.py`'s HEAD-shape regex MUST update this ADR's named interaction shapes and the corresponding section in `revert-and-rollback-discipline.md`. Cross-references from the ops doc are bibliographic per [ADR 0036](0036-expression-contract-for-inward-documents.md).
- Cascade additions to [`cross-references.md`](../operations/cross-references.md): the new ops doc gains rows under "Operations docs → consumers"; this ADR gains a row under "Engine ADRs → consumers"; [`code-discipline.md`](../operations/code-discipline.md) and [`migration-discipline.md`](../operations/migration-discipline.md) gain `See also` pointers to the new sibling.
- [`engine/operations/README.md`](../operations/README.md) index gains a bullet under "Decisions and review". [`../../CLAUDE.md`](../../CLAUDE.md) "Topical pointers" gains a one-line bullet.
- No code changes. The five interactions already have stable, verified shapes; this ADR records that fact + records the rejection of the proposed code changes.
- **No first-exercise readiness note required per [ADR 0053](0053-mechanism-first-exercise-gate.md):** this is a procedural ops doc + ADR, not a cross-cutting mechanism. No new tool wraps a harness gate; no novel cross-session protocol is introduced; no shape-verification logic ships. The trigger criteria do not fire. Mirrors the negative-finding precedent from ADRs 0069, 0070, 0071, 0072, 0073, 0075, 0077 (8th consecutive ADR applying the discipline).

## See also

- [Issue #86](https://github.com/StarshipSuperjam/paideia/issues/86) — analysis-outcome from cross-check of `addyosmani/agent-skills`'s `git-workflow-and-versioning` skill against Paideia practice; closes at S-0140.
- [`engine/operations/revert-and-rollback-discipline.md`](../operations/revert-and-rollback-discipline.md) — Layer 1 source-of-truth this ADR operationalizes.
- [ADR 0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) — routine-mode lifecycle push wrapper; named interaction shape for the eager-claim race.
- [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md) — migration apply wrapper; named interaction shape for in-flight SQL rollback.
- [ADR 0052](0052-routine-boot-freshness-and-concurrency-defense.md) — routine eager-claim recovery; named interaction shape for the narrow recovery.
- [ADR 0076](0076-build-mode-lifecycle-push-wrapping.md) — build-mode lifecycle push wrapper sibling; same `DELIVERABLE_SUBJECT_RE` source.
- [ADR 0077](0077-adr-template-alternatives-considered-section.md) — the "Alternatives Considered" template pattern this ADR dogfoods.
- [ADR 0036](0036-expression-contract-for-inward-documents.md) — bibliographic cross-reference posture; load-bearing for how the new ops doc cross-references migration-discipline.md without duplication.
- [ADR 0041](0041-cascade-discipline-three-validator-checks-plus-manual-procedures.md) — cascade discipline; load-bearing for the future-change posture in Consequences.
- [`engine/operations/adr-authoring.md`](../operations/adr-authoring.md) — Status conventions and supersession chain; named interaction shape.
- [`engine/operations/migration-discipline.md`](../operations/migration-discipline.md) — rollback-migration authorship (cross-referenced, not duplicated).
- [`engine/operations/code-discipline.md`](../operations/code-discipline.md) — sibling sub-discipline.
- [`engine/operations/escalation-criteria.md`](../operations/escalation-criteria.md) — destructive-action rule (the rule the constructive procedure satisfies).
