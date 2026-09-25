"""Tests for `src.case_candidate_metrics`: the candidate-leads crosstabs.

Real-data tests run against the live tree's `data/case_candidates.yaml` and
`config/legal_issues.yaml` -- the same register `tests/test_case_candidates.py`
exercises. The edge-case tests build a small, genuinely-written `tmp_path`
project (real YAML/JSON files, no mocks) to exercise branches the live
register may not currently carry: a candidate with no recorded court, a
candidate with an unparseable filing date, and a candidate surfaced by more
than one legal issue.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from src import case_candidate_metrics as ccm

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ── pure `court_level` classification ───────────────────────────────────


def test_court_level_classifies_known_shapes():
    assert ccm.court_level("Supreme Court of the United States") == "supreme"
    assert ccm.court_level("Mississippi Supreme Court") == "supreme"
    assert ccm.court_level("Court of Appeals for the Ninth Circuit") == "appellate"
    assert ccm.court_level("Court of Special Appeals of Maryland") == "appellate"
    assert ccm.court_level("Connecticut Appellate Court") == "appellate"
    assert ccm.court_level("District Court, N.D. California") == "trial"
    assert ccm.court_level("Vermont Superior Court") == "trial"
    assert ccm.court_level("Pennsylvania Court of Common Pleas, Philadelphia County") == "trial"
    assert ccm.court_level("United States Bankruptcy Court, M.D. Florida") == "trial"


def test_court_level_stays_other_unknown_for_missing_or_unplaceable_names():
    assert ccm.court_level(None) == "other_unknown"
    assert ccm.court_level("") == "other_unknown"
    assert ccm.court_level("California Attorney General Reports") == "other_unknown"
    assert ccm.court_level("United States Court of International Trade") == "other_unknown"
    assert ccm.court_level("North Carolina Business Court") == "other_unknown"


def test_court_level_result_is_always_a_declared_bucket():
    for court in (None, "", "Supreme Court", "Court of Appeals", "District Court", "anything else"):
        assert ccm.court_level(court) in ccm.COURT_LEVELS


# ── real register: shape and totals ─────────────────────────────────────


def test_candidates_by_issue_and_court_level_covers_every_declared_issue_and_level():
    from src import case_candidates as cc

    grid = ccm.candidates_by_issue_and_court_level(PROJECT_ROOT)
    assert set(grid) == set(cc.known_issue_ids(PROJECT_ROOT))
    for levels in grid.values():
        assert set(levels) == set(ccm.COURT_LEVELS)
        assert all(isinstance(v, int) and v >= 0 for v in levels.values())


def test_candidates_by_issue_and_court_level_cell_sum_is_at_least_the_register_count():
    """A candidate is counted once per issue it was surfaced under, so the
    crosstab's total is >= the register's row count, with equality only when
    no candidate carries more than one issue_id."""
    grid = ccm.candidates_by_issue_and_court_level(PROJECT_ROOT)
    cell_total = sum(sum(levels.values()) for levels in grid.values())
    assert cell_total >= ccm.total_candidate_count(PROJECT_ROOT)


def test_candidates_by_decade_totals_the_full_register_exactly_once_each():
    """Unlike the issue crosstab, the decade distribution counts each
    candidate exactly once, so it always sums to the register's row count."""
    decades = ccm.candidates_by_decade(PROJECT_ROOT)
    assert sum(decades.values()) == ccm.total_candidate_count(PROJECT_ROOT)
    assert all(v >= 0 for v in decades.values())


def test_candidates_by_decade_keys_are_chronological_with_unknown_last():
    decades = ccm.candidates_by_decade(PROJECT_ROOT)
    keys = list(decades)
    chronological = [k for k in keys if k != "unknown"]
    assert chronological == sorted(chronological)
    if "unknown" in keys:
        assert keys[-1] == "unknown"


def test_issue_count_with_candidates_is_bounded_by_declared_issues():
    with_candidates = ccm.issue_count_with_candidates(PROJECT_ROOT)
    declared = ccm.declared_legal_issue_count(PROJECT_ROOT)
    assert 0 <= with_candidates <= declared


def test_declared_query_count_matches_the_query_registry():
    from src import case_candidates as cc

    assert ccm.declared_query_count(PROJECT_ROOT) == len(cc.load_query_registry(PROJECT_ROOT))


def test_total_candidate_count_matches_the_register():
    from src import case_candidates as cc

    register = cc.generate_register(PROJECT_ROOT)
    assert ccm.total_candidate_count(PROJECT_ROOT) == len(register.candidates)


# ── tmp_path edge cases: unknown court, unparseable date, multi-issue ────


