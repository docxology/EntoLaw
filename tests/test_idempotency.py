"""Determinism: registry-derived variables are stable across regeneration."""

from __future__ import annotations

from pathlib import Path

from src import manuscript_variables as mv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_PROVENANCE = {"GENERATION_TIMESTAMP"}


def test_variables_are_deterministic_modulo_provenance():
    a = mv.generate_variables(PROJECT_ROOT)
    b = mv.generate_variables(PROJECT_ROOT)
    a2 = {k: v for k, v in a.items() if k not in _PROVENANCE}
    b2 = {k: v for k, v in b.items() if k not in _PROVENANCE}
    assert a2 == b2


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
