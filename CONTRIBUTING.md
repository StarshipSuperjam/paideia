# Contributing to Paideia

Paideia is a personal project under the Apache License 2.0. The maintainer is the sole regular contributor. Outside contributions are welcome but accepted at the maintainer's discretion — there is no SLA on response time, no commitment to merge any given change, and no obligation to follow contributor-suggested direction.

If you fork Paideia for App Store distribution, please rebrand the product. The "Paideia" name and brand identity are not Apache-licensed and remain associated with this repository.

## How the project is built

Paideia is built primarily by AI sessions running under [Claude Code](https://claude.com/claude-code). The session protocol is the contribution unit — each session claims a slot, does scoped work, lands an atomic set of commits, and pushes. See:

- [`CLAUDE.md`](CLAUDE.md) — AI orientation; auto-loaded at every session start. The startup ceremony, three session modes (exploration / build / routine), standing rules, and budget guidance live here.
- [`engine/operations/README.md`](engine/operations/README.md) — index of procedural docs. Read [`engine/operations/session-build-lifecycle.md`](engine/operations/session-build-lifecycle.md) and [`engine/operations/session-shutdown-sequence.md`](engine/operations/session-shutdown-sequence.md) for the build-session lifecycle.
- [`engine/STATE.md`](engine/STATE.md) — current phase, next session's work item.
- [`engine/changelog/`](engine/changelog/) — per-session changelog directory per [ADR 0092](engine/adr/0092-per-session-changelog-directory.md); one entry per material-change session. Aggregate views via `python3 engine/tools/changelog_aggregate.py`. Historical pre-S-0198 monolithic file preserved at [`engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md`](engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md).
- [`engine/adr/README.md`](engine/adr/README.md) and [`product/adr/README.md`](product/adr/README.md) — the decisions that shape the project (engine-side vs. product-side per [ADR 0037](engine/adr/0037-engine-product-wall-and-changelog-rename.md)).

## Code style and gates

`engine/tools/validate.py` runs in the pre-commit hook. Hard-fails block the commit; soft-warns are recorded in `engine/session/current.json`'s `outcome_summary` for cross-session telemetry. See [`engine/operations/tools-validate-interpretation.md`](engine/operations/tools-validate-interpretation.md).

Python code is linted with `ruff`, type-checked with `mypy`, tested with `pytest`. The project venv is managed by `uv` — `uv sync` is the canonical install path. See [`engine/operations/dependency-discipline.md`](engine/operations/dependency-discipline.md).

## Commit conventions

[Conventional Commits](https://www.conventionalcommits.org/). Types in active use: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`, `perf`. Eager-claim session commits use `chore(session):`.

## Reporting issues

Open a GitHub Issue with one of the standard labels (`bug`, `enhancement`, `tech-debt`, `cleanup`, `documentation`, `question`, `health-check-finding`, `upstream`). For security vulnerabilities, see [SECURITY.md](SECURITY.md) — use the GitHub private vulnerability report channel.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Reports of conduct violations route through the same GitHub security-advisory channel as vulnerabilities.
