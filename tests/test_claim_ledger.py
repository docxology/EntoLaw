"""Tests for the claim-ledger loader and fail-closed verification oracle."""

from __future__ import annotations

from pathlib import Path

from src import claim_ledger as cl

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _err_msgs(findings):
    return " ".join(f.message for f in findings)


def test_real_ledger_loads_and_validates_clean():
    claims = cl.load_claims(PROJECT_ROOT / "data" / "claim_ledger.yaml")
    assert len(claims) >= 3
    assert all(c.verification is not None for c in claims)
    findings = list(cl.validate_claim_ledger(PROJECT_ROOT))
    assert not [f for f in findings if f.severity == "error"]


def test_high_risk_current_claims_are_ledgered():
    claim_ids = {
        c.claim_id for c in cl.load_claims(PROJECT_ROOT / "data" / "claim_ledger.yaml")
    }
    assert {
        "ca-vector-districts-1915",
        "monarch-proposed-not-final-2026",
        "new-world-screwworm-texas-2026",
        "farmed-insects-trillion-scale",
    } <= claim_ids


def test_claim_coverage_by_anchor_includes_declared_sections():
    coverage = cl.claim_coverage_by_anchor(PROJECT_ROOT)
    assert coverage["sec:protected"] >= 2
    assert coverage["sec:threat"] >= 1
    assert coverage["sec:invention"] >= 1
    assert coverage["sec:welfare"] >= 2
    assert all(anchor.startswith("sec:") for anchor in coverage)
    assert list(coverage) == [
        "sec:abstract",
        "sec:introduction",
        "sec:witness",
        "sec:threat",
        "sec:protected",
        "sec:property",
        "sec:invention",
        "sec:defendant",
        "sec:welfare",
        "sec:weapon",
        "sec:interconnections",
        "sec:methods",
        "sec:conclusion",
        "sec:references",
    ]


def test_load_claims_missing_file_returns_empty(tmp_path):
    assert cl.load_claims(tmp_path / "absent.yaml") == ()


def _claim(**v):
    base = dict(
        status="verified",
        verified_value="value",
        source_url="https://example.org/a",
        source_quote="a quotable phrase",
        as_of="2026",
        confidence="high",
        checked="2026-06-25",
    )
    base.update(v)
    return cl.Claim(
        claim_id="c",
        claim="claim",
        source="src",
        anchor="sec:x",
        verification=cl.ClaimVerification(
            status=base["status"],
            verified_value=base["verified_value"],
            source_url=base["source_url"],
            source_quote=base["source_quote"],
            as_of=base["as_of"],
            confidence=base["confidence"],
            checked=base["checked"],
            source_quotes=(base["source_quote"],) if base["source_quote"] else (),
        ),
    )


def test_missing_verification_block_is_error():
    claim = cl.Claim("c", "claim", "src", "sec:x", verification=None)
    findings = list(cl._verification_findings(claim, PROJECT_ROOT))
    assert "missing verification block" in _err_msgs(findings)


def test_verification_field_errors():
    cases = {
        "verification.status": _claim(status="bogus"),
        "verification.confidence": _claim(confidence="bogus"),
        "verification.source_url is empty": _claim(source_url=""),
        "verification.verified_value is empty": _claim(verified_value=""),
        "verification.as_of is empty": _claim(as_of=""),
        "verification.checked is empty": _claim(checked=""),
        "is not an ISO date": _claim(checked="June 2026"),
        "not a well-formed http": _claim(source_url="ftp://x"),
    }
    for needle, claim in cases.items():
        assert needle in _err_msgs(list(cl._verification_findings(claim, PROJECT_ROOT)))


def test_quote_requirements():
    no_quote = _claim(source_quote="")
    assert "requires at least one non-empty source_quote" in _err_msgs(
        list(cl._verification_findings(no_quote, PROJECT_ROOT))
    )
    short = _claim(source_quote="tiny")
    assert "too short" in _err_msgs(
        list(cl._verification_findings(short, PROJECT_ROOT))
    )


def test_documented_status_requires_real_repo_path():
    no_path = _claim(status="documented", verified_value="no path here")
    assert "must cite an in-repo module" in _err_msgs(
        list(cl._verification_findings(no_path, PROJECT_ROOT))
    )
    bad_path = _claim(status="documented", verified_value="see src/nope.py")
    assert "does not exist in the repo" in _err_msgs(
        list(cl._verification_findings(bad_path, PROJECT_ROOT))
    )
    good = _claim(status="documented", verified_value="encoded in src/roles.py")
    assert not list(cl._verification_findings(good, PROJECT_ROOT))


def test_coerce_source_quotes_dedupes_and_accepts_string():
    raw = {"source_quote": "alpha", "source_quotes": "beta"}
    assert cl._coerce_source_quotes(raw) == ("alpha", "beta")
    raw2 = {"source_quote": "alpha", "source_quotes": ["alpha", "gamma"]}
    assert cl._coerce_source_quotes(raw2) == ("alpha", "gamma")


def test_source_and_anchor_must_resolve(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "manuscript").mkdir()
    (tmp_path / "manuscript" / "references.bib").write_text(
        "@misc{realkey, title={x}}\n", encoding="utf-8"
    )
    (tmp_path / "manuscript" / "s.md").write_text("# S {#sec:real}\n", encoding="utf-8")
    (tmp_path / "data" / "claim_ledger.yaml").write_text(
        "claims:\n"
        "  - id: c1\n"
        "    claim: x\n"
        "    source: missingkey\n"
        "    anchor: sec:missing\n"
        "    verification:\n"
        "      status: verified\n"
        "      verified_value: v\n"
        "      source_url: https://example.org/a\n"
        "      source_quote: a quotable phrase\n"
        "      as_of: '2026'\n"
        "      confidence: high\n"
        "      checked: '2026-06-25'\n",
        encoding="utf-8",
    )
    msgs = _err_msgs(list(cl.validate_claim_ledger(tmp_path)))
    assert "not in references.bib" in msgs
    assert "not declared in manuscript" in msgs
