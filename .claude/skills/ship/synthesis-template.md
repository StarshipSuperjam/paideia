# `/ship` synthesis output template

> Reference card per [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md). Consulted at step 5 of [`SKILL.md`](SKILL.md). The structured Markdown shape below is what `/ship` emits as its verdict report.

## Output shape

```markdown
## `/ship` — <branch-name> @ <SHA-short> — VERDICT: <GO|GO-WITH-CAVEATS|NO-GO>

**Change size:** N lines (M files). **Coverage:** P% (floor: 78%, baseline: 80%; Δ: ±X.Xpp).
**Coverage source:** `gh run view` (CI run <run-id>) | `pytest --cov` fallback (slow path, ~3.5min).
**Sub-agents:** code-review ✓ | security-review ✓ | coverage ✓ (or × with error reason).

### Verdict rationale

<One-or-two-sentence summary of which matrix rows fired and why.>

For NO-GO, name every triggering row. For GO-WITH-CAVEATS, name the Required findings and overlay status. For GO, state which overlays were N-A vs. PASS.

### Per-axis summary

| Axis | Verdict | One-line |
|---|---|---|
| Correctness | PASS / FAIL | <one-line from /review> |
| Readability | PASS / FAIL | <one-line from /review> |
| Architecture | PASS / FAIL | <one-line from /review> |
| Security | PASS / FAIL | <one-line from /security-review aggregate> |
| Performance | PASS / FAIL | <one-line from /review> |
| Coverage | PASS / FAIL | P% vs. 78% floor (Δ ±X.Xpp vs. 80% baseline) |
| Scope-lock | PASS / N-A | <one-line; N-A for build-mode> |
| ADR-citation | PASS / FAIL / N-A | <one-line; N-A if no contract surface touched> |
| engine_memory decisions-room drawer | PASS / Required / N-A | <one-line; N-A if no new ADR> |
| First-exercise readiness | PASS / FAIL / N-A | <one-line; N-A if no new cross-cutting mechanism> |

### Required actions

> Present only on NO-GO and GO-WITH-CAVEATS verdicts.

- **<Severity>** <Axis>: <one-line finding> — <action>
- ...

Order: NO-GO blockers first, then Required findings, then Required-tier overlay gaps.

### Sub-agent reports

#### `/review` report

<Verbatim report from sub-agent 1 — the full `/review` structured Markdown including its own Findings table, Paideia overlay checks, and Anti-rationalization self-check.>

#### `/security-review` report

<Verbatim report from sub-agent 2 — the full `/security-review` structured Markdown including OWASP Top 10 grid, Paideia overlay grid, Findings table, Defense-in-depth cross-check, and Anti-rationalization self-check.>

#### Coverage report

<Verbatim report from sub-agent 3 — overall coverage %, delta vs. baseline, per-file movement on diff-modified files, PASS/FAIL vs. floor, source path (`gh run view` or `pytest --cov`).>

### Anti-rationalization self-check

Reviewed against [`../review/anti-rationalization.md`](../review/anti-rationalization.md): no rationalizations applied at synthesis time.

### Override audit (only present if user overrode NO-GO)

- **Override reason given:** <verbatim from user>
- **Rationalization pattern identified:** <row of anti-rationalization.md cited>
- **Rebuttal delivered:** <one-line summary>
- **User decision:** proceeded / accepted finding / amended scope.
- **Routing of finding:** Issue #<num> filed / fixed in-session / explicitly deferred.
```

## Calibration notes for verdict authors

- **N-A is a real verdict, not a cop-out.** Pre-Phase-6 the Authentication and Headers OWASP items are usually N-A; the scope_lock overlay is N-A on build-mode sessions. Mark them N-A explicitly rather than inflating to PASS.
- **GO-WITH-CAVEATS is not "ship despite findings".** The Required findings list is mandatory action — author addresses before merge. The verdict is "the change is sound but two specific things must be fixed."
- **NO-GO is not "ship is forbidden".** The user can override; the anti-rationalization rebuttal makes the override visible. The verdict is "we strongly recommend not merging in this shape."
- **Empty sub-agent reports are a gap, not a clean-go.** If `/review` returns "no findings" with no structured report, treat as `SUB-AGENT GAP` and NO-GO. Honest clean-goes include a structured report with empty Findings tables.
- **Coverage Δ is informational, not gating.** The gate is the absolute floor (78%); a drop from 90% to 85% is GO if both remain above floor (the report still surfaces the delta).

## See also

- [`SKILL.md`](SKILL.md) — the procedure that emits this report shape.
- [ADR 0081](../../../engine/adr/0081-ship-multi-model-orchestration-skill.md) — the citable contract.
- [`../review/SKILL.md`](../review/SKILL.md) §"Output shape" — analogous report shape for `/review` alone.
- [`../security-review/SKILL.md`](../security-review/SKILL.md) §"Output shape" — analogous report shape for `/security-review` alone.
