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
`src/figure_captions.py`, a renderer in `src/figure_bundle.py`, and a non-empty
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

Then render from the sibling template checkout:

```bash
cd /Users/4d/Documents/GitHub/template
uv run python scripts/03_render_pdf.py --project working/EntoLaw
cd /Users/4d/Documents/GitHub/projects/working/EntoLaw
uv run python scripts/finalize_web_export.py
```

Confirm the rendered surfaces exist and contain no unresolved manuscript
tokens, raw citation markers, or broken figure references:

- `output/pdf/EntoLaw_combined.pdf`
- `output/web/index.html`
- `output/data/manuscript_variables.json`
- `output/reports/validation.json`
- every captioned `output/figures/*.png`
