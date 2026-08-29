# AGENTS.md — EntoLaw docs/

## Scope
Guidance for agents working in this documentation directory.

## Layout
- `README.md` — human entry point; repo purpose, layout, run/test commands copied from `pyproject.toml`
- `ACCURACY_METHODOLOGY.md` — registry-to-manuscript accuracy contract
- `REVIEW_PROTOCOL.md` — claim and citation review protocol

## Conventions observed in this repo
- Manuscript prose contains `{{TOKEN}}` placeholders by design; they are
  substituted at render time from registry-derived variables
  (`scripts/generate_manuscript_variables.py`, `scripts/z_generate_manuscript_variables.py`).
  Never hard-code numbers into prose.
- Registry-derived facts must remain `{{TOKEN}}` values or registry-backed text
  (see REVIEW_PROTOCOL.md).
- Business logic lives in `src/`; `scripts/` files are thin orchestrators.

## Maintenance
Keep this index current when files are added or removed. Only factual claims
traceable to repo files belong here.
