from __future__ import annotations

import re
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from .claim_ledger_models import Claim, ClaimVerification


def _coerce_source_quotes(raw: dict) -> tuple[str, ...]:
    quotes: list[str] = []
    primary = raw.get("source_quote", "")
    if isinstance(primary, str) and primary.strip():
        quotes.append(primary.strip())
    supplemental = raw.get("source_quotes", ())
    if isinstance(supplemental, str):
        supplemental = (supplemental,)
    if isinstance(supplemental, (list, tuple)):
        for item in supplemental:
            quote = str(item).strip()
            if quote:
                quotes.append(quote)
    deduped: list[str] = []
    seen: set[str] = set()
    for quote in quotes:
        if quote not in seen:
            deduped.append(quote)
            seen.add(quote)
    return tuple(deduped)


def _load_verification(entry: dict) -> ClaimVerification | None:
    raw = entry.get("verification")
    if not isinstance(raw, dict):
        return None
    source_quotes = _coerce_source_quotes(raw)
    source_quote = str(raw.get("source_quote", "")) or (
        source_quotes[0] if source_quotes else ""
    )
    return ClaimVerification(
        status=str(raw.get("status", "")),
        verified_value=str(raw.get("verified_value", "")),
        source_url=str(raw.get("source_url", "")),
        source_quote=source_quote,
        as_of=str(raw.get("as_of", "")),
        confidence=str(raw.get("confidence", "")),
        checked=str(raw.get("checked", "")),
        source_quotes=source_quotes,
    )


def load_claims(path: Path) -> tuple[Claim, ...]:
    if not path.exists():
        return ()
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    claims: list[Claim] = []
    for entry in payload.get("claims") or []:
        claims.append(
            Claim(
                claim_id=str(entry["id"]),
                claim=str(entry["claim"]),
                source=str(entry["source"]),
                anchor=str(entry["anchor"]),
                verification=_load_verification(entry),
            )
        )
    return tuple(claims)


def claim_count(project_root: Path | None = None) -> int:
    root = (project_root or Path(__file__).resolve().parent.parent).resolve()
    return len(load_claims(root / "data" / "claim_ledger.yaml"))


def claim_coverage_by_anchor(project_root: Path | None = None) -> dict[str, int]:
    root = (project_root or Path(__file__).resolve().parent.parent).resolve()
    anchors = _section_anchors_in_manuscript_order(root / "manuscript")
    coverage = {anchor: 0 for anchor in anchors}
    for claim in load_claims(root / "data" / "claim_ledger.yaml"):
        coverage.setdefault(claim.anchor, 0)
        coverage[claim.anchor] += 1
    return coverage


def _section_anchors_in_manuscript_order(manuscript_dir: Path) -> tuple[str, ...]:
    anchor_pattern = re.compile(r"\{#(sec:[A-Za-z0-9_:-]+)(?:\s+[^}]*)?\}")
    anchors: list[str] = []
    seen: set[str] = set()
    for path in sorted(manuscript_dir.glob("*.md")):
        if path.name in {"AGENTS.md", "README.md", "SYNTAX.md"}:
            continue
        text = re.sub(r"`[^`]*`", "", path.read_text(encoding="utf-8"))
        for match in anchor_pattern.finditer(text):
            anchor = match.group(1)
            if anchor not in seen:
                anchors.append(anchor)
                seen.add(anchor)
    return tuple(anchors)
