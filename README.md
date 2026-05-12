# Paideia

A knowledge mastery app built on a pedagogical dependency graph. Generates personalized learning paths, provides AI-driven Socratic teaching, and tracks mastery across texts and sessions. Philosophy is the first domain; the architecture is domain-agnostic.

**Project setup and current build state.** `engine/STATE.md` carries the canonical current state (current phase, last build session, next session's work item). `engine/ENGINE_LOG.md` carries the full chronological history of engine changes. Backup tags annotate phase boundaries (`pre-phase-3-v0.0.1` cut before Phase 3 SQL build).

**Repository:** https://github.com/StarshipSuperjam/paideia

---

## What this is

Paideia is built on a **pedagogical dependency graph** — not a historical influence map. The key insight: "you need Kant's epistemology before phenomenology" is a different claim than "Kant influenced Husserl." The graph encodes what you must understand before something else makes sense.

Users select a target topic. The system traverses prerequisites, topologically sorts them, and generates a reading syllabus for each step. A persistent learner model tracks mastery across sessions and texts.

For full project vision and audience framing, see [`product/docs/MISSION.md`](product/docs/MISSION.md). The strong working commitments and architectural decisions are recorded as ADRs split across [`engine/adr/`](engine/adr/) (the AI build apparatus) and [`product/adr/`](product/adr/) (Paideia-the-product).

---

## Repo map

The repo is partitioned into `engine/` (the AI build apparatus the user and Claude run together to construct Paideia) and `product/` (Paideia itself — pedagogy, content, runtime architecture).

```
paideia/
├── README.md                       # this file
├── LICENSE                         # Apache License 2.0 (see NOTICE for copyright)
├── NOTICE                          # Apache 2.0 attribution notice
├── CONTRIBUTING.md                 # contribution guidelines + pointers
├── CODE_OF_CONDUCT.md              # Contributor Covenant v2.1
├── SECURITY.md                     # vulnerability disclosure policy (BYOK posture per ADR 0065)
├── CLAUDE.md                       # AI orientation; auto-loaded by Claude Code; engine-side content kept at root because the harness expects it there (ADR 0037 edge-case (c))
├── ROADMAP.md                      # phase sequence with success criteria; carries [ENGINE] / [PRODUCT] markers
├── HANDOFF.md                      # running log of items deferred to future major-state-transitions
│
├── engine/                         # the AI build apparatus
│   ├── STATE.md                    # current phase + next session's work item
│   ├── ENGINE_LOG.md               # engine state-of-record audit log (Keep-a-Changelog format); was CHANGELOG.md before ADR 0037
│   ├── adr/                        # engine ADRs (graph validation, health checks, expression contracts, the partition itself)
│   │   ├── README.md               # engine-side index
│   │   └── NNNN-<title>.md         # one per decision (0016, 0022, 0036, 0037)
│   ├── operations/                 # procedural docs — one file per topic; the lifecycle, validators, hook wiring, MemPalace conventions
│   ├── session/                    # session-protocol layer
│   │   ├── register_state.json     # counter (next_id, last_claimed, current_status)
│   │   ├── current.json            # claim file — only present during in-progress sessions
│   │   └── archive/                # closed sessions, one S-NNNN.json per
│   └── tools/                      # build tooling
│       ├── validate.py             # cross-reference + format validator (extension point for Phase 4 graph audit per ADR 0016)
│       ├── validate-history.jsonl  # per-invocation telemetry; consumed by health checks (per ADR 0022)
│       ├── sweep_worktrees.sh      # cleanup utility, run on demand
│       ├── setup.sh                # symlinks pre-commit hook into .git/hooks/
│       └── hooks/
│           ├── pre-commit          # validates and enforces bimodal session protocol (build / closing / exploration)
│           └── mempalace-hook-wrapper.sh  # captures stop/precompact events to MemPalace
│
├── product/                        # Paideia itself
│   ├── AGENT_INSTRUCTIONS.md       # rendering policy (product-facing; consumer-of-record is learner-facing prose per ADR 0027)
│   ├── CHANGELOG.md                # reserved learner-visible product release log; first entry at Phase 9 release prep
│   ├── adr/                        # product ADRs (pedagogy, learner model, schema, business, runtime architecture)
│   │   ├── README.md               # product-side index
│   │   └── NNNN-<title>.md         # 33 ADRs (0001–0015 minus 0016, 0017–0021, 0023–0035 minus 0036/0037)
│   └── docs/                       # design documents
│       ├── MISSION.md              # vision, audience framing, strong working commitments (with ADR cross-refs)
│       ├── CROSS_REFERENCES.md     # high-value file-dependency cross-references; phase-boundary checks
│       ├── architecture.md         # graph data model
│       ├── pedagogy.md             # teaching design
│       ├── pedagogy/inferences.md  # inference patterns
│       ├── learner-model.md        # mastery, decay, events
│       ├── self-correction.md      # tension log, reviewer pipeline
│       ├── infrastructure.md       # tech stack, deployment
│       ├── ui-architecture.md      # Discovery / Planning / Engagement triad surfaces
│       ├── content-strategy.md     # corpus, licensing
│       ├── session-lifecycle.md    # entry flow
│       ├── reading-system.md       # close reading
│       ├── expansion.md            # future scope
│       ├── business.md             # commercial model
│       ├── tensions.md             # open questions (active); pre-commit-hook-allowed in exploration mode
│       ├── prep-paideia-prompt-pack.md  # 14-session deliberation prompts (sessions 1–8 closed pre-foundation)
│       ├── mempalace.yaml          # MemPalace wing/room config
│       └── entities.json           # MemPalace entity classification (projects-only)
│
├── build_plan/                     # per-phase build chunks bridging engine and product (orientation + per-phase contracts + migration bridge)
│
├── .claude/                        # Claude Code harness configuration (stays at root per ADR 0037)
│   ├── commands/
│   │   └── start-engine.md         # slash command — claims next session slot
│   ├── settings.json               # Stop and PreCompact hooks wiring MemPalace capture
│   └── settings.local.json         # gitignored; per-developer overrides
│
├── .mcp.json                       # gitignored; MCP server registrations (Supabase + MemPalace)
├── .env                            # gitignored; secrets
└── .env.example                    # template
```

The full repo map mirrors `engine/STATE.md` and `ROADMAP.md`. `engine/STATE.md` names the current phase; `ROADMAP.md` names the whole arc.

---

## How to start a session

This project is built primarily by AI sessions. Two session modes:

### Default mode — exploration

Just open Claude Code in this repo and start chatting. Default posture is **design partner**: discuss, sketch, push back, work through ideas in conversation. **No project file edits to tracked files. No commits. No slot claim.** When a discussion converges on something worth committing, convert with `/start-engine`.

The pre-commit hook restricts exploration-mode commits to: `.claude/plans/`, `HANDOFF.md`, `product/docs/tensions.md`. Anything else is refused with a pointer to `/start-engine`.

MemPalace captures exploration conversations under the `exploration` tag — knowing "we considered X, rejected for reason Y" prevents re-litigation.

### Build mode — `Start Engine` or `/start-engine`

Type `Start Engine` (or invoke the slash command `/start-engine`) to convert to a build session. The slash command claims the next slot via the eager-claim ritual: bumps `engine/session/register_state.json`, writes `engine/session/current.json`, commits + pushes the claim immediately so concurrent sessions cannot collide. Then does the planned work, runs the shutdown sequence (audit + spot-check + `engine/STATE.md` / `engine/ENGINE_LOG.md` updates + archive + commit + push) at close.

Build sessions write to MemPalace under `decision` / `work` tags; build sessions update `engine/ENGINE_LOG.md`, ADR statuses, `engine/STATE.md`.

For procedural depth, see `CLAUDE.md` and `engine/operations/`.

---

## Setup for a fresh clone

```bash
git clone https://github.com/StarshipSuperjam/paideia.git
cd paideia

# Install pre-commit hook (validates structure + enforces session protocol on every commit)
./engine/tools/setup.sh

# Create local .env from template
cp .env.example .env

# Populate .env interactively (one-time; .env is gitignored and persists)
# Prompts only for missing keys. Validates SUPABASE_DB_URL with a real
# psycopg.connect() before writing. Idempotent — re-runnable.
python3 engine/tools/setup_env.py

# Create local .mcp.json (the committed copy is gitignored as it carries PATs)
# Configure Supabase MCP (project ref ozooosgnuzxqqypotlke) and MemPalace MCP
# See engine/operations/mempalace-operations.md for MemPalace install + init
```

After setup, restart Claude Code so the new MCP servers load.

`SUPABASE_DB_URL` is required for Phase 5+ seed-authoring routine sessions and `validate.py`'s graph audit (per [ADR 0016](engine/adr/0016-graph-construction-needs-live-validation.md)). The DB password is dashboard-only by Supabase's design — no CLI/MCP/REST path retrieves it. Get it from `https://supabase.com/dashboard/project/<project-ref>/settings/database` ("Connection string" section, either Direct connection or Session pooler tab works) and paste when `setup_env.py` prompts. Reset the password first if the dashboard shows it as `[YOUR-PASSWORD]`. After this one-time setup, every routine fire reads the populated `.env` automatically.

---

## License

[Apache License 2.0](LICENSE). Copyright (c) 2026 The Paideia Project Contributors; see [NOTICE](NOTICE) for the attribution notice.

The "Paideia" name and product brand are not Apache-licensed. If you fork for App Store distribution, please rebrand. See [CONTRIBUTING.md](CONTRIBUTING.md) for full contribution guidance.
