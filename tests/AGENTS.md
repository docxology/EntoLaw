# AGENTS.md — `EntoLaw/tests`

> `tests/` of the parent project. Verified by direct listing (fleet doc pass, 2026-08-29).

## Scope
- Local-only path under `projects/ongoing/` — matched by the root `.gitignore`
  rule `projects/*`; never commit, add, or push anything here.
- Parent standard: the `AGENTS.md` of the lifecycle directory this project sits in; parent project docs: `EntoLaw/AGENTS.md`.

## Layout
Files: `AGENTS.md`, `README.md`, `__init__.py`, `conftest.py`, `test_bibliography.py`, `test_case_candidate_metrics.py`, `test_case_candidates.py`, `test_citations.py`, `test_claim_ledger.py`, `test_courtlistener_watch_and_alerts.py`, `test_figures.py`, `test_idempotency.py`, `test_live_claim_sources.py`, `test_manuscript_no_hardcoded_stats.py`, `test_manuscript_variables.py`, `test_metrics_and_package.py`, `test_publication_readiness.py`, `test_registries.py`, `test_release_boundary.py`, `test_render_hydration.py`, `test_scripts.py`, `test_validation.py`

> Note (added while adding `test_case_candidate_metrics.py`): this list was
> stale before this edit -- `test_case_candidates.py`, `test_release_boundary.py`,
> and `test_courtlistener_watch_and_alerts.py` already existed on disk but were
> missing here. Left as a known pre-existing gap in the rest of this file's
> prose (module-count references etc.); out of scope for this change.

## Kind
- Category: **src**. `tests/` of the parent project.

## Agent notes
- See the parent project's AGENTS.md/README.md for the authoritative description.

## Gotchas
- None beyond the local-only rule above.
