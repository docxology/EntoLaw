# entolaw-size-ok: source-owned timeline registry records; split from facade for size gate.
"""Historical milestones of entomological law — the long historical arc.

The timeline carries the field's history-driven roles (the *defendant* of the
medieval animal trials and the *weapon* of entomological warfare) that have no
modern reporter citations, alongside the dated turning points of the
forensic, conservation, property, and biotech strands. Events are tagged with
a :mod:`src.roles` slug so the legislative/forensic timeline figure and the
role-coverage metrics draw from one source.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import roles


@dataclass(frozen=True)
class Milestone:
    """A dated milestone in the history of entomological law.

    Attributes:
        year: Year of the milestone.
        title: Short milestone name.
        role: The :mod:`src.roles` slug it belongs to.
        description: One-sentence source-anchored description.
    """

    year: int
    title: str
    role: str
    description: str


MILESTONES: tuple[Milestone, ...] = (
    Milestone(
        year=-1650,
        title="Hittite Laws on bees and hives",
        role="property",
        description="The Hittite Laws tariff theft of bees in a swarm and "
        "theft of bee hives, making apiculture property an early written "
        "legal category.",
    ),
    Milestone(
        year=200,
        title="Mishnah on beehives and nuisance",
        role="property",
        description="Mishnah Bava Batra treats beehives, bees, swarms, "
        "honeycombs, and mustard-near-bees conflict as sale and neighbor-law "
        "subjects.",
    ),
    Milestone(
        year=507,
        title="Salic Law on stolen bees",
        role="property",
        description="The Salic Law gives stolen bees their own theft title, "
        "showing that early successor-kingdom tariff law made bee property "
        "a named legal object.",
    ),
    Milestone(
        year=533,
        title="Justinian on bee property",
        role="property",
        description="Justinian's Institutes and Digest class bees as naturally "
        "wild: a swarm is owned by hiving it, and a departed swarm remains "
        "owned only while visible and easy to pursue.",
    ),
    Milestone(
        year=643,
        title="Rothari on hives and bee trees",
        role="property",
        description="Rothari's Lombard code distinguishes theft from an "
        "apiary vessel from taking bees out of another person's marked tree.",
    ),
    Milestone(
        year=1235,
        title="The Sickle Murder",
        role="witness",
        description="Song Ci records the first forensic entomology: flies settle "
        "on the one blade bearing invisible blood, forcing a confession.",
    ),
    Milestone(
        year=1290,
        title="Fleta on bee occupation",
        role="property",
        description="Fleta restates the medieval English rule that bees are "
        "wild by nature and become property only through effective enclosure "
        "or visible, practicable pursuit.",
    ),
    Milestone(
        year=1487,
        title="The slugs of Autun",
        role="defendant",
        description="An ecclesiastical court proceeds against crop-destroying "
        "slugs — one of the earliest documented insect/pest prosecutions.",
    ),
    Milestone(
        year=1531,
        title="Chassenée's treatise",
        role="defendant",
        description="Bartholomew Chassenée writes the first legal treatise on "
        "insect prosecution, arguing vermin are 'lay persons' entitled to "
        "counsel.",
    ),
    Milestone(
        year=1545,
        title="Weevils of St-Julien (first trial)",
        role="defendant",
        description="A vine-weevil prosecution is dismissed on the theory that "
        "the insects are a divine scourge.",
    ),
    Milestone(
        year=1587,
        title="Weevils of St-Julien (sequel)",
        role="defendant",
        description="In an eight-month trial the community offers the weevils a "
        "land preserve — an eerie foreshadowing of modern critical-habitat "
        "designation.",
    ),
    Milestone(
        year=1619,
        title="Virginia silk-input mandate",
        role="invention",
        description="Virginia's first assembly requires mulberry planting and "
        "silk-flax work, treating colonial silk inputs as statutory economic "
        "policy.",
    ),
    Milestone(
        year=1658,
        title="Virginia mulberry-tree act",
        role="invention",
        description="Colonial Virginia requires landowners to plant mulberry "
        "trees for silk production, treating silkworm infrastructure as public "
        "economic policy.",
    ),
    Milestone(
        year=1766,
        title="Blackstone on hived bees",
        role="property",
        description="Blackstone carries Roman bee doctrine into common-law "
        "commentary, treating hived bees as qualified property under both "
        "natural and civil law.",
    ),
    Milestone(
        year=1855,
        title="The Bergeret case",
        role="witness",
        description="Bergeret d'Arbois publishes the first Western post-mortem-"
        "interval estimate by insect succession (a mummified infant).",
    ),
    Milestone(
        year=1877,
        title="UK Destructive Insects Act",
        role="threat",
        description="Britain authorizes orders against Colorado beetle, including "
        "landing prohibitions, crop destruction, entry, records, compensation, "
        "and penalties.",
    ),
    Milestone(
        year=1884,
        title="Evans prints Bugs and Beasts",
        role="defendant",
        description="E.P. Evans publishes a pre-1900 English synthesis of "
        "animal and insect prosecutions, later expanded into his canonical "
        "book.",
    ),
    Milestone(
        year=1894,
        title="Mégnin's La Faune des Cadavres",
        role="witness",
        description="Jean-Pierre Mégnin systematizes the succession model of "
        "arthropod waves on remains.",
    ),
    Milestone(
        year=1912,
        title="Plant Quarantine Act",
        role="threat",
        description="Congress creates the federal plant-quarantine apparatus for "
        "plant diseases and insect pests with Bureau of Entomology participation.",
    ),
    Milestone(
        year=1922,
        title="Honeybee Act",
        role="property",
        description="Congress restricts honey-bee importation, the federal "
        "backbone of US apiculture law.",
    ),
    Milestone(
        year=1935,
        title="The Buck Ruxton 'Jigsaw Murders'",
        role="witness",
        description="The first UK murder conviction using entomology; larvae "
        "aged at 12–14 days.",
    ),
    Milestone(
        year=1940,
        title="Unit 731 Ningbo attack",
        role="weapon",
        description="Japan air-drops plague-infected fleas on Ningbo; the "
        "single attack causes roughly 1,500 deaths.",
    ),
    Milestone(
        year=1954,
        title="US Operation Big Itch",
        role="weapon",
        description="A Cold War US program tests uninfected flea dispersal for "
        "entomological warfare.",
    ),
    Milestone(
        year=1972,
        title="Biological Weapons Convention",
        role="weapon",
        description="The BWC treats insect vectors as covered means of delivery "
        "under its General Purpose Criterion.",
    ),
    Milestone(
        year=1973,
        title="Endangered Species Act",
        role="protected",
        description="The ESA extends federal species protection to arthropods "
        "and other invertebrates for the first time.",
    ),
    Milestone(
        year=1976,
        title="First insect ESA listings",
        role="protected",
        description="The Schaus swallowtail is among the first insects listed "
        "under the Endangered Species Act, alongside the Bahama swallowtail.",
    ),
    Milestone(
        year=1980,
        title="Diamond v. Chakrabarty",
        role="invention",
        description="The Supreme Court holds that human-made living organisms "
        "are patentable, opening the door to engineered insects.",
    ),
    Milestone(
        year=1997,
        title="Home Builders v. Babbitt",
        role="protected",
        description="The D.C. Circuit upholds federal power to protect a purely "
        "intrastate fly under the Commerce Clause.",
    ),
    Milestone(
        year=2017,
        title="Rusty patched bumble bee listed",
        role="protected",
        description="The first continental-US bee gains ESA protection.",
    ),
    Milestone(
        year=2018,
        title="Kirstin Lobato exoneration",
        role="witness",
        description="The first exoneration based on the *absence* of blowfly "
        "colonization, proving death after dark.",
    ),
    Milestone(
        year=2020,
        title="Oxitec mosquito release",
        role="invention",
        description="EPA permits the experimental release of genetically "
        "engineered Aedes aegypti in the Florida Keys.",
    ),
    Milestone(
        year=2022,
        title="'Bees are fish' and the Sentience Act",
        role="protected",
        description="Almond Alliance holds bumblebees are 'fish' under CESA the "
        "same year the UK Sentience Act covers decapods and cephalopods.",
    ),
    Milestone(
        year=2024,
        title="Murder hornet eradicated",
        role="threat",
        description="The northern giant hornet is declared eradicated from the "
        "US — the first Vespa eradication in North America.",
    ),
    Milestone(
        year=2026,
        title="Monarch proposal and screwworm detection",
        role="protected",
        description="FWS still treats the monarch listing as proposed while a "
        "New World screwworm detection in Texas reactivates sterile-insect "
        "eradication.",
    ),
)


def all_milestones() -> tuple[Milestone, ...]:
    """Return every milestone in chronological order."""
    return MILESTONES


def by_role(role_slug: str) -> tuple[Milestone, ...]:
    """Return milestones for ``role_slug``."""
    return tuple(m for m in MILESTONES if m.role == role_slug)


def span() -> tuple[int, int]:
    """Return the ``(earliest, latest)`` milestone years."""
    years = [m.year for m in MILESTONES]
    return min(years), max(years)


def span_years() -> int:
    """Return the number of years the timeline covers."""
    earliest, latest = span()
    return latest - earliest


def counts_by_role() -> dict[str, int]:
    """Return a count of milestones per declared role (zero-filled)."""
    counts = {slug: 0 for slug in roles.role_slugs()}
    for milestone in MILESTONES:
        counts[milestone.role] += 1
    return counts
