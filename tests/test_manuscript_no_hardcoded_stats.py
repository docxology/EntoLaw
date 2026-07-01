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


def _ledger_number_corpus() -> set[str]:
    nums: set[str] = set()
    for c in load_claims(PROJECT_ROOT / "data" / "claim_ledger.yaml"):
        blob = [c.claim]
        if c.verification:
            blob += [c.verification.verified_value, c.verification.source_quote]
            blob += list(c.verification.source_quotes)
        for piece in blob:
            nums.update(_norm(m) for m in _NUM.findall(piece))
    return nums


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
    corpus = _ledger_number_corpus()
    raw = (PROJECT_ROOT / "manuscript" / md).read_text(encoding="utf-8")
    text = _strip(raw)
    offenders: list[str] = []
    for pat in _STAT_PATTERNS:
        for m in pat.finditer(text):
            num_match = _NUM.search(m.group(0))
            if not num_match:
                continue
            num = _norm(num_match.group(0))
            if num and num not in corpus:
                offenders.append(m.group(0).strip())
    assert not offenders, (
        f"{md}: statistic(s) neither auto-injected as a {{{{TOKEN}}}} nor validated "
        f"in data/claim_ledger.yaml: {offenders}"
    )


def test_gate_detects_a_planted_hardcoded_stat():
    """Negative control: the detector must flag an unregistered statistic."""
    planted = "The trade is worth $7,777, spans 9,999 species, and raises 777 trillion insects.\n"
    text = _strip(planted)
    corpus = _ledger_number_corpus()
    hits = []
    for pat in _STAT_PATTERNS:
        for m in pat.finditer(text):
            num = _norm(_NUM.search(m.group(0)).group(0))
            if num not in corpus:
                hits.append(m.group(0))
    assert any("7,777" in h or "7777" in h for h in hits)
    assert any("9,999" in h or "9999" in h for h in hits)
    assert any("777 trillion" in h for h in hits)
