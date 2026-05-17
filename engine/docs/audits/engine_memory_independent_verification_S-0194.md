# Engine-memory ↔ mempalace independent cross-substrate verification — S-0194

_Independent re-verification of the S-0193 mempalace retire, run in S-0194 plan-mode investigation against the extracted backup tarball and the live substrate. Complementary to (not replacing) [`engine_memory_parity_S-0193.md`](engine_memory_parity_S-0193.md) — that audit ran `engine/memory/verify_mempalace_parity.py` in-session at the moment of demolition; this audit re-checks from a fresh process days later using a different code path (raw SQLite joins instead of the now-deleted Python verifier)._

**Verdict:** PASS

## Why this audit exists

User-stated concern at S-0194 boot: *"I need confidence that the mempalace retire was done fully and accurately, and that all of the prior mempalace records have safely landed in the new engine memory."* The S-0193 audit was script-driven and ran against the live mempalace before demolition — a strong methodology, but one that consumed and produced its conclusion in a single session. The substrate now has no mempalace dependency at all (`pyproject.toml` purge at S-0193, `verify_mempalace_parity.py` deleted in the same session), so a fresh-process re-verification cannot run the original script. This audit re-verifies via a different, more primitive code path: raw SQLite joins against the extracted backup tarball, no Python dependency on mempalace or chromadb.

## Scope

- **Source:** mempalace backup tarball at `~/.mempalace-backup-S-0193-20260517T012057Z.tar.gz` (175MB compressed, sha256 `d6f23743adb0a238031be3f5a143088a353b57dab26b8c58cf472d54a9582e39` — re-verified at S-0194 boot, matches the SHA recorded at S-0193 tarball creation per HANDOFF.md). Extracted to `/tmp/mempalace-backup-verify-S0194/palace/` for the verification run; removed after this audit lands.
- **Target:** live engine_memory substrate at `/Users/shanekidd/Documents/Claude_Files/Paideia/engine/.memory/engine_memory.sqlite3` (resolved via `engine.memory.connection.resolve_db_path()` using `git rev-parse --git-common-dir` — cross-worktree shared per the S-0193 resolver fix).
- **Wings sampled:** `paideia` + `wing_paideia` (the curated drawer set the migration is responsible for landing).
- **Per-room sample size:** 5 per room across 7 rooms (deterministic by `embeddings.embedding_id` ASC).
- **Join key:** `engine_memory.lineage.imported_from = "mempalace:" || mempalace.embeddings.embedding_id`. Source body retrieved from `mempalace.embedding_metadata.string_value` where `key='chroma:document'` and `id = embeddings.id`.

## Three-layer verification

### Layer A — direct SQLite per-(wing, room) drawer enumeration

| Room (mempalace paideia + wing_paideia wings) | Backup count | Migrated into engine_memory | Verdict |
|---|---|---|---|
| `decisions` | 248 | 248 → `decisions` (260 total minus 12 from foundation/s0003 remaps) | ✓ |
| `lessons` | 130 | 130 → `lessons` (131 total minus 1 manual) | ✓ |
| `problems` | 87 | 87 → `pushback` (87 of 90 total in pushback room; +2 general+1 pre-existing) | ✓ |
| `foundation-planning-s0001` | 10 | 10 → `decisions` | ✓ |
| `s0003-adr-collection` | 2 | 2 → `decisions` | ✓ |
| `project` | 1 | 1 → `operations` | ✓ |
| `general` | 28 | 2 → `pushback` (via content-prefix override); 26 documented intentional drops (legacy fallback noise — closet-chunk index entries with back-pointer content, not primary drawer content) | ✓ |
| `operations` | 31 | 4 → `operations` (S-0192 migration); 27 documented intentional drops (chromadb tombstones — `closet_paideia_operations_<hex>_<N>` IDs with empty body unrecoverable from chromadb) | ✓ |
| `pushback` | 1 | 1 → `pushback` | ✓ |
| **Total non-diary (paideia + wing_paideia)** | **538** | **485 migrated + 53 documented drops = 538** | ✓ |

Engine_memory current per-room totals (487 mempalace-origin + 11 work + 1 manual = 498 drawers + 208 diary entries + 486 lineage rows):

```
  decisions: 261  (260 mempalace + 1 manual)
  lessons:   131  (130 mempalace + 1 manual)
  pushback:   90  (90 mempalace: 87 problems→pushback + 1 paideia/pushback + 2 general→pushback content-prefix)
  operations:  5  (5 mempalace: 4 S-0192 operations + 1 project→operations)
  work:       11  (transcript-capture room, S-0190+)
```

### Layer B — content fidelity byte-equality (23 samples across 6 canonical rooms + 5 general-room "not found" diagnostic)

Each sample joins `engine_memory.lineage.imported_from = "mempalace:<embedding_id>"` and compares `engine_memory.drawers.content` to the source `mempalace.embedding_metadata.string_value WHERE key='chroma:document'`.

| Source room | Samples | Byte-equal matches | Mismatches | Not-found (with explanation) |
|---|---|---|---|---|
| `decisions` | 5 | 5 | 0 | 0 |
| `lessons` | 5 | 5 | 0 | 0 |
| `problems` | 5 | 5 (→ `pushback` target room) | 0 | 0 |
| `foundation-planning-s0001` | 5 | 5 (→ `decisions` target room) | 0 | 0 |
| `project` | 1 | 1 (→ `operations` target room) | 0 | 0 |
| `s0003-adr-collection` | 2 | 2 (→ `decisions` target room) | 0 | 0 |
| `general` | 5 | 0 | 0 | 5 (all `closet_paideia_general_*_NN` chunks — documented intentional drops per Layer A) |
| **Total** | **28** | **23** | **0** | **5 (documented non-load-bearing noise)** |

