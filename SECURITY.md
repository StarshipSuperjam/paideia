# Security Policy

## Project status

Paideia is an open-source personal project under the Apache License 2.0. No commercial SLA. Best-effort response from the maintainer.

## Reporting a vulnerability

Report security vulnerabilities privately via GitHub's security-advisory channel: [https://github.com/StarshipSuperjam/paideia/security/advisories/new](https://github.com/StarshipSuperjam/paideia/security/advisories/new).

Do **not** open a public issue or pull request describing the vulnerability.

## BYOK posture (load-bearing)

Per [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md), Paideia ships under a Bring-Your-Own-Key model on the user-facing iOS app:

> The user's Anthropic API key lives only on-device in iOS Keychain. No Paideia-controlled server receives the key, proxies the API, or observes the API exchange.

The app stores the user's API key under iOS Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` and no iCloud sync. The app makes direct HTTPS calls to Anthropic's API from the device; no Paideia-controlled middlebox exists in the API exchange path.

The maintainer-side back-end (Supabase + engine tooling) handles graph construction, graph analysis, and aggregated mastery-state ingestion. It never receives, proxies, or observes user API keys.

## Scope of concern

- **Credential exposure in tracked files** — `.env`, `.mcp.json`, and any file containing live credentials are gitignored. If you find a credential committed to the repo, treat it as compromised, rotate it, and report.
- **Graph data (Supabase)** — the project ref is named in committed config; service-role tokens live in gitignored `.mcp.json` / `.env`. The dev tier has no production user data; Phase 6+ will introduce per-user RLS-gated tables.
- **Engine-side build tooling** — Python tools in `engine/tools/`. Dependencies are pinned in `pyproject.toml` / `uv.lock`; supply-chain integrity rides on `uv sync` reproducibility.
- **iOS app surface (Phase 6+)** — once the app surface lands, the BYOK key-handling and direct-Anthropic-call posture above is the primary attack surface. The maintainer's own deployment process (Apple build, IPA signing, App Store submission) is in scope.
- **MemPalace** — local-first, no cloud calls at the core layer. The palace at `~/.mempalace/palace` is locally sensitive; it can contain verbatim conversation history.

## Out of scope

- Third-party platform security: Anthropic's API surface, Supabase's hosted Postgres, Apple's iOS Keychain, Apple's App Store distribution. Defer to upstream security postures and report vulnerabilities to those vendors directly.
- Theoretical attacks on unreleased components (Phase 6+ teaching layer, Phase 9 commercial launch surface).
- DoS scenarios on the dev Supabase instance (free tier, no production data).
- Speculative attacks on dependencies you have not verified are exploitable on Paideia's current usage.

## Disclosure timeline

Best-effort response from the maintainer. No formal SLA. Critical issues (live credential exposure, ability to impersonate users post-Phase-6, key-extraction paths from the BYOK boundary) get prioritized; lower-severity issues queue against the maintainer's session schedule.
