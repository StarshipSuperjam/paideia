# ADR 0071 — Project-wired `/security-review` skill (OWASP Top 10 + Paideia overlays)

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0134

## Context

Pre-S-0134, Paideia's security posture has three pre-commit / CI gates: gitleaks ([ADR 0067](0067-gitleaks-pre-commit-secret-scanning.md)) catches committed secrets, bandit ([ADR 0068](0068-bandit-sast-pre-commit-and-ci.md)) catches insecure-pattern code (B-codes), Dependabot ([ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md)) catches vulnerable dependency versions. None of the three walks a full OWASP Top 10 checklist with measurable thresholds (bcrypt rounds ≥ 12, JWT verification order signature→expiration→issuer→audience, CSP `default-src 'self'` baseline, parameterized queries enforced semantically). None checks Paideia-specific overlays: Supabase RLS policies are *semantically* correct (not just present per `validate.py`'s structural soft-warn), `apply_migration.py` Layer 2.5 postcondition-assertion blocks are present and sensible (per [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md) post-S-0094 contract), MemPalace + KG writes do not carry credentials or PII (a concern that escalated at S-0130's OSS-flip per [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md) when the repo became world-readable).

The global `/security-review` skill (Claude Code's default) is available but project-unaware — it does not know Supabase RLS semantics, the Paideia migration-contract shape, or the MemPalace substrate. Phase 6+ surfaces (per [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md)) will introduce authentication, authorization, API endpoints, headers, sessions — exactly the surfaces OWASP Top 10 targets — and a project-wired security review is the discipline gate before those surfaces ship.

[Issue #74](https://github.com/StarshipSuperjam/paideia/issues/74) named the adoption as Tier 2 of the SWE-hardening rollout, paired with [Issue #73](https://github.com/StarshipSuperjam/paideia/issues/73) (Pairing C in `engine/STATE.md`'s SWE-hardening table). Both adapt from `addyosmani/agent-skills` with identical authoring pattern; `/review` is the writer-side, `/security-review` is the depth-N security pass (this ADR's subject), and both will be composed by future `/ship` per [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76).

Pattern source: [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) `skills/security-and-hardening/SKILL.md` + `references/security-checklist.md`. Adapted, not cloned — Paideia-specific overlays (Supabase RLS verification, postcondition-assertion verification, MemPalace + KG PII discipline) are project-specific additions.

## Decision

A new project Skill at `.claude/skills/security-review/SKILL.md` carries the recipe for Paideia's security review. The doctrine is the SKILL.md body — no separate Layer 1 ops-doc, because the skill body IS the security-review doctrine. Two companion reference cards: `.claude/skills/security-review/owasp-checklist.md` (per-OWASP-item Pass / Fail / N-A grid with Paideia instantiation notes) and `.claude/skills/security-review/paideia-overlays.md` (project-specific overlays beyond OWASP). The anti-rationalization table lives at `.claude/skills/review/anti-rationalization.md` per [ADR 0070](0070-project-wired-review-skill.md) and is shared with this skill. `disable-model-invocation: true` per [ADR 0044](0044-skill-conversion-recipe-vs-reference.md).

### 1. Full OWASP Top 10 walk

A01 Broken Access Control / A02 Cryptographic Failures / A03 Injection / A04 Insecure Design / A05 Security Misconfiguration / A06 Vulnerable Components / A07 Authentication Failures / A08 Data Integrity Failures / A09 Logging & Monitoring / A10 SSRF. Per [`owasp-checklist.md`](../../.claude/skills/security-review/owasp-checklist.md), each item gets a Pass / Fail / N-A verdict with one-line reasoning. N-A is a real verdict — most items will be N-A on most pre-Phase-6 changes; the explicit walk catches the items a less-structured pass might silently skip.

### 2. Measurable thresholds

Where applicable, the skill names specific measurable thresholds (not just "secure"):

- bcrypt rounds ≥ 12 (or argon2id).
- JWT verification order: signature → expiration → issuer → audience (all four; in order).
- HSTS `max-age` ≥ 31536000 (1 year) with `includeSubDomains` and `preload`.
- CSP `default-src 'self'` baseline; any `unsafe-inline` / `unsafe-eval` requires justification.
- `uv.lock` integrity per [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md) (hash-locked).

The thresholds are the contract `/security-review` enforces; "is it secure" without naming the threshold is the failure mode this skill exists to prevent.

### 3. Three Paideia-specific overlays

Run alongside the OWASP walk. Per [`paideia-overlays.md`](../../.claude/skills/security-review/paideia-overlays.md):

- **Supabase RLS verification.** Every `public.*` table touched by the change has its policies read and semantically verified against the table's intended access model. `validate.py` soft-warns on missing RLS; this skill verifies the policy *content*. `USING (true)` without ADR-level justification is `Critical`.
- **`apply_migration.py` postcondition-assertion verification.** Every new migration must carry a `-- Postcondition-Assertions:` block per [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5. The wrapper runs them automatically; this skill verifies the block exists, the assertions sensibly match the body, and assertions are not overspecified.
- **MemPalace + KG PII discipline.** Every drawer/diary/KG write is reviewed for credentials and PII. Post-OSS-flip per [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md), the repo is world-readable, so committed MemPalace content under `engine/session/archive/*.json` and any drawer content that ends up in the repo is publicly visible.

### 4. Severity tiers reused from `/review`

Same Critical / Required / Nit / Optional / FYI rubric per [ADR 0070](0070-project-wired-review-skill.md). Security findings skew toward Critical and Required — the cost of a false-negative (missed vulnerability) is asymmetric vs. the cost of a false-positive.

### 5. Output as structured Markdown report

A Markdown report with the OWASP grid, the Paideia overlay grid, severity-tiered findings, a defense-in-depth cross-check (gitleaks / bandit / Dependabot status), and an anti-rationalization self-check (against the shared table at `.claude/skills/review/anti-rationalization.md`).

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

The `/security-review` skill adoption is evaluated against the four cross-cutting criteria from [ADR 0053](0053-mechanism-first-exercise-gate.md):

- ❌ Criterion 1 — new session mode. **No.** `/security-review` is invoked from inside any existing session mode at the user's discretion.
- ❌ Criterion 2 — new validator soft-warn category. **No.** This adoption introduces no `validate.py` soft-warns; the skill is invoked by the user, not by an automated gate.
- ❌ Criterion 3 — new state file the boot procedure reads. **No.** No new file under `engine/session/` or anywhere the boot procedure reads.
- ❌ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **No.** This adoption touches `.claude/skills/security-review/SKILL.md` + `.claude/skills/security-review/owasp-checklist.md` + `.claude/skills/security-review/paideia-overlays.md` + this ADR + `engine/adr/README.md` row + `engine/STATE.md` row + `engine/ENGINE_LOG.md` entry. Seven surfaces; one Skill (recipe), two reference cards, this ADR, three index/state entries. Zero ops-doc files; zero tooling files. Under the threshold.

Zero criteria satisfied → **no first-exercise readiness note required.** Mirrors [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) (Dependabot, S-0133) and [ADR 0070](0070-project-wired-review-skill.md) (same Pairing C, sibling) precedents. The Issue #74 body's pre-S-0134 assertion "First-exercise readiness note per ADR 0053. Cross-cutting" was authored before the rubric was being strictly applied per Issue; the rubric evaluation here is the binding judgment.

First real invocation of `/security-review` against a substantive change is the empirical verification. Captured as a follow-up to this ADR's "Empirical record" subsection or in the next session's `outcome_summary`, mirroring [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md)'s "First-PR-arrival verification (pending)" pattern.

### Other consequences

- **Positive — full OWASP coverage with explicit N-A verdicts.** The walk catches items a less-structured pass might silently skip. Marking an item N-A is a real verdict, not a gap.
- **Positive — measurable thresholds replace "secure" hand-waving.** bcrypt rounds ≥ 12 is mechanical; "use bcrypt" is hand-waving. The threshold catalog in the SKILL.md is the binding contract.
- **Positive — Supabase RLS overlay catches semantic policy bugs.** `validate.py` checks RLS is enabled; this skill checks the policy actually achieves the intended access control. `USING (true)` without justification is `Critical`.
- **Positive — postcondition-assertion overlay extends [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5.** The wrapper enforces the block's grammar; the skill verifies the block's semantic adequacy.
- **Positive — MemPalace PII overlay is timely.** Post-S-0130 OSS-flip, the repo is public; committed MemPalace content is world-readable. The S-0130 141-file PII sweep is the precedent; this overlay catches new-content drift.
- **Cost — manual invocation only.** Per `disable-model-invocation: true`. Mirrors [ADR 0070](0070-project-wired-review-skill.md)'s acknowledgement of this cost; same mitigation (AI surfaces `/security-review` as a suggestion on security-relevant changes; user confirms).
- **Cost — depth-N pass takes longer than depth-0.** A `/security-review` pass on a Phase 6+ auth surface is non-trivial; the reviewer reads the upstream OWASP item references, the relevant Paideia overlays, and the implementation. Acceptable cost; the asymmetric value of catching a vulnerability before merge justifies it.
- **Cost — pattern source maintenance.** The OWASP Top 10 updates periodically (most recent: 2021). The skill should sync to the latest OWASP list at audit time per the maintainer's discretion. Drift over multiple years could leave the skill targeted at a stale Top 10; the soft cadence is "re-check on each major OWASP version bump."
- **Out-of-scope — automated SAST beyond bandit.** `semgrep` and similar deeper SAST tools were not pulled in here. Bandit per [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md) is the SAST gate; `/security-review` is the human-judgment depth pass. If bandit proves insufficient in practice, evaluate semgrep separately.
- **Out-of-scope — pip-audit / safety pre-commit gate.** Per [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) out-of-scope; Dependabot covers the CVE surface at PR granularity.
- **Out-of-scope — full-codebase security audit.** A periodic audit walking the whole repo (not just the change's diff) is a separate posture, gated by [Issue #84](https://github.com/StarshipSuperjam/paideia/issues/84) (≥2 collaborators OR Phase 6 complete). `/security-review` is per-change; the full audit is per-cadence.
- **Out-of-scope — threat-model authoring.** The skill verifies against the *current* threat model (Paideia's posture per existing ADRs); it does not author or update the threat model. Threat-model drift is a separate concern.

### Interaction with existing layers

- **vs. gitleaks ([ADR 0067](0067-gitleaks-pre-commit-secret-scanning.md)):** gitleaks is the pre-commit gate that catches committed secrets. `/security-review` reads the in-flight code and config for secrets gitleaks might miss (a planned-but-not-yet-committed credential pattern; a config field that *should* be redacted at log time but isn't yet). Defense-in-depth.
- **vs. bandit ([ADR 0068](0068-bandit-sast-pre-commit-and-ci.md)):** bandit is the pre-commit + CI SAST that catches insecure code patterns. `/security-review` reads for semantic security: bcrypt rounds-count threshold, JWT verification order, CSP allowlist scoping. Defense-in-depth.
- **vs. Dependabot ([ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md)):** Dependabot surfaces vulnerable deps via weekly PRs. `/security-review` reads new dependencies' security posture *before* the version bump matters and cross-references open Dependabot alerts at review time. Defense-in-depth.
- **vs. `/review` ([ADR 0070](0070-project-wired-review-skill.md)):** `/review` has Security as one of five axes — depth-0; flag the obvious. `/security-review` is depth-N — full OWASP walk + Paideia overlays. Orthogonal; both compose in future `/ship`.
- **vs. [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5:** ADR 0055's wrapper enforces the `-- Postcondition-Assertions:` block's grammar mechanically (exit code 2 on malformed block; exit code 8 on assertion failure). `/security-review`'s overlay 2 verifies the block is *semantically* adequate (assertions match the body's intended effect; not overspecified).
- **vs. [ADR 0056](0056-mempalace-mechanical-adoption-checks.md):** ADR 0056 enforces MemPalace *usage* discipline (call counts via the PostToolUse hook). `/security-review`'s overlay 3 enforces MemPalace *content* discipline (no PII, no credentials). Orthogonal.
- **vs. future `/ship` ([Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76)):** This skill is the reviewer-side. `/ship` will orchestrate writer-side (`/review`) + reviewer-side (this skill) + response cycle + human adjudication.

### Empirical record

**S-0134 (authoring):** `.claude/skills/security-review/SKILL.md` + `owasp-checklist.md` + `paideia-overlays.md` committed at HEAD. The skill has not yet been invoked against a real change in this session.

**First-invocation verification (pending).** The first `/security-review` invocation against a substantive change in a future session is the empirical exercise. Expected: structured Markdown report with OWASP Top 10 grid, Paideia overlay grid, severity-tiered findings, defense-in-depth cross-check, anti-rationalization self-check. The natural near-term occasions are: a Phase 6+ auth surface session; any future migration that the reviewer wants the Layer 2.5 assertion block sanity-checked on; any change touching the MemPalace write surface. Verification recorded as a follow-up commit to this ADR's "Empirical record" subsection, or in the invoking session's `outcome_summary` per `engine/operations/session-shutdown-sequence.md`. Mirrors [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md)'s "First-PR-arrival verification (pending)" pattern.

## See also

- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise gate; trigger-criterion evaluation above (zero criteria; no readiness note required).
- [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md) — postcondition-assertion Layer 2.5; overlay 2 extends.
- [ADR 0056](0056-mempalace-mechanical-adoption-checks.md) — MemPalace mechanical adoption; orthogonal to overlay 3's content discipline.
- [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md) — OSS flip; why overlay 3 (MemPalace + KG PII) matters now.
- [ADR 0067](0067-gitleaks-pre-commit-secret-scanning.md) — secret scanning; defense-in-depth sibling.
- [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md) — SAST; defense-in-depth sibling.
- [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) — Dependabot; defense-in-depth sibling. Precedent for the rubric-negative evaluation block.
- [ADR 0070](0070-project-wired-review-skill.md) — `/review` companion; same Pairing C session. Anti-rationalization table is shared.
- [`.claude/skills/security-review/SKILL.md`](../../.claude/skills/security-review/SKILL.md) — the skill itself.
- [`.claude/skills/security-review/owasp-checklist.md`](../../.claude/skills/security-review/owasp-checklist.md) — companion reference card (OWASP grid).
- [`.claude/skills/security-review/paideia-overlays.md`](../../.claude/skills/security-review/paideia-overlays.md) — companion reference card (Paideia overlays).
- [`.claude/skills/review/anti-rationalization.md`](../../.claude/skills/review/anti-rationalization.md) — shared anti-rationalization table.
- [Issue #74](https://github.com/StarshipSuperjam/paideia/issues/74) — closes this ADR.
- [Issue #73](https://github.com/StarshipSuperjam/paideia/issues/73) — Pairing C sibling.
- [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76) — `/ship` orchestrator that will compose this skill.
- [OWASP Top 10 (current)](https://owasp.org/Top10/) — upstream source.
- Pattern source: `addyosmani/agent-skills/skills/security-and-hardening/SKILL.md` + `references/security-checklist.md` (adapted, not cloned).
