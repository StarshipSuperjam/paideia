# Cascade discipline

> When a structural relationship in the project changes — an ADR is superseded, a file is renamed, an operations doc is restructured, an ADR-named deliverable lands — the relationship's downstream side needs an audit. Cascade discipline names the audits; the validator mechanizes a slice; the rest is authorial procedure triggered by lifecycle events. Per [ADR 0041](../adr/0041-cascade-analysis-discipline.md).

This document is the Layer 1 source-of-truth for the cascade-analysis pattern, in the sense of [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md). It is read at the moments a cascading change is about to be made, not as background reference.

## Mechanical checks

`engine/tools/validate.py` runs three soft-warn checks every commit. Each is documented in detail in [`tools-validate-interpretation.md`](tools-validate-interpretation.md); the summary here is what each catches.

- **`superseded_adr_currency`** — a doc cites an ADR that is now `Superseded by ADR NNNN`, and the citation does not mark itself as historical. Surfaces stale "per ADR 0002" references after ADR 0002 was superseded.
- **`adr_back_reference_orphan`** — an `Accepted` ADR has no inbound citation outside its own subtree. Surfaces ADRs that may be load-bearing-for-future-work or may be dead weight; the answer is a judgment call.
- **`adr_consequences_deliverable_audit`** — an ADR's Consequences section anticipated a deliverable "around S-NNNN," that session is closed, and the deliverable is absent. Surfaces promised-but-not-delivered work.

The checks are soft-warn because each can legitimately fire and be left in place — the orphan check on a Phase 8 ADR before Phase 8 starts; the supersession check on a doc that intentionally cites the historical ADR as historical context. Soft-warn means recorded in `outcome_summary.soft_warns` and surfaced at boot if persistent (per [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md)). The session decides whether to act, annotate, or accept.

## Manual cascade procedures

When a session is about to make one of the changes below, run the named audit before the change closes. The audit is part of the change, not a follow-up.

### Renaming or moving a tracked file

1. `git grep -l '<old-path>'` — list every tracked file that mentions the old path.
2. For each match, decide: update the reference, or accept that the reference is now historical.
3. The same commit that moves the file updates the references. Splitting them across commits leaves the validator green and the docs broken until the next commit lands.

The mechanical alternative — having the validator detect "old-path mentioned but file no longer at that location" — is partially covered by `cross_references_resolve` for `CROSS_REFERENCES.md` and by Markdown link resolution generally. It does not cover prose mentions outside link syntax, which is why the manual grep is named here.

### Superseding an ADR

1. The new ADR carries `Status: Accepted` and a `Supersedes: ADR NNNN` line.
2. The old ADR's `Status:` flips to `Superseded by ADR NNNN`.
3. `git grep -l '<old-adr-id>'` outside `*/adr/*` and `engine/ENGINE_LOG.md` — list every doc citing the old ADR.
4. For each match: re-point to the new ADR, OR add a `(superseded by ADR NNNN)` qualifier if the citation is intentionally historical, OR rewrite the surrounding paragraph if the supersession changes the substance of what the doc says.
5. Update [`product/docs/CROSS_REFERENCES.md`](../../product/docs/CROSS_REFERENCES.md) if the superseded ADR appeared there.
6. Same commit. Splitting leaves the `superseded_adr_currency` check firing on the next commit.

The cross-engine/product-partition supersession case is unchanged in mechanics — the new ADR lives in whichever subtree fits its load-bearing reader, per [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md).

### Restructuring an operations doc

When an operations doc is split, merged, or has its name changed:

1. `git grep -l '<old-doc-filename>'` — list every doc that links to the doc being restructured.
2. Update each link to the new shape (split: which of the new docs carries the cited content?; merge: the merged doc; rename: the new name).
3. If the doc was cited from CLAUDE.md's "Topical pointers" section, update that entry.
4. If the doc was cited from an ADR's "See also," update that section. Be careful: the ADR's body text may also cite the doc.

Merges and splits are higher-risk than renames because the cited content's location may change in ways `git grep` on filename doesn't catch. The author of the restructure is responsible for tracing each citation to the correct new location.

### Changing the Issue body shape in `issue-discipline.md`

The body shape that GitHub Issues must follow lives in [`issue-discipline.md`](issue-discipline.md) "Issue body shape" section, and is mechanized via [`.github/ISSUE_TEMPLATE/*.yml`](../../.github/ISSUE_TEMPLATE) per [ADR 0075](../adr/0075-github-issue-templates.md). Templates and the doc must change together; drift would silently degrade the mechanization.

