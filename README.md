# Paideia

A knowledge mastery app built on a pedagogical dependency graph. Generates personalized learning paths, provides AI-driven Socratic teaching, and tracks mastery across texts and sessions. Philosophy is the first domain; the architecture is domain-agnostic.

**Status:** design and prototyping. Foundation phase closed (S-0003); Phase 1 (Contract Lock) opens at S-0004.

**Repository:** https://github.com/StarshipSuperjam/paideia (private)

---

## What this is

Paideia is built on a **pedagogical dependency graph** — not a historical influence map. The key insight: "you need Kant's epistemology before phenomenology" is a different claim than "Kant influenced Husserl." The graph encodes what you must understand before something else makes sense.

Users select a target topic. The system traverses prerequisites, topologically sorts them, and generates a reading syllabus for each step. A persistent learner model tracks mastery across sessions and texts.

For full project vision and audience framing, see [`docs/MISSION.md`](docs/MISSION.md). The 12 strong working commitments and 10 architectural decisions are recorded as ADRs in [`adr/`](adr/) (the contract layer).

---

## Repo map

```
paideia/
├── README.md                       # this file
├── LICENSE                         # proprietary, all rights reserved (Shane Kidd)
├── CHANGELOG.md                    # change history (Keep-a-Changelog format)
├── SECURITY.md                     # vulnerability disclosure policy
├── CLAUDE.md                       # AI orientation; auto-loaded; lightweight startup ceremony
├── STATE.md                        # current phase + next session's work item
├── ROADMAP.md                      # phase sequence with success criteria
├── HANDOFF.md                      # running log of items deferred to future major-state-transitions
│
├── docs/                           # design documents
│   ├── MISSION.md                  # vision, audience framing, strong working commitments (with ADR cross-refs)
│   ├── CROSS_REFERENCES.md         # high-value file-dependency cross-references; phase-boundary checks
│   ├── architecture.md             # graph data model
│   ├── pedagogy.md                 # teaching design
│   ├── learner-model.md            # mastery, decay, events
│   ├── self-correction.md          # tension log, reviewer pipeline
│   ├── infrastructure.md           # tech stack, deployment
│   ├── ui-architecture.md          # Discovery / Planning / Engagement triad surfaces
│   ├── content-strategy.md         # corpus, licensing
│   ├── session-lifecycle.md        # entry flow
│   ├── reading-system.md           # close reading
│   ├── expansion.md                # future scope
│   ├── business.md                 # commercial model
│   ├── tensions.md                 # open questions (active)
│   ├── ideation.md                 # captured but not yet consumed
│   ├── prep-paideia-prompt-pack.md # 14-session deliberation prompts (sessions 1–8 closed pre-foundation)
│   ├── mempalace.yaml              # MemPalace wing/room config
│   ├── entities.json               # MemPalace entity classification (projects-only)
│   └── operations/                 # procedures by topic; one file per topic; AI sees topics via `ls`
│
├── adr/                            # 22 numbered Architecture Decision Records (all Status: Accepted)
│   ├── README.md                   # index + status conventions; full Nygard guidance in docs/operations/adr-authoring.md
│   └── NNNN-<title>.md             # one per decision (0001–0012 commitments; 0013–0022 architectural decisions)
│
├── session/                        # session-protocol layer
│   ├── register_state.json         # counter (next_id, last_claimed, current_status)
│   ├── current.json                # claim file — only present during in-progress sessions
│   └── archive/                    # closed sessions, one S-NNNN.json per
│
├── supabase/                       # Phase 3+ migrations
│   └── migrations/
│       ├── ROUTING.md              # numeric prefix scheme + per-session narrative manifest (placeholder; Phase 4)
│       └── PREDICATE_MANIFEST.md   # canonical edge-type registry (placeholder; Phase 4)
│
├── tools/                          # build tooling
│   ├── validate.py                 # cross-reference + format validator (extension point for Phase 4 graph audit)
│   ├── validate-history.jsonl      # per-invocation telemetry; consumed by health checks (per ADR 0022)
│   ├── sweep_worktrees.sh          # cleanup utility, run on demand
│   ├── setup.sh                    # symlinks pre-commit hook into .git/hooks/
│   └── hooks/
│       └── pre-commit              # validates and enforces bimodal session protocol (build / closing / exploration)
│
├── .claude/
│   ├── commands/
│   │   └── start-engine.md         # slash command — claims next session slot
│   ├── settings.json               # Stop and PreCompact hooks wiring MemPalace capture
│   └── settings.local.json         # gitignored; per-developer overrides
│
├── .mcp.json                       # gitignored; MCP server registrations (Supabase + MemPalace)
├── .env                            # gitignored; secrets
└── .env.example                    # template
```

