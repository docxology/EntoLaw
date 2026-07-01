"""Registry-content tests for roles, cases, statutes, species, institutions,
timeline, and interconnections — real data, structural invariants."""

from __future__ import annotations

import pytest

from src import (
    cases,
    citations,
    institutions,
    interconnections,
    roles,
    species,
    statutes,
    timeline,
)


# ── roles ────────────────────────────────────────────────────────────────


def test_roles_registry_has_eight_current_entries():
    slugs = roles.role_slugs()
    assert len(slugs) == 8
    assert len(set(slugs)) == 8
    assert "witness" in slugs and "weapon" in slugs


def test_role_find_and_table():
    assert roles.find("witness").domain == "Forensic entomology"
    with pytest.raises(KeyError):
        roles.find("nonexistent")
    table = roles.role_table_markdown()
    assert "Legal role" in table and "Forensic entomology" in table


def test_every_role_anchor_is_sec_anchor():
    for role in roles.all_roles():
        assert role.anchor.startswith("sec:")


# ── cases ────────────────────────────────────────────────────────────────


def test_cases_have_unique_parseable_citations():
    seen = set()
    for c in cases.all_cases():
        assert c.slug not in seen
        seen.add(c.slug)
        assert citations.citation_is_parseable(c.citation), c.citation
        assert c.role in roles.role_slugs()
        assert c.jurisdiction in cases.JURISDICTIONS


def test_case_counts_by_role_cover_all_roles():
    counts = cases.counts_by_role()
    assert set(counts) == set(roles.role_slugs())
    assert counts["witness"] >= 1
    # history/statute-driven roles legitimately carry zero modern cases
    assert counts["defendant"] == 0


def test_cases_by_role_and_jurisdiction_and_find():
    assert cases.by_role("witness")
    assert cases.by_jurisdiction("U.S. Supreme Court")
    assert cases.find("daubert").year == 1993
    with pytest.raises(KeyError):
        cases.find("nope")
    assert "Daubert" in cases.case_table_markdown()


# ── statutes ─────────────────────────────────────────────────────────────


def test_statutes_have_recognised_citations_and_vocab():
    seen = set()
    for s in statutes.all_statutes():
        assert s.slug not in seen
        seen.add(s.slug)
        assert citations.instrument_is_recognised(s.citation), s.citation
        assert s.category in statutes.categories()
        assert s.jurisdiction in statutes.jurisdictions()
        assert s.role in roles.role_slugs()
        for cross in s.cross_references:
            assert citations.instrument_is_recognised(cross), cross


def test_statute_filters_and_find():
    assert statutes.by_category("quarantine")
    assert statutes.by_role("threat")
    assert statutes.by_jurisdiction("EU")
    assert statutes.find("esa").short_title.startswith("Endangered")
    with pytest.raises(KeyError):
        statutes.find("nope")
    assert "Endangered" in statutes.statute_table_markdown()


def test_all_nine_categories_are_used():
    used = {s.category for s in statutes.all_statutes()}
    assert used == set(statutes.categories())


# ── species ──────────────────────────────────────────────────────────────


def test_species_vocab_and_uniqueness():
    seen = set()
    for t in species.all_taxa():
        assert t.slug not in seen
        seen.add(t.slug)
        assert t.role in roles.role_slugs()
        assert t.scientific_name.strip()
        assert t.status.strip()


def test_species_helpers():
    assert species.by_role("threat")
    assert species.find("monarch").common_name == "monarch butterfly"
    with pytest.raises(KeyError):
        species.find("nope")
    counts = species.counts_by_role()
    assert set(counts) == set(roles.role_slugs())
    assert "Danaus" in species.species_table_markdown()


def test_every_role_has_at_least_one_taxon():
    counts = species.counts_by_role()
    for slug in roles.role_slugs():
        assert counts[slug] >= 1, slug


# ── institutions ─────────────────────────────────────────────────────────


def test_institutions_vocab_and_find():
    seen = set()
    for i in institutions.all_institutions():
        assert i.slug not in seen
        seen.add(i.slug)
        assert i.role in roles.role_slugs()
        assert i.function.strip()
    assert institutions.by_role("witness")
    assert institutions.find("abfe").acronym == "ABFE"
    with pytest.raises(KeyError):
        institutions.find("nope")


# ── timeline ─────────────────────────────────────────────────────────────


def test_timeline_span_and_roles():
    earliest, latest = timeline.span()
    assert earliest == -1650
    assert latest >= 2024
    assert timeline.span_years() == latest - earliest
    for m in timeline.all_milestones():
        assert m.role in roles.role_slugs()
        assert -2000 <= m.year <= 2100
    assert timeline.by_role("defendant")
    counts = timeline.counts_by_role()
    assert set(counts) == set(roles.role_slugs())


# ── interconnections ─────────────────────────────────────────────────────


def test_interconnections_link_valid_roles():
    for link in interconnections.all_interconnections():
        assert len(link.roles) >= 2
        for r in link.roles:
            assert r in roles.role_slugs()
    assert interconnections.find("biotech_pivot").theme.startswith("Biotechnology")
    with pytest.raises(KeyError):
        interconnections.find("nope")
    degree = interconnections.role_link_degree()
    # the definitional problem touches every role at least once
    assert all(v >= 1 for v in degree.values())
    assert "Theme" in interconnections.interconnection_table_markdown()
