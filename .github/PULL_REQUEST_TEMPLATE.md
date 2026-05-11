<!--
PR template authored at S-0131 per engine/adr/0066-pr-template-and-branch-protection.md
(Issue #69). Adapted from affaan-m/everything-claude-code; not verbatim.

The checklist encodes Paideia's session-discipline contracts. Items that
do not apply should be marked N/A explicitly rather than left unchecked —
an unchecked item reads as "skipped" in review, not "irrelevant."
-->

## Summary

<!-- One paragraph: what changed, why. -->

## Conventional commit type

<!-- Mark exactly one. The eager-claim case is listed separately because
     `chore(session):` commits should be on their own commit per the
     session-build-lifecycle. -->

- [ ] feat / fix / docs / refactor / chore / test / ci / perf
- [ ] `chore(session):` (eager-claim only; should be on its own commit)

## Discipline checklist

- [ ] Local `validate.py` passes (no hard-fails)
- [ ] Soft-warns reviewed and either resolved or recorded in `outcome_summary`
- [ ] ADR authored or amended if a settled decision landed (link below)
- [ ] MemPalace `decision` drawer captured if an ADR was authored
- [ ] First-exercise readiness note authored if a cross-cutting mechanism is introduced (per [ADR 0053](engine/adr/0053-mechanism-first-exercise-gate.md))
- [ ] Routine-mode `scope_lock` honored (if applicable)
- [ ] Secrets: no credentials, keys, or env values in diff

## Links

- ADR: <!-- link or N/A -->
- Plan file: <!-- link or N/A -->
- Closes: <!-- #<issue> or N/A -->
