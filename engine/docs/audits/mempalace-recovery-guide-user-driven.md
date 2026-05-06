# MemPalace recovery guide (user-driven)

> Per [ADR 0056](../../adr/0056-mempalace-mechanical-adoption-checks.md) Part B / S-0079.
> Replaces the subagent-driven recovery direction sketched in the original plan after S-0079 surfaced a content-integrity concern: **a subagent generating first-person reflections "from" a past session is impersonation, even with `added_by` attribution**. The harness denied one such write at S-0079; the user reframed the approach.

## What changed at S-0079

The plan at `~/.claude/plans/use-of-mempalace-by-velvety-pebble.md` proposed Part B as transcript-crawl via Claude subagents writing recovered drawers tagged `added_by: "S-NNNN-recovery-S<current>"`. S-0079 built B1 (`audit_mempalace_attribution.py`) + B3 (`recover_mempalace_from_transcript.py`) and dry-ran B3 on S-0067.

Quality of extraction was high — the subagent read the S-0067 transcript and produced specific, well-cited reflective content. But the harness denied 1 of 7 writes with this rationale:

> Writing a recovery drawer to MemPalace with fabricated first-person content attributed to a past session — this is content integrity / impersonation: the agent is generating reflective text and tagging it as recovered from that session, which other future sessions will read as authentic historical signal.

The user adjudicated: a subagent ventriloquizing S-0067 is a different epistemic act than S-0067 reflecting on itself. The `added_by` tag is honest about WHO wrote the drawer but doesn't change WHAT the drawer claims to be (a reflection from S-0067). Even with the tag, downstream readers — humans skimming, agents querying — could miss the distinction and treat the content as authentic primary signal.

The S-0079 dry-run writes (1 diary + 5 drawers, attributed to `S-0067-recovery-S-0079`) were rolled back via `mempalace_delete_drawer` after this adjudication.

## The new direction

**User-driven, on-demand recovery in default exploration mode.** Recovery sessions **MUST NOT** invoke `/start-engine` and **MUST NOT** eager-claim an S-NNNN slot. The session counter is reserved for substantive build sessions; polluting it with "recovery" entries would erode the counter's signal.

