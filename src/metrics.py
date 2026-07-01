"""Aggregate metrics over the entomological-law registries.

These functions exist so the manuscript prose can refer to field totals
(number of roles, cases, statutes by category, species, institutions,
milestones, interconnections) without hard-coding values. The single source
of truth for every count is the corresponding registry module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from . import cases, institutions, interconnections, roles, species, statutes, timeline


@dataclass(frozen=True)
class FieldMetrics:
    """Headline counts across the registries.

    Attributes:
        role_count: Number of declared legal roles.
        case_count: Total registered cases.
        cases_by_role: Map role slug → case count.
        cases_by_jurisdiction: Map jurisdiction → case count.
        statute_count: Total registered statutes/treaties.
        statutes_by_category: Map category → count.
        statutes_by_jurisdiction: Map jurisdiction → count.
        category_count: Number of non-empty statute categories.
        species_count: Total registered taxa.
        species_by_role: Map role slug → taxa count.
        institution_count: Total registered institutions.
        milestone_count: Total timeline milestones.
        timeline_span_years: Years spanned by the timeline.
        interconnection_count: Total cross-domain interconnection themes.
        roles_with_case_law: Number of roles with at least one registered case.
    """

    role_count: int
    case_count: int
    cases_by_role: Mapping[str, int]
    cases_by_jurisdiction: Mapping[str, int]
    statute_count: int
    statutes_by_category: Mapping[str, int]
    statutes_by_jurisdiction: Mapping[str, int]
    category_count: int
    species_count: int
    species_by_role: Mapping[str, int]
    institution_count: int
    milestone_count: int
    timeline_span_years: int
    interconnection_count: int
    roles_with_case_law: int


def compute() -> FieldMetrics:
    """Return :class:`FieldMetrics` computed from the live registries."""
    case_roles = cases.counts_by_role()

    stat_by_cat: dict[str, int] = {c: 0 for c in statutes.categories()}
    for s in statutes.all_statutes():
        stat_by_cat[s.category] += 1

    stat_by_jur: dict[str, int] = {j: 0 for j in statutes.jurisdictions()}
    for s in statutes.all_statutes():
        stat_by_jur[s.jurisdiction] += 1

    case_by_jur: dict[str, int] = {j: 0 for j in cases.JURISDICTIONS}
    for c in cases.all_cases():
        case_by_jur[c.jurisdiction] += 1

    return FieldMetrics(
        role_count=len(roles.all_roles()),
        case_count=len(cases.all_cases()),
        cases_by_role=case_roles,
        cases_by_jurisdiction=case_by_jur,
        statute_count=len(statutes.all_statutes()),
        statutes_by_category=stat_by_cat,
        statutes_by_jurisdiction=stat_by_jur,
        category_count=sum(1 for v in stat_by_cat.values() if v > 0),
        species_count=len(species.all_taxa()),
        species_by_role=species.counts_by_role(),
        institution_count=len(institutions.all_institutions()),
        milestone_count=len(timeline.all_milestones()),
        timeline_span_years=timeline.span_years(),
        interconnection_count=len(interconnections.all_interconnections()),
        roles_with_case_law=sum(1 for v in case_roles.values() if v > 0),
    )


def role_coverage_matrix() -> dict[str, dict[str, int]]:
    """Return per-role evidence counts (cases, statutes, species, milestones).

    The matrix is the data behind the role-coverage figure: for each legal
    role, how many cases, statutes, species, and historical milestones the
    registries encode.
    """
    case_counts = cases.counts_by_role()
    species_counts = species.counts_by_role()
    milestone_counts = timeline.counts_by_role()
    statute_counts = {slug: 0 for slug in roles.role_slugs()}
    for s in statutes.all_statutes():
        statute_counts[s.role] += 1
    return {
        role.slug: {
            "cases": case_counts[role.slug],
            "statutes": statute_counts[role.slug],
            "species": species_counts[role.slug],
            "milestones": milestone_counts[role.slug],
        }
        for role in roles.all_roles()
    }
