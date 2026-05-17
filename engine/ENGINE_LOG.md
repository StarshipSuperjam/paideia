# ENGINE_LOG.md — moved

> This file's role retired at S-0198 per [ADR 0092](adr/0092-per-session-changelog-directory.md).
>
> **New surface:** [`engine/changelog/`](changelog/) — per-session entries at `<YYYY>/<S-NNNN>-<slug>.md` with schema-validated frontmatter + 50/70-line cap. Synthesize Keep-a-Changelog `[Unreleased]` views via `python3 engine/tools/changelog_aggregate.py`.
>
> **Historical archive (2,799 lines, byte-preserved):** [`engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md`](changelog/_history/ENGINE_LOG-pre-0.1.0.md) — verbatim record of foundation-period material engine changes S-0001 → S-0197.
>
> **First release entry:** [`engine/changelog/2026/S-0198-0.1.0-foundation-close.md`](changelog/2026/S-0198-0.1.0-foundation-close.md) — the foundation-close synthesis at git tag `engine-v0.1.0`.

This transitional stub exists only to keep cold readers and unintended cross-references from hitting a broken pointer during the S-0198 cascade-update window. It will be deleted once the 22 inbound references (CLAUDE.md, STATE.md, ROADMAP.md, README.md, HANDOFF.md, 6 ops docs, 5 ADRs) all re-point to the new directory pattern.
