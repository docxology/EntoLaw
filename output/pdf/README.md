# pdf

PDF render products for `EntoLaw`.

## Contents
- `EntoLaw_manuscript_combined.pdf` — the current local render (`scripts/render_manuscript.py`), ignored: its bookend barcode strip carries the template's wall-clock stamp. Formal publication is forbidden by `config/manuscript_metadata.yaml`.
- `EntoLaw_combined.pdf` — the historical v1.0.0 version of record (DOI-bearing, 2026-07-02); kept as-is and not regenerated.
- `_combined_manuscript.{md,tex,aux,bbl,toc}`, `references.bib` — deterministic LaTeX inputs and intermediates of the current render.
- `AGENTS.md`, `README.md`.

LaTeX/biber logs (`*.log`, `*.blg`) and the current render PDF are run-local and ignored.

## Usage
- See `EntoLaw/output/README.md` for how this directory is produced and used.
