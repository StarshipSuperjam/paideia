"""Predicate runner for routine-mode target files (`auto_target.json`).

Layer 1 contract per ADR 0051. The runner reads a target file, walks each
task's criteria, and reports per-criterion pass/fail. Routine-mode boot
calls this to decide which task is eligible (any task whose criteria are
not yet all-passing AND whose ``depends_on`` are all complete) and to
detect target-met (every task is `complete` AND its criteria still pass).

Five criterion types ship at landing. Adding a new type is one function
in :data:`CRITERION_TYPES` plus a test. The ``predicate`` type is the
explicit escape hatch for criteria that don't fit the four named types
— register a callable in :data:`PREDICATE_REGISTRY` alongside its test.

Inputs
------
- ``--target`` (default ``engine/session/auto_target.json``): path to
  the target file.
- ``--task-id`` (optional): restrict checks to one task; useful for
  routine-mode boot when the dispatcher wants to confirm a single
  task's eligibility / completion.
- ``--json`` (optional): emit machine-readable output instead of the
  human-readable default.

Output (default mode)
---------------------
Per task: ``[mark] <id>  <name>  (status=<file_status>)`` where mark is
``✓`` if every criterion passed, else ``✗``. Each criterion appears
indented below: ``  [mark] <type>  — <detail>``.

Output (``--json``)
-------------------
List of objects, one per task:
``{"id", "name", "status", "all_passed", "criteria": [{"type", "passed",
"detail"}, ...]}``.

Exit codes
----------
- ``0`` — every checked task's criteria all passed.
- ``1`` — at least one task has a failing criterion (or the target
  file is missing / malformed, or the requested ``--task-id`` doesn't
  exist).

Out of scope
------------
- No mutation of the target file. Status writes happen in the boot
  procedure of session-build-lifecycle.md, not here.
- No dependency walk. Whether a task is *eligible* (depends_on all
  complete) is decided by the boot procedure / dispatcher, not by this
  tool. This tool only reports per-task criterion truth.
- No remediation. A failing criterion is a fact, not an alarm.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[2]

# Local helper at engine/tools/scrub_env.py — see ADR 0045.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrub_env import scrubbed_env  # noqa: E402


# ---------------------------------------------------------------------------
# Predicate registry — escape hatch for non-standard criteria
# ---------------------------------------------------------------------------

PREDICATE_REGISTRY: dict[str, Callable[..., bool]] = {}


def register_predicate(
    name: str,
) -> Callable[[Callable[..., bool]], Callable[..., bool]]:
    """Decorator: register a callable as a named predicate.

    The callable receives criterion ``params`` as kwargs and must return
    a truthy/falsy value. Place definitions in this module so cold-context
    readers can find them; tests live in test_check_target.py.
    """

    def decorator(fn: Callable[..., bool]) -> Callable[..., bool]:
        PREDICATE_REGISTRY[name] = fn
        return fn

    return decorator


# ---------------------------------------------------------------------------
# Criterion runners
# ---------------------------------------------------------------------------


def _check_migration_applied(*, id: str, **_: Any) -> tuple[bool, str]:
    """Verify a migration id is recorded as applied."""
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        return False, "SUPABASE_DB_URL not set; cannot verify"
    try:
        import psycopg  # type: ignore[import-not-found,unused-ignore]
    except ImportError:
        return False, "psycopg not available; cannot verify"
    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = %s",
                    (id,),
                )
                if cur.fetchone() is None:
                    return False, f"migration {id} not in schema_migrations"
                return True, f"migration {id} applied"
    except Exception as exc:
        return False, f"db query failed: {exc!s}"


def _check_validate_passes(**_: Any) -> tuple[bool, str]:
    """Run validate.py; pass iff zero hard-fails.

    validate.py uses three exit codes: 0 (clean), 1 (soft-warns only), 2 (hard
    fails). Per auto_target.schema.md (`validate_passes` section), soft-warns
    are advisory and do not fail the criterion. So this criterion treats exit
    0 and exit 1 as pass; exit 2 (or any other failure) is fail.
    """
    cmd = [sys.executable, str(REPO_ROOT / "engine/tools/validate.py")]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, env=scrubbed_env(), timeout=300
        )
    except subprocess.TimeoutExpired:
        return False, "validate.py timeout"
    except FileNotFoundError as exc:
        return False, f"validate.py not runnable: {exc!s}"
    if result.returncode in (0, 1):
        return True, f"validate.py exit {result.returncode} (no hard-fails)"
    snippet = (result.stderr or result.stdout).strip().splitlines()[-1:]
    return (
        False,
        f"validate.py exit {result.returncode}: {snippet[0] if snippet else '<no stderr>'}",
    )


_STATUS_RE = re.compile(r"\*\*Status:\*\*\s*(.+?)\s*$", re.MULTILINE)


def _check_adr_status(*, id: str, status: str, **_: Any) -> tuple[bool, str]:
    """Verify an ADR's frontmatter Status field matches expected."""
    matches: list[Path] = []
    for adr_dir in (REPO_ROOT / "engine" / "adr", REPO_ROOT / "product" / "adr"):
        if not adr_dir.exists():
            continue
        matches.extend(sorted(adr_dir.glob(f"{id}-*.md")))
    if not matches:
        return False, f"no ADR file found for id {id}"
    if len(matches) > 1:
        return False, f"multiple ADR files match id {id}: {[p.name for p in matches]}"
    text = matches[0].read_text()
    m = _STATUS_RE.search(text)
    if not m:
        return False, f"ADR {id} has no Status line"
    actual = m.group(1).strip()
    if status == "*":
        return bool(actual), f"Status: {actual}"
    if actual.lower() == status.lower():
        return True, f"Status: {actual}"
    return False, f"Status: {actual} (expected {status})"


