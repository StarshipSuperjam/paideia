# `auto_target.json` schema

> Reference for the target file consumed by routine-mode sessions per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md). Authored by master plan sessions (interactive); read by routine sessions (unattended) at every boot.
>
> Single instance lives at `engine/session/auto_target.json`. Its presence is the routine-mode signal — absence falls back to the standard interactive boot per [`engine/operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md).

## Top-level fields

| Field | Type | Required | Description |
|---|---|---|---|
| `target_id` | string | yes | Unique identifier (e.g., `T-PHASE-5`, `T-S0044-ADOPTION`). Surfaced in HANDOFF entries and outcome summaries. |
| `goal` | string | yes | One-line plain-English goal. Read by humans; routine sessions surface it in log lines. |
| `paused` | bool | yes | When `true`, routine sessions exit on boot without claiming a slot. Toggle to halt the loop without disabling the routine in the Claude Code UI. |
| `max_sessions` | int | yes | Hard ceiling on routine-mode sessions per `target_id`. Counted from `engine/session/archive/` matches. Reached → halt with HANDOFF, regardless of progress. |
| `max_wall_clock_hours` | int | no | Advisory only; not mechanically enforced. Wall-clock attribution across sessions is harder than session count and not worth the implementation surface. Documented as a hint to the user. |
| `tasks` | list[Task] | yes | Ordered list of work items. Order matters only for tie-breaking when multiple tasks are simultaneously eligible. Dependencies are explicit via `depends_on`. |

## Task fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Task identifier unique within this target (e.g., `P5-01`, `T1`). Referenced by `depends_on` and HANDOFF entries. |
| `name` | string | yes | One-line plain-English task name. |
| `depends_on` | list[task_id] | yes | List of task ids that must be `complete` before this task is eligible. Empty list = no dependencies. Cycles are not allowed (ill-formed; predicate runner refuses to load). |
| `criteria` | list[Criterion] | yes | All criteria must pass for the task to transition to `complete`. Empty list is allowed but unusual (the task can never auto-complete). |
| `scope_lock` | object | yes | `{allowed_paths: [glob, ...]}`. The active task's allowed_paths are unioned with the operational allowlist (per ADR 0051) at commit time. Glob format is git-style (e.g., `engine/migrations/0042_*`, `build_plan/P_5_subdomains/**/*.md`). |
| `status` | string | yes | One of `pending` \| `in_progress` \| `complete` \| `blocked`. Initial state is `pending`. Routine sessions write status changes; the master-plan-integrity check (per ADR 0051) hard-fails routine commits that diff any non-status keys. |
| `blocked_reason` | string | no | Required when `status == blocked`; otherwise omitted. Free-form prose; surfaces in HANDOFF entries. |

## Criterion types

Each criterion is an object with a `type` field plus type-specific parameters. The runner is [`engine/tools/check_target.py`](../tools/check_target.py) — adding a new type is one Python function plus a registry entry plus a test. Five types ship with ADR 0051.

### `migration_applied`

Checks Supabase migration history for an applied id.

```json
{"type": "migration_applied", "id": "0042_epistemology_concepts"}
```

Behavior: queries `supabase_migrations.schema_migrations` (via `SUPABASE_DB_URL` if set). When `SUPABASE_DB_URL` is absent or the query fails (network, auth, schema not yet provisioned), the criterion reports "cannot verify" — treated as not-satisfied rather than crashing the predicate runner. The session itself surfaces the inability via HANDOFF if the criterion is load-bearing for its task.

### `validate_passes`

Runs `validate.py`; passes iff zero hard-fails.

```json
{"type": "validate_passes"}
```

Optional parameter: `subset: <string>` to scope the validator to a check group (e.g., `migrations`, `cascade`, `mempalace`). Default is the full default-mode run. Soft-warns are advisory and do not fail the criterion (per ADR 0042's lifecycle — soft-warns surface across sessions, not within one).

### `adr_status`

Checks ADR file frontmatter for the configured `Status` value.

```json
{"type": "adr_status", "id": "0051", "status": "Accepted"}
```

Behavior: reads `engine/adr/<id>-*.md` or `product/adr/<id>-*.md` (whichever exists; an ADR id is unique across the partition per ADR 0037). Whitespace-tolerant parse of the `- **Status:**` line. Wildcards: `status: "*"` accepts any non-empty value.

### `file_exists`

Checks a path exists relative to repo root.

```json
{"type": "file_exists", "path": "engine/build_readiness/phase_5.md"}
```

Behavior: literal path check. Globs are not expanded (criterion is satisfied by existence of the exact path). For glob-shaped checks, use `predicate`.

### `predicate`

Runs a named callable from a registry.

```json
{"type": "predicate", "name": "seed_concepts_count_at_least_n", "params": {"n": 50}}
```

Behavior: looks up `name` in `check_target.PREDICATE_REGISTRY` (a dict mapping name → callable); calls it with `params` as kwargs; expects the callable to return `bool`. The callable lives in `check_target.py` alongside its tests. Adding a new predicate is the project's standard escape hatch for criteria that don't fit the four named types.

## Complete example — Phase 5 sketch

```json
{
  "target_id": "T-PHASE-5",
  "goal": "Phase 5 seed graph build — 8 subdomain seeds + cross-bridges + closeout",
  "paused": false,
  "max_sessions": 14,
  "max_wall_clock_hours": 48,
  "tasks": [
    {
      "id": "P5-01",
      "name": "Epistemology seed",
      "depends_on": [],
      "criteria": [
        {"type": "migration_applied", "id": "0042_epistemology_concepts"},
        {"type": "validate_passes"}
      ],
      "scope_lock": {
        "allowed_paths": [
          "engine/migrations/0042_*",
          "build_plan/P_5_subdomains/epistemology.md"
        ]
      },
      "status": "pending"
    },
    {
      "id": "P5-09",
      "name": "Cross-bridges between subdomains",
      "depends_on": ["P5-01", "P5-02", "P5-03", "P5-04", "P5-05", "P5-06", "P5-07", "P5-08"],
      "criteria": [
        {"type": "validate_passes"},
        {"type": "predicate", "name": "all_subdomains_bridged", "params": {}}
      ],
      "scope_lock": {
        "allowed_paths": ["engine/migrations/0050_cross_bridges*"]
      },
      "status": "pending"
    },
    {
      "id": "P5-10",
      "name": "Phase 5 closeout ADR + STATE.md update",
      "depends_on": ["P5-09"],
      "criteria": [
        {"type": "adr_status", "id": "0052", "status": "Accepted"},
        {"type": "file_exists", "path": "engine/build_readiness/phase_5_closeout.md"}
      ],
      "scope_lock": {
        "allowed_paths": [
          "engine/adr/0052-*",
          "engine/build_readiness/phase_5_closeout.md",
          "engine/STATE.md"
        ]
      },
      "status": "pending"
    }
  ]
}
```

## Authoring conventions

- **Author the file in a master plan session, not a routine session.** Routine sessions are forbidden from editing it (other than status fields) by the master-plan-integrity hook.
- **Order tasks by intended execution order.** Dependencies handle the hard sequencing; ordering within an eligibility tier is preserved as authored, so place earlier-in-mind tasks first.
- **Scope_lock paths should be tight.** Narrower allowed_paths = stronger anti-rogue guarantee. Don't write `engine/**/*.py` if the work touches three specific files; list the three.
- **Break work into session-sized tasks.** A task should fit in one routine session (~hour, ~1 hour wall-clock). If a task is too large, split it; don't rely on multiple routine sessions to incrementally complete one task.
- **Criteria must be objective and runnable.** Subjective criteria ("the design feels right") belong in the master plan session (interactive), not in the target file. The target file describes what a routine session can mechanically verify.

## Operational notes

- The file is committed to git. It evolves only via interactive master plan sessions (initial author + revision-on-HANDOFF) and via routine-session status writes (which the master-plan-integrity check ratchets to status fields only).
- When the target is fully complete, routine sessions still fire on cadence and exit cleanly within seconds. Cost is negligible. The user can disable the routine in the UI between phases or just leave it; the next master plan session that authors a new target picks up.
- Multiple targets are not simultaneously active. Replacing a target is: complete or archive the current one (delete the file or set every task to `complete`/`blocked`), then author the new target. The schema does not support stacked targets.
