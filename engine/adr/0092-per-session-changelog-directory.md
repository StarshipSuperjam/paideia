# ADR 0092 — Per-session changelog directory replaces monolithic ENGINE_LOG.md (supersedes ADR 0037 in part)

- **Status:** Accepted
- **Date:** 2026-05-17
- **Deciders:** S-0198
- **Supersedes:** [ADR 0037](0037-engine-product-wall-and-changelog-rename.md) — only the ENGINE_LOG-naming/structure clauses (the engine/product wall partition stays Accepted; the file's structural form changes from monolithic to per-session directory).

## Context

[ADR 0037](0037-engine-product-wall-and-changelog-rename.md) (S-0022) renamed `CHANGELOG.md` to `ENGINE_LOG.md` — committed to a single Keep-a-Changelog-formatted file at `engine/ENGINE_LOG.md` carrying a `[Unreleased]` block that accreted material engine changes session by session, with the preamble committing the project to a `0.1.0` cut at foundation close. Foundation is closed (Phase 5 done; OQ-DEC1 settled at S-0152 per product ADRs 0085–0088; OSS pivot landed S-0128–S-0130; SWE-hardening Tier 1+2 done; ADR collection at 91), but the cut has never executed; ENGINE_LOG.md is **2,799 lines** with zero prior release sections.

[Issue #132](https://github.com/StarshipSuperjam/paideia/issues/132) (filed from the S-0184 health-check audit's Finding-ENGINE-LOG; user adjudicated option (d) — cut + structural split + duplication audit combined) named the file as overdue per its own preamble convention. Issue #132's prescription was three-part: prune duplication, cut to a dated `[0.1.0]` section, split closed releases into `ENGINE_LOG_HISTORY.md`. The user has independently authored a generalized solution in the Engine reference template (`/Users/shanekidd/Documents/Claude_Files/Engine/.engine/changelog/`) that takes a structurally different shape: a **per-session changelog directory** at `.engine/changelog/<YYYY>/<S-NNNN>-<slug>.md` with YAML-frontmatter validation against a schema, a 50-line-soft / 70-line-hard body cap, an aggregator that synthesizes `[Unreleased]` views on demand from per-session entries since the last release tag, and an annual rollover convention to `_history/<YYYY>/`. The user directed Paideia to adopt the Engine reference's pattern rather than execute Issue #132's prescription literally.

The Engine reference's pattern reframes Issue #132's three parts as Consequences-of-adoption:
- **Part 1 (duplication audit)** becomes structural rather than retroactive. The 50-line cap + `material_change_class` enum + going-forward-only discipline force the duplication audit at write time, not after the fact.
- **Part 2 (cut 0.1.0)** becomes a single bounded `0.1.0-foundation-close-S-0198.md` synthesis entry capturing only material engine-change content not in structured archives.
- **Part 3 (structural split)** becomes the directory layout itself (`<YYYY>/` for active, `_history/` for closed years; the historical 2,799 lines preserve byte-for-byte under `_history/ENGINE_LOG-pre-0.1.0.md`).

### Load-bearing premises

Per [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md). This ADR triggers extraction step under three of the four classes: (1) cross-cutting mechanism authoring per [ADR 0053](0053-mechanism-first-exercise-gate.md) trigger criterion #4 (Consequences span 25+ surfaces: schema, validator checks, shutdown skill, ops doc, 5 ADRs, 22 inbound prose pointers, aggregator tool, hook test fixtures); (2) supersession of a load-bearing prior decision (ADR 0037's ENGINE_LOG-naming clauses); (4) contract-shape change (the file's structural form mutates monolithic→directory).

1. **The structured per-session archives (`engine/session/archive/S-NNNN.json`) carry the canonical material content; ENGINE_LOG.md's `[Unreleased]` body duplicates 75–90% of it.** *Falsifier:* a sampled comparison shows the duplication rate <50% or finds substantial unique content in ENGINE_LOG. *Test status — empirically verified in-context at this session's authoring.* Sampled 5 sessions evenly distributed (S-0030 health-check; S-0070 Phase 5 philosophy-of-mind migration; S-0110 routine SEP audit; S-0150 backlog batch close; S-0190 engine-memory capture). Per-session overlap ranged 75–90%, mean ~83%. Unique content in ENGINE_LOG was narrow: file-deliverable bullets with paths + commit-link wrappers + Keep-a-Changelog Added/Changed/Removed sectional structure. The archive's `outcome_summary` carried the substantive narrative (what shipped, why, telemetry, what surprised). The per-session changelog entry pattern preserves the unique-to-ENGINE_LOG content (file deliverables + classification) while eliminating the duplicative narrative.

2. **Per-session entries with a 50-line cap force material-change selection at write time.** *Falsifier:* the 50-line cap is regularly exceeded by sessions that genuinely need more lines, OR is regularly met by sessions that didn't need to write at all. *Test status — partially testable now:* the Engine reference's existing 11 sample entries (`S-0002` through `S-0011`) all land between 30–50 lines; the format converges naturally to "summary + section bullets + see-also pointers." Empirical validation continues at first natural exercise per the first-exercise readiness note.

3. **The 22 inbound prose references can absorb the rename in a single cascade commit.** *Falsifier:* `git grep -l "engine/ENGINE_LOG.md"` after the cascade returns >2 unintended matches in active surfaces (intended residue: ADR 0037 supersession amendment subsection, this ADR's Supersedes line, the moved `_history/` file's own internal cross-refs). *Test status — empirically verifiable post-cascade.* Mechanical greppability; cascade lands in single commit (Part G of the approved plan).

4. **The Engine reference template's structure ports cleanly into Paideia's flatter `engine/` tree.** *Falsifier:* the port introduces apparatus Paideia doesn't have (e.g., `.engine/contracts/governance/governed_files.yaml`) that doesn't fit Paideia's existing layout. *Test status — empirically resolved at authoring.* Paideia uses `engine/` (not `.engine/`); schemas land at new top-level `engine/schemas/` (Paideia lacks `contracts/schemas/`); the `governed_files.yaml` apparatus is *not* ported (Paideia uses a standalone validator check for the README line-cap; see Alternatives Considered). Mapping summary in Consequences.

5. **The aggregator's `--since <git-tag>` flag requires `git tag` discipline; the 0.1.0 cut creates the first such engine-side tag.** *Falsifier:* a future release skips the tag, breaking aggregator `--since` semantics. *Test status — verifiable at session close.* The S-0198 close creates `engine-v0.1.0`; future release ADRs commit to the tagging discipline. The aggregator falls back gracefully (no `--since` → emits all entries; tag missing → exits non-zero with explicit error).

## Decision

The project replaces the monolithic `engine/ENGINE_LOG.md` with a **per-session changelog directory** at `engine/changelog/<YYYY>/<S-NNNN>-<slug>.md`, schema-validated frontmatter, 50/70-line cap, aggregator-driven `[Unreleased]` synthesis. Six specific shapes:

1. **Directory layout.** `engine/changelog/` carries `README.md` (governance), `<YYYY>/` for active-year entries, `_history/` for rollover destination. Entries: `<S-NNNN>-<slug>.md` with `S-NNNN` matching the session_id frontmatter field; slug human-authored, kebab-case. The historical `engine/ENGINE_LOG.md` (2,799 lines) moves to `engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md` byte-for-byte (sha256 captured in the move-commit message).

2. **Frontmatter schema (validated at commit-time).** YAML frontmatter required: `session_id` (pattern `^S-[0-9]{4}$`), `session_type` (enum: `build` / `routine` / `exploration`), `closed_at` (ISO 8601 date-time UTC), `material_change_class` (enum: `adr` / `policy` / `check` / `audit` / `operation` / `tool` / `skill` / `module` / `schema` / `infrastructure` / `docs` / `mixed`), `module` (string; cross-cutting → `"multi"`). Optional: `summary` (string, max 200 chars). Schema at `engine/schemas/changelog-entry.schema.json` (ported byte-for-byte from Engine ref).

3. **Body cap.** 50 lines soft (validator soft-warn `changelog_entry_soft_cap`) including frontmatter; 70 lines hard (validator hard-fail `changelog_entry_hard_cap`). The cap forces summary-plus-pointers shape; substantive narrative belongs in the structured archive.

4. **Material-change discipline.** Trivial fixes (typos, formatting, rerun-tests) do NOT write entries. The 12-class enum names what qualifies; AI judgment at shutdown step 7 decides whether the session produced material change. "When in doubt, no entry is better than an empty one." The structured archive at `engine/session/archive/S-NNNN.json` carries the canonical session record regardless of whether a changelog entry is written.

5. **Aggregator.** `engine/tools/changelog_aggregate.py` synthesizes Keep-a-Changelog `[Unreleased]` views on demand. CLI: `--since <git-tag>` (entries with `closed_at > git tag committer-date`); `--module <name>` (frontmatter filter); `--format markdown|json`; `--validate-only` (lint entries against schema without emitting). Grouping by `material_change_class`.

6. **Release tagging discipline.** Each release cut creates a git tag (`engine-v<N.N.N>`). The 0.1.0 cut at S-0198 creates `engine-v0.1.0`. Future release-cut ADRs reference this tagging convention; the aggregator's `--since` uses tags as boundary markers.

The engine/product wall (ADR 0037 Decision part 2) stays Accepted unchanged. ADR 0037 flips to `Status: Superseded in part by ADR 0092` with a Supersession Amendment subsection describing the structural-form change while preserving the wall partition.

## Alternatives Considered

Per [ADR 0077](0077-adr-template-alternatives-considered-section.md).

### A1 — Issue #132's literal three-part prescription (preserve monolithic file + cut to `[0.1.0]` + split history file)

- **What:** Keep `engine/ENGINE_LOG.md` as a single file with `[Unreleased]` + `[0.1.0]` sections; move closed `[0.1.0]` block to `engine/ENGINE_LOG_HISTORY.md`; ENGINE_LOG.md carries preamble + `[Unreleased]` + pointer.
- **Pros:** Smallest scope; preserves the existing Keep-a-Changelog format unmodified; the duplication audit (Part 1) becomes a one-time retroactive pass with reusable discipline going forward.
- **Cons:** The going-forward discipline is still posture (AI judgment at shutdown step 7 not to duplicate archive content); no mechanical enforcement. The 50-line cap that the per-session directory pattern enforces structurally lives nowhere in A1. ENGINE_LOG.md continues to be a write-mostly surface; the next cut at 0.2.0 will face the same 2,799-line problem at a smaller scale.
- **Rejected because:** the user has authored the Engine reference's solution and directed Paideia to adopt it. A1 is the path Issue #132 named but is no longer the chosen path.

### A2 — Per-session directory + full `governed_files.yaml` apparatus port from Engine ref

- **What:** Port not just the changelog pattern but also the Engine ref's `.engine/contracts/governance/governed_files.yaml` + `check_governance()` system that mechanically enforces line-caps + frontmatter-sync across any file declaring `governed: true`.
- **Pros:** Unified governance surface; line-cap discipline becomes extensible to other Paideia files (ADRs, ops docs, operations specifications).
- **Cons:** Substantial extra scope — Paideia has no `contracts/governance/` directory; the apparatus would add ~150 LOC of validate.py logic + a new schema + a registry file + cascade updates wherever `governed: true` frontmatter might apply. The changelog adoption does not require it; the standalone changelog validator check (Part D of the approved plan) covers the line-cap enforcement need at narrower scope.
- **Rejected because:** scope creep beyond the changelog adoption. A separate adoption ADR can pull in the `governed_files.yaml` apparatus when there's a second qualifying file class beyond the changelog README.

### A3 — Retroactively split the existing 2,799 lines into ~197 per-session entries

- **What:** Programmatically extract per-session entries from the historical ENGINE_LOG by parsing the `### Added/Changed/Removed (S-NNNN — ...)` sectional structure; author one `<YYYY>/<S-NNNN>-<slug>.md` per material-change session. Schema-validate the result.
- **Pros:** Historical record lives in the new structure; aggregator can produce full retrospective views.
- **Cons:** Estimated ~3,000 LOC of authoring + manual review. ~80% of historical entries would breach the 50-line cap (they're prose-heavy paragraphs sized when the cap didn't exist), requiring substantial editorial pruning per entry. The historical content is already byte-preserved under `_history/ENGINE_LOG-pre-0.1.0.md`; the structured archive at `engine/session/archive/S-NNNN.json` carries the canonical record. Retroactive authoring duplicates the historical record at the cost of one substantial session for marginal forward-looking value.
- **Rejected because:** the 0.1.0 release synthesis entry is the bounded historical view; the archived raw file is the verbatim record; retroactive per-session authoring is the heavy middle path that produces nothing the other two surfaces don't already.

### A4 — Delete engine/ENGINE_LOG.md outright; archives are the historical record

- **What:** Remove engine/ENGINE_LOG.md entirely; rely on `engine/session/archive/S-NNNN.json` for the historical record; start the per-session changelog pattern fresh.
- **Pros:** Cleanest break; eliminates the duplication surface entirely.
- **Cons:** Loses the chronological narrative view (the archives are per-session JSON files, not a chronological prose surface); loses the Keep-a-Changelog Added/Changed/Removed sectional organization that has value as a release-prep surface; cold readers querying "what changed across the foundation" lose their primary reading surface.
- **Rejected because:** the historical narrative surface is load-bearing for cold readers, release prep, audit-time review. Preserving under `_history/` costs near-zero (one byte-preserved move + a 0.1.0 synthesis entry) and preserves the reading affordance.

### A5 — Per-session directory + full Engine-ref aggregator (chosen)

- **What:** This ADR's Decision. Adopt the Engine reference pattern in Paideia-tailored form: `engine/changelog/<YYYY>/<S-NNNN>-<slug>.md` + schema + full aggregator (Engine ref's planned Session-4 scope, not the skeleton).
- **Pros:** Structural discipline replaces posture; the duplication-audit-as-discipline problem closes at the cap (Part 1 of Issue #132 becomes Consequences-of-adoption). Engine ref's pattern has been load-tested across the Engine template's own session sequence (11 sample entries) and converges on 30–50-line entries naturally. Paideia's flatter `engine/` tree absorbs the port without requiring contracts/ apparatus.
- **Rejected because:** not rejected — chosen.

## Consequences

- **`engine/ENGINE_LOG.md` is moved to `engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md`** byte-for-byte (sha256 captured in the move-commit message). The original path stops being a write surface. A transitional stub at the original path lives only across the cascade-commit window; deleted at cascade-end.

- **`engine/changelog/2026/0.1.0-foundation-close-S-0198.md`** is the first per-session entry. Synthesizes material engine-change content from S-0001–S-0197 not in structured archives. Body up to 70 lines (uses the hard cap rather than the soft cap because release synthesis is exceptional content; routine per-session entries respect the 50-line soft cap).

- **`engine/changelog/README.md`** carries governance frontmatter (`governed: true / line_cap_soft: 50 / line_cap_hard: 70`); the documentation-of-intent is mechanically enforced by `check_changelog_readme_governance` in validate.py (standalone check, not `governed_files.yaml` apparatus).

- **`engine/schemas/changelog-entry.schema.json`** is the new top-level schemas directory in Paideia. `engine/schemas/README.md` orients the directory's purpose. Future schemas (e.g., session-archive-frontmatter) can land here without contracts/ apparatus.

- **`engine/tools/changelog_aggregate.py`** ships full Session-4-scope implementation: frontmatter parsing, schema validation, grouping by `material_change_class`, `--since <git-tag>` + `--module` filters, markdown + JSON output, `--validate-only` mode. Reuses `engine/tools/timestamps.py` per ADR 0058; reuses the venv-import pattern from `engine/tools/archive_session.py`. ~15 pytests against tmp-dir fixtures.

- **`engine/tools/validate.py`** loses `engine_log_format` check (lines 414–427) and gains `check_changelog_entries` + `check_changelog_readme_governance`. The ENGINE_LOG.md exclusion in `validate_adr_back_reference_orphan` is replaced with a directory-prefix exclusion for `engine/changelog/` entries. ~10 new pytests.

- **`engine/operations/session-shutdown-sequence.md` step 7 + `.claude/skills/session-shutdown-sequence/SKILL.md` step 7** rewrite in lockstep per [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) recipe-vs-reference flow. New prose names the directory pattern, the 12 material_change_class enums, the 50-line cap, and the "trivial fixes do NOT write entries" discipline.

- **22 inbound prose references** rewire in a single cascade commit (5 root files: CLAUDE.md, STATE.md, ROADMAP.md, README.md, HANDOFF.md; 6 ops docs; 5 ADRs including ADR 0037's Supersession Amendment).

- **ADR 0037 flips to `Status: Superseded in part by ADR 0092`** with a Supersession Amendment subsection. The engine/product wall partition (ADR 0037 Decision part 2) stays Accepted; only the ENGINE_LOG-naming/structure clauses (Decision part 1 + the rename-rationale paragraphs) are superseded. Body preserved per status-conventions one-directional-pointer rule.

- **ADRs 0036, 0041, 0042, 0048** acquire light refresh updates — references to ENGINE_LOG.md as the layer-2 trace target update to point at the new directory pattern; their semantic role (four-layer trace; cascade-audit exclusion; soft-warn lifecycle; HANDOFF-vs-Issue partition) is unchanged.

- **First-exercise readiness note** authored at `engine/build_readiness/per_session_changelog_first_exercise.md` per [ADR 0053](0053-mechanism-first-exercise-gate.md). T1-A closes when this session (S-0198) writes its own changelog entry at close (the 0.1.0 release synthesis IS the first entry); T1-B at the next session's close (first non-release per-session entry); T1-C when the aggregator runs against ≥2 entries.

- **Release tagging discipline.** `engine-v0.1.0` git tag created at the S-0198 close commit. Future engine-side release cuts follow the same tagging convention.

- **Out-of-scope (explicit non-adoptions; future Issues):** annual rollover automation (Engine ref defers as manual; Paideia inherits); `governed_files.yaml` apparatus port (separate adoption ADR when a second qualifying file class lands); retroactive per-session authoring for S-0001–S-0197 (archives + 0.1.0 synthesis cover the historical view); slug/year-folder generator helpers (manual authoring is the Engine ref pattern); STATE.md prose narrative compaction (separate cleanup Issue STATE.md itself flags).

## See also

- [ADR 0037](0037-engine-product-wall-and-changelog-rename.md) — superseded in part. Engine/product wall partition stays Accepted; ENGINE_LOG-naming/structure clauses superseded by this ADR.
- [ADR 0036](0036-expression-contract-for-inward-documents.md) — four-layer trace system. Layer 2 (ENGINE_LOG) is now the per-session changelog directory; layer role unchanged.
- [ADR 0041](0041-cascade-analysis-discipline.md) — cascade-audit exclusion list updates from `ENGINE_LOG.md` filename match to `engine/changelog/` directory-prefix match.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn 3-of-5 trend canon stays in archives; ENGINE_LOG/changelog is not the soft-warn surface.
- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — shutdown SKILL ↔ Layer-1 doc parity; step 7 rewires in lockstep.
- [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — HANDOFF reserves for session-internal; Issues for cross-session; ENGINE_LOG / changelog role (material-change-only narrative) unchanged.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness note authored.
- [ADR 0058](0058-canonical-timestamp-format.md) — aggregator uses `engine/tools/timestamps.py` for `closed_at` parsing.
- [ADR 0077](0077-adr-template-alternatives-considered-section.md) — Alternatives Considered template.
- [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — extraction step dogfooded above.
- [ADR 0089](0089-skill-layer1-parity-validator-check.md) — `skill_layer1_parity_drift` check confirms step-7 rewrite parity post-edit.
- [ADR 0091](0091-engine-memory-substrate-sqlite-fts5.md) — sibling cross-cutting mechanism ADR; this ADR follows the same extraction-step + Alternatives-Considered + Consequences shape.
- Engine reference: `/Users/shanekidd/Documents/Claude_Files/Engine/.engine/changelog/` — pattern source. Adoption mapping: `.engine/changelog/` → `engine/changelog/`; `.engine/contracts/schemas/changelog-entry.schema.json` → `engine/schemas/changelog-entry.schema.json`; `.engine/tools/changelog/changelog_aggregate.py` → `engine/tools/changelog_aggregate.py`; `.engine/contracts/governance/governed_files.yaml` NOT ported (standalone validator check instead).
- [Issue #132](https://github.com/StarshipSuperjam/paideia/issues/132) — closes. Part 1 (duplication audit) becomes structural; Part 2 (0.1.0 cut) lands at S-0198; Part 3 (structural split) lands as the directory pattern itself.
- [`engine/build_readiness/per_session_changelog_first_exercise.md`](../build_readiness/per_session_changelog_first_exercise.md) — first-exercise readiness note.
