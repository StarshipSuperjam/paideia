# Session shutdown sequence

> How a build session closes cleanly. Boot procedure lives in [`session-build-lifecycle.md`](session-build-lifecycle.md).

## When this runs

At the end of every build session — once substantive work is at a commitable checkpoint, before the conversation ends. Run in order. Do not skip steps; the shutdown produces the durable artifacts that downstream sessions read.

## Sequence

### 1. Audit pass

Run `tools/validate.py` from the repo root. Resolve any hard-fails — these are blocking by default in the pre-commit hook anyway, so reaching shutdown means the working tree should already be clean of hard-fails. If somehow a hard-fail surfaces (e.g., a file referenced in CROSS_REFERENCES.md that you intended to create but didn't), fix it before continuing.

Soft-warns are not blocking but must be recorded — they feed health-check telemetry. Note the per-category counts; you'll write them into `outcome_summary` below.

### 2. Spot-check

For every artifact created or modified in this session, ask:

- **Confidence labels honest?** If a doc claims "settled," it's settled; if it's a working hypothesis, it says so. Don't overclaim certainty.
- **Type framing correct?** A reference doc reads as reference (declarative). A procedure reads as procedure (imperative). A decision record reads as a decision (Status field, Context, Consequences).
- **Cross-references resolve?** Every link or `path/file.md` mention points at something real. Particularly important for `docs/CROSS_REFERENCES.md` — the validator catches missing files but not wrong paths to existing ones.
- **Voice consistent with the file's purpose?** Operations docs are AI-facing; design docs are human-and-AI-facing; ADRs are decision-of-record.

The audit catches structural mistakes. The spot-check catches judgment mistakes.

### 3. Update `STATE.md`

Edit the `## Current` table:

- **Last build session** → `S-<this session's id> (<date>) — <one-line summary>`.
- **Last commit on main** → leave the placeholder pointing at `git log --oneline -1 main`; the next session reads it live.

Edit the `## Next session work item` block:

- Replace with the next session's scope. Be concrete: what files get authored, what files get retired, what success looks like. The next session reads this cold; it should be sufficient.
- If this session uncovered new work that should sit before what was previously next, surface it here and update `ROADMAP.md` if the change crosses a phase boundary.

### 4. Update `CHANGELOG.md`

Under `[Unreleased]`, add entries by category (Added / Changed / Removed / Deprecated / Fixed / Security). Material-change criteria — log it if it meets *any* of these:

- New top-level file or directory.
- New or removed ADR.
- New or removed entry in `docs/`.
- Breaking change to a schema, predicate, or commitment.
- New session-protocol behavior (hooks, commands, register fields).
- New or changed CHANGELOG-tracked design commitment.

Skip these — not material:

- In-session commit messages on application code (Phase 9+; tracked in git only).
- Typo fixes, formatting cleanups, link repairs.
- Minor wording revisions inside an existing doc.

At the next release tag (e.g., `0.1.0` at Phase 0 close), the `[Unreleased]` block gets promoted to a dated section.

### 5. Fill `session/current.json` `outcome_summary`

~50 words. What got done, soft-warn category counts, anything noteworthy for health-check telemetry. Example shape:

```
"outcome_summary": "Procedural layer landed: CLAUDE.md + 11 operations docs + MISSION.md + CROSS_REFERENCES.md. Hooks wired for MemPalace capture. CONTEXT.md retired. validate.py: 0 hard-fails, 2 soft-warns (expected_future_file_missing for adr/, will resolve in S-0003). Next: S-0003 ADR collection."
```

Honest summaries beat flattering ones — health-check trend analysis depends on them.

### 6. Archive the claim

```bash
mv session/current.json session/archive/S-<NNNN>.json
```

Add a `closed_at` timestamp and update `status` to `closed` (or `closed_partial` if you hit a budget cap mid-work):

```json
{
  "id": "S-<NNNN>",
  "started_at": "...",
  "closed_at": "<ISO-8601 UTC>",
  "status": "closed",
  ...
  "outcome_summary": "..."
}
```

Update `session/register_state.json`:

```json
{
  "next_id": "<unchanged from claim>",
  "last_claimed": "S-<NNNN>",
  "current_status": "closed"
}
```

### 7. Final commit + main FF + push

Commit message uses Conventional Commits with the session ID:

```
<type>(<scope>): <summary>

S-<NNNN> close: <one-line outcome>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Then:

```bash
git -C <parent-repo-path> merge --ff-only <worktree-branch>
git -C <parent-repo-path> push origin main
```

No per-push confirmation — the `/start-engine` invocation at session boot already authorizes the shutdown push (per `session-build-lifecycle.md` Push policy). After the push completes, the session is closed.

## Updating design docs during a session

Design docs in `docs/` (not the operations procedures, the project-content docs: `architecture.md`, `pedagogy.md`, `tensions.md`, etc.) follow a maintenance protocol that applies throughout the session, not just at shutdown:

- **Strong idea clarified or strengthened** → add to the relevant downstream file. If it rises to a core commitment, surface it in `docs/MISSION.md` (Strong working commitments) and `ROADMAP.md` (Strong working commitments referenced throughout).
- **New tension** → add to `docs/tensions.md` with enough context for a future session to understand the stakes. Date the entry.
- **Tension resolved** → move from `docs/tensions.md` to the relevant downstream file with a "Resolved: YYYY-MM-DD" line. Don't delete the entry from `tensions.md` — re-mark it `Resolved` so the historical record is preserved in place.
- **New commitment + reasoning** → both the *what* and the *why* land in an ADR per [`adr-authoring.md`](adr-authoring.md). The conversational story lands in MemPalace under the `decision` tag (per [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md)). The transitional `design-reasoning.md` file (used during S-0001 / S-0002) retired at S-0003 close — its 8 entries became ADRs 0013, 0014, 0015, 0017, 0018, 0019, 0020, 0021.
- **Idea surfaces but isn't ready for a file** → capture in `docs/ideation.md`. When consumed into a downstream file or rejected, update its status with a date.
- **Deprecated files** → absorption + delete pattern. (a) Absorb the reasoning into the right downstream artifact (an ADR for structural decisions; a doc revision for content; a MemPalace `decision` drawer for the conversational story). (b) `git rm` the original. Recovery is via git tag (e.g., `pre-foundation-v0.0.0`) or `git show <commit>:<path>`. Update any references in `docs/CROSS_REFERENCES.md` and consuming docs in the same commit. *Escape hatch:* if a retired structural artifact (a schema, graph snapshot, migration export) would benefit from in-tree side-by-side comparison with a current artifact — and that need is referenced from a current ADR or doc — file it as `_archive/<descriptive-slug>/MANIFEST.md` + the artifact (one-off, not the default). The S-0003 retirement of `design-reasoning.md` and the S-0002 retirement of `CONTEXT.md` are absorption + delete examples; neither was archived because the reasoning was fully redistributed.
- **Dead ends** → don't record. Design docs are forward-looking; MemPalace `exploration` drawers carry the dead-end reasoning if anyone ever needs it.
- **Note dates only where the date is the artifact's content.** A CHANGELOG entry's date, a Resolved-tension marker's `Resolved: YYYY-MM-DD`, an ADR's `Date:` header field — these are the artifact doing its job. Inside body prose of governed files (per [`document-voice.md`](document-voice.md)), revision dates and session-attribution markers like `**Added: YYYY-MM-DD (S-NNNN)**` migrate to CHANGELOG and git history; the body describes present state, not the path the file took to it.

These updates each generate a CHANGELOG entry per the material-change criteria above.

## Partial closure (budget cap reached)

If a session hits its budget cap (per CLAUDE.md guidance) mid-work:

1. Halt at the next sensible boundary (don't leave the working tree in an unparseable state).
2. Run validate.py. Address any hard-fails.
3. Fill `outcome_summary` with what got done **and** what remains. Mark status `closed_partial`.
4. Update STATE.md's next-session work item to the unfinished portion plus context for the picking-up session.
5. Archive, commit (`<type>(<scope>): <summary> — partial close`), FF, push.

The next session picks up cleanly from STATE.md without re-deriving where things left off.

## Recovery (interrupted shutdown)

A clean close runs steps 1–7 in sequence. If the session crashes, hits a network error, or otherwise halts mid-shutdown, the observable state determines the recovery path:

1. **Halted before step 6 (archive).** `current.json` present; `register_state.json` `current_status: in_progress`. Resume from step 1 — run `tools/validate.py`, complete spot-check, finish updating STATE.md / CHANGELOG, fill `outcome_summary`, then archive and final-commit.

2. **Halted between archive (step 6) and final commit (step 7).** `archive/S-<NNNN>.json` present, `current.json` absent, `register_state.json` `current_status: closed`. The archive move sits unstaged or staged in the working tree. Stage and commit the planned final commit; FF main; push.

3. **Halted after final commit, before FF + push.** Final commit exists locally; `git log origin/main..HEAD` shows it. FF main and push. No state edits required.

4. **Split state.** Both `archive/S-<NNNN>.json` and `current.json` present, or `register_state.json` `current_status` disagrees with which file exists. This shape should not occur with a clean close. Reconcile manually — read both files, identify which carries the fuller `outcome_summary`, do not delete either blindly. Escalate per [`escalation-criteria.md`](escalation-criteria.md) if the right reconciliation is unclear.

The recovery procedure is documented for completeness; it has not been exercised on a real interrupted close.

## See also

- [`session-build-lifecycle.md`](session-build-lifecycle.md) — open-of-session protocol.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — soft-warn category meanings.
- [`health-check.md`](health-check.md) — what telemetry feeds the periodic audit.
