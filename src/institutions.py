"""Certifying and regulatory institutions of entomological law.

Each role has an institutional backbone — the certifying boards behind expert
testimony, the agencies that run quarantines and species listings, the food-
safety authorities that clear edible insects. This registry pins those bodies
to the role they serve so the manuscript can describe the field's machinery
without hard-coding institution counts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Institution:
    """A board, agency, or society operating within the field.

    Attributes:
        slug: Stable identifier.
        name: Full institution name.
        acronym: Common acronym (may equal a short form of the name).
        role: The :mod:`src.roles` slug it principally serves.
        function: One-sentence description of its legal function.
        founded: Founding/established year, if known.
    """

    slug: str
    name: str
    acronym: str
    role: str
    function: str
    founded: int | None = None


INSTITUTIONS: tuple[Institution, ...] = (
    Institution(
        slug="abfe",
        name="American Board of Forensic Entomology",
        acronym="ABFE",
        role="witness",
        function="Certifies North American forensic entomologists (Diplomate, "
        "Member, Technician) and can revoke certification for casework beyond "
        "scope.",
    ),
    Institution(
        slug="eafe",
        name="European Association for Forensic Entomology",
        acronym="EAFE",
        role="witness",
        function="Professional body coordinating forensic-entomology practice "
        "and standards in Europe.",
        founded=1996,
    ),
    Institution(
        slug="nafea",
        name="North American Forensic Entomology Association",
        acronym="NAFEA",
        role="witness",
        function="Hosts certification examinations and convenes North American "
        "forensic entomologists.",
        founded=1991,
    ),
    Institution(
        slug="osac",
        name="NIST OSAC Forensic Entomology Task Group",
        acronym="OSAC",
        role="witness",
        function="Develops documentary standards for forensic entomology within "
        "the US standards infrastructure.",
    ),
    Institution(
        slug="aphis_ppq",
        name="USDA APHIS Plant Protection and Quarantine",
        acronym="APHIS PPQ",
        role="threat",
        function="Determines what plants and pests may be imported or moved "
        "interstate and runs federal quarantines under the Plant Protection Act.",
    ),
    Institution(
        slug="ippc_secretariat",
        name="International Plant Protection Convention Secretariat",
        acronym="IPPC",
        role="threat",
        function="Maintains the ISPMs that serve as the phytosanitary benchmark "
        "under the WTO SPS Agreement.",
    ),
    Institution(
        slug="usfws",
        name="U.S. Fish and Wildlife Service",
        acronym="USFWS",
        role="protected",
        function="Lists and protects endangered insects under the ESA and "
        "enforces CITES insect-trade controls.",
    ),
    Institution(
        slug="xerces",
        name="Xerces Society for Invertebrate Conservation",
        acronym="Xerces",
        role="protected",
        function="Advocates for invertebrate listings and petitions, including "
        "the bumblebee CESA effort.",
    ),
    Institution(
        slug="cdfw",
        name="California Department of Fish and Wildlife",
        acronym="CDFW",
        role="protected",
        function="Administers the California Endangered Species Act, whose "
        "'fish' definition reaches invertebrates after Almond Alliance.",
    ),
    Institution(
        slug="epa_opp",
        name="EPA Office of Pesticide Programs",
        acronym="EPA OPP",
        role="invention",
        function="Registers pesticides and engineered insect releases under "
        "FIFRA and the Coordinated Framework.",
    ),
    Institution(
        slug="efsa",
        name="European Food Safety Authority",
        acronym="EFSA",
        role="invention",
        function="Issues the safety opinions that underpin EU novel-food "
        "authorizations for edible insects.",
    ),
    Institution(
        slug="central_silk_board",
        name="Central Silk Board (India)",
        acronym="CSB",
        role="invention",
        function="Statutory body regulating silkworm seed quality, the silk "
        "cess, and export policy under the Central Silk Board Act.",
        founded=1948,
    ),
)


def all_institutions() -> tuple[Institution, ...]:
    """Return every registered institution, in canonical order."""
    return INSTITUTIONS


def by_role(role_slug: str) -> tuple[Institution, ...]:
    """Return institutions serving ``role_slug``."""
    return tuple(i for i in INSTITUTIONS if i.role == role_slug)


def find(slug: str) -> Institution:
    """Return the institution with ``slug`` or raise ``KeyError``."""
    for institution in INSTITUTIONS:
        if institution.slug == slug:
            return institution
    raise KeyError(f"unknown institution slug: {slug}")
