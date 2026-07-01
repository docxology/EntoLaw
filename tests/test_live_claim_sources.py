"""Live oracle for the claim ledger (run with ``-m live``).

Fetches each claim's ``source_url`` and asserts every recorded quote snippet is
present, so "verified" is a re-runnable fact rather than a stored assertion.
Skipped by default (the offline suite must stay network-free); enable with
``uv run pytest -m live``. Honors ``ENTOLAW_OFFLINE=1`` as an explicit skip.
"""

from __future__ import annotations

import os
import re
import urllib.request
from pathlib import Path

import pytest

from src.claim_ledger import load_claims

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_CLAIMS = load_claims(PROJECT_ROOT / "data" / "claim_ledger.yaml")

pytestmark = pytest.mark.live


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).lower()


@pytest.mark.skipif(
    os.environ.get("ENTOLAW_OFFLINE") == "1", reason="offline mode requested"
)
@pytest.mark.parametrize("claim", _CLAIMS, ids=[c.claim_id for c in _CLAIMS])
def test_claim_source_quote_is_live(claim):
    v = claim.verification
    assert v is not None and v.source_url
    req = urllib.request.Request(v.source_url, headers={"User-Agent": "EntoLaw/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        body = _normalize(resp.read().decode("utf-8", errors="replace"))
    for quote in v.source_quotes:
        assert _normalize(quote) in body, f"{claim.claim_id}: missing quote {quote!r}"
