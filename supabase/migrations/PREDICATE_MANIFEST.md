# supabase/migrations/PREDICATE_MANIFEST.md — Canonical edge-type registry

> **Placeholder created S-0001. Fleshed out in Phase 4** when graph construction begins. Adding a new predicate is a CHANGELOG-tracked material change; the same session that introduces the predicate must update this file.

## Why this file exists

Every edge in the Paideia graph carries a `type` field naming its predicate (e.g., `prerequisite`, `enables`). Free-form predicates accumulate schema drift silently across sessions — different sessions inventing equivalent-but-not-identical names (`is_prerequisite_for` vs `prerequisite`) until the audit at session N discovers 50+ undeclared variants.

This file is the canonical registry. `tools/validate.py`'s graph-audit extension point (per [`adr/0016-graph-construction-needs-live-validation.md`](../../adr/0016-graph-construction-needs-live-validation.md)) reads this file and **soft-warns on any edge whose type is not listed here**. New predicates are introduced by:

1. Adding an entry to this file in the same session that uses the new predicate.
2. Recording the addition under "Added" in CHANGELOG.md `[Unreleased]`.
3. Naming the predicate's domain (what kinds of nodes it connects) and range (what relationship it asserts).

The audit catches drift; this manifest closes the loop by making the catch's resolution unambiguous.

## Predicate registry

(Empty until Phase 4. The first entries land when Phase 5's epistemology session ships the first seed migration.)

| Predicate | Domain | Range | Cardinality | Description |
|---|---|---|---|---|
| *(none yet)* | | | | |

## Reserved-but-unused predicates

(Predicates considered during design but not yet used in any seed migration. If never used, they should be removed from this list at the next health check.)

| Predicate | Source ADR | Status |
|---|---|---|
| *(none yet)* | | |

---

*Last updated: 2026-04-29 (S-0001 placeholder created)*
