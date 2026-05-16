"""Thin CLI entrypoint for the engine-memory transcript capture hook.

Invoked from ``engine/tools/hooks/engine-memory-capture.sh`` as
``python -m engine.memory.capture {stop,precompact}``. The bash hook
needs a stable Python entrypoint that doesn't change as
``transcript_capture.py`` evolves — this module is the seam.

The harness pipes a JSON event to stdin; ``transcript_capture.capture``
reads it directly. Unknown arg defaults to ``"stop"`` (the safer
default — under-firing the precompact watermark is preferable to
over-firing the stop watermark).
"""

from __future__ import annotations

import sys

from engine.memory import transcript_capture


def main(argv: list[str] | None = None) -> int:
    """Dispatch to ``transcript_capture.capture`` based on argv[1]."""
    if argv is None:
        argv = sys.argv
    hook_kind = argv[1] if len(argv) > 1 else "stop"
    if hook_kind not in ("stop", "precompact"):
        # Unknown hook kind — no-op exit 0 rather than raising. The hook
        # never blocks the harness.
        return 0
    return transcript_capture.capture(hook_kind)  # type: ignore[arg-type]


if __name__ == "__main__":
    sys.exit(main())
