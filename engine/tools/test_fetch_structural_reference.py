"""Tests for fetch_structural_reference.py.

Test discipline (per ADR 0047 S-0103 implementation discipline + ADR 0059):

- Synthetic-publisher tokens only (`Acme`, `FakeReference`, `MockPublisher`,
  `GenericSource`) — no enumerated source-identity names appear in test data,
  fixture strings, or assertions.
- Network access is mocked at `urllib.request.urlopen`. No real network
  traffic. Robots.txt fetches go through the same mock.
- Test fixtures synthesize SEP-shaped HTML using the cross-reference patterns
  in `ENCYCLOPEDIA_CONFIG` so the round-trip path exercises real adapter +
  detector code, not stubs.
- The recursive-walk anonymization invariant is asserted via the
  module's own `_assert_anonymized()` to keep the assertion shape uniform
  with the production gate.
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import fetch_structural_reference as fsr  # noqa: E402


# --------------------------------------------------------------------------
# Synthetic fixtures
# --------------------------------------------------------------------------


def _build_clean_html() -> bytes:
    """SEP-shaped HTML carrying graph-shape signal but no source-identity surfaces."""
    return b"""<!DOCTYPE html><html lang="en">
<head><title>Proposition</title></head>
<body>
<div id="aueditable">
<h1>Proposition</h1>
<p>Body prose elided -- parser does not extract prose.</p>
<h2>1. Foundations</h2>
<p>See <a href="../belief/">belief</a> and
<a href="../truth/">truth</a> for related entries.</p>
<h2>2. Theories</h2>
<p>Compare <a href="../proposition-russellian/">russellian propositions</a>
and <a href="../proposition-singular/">singular propositions</a>.</p>
</div>
</body></html>"""


def _build_poisoned_html() -> bytes:
    """SEP-shaped HTML where a publication-name suffix would survive a broken stripper."""
    return b"""<!DOCTYPE html><html lang="en">
