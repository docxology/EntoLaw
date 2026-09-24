"""Tests for the CourtListener case-candidate register.

Real-data throughout: the live query registry, the real recorded responses
under ``data/courtlistener_cache/``, and — for the cache-payload shaping test
— a real ``legal_informatics.courtlistener_search.SearchPage`` parsed from a
real (small, hand-written but genuinely JSON) provider response body via the
engine's own ``parse_search_response``. No mocks and no patched HTTP anywhere
in this file, matching ``AGENTS.md``'s "No mocks" convention.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from legal_informatics.courtlistener_search import parse_search_response
from src import case_candidates as cc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATE_SCRIPT = PROJECT_ROOT / "scripts" / "generate_case_candidates.py"
FETCH_SCRIPT = PROJECT_ROOT / "scripts" / "fetch_case_candidate_queries.py"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )


# ── query registry ──────────────────────────────────────────────────────


def test_query_registry_loads_and_declares_at_least_one_query_per_issue():
    queries = cc.load_query_registry(PROJECT_ROOT)
    assert len(queries) >= 8
    issue_ids = {q.issue_id for q in queries}
    known = cc.known_issue_ids(PROJECT_ROOT)
    assert issue_ids <= known, f"declared issue_id(s) not in config/legal_issues.yaml: {issue_ids - known}"
    # Every declared legal issue is targeted by at least one query.
    assert known <= issue_ids, f"legal issue(s) with no case-candidate query: {known - issue_ids}"


def test_query_ids_are_unique_and_query_registry_rejects_a_duplicate(tmp_path):
    queries = cc.load_query_registry(PROJECT_ROOT)
    ids = [q.query_id for q in queries]
    assert len(ids) == len(set(ids))

    bad = tmp_path
    (bad / "config").mkdir()
    (bad / "config" / "case_candidate_queries.yaml").write_text(
        "version: '1.0'\n"
        "queries:\n"
        "  - query_id: dup\n"
        "    text: foo\n"
        "    search_type: o\n"
        "    issue_id: some_issue\n"
        "  - query_id: dup\n"
        "    text: bar\n"
        "    search_type: o\n"
        "    issue_id: some_issue\n",
        encoding="utf-8",
    )
    with pytest.raises(cc.CaseCandidateError, match="declared twice"):
        cc.load_query_registry(bad)


def test_query_registry_rejects_missing_required_field(tmp_path):
    bad = tmp_path
    (bad / "config").mkdir()
    (bad / "config" / "case_candidate_queries.yaml").write_text(
        "version: '1.0'\nqueries:\n  - query_id: incomplete\n    text: foo\n",
        encoding="utf-8",
    )
    with pytest.raises(cc.CaseCandidateError):
        cc.load_query_registry(bad)


def test_query_registry_missing_file_raises(tmp_path):
    with pytest.raises(cc.CaseCandidateError, match="not found"):
        cc.load_query_registry(tmp_path)


# ── cached responses (real recorded data) ───────────────────────────────


def test_every_declared_query_has_a_cached_response():
    queries = cc.load_query_registry(PROJECT_ROOT)
    responses = cc.load_all_cached_responses(PROJECT_ROOT, queries)
    assert len(responses) == len(queries)
    for query, response in zip(queries, responses):
        assert response.query_id == query.query_id
        assert response.text == query.text
        assert response.fetched_at  # a real ISO-8601 timestamp was recorded


def test_cached_response_missing_file_raises(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "case_candidate_queries.yaml").write_text(
        yaml.safe_dump(
            {
                "version": "1.0",
                "queries": [
                    {
                        "query_id": "nope",
                        "text": "anything",
                        "search_type": "o",
                        "issue_id": "some_issue",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    queries = cc.load_query_registry(tmp_path)
    with pytest.raises(cc.CaseCandidateError, match="no cached response"):
        cc.load_cached_response(tmp_path, queries[0])


def test_cached_response_stale_text_raises(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "case_candidate_queries.yaml").write_text(
        yaml.safe_dump(
            {
                "version": "1.0",
                "queries": [
                    {
                        "query_id": "q1",
                        "text": "new query text",
                        "search_type": "o",
                        "issue_id": "some_issue",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    cache_dir = tmp_path / "data" / "courtlistener_cache"
    cache_dir.mkdir(parents=True)
    (cache_dir / "q1.json").write_text(
        json.dumps({"query_id": "q1", "text": "old query text", "search_type": "o", "results": []}),
        encoding="utf-8",
    )
    queries = cc.load_query_registry(tmp_path)
    with pytest.raises(cc.CaseCandidateError, match="query text disagrees"):
        cc.load_cached_response(tmp_path, queries[0])


# ── building / merging ──────────────────────────────────────────────────


def _query(query_id: str, issue_id: str, text: str = "x") -> cc.CandidateQuery:
    return cc.CandidateQuery(query_id=query_id, text=text, search_type="o", issue_id=issue_id, note="")


def _result(cluster_id: str | None, case_name: str = "A v. B") -> cc.CachedResult:
    return cc.CachedResult(
        cluster_id=cluster_id,
        case_name=case_name,
        court="Some Court",
        date_filed="2020-01-01",
        absolute_url=f"/opinion/{cluster_id}/a-v-b/" if cluster_id else None,
        docket_number="20-1",
        citations=(),
    )


def test_build_candidate_register_dedups_across_queries_and_merges_issue_ids():
    q1 = _query("q1", "issue_a")
    q2 = _query("q2", "issue_b")
    shared = _result("111")
    response1 = cc.CachedQueryResponse(
        query_id="q1", text="x", search_type="o", fetched_at="t1", hit_count=1, approximate=False, results=(shared,)
    )
    response2 = cc.CachedQueryResponse(
        query_id="q2", text="x", search_type="o", fetched_at="t2", hit_count=1, approximate=False, results=(shared,)
    )
    register = cc.build_candidate_register((q1, q2), (response1, response2))
    assert len(register.candidates) == 1
    candidate = register.candidates[0]
    assert candidate.candidate_id == "cl-111"
    assert candidate.query_ids == ("q1", "q2")
    assert candidate.issue_ids == ("issue_a", "issue_b")
    assert candidate.status == cc.STATUS_CANDIDATE


def test_build_candidate_register_keeps_distinct_clusters_separate():
    q1 = _query("q1", "issue_a")
    response = cc.CachedQueryResponse(
        query_id="q1",
        text="x",
        search_type="o",
        fetched_at="t1",
        hit_count=2,
        approximate=False,
        results=(_result("111"), _result("222")),
    )
    register = cc.build_candidate_register((q1,), (response,))
    assert {c.candidate_id for c in register.candidates} == {"cl-111", "cl-222"}


def test_build_candidate_register_gives_a_missing_cluster_id_a_deterministic_fallback_key():
    q1 = _query("q1", "issue_a")
    result = _result(None, case_name="No Cluster Case")
    response = cc.CachedQueryResponse(
        query_id="q1", text="x", search_type="o", fetched_at="t1", hit_count=1, approximate=False, results=(result,)
    )
    register_a = cc.build_candidate_register((q1,), (response,))
    register_b = cc.build_candidate_register((q1,), (response,))
    assert register_a.candidates[0].candidate_id == register_b.candidates[0].candidate_id
    assert register_a.candidates[0].candidate_id.startswith("nc-")


def test_build_candidate_register_rejects_mismatched_queries_and_responses():
    q1 = _query("q1", "issue_a")
    response = cc.CachedQueryResponse(
        query_id="different", text="x", search_type="o", fetched_at="t1", hit_count=0, approximate=False, results=()
    )
    with pytest.raises(cc.CaseCandidateError):
        cc.build_candidate_register((q1,), (response,))


def test_every_candidate_carries_status_candidate_never_verified():
    with pytest.raises(cc.CaseCandidateError):
        cc.CaseCandidate(
            candidate_id="x",
            cluster_id="1",
            case_name="n",
            court="c",
            date_filed="d",
            url="u",
            query_ids=("q1",),
            issue_ids=("issue_a",),
            status="verified",
        )


# ── rendering / determinism ─────────────────────────────────────────────


def test_render_candidate_register_is_deterministic_across_rebuilds():
    register_a = cc.generate_register(PROJECT_ROOT)
    register_b = cc.generate_register(PROJECT_ROOT)
    assert cc.render_candidate_register(register_a) == cc.render_candidate_register(register_b)


def test_committed_register_matches_its_declared_inputs():
    """The live tree's data/case_candidates.yaml is exactly what its declared
    inputs (config/case_candidate_queries.yaml + data/courtlistener_cache/)
    produce right now — the same assertion --check makes."""
    assert cc.check_register(PROJECT_ROOT) == []


def test_committed_register_never_contains_the_word_verified():
    path = PROJECT_ROOT / cc.REGISTER_RELPATH
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    for candidate in payload["candidates"]:
        assert candidate["status"] == "candidate"
    # Belt and suspenders: the literal string never appears as a value.
    rendered = path.read_text(encoding="utf-8")
    assert "status: verified" not in rendered


def test_committed_register_every_query_id_and_issue_id_is_consistent():
    path = PROJECT_ROOT / cc.REGISTER_RELPATH
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    declared_query_ids = {q["query_id"] for q in payload["queries"]}
    known_issues = cc.known_issue_ids(PROJECT_ROOT)
    for candidate in payload["candidates"]:
        assert set(candidate["query_ids"]) <= declared_query_ids
        assert set(candidate["issue_ids"]) <= known_issues


# ── boundary: never feeds the manuscript or the claim ledger ───────────


def test_case_candidates_is_not_referenced_by_the_manuscript_or_claim_ledger():
    manuscript_dir = PROJECT_ROOT / "docs" / "manuscript"
    for path in manuscript_dir.glob("*.md"):
        assert "case_candidates" not in path.read_text(encoding="utf-8")
    claim_ledger_text = (PROJECT_ROOT / "data" / "claim_ledger.yaml").read_text(encoding="utf-8")
    assert "case_candidates" not in claim_ledger_text
    case_records_text = (PROJECT_ROOT / "src" / "case_records.py").read_text(encoding="utf-8")
    assert "case_candidates" not in case_records_text


def test_case_candidates_module_is_not_imported_by_validation_or_manuscript_variables():
    for module_name in ("validation.py", "manuscript_variables.py"):
        text = (PROJECT_ROOT / "src" / module_name).read_text(encoding="utf-8")
        assert "case_candidates" not in text


# ── cache-payload shaping (real SearchPage, no mocks) ───────────────────


def test_build_cache_payload_shapes_a_real_parsed_search_page():
    body = json.dumps(
        {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "caseName": "Example v. Widget",
                    "cluster_id": 555,
                    "court": "Some Circuit",
                    "dateFiled": "2019-05-01",
                    "absolute_url": "/opinion/555/example-v-widget/",
                    "docketNumber": "19-1",
                    "citation": ["1 F.4th 1"],
                },
                {
                    "caseName": "Second Example",
                    "cluster_id": 556,
                    "court": "Some Circuit",
                    "dateFiled": "2019-06-01",
                    "absolute_url": "/opinion/556/second-example/",
                },
            ],
        }
    ).encode("utf-8")
    page = parse_search_response(body, search_type="o")
    query = _query("q1", "issue_a", text="whatever")
    payload = cc.build_cache_payload(query, page, fetched_at="2026-01-01T00:00:00+00:00")

    assert payload["query_id"] == "q1"
    assert payload["hit_count"] == 2
    assert payload["approximate"] is False
    assert len(payload["results"]) == 2
    first = payload["results"][0]
    assert first["case_name"] == "Example v. Widget"
    assert first["cluster_id"] == "555"
    assert first["citations"] == ["1 F.4th 1"]

    # And the shaped payload round-trips through the same loader used for a
    # real cache file on disk.
    cached = cc._load_cached_result(first, Path("irrelevant"))
    assert cached.case_name == "Example v. Widget"
    assert cached.cluster_id == "555"


# ── CLI (subprocess, real files) ────────────────────────────────────────


def test_generate_case_candidates_check_is_clean_on_the_live_tree():
    result = _run(GENERATE_SCRIPT, "--check")
    assert result.returncode == 0, result.stderr
    assert "0 drift finding(s)" in result.stdout


def test_generate_case_candidates_rewrite_reproduces_the_committed_file(tmp_path):
    """Running the generator against a fresh copy of the live inputs reproduces
    the exact committed bytes -- the real regenerate-from-scratch path."""
    import shutil

    work = tmp_path / "proj"
    (work / "config").mkdir(parents=True)
    (work / "data" / "courtlistener_cache").mkdir(parents=True)
    shutil.copy(PROJECT_ROOT / "config" / "case_candidate_queries.yaml", work / "config")
    for cache_file in (PROJECT_ROOT / "data" / "courtlistener_cache").glob("*.json"):
        shutil.copy(cache_file, work / "data" / "courtlistener_cache")

    result = _run(GENERATE_SCRIPT, "--project-root", str(work))
    assert result.returncode == 0, result.stderr
    written = (work / "data" / "case_candidates.yaml").read_text(encoding="utf-8")
    committed = (PROJECT_ROOT / "data" / "case_candidates.yaml").read_text(encoding="utf-8")
    assert written == committed


def test_generate_case_candidates_check_reports_drift_when_missing(tmp_path):
    import shutil

    work = tmp_path / "proj"
    (work / "config").mkdir(parents=True)
    (work / "data" / "courtlistener_cache").mkdir(parents=True)
    shutil.copy(PROJECT_ROOT / "config" / "case_candidate_queries.yaml", work / "config")
    for cache_file in (PROJECT_ROOT / "data" / "courtlistener_cache").glob("*.json"):
        shutil.copy(cache_file, work / "data" / "courtlistener_cache")

    result = _run(GENERATE_SCRIPT, "--check", "--project-root", str(work))
    assert result.returncode == 1
    assert "drift finding" in result.stdout
    assert "missing" in result.stderr


def test_fetch_script_without_network_lists_and_opens_no_socket():
    """Without --network the fetch script performs no I/O beyond reading the
    registry and cache directory: every declared query is already cached on
    the live tree, so it reports nothing pending."""
    result = _run(FETCH_SCRIPT)
    assert result.returncode == 0, result.stderr
    assert "nothing to fetch" in result.stdout


def test_fetch_script_lists_a_query_missing_from_the_cache(tmp_path):
    import shutil

    work = tmp_path / "proj"
    (work / "config").mkdir(parents=True)
    (work / "data" / "courtlistener_cache").mkdir(parents=True)
    shutil.copy(PROJECT_ROOT / "config" / "case_candidate_queries.yaml", work / "config")
    # No cache files copied: every declared query is pending.
    result = _run(FETCH_SCRIPT, "--project-root", str(work))
    assert result.returncode == 0, result.stderr
    assert "would be fetched" in result.stdout
    assert "--network" in result.stdout
