"""Interactive ``.env`` setup helper for fresh clones.

Reads ``.env.example`` to determine the canonical key set and per-key
comments. Reads ``.env`` (if present) to preserve existing values. For
each canonical key that is missing or empty, prompts the user with the
comments from ``.env.example`` and any per-key guidance.
``SUPABASE_DB_URL`` gets a real ``psycopg.connect()`` validation step so
the password is verified at setup time rather than discovered later in
a Phase 5 routine fire.

Idempotent: re-running when all values are populated prints "all set"
and exits.

Atomic: writes ``.env.tmp`` then ``rename`` (POSIX atomic) so a crash
mid-write cannot corrupt ``.env``.

Per Issue #7 (S-0048) — replaces "user manually pastes the URL into
.env once, ever" with a guided one-time setup that validates as it
goes. Subsequent routine fires read the populated ``.env`` directly;
no per-session prompting.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable

ENV_PATH = Path(".env")
ENV_EXAMPLE_PATH = Path(".env.example")

ValidatorResult = tuple[bool, str]
Validator = Callable[[str], ValidatorResult]


def _validate_supabase_db_url(value: str) -> ValidatorResult:
    """Validate by attempting a real Postgres connection + ``SELECT version()``."""
    if not value.strip():
        return False, "empty input"
    value = value.strip()
    if not value.startswith("postgresql://"):
        return False, "must start with postgresql://"
    # psycopg is in the venv (per engine/tools/requirements.txt) but may
    # be absent from system Python. The pre-commit hook's mypy subprocess
    # uses whichever interpreter is on PATH; under venv it finds psycopg
    # (so the ignore is "unused"), under system Python it can't (so the
    # ignore IS used). The `unused-ignore` ignore-code suppresses mypy's
    # complaint in the venv case while keeping `import-not-found` quiet
    # in the system-Python case.
    try:
        import psycopg  # type: ignore[import-not-found, unused-ignore]
    except ImportError:
        return True, "(skipping connection check — psycopg not installed)"
    try:
        with psycopg.connect(value, connect_timeout=10) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                row = cur.fetchone()
                version = row[0] if row else "<unknown>"
        return True, f"connection valid (server: {version[:70]}...)"
    except Exception as exc:  # noqa: BLE001  (broad-except is intentional;
        # any psycopg failure is a clear validation no — we don't need to
        # discriminate further at the prompt level)
        return False, f"connection failed: {exc}"


VALIDATORS: dict[str, Validator] = {
    "SUPABASE_DB_URL": _validate_supabase_db_url,
}


def parse_env_example(text: str) -> list[tuple[str, list[str]]]:
    """Parse ``.env.example``.

    Returns ``[(KEY, comments_above)]`` preserving order and the
    blank-line-separated comment block above each key.
    """
    blocks: list[tuple[str, list[str]]] = []
    current_comments: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "":
            current_comments.append(line)
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            blocks.append((key, current_comments))
            current_comments = []
    return blocks


def parse_env(text: str) -> dict[str, str]:
    """Parse ``.env`` — return ``KEY -> value`` dict (comments ignored)."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "":
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def write_env_atomic(target: Path, blocks: list[tuple[str, list[str], str]]) -> None:
    """Write ``.env`` from ``(key, comments, value)`` tuples atomically.

    The temporary file lives next to the target and is renamed in place
    under POSIX atomicity guarantees. Permissions are set to 0600
    (owner read/write only) so the file's secrets cannot be read by
    other users on a multi-user host.
    """
    lines: list[str] = []
    for key, comments, value in blocks:
        if comments:
            lines.extend(comments)
        lines.append(f"{key}={value}")
    content = "\n".join(lines) + "\n"
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content)
    os.chmod(tmp, 0o600)
    tmp.rename(target)


def _prompt_for_value(key: str, comments: list[str]) -> str:
    """Prompt the user for ``KEY``; loop on validation failure."""
    print()
    print(f"=== {key} ===")
    for c in comments:
        print(c)
    while True:
        value = input(f"{key}: ").strip()
        validator = VALIDATORS.get(key)
        if validator is None:
            return value
        ok, message = validator(value)
        if ok:
            if message:
                print(f"  OK: {message}")
            return value
        print(f"  FAIL: {message}")
        retry = input("  Retry? [Y/n] ").strip().lower()
        if retry == "n":
            print(
                "  Skipping. .env will keep this key empty; re-run setup_env.py later."
            )
            return ""


def determine_blocks(
    example_blocks: list[tuple[str, list[str]]],
    existing: dict[str, str],
    prompt_fn: Callable[[str, list[str]], str] = _prompt_for_value,
) -> tuple[list[tuple[str, list[str], str]], bool]:
    """Walk canonical keys; assemble ``(key, comments, value)`` tuples.

    Returns ``(blocks, prompted_any)`` so the caller can short-circuit
    the file-write if everything was already populated.
    """
    final_blocks: list[tuple[str, list[str], str]] = []
    prompted_any = False
    for key, comments in example_blocks:
        existing_value = existing.get(key, "")
        if existing_value:
            final_blocks.append((key, comments, existing_value))
        else:
            prompted_any = True
            value = prompt_fn(key, comments)
            final_blocks.append((key, comments, value))
    return final_blocks, prompted_any


def main() -> int:
    if not ENV_EXAMPLE_PATH.is_file():
        print(
            "[setup_env] .env.example not found in current directory.",
            file=sys.stderr,
        )
        print("  Run from the repo root.", file=sys.stderr)
        return 2

    example_blocks = parse_env_example(ENV_EXAMPLE_PATH.read_text())
    existing: dict[str, str] = {}
    if ENV_PATH.is_file():
        existing = parse_env(ENV_PATH.read_text())

    final_blocks, prompted_any = determine_blocks(example_blocks, existing)
    if not prompted_any:
        print("[setup_env] All canonical keys already populated. Nothing to do.")
        return 0

    write_env_atomic(ENV_PATH, final_blocks)
    print(f"\n[setup_env] Wrote {ENV_PATH.resolve()}")
    print("  Permissions: 0600 (owner read/write only)")
    print("  Re-run setup_env.py at any time to add missing keys.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
