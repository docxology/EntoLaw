# data

`data/` of the parent project.

Part of `EntoLaw` (EntoTech lane, local-only under `projects/ongoing/`).

## Contents
Files: `AGENTS.md`, `README.md`, `claim_ledger.yaml`, `case_candidates.yaml`,
`courtlistener_cache/`

## Usage
- See `EntoLaw/README.md` for how this directory is produced and used.
- `case_candidates.yaml` and `courtlistener_cache/` are the CourtListener
  case-candidate register; see `docs/CASE_CANDIDATES.md` for what it is, how
  to rebuild it (`scripts/fetch_case_candidate_queries.py`,
  `scripts/generate_case_candidates.py`), and how to promote a candidate into
  a real claim.
