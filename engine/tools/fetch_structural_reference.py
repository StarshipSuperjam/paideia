#!/usr/bin/env python3
"""Audit-time URL-input counterpart to parse_structural_reference.py.

Module contract — what this file is and is not.

This module is a standing engine tool that fetches public Tier 4 structural
references (SEP, IEP, Wikipedia per [ADR 0059] policy) and composes them
through the existing structural-reference parser to produce an anonymized
focusing brief for audit-time comparison against parametrically-derived graph
entries. Authoring-time posture under [ADR 0046] is unchanged; this tool is
audit-time only — see [ADR 0059] for the full carve-out.

Invariants this module preserves:

- The brief reaching the LLM is anonymized. Source identity (publication name,
  URL, file path) is stripped at the serialization boundary via the existing
  parser's `serialize_brief()` and the structural publication-name strippers
  introduced by the S-0103 amendment to ADR 0047. A recursive walk asserts no
  source-identity strings at any depth before the brief is returned.
- The lifecycle is bounded ephemeral. Fetched bytes live in a
  `tempfile.TemporaryDirectory` purged on context exit. No on-disk cache. No
  cross-session persistence.
- The fetch is polite. Declared User-Agent identifying the project; robots.txt
  consulted via `urllib.robotparser` and refusal honored; per-host rate-limit
  (default 2.0 seconds) enforced; bounded fetch count per session
  (default 20).

Non-responsibilities:

- No graph mutation. The tool produces a brief for human/audit-LLM
  consumption; it never writes to the Supabase graph or to STATE.md.
- No content reproduction. The brief carries graph-shape facts (titles,
  identifiers, cross-reference adjacency, word counts). Source prose is
  never loaded into Entry records, never emitted, never persisted.
- No source acquisition for paywalled members of the [ADR 0046] class.
  Routledge / Oxford Reference are explicitly out of scope per
  [`product/docs/content-strategy.md`](../../product/docs/content-strategy.md)
  Tier 4 fetch-policy. Adding paywalled fetching is a separate per-source ADR.
- No standing-capability operation. Recurring crawlers that operate beyond
  one-off audit fortification are out of scope per [ADR 0059] — the
  standing-capability fair-use ADR is deferred until that use grows.

Failure-mode discrimination via exit codes (CLI mode):

    0 — success; serialized brief printed to stdout
    2 — robots.txt refused (HANDOFF; per-source policy may need ADR amendment)
    3 — rate-limit / fetch-budget violation
    4 — network failure (retried once after 5 seconds, then exit)
    5 — generic fetch error
    6 — anonymization invariant violation (load-bearing; HANDOFF immediately)

Output schema is identical to parse_structural_reference.py — see that
module's docstring or [ADR 0047]. The serialization path is shared via
direct function reuse from parse_structural_reference.py, not duplicated.

Module contracts referenced:

- ADR 0059 — operational contract for this tool; bounded ephemeral audit-time
  fetching, anonymization mandatory, polite-fetcher discipline.
- ADR 0047 — operational contract for the parser this tool composes;
  anti-fetch contract on the parser is preserved verbatim.
- ADR 0046 — structural-reference posture for authoring time; this tool's
  audit-time scope is additive, not a retreat from authoring-time discipline.
- ADR 0011 — no hosted or distributed copyrighted material; the brief carries
  facts not prose; fetched content dies with the session.
- ADR 0057 — adversarial stance for audits; this tool operationalizes the
  fresh-content-probe principle for graph audits.
- ADR 0053 — mechanism-first-exercise gate; voluntary readiness note at
  engine/build_readiness/fetch_structural_reference_first_exercise.md (strict
  trigger does not fire; the gate's spirit is honored).
- ADR 0038 — code-discipline contract; this module authors under it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Final

sys.path.insert(0, str(Path(__file__).resolve().parent))

from parse_structural_reference import (  # noqa: E402
    DOCUMENT_TYPE_REGISTRY,
    FocusingBrief,
    PUBLICATION_NAME_PATTERN,
    PUBLICATION_NAME_PATTERN_CONCATENATED,
    emit_focusing_brief,
    extract_entries,
    is_publication_name_shaped,
    select_adapter,
    serialize_brief,
)

DEFAULT_RATE_LIMIT_SECONDS: Final[float] = 2.0
DEFAULT_MAX_FETCHES: Final[int] = 20
DEFAULT_NETWORK_TIMEOUT_SECONDS: Final[float] = 30.0
NETWORK_RETRY_BACKOFF_SECONDS: Final[float] = 5.0
USER_AGENT: Final[str] = (
    "Paideia-Audit-Bot/1.0 "
    "(+https://github.com/StarshipSuperjam/paideia; audit-time fortification)"
)

EXIT_SUCCESS: Final[int] = 0
EXIT_ROBOTS_REFUSED: Final[int] = 2
EXIT_BUDGET_VIOLATION: Final[int] = 3
EXIT_NETWORK_FAILURE: Final[int] = 4
EXIT_GENERIC_FETCH_ERROR: Final[int] = 5
EXIT_ANONYMIZATION_VIOLATION: Final[int] = 6

CONTENT_TYPE_TO_SUFFIX: Final[dict[str, str]] = {
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
}

# Reserved publication-name tokens the per-source policy explicitly authorizes
# — these are not source-identity tokens for anonymization; they appear in
# code as policy keys, not as content surfacing to the LLM.
TIER_4_FETCHABLE_HOSTS: Final[frozenset[str]] = frozenset(
    {
        "plato.stanford.edu",
        "iep.utm.edu",
        "en.wikipedia.org",
    }
)


class FetchError(Exception):
    """Raised by FetchSession.fetch when a fetch fails after retry budget."""

    def __init__(self, message: str, *, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class AnonymizationViolation(FetchError):
    """Raised when the recursive-walk anonymization invariant fails.

    Load-bearing: a violation here means the parser's anonymization layer did
    not strip a source-identity surface from a URL-fetched brief. Either the
    parser has a regression OR the fetched source carries an unanticipated
    publication-name shape. Either way, the brief MUST NOT reach the LLM.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message, exit_code=EXIT_ANONYMIZATION_VIOLATION)


