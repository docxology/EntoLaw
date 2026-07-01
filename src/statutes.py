from __future__ import annotations

from . import roles
from .statute_records import CATEGORIES, JURISDICTIONS, STATUTES, Statute


def all_statutes() -> tuple[Statute, ...]:
    return STATUTES


def categories() -> tuple[str, ...]:
    return CATEGORIES


def jurisdictions() -> tuple[str, ...]:
    return JURISDICTIONS


def by_category(category: str) -> tuple[Statute, ...]:
    return tuple(s for s in STATUTES if s.category == category)


def by_role(role_slug: str) -> tuple[Statute, ...]:
    return tuple(s for s in STATUTES if s.role == role_slug)


def by_jurisdiction(jurisdiction: str) -> tuple[Statute, ...]:
    return tuple(s for s in STATUTES if s.jurisdiction == jurisdiction)


def find(slug: str) -> Statute:
    for statute in STATUTES:
        if statute.slug == slug:
            return statute
    raise KeyError(f"unknown statute slug: {slug}")


def statute_table_markdown() -> str:
    header = "| Instrument | Citation | Category | Role |"
    sep = "|---|---|---|---|"
    rows = [header, sep]
    for statute in STATUTES:
        role = roles.find(statute.role).title
        rows.append(
            f"| {statute.short_title} | {statute.citation} | "
            f"{statute.category} | {role} |"
        )
    return "\n".join(rows)
