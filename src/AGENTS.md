# AGENTS.md — `EntoLaw/src`

> `src/` of the parent project. Verified by direct listing (fleet doc pass, 2026-08-29).

## Scope
- Local-only path under `projects/ongoing/` — matched by the root `.gitignore`
  rule `projects/*`; never commit, add, or push anything here.
- Parent standard: the `AGENTS.md` of the lifecycle directory this project sits in; parent project docs: `EntoLaw/AGENTS.md`.

## Layout
Files: `AGENTS.md`, `README.md`, `__init__.py`, `case_candidate_cache.py`, `case_candidate_metrics.py`, `case_candidates.py`, `case_records.py`, `cases.py`, `citations.py`, `claim_ledger.py`, `claim_ledger_loading.py`, `claim_ledger_models.py`, `claim_ledger_validation.py`, `figure_caption_records.py`, `institutions.py`, `interconnections.py`, `manuscript_variables.py`, `metrics.py`, `roles.py`, `species.py`, `statute_records.py`, `statutes.py`, `taxon_records.py`, `timeline.py`, `validation.py`, `viz.py`, `viz_citation_date_records.py`, `viz_cover.py` — 28 files total

- `case_candidates.py` — CourtListener case-CANDIDATE register:
  builds/renders/checks `data/case_candidates.yaml` from the inputs read by
  `case_candidate_cache.py` (the query registry `config/case_candidate_queries.yaml`,
  the recorded responses in `data/courtlistener_cache/`, and their record types;
  split out for the publication size gate, re-exported by `case_candidates`). Every row is
  `status: candidate`; nothing here can write `verified`. See
  `docs/CASE_CANDIDATES.md`.
- `case_candidate_metrics.py` — pure cross-tabs over the candidate register for
  the candidate-leads figure: candidates per declared legal issue by
  conservatively-derived court level (`court_level`), and candidates by filing
  decade. Reads `case_candidates` and `config/legal_issues.yaml` only; writes
  nothing and cannot promote a row past `status: candidate`. The only module
  through which `manuscript_variables.py` and `viz.py` ever see candidate
  data — see `docs/CASE_CANDIDATES.md`'s "Surfaced, never promoted" section.

## Kind
- Category: **src**. `src/` of the parent project.

## Agent notes
- See the parent project's AGENTS.md/README.md for the authoritative description.

## Gotchas
- None beyond the local-only rule above.
