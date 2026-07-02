from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

from src import manuscript_variables as mv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# This project is developed nested inside a sibling "research-template" repo
# checkout (see README "Render the manuscript from the sibling template
# checkout"); this test exercises that template's rendering pipeline. A
# standalone clone of this repo (e.g. GitHub Actions CI, an external
# contributor) has no such sibling checkout, so the test skips rather than
# failing closed on an environment precondition it cannot control.
TEMPLATE_ROOT = PROJECT_ROOT.parents[2] / "template"


@pytest.mark.skipif(
    not TEMPLATE_ROOT.exists(),
    reason=f"sibling template checkout not present at {TEMPLATE_ROOT} (expected in a standalone clone)",
)
def test_template_hydration_writes_resolved_manuscript_tree(tmp_path):
    if str(TEMPLATE_ROOT) not in sys.path:
        sys.path.insert(0, str(TEMPLATE_ROOT))
    from infrastructure.rendering.manuscript_injection import (
        write_resolved_manuscript_tree,
    )

    project = tmp_path / "project"
    shutil.copytree(PROJECT_ROOT / "manuscript", project / "manuscript")
    variables = mv.generate_variables(PROJECT_ROOT)
    assert "CLAIM_LEDGER_COUNT" in variables

    write_resolved_manuscript_tree(project, variables)

    rendered = project / "output" / "manuscript" / "11_methods.md"
    text = rendered.read_text(encoding="utf-8")
    assert "{{" not in text
    assert "FIGURE_CAPTION" not in text
    assert "claim-ledger" in text.lower()
    assert (project / "output" / "manuscript" / "references.bib").exists()
