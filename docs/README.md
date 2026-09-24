# EntoLaw — Documentation

**EntoLaw** (`entolaw`, v0.1.0) is a source-anchored registry and claim-sourced
manuscript project mapping registered legal roles of the insect. Registries
under `src/` (cases, statutes, species, institutions, roles, citations,
interconnections, timeline) drive every number in `docs/manuscript/` via
`{{TOKEN}}` injection; see [ACCURACY_METHODOLOGY.md](ACCURACY_METHODOLOGY.md)
and [REVIEW_PROTOCOL.md](REVIEW_PROTOCOL.md).

## Layout

- `src/` — registry models, claim-ledger validation, figure generation
- `scripts/` — thin orchestrators (figures, manuscript variables, inventory, web export)
- `docs/manuscript/` — section files `00_abstract.md` … `12_conclusion.md`, `99_references.md`
- `data/`, `output/` — registry inputs and generated figures/variables
- `tests/` — registry and ledger validation tests

## Run / test (from pyproject.toml)

```bash
uv sync
uv run pytest              # testpaths = ["tests"]
```

## Documentation in this directory

- [ACCURACY_METHODOLOGY.md](ACCURACY_METHODOLOGY.md) — how registry-derived facts stay true by construction
- [REVIEW_PROTOCOL.md](REVIEW_PROTOCOL.md) — review discipline for claims and citations
- [CASE_CANDIDATES.md](CASE_CANDIDATES.md) — the CourtListener case-candidate
  register (`data/case_candidates.yaml`): never a claim source, and how to
  promote a candidate into one
- [COURTLISTENER_WATCH.md](COURTLISTENER_WATCH.md) — the declared saved-search
  watches and search alerts this project monitors over time, dry-run default,
  no-delete guarantee, and the rate budget

## Status

Docs hub created by the docs-audit pass (2026-08-29); the two existing docs
files were audited and left unchanged.
