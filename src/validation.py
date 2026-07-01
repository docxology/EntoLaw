"""Cross-cutting validation layer for the entomological-law registries.

Every registry validator is a pure function returning
``Iterable[ValidationFinding]``; :func:`validate_registries` concatenates them
and the claim-ledger validator into one :class:`ValidationSummary`. The layer
fails closed: a malformed citation, an out-of-vocabulary role/category, a
duplicate slug, or an empty required field is an ``error`` finding, and
``scripts/run_inventory.py`` writes the result to
``output/reports/validation.json``.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping

from . import (
    cases,
    institutions,
    interconnections,
    roles,
    species,
    statutes,
    timeline,
)
from .citations import citation_is_parseable, instrument_is_recognised

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"
SEVERITIES: tuple[str, ...] = (SEVERITY_ERROR, SEVERITY_WARNING, SEVERITY_INFO)

_ANCHOR_RE = re.compile(r"^sec:[a-z_]+$")


@dataclass(frozen=True)
class ValidationFinding:
    """A single validation finding.

    Attributes:
        severity: One of :data:`SEVERITIES`.
        source: Dotted identifier of the validator (e.g. ``"registry.cases"``).
        target: Identifier of the entity (slug / citation). Empty when global.
        message: One-sentence human-readable description.
    """

    severity: str
    source: str
    target: str
    message: str

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity {self.severity!r} not in {SEVERITIES}")


@dataclass(frozen=True)
class ValidationSummary:
    """Counts of findings by severity, plus the findings themselves."""

    findings: tuple[ValidationFinding, ...]
    counts: Mapping[str, int]

    @property
    def ok(self) -> bool:
        """``True`` iff no ``error``-severity findings are present."""
        return self.counts.get(SEVERITY_ERROR, 0) == 0


def _err(source: str, target: str, message: str) -> ValidationFinding:
    return ValidationFinding(SEVERITY_ERROR, source, target, message)


def _warn(source: str, target: str, message: str) -> ValidationFinding:
    return ValidationFinding(SEVERITY_WARNING, source, target, message)


# ── Registry validators ─────────────────────────────────────────────────


def validate_roles(items=None) -> Iterable[ValidationFinding]:
    """Validate role slug uniqueness, anchor shape, and non-empty fields."""
    items = roles.all_roles() if items is None else items
    seen: set[str] = set()
    for role in items:
        if role.slug in seen:
            yield _err("registry.roles", role.slug, "duplicate role slug")
        seen.add(role.slug)
        if not _ANCHOR_RE.match(role.anchor):
            yield _err(
                "registry.roles",
                role.slug,
                f"anchor {role.anchor!r} is not a sec:* anchor",
            )
        if not role.core_question.strip():
            yield _warn("registry.roles", role.slug, "core_question is empty")


def validate_cases(items=None) -> Iterable[ValidationFinding]:
    """Validate case citations, role/jurisdiction vocab, and uniqueness."""
    items = cases.all_cases() if items is None else items
    valid_roles = set(roles.role_slugs())
    seen: set[str] = set()
    for case in items:
        if case.slug in seen:
            yield _err("registry.cases", case.slug, "duplicate case slug")
        seen.add(case.slug)
        if not citation_is_parseable(case.citation):
            yield _err(
                "registry.cases",
                case.slug,
                f"citation {case.citation!r} does not match the citation grammar",
            )
        if case.role not in valid_roles:
            yield _err(
                "registry.cases", case.slug, f"role {case.role!r} outside vocabulary"
            )
        if case.jurisdiction not in cases.JURISDICTIONS:
            yield _err(
                "registry.cases",
                case.slug,
                f"jurisdiction {case.jurisdiction!r} outside vocabulary",
            )
        if not case.holding.strip():
            yield _err("registry.cases", case.slug, "holding is empty")


def validate_statutes(items=None) -> Iterable[ValidationFinding]:
    """Validate statute citations, category/jurisdiction/role vocab, x-refs."""
    items = statutes.all_statutes() if items is None else items
    valid_roles = set(roles.role_slugs())
    seen: set[str] = set()
    for statute in items:
        if statute.slug in seen:
            yield _err("registry.statutes", statute.slug, "duplicate statute slug")
        seen.add(statute.slug)
        if not instrument_is_recognised(statute.citation):
            yield _err(
                "registry.statutes",
                statute.slug,
                f"citation {statute.citation!r} is not a recognised instrument",
            )
        if statute.category not in statutes.categories():
            yield _err(
                "registry.statutes",
                statute.slug,
                f"category {statute.category!r} outside vocabulary",
            )
        if statute.jurisdiction not in statutes.jurisdictions():
            yield _err(
                "registry.statutes",
                statute.slug,
                f"jurisdiction {statute.jurisdiction!r} outside vocabulary",
            )
        if statute.role not in valid_roles:
            yield _err(
                "registry.statutes",
                statute.slug,
                f"role {statute.role!r} outside vocabulary",
            )
        if not statute.summary.strip():
            yield _warn("registry.statutes", statute.slug, "summary is empty")
        for cross in statute.cross_references:
            if not instrument_is_recognised(cross):
                yield _warn(
                    "registry.statutes",
                    statute.slug,
                    f"cross_reference {cross!r} is not a recognised instrument",
                )


def validate_species(items=None) -> Iterable[ValidationFinding]:
    """Validate taxa role vocab, non-empty names, and uniqueness."""
    items = species.all_taxa() if items is None else items
    valid_roles = set(roles.role_slugs())
    seen: set[str] = set()
    for taxon in items:
        if taxon.slug in seen:
            yield _err("registry.species", taxon.slug, "duplicate taxon slug")
        seen.add(taxon.slug)
        if taxon.role not in valid_roles:
            yield _err(
                "registry.species",
                taxon.slug,
                f"role {taxon.role!r} outside vocabulary",
            )
        if not taxon.scientific_name.strip():
            yield _err("registry.species", taxon.slug, "scientific_name is empty")
        if not taxon.status.strip():
            yield _warn("registry.species", taxon.slug, "status is empty")


def validate_institutions(items=None) -> Iterable[ValidationFinding]:
    """Validate institution role vocab and uniqueness."""
    items = institutions.all_institutions() if items is None else items
    valid_roles = set(roles.role_slugs())
    seen: set[str] = set()
    for inst in items:
        if inst.slug in seen:
            yield _err("registry.institutions", inst.slug, "duplicate institution slug")
        seen.add(inst.slug)
        if inst.role not in valid_roles:
            yield _err(
                "registry.institutions",
                inst.slug,
                f"role {inst.role!r} outside vocabulary",
            )
        if not inst.function.strip():
            yield _warn("registry.institutions", inst.slug, "function is empty")


def validate_timeline(items=None) -> Iterable[ValidationFinding]:
    """Validate milestone role vocab and sane year ordering."""
    items = timeline.all_milestones() if items is None else items
    valid_roles = set(roles.role_slugs())
    for milestone in items:
        if milestone.role not in valid_roles:
            yield _err(
                "registry.timeline",
                milestone.title,
                f"role {milestone.role!r} outside vocabulary",
            )
        if not (-2000 <= milestone.year <= 2100):
            yield _err(
                "registry.timeline",
                milestone.title,
                f"year {milestone.year} outside the plausible range",
            )


def validate_interconnections(items=None) -> Iterable[ValidationFinding]:
    """Validate interconnection role membership and arity (>= 2 roles)."""
    items = interconnections.all_interconnections() if items is None else items
    valid_roles = set(roles.role_slugs())
    seen: set[str] = set()
    for link in items:
        if link.slug in seen:
            yield _err(
                "registry.interconnections", link.slug, "duplicate interconnection slug"
            )
        seen.add(link.slug)
        if len(link.roles) < 2:
            yield _err(
                "registry.interconnections",
                link.slug,
                "an interconnection must link at least two roles",
            )
        for role_slug in link.roles:
            if role_slug not in valid_roles:
                yield _err(
                    "registry.interconnections",
                    link.slug,
                    f"role {role_slug!r} outside vocabulary",
                )


# ── Aggregator ──────────────────────────────────────────────────────────


def validate_registries(project_root: Path | None = None) -> ValidationSummary:
    """Run every registry validator and the claim-ledger validator."""
    from .claim_ledger import validate_claim_ledger

    all_findings: list[ValidationFinding] = []
    all_findings.extend(validate_roles())
    all_findings.extend(validate_cases())
    all_findings.extend(validate_statutes())
    all_findings.extend(validate_species())
    all_findings.extend(validate_institutions())
    all_findings.extend(validate_timeline())
    all_findings.extend(validate_interconnections())
    all_findings.extend(validate_claim_ledger(project_root))

    counts: dict[str, int] = {s: 0 for s in SEVERITIES}
    for finding in all_findings:
        counts[finding.severity] += 1
    return ValidationSummary(findings=tuple(all_findings), counts=counts)


def write_validation_report(summary: ValidationSummary, path: Path) -> Path:
    """Persist the summary as a JSON report at ``path``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ok": summary.ok,
        "counts": dict(summary.counts),
        "findings": [asdict(f) for f in summary.findings],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path
