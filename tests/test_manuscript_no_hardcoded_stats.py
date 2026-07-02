"""Gate: no hard-coded statistic in the manuscript.

Every magnitude-bearing number in manuscript prose must be EITHER:
  (a) auto-injected — written as a ``{{TOKEN}}`` resolved from
      ``src.manuscript_variables`` (registry-derived counts), OR
  (b) validated — its value appears in a ``data/claim_ledger.yaml`` entry's
      claim / verified_value / source_quote(s) (externally-sourced statistics).

Inherent non-statistics (years, statute / rule section numbers, bill numbers,
software versions) are exempted by construction.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.claim_ledger import load_claims

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SKIP = {"AGENTS.md", "README.md", "SYNTAX.md"}

_NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
_STAT_PATTERNS = (
    re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?"),  # $1,000
    re.compile(
        r"(?<![\d,.])\d[\d,]*(?:\.\d+)?\s*"
        r"(?:trillion|million|billion|thousand|percent|%)",
        re.IGNORECASE,
    ),  # 76 percent, 82%
    re.compile(r"(?<![\d,.])\d{1,3}(?:,\d{3})+"),  # 1,500 ; 440,000
    re.compile(r"(?<![\d,.])\d+\+"),  # 25+
    re.compile(
        r"(?<![\d,.])\d{2,3}\s+(?:species|states|hives|deaths|butterflies|cases|"
        r"statutes|taxa|roles|milestones)\b",
        re.IGNORECASE,
    ),  # 93 species, 16 states
)


def _norm(num: str) -> str:
    return num.replace(",", "").rstrip("+").rstrip(".")


_ANCHOR = re.compile(r"\{#(sec:[A-Za-z0-9_:-]+)(?:\s+[^}]*)?\}")


def _ledger_numbers_by_anchor() -> dict[str, set[str]]:
    """Map each section anchor to the numbers its OWN attached claims justify.

    Numbers are pooled per ``claim.anchor``, never globally: a figure registered
    for one section (e.g. a percentage tied to one claim's anchor) must not
    silently validate the same digits in an unrelated section that carries no
    claim justifying them.
    """
    by_anchor: dict[str, set[str]] = {}
    for c in load_claims(PROJECT_ROOT / "data" / "claim_ledger.yaml"):
        blob = [c.claim]
        if c.verification:
            blob += [c.verification.verified_value, c.verification.source_quote]
            blob += list(c.verification.source_quotes)
        bucket = by_anchor.setdefault(c.anchor, set())
        for piece in blob:
            bucket.update(_norm(m) for m in _NUM.findall(piece))
    return by_anchor


def _ledger_number_corpus() -> set[str]:
    """Union of every anchor's numbers (used only by the negative control)."""
    corpus: set[str] = set()
    for nums in _ledger_numbers_by_anchor().values():
        corpus |= nums
    return corpus


def _file_section_anchors(raw: str) -> set[str]:
    """Section anchors (``{#sec:...}``) declared in one manuscript file."""
    return set(_ANCHOR.findall(re.sub(r"`[^`]*`", "", raw)))


def _stat_offenders(text: str, accepted: set[str]) -> list[str]:
    """Statistic tokens in ``text`` whose number is not in ``accepted``."""
    offenders: list[str] = []
    for pat in _STAT_PATTERNS:
        for m in pat.finditer(text):
            num_match = _NUM.search(m.group(0))
            if not num_match:
                continue
            num = _norm(num_match.group(0))
            if num and num not in accepted:
                offenders.append(m.group(0).strip())
    return offenders


def _strip(text: str) -> str:
    text = re.sub(r"\{\{[^}]+\}\}", " ", text)  # token injections — exempt (a)
    text = re.sub(r"\{[^{}]*\}", " ", text)  # pandoc attr blocks
    text = re.sub(r"`[^`]*`", " ", text)  # inline code spans
    text = re.sub(r"\]\([^)]*\)", " ", text)  # markdown link/image targets
    text = re.sub(r"§+\s*\d[\d.]*", " ", text)  # statute/section numbers
    text = re.sub(r"\b(?:Rule|AB|SB)\s+\d[\d.]*", " ", text)  # rules / bill numbers
    text = re.sub(r"\b(?:1[5-9]|20)\d{2}\b", " ", text)  # years
    return text


def _manuscript_files() -> list[str]:
    return sorted(
        p.name
        for p in (PROJECT_ROOT / "manuscript").glob("*.md")
        if p.name not in _SKIP
    )


@pytest.mark.parametrize("md", _manuscript_files())
def test_manuscript_statistic_is_token_or_validated(md: str):
    by_anchor = _ledger_numbers_by_anchor()
    raw = (PROJECT_ROOT / "manuscript" / md).read_text(encoding="utf-8")
    anchors = _file_section_anchors(raw)
    accepted: set[str] = set()
    for anchor in anchors:
        accepted |= by_anchor.get(anchor, set())
    offenders = _stat_offenders(_strip(raw), accepted)
    assert not offenders, (
        f"{md}: statistic(s) neither auto-injected as a {{{{TOKEN}}}} nor validated "
        f"in data/claim_ledger.yaml for this section's anchor(s) "
        f"{sorted(anchors)}: {offenders}"
    )


def test_gate_detects_a_planted_hardcoded_stat():
    """Negative control: the detector must flag an unregistered statistic."""
    planted = "The trade is worth $7,777, spans 9,999 species, and raises 777 trillion insects.\n"
    hits = _stat_offenders(_strip(planted), _ledger_number_corpus())
    assert any("7,777" in h or "7777" in h for h in hits)
    assert any("9,999" in h or "9999" in h for h in hits)
    assert any("777 trillion" in h for h in hits)


def test_number_valid_in_one_section_is_rejected_in_an_unrelated_section():
    """A figure registered for one anchor must not validate in another section.

    ``94.7`` is justified only by the North-American protection-gap claim, which
    is anchored at ``sec:protected``. Planted into a ``sec:welfare`` section it
    must be flagged as an offender; the identical prose must still pass when the
    accepted set is scoped to its own ``sec:protected`` anchor. This is the
    property a global number pool would silently break.
    """
    by_anchor = _ledger_numbers_by_anchor()
    assert "94.7" in by_anchor.get("sec:protected", set())
    assert "94.7" not in by_anchor.get("sec:welfare", set())

    planted = _strip("Advocates note that 94.7 percent of colonies were affected.\n")

    rejected = _stat_offenders(planted, by_anchor.get("sec:welfare", set()))
    assert any("94.7" in h for h in rejected), (
        "per-section scoping failed: a sec:protected-only number passed in "
        "an unrelated sec:welfare section"
    )

    accepted = _stat_offenders(planted, by_anchor.get("sec:protected", set()))
    assert not any(
        "94.7" in h for h in accepted
    ), "the same number must validate in the section its claim is anchored to"
