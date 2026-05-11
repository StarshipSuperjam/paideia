# fetch_structural_reference.py — mechanism-first-exercise gate report

> Authored by S-0106 per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Covers the first interactive exercise of the audit-time fetcher that [ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md) introduces. **Voluntary gate**: the strict trigger criterion does not fire (see evaluation below); the gate is applied anyway because the [Phase 5 production audit master plan](phase_5_production_audit.md) routes routine-mode audit sessions to the new tool, and the gate's spirit (catch S-0048-shape gaps before unattended use) applies despite the strict trigger not firing.

## Mechanism summary

[`engine/tools/fetch_structural_reference.py`](../tools/fetch_structural_reference.py) is the URL-input counterpart to [`parse_structural_reference.py`](../tools/parse_structural_reference.py). It composes a polite-fetcher wrapper (User-Agent, robots.txt via `urllib.robotparser`, per-host rate-limit, bounded fetch budget, ephemeral `tempfile.TemporaryDirectory` lifecycle) around the existing parser's public API (`select_adapter` + `extract` + `extract_entries` + `emit_focusing_brief` + `serialize_brief`) plus an additional anonymization-invariant gate (`_assert_anonymized` recursive walk).

The tool is for *audit-time* use only per [ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md). Authoring-time posture under [ADR 0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) is unchanged. Fetched bytes live in process memory and die with the `FetchSession` context manager; no on-disk cache; no cross-session persistence.

## Trigger criterion evaluation (per ADR 0053)

| Criterion | Status |
|---|---|
| #1 — introduces a new session mode | No (it is a tool, not a session mode) |
| #2 — introduces a new validator soft-warn category requiring session-side discipline | No (`validate.py` is unchanged in this session) |
| #3 — introduces a new state file the boot procedure reads | No (ephemeral in-process cache; no boot integration) |
| #4 — Consequences span ≥ 3 ops docs OR ≥ 5 tooling files | No (1 ops doc — [`cross-references.md`](../operations/cross-references.md); 2 tooling files — the tool + tests; 4 doc amendments — ADR 0047 / phase_5_production_audit.md / content-strategy.md / ENGINE_LOG.md) |

**Strict trigger does not fire.** Per ADR 0053's "trigger when in doubt" bias: the gate is applied voluntarily because (a) the master-plan amendment routes unattended routine-mode audit sessions to the new tool and (b) network-dependent operations have failure surfaces that real-world execution exposes more reliably than analysis. The cost of a voluntary gate (this report authored at landing time) is much smaller than the cost of a missed trigger (the S-0048 → S-0055 serialized-Issue pattern).

## Phase 0 empirical findings — covered by unit tests at S-0106

The 27 tests in [`engine/tools/test_fetch_structural_reference.py`](../tools/test_fetch_structural_reference.py) cover the major failure surfaces against synthetic fixtures that mock `urllib.request.urlopen` (no real network traffic):

- **`TestFetchSessionLifecycle`** — tmpdir created on `__enter__`, purged on `__exit__`, unavailable outside `with` block; parameter validation rejects negative rate-limit and zero `max_fetches`.
- **`TestRobotsTxtCompliance`** — disallowed URL refused with exit code 2; allowed URL proceeds; robots-unavailable (URLError) and robots-404 both proceed conservatively per the documented "no policy → conservative proceed" rule.
- **`TestRateLimit`** — first fetch does not sleep; second fetch within rate-limit window sleeps for the deficit (asserted to within 0.05s).
- **`TestNetworkFailureAndRetry`** — first-call URLError triggers retry after `NETWORK_RETRY_BACKOFF_SECONDS` sleep; persistent failure exits with code 4.
- **`TestAnonymizationInvariant`** — clean briefs pass; publication-name strings at top level, in nested entries, in deeply-nested arrays, raw URLs, and concatenated patterns each raise `AnonymizationViolation`.
- **`TestComposition`** — synthetic SEP-shaped HTML round-trips through the fetch path and yields a `FocusingBrief` with entries; `source_path` and per-entry `source_url` are stripped at the serialization boundary; unknown document_type raises with exit code 5.
- **`TestExitCodes`** — CLI mode emits codes 0/2/4/6 directly via `main(...)` invocation against synthetic stubs; budget violation (code 3) reachable via direct `FetchSession.fetch` over-budget call.
- **`TestTier4Hosts`** — sanity backstop on the `TIER_4_FETCHABLE_HOSTS` constant (no paywalled-publisher hosts present).

Existing `parse_structural_reference.py` test suite (155 tests) still passes — the new tool's imports and composition do not regress the parser.

## Tier 1 findings (must close before unattended use)

