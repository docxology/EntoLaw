# output

The [local gate](../config/local_validation.yaml) produces the current build
outputs. Edit the corresponding source or generator to change them.

## Contents
Tracked subfolders (byte-stable across clean rebuilds of one commit):
`coding_review_v1/`, `data/`, `figures/`, `graphical_abstract_v1/`,
`manuscript/`, `pdf/`, `qa/`, `reports/`, `web/`, plus `epub/`, which holds
only the historical v1.0.0 EPUB and is not regenerated.

Ignored run-local paths (see `.gitignore`): `quality/` (per-step validation
logs), `rendered/` (the renderer's staging tree), `web/assets/` (the
regenerated web font bundle), `figures/transmission_integrity_strip.png` and
`pdf/EntoLaw_manuscript_combined.pdf` (both carry the template's wall-clock
barcode stamp).

Files: `AGENTS.md`, `README.md`

## Usage
- Regenerate with `.venv/bin/python -m legal_informatics.local_validation --project-root .`
  (see `docs/local_validation.md`). Build stamps come from `SOURCE_DATE_EPOCH`
  or the declared `paper.date`, never the wall clock.
