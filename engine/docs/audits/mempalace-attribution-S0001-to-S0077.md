# MemPalace attribution audit — S-0001 to S-0077

> One-shot audit produced by [`engine/tools/audit_mempalace_attribution.py`](../../tools/audit_mempalace_attribution.py).
> Per [ADR 0056](../../adr/0056-mempalace-mechanical-adoption-checks.md) and the approved plan at `~/.claude/plans/use-of-mempalace-by-velvety-pebble.md` (Part B). Surfaces the per-session list of missing deliberate-content writes (diary entries; pushback / lesson / decision drawers).

## Recovery shape (corrected at S-0080)

S-0079 misread the recovery direction twice (subagent-driven first-person extraction; user-driven analytical-voice from a separate session). The actual recovery shape, per the user's direction:

- The user has the original sessions still accessible.
- The user pastes a brief reflection prompt into each missing session.
- That original session writes its own MemPalace entries in its own voice — no impersonation, honest first-person attribution to its own `S-NNNN`, original session's own context (no transcript re-reading needed).

The reflection prompt to give each original session lives in the chat history where the prompt was developed; copy it from there. It instructs the session to: search MemPalace first to avoid duplicates, then write a diary entry (via `mempalace_diary_write`), pushback drawers (`room=problems`), lesson drawers (`room=lessons`), and decision drawers (`room=decisions`) for any ADRs the session authored — each with `added_by` set to the session's own id.

The S-0079 wrapper `engine/tools/recover_mempalace_from_transcript.py` and the user-driven recovery guide at `engine/docs/audits/mempalace-recovery-guide-user-driven.md` were both deleted at S-0080 — they encoded the wrong shape (separate session reading transcripts) and would mislead future readers.

This audit report (the missing-session list below) is the only S-0079 deliverable that survives. The B1 audit script that produced it (`engine/tools/audit_mempalace_attribution.py`) also stays.

## Summary

- Sessions audited: **77** (S-0001 → S-0077).
- Mode breakdown: interactive=2, routine=17, unmoded=58.
- Categories:
  - **complete**: 18
  - **diary_only_missing**: 17
  - **decisions_missing**: 0
  - **both_missing**: 1
  - **no_signal**: 41

Field semantics:

- `diary` — `✅` if a `room=diary, agent=claude` drawer matches by topic-id or filed_at-window. `❌` if neither.
- `dec` — count of `room=decisions` drawers attributed to the session via `added_by`.
- `adr` — count of ADR files added in the session's commit range.
- `pb` / `les` — pushback / lesson drawer counts attributed to the session.
- `cat` — categorization (see below).

Category meaning:

- `complete` — diary present AND adr count ≤ decision drawer count.
- `diary_only_missing` — no diary; decisions/ADRs match.
- `decisions_missing` — diary present but ADRs > decisions.
- `both_missing` — diary absent AND ADRs > decisions.
- `no_signal` — no diary AND no ADRs in window. Recovery may yield little.

## Interactive sessions

| Session | diary | dec | adr | pb | les | category |
|---|---|---|---|---|---|---|
| S-0072 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0077 | ❌ | 0 | 0 | 0 | 0 | no_signal |

## Routine sessions

| Session | diary | dec | adr | pb | les | category |
|---|---|---|---|---|---|---|
| S-0050 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0053 | ✅(w) | 0 | 0 | 0 | 0 | complete |
| S-0054 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0056 | ✅(w) | 0 | 0 | 0 | 0 | complete |
| S-0057 | ✅(w) | 0 | 0 | 0 | 0 | complete |
| S-0058 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0059 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0061 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0063 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0066 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0068 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0070 | ✅(w) | 0 | 0 | 0 | 0 | complete |
| S-0071 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0073 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0074 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0075 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0076 | ✅(w) | 0 | 0 | 0 | 0 | complete |

## Sessions without `mode` field (pre-S-0048)

| Session | diary | dec | adr | pb | les | category |
|---|---|---|---|---|---|---|
| S-0001 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0002 | ❌ | 2 | 0 | 0 | 0 | diary_only_missing |
| S-0003 | ❌ | 23 | 0 | 0 | 0 | diary_only_missing |
| S-0004 | ❌ | 2 | 0 | 0 | 0 | diary_only_missing |
| S-0005 | ❌ | 2 | 0 | 0 | 0 | diary_only_missing |
| S-0006 | ❌ | 1 | 0 | 0 | 0 | diary_only_missing |
| S-0007 | ❌ | 2 | 0 | 0 | 0 | diary_only_missing |
| S-0008 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0009 | ❌ | 1 | 0 | 0 | 0 | diary_only_missing |
| S-0010 | ❌ | 1 | 0 | 0 | 0 | diary_only_missing |
| S-0011 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0012 | ❌ | 3 | 0 | 0 | 0 | diary_only_missing |
| S-0013 | ❌ | 1 | 0 | 0 | 0 | diary_only_missing |
| S-0014 | ❌ | 1 | 0 | 0 | 0 | diary_only_missing |
| S-0015 | ❌ | 1 | 0 | 0 | 0 | diary_only_missing |
| S-0016 | ❌ | 3 | 0 | 0 | 0 | diary_only_missing |
| S-0017 | ❌ | 1 | 0 | 0 | 0 | diary_only_missing |
| S-0018 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0019 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0020 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0021 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0022 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0023 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0024 | ❌ | 1 | 0 | 0 | 0 | diary_only_missing |
| S-0025 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0026 | ❌ | 1 | 0 | 0 | 0 | diary_only_missing |
| S-0027 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0028 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0029 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0030 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0031 | ❌ | 3 | 0 | 0 | 0 | diary_only_missing |
| S-0032 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0033 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0034 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0035 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0036 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0037 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0038 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0039 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0040 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0041 | ✅(w) | 0 | 0 | 0 | 1 | complete |
| S-0042 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0043 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0044 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0045 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0046 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0047 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0048 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0049 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0051 | ✅ | 0 | 0 | 0 | 0 | complete |
| S-0052 | ✅(w) | 0 | 0 | 0 | 1 | complete |
| S-0055 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0060 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0062 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0064 | ❌ | 0 | 1 | 0 | 0 | both_missing |
| S-0065 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0067 | ❌ | 0 | 0 | 0 | 0 | no_signal |
| S-0069 | ❌ | 0 | 0 | 0 | 0 | no_signal |

