"""Tests for the legal-citation parser."""

from __future__ import annotations

import pytest

from src import citations


@pytest.mark.parametrize(
    "text,kind",
    [
        ("7 U.S.C. § 7712", "statute"),
        ("7 C.F.R. § 301.92", "statute"),
        ("Regulation (EU) 2015/2283", "eu_instrument"),
        ("Directive 2010/63/EU", "eu_instrument"),
        ("85 FR 81737", "federal_register"),
        ("U.S. Patent 4,736,866", "patent"),
        ("No. 22-1052", "docket"),
        ("Colorado HB24-1117 (2024)", "state_bill"),
        ("Utah H.B. 138 (2025)", "state_bill"),
        ("Fed. R. Evid. 702", "rule"),
        ("[1939] 1 KB 471", "uk_case"),
        ("509 U.S. 579", "case"),
        ("79 Cal.App.5th 337", "case"),
        ("Biological Weapons Convention (1972)", "named_instrument"),
        ("Animal Welfare (Sentience) Act 2022", "named_instrument"),
        ("a plain sentence with no citation", "unrecognised"),
    ],
)
def test_citation_kind(text, kind):
    assert citations.citation_kind(text) == kind


def test_citation_is_parseable_true_and_false():
    assert citations.citation_is_parseable("447 U.S. 303")
    assert not citations.citation_is_parseable("just some words here")


def test_reporter_citation_requires_a_reporter_word():
    # Two bare numbers must NOT pass as a reporter citation (regression for the
    # zero-reporter-word false positive).
    assert not citations.citation_is_parseable("100 200")
    assert not citations.citation_is_parseable("2 3")
    # A real citation with a reporter token still parses.
    assert citations.citation_is_parseable("15 Wend. 550")


def test_instrument_is_recognised_accepts_named_acts():
    assert citations.instrument_is_recognised("Honeybee Act of 1922")
    assert citations.instrument_is_recognised("509 U.S. 579")
    assert not citations.instrument_is_recognised("not an instrument at all")


def test_extract_year_prefers_parenthetical():
    assert citations.extract_year("293 F. 1013 (D.C. Cir. 1923)") == 1923
    assert citations.extract_year("[1939] 1 KB 471") == 1939
    assert citations.extract_year("Honeybee Act of 1922") == 1922
    assert citations.extract_year("no year here") is None
