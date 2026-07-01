from __future__ import annotations

from . import roles
from .taxon_records import TAXA, Taxon


def all_taxa() -> tuple[Taxon, ...]:
    return TAXA


def by_role(role_slug: str) -> tuple[Taxon, ...]:
    return tuple(t for t in TAXA if t.role == role_slug)


def find(slug: str) -> Taxon:
    for taxon in TAXA:
        if taxon.slug == slug:
            return taxon
    raise KeyError(f"unknown taxon slug: {slug}")


def counts_by_role() -> dict[str, int]:
    counts = {slug: 0 for slug in roles.role_slugs()}
    for taxon in TAXA:
        counts[taxon.role] += 1
    return counts


def species_table_markdown() -> str:
    header = "| Taxon | Common name | Role | Legal status |"
    sep = "|---|---|---|---|"
    rows = [header, sep]
    for taxon in TAXA:
        role = roles.find(taxon.role).title
        rows.append(
            f"| *{taxon.scientific_name}* | {taxon.common_name} | "
            f"{role} | {taxon.status} |"
        )
    return "\n".join(rows)
