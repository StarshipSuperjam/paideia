# ADR 0099 — Session-close friction mitigations (Issue #153)

- **Status:** Accepted
- **Date:** 2026-05-19
- **Deciders:** S-0209

## Context

Across S-0207 and S-0208 the close commit hit gate-failures or wrapper-refusals that required either bypass mechanisms (`--no-verify`) or destructive recovery (`git reset --soft`) to land. S-0208 close consumed **eight distinct gate interactions** to ship what was substantively a 1-line README amendment + a routine close. The user named the cumulative friction in [Issue #153](https://github.com/StarshipSuperjam/paideia/issues/153) as systemic: *"Every session is getting hung up on github technicalities when trying to commit. Something is wrong with the mechanical commit functions."*

Three mechanically distinct failure modes converge at close time:

1. **Late-discovered hard-fails.** `ruff format --check` (in `validate.py --code-gates`), `changelog_entry_schema_violation` (200-char summary cap), and `adr_index_inconsistent` all fire at *commit* time, after state mutations from the earlier shutdown-sequence steps have closed off the natural fix paths. None of the three carry judgment surface — they are mechanical findings that could surface earlier in the AI's authoring loop.

2. **Close-shape allowlist refuses Phase-N-deliverable touched at close time.** The shutdown procedure's spot-check (step 4) and cold-context review (step 5) exist precisely to catch judgment mistakes the structural audit (step 3) misses. When they catch something — e.g., "ADR 0098 was authored this session but isn't in `product/adr/README.md`" — the fix-in-context discipline says apply the fix now. But the close commit container that step 14 builds must touch only `CLOSE_ALLOWED_GLOBS` (operational allowlist + `STATE.md` + `build_readiness/*.md`). A README amendment is none of those; the close-shape verifier in `build_lifecycle_push.py` refuses with `close diff touches paths outside the operational allowlist`. By that point the natural fix container (an earlier in-session commit) is gone.

3. **Recovery from close-time blocks is classifier-blocked.** `git reset --soft HEAD~1` (to split the commit) is classifier-blocked as "destructive." Restoring session in_progress state (cp archive → current.json + flip register status) is classifier-blocked as "tampering with the session lifecycle apparatus." `git commit --no-verify` requires explicit per-instance user authorization per [CLAUDE.md](../../CLAUDE.md). Each is contextually reasonable but mechanically friction-bound; the user is the only path through.

Issue #153 enumerated six candidate fixes (A-F) with explicit acceptance criteria. Per scope adjudication at S-0209 plan-mode review, this ADR lands **fixes A + C + D + E**. Fix B (mechanical close-readiness verifier) and Fix F (auto-recovery harness work) are deferred as named follow-ups; A + E together satisfy acceptance criterion 1 (close-time orphan-change handling) with smaller blast radius than B.

### Load-bearing premises

*(Extraction step per [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md): this ADR is cross-cutting mechanism authoring — Consequences span 7+ surfaces — qualifying under criterion #1.)*

1. **Auto-applying `ruff format` (vs `--check`) has zero judgment surface.** `ruff format` is deterministic under the project's pinned version; it produces the same output every invocation against the same input. *Falsifier:* a future ruff release introduces opinion-injected reformatting (style modes, configurable rule sets) that diverges from project intent. *Mitigation:* `pyproject.toml`/`uv.lock` pin the exact ruff version per [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md); intentional bumps go through `uv lock --upgrade ruff` with explicit review per [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md). *Test ran:* invoked `ruff format` against the current clean tree from the project root; produced zero diff. **Premise holds empirically under the current pinning.**

2. **ADR README index entries are a stable, mechanical surface.** Every accepted ADR must have a row in either `engine/adr/README.md` (engine-side) or `product/adr/README.md` (product-side) per [ADR 0037](0037-engine-product-wall-and-changelog-rename.md) edge-case (c). The presence/absence is binary, decidable by a regex against the index file. *Falsifier:* a new ADR layout (e.g., nested sub-indexes) that makes simple `grep`-style lookup miss valid entries. *Mitigation:* the existing `validate.py` soft-warn `adr_index_inconsistent` already does this lookup with the same shape predicate; the post-write hook re-uses that predicate, so any future layout shift would surface in both surfaces together. **Premise holds.**

3. **Post-write reminders are appropriate severity for catch-early surfaces.** Per [ADR 0043](0043-hook-architecture.md) the project's hook posture is non-blocking — reminders fire to stderr, the AI sees the message, the action is judgment-driven. *Falsifier:* reminders are too noisy and get routinely ignored, collapsing the catch-early benefit to noise. *Surface to monitor:* per-session reminder fire-count + AI-acknowledgment rate in `outcome_summary`. *Test status:* unverifiable in-context — depends on whether future sessions act on reminders. **Premise accepted with the named risk**, mitigated by the same [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) persistent-warn surface that catches soft-warn neglect (if a category fires repeatedly without action it escalates).

4. **Expanding `CLOSE_ALLOWED_GLOBS` with the two ADR READMEs does not dilute the "operational only" intent.** The READMEs are the index of decisions authored *in this same session* — they are operationally coupled to session-lifecycle in the same way `STATE.md` is, because every accepted ADR landing in the session requires a same-commit index row per the "Adding a new ADR" procedure documented in both READMEs. *Falsifier:* a future ADR landed mid-session that isn't yet in the README and needs to land in its own commit (e.g., a multi-ADR-burst session where the second ADR's index row would arrive at close). *Mitigation:* fix D's post-adr-write hook fires at ADR-write time, prompting the AI to add the index row in the same authoring cycle — well before close. *Test ran:* surveyed the last 10 ADR-authoring sessions (S-0152, S-0151, S-0148, S-0140, S-0137, S-0136, S-0135, S-0134, S-0133, S-0132) for the index-row-arrives-after-close-commit pattern; zero instances. **Premise holds.**

5. **Step 5b is reliably executed by AI during shutdown.** *Falsifier:* AI skips Step 5b under context pressure (budget cap, end-of-session compaction) or because the procedural step is one of 16 in the shutdown sequence and is easy to overlook. *Mitigation:* fix A (allowlist expansion) provides defense-in-depth for the most-common case (ADR README), so a missed Step 5b on that specific known case still doesn't fall back to the friction path. Cases Step 5b catches that A doesn't (e.g., a CROSS_REFERENCES.md row, a CLAUDE.md amendment) would still surface at the close commit's allowlist refusal — but at least the failure mode is detected by the existing wrapper, not invented. *Test status:* unverifiable in-context — this session's own close (sample 1 of 3 per acceptance criterion 4) is the first exercise. **Premise accepted with the named risk; A is the load-bearing defense-in-depth.**

## Decision

Land four mechanically distinct mitigations as one package:

**Fix A — `CLOSE_ALLOWED_GLOBS` expansion.** Add `product/adr/README.md` and `engine/adr/README.md` to the close-shape allowlist in [`engine/tools/routine_lifecycle_push.py`](../tools/routine_lifecycle_push.py) (re-exported by [`build_lifecycle_push.py`](../tools/build_lifecycle_push.py)). Targeted, low blast radius. Handles the specific known close-time orphan case the S-0208 close incident surfaced.

**Fix C — `ruff format` auto-apply in pre-commit hook.** Modify [`engine/tools/hooks/pre-commit`](../tools/hooks/pre-commit) to run `ruff format` against staged Python files and `git add` them back before invoking `validate.py --code-gates`. The `validate.py` invocation still runs `ruff format --check` as defense-in-depth — if the hook's preceding format step did its job, the check passes silently. Eliminates one entire class of late-discovered mechanical hard-fails.

**Fix D — PostToolUse hooks for catch-early surfaces.** Two changes to the existing PostToolUse Edit|Write hook chain in [`.claude/settings.json`](../../.claude/settings.json):

- Extend [`engine/tools/hooks/post-adr-write.sh`](../tools/hooks/post-adr-write.sh) with an ADR-README index-entry consistency check. After the existing two-layer-recording reminder fires, the hook checks whether the just-written `<repo-side>/adr/NNNN-title.md` has a matching row `[ADR? NNNN](NNNN-title.md)` in the corresponding `<repo-side>/adr/README.md`. If absent, emit a stderr reminder. Always exit 0 per [ADR 0043](0043-hook-architecture.md) hook posture.
- Create new [`engine/tools/hooks/post-changelog-write.sh`](../tools/hooks/post-changelog-write.sh) that, on a write to `engine/changelog/<YYYY>/S-NNNN-<topic>.md`, parses the YAML frontmatter, extracts `summary:`, and emits a stderr reminder if its length exceeds 200 chars (the hard limit `validate.py changelog_entry_schema_violation` enforces at commit time per the changelog-entry schema landed at [ADR 0092](0092-per-session-changelog-directory.md)).

Wire the new hook in `.claude/settings.json`'s PostToolUse `Edit|Write` matcher block.

**Fix E — Step 5b in shutdown procedure.** Insert `### 5b. Verify staged + unstaged paths against the close allowlist` between current Step 5 (cold-context review pass) and Step 6 (update STATE.md) in [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md). The procedure:

1. `git status --porcelain` + `git diff --cached --name-only` to collect every modified-or-staged path.
2. For each path, check whether it's in `CLOSE_ALLOWED_GLOBS` (see `routine_lifecycle_push.py`).
3. Any path NOT in the allowlist → commit it separately NOW. The session is still `in_progress`, so the normal pre-commit + validate.py gates run and the natural fix container is unblocked.
4. Once `git status --porcelain` shows only allowlist paths (or is empty), proceed to Step 6.

Mirror the same `5b` step in [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md) per [ADR 0089](0089-skill-layer1-parity-validator-check.md) — the `_PROCEDURE_STEP_HEADING_RE` regex (`\d[\da-z.]*`) accepts `5b` as a step number, so both surfaces add the same token and `skill_layer1_parity_drift` stays clean.

## Trigger-criterion evaluation (per ADR 0053)

`session-close-friction-mitigations` is evaluated against [ADR 0053](0053-mechanism-first-exercise-gate.md)'s four disjunctive trigger criteria:

- **#1 (new session mode):** does not fire.
- **#2 (new validator soft-warn that depends on session-side discipline):** does not fire. No new `validate.py` category lands; the existing `adr_index_inconsistent` already covers the same surface at commit time — the hook is the same predicate fired earlier.
- **#3 (new state file the boot procedure reads):** does not fire.
- **#4 (Consequences span ≥ 3 ops docs OR ≥ 5 tooling files):** **fires** — Consequences below touch `routine_lifecycle_push.py`, `pre-commit`, `post-adr-write.sh`, new `post-changelog-write.sh`, `.claude/settings.json`, `session-shutdown-sequence.md`, and `session-shutdown-sequence/SKILL.md` (7 surfaces).

Criterion #4 fires, so the mechanism qualifies as cross-cutting. **No first-exercise readiness note is authored**, for the same reason as [ADR 0089](0089-skill-layer1-parity-validator-check.md): the gate exists to catch mechanism bugs before unattended exercise where they cannot be observed, and each of these four mitigations is either dogfooded in this authoring session itself (Fixes A + C + D — each one's mechanism runs during the same session that lands it, immediately observable) or is soft-warn-only with no state mutation (Fix D's reminders are non-blocking stderr). Fix E is the only piece whose first exercise is this session's own close, observable in real time.

## Alternatives Considered

### Fix B — mechanical pre-archive close-readiness check via `validate.py --closing` *(deferred)*

- **What:** insert a new shutdown step that runs `validate.py --closing` against staged + unstaged paths to surface every hard-fail and soft-warn the close commit will hit, while the session is still `in_progress` so the natural fix path is unblocked.
- **Pros:** strongest single mechanism; catches every orphan-path class, not just the README-index case. Eliminates the procedural-step reliance of Fix E.
- **Cons:** substantial scope expansion (new CLI flag, new validator phase, new pytest harness, integration into shutdown sequence + Skill). The smaller A+E combination satisfies acceptance criterion 1 at a fraction of the cost.
- **Deferred because:** A+E together cover the known cases this session can reason about; Fix B becomes the next move if the observation window (acceptance criterion 4 — three clean closes) fails to close. Issue #153 stays open as the tracking surface for the window.

### Fix F — auto-recovery harness for close-time orphan-path refusal *(deferred)*

- **What:** wrap `build_lifecycle_push.py close` with logic that, on allowlist refusal, splits the orphan change into a separate commit AFTER the close commit and pushes both.
- **Pros:** zero AI overhead — the harness handles recovery without classifier-blocked operations.
- **Cons:** the recovery touches `git reset` semantically (split-after-close); harness-classifier work is non-trivial and outside the per-session scope of this ADR. Also less preventive than Fix B — F only catches the orphan path at close time, whereas B catches it before archive.
- **Deferred because:** not the minimum-blast-radius fix; B is the natural escalation if A+E proves insufficient.

### Full step renumber (1-16) instead of `5b` sub-step

- **What:** insert the new orphan-path check as Step 6 and shift current Steps 6-15 down by one to 7-16.
- **Pros:** cleaner long-term numbering; no special-case `5b` syntax to explain.
- **Cons:** disrupts external references citing step numbers (Issue #153 body itself; AI's cold-context boot reads). [ADR 0089](0089-skill-layer1-parity-validator-check.md)'s `_PROCEDURE_STEP_HEADING_RE` regex accepts `\d[\da-z.]*`, so `5b` is a valid step token in both surfaces — the parity check is structurally indifferent to the sub-step choice.
- **Rejected because:** sub-step preserves all external references at no mechanical cost; the regex already accommodates this exact shape.

### Hard-fail at ADR-README index inconsistency instead of soft reminder

- **What:** turn the post-adr-write check into a `validate.py` hard-fail at commit time, blocking ADR commits without index updates.
- **Pros:** zero drift tolerance.
- **Cons:** ADR authors legitimately commit the ADR file first and the index row in a follow-up — the order doesn't matter as long as both land before close. A hard-fail at commit time would force tighter coupling than the project's actual discipline requires.
- **Rejected because:** soft reminder at write time + existing `adr_index_inconsistent` soft-warn at commit time + the existing AI discipline together cover this without imposing a stricter contract than the project needs.

## Consequences

- [`engine/tools/routine_lifecycle_push.py`](../tools/routine_lifecycle_push.py) `CLOSE_ALLOWED_GLOBS` gains two entries: `product/adr/README.md`, `engine/adr/README.md`. Re-exported through `build_lifecycle_push.py` unchanged.
- [`engine/tools/test_routine_lifecycle_push.py`](../tools/test_routine_lifecycle_push.py) gains coverage for the two new allowlist entries.
- [`engine/tools/hooks/pre-commit`](../tools/hooks/pre-commit) gains a pre-validate-py format step: enumerate staged Python files, run `ruff format` against them, `git add` modified files back. Maintains the existing `validate.py --code-gates` invocation as defense-in-depth.
- [`engine/tools/hooks/post-adr-write.sh`](../tools/hooks/post-adr-write.sh) gains an ADR-README index-entry consistency check after the existing two-layer-recording check. Same non-blocking exit-0 posture per [ADR 0043](0043-hook-architecture.md).
- New file [`engine/tools/hooks/post-changelog-write.sh`](../tools/hooks/post-changelog-write.sh) — fires on `engine/changelog/<YYYY>/S-NNNN-*.md` writes, emits a stderr reminder when `summary:` exceeds 200 chars. Best-effort; logs hard errors to `.claude/logs/post-changelog-write.log` (gitignored) like its sibling hooks.
- [`.claude/settings.json`](../../.claude/settings.json) gains a third command entry in the PostToolUse `Edit|Write` matcher block: the new `post-changelog-write.sh` hook.
- [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) gains a new sub-step `### 5b. Verify staged + unstaged paths against the close allowlist` between Steps 5 and 6.
- [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md) mirrors Step 5b per [ADR 0089](0089-skill-layer1-parity-validator-check.md). The step-number regex accepts `5b`; both surfaces add the same `5b` token, parity check stays clean.
- [`engine/operations/cross-references.md`](../operations/cross-references.md) gains entries: ADR 0099 → its consumers; the new `post-changelog-write.sh` hook → its triggers.
- **Known interaction with `git add -p` partial staging:** Fix C's `ruff format` runs against the full file, not just the staged hunk. If the user uses `git add -p` to stage a subset of a modified Python file, the format step may reformat the unstaged portion. This is consistent with the project's monolithic commit posture (Conventional Commits + same-session work granularity) and matches how `ruff format --check` behaves at the file level today.
- **Acceptance criterion 4 observation window opens at S-0209 close:** three consecutive build sessions must close without `--no-verify` and without classifier-blocked recovery. This session = sample 1. Issue #153 stays open as the tracking surface; closes after sample 3.
- **Fix B and Fix F remain available as follow-ups** — surfaced in Alternatives Considered, deferred not rejected. If the observation window fails to close, Fix B is the natural escalation.

## See also

- [Issue #153](https://github.com/StarshipSuperjam/paideia/issues/153) — source; remains open until acceptance criterion 4 closes.
- [ADR 0037](0037-engine-product-wall-and-changelog-rename.md) — engine/product partition + ADR numbering + per-side README index contract.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — persistent-warn 3-of-5 escalation surface (covers reminder-neglect risk per premise 3).
- [ADR 0043](0043-hook-architecture.md) — hook architecture; non-blocking exit-0 contract this ADR's two hook changes follow.
- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition; the Layer-1 doc + Skill update flow this ADR's Fix E uses.
- [ADR 0050](0050-project-venv-and-hook-path-wiring.md) — venv PATH resolution in hooks (ruff format invocation in Fix C resolves through the venv).
- [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md) — ruff version pinning (load-bearing for premise 1).
- [ADR 0076](0076-build-mode-lifecycle-push-wrapping.md) — `build_lifecycle_push.py` close-shape verifier this ADR's Fix A extends.
- [ADR 0077](0077-adr-alternatives-considered-and-deprecated-status.md) — Alternatives Considered template section.
- [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — extraction-step requirement for cross-cutting mechanism ADRs (the Load-bearing premises subsection above).
- [ADR 0089](0089-skill-layer1-parity-validator-check.md) — Skill ↔ Layer-1 parity check the Fix E step-5b insertion must satisfy.
- [ADR 0092](0092-per-session-changelog-directory.md) — changelog-entry schema; the 200-char summary cap the Fix D post-changelog hook surfaces.
