# Changelog

All notable changes to EntoLaw are documented here.

## [0.1.0] — 2026-06-25

Initial release: a source-anchored, reproducible field map of entomological law.

### Added

- Eight-role spine (`src/roles.py`) and registries for cases, statutes,
  species, institutions, timeline, and interconnections.
- `manuscript_variables` token generation, `claim_ledger` with offline + live
  oracles, cross-registry `validation`, and `package_map` self-description.
- Deterministic matplotlib figure layer (`viz`, `figure_bundle`) — ten captioned
  figures plus a cover.
- Modular claim-sourced manuscript (abstract → conclusion + methods), with token,
  citation, and cross-reference closure.
- Claim ledger seeded with three live-verified external statistics
  (ESA invertebrate definition; Hallmann 2017 biomass decline; UK Sentience Act
  scope), confirmed 2026-06-25.
- Test suite (no mocks): registry invariants, citation parsing, injectable
  validators, closure gates, no-hard-coded-statistic gate with negative control,
  figure totality, determinism, and a `-m live` claim oracle. `src/` coverage ≈ 97%.
- End-to-end render verified through the template (combined PDF + HTML).