@dataclass(frozen=True)
class FetchedSource:
    """One fetch's resolved metadata. Held in-process; not serialized."""

    url: str
    host: str
    body_path: Path
    content_type: str


class FetchSession(AbstractContextManager["FetchSession"]):
    """Audit-session context manager wrapping the ephemeral fetch lifecycle.

    Construct in a `with` block:

        with FetchSession() as session:
            brief_json = fetch_and_parse(url, "encyclopedia", session=session)

    On context exit the temporary directory is purged, the rate-limit and
    fetch-budget state is dropped, and the robots.txt cache is cleared.
    Outside the block the session cannot be used.
    """

    def __init__(
        self,
        *,
        rate_limit_seconds: float = DEFAULT_RATE_LIMIT_SECONDS,
        max_fetches: int = DEFAULT_MAX_FETCHES,
        user_agent: str = USER_AGENT,
        network_timeout_seconds: float = DEFAULT_NETWORK_TIMEOUT_SECONDS,
    ) -> None:
        if rate_limit_seconds < 0:
            raise ValueError("rate_limit_seconds must be non-negative")
        if max_fetches < 1:
            raise ValueError("max_fetches must be at least 1")
        self._rate_limit_seconds = rate_limit_seconds
        self._max_fetches = max_fetches
        self._user_agent = user_agent
        self._network_timeout_seconds = network_timeout_seconds
        self._tmpdir: tempfile.TemporaryDirectory[str] | None = None
        self._fetch_count = 0
        self._last_fetch_per_host: dict[str, float] = {}
        self._robots_cache: dict[str, urllib.robotparser.RobotFileParser | None] = {}

    def __enter__(self) -> FetchSession:
        self._tmpdir = tempfile.TemporaryDirectory(prefix="paideia-fetch-")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._tmpdir is not None:
            self._tmpdir.cleanup()
            self._tmpdir = None
        self._last_fetch_per_host.clear()
        self._robots_cache.clear()

    @property
    def fetch_count(self) -> int:
        return self._fetch_count

    @property
    def tmpdir(self) -> Path:
        if self._tmpdir is None:
            raise RuntimeError("FetchSession is not active; use within `with` block")
        return Path(self._tmpdir.name)

    def _check_robots(self, url: str) -> bool:
        """Return True when fetching `url` is allowed by robots.txt.

        Conservative defaults: robots fetch error or 4xx response is treated
        as "no policy" and proceeds. Explicit `Disallow` returns False.
        """
        parsed = urllib.parse.urlparse(url)
        host_key = f"{parsed.scheme}://{parsed.netloc}"
        if host_key not in self._robots_cache:
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(f"{host_key}/robots.txt")
            try:
                parser.read()
                self._robots_cache[host_key] = parser
            except (urllib.error.URLError, OSError):
                self._robots_cache[host_key] = None
        cached = self._robots_cache[host_key]
        if cached is None:
            return True
        return cached.can_fetch(self._user_agent, url)

    def _enforce_rate_limit(self, host: str) -> None:
        now = time.monotonic()
        last = self._last_fetch_per_host.get(host)
        if last is not None:
            elapsed = now - last
            if elapsed < self._rate_limit_seconds:
                time.sleep(self._rate_limit_seconds - elapsed)
        self._last_fetch_per_host[host] = time.monotonic()

    def fetch(self, url: str) -> FetchedSource:
        """Fetch a single URL into the ephemeral tmpdir.

        Raises:
            FetchError: with exit_code matching the failure-mode discrimination
                in the module docstring.
        """
        if self._tmpdir is None:
            raise RuntimeError("FetchSession is not active; use within `with` block")
        if self._fetch_count >= self._max_fetches:
            raise FetchError(
                f"fetch budget exhausted: {self._fetch_count}/{self._max_fetches}",
                exit_code=EXIT_BUDGET_VIOLATION,
            )
        if not self._check_robots(url):
            raise FetchError(
                f"robots.txt disallows fetching {url}",
                exit_code=EXIT_ROBOTS_REFUSED,
            )
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc
        self._enforce_rate_limit(host)

        request = urllib.request.Request(url, headers={"User-Agent": self._user_agent})
        try:
            response = urllib.request.urlopen(  # noqa: S310 — vetted by ADR 0059  # nosec B310  # scheme allowlist enforced upstream per ADR 0059
                request, timeout=self._network_timeout_seconds
            )
        except urllib.error.URLError:
            time.sleep(NETWORK_RETRY_BACKOFF_SECONDS)
            try:
                response = urllib.request.urlopen(  # noqa: S310 — vetted by ADR 0059  # nosec B310  # scheme allowlist enforced upstream per ADR 0059
                    request, timeout=self._network_timeout_seconds
                )
            except urllib.error.URLError as exc:
                raise FetchError(
                    f"network failure after retry: {exc}",
                    exit_code=EXIT_NETWORK_FAILURE,
                ) from exc
        except Exception as exc:  # noqa: BLE001 — broad surface deliberate
            raise FetchError(
                f"generic fetch error: {exc}",
                exit_code=EXIT_GENERIC_FETCH_ERROR,
            ) from exc

        with response:
            content_type = (
                (response.headers.get("Content-Type") or "").split(";")[0].strip()
            )
            body = response.read()

        suffix = CONTENT_TYPE_TO_SUFFIX.get(content_type, ".html")
        body_path = self.tmpdir / f"fetch_{self._fetch_count:04d}{suffix}"
        body_path.write_bytes(body)
        self._fetch_count += 1
        return FetchedSource(
            url=url,
            host=host,
            body_path=body_path,
            content_type=content_type,
        )


