"""Determinism: registry-derived variables are stable across regeneration."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from src import manuscript_variables as mv

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_variables_are_deterministic_including_build_stamp():
    """No wall-clock exemption: the build stamp is pinned, so every token is stable."""
    a = mv.generate_variables(PROJECT_ROOT)
    b = mv.generate_variables(PROJECT_ROOT)
    assert a == b
    expected = datetime.fromtimestamp(mv.build_epoch(PROJECT_ROOT), tz=timezone.utc)
    assert a["GENERATION_TIMESTAMP"] == expected.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_build_epoch_defaults_to_declared_paper_date():
    declared = yaml.safe_load((PROJECT_ROOT / "docs/manuscript/config.yaml").read_text(encoding="utf-8"))
    day = datetime.strptime(str(declared["paper"]["date"]), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    assert mv.build_epoch(PROJECT_ROOT, environ={}) == int(day.timestamp())


def test_build_epoch_honors_source_date_epoch():
    assert mv.build_epoch(PROJECT_ROOT, environ={"SOURCE_DATE_EPOCH": " 1700000000 "}) == 1700000000


def test_build_epoch_refuses_non_numeric_source_date_epoch():
    with pytest.raises(ValueError, match="SOURCE_DATE_EPOCH"):
        mv.build_epoch(PROJECT_ROOT, environ={"SOURCE_DATE_EPOCH": "yesterday"})


def test_build_epoch_is_absent_without_manuscript_config(tmp_path):
    assert mv.build_epoch(tmp_path, environ={}) is None


def test_build_epoch_refuses_malformed_paper_date(tmp_path):
    config = tmp_path / "docs/manuscript/config.yaml"
    config.parent.mkdir(parents=True)
    config.write_text('paper:\n  date: "July 2026"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="paper.date"):
        mv.build_epoch(tmp_path, environ={})


def test_case_table_binds_one_row_per_registry_entry_in_order():
    """The table is generated from the registry: one data row per case, in the
    registry's order (binds output to source rather than to itself)."""
    from src import cases

    rows = cases.case_table_markdown().splitlines()
    data_rows = rows[2:]  # skip header + separator
    registry = cases.all_cases()
    assert len(data_rows) == len(registry)
    for row, case in zip(data_rows, registry):
        assert case.name in row
        assert case.citation in row


def test_statute_table_binds_one_row_per_registry_entry_in_order():
    from src import statutes

    rows = statutes.statute_table_markdown().splitlines()
    data_rows = rows[2:]
    registry = statutes.all_statutes()
    assert len(data_rows) == len(registry)
    for row, statute in zip(data_rows, registry):
        assert statute.citation in row


def test_field_metrics_json_regenerates_identically(tmp_path):
    """Write the metrics report twice and diff: catches any ordering
    nondeterminism in the registry-derived aggregation (real regeneration)."""
    import json
    from dataclasses import asdict

    from src import metrics

    a = json.dumps(asdict(metrics.compute()), sort_keys=True)
    b = json.dumps(asdict(metrics.compute()), sort_keys=True)
    (tmp_path / "a.json").write_text(a, encoding="utf-8")
    (tmp_path / "b.json").write_text(b, encoding="utf-8")
    assert (tmp_path / "a.json").read_text() == (tmp_path / "b.json").read_text()