def _write_fixture_project(root: Path) -> None:
    """A small, real, two-issue / two-query project under ``root``.

    Candidates:
      - cluster 1: found only by q1 (issue_a). Court is a real supreme court
        name; date is a clean, parseable filing date.
      - cluster 2: found only by q1 (issue_a). Court is missing (``None``)
        and date is missing (``None``).
      - cluster 3: found by BOTH q1 (issue_a) and q2 (issue_b) -- a
        multi-issue candidate. Court is a name the classifier cannot place,
        and the date is present but unparseable.
    """
    (root / "config").mkdir(parents=True)
    (root / "data" / "courtlistener_cache").mkdir(parents=True)

    (root / "config" / "legal_issues.yaml").write_text(
        "# JSON-in-yaml, same convention as the live project.\n"
        + json.dumps([{"issue_id": "issue_a"}, {"issue_id": "issue_b"}]),
        encoding="utf-8",
    )
    (root / "config" / "case_candidate_queries.yaml").write_text(
        yaml.safe_dump(
            {
                "version": "1.0",
                "queries": [
                    {"query_id": "q1", "text": "query one", "search_type": "o", "issue_id": "issue_a"},
                    {"query_id": "q2", "text": "query two", "search_type": "o", "issue_id": "issue_b"},
                ],
            }
        ),
        encoding="utf-8",
    )

    def _result(cluster_id: str, case_name: str, court: str | None, date_filed: str | None) -> dict:
        return {
            "cluster_id": cluster_id,
            "case_name": case_name,
            "court": court,
            "date_filed": date_filed,
            "absolute_url": f"/opinion/{cluster_id}/x/",
            "docket_number": "20-1",
            "citations": [],
        }

    q1_results = [
        _result("1", "A v. B", "Supreme Court of Testland", "1995-05-01"),
        _result("2", "C v. D", None, None),
        _result("3", "E v. F", "Some Unplaceable Tribunal", "not-a-date"),
    ]
    q2_results = [_result("3", "E v. F", "Some Unplaceable Tribunal", "not-a-date")]

    for query_id, text, results in (("q1", "query one", q1_results), ("q2", "query two", q2_results)):
        payload = {
            "query_id": query_id,
            "text": text,
            "search_type": "o",
            "fetched_at": "2026-01-01T00:00:00+00:00",
            "hit_count": len(results),
            "approximate": False,
            "results": results,
        }
        (root / "data" / "courtlistener_cache" / f"{query_id}.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )


def test_a_candidate_with_no_recorded_court_lands_in_other_unknown(tmp_path):
    _write_fixture_project(tmp_path)
    grid = ccm.candidates_by_issue_and_court_level(tmp_path)
    # cluster 2 (no court) and cluster 3 (unplaceable court) both land in
    # issue_a's other_unknown bucket; cluster 1 (a real supreme court) does not.
    assert grid["issue_a"]["other_unknown"] == 2
    assert grid["issue_a"]["supreme"] == 1


def test_a_multi_issue_candidate_is_counted_once_per_issue_in_the_crosstab(tmp_path):
    _write_fixture_project(tmp_path)
    grid = ccm.candidates_by_issue_and_court_level(tmp_path)
    # cluster 3 was found by both q1 (issue_a) and q2 (issue_b), so it
    # contributes one count to each issue's other_unknown cell.
    assert grid["issue_a"]["other_unknown"] == 2  # clusters 2 and 3
    assert grid["issue_b"]["other_unknown"] == 1  # cluster 3 only
    cell_total = sum(sum(levels.values()) for levels in grid.values())
    assert cell_total == 4  # 3 candidates, cluster 3 counted twice
    assert ccm.total_candidate_count(tmp_path) == 3


def test_a_missing_or_unparseable_date_filed_lands_in_the_unknown_decade(tmp_path):
    _write_fixture_project(tmp_path)
    decades = ccm.candidates_by_decade(tmp_path)
    assert decades["1990s"] == 1  # cluster 1
    assert decades["unknown"] == 2  # cluster 2 (missing) + cluster 3 (unparseable)
    # Unlike the issue crosstab, the multi-issue candidate (cluster 3) is
    # still counted exactly once here.
    assert sum(decades.values()) == 3


def test_declared_issue_with_zero_candidates_still_appears_as_a_zero_row(tmp_path):
    _write_fixture_project(tmp_path)
    # Add a third declared issue that no query targets.
    (tmp_path / "config" / "legal_issues.yaml").write_text(
        json.dumps([{"issue_id": "issue_a"}, {"issue_id": "issue_b"}, {"issue_id": "issue_c"}]),
        encoding="utf-8",
    )
    grid = ccm.candidates_by_issue_and_court_level(tmp_path)
    assert grid["issue_c"] == {level: 0 for level in ccm.COURT_LEVELS}
    assert ccm.issue_count_with_candidates(tmp_path) == 2
    assert ccm.declared_legal_issue_count(tmp_path) == 3
