# AGENTS.md — `EntoLaw/output`

> Generated artifacts. Layout verified by direct listing after a clean local validation build (2026-11-16).

## Scope
- Parent project docs: `EntoLaw/AGENTS.md`. Never hand-edit generated files; change the generator and rebuild.

## Layout
Tracked: `coding_review_v1/`, `data/`, `epub/` (historical v1.0.0 only), `figures/`, `graphical_abstract_v1/`, `manuscript/`, `pdf/`, `qa/`, `reports/`, `web/`, `AGENTS.md`, `README.md`.
Ignored, run-local: `quality/`, `rendered/`, `web/assets/`, `figures/transmission_integrity_strip.png`, `pdf/EntoLaw_manuscript_combined.pdf`, `data/local_validation_receipt.json`, `data/manuscript_render_receipt.json`, `data/project_inventory.json`, `data/courtlistener/`.

## Gotchas
- A second clean build of the same commit must leave `git status --porcelain` empty; any new volatile field is a determinism defect, not a reason to ignore the file.
- The renderer rewrites `web/` wholesale, so no curated guide can live inside `web/`.
