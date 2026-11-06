# Methods: Registry-First, Claim-Ledgered Legal Synthesis {#sec:methods}

This reference is built so that the map and the evidence cannot drift apart. All domain knowledge lives in {{REGISTRY_COUNT}} source-of-truth registries under `src/` — roles, cases, statutes, species, institutions, timeline, and interconnections — and every reader-facing artifact is regenerated from them, as shown in the architecture figure.

![{{FIGURE_CAPTION_ARCHITECTURE}}](../output/figures/architecture.png){#fig:architecture width=95%}

## Token closure: every count comes from code

Every magnitude-bearing number in this prose is a double-brace token (a `TOKEN` wrapped in doubled braces) resolved at build time by `src.manuscript_variables.generate_variables`. The closure test asserts that every token referenced in the manuscript is generated and that the generator emits no orphan, so a registry edit that changes a count (say, adding a case) updates the prose automatically, and a hand-typed count that drifts from its registry fails the build. The {{STATUTE_COUNT}} statutes span {{JURISDICTION_COUNT}} jurisdictions, shown in the statutes-by-jurisdiction figure; that number, like the {{CASE_COUNT}} cases and the {{FIGURE_COUNT}} figures, is generated, never typed.

![{{FIGURE_CAPTION_STATUTES_BY_JURISDICTION}}](../output/figures/statutes_by_jurisdiction.png){#fig:statutes_by_jurisdiction width=80%}

## Claim ledger, validation, and reproducibility

Counts come from the registries; *external* and volatile current-status claims do not. Each externally-sourced statistic written as a numeral, and each date-sensitive status claim that the manuscript needs to preserve, is registered in `data/claim_ledger.yaml` with a verification record: the source URL, a verbatim supporting quote, an as-of date, a confidence label, and the date the check was last run. The current ledger contains {{CLAIM_LEDGER_COUNT}} quote-backed entries, with section coverage shown in the claim-ledger coverage figure. Two oracles bind these claims. The **offline** oracle (`src.claim_ledger.validate_claim_ledger`) proves each claim is attributed to a real bibliography key, anchored to a declared section, and carries a complete, fail-closed verification block — it cannot prove a number is *true*. The **live** oracle (`tests/test_live_claim_sources.py`, run with `-m live`) fetches each source URL and confirms the recorded quotes appear, so "verified" is a re-runnable fact rather than an assertion. This boundary is deliberate and documented: the green offline gate guarantees *shape and attribution*; only the live oracle guarantees *correspondence to the source*.

![{{FIGURE_CAPTION_CLAIM_LEDGER_COVERAGE}}](../output/figures/claim_ledger_coverage.png){#fig:claim_ledger_coverage width=80%}

Citations, cross-references, and statistics all pass through their own validation gates. A cross-registry validator fails closed on a malformed citation, an out-of-vocabulary role or category, a duplicate slug, or an empty required field, and writes its findings to `output/reports/validation.json`. A separate gate scans the manuscript for any numeral-form magnitude that is neither a generated token nor a value present in the claim ledger, with a negative control proving the detector fires on a planted statistic. Together these gates make the reference's central promise machine-checkable: no numeral-form statistic reaches the page unbacked. The bibliography is also treated as data. The citation-date figure, previewed at the start of this reference, parses `references.bib` directly, so the reader can see where the source base is early legal text, where it is modern scholarship, and where it is official current-status material.

## Candidate case leads (unreviewed)

A separate, clearly-bounded pass runs alongside the registries above: `scripts/fetch_case_candidate_queries.py` submits {{CANDIDATE_QUERY_COUNT}} declared CourtListener opinion-search queries (`config/case_candidate_queries.yaml`) against the {{LEGAL_ISSUE_COUNT}} legal issues in `config/legal_issues.yaml`, and `scripts/generate_case_candidates.py` rebuilds `data/case_candidates.yaml` deterministically, offline, from the recorded responses. **Every one of the {{CANDIDATE_TOTAL_COUNT}} rows that register holds is an unreviewed search hit, not a finding**: each carries `status: candidate`, meaning CourtListener returned it for a declared query and nothing about it has been read, weighed, or admitted. No candidate has entered `references.bib`, `data/claim_ledger.yaml`, or `src/case_records.py` by virtue of appearing here, and no function in `src/case_candidates.py` can write anything but `candidate` into that field. {{CANDIDATE_ISSUE_COUNT}} of the {{LEGAL_ISSUE_COUNT}} declared issues have at least one surfaced candidate so far, shown below by conservatively-derived court level, with filings by decade alongside.

![{{FIGURE_CAPTION_CASE_CANDIDATES_BY_ISSUE}}](../output/figures/case_candidates_by_issue.png){#fig:case_candidates_by_issue width=90%}

Promoting a candidate into an actual citation, claim, or case-record entry is a human decision made after reading the opinion, never a pipeline step — see `docs/CASE_CANDIDATES.md` for the promotion path and the boundary `tests/test_case_candidates.py` enforces around it.

Finally, this build carries its own provenance: generated on `{{PLATFORM}}` under Python `{{PYTHON_VERSION}}` from configuration hash `{{CONFIG_HASH}}` at `{{GENERATION_TIMESTAMP}}`. The same version-controlled inputs regenerate the inventories, the validation report, the figures, the manuscript variables, and this document with identical registry-derived content, modulo the provenance stamp.

## Selected-frame statistics and visible limits

The registry frame is a curated collection of decisions and patents, rather
than a probability sample of disputes or a complete doctrinal census.
`src.registry_analysis.analyze_registry` adapts its stable entry identifiers to
the shared engine's descriptive analysis. The adjacent figure table records
exact member IDs, numerator and denominator, the mapping from generic grouping
fields to jurisdiction and registered role, and source digests. A year in the
registry retains year precision; it is not a request, event or production date.
No disclosure rate, response duration or agency comparison is inferred.

![{{FIGURE_CAPTION_REGISTRY_FRAME}}](../output/figures/registry_frame.png){#fig:registry_frame width=95%}

The cross-tab exposes the joint composition hidden by separate role and
jurisdiction totals. A zero cell describes the encoded frame, not absence of
case law, an insect role, or agency records. The analysis protocol makes this
finite-frame estimand explicit. AAPOR's discussion of inferential assumptions
motivates that caution; using it for a curated legal registry is this project's
adaptation [@methods_aapor_nonprobability].

## Located argument review and a discriminating acquisition plan

The rhetorical codebook separates the source's proposition, grounds, scope,
qualification and an alternative explanation. Entman's selection/salience
framework offers a vocabulary for human framing memos; Grimmer and Stewart
motivate source-specific validation of computational text analysis
[@methods_entman_framing; @methods_grimmer_stewart]. These methods do not convert
a registry's authored holding summary into a freshly read opinion, or a legal
role into a claim about an agency's intent.

`config/records_research.yaml` asks role-specific questions and names candidate
record categories, alternative explanations and routing review. Forensic
validation, quarantine decisions, conservation records, property disputes,
patent files, historical process, ethics deliberation and public oversight
require different documentary tests. The declaration asserts no record's
existence and sends no request. Each proposed inference needs a located source
and a record that could also challenge it.

Custody determines the access route. Federal FOIA does not provide access to
records held by federal courts; California's judicial administrative access
rule separately distinguishes administrative and adjudicative records
[@methods_doj_foia_scope; @methods_ca_judicial_access]. An agency record about a
proceeding and the court file itself are different acquisition questions. The
public-source ledger retains current-law retrieval limits, and every request
plan requires human jurisdiction and scope review before any correspondence.
