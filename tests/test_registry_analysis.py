"""A real curated frame keeps exclusive counts and unavailable event ages honest."""
from dataclasses import replace
import hashlib
import json

import pytest

from legal_informatics.analysis_models import AnalysisError
from src.cases import all_cases
from src.registry_analysis import analyze_registry, registry_frame_figure


def test_registry_cells_partition_actual_frame():
    records = all_cases()
    result = analyze_registry(records)
    assert sum(cell.count for cell in result.cells) == len(records)
    assert sorted(unit for cell in result.cells for unit in cell.unit_ids) == sorted(result.unit_ids)
    for cell in result.cells:
        assert cell.unit_ids == tuple("case:" + row.slug for row in records
                                      if row.jurisdiction == cell.jurisdiction and row.role == cell.role)
    year = next(row for row in result.measures if row.name == "registered_year recorded")
    assert year.numerator == year.denominator == len(records)
    assert not year.missing_ids


def test_empty_frame_has_no_invented_cells_or_observations():
    result = analyze_registry(())
    assert result.unit_ids == result.cells == ()
    assert all(row.numerator == row.denominator == 0 for row in result.measures)


def test_duplicate_and_unknown_role_refuse():
    row = all_cases()[0]
    with pytest.raises(AnalysisError, match="unique"):
        analyze_registry((row, row))
    with pytest.raises(ValueError, match="undeclared"):
        analyze_registry((replace(row, role="unknown_role"),))


def test_figure_table_is_bound_to_real_source_and_render(tmp_path):
    image = registry_frame_figure(tmp_path / "registry_frame.png")
    table = json.loads(image.with_suffix(".json").read_text())
    assert image.read_bytes().startswith(b"\x89PNG")
    assert table["figure_sha256"] == hashlib.sha256(image.read_bytes()).hexdigest()
    assert sum(row["count"] for row in table["cells"]) == table["denominator"]
    assert len(table["unit_ids"]) == len(all_cases())
    assert all(len(value) == 64 for value in table["sources"].values())
