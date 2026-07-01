"""Figure orchestration: render every captioned figure plus the cover.

``FIGURE_RENDERERS`` binds each :mod:`src.figure_captions` slug to its
:mod:`src.viz` renderer; ``tests/test_figure_bundle.py`` asserts the binding is
total in both directions, so a figure can neither be captioned without being
rendered nor rendered without a caption.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from . import figure_captions, viz

# slug → renderer(out_path) -> Path
FIGURE_RENDERERS: dict[str, Callable[[Path], Path]] = {
    "roles_overview": viz.roles_overview,
    "timeline": viz.timeline_figure,
    "cases_by_role": viz.cases_by_role,
    "cases_by_jurisdiction": viz.cases_by_jurisdiction,
    "statutes_by_category": viz.statutes_by_category,
    "statutes_by_jurisdiction": viz.statutes_by_jurisdiction,
    "species_by_role": viz.species_by_role,
    "role_interconnections": viz.role_interconnections,
    "role_coverage": viz.role_coverage,
    "claim_ledger_coverage": viz.claim_ledger_coverage,
    "citation_dates": viz.citation_dates,
    "architecture": viz.architecture,
}


def captioned_slugs() -> tuple[str, ...]:
    """Return the slugs declared in the caption registry."""
    return tuple(c.slug for c in figure_captions.all_captions())


def build_figures(figures_dir: Path) -> tuple[Path, ...]:
    """Render every captioned figure plus the cover into ``figures_dir``.

    Returns the written PNG paths in deterministic slug order, cover last.
    """
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for slug in sorted(FIGURE_RENDERERS):
        renderer = FIGURE_RENDERERS[slug]
        paths.append(renderer(figures_dir / f"{slug}.png"))
    paths.append(viz.cover(figures_dir / "cover.png"))
    return tuple(paths)
