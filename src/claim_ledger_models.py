from __future__ import annotations

from dataclasses import dataclass

STATUS_VERIFIED = "verified"
STATUS_VERIFIED_WITH_NUANCE = "verified_with_nuance"
STATUS_DOCUMENTED = "documented"
VERIFICATION_STATUSES: tuple[str, ...] = (
    STATUS_VERIFIED,
    STATUS_VERIFIED_WITH_NUANCE,
    STATUS_DOCUMENTED,
)
CONFIDENCES: tuple[str, ...] = ("high", "medium", "low")


@dataclass(frozen=True)
class ClaimVerification:
    status: str
    verified_value: str
    source_url: str
    source_quote: str
    as_of: str
    confidence: str
    checked: str
    source_quotes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Claim:
    claim_id: str
    claim: str
    source: str
    anchor: str
    verification: ClaimVerification | None = None
