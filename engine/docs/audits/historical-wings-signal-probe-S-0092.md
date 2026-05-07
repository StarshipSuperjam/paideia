# Historical full-encoded-path wings — signal probe (S-0092)

> Phase 1 of S-0092 (issue close-out campaign C3). Closes the investigation half of [Issue #41](https://github.com/StarshipSuperjam/paideia/issues/41); the execution half (bulk delete) lands in Phase 3 of the same session.

## Scope

Nine MemPalace wings whose names contain the full encoded worktree path (leading `-Users-...`). Their drawers cannot be touched by wing-filtered MCP calls because the upstream filter rejects hyphenated wing names ("wing contains invalid characters" — Issues [#1](https://github.com/StarshipSuperjam/paideia/issues/1), [#2](https://github.com/StarshipSuperjam/paideia/issues/2), [MemPalace/mempalace#1394](https://github.com/MemPalace/mempalace/issues/1394)). The S-0084 [`engine/tools/mempalace_rebuild_hnsw.py`](../../tools/mempalace_rebuild_hnsw.py) work proved direct chromadb-sqlite access bypasses the validator; this probe uses that same direct-access pattern.

## Method

Two-pass probe against `~/.mempalace/palace/chroma.sqlite3` opened read-only:

1. **Stride sample.** Per wing, take the first 200 internal IDs ordered by id, stride-sample 10 across that window. For each sample fetch all `embedding_metadata` rows + the `chroma:document` row; record `tag`, `type`, `added_by`, `room`, and the first 120 chars of body.
2. **Comprehensive aggregate.** Across ALL 37,634 drawers in any wing matching `string_value LIKE '-Users-%'`, count: distinct `added_by` values; distinct `room` values; drawers with non-empty `tag`; drawers with non-empty `type`; the full key set present on any historical-wing drawer.

The aggregate pass is the load-bearing one: it answers definitively whether any curated marker exists in the population. The stride sample is body-content sanity check only.

## Results

### Per-wing counts (Phase 1 census)

| Wing (worktree-name suffix) | Drawer count |
|---|---:|
| `infallible-antonelli-cd2efd` | 6,531 |
| `admiring-heisenberg-c97499` | 6,467 |
| `infallible-mestorf-084f1a` | 5,740 |
| `frosty-dijkstra-484bac` | 4,889 |
| `amazing-shaw-809d26` | 3,252 |
| `tender-jepsen-80be2e` | 2,949 |
| `unruffled-ride-236a8d` | 2,666 |
| `eloquent-knuth-423df2` | 2,652 |
| `hardcore-napier-c3c830` | 2,488 |
| **Total** | **37,634** |

(Drift of +0 vs the S-0088 audit; +67 vs the S-0091 close `mempalace_status` snapshot — auto-capture continued running between sessions before the C3 hook-disable will land in C2-followup work.)

### Aggregate signal markers

| Marker | Count across 37,634 historical-wing drawers |
|---|---:|
| `tag` non-empty | **0** |
| `type` non-empty | **0** |
| `added_by` distinct values | `{'mempalace': 37,567}` (67 drawers omit the field — older auto-capture format) |
| `room` distinct values | `{'general': 37,634}` |
| `decision`/`pushback`/`lesson` markers | **0** (none anywhere in tag, type, or room) |

Stride sample bodies are uniformly conversation-transcript chunks (JSON snippets, partial tool-result bodies, mid-turn assistant text). Representative previews:

- `0b-08b9fb442f86","version":"2.1.121","gitBranch":"claude/infallible-antonelli-cd2efd","slug":"mempalace-structure-and-us`
- `gnostics":null},"requestId":"req_011CaedTv2i82vQJvtaKjXct","type":"assistant","uuid":"12fa7593-161f-4413-abfa-842bf7ff7b`
- `numLines":15,"startLine":395,"totalLines":440}},"sourceToolAssistantUUID":"d043681d-5705-4056-a664-545540ccf8b8","userTy`

The fourth sample in the largest wing surfaced one substantive line — *"both Stop/PreCompact wrapper and post-adr-write hooks will silently fail. Fix path: install the CLI in a location the ho..."* — but it carries no `tag`/`type` and lives in `room: general` with `added_by: mempalace`. This is a captured assistant turn from a debugging session, not a curated decision drawer. The substantive content of that exchange landed in the canonical apparatus elsewhere (the path-fix went into the `scrub_env.sh` hook wiring at S-0050; see [ADR 0050](../../adr/0050-project-venv-and-hook-path-wiring.md)).

## Verdict

**Bulk-delete-clean for all 9 wings. Zero preservation candidates.**

The signal probe confirms what the S-0086 adversarial review hypothesized in recommendation R3 #40C ("Recommend retire if a workaround exists for accessing the wings"). The workaround now exists (S-0084's direct-chromadb pattern); the signal density is verified zero across the entire 37,634-drawer population, not extrapolated from a small sample.

The Phase 1 halt-and-escalate trigger (>20% high-signal density) **does not fire**. Phase 2 (extend `prune_mempalace.py` with `--apply` mode) and Phase 3 (pre-flight backup → user destructive-action confirmation → execute bulk-delete) proceed as planned.

## Cross-references

- [S-0086 adversarial review](mempalace-adversarial-review-S-0086.md) — recommendation R3 #40C, "Recommend retire if a workaround exists; defer if not."
- [Issue #41](https://github.com/StarshipSuperjam/paideia/issues/41) — the close-out scope this probe gates.
- [`engine/tools/prune_mempalace.py`](../../tools/prune_mempalace.py) `enumerate_historical_paths()` (line 176) — the access pattern this probe extends.
- [`engine/tools/mempalace_rebuild_hnsw.py`](../../tools/mempalace_rebuild_hnsw.py) — S-0084's non-destructive direct-chromadb template.
