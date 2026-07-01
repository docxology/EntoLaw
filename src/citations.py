"""Legal-citation parsing for the entomological-law registries.

Single source of truth for deciding whether a citation string is well-formed
against the citation grammars this field actually uses. Entomological law
spans many reporters and codes, so the grammar is deliberately a *union* of
recognised forms rather than one canonical shape:

* **U.S. case reporters** — ``509 U.S. 579``, ``130 F.3d 1041``,
  ``293 F. 1013``, ``447 U.S. 303`` (optionally with a parenthetical court
  and year, e.g. ``293 F. 1013 (D.C. Cir. 1923)``).
* **State reporters** — ``79 Cal.App.5th 337``, ``2 Cal.5th 608``,
  ``15 Wend. 550``, ``152 So. 2d 736``, ``19 Kan. App. 2d 134``.
* **English neutral/reporter citations** — ``[1939] 1 KB 471``.
* **U.S. statutes / regulations** — ``7 U.S.C. § 7712``,
  ``7 U.S.C. §§ 7701–7786``, ``18 U.S.C. § 42``, ``7 C.F.R. § 301.92``,
  ``21 U.S.C. § 342``.
* **EU / international instruments** — ``Regulation (EU) 2015/2283``,
  ``Directive 2010/63/EU``, ``Federal Register`` notices (``85 FR 81737``).

The parser does not assert a citation is *correct law* — only that it is
*shaped like a citation* of a recognised kind, which is what
``validation.validate_*_registry`` needs to fail closed on a malformed
entry. Truth of the holding/section is bound separately by the claim ledger
and the live oracle.
"""

from __future__ import annotations

import re

# Reporter case citations: "<vol> <reporter> <page>", reporter being a run of
# capitalised abbreviations (U.S., F.3d, Cal.App.5th, So. 2d, KB, Wend., ...).
_REPORTER_RE = re.compile(
    r"\b\d{1,4}\s+"  # volume
    r"(?:[A-Z][A-Za-z.]*\.?\s*)+"  # reporter words — at least one (U.S., F.3d, So.)
    r"(?:\d+[a-z]{0,2}\s+)?"  # optional reporter series token (3d, 5th, 2d)
    r"\d{1,4}\b"  # first page
)
# English bracketed-year citation: "[1939] 1 KB 471".
_UK_RE = re.compile(r"\[(?:1[5-9]|20)\d{2}\]\s+\d*\s*[A-Z][A-Za-z.]+\s+\d{1,4}\b")
# U.S.C. / C.F.R. style: "7 U.S.C. § 7712", "7 C.F.R. § 301.92", ranges with §§.
_USC_RE = re.compile(
    r"\b\d{1,2}\s+(?:U\.S\.C\.|C\.F\.R\.)\s*§+\s*\d[\d.]*"
    r"(?:\s*[-–]\s*\d[\d.]*)?"
)
# EU regulations / directives: "Regulation (EU) 2015/2283", "Directive 2010/63/EU".
_EU_RE = re.compile(
    r"\b(?:Regulation|Directive)\s+(?:\(EU\)\s+)?\d{4}/\d{1,4}(?:/EU|/EC)?",
    re.IGNORECASE,
)
# Federal Register notice: "85 FR 81737".
_FR_RE = re.compile(r"\b\d{1,3}\s+FR\s+\d{3,6}\b")
# U.S. Patent grant number used in cross-refs ("U.S. Patent 4,736,866").
_PATENT_RE = re.compile(r"\bU\.S\.\s+Patent\s+[\d,]{5,}\b")
# Court docket for a recent, not-yet-reported opinion ("No. 22-1052").
_DOCKET_RE = re.compile(r"\bNo\.\s+\d{1,2}-\d{2,5}\b")
_STATE_BILL_RE = re.compile(
    r"\b[A-Z][A-Za-z]+\s+(?:H\.?B\.?|S\.?B\.?)\s*(?:\d{2}-)?\d{1,5}"
    r"\s*\(20\d{2}\)"
)
# Procedural rules cited by number ("Fed. R. Evid. 702", "Rule 702").
_RULE_RE = re.compile(
    r"\b(?:Fed\.\s*R\.\s*(?:Evid|Civ\.?\s*P|Crim\.?\s*P)\.?|Rule)\s+\d+\b",
    re.IGNORECASE,
)
# A named statute/treaty/regulation instrument: an instrument word qualified by
# a year, a section symbol, a chapter, or an Article. Strict enough that a bare
# noun ("the Act") does not match, loose enough to admit "Endangered Species
# Act of 1973", "Biological Weapons Convention (1972)", "Fish & Game Code § 45".
_NAMED_INSTRUMENT_RE = re.compile(
    r"\b(?:Act|Convention|Protocol|Treaty|Framework|Regulation|Directive|"
    r"Order|Code|Rules?|Amendment|Institutes|Agreement)\b[^\n]*?"
    r"(?:\b(?:1[5-9]\d{2}|20\d{2})\b|§|\bch\.|\bArt(?:icle)?\.?\b|/)",
    re.IGNORECASE,
)

_PATTERNS: tuple[re.Pattern[str], ...] = (
    _USC_RE,
    _EU_RE,
    _FR_RE,
    _UK_RE,
    _PATENT_RE,
    _DOCKET_RE,
    _STATE_BILL_RE,
    _RULE_RE,
    _REPORTER_RE,
)


def citation_is_parseable(text: str) -> bool:
    """Return ``True`` when ``text`` contains at least one recognised citation."""
    return any(pattern.search(text) for pattern in _PATTERNS)


def citation_kind(text: str) -> str:
    """Classify a citation into a coarse kind for provenance figures.

    Returns one of ``"statute"`` (U.S.C./C.F.R.), ``"eu_instrument"``,
    ``"federal_register"``, ``"patent"``, ``"uk_case"``, ``"case"``
    (any other reporter citation), or ``"unrecognised"``.
    """
    if _USC_RE.search(text):
        return "statute"
    if _EU_RE.search(text):
        return "eu_instrument"
    if _FR_RE.search(text):
        return "federal_register"
    if _PATENT_RE.search(text):
        return "patent"
    if _DOCKET_RE.search(text):
        return "docket"
    if _STATE_BILL_RE.search(text):
        return "state_bill"
    if _RULE_RE.search(text):
        return "rule"
    if _UK_RE.search(text):
        return "uk_case"
    if _REPORTER_RE.search(text):
        return "case"
    if _NAMED_INSTRUMENT_RE.search(text):
        return "named_instrument"
    return "unrecognised"


def instrument_is_recognised(text: str) -> bool:
    """Return ``True`` for a citation OR a named statute/treaty instrument.

    Statutes in this field are frequently cited by name and year rather than
    by a reporter or U.S.C. section (``Biological Weapons Convention 1972``,
    ``Animal Welfare (Sentience) Act 2022``). The statute-registry validator
    uses this looser gate; the case-registry validator uses the strict
    :func:`citation_is_parseable`.
    """
    return citation_is_parseable(text) or bool(_NAMED_INSTRUMENT_RE.search(text))


def extract_year(text: str) -> int | None:
    """Return the 4-digit year embedded in a citation, if any.

    Prefers a parenthetical/bracketed year (``(1993)`` / ``[1939]``) over a
    bare year so ``293 F. 1013 (D.C. Cir. 1923)`` resolves to 1923 rather
    than to the volume or page number.
    """
    paren = re.search(r"[(\[](1[5-9]\d{2}|20\d{2})[)\]]", text)
    if paren:
        return int(paren.group(1))
    bare = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", text)
    return int(bare.group(1)) if bare else None
