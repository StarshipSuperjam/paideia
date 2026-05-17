# Escalation criteria

> When to interrupt the user mid-session. The general rule lives in `CLAUDE.md`; this file gives worked examples and the calibration heuristics.

## The rule

Auto-mode (and build-mode generally) is biased toward continuous execution. Do **not** pause and escalate to the user EXCEPT for:

1. **Irreversible-with-unclear-path** — a decision propagates as irreversible structure across multiple downstream sessions AND the right direction is genuinely unclear.
2. **Unsolvable** — multiple approaches tried, no viable path.
3. **Destructive-action confirmation** — `rm -rf`, `git reset --hard`, force-push, deleting tracked files in bulk.

Routine judgment calls during a session are **session-internal**. Record them in `session/current.json`'s `outcome_summary`, don't escalate.

## What counts as "irreversible-with-unclear-path"

The decision must satisfy *both* halves:

- **Irreversible** — propagates structurally to multiple downstream artifacts (schema, ADR, naming convention, file layout). Reversing it later means rewriting those artifacts, not patching.
- **Unclear path** — the AI can't make the call from existing material in the repo (CLAUDE.md + docs/ + STATE.md + ROADMAP.md + relevant ADRs). It's not a research-and-decide; it's a value-call where the user's preference is load-bearing and unknown.

If the decision is irreversible but the path is clear from existing material — proceed. If the path is unclear but the decision is reversible — make the best call, log it, move on.

### Worked examples — escalate

- "Should the audit category for missing teaching_notes be `missing_teaching_notes` or fold into `missing_summary`?" — names a category that downstream sessions will reference; once committed, renaming requires migration. The user's editorial preference is unknown.
- "Should this retirement leave a structural artifact behind for in-tree side-by-side comparison, or is git tag/history recovery sufficient?" — the answer depends on whether a current artifact (an ADR, a doc) needs to reference the retired one as a *thing to look at*, not just as history. The escape-hatch pattern in `session-shutdown-sequence.md` allows one-off archives; the call to invoke it is a value judgment.
- "About to write a prerequisite edge claim that I'm not confident is pedagogically correct — is this within scope to commit, or should it sit in `docs/tensions.md` first?" — writing the wrong claim into the seed graph propagates structurally.

### Worked examples — don't escalate

- "Should this commit message say 'add' or 'introduce'?" — reversible and minor; pick one.
- "Two ways to phrase a paragraph in `engine-memory-operations.md`" — purely editorial; no downstream propagation.
- "Validator emits a soft-warn — fix now or note in outcome_summary?" — explicit guidance in `tools-validate-interpretation.md` — note it, don't ask.

## What counts as "unsolvable"

You've tried multiple approaches (read more code, restructured the diff, queried MemPalace, considered alternatives) and there's no viable path forward without a user input the AI doesn't have.

This is rare. Most "I'm stuck" moments are actually "I haven't read enough yet." Before escalating, ask: have I exhausted the existing repo material? Did MemPalace surface anything? Did I check the relevant ADR's Consequences section?

If yes to all and still stuck: escalate with a concrete summary of approaches tried.

## What counts as "destructive"

Always confirm. No exceptions in auto mode.

- `rm -rf` against a directory.
- `git reset --hard` (anything that discards uncommitted work).
- `git push --force` (anything overwriting remote state).
- `git branch -D` for branches that may carry unmerged work.
- Deleting tracked files in bulk (>3 files in one commit).
- Dropping a database table or running a migration that loses data.
- Modifying CI/CD or hooks in ways that bypass safety gates.

The pattern: pause, summarize what's about to change and what'll be lost, ask for confirmation. Yes-from-the-user once does not generalize — the next destructive action needs its own confirmation.

## Calibration

- **User venting/exploring** — looser. Don't interrupt every 30 seconds; let them think aloud.
- **User proposing a commitment** — tighter. Surface specific concerns at the moment of noticing.
- **AI executing in build mode** — even tighter. The interrupt criteria above are the bar.

## See also

- `CLAUDE.md` — the rule itself.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — where session-internal judgment calls land.
