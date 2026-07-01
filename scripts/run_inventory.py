#!/usr/bin/env python3
"""Emit registry inventory CSVs, field metrics, and the validation report.

Thin orchestrator over the ``src/`` registries and validators. Writes one CSV
per registry under ``output/data/`` plus ``field_metrics.json`` and
``validation.json`` under ``output/reports/``. Prints each written path.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
for _p in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from src import (  # noqa: E402
    cases,
    institutions,
    interconnections,
    metrics,
    roles,
    species,
    statutes,
    timeline,
    validation,
)


def _write_csv(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _flatten(v) for k, v in row.items()})
    return path


def _flatten(value):
    if isinstance(value, (list, tuple)):
        return "; ".join(str(v) for v in value)
    return value


def write_inventory(project_root: Path = PROJECT_ROOT) -> tuple[list[Path], validation.ValidationSummary]:
    data_dir = project_root / "output" / "data"
    reports_dir = project_root / "output" / "reports"
    written: list[Path] = []

    registries = {
        "roles": [asdict(r) for r in roles.all_roles()],
        "cases": [asdict(c) for c in cases.all_cases()],
        "statutes": [asdict(s) for s in statutes.all_statutes()],
        "species": [asdict(t) for t in species.all_taxa()],
        "institutions": [asdict(i) for i in institutions.all_institutions()],
        "timeline": [asdict(m) for m in timeline.all_milestones()],
        "interconnections": [
            asdict(x) for x in interconnections.all_interconnections()
        ],
    }
    for name, rows in registries.items():
        written.append(_write_csv(data_dir / f"{name}_inventory.csv", rows))

    metrics_path = reports_dir / "field_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(
        json.dumps(asdict(metrics.compute()), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    written.append(metrics_path)

    summary = validation.validate_registries(project_root)
    written.append(
        validation.write_validation_report(summary, reports_dir / "validation.json")
    )

    return written, summary


def main(project_root: Path = PROJECT_ROOT) -> int:
    written, summary = write_inventory(project_root)
    for path in written:
        print(path)
    if not summary.ok:
        print("VALIDATION FAILED: see validation.json", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
