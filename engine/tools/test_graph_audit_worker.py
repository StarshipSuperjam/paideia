"""Tests for engine.tools.graph_audit_worker per ADR 0101.

Exercises the worker's main() entry point directly (no subprocess
spawn) — the function is pure under monkey-patched ``validate``, so
each exit code is testable without process boundary noise.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from engine.tools import graph_audit_worker, validate


class TestGraphAuditWorkerMain:
    """worker.main(): returns exit codes for the parent's dispatch."""

    def test_main_emits_json_on_success(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Happy path: nodes+edges round-trip through stdout as one JSON line."""
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
        nodes = [{"id": "n1", "label": "node-1"}]
        edges = [{"id": "e1", "source_id": "n1", "target_id": "n1"}]
        monkeypatch.setattr(
            validate, "_read_graph_from_db", lambda _: (nodes, edges)
        )

        exit_code = graph_audit_worker.main()
        assert exit_code == graph_audit_worker.EXIT_SUCCESS

        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload == {"nodes": nodes, "edges": edges}

    def test_main_exits_2_when_env_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """SUPABASE_DB_URL absence is a parent contract violation."""
        monkeypatch.delenv("SUPABASE_DB_URL", raising=False)

        exit_code = graph_audit_worker.main()
        assert exit_code == graph_audit_worker.EXIT_ENV_MISSING

        err = capsys.readouterr().err
        assert "SUPABASE_DB_URL env missing" in err

    def test_main_exits_3_on_psycopg_import_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """psycopg unavailable → exit 3 so parent records graph_audit_skipped."""
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")

        def boom(_: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
            raise ImportError("No module named 'psycopg'")

        monkeypatch.setattr(validate, "_read_graph_from_db", boom)

        exit_code = graph_audit_worker.main()
        assert exit_code == graph_audit_worker.EXIT_PSYCOPG_IMPORT_ERROR

        err = capsys.readouterr().err
        assert "psycopg unavailable" in err

    def test_main_exits_4_on_psycopg_query_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """psycopg connect/query error → exit 4 with stderr message."""
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")

        def boom(_: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
            raise RuntimeError("connection refused by pooler")

        monkeypatch.setattr(validate, "_read_graph_from_db", boom)

        exit_code = graph_audit_worker.main()
        assert exit_code == graph_audit_worker.EXIT_DB_ERROR

        err = capsys.readouterr().err
        assert "RuntimeError" in err
        assert "connection refused" in err

    def test_main_exits_5_on_serialization_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """An unserializable row → exit 5 (defense-in-depth for future schema).

        Today's schema can't actually produce this — premise 3 of ADR 0101
        says all returned types are JSON-safe under ``default=str``. The
        path exists in case a future seed introduces something that
        ``default=str`` itself fails on (e.g., a custom object whose
        ``__str__`` raises).
        """
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")

        class UnserializableShim:
            def __str__(self) -> str:
                raise ValueError("cannot stringify this object")

        unserializable = [{"id": UnserializableShim()}]
        monkeypatch.setattr(
            validate, "_read_graph_from_db", lambda _: (unserializable, [])
        )

        exit_code = graph_audit_worker.main()
        assert exit_code == graph_audit_worker.EXIT_JSON_ERROR

        err = capsys.readouterr().err
        assert "JSON serialization failed" in err

    def test_main_handles_empty_corpus(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Zero-node / zero-edge corpus serializes as empty arrays."""
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
        monkeypatch.setattr(
            validate, "_read_graph_from_db", lambda _: ([], [])
        )

        exit_code = graph_audit_worker.main()
        assert exit_code == graph_audit_worker.EXIT_SUCCESS
        out = capsys.readouterr().out
        assert json.loads(out) == {"nodes": [], "edges": []}

    def test_main_uses_compact_separators(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Output is single-line compact JSON (one ``\\n`` would split parser).

        The parent reads stdout as a single string and calls
        ``json.loads(...)``. A multi-line dump would still parse, but
        compact form is the contract for predictability.
        """
        monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
        monkeypatch.setattr(
            validate,
            "_read_graph_from_db",
            lambda _: ([{"id": "a"}], [{"id": "e1"}]),
        )

        graph_audit_worker.main()
        out = capsys.readouterr().out
        # Compact separators produce no spaces after ``,`` or ``:``;
        # the contract is one-line output.
        assert " " not in out, (
            "Worker must emit compact JSON without spaces; deviation indicates "
            "default-separator drift that could affect downstream parsers"
        )
        assert "\n" not in out
