# Descriptive statistics for a selected records archive

This protocol is an analysis design, not a finding about an agency. The unit of
analysis is declared separately for requests, communications, attachments,
documents, pages, and coded passages. A request can contain several documents;
their counts cannot be substituted for one another.

## Frame and estimands

Freeze the request IDs, retained input hashes, extraction version and project
reference date before computing. Describe the archive's selection mechanism and
time coverage. Deduplicate within the declared unit using stable identifiers;
retain cross-project overlap as a separate field rather than adding project
totals. Report a flow from selected requests to accessible communications,
declared attachments, retained bytes, extracted text and reviewed content. Each
transition has its own denominator and exclusion reasons.

For each proportion publish the numerator IDs, denominator IDs, missing IDs,
eligibility rule and formula. Report `n/N` beside any percentage. An empty
denominator is unavailable, never zero percent. Distinguish a verified zero from
an absent field, unread file, failed extraction, unsupported jurisdiction and
not-applicable unit. The complements of different denominators cannot be added.

These archives support finite-frame description. They do not support estimates
of nationwide disclosure rates or comparisons of institutional performance
without a sampling design, comparable scopes and a defended estimand. AAPOR's
non-probability sampling report motivates explicit assumptions; applying that
principle to selected request archives is this project's methodological choice.

## Dates, duration and incomplete observation

Keep submission, agency receipt, acknowledgment, determination, production,
appeal and platform-update timestamps distinct. Preserve timezone and date-only
precision. Record the source and status of every date: read instrument,
transmission estimate, platform proxy, or unavailable. Calendar age at a fixed
reference date is an operational measure, not a legal duration or production
latency. Quantiles of observed ages describe that eligible subset only; state
the quantile convention and eligible/missing counts.

A survival analysis requires a justified origin, defined event, observed event
date, censoring rule and assessment of informative censoring. A closed platform
status alone supplies none of these. Do not turn unresolved requests into
completed durations. Retain them as unresolved at the snapshot. No automatic
Kaplan–Meier curve, p-value, confidence interval or regression belongs in this
phase. Future comparative work should preregister the frame and covariates,
retain competing outcomes and model the selection process.

## Review and robustness

Publish coverage by agency and jurisdiction alongside aggregate coverage.
Treat repeated requests within an agency and multiple documents within a request
as related observations. Compare counts with and without proxy-date rows and
with unresolved units retained; describe the changed denominator, not a causal
effect. For lexical cues, publish document presence and passage count separately
so boilerplate repetition cannot become apparent evidentiary weight.

For human coding, fix the unit and codebook, independently double-code a declared
subset, retain disagreements, adjudication reasons and codebook revisions.
Report the contingency table and agreement denominator before choosing any
reliability coefficient. A single reader or deterministic regex cannot provide
inter-coder reliability. Do not report reliability without those observations.

## Figure contract

Every figure names its unit, frame, reference date, denominator, missingness,
date basis and relevant source hashes. Use directly labelled bars or dot plots
for small frames, stable ordering, visible zero categories and a distinct
unavailable category. Keep unrelated units on separate panels. Avoid truncated
bar axes, dual axes, decorative network edges and color-only distinctions.
Accompany figures with a machine-readable table and explanatory caption. A
coverage diagram measures the archive's documentation, not responsive-record
completeness, legal compliance or institutional intent.
