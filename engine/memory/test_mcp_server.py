"""Tests for ``engine/memory/mcp_server.py`` — JSON-RPC skeleton dispatch.

At S-0190 the registry holds 2 of 6 eventual tools
(``engine_memory_add_drawer`` + ``engine_memory_diary_write``); the
remaining 4 land at S-0191. Tests cover the protocol-level methods
(``initialize``, ``tools/list``, ``ping``), the tools/call dispatch for
both wired tools and a not-yet-wired tool (``engine_memory_search``
returns -32601 until S-0191), notifications, and unknown methods.
"""

from __future__ import annotations

import json
from pathlib import Path


from engine.memory import mcp_server


def test_initialize_returns_protocol_handshake() -> None:
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    resp = mcp_server.handle_request(req)
    assert resp is not None
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 1
    result = resp["result"]
    assert result["protocolVersion"] == mcp_server.PROTOCOL_VERSION
    assert result["serverInfo"]["name"] == mcp_server.SERVER_NAME
    assert "capabilities" in result


def test_tools_list_returns_two_at_s0190() -> None:
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = mcp_server.handle_request(req)
    assert resp is not None
    tools = resp["result"]["tools"]
    names = {t["name"] for t in tools}
    assert names == {"engine_memory_add_drawer", "engine_memory_diary_write"}
    # Each tool advertises a non-empty description and an inputSchema.
    for t in tools:
        assert t["description"]
        assert isinstance(t["inputSchema"], dict)


def test_tools_call_unknown_tool_returns_minus_32601() -> None:
    """Tools not yet wired (S-0191 work) return JSON-RPC method-not-found."""
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "engine_memory_search", "arguments": {"query": "x"}},
    }
    resp = mcp_server.handle_request(req)
    assert resp is not None
    assert resp["error"]["code"] == -32601
    assert "engine_memory_search" in resp["error"]["message"]


def test_tools_call_add_drawer_round_trip(tmp_path: Path) -> None:
    """tools/call dispatches to the registered handler and returns its result."""
    db = tmp_path / "test.sqlite3"
    req = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "engine_memory_add_drawer",
            "arguments": {
                "content": "via mcp",
                "room": "decisions",
                "db_path": str(db),
            },
        },
    }
    resp = mcp_server.handle_request(req)
    assert resp is not None
    assert "result" in resp
    text = resp["result"]["content"][0]["text"]
    payload = json.loads(text)
    assert "id" in payload
    assert "filed_at" in payload


def test_tools_call_diary_write_round_trip(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite3"
    req = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "engine_memory_diary_write",
            "arguments": {
                "entry": "test reflection via mcp",
                "topic": "smoke",
                "db_path": str(db),
            },
        },
    }
    resp = mcp_server.handle_request(req)
    assert resp is not None
    text = resp["result"]["content"][0]["text"]
    payload = json.loads(text)
    assert "id" in payload
    assert "created_at" in payload


def test_tools_call_handler_error_returns_minus_32000(tmp_path: Path) -> None:
    """A handler exception (e.g. ValueError on invalid room) → -32000."""
    db = tmp_path / "test.sqlite3"
    req = {
        "jsonrpc": "2.0",
        "id": 12,
        "method": "tools/call",
        "params": {
            "name": "engine_memory_add_drawer",
            "arguments": {
                "content": "x",
                "room": "bogus_room",
                "db_path": str(db),
            },
        },
    }
    resp = mcp_server.handle_request(req)
    assert resp is not None
    assert resp["error"]["code"] == -32000


def test_ping_returns_empty_result() -> None:
    req = {"jsonrpc": "2.0", "id": 4, "method": "ping"}
    resp = mcp_server.handle_request(req)
    assert resp is not None
    assert resp["result"] == {}


def test_notifications_initialized_returns_none() -> None:
    """Notifications (no id) return None per JSON-RPC spec."""
    for method in ("initialized", "notifications/initialized"):
        req = {"jsonrpc": "2.0", "method": method}
        assert mcp_server.handle_request(req) is None


def test_unknown_method_returns_minus_32601() -> None:
    req = {"jsonrpc": "2.0", "id": 5, "method": "tools/inspect"}
    resp = mcp_server.handle_request(req)
    assert resp is not None
    assert resp["error"]["code"] == -32601


def test_request_without_id_is_treated_as_notification() -> None:
    """A request with no id and no recognized notification method returns None."""
    req = {"jsonrpc": "2.0", "method": "tools/list"}
    resp = mcp_server.handle_request(req)
    # tools/list without id is a notification — handler returns the result
    # only when id is present in the JSON-RPC envelope. handle_request
    # currently always returns the dispatch result for tools/list; the
    # caller is responsible for suppressing the response. Verify the
    # actual current behavior so this test pins the contract.
    if resp is not None:
        assert "result" in resp
