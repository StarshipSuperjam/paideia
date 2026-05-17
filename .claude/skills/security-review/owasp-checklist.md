# OWASP Top 10 checklist (Paideia-instantiated)

> Companion reference card for [`/security-review`](SKILL.md). Per-OWASP-item Pass / Fail / N-A grid with Paideia-specific instantiation notes. Authored at S-0134 per [ADR 0071](../../../engine/adr/0071-project-wired-security-review-skill.md). Source: [OWASP Top 10 (2021 / current)](https://owasp.org/Top10/). Updates flow as the OWASP list updates.

## A01 — Broken Access Control

**What it is:** Failures in authentication and authorization that let users access resources they shouldn't.

**Paideia surfaces:**

- Phase 6+ API endpoints (per ADR 0065 product); pre-Phase-6 N-A in most cases.
- Supabase RLS policies on every `public.*` table (overlap with the RLS overlay).
- The MCP server surface — MCP tools that read/write project state should not be reachable by unauthorized callers (mitigated by the MCP server's authorization model, but worth verifying when a new tool is added).

**Pass conditions:** Every user-input-driven DB query verifies ownership/access; RLS policies are semantically grounded in `user_id = auth.uid()` or equivalent; no service-role bypass without explicit ADR justification.

**Fail signals:** IDOR-style queries (e.g., `SELECT * FROM user_data WHERE id = $user_supplied_id` without an access-check); `USING (true)` RLS clauses without justification; service-role caller scope is undefined.

## A02 — Cryptographic Failures

**What it is:** Sensitive data exposed via weak cryptography, missing TLS, plaintext storage, or wrong primitive choices.

**Paideia surfaces:**

- TLS for all external calls (any HTTP literal in a path issuing network requests).
- Future field-level encryption for PII (deferred to a future privacy ADR).
- Supabase manages encryption-at-rest at the disk level — disk-level encryption is not under direct project control here.

**Pass conditions:** All external endpoints HTTPS; no plaintext storage of credentials (gitleaks defense-in-depth); strong primitives (bcrypt rounds ≥ 12 / argon2id; AES-GCM / ChaCha20-Poly1305 if symmetric encryption is added).

**Fail signals:** `http://` in a non-loopback context; `bcrypt.hashpw(password, bcrypt.gensalt(8))` (rounds < 12); MD5 / SHA1 for security-relevant hashing; hardcoded credentials in code or config.

## A03 — Injection

**What it is:** Untrusted input flowing into an interpreter (SQL, shell, eval, LDAP, OS command, XPath) without escape or parameterization.

**Paideia surfaces:**

- `psycopg.execute(sql)` with f-string interpolation — `Critical`.
- `subprocess.run(shell_command)` with user-controlled input — `Critical`.
- Future Phase 6+ frontend with `dangerouslySetInnerHTML` / `eval()` / `Function()` — `Critical`.
- Seed migrations are static and pre-authored, so they don't surface this — but the migration *contract* must use parameterization-safe patterns for any future dynamic migration.

**Pass conditions:** All DB queries parameterized (`execute("SELECT ... WHERE id = %s", (id,))`); all shell calls use `shlex.quote` or pass arguments as a list; no string-built SQL anywhere.

**Fail signals:** f-string SQL; `+` string concatenation in DB calls; `shell=True` with user input; `eval(user_input)`.

## A04 — Insecure Design

**What it is:** Security flaws designed into the system, not bug-level mistakes — missing rate limits, missing audit trail, missing role separation.

**Paideia surfaces:**

- ADR-level design choices: review ADRs touching auth, session management, data handling for missing design controls.
- Per-tool design: does the tool produce an audit trail? (ENGINE_LOG and session archives provide one for build apparatus; Phase 6+ API operations need separate audit logs.)

**Pass conditions:** Audit trails for security-relevant operations; rate limits where applicable; role separation in design when multiple privilege levels exist.

**Fail signals:** Authoring an auth surface without an audit trail; service that takes user input without rate limiting; single-role system where multi-role makes sense.

## A05 — Security Misconfiguration

**What it is:** Default credentials, verbose error messages, unnecessary services enabled, missing security headers.

**Paideia surfaces:**

- Supabase project config (anon key vs. service-role key scope).
- Phase 6+ HTTP server config (headers, CORS, etc. — see SKILL.md Headers section).
- `.env` files committed (gitleaks catches; this verifies semantically).
- Open Dependabot alerts unmitigated.

**Pass conditions:** No default credentials anywhere; production-grade headers; minimal CORS; Dependabot alerts handled within reasonable cadence.

**Fail signals:** `psql -U postgres` with empty password reachable; `Access-Control-Allow-Origin: *` with credentials; verbose `traceback` in production responses; long-standing Dependabot alerts at `priority:urgent`.

## A06 — Vulnerable and Outdated Components

**What it is:** Dependencies with known CVEs unpatched.

**Paideia surfaces:**

- The `pyproject.toml` floor pins + `uv.lock` transitive graph per [ADR 0064](../../../engine/adr/0064-uv-lockfile-and-reproducible-builds.md).
- The `.github/workflows/*.yml` action pins (`astral-sh/setup-uv@v3`, `actions/checkout@v4`, etc.) per [ADR 0069](../../../engine/adr/0069-dependabot-pip-and-actions-ecosystems.md).

**Pass conditions:** No open Dependabot alerts at `priority:urgent`; no obvious vulnerable-version pins on the change's direct deps; uv.lock current per `uv lock --check`.

**Fail signals:** Adding a dep with a known CVE; ignoring an open Dependabot PR for >2 weeks without justification; lockfile stale per `uv lock --check`.

## A07 — Identification and Authentication Failures

**What it is:** Weak passwords accepted, weak session management, no MFA on sensitive paths, exposed credentials.

**Paideia surfaces:**

- Phase 6+ user auth (Supabase Auth handles much of this).
- API key handling on the BYOK pipeline per [ADR 0065 (product)](../../../product/adr/0065-oss-pivot-and-byok-disposition.md) — user-supplied keys in iOS Keychain; server stays key-blind.

**Pass conditions:** Passwords hashed bcrypt-12+; sessions expire; MFA available where the threat model demands; API keys never logged or persisted server-side.

**Fail signals:** No password complexity (project posture: lean on Supabase Auth's default); session-without-expiry; API key landing in a log line.

## A08 — Software and Data Integrity Failures

**What it is:** Code/data updated without integrity verification — supply-chain attacks, untrusted deserialization, CI/CD compromise.

**Paideia surfaces:**

- CI pipeline signing — currently not signed; deferred until ≥2 collaborators.
- `uv.lock` integrity per [ADR 0064](../../../engine/adr/0064-uv-lockfile-and-reproducible-builds.md) (hash-locked).
- No pickle / unsafe deserialization anywhere in `engine/tools/`.

**Pass conditions:** Lockfile hashes intact; no unsafe deserialization (`pickle`, `marshal`, `yaml.unsafe_load`); CI workflow files version-pinned.

**Fail signals:** Adding `pickle.loads(user_input)`; `yaml.load(stream)` without `Loader=yaml.SafeLoader`; CI action pinned to `@main` instead of a version tag.

## A09 — Security Logging and Monitoring Failures

**What it is:** Security events not logged, logs not monitored, no alert pipeline.

**Paideia surfaces:**

- Build apparatus has ENGINE_LOG + session archives + engine_memory diaries — strong audit trail for engine changes.
- Phase 6+ runtime needs separate logging for security events (auth failures, IDOR attempts, RLS denials).

**Pass conditions:** Engine changes are logged (ENGINE_LOG entries authored per shutdown protocol); future Phase 6+ paths log auth events.

**Fail signals:** Phase 6+ auth-failure path that silently returns; no log of an IDOR rejection.

## A10 — Server-Side Request Forgery (SSRF)

**What it is:** Server fetches a URL from user input without validation.

**Paideia surfaces:**

- Pre-Phase-6 N-A for runtime (no server-side URL fetch from user input).
- Build apparatus does fetch URLs (e.g., `engine/tools/fetch_structural_reference.py`) but the inputs are author-controlled, not user-supplied; N-A.

**Pass conditions:** Any server-side fetch validates the URL against an allowlist; no `http://169.254.169.254/` (cloud metadata) reachability.

**Fail signals:** `requests.get(user_supplied_url)` without validation.

## How to use this card

For each surface the change touches, walk down the list, mark each item PASS / FAIL / N-A in the report grid, and capture the one-line reasoning. N-A is a real verdict — most items will be N-A on most pre-Phase-6 changes.

## See also

- [`SKILL.md`](SKILL.md) — `/security-review` recipe; references this card.
- [`paideia-overlays.md`](paideia-overlays.md) — project-specific overlays beyond OWASP.
- [`../review/anti-rationalization.md`](../review/anti-rationalization.md) — shared anti-rationalization table.
- [ADR 0071](../../../engine/adr/0071-project-wired-security-review-skill.md) — citable contract.
- [OWASP Top 10](https://owasp.org/Top10/) — upstream source.
