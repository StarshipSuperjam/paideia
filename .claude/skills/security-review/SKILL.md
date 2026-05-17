---
name: security-review
description: Run a Paideia security review against the OWASP Top 10 with measurable thresholds (bcrypt rounds, JWT verification order, CSP shape, parameterized queries) plus Paideia-specific overlays (Supabase RLS, apply_migration postcondition assertions per ADR 0055, engine_memory PII discipline). Defense-in-depth orthogonal to gitleaks (ADR 0067) + bandit (ADR 0068) + Dependabot (ADR 0069). Adapted from `addyosmani/agent-skills/skills/security-and-hardening` per ADR 0071.
disable-model-invocation: true
---

# security-review

> Project-wired `/security-review` for Paideia. The doctrine is this SKILL.md per [ADR 0071](../../../engine/adr/0071-project-wired-security-review-skill.md) — no separate Layer 1 ops-doc, because the skill body IS the security-review doctrine. Updates land here. Two companion reference cards: [`owasp-checklist.md`](owasp-checklist.md) (the per-item grid) and [`paideia-overlays.md`](paideia-overlays.md) (project-specific items). The anti-rationalization table lives at [`../review/anti-rationalization.md`](../review/anti-rationalization.md) and is shared.

## When to invoke

A `/security-review` pass is warranted whenever a change touches a security-relevant surface — and crucially, *before* the change exists too: design-time review when a new auth surface, data-handling boundary, or user-input pipeline is being added. Phase 6+ will surface this routinely; pre-Phase-6 the relevant surfaces are migrations (per [ADR 0055](../../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) postcondition assertions), tool code touching `psycopg`/external APIs, and the engine_memory write surface (KG retired alongside the chromadb substrate).

The skill is the depth pass for security. It is orthogonal to:

- **gitleaks** ([ADR 0067](../../../engine/adr/0067-gitleaks-pre-commit-secret-scanning.md)) — pre-commit secret-scan. Catches committed credentials. `/security-review` reads the in-flight code and config for secrets that gitleaks misses (e.g., a planned-but-not-yet-committed credential pattern, a config field that *should* be redacted at log time).
- **bandit** ([ADR 0068](../../../engine/adr/0068-bandit-sast-pre-commit-and-ci.md)) — pre-commit + CI SAST. Catches insecure code patterns (B-codes). `/security-review` reads for *semantic* security: is the bcrypt rounds-count above the threshold? Is the JWT verification order correct? Is the CSP allowlist actually scoped?
- **Dependabot** ([ADR 0069](../../../engine/adr/0069-dependabot-pip-and-actions-ecosystems.md)) — weekly vulnerable-dep surfacing. `/security-review` reads for new dependencies' security posture *before* the version bump matters.

None of those three substitutes for `/security-review`. The skill composes with [`/ship`](../ship/SKILL.md) per [ADR 0081](../../../engine/adr/0081-ship-multi-model-orchestration-skill.md) (landed at S-0148) as the security-depth sub-agent alongside [`/review`](../review/SKILL.md) (writer-side) and a coverage-delta check. `/ship` runs all three as parallel sub-agents and synthesizes a GO / GO-WITH-CAVEATS / NO-GO verdict. Use `/security-review` directly for narrow security-only passes; use `/ship` for the full pre-merge composition.

## OWASP Top 10 walk

