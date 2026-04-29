# Paideia

A knowledge mastery app built on a pedagogical dependency graph. Generates personalized learning paths, provides AI-driven Socratic teaching, and tracks mastery across texts and sessions. Philosophy is the first domain; the architecture is domain-agnostic.

**Status:** design and prototyping. Foundation phase in progress.

**Repository:** https://github.com/StarshipSuperjam/paideia (private)

---

## What this is

Paideia is built on a **pedagogical dependency graph** — not a historical influence map. The key insight: "you need Kant's epistemology before phenomenology" is a different claim than "Kant influenced Husserl." The graph encodes what you must understand before something else makes sense.

Users select a target topic. The system traverses prerequisites, topologically sorts them, and generates a reading syllabus for each step. A persistent learner model tracks mastery across sessions and texts.

For full project vision and audience framing, see [`docs/MISSION.md`](docs/MISSION.md) (lands in S-0002).

---

## Repo map

```
paideia/
├── README.md                       # this file
├── LICENSE                         # proprietary, all rights reserved (Shane Kidd)
├── CHANGELOG.md                    # change history (Keep-a-Changelog format)
├── SECURITY.md                     # vulnerability disclosure policy
├── CLAUDE.md                       # AI orientation; auto-loaded; lightweight startup ceremony (S-0002)
├── STATE.md                        # current phase + next session's work item
├── ROADMAP.md                      # phase sequence with success criteria
├── HANDOFF.md                      # running log of items deferred to future major-state-transitions
│
├── docs/                           # design documents (lands at start of S-0001 reorganization)
│   ├── MISSION.md                  # vision, audience, principles (S-0002)
│   ├── CROSS_REFERENCES.md         # high-value file-dependency cross-references (S-0002)
│   ├── architecture.md             # graph data model
│   ├── pedagogy.md                 # teaching design
│   ├── learner-model.md            # mastery, decay, events
│   ├── self-correction.md          # tension log, reviewer pipeline
│   ├── infrastructure.md           # tech stack, deployment
│   ├── ui-architecture.md          # globe, syllabus surfaces
│   ├── content-strategy.md         # corpus, licensing
│   ├── session-lifecycle.md        # entry flow
│   ├── reading-system.md           # close reading
│   ├── expansion.md                # future scope
│   ├── business.md                 # commercial model
│   ├── tensions.md                 # open questions (active)
│   ├── ideation.md                 # captured but not yet consumed
│   └── operations/                 # procedures by topic; one file per topic; AI sees topics via `ls` (S-0002)
│
├── adr/                            # numbered Architecture Decision Records (S-0003)
│
├── session/                        # session-protocol layer
│   ├── register_state.json         # counter (next_id, last_claimed)
│   ├── current.json                # claim file for the in-progress session
│   └── archive/                    # closed sessions, one S-NNNN.json per
│
├── supabase/                       # Phase 3+ migrations
│   └── migrations/
│       ├── ROUTING.md              # numeric prefix scheme + per-session narrative manifest (placeholder; Phase 4)
│       └── PREDICATE_MANIFEST.md   # canonical edge-type registry (placeholder; Phase 4)
│
├── tools/                          # build tooling
│   ├── validate.py                 # cross-reference + format validator (extension point for Phase 4 graph audit)
│   ├── sweep_worktrees.sh          # cleanup utility, run on demand
│   ├── setup.sh                    # symlinks pre-commit hook into .git/hooks/
│   └── hooks/
│       └── pre-commit              # validates and enforces bimodal session protocol
│
├── .claude/
│   └── commands/
│       └── start-engine.md         # slash command — claims next session slot
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

Just open Claude Code in this repo and start chatting. Default posture is **design partner**: discuss, sketch, push back, work through ideas in conversation. **No project file edits. No commits. No slot claim.** When a discussion converges on something worth committing, convert with `/start-engine`.

MemPalace captures exploration conversations under the `exploration` tag — knowing "we considered X, rejected for reason Y" prevents re-litigation.

### Build mode — `Start Engine` or `/start-engine`

Type `Start Engine` (or invoke the slash command `/start-engine`) to convert to a build session. The slash command claims the next slot via the eager-claim ritual: bumps `session/register_state.json`, writes `session/current.json`, commits + pushes the claim immediately. Then does the planned work, audits + commits + pushes at close.

Build sessions write to MemPalace under `decision` / `work` tags; build sessions update CHANGELOG.md, ADR statuses, STATE.md.

For procedural depth, see `CLAUDE.md` (S-0002) and `docs/operations/` (S-0002).

---

## Setup for a fresh clone

```bash
git clone https://github.com/StarshipSuperjam/paideia.git
cd paideia

# Install pre-commit hook (validates structure on every commit)
./tools/setup.sh

# Create local .env from template
cp .env.example .env
# Then fill in ANTHROPIC_API_KEY and Supabase credentials

# Create local .mcp.json (the committed copy is gitignored as it carries PATs)
# Configure Supabase MCP (project ref ozooosgnuzxqqypotlke) and MemPalace MCP
# See docs/operations/mempalace-operations.md (S-0002) for MemPalace install

# Restart Claude Code so the new MCP servers load
```

---

## License

Proprietary, all rights reserved. See `LICENSE`.

---

## Project history

Pre-Foundation design phase: 8 of 14 prompt-pack sessions closed (Schema Foundations, Session Lifecycle, Assessment & Mastery Verification, Self-Correction & Node Mapping, Reading System & Outline Generation, Product Identity & Institutional Design, Learner Model Implementation, Seed Graph & Node Schema), settling 12 strong working commitments + 10 architectural decisions absorbed into ADRs 0001-0022 during S-0003.

Foundation phase (S-0001 through S-0003): industry-standard project skeleton, session-protocol layer, MemPalace integration, ADR collection.
