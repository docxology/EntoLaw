"""Validation-layer tests: clean registries pass; injected bad data fails.

Bad data is constructed as real dataclass instances (no mocks) and passed to
the injectable validators so every fail-closed branch is exercised.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src import validation
from src.cases import Case
from src.institutions import Institution
from src.interconnections import Interconnection
from src.roles import LegalRole
from src.species import Taxon
from src.statutes import Statute
from src.timeline import Milestone

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _errors(findings):
    return [f for f in findings if f.severity == validation.SEVERITY_ERROR]


def test_validation_finding_rejects_bad_severity():
    with pytest.raises(ValueError):
        validation.ValidationFinding("nope", "s", "t", "m")


def test_summary_ok_property():
    summ = validation.validate_registries(PROJECT_ROOT)
    assert summ.ok
    assert summ.counts["error"] == 0


def test_clean_registries_yield_no_errors():
    for fn in (
        validation.validate_roles,
        validation.validate_cases,
        validation.validate_statutes,
        validation.validate_species,
        validation.validate_institutions,
        validation.validate_timeline,
        validation.validate_interconnections,
    ):
        assert not _errors(list(fn()))


def test_bad_roles_flagged():
    good = LegalRole("witness", "T", "D", "Q", "sec:witness")
    dup = LegalRole("witness", "T", "D", "Q", "sec:witness")
    bad_anchor = LegalRole("x", "T", "D", "Q", "witness")
    empty_q = LegalRole("y", "T", "D", "  ", "sec:y")
    findings = list(validation.validate_roles([good, dup, bad_anchor, empty_q]))
    msgs = " ".join(f.message for f in findings)
    assert "duplicate role slug" in msgs
    assert "not a sec:* anchor" in msgs


def test_bad_cases_flagged():
    bad = Case("x", "n", "not a citation", 2020, "Mars court", "nope", "", "s")
    dup_a = Case("d", "n", "509 U.S. 579", 1, "U.S. Supreme Court", "witness", "h", "s")
    dup_b = Case("d", "n", "509 U.S. 579", 1, "U.S. Supreme Court", "witness", "h", "s")
    findings = _errors(list(validation.validate_cases([bad, dup_a, dup_b])))
    msgs = " ".join(f.message for f in findings)
    assert "does not match the citation grammar" in msgs
    assert "outside vocabulary" in msgs
    assert "holding is empty" in msgs
    assert "duplicate case slug" in msgs


def test_bad_statutes_flagged():
    bad = Statute(
        "x",
        "no instrument",
        "t",
        "badcat",
        "Atlantis",
        "norole",
        "",
        ("not an instrument",),
    )
    findings = list(validation.validate_statutes([bad]))
    msgs = " ".join(f.message for f in findings)
    assert "is not a recognised instrument" in msgs
    assert "category" in msgs and "jurisdiction" in msgs
    assert "summary is empty" in msgs


def test_bad_species_flagged():
    bad = Taxon("x", "  ", "c", "norole", "  ", "i", "n")
    dup_a = Taxon("d", "Sci", "c", "witness", "ok", "i", "n")
    dup_b = Taxon("d", "Sci", "c", "witness", "ok", "i", "n")
    findings = list(validation.validate_species([bad, dup_a, dup_b]))
    msgs = " ".join(f.message for f in findings)
    assert "scientific_name is empty" in msgs
    assert "role" in msgs and "outside vocabulary" in msgs
    assert "duplicate taxon slug" in msgs


def test_bad_institutions_flagged():
    bad = Institution("x", "n", "a", "norole", "  ")
    findings = list(validation.validate_institutions([bad]))
    msgs = " ".join(f.message for f in findings)
    assert "outside vocabulary" in msgs
    assert "function is empty" in msgs


def test_bad_timeline_flagged():
    bad = Milestone(-2500, "t", "norole", "d")
    findings = _errors(list(validation.validate_timeline([bad])))
    msgs = " ".join(f.message for f in findings)
    assert "outside vocabulary" in msgs
    assert "outside the plausible range" in msgs


def test_bad_interconnections_flagged():
    too_few = Interconnection("a", "t", ("witness",), "d")
    bad_role = Interconnection("b", "t", ("witness", "norole"), "d")
    dup_a = Interconnection("c", "t", ("witness", "threat"), "d")
    dup_b = Interconnection("c", "t", ("witness", "threat"), "d")
    findings = list(
        validation.validate_interconnections([too_few, bad_role, dup_a, dup_b])
    )
    msgs = " ".join(f.message for f in findings)
    assert "at least two roles" in msgs
    assert "outside vocabulary" in msgs
    assert "duplicate interconnection slug" in msgs


def test_write_validation_report(tmp_path):
    summ = validation.validate_registries(PROJECT_ROOT)
    out = validation.write_validation_report(summ, tmp_path / "v.json")
    assert out.exists()
    assert '"ok": true' in out.read_text(encoding="utf-8")
