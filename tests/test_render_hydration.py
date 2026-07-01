from __future__ import annotations

import shutil
import sys
from pathlib import Path

from src import manuscript_variables as mv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PROJECT_ROOT.parents[2] / "template"


def test_template_hydration_writes_resolved_manuscript_tree(tmp_path):
    assert TEMPLATE_ROOT.exists(), f"template checkout missing at {TEMPLATE_ROOT}"
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