Walk every change against the [OWASP Top 10](https://owasp.org/Top10/) items relevant to the surface. The [`owasp-checklist.md`](owasp-checklist.md) reference card has the per-item Pass / Fail / N-A grid. The sections below give the measurable thresholds. Use the Pass / Fail / N-A grid in the structured report (see "Output shape").

### Authentication

Phase 6+ surface; pre-Phase-6 N-A in nearly every case. When present:

- **Password storage:** bcrypt with rounds ≥ 12, or argon2id. Hash inputs from server-trusted random source. Flag any rounds < 12 as `Critical`.
- **MFA enforcement:** required for admin paths, sensitive operations, and any path the threat model identifies. Pre-Phase-6 N-A.
- **Account lockout:** N failed attempts → lock or rate-limit. The threshold is configurable; the *presence* of the mechanism is checkable.

### Authorization

- **IDOR prevention:** every user-input-driven DB query must verify ownership/access on the requesting user. Flag any query that takes a user-supplied ID without an accompanying access-check as `Critical`.
- **Principle of least privilege:** Supabase RLS policies on every `public.*` table. Per the Paideia overlay below.
- **Role-based access control consistency:** if roles exist, every authorized path must check them. Drift in the check shape is `Required`.

### Input validation

- **Allowlist-based, not denylist.** Allowlists are exhaustive; denylists silently miss new attack surfaces.
- **Parameterized queries.** Any string-concat SQL is `Critical`. The Paideia seed migrations are static and pre-authored, so they don't surface this — but Phase 6+ API code is the risk.
- **Output encoding.** Phase 6+ frontend surface. Any user-controlled string flowing to HTML without explicit encoding is `Critical`.

### Headers and transport

Phase 6+ surface; N-A pre-deployable.

- **Content-Security-Policy:** allowlist, not wildcard. `default-src 'self'` is the baseline; every `unsafe-inline` / `unsafe-eval` requires explicit justification.
- **HSTS:** `Strict-Transport-Security` with `max-age` ≥ 31536000 (1 year), `includeSubDomains`, `preload` per submission to the HSTS preload list.
- **X-Frame-Options:** `DENY` or `SAMEORIGIN`.
- **X-Content-Type-Options:** `nosniff`.
- **CORS allowlist, not `*`.** Wildcard CORS with credentials is `Critical`.

### Session and token

Phase 6+ surface.

- **JWT verification order:** signature → expiration → issuer → audience. *All four.* Flag any verification that checks fewer or in wrong order as `Critical`.
- **Session timeout enforced** at sensible boundaries.
- **Token refresh discipline:** rotation, expiration, revocation list.

### Data protection

- **TLS for all external calls.** Any `http://` literal in a code path that issues network requests is `Critical`. Internal-loopback exception requires explicit comment.
- **At-rest encryption** for sensitive fields. Supabase manages encryption-at-rest at the disk level; field-level encryption for PII is a separate decision per future privacy ADR.
- **PII handling.** Per the Paideia overlay below.

### Dependency audit

- **Cross-reference open Dependabot PRs / alerts** ([ADR 0069](../../../engine/adr/0069-dependabot-pip-and-actions-ecosystems.md)). Any open `priority:urgent` Dependabot alert is `Critical` and the merge is gated.
- **Any new dependency introduced this change?** Read the upstream's recent CVE history. The new dep's transitive surface is now in `uv.lock` per [ADR 0064](../../../engine/adr/0064-uv-lockfile-and-reproducible-builds.md).

## Paideia-specific overlays

These are NOT optional. They run alongside the OWASP walk. The [`paideia-overlays.md`](paideia-overlays.md) reference card has the full grid; the high points:

### Supabase RLS verification

Every `public.*` table must have RLS enabled. `validate.py` soft-warns when missing; `/security-review` verifies that the enabled policy is *semantically* correct (not just present).

For each RLS-enabled table touched by the change:

- What does the policy let `auth.uid()` do? Read, write, both?
- Is the policy clause grounded in `user_id = auth.uid()` (the standard ownership check)?
- Are there service-role bypasses? If so, is the service-role caller actually trusted?

A policy that says `USING (true)` (allow-all) is `Critical` unless explicitly justified (e.g., a `cache_metadata` table that is intentionally world-readable per a documented ADR).

### `apply_migration.py` postcondition-assertion verification

Per [ADR 0055](../../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5: every migration must carry a `-- Postcondition-Assertions:` block in its contract header. The block contains lines of the form `--   <SELECT returning one integer> :: <expected integer>`.

For each new migration in the change:

- Does the block exist? (Missing block is `Required` per the ADR's pre-S-0094 grandfather clause; new migrations land with the block.)
- Do the assertions sensibly verify the body's effect? (E.g., a migration adding N rows should have an assertion verifying the row count rose by exactly N.)
- Are the assertions overspecified? (Asserting every row's exact data is fragile.)

### engine_memory PII discipline

The engine_memory substrate and the KG storage layer are project-internal but should not carry credentials. For every change that writes to engine_memory (via `engine_memory_add_drawer`, `engine_memory_diary_write`, etc.) or the project archives:

- Does the content include any password, token, API key, or other credential? `Critical`.
- Does the content include any PII (real names other than maintainer self-reference, email addresses, etc.)? `Required` to redact.
- Does the diary content (per ADR 0091) follow the AAAK compression discipline so it's not human-readable narrative that could leak PII?

## Severity tiers

Same five-tier rubric as [`/review`](../review/SKILL.md): Critical / Required / Nit / Optional / FYI. See [`/review`'s SKILL.md`](../review/SKILL.md#severity-tiers) for definitions.

Security findings skew toward Critical and Required — the cost of a false-negative (missed vulnerability) is asymmetric vs. the cost of a false-positive (extra review cycle). Calibrate honestly; do not deflate.

## Output shape

A structured Markdown report. Per-OWASP-item Pass / Fail / N-A grid plus severity-tiered findings plus the anti-rationalization self-check.

```markdown
## `/security-review` — <branch-name> @ <SHA-short>

**Surfaces touched:** <auth / authz / input / headers / session / data / deps / migrations / engine_memory / KG (KG retired)>.

### OWASP Top 10 grid

| Item | Verdict | Reasoning |
|---|---|---|
| A01 Broken Access Control | PASS / FAIL / N-A | <one-line> |
| A02 Cryptographic Failures | PASS / FAIL / N-A | <one-line> |
| A03 Injection | PASS / FAIL / N-A | <one-line> |
| A04 Insecure Design | PASS / FAIL / N-A | <one-line> |
| A05 Security Misconfiguration | PASS / FAIL / N-A | <one-line> |
| A06 Vulnerable Components | PASS / FAIL / N-A | <one-line> |
| A07 Authentication Failures | PASS / FAIL / N-A | <one-line> |
| A08 Data Integrity Failures | PASS / FAIL / N-A | <one-line> |
| A09 Logging / Monitoring | PASS / FAIL / N-A | <one-line> |
| A10 SSRF | PASS / FAIL / N-A | <one-line> |

### Paideia overlay grid

| Overlay | Verdict | Reasoning |
|---|---|---|
| Supabase RLS verification | PASS / FAIL / N-A | <one-line> |
| Postcondition-assertion block (ADR 0055) | PASS / FAIL / N-A | <one-line> |
| engine_memory / KG (KG retired) PII discipline | PASS / FAIL / N-A | <one-line> |

### Findings

| Severity | OWASP / overlay | Finding | File:Line | Suggested action |
|---|---|---|---|---|
| Critical | A03 Injection | <one-line> | path/to/file.py:42 | <action> |
| Required | RLS overlay | <one-line> | product/seed-graph/migrations/NNNN.sql | <action> |

### Defense-in-depth cross-check

- **gitleaks:** clean (pre-commit gate per ADR 0067).
- **bandit:** clean (pre-commit + CI per ADR 0068).
- **Dependabot:** no open `priority:urgent` alerts.

### Anti-rationalization self-check

- Reviewed against [`../review/anti-rationalization.md`](../review/anti-rationalization.md): no rationalizations applied.
```

N-A is a real verdict — most OWASP items will be N-A on most pre-Phase-6 changes. PASS / FAIL / N-A are calibrated; do not inflate FAIL to look thorough or inflate PASS to ship faster.

## Failure modes this skill prevents

- **OWASP coverage gaps.** Walking the Top 10 explicitly catches the items a code-review pass might silently skip ("we don't have CORS, N-A" is a valid verdict — but it's an explicit one).
- **Measurable-threshold drift.** "bcrypt is fine" without checking the rounds count is the failure. The threshold (≥12) is mechanical.
- **JWT-verification-order bugs.** The signature → expiration → issuer → audience order is non-obvious; the skill names it explicitly.
- **RLS-as-presence-not-policy.** `validate.py` checks RLS is enabled; this skill checks the *policy* is semantically right.
- **Postcondition-assertion-block omission.** Per ADR 0055 Layer 2.5; the skill verifies the block, not just the migration file.
- **engine_memory credential leaks.** The KG substrate is project-internal but not authorized to carry credentials; the overlay catches this.

## Failure modes this skill does NOT prevent

- **Threat-model errors.** If the threat model is wrong (e.g., trusting an upstream that shouldn't be trusted), the skill verifies against the wrong threat model. Threat-model drift is a separate concern.
- **Runtime exploits in unverified surfaces.** A surface not touched by the current change is not reviewed; periodic full-codebase security audits cover this gap, gated by [Issue #84](https://github.com/StarshipSuperjam/paideia/issues/84) (≥2 collaborators OR Phase 6 complete).
- **Social-engineering and physical attacks.** Out of scope.

## See also

- [`owasp-checklist.md`](owasp-checklist.md) — per-OWASP-item grid (the canonical reference).
- [`paideia-overlays.md`](paideia-overlays.md) — project-specific overlays.
- [`../review/anti-rationalization.md`](../review/anti-rationalization.md) — shared with [`/review`](../review/SKILL.md).
- [ADR 0071](../../../engine/adr/0071-project-wired-security-review-skill.md) — the citable contract.
- [`/review`](../review/SKILL.md) — five-axis code review (depth-0 security pass is one of its axes; this is the depth-N pass).
- [`/ship`](../ship/SKILL.md) — multi-model orchestrator composing this skill (landed at S-0148 per [ADR 0081](../../../engine/adr/0081-ship-multi-model-orchestration-skill.md)).
- [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition.
- [ADR 0055](../../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) — postcondition-assertion block (Layer 2.5).
- [ADR 0067](../../../engine/adr/0067-gitleaks-pre-commit-secret-scanning.md), [ADR 0068](../../../engine/adr/0068-bandit-sast-pre-commit-and-ci.md), [ADR 0069](../../../engine/adr/0069-dependabot-pip-and-actions-ecosystems.md) — defense-in-depth siblings.
- Pattern source: `addyosmani/agent-skills/skills/security-and-hardening/SKILL.md` + `references/security-checklist.md` (adapted, not cloned).
