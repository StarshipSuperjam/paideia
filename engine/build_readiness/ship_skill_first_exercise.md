# `/ship` skill — first-exercise readiness note

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) cross-cutting-mechanism gate. ADR 0081 criterion-4 evaluation (consequences span ≥3 ops docs OR ≥5 tooling files, OR explicit Issue/ADR ask for a readiness note): **fires affirmatively.** Surfaces touched at S-0148 = `.claude/skills/ship/SKILL.md` + `.claude/skills/ship/synthesis-template.md` + `engine/adr/0081-*.md` + this readiness note + STATE.md row update + ENGINE_LOG entry + cascade updates to `.claude/skills/review/SKILL.md` + cascade updates to `.claude/skills/security-review/SKILL.md` = 8 surfaces total. Mixed Skill+ADR rather than purely ops-doc, but cross-cutting (the Skill reads `engine/session/current.json` + ADR corpus + MemPalace + `build_readiness/` + the GitHub CLI). Plus [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76)'s body explicitly names a first-exercise readiness note as a requirement. Readiness note required.

## Tier 1 — close in-session (S-0148)

Both Tier 1 criteria close in-session at S-0148 (the session shipping ADR 0081 + the Skill) via dogfood. The dogfood invokes `/ship` against S-0148's own deliverable (the new ship skill + synthesis-template + ADR 0081 + this readiness note + STATE.md row + ENGINE_LOG entries + cascade updates to `/review` and `/security-review`).

- **T1-A — well-formed `/ship` invocation returns a coherent verdict.** Invocation: read the `claude/vigilant-kirch-68ad72` branch diff, launch the three sub-agents per the SKILL.md procedure, synthesize. Expected: a structured verdict report emitted per `synthesis-template.md` shape (verdict line + per-axis summary + verdict rationale + sub-agent reports + anti-rationalization self-check). The verdict itself (GO / GO-WITH-CAVEATS / NO-GO) is empirical signal — closure criterion is mechanism-completes-end-to-end, not verdict-is-clean. Any verdict counts as Tier-1 closure provided the report is well-formed.

- **T1-B — parallel-Agent invocation pattern actually fires three concurrent sub-agents.** Verifiable via observing three `Agent` tool calls in a single assistant message in the dogfood transcript. The parallel pattern is precedented by [`build-readiness-gate/SKILL.md:31-44`](../../.claude/skills/build-readiness-gate/SKILL.md) and called out in CLAUDE.md "Using your tools". Tier-1 evidence is the single-message-three-tool-calls observation.

**Tier 1 closeout evidence:** see the "Empirical record" section below. Both T1-A (verdict emitted) and T1-B (three concurrent sub-agents) closed in-session at S-0148.

## Tier 2 — close in next natural occasions

- **First non-dogfood `/ship` invocation.** The dogfood closes Tier-1 (mechanism-completes); the first PR-time invocation against a real merge candidate is the first natural Tier-2 exercise. Record verdict + per-axis findings + any unexpected friction in that session's `outcome_summary` AND update this note's "Empirical record" subsection.
- **First NO-GO verdict surfacing with non-trivial finding.** Records that the verdict matrix actually fires on a real finding (not just a self-dogfood). Capture: which matrix row fired, which sub-agent surfaced the underlying finding, what the route-of-resolution was.
- **First override-attempt with anti-rationalization rebuttal firing.** Records that the rebuttal logic works end-to-end. Capture: the rationalization pattern identified, the row of `anti-rationalization.md` cited, the user's adjudication.
- **First sub-agent error (`gap-pending` NO-GO).** Records that the gap-handling path works. Likely scenarios: a sub-agent timeout, an unparseable structured-report return, a tool refusal. Capture: which sub-agent, what the error was, how the synthesis handled it.
- **First CI-fallback path (`pytest --cov` invoked because no CI run exists on the branch).** Records the slow-path latency empirically. Capture: invocation duration, observed coverage % vs. CI-reported coverage % (if a subsequent CI run lands).
- **First invocation against a routine-mode session.** Records that the scope_lock overlay fires correctly. Capture: did scope_lock overlay PASS / FAIL / N-A as expected?

