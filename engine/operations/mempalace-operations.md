# MemPalace operations

> Install, initialize, populate, and capture-on-stop. MemPalace is the project's semantic memory: drawers (verbatim memories) organized into rooms (topics) within wings (projects), connected by halls (intra-wing) and tunnels (inter-wing). For tag conventions, see [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md).

## What MemPalace does for Paideia

It captures the conversational substrate that ADRs and ENGINE_LOG can't hold:

- **Exploration sessions** — "we considered X, rejected for Y" — so future sessions don't re-litigate.
- **Decision moments** — the verbatim reasoning at the moment a commitment was settled (the *story* behind the ADR's *contract*).
- **Work logs** — what a build session actually did, indexed by similarity for cold-start retrieval.

Two layers of decision recording (per CLAUDE.md): ADRs are the contract, MemPalace is the story.

## Project usage scope

MemPalace ships a broad surface (~19 MCP tools, plus a knowledge graph, per-agent diary, and cross-wing tunnels). This project does not use all of it. Naming the scope explicitly so sessions don't follow the generic protocol message MemPalace's `mempalace_status` tool emits:

**What this project uses:**

- **`mempalace_search`** — boot-time recall of context relevant to the next-session work item (per `session-build-lifecycle.md` step 3); anywhere mid-session when checking for prior reasoning.
- **`mempalace_add_drawer`** — manual capture of ADR-companion `decision` drawers, `pushback` drawers, `lesson` drawers, and ad-hoc exploration captures. The verbatim-conversational layer the hooks under-capture.
- **`mempalace_diary_write` / `mempalace_diary_read`** — first-person AI session journal. Written at shutdown per `session-shutdown-sequence.md`; read at boot per `session-build-lifecycle.md`. Distinct from `outcome_summary` (outcome-focused) and ENGINE_LOG (third-person artifact narrative): the diary carries the AI's reflection on the session — what surprised me, what I noticed but didn't act on, where my judgment was uncertain. Adopted at S-0032; see `agent_name` selection note below.
- **`mempalace_status` / `mempalace_list_drawers` / `mempalace_get_drawer` / `mempalace_list_rooms` / `mempalace_list_wings`** — read-only inspection. Used during audits and ad-hoc queries.
- **Stop and PreCompact capture hooks** — auto-capture conversation chunks via `mempalace-hook-wrapper.sh` (per the Capture section below). Captured drawers default-tag `work` for build sessions, `exploration` for default-mode sessions.

**What this project does NOT use:**

- **Knowledge graph** (`mempalace_kg_query` / `mempalace_kg_add` / `mempalace_kg_invalidate` / `mempalace_kg_stats` / `mempalace_kg_timeline`). Reason: the project encodes structural facts and temporal validity in ADRs (`Status: Superseded by ADR NNNN`, `Date: YYYY-MM-DD`), in `STATE.md` (current pointer), in `engine/operations/cross-references.md` (engine-side dependency map), and in `product/docs/CROSS_REFERENCES.md` (product-side). A KG layer would duplicate without adding query power the project actually needs. Re-evaluate if the project ever wants temporal queries of the form *"show me everything that depended on ADR 0017 before it was superseded"* — answerable today only by grep + reading.
- **Tunnels** (`mempalace_find_tunnels` / `mempalace_list_tunnels` / `mempalace_create_tunnel` / `mempalace_delete_tunnel` / `mempalace_traverse`). Reason: tunnels link rooms across wings; the project has one active wing (`paideia`) plus the diary wing (`wing_claude` per the diary note below). Re-evaluate when (if) a second project shares this MemPalace install.
- **AAAK compressed dialect for project drawers** (`mempalace_get_aaak_spec`). Reason: Paideia drawers are conversational verbatim; AAAK's compression is for memory across thousands of drawers per agent (the diary wing may eventually use AAAK; project drawers do not).

**`agent_name` for the diary:** `claude` — matches MemPalace's own AAAK examples and creates a clean `wing_claude` separate from `wing_paideia`. The diary is the AI's continuity layer across sessions; keeping it in its own wing means project-content drawers and reflection drawers don't compete in semantic search.

When a future session is uncertain whether a tool fits the project's surface: the answer is in this section. If the surface needs to grow (e.g., adopting the KG), the addition lands here first as a project decision before the tool is invoked at scale.

## Architecture (4-level hierarchy)

```
Wing      (project or person, e.g., "paideia")
└── Room  (topic, e.g., "operations", "self-correction")
    └── Closet  (summary nodes derived from drawers)
        └── Drawer  (verbatim memory; the atomic unit)
```

**Halls** connect rooms within a wing (cross-topic links). **Tunnels** connect rooms across wings (cross-project links). Most queries traverse drawers via similarity search; halls and tunnels surface when explicitly traversed.

## Install

MemPalace 3.3.3 ships as a Python package. Installed at user-scope:

```
/Users/<user>/Library/Python/3.9/bin/mempalace
/Users/<user>/Library/Python/3.9/bin/mempalace-mcp
```

The MCP server (`mempalace-mcp`) is registered in `.mcp.json` (gitignored — contains no secrets but kept local for parity with the Supabase entry):

```json
{
  "mcpServers": {
    "mempalace": {
      "command": "/Users/shanekidd/Library/Python/3.9/bin/mempalace-mcp"
    }
  }
}
```

Restart Claude Code after editing `.mcp.json` for the server to load.

## Initialize against this repo

Run from the repo root. Initialize the wing only — do **not** mine the operations docs (per S-0032 audit Improvement E):

```bash
mempalace init .
```

Per the S-0032 audit, the original install at S-0002 ran `mempalace mine docs/` (pre-S-0024 partition) which produced 88 drawers in the `operations` room — chunks of `engine/operations/*.md`. Those chunks compete with conversational drawers in semantic search and crowd retrieval (the same operations doc returns five times against unrelated queries because `mempalace mine` chunks each file into multiple drawers). The operations docs already live in git, queryable via grep + Read; reindexing them as drawers duplicates the content and dilutes search.

Going forward: do not mine `engine/operations/` or `product/docs/` (or any other directory whose content is already in version control and consumed via Read). MemPalace's role here is the conversational substrate that ADRs and ENGINE_LOG can't hold — captured drawers from Stop/PreCompact hooks and manual `mempalace_add_drawer` calls. The 88 existing operations-doc drawers can be cleaned up in a future cleanup session; the install procedure no longer recreates them.

Verify with `mempalace status` and `mempalace_list_rooms` (MCP tool). Expect: at least `general` (auto-capture default per the room-targeting conventions in [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md)).

## Capture on session events (Claude Code hooks)

MemPalace 3.3.3 does **not** auto-capture conversations. Capture requires Claude Code hooks wired in `.claude/settings.json`. Two hook types:

- **Stop hook** — fires after every 15 human messages. Tracks save points per session in `~/.mempalace/hook_state/`. Honors `stop_hook_active` to prevent infinite loops.
- **PreCompact hook** — fires before context compaction. Always blocks with a comprehensive save instruction (compaction means the AI is about to lose detailed context).

Both hooks invoke the same binary, behind a wrapper that surfaces capture failures to a log file:

```
echo '{"session_id":"...","stop_hook_active":false,"transcript_path":"..."}' | tools/hooks/mempalace-hook-wrapper.sh --hook stop --harness claude-code
```

The wrapper ([`tools/hooks/mempalace-hook-wrapper.sh`](../tools/hooks/mempalace-hook-wrapper.sh)) passes args and stdin through to `mempalace hook run`, captures the exit code and stderr, and appends a single timestamped success/failure line to `.claude/logs/mempalace-hook.log` (gitignored — per-clone state). It always exits 0 to the harness, so capture issues never block the session. The next session's boot procedure reads the log and surfaces unacknowledged failure entries; see [`session-build-lifecycle.md`](session-build-lifecycle.md)'s Recovery section.

Configuration in `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "tools/hooks/mempalace-hook-wrapper.sh --hook stop --harness claude-code"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "tools/hooks/mempalace-hook-wrapper.sh --hook precompact --harness claude-code"
          }
        ]
      }
    ]
  }
}
```

Note: `.gitignore` previously excluded `.claude/*` (with an exception only for `.claude/commands/`). For `settings.json` to ship with the repo, add an exception:

```
!.claude/settings.json
```

`settings.local.json` remains gitignored — it carries per-developer permissions.

## Querying from inside Claude Code

The MemPalace MCP server exposes ~19 tools. Highest-frequency ones:

- `mempalace_search` — semantic search across drawers; returns verbatim content with similarity scores. Use short keyword queries (max 250 chars). Filter with `wing` / `room` for scoped recall.
- `mempalace_list_rooms` / `mempalace_list_wings` / `mempalace_list_drawers` — directory listings.
- `mempalace_kg_query` — knowledge-graph traversal across closets.
- `mempalace_diary_read` — reads the per-day session diary.
- `mempalace_add_drawer` — manual capture (use sparingly; the hooks handle most cases).
- `mempalace_status` — palace overview.

Tag conventions (`exploration` / `decision` / `work`) live in [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md).

## Verifying capture is working

After S-0002 hooks land, run a build session and confirm:

```bash
mempalace status
# Expect: drawer count > 0, last write timestamp matches recent activity
```

If drawers aren't appearing: check `~/.mempalace/hook_state/` for stale lock files; check `mempalace --version` (must be 3.3.3+); check that Claude Code restarted after the `.mcp.json` and `.claude/settings.json` edits.

## Known issues

- **`mempalace_graph_stats.total_rooms` undercount.** The MCP tool `mempalace_graph_stats` reports `total_rooms: 4` against `mempalace_get_taxonomy`'s 5 (verified at S-0032 — `general`, `operations`, `decisions`, `foundation-planning-s0001`, `s0003-adr-collection` all exist via taxonomy and CLI `mempalace status`, but graph_stats's room index drops one). Cosmetic — drawer queries and search are unaffected. Likely cause: the graph index was built when the legacy `decisions` row had only one drawer with a `general`-prefixed ID (`drawer_paideia_general_1d310bc491affc6ec6274280`), and the indexer didn't re-register the room when the prefix later normalized. CLI `mempalace repair --help` covers vector-index rebuild (segfault recovery), not graph-index reindex; no upstream-side fix attempted in S-0032. Workaround: trust `mempalace_get_taxonomy` for room counts; treat `mempalace_graph_stats` as approximate.

## See also

- [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md) — when to apply which tag, and where each tag's drawers go (room-targeting conventions added at S-0032).
- `HANDOFF.md` (top-level) — historical record of the MemPalace setup decisions made in S-0001.