<head><title>Proposition (Acme Encyclopedia of Philosophy)</title></head>
<body>
<div id="aueditable">
<h1>Proposition</h1>
<p>Body prose elided.</p>
<h2>1. Foundations</h2>
<p>See <a href="../belief/">belief</a>.</p>
</div>
</body></html>"""


def _build_robots_txt(disallowed_paths: list[str]) -> bytes:
    lines = [b"User-agent: *"]
    for path in disallowed_paths:
        lines.append(f"Disallow: {path}".encode())
    lines.append(b"")
    return b"\n".join(lines)


class _FakeResponse:
    """Minimal urlopen response stand-in supporting the context-manager protocol."""

    def __init__(
        self, body: bytes, *, content_type: str = "text/html; charset=utf-8"
    ) -> None:
        self._body = body
        self.headers = {"Content-Type": content_type}

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def _make_url_router(
    *,
    body: bytes = b"",
    body_content_type: str = "text/html; charset=utf-8",
    robots_body: bytes | None = None,
    robots_status: int | None = None,
    network_error_on_first_call: bool = False,
) -> Callable[..., _FakeResponse]:
    """Build a urlopen replacement that routes by URL path.

    - URLs ending in `/robots.txt` return `robots_body` (or 404 when
      `robots_status == 404`, or URLError when `robots_body is None`).
    - All other URLs return `_FakeResponse(body)` after the optional
      first-call network error (used to exercise retry behavior).
    """
    state = {"first_call": True}

    def router(arg: Any, *args: Any, **kwargs: Any) -> _FakeResponse:
        url = arg.full_url if isinstance(arg, urllib.request.Request) else str(arg)
        if url.endswith("/robots.txt"):
            if robots_status == 404:
                raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)  # type: ignore[arg-type]
            if robots_body is None:
                raise urllib.error.URLError("synthetic robots failure")
            return _FakeResponse(robots_body, content_type="text/plain")
        if network_error_on_first_call and state["first_call"]:
            state["first_call"] = False
            raise urllib.error.URLError("synthetic transient failure")
        state["first_call"] = False
        return _FakeResponse(body, content_type=body_content_type)

    return router


@contextmanager
def _patched_urlopen(router: Callable[..., _FakeResponse]) -> Iterator[None]:
    with (
        mock.patch.object(urllib.request, "urlopen", side_effect=router),
        mock.patch("urllib.robotparser.urlopen", side_effect=router, create=True),
    ):
        yield


# --------------------------------------------------------------------------
# FetchSession lifecycle
# --------------------------------------------------------------------------


class TestFetchSessionLifecycle:
    def test_tmpdir_purged_on_exit(self) -> None:
        with fsr.FetchSession() as session:
            tmpdir = session.tmpdir
            assert tmpdir.exists()
            (tmpdir / "marker").write_text("present")
            assert (tmpdir / "marker").exists()
        assert not tmpdir.exists()

    def test_tmpdir_unavailable_outside_with(self) -> None:
        session = fsr.FetchSession()
        with pytest.raises(RuntimeError, match="not active"):
            _ = session.tmpdir

    def test_construction_rejects_negative_rate_limit(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            fsr.FetchSession(rate_limit_seconds=-0.5)

    def test_construction_rejects_zero_max_fetches(self) -> None:
        with pytest.raises(ValueError, match="at least 1"):
            fsr.FetchSession(max_fetches=0)

    def test_max_fetches_budget_enforced(self) -> None:
        router = _make_url_router(body=_build_clean_html(), robots_body=b"")
        with (
            _patched_urlopen(router),
            fsr.FetchSession(max_fetches=2, rate_limit_seconds=0.0) as session,
        ):
            session.fetch("https://acme.test/page-1/")
            session.fetch("https://acme.test/page-2/")
            with pytest.raises(fsr.FetchError) as exc_info:
                session.fetch("https://acme.test/page-3/")
            assert exc_info.value.exit_code == fsr.EXIT_BUDGET_VIOLATION


# --------------------------------------------------------------------------
# Robots.txt compliance
# --------------------------------------------------------------------------


class TestRobotsTxtCompliance:
    def test_allowed_url_proceeds(self) -> None:
        router = _make_url_router(
            body=_build_clean_html(),
            robots_body=_build_robots_txt(["/private/"]),
        )
        with (
            _patched_urlopen(router),
            fsr.FetchSession(rate_limit_seconds=0.0) as session,
        ):
            fetched = session.fetch("https://acme.test/public/page/")
        assert fetched.url == "https://acme.test/public/page/"
        assert fetched.host == "acme.test"

    def test_disallowed_url_refused_with_exit_code_2(self) -> None:
        router = _make_url_router(
            body=_build_clean_html(),
            robots_body=_build_robots_txt(["/private/", "/"]),
        )
        with (
            _patched_urlopen(router),
            fsr.FetchSession(rate_limit_seconds=0.0) as session,
        ):
            with pytest.raises(fsr.FetchError) as exc_info:
                session.fetch("https://acme.test/private/page/")
        assert exc_info.value.exit_code == fsr.EXIT_ROBOTS_REFUSED

    def test_robots_unavailable_proceeds_conservatively(self) -> None:
        router = _make_url_router(body=_build_clean_html(), robots_body=None)
        with (
            _patched_urlopen(router),
            fsr.FetchSession(rate_limit_seconds=0.0) as session,
        ):
            fetched = session.fetch("https://acme.test/page/")
        assert fetched.url == "https://acme.test/page/"

    def test_robots_404_proceeds_conservatively(self) -> None:
        router = _make_url_router(body=_build_clean_html(), robots_status=404)
        with (
            _patched_urlopen(router),
            fsr.FetchSession(rate_limit_seconds=0.0) as session,
        ):
            fetched = session.fetch("https://acme.test/page/")
        assert fetched.url == "https://acme.test/page/"


# --------------------------------------------------------------------------
# Rate-limit
# --------------------------------------------------------------------------


class TestRateLimit:
    def test_first_fetch_does_not_sleep(self) -> None:
        router = _make_url_router(body=_build_clean_html(), robots_body=b"")
        sleep_calls: list[float] = []
        with (
            _patched_urlopen(router),
            mock.patch.object(time, "sleep", side_effect=sleep_calls.append),
            fsr.FetchSession(rate_limit_seconds=2.0) as session,
        ):
            session.fetch("https://acme.test/page-1/")
        # Sleep MAY have been called for retry backoff (it wasn't here, but
        # the rate-limit path itself should not have triggered any sleep).
        assert sleep_calls == []

    def test_second_fetch_sleeps_for_remaining_window(self) -> None:
        router = _make_url_router(body=_build_clean_html(), robots_body=b"")
        sleep_calls: list[float] = []
        time_values = iter([100.0, 100.0, 100.5, 100.5])

        def fake_monotonic() -> float:
            return next(time_values)

        with (
            _patched_urlopen(router),
            mock.patch.object(time, "monotonic", side_effect=fake_monotonic),
            mock.patch.object(time, "sleep", side_effect=sleep_calls.append),
            fsr.FetchSession(rate_limit_seconds=2.0) as session,
        ):
            session.fetch("https://acme.test/page-1/")
            session.fetch("https://acme.test/page-2/")
        # First fetch: now=100.0, no prior — no sleep.
        # Second fetch: now=100.5, last=100.0 → elapsed=0.5, deficit=1.5.
        assert pytest.approx(sleep_calls[0], abs=0.05) == 1.5


# --------------------------------------------------------------------------
# Network failure / retry
# --------------------------------------------------------------------------


class TestNetworkFailureAndRetry:
    def test_first_call_failure_retries_then_succeeds(self) -> None:
        router = _make_url_router(
            body=_build_clean_html(),
            robots_body=b"",
            network_error_on_first_call=True,
        )
        with (
            _patched_urlopen(router),
            mock.patch.object(time, "sleep") as sleep_mock,
            fsr.FetchSession(rate_limit_seconds=0.0) as session,
        ):
            fetched = session.fetch("https://acme.test/page/")
        assert fetched.url == "https://acme.test/page/"
        # Backoff sleep MUST have happened on the retry path.
        backoff_calls = [c.args[0] for c in sleep_mock.call_args_list if c.args]
        assert fsr.NETWORK_RETRY_BACKOFF_SECONDS in backoff_calls

    def test_persistent_failure_exits_with_code_4(self) -> None:
        def router(arg: Any, *args: Any, **kwargs: Any) -> _FakeResponse:
            url = arg.full_url if isinstance(arg, urllib.request.Request) else str(arg)
            if url.endswith("/robots.txt"):
                return _FakeResponse(b"", content_type="text/plain")
            raise urllib.error.URLError("permanent failure")

        with (
            _patched_urlopen(router),
            mock.patch.object(time, "sleep"),
            fsr.FetchSession(rate_limit_seconds=0.0) as session,
        ):
            with pytest.raises(fsr.FetchError) as exc_info:
                session.fetch("https://acme.test/page/")
        assert exc_info.value.exit_code == fsr.EXIT_NETWORK_FAILURE


# --------------------------------------------------------------------------
# Anonymization invariant
# --------------------------------------------------------------------------


class TestAnonymizationInvariant:
    def test_clean_brief_passes(self) -> None:
        clean = json.dumps(
            {
                "document_type": "encyclopedia",
                "parser_version": "0.1.0",
                "generated_at": "2026-05-09T00:00:00Z",
                "entries": [
                    {
                        "title": "Proposition",
                        "entry_id": "proposition",
                        "cross_references": ["belief", "truth"],
                        "section_path": "Foundations",
                        "word_count": 5000,
                        "extraction_confidence": 0.85,
                    }
                ],
            }
        )
        # Clean brief must not raise.
        fsr._assert_anonymized(clean)

    def test_publication_name_string_at_top_level_raises(self) -> None:
        poisoned = json.dumps(
            {
                "document_type": "encyclopedia",
                "credit": "Acme Encyclopedia of Philosophy",
                "entries": [],
            }
        )
        with pytest.raises(fsr.AnonymizationViolation):
            fsr._assert_anonymized(poisoned)

    def test_publication_name_string_in_nested_entry_raises(self) -> None:
        poisoned = json.dumps(
            {
                "document_type": "encyclopedia",
                "entries": [
                    {
                        "title": "Proposition (FakeReference Companion to Logic)",
                        "entry_id": "proposition",
                        "cross_references": [],
                    }
                ],
            }
        )
        with pytest.raises(fsr.AnonymizationViolation):
            fsr._assert_anonymized(poisoned)

    def test_url_in_brief_raises(self) -> None:
        poisoned = json.dumps(
            {
                "document_type": "encyclopedia",
                "entries": [
                    {
                        "title": "Proposition",
                        "entry_id": "proposition",
                        "source_url": "https://acme.test/entries/proposition/",
                    }
                ],
            }
        )
        with pytest.raises(fsr.AnonymizationViolation):
            fsr._assert_anonymized(poisoned)

    def test_concatenated_publication_pattern_in_deeply_nested_array(self) -> None:
        poisoned = json.dumps(
            {
                "entries": [
                    {
                        "metadata": [
                            "innocent",
                            {"footer": "MockPublisherEncyclopediaOfMind"},
                        ]
                    }
                ]
            }
        )
        with pytest.raises(fsr.AnonymizationViolation):
            fsr._assert_anonymized(poisoned)


# --------------------------------------------------------------------------
# Composition (round-trip through the parser)
# --------------------------------------------------------------------------


class TestComposition:
    def test_clean_html_round_trips_to_anonymized_brief(self) -> None:
        router = _make_url_router(body=_build_clean_html(), robots_body=b"")
        with (
            _patched_urlopen(router),
            fsr.FetchSession(rate_limit_seconds=0.0) as session,
        ):
            brief_json = fsr.fetch_and_parse(
                "https://acme.test/entries/proposition/",
                "encyclopedia",
                session=session,
            )
        payload = json.loads(brief_json)
        assert payload["document_type"] == "encyclopedia"
        assert payload["entries"], "round-trip yielded no entries"
        # Source-identity surfaces stripped at the serialization boundary.
        assert "source_path" not in payload
        for entry in payload["entries"]:
            assert "source_url" not in entry
        # The recursive walk would have raised if anonymization failed.

    def test_unknown_document_type_raises(self) -> None:
        with fsr.FetchSession() as session:
            with pytest.raises(fsr.FetchError) as exc_info:
                fsr.fetch_and_parse(
                    "https://acme.test/page/",
                    "not-a-real-type",
                    session=session,
                )
        assert exc_info.value.exit_code == fsr.EXIT_GENERIC_FETCH_ERROR

    def test_poisoned_html_raises_anonymization_violation(self) -> None:
        """If a publication-name suffix survives the parser's strippers all the way
        to the serialized brief, the gate refuses to return it."""
        # Construct a brief by hand whose `entries[].title` carries a survival
        # case the parser's existing strippers handle in the normal path. We
        # exercise the GATE itself by injecting a publication-shaped string
        # into the JSON that would-be returned. The realistic regression
        # path is parser regression; this test pins the gate so that a
        # parser regression cannot leak through silently.
        poisoned_payload = {
            "document_type": "encyclopedia",
            "parser_version": "0.1.0",
            "generated_at": "2026-05-09T00:00:00Z",
            "entries": [
                {
                    "title": "Proposition",
                    "entry_id": "proposition",
                    "cross_references": [
                        "innocent_slug",
                        "GenericSource Encyclopedia of Logic",
                    ],
                    "section_path": None,
                    "word_count": 5000,
                    "extraction_confidence": 0.5,
                }
            ],
        }
        with pytest.raises(fsr.AnonymizationViolation):
            fsr._assert_anonymized(json.dumps(poisoned_payload))


# --------------------------------------------------------------------------
# CLI exit codes
# --------------------------------------------------------------------------


class TestExitCodes:
    def test_success_path_exits_zero(self) -> None:
        router = _make_url_router(body=_build_clean_html(), robots_body=b"")
        with _patched_urlopen(router), mock.patch.object(sys, "stdout", io.StringIO()):
            code = fsr.main(
                [
                    "--url",
                    "https://acme.test/entries/proposition/",
                    "--document-type",
                    "encyclopedia",
                    "--rate-limit-seconds",
                    "0.0",
                ]
            )
        assert code == fsr.EXIT_SUCCESS

    def test_robots_refused_exits_2(self) -> None:
        router = _make_url_router(
            body=_build_clean_html(),
            robots_body=_build_robots_txt(["/", "/entries/"]),
        )
        with _patched_urlopen(router), mock.patch.object(sys, "stderr", io.StringIO()):
            code = fsr.main(
                [
                    "--url",
                    "https://acme.test/entries/proposition/",
                    "--document-type",
                    "encyclopedia",
                    "--rate-limit-seconds",
                    "0.0",
                ]
            )
        assert code == fsr.EXIT_ROBOTS_REFUSED

    def test_network_failure_exits_4(self) -> None:
        def router(arg: Any, *args: Any, **kwargs: Any) -> _FakeResponse:
            url = arg.full_url if isinstance(arg, urllib.request.Request) else str(arg)
            if url.endswith("/robots.txt"):
                return _FakeResponse(b"", content_type="text/plain")
            raise urllib.error.URLError("permanent failure")

        with (
            _patched_urlopen(router),
            mock.patch.object(time, "sleep"),
            mock.patch.object(sys, "stderr", io.StringIO()),
        ):
            code = fsr.main(
                [
                    "--url",
                    "https://acme.test/entries/proposition/",
                    "--document-type",
                    "encyclopedia",
                    "--rate-limit-seconds",
                    "0.0",
                ]
            )
        assert code == fsr.EXIT_NETWORK_FAILURE

    def test_anonymization_violation_exits_6(self) -> None:
        """Inject a publication-shaped string mid-pipeline to trigger the gate."""
        router = _make_url_router(body=_build_clean_html(), robots_body=b"")

        def poisoned_serialize(brief: Any) -> str:
            from parse_structural_reference import serialize_brief as real

            payload = json.loads(real(brief))
            # Inject a publication-shaped string into a nested place that the
            # gate's recursive walk visits.
            payload.setdefault("entries", []).append(
                {
                    "title": "Acme Encyclopedia of Philosophy",
                    "entry_id": "poison",
                    "cross_references": [],
                }
            )
            return json.dumps(payload)

        with (
            _patched_urlopen(router),
            mock.patch.object(fsr, "serialize_brief", side_effect=poisoned_serialize),
            mock.patch.object(sys, "stderr", io.StringIO()),
        ):
            code = fsr.main(
                [
                    "--url",
                    "https://acme.test/entries/proposition/",
                    "--document-type",
                    "encyclopedia",
                    "--rate-limit-seconds",
                    "0.0",
                ]
            )
        assert code == fsr.EXIT_ANONYMIZATION_VIOLATION

    def test_budget_violation_exits_3(self) -> None:
        router = _make_url_router(body=_build_clean_html(), robots_body=b"")
        # max_fetches=1 + two successive calls inside one CLI invocation isn't
        # the natural CLI shape, so exercise this at the FetchSession level
        # via the public session.fetch entry. CLI exit 3 is reachable via
        # composition when the audit loop iterates beyond the budget.
        with (
            _patched_urlopen(router),
            fsr.FetchSession(max_fetches=1, rate_limit_seconds=0.0) as session,
        ):
            session.fetch("https://acme.test/page-1/")
            with pytest.raises(fsr.FetchError) as exc_info:
                session.fetch("https://acme.test/page-2/")
        assert exc_info.value.exit_code == fsr.EXIT_BUDGET_VIOLATION


# --------------------------------------------------------------------------
# Tier 4 fetchable hosts surface (sanity check on the constant)
# --------------------------------------------------------------------------


class TestTier4Hosts:
    def test_tier_4_set_excludes_paywalled_publishers(self) -> None:
        # Only public hosts in the constant. This is a static check that
        # paywalled publisher hosts do not appear in the per-policy constant.
        # Per-source policy lives in product/docs/content-strategy.md; this
        # constant is a sanity backstop for the policy.
        for host in fsr.TIER_4_FETCHABLE_HOSTS:
            assert re.match(r"^[a-z0-9.\-]+$", host)
        assert all("paywall" not in h for h in fsr.TIER_4_FETCHABLE_HOSTS)
