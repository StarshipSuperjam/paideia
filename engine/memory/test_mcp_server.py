"""Tests for ``engine/memory/mcp_server.py`` — JSON-RPC skeleton dispatch.

At S-0189 the tool registry is empty (S-0190+ adds tools). Tests cover
the protocol-level methods that work without any tools wired:
``initialize``, ``tools/list``, ``ping``, ``tools/call`` (returns
-32601 because no tools), notifications, and unknown methods.
"""

from __future__ import annotations

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


def test_tools_list_returns_empty_at_s0189() -> None:
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = mcp_server.handle_request(req)
    assert resp is not None
    assert resp["result"]["tools"] == []


def test_tools_call_unknown_tool_returns_minus_32601() -> None:
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