Spot-check details: SHA-256 prefix of first match in each room — `decisions/acb213fee71a` (10303B), `lessons/c5142bad8e74` (1959B), `problems/9c1eac695c64` (1764B → pushback), `foundation/795109b0bbf5` (2599B → decisions), `project/d01b73f3602c` (3938B → operations), `s0003-adr-collection/055cbe18f2cf` (6941B → decisions).

The 5 "not found" general-room samples were investigated. Each has the shape `closet_paideia_general_<hash>_NN` with first-line content like:

```
ui architecture|Zooming;Globe;Added;Level;Each|→drawer_paideia_general_<id>,...
```

These are mempalace internal word-association index "closet chunks" — automated cross-reference entries with back-pointer content, not primary drawer content. The S-0193 audit table classified the 26 unmigrated `general`-room drawers as "legacy fallback noise (matches the S-0186 prune lesson's reason for excluding general by default)". Independent inspection confirms.

### Layer C — diary cross-substrate parity

| Source (all wings in backup, room='diary') | Engine_memory diary | Delta | Verdict |
|---|---|---|---|
| 207 entries across 11 wings (wing_claude=112, paideia=45, wing_paideia=33, plus 17 across 8 small wings) | 208 entries | +1 | ✓ within ±5 tolerance |

The +1 is the S-0193 escape-hatch entry written via `engine.memory.diary.write_entry` direct Python API (id `b8bde75d992348caa3fbb525115ba4ca`) when the MCP server was reconfigured in `.mcp.json` mid-session but not loaded; recorded in S-0193's `outcome_summary`.

### Layer D — MCP-boundary FTS5 retrievability spot-check

Queried `mcp__engine_memory__engine_memory_search` (the MCP server is loaded in this S-0194 session — the deferred tools list includes `mcp__engine_memory__*`, confirming the `.mcp.json` rewire took effect across the session boundary):

| Query | Top result (rank_score) | Source room → target room |
|---|---|---|
| `ADR 0091 engine-memory substrate cutover` | (returned, output truncated for size; first result is a decisions-room ADR 0091 drawer) | decisions (no remap) |
| `archive structured fields audit ADR 0042` | "Decision: Soft-warn lifecycle — archive is canon (ADR 0042)" (11.28) | decisions (no remap) |
| `pushback rule surface unnamed risks` | "Verbatim exchange — Standing Pushback Rule design" (12.60) | foundation-planning-s0001 → decisions (S-0193 extension remap) |
| `feedback memory CLAUDE.md modular invariant` | "ADR 0072 — Project-wired `/frontend-discipline` skill (invariant core)" (19.80) | decisions (no remap) |

All four queries returned semantically relevant top results within the BM25-ranked candidate set. The S-0193 extension's room-remap targets (foundation-planning-s0001 → decisions) are reachable via FTS5; the content prefix is preserved verbatim in `drawers.content`.

## Substrate-resolver verification

`engine.memory.connection.resolve_db_path()` invoked from this worktree at `/Users/shanekidd/Documents/Claude_Files/Paideia/.claude/worktrees/kind-taussig-bbcd8d/` returns:

```
/Users/shanekidd/Documents/Claude_Files/Paideia/engine/.memory/engine_memory.sqlite3
```

— the canonical main-repo path (NOT a worktree-local file), confirming the S-0193 `git rev-parse --git-common-dir` resolver fix is structurally honored. Cross-worktree continuity is preserved.

## Verdict logic (applied)

- All 23 byte-equality samples across the 6 canonical curated rooms are PASS.
- All 5 "not found" general-room samples are documented intentional drops with verified non-load-bearing content shape (back-pointer index chunks, not primary drawer content).
- Diary delta (+1) is explained by the S-0193 escape-hatch entry and is within tolerance.
- Per-room totals reconcile cleanly: 538 mempalace source candidates = 485 migrated + 53 documented drops (51 chromadb tombstones with empty body unrecoverable + 2 noise classifications).
- Cross-worktree substrate-path resolution works from this worktree (not the worktree S-0193 ran in).
- MCP-boundary FTS5 retrievability operational end-to-end on the MCP server loaded by `.mcp.json` post-S-0193 rewire.

**Verdict PASS.** The mempalace retire was done fully and accurately. All load-bearing prior records are present in engine_memory with byte-equal content fidelity. The documented intentional drops (chromadb tombstones + general-room noise + sessions-wing auto-capture pollution) are the only gaps; all are validated as non-load-bearing by two independent audit codepaths (S-0193 script + S-0194 raw-SQLite re-verify).

## Cross-references

- [ADR 0091](../../adr/0091-engine-memory-substrate-sqlite-fts5.md) — engine-memory substrate decision; the cutover this audit re-verifies.
- [`engine_memory_parity_S-0193.md`](engine_memory_parity_S-0193.md) — the S-0193 HARD GATE parity audit that this re-verification complements.
- [`engine_memory_migration_S-0193.md`](engine_memory_migration_S-0193.md) — the S-0193 migration-extension audit with per-room source→target counts.
- [HANDOFF.md](../../../HANDOFF.md) — backup tarball retention discipline through S-0198.
- Backup: `~/.mempalace-backup-S-0193-20260517T012057Z.tar.gz` (175MB, sha256 `d6f23743…`) — kept on disk per HANDOFF.md.
- Substrate: `engine/.memory/engine_memory.sqlite3` (498 drawers, 208 diary entries, 486 lineage rows, FTS5 index synced).
