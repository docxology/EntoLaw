# Evidence-linked rhetorical review codebook

The object is a passage in a retained source, not a person's psychology. Preserve
the document hash, request/communication/attachment IDs, page and character
offsets, exact context, extraction method and review coverage. OCR requires page
inspection before quoting a legally significant symbol, name or negation.

## Coding dimensions

| Dimension | What the reviewer records | Boundary |
|---|---|---|
| Speech act | acknowledgment, clarification, search account, referral, determination, withholding, production commitment | Code the passage's function; a status badge is insufficient. |
| Proposition | the narrow claim actually expressed | Keep speaker attribution; do not endorse the claim. |
| Ground | the cited search, record, policy or legal provision | A citation's presence does not establish its applicability. |
| Warrant | the explicit connection between ground and claim | Mark an inferred warrant as analyst interpretation. |
| Qualification | scope, date range, custodian, conditions, hedges and exceptions | Preserve restrictive words and negative constructions. |
| Alternative | a plausible competing explanation and what would distinguish it | Absence of a document is compatible with several explanations. |
| Remedy or next step | clarification, routing, review, payment decision, appeal information | A candidate action is not an established legal entitlement. |
| Framing memo | how a passage presents the problem and proposed response | Human interpretation; no automatic intent label. |

The argument structure is an adaptation of Toulmin's vocabulary; the verified
publisher record and frontmatter identify the work, while a full chapter reading
remains pending. Entman's treatment of selection and salience supplies a vocabulary for the
framing memo; its targeted passage was read in a university-hosted article copy.
This application does not measure effects on an audience. Grimmer and Stewart's account of text-analysis validation
supports keeping computational output subordinate to problem-specific reading.

## Existence, custody and search

Keep distinct: existence neither confirmed nor denied; no responsive records
reported after a described search; no search described; records outside a named
component's custody; records referred elsewhere; records withheld under an
asserted authority; records released; and unavailable evidence. Do not collapse
them into a single refusal category. A response limited to an inspector general
does not describe an entire agency; a finding-aid search does not necessarily
describe every archival series. A different case number is a linkage problem to
resolve before using the letter in a project narrative.

## Computational cues and adjudication

Lexical cues locate candidate spans. They do not classify legal merit, truth,
tone, deception, motive or a valid determination. Preserve all matching spans
and the rule version; inspect surrounding text, negation, quotations and who is
speaking. Count both documents with a cue and repeated occurrences. Label every
unreviewed hit `candidate_review_required`. A non-hit means only that the rule
did not match; it is not absence of a rhetorical feature.

A reviewer records accepted/rejected/uncertain, a rationale, the checked source
locator and whether the source is complete. Corrections create a new derived
annotation; they never rewrite the source. Conflicting interpretations remain
visible until adjudicated. A revised codebook requires a new version and a
declared recoding policy. Automated cues and human judgments belong in separate
tables so a later visual cannot silently promote one into the other.

## Inquiry matrix

For each proposed substantive inference retain: claim; located evidence;
limiting context; alternative explanation; missing discriminating record;
appropriate custodian/jurisdiction; proposed bounded search; and review state.
Start with a question when the corpus does not support a claim. A scholarly
analogy can motivate the question but cannot show that an agency holds a record.
Request plans should test competing explanations instead of collecting only
confirming material. No score is a probability that the claim is true.