def _check_file_exists(*, path: str, **_: Any) -> tuple[bool, str]:
    full = REPO_ROOT / path
    if full.exists():
        return True, f"exists: {path}"
    return False, f"not found: {path}"


def _check_predicate(
    *, name: str, params: dict[str, Any] | None = None, **_: Any
) -> tuple[bool, str]:
    if name not in PREDICATE_REGISTRY:
        return False, f"predicate '{name}' not registered"
    try:
        result = PREDICATE_REGISTRY[name](**(params or {}))
    except Exception as exc:
        return False, f"predicate '{name}' raised: {exc!s}"
    if result:
        return True, f"predicate '{name}' returned truthy"
    return False, f"predicate '{name}' returned falsy"


CRITERION_TYPES: dict[str, Callable[..., tuple[bool, str]]] = {
    "migration_applied": _check_migration_applied,
    "validate_passes": _check_validate_passes,
    "adr_status": _check_adr_status,
    "file_exists": _check_file_exists,
    "predicate": _check_predicate,
}


# ---------------------------------------------------------------------------
# Top-level interface
# ---------------------------------------------------------------------------


@dataclass
class CriterionResult:
    type: str
    passed: bool
    detail: str


@dataclass
class TaskResult:
    id: str
    name: str
    status: str
    criteria_results: list[CriterionResult]
    all_passed: bool


def load_target(path: Path) -> dict[str, Any]:
    """Load a target file. Caller handles FileNotFoundError / json errors."""
    data: dict[str, Any] = json.loads(path.read_text())
    return data


def check_criterion(criterion: dict[str, Any]) -> CriterionResult:
    ctype = criterion.get("type")
    if not isinstance(ctype, str):
        return CriterionResult(
            type="<missing>", passed=False, detail="criterion missing 'type' field"
        )
    runner = CRITERION_TYPES.get(ctype)
    if runner is None:
        return CriterionResult(
            type=ctype, passed=False, detail=f"unknown criterion type: {ctype}"
        )
    kwargs = {k: v for k, v in criterion.items() if k != "type"}
    try:
        passed, detail = runner(**kwargs)
    except TypeError as exc:
        return CriterionResult(
            type=ctype, passed=False, detail=f"criterion call failed: {exc!s}"
        )
    return CriterionResult(type=ctype, passed=passed, detail=detail)


def check_task(task: dict[str, Any]) -> TaskResult:
    criteria = task.get("criteria", [])
    results = [check_criterion(c) for c in criteria]
    # Empty criteria list → not auto-completable. Authoring decision per ADR 0051.
    all_passed = bool(results) and all(r.passed for r in results)
    return TaskResult(
        id=task.get("id", "<missing>"),
        name=task.get("name", ""),
        status=task.get("status", ""),
        criteria_results=results,
        all_passed=all_passed,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    # Walk-up .env loader (per Issue #8 / S-0049). Routine sessions
    # launch in worktrees that do not have a local .env; this walks up
    # to the main repo's .env so SUPABASE_DB_URL becomes visible to
    # `_check_migration_applied`. Does NOT override pre-set values, so
    # explicit `SUPABASE_DB_URL=... python3 ...` invocations still win.
    from load_env import load_dotenv_walk_up

    load_dotenv_walk_up()

    ap = argparse.ArgumentParser(description="Check auto_target.json criteria")
    ap.add_argument(
        "--target",
        default=str(REPO_ROOT / "engine" / "session" / "auto_target.json"),
        help="Path to auto_target.json",
    )
    ap.add_argument("--task-id", help="Restrict check to this task")
    ap.add_argument("--json", action="store_true", help="Emit JSON output")
    args = ap.parse_args(argv)

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"target file not found: {target_path}", file=sys.stderr)
        return 1

    try:
        target = load_target(target_path)
    except json.JSONDecodeError as exc:
        print(f"target file malformed: {exc!s}", file=sys.stderr)
        return 1

    tasks = target.get("tasks", [])
    if args.task_id:
        tasks = [t for t in tasks if t.get("id") == args.task_id]
        if not tasks:
            print(f"task id not found: {args.task_id}", file=sys.stderr)
            return 1

    results = [check_task(t) for t in tasks]

    if args.json:
        payload = [
            {
                "id": r.id,
                "name": r.name,
                "status": r.status,
                "all_passed": r.all_passed,
                "criteria": [
                    {"type": c.type, "passed": c.passed, "detail": c.detail}
                    for c in r.criteria_results
                ],
            }
            for r in results
        ]
        print(json.dumps(payload, indent=2))
    else:
        for r in results:
            mark = "PASS" if r.all_passed else "FAIL"
            print(f"[{mark}] {r.id}  {r.name}  (status={r.status})")
            for c in r.criteria_results:
                cmark = "  PASS" if c.passed else "  FAIL"
                detail = f"  — {c.detail}" if c.detail else ""
                print(f"  [{cmark.strip()}] {c.type}{detail}")

    return 0 if all(r.all_passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
