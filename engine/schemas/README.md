# engine/schemas/

> JSON Schema definitions for engine-side validated content. Schemas are loaded by `engine/tools/validate.py` and other tools at commit-time or run-time.

## Contents

- [`changelog-entry.schema.json`](changelog-entry.schema.json) — per-session changelog entry frontmatter validation. Consumer: `engine/tools/changelog_aggregate.py` (at validate-only mode + at parse time), `engine/tools/validate.py` (`check_changelog_entries`). Per [ADR 0092](../adr/0092-per-session-changelog-directory.md).

## Discipline

- **Draft 2020-12** is the JSON Schema dialect.
- **`$id`** uses the project's GitHub URL as namespace.
- **`additionalProperties: false`** is the default for object schemas (frontmatter is closed; explicit fields only).
- New schemas land here when their content surface warrants reusable mechanical validation. If a schema is only consumed by one tool, inline definitions in that tool are acceptable; promote to `engine/schemas/` when ≥2 consumers or when external tools (linters, IDEs) benefit from a standalone file.

## Related

- `engine/session/archive/` — per-session structured archives validated by `audit_archive_structured_fields.py` against required-field allowlist (in-script, not a JSON Schema). Promotion-to-schema candidate when the required-field set stabilizes.
- `engine/changelog/` — per-session changelog entries; frontmatter validated against `changelog-entry.schema.json`.
