# Accuracy Methodology

This project makes two distinct kinds of promise about its numbers, and it is
important not to confuse them.

## 1. Registry-derived counts (proved by the offline gates)

Every magnitude in the manuscript that describes *this project's own encoded
material* — the number of legal roles, cases, statutes, categories, species,
institutions, milestones, and interconnections — is generated from the
registries under `src/` by `src.manuscript_variables.generate_variables` and
injected as a `{{TOKEN}}`. These numbers are **true by construction**: the
`tests/test_manuscript_variables.py` closure test fails if any token in the
prose is not generated, and `tests/test_manuscript_no_hardcoded_stats.py` fails
if any **numeral-form** magnitude in the prose is neither a token nor a
ledger-backed value. A count cannot drift from its registry without turning the
build red.

The no-hard-coded-statistic gate operates on numeral-form magnitudes
(`$1,000`, `76%`, `9,999`, `777 trillion`, `25+`, `93 species`) and ships a negative control
proving the detector fires on a planted numeral. Deliberately vague figures are
not numerically gated by that detector, but large external magnitudes and
volatile current-status claims still belong in the claim ledger when the
manuscript depends on them.

The scope of these numbers is exactly the encoded registries — a curated set of
leading authorities chosen to anchor each role, **not** a census of the entire
field. Every figure caption states this scope explicitly.

## 2. Externally-sourced statistics (offline-shaped, live-verified)

Statistics and current-status claims that come from outside the project — e.g.
the magnitude of the flying-insect-biomass decline or whether a proposed listing
has become final — are registered in `data/claim_ledger.yaml`. Each entry pins
the claim, a `references.bib` source key, the manuscript anchor, and a
verification record: the source URL, a verbatim supporting quote, the as-of
date, a confidence label, and the date the check was run.

Two oracles bind these claims:

* **Offline** (`src.claim_ledger.validate_claim_ledger`, in the default test
  run) proves each claim is *attributed* (real bib key), *anchored* (declared
  section), and carries a *complete, well-formed verification block*. It does
  **no network I/O** and therefore cannot prove a number is true.
* **Live** (`tests/test_live_claim_sources.py`, run with `uv run pytest -m
  live`) fetches each `source_url` and asserts every recorded quote appears.
  This is the binding correspondence check.

The ledger entries shipped in this version were live-fetched and confirmed on
the `checked` date stored in each verification block. The live oracle
re-confirms them on demand; if a source page changes wording, the live oracle is
expected to fail and the entry must be re-verified and corrected. **A green
offline run guarantees shape and attribution; only `-m live` guarantees
correspondence to the source.**

## What this project does *not* claim

* It does not claim its registries are exhaustive. They are curated.
* It does not opine on unsettled law; holdings are summarized and cited, not
  adjudicated.
* It does not assert that every colourful figure from the source literature is
  in the manuscript — only those bound either to a registry token or to a
  live-verifiable ledger entry are stated as numbers; others are described
  qualitatively with a citation.
