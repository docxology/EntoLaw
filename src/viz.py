# entolaw-size-ok: source-owned figure adapter layer; renders EntoLaw's registries through the engine's figure harnesses.
"""EntoLaw's figure layer: registries in, PNGs out.

Every generic rendering mechanic — axes styling, bar/heatmap harnesses,
network and pipeline diagrams, citation-date panels, and the build pipeline
itself — lives in ``legal_informatics`` (``viz_theme``, ``viz_bars``,
``viz_timeline``, ``viz_network``, ``viz_citation_dates``,
``figure_bundle``, ``package_map``). This module supplies only what is
EntoLaw's own: the domain palettes, the registry-driven data each figure
plots, and the caption→renderer binding that ``tests/test_figures.py``
asserts stays total.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from legal_informatics.figure_bundle import (
    build_figures as _engine_build_figures,
    captioned_slugs as _engine_captioned_slugs,
)
from legal_informatics.package_map import Method, build_package_map
from legal_informatics.viz_bars import (
    claim_coverage_bars,
    coverage_heatmap,
    grouped_bars,
    horizontal_bars,
)
from legal_informatics.viz_citation_dates import (
    CitationPanel,
    citation_dates as _render_citation_dates,
)
from legal_informatics.viz_network import (
    NetworkLink,
    circular_network,
    pipeline_diagram,
)
from legal_informatics.viz_timeline import EraBand, Milestone, milestone_timeline
from legal_informatics.viz_theme import FALLBACK_COLOR

from . import (
    cases,
    claim_ledger,
    interconnections,
    metrics,
    roles,
    species,
    timeline,
)
from .figure_caption_records import FIGURE_CAPTIONS
from .viz_citation_date_records import (
    DATE_BANDS,
    FAMILY_COLORS,
    FAMILY_ORDER,
    FOCAL_CALLOUTS,
    PRE_2000_BRIDGE_CALLOUT_KEYS,
    SOURCE_FAMILIES,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_REFERENCES_BIB = _PROJECT_ROOT / "docs" / "manuscript" / "references.bib"

# ── Domain palettes (EntoLaw vocabulary; the engine stays palette-free) ─────
ROLE_COLORS: dict[str, str] = {
    "witness": "#1f77b4",
    "threat": "#d62728",
    "protected": "#2ca02c",
    "property": "#9467bd",
    "invention": "#ff7f0e",
    "defendant": "#8c564b",
    "moral_patient": "#e377c2",
    "weapon": "#7f7f7f",
}

EVIDENCE_KIND_COLORS: dict[str, str] = {
    "cases": "#2563eb",
    "statutes": "#059669",
    "species": "#f59e0b",
    "milestones": "#7c3aed",
}

JURISDICTION_COLORS: dict[str, str] = {
    "US-federal": "#1d4ed8",
    "US-state": "#0f766e",
    "EU": "#7c3aed",
    "UK": "#be123c",
    "India": "#c2410c",
    "USSR": "#b91c1c",
    "international": "#334155",
    "Canada": "#dc2626",
    "England & Wales": "#9333ea",
    "U.S. patent": "#ea580c",
    "U.S. Supreme Court": "#0f172a",
    "U.S. federal appellate": "#2563eb",
    "U.S. state": "#0f766e",
}

CATEGORY_COLORS: dict[str, str] = {
    "forensic": "#2563eb",
    "quarantine": "#dc2626",
    "conservation": "#16a34a",
    "property": "#9333ea",
    "biotech_ip": "#ea580c",
    "food": "#f59e0b",
    "welfare": "#db2777",
    "public_health": "#0891b2",
    "warfare": "#475569",
}

ANCHOR_COLORS: dict[str, str] = {
    "witness": ROLE_COLORS["witness"],
    "threat": ROLE_COLORS["threat"],
    "protected": ROLE_COLORS["protected"],
    "property": ROLE_COLORS["property"],
    "invention": ROLE_COLORS["invention"],
    "defendant": ROLE_COLORS["defendant"],
    "welfare": ROLE_COLORS["moral_patient"],
    "weapon": ROLE_COLORS["weapon"],
    "interconnections": "#334155",
}

# Edge colour per interconnection theme (the role-interconnections figure).
_THEME_COLORS: dict[str, str] = {
    "definitional_problem": "#94a3b8",
    "expert_testimony_bridge": "#2563eb",
    "biotech_pivot": "#ea580c",
    "property_conservation_mirror": "#16a34a",
    "ancient_modern_rhyme": "#7c3aed",
}


def _role_label(slug: str) -> str:
    """Reader-facing label for a role slug."""
    return roles.find(slug).title


# ── Bar and heatmap figures ────────────────────────────────────────────────
def roles_overview(path: Path) -> Path:
    """Grouped bar of each role's case / statute / species / milestone counts."""
    return grouped_bars(
        path,
        metrics.role_coverage_matrix(),
        rows=[(r.slug, r.title) for r in roles.all_roles()],
        kinds=[
            ("cases", "Cases"),
            ("statutes", "Statutes"),
            ("species", "Species"),
            ("milestones", "history"),
        ],
        kind_colors=EVIDENCE_KIND_COLORS,
        title="Evidence profile of each legal role",
        ylabel="Registry entries",
    )


