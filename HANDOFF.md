# Handoff Log

> Running log of items deferred to a future *next-session-must-resolve* transition. Not a contract; a convenience so transition sessions don't re-solve already-solved problems. Add entries here ONLY when the next session must pick up the item immediately AND it doesn't belong in ENGINE_LOG, an ADR, or a GitHub Issue (per [ADR 0048](engine/adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — cross-session deferrals route to Issues by default; HANDOFF.md is reserved for session-internal handoffs).
>
> **Disposition discipline (added at S-0036, retroactively applied to live entries at S-0041).** Every section carries a `**Disposition:**` line in one of five forms: `fixed-in-session @ <SHA>`, `deferred-with-user-confirmation`, `out-of-scope`, `not-actionable`, or `tracked-as-issue #<num>`. For resolved entries, a `**Resolved:**` line names the session and downstream artifact (ADR, ENGINE_LOG entry, ops-doc edit, commit SHA). The `engine/tools/audit_handoff_dispositions.py` script audits new sections at session shutdown.
>
> **Prune-on-resolve discipline (added at S-0121 audit inline cleanup).** Resolved sections are pruned at the next interactive session that touches HANDOFF.md. The eight resolved sections from S-0002 / S-0033 / S-0035 / S-0041 / S-0049 / S-0051 / S-0062 / S-0064 retired at S-0121 — content preserved in git history (each section's `**Resolved:**` line named the downstream artifact: ADRs 0045 / 0055, commits `21285f8` / `ae85e20` / `6b7999c` / `2609aaf` / `ca36c17`, Issues #8 / #9 / #17 / #18, and tooling at `engine/tools/scrub_env.sh` / `load_env.py` / `apply_migration.py` / `routine_lifecycle_push.py` — all verified extant at prune time). The S-0121 audit report's User adjudication subsection carries the recommendation for an automated prune-discipline posture rule (extending `audit_handoff_dispositions.py` to flag long-resolved sections for the next interactive HANDOFF touch); downstream session executes if approved.
>
> **Scope discipline.** Add an entry here ONLY when the next session must pick up the item immediately. Cross-session deferrals (bugs, tech-debt, cleanup, enhancements, doc work, open questions, health-check findings) route to GitHub Issues with appropriate labels per ADR 0048. Resolved entries leave under the prune-on-resolve discipline above.

---

_No open handoff entries as of S-0121._
