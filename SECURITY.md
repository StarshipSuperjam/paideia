# Security Policy

## Reporting a vulnerability

This is a private, pre-launch project. If you discover a security vulnerability — whether in dependencies, configuration, exposed secrets, or application logic — report it directly and privately to the project owner.

Do **not** open a public issue or pull request describing the vulnerability.

## Scope

Active concerns include:

- **API key exposure** — `.env`, `.mcp.json`, and any file containing credentials are gitignored. If you find a credential committed to the repo, treat it as compromised, rotate it, and report.
- **Dependency vulnerabilities** — Python and Node packages declared in `requirements.txt` / `package.json` (when those land in later phases). Notable runtime dependencies: `mempalace`, `chromadb`, `psycopg`, `@supabase/mcp-server-supabase`.
- **Supabase** — project ref is named in committed config; the access token is in gitignored `.mcp.json`. The token has scoped permissions per its issuance; if compromised, rotate from the Supabase dashboard.
- **MemPalace** — local-first, no cloud calls at the core layer. The palace lives at `~/.mempalace/palace` by default; treat as locally sensitive (it can contain verbatim conversation history including any secrets discussed in chat).
- **User-supplied content** (post-Phase 7) — close-reading user-uploaded texts are stored per-user; access controls enforce owner-only access.

## What's out of scope

- Theoretical attacks against unreleased components (Phase 7+ teaching layer, Phase 9 UI)
- DoS scenarios on the dev Supabase instance (free tier, no production data)
- Speculative attacks on dependencies you haven't verified are exploitable

## Disclosure timeline

Private response within a reasonable timeframe given the project's pre-launch status. No formal SLA until commercial launch.
