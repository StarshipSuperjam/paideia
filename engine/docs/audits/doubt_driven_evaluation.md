# Doubt-driven-development evaluation audit

- **Date:** 2026-05-13
- **Session:** S-0151
- **Issue:** [#77](https://github.com/StarshipSuperjam/paideia/issues/77)
- **Outcome ADR:** [ADR 0084](../../adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md)

## Purpose

Evaluate whether the `doubt-driven-development` workflow (CLAIM → EXTRACT → DOUBT → RECONCILE) from `addyosmani/agent-skills` adds value over Paideia's existing posture (the standing pushback rule in [CLAUDE.md](../../../CLAUDE.md), the project-wired [/review](../../../.claude/skills/review/SKILL.md) skill, ADR-authoring discipline per [ADR 0077](../../adr/0077-adr-template-alternatives-considered-section.md)). Settles by becoming one of: a new `.claude/skills/doubt-driven/SKILL.md`, a CLAUDE.md pushback-rule amendment, or a wontfix close.

## Workflow definition (for reference)

1. **CLAIM** — state the decision in one sentence.
2. **EXTRACT** — list every load-bearing assumption the decision depends on.
3. **DOUBT** — for each assumption, name one concrete scenario where it could be wrong.
4. **RECONCILE** — either (a) revise the claim, (b) revise the assumption, or (c) accept the claim with named risks.

## Corpus skim

The 30 ADRs landed S-0042 → S-0150 (engine + product partitions, 2026-05-04 through 2026-05-13) were skimmed for:

- Supersession relationships (replacing a load-bearing decision).
- Consequences sections amended post-landing in the same or adjacent session (signal of in-flight reconciliation work).
- Decisions whose rejected alternatives later became load-bearing (signal of an unsurfaced premise).
- Multi-surface cross-cutting mechanisms per [ADR 0053](../../adr/0053-mechanism-first-exercise-gate.md) trigger criterion #4.

High-signal candidates surfaced from the skim:

| ADR | Session | Signal |
|---|---|---|
| 0049 | S-0042 | `scope_lock` at boot; multi-session downstream; issue body's explicit suggestion |
| 0054 | S-0060 | Lifecycle-push wrapping; explicit "interactive doesn't trigger the gate" premise later falsified at S-0137 → ADR 0076 |
| 0063 | S-0126 | Validator tiered targets; structural-phase composition assumption falsified within ONE session of landing (S-0127 re-fold added health_probe phase) |
| 0076 | S-0138 | Build-mode lifecycle-push wrappers; directly closed the falsified premise from ADR 0054 |
| 0042 | S-0033 | Soft-warn lifecycle archive canon; fundamental contract; many downstream consumers (not picked — pattern would replicate 0049's findings) |
| 0067 | S-0132 | Gitleaks pre-commit; standard pattern; low signal (not picked) |
| 0079 | S-0145 | HNSW threshold tuning; mechanical decision (not picked) |

**Three historical picks for full workflow application** (plus the in-session upcoming decision):

- **Historical #1: ADR 0049** (scope-lock at boot + descope-reorder audit + defer-handle). Issue body's explicit suggestion.
- **Historical #2: ADR 0054** (lifecycle-push wrapping). Contains an empirically-falsified "Out of scope" premise that triggered ADR 0076 mid-flight at S-0138.
- **Historical #3: ADR 0063** (validator tiered runtime targets). Contains a structural-phase composition assumption falsified within one session (S-0127 in-session re-fold).
- **In-session upcoming: Phase A1's path proposal** for [Issue #116](https://github.com/StarshipSuperjam/paideia/issues/116) (cache the non-ADR md-file reads in `validate_adr_back_reference_orphan`).

## Workflow application 1 — ADR 0049 (scope-lock at boot)

### CLAIM

Mechanize scope discipline by declaring `declared_scope` at boot, auditing `scope_delivery` at shutdown, and capturing `next_session_handle` to anchor a positive defer contract — five rules total, each non-blocking soft-warns visible to the AI through the lifecycle.

### EXTRACT

1. Every session has a declarable scope at boot time (either build-plan phase or operational prose).
2. The `phase:` token matched against `build_plan/MANIFEST.md` catches the S-0037 reordering vector specifically.
3. Asking the AI an explicit question at shutdown (`"Did you deliver the declared scope?"`) produces honest, audit-quality answers.
4. A 3-of-5 multi-session surface threshold is the right cadence for surfacing scope erosion.
5. The hedge-pattern regex set (`future session`, `next session will`, etc.) sufficiently covers indefinite-defer phrasing.
6. Forcing a `next_session_handle` value (`#NN`, `S-NNNN`, or `null`) anchors a positive contract — false positives become "you forgot to declare" rather than "your prose tripped a regex."

### DOUBT

1. **A session may have no declarable scope at boot.** A purely exploratory build session converted from default mode mid-conversation has no pre-declared scope. *Concrete scenario:* user starts a conversation talking through Phase 6 design, decides 30 minutes in to run `/start-engine` and capture some ADRs from the discussion. The scope is "whatever crystallized in the chat" — not declarable as a 1-3 sentence prose item upfront.
2. **The `phase:` token check is substring-match.** *Concrete scenario:* a session declares `phase: 4.5` while build-plan is at `phase: 4_5` (underscore vs dot). False negative on the typo.
3. **The shutdown prompt may produce performative-positive answers.** LLM training rewards agreement-style responses. *Concrete scenario:* a session that descoped silently mid-work answers `delivered: true` because the partial work matches a re-interpreted scope statement after the fact.
4. **3-of-5 may be too lenient OR too strict.** *Concrete scenario:* a string of 4 audit-style sessions (low-deliverable by nature) followed by 1 substantive session falsely fires the threshold. Or: a single session that descoped 10 separate things in one session fires nothing.
5. **Hedge regex coverage is bounded.** *Concrete scenario:* "we'll circle back" or "TODO for later" or "marked for revisit" — neither in the regex set; the unhandled defer slips.
6. **Anchoring `next_session_handle` as positive contract assumes the AI fills it accurately.** *Concrete scenario:* an AI fills `next_session_handle: "S-0152"` when the work was deferred to a different session ID, or to an unknown future session — the validator can't verify intent, only existence.

### RECONCILE

- Premise 1 — **accept with named risk**. The ADR text does say "operational/engine-apparatus work that doesn't map to a build-plan phase, the prose has no `phase:` token and is unrestricted" — exploratory-to-build conversions get unrestricted prose. Risk surfaced but tolerated; the cost of forcing a phase token is higher than the benefit.
- Premise 2 — **revise**: would have justified a normalization step (token canonicalization: replace `_` with `.`, lowercase). Not present in the original ADR. Cost so far: zero (no observed false-negative in field). Could add cheaply if it surfaces.
- Premise 3 — **revise**: doubt-driven extraction at shutdown is a known LLM failure mode. The mitigation (per the ADR Consequences: "raise the cost" rather than "prevent") is acknowledged. Stronger mitigation would be a second-look pass (e.g., have a sub-agent grep the session's commits and answer the same question independently). Cost-of-fix high; defer.
- Premise 4 — **accept**. Inherits the soft-warn lifecycle canon per ADR 0042; the 3-of-5 threshold has held in practice.
- Premise 5 — **revise**: candidate to extend regex over time. Open Issue-able if a slipped hedge phrase becomes painful.
- Premise 6 — **accept with named risk**. The validator verifies `#<num>` exists and `S-NNNN` exists; intent is unverifiable.

**Net assessment of ADR 0049 retrospect.** The ADR's design rationale already implicitly addressed several of these via "raise the cost" framing rather than "prevent." Doubt-driven extraction would have surfaced premise 2 (token canonicalization, fixable cheaply) and premise 5 (regex coverage extensibility) at author-time. **Modest gain on a well-considered ADR.**

## Workflow application 2 — ADR 0054 (lifecycle-push wrapping)

### CLAIM

All routine-mode pushes to `origin/main` route through `engine/tools/routine_lifecycle_push.py` (three modes: `eager-claim`, `deliverable`, `close`), each shape-verifying HEAD before pushing via subprocess to bypass the harness "Default Branch Push" gate.

### EXTRACT

1. The harness gate is a hardcoded client-side heuristic on Bash command surface, NOT on subprocess-spawned git operations from a permitted python script.
2. **Interactive `/start-engine` sessions don't trigger the gate** (user-presence heuristic). *(This is the explicit "Out of scope" claim at ADR 0054 line 137.)*
3. Phase 0 empirical probe (commit `8df1c38`) verifies the bypass hypothesis from interactive context.
4. The subprocess-bypass pattern from `routine_boot_freshness.py` / `routine_eager_claim_recovery.py` generalizes to the push step.
5. Per-mode shape verification refuses malformed commits; on refusal, no destructive recovery happens.
6. Failure-mode discrimination via exit codes (0/2/3/4/5) lets the caller act differently per failure cause.

### DOUBT

1. Premise 1 — **what's the evidence the gate is fixed-shape on Bash surface only?** The S-0060 plan says agent-driven Claude Code documentation review confirmed this. *Concrete scenario:* a future Claude Code update adds subprocess-level hooks (low-probability but unverified). Mitigation already named in Cost section.
2. Premise 2 — **THIS IS THE LOAD-BEARING UNVERIFIED PREMISE.** What's the evidence interactive sessions don't trigger the gate? *Concrete scenario:* a user-presence heuristic that depends on harness state may fire OR not fire depending on subtle context (recent typing? session age? recently approved push?). The Phase 0 baseline run (line 23 of the ADR) says interactive succeeded without prompting — but that's ONE run, not a categorical exclusion. **The premise was empirically falsified at S-0137 (interactive build session push triggered the gate) and motivated ADR 0076's emergency `build_lifecycle_push.py` work.**
3. Premise 3 — **the probe ran once.** *Concrete scenario:* concurrent harness state at probe time matched the harness state of all future runs. Verified by the same one-shot probe. The variance was not tested.
4. Premise 4 — **subprocess-bypass pattern generalization assumes the harness inspects only the leading Bash command.** *Concrete scenario:* the harness may inspect inside multi-command Bash invocations (`cmd1; cmd2`). Per S-0046's gate-inspection lesson, this is exactly how it does work.
5. Premise 5 — **shape verification refusal-without-mutation**. *Concrete scenario:* an interrupted refusal mid-execution (signal, OS kill) could leave intermediate state. Edge case; not load-bearing.
6. Premise 6 — **accept**. Exit-code conventions are mechanical; well-tested.

### RECONCILE

- Premise 2 — **REVISE: the assumption should have been tested under routine-mode load AND interactive-mode load before being recorded as "Out of scope."** If extraction had named premise 2 and DOUBT had named the scenario "a future interactive session triggers the gate despite this assumption," the cheap empirical test would have been: have a third-party human user manually run `/start-engine` against `origin/main` and see whether the gate fires. The test was instead deferred to "interactive sessions don't trigger the gate (user-presence heuristic)" as an asserted fact — and the assertion was falsified at S-0137. Cost of the falsification: ADR 0076 (~300 lines), `build_lifecycle_push.py` + tests (~400 lines), one in-session emergency at S-0138.
- All other premises — accept or already mitigated.

**Net assessment of ADR 0054 retrospect.** **Doubt-driven extraction would have surfaced the load-bearing unverified premise (premise 2) at author-time with high confidence.** The cost of an empirical test at that point (one user re-running `/start-engine` against `origin/main` to see if the gate fires) was tiny relative to the downstream cost of the falsification. **High-value historical case for doubt-driven discipline.**

## Workflow application 3 — ADR 0063 (validator tiered runtime targets)

### CLAIM

Mechanize three coupled changes at S-0126: (1) tiered runtime targets — structural <500ms, health-probe <5s, graph-audit <5s, total <11s — replace the prior unitary `<500ms` target; (2) per-phase timing instrumentation in `validate.py main()`; (3) per-phase regression soft-warn fires when any phase exceeds 1.5× target across 3 consecutive runs.

### EXTRACT

1. The four functions invoked from `main()`'s structural-phase block are categorically "structural" — in-memory file/regex checks, no DB or subprocess.
2. The `<500ms` target is appropriate for the structural phase as it stands at S-0126.
3. 1.5× breach across 3 consecutive runs is the right sensitivity tier for the regression soft-warn.
4. New phases added to `VALIDATOR_PHASE_TARGETS_MS` automatically extend the regression check via dict-key iteration.
5. Per-phase fields are emitted only by the default-mode pipeline; gate-flag modes that don't run the full pipeline are excluded.
6. The audit (S-0121 Retire-D recommendation) is the correct trigger for retiring the unitary target.

### DOUBT

1. Premise 1 — **THIS IS THE LOAD-BEARING UNVERIFIED PREMISE.** What's the evidence each function is "in-memory file/regex"? *Concrete scenario:* `validate_shared_state_health` calls `probe_palace.py` (chromadb subprocess + ONNX/CoreML embedder load); `validate_issue_collisions` shells out to `gh issue list`. Both are subprocess-launching, both have intrinsic cost orders of magnitude higher than file/regex. **The premise was falsified by the FIRST natural fire of the regression check at S-0126 close (median ~3700ms structural, dominated by the chromadb open).** Cost: in-session re-fold at S-0127 adding the health-probe phase — one session of focused work.
2. Premise 2 — accept conditionally. Target is appropriate for the *cleaned* structural phase (post-S-0127 fold), not the original.
3. Premise 3 — **1.5× / 3-run threshold has been only empirically calibrated via the S-0126 first-fire and now the S-0146 second-fire.** *Concrete scenario:* corpus growth produces gradual drift below threshold that the rolling-3 window never catches. Acknowledged in the ADR Consequences ("If exercise produces false-positives, ... adjustment").
4. Premise 4 — accept; verified by S-0127's clean extension to four phases.
5. Premise 5 — accept; correctly scoped.
6. Premise 6 — accept; audit-driven contract changes are the recommended trigger per ADR 0057.

### RECONCILE

- Premise 1 — **REVISE: should have been tested at author-time.** Extraction would have named "each function is in-memory file/regex" as a load-bearing premise; DOUBT would have asked "what makes each function structural?"; the cheap empirical test would have been: time each function once during the ADR-authoring session. That single test would have surfaced the ~3500ms `validate_shared_state_health` contribution and motivated the four-phase model BEFORE the structural-target landed. Cost of the falsification: S-0127's in-session work (~half a session, by the Consequences narrative — moving two functions, adding the phase boundary, updating tests, fold-amending the ADR).

**Net assessment of ADR 0063 retrospect.** **Doubt-driven extraction would have surfaced the structural-phase composition premise at author-time.** Same pattern as ADR 0054 — a confident assertion about a contingent fact, falsifiable by a cheap empirical test, not run. **High-value historical case for doubt-driven discipline.**

## Workflow application 4 — Phase A1 in-session upcoming decision

### CLAIM

Tune `validate_adr_back_reference_orphan` by caching each non-ADR md-file read once across all ADRs (Path A from the S-0151 Phase A1 deliberation), expected to drop the function's runtime from ~376ms (63% of structural phase) to ~40-80ms and bring the structural phase well under the 500ms target without changing the contract.

### EXTRACT

1. The dominant cost is O(N_adr × N_md) file opens — reads each non-ADR .md file once per Accepted/Deprecated ADR.
2. The cache memory cost is acceptable (~300 md files × ~5KB = ~1.5MB).
3. Cached file contents are stable for the duration of the run (single-process, no concurrent writers).
4. The change is semantic-preserving (same files inspected, same regex applied, same soft-warn output).
5. Tuning the hot check is preferred over bumping the target (Path A vs Path C) because the dominant cost is in ONE function, not spread across the corpus.
6. The optimization is independent of other structural-phase work — no cross-function coupling.

### DOUBT

1. Premise 1 — accept. Profile data verifies: 376ms median (n=5), 63% of structural phase, with all other ADR scanners <12ms.
2. Premise 2 — accept. ~1.5MB is well within process memory bounds.
3. Premise 3 — **what about scenarios where md files are written DURING a validate.py run?** *Concrete scenario:* a pre-commit hook runs validate.py and a concurrent editor saves an md file mid-run. Result: the cached content is stale relative to the on-disk version. *Mitigation:* the function is read-only and short-lived; pre-commit blocks file edits during its own run via git's index lock; the cache exists only for the function's duration (not process-lifetime). Risk acceptable.
4. Premise 4 — **what about reading from a different path?** *Concrete scenario:* if the cache key is the Path object and two ADRs reference the same file via different relative paths, the cache misses. *Mitigation:* use `Path.resolve()` or store the absolute Path consistently.
5. Premise 5 — **is the assumption that the cost is in ONE function justified by the profile?** *Concrete scenario:* the profile (n=5) may understate variance; a future corpus growth could push another function into the hot zone. *Mitigation:* the regression check fires when ANY phase exceeds 1.5× target — gives next-step signal for further tuning when needed. No need to over-engineer now.
6. Premise 6 — **could the optimization break a contract?** *Concrete scenario:* a future check authored against `validate_adr_back_reference_orphan` assumes file-reads are fresh per call. *Mitigation:* the function is internal; the cache is internal to the function body; no external contract change.

### RECONCILE

- Premise 1 — accept.
- Premise 2 — accept.
- Premise 3 — accept with named risk (mitigated by short-lived cache scope).
- Premise 4 — **revise the implementation**: ensure cache key uses a consistent Path normalization (use the same Path object the caller already constructs from `_tracked_md_files`; if needed, store as resolved absolute Path).
- Premise 5 — accept; the regression check is the future-tuning signal.
- Premise 6 — accept; the change is internal-only.

**Net assessment.** The Path A proposal survives the doubt pass. One refinement (premise 4: Path normalization) added to the implementation note. **No change to the path leaning.**

**Counterfactual.** If the doubt pass had surfaced a substantive concern (e.g., the cache hides per-call regressions in a way that masks future bugs), the path would have been revised. The discipline value is in the EXTRACTION step — making premises explicit forces verification of each.

## Distinguishing doubt-driven from `/review`

- **`/review`** runs against staged changes (post-authoring). It walks five axes (correctness / reusability / scope / quality / overlay-skill compliance) and an anti-rationalization rebuttal table. Optimized for catching bugs and scope creep in already-written code.
- **Doubt-driven** runs against the *decision shape itself* (pre-authoring). It walks four steps (claim / extract / doubt / reconcile) and forces empirical testing of unverified premises. Optimized for catching unverified load-bearing premises before authoring.

The two are sequential, not redundant. Doubt-driven applied before authoring → ADR/code authored on a verified premise base → `/review` applied to the authored code → staged changes reviewed against the verified premises. Each catches a different failure mode.

## Outcome decision

### Three candidate outcomes

**Option 1 — new skill `.claude/skills/doubt-driven/SKILL.md`**

A project-wired skill with `disable-model-invocation: true`, documented triggers (cross-cutting mechanism authoring; supersession ADR; posture-to-machinery conversion; contract-shape change). Invoked explicitly by the AI before authoring a qualifying decision.

- *Pros*: explicit invocation surface; mirrors the existing `/review` + `/security-review` + `/ship` skill pattern; gives the workflow first-class affordance.
- *Cons*: AI invocation discipline is empirically weak — even the existing `/review` and `/security-review` skills have their "Empirical record (pending)" subsections still open at S-0148. Adding another opt-in skill that the AI must remember to invoke is unlikely to produce reliable adoption. The historical failure cases (ADR 0054, ADR 0063) didn't fail for lack of a workflow — they failed because the author didn't extract the unverified premise. A skill with the same triggers doesn't change the extraction step's prominence.
- *Rejected because*: the empirical pattern across 0049/0054/0063 is that the *extraction step* is what's missing, not the workflow vocabulary. A new skill adds vocabulary; what's needed is integration into the pushback-rule the AI already reads.

**Option 2 — CLAUDE.md pushback-rule extension** *(Recommended)*

Extend the pushback-rule section in CLAUDE.md with a sub-rule: for decision classes (cross-cutting mechanism; supersession; posture-to-machinery conversion; contract-shape change), the AI runs an explicit **extraction step** before authoring the Decision section — list load-bearing premises as bullets, name what would falsify each, run a cheap empirical test if available. The four-step workflow (CLAIM → EXTRACT → DOUBT → RECONCILE) is the procedure; pushback-rule is the trigger.

- *Pros*: integrates with the rule the AI already reads at every session start. Reuses the existing standing pushback rule's authority (memory + CLAUDE.md). Extraction step is the surgical missing piece per this audit's findings — making it the load-bearing addition rather than wrapping it in a separate skill body. The trigger classes are the ones the audit identified as historically vulnerable.
- *Cons*: posture-not-machinery — there is no mechanical enforcement, only AI discipline. Drift risk is real; if a session forgets to run extraction on a qualifying decision, no alarm fires. Same posture risk as the standing pushback rule itself (acknowledged in CLAUDE.md's "Posture vs machinery" section).
- *Rejected because*: not rejected — chosen.

**Option 3 — wontfix close**

The existing posture (pushback rule + `/review` + ADR 0077 Alternatives Considered + four-eyes user review) is sufficient. No new mechanism.

- *Pros*: minimal change; preserves status quo.
- *Cons*: the audit's findings explicitly contradict this — the historical pattern across 0054/0063 shows the existing posture didn't catch the "unverified load-bearing premise" class. The cost of those failures (ADR 0076 emergency session, S-0127 in-session re-fold) is concrete. Discarding a known-failed posture without any intervention forecloses the cheapest possible remediation.
- *Rejected because*: the audit produces affirmative evidence that the existing posture misses the unverified-premise class. Wontfix is the choice of "no action" against evidence of need.

### Decision

**Option 2 — CLAUDE.md pushback-rule extension.** The extraction step is the surgical addition the historical pattern names. Integration with the existing pushback rule reuses existing reading-discipline. Posture-not-machinery risk is acknowledged and shared with the rest of the pushback-rule discipline.

### Trigger classes (load-bearing)

The extraction step fires for decision classes where historical failures cluster:

- **Cross-cutting mechanism authoring** — any ADR whose Consequences would touch ≥5 surfaces per [ADR 0053](../../adr/0053-mechanism-first-exercise-gate.md) trigger #4 (this is the mechanism-first-exercise gate's threshold; reusing it keeps the rule sets aligned).
- **Supersession ADR** — replacing a load-bearing prior decision (Status changes from Accepted to Superseded; new ADR has `Supersedes: ADR-XXXX` field).
- **Posture-to-machinery conversion** — CLAUDE.md "Posture vs machinery" section gains a new entry.
- **Contract-shape change** — schema additions to load-bearing structured-archive fields (per ADR 0042); target-value adjustments to validator phase budgets (per ADR 0063); rename or repartition of ADR sequences (per ADR 0037).

### Procedure (for the CLAUDE.md addition)

At the bottom of the Context section, before authoring the Decision section, the AI authors a `### Load-bearing premises` subsection listing:

1. The premises the Decision will rest on (one bullet each).
2. For each premise: what would falsify it (one sentence).
3. For each premise that can be cheaply tested: the test and its result.

If extraction surfaces an unverified premise that can be tested in-context, the test runs before the Decision is authored. If a premise is unverifiable in-context (requires future empirical signal), it's named in the ADR Consequences as a known assumption with a fallback procedure.

### Sunset criterion

If 5 consecutive sessions complete qualifying decisions and the extraction step surfaces nothing new (i.e., the rule produces zero behavioral signal), revisit whether the extraction step has converged into implicit AI discipline and can be retired from explicit CLAUDE.md text. Track via the same soft-warn lifecycle as other postures (ADR 0042 archive canon) — though this rule itself is posture, the *outcomes* (load-bearing-premise sections in ADRs) are inspectable post-hoc.

## Cross-references

- [ADR 0084](../../adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — outcome ADR codifying Option 2.
- [CLAUDE.md](../../../CLAUDE.md) Standing rules → Pushback rule — receives the extraction-step sub-rule.
- [ADR 0049](../../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — historical workflow application #1.
- [ADR 0054](../../adr/0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) — historical workflow application #2 (load-bearing premise falsified at S-0137).
- [ADR 0063](../../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — historical workflow application #3 (structural-phase composition assumption falsified at S-0127).
- [ADR 0076](../../adr/0076-build-mode-lifecycle-push-wrapping.md) — the emergency response to ADR 0054's falsified premise; the cost.
- [ADR 0077](../../adr/0077-adr-template-alternatives-considered-section.md) — sibling discipline (Alternatives Considered as post-Decision section). The extraction step adds the *pre-Decision* surface.
- `/review` skill at [`.claude/skills/review/SKILL.md`](../../../.claude/skills/review/SKILL.md) — post-authoring counterpart.
- `feedback_pushback_rule.md` (user memory) — the user-memory rule this extends.
- [Issue #77](https://github.com/StarshipSuperjam/paideia/issues/77) — closes.
