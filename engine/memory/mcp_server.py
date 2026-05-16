#!/usr/bin/env python3
"""Engine-memory MCP server (skeleton; tools wired across S-0190–S-0192).

Per ADR 0091, the substrate exposes exactly six MCP tools. None are
wired at S-0189; this module ships the JSON-RPC stdio scaffolding that
S-0190 (capture surface), S-0191 (read surface + verification harness),
and S-0192 (MCP swap) hang tool handlers off.

Pattern mirrors mempalace's ``mcp_server.py`` (raw JSON-RPC over stdio,
no third-party MCP SDK dependency). The substrate ships inside the
``engine/`` subtree and uses only the Python standard library plus the
sibling modules in this package — no PyPI install required for the MCP
layer (the chromadb / mempalace deps stay pinned in pyproject.toml only
until S-0193 for the export-and-replay path).

Invocation::

    python -m engine.memory.mcp_server

The S-0192 ``.mcp.json`` rewire points the ``engine_memory`` server
entry at this module.
"""

from __future__ import annotations

# --- MCP stdio protection ----------------------------------------------------
# JSON-RPC over stdio requires stdout to carry only valid JSON-RPC. Some
# transitive imports may print banners or warnings to stdout, which would
# corrupt the protocol. Redirect stdout → stderr at both Python and FD level
# before any heavy import (currently the package has no such imports, but the
# discipline carries forward as S-0190+ tool wiring brings in more deps).
import os
import sys

_REAL_STDOUT = sys.stdout
_REAL_STDOUT_FD: int | None = None
try:
    _REAL_STDOUT_FD = os.dup(1)
    os.dup2(2, 1)
except (OSError, AttributeError):
    pass
sys.stdout = sys.stderr

import json  # noqa: E402
import logging  # noqa: E402
from typing import Any  # noqa: E402

from engine.memory.connection import get_conn  # noqa: E402

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "engine_memory"
SERVER_VERSION = "0.1.0"

logger = logging.getLogger(SERVER_NAME)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Tool registry. Empty at S-0189; populated by S-0190+ wiring.
# Shape: {tool_name: {"input_schema": {...}, "handler": callable}}
TOOLS: dict[str, dict[str, Any]] = {}


def _restore_stdout() -> None:
    """Restore real stdout for MCP JSON-RPC output."""
    global _REAL_STDOUT, _REAL_STDOUT_FD
    if _REAL_STDOUT_FD is not None:
        try:
            os.dup2(_REAL_STDOUT_FD, 1)
            os.close(_REAL_STDOUT_FD)
        except OSError:
            pass
        _REAL_STDOUT_FD = None
    sys.stdout = _REAL_STDOUT


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    """Dispatch a JSON-RPC request to its handler.

    Notifications (no ``id``) return ``None`` per JSON-RPC spec.
    Unknown methods return ``-32601``.
    """
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }

    if method == "initialized" or method == "notifications/initialized":
        return None

    if method == "tools/list":
        tools_list = [
            {
                "name": name,
                "description": spec.get("description", ""),
                "inputSchema": spec.get("input_schema", {"type": "object"}),
            }
            for name, spec in TOOLS.items()
        ]
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}}

    if method == "tools/call":
        tool_name = params.get("name", "")
        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }
        handler = TOOLS[tool_name]["handler"]
        try:
            result = handler(**(params.get("arguments") or {}))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                    ]
                },
            }
        except Exception:
            logger.exception("Tool error in %s", tool_name)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": "Internal tool error"},
            }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if req_id is None:
        return None
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def main() -> None:
    """Run the JSON-RPC stdio loop until EOF."""
    _restore_stdout()
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError):
                pass

    # Open the substrate once at startup so schema is applied + the file
    # exists before any tool call. Closed immediately — tools open fresh
    # connections on demand.
    conn = get_conn()
    conn.close()
    logger.info("engine_memory MCP server starting (no tools wired at S-0189)")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception:
            logger.exception("Server error")


if __name__ == "__main__":
    main()
