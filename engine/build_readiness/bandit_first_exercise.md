# bandit SAST — first-exercise readiness

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Tracks readiness criteria for the bandit pre-commit + CI SAST gate landed at S-0132 per [ADR 0068](../adr/0068-bandit-sast-pre-commit-and-ci.md) (Issue [#70](https://github.com/StarshipSuperjam/paideia/issues/70)).

## Trigger criteria evaluation

Per ADR 0053 the mechanism qualifies for a readiness note when ANY of:

- ❌ Criterion 1 — introduces new session mode. **No.**
- ❌ Criterion 2 — introduces new validator soft-warn category. **No** (bandit gates via its own exit code, not validate.py categories).
- ✅ Criterion 3 — introduces new state the boot procedure (or any standing tool) reads. **Yes** — every commit now runs `bandit` as a hard-fail gate via the pre-commit hook; the venv must contain bandit (currently resolved to 1.9.4 per `uv.lock`). The pre-commit hook surfaces an actionable `uv sync` error if bandit is missing.
- ✅ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — `engine/tools/hooks/pre-commit` (extended), `engine/tools/bandit.yaml` (new), `.github/workflows/validate.yml` (extended), `pyproject.toml` (bandit dep added), `uv.lock` (regenerated), 6 production-tool + 4 test files refactored or annotated for nosec placement, ADR 0068, this readiness note = >10 surfaces.

Two criteria satisfied (3 + 4) → readiness note required.

## Mechanism

Three coupled mechanisms landed in this session:

1. **Pre-commit hook step** — `engine/tools/hooks/pre-commit` invokes `uv run bandit -c engine/tools/bandit.yaml -ll -ii -q <STAGED_PY>` after the gitleaks step and before the code-discipline gates. Hard-fail blocks commit. STAGED_PY discovered via `git diff --cached --diff-filter=ACMR` filtered to `^engine/.*\.py$` (same shape as the existing code-gates discovery). Silent no-op when no Python staged.
2. **Project config** — `engine/tools/bandit.yaml` skips B101 (assert_used) globally (pytest convention). `assert_used.skips` exempts `**/test_*.py` + `**/*_test.py` as defense-in-depth. No `exclude_dirs` or `tests` whitelist; the inline `# nosec` discipline handles per-finding decisions.
3. **CI step** — `.github/workflows/validate.yml`'s `validate.py` job gains `Run bandit SAST on engine/ + product/seed-graph/` running `uv run bandit -r engine/ product/seed-graph/ -c engine/tools/bandit.yaml -ll -ii -q`. Full-tree scan; hard-fail.

## Readiness criteria

### Tier 1 — must close this session

- **T1-A — pre-commit hard-fails on a staged file containing `eval()`.** Author a scratch Python file containing `def f(s): return eval(s)`, stage it, attempt a commit, confirm bandit hard-fails with B307 (`use_of_eval`) finding at HIGH/HIGH and the commit is blocked. Revert. Closes empirically in-session.
- **T1-B — CI step lights up green on the deliverable push.** After the bandit deliverables land in HEAD and main FF's, observe the GitHub Actions `validate.py` job for the bandit step; confirm it concludes successfully (corpus is clean at gate threshold per the baseline triage in ADR 0068 Empirical record). Closes empirically in-session post-FF.

### Tier 2 — settle-in-advance, document, non-blocking

- **First natural CI-red bandit step on `main`.** A future commit that introduces a B-rule trigger (semantic vulnerability) lands red on CI. Cleanup-session signal per the existing `engine/tools/hooks/session-start.sh` CI-red surface (per ADR 0065 engine). Record the trigger + the fix.
- **First inline `# nosec` annotation added post-S-0132 baseline.** Track the time-to-first-new-annotation. If the rate is low (1-2/quarter), the discipline is holding. If it's high (every session adds annotations), the gate may be too strict OR a code-pattern that bandit dislikes is becoming pervasive; re-evaluate.
- **Bandit version drift.** uv.lock pins the exact version; pyproject.toml floor pin is `>=1.7.0`. Major-version bumps require ADR amendment (rule set changes can introduce new finding categories that need triage).

### Tier 3 — named-and-deferred forward-pointers

- **B-rule additions in future bandit releases.** Bandit periodically adds new checkers (e.g., recent additions for `jinja2.Template(autoescape=False)`, `Flask debug=True`). A bandit minor-version bump that adds a new active rule may trigger findings on existing code. Discipline: run `uv run bandit -r engine/ product/seed-graph/ -c engine/tools/bandit.yaml -ll -ii` post-bump, triage findings (fix or `# nosec` with reason), then bump.
- **Bandit on Phase 9 SwiftUI codebase.** Bandit is Python-only. iOS native code SAST would be its own adoption (SwiftLint security rules, Periphery, etc.), gated on Phase 9 entry per ADR 0065 product.
- **Coverage gate composition with #71 pytest-cov.** Bandit's coverage of the engine corpus is one signal; #71 will add another (test coverage). Both gates compose in the same `validate.py` job. Re-evaluate the 10-minute pipeline budget per ADR 0065 decision 4 if the combined runtime crosses 5 minutes.

## Status

- **T1-A** — *to close empirically post-FF.* (Hook gains the bandit step only after the bandit-deliverables commit is FF'd into the parent repo's working tree.)
- **T1-B** — *to close empirically post-FF.* (CI runs on the FF'd push.)

(Both Tier-1 criteria close before S-0132 archives. This file is updated with the verification SHAs and CI run IDs as each closes.)

## Risk surface (deliberate posture)

**Bandit-rule-add risk.** Future bandit minor-version bumps may add new rules that fire on existing code. Mitigation: dependency-discipline.md's lockfile pin keeps the rule set stable until intentional bump. The bump itself is a triage moment (run the gate, fix or annotate, bump).

**False-positive accumulation risk.** As `# nosec` annotations accumulate, the meaning of "this corpus is safe" weakens. Mitigation: the inline-reason discipline keeps each annotation auditable; a future health-check audit per ADR 0022 can sweep all `# nosec` annotations to validate the reasons still apply. Tracked in Tier 2 ("first inline `# nosec` post-S-0132").

**LOW-finding-blindness risk.** Gate threshold `-ll -ii` filters LOW-severity findings (B101 / B404 / B603 / B607 / B112 / B606 / B110 — bandit's 244-finding baseline below threshold). A genuinely-bad LOW finding could land without surface. Mitigation: each below-threshold class is reviewed in ADR 0068 decision 4; bandit categorizes the actually-actionable classes (B307 eval, B306 mktemp, B311 random for cryptography, B321 ftplib, B501-505 ssl/tls misconfig, B608 SQL, B105 hardcoded password, etc.) as MEDIUM+ severity by design.

**Refactor-for-nosec-placement risk.** Three production-tool functions were refactored (extract SQL into a named variable) to put `# nosec B608` on the line bandit flags. The refactor is shape-preserving (241 tests pass post-refactor) but introduces churn. Future refactors of the same pattern should preserve the named-`sql` variable. Forward note for reviewers in the affected files: `audit_mempalace_attribution.attribute_drawer_metadata`, `mempalace_rebuild_hnsw.fetch_metadata_rows`, `prune_mempalace.enumerate_paideia_mined_internal_ids` + `fetch_embedding_uuids` + `fetch_uuids_by_collection`.

**CI runtime budget risk.** Current bandit full-tree scan ~2s on 32K LoC. Combined with the existing `validate.py` default + `--code-gates` + `pytest` jobs, the `validate.py` job is ~2.5 min cold / ~30s cached. Adding bandit pushes it to ~2.7 min. Within the 10-minute budget; re-evaluate at Phase 6 entry when the corpus is larger.

## Cross-references

- [ADR 0068](../adr/0068-bandit-sast-pre-commit-and-ci.md) — the contract.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the gate itself.
- [ADR 0067](../adr/0067-gitleaks-pre-commit-secret-scanning.md) — Pairing A sibling (gitleaks).
- [ADR 0064](../adr/0064-uv-lockfile-and-reproducible-builds.md) — bandit pinned in `pyproject.toml` + `uv.lock`.
- [ADR 0065 (engine)](../adr/0065-validate-py-mirror-to-ci.md) — CI mirror (this gate extends the workflow).
- [`engine/tools/bandit.yaml`](../tools/bandit.yaml) — config.
- [`engine/tools/hooks/pre-commit`](../tools/hooks/pre-commit) — host hook.
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — refresh procedure.
- [Issue #70](https://github.com/StarshipSuperjam/paideia/issues/70) — closes.
- [Issue #71](https://github.com/StarshipSuperjam/paideia/issues/71) — composes with this gate in the same CI job.
