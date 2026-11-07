from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

from legal_informatics.pipeline_plan import find_template_root
from src import manuscript_variables as mv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Discover the actual declared template instead of an obsolete ancestor layout.

TEMPLATE_ROOT = find_template_root([PROJECT_ROOT])


@pytest.mark.skipif(
    TEMPLATE_ROOT is None,
    reason="declared template checkout is unavailable in this standalone environment",
)

def test_template_hydration_writes_resolved_manuscript_tree(tmp_path):
    assert TEMPLATE_ROOT is not None
    if str(TEMPLATE_ROOT) not in sys.path:
        sys.path.insert(0, str(TEMPLATE_ROOT))
    from infrastructure.rendering.manuscript_injection import (
        write_resolved_manuscript_tree,
    )

    project = tmp_path / "project"
    shutil.copytree(
        PROJECT_ROOT / "docs" / "manuscript", project / "docs" / "manuscript"
    )
    variables = mv.generate_variables(PROJECT_ROOT)
    assert "CLAIM_LEDGER_COUNT" in variables

    write_resolved_manuscript_tree(project, variables)

    opening = project / "output" / "manuscript" / "00_abstract.md"
    assert opening.read_text().count("graphical_abstract_v1.png") == 1

    rendered = project / "output" / "manuscript" / "11_methods.md"
    text = rendered.read_text(encoding="utf-8")
    assert "{{" not in text
    assert "FIGURE_CAPTION" not in text
    assert "claim-ledger" in text.lower()
    assert (project / "output" / "manuscript" / "references.bib").exists()
