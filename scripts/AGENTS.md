# AGENTS.md — `EntoLaw/scripts`

Thin-orchestrator contract for the scripts of this project (2026-09 scripts
audit remediation).

## Contract

- `scripts/` holds thin orchestrators ONLY: path bootstrap (shared
  `PROJECT_ROOT` / `sys.path` pattern), logging/printing, and a single
  delegated call into `src.*` entrypoints.
- Business, data, plot, and analysis logic lives in `src/` — importable and
  tested under `tests/`.
- Scripts never import other scripts: shared logic is promoted into `src/` and
  both call sites delegate to it (e.g. `compute_and_save` in
  `src.manuscript_variables`, used by both manuscript-variable entry points).
- Serialization helpers used by scripts (e.g. CSV writing in
  `src.io_helpers`) live in `src/`, not inline in a script.
- Any logic that outgrows bootstrap/delegation moves to `src/` with tests.

## Inventory

| Script | Delegates to | Output |
|--------|--------------|--------|
| `run_inventory.py` | `src.io_helpers`, `src.metrics`, `src.validation`, registry modules | `output/data/*_inventory.csv`, `output/reports/field_metrics.json`, `output/reports/validation.json` |
| `generate_manuscript_variables.py` | `src.manuscript_variables.compute_and_save` | `output/data/manuscript_variables.json` |
| `z_generate_manuscript_variables.py` | `src.manuscript_variables.compute_and_save`, `infrastructure.rendering.manuscript_injection` | `output/data/manuscript_variables.json` + injected `output/manuscript/*` |
| `generate_figures.py` | `src.figure_bundle.build_figures` | `output/figures/*.png` |
| `finalize_web_export.py` | — | `output/web/figures` (symlink or copy) |

## Testing

- `uv run pytest -m "not live"` covers the delegating entrypoints via
  `tests/test_scripts.py` and the promoted logic (e.g. `tests/test_io_helpers.py`,
  `tests/test_manuscript_variables.py`).
- Live-checkable claims are gated separately with `uv run pytest -m live`
  (see the parent `AGENTS.md` for the full gate list).
