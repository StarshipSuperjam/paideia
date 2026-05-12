# ADR 0067 — `gitleaks` pre-commit secret scanning + GitHub-native scanning

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0132

## Context

Pre-S-0132, Paideia's secret hygiene relies on three layers: `.env*` gitignored, `.env.example` committed as the variable surface, and human review. There is no automated secret scanner anywhere in the pipeline. A `git add -f .env` slip, a forgotten test-fixture credential, a debug-print of an env var captured in a tracked log, or a leaked key in a migration comment all bypass current defenses.

The repo went OSS (Apache 2.0) + publicly visible at S-0130 per [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md), which raises the cost of a leak — anyone reading GitHub at the moment of leak captures the secret. Pre-Phase-6 there are no production credentials yet (BYOK shifts the Anthropic key to the user's iOS Keychain per ADR 0065 product commitment 4), but engine-side build tooling already touches a Supabase service-role pooler URL via `SUPABASE_DB_URL` for the Phase 4+ live-graph audit per [ADR 0016](0016-graph-construction-needs-live-validation.md). One commit-by-accident of a populated `.env` exposes the service-role URL.

[Issue #66](https://github.com/StarshipSuperjam/paideia/issues/66) named the adoption as Tier 1 of the SWE-hardening rollout; Pairing A bundles this with [Issue #70](https://github.com/StarshipSuperjam/paideia/issues/70) bandit per the rollout table in `engine/STATE.md` because both extend the pre-commit hook + tooling config + add a first-exercise readiness note. Pairing A unblocks once [Issue #65](https://github.com/StarshipSuperjam/paideia/issues/65) lockfile (closed at S-0127 per ADR 0064) and [Issue #68](https://github.com/StarshipSuperjam/paideia/issues/68) CI mirror (closed at S-0131 per ADR 0065 engine) are in. Both are in.

Pattern source: [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) `pre-commit-config.yaml` cites `gitleaks` as the canonical secret scanner; [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) `ci-cd-and-automation` reinforces the two-layer (pre-commit + GitHub-native) approach.

## Decision

Two layers landing in the same session per Issue #66's "both must land in the same session" stipulation. Five coupled choices mechanize the adoption.

### 1. `gitleaks` pre-commit step before code-discipline gates

The pre-commit hook (`engine/tools/hooks/pre-commit`) gains a new step between the worktree settings.json sync check (line 165) and the code-discipline gates (line 172). Invocation:

```bash
gitleaks protect --staged --config engine/tools/gitleaks.toml --redact --no-banner
```

- `protect --staged` scans the staged diff (not the full tree, not history) — fastest fail-fast on the in-flight commit.
- `--config engine/tools/gitleaks.toml` pins the rule set to the project's config (inherits defaults + project allowlist; see decision 3).
- `--redact` masks any detected secret value in stderr so the secret itself does not land in the local terminal scrollback or in the CI step log.
- `--no-banner` suppresses the ASCII-art banner from gitleaks' default output.
- Hard-fail (non-zero exit) blocks the commit with stderr guidance pointing at this ADR + `gitleaks.toml`.

The hook checks `command -v gitleaks` first and hard-fails with installation guidance if gitleaks is absent — the binary is a project prerequisite, not a Python dep, so it cannot be installed via `uv sync`.

### 2. Version pin: gitleaks 8.30.1 via `brew install gitleaks`

Installation path documented in `engine/operations/dependency-discipline.md` "External tool prerequisites" subsection (authored in the same commit). The pin is 8.30.1 — the version installed at S-0132 against the Darwin/arm64 Homebrew bottle. Recorded forensically: future sessions verify with `gitleaks version`; substantive version drift (8.x → 9.x major bump) requires an ADR amendment because the config schema changes across major versions.

Alternative paths considered + rejected:
- `go install github.com/gitleaks/gitleaks/v8@vX.Y.Z` — works but requires Go toolchain on every maintainer machine; brew avoids the toolchain.
- Vendored binary committed under `engine/tools/` — repo bloat (15.4 MB), platform-specific, defeats reproducible-builds (the binary cannot be regenerated from source pin alone).
- Python `gitleaks-py` wrapper — not maintained, wraps the Go binary at runtime anyway.

### 3. Config inherits defaults + project allowlist; allowlist entries are individually justified

`engine/tools/gitleaks.toml` (authored in this session) sets `[extend].useDefault = true` so the gitleaks 8.x bundled rule set (AWS / GCP / Azure / Anthropic / OpenAI / Slack / GitHub / Stripe / generic-API-key + ~100 more) is the baseline. Two project-specific `[[allowlists]]` blocks layer on top:

- **`.env.example` path-scoped allowlist** — guards against future placeholder additions (`AWS_KEY=your_key_here`) tripping shape-matchers. The current `.env.example` is variable-name-only with empty values, but the allowlist is forward-defense.
- **Documentation + ADR + readiness-note path-scoped allowlist for canonical AWS docs example token** — `AKIAIOSFODNN7EXAMPLE` is AWS's own documentation example; gitleaks recognizes the shape and flags it. ADRs, operations docs, build_readiness notes, and ENGINE_LOG legitimately cite it (this ADR is one such file).

Adding a new allowlist entry requires the same-session inline comment naming the reason. Silent allowlist suppressions accumulate and lose meaning — the same posture as bandit's rule-skip discipline per [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md) decision 4.

### 4. GitHub-native secret scanning + push protection

Enabled via `gh api -X PATCH repos/StarshipSuperjam/paideia --input -` with the JSON body:

```json
{
  "security_and_analysis": {
    "secret_scanning": {"status": "enabled"},
    "secret_scanning_push_protection": {"status": "enabled"}
  }
}
```

Two distinct features:

- **Secret scanning** scans the full repo history and every new push against GitHub's partner-provided detector set (broader than gitleaks' bundled rules; covers provider-validated tokens that gitleaks shape-matches but doesn't validate). Alerts surface in the repo Security tab.
- **Push protection** blocks pushes that introduce a partner-recognized secret pattern. Server-side defense for any clone that bypasses local pre-commit (other contributors, CI-only pushes, web-UI commits).

Both are free for public OSS repos under GitHub Advanced Security's free tier. Verify activation with `gh api repos/StarshipSuperjam/paideia --jq '.security_and_analysis'` round-trip read; record the response payload verbatim in the session's ENGINE_LOG entry.

`secret_scanning_non_provider_patterns` (generic high-entropy strings) and `secret_scanning_validity_checks` (live-validation against provider APIs) are NOT enabled in this session — the former produces high false-positive volume; the latter requires consent to outbound provider calls. Deferred trigger: re-evaluate at the first false-positive surface or when a second collaborator joins.

### 5. CI defense-in-depth: no separate CI step for gitleaks

GitHub-native scanning runs on every push to `main` and every PR; it is the CI-layer secret-scan. Adding a `gitleaks` step to `.github/workflows/validate.yml` would duplicate the surface and slow the 10-minute budget for no marginal coverage. The two-layer defense is pre-commit + GitHub-native; no third layer.

Bandit's [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md) decision 5 takes the opposite stance — bandit IS added as a CI step — because bandit operates on code shape (catches `eval()`, `shell=True`) where GitHub provides no equivalent server-side scan. The two adoptions diverge here deliberately.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

gitleaks adoption qualifies as cross-cutting and requires a first-exercise readiness gate:

- ❌ Criterion 1 — new session mode. **No.**
- ❌ Criterion 2 — new validator soft-warn category. **No** in this session — the `gitleaks_config_drift` soft-warn named in Issue #66 is deferred per decision 3 + the plan-approved scope discipline. Captured as a follow-up enhancement Issue at session close if wanted.
- ✅ Criterion 3 — new state the boot procedure (or any standing tool) reads. **Yes** — every commit now runs `gitleaks` as a hard-fail gate; the binary's presence and version is a new state surface every session boot implicitly assumes. The pre-commit hook itself surfaces an actionable error if gitleaks is missing.
- ✅ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — `engine/tools/hooks/pre-commit` (extended), `engine/tools/gitleaks.toml` (new), `engine/operations/dependency-discipline.md` (External tool prerequisites subsection added), `engine/build_readiness/gitleaks_first_exercise.md` (new), this ADR, plus the GitHub-side enablement = 6 surfaces.

Two criteria satisfied (3 + 4) → readiness note required. Authored at [`engine/build_readiness/gitleaks_first_exercise.md`](../build_readiness/gitleaks_first_exercise.md).

### Other consequences

- **Positive — secret-leak defense at three layers.** `.gitignore` + `gitleaks` pre-commit + GitHub-native scanning + push protection. A leak requires all four to fail.
- **Positive — pre-commit fail-fast.** gitleaks runs on the staged diff (millisecs) before the more-expensive code-discipline gates. The cheapest gate is the first gate.
- **Positive — pairing with [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md).** Defense-in-depth: gitleaks catches *committed secrets*; bandit catches *insecure-pattern code* that creates exploit-class antipatterns. Both extend the same pre-commit hook; both pair-land in S-0132.
- **Positive — external-contributor protection.** Push protection prevents a future contributor from inadvertently committing a secret to a PR branch (their push is server-side rejected).
- **Cost — every maintainer machine needs gitleaks installed.** Documented in `engine/operations/dependency-discipline.md` "External tool prerequisites". The pre-commit hook fail-fast with installation guidance mitigates discoverability.
- **Cost — false-positive risk on fixture additions.** A future test fixture or doc edit that contains a real-shaped fake key (e.g., a tutorial on what a Stripe key looks like) trips the gate. Mitigation: the path-scoped allowlist for `engine/adr/`, `engine/operations/`, `engine/build_readiness/`, and `engine/ENGINE_LOG.md` covers the documented surface; ad-hoc fixtures add an allowlist entry in the same commit.
- **Cost — config-drift surface.** `engine/tools/gitleaks.toml` is a new file that can drift from intent. The forthcoming `gitleaks_config_drift` validate.py soft-warn (deferred to a follow-up Issue) detects co-edits of `.env*` and `gitleaks.toml` in the same commit (a shape that suggests allowlist tampering). Until that lands, reviewer attention is the only check.
- **Out-of-scope — secret rotation procedure.** This ADR adds detection; rotation is downstream. Will land alongside the first real Phase 6+ secret surface.
- **Out-of-scope — `gitleaks_config_drift` soft-warn.** Issue #66 named it; deferred per the plan-approved S-0132 scope discipline. Captured as a follow-up enhancement Issue at session close.
- **Out-of-scope — `secret_scanning_non_provider_patterns` and `secret_scanning_validity_checks`.** Generic-string and provider-validation features deferred per decision 4 — high false-positive volume + outbound-call consent are not warranted today.

### Empirical record of GitHub-native enablement

Pre-S-0132 `gh api repos/StarshipSuperjam/paideia --jq '.security_and_analysis'` returned all features `disabled`:

```json
{
  "dependabot_security_updates": {"status": "disabled"},
  "secret_scanning": {"status": "disabled"},
  "secret_scanning_non_provider_patterns": {"status": "disabled"},
  "secret_scanning_push_protection": {"status": "disabled"},
  "secret_scanning_validity_checks": {"status": "disabled"}
}
```

Post-enablement read-back recorded in the S-0132 ENGINE_LOG entry; the gitleaks first-exercise readiness note captures the round-trip verification under T1-C.

## See also

- [ADR 0038](0038-three-layer-expression-contract-ai-authored-code.md) — three-layer expression contract; this gate is Layer 2 sibling for the secret-scan surface.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle (the future `gitleaks_config_drift` category will surface here).
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; this adoption qualifies.
- [ADR 0065 (engine)](0065-validate-py-mirror-to-ci.md) — CI mirror (which intentionally does NOT add a gitleaks step per decision 5).
- [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md) — Pairing A sibling; bandit SAST.
- [`engine/build_readiness/gitleaks_first_exercise.md`](../build_readiness/gitleaks_first_exercise.md) — first-exercise readiness note.
- [`engine/tools/gitleaks.toml`](../tools/gitleaks.toml) — config file.
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — External tool prerequisites subsection (gitleaks install).
- [Issue #66](https://github.com/StarshipSuperjam/paideia/issues/66) — closes.
- Pattern source: `affaan-m/everything-claude-code` `pre-commit-config.yaml`; `addyosmani/agent-skills` `ci-cd-and-automation`.
