---
session_id: S-0209
session_type: build
closed_at: "2026-05-19T15:05:00Z"
material_change_class: mixed
module: multi
summary: Issue #153 fix package (ADR 0099 + Fix A/C/D/E). Allowlist widened, ruff format auto-apply, post-write reminders, Step 5b. Issue #154 filed.
---

# S-0209 — Issue #153 session-close friction mitigations — 2026-05-19

Engine ADR 0099 + four mechanically distinct mitigations addressing the close-friction failure modes [Issue #153](https://github.com/StarshipSuperjam/paideia/issues/153) quantified across S-0207 + S-0208 closes (~14 distinct gate interactions, `--no-verify` + classifier-blocked recovery required to land what was substantively a few README amendments and routine closes). Diverted from the originally-planned Cluster 4 work item because Issue #153 carried `priority:urgent`. Fix B (mechanical close-readiness verifier) + Fix F (auto-recovery harness) named in Alternatives Considered as deferred follow-ups.

## Added

- **[`engine/adr/0099-session-close-friction-mitigations.md`](../../adr/0099-session-close-friction-mitigations.md)** — cross-cutting mechanism authoring (Consequences span 7 surfaces), triggers ADR 0084 extraction step. 5 load-bearing premises authored: (1) `ruff format` deterministic under pinned version (tested in-context: zero diff on clean tree); (2) ADR README index entries are a stable mechanical surface (predicate matches the existing `adr_index_inconsistent` soft-warn); (3) post-write reminders are appropriate severity per ADR 0043 (mitigation: ADR 0042 persistent-warn 3-of-5 escalation); (4) ADR-README addition to `CLOSE_ALLOWED_GLOBS` doesn't dilute "operational only" intent (tested via last-10-ADR-session survey: zero counter-examples); (5) Step 5b reliable execution (mitigated by Fix A defense-in-depth for known case). Trigger-criterion evaluation per ADR 0053: criterion #4 fires (7 surfaces); first-exercise readiness note NOT authored because all four mitigations are dogfooded in this same session.
- **Index row in [`engine/adr/README.md`](../../adr/README.md)** for ADR 0099.
- **[`engine/tools/hooks/post-changelog-write.sh`](../../tools/hooks/post-changelog-write.sh)** — new PostToolUse hook (Fix D part 2). Fires on `engine/changelog/<YYYY>/S-NNNN-*.md` writes, parses YAML frontmatter, extracts `summary:`, emits stderr reminder if length > 200 chars (the cap `validate.py changelog_entry_schema_violation` enforces at commit time). Non-blocking exit-0 per ADR 0043.
- **[`engine/tools/test_hooks_post_write.py`](../../tools/test_hooks_post_write.py)** — 8 pytests covering both post-write hooks against tmp-dir git repos with synthetic JSON payloads (4 for ADR-index reminder: miss/hit/partition-routing/link-prefix-form; 4 for changelog summary: over-cap/within-cap/non-changelog-path-skip/summary-absent).
- **engine_memory drawers**: decisions `c0ec3dfc` (ADR 0099 conversational reasoning + A+E scope adjudication); pushback `fcd3e824` (user reframe "Wasn't this whole session to prevent things just like this?" — name sibling failure modes you didn't anticipate during fix-package sessions); lesson `1e3071aa` (worktrees share parent .git/hooks/ via symlink — hook content edits don't take effect in worktree commits until main repo's working tree FFs); diary `c2dfb077`.
- **[Issue #154](https://github.com/StarshipSuperjam/paideia/issues/154)** filed mid-session — `check_settings_sync.py` bidirectional-assumption bug. The check assumes the harness wrote to main repo's `.claude/settings.json` and worktree's copy is stale; in S-0209's case the worktree's copy was the canonical correct version and main was stale. Auto-mode classifier denied both sync directions; user authorized inverse-direction cp manually. Sibling failure mode in Issue #153's same class but not in the Issue body's enumerated three.

## Changed

- **[`engine/tools/routine_lifecycle_push.py`](../../tools/routine_lifecycle_push.py)** — Fix A: `CLOSE_ALLOWED_GLOBS` widened by two entries — `engine/adr/README.md` + `product/adr/README.md`. Inline rationale comment cites ADR 0099 + the S-0208 incident. Bounded scope: only the two index files themselves; arbitrary edits elsewhere under `engine/adr/` or `product/adr/` (ADR file authoring) still require their own in-session commits.
- **[`engine/tools/test_routine_lifecycle_push.py`](../../tools/test_routine_lifecycle_push.py)** — Fix A: `test_close_allowed_globs_derived_from_canonical_operational_allowlist` extended to assert both new entries with rationale citations; new `test_close_accepts_adr_readme_edit` exercises a close commit touching both README files (6/6 close-shape tests pass).
- **[`engine/tools/hooks/pre-commit`](../../tools/hooks/pre-commit)** — Fix C: auto-apply `ruff format` against staged Python files and `git add` them back BEFORE invoking `validate.py --code-gates`. Downstream `--code-gates` still runs `ruff format --check` as defense-in-depth. Eliminates one entire class of late-discovered hard-fails at commit time. Plus defense-in-depth `scrub_env.sh` sourcing (per ADR 0050) so bare `ruff`/`python3`/`mypy` invocations resolve via the project venv's PATH (other hooks already source this; pre-commit historically relied on parent-shell PATH). Known interaction: ruff format runs against full file, not just staged hunk — documented in ADR 0099 Consequences.
- **[`engine/tools/hooks/post-adr-write.sh`](../../tools/hooks/post-adr-write.sh)** — Fix D part 1: new ADR-README index consistency check inserted after the existing two-layer-recording check. Routes by partition: engine ADRs check `engine/adr/README.md`, product ADRs check `product/adr/README.md` (per ADR 0037 wall). Accepts both `[NNNN](NNNN-foo.md)` and `[ADR NNNN](NNNN-foo.md)` link conventions. Non-blocking exit-0; reminder fires on miss, silent on hit.
- **[`.claude/settings.json`](../../../.claude/settings.json)** — PostToolUse `Edit|Write` matcher block extended with `engine/tools/hooks/post-changelog-write.sh` alongside the existing `post-adr-write.sh` + `post-state-edit.sh`.
- **[`engine/operations/session-shutdown-sequence.md`](../../operations/session-shutdown-sequence.md)** — Fix E: new sub-step `### 5b. Verify staged + unstaged paths against the close allowlist` inserted between cold-review (step 5) and STATE.md update (step 6). Procedural backstop — AI executes a one-shot Python invocation of `check_routine_scope.matches_any` against `CLOSE_ALLOWED_GLOBS` for each modified/staged/untracked path; commits any out-of-allowlist path separately while still `in_progress`.
- **[`.claude/skills/session-shutdown-sequence/SKILL.md`](../../../.claude/skills/session-shutdown-sequence/SKILL.md)** — Fix E mirror: Step 5b mirrored per ADR 0089 Skill ↔ Layer-1 parity contract. `_PROCEDURE_STEP_HEADING_RE` regex (`\d[\da-z.]*`) accepts `5b` as a step token; both surfaces now have step-number set `{1,2,3,4,5,5b,6,7,8,8a,8b,9,10..15}`; `skill_layer1_parity_drift` does not fire; 15/15 parity tests pass including `real_repo_smoke`.

## Observability

- **Issue #153 acceptance criterion 4 observation window opened at this close.** 3 consecutive build sessions must close without `--no-verify` and without classifier-blocked recovery before the Issue closes. This session = sample 1.
- **First natural exercise of Step 5b** during S-0209's own close: `git status --porcelain` showed only `engine/session/current.json` modified (operational allowlist member); `verify_close_shape` accepted; no orphan path required separate commit.

## Soft-warns / notable surface

- **`engine_memory_zero_citations_after_search`** fired at `validate.py --final-check`: 1 search call at boot but no drawer IDs surfaced in outcome_summary/diary/commit-messages at that point. Cleared after diary write + outcome_summary fill (which cite the drawer IDs).
- The same `issue_collision` soft-warn fired 8-9 times per commit on every commit this session, all keyword-matching to Issue #153 (correctly) plus 7-8 false positives (Issues with keywords like "pre-commit", "include", "product", etc.). Expected behavior; not a defect.
