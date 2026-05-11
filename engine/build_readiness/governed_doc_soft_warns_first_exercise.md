# Governed-doc soft-warns — first-exercise readiness

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Tracks readiness criteria for the three soft-warns landed at S-0126 per [ADR 0062](../adr/0062-retire-adr-inline-amendments-and-governed-doc-soft-warns.md) (Issue [#87](https://github.com/StarshipSuperjam/paideia/issues/87) part b).

## Mechanism

Three new soft-warn categories in `engine/tools/validate.py`, run in the structural-phase block:

- **`state_md_row_count`** — fires when `engine/STATE.md` exceeds `STATE_MD_ROW_COUNT_THRESHOLD` (default 180; baseline at S-0126 was 118 rows).
- **`adr_consequences_amendment_header`** — zero-tolerance pattern catch on any `### Amendment` header in any `engine/adr/*.md` or `product/adr/*.md` file.
- **`handoff_long_resolved_sections`** — fires when (1) total `**Resolved:**` section count exceeds 5, or (2) any single resolved section's `S-NNNN` is more than 10 sessions older than the current session.

All three are documented per category in [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md).

## Readiness criteria

- **T1-A** — validator surfaces one of the three categories against a real (non-synthetic) candidate in any future session.
- **T1-B** — the surfaced soft-warn motivates a corrective edit:
  - `state_md_row_count`: trim STATE.md per the file's preamble (move per-session prose to archive + ENGINE_LOG.md), OR bump `STATE_MD_ROW_COUNT_THRESHOLD` with evidence the growth is load-bearing.
  - `adr_consequences_amendment_header`: fold the amendment substance into the ADR body as present-truth and delete the header. The pattern catch is zero-tolerance — there is no legitimate "leave it" path.
  - `handoff_long_resolved_sections`: prune the offending sections per the HANDOFF.md preamble's prune-on-resolve discipline.

Not silencing the warn via threshold bump without evidence is the load-bearing posture — if a category's threshold turns out to be wrong, fix the threshold with reasoning; do not raise it to make a real signal go away.

## Status

- **Open.** Awaits first natural exercise. Synthetic-fixture tests at [`engine/tools/test_validate.py`](../tools/test_validate.py) — `TestValidateStateMdRowCount` (3 tests), `TestValidateAdrConsequencesAmendmentHeaders` (5 tests), `TestValidateHandoffLongResolvedSections` (6 tests) — confirm the mechanism fires correctly on synthetic inputs (14 tests total, all green).
- Current repo state at S-0126: STATE.md = 118 rows (under threshold 180); zero `### Amendment` headers in any ADR (Retire-C just landed); HANDOFF.md has zero `**Resolved:**` sections (pruned at S-0121). No category fires on the live repo at first instrumentation; T1-A will close when STATE.md grows past 180 OR a future ADR author attempts an amendment block OR HANDOFF accumulates resolved sections.

## Cross-references

- [ADR 0062](../adr/0062-retire-adr-inline-amendments-and-governed-doc-soft-warns.md) — the contract.
- [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) — the expression contract these soft-warns mechanize for governed-doc surfaces.
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — per-category soft-warn entries.
- [Issue #87](https://github.com/StarshipSuperjam/paideia/issues/87) — source.
- `docs/health-checks/S-0121.md` — audit source (Retire-C + recommended soft-warns).
