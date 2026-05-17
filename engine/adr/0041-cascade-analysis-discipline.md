# ADR 0041 — Cascade-analysis discipline: mechanical checks plus manual procedures

- **Status:** Accepted
- **Date:** 2026-05-02
- **Deciders:** S-0029

## Context

The project has 40 ADRs (post-S-0027), ~30 operations docs, two ADR README indices, a forward-only `product/docs/CROSS_REFERENCES.md`, and growing inter-document dependency. Three failure modes have already manifested:

1. **Stale superseded-ADR citations.** When ADR 0002 was superseded by ADR 0032 (and 0032 by 0035), some downstream files were updated to re-point and some were not. `validate.py`'s `cross_references_resolve` confirms the link target exists; it does not check whether the cited ADR is still the current commitment for that topic. A doc citing "per ADR 0002" reads as authoritative even though ADR 0002's status now says `Superseded by ADR 0032`.
2. **Orphaned ADRs.** An ADR can land, get cited nowhere, and stay forever as "Accepted" without any downstream work depending on it. The orphan may be load-bearing for future work or it may be dead weight; nothing surfaces the question. The existing `adr_index_consistency` check catches "ADR file exists but README index doesn't list it"; it does not catch "ADR is indexed but no doc cites it."
3. **Promised-but-not-delivered Consequences.** ADR 0022's Consequences section anticipated `tools/health_check.py` "around S-0025." S-0025 was repurposed for the cross-reference sweep, no subsequent session claimed health_check.py, and nothing flagged the gap. The cadence trigger (per ADR 0022) was scheduled to fire at S-0030 against machinery that didn't exist.

The common shape of all three: a structural relationship exists (supersession, citation, deliverable promise) and the project's machinery does not audit whether the relationship's downstream side is current. The pre-commit validator catches structural invariants (file missing, JSON malformed); cascade-analysis is the missing audit channel between "structural invariants pass" and "the documentation describes the project as it is now."

The CLAUDE.md "Posture vs machinery" section already names two-layer decision recording and the startup ceremony order as posture. Cascade audits are similar in shape — they degrade silently and the AI's discipline alone has been insufficient. This ADR moves a slice of cascade auditing from posture to machinery (three soft-warn validator checks) and codifies the rest as an operations doc with manual procedures triggered by lifecycle events.

## Decision

The project carries a cascade-analysis discipline composed of two parts:

1. **Three soft-warn validator checks** in `engine/tools/validate.py`, run by the pre-commit hook on every commit:
   - `validate_superseded_adr_currency` — for each ADR with status `Superseded by ADR NNNN`, grep tracked `.md` files outside `*/adr/*` and `engine/ENGINE_LOG.md` for the superseded ADR's id; soft-warn on any citation whose surrounding context does not mark the reference as historical (substring `superseded` case-insensitive within 50 chars, or co-occurrence of the new ADR id).
   - `validate_adr_back_reference_orphan` — for each ADR with status `Accepted`, grep tracked `.md` files outside `*/adr/*` for the ADR id; soft-warn on any ADR with zero matches outside its own subtree. The check produces false positives for load-bearing-but-uncited ADRs (e.g., ADRs that ground a future phase's decisions); annotation in the ADR's own header marks the ADR as intentional-orphan and suppresses the warn.
   - `validate_adr_consequences_deliverable_audit` — heuristic regex against each ADR's Consequences section for substrings of the form `(anticipated|lands?|expected|targeted) (around |at |in )?S-(\d{4})`; for each match, check whether the named session is closed per `engine/session/archive/` and whether any deliverable file path also named in the ADR text exists on disk; soft-warn when the session is closed and the deliverable is absent.

2. **`engine/operations/cascade-discipline.md`** as the Layer 1 source-of-truth document for the manual cascade procedures the validator cannot mechanize: file rename / move (grep tracked docs for old path); ADR supersession (update CROSS_REFERENCES.md, audit citing docs, add `(superseded by …)` qualifier or re-point); operations doc restructure (grep for inbound citations and audit each); deliverable-completion handshake (when an ADR-named deliverable lands, the closing commit cites the ADR by id so future audits can verify).

The ops doc also names the lifecycle integration points: the existing session-shutdown spot-check step is extended to include a cascade-audit pass when the session touched ADRs, ops docs, or `engine/STATE.md`; the build-readiness gate adds a downstream-impact-of-this-chunk question to its triage. Both extensions are posture in this ADR — they encode an authorial habit. Mechanizing them is deferred until practice shows posture is insufficient.

## Consequences

`engine/tools/validate.py` carries three additional soft-warn checks. The first run on the existing repo will surface findings against current documents — those are recorded in S-0029's `outcome_summary.soft_warns` and triaged in the next non-trivial session. The orphan check is expected to flag several ADRs that are load-bearing for future work (e.g., ADRs about Phase 7 features); each gets a header annotation per the suppression mechanism above.

`engine/operations/cascade-discipline.md` joins the operations docs library; CLAUDE.md's "Topical pointers" section gains an entry. The shutdown sequence and build-readiness gate ops docs gain text naming the cascade-audit pass; this is amendment-only (no new ADR for the lifecycle-doc changes) per ADR 0036's amendment asymmetry.

Two trade-offs accepted:

- **Heuristic checks have false positives.** The Consequences-deliverable audit's regex is intentionally narrow; it catches the literal "tools/foo.py around S-0025" shape and misses prose that promises a deliverable in different language. Tightening the regex risks more false negatives. The check's value is partial coverage of a class that today has zero coverage; the residue is caught by the periodic health check.
- **The orphan check's annotation mechanism creates a small surface for hiding real orphans.** A future session could mark a genuinely-dead ADR as intentional-orphan and silence the warn. Mitigation: the periodic health check (per ADR 0022) audits the annotation list and asks whether each is still load-bearing. The annotation is a deferral mechanism, not a permanent exemption.

The discipline is not retroactive on past sessions' authoring choices. ADRs and docs authored before this ADR are not held to the new checks at authoring time; the validator surfaces drift on next commit-touch of the affected files. The first cleanup pass is the natural way to bring the existing corpus current.

## See also

- [ADR 0022](0022-periodic-project-health-checks.md) — the periodic audit that catches the residue cascade-discipline does not mechanize.
- [ADR 0036](0036-expression-contract-for-inward-documents.md) — the inward-document expression contract `cascade-discipline.md` is authored under.
- [ADR 0037](0037-engine-product-wall-and-changelog-rename.md) — the engine/product partition; cascade audits respect the wall (engine docs cite engine ADRs unless cross-cutting).
- [ADR 0040](0040-build-readiness-gate-before-substantive-build-sessions.md) — the gate that gains a downstream-impact-of-this-chunk triage question.
- [`engine/operations/cascade-discipline.md`](../operations/cascade-discipline.md) — the operationalized procedures.
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — soft-warn category interpretation, extended with the three new checks.
- [`product/docs/CROSS_REFERENCES.md`](../../product/docs/CROSS_REFERENCES.md) — the existing forward-mapping the supersession procedure updates by hand.
- [ADR 0092](0092-per-session-changelog-directory.md) — S-0198. The cascade-audit `validate_adr_back_reference_orphan` exclusion list extends from the legacy `ENGINE_LOG.md` filename match to a directory-prefix exclusion for `engine/changelog/` (per-session entries reference ADRs as commit-pointer prose, not load-bearing back-refs).