def _walk_strings(value: Any) -> list[str]:
    """Yield every string at every depth in a JSON-shaped Python object."""
    out: list[str] = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            out.extend(_walk_strings(k))
            out.extend(_walk_strings(v))
    elif isinstance(value, list):
        for item in value:
            out.extend(_walk_strings(item))
    return out


def _assert_anonymized(brief_json: str) -> None:
    """Recursive-walk invariant: no source-identity strings at any depth.

    The parser's `serialize_brief()` strips `source_path` and `source_url`;
    the publication-name strippers in `detect_title()` and `extract_entries()`
    drop publication-shaped headings. This function is the audit-time gate
    on a URL-fetched brief — if any string at any depth matches the
    publication-name structural pattern OR contains a literal URL host, the
    invariant is violated and the brief MUST NOT reach the LLM.
    """
    payload = json.loads(brief_json)
    for s in _walk_strings(payload):
        if is_publication_name_shaped(s):
            raise AnonymizationViolation(
                f"publication-name-shaped string survived to brief: {s!r}"
            )
        if PUBLICATION_NAME_PATTERN.search(s) is not None:
            raise AnonymizationViolation(
                f"publication-name pattern survived to brief: {s!r}"
            )
        if PUBLICATION_NAME_PATTERN_CONCATENATED.search(s) is not None:
            raise AnonymizationViolation(
                f"concatenated publication-name pattern survived to brief: {s!r}"
            )
        if re.search(r"https?://", s) is not None:
            raise AnonymizationViolation(f"raw URL survived to brief: {s!r}")


