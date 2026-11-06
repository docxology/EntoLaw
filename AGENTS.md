# AGENTS.md — EntoLaw

Working rules for AI agents and contributors in this project.

## Architecture (thin orchestrator)

All domain knowledge is **data in registries** under `src/`. Scripts and the
manuscript are thin consumers. Never hard-code a count, a citation list, or a
figure caption in prose — derive it.

- Add a case/statute/species/etc. by editing the registry module, not the
  manuscript. The `{{TOKEN}}` counts and figures update automatically.
- Every legal proposition in the manuscript carries a `[@bibkey]` citation that
  must exist in `docs/manuscript/references.bib`.
- Every magnitude in the prose is either a `{{TOKEN}}` (registry-derived) or a
  value present in `data/claim_ledger.yaml` (external). There is no third way —
  `tests/test_manuscript_no_hardcoded_stats.py` enforces it.

## Adding an external statistic

1. Add a `[@key]` source to `references.bib`.
2. Add a claim entry to `data/claim_ledger.yaml` with a full verification block
   (status, verified_value, source_url, source_quote(s), as_of, confidence,
   checked) anchored to a declared `sec:*`.
3. Confirm it live only under a separately authorized network workflow: `.venv/bin/python -m pytest -m live -k <claim_id>`. Do **not** mark a
   claim `verified` with a quote you have not fetched — that is the exact
   failure mode the ledger exists to prevent.

Use the same path for volatile current-status claims even when they are not
strictly numeral-form statistics. If the manuscript depends on an as-of-date
legal or biological status, bind it to a short live-checkable quote.

## Gates (all must pass)

```bash
.venv/bin/python -m legal_informatics.local_validation --project-root .
```

- token closure (`test_manuscript_variables.py`)
- citation closure (every `[@key]` in `references.bib`)
- cross-reference closure (every `@sec:`/`@fig:` resolves)
- claim-ledger validation (`test_claim_ledger.py`)
- no hard-coded statistic (`test_manuscript_no_hardcoded_stats.py`)
- figure ↔ caption totality (`test_figures.py`)
- render-time hydration (`test_render_hydration.py`)

The supported runtime is the declared Python 3.15.2 environment. Execute the
bounded local gate through the vault's qualified offline runner; dependency setup
is a separate governed operation. The declaration in `config/local_validation.yaml`
retains the non-live coverage suite and actual local render, and now checks the
local research resource contract before accepting the source. Existing source
verification dates and curated registry facts are not refreshed by this gate.

## No mocks

Tests use real dataclass instances and real files. Validation error branches
are tested by passing crafted-but-real bad data to the injectable validators
(`validate_cases([bad_case])`), never by patching.

## Rendering

From this project root, follow `docs/REVIEW_PROTOCOL.md` and run the declared
hydration and local render scripts. The hydrator uses the shared template
discovery contract and respects the declared template environment; never
replace it with an ancestor-count assumption. The shared local renderer
requires an actual PDF/HTML result and performs no external publication.
`config/manuscript_metadata.yaml` declares public source visibility with formal
publication forbidden for this workflow. Historical DOI metadata is retained.
