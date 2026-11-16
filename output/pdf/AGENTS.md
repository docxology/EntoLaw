# AGENTS.md — `EntoLaw/output/pdf`

> PDF render products. Layout verified by direct listing after a clean local validation build (2026-11-16).

## Scope
- Parent docs: `EntoLaw/output/AGENTS.md`.

## Layout
Tracked: `EntoLaw_combined.pdf` (historical v1.0.0 record, never regenerated), `_combined_manuscript.{md,tex,aux,bbl,toc}`, `references.bib`, `AGENTS.md`, `README.md`. Ignored: `*.log`, `*.blg`, `EntoLaw_manuscript_combined.pdf` (current local render).

## Gotchas
- Never overwrite `EntoLaw_combined.pdf`: it is the published v1.0.0 artifact bound to its DOI.
- `scripts/render_manuscript.py` pins `SOURCE_DATE_EPOCH`, so the PDF text, `/CreationDate` and trailer `/ID` are stable; only the bookend barcode strip (pages 1 and last) still carries the template's wall-clock stamp, which is why the render PDF is not tracked.
