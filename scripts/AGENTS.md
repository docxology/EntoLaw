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
- Serialization helpers used by scripts (CSV writing in
  `legal_informatics.io_helpers`) live in the engine, not inline in a script.
- Any logic that outgrows bootstrap/delegation moves to `src/` with tests.

## Inventory

| Script | Delegates to | Output |
|--------|--------------|--------|
| `run_inventory.py` | `legal_informatics.io_helpers`, `src.metrics`, `src.validation`, registry modules | `output/data/*_inventory.csv`, `output/reports/field_metrics.json`, `output/reports/validation.json` |
| `generate_manuscript_variables.py` | `src.manuscript_variables.compute_and_save` | `output/data/manuscript_variables.json` |
| `z_generate_manuscript_variables.py` | `src.manuscript_variables.compute_and_save`, `infrastructure.rendering.manuscript_injection` | `output/data/manuscript_variables.json` + injected `output/manuscript/*` |
| `generate_figures.py` | `src.viz.build_figures` (binding + domain renderers over `legal_informatics.figure_bundle`) | `output/figures/*.png` |
| `finalize_web_export.py` | — | `output/web/figures` (symlink or copy) |
| `scrape_updates.py` | `legal_informatics.legal_updates`, `legal_informatics.legal_updates_ingestion` | `output/data/legal_updates_discovery.json` (+ ingestion state ledger under `output/data/legal_updates_store/`) |
| `check_module_map.py` | `legal_informatics.module_map` | Checks/rewrites `src/AGENTS.md` against `src/` and `config/module_groups.yaml` |
| `check_docs_inventory.py` | `legal_informatics.inventory`, `legal_informatics.privacy_labels` | `output/data/project_inventory.json` |
| `check_metadata_consistency.py` | — | Compares version/title/license/keywords/authors/DOI across `pyproject.toml`, `CITATION.cff`, `codemeta.json`, `.zenodo.json`, `docs/manuscript/config.yaml` against `CITATION.cff` as the declared source; no output file, exit code only |
| `check_release_boundary.py` | — | Scans every git-tracked file for credentials, non-public emails, absolute local paths, internal hostnames, private-repo references, and oversized binaries; no output file, exit code only |
| `fetch_case_candidate_queries.py` | `legal_informatics.courtlistener_client`, `legal_informatics.courtlistener_search`, `src.case_candidates.build_cache_payload` | `data/courtlistener_cache/<query_id>.json` (network-touching; the only script in this pair that opens a socket) |
| `generate_case_candidates.py` | `src.case_candidates` | `data/case_candidates.yaml` (offline; `--check` verifies without rewriting) |

## Testing

- `uv run pytest -m "not live"` covers the delegating entrypoints via
  `tests/test_scripts.py` and the promoted logic (e.g. `tests/test_io_helpers.py`,
  `tests/test_manuscript_variables.py`).
- Live-checkable claims are gated separately with `uv run pytest -m live`
  (see the parent `AGENTS.md` for the full gate list).