The full repo map mirrors `STATE.md` and `ROADMAP.md`. `STATE.md` names the current phase; `ROADMAP.md` names the whole arc.

---

## How to start a session

This project is built primarily by AI sessions. Two session modes:

### Default mode — exploration

Just open Claude Code in this repo and start chatting. Default posture is **design partner**: discuss, sketch, push back, work through ideas in conversation. **No project file edits to tracked files. No commits. No slot claim.** When a discussion converges on something worth committing, convert with `/start-engine`.

The pre-commit hook restricts exploration-mode commits to: `.claude/plans/`, `HANDOFF.md`, `docs/tensions.md`, `docs/ideation.md`. Anything else is refused with a pointer to `/start-engine`.

MemPalace captures exploration conversations under the `exploration` tag — knowing "we considered X, rejected for reason Y" prevents re-litigation.

### Build mode — `Start Engine` or `/start-engine`

Type `Start Engine` (or invoke the slash command `/start-engine`) to convert to a build session. The slash command claims the next slot via the eager-claim ritual: bumps `session/register_state.json`, writes `session/current.json`, commits + pushes the claim immediately so concurrent sessions cannot collide. Then does the planned work, runs the shutdown sequence (audit + spot-check + STATE/CHANGELOG updates + archive + commit + push) at close.

Build sessions write to MemPalace under `decision` / `work` tags; build sessions update `CHANGELOG.md`, ADR statuses, `STATE.md`.

For procedural depth, see `CLAUDE.md` and `docs/operations/`.

---

## Setup for a fresh clone

```bash
git clone https://github.com/StarshipSuperjam/paideia.git
cd paideia

# Install pre-commit hook (validates structure + enforces session protocol on every commit)
./tools/setup.sh

# Create local .env from template
cp .env.example .env
# Then fill in ANTHROPIC_API_KEY and Supabase credentials

# Create local .mcp.json (the committed copy is gitignored as it carries PATs)
# Configure Supabase MCP (project ref ozooosgnuzxqqypotlke) and MemPalace MCP
# See docs/operations/mempalace-operations.md for MemPalace install + init
```

After setup, restart Claude Code so the new MCP servers load.

---

## License

Proprietary, all rights reserved. See `LICENSE`.

---

## Project history

**Pre-foundation design phase.** 8 of 14 prompt-pack sessions closed (Schema Foundations, Session Lifecycle, Assessment & Mastery Verification, Self-Correction & Node Mapping, Reading System & Outline Generation, Product Identity & Institutional Design, Learner Model Implementation, Seed Graph & Node Schema). Settled the 12 strong working commitments and the architectural decisions absorbed into ADRs 0001–0022 during S-0003. Backup tag at `pre-foundation-v0.0.0` (commit `fa70b8c`).

**Foundation phase (S-0001 → S-0003) — closed.** Industry-standard project skeleton, session-protocol layer with eager-claim ritual + bimodal hook, MemPalace integration with capture hooks, procedural layer (CLAUDE.md + 11-file `docs/operations/` library + MISSION.md + CROSS_REFERENCES.md), 22-ADR collection. `tools/validate.py` returns 0 hard-fails / 0 soft-warns at Foundation close.

**Phase 1 (Contract Lock) — pending.** Opens at S-0004 with prompt-pack Session 9 (Engagement Depth Aggregation). Per [`ROADMAP.md`](ROADMAP.md), Phase 1 also closes prompt-pack Sessions 10–11, authors `AGENT_INSTRUCTIONS.md`, and adds `confidence_level` to the node schema.