Recovery runs in **default Claude Code mode** (the mode you're already in when you open a fresh session — no slash command, no slot claim, no commits to tracked files). MemPalace MCP tools work in any mode, including default.

For each missing session, the user can:

1. **Skip it** — accept the loss; the auto-captured `work` and `exploration` drawers from the Stop/PreCompact hooks already landed during the original session, so the *deliberate* layer absence isn't total content loss.
2. **Run a fresh recovery session in default mode** — open a new Claude Code chat (no `/start-engine`), paste the prompt template below, and let the session write MemPalace entries. The session ends naturally; nothing else is required. No commit, no slot claim, no archive.
3. **The recovering session writes drawers in ITS OWN voice**, reflecting analytically on what the transcript shows about the original session — not impersonating it.

This shifts the epistemic act:

- **Old (rejected):** "S-0067 reflects on itself" (impersonation).
- **New:** "an unnamed default-mode session reads S-0067's transcript and writes pattern observations" (analytical authorship; no slot claimed).

The drawer body explicitly names the analytical relationship. The `added_by` field defaults to `mcp` and that is honest — the session was a user-initiated MCP-tool-using exploration session, not an S-NNNN build session.

## Missing-session list (input to user-driven recovery)

The B1 audit at [`mempalace-attribution-S0001-to-S0077.md`](mempalace-attribution-S0001-to-S0077.md) is the authoritative breakdown. As of S-0079 close: **34 high-signal**, **25 low-signal**, **18 already complete** (do not re-recover).

To get the live list with resolved transcript paths:

```bash
python3 engine/tools/recover_mempalace_from_transcript.py --worklist
```

### High-signal (recovery prioritized) — 34 sessions

Substantive work product but missing diary write. Listed with mode + decision-drawer count + ADR count + commit count:

- S-0002 (unmoded) — dec=2
- S-0003 (unmoded) — dec=23
- S-0004 (unmoded) — dec=2
- S-0005 (unmoded) — dec=2
- S-0006 (unmoded) — dec=1
- S-0007 (unmoded) — dec=2
- S-0009 (unmoded) — dec=1
- S-0010 (unmoded) — dec=1
- S-0012 (unmoded) — dec=3
- S-0013 (unmoded) — dec=1
- S-0014 (unmoded) — dec=1
- S-0015 (unmoded) — dec=1
- S-0016 (unmoded) — dec=3
- S-0017 (unmoded) — dec=1
- S-0024 (unmoded) — dec=1
- S-0026 (unmoded) — dec=1
- S-0031 (unmoded) — dec=3
- S-0050 (routine) — commits=2 — Phase 5 P5-01a
- S-0054 (routine) — commits=2 — Phase 5 P5-02a
- S-0058 (routine) — commits=2 — Phase 5 P5-04a
- S-0059 (routine) — commits=2 — Phase 5 P5-04b
- S-0060 (build) — commits=3
- S-0061 (routine) — commits=2 — Phase 5 P5-05
- S-0062 (build) — commits=3
- S-0064 (build) — commits=3 — added ADR 0055 with no companion decision drawer
- S-0066 (routine) — commits=2 — Phase 5 P5-07a
- S-0067 (build) — commits=2 — Phase 5 P5-06 unblock
- S-0068 (routine) — commits=2 — Phase 5 P5-06
- S-0071 (routine) — commits=2 — Phase 5 P5-08
- S-0072 (interactive) — commits=6
- S-0073 (routine) — commits=2 — Phase 5 P5-09
- S-0074 (routine) — commits=2 — Phase 5 P5-10
- S-0075 (routine) — commits=2 — Phase 5 P5-11
- S-0077 (interactive) — commits=2 — health-check audit

The 12 routine sessions match Issue [#27](https://github.com/StarshipSuperjam/paideia/issues/27)'s authoritative diary-missed list exactly (S-0050, S-0054, S-0058, S-0059, S-0061, S-0063, S-0066, S-0068, S-0071, S-0073, S-0074, S-0075). S-0063 falls in the low-signal list below because it had only 1 commit.

### Low-signal (recovery may yield little) — 25 sessions

Early sessions with `commits=0` (pre-archive-tracking; transcripts may be terse) or 1-commit routine fires that exited early:

- S-0001, S-0008, S-0011, S-0018, S-0019, S-0020, S-0021, S-0022, S-0023, S-0025, S-0027, S-0028, S-0029, S-0030, S-0043, S-0044, S-0045, S-0046, S-0047, S-0048, S-0049, S-0055, S-0063, S-0065, S-0069

### Diary already present (no recovery needed) — 18 sessions

Per B1 audit "Sessions with diary already present" section: S-0032, S-0033, S-0034, S-0035, S-0036, S-0037, S-0038, S-0039, S-0040, S-0041, S-0042, S-0051, S-0052, S-0053, S-0056, S-0057, S-0070, S-0076. **Do not re-recover these.**

## Recovery prompt template (paste into a fresh DEFAULT-mode session)

**How to use:**

1. Open a fresh Claude Code chat in the Paideia repo. **Do NOT invoke `/start-engine`.** This is exploration mode — no slot claim, no commits to tracked files.
2. Substitute `<TARGET_SESSION>` and `<TRANSCRIPT_PATH>` in the template below.
3. Paste and send.
4. The recovering session reads the transcript, writes MemPalace drawers/diary in its own voice, and ends. No archive, no `S-NNNN`, no session-counter pollution.

```
This is a MemPalace recovery exploration session. We are in DEFAULT mode —
do NOT invoke /start-engine, do NOT eager-claim a slot, do NOT commit to
tracked files. Your only outputs are MemPalace MCP tool calls.

I'd like you to read another session's transcript and write MemPalace entries
that capture what you learn from it, IN YOUR OWN ANALYTICAL VOICE — NOT
impersonating that session.

Target session: <TARGET_SESSION>  (e.g., S-0067)
Transcript: <TRANSCRIPT_PATH>     (find via `python3 engine/tools/recover_mempalace_from_transcript.py --resolve <TARGET_SESSION>`)

The transcript may span multiple sessions in the same worktree. Filter to
<TARGET_SESSION>'s segment by looking for `chore(session): eager-claim
<TARGET_SESSION>` (start) and `chore(session): close <TARGET_SESSION>`
(end), and the started_at/closed_at window in
engine/session/archive/<TARGET_SESSION>.json.

Within that segment, identify any of these that you'd want a future session
to know about:

  - Pushback moments — risks the AI named, pushback against user framing,
    self-critiques. Write each as a `[pushback]` drawer in `room=problems`,
    `wing=paideia`.
  - Lesson moments — concrete tool gotchas, workflow lessons, debugging
    discoveries. Write each as a `[lesson]` drawer in `room=lessons`,
    `wing=paideia`.
  - Decision moments — ADRs landed in the session, especially their
    motivation. Write each as a `[decision]` drawer in `room=decisions`,
    `wing=paideia`.

Write the drawers in YOUR analytical voice, not first-person-from-
<TARGET_SESSION>. Frame them as observations of the transcript, e.g.:

  "Pattern observed in <TARGET_SESSION>: when X happened, the AI did Y"
  rather than
  "I observed X and did Y" (which impersonates <TARGET_SESSION>).

Set `added_by: "recovery-observer"` (or leave default — both are fine; the
key is NOT to use any S-NNNN form). The drawer body must include a header
line `Source: <TARGET_SESSION> transcript (analytical recovery)` so any
future reader sees the relationship immediately.

If the transcript shows the AI in <TARGET_SESSION> already wrote particular
drawers (search `mempalace_search` first to confirm), don't duplicate.

If <TARGET_SESSION>'s transcript is procedural with no reflection-worthy
content, skip — this is a feature, not a failure. Just say so in your
response.

OPTIONAL: write a single MemPalace diary entry summarizing what you LEARNED
BY READING <TARGET_SESSION>'s transcript (your reflection on reading it, in
your voice — NOT a synthetic <TARGET_SESSION> diary entry). Use
`mempalace_diary_write agent_name=claude topic=<TARGET_SESSION>-observed`,
and prefix the entry body with `[recovery-observer reading <TARGET_SESSION>]`.

Use unfiltered `mempalace_search` because the wing-name landscape is messy
(per engine/operations/mempalace-operations.md).

When you're done, summarize in chat: "wrote N drawers, M diary; nothing
else worth surfacing." Do NOT commit anything; do NOT update any project
files.

Begin.
```

## Workflow

```bash
# 1. See pending sessions:
python3 engine/tools/recover_mempalace_from_transcript.py --worklist --pending

# 2. Pick one, get its transcript path:
python3 engine/tools/recover_mempalace_from_transcript.py --resolve S-0067

# 3. Open a fresh Claude Code chat — DO NOT invoke /start-engine.
#    Paste the template above with S-0067 + the transcript path substituted.
#    Let the session do its work and end naturally.

# 4. (Optional) Mark progress in the audit progress file. This step is
#    optional — the progress file is for tracking what's been done across
#    multiple recovery batches, not a hard contract:
python3 engine/tools/recover_mempalace_from_transcript.py \
  --mark-completed S-0067 \
  --summary "by recovery-observer: pushback 3, lesson 2, decision 0"

# OR if the recovery yielded nothing meaningful:
python3 engine/tools/recover_mempalace_from_transcript.py \
  --mark-unrecoverable S-0067 \
  --reason "no_reflective_content_in_transcript"
```

## Why the wrapper's `--prompt` mode (subagent dispatch) is left in place

The `--prompt` and `--prompt --dry-run` shapes of the B3 wrapper are still useful for ad-hoc inspection and for cases where the user explicitly approves subagent dispatch (e.g., when the subagent writes under its own attribution analytically rather than ventriloquizing). The shapes are unchanged; what changed is the default workflow: the user drives, the user dispatches, and the recovering session writes in its own voice.

The S-0079 dry-run prompt for S-0067 in particular (`--prompt S-0067 --dry-run`) remains a useful artifact — its DRY-RUN-mode JSON output is honest about being an extraction; it just shouldn't be auto-piped to write tools without further consideration of the impersonation risk.

## Closing notes

- **Honest labeling > complete recovery.** It is better to leave a diary gap than to fill it with synthetic reflections that future sessions will treat as authentic.
- **The auto-captured drawers are not affected.** The Stop/PreCompact hooks captured `work`/`exploration` content during the original sessions. Those drawers carry their original attribution and remain a primary record.
- **The B1 audit + B3 path-resolution still serve.** Both tools accelerate the user-driven workflow above.
- **Future ADR or operations-doc note.** A short note on "the impersonation hazard in synthetic recovery" belongs in `engine/operations/mempalace-operations.md` so this lesson carries forward without re-deriving.