## Recovery worklist

All sessions where the diary write is missing — input to `recover_mempalace_from_transcript.py`. Sessions marked `(low signal)` had ≤ 1 commit and no ADRs/decisions; the executor will still scan but the subagent's skip-if-empty rule may apply.

### High-signal (recovery prioritized)

- S-0002 (unmoded) — diary_only_missing — dec=2 commits=0
- S-0003 (unmoded) — diary_only_missing — dec=23 commits=0
- S-0004 (unmoded) — diary_only_missing — dec=2 commits=0
- S-0005 (unmoded) — diary_only_missing — dec=2 commits=0
- S-0006 (unmoded) — diary_only_missing — dec=1 commits=0
- S-0007 (unmoded) — diary_only_missing — dec=2 commits=0
- S-0009 (unmoded) — diary_only_missing — dec=1 commits=0
- S-0010 (unmoded) — diary_only_missing — dec=1 commits=0
- S-0012 (unmoded) — diary_only_missing — dec=3 commits=0
- S-0013 (unmoded) — diary_only_missing — dec=1 commits=0
- S-0014 (unmoded) — diary_only_missing — dec=1 commits=0
- S-0015 (unmoded) — diary_only_missing — dec=1 commits=0
- S-0016 (unmoded) — diary_only_missing — dec=3 commits=0
- S-0017 (unmoded) — diary_only_missing — dec=1 commits=0
- S-0024 (unmoded) — diary_only_missing — dec=1 commits=0
- S-0026 (unmoded) — diary_only_missing — dec=1 commits=0
- S-0031 (unmoded) — diary_only_missing — dec=3 commits=0
- S-0050 (routine) — no_signal — dec=0 commits=2
- S-0054 (routine) — no_signal — dec=0 commits=2
- S-0058 (routine) — no_signal — dec=0 commits=2
- S-0059 (routine) — no_signal — dec=0 commits=2
- S-0060 (build) — no_signal — dec=0 commits=3
- S-0061 (routine) — no_signal — dec=0 commits=2
- S-0062 (build) — no_signal — dec=0 commits=3
- S-0064 (build) — both_missing — dec=0 commits=3 ADRs=0055-apply-migration-wrapping-against-production-reads-gate.md
- S-0066 (routine) — no_signal — dec=0 commits=2
- S-0067 (build) — no_signal — dec=0 commits=2
- S-0068 (routine) — no_signal — dec=0 commits=2
- S-0071 (routine) — no_signal — dec=0 commits=2
- S-0072 (interactive) — no_signal — dec=0 commits=6
- S-0073 (routine) — no_signal — dec=0 commits=2
- S-0074 (routine) — no_signal — dec=0 commits=2
- S-0075 (routine) — no_signal — dec=0 commits=2
- S-0077 (interactive) — no_signal — dec=0 commits=2

### Low-signal (recovery may yield little)

- S-0001 (unmoded) — no_signal — commits=0
- S-0008 (unmoded) — no_signal — commits=0
- S-0011 (unmoded) — no_signal — commits=0
- S-0018 (unmoded) — no_signal — commits=0
- S-0019 (unmoded) — no_signal — commits=0
- S-0020 (unmoded) — no_signal — commits=0
- S-0021 (unmoded) — no_signal — commits=0
- S-0022 (unmoded) — no_signal — commits=0
- S-0023 (unmoded) — no_signal — commits=0
- S-0025 (unmoded) — no_signal — commits=0
- S-0027 (unmoded) — no_signal — commits=0
- S-0028 (unmoded) — no_signal — commits=0
- S-0029 (unmoded) — no_signal — commits=0
- S-0030 (unmoded) — no_signal — commits=0
- S-0043 (unmoded) — no_signal — commits=0
- S-0044 (unmoded) — no_signal — commits=0
- S-0045 (unmoded) — no_signal — commits=0
- S-0046 (unmoded) — no_signal — commits=0
- S-0047 (unmoded) — no_signal — commits=0
- S-0048 (unmoded) — no_signal — commits=0
- S-0049 (unmoded) — no_signal — commits=0
- S-0055 (unmoded) — no_signal — commits=0
- S-0063 (routine) — no_signal — commits=1
- S-0065 (unmoded) — no_signal — commits=0
- S-0069 (unmoded) — no_signal — commits=0

## Sessions with diary already present (no recovery needed)

- S-0032 (unmoded) — diary by topic
- S-0033 (unmoded) — diary by topic
- S-0034 (unmoded) — diary by topic
- S-0035 (unmoded) — diary by topic
- S-0036 (unmoded) — diary by topic
- S-0037 (unmoded) — diary by topic
- S-0038 (unmoded) — diary by topic
- S-0039 (unmoded) — diary by topic
- S-0040 (unmoded) — diary by topic
- S-0041 (unmoded) — diary by window
- S-0042 (unmoded) — diary by topic
- S-0051 (unmoded) — diary by topic
- S-0052 (unmoded) — diary by window
- S-0053 (routine) — diary by window
- S-0056 (routine) — diary by window
- S-0057 (routine) — diary by window
- S-0070 (routine) — diary by window
- S-0076 (routine) — diary by window