| ID | Finding | Status |
|---|---|---|
| T1-A | Anonymization invariant must catch publication-name surfaces from a real SEP fetch | **Resolved at S-0122.** 31 of 33 successful real-SEP fetches against `plato.stanford.edu` produced 0 `AnonymizationViolation` events. The `_assert_anonymized` recursive walk against `is_publication_name_shaped` / `PUBLICATION_NAME_PATTERN` handled live SEP HTML cleanly. The structural-pattern approach (vs enumerated-tokens) absorbed the source-format variability. See [`phase_5_production_audit_findings.md`](phase_5_production_audit_findings.md) §"Empirical-fortification first-exercise outcomes". |
| T1-B | Robots.txt fetch and parse against the real SEP host must succeed under default User-Agent | **Resolved at S-0122.** All 31 successful fetches proceeded normally; the implicit `urllib.robotparser` check did not block any URL. The User-Agent (`Paideia-Audit-Bot/1.0 +https://github.com/StarshipSuperjam/paideia audit-time fortification`) was accepted by SEP without rate-limit or block events. |
| T1-C | Rate-limit (default 2.0s) must be empirically observable against real network | **Resolved at S-0122.** Wall-clock per-fetch elapsed times across the 31 successful fetches show a clean rate-limit signature: typical range 1.94s-2.10s per fetch, reflecting the 2.0s rate-limit sleep + a small variable network-fetch component. The first fetch in the queue (`aristotle-causality`, 0.45s) had no prior fetch to gate; subsequent fetches consistently sat at the ~2s rate-limit boundary. |
| T1-D | One-fetch round-trip against a real SEP URL must produce a non-empty `FocusingBrief.entries` | **Resolved at S-0122.** All 31 successful fetches returned exactly 1 entry with substantial structural content (word_counts ranging from 9,035 to 45,393; cross_references ranging from 4 to 34 per entry; `extraction_confidence` ≥ 0.99 across the corpus; `section_path` populated for all). |
| T1-E | The `User-Agent` string declared in the tool must be acceptable to SEP / IEP / Wikipedia under their respective bot-policy norms | **Resolved at S-0106.** The User-Agent identifies the project (`Paideia-Audit-Bot/1.0`), declares contact (`+https://github.com/StarshipSuperjam/paideia`), and names the use (`audit-time fortification`). This matches the pattern publishers' bot policies typically expect. Adjustment is a docstring edit + constant change in the consuming session if any host pushes back. |
| T1-F | Failure-mode discrimination must produce distinct exit codes the audit-loop can branch on | **Resolved at S-0106.** Exit codes 0/2/3/4/5/6 each have dedicated test cases; `FetchError.exit_code` is the discriminating field; CLI mode propagates through `main()`'s `return exc.exit_code` path. |

## Tier 2 findings (settle in advance and document)

| ID | Finding | Status |
|---|---|---|
| T2-A | Per-host rate-limit may be insufficient under heavy session pace | Documented. The `rate_limit_seconds` parameter is configurable; default 2.0 is conservative. If a routine session needs to fortify many verdicts in one fire, the audit-loop adjusts the per-fetch budget OR the rate-limit downward toward the minimum that respects each host's stated policy. |
| T2-B | Anonymization recursive walk's regex set is correct as of S-0106; future SEP / IEP / Wikipedia HTML-structure changes may surface new publication-name shapes | Documented. The recursive walk uses `is_publication_name_shaped` and `PUBLICATION_NAME_PATTERN` from the existing parser — both are structural patterns, not enumerated tokens, so source-format evolution is absorbed by the structural shape. New publication-name shapes that emerge are caught by the recursive walk and would surface as `AnonymizationViolation` (exit 6) rather than silently leaking. |
| T2-C | The CLI's `--max-fetches` budget is per-invocation, not per-session | Documented. Routine sessions invoke the CLI once per verdict; audit-loop tracks aggregate fetches outside the tool. If aggregate-budget tracking becomes necessary, a future ADR can add a session-scoped budget file. |

## Tier 3 findings (deferred forward-pointers)

| ID | Finding | Notes |
|---|---|---|
| T3-A | A standing-capability fetcher (recurring crawler) requires a separate ADR per [ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md) | Deferred until that use grows. Aggregation under fair use's four-factor balancing test shifts when one-off transforms into recurring; the deferred ADR is the future hook. |
| T3-B | Per-source policy expansion (paywalled members of the [ADR 0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) class — Routledge, Oxford Reference) requires a per-source ADR with the chosen institutional-credential mechanism | Deferred until a session pursues paywalled fetching. The current `TIER_4_FETCHABLE_HOSTS` constant excludes these; expansion requires content-strategy.md table + tool constant + per-source ADR in the same commit. |
| T3-C | A `fetch_budget_exceeded_session` validator soft-warn could fire if routine-block telemetry shows the budget is being silently exhausted | Deferred per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) lifecycle. Add the soft-warn category only when the routine block produces evidence of silent exhaustion; speculative addition violates "don't add features beyond what the task requires." |

## Closes when

This report's T1-A through T1-D Tier 1 findings close at the first interactive audit-closeout session that fortifies S-0104 medium-confidence verdicts (or comparable medium-confidence verdicts from later AUDIT-* routine fires). That session's outcome_summary should record:

- Number of fetches successfully completed against `plato.stanford.edu`
- Whether any `AnonymizationViolation` (exit 6) fired against real SEP HTML and the resolution if so
- Whether the rate-limit + robots.txt + User-Agent posture was acceptable to the host (no rate-limit or block events)
- Verdict-update tally: how many medium-confidence verdicts changed direction or type after fortification, and how many were corroborated

**S-0122 outcome (closed at the Phase 5 production-audit closeout):**

- **Fetches successfully completed against `plato.stanford.edu`:** 31 (of 33 queued; 2 errors were 404s on URL-slug guesses for nodes that don't have stand-alone SEP entries — `hanson` covered by `science-theory-observation`; `legitimacy-political` skipped, covered by other entries' cross-references)
- **AnonymizationViolation events:** 0 across 31 successful fetches
- **Rate-limit + robots.txt + User-Agent posture:** acceptable to the host; no rate-limit / block / 403 / 429 events; empirical rate-limit ~2.0s/fetch as configured
- **Verdict-update tally:** 30 corroborated (65%), 15 with forward link present (33%; of which 3 spurious matches, 7 relation-confirmed-but-direction-still-open, 5 genuine partial-weakening), 1 structural-only (granularity-mismatch on N-8 bayesian_epistemology)

See [`phase_5_production_audit_findings.md`](phase_5_production_audit_findings.md) §"Empirical-fortification first-exercise outcomes" for the full disposition.
