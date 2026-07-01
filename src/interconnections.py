"""Cross-domain interconnections — the recurring machinery linking the roles.

The registered roles are not silos. The same legal devices recur across them: the
definitional fight over what category a bug belongs to, the expert testimony
that binds forensic and regulatory proof, biotechnology as the pivot among
product/conservation/weapon/welfare, the property/conservation mirror, and
the rhyme between the ancient animal trials and cutting-edge rights debates.

Each interconnection links two or more :mod:`src.roles` slugs under a named
theme. The registry powers the role-interconnection network figure and the
manuscript's synthesis section; :mod:`src.validation` fails closed on any
link that names a role not declared in :mod:`src.roles`.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import roles


@dataclass(frozen=True)
class Interconnection:
    """A theme that links two or more legal roles.

    Attributes:
        slug: Stable identifier.
        theme: Short theme name.
        roles: The role slugs this theme connects (two or more).
        description: One- or two-sentence explanation of the linkage.
    """

    slug: str
    theme: str
    roles: tuple[str, ...]
    description: str


INTERCONNECTIONS: tuple[Interconnection, ...] = (
    Interconnection(
        slug="definitional_problem",
        theme="The definitional problem",
        roles=(
            "witness",
            "threat",
            "protected",
            "property",
            "invention",
            "defendant",
            "moral_patient",
            "weapon",
        ),
        description="Entomological law is, at root, a series of fights over what "
        "category a bug belongs to: is a bumblebee a 'fish', a screwworm a "
        "'plant pest', a fly 'wildlife', an insect 'made by man', a cricket "
        "'sentient'?",
    ),
    Interconnection(
        slug="expert_testimony_bridge",
        theme="Expert testimony binds forensic and regulatory law",
        roles=("witness", "threat"),
        description="Proving invasive-pest causation requires the same "
        "entomological expertise as proving time of death — a tree-infestation "
        "suit failed for lack of an insect expert.",
    ),
    Interconnection(
        slug="biotech_pivot",
        theme="Biotechnology is the pivot point",
        roles=("invention", "protected", "weapon", "moral_patient"),
        description="GM and gene-drive insects are simultaneously regulated "
        "products, conservation tools or threats, potential weapons, and moral "
        "patients in farmed-welfare debates.",
    ),
    Interconnection(
        slug="property_conservation_mirror",
        theme="Property and conservation are mirror images",
        roles=("property", "protected"),
        description="Roman and common-law bee possession rules sit opposite "
        "modern bumblebee protection under the same ferae naturae doctrine.",
    ),
    Interconnection(
        slug="ancient_modern_rhyme",
        theme="The ancient and the cutting-edge rhyme",
        roles=("defendant", "protected", "moral_patient"),
        description="Roman bee pursuit, Irish bee trespass, and the 1587 "
        "weevil preserve foreshadow modern fights over habitat, rights, and "
        "legally actionable insect status.",
    ),
)


def all_interconnections() -> tuple[Interconnection, ...]:
    """Return every interconnection, in canonical order."""
    return INTERCONNECTIONS


def find(slug: str) -> Interconnection:
    """Return the interconnection with ``slug`` or raise ``KeyError``."""
    for link in INTERCONNECTIONS:
        if link.slug == slug:
            return link
    raise KeyError(f"unknown interconnection slug: {slug}")


def role_link_degree() -> dict[str, int]:
    """Return how many interconnection themes touch each role."""
    degree = {slug: 0 for slug in roles.role_slugs()}
    for link in INTERCONNECTIONS:
        for role_slug in link.roles:
            degree[role_slug] += 1
    return degree


def interconnection_table_markdown() -> str:
    """Render the interconnection registry as a markdown table."""
    header = "| Theme | Roles linked | Description |"
    sep = "|---|---|---|"
    rows: list[str] = [header, sep]
    for link in INTERCONNECTIONS:
        titles = ", ".join(roles.find(r).title for r in link.roles)
        rows.append(f"| {link.theme} | {titles} | {link.description} |")
    return "\n".join(rows)