When a session updates the body shape (a new required section added, an existing one renamed, a per-type field added or removed):

1. Update [`issue-discipline.md`](issue-discipline.md) — the source-of-truth.
2. Update each [`.github/ISSUE_TEMPLATE/*.yml`](../../.github/ISSUE_TEMPLATE) file's `body:` entries to match (field labels, required-ness, defaults, ordering).
3. If a heading rename changed the body content the scanner reads — verify [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py)'s substring contract still holds (the scanner reads body content, not headings, so heading-only renames are usually safe; new-field additions warrant a sanity check that the field's value contributes to the body string the scanner sees).
4. Same commit. Splitting leaves templates and doc out of sync until the next commit; a Web-UI author between the two commits gets a stale form.

No validator soft-warn mechanizes this cascade — the surface is rare and the manual procedure suffices. Future sessions adding doc-or-template-only changes are the natural failure mode; the session-shutdown spot-check catches it (per the cascade-trigger extension below).

### Closing a deliverable an ADR named

When a session lands a deliverable that an ADR's Consequences section anticipated:

1. The closing commit message names the ADR by id (e.g., `feat(tools): land health_check.py per ADR 0022 Consequences`).
2. The session's ENGINE_LOG entry names the ADR-id-and-deliverable handshake explicitly (e.g., `Added: engine/tools/health_check.py — closes the deliverable promised in ADR 0022 Consequences ("tools/health_check.py around S-0025")`).
3. The `adr_consequences_deliverable_audit` check passes for that ADR on the next commit because the deliverable file now exists on disk.

The handshake is the cascade-discipline answer to "an ADR promised X; how does the project know X happened?" Without the handshake, the deliverable can land without anything updating the ADR's Consequences expectation, and a future health check has to reconstruct the relationship from inference.

## Cascade triggers in lifecycle

Cascade audits attach to two existing lifecycle events. Both extensions are posture, mechanized only insofar as the operations docs name them.

### Session shutdown

[`session-shutdown-sequence.md`](session-shutdown-sequence.md)'s spot-check step asks "for every artifact created or modified in this session: cross-references resolve?" Cascade discipline extends this with: "did this session touch an ADR, an operations doc, or `engine/STATE.md`? If yes, run the manual cascade procedure for that change kind before closing."

The mechanical checks catch the structural slice; the spot-check catches the prose-mention slice the validator cannot see.

### Build-readiness gate

[`build-readiness-gate.md`](build-readiness-gate.md)'s triage phase produces Tier 1 / Tier 2 / Tier 3 findings. Cascade discipline adds a triage question: "what downstream artifacts will this chunk's authoring affect — ops docs, ADRs, validator checks, lifecycle steps? Which need the cascade procedure run before the chunk's authoring lands?"

The question is not always actionable at gate time (the chunk's own authoring is what produces the downstream impact). Naming it in the gate report makes the downstream-impact surface explicit, so the build session can plan its commit boundaries to keep cascading changes within commits rather than splitting them.

## Annotation mechanism for intentional orphans

The `adr_back_reference_orphan` check fires on any `Accepted` ADR with no citations outside its own subtree. Some ADRs are intentionally orphaned at authoring time — they ground a future phase's decisions, or they are reference material the project will cite when the relevant work begins.

To suppress the warn:

1. Add a header line to the ADR file directly under the metadata block:
   ```
   - **Orphan-OK:** <reason>; revisit at <session-id-or-phase>
   ```
2. The validator parses this line and skips the orphan warn for ADRs carrying it.
3. The periodic health check (per [ADR 0022](../adr/0022-periodic-project-health-checks.md)) audits the orphan-OK list and surfaces any whose revisit-by trigger has passed.

The annotation is a deferral, not a permanent exemption. An ADR that carries `Orphan-OK` for many cadence cycles without coming off the list becomes a candidate for explicit deprecation or supersession at the next health check.

## See also

- [ADR 0041](../adr/0041-cascade-analysis-discipline.md) — the citable contract this document operationalizes.
- [ADR 0022](../adr/0022-periodic-project-health-checks.md) — the periodic audit that catches the residue.
- [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) — inward-document contract this doc is authored under.
- [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md) — partition the cascade audits respect.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — per-check interpretation guidance, extended with the three new checks.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — extended spot-check.
- [`build-readiness-gate.md`](build-readiness-gate.md) — extended triage question.
- [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md) — how the new soft-warns surface across sessions.
- [`product/docs/CROSS_REFERENCES.md`](../../product/docs/CROSS_REFERENCES.md) — the existing forward-mapping that supersessions update by hand.
