# EntoLaw — A Field Map of Entomological Law

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21137276.svg)](https://doi.org/10.5281/zenodo.21137276)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/docxology/EntoLaw)](https://github.com/docxology/EntoLaw/releases)

A source-anchored, reproducible reference for **entomological law** (legal
entomology): the synthetic field where insects and the legal system collide.
The reference is organized around eight registered legal **roles** an insect can
occupy — witness, regulated threat, protected subject, property, invention,
defendant, moral patient, and weapon — while leaving room for other roles a
larger field map could add. It binds those roles to a machine-readable
registry of cases, statutes, species, institutions, historical milestones, and
cross-domain interconnections.

It is built on the research-template's two-layer, thin-orchestrator,
claim-sourced pattern: all domain knowledge lives in source-of-truth registries
under `src/`, every count in the
manuscript is generated from those registries, legal propositions are
source-bound in the bibliography, and every externally-sourced numeral is bound to a
verifiable quote in a claim ledger.

## What's here

| Path | Contents |
| --- | --- |
| `src/roles.py` | Registered legal roles (the manuscript spine) |
| `src/cases.py` | Landmark decisions (Daubert, Almond Alliance, Chakrabarty, …) |
| `src/statutes.py` | Statutes, regulations, treaties across nine categories |
| `src/species.py` | Insect taxa by role (lanternfly, monarch, Oxitec mosquito, trial weevils, …) |
| `src/institutions.py` | Certifying and regulatory bodies (ABFE, APHIS, USFWS, EFSA, …) |
| `src/timeline.py` | Long historical arc of milestones (533 → 2026) |
| `src/interconnections.py` | The recurring themes that link the roles |
| `src/manuscript_variables.py` | `{{TOKEN}}` generation (no hard-coded prose numbers) |
| `src/claim_ledger.py` + `data/claim_ledger.yaml` | External-statistic verification |
| `src/viz.py`, `src/figure_bundle.py` | Deterministic matplotlib figures |
| `manuscript/` | Modular, token-injected manuscript (abstract → conclusion) |
| `docs/ACCURACY_METHODOLOGY.md` | What the offline gates prove vs. the live oracle |
| `docs/REVIEW_PROTOCOL.md` | Deep-review checklist and final gate sequence |

## Quick start

```bash
uv sync                                   # or: uv run ...
uv run ruff check .                       # lint gate
uv run pytest -m "not live"               # full offline suite (90%+ coverage on src/)
uv run pytest -m live                     # live claim-ledger oracle (network)
uv run python scripts/run_inventory.py    # inventories, metrics, validation report
uv run python scripts/generate_figures.py # render all figures
```

Render the manuscript from the sibling template checkout (the project is a
symlinked `projects/working/` project):

```bash
cd /Users/4d/Documents/GitHub/template
uv run python scripts/03_render_pdf.py --project working/EntoLaw
```

## Guarantees and their limits

The offline test suite guarantees the manuscript's *internal* numbers are
generated from the registries and cannot drift, and that every numeral-form
external statistic is attributed and well-formed. The claim ledger also covers
volatile current-status claims that the manuscript needs to preserve. Only
`uv run pytest -m live` confirms that the ledger's quotes still appear at their
sources. See [`docs/ACCURACY_METHODOLOGY.md`](docs/ACCURACY_METHODOLOGY.md)
and [`docs/REVIEW_PROTOCOL.md`](docs/REVIEW_PROTOCOL.md) for the full boundary.
The registries are curated to anchor each role with its leading authorities —
they are not a census of the entire field, and every figure caption states that
scope.

## Citation

Cite via [`CITATION.cff`](CITATION.cff), or:

```bibtex
@software{friedman2026entomologicallaw,
  title   = {Entomological Law},
  author  = {Friedman, Daniel Ari},
  year    = {2026},
  version = {1.0.0},
  doi     = {10.5281/zenodo.21137276},
  url     = {https://github.com/docxology/EntoLaw}
}
```

**Concept DOI** (always resolves to the latest version): [10.5281/zenodo.21137276](https://doi.org/10.5281/zenodo.21137276)
**v1.0.0 record:** [10.5281/zenodo.21137277](https://doi.org/10.5281/zenodo.21137277) · [GitHub release](https://github.com/docxology/EntoLaw/releases/tag/v1.0.0)

Licensed under [CC-BY-4.0](LICENSE).
