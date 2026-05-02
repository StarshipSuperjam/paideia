# Sub-agent validation

> When to delegate to a sub-agent (Explore, Plan, general-purpose), how to brief them, and how to validate their output before acting on it.

## When to delegate

Delegate when the work would either bloat the main session's context or run as independent parallel inquiry:

- **Open-ended research across the codebase** — "How is X implemented across the project?" with uncertain scope. Use `Explore`.
- **Design-validation pass** — "Here's an approach; does anything in the codebase contradict it?". Use `Plan` (or `general-purpose` for a second opinion).
- **Independent parallel queries** — when you need three different lookups and they don't depend on each other, fan out three sub-agents in one message rather than executing serially.

Don't delegate when:

- The target file or symbol is already known. Use `Read` or `grep` directly.
- The task is conversational or judgment-heavy in ways that depend on the main session's accumulated context.
- The investigation is two grep calls deep — the overhead of briefing a sub-agent exceeds the cost of doing it inline.

## Briefing style

Sub-agents start cold. They have not seen this conversation, do not know what's been tried, do not know why the task matters. The prompt must be self-contained.

A good prompt names:

- The user's intent and why it matters.
- What's already been ruled out.
- The boundaries of acceptable investigation (don't fix bugs you spot unless asked; don't refactor; don't write code if the task is research).
- The desired output shape ("under 200 words," "a punch list," "file paths and line numbers").

A bad prompt is terse and command-style. It produces shallow generic work.

## Output validation

Treat a sub-agent's report as a research brief, not a verdict. Validate before acting:

- **Trust but verify.** The agent's summary describes what it intended to do, not necessarily what it did. If it touched files, check the diff. If it cited a file path, open it.
- **Scope check.** Did the agent stay within the briefed scope? Sub-agents sometimes over-implement when given an "investigate" prompt. Re-read its output for unrequested changes.
- **Contradicts what you know?** If the report contradicts something you've already established in the main session, the sub-agent is more likely wrong than you are — it lacks your context. Re-read its sources before adopting its conclusion.

## Parallel fan-out

When dispatching multiple sub-agents in one message, give each a distinct focus. Overlap dilutes signal. Example:

- Agent A — search for existing implementations of feature X.
- Agent B — survey related tests and what they assert.
- Agent C — check upstream dependency ADRs for constraints.

Three different lenses on the same question. Merge findings in the main session, not in a sub-agent.

## When the sub-agent should write code

Be explicit. Sub-agents will assume "research only" unless told otherwise. If you want the agent to make edits, say so and specify:

- The exact files in scope.
- Whether to commit (default: no).
- Whether to run tests (default: no).

If the change is non-trivial, do it in the main session — sub-agent edits are harder to course-correct mid-stream.

## See also

- [`escalation-criteria.md`](escalation-criteria.md) — what counts as work the AI can decide vs. work that needs the user.
- Claude Code Agent tool reference — `Agent` tool documentation in the harness.
