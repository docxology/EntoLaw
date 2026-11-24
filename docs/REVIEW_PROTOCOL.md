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

Run the [declared local validation gate](local_validation.md). It builds the
inventories and figures, hydrates the manuscript, renders PDF and HTML,
finalizes web assets, and runs the non-live tests with the coverage floor.
Use the [case-candidate check](CASE_CANDIDATES.md) when reviewing cached
search material.

Inspect the rendered surfaces for unresolved manuscript tokens, raw citation
markers and broken figure references:

- `output/rendered/manuscript/<checkout-name>_manuscript_combined.pdf`
- `output/web/index.html`
- `output/data/manuscript_variables.json`
- `output/reports/validation.json`
- every captioned PNG in `output/figures/`

Run the live claim quote check only with separate network authorization.
From the provisioned project environment, use
`.venv/bin/python -m pytest -m live`. An offline receipt records the local build
and structure checks. Preserve original verification dates unless the source
was fetched and reviewed again.

The distribution declaration permits public source and forbids formal
publication. [Proofreading](../PROOFREADING.md) records the owner decisions
and review needed before considering a separate publication workflow.