def _counted_by_role(counts: dict[str, int], title: str, xlabel: str, path: Path) -> Path:
    role_list = roles.all_roles()
    return horizontal_bars(
        path,
        [r.title for r in role_list],
        [counts[r.slug] for r in role_list],
        title=title,
        xlabel=xlabel,
        colors=[ROLE_COLORS[r.slug] for r in role_list],
    )


def cases_by_role(path: Path) -> Path:
    """Bar of case counts per role."""
    return _counted_by_role(cases.counts_by_role(), "Registered cases by legal role", "Cases", path)


def species_by_role(path: Path) -> Path:
    """Bar of taxa counts per role."""
    return _counted_by_role(species.counts_by_role(), "Insect taxa by legal role", "Taxa", path)


def _metrics_bar(
    attribute: str, title: str, palette: dict[str, str], fallback: str, path: Path
) -> Path:
    m = metrics.compute()
    items = [(k, v) for k, v in getattr(m, attribute).items() if v > 0]
    return horizontal_bars(
        path,
        [k for k, _ in items],
        [v for _, v in items],
        title=title,
        xlabel="Instruments",
        colors=[palette.get(k, fallback) for k, _ in items],
        sort_by_value=True,
    )


def cases_by_jurisdiction(path: Path) -> Path:
    """Bar of case counts per jurisdiction."""
    m = metrics.compute()
    items = [(k, v) for k, v in m.cases_by_jurisdiction.items() if v > 0]
    return horizontal_bars(
        path,
        [k for k, _ in items],
        [v for _, v in items],
        title="Registered cases by jurisdiction",
        xlabel="Cases",
        colors=[JURISDICTION_COLORS.get(k, FALLBACK_COLOR) for k, _ in items],
        sort_by_value=True,
    )


def statutes_by_category(path: Path) -> Path:
    """Bar of statute counts per category."""
    return _metrics_bar(
        "statutes_by_category",
        "Statutes and treaties by category",
        CATEGORY_COLORS,
        "#0f766e",
        path,
    )


def statutes_by_jurisdiction(path: Path) -> Path:
    """Bar of statute counts per jurisdiction."""
    return _metrics_bar(
        "statutes_by_jurisdiction",
        "Statutes and treaties by jurisdiction",
        JURISDICTION_COLORS,
        "#0369a1",
        path,
    )


def role_coverage(path: Path) -> Path:
    """Heatmap of roles against evidence kinds."""
    kinds = ("cases", "statutes", "species", "milestones")
    coverage = metrics.role_coverage_matrix()
    role_list = roles.all_roles()
    grid = [[coverage[r.slug][k] for k in kinds] for r in role_list]
    return coverage_heatmap(
        path,
        grid,
        [r.title for r in role_list],
        [k.capitalize() for k in kinds],
        title="Role coverage matrix with evidence totals",
    )


def claim_ledger_coverage(path: Path) -> Path:
    """Bar of quote-backed claim-ledger entries per manuscript section."""
    return claim_coverage_bars(
        path,
        claim_ledger.claim_coverage_by_anchor(_PROJECT_ROOT),
        palette=ANCHOR_COLORS,
        title="Live-checkable claim coverage by manuscript section",
        xlabel="Quote-backed claim-ledger entries",
    )


# ── Timeline figure ────────────────────────────────────────────────────────
#: Milestone title → ``(callout label, offset)``; untitled entries stay plain.
_TIMELINE_CALLOUTS: dict[str, tuple[str, tuple[int, int]]] = {
    "Hittite Laws on bees and hives": ("Hittite\nhives", (0, 15)),
    "Mishnah on beehives and nuisance": ("Mishnah\nbees", (0, -18)),
    "Salic Law on stolen bees": ("Salic\nbee theft", (-30, 15)),
    "Justinian on bee property": ("Roman\nbees", (36, 25)),
    "Rothari on hives and bee trees": ("Rothari\nhives", (0, -18)),
    "The Sickle Murder": ("Sickle\nMurder", (0, 9)),
    "Fleta on bee occupation": ("Fleta\nbees", (0, 9)),
    "Weevils of St-Julien (sequel)": ("weevils\npreserve", (0, 9)),
    "Virginia silk-input mandate": ("VA silk\ninputs", (0, 9)),
    "Blackstone on hived bees": ("Blackstone\nbees", (0, 9)),
    "UK Destructive Insects Act": ("UK pest\norders", (0, 13)),
    "Plant Quarantine Act": ("US plant\nquarantine", (-38, -22)),
    "Biological Weapons Convention": ("BWC", (30, 9)),
    "Diamond v. Chakrabarty": ("Chakrabarty", (0, 9)),
    "Monarch proposal and screwworm detection": ("monarch\n+ screwworm", (0, 9)),
    "Kirstin Lobato exoneration": ("Lobato\nexoneration", (30, 18)),
}

