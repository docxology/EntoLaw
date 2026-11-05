"""Finite-frame analysis of the curated public decision/patent registry."""
from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from legal_informatics.analysis_models import CountMeasure, Observation, RecordedDate, UnitId
from legal_informatics.descriptive_analysis import describe_population
from legal_informatics.privacy_labels import write_labelled_json

from .case_records import Case
from .cases import all_cases
from .roles import LEGAL_ROLES


@dataclass(frozen=True, slots=True)
class RegistryCell:
    """One mutually exclusive jurisdiction/role cell with its exact members."""

    jurisdiction: str
    role: str
    count: int
    unit_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RegistryAnalysis:
    """Curated coverage, with no estimate of the universe of legal disputes."""

    unit_ids: tuple[str, ...]
    jurisdictions: tuple[str, ...]
    roles: tuple[str, ...]
    measures: tuple[CountMeasure, ...]
    cells: tuple[RegistryCell, ...]


def analyze_registry(records: Sequence[Case]) -> RegistryAnalysis:
    """Adapt real registry entries to the engine's located descriptive API."""
    observations = tuple(
        Observation(
            unit_id=UnitId("case:" + row.slug),
            group=row.jurisdiction,
            status=row.role,
            age_days=None,
            dates=(RecordedDate("registered_year", str(row.year),
                                "curated_registry_year_precision", "src/case_records.py#" + row.slug),),
            locator="src/case_records.py#" + row.slug,
        ) for row in records
    )
    measures = describe_population(observations)
    jurisdictions = tuple(sorted({row.jurisdiction for row in records}))
    roles = tuple(role.slug for role in LEGAL_ROLES)
    unknown = {row.role for row in records} - set(roles)
    if unknown:
        raise ValueError("registry contains an undeclared legal role")
    cells = tuple(
        RegistryCell(jurisdiction, role, len(members), members)
        for jurisdiction in jurisdictions for role in roles
        for members in [tuple("case:" + row.slug for row in records
                              if row.jurisdiction == jurisdiction and row.role == role)]
    )
    return RegistryAnalysis(tuple(str(row.unit_id) for row in observations),
                            jurisdictions, roles, measures, cells)


def registry_frame_figure(path: Path) -> Path:
    """Render a labelled cross-tab and an adjacent source-bound data table."""
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    from legal_informatics import analysis_models, descriptive_analysis
    from legal_informatics.viz_theme import _save

    result = analyze_registry(all_cases())
    cell_map = {(row.jurisdiction, row.role): row.count for row in result.cells}
    values = [[cell_map[(jurisdiction, role)] for role in result.roles]
              for jurisdiction in result.jurisdictions]
    fig, ax = plt.subplots(figsize=(12, 6.4))
    image = ax.imshow(values, cmap="Blues", vmin=0, aspect="auto")
    ax.set_xticks(range(len(result.roles)), [role.replace("_", "\n") for role in result.roles])
    ax.set_yticks(range(len(result.jurisdictions)), result.jurisdictions)
    maximum = max(cell_map.values())
    for y, line in enumerate(values):
        for x, value in enumerate(line):
            ax.text(x, y, str(value), ha="center", va="center",
                    color="white" if value > maximum / 2 else "#172033", fontsize=11)
    ax.set_title(f"Curated decisions and patents: jurisdiction × registered role\n"
                 f"Selected frame N={len(result.unit_ids)}; each cell counts registry entries", pad=16)
    ax.set_xlabel("Registry category; one principal role per entry")
    colorbar = fig.colorbar(image, ax=ax, label="Entries in the selected registry")
    colorbar.locator = MaxNLocator(nbins=5, integer=True)
    colorbar.update_ticks()
    fig.text(0.02, 0.02,
             "Zero = no encoded entry in this cell. Registry absence is not absence of law or records.\n"
             "A curated holding summary is not a fresh opinion reading; decision year is year precision only.",
             fontsize=9, color="#475569")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    source_files = {
        "src/case_records.py": Path(__file__).with_name("case_records.py"),
        "src/roles.py": Path(__file__).with_name("roles.py"),
        "src/registry_analysis.py": Path(__file__),
        "engine/analysis_models.py": Path(analysis_models.__file__),
        "engine/descriptive_analysis.py": Path(descriptive_analysis.__file__),
    }
    table = {
        "schema_version": 1,
        "unit": "curated_decision_or_patent_entry",
        "frame": "src.case_records.CASES as encoded in this source revision",
        "date_basis": "curated registry year; not an event or request date",
        "denominator": len(result.unit_ids),
        "unit_ids": result.unit_ids,
        "display_fields": {"group": "jurisdiction", "status": "registered legal role"},
        "measures": [asdict(row) for row in result.measures],
        "cells": [asdict(row) for row in result.cells],
        "limits": ["Selected curated frame; no population inference",
                   "No agency request, production, disclosure or legal-compliance measure",
                   "No source-opinion reading inferred from a registry summary"],
        "sources": {name: hashlib.sha256(source.read_bytes()).hexdigest()
                    for name, source in source_files.items()},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    _save(fig, path)
    table["figure_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    write_labelled_json(
        Path(__file__).resolve().parents[1], "output/figures/registry_frame.json", table,
        destination=path.with_suffix(".json"),
    )
    return path
