# Paideia-specific security overlays

> Companion reference card for [`/security-review`](SKILL.md). Project-specific overlays beyond the OWASP Top 10 in [`owasp-checklist.md`](owasp-checklist.md). Authored at S-0134 per [ADR 0071](../../../engine/adr/0071-project-wired-security-review-skill.md). These overlays are NOT optional — they run alongside the OWASP walk.

## Overlay 1: Supabase RLS verification

**Why it's an overlay:** Supabase RLS is the load-bearing access control in Paideia's data model — every `public.*` table is gated by RLS policies; without correct policies the entire schema is world-readable. `validate.py` soft-warns when RLS is *missing*; this overlay verifies the enabled policy is *semantically* correct.

### Procedure

For every `public.*` table touched by the change:

1. Read the table's RLS policies (`SELECT * FROM pg_policies WHERE tablename = '<table>'`).
2. For each policy:
   - **Operation scope:** SELECT, INSERT, UPDATE, DELETE, ALL.
   - **`USING` clause:** what predicate gates read?
   - **`WITH CHECK` clause:** what predicate gates write?
   - **Roles:** which roles is the policy attached to? `anon` / `authenticated` / `service_role`.

3. Verify each policy against the table's intended access model:
   - Ownership-keyed tables: `USING (user_id = auth.uid())` and matching `WITH CHECK`.
   - World-readable tables (e.g., a published curriculum graph): `USING (true)` for SELECT only, with INSERT/UPDATE/DELETE policies that gate writes appropriately.
   - Service-role-only tables: no `anon` / `authenticated` policies; service-role bypasses RLS by default.

### Pass / Fail / N-A

- **PASS:** every touched table's policy matches its intended access model; no `USING (true)` without explicit justification.
- **FAIL:** any policy permits broader access than intended; any `USING (true)` without ADR-level justification.
- **N-A:** the change does not touch any `public.*` table.

### Failure examples to catch

- Adding a `user_data` table with `USING (true)` because the policy author wanted "to test it works" — should have been `USING (auth.uid() = user_id)`.
- A policy attached only to `anon` but the table is meant for authenticated users — `authenticated` should be the role.
- A `WITH CHECK` clause that's lax-er than the `USING` clause, allowing writes that shouldn't be readable back.

## Overlay 2: `apply_migration.py` postcondition-assertion verification

**Why it's an overlay:** Per [ADR 0055](../../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5, every migration must declare its expected end-state via `-- Postcondition-Assertions:` block. The wrapper runs the assertions automatically; this overlay verifies the block is present and *sensibly* matches the body.

### Procedure

For every new migration (`product/seed-graph/migrations/NNNN_*.sql`):

1. Read the contract header at the top of the migration. Specifically the `-- Postcondition-Assertions:` block.

2. Each assertion line should be:

   ```
   --   <SELECT returning one integer> :: <expected integer>
   ```

3. Verify:
   - **Block exists.** Per ADR 0055's pre-S-0094 grandfather clause, pre-S-0094 migrations may lack the block; new migrations must include it. Missing block on a new migration is `Required`.
   - **Assertions sensibly verify the body's effect.** A migration that inserts N rows should assert the row count rose by N. A migration that deletes M rows should assert the count fell by M. A migration that updates a column should assert the value distribution changed as expected.
   - **Assertions are not overspecified.** Asserting every row's exact data is fragile (any test fixture change breaks every assertion); assert row counts and key-aggregate values, not row contents.
   - **Assertion grammar is valid.** The wrapper parses the grammar; an unparseable line surfaces as exit-2 from the wrapper. The overlay double-checks at review time.

### Pass / Fail / N-A

- **PASS:** every new migration has a `-- Postcondition-Assertions:` block with sensible, non-overspecified assertions covering the body's intended effect.
- **FAIL:** missing block on a new migration; assertions don't match the body (e.g., body inserts 5 rows, assertion checks for 10); overspecified assertions.
- **N-A:** the change does not include any new migration.

### Failure examples to catch

