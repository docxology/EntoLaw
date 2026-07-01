"""Registered legal roles an insect can occupy — the spine of the field.

Entomological law has no single statute or casebook. It coheres around the
*legal status an insect occupies in a given dispute*: the same organism is,
in turn, a witness, a regulated threat, a protected subject, property, an
invention, a defendant, a moral patient, or a weapon. Each role poses a core
legal question the system was not designed to answer, and each is governed by
a distinct cluster of doctrine.

This registry is the source of truth for the manuscript's per-role sections,
the role-count token, and the role/domain figures. Cases, statutes, species,
and timeline events all tag themselves with one of these ``slug`` values, and
:mod:`src.validation` fails closed if any of them references a role not
declared here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class LegalRole:
    """One legal role an insect can occupy.

    Attributes:
        slug: Stable lower-snake-case identifier used as the cross-reference
            key by every other registry.
        title: Human-readable role name (e.g. ``"Witness / evidence"``).
        domain: The named legal sub-field (e.g. ``"Forensic entomology"``).
        core_question: The question this role forces the legal system to
            answer.
        anchor: The manuscript section anchor (``sec:*``) where the role is
            treated, so prose cross-references and the registry cannot drift.
    """

    slug: str
    title: str
    domain: str
    core_question: str
    anchor: str


LEGAL_ROLES: tuple[LegalRole, ...] = (
    LegalRole(
        slug="witness",
        title="Witness / evidence",
        domain="Forensic entomology",
        core_question="When did death occur, and where?",
        anchor="sec:witness",
    ),
    LegalRole(
        slug="threat",
        title="Regulated threat",
        domain="Quarantine & invasive-species law",
        core_question="May this organism cross a border?",
        anchor="sec:threat",
    ),
    LegalRole(
        slug="protected",
        title="Protected subject",
        domain="Conservation / endangered-species law",
        core_question="Does the state owe this species survival?",
        anchor="sec:protected",
    ),
    LegalRole(
        slug="property",
        title="Property",
        domain="Common law of wild animals",
        core_question="Who owns this swarm, hive, or specimen?",
        anchor="sec:property",
    ),
    LegalRole(
        slug="invention",
        title="Invention / product",
        domain="IP, biotech & food law",
        core_question="Can this insect be patented, engineered, or eaten?",
        anchor="sec:invention",
    ),
    LegalRole(
        slug="defendant",
        title="Defendant",
        domain="Historical animal trials",
        core_question="Can a pest be tried and punished?",
        anchor="sec:defendant",
    ),
    LegalRole(
        slug="moral_patient",
        title="Moral patient",
        domain="Emerging welfare & sentience law",
        core_question="Can an insect be wronged?",
        anchor="sec:welfare",
    ),
    LegalRole(
        slug="weapon",
        title="Weapon",
        domain="International humanitarian law & biosecurity",
        core_question="May insects be used in war?",
        anchor="sec:weapon",
    ),
)


def all_roles() -> tuple[LegalRole, ...]:
    """Return every declared legal role, in canonical order."""
    return LEGAL_ROLES


def role_slugs() -> tuple[str, ...]:
    """Return the controlled vocabulary of role slugs."""
    return tuple(role.slug for role in LEGAL_ROLES)


def find(slug: str) -> LegalRole:
    """Return the role with ``slug`` or raise ``KeyError``."""
    for role in LEGAL_ROLES:
        if role.slug == slug:
            return role
    raise KeyError(f"unknown legal role slug: {slug}")


def role_table_markdown() -> str:
    """Render the role taxonomy as a markdown table for manuscript injection."""
    header = "| Legal role of the insect | Domain | Core question |"
    sep = "|---|---|---|"
    rows: list[str] = [header, sep]
    for role in LEGAL_ROLES:
        rows.append(f"| {role.title} | {role.domain} | {role.core_question} |")
    return "\n".join(rows)


def roles_with(predicate) -> Iterable[LegalRole]:  # pragma: no cover - helper
    """Yield roles matching ``predicate`` (kept for downstream filters)."""
    return (role for role in LEGAL_ROLES if predicate(role))
