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

**T1-A closeout (verdict emission, 2026-05-13T19:xxZ):**
`/ship` invocation on `claude/vigilant-kirch-68ad72` @ `3eee12c` returned verdict **NO-GO** with 3 `Required` findings from the `/review` sub-agent (cluster-signal matrix row fired). Sub-agent statuses: code-review ✓ (14 findings: 3 Required + 4 Nit + 4 Optional + 4 FYI), security-review ✓ (0 Critical, 0 Required, 2 FYI; OWASP grid all PASS or N-A; Paideia overlays all N-A — diff is Markdown-only), coverage ✓ (79.88% overall, +1.88pp over 78% floor, −0.12pp vs 80% S-0136 baseline; 1361 tests passing). Coverage source: `pytest --cov` fallback (no CI run on branch — direct-to-main via build_lifecycle_push.py per ADR 0076). Wall time ≈3:50min for coverage; sub-agents 1 + 2 ≈2min in parallel. **T1-A: GREEN** — mechanism completed end-to-end; verdict report well-formed per `synthesis-template.md`.

**T1-B closeout (parallel-agent invocation pattern, 2026-05-13T19:xxZ):**
Single assistant message contained three concurrent `Agent` tool calls (`subagent_type: general-purpose` × 3). Transcript-observable in S-0148 session. All three sub-agents executed concurrently per CLAUDE.md "Using your tools" guidance + `build-readiness-gate/SKILL.md:31-44` precedent. **T1-B: GREEN.**

**3 Required findings + fix disposition:**
1. **ADR 0041 wrong filename** in ADR 0081 + ENGINE_LOG.md + STATE.md (`0041-cascade-discipline-three-validator-checks-plus-manual-procedures.md` vs canonical `0041-cascade-analysis-discipline.md`). Fixed in-session per `feedback_no_session_cascade.md`; all three files corrected.
2. **`Agent` tool name + dispatch verification.** Sub-agent surfaced the concern from its (correctly scoped) restricted view. The dogfood itself empirically validated the dispatch — three Agent calls executed concurrently. Fixed in-session by adding a one-line clarification to SKILL.md naming `Agent` as the dispatch primitive + a back-reference to this readiness note's empirical record.
3. **Skill-self-exclusion ambiguity** ("ADR-only edits with no code touch" exclusion vs "modified Skills" inclusion). Real ambiguity on Skill+ADR landings (the S-0148 shape). Fixed in-session: tightened the exclusion to "ADR-only edits with no other artifact touch" + added explicit "Inclusion-list precedence rule" naming the S-0148 shape as the exemplar.

**Notable observations:**
- **Tier-1 closure under NO-GO**, per the user-approved plan ("Record any verdict as Tier-1 closure" — the closure criterion is mechanism-completes-end-to-end, not verdict-is-clean). The 3 Required findings being real and fixable in-session is empirical value the dogfood delivered — would have shipped uncorrected without it.
- **`/security-review` correctly applied N-A discipline** across the OWASP grid for a Markdown-only diff. Demonstrated honest calibration (resisted the "mark everything PASS to look thorough" failure mode named in its anti-rationalization self-check).
- **Coverage sub-agent confirmed ADR 0081 decision 2's expectation empirically.** Documentation-only diff has mechanically-zero coverage exposure; the 79.88% vs 80% baseline drift is measurement variance below noise threshold.
- **First-exercise friction not anticipated:** the parent-side overlays (step 3) require reading `engine/session/current.json` explicitly. Surfaced by sub-agent 1 as an Optional finding; addressed by the existing step-1 ("Load context") which already names this read but described it as conditional ("if mid-session"). Tightening to unconditional read is queued as a Tier-2 follow-up (`/ship` is always mid-session by construction).
- **Synthesis-template.md borderline-redundant** per sub-agent 1's Nit finding. Deferred: the template inlining decision is a future authoring-call (could collapse OR enrich with worked examples). Recorded as a Tier-3 forward-pointer.
- **Cluster-signal matrix condition needs sharpening** per sub-agent 1's Optional finding 8: the current "≥3 Required findings (cluster signal across reviewers)" wording counts intra-sub-agent clusters too. The dogfood empirically hit this exact case (all 3 Required from one sub-agent). Filed as a Tier-2 forward-pointer for the next NO-GO surface session.
- **Fast-path `gh run view` command tightening** per sub-agent 1's Optional finding 9 (filter by `--workflow validate.yml`). Filed as Tier-2 forward-pointer.

**Follow-on deliverable commit** at S-0148 close authored the 3 Required fixes + this empirical record + the readiness-note updates. The wrapper's catchup-aware deliverable mode (per ADR 0076 Amendment v3) pushed the eager-claim + main deliverable + follow-on deliverable together as a coherent close.

### Pattern note for future sessions

The S-0148 dogfood establishes the first-invocation pattern. Sessions invoking `/ship` should:

1. Read the SKILL.md before first invocation in a session (the Skill carries `disable-model-invocation: true`; no auto-fire).
2. Pass the branch diff verbatim to each sub-agent — do not summarize. Each sub-agent re-derives its own findings from the diff, not from the parent's summary.
3. Apply the four Paideia overlays at synthesis-time per the SKILL.md "Procedure step 3", not delegated.
4. Use the `synthesis-template.md` shape for the verdict report; do not invent ad-hoc shapes.
5. If a NO-GO triggers, do not silently downgrade — the verdict matrix is the calibration; rebuttal-and-override is the user's escape hatch, not the AI's.
