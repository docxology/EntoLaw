# scripts

Thin orchestrator scripts for the EntoLaw project. Business, data, and plot
logic lives in `src/` (importable and tested); each script only does path
bootstrap, logging, and a single delegated call.

## Inventory

| Script | Purpose | Delegates to | Command |
|--------|---------|--------------|---------|
| `run_inventory.py` | Emit one inventory CSV per registry, `field_metrics.json`, and `validation.json` | `legal_informatics.io_helpers.write_csv`, `src.metrics.compute`, `src.validation.validate_registries`, registry modules | `uv run python scripts/run_inventory.py` |
| `generate_manuscript_variables.py` | Compute manuscript variables and save them as JSON (no injection) | `src.manuscript_variables.compute_and_save` | `uv run python scripts/generate_manuscript_variables.py` |
| `z_generate_manuscript_variables.py` | Render-pipeline hydrator: save variables JSON, then substitute every `{{TOKEN}}` into `output/manuscript/` | `src.manuscript_variables.compute_and_save`, `infrastructure.rendering.manuscript_injection.write_resolved_manuscript_tree` | Run by the renderer before PDF/HTML rendering |
| `generate_figures.py` | Render all registry-derived figures | `src.viz.build_figures` (domain renderers over `legal_informatics.figure_bundle`) | `uv run python scripts/generate_figures.py` |
| `finalize_web_export.py` | Publish rendered figures into the web export tree (symlink or copy) | — | `uv run python scripts/finalize_web_export.py` |
| `scrape_updates.py` | Describe/parse/discover legal-update feeds, then optionally ingest them into the idempotent state ledger | `legal_informatics.legal_updates`, `legal_informatics.legal_updates_ingestion` | `uv run python scripts/scrape_updates.py describe` |
| `check_module_map.py` | Check (or `--write`) the `src/AGENTS.md` module map against `src/` and `config/module_groups.yaml` | `legal_informatics.module_map` | `uv run python scripts/check_module_map.py` |
| `check_docs_inventory.py` | Regenerate the project inventory; fail on broken/escaping/absolute doc links | `legal_informatics.inventory`, `legal_informatics.privacy_labels` | `uv run python scripts/check_docs_inventory.py` |
| `check_metadata_consistency.py` | Check version/title/license/keywords/authors/DOI agree across `pyproject.toml`, `CITATION.cff`, `codemeta.json`, `.zenodo.json`, `docs/manuscript/config.yaml` (against `CITATION.cff` as the declared source) | — | `uv run python scripts/check_metadata_consistency.py` |
| `check_release_boundary.py` | Scan the git-tracked tree for credentials, non-public emails, absolute local paths, internal hostnames, private-repo references, and oversized binaries | — | `uv run python scripts/check_release_boundary.py` |

Outputs land under `output/data/`, `output/reports/`, `output/figures/`, and
`output/web/`; the entrypoints print each written path.
