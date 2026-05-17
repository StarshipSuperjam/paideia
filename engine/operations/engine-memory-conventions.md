# Engine-memory conventions

> Room + source_kind + tag vocabulary for the engine-memory substrate. Layer 1 source-of-truth for what goes where.
>
> The substrate's mechanics live in [`engine-memory-operations.md`](engine-memory-operations.md). This document covers the authorial discipline: which room a drawer belongs in, what `source_kind` to record, when to write a drawer at all, when not to.

## Rooms (schema-enforced)

The `drawers.room` CHECK constraint admits exactly seven values. The first five are the curated rooms — content authored deliberately, content that survives session boundaries as a load-bearing recall surface. The remaining two cover machine-captured and legacy fallback content.

| Room | What it holds | Example |
|---|---|---|
| `decisions` | Settled decisions, ADR companions, named architectural choices. The narrative form of decisions that ADRs record as contract. | A drawer paired with an ADR landing: "ADR 0091 — chose SQLite + FTS5 over Postgres pgvector because the engine/product wall holds only if memory storage stays out of paideia-dev." |
| `pushback` | Risk-surfacing moments. Times the AI or user named a concern that changed direction. | "Pushback against routine-mode auto-recovery on stale lockfile — too eager; user wanted manual reconciliation." |
| `lessons` | Procedural failures + fixes. Things that went wrong + what we learned. | "Pre-commit hook hung indefinitely on paused Supabase because psycopg.connect lacked connect_timeout; added timeout in S-0186." |
| `exploration` | Approaches investigated but not committed. Trade-off notes, considered-and-rejected alternatives. | "Considered upstream MemPalace contribution to fix Issue #134; rejected because release cadence is too slow and the engine/product wall argues for ownership." |
| `operations` | Operational reference: shapes, schemas, common commands, tool invocations the project uses repeatedly. | "Running migration replay against live palace: `python -m engine.memory.migrate_from_mempalace --db-path <main-repo>/engine/.memory/engine_memory.sqlite3`." |
| `work` | Stop/PreCompact hook auto-capture of session transcripts. **Do not author manually.** The capture surface is owned by `engine/memory/capture.py`. | (machine-written) |
| `general` | Legacy fallback. **Avoid for new content.** Anything that doesn't fit a curated room probably doesn't belong in the substrate at all. | (historical) |

## Source kinds (schema-enforced)

The `drawers.source_kind` CHECK constraint admits five values:

| Source kind | When to use |
|---|---|
| `manual` | Default for deliberate `engine_memory_add_drawer` calls from a session. |
| `hook_stop` | Reserved for `engine-memory-capture.sh stop` writes. Never use manually. |
| `hook_precompact` | Reserved for `engine-memory-capture.sh precompact` writes. Never use manually. |
| `export_replay` | Reserved for [`engine/memory/migrate_from_mempalace.py`](../memory/migrate_from_mempalace.py) and any future one-shot import scripts. |
| `migration_seed` | Reserved for ADR-tracked seed authoring (e.g., a future operation that pre-populates the substrate with curated content from outside MemPalace). |

The `agent` column defaults to `'claude'` — set it explicitly only if a non-Claude agent ever writes drawers (currently never; reserved for future multi-agent use).

## Tags

The `drawers.tags` column is a JSON array of lowercase snake_case strings. The substrate's tag-class boost (per ADR 0091 Decision 3) adds +0.15 to BM25 rank for drawers carrying `decision`, `pushback`, or `lesson` — these three are the load-bearing class tags. Other tags are forensic / topic-scoped.

**Common tags (load-bearing class markers):**

- `decision` — pair with `room='decisions'`. Adds tag-class boost.
- `pushback` — pair with `room='pushback'`. Adds tag-class boost.
- `lesson` — pair with `room='lessons'`. Adds tag-class boost.

**Common tags (topic / source markers):**

- `adr` — drawer is an ADR companion (per the two-layer decision recording rule in [CLAUDE.md](../../CLAUDE.md)).
- `transcript` — auto-written by `engine-memory-capture.sh` on `room='work'` drawers.
- `engine-memory` — drawer concerns the substrate itself.
- `phase-5`, `phase-6`, etc. — project-phase marker.
- `routine-mode`, `interactive` — session-mode marker when relevant.
- `mempalace-retirement` — drawer concerns the MemPalace cutover (transitional; obsolete after S-0193).

**Style.** Lowercase, snake_case, prefer short forms. The tag list is small and additive; if you find yourself inventing a one-off tag for a single drawer, it's probably not useful — content-driven FTS5 retrieval finds it anyway.

## When NOT to write a drawer

A drawer is a recall surface for content downstream sessions will benefit from finding. If the content fails any of these tests, don't write it:

- **`git log` already captures it.** Commit messages, ADR bodies, ENGINE_LOG entries, ROADMAP edits — these are durable, searchable, and indexed by tools sessions already use. Drawers about "I committed X" or "I added Y to STATE.md" are noise.
- **Transient state.** Tool output, error messages, "I tried Z and it didn't work, then I tried Z' and it did" — the artifact downstream sessions need is in the commit that landed the fix.
- **The fix is the artifact.** A lesson is "WHY the fix was needed and what would catch it next time," not "the fix exists at SHA `abc1234`."
- **Single-session detail.** "I'm using approach W for this session's work" — the plan file (`engine/session/current_plan.md`) is the right surface.

A drawer is worth writing when:

- Future sessions reading the work item cold would benefit from finding this content.
- The content explains a non-obvious WHY (rule + reason + how to apply), not a what.
- The content survives the next refactor — names a posture, a constraint, a pattern, not a specific file path or function name.

## Authoring patterns

**ADR companion (`decisions` + `decision` tag).** Pair every ADR landing with one `engine_memory_add_drawer` per [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md) (replaces ADR 0056's MemPalace pairing). Drawer content names the decision in conversational form: what was settled, what alternatives were rejected, the load-bearing reason. The PostToolUse hook on ADR writes can soft-warn when an ADR lands without a matching drawer.

**Pushback (`pushback` + `pushback` tag).** Capture when the user surfaces a risk concretely or when the AI catches itself about to do something risky. The drawer's value is reading it cold in a future session and recognizing the pattern early — "we already pushed back against this at S-NNNN; here's why."

**Lessons (`lessons` + `lesson` tag).** Capture when a procedural failure surfaces a missing or wrong mechanism. The drawer is the rule + the why + the how-to-apply, not the bug report.

**Exploration (`exploration`).** Capture when an alternative was considered seriously enough that a future session evaluating the same alternative deserves to know "we looked, here's why we didn't go."

**Operations (`operations`).** Capture when an invocation, a debugging recipe, or a common shape is the thing future sessions need to find. Keep it terse — operational reference, not narrative.

## See also

- [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md) — substrate decision; the rooms / source kinds / tag-class boost are commitments here.
- [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle; persistent-warn surface reads forward to this doc's room/tag discipline.
- [`engine-memory-operations.md`](engine-memory-operations.md) — substrate mechanics (schema, hooks, MCP surface).
