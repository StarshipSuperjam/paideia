# Anti-rationalization reference card

> Companion reference for [`/review`](SKILL.md) and [`/security-review`](../security-review/SKILL.md). The canonical version of the table lives here; both skills reference it. Authored at S-0134 per [ADR 0070](../../../engine/adr/0070-project-wired-review-skill.md) (adapted from `addyosmani/agent-skills/skills/code-review-and-quality/references/anti-rationalization.md` with Paideia-specific rows added).

## The table

A reviewer (or reviewee) tempted by any false claim on the left should read the reality check on the right. The table is consulted whenever a review finding is being downgraded, dismissed, or deferred — *especially* when the reason feels convincing.

| False claim | Reality check |
|---|---|
| "It works, that's sufficient." | Unreadable or insecure working code is compounding debt. Working ≠ done. |
| "Author knows it's correct." | Authors miss their own assumptions. Review catches blind spots that re-reading the diff cannot. |
| "We'll clean up later." | Deferred cleanup doesn't happen. Per `engine/operations/issue-discipline.md`: either file an Issue (if real and out-of-scope) or fix in-context now. "Later" is not a routing option. |
| "AI code is probably fine." | AI-generated code needs *heightened* scrutiny, not reduced. The author and the AI share blind spots. The reviewer's job is the fresh-eyes pass. |
| "Passing tests = good code." | Tests are necessary but not sufficient. They don't catch architecture, readability, security, or contract drift. |
| "validate.py passed, ship it." | (Paideia-specific.) `validate.py` is contract-shape enforcement — soft-warns + a handful of hard-fails for known structural failure modes. Five-axis review is orthogonal: semantic correctness, readability, architecture, security depth, performance. Both passes are load-bearing. |
| "It's in scope_lock." | (Paideia-specific.) Scope_lock per [ADR 0051](../../../engine/adr/0051-routine-mode-and-engine-loop.md) is path-level safety — "did the routine touch only allowed paths?" Review is correctness-level — "is what landed actually correct?" Both apply. A scope_lock-compliant commit can still be wrong. |
| "The cold-review subagent at shutdown will catch it." | (Paideia-specific.) Cold-review per [ADR 0038](../../../engine/adr/0038-expression-contract-for-ai-authored-code.md) / [ADR 0039](../../../engine/adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) is a session-end pass against the contract block. `/review` is a pre-merge pass against the implementation. Cold-review catches "code drifted from its contract"; `/review` catches "the contract itself was wrong, or the implementation has issues the contract doesn't bind." Both are load-bearing. |
| "This is a small change, no review needed." | "Small" is judgment-bound. The change-size discipline in [`SKILL.md`](SKILL.md) gives the operational test. A one-line `if` flip can be a critical bug; a 300-line refactor can be uniformly correct. Calibrate honestly. |
| "It's a routine-mode change; the apparatus catches everything." | (Paideia-specific.) Routine-mode catches *scope* (path-level) and *master plan integrity* (auto_target.json keys). It does not catch *correctness* of the substantive deliverable. Skim every routine-batch landing. |
| "The PR title says what it does." | The PR title is one sentence. Review walks the implementation. Trusting the title without reading is the failure mode the table exists to catch. |
| "I read the diff and it looks fine." | "Looks fine" is the rationalization. Walk the five axes. Apply the overlays. Calibrate severity. Output the structured report. |
| "Adding this complexity is necessary for future requirements." | Per CLAUDE.md: "Don't design for hypothetical future requirements. Three similar lines is better than a premature abstraction." If the requirement isn't here, the abstraction is speculative. |
| "I added error handling because it's good practice." | Per CLAUDE.md: "Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries." Defensive coding inside trusted boundaries is dead weight. |
| "The comment explains what the code does, so the code is fine." | Per CLAUDE.md: "Don't explain WHAT the code does, since well-named identifiers already do that." If the code needs a what-comment, rename for clarity instead. Why-comments only when non-obvious. |

## How to use the table during review

1. Walk every finding you're tempted to downgrade or dismiss.
2. Find the row that matches your reason for downgrading.
3. Read the reality check.
4. If the reality check applies — restore the finding's severity.
5. If your reason genuinely doesn't match any row (legitimate exception) — record it in the review report's "Anti-rationalization self-check" section with the specific reason. The act of writing the exception out is the calibration.

## Why this is a separate file

Per [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md), the SKILL.md is the recipe (read top-to-bottom at review time). This table is reference (consulted multiple times during a single review). The partition is structural, not stylistic.

Both skills (`/review` and `/security-review`) share this single canonical table. Adding a new row updates one file; both skills pick up the change.

## See also

- [`SKILL.md`](SKILL.md) — `/review` recipe.
- [`../security-review/SKILL.md`](../security-review/SKILL.md) — `/security-review` recipe (reuses this table).
- [ADR 0070](../../../engine/adr/0070-project-wired-review-skill.md) — contract.
