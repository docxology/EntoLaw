from __future__ import annotations

from . import roles
from .case_records import CASES, JURISDICTIONS, Case

__all__ = [
    "CASES",
    "JURISDICTIONS",
    "Case",
    "all_cases",
    "by_jurisdiction",
    "by_role",
    "case_table_markdown",
    "counts_by_role",
    "find",
]


def all_cases() -> tuple[Case, ...]:
    return CASES


def by_role(role_slug: str) -> tuple[Case, ...]:
    return tuple(c for c in CASES if c.role == role_slug)


def by_jurisdiction(jurisdiction: str) -> tuple[Case, ...]:
    return tuple(c for c in CASES if c.jurisdiction == jurisdiction)


def find(slug: str) -> Case:
    for case in CASES:
        if case.slug == slug:
            return case
    raise KeyError(f"unknown case slug: {slug}")


def counts_by_role() -> dict[str, int]:
    counts = {slug: 0 for slug in roles.role_slugs()}
    for case in CASES:
        counts[case.role] += 1
    return counts


def case_table_markdown() -> str:
    header = "| Case | Citation | Role | Holding |"
    sep = "|---|---|---|---|"
    rows = [header, sep]
    for case in CASES:
        role = roles.find(case.role).title
        rows.append(f"| *{case.name}* | {case.citation} | {role} | {case.holding} |")
    return "\n".join(rows)
