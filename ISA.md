# ISA — EntoLaw

The Ideal State Artifact for the EntoLaw project: a source-anchored,
reproducible field map of entomological law.

## Problem

The intersection of insects and law is a genuinely transdisciplinary field with
no master statute, no professional society spanning it, and no comprehensive
treatise. Existing surveys mix prose summaries with anecdotes that rot as
statutes are recodified and holdings distinguished, and they state colourful
statistics with no machine-checkable link to a source.

## Vision

A registry-first, claim-sourced reference in which (a) the field is organized by
the eight legal **roles** an insect occupies; (b) every count in the prose is
generated from source-of-truth registries; (c) every legal proposition is cited
to a primary authority; and (d) every externally-sourced numeral is bound to a
quotable, re-checkable source. The map and the territory cannot drift apart.

## Out of scope

- Adjudicating unsettled law or offering legal advice.
- Exhaustively enumerating every case, statute, or species — registries are
  curated to anchor each role with its leading authorities.
- Live network access in the default test run (reserved for the `-m live` oracle).

## Principles

- Thin orchestrator: business logic lives in `src/`; scripts and prose consume it.
- No hard-coded statistic: tokens or claim-ledger, never a bare literal.
- Honesty boundary: offline gates prove shape/attribution; the live oracle
  proves correspondence (see `docs/ACCURACY_METHODOLOGY.md`).
- No mocks: real data, real files, injectable validators for error paths.

## Goal & Criteria

- [x] Eight legal roles encoded as the manuscript spine (`src/roles.py`).
- [x] Registries for cases, statutes, species, institutions, timeline, and
  interconnections, all validated against controlled vocabularies.
- [x] Manuscript with token closure, citation closure, and cross-reference
  closure; abstract → conclusion plus a methods section documenting the contract.
- [x] Claim ledger with a fail-closed offline oracle and a live oracle; shipped
  entries live-verified 2026-06-25.
- [x] Deterministic matplotlib figures, one per caption, plus a cover.
- [x] `src/` test coverage ≥ 90% with no mocks; combined PDF + HTML render
  through the template.

## Test Strategy

Registry-content invariants; citation-grammar parsing; validation with injected
real bad data; token/citation/cross-reference closure against the manuscript;
no-hard-coded-statistic gate with a negative control; figure ↔ caption
totality; determinism of registry-derived variables; and a `-m live` claim
oracle.

## Verification

`uv run pytest -m "not live" --cov=src` → 89 passed, coverage ≈ 97%.
`scripts/run_inventory.py` → 0 validation errors. `scripts/03_render_pdf.py
--project working/EntoLaw` → combined PDF + 14 HTML sections, no unresolved
tokens.
