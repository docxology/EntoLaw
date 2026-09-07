# scripts

Thin orchestrator scripts for the EntoLaw project. Business, data, and plot
logic lives in `src/` (importable and tested); each script only does path
bootstrap, logging, and a single delegated call.

## Inventory

| Script | Purpose | Delegates to | Command |
|--------|---------|--------------|---------|
| `run_inventory.py` | Emit one inventory CSV per registry, `field_metrics.json`, and `validation.json` | `src.io_helpers.write_csv`, `src.metrics.compute`, `src.validation.validate_registries`, registry modules | `uv run python scripts/run_inventory.py` |
| `generate_manuscript_variables.py` | Compute manuscript variables and save them as JSON (no injection) | `src.manuscript_variables.compute_and_save` | `uv run python scripts/generate_manuscript_variables.py` |
| `z_generate_manuscript_variables.py` | Render-pipeline hydrator: save variables JSON, then substitute every `{{TOKEN}}` into `output/manuscript/` | `src.manuscript_variables.compute_and_save`, `infrastructure.rendering.manuscript_injection.write_resolved_manuscript_tree` | Run by the renderer before PDF/HTML rendering |
| `generate_figures.py` | Render all registry-derived figures | `src.figure_bundle.build_figures` | `uv run python scripts/generate_figures.py` |
| `finalize_web_export.py` | Publish rendered figures into the web export tree (symlink or copy) | — | `uv run python scripts/finalize_web_export.py` |

Outputs land under `output/data/`, `output/reports/`, `output/figures/`, and
`output/web/`; the entrypoints print each written path.
