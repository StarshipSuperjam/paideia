# ADR 0075 — GitHub issue templates for the eight type labels

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0137

## Context

Pre-S-0137, Paideia documents eight type labels (`bug`, `enhancement`, `tech-debt`, `cleanup`, `health-check-finding`, `upstream`, `documentation`, `question`) and a required Issue body shape (Context / Symptom / Proposed approach / Affected files / Cross-references) in [`engine/operations/issue-discipline.md`](../operations/issue-discipline.md). The structure is held entirely by author discipline — no `.github/ISSUE_TEMPLATE/` exists. Web-UI authors land free-form prose; collaborators (or the user under context pressure) skip required sections; the collision-detection scanner at [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py) reads body content that may or may not carry the expected shape.

[Issue #72](https://github.com/StarshipSuperjam/paideia/issues/72) named the adoption as the last remaining Tier 2 SWE-hardening unit. With this ADR, Tier 2 closes entirely (Pairing A #66 + #70 closed at S-0132 per ADRs 0067 + 0068; #71 pytest-cov at S-0136 per ADR 0074; Pairing C #73 + #74 at S-0134 per ADRs 0070 + 0071; #75 at S-0135 per ADRs 0072 + 0073).

`.github/` precedent: [`PULL_REQUEST_TEMPLATE.md`](../../.github/PULL_REQUEST_TEMPLATE.md) per [ADR 0066](0066-pr-template-and-branch-protection.md) (S-0131); [`dependabot.yml`](../../.github/dependabot.yml) per [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) (S-0133); [`workflows/validate.yml`](../../.github/workflows/validate.yml) per [ADR 0083 engine](0083-validate-py-mirror-to-ci.md) (S-0131) — the existing surface is comfortable territory for adding mechanical defaults.

Pattern source: standard GitHub issue forms (`.yml` config files under `.github/ISSUE_TEMPLATE/`). No project-external authoring pattern is adapted here; the GitHub spec is the spec.

## Decision

Six coupled choices mechanize the adoption.

### 1. YAML issue forms over Markdown templates

GitHub supports two template flavors: `.md` (template body pre-fills the Markdown editor; no required-field UI) and `.yml` (structured form with required-field UI, dropdowns, inputs, textareas). Issue #72's verification criterion *"submitting incomplete form blocked"* is only achievable with YAML forms. Markdown templates would let an author submit a wholly-empty body, defeating the mechanization. YAML forms chosen.

Cost: YAML schema constrains presentation more rigidly than Markdown (no inline links inside field labels; markdown-block intros are the only place for prose introductions). Acceptable — the structure is the value.

### 2. Eight templates corresponding 1:1 to the eight type labels

Each type label gets its own template file. Per-type extra fields (Reproduction + Expected vs. actual on `bug`; Compounding cost on `tech-debt`; Batch with on `cleanup`; Source audit report path on `health-check-finding`; Resolution path on `question`; Upstream tracker URL on `upstream`) reflect per-label legitimate variation; merging into a unified template with conditional fields would either drop the per-type semantics or recreate them via YAML branching the spec doesn't fully support.

Rejected: single unified template. Each label needs different focus — pre-fragmentation would conflate.

Rejected: splitting across multiple ADRs (mirroring the [ADR 0072](0072-frontend-discipline-skill.md) / [ADR 0073](0073-paideia-frontend-overlays-skill.md) precedent). The 0072/0073 split was driven by orthogonal universal-vs-tailored concerns; here all eight templates encode one body-shape discipline. Single ADR is the right shape.

### 3. Required-field discipline matches `issue-discipline.md` body shape exactly

All eight templates require: Context, Symptom, Proposed approach, Affected files (defaulted), Cross-references. Per-type additions inherit the same required-by-default posture, with one deliberate exception: `cleanup`'s **Batch with** is optional. A cleanup item that legitimately stands alone shouldn't be forced to invent a batch; the option remains for items that do cluster.

The shape is the contract documented in [`issue-discipline.md`](../operations/issue-discipline.md) "Issue body shape" section. Templates mechanize it; the doc remains the source-of-truth. When the doc's shape changes, templates change in lockstep (see decision 6).

### 4. "Affected files" default is the literal `- (not yet identified)` as authorial-discipline signal

The collision-detection scanner at [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py) (lines 224-226) does substring-matching of touched paths against Issue body+title — `path.lower() in haystack`. It does NOT regex-match the literal `- (not yet identified)`. The literal is an **authorial-discipline signal** so future-cold readers know paths weren't omitted by mistake; the scanner reads paths from the section content when paths exist.

Templates pre-fill the literal in the **Affected files** textarea so the discipline signal is preserved by default. Authors who know the touch surface override the literal with actual paths; the substring scanner then finds them. Authors who don't know yet leave the literal in place; the scanner cannot match but the discipline signal is honest.

Issue #72's body framing — *"the scanner-recognized literal `- (not yet identified)`"* — was loose. This ADR clarifies: the literal is for human readers; the scanner reads paths from whatever shape the section actually holds.

### 5. `config.yml` disables blank-issue creation and links to `issue-discipline.md`

`.github/ISSUE_TEMPLATE/config.yml` sets `blank_issues_enabled: false` so the web UI no longer offers the blank-issue fast-path — every new Issue picks a typed template. `contact_links` carries one entry pointing to `issue-discipline.md` on the public GitHub web URL, so authors who need to consult the body-shape contract have a one-click route from the template chooser.

Rejected: keeping the blank fallback. A blank Issue is exactly what the templates prevent — leaving the fallback creates a parallel path that defeats the mechanization. The cost of removing it (an author with an unusual Issue must pick the closest template and customize) is small.

### 6. Cascade contract with `issue-discipline.md` via new entry in `cascade-discipline.md`

When `issue-discipline.md` body-shape changes (a new required section added, an existing one renamed, a per-type field added), all eight templates must update in lockstep. The change is small but easy to miss, and a drift would silently degrade the mechanization. New entry under [`cascade-discipline.md`](../operations/cascade-discipline.md) "Manual cascade procedures" names the four-step procedure:

1. Update `issue-discipline.md`.
2. Update each `.github/ISSUE_TEMPLATE/*.yml` field/heading in lockstep.
3. Verify `scan_issue_collisions.py` substring contract still holds if heading text changed (the scanner reads body content, not headings — heading rename is usually safe, but worth checking).
4. Same-commit landing (splitting leaves the templates and the doc out of sync until the next commit).

No new validator soft-warn category. The cascade is rare enough that posture suffices; the audit-time spot-check at session shutdown plus the manual procedure suffice for the surface.

**No title-prefix convention.** Recent Issues (#75–#106) do not use `Bug:` / `Enhancement:` prefixes. Templates leave the title blank for the author to write a concrete one-line title; auto-applied labels provide the type signal. The Issue #72 body's "Bug:" / "Enhancement:" examples were nominal at rollout-authoring time and are treated as such here. A future ADR amendment could adopt prefixes if a posture change is wanted; this ADR matches existing posture.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

GitHub issue template adoption is evaluated against the four cross-cutting criteria from [ADR 0053](0053-mechanism-first-exercise-gate.md):

- ❌ Criterion 1 — new session mode. **No.** Templates are GitHub-web-UI surface; sessions don't invoke them.
- ❌ Criterion 2 — new validator soft-warn category. **No.** Templates mechanize a doc; `validate.py` is unaffected.
- ❌ Criterion 3 — new state file the boot procedure reads. **No.** The boot procedure reads `register_state.json`, `current.json`, and `STATE.md`; templates introduce no new state.
- ❌ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **No.** This adoption touches `.github/ISSUE_TEMPLATE/{config,bug,enhancement,tech-debt,cleanup,health-check-finding,documentation,question,upstream}.yml` (9 files), this ADR, `engine/operations/issue-discipline.md` (one-line pointer), `engine/operations/cascade-discipline.md` (one new section), `engine/adr/README.md` (one index row), `engine/STATE.md` (close row), `engine/ENGINE_LOG.md` (one entry). Two ops docs touched; zero tooling files touched (the YAML files are config, not Python tooling). Under the ≥3 ops docs or ≥5 tooling files threshold.

Zero criteria satisfied → **no first-exercise readiness note required.** Standard GitHub feature; not a novel cross-cutting mechanism. Mirrors [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) (Dependabot, S-0133), [ADR 0070](0070-project-wired-review-skill.md) and [ADR 0071](0071-project-wired-security-review-skill.md) (S-0134), and [ADRs 0072 + 0073](0072-frontend-discipline-skill.md) (S-0135) precedents. Issue #72 body's pre-S-0137 "no first-exercise readiness note required" assertion aligns with the rubric evaluation here.

### Other consequences

- **Positive — mechanizes the body-shape posture.** Authors who go through the template chooser cannot skip Context, Symptom, Proposed approach, Affected files, or Cross-references. The discipline that previously lived in author memory now lives in the form UI.
- **Positive — auto-applied labels remove a manual triage step.** Picking `bug.yml` lands an Issue with `bug` already applied. The labels surface boot-time backlog counts and the collision-detection scanner; reducing the per-Issue triage cost is direct project value.
- **Positive — per-type extra fields surface load-bearing information at authoring time.** `bug`'s Reproduction + Expected vs. actual; `health-check-finding`'s Source audit report path (load-bearing for the boot surface's `Active health-check audits` lines); `upstream`'s tracker URL (without which an upstream is uncatchable when it moves); `question`'s Resolution path (which keeps the question type honest about how it should resolve). Each addition is a specific friction-removal for that label's natural shape.
- **Cost — template/doc drift now a real risk.** Pre-S-0137 the doc was the only surface; drift was impossible. Post-S-0137 the templates and the doc both encode the shape; if one changes without the other, the mechanization degrades silently. Addressed by the cascade-discipline entry (decision 6). The cost is small but real.
- **Cost — nine new files in `.github/`.** Surface enlargement is minor (`.github/ISSUE_TEMPLATE/` is the spec-defined location; the files are config-shape, not code).
- **Cost — blank-issue authors lose the fast-path.** A user with an unusual Issue must pick the closest template and customize. Per decision 5, this is by design — the blank-issue fast-path is exactly what the templates prevent. Estimated frequency: rare.
- **Out of scope — title prefix convention.** Decision 6 settles this against adoption. Future ADR amendment could revisit.
- **Out of scope — dropdown for `priority:urgent`.** Per `issue-discipline.md`, `priority:urgent` is applied manually at triage time, not at authoring time. Adding a priority dropdown would invite over-application and erode the LOUD-surface signal.
- **Out of scope — HANDOFF.md templating.** Per [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md), HANDOFF.md is a Markdown surface authored by sessions, not by web-UI users; templating it would mechanize a discipline that doesn't have a web-UI surface to mechanize.
- **Out of scope — automatic Issue-template-update on `issue-discipline.md` change.** A pre-commit check that catches template-doc drift would be a `validate.py` soft-warn; deliberately not added (decision 6). Posture suffices for this surface.

### Empirical record (pending — first natural Issue filing)

First real authoring through templates is the natural verification — the next session that files an Issue exercises the template chooser, the required-field UI block, and the auto-label behavior. Record at that point in this subsection: which template was used, whether the required-field UI blocked an attempted incomplete submit, whether the auto-label landed cleanly, and any UX-friction surfaces discovered.

The S-0137 closeout includes one optional in-session test: file a deliberate test Issue (then close it) to exercise the template chooser end-to-end. Decision deferred — natural-first-use is the canonical verification; a synthetic test adds little.

## See also

- [Issue #72](https://github.com/StarshipSuperjam/paideia/issues/72) — closes.
- [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — HANDOFF/Issues split that `issue-discipline.md` operationalizes.
- [ADR 0049](0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — `declared_scope` that the collision-detection scanner consumes.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; this adoption is explicitly under the threshold.
- [ADR 0066](0066-pr-template-and-branch-protection.md) — `.github/` precedent for surface-level discipline checklist mechanization.
- [`engine/operations/issue-discipline.md`](../operations/issue-discipline.md) — Layer 1 source-of-truth that this ADR's mechanization tracks.
- [`engine/operations/cascade-discipline.md`](../operations/cascade-discipline.md) — extended with the new cascade procedure (decision 6).
- [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py) — the scanner whose substring contract this ADR clarifies (decision 4).
- Pattern source: standard GitHub issue forms specification.
