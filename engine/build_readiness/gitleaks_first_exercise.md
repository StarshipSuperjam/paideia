# gitleaks — first-exercise readiness

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Tracks readiness criteria for the gitleaks pre-commit + GitHub-native secret scanning adoption landed at S-0132 per [ADR 0067](../adr/0067-gitleaks-pre-commit-secret-scanning.md) (Issue [#66](https://github.com/StarshipSuperjam/paideia/issues/66)).

## Trigger criteria evaluation

Per ADR 0053 the mechanism qualifies for a readiness note when ANY of:

- ❌ Criterion 1 — introduces new session mode. **No.**
- ❌ Criterion 2 — introduces new validator soft-warn category. **No** in S-0132 — `gitleaks_config_drift` was named by Issue #66 but is deferred per ADR 0067 decision 3 + the plan-approved S-0132 scope discipline.
- ✅ Criterion 3 — introduces new state the boot procedure (or any standing tool) reads. **Yes** — every commit now runs `gitleaks` as a hard-fail gate via the pre-commit hook; the binary's presence and version is a new state surface every session boot implicitly assumes. The pre-commit hook itself surfaces an actionable error if gitleaks is missing.
- ✅ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — `engine/tools/hooks/pre-commit` (extended), `engine/tools/gitleaks.toml` (new), `engine/operations/dependency-discipline.md` (External tool prerequisites subsection added), this readiness note, ADR 0067, plus the GitHub-side enablement = 6 surfaces.

Two criteria satisfied (3 + 4) → readiness note required.

## Mechanism

Three coupled mechanisms landed in this session:

1. **Pre-commit hook step** — `engine/tools/hooks/pre-commit` invokes `gitleaks protect --staged --config engine/tools/gitleaks.toml --redact --no-banner` between the worktree settings.json sync check (line 165) and the code-discipline gates (line 172). Hard-fail blocks commit. Path-resolved via the venv PATH-prepend in `engine/tools/scrub_env.sh` per [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md); gitleaks itself is a Go binary outside the venv, resolved via the system PATH (brew-installed at `/opt/homebrew/bin/gitleaks` on Darwin/arm64).
2. **Project config** — `engine/tools/gitleaks.toml` inherits gitleaks 8.x default rule set via `[extend].useDefault = true` and adds two path-scoped allowlists (`.env.example`, and ADR/operations/build_readiness/ENGINE_LOG paths for canonical fake-secret tokens used in documentation).
3. **GitHub-native secret scanning + push protection** — Enabled via `gh api -X PATCH repos/StarshipSuperjam/paideia` with `security_and_analysis.secret_scanning.status=enabled` + `security_and_analysis.secret_scanning_push_protection.status=enabled`. Server-side defense layer; runs against full history + every push.

## Readiness criteria

### Tier 1 — must close this session

- **T1-A — pre-commit hard-fails on a staged fake secret.** Author a scratch file containing the canonical fake AWS access key (`AKIAIOSFODNN7EXAMPLE` and a 40-char shape secret), attempt a commit, confirm gitleaks hard-fails with the redacted finding line and the commit is blocked. Revert the scratch file. Closes empirically in-session.
- **T1-B — allowlist excludes `.env.example`.** Stage a touch (no-op change) to `.env.example`, attempt a commit, confirm the commit passes the gitleaks step. Closes empirically in-session.
- **T1-C — GitHub-native scanning + push protection enabled.** Round-trip `gh api repos/StarshipSuperjam/paideia --jq '.security_and_analysis'` post-enablement → confirm `secret_scanning.status=enabled` AND `secret_scanning_push_protection.status=enabled`. Record the response payload verbatim in the S-0132 ENGINE_LOG entry. Closes empirically in-session.

### Tier 2 — settle-in-advance, document, non-blocking

- **First false-positive against an unscripted fixture or doc surface.** Track the time-to-first-false-positive and the path that tripped; if it lands on a structural surface the allowlist already covers, no action (false alarm). If it lands somewhere the allowlist does not cover, add an allowlist entry in the triggering commit with an inline reason.
- **First push-protection block against a real secret-shape on a contributor PR.** Server-side defense exercising its purpose. Record the block; the contributor either rotates the secret AND amends the commit, or marks the alert dismissed-as-false-positive with a comment. Procedure cold-documented in this note; close T2 when a natural exercise happens.
- **`gitleaks_config_drift` soft-warn (deferred).** Issue #66 named the soft-warn but ADR 0067 decision 3 + plan-approved S-0132 scope deferred it. File an enhancement Issue at session close; readiness for the soft-warn lands when the Issue is picked up.

### Tier 3 — named-and-deferred forward-pointers

- **Major-version bump (8.x → 9.x).** Gitleaks 9.x will change the config schema. The forensic version pin `8.30.1` is recorded in ADR 0067 decision 2; an amendment to ADR 0067 is required before bumping.
- **`secret_scanning_non_provider_patterns` enablement.** GitHub's generic high-entropy string detector. Today the false-positive volume is not warranted; re-evaluate at the first real-shaped-but-missed secret leak or when the engine surfaces a custom secret format that no provider knows.
- **`secret_scanning_validity_checks` enablement.** Live validation against provider APIs. Requires consent to outbound provider calls. Re-evaluate when production credentials exist (post-Phase 6 backend auth surface).
- **Secret-rotation procedure.** Detection only today; rotation procedure lands alongside the first real production-credential surface.

## Status

- **T1-A — closed at S-0132 (empirically verified).** A scratch fixture `_gitleaks_test_scratch.txt` was authored with a non-canonical fake AWS pair (`AKIAZ7XJTESTKEYAAAAA` + a 40-char shape secret). `git add` succeeded; `git commit` triggered the pre-commit hook's new gitleaks step → gitleaks scanned the staged 187-byte diff in ~26ms and reported `leaks found: 1`; the hook printed `[pre-commit] gitleaks detected a secret in the staged diff. Commit blocked.` + the redacted finding + the ADR pointer + the allowlist guidance line; the commit did NOT land (`git log -1` still showed `7ee6271` post-test). Scratch unstaged + deleted; working tree clean. Test against post-FF hook at SHA `7ee6271`.
- **T1-B — closed at S-0132 (empirically verified).** A placeholder-shaped AWS access-key value (`AKIAIOSFODNN7AAAAAA`) was temporarily appended to `.env.example`, staged, and scanned via `gitleaks protect --staged --config engine/tools/gitleaks.toml --redact --no-banner`. Result: `scanned ~88 bytes ... no leaks found`, exit 0 — the `.env.example` path-scoped allowlist correctly suppressed the otherwise-flaggable placeholder. The change was unstaged + reverted; working tree clean post-test. Allowlist behavior verified against post-FF hook at SHA `7ee6271`.
- **T1-C — closed at S-0132 (empirically verified).** `gh api -X PATCH repos/StarshipSuperjam/paideia` with `security_and_analysis.secret_scanning.status=enabled` + `security_and_analysis.secret_scanning_push_protection.status=enabled` returned 200; round-trip `gh api repos/StarshipSuperjam/paideia --jq '.security_and_analysis'` confirms:
  ```json
  {"dependabot_security_updates": {"status": "disabled"},
   "secret_scanning": {"status": "enabled"},
   "secret_scanning_non_provider_patterns": {"status": "disabled"},
   "secret_scanning_push_protection": {"status": "enabled"},
   "secret_scanning_validity_checks": {"status": "disabled"}}
  ```
  `dependabot_security_updates: disabled` is intentional — Issue [#67](https://github.com/StarshipSuperjam/paideia/issues/67) Dependabot adoption is a separate Tier 1 item (next eligible after S-0132 closes). `non_provider_patterns` + `validity_checks: disabled` per ADR 0067 decision 4 (false-positive volume + outbound-call consent not warranted today).

## Risk surface (deliberate posture)

**External-tool-missing risk.** If gitleaks is uninstalled on a maintainer machine (clone-without-brew, OS reinstall, etc.) the pre-commit hook hard-fails every commit with installation guidance. Mitigation: the failure message names the brew install command and points at ADR 0067 + `engine/operations/dependency-discipline.md`. Worst case: maintainer reads the message and runs the install. Not silent.

**False-positive blocking real work.** A doc edit that legitimately cites a real-shaped fake key on a path NOT in the allowlist hard-fails the commit. Mitigation: the allowlist covers `engine/adr/`, `engine/operations/`, `engine/build_readiness/`, `engine/ENGINE_LOG.md`, and `product/adr/`. New ADR or operations-doc paths added to the project are auto-covered; ad-hoc fixture additions outside those paths require an allowlist entry in the same commit. The allowlist entry's inline reason satisfies the no-silent-suppression discipline.

**Push-protection bypass.** Push protection can be bypassed by the contributor via the `--push-option=secret-scanning-bypass=...` flag with a category (false-positive, used-in-tests, will-rotate-soon). The bypass is logged at GitHub and surfaces in the Security tab. Solo-dev today; revisit when a second collaborator joins ([Issue #80](https://github.com/StarshipSuperjam/paideia/issues/80) CODEOWNERS trigger).

**Config-drift surface.** `engine/tools/gitleaks.toml` is a new file. A drift from intent (a future commit that broadens the allowlist beyond its inline reasons) is reviewer-attention-only today. The deferred `gitleaks_config_drift` soft-warn (Issue #66 named it; ADR 0067 decision 3 documents the deferral) will mechanize this when authored.

## Cross-references

- [ADR 0067](../adr/0067-gitleaks-pre-commit-secret-scanning.md) — the contract.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the gate itself.
- [ADR 0068](../adr/0068-bandit-sast-pre-commit-and-ci.md) — Pairing A sibling (bandit SAST).
- [`engine/tools/gitleaks.toml`](../tools/gitleaks.toml) — config.
- [`engine/tools/hooks/pre-commit`](../tools/hooks/pre-commit) — host hook.
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — External tool prerequisites.
- [Issue #66](https://github.com/StarshipSuperjam/paideia/issues/66) — closes.
- [Issue #80](https://github.com/StarshipSuperjam/paideia/issues/80) — re-evaluate push-protection bypass posture when this triggers.
