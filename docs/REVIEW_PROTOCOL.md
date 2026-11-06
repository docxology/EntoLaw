# Review Protocol

Use this protocol for manuscript, registry, and release-readiness passes.

## Accuracy Pass

Read every manuscript section against the registries under `src/` and the
external claims in `data/claim_ledger.yaml`.

- Registry-derived facts must stay as `{{TOKEN}}` values or registry-backed
  tables.
- External statistics and volatile current-status claims must have a claim
  ledger entry with a real bibliography key, declared manuscript anchor,
  source URL, short quote, `as_of`, `confidence`, and `checked`.
- Broad synthesis wording must name its boundary: encoded registry, cited
  source, jurisdiction, or as-of date.
- Do not describe the registries as exhaustive.

## Figure And Output Pass

Every figure referenced in the manuscript must have a caption record in
`src/figure_caption_records.py`, a renderer bound in `src/viz.py`, and a non-empty
PNG in `output/figures/`.

Captions must include reader-facing provenance and caveats. The claim-ledger
coverage figure is the package-level check that shows where quote-backed claims
sit across the manuscript sections.

## Final Gates

Run these before claiming the package is ready:

```bash
uv run ruff check .
uv run python scripts/run_inventory.py
uv run python scripts/generate_figures.py
uv run pytest -m "not live" --cov=src --cov-fail-under=90
uv run pytest -m live
```

Then render locally using the declared template:

```bash
.venv/bin/python scripts/z_generate_manuscript_variables.py
.venv/bin/python scripts/render_manuscript.py
.venv/bin/python scripts/finalize_web_export.py
```

The renderer uses the template's actual RenderManager and writes a source-bound
local receipt; it does not run a publishing stage. A missing template fails the
declared render step. The source distribution declaration is public/forbidden:
public source metadata and historical DOIs do not authorize a new formal release.

Confirm the rendered surfaces exist and contain no unresolved manuscript
tokens, raw citation markers, or broken figure references:

- `output/rendered/manuscript/EntoLaw_manuscript_combined.pdf`
- `output/web/index.html`
- `output/data/manuscript_variables.json`
- `output/reports/validation.json`
- every captioned `output/figures/*.png`
