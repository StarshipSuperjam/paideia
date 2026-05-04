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
- **Tunnels** (`mempalace_find_tunnels` / `mempalace_list_tunnels` / `mempalace_create_tunnel` / `mempalace_delete_tunnel` / `mempalace_traverse`). Reason: tunnels link rooms across wings; project content lands across multiple worktree-derived wings (per the wing-naming behavior described in Known issues below) plus the historical `paideia` wing and the diary wing (`wing_claude`). Re-evaluate when (if) a second project shares this MemPalace install or when the upstream wing-naming behavior is reconciled with the documented intent.
- **AAAK compressed dialect for project drawers** (`mempalace_get_aaak_spec`). Reason: Paideia drawers are conversational verbatim; AAAK's compression is for memory across thousands of drawers per agent (the diary wing may eventually use AAAK; project drawers do not).

**`agent_name` for the diary:** `claude` — matches MemPalace's own AAAK examples and writes diary entries into a `wing_claude` wing distinct from project-content wings. The diary is the AI's continuity layer across sessions; keeping it in its own wing means project-content drawers and reflection drawers don't compete in semantic search.

**Wing-name reality vs. documented intent.** The project's documented intent (S-0001 / S-0002 era) was a single `paideia` wing for project content plus `wing_claude` for the diary. Actual behavior diverges by version. In mempalace 3.3.3 (S-0040 diagnosis): hook auto-capture derived wing names from the full encoded transcript-path directory (e.g., `-Users-shanekidd-Documents-Claude-Files-Paideia--claude-worktrees-eloquent-knuth-423df2`), producing one wing per worktree. In mempalace 3.3.4 (S-0043 verification, the version now installed in the project venv per [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md)): the derivation in `mempalace/hooks_cli.py:_wing_from_transcript_path()` shifted to `encoded.rsplit("-", 1)[-1]`, returning `wing_<last-token>` — main sessions derive `wing_paideia` (a new wing distinct from the documented bare `paideia`); worktree sessions derive `wing_<random-hash>` (e.g., `wing_a5d511`), still per-worktree because each worktree's path-suffix is unique. The historical bare `paideia` wing exists with 488 drawers across 6 rooms (`general`, `operations`, `decisions`, `foundation-planning-s0001`, `diary`, `s0003-adr-collection`) from manual `mempalace mine --wing paideia` invocations and early-session captures. Consequence: searching across "the project" requires unfiltered `mempalace_search`, not a wing-filtered query, and now spans `paideia` + `wing_paideia` + per-worktree wings + `wing_claude` (diary). See Known issues below for the related wing-filtered-search upstream bug that compounds this.

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

MemPalace ships as a Python package on PyPI. Per [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md), the project pins it in [`engine/tools/requirements.txt`](../tools/requirements.txt) (`mempalace>=3.3.3`) and installs it into the project venv at `<main_repo>/.venv/`. Resolves to 3.3.4 as of S-0043.

```
<main_repo>/.venv/bin/mempalace
<main_repo>/.venv/bin/mempalace-mcp
```

(Pre-S-0043 history: mempalace lived at user-scope at `/Users/<user>/Library/Python/3.9/bin/`. The migration into the venv addressed recurring Python-version issues with the tool and unified the project's Python stack under 3.12.)

The MCP server (`mempalace-mcp`) is registered in `.mcp.json` (gitignored — kept local for parity with the Supabase entry):

```json
{
  "mcpServers": {
    "mempalace": {
      "command": "/Users/<user>/path/to/Paideia/.venv/bin/mempalace-mcp"
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

- **Wing-filtered search throws "Internal error: Error finding id" upstream.** Diagnosed at S-0040 against mempalace 3.3.3; **re-verified at S-0043 against 3.3.4** (now installed in the project venv per [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md)) — bug reproduces verbatim, same error string, same code path. Reproducible across the MCP `mempalace_search` tool and the CLI `mempalace search --wing <name>` for every wing tested (`paideia`, `sessions`, `wing_paideia`). `mempalace_list_wings` and `mempalace status` show the wings exist with the expected drawer counts; the search code path's wing-resolution fails. Wing names containing hyphens (the worktree-derived names produced by hook auto-capture) additionally trigger an MCP-side `"wing contains invalid characters"` rejection before reaching the upstream code path. Workaround: rely on **unfiltered** `mempalace_search` for all queries; results carry their `wing` field for caller-side filtering when needed. Boot-procedure step 3 (`session-build-lifecycle.md`, CLAUDE.md startup ceremony) does not prescribe wing-filtered search — it works with the unfiltered fallback. Filed as Issue [#1](https://github.com/StarshipSuperjam/paideia/issues/1).

- **Hook auto-capture wing-naming derives per-worktree wings.** Diagnosed at S-0040 against mempalace 3.3.3 (full-encoded-path wings); **behavior changed but not fixed in 3.3.4**, re-verified at S-0043. The 3.3.4 derivation in `mempalace/hooks_cli.py:_wing_from_transcript_path()` does `encoded.rsplit("-", 1)[-1]` and returns `wing_<last-token>`. Direct invocation against sample paths: main session derives `wing_paideia`; worktree session derives `wing_<random-hash>` (e.g., `wing_a5d511`) — still per-worktree because each worktree's path-suffix is unique. The S-0001 / S-0002 era documented a single bare `paideia` wing for project content; the new auto-capture `wing_paideia` is a **distinct wing** from the documented `paideia` wing (488 drawers, manually curated as of S-0041). The `mempalace hook run` CLI does not accept a `--wing` argument; the hook wrapper at [`engine/tools/hooks/mempalace-hook-wrapper.sh`](../tools/hooks/mempalace-hook-wrapper.sh) cannot pass a wing override. Compounded by the wing-search bug above: even if the wing-naming were corrected, wing-filtered search would still be broken. Practical impact: project content lands across multiple worktree-derived wings plus a separate `wing_paideia` for main-session captures; unfiltered search still surfaces all of it; the documented bare `paideia` wing remains as a manually-curated anchor from explicit `mempalace_add_drawer` and historical `mempalace mine --wing paideia` invocations. No in-project remediation required while the upstream bugs persist; document as project reality. Filed as Issue [#2](https://github.com/StarshipSuperjam/paideia/issues/2).

## See also

- [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md) — when to apply which tag, and where each tag's drawers go (room-targeting conventions added at S-0032).
- `HANDOFF.md` (top-level) — historical record of the MemPalace setup decisions made in S-0001.
