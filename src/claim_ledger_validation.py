from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from .claim_ledger_loading import load_claims
from .claim_ledger_models import (
    CONFIDENCES,
    STATUS_DOCUMENTED,
    STATUS_VERIFIED,
    STATUS_VERIFIED_WITH_NUANCE,
    VERIFICATION_STATUSES,
    Claim,
)
from .validation import SEVERITY_ERROR, ValidationFinding

_QUOTE_REQUIRED_STATUSES = frozenset({STATUS_VERIFIED, STATUS_VERIFIED_WITH_NUANCE})
_URL_RE = re.compile(r"^https?://[^\s]+$")
_REPO_PATH_RE = re.compile(r"\b(src/[\w./-]+\.py)\b")
_MIN_QUOTE_LEN = 8
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _verification_findings(entry: Claim, root: Path) -> Iterable[ValidationFinding]:
    v = entry.verification
    if v is None:
        yield ValidationFinding(
            SEVERITY_ERROR,
            "claim_ledger",
            entry.claim_id,
            "missing verification block (status/source_url/source_quote(s)/as_of/checked)",
        )
        return
    if v.status not in VERIFICATION_STATUSES:
        yield ValidationFinding(
            SEVERITY_ERROR,
            "claim_ledger",
            entry.claim_id,
            f"verification.status={v.status!r} not in {VERIFICATION_STATUSES}",
        )
    if v.confidence not in CONFIDENCES:
        yield ValidationFinding(
            SEVERITY_ERROR,
            "claim_ledger",
            entry.claim_id,
            f"verification.confidence={v.confidence!r} not in {CONFIDENCES}",
        )
    if not v.source_url:
        yield ValidationFinding(SEVERITY_ERROR, "claim_ledger", entry.claim_id, "verification.source_url is empty")
    if not v.verified_value:
        yield ValidationFinding(SEVERITY_ERROR, "claim_ledger", entry.claim_id, "verification.verified_value is empty")
    if not v.as_of:
        yield ValidationFinding(SEVERITY_ERROR, "claim_ledger", entry.claim_id, "verification.as_of is empty")
    if not v.checked:
        yield ValidationFinding(SEVERITY_ERROR, "claim_ledger", entry.claim_id, "verification.checked is empty")
    elif not _ISO_DATE_RE.match(v.checked):
        yield ValidationFinding(
            SEVERITY_ERROR,
            "claim_ledger",
            entry.claim_id,
            f"verification.checked={v.checked!r} is not an ISO date (YYYY-MM-DD)",
        )
    if v.source_url and not _URL_RE.match(v.source_url):
        yield ValidationFinding(
            SEVERITY_ERROR,
            "claim_ledger",
            entry.claim_id,
            f"verification.source_url={v.source_url!r} is not a well-formed http(s) URL",
        )
    if v.status in _QUOTE_REQUIRED_STATUSES and not v.source_quotes:
        yield ValidationFinding(
            SEVERITY_ERROR,
            "claim_ledger",
            entry.claim_id,
            f"verification.status={v.status!r} requires at least one non-empty "
            "source_quote (the live oracle confirms it)",
        )
    elif v.status in _QUOTE_REQUIRED_STATUSES:
        for quote in v.source_quotes:
            if len(quote.strip()) < _MIN_QUOTE_LEN:
                yield ValidationFinding(
                    SEVERITY_ERROR,
                    "claim_ledger",
                    entry.claim_id,
                    f"verification.source_quote={quote!r} is too short "
                    f"(<{_MIN_QUOTE_LEN} chars) to resist incidental matches",
                )
    if v.status == STATUS_DOCUMENTED:
        cited_paths = _REPO_PATH_RE.findall(v.verified_value)
        if not cited_paths:
            yield ValidationFinding(
                SEVERITY_ERROR,
                "claim_ledger",
                entry.claim_id,
                "verification.status='documented' must cite an in-repo module "
                "(e.g. src/statutes.py) in verified_value",
            )
        for rel in cited_paths:
            if not (root / rel).exists():
                yield ValidationFinding(
                    SEVERITY_ERROR,
                    "claim_ledger",
                    entry.claim_id,
                    f"documented-status module path {rel!r} does not exist in the repo",
                )


def validate_claim_ledger(project_root: Path | None = None) -> Iterable[ValidationFinding]:
    root = (project_root or Path(__file__).resolve().parent.parent).resolve()
    ledger_path = root / "data" / "claim_ledger.yaml"
    manuscript_dir = root / "manuscript"
    bib_path = manuscript_dir / "references.bib"

    claims = load_claims(ledger_path)
    if not claims:
        return

    from .manuscript_variables import bibtex_key_inventory, manuscript_anchor_inventory

    declared = bibtex_key_inventory(bib_path)
    anchors = manuscript_anchor_inventory(manuscript_dir)

    for entry in claims:
        if entry.source not in declared:
            yield ValidationFinding(
                SEVERITY_ERROR,
                "claim_ledger",
                entry.claim_id,
                f"source={entry.source!r} not in references.bib",
            )
        if entry.anchor not in anchors:
            yield ValidationFinding(
                SEVERITY_ERROR,
                "claim_ledger",
                entry.claim_id,
                f"anchor={entry.anchor!r} not declared in manuscript/*.md",
            )
        yield from _verification_findings(entry, root)