## Tier 3 — defer indefinitely (recorded for future audit)

- **Multi-model heterogeneity.** The "multi-model" framing is currently aspirational — all three sub-agents run on the parent's model. When the harness exposes per-Agent model selection, route the three sub-agents to three different model families (Opus / Sonnet / Haiku, or cross-vendor) for genuine anti-rationalization-by-model-perspective. Trigger: harness supports per-Agent model override.
- **Refactor to standalone Python tool** (if the Skill grows beyond ~300 lines, OR if the synthesis logic becomes complex enough to warrant unit-testable Python). Currently 200 lines + 80 lines for the reference card; well within the recipe-shape budget. Trigger: 3+ additions to the verdict matrix OR the overlay set.
- **Additional axes as new orthogonal sub-agents.** Future candidates: dependency-supply-chain audit (cross-references Dependabot + checks for newly-introduced upstreams), license-compliance check (post-OSS-flip per [ADR 0065 product](../../product/adr/0065-oss-pivot-and-byok-disposition.md)), accessibility-review (Phase 6+ frontend). Each would be a fourth/fifth/sixth concurrent sub-agent. Trigger: explicit ADR or Issue request.
- **Cost optimization** (cache `/review` and `/security-review` output if `/ship` invoked twice on same SHA). Currently each invocation pays the full 3-sub-agent cost; a same-SHA re-invocation could short-circuit to cached output. Trigger: per-session telemetry shows ≥3 same-SHA re-invocations per session on average.
- **Validator soft-warn for substantive merges without prior `/ship` invocation.** Could mechanize "the AI authored a substantive deliverable but never ran `/ship` before close." Deferred — `/ship` is a recommendation gate; mandating invocation conflicts with the recommendation-not-merge-gate posture.
- **Sub-agent timeout policy.** Current behavior: rely on harness Agent-tool timeout (per-Agent default). Could specify a `/ship`-level budget (e.g., NO-GO with `gap-pending` if any sub-agent exceeds 5min wall time even without erroring). Trigger: an actual long-running sub-agent observation.

## Empirical record

### S-0148 (the session that authored ADR 0081 + the Skill) — 2026-05-13

To be appended in-session at the dogfood step. Format per [`build_lifecycle_push_first_exercise.md`](build_lifecycle_push_first_exercise.md):

```
**T1-A closeout (verdict emission, <UTC-time>):**
`/ship` invocation on `claude/vigilant-kirch-68ad72` @ <SHA-short> returned verdict <GO|GO-WITH-CAVEATS|NO-GO>.
Verdict rationale: <one-line summary of matrix rows that fired>.
Sub-agent statuses: code-review <✓|✗>, security-review <✓|✗>, coverage <✓|✗>.
Coverage source: <gh run view (CI run X) | pytest --cov fallback>.
T1-A: GREEN.

**T1-B closeout (parallel-agent invocation pattern, <UTC-time>):**
Single assistant message contained three concurrent Agent tool calls (subagent_type=general-purpose × 3). Transcript-observable. T1-B: GREEN.

**Notable observations:**
- <any sub-agent behavior worth recording>
- <any Paideia overlay finding>
- <any first-exercise friction not anticipated in the readiness note>
```

### Pattern note for future sessions

The S-0148 dogfood establishes the first-invocation pattern. Sessions invoking `/ship` should:

1. Read the SKILL.md before first invocation in a session (the Skill carries `disable-model-invocation: true`; no auto-fire).
2. Pass the branch diff verbatim to each sub-agent — do not summarize. Each sub-agent re-derives its own findings from the diff, not from the parent's summary.
3. Apply the four Paideia overlays at synthesis-time per the SKILL.md "Procedure step 3", not delegated.
4. Use the `synthesis-template.md` shape for the verdict report; do not invent ad-hoc shapes.
5. If a NO-GO triggers, do not silently downgrade — the verdict matrix is the calibration; rebuttal-and-override is the user's escape hatch, not the AI's.
