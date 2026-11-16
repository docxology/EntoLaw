# Methods: Registry-First, Claim-Ledgered Legal Synthesis {#sec:methods}

This reference is built so that the map and the evidence cannot drift apart. All domain knowledge lives in 7 source-of-truth registries under `src/` — roles, cases, statutes, species, institutions, timeline, and interconnections — and every reader-facing artifact is regenerated from them, as shown in the architecture figure.

![How 7 source-owned registries become reproducible outputs. Pure generator methods — metrics, validation, manuscript-variable generation, and figure rendering — turn registry data into inventories, reports, figures, and the rendered manuscript itself. Read as: the package treats the manuscript as a compiled artifact, not as the source of legal facts. Why it matters: readers can audit whether prose, visuals, and counts share the same inputs. Provenance: `src/viz.py`. Caveat: a local build-pipeline description, not a deployment diagram.](../output/figures/architecture.png){#fig:architecture width=95%}

## Token closure: every count comes from code

Every magnitude-bearing number in this prose is a double-brace token (a `TOKEN` wrapped in doubled braces) resolved at build time by `src.manuscript_variables.generate_variables`. The closure test asserts that every token referenced in the manuscript is generated and that the generator emits no orphan, so a registry edit that changes a count (say, adding a case) updates the prose automatically, and a hand-typed count that drifts from its registry fails the build. The 43 statutes span 10 jurisdictions, shown in the statutes-by-jurisdiction figure; that number, like the 18 registry entries and the 14 registered inventory figures, is generated, never typed.

![The same 43 instruments partitioned by issuing jurisdiction — US-federal, US-state, US-colonial, UK, India, Muscovy, Russian Empire, USSR, EU, and international — showing the field's multi-level legal architecture. Read as: insect law is built through stacked authority, with local movement rules, national statutes, and international instruments all operating at once. Why it matters: no single legal layer owns the field's risk decisions. Provenance: `src/statutes.py`. Caveat: jurisdiction is the issuing level, not a measure of reach or enforcement.](../output/figures/statutes_by_jurisdiction.png){#fig:statutes_by_jurisdiction width=80%}

## Claim ledger, validation, and reproducibility

Counts come from the registries; *external* and volatile current-status claims do not. Each externally-sourced statistic written as a numeral, and each date-sensitive status claim that the manuscript needs to preserve, is registered in `data/claim_ledger.yaml` with a verification record: the source URL, a verbatim supporting quote, an as-of date, a confidence label, and the date the check was last run. The current ledger contains 20 quote-backed entries, with section coverage shown in the claim-ledger coverage figure. Two oracles bind these claims. The **offline** oracle (`src.claim_ledger.validate_claim_ledger`) proves each claim is attributed to a real bibliography key, anchored to a declared section, and carries a complete, fail-closed verification block — it cannot prove a number is *true*. The **live** oracle (`tests/test_live_claim_sources.py`, run with `-m live`) fetches each source URL and confirms the recorded quotes appear, so "verified" is a re-runnable fact rather than an assertion. This boundary is deliberate and documented: the green offline gate guarantees *shape and attribution*; only the live oracle guarantees *correspondence to the source*.

![Coverage of the 20 live-checkable claim-ledger entries by declared manuscript section. Provenance: `src.claim_ledger.claim_coverage_by_anchor()`. Read as: volatile current-status and external magnitude claims are isolated where live evidence, not registry counts, carries the truth burden. Why it matters: it makes the manuscript's fact-checking boundary auditable by section. Caveat: a section with zero entries may still contain registry-derived facts or qualitative cited claims; this figure shows external/current claims that require a quote-backed verification block.](../output/figures/claim_ledger_coverage.png){#fig:claim_ledger_coverage width=80%}

Citations, cross-references, and statistics all pass through their own validation gates. A cross-registry validator fails closed on a malformed citation, an out-of-vocabulary role or category, a duplicate slug, or an empty required field, and writes its findings to `output/reports/validation.json`. A separate gate scans the manuscript for any numeral-form magnitude that is neither a generated token nor a value present in the claim ledger, with a negative control proving the detector fires on a planted statistic. Together these gates make the reference's central promise machine-checkable: no numeral-form statistic reaches the page unbacked. The bibliography is also treated as data. The citation-date figure, previewed at the start of this reference, parses `references.bib` directly, so the reader can see where the source base is early legal text, where it is modern scholarship, and where it is official current-status material.

## Candidate case leads (unreviewed)

A separate, clearly-bounded pass runs alongside the registries above: `scripts/fetch_case_candidate_queries.py` submits 14 declared CourtListener opinion-search queries (`config/case_candidate_queries.yaml`) against the 8 legal issues in `config/legal_issues.yaml`, and `scripts/generate_case_candidates.py` rebuilds `data/case_candidates.yaml` deterministically, offline, from the recorded responses. **Every one of the 176 rows that register holds is an unreviewed search hit, not a finding**: each carries `status: candidate`, meaning CourtListener returned it for a declared query and nothing about it has been read, weighed, or admitted. No candidate has entered `references.bib`, `data/claim_ledger.yaml`, or `src/case_records.py` by virtue of appearing here, and no function in `src/case_candidates.py` can write anything but `candidate` into that field. 7 of the 8 declared issues have at least one surfaced candidate so far, shown below by conservatively-derived court level, with filings by decade alongside.

![The 176 CourtListener case CANDIDATES the candidate-query pipeline has surfaced so far, grouped by declared legal issue and a conservatively-derived court level (supreme, appellate, trial, other/unknown), with filings by decade in the side panel. Read as: this is a lead list, not a finding -- every bar counts an unreviewed CourtListener opinion-search hit that `status: candidate` in `data/case_candidates.yaml` records and nothing more. Why it matters: it shows where the case law the manuscript has not yet reviewed is concentrated, without letting a search hit stand in for a verified authority. Provenance: `src.case_candidate_metrics` over `data/case_candidates.yaml` and `config/legal_issues.yaml`. Caveat: court level is derived from the court name string alone and is conservative -- a name this rule cannot place stays other/unknown rather than guessed; see `docs/CASE_CANDIDATES.md`.](../output/figures/case_candidates_by_issue.png){#fig:case_candidates_by_issue width=90%}

Promoting a candidate into an actual citation, claim, or case-record entry is a human decision made after reading the opinion, never a pipeline step — see `docs/CASE_CANDIDATES.md` for the promotion path and the boundary `tests/test_case_candidates.py` enforces around it.

Finally, this build carries its own provenance: generated on `Darwin arm64` under Python `3.15.2` from configuration hash `1ec3a8837d9f0773`, with build stamp `2026-07-02T00:00:00Z`. The stamp is not the wall clock: it is `SOURCE_DATE_EPOCH` when an outer build pins one, and otherwise the manuscript's declared date, so the same version-controlled inputs on the same platform regenerate the inventories, the figures, the manuscript variables, and this document's text and LaTeX source byte-for-byte. One exception remains outside this project: the rendering template's bookend integrity strip still stamps its barcode from the wall clock, so the rendered PDF differs between builds on its first and last pages only and is not kept under version control.

## Selected-frame statistics and visible limits

The registry frame is a curated collection of decisions and patents, rather
than a probability sample of disputes or a complete doctrinal census.
`src.registry_analysis.analyze_registry` adapts its stable entry identifiers to
the shared engine's descriptive analysis. The adjacent figure table records
exact member IDs, numerator and denominator, the mapping from generic grouping
fields to jurisdiction and registered role, and source digests. A year in the
registry retains year precision; it is not a request, event or production date.
No disclosure rate, response duration or agency comparison is inferred.

![Read as: jurisdiction by principal registered role for the selected curated decision/patent frame. Cells show exact entry counts; the adjacent JSON table retains member identifiers, denominators and source hashes. A zero means no encoded entry, not absence of doctrine or records. Why it matters: the joint table exposes the registry composition hidden by separate role and jurisdiction totals. Provenance: src/registry_analysis.py over src/case_records.py and src/roles.py through the shared descriptive engine. Caveat: authored summaries and year-only dates are not new opinion readings, request durations or a representative sample of legal disputes.](../output/figures/registry_frame.png){#fig:registry_frame width=95%}

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

## Instrument type changes the proposition being tested

A patent grant, an appellate disposition and a statutory eligibility ruling
are different legal acts. The selected new primary readings are recorded in
`docs/research/instrument_readings.json`, with host, exact reviewed extent and
retrieval failures. No full opinion reading or present legal status is inferred
from those targeted passages.

The OncoMouse patent's front page and claim show an issued instrument and a
bounded claimed invention, not a judicial ruling that the patent is valid
[@depth_oncomouse]. The historical PHS agreement identifies patent-related use
and transfer terms; it is not a current license or validity judgment
[@depth_phsmou]. The research discriminator is the particular claim, file history
or agreement and its operative period, rather than a biological category alone.

Westerfield's opening states affirmance and describes the defense's reliance on
entomological evidence [@depth_westerfield]. That supports the disposition, not
the former registry inference that a jury discarded a field of expertise. A
stronger account would require the opinion's actual issue analysis and the
trial record: what inference was offered, what assumptions were disputed, and
what ruling resolved which objection. The source selection does not establish
how jurors reasoned or a general error rate for entomology.

Almond Alliance's introduction and conclusion address eligibility under CESA's
statutory definitions and listing requirements [@depth_almond]. That does not
make a universal biological classification or establish a species' current
listing. The primary opinion was read from the Stanford law clinic's copy;
the official opinion endpoint was unavailable. Its original disposition is
distinguished from later treatment, which this targeted reading does not verify.

| Research question | Discriminating evidence | Limit on access or inference |
| --- | --- | --- |
| Was an expert inference admitted and on what ground? | Issue, ruling, record citation and alternative explanation | A court file is not a federal-agency FOIA file |
| What does a patent instrument claim? | Exact claim, specification, prosecution and cited instrument version | Issuance alone is no judicial validity finding |
| Why did a listing decision cover a taxon? | Statutory definition, eligibility reasoning and separate listing record | Eligibility is not biological identity or current listing |
| Did an agency use a patented research tool? | A dated agreement, institutional record and custodian linkage | A historical public agreement proves no present agency holding |

No request is sent and no record's existence is presumed. Any justified
correspondence remains DRAFT — NOT SENT pending human scope and custodian review.

## A prospective review of legal propositions

EntoLaw — prospective located argument review

Unit definition: One declared source span with exact byte digest, parsed-text selector and character offsets; the unit is not a complete request or instrument.

Selection: Purposive contrasts among scope, attribution and evidentiary-linkage problems already identified in this project; not random or exhaustive and not a prevalence denominator.

Codebook version: 2026-11-06-v1

Expected codebook SHA256: 7f204c9f02c470d6db758b796f06ebb613bfb19ec6cd16bdadb34cddf54a0623. Every performed judgment must name this exact digest.

Review plan: Future reviewers would first record source kind and apply each code independently using the include/exclude rules, retaining uncertain decisions and rationales. Discuss disagreements only after preserving original independent judgments; do not backfill them from lexical cues or later consensus. No actual reviewers, independent pairs or judgments are supplied in this edition.

Declared frame: 6 located excerpts; 4 codes. Performed reviewer aliases: 0; explicit judgments: 0; declared independent pairs: 0.

Units are a declared finite excerpt frame, not a probability sample of records, agencies or rhetorical functions. Source kinds remain separate strata; overlapping or repeated passages may be dependent.

A planned review and automatic lexical cues are not human judgments. Missing assignments, explicit uncertainty and explicit absence are distinct states; none is imputed.

Each coefficient uses only the same units and codebook coded present/absent by the named pair. Uncertain or missing decisions are excluded and enumerated. Complete-case selection can distort apparent agreement.

Independence is a reviewer declaration, not an authenticated fact. Consensus/adjudicated labels must not be entered as independent judgments. Multiple coder pairs share units and are never pooled as independent observations.

Observed agreement and Cohen's kappa describe reproducibility of these coding decisions, not truth, rhetorical validity, speaker intent, search adequacy or legal compliance. No universal acceptability threshold, significance test or inferential interval is supplied.

Kappa uses coder-specific marginal proportions: (observed - expected)/(1 - expected). It is withheld for fewer than two complete pairs or expected agreement of one; marginal imbalance can make kappa diverge from raw agreement. Always inspect the contingency cells and coverage.

The operational definitions below are project-designed. Agreement and validity
are separate questions [@artstein2008]. The selected units mix authored registry
summaries with explicitly copied primary passages; they must retain those source
kinds when reviewed. No coder, independent session or judgment is supplied.

### SCOPE: Explicit scope boundary

Definition: The selected span states a time, component, record, instrument or subject boundary relevant to its proposition.

Include when: A boundary is actually stated and can be transcribed with its source kind.

Exclude when: The reviewer supplies a plausible boundary or treats a requester's proposed scope as an agency's accepted search.

Counterexample: A bare closed label states no searched locations or period.

### ACT: Attributed documentary act

Definition: The span identifies an attributed request, acknowledgment, routing, search statement, determination, grant or judicial act.

Include when: The act and its speaker or instrument can be identified from the unit's located context; keep summary attribution explicit.

Exclude when: A platform stage or reader interpretation is promoted into the underlying instrument or legal effect.

Counterexample: A task named appeal is not proof that an appeal was filed or decided.

### BRIDGE: Explicit evidentiary bridge

Definition: The span actually supplies the linkage needed for the stronger proposition under review.

Include when: The instrument's type, proposition and statutory or procedural scope are explicitly linked; issuance, adjudication and listing eligibility remain distinct.

Exclude when: A co-mention, a cultural association, a matching surname or a plausible custodian is the only connection.

Counterexample: A patent title and grant date do not establish a judicial decision on patent validity.

### QUALIFIER: Qualification of inference

Definition: The unit explicitly limits what its statement, source type or evidence supports.

Include when: A stated qualification limits the proposition; distinguish uncertainty from a definitive negative.

Exclude when: The reviewer adds a caveat that is absent from the unit or treats missing text as an explicit disclaimer.

Counterexample: The absence of a search description is not a statement that no search occurred.

### Selected excerpt depth_almond-copy

Printed page 35; line wrapping normalized, no words added. Local copy only; original bytes are not present.

Expected unit SHA256: 0ebc0fb2bb204d5f369d71ffc6cd9a323493e7a2dc786d29404dffcf408be56b.

**context; primary_passage_copy**

the Commission may list any invertebrate as an endangered or threatened species under 2062 and 2067, if the invertebrate meets the requirements of those statutes

Source: docs/research/instrument\_readings.json; pointer: /readings/1/excerpt; characters 0:161; SHA256 prefix 8a2706f0556d.

### Selected excerpt depth_oncomouse-copy

Front-page title only; not a judicial holding or a complete claim. Local copy only; original bytes are not present.

Expected unit SHA256: 707fe2d915f445b33629bf621ff4fd42f037086952b757900bc23973152bf210.

**context; primary_passage_copy**

TRANSGENIC NON-HUMAN MAMMALS

Source: docs/research/instrument\_readings.json; pointer: /readings/2/excerpt; characters 0:28; SHA256 prefix 8a2706f0556d.

### Selected excerpt depth_westerfield-copy

Printed page 1; the reviewed opening's disposition only. Local copy only; original bytes are not present.

Expected unit SHA256: 008af4d7fa79a0c32dc0ad216be4d42edef5934549e41d3b08ff5edf95ddafcc.

**context; primary_passage_copy**

We affirm the judgment in its entirety.

Source: docs/research/instrument\_readings.json; pointer: /readings/0/excerpt; characters 0:39; SHA256 prefix 8a2706f0556d.

### Selected excerpt registry-depth_almond

Authored registry holding summary; this source kind cannot authenticate an underlying instrument.

Expected unit SHA256: c40f78f33d3b8665b98dc1b02d9ea3bd58d9b0c3b3250874af09648e0f0a4add.

**context; declared_summary**

Terrestrial invertebrates can qualify for CESA listing under statutory fish definitions.

Source: src/case\_records.py; pointer: (whole text); characters 6366:6454; SHA256 prefix 63fd7026bdab.

### Selected excerpt registry-depth_oncomouse

Authored registry holding summary; this source kind cannot authenticate an underlying instrument.

Expected unit SHA256: 705b7c8e4fb4de431322c9c6520bf838ba9c4c6e347c86690253f99352659116.

**context; declared_summary**

The patent issued with claims to a specified transgenic non-human mammal.

Source: src/case\_records.py; pointer: (whole text); characters 10155:10228; SHA256 prefix 63fd7026bdab.

### Selected excerpt registry-depth_westerfield

Authored registry holding summary; this source kind cannot authenticate an underlying instrument.

Expected unit SHA256: 8a96cb678660a05a64e900b6a7dd129dc4948865d2df5439c28f599c4f7cf290.

**context; declared_summary**

The judgment was affirmed; the defense relied on entomological evidence.

Source: src/case\_records.py; pointer: (whole text); characters 3509:3581; SHA256 prefix 63fd7026bdab.

No performed reviewers or judgments declared; reliability is not assessed.

No independent coding pair declared; no agreement or kappa is estimated.

![Selected-excerpt composition by declared source kind and explicit coding coverage. Present, absent, uncertain and missing remain distinct. The assignment panel pools selected kinds only for display; the results retain separate kind-specific denominators. With no performed reviewers the frame-composition counts remain visible and coding is not assessed. Lexical cues are never judgments. At most 24 assignment rows are displayed; all rows remain in the structured results.](../figures/coding_review_v1_coverage.png){#fig:coding_review_v1_coverage width=0.95\textwidth}

![Complete-case contingency cells for each declared independent coder pair and code, with paired/eligible counts. Each pair remains separate; shared units are not independent replications. Kappa and observed agreement concern coding reproducibility only, not rhetorical validity, intent, legal adequacy or compliance. A missing review is not zero agreement.](../figures/coding_review_v1_agreement.png){#fig:coding_review_v1_agreement width=0.95\textwidth}
