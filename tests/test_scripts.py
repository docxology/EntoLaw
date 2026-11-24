from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from scripts import (
    finalize_web_export,
    generate_figures,
    generate_manuscript_variables,
    run_inventory,
)


def test_declared_engine_tools_build_and_check_in_an_alternate_layout(tmp_path):
    project = Path(__file__).resolve().parents[1]
    alternate = tmp_path / "relocated" / "analysis"
    for relative in ("config", "docs/research", "src"):
        shutil.copytree(project / relative, alternate / relative, ignore=shutil.ignore_patterns("__pycache__"))
    declaration = yaml.safe_load((alternate / "config/local_validation.yaml").read_text(encoding="utf-8"))
    tooling = [
        step for step in declaration["steps"]
        if step["name"] in {"coding-review", "coding-review-check", "graphical-abstract", "graphical-abstract-check"}
    ]
    assert len(tooling) == 4
    for step in tooling:
        assert step["argv"][1:3] == ["-m", "legal_informatics.muckraker.domain_cli"]
        result = subprocess.run(
            [sys.executable, *step["argv"][1:]], cwd=alternate,
            capture_output=True, text=True, timeout=90, check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr


def test_generate_manuscript_variables_writes_canonical_data_json(tmp_path):
    out = generate_manuscript_variables.main(tmp_path)
    assert out == tmp_path / "output" / "data" / "manuscript_variables.json"
    assert out.exists()
    assert not (tmp_path / "output" / "reports" / "manuscript_variables.json").exists()
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["ROLE_COUNT"] == "8"


def test_finalize_web_export_serves_figures_from_web_dir(tmp_path):
    figures = tmp_path / "output" / "figures"
    figures.mkdir(parents=True)
    (figures / "figure.png").write_bytes(b"png")

    web_figures = finalize_web_export.ensure_web_figure_link(tmp_path)

    assert web_figures == tmp_path / "output" / "web" / "figures"
    assert web_figures.exists()
    if web_figures.is_symlink():
        assert web_figures.resolve() == figures.resolve()
    else:
        assert (web_figures / "figure.png").read_bytes() == b"png"


def test_generate_figures_writes_project_output_figures(tmp_path):
    paths = generate_figures.main(tmp_path)

    assert paths
    assert all(path.parent == tmp_path / "output" / "figures" for path in paths)
    assert (tmp_path / "output" / "figures" / "cover.png").exists()
    assert all(path.exists() and path.stat().st_size > 0 for path in paths)


def test_run_inventory_returns_zero_and_writes_reports(tmp_path):
    code = run_inventory.main(tmp_path)
    assert code == 0
    report = tmp_path / "output" / "reports" / "validation.json"
    assert json.loads(report.read_text(encoding="utf-8"))["ok"] is True
    assert (tmp_path / "output" / "reports" / "field_metrics.json").exists()
    assert (tmp_path / "output" / "data" / "roles_inventory.csv").exists()


def test_run_inventory_returns_nonzero_when_validation_fails(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "claim_ledger.yaml").write_text(
        "claims:\n"
        "  - id: bad\n"
        "    claim: bad\n"
        "    source: missing_key\n"
        "    anchor: sec:missing\n"
        "    verification:\n"
        "      status: verified\n"
        "      verified_value: value\n"
        "      source_url: https://example.org/source\n"
        "      source_quote: a sufficiently long quote\n"
        "      as_of: '2026'\n"
        "      confidence: high\n"
        "      checked: '2026-06-29'\n",
        encoding="utf-8",
    )

    code = run_inventory.main(tmp_path)

    assert code == 1
    report = json.loads(
        (tmp_path / "output" / "reports" / "validation.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["ok"] is False
    assert report["counts"]["error"] >= 1
