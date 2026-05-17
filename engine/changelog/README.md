<!--
governed: true
line_cap_soft: 50
line_cap_hard: 70
-->

# Changelog

Per-session bounded changelog entries. One file per session-that-produced-material-change. Replaces the monolithic `ENGINE_LOG.md` pattern per [ADR 0092](../adr/0092-per-session-changelog-directory.md).

## Layout

```
changelog/
├─ README.md            # this file
├─ <YYYY>/              # per-year directories
│  ├─ S-0198-0.1.0-foundation-close.md
│  └─ S-NNNN-<slug>.md
└─ _history/            # annual rollover destination + pre-cutover historical archive
   └─ ENGINE_LOG-pre-0.1.0.md   # the monolithic 2,799-line pre-S-0198 record
```

## Discipline

- **Only on material change.** Shutdown step 7 writes an entry only if the session produced one of the 12 classes in [`engine/schemas/changelog-entry.schema.json`](../schemas/changelog-entry.schema.json): `adr` / `policy` / `check` / `audit` / `operation` / `tool` / `skill` / `module` / `schema` / `infrastructure` / `docs` / `mixed`. Trivial fixes (typos, formatting, rerun-tests) do NOT write entries. When in doubt, no entry is better than an empty one.
- **50-line soft cap / 70-line hard cap.** Each entry bounded to 50 lines (validator soft-warn) / 70 lines (validator hard-fail) including frontmatter. Cap forces summary-plus-pointers shape; the structured archive at `engine/session/archive/S-NNNN.json` carries the canonical session record.
- **Append-only within year.** Existing entries are not edited after the session closes. Corrections land as new entries citing the prior one.
- **Annual rollover.** Each year on Jan 1 (or first session of the year), the previous year's directory moves into `_history/<YYYY>/`. Manual procedure; no automation. Active reference for the current year stays at `<YYYY>/`.

## Frontmatter

Validated by [`engine/schemas/changelog-entry.schema.json`](../schemas/changelog-entry.schema.json). Required fields: `session_id` (pattern `^S-[0-9]{4}$`), `session_type` (`build` / `routine` / `exploration`), `closed_at` (ISO 8601 UTC), `material_change_class` (12-enum above), `module` (string; `multi` if cross-module). Optional: `summary` (max 200 chars; full narrative in body).

## Aggregation

`[Unreleased]` synthesis on demand via [`engine/tools/changelog_aggregate.py`](../tools/changelog_aggregate.py): reads `<YYYY>/*.md` entries, groups by `material_change_class`, emits Keep-a-Changelog markdown. CLI: `--since <git-tag>`, `--module <name>`, `--format markdown|json`, `--validate-only`.

## What does NOT go here

- Per-session narrative (full prose) → session archive (`engine/session/archive/S-NNNN.json` `outcome_summary`).
- Decisions with rationale → ADRs (`engine/adr/` or `product/adr/`).
- Audit findings → reports (`docs/health-checks/`).
- Cross-session deferred items → HANDOFF.md (session-internal) or GitHub Issues (cross-session) per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).

See [ADR 0092](../adr/0092-per-session-changelog-directory.md) and [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) step 7.
