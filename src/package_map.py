"""Machine-readable self-description of the package: inputs, methods, outputs.

The manuscript's domain figures visualize the field; this module lets the
manuscript also visualize the *package itself*. Every count the architecture
figure and its caption use is derived from these declarations (never
hard-coded in prose), and ``tests/test_package_map.py`` binds the declarations
to the live importable modules so they cannot silently drift from the code
they describe.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: Source-of-truth registries (each emits an inventory CSV).
REGISTRIES: tuple[str, ...] = (
    "roles",
    "cases",
    "statutes",
    "species",
    "institutions",
    "timeline",
    "interconnections",
)


@dataclass(frozen=True)
class Method:
    """One pure generator method in the package pipeline."""

    name: str
    role: str


METHODS: tuple[Method, ...] = (
    Method("metrics.compute", "aggregate registry metrics"),
    Method("validation.validate_registries", "cross-registry validation"),
    Method("manuscript_variables.generate_variables", "{{TOKEN}} generation"),
    Method("claim_ledger.claim_coverage_by_anchor", "claim-ledger section coverage"),
    Method("figure_bundle.build_figures", "figure rendering"),
)

#: Inventory CSVs written by ``run_inventory`` (one per registry).
INVENTORY_CSVS: tuple[str, ...] = tuple(f"{name}_inventory.csv" for name in REGISTRIES)

#: Machine-readable report JSONs.
REPORT_JSONS: tuple[str, ...] = (
    "field_metrics.json",
    "validation.json",
)

DATA_JSONS: tuple[str, ...] = ("manuscript_variables.json",)

COVER_ART_ASSETS: tuple[str, ...] = ("cover",)


def figure_count() -> int:
    """Number of analytical figures the package renders."""
    from . import figure_captions

    return len(figure_captions.all_captions())


def input_counts() -> dict[str, int]:
    """Input-side cardinalities, keyed by display label."""
    from . import claim_ledger

    ledger_path = _PROJECT_ROOT / "data" / "claim_ledger.yaml"
    claim_count = len(claim_ledger.load_claims(ledger_path))
    return {
        "Registries": len(REGISTRIES),
        "Claim-ledger entries": claim_count,
        "Methods": len(METHODS),
    }


def output_counts() -> dict[str, int]:
    """Output-side cardinalities, keyed by display label."""
    from . import claim_ledger, manuscript_variables, validation

    token_count = len(manuscript_variables.generate_variables(_PROJECT_ROOT))
    finding_count = len(validation.validate_registries(_PROJECT_ROOT).findings)
    coverage_count = len(claim_ledger.claim_coverage_by_anchor(_PROJECT_ROOT))
    return {
        "Inventory CSVs": len(INVENTORY_CSVS),
        "Report JSONs": len(REPORT_JSONS),
        "Data JSONs": len(DATA_JSONS),
        "Cover art": len(COVER_ART_ASSETS),
        "Figures": figure_count(),
        "Manuscript tokens": token_count,
        "Claim-ledger anchors": coverage_count,
        "Validation findings": finding_count,
    }


def pipeline_stages() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Ordered ``(stage_label, node_labels)`` for the architecture figure."""
    inputs = (
        f"{len(REGISTRIES)} registries",
        "claim ledger",
        "references.bib",
    )
    methods = tuple(m.name for m in METHODS)
    outputs = (
        f"{len(INVENTORY_CSVS)} inventory CSVs",
        f"{len(REPORT_JSONS)} report JSONs",
        f"{len(DATA_JSONS)} data JSONs",
        f"{len(COVER_ART_ASSETS)} cover art asset",
        f"{figure_count()} figures",
        "manuscript PDF",
    )
    return (("Inputs", inputs), ("Methods", methods), ("Outputs", outputs))