- A migration that adds an index but its assertion checks row count — useless because the body doesn't change row counts.
- A migration with `-- Postcondition-Assertions:` followed by a SELECT that returns a non-integer (the wrapper rejects this; the review catches it pre-commit).
- A "this migration is a no-op rollback marker" migration with NO assertion block — pre-S-0094 grandfather clause may apply; new migrations should at minimum assert "the body changed nothing" (row count delta = 0).

## Overlay 3: MemPalace + KG PII discipline

**Why it's an overlay:** The MemPalace substrate and the KG storage layer are project-internal but accessible to anyone who reads the repo or runs the MCP server. Pre-OSS-flip this was a closed loop; post-OSS-flip ([ADR 0065 (product)](../../../product/adr/0065-oss-pivot-and-byok-disposition.md) S-0130) the repo is public — MemPalace content under `engine/session/archive/*.json` and any diary/drawer content that ends up committed is world-readable.

### Procedure

For every change that writes to MemPalace or the KG:

1. **Drawer writes** (`mempalace_add_drawer`):
   - Does the content include any password, token, API key, or other credential? `Critical`.
   - Does the content include PII other than the maintainer's self-reference? `Required` to redact (per the S-0130 sweep — 141 files were redacted from `/Users/shanekidd/` to `~/`; the same posture applies here).
   - Does the content include the user's real name in a context where the maintainer-tag would suffice?

2. **Diary writes** (`mempalace_diary_write`):
   - AAAK-compressed form per [ADR 0056](../../../engine/adr/0056-mempalace-mechanical-adoption-checks.md) — does the entry follow the format?
   - Free-text diary entries should follow the same redaction discipline as drawers.

3. **KG writes** (`mempalace_kg_add`):
   - Does the entity / claim include PII? Same redaction discipline.

4. **Session archive** (`engine/session/archive/S-NNNN.json`):
   - The archive's `outcome_summary` field is committed. Apply the same discipline.
   - The `working_on` field is committed. Same.

### Pass / Fail / N-A

- **PASS:** no credentials, no PII beyond maintainer self-reference, no real-name leaks.
- **FAIL:** any credential in any drawer / diary / KG entity / archive field; any PII without redaction.
- **N-A:** the change does not write to MemPalace, the KG, or the session archive.

### Failure examples to catch

- A diary entry that quotes a Supabase service-role key during a debugging session — `Critical`; rotate the key immediately.
- A drawer that names a non-maintainer user by full name in a context where the role-name would suffice.
- An `outcome_summary` field that includes a raw API endpoint URL with credentials embedded.

## Overlay 4 (forward-pointer): Phase 6+ privacy ADR

When a privacy ADR lands (Phase 6+ surface), this card gains a fourth overlay for the project's privacy posture (data retention, deletion guarantees, GDPR / CCPA / Apple App Store privacy-label posture). Pre-Phase-6 N-A.

## How to use this card

Run the overlays *in addition* to the OWASP walk in [`owasp-checklist.md`](owasp-checklist.md). Mark each overlay PASS / FAIL / N-A in the report's "Paideia overlay grid" section. The overlays often correlate with OWASP items (Overlay 1 ↔ A01; Overlay 2 ↔ A08; Overlay 3 ↔ A02) but are distinct — the OWASP item is the failure mode in general; the overlay is the Paideia-specific instantiation.

## See also

- [`SKILL.md`](SKILL.md) — `/security-review` recipe.
- [`owasp-checklist.md`](owasp-checklist.md) — OWASP Top 10 grid.
- [`../review/anti-rationalization.md`](../review/anti-rationalization.md) — shared anti-rationalization table.
- [ADR 0055](../../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) — postcondition-assertion contract (Overlay 2).
- [ADR 0056](../../../engine/adr/0056-mempalace-mechanical-adoption-checks.md) — MemPalace mechanical adoption (Overlay 3 context).
- [ADR 0065 (product)](../../../product/adr/0065-oss-pivot-and-byok-disposition.md) — OSS flip context (why Overlay 3 matters now).
- [ADR 0071](../../../engine/adr/0071-project-wired-security-review-skill.md) — citable contract.