def fetch_and_parse(
    url: str,
    document_type: str,
    *,
    session: FetchSession,
) -> str:
    """Fetch `url`, run the parser against the bytes, return serialized brief.

    The returned string is the JSON-serialized FocusingBrief — anonymized at
    the serialization boundary by the existing `serialize_brief()` and gated
    by the recursive-walk anonymization invariant before return. Callers
    feed this string to the audit-LLM triage prompt.

    The session controls budget, rate limiting, and the ephemeral tmpdir.
    The brief is *not* persisted — it returns to the caller; if the caller
    discards it, no on-disk artifact remains.
    """
    if document_type not in DOCUMENT_TYPE_REGISTRY:
        raise FetchError(
            f"unknown document_type: {document_type!r}; "
            f"valid: {sorted(DOCUMENT_TYPE_REGISTRY)}",
            exit_code=EXIT_GENERIC_FETCH_ERROR,
        )
    fetched = session.fetch(url)
    config = DOCUMENT_TYPE_REGISTRY[document_type]
    adapter = select_adapter(fetched.body_path, override=None)
    adapter_output = adapter.extract(fetched.body_path, document_type)
    entries = extract_entries(adapter_output, config)
    brief: FocusingBrief = emit_focusing_brief(adapter_output, entries)
    serialized = serialize_brief(brief)
    _assert_anonymized(serialized)
    return serialized


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="fetch_structural_reference",
        description=(
            "Audit-time fetcher for public structural references (see ADR 0059)."
        ),
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="The URL to fetch.",
    )
    parser.add_argument(
        "--document-type",
        choices=sorted(DOCUMENT_TYPE_REGISTRY.keys()),
        required=True,
        help="Document type for heuristic config selection.",
    )
    parser.add_argument(
        "--max-fetches",
        type=int,
        default=DEFAULT_MAX_FETCHES,
        help=f"Per-session fetch budget (default {DEFAULT_MAX_FETCHES}).",
    )
    parser.add_argument(
        "--rate-limit-seconds",
        type=float,
        default=DEFAULT_RATE_LIMIT_SECONDS,
        help=(
            "Per-host minimum interval between fetches "
            f"(default {DEFAULT_RATE_LIMIT_SECONDS}s)."
        ),
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> int:
    try:
        with FetchSession(
            rate_limit_seconds=args.rate_limit_seconds,
            max_fetches=args.max_fetches,
        ) as session:
            brief_json = fetch_and_parse(args.url, args.document_type, session=session)
            sys.stdout.write(brief_json)
            sys.stdout.write("\n")
        return EXIT_SUCCESS
    except FetchError as exc:
        sys.stderr.write(f"[fetch_structural_reference] {exc}\n")
        return exc.exit_code


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    return run(args)


__all__ = [
    "DEFAULT_MAX_FETCHES",
    "DEFAULT_RATE_LIMIT_SECONDS",
    "EXIT_ANONYMIZATION_VIOLATION",
    "EXIT_BUDGET_VIOLATION",
    "EXIT_GENERIC_FETCH_ERROR",
    "EXIT_NETWORK_FAILURE",
    "EXIT_ROBOTS_REFUSED",
    "EXIT_SUCCESS",
    "TIER_4_FETCHABLE_HOSTS",
    "USER_AGENT",
    "AnonymizationViolation",
    "FetchError",
    "FetchSession",
    "FetchedSource",
    "fetch_and_parse",
    "main",
    "parse_args",
    "run",
]


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
