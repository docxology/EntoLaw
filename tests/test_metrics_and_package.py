"""Tests for metrics aggregation, package self-description, and figure captions."""

from __future__ import annotations

from pathlib import Path

import pytest

from src import (
    cases,
    claim_ledger,
    figure_captions,
    manuscript_variables as mv,
    metrics,
    package_map,
    roles,
    species,
    statutes,
    timeline,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "manuscript"


def test_metrics_match_registries():
    m = metrics.compute()
    assert m.role_count == len(roles.all_roles())
    assert m.case_count == len(cases.all_cases())
    assert m.statute_count == len(statutes.all_statutes())
    assert m.species_count == len(species.all_taxa())
    assert m.milestone_count == len(timeline.all_milestones())
    assert m.roles_with_case_law == sum(
        1 for v in cases.counts_by_role().values() if v > 0
    )


def test_role_coverage_matrix_shape():
    matrix = metrics.role_coverage_matrix()
    assert set(matrix) == set(roles.role_slugs())
    for cell in matrix.values():
        assert set(cell) == {"cases", "statutes", "species", "milestones"}
    # cases total across roles equals registry case count
    assert sum(c["cases"] for c in matrix.values()) == len(cases.all_cases())


def test_package_map_declarations_match_modules():
    # Every named registry module is importable.
    import importlib

    for name in package_map.REGISTRIES:
        importlib.import_module(f"src.{name}")
    assert package_map.figure_count() == len(figure_captions.all_captions())
    assert len(package_map.INVENTORY_CSVS) == len(package_map.REGISTRIES)
    assert package_map.REPORT_JSONS == ("field_metrics.json", "validation.json")
    assert package_map.DATA_JSONS == ("manuscript_variables.json",)


def test_facade_modules_document_reexports():
    from src import viz

    for name in claim_ledger.__all__:
        assert hasattr(claim_ledger, name), name
    for name in viz.__all__:
        assert hasattr(viz, name), name
    assert "load_claims" in claim_ledger.__all__
    assert "roles_overview" in viz.__all__


def test_package_map_counts():
    ins = package_map.input_counts()
    outs = package_map.output_counts()
    assert ins["Registries"] == len(package_map.REGISTRIES)
    assert ins["Claim-ledger entries"] == len(
        claim_ledger.load_claims(PROJECT_ROOT / "data" / "claim_ledger.yaml")
    )
    assert outs["Figures"] == package_map.figure_count()
    assert outs["Report JSONs"] == len(package_map.REPORT_JSONS)
    assert outs["Data JSONs"] == len(package_map.DATA_JSONS)
    assert outs["Cover art"] == len(package_map.COVER_ART_ASSETS)
    assert outs["Claim-ledger anchors"] == len(
        claim_ledger.claim_coverage_by_anchor(PROJECT_ROOT)
    )
    stages = package_map.pipeline_stages()
    assert [s[0] for s in stages] == ["Inputs", "Methods", "Outputs"]
    method_stage = dict(stages)["Methods"]
    assert tuple(m.name for m in package_map.METHODS) == method_stage
    assert "claim_ledger.claim_coverage_by_anchor" in method_stage
    assert any("data JSON" in label for label in dict(stages)["Outputs"])
    assert any("cover art" in label for label in dict(stages)["Outputs"])


def test_caption_contract_is_satisfied():
    anchors = mv.manuscript_anchor_inventory(MANUSCRIPT)
    fig_anchors = {a for a in anchors if a.startswith("fig:")}
    errors = figure_captions.caption_contract_errors(
        figure_captions.all_captions(), fig_anchors
    )
    assert not errors, errors


def test_caption_tokens_resolve_fully():
    variables = mv.generate_variables(PROJECT_ROOT)
    tokens = figure_captions.caption_tokens(variables)
    assert not figure_captions.unresolved_caption_placeholders(tokens)
    assert variables["CLAIM_LEDGER_COUNT"] == str(
        len(claim_ledger.load_claims(PROJECT_ROOT / "data" / "claim_ledger.yaml"))
    )
    assert (
        figure_captions.caption_by_slug("timeline").token_name
        == "FIGURE_CAPTION_TIMELINE"
    )
    assert figure_captions.caption_by_anchor("fig:timeline").slug == "timeline"
    with pytest.raises(KeyError):
        figure_captions.caption_by_slug("nope")
    with pytest.raises(KeyError):
        figure_captions.caption_by_anchor("fig:nope")


def test_caption_contract_detects_missing_caption():
    errors = figure_captions.caption_contract_errors(
        figure_captions.all_captions(), {"fig:does_not_exist"}
    )
    assert any("missing caption for fig:does_not_exist" in e for e in errors)


def test_caption_quality_contracts_are_reader_facing():
    for caption in figure_captions.all_captions():
        assert caption.alt_text.strip().endswith(".")
        assert len(caption.alt_text.split()) >= 7
        assert caption.provenance.startswith("Generated from ")
        assert caption.caveat
        assert "Read as:" in caption.manuscript_caption
        assert "Why it matters:" in caption.manuscript_caption
        assert "Provenance:" in caption.manuscript_caption
        assert "Caveat:" in caption.manuscript_caption


def test_claim_ledger_coverage_figure_is_source_owned():
    caption = figure_captions.caption_by_slug("claim_ledger_coverage")
    assert caption.anchor == "fig:claim_ledger_coverage"
    assert caption.token_name == "FIGURE_CAPTION_CLAIM_LEDGER_COVERAGE"