#: Shaded era spans: ``(start, end, label, color, label_frac)``.
_ERA_BANDS: tuple[tuple[int, int, str, str, float], ...] = (
    (-1700, 500, "ancient\napiculture law", "#fff7ed", 0.5),
    (500, 1800, "pre-modern\nproperty, trials + silk", "#f8fafc", 0.5),
    (1800, 1970, "evidence\n+ property", "#eef6ff", 0.16),
    (1970, 2027, "modern regulation\n+ welfare", "#f0fdf4", 0.5),
)


def _timeline_milestones() -> list[Milestone]:
    mapped: list[Milestone] = []
    for ms in timeline.all_milestones():
        callout = _TIMELINE_CALLOUTS.get(ms.title)
        if callout is None:
            mapped.append(Milestone(row=ms.role, year=ms.year, title=ms.title))
        else:
            mapped.append(Milestone(ms.role, ms.year, ms.title, callout[0], callout[1]))
    return mapped


def timeline_figure(path: Path) -> Path:
    """Scatter of milestones by year, lane and colour by role."""
    role_order = list(roles.role_slugs())
    era_bands = tuple(
        EraBand(
            start,
            end,
            label,
            color,
            label_frac,
            label_row=len(role_order) - (1.75 if start >= 1970 else 0.35),
        )
        for start, end, label, color, label_frac in _ERA_BANDS
    )
    return milestone_timeline(
        path,
        _timeline_milestones(),
        role_order,
        [_role_label(slug) for slug in role_order],
        ROLE_COLORS,
        era_bands=era_bands,
        title="Milestones by legal role",
    )


# ── Network and pipeline figures ───────────────────────────────────────────
def role_interconnections(path: Path) -> Path:
    """Circular network of roles linked by interconnection themes."""
    role_list = list(roles.role_slugs())
    links = [
        NetworkLink(
            key=link.slug,
            label=(
                f"{link.theme} (touches "
                + ("all" if set(link.roles) == set(role_list) else f"{len(link.roles)} of {len(role_list)}")
                + " roles)"
                if link.slug == "definitional_problem"
                else link.theme
            ),
            members=tuple(link.roles),
            color=_THEME_COLORS[link.slug],
            linewidth=0.9 if link.slug == "definitional_problem" else 2.0,
            alpha=0.16 if link.slug == "definitional_problem" else 0.55,
            curvature=0.08 if link.slug == "definitional_problem" else None,
        )
        for link in interconnections.all_interconnections()
    ]
    return circular_network(
        path,
        nodes=role_list,
        node_labels={slug: _role_label(slug) for slug in role_list},
        node_colors=ROLE_COLORS,
        links=links,
        node_degrees=interconnections.role_link_degree(),
        hub_label="status\nmigration",
        hub_note="node number = linked themes",
        title="Interconnection themes across legal roles",
        note="Edge colour = shared theme; node size and number = how many themes touch that role.",
    )


def architecture(path: Path) -> Path:
    """Three-column inputs → methods → outputs pipeline diagram."""
    return pipeline_diagram(
        path,
        pipeline_stages(),
        title="Package architecture: source registries to rendered outputs",
    )


# ── Citation-dates figure (bibliography family tables stay in EntoLaw) ─────
#: EntoLaw's three strips: pre-1700, the 1700-1999 bridge, and 2000+.
_CITATION_PANELS: tuple[CitationPanel, ...] = (
    CitationPanel(
        None,
        1700,
        "Pre-1700 legal-historical, regulatory, and scientific foundations",
    ),
    CitationPanel(
        1700,
        2000,
        "1700-1999 scholarship, statutes, and case-law consolidation",
        callout_keys=frozenset(PRE_2000_BRIDGE_CALLOUT_KEYS),
    ),
    CitationPanel(
        2000,
        None,
        "2000+ current law, official sources, and live scholarship",
        annotate_focal=False,
    ),
)


def citation_dates(path: Path) -> Path:
    """Multi-panel citation-dates figure from ``references.bib``."""
    return _render_citation_dates(
        _REFERENCES_BIB,
        path,
        panels=_CITATION_PANELS,
        families=SOURCE_FAMILIES,
        family_order=FAMILY_ORDER,
        family_colors=FAMILY_COLORS,
        date_bands=DATE_BANDS,
        focal_callouts=FOCAL_CALLOUTS,
    )


# ── Package surface (declared here; counts derived by the engine) ──────────
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

METHODS: tuple[Method, ...] = (
    Method("metrics.compute", "aggregate registry metrics"),
    Method("validation.validate_registries", "cross-registry validation"),
    Method("manuscript_variables.generate_variables", "{{TOKEN}} generation"),
    Method("claim_ledger.claim_coverage_by_anchor", "claim-ledger section coverage"),
    Method("viz.build_figures", "figure rendering"),
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

#: Output filename groups declared for the engine's package mapping.
PACKAGE_OUTPUTS: dict[str, tuple[str, ...]] = {
    "Inventory CSVs": INVENTORY_CSVS,
    "Report JSONs": REPORT_JSONS,
    "Data JSONs": DATA_JSONS,
    "Cover art": COVER_ART_ASSETS,
    "Figures": tuple(caption.slug for caption in FIGURE_CAPTIONS),
}

_BASE_PACKAGE_MAP = build_package_map(REGISTRIES, METHODS, PACKAGE_OUTPUTS)


def figure_count() -> int:
    """Number of analytical figures the package renders."""
    return len(FIGURE_CAPTIONS)


def input_counts() -> dict[str, int]:
    """Input-side cardinalities, keyed by display label."""
    counts = dict(_BASE_PACKAGE_MAP["input_counts"])
    counts["Claim-ledger entries"] = len(
        claim_ledger.load_claims(_PROJECT_ROOT / "data" / "claim_ledger.yaml")
    )
    return counts


def output_counts() -> dict[str, int]:
    """Output-side cardinalities, keyed by display label."""
    from . import manuscript_variables, validation  # lazy: breaks the import cycle

    counts = dict(_BASE_PACKAGE_MAP["output_counts"])
    counts["Manuscript tokens"] = len(
        manuscript_variables.generate_variables(_PROJECT_ROOT)
    )
    counts["Claim-ledger anchors"] = len(
        claim_ledger.claim_coverage_by_anchor(_PROJECT_ROOT)
    )
    counts["Validation findings"] = len(
        validation.validate_registries(_PROJECT_ROOT).findings
    )
    return counts


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


# ── Caption→renderer binding ───────────────────────────────────────────────
# slug → renderer(out_path) -> Path
FIGURE_RENDERERS: dict[str, Callable[[Path], Path]] = {
    "roles_overview": roles_overview,
    "timeline": timeline_figure,
    "cases_by_role": cases_by_role,
    "cases_by_jurisdiction": cases_by_jurisdiction,
    "statutes_by_category": statutes_by_category,
    "statutes_by_jurisdiction": statutes_by_jurisdiction,
    "species_by_role": species_by_role,
    "role_interconnections": role_interconnections,
    "role_coverage": role_coverage,
    "claim_ledger_coverage": claim_ledger_coverage,
    "citation_dates": citation_dates,
    "architecture": architecture,
}


def captioned_slugs() -> tuple[str, ...]:
    """Return the slugs declared in the caption registry."""
    return _engine_captioned_slugs(FIGURE_CAPTIONS)


def build_figures(figures_dir: Path) -> tuple[Path, ...]:
    """Render every captioned figure plus the cover into ``figures_dir``.

    Returns the written PNG paths in deterministic slug order, cover last.
    """
    return _engine_build_figures(
        figures_dir,
        list(FIGURE_RENDERERS.items()),
        captions=FIGURE_CAPTIONS,
        cover_renderer=cover,
    )


__all__ = [
    "ANCHOR_COLORS",
    "CATEGORY_COLORS",
    "COVER_ART_ASSETS",
    "DATA_JSONS",
    "EVIDENCE_KIND_COLORS",
    "FIGURE_RENDERERS",
    "INVENTORY_CSVS",
    "JURISDICTION_COLORS",
    "METHODS",
    "PACKAGE_OUTPUTS",
    "REGISTRIES",
    "REPORT_JSONS",
    "ROLE_COLORS",
    "architecture",
    "build_figures",
    "captioned_slugs",
    "cases_by_jurisdiction",
    "cases_by_role",
    "citation_dates",
    "claim_ledger_coverage",
    "cover",
    "figure_count",
    "input_counts",
    "output_counts",
    "pipeline_stages",
    "role_coverage",
    "role_interconnections",
    "roles_overview",
    "species_by_role",
    "statutes_by_category",
    "statutes_by_jurisdiction",
    "timeline_figure",
]


# Imported last: viz_cover reads this module's ROLE_COLORS at its own import
# time, so the palettes above must already be bound.
from .viz_cover import cover  # noqa: E402
