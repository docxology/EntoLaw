"""Bibliography hygiene and claim-ledger source binding."""

from __future__ import annotations

import re
from pathlib import Path

from src import claim_ledger as cl
from src import manuscript_variables as mv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "manuscript"


def test_no_duplicate_bibtex_keys():
    text = (MANUSCRIPT / "references.bib").read_text(encoding="utf-8")
    keys = re.findall(r"@\w+\{\s*([A-Za-z][A-Za-z0-9_:-]*)\s*,", text)
    duplicates = sorted({k for k in keys if keys.count(k) > 1})
    assert not duplicates, f"duplicate bib keys: {duplicates}"


def test_claim_ledger_sources_are_in_bibliography():
    bib = mv.bibtex_key_inventory(MANUSCRIPT / "references.bib")
    claims = cl.load_claims(PROJECT_ROOT / "data" / "claim_ledger.yaml")
    for claim in claims:
        assert claim.source in bib, claim.source


def _bib_entry_types_and_bodies() -> dict[str, tuple[str, str]]:
    text = (MANUSCRIPT / "references.bib").read_text(encoding="utf-8")
    entries: dict[str, tuple[str, str]] = {}
    for match in re.finditer(r"@(\w+)\{\s*([^,]+),([\s\S]*?)(?=\n@\w+\{|\Z)", text):
        entries[match.group(2)] = (match.group(1).lower(), match.group(3))
    return entries


def test_cited_statutes_have_institutional_authors():
    entries = _bib_entry_types_and_bodies()
    cited = mv.manuscript_citation_inventory(MANUSCRIPT)
    offenders = [
        key
        for key in sorted(cited)
        if entries.get(key, ("", ""))[0] == "statute"
        and "author = {{" not in entries[key][1]
    ]
    assert not offenders, offenders


def test_every_cited_key_exists_and_is_used():
    bib = mv.bibtex_key_inventory(MANUSCRIPT / "references.bib")
    cited = mv.manuscript_citation_inventory(MANUSCRIPT)
    # all cited keys are defined
    assert cited <= bib
    # the manuscript actually cites a substantial fraction of the bib
    assert len(cited) >= 30


def test_added_connective_scholarship_is_cited():
    bib = mv.bibtex_key_inventory(MANUSCRIPT / "references.bib")
    cited = mv.manuscript_citation_inventory(MANUSCRIPT)
    expected = {
        "jasanoff2015serviceable",
        "tomberlin2011roadmap",
        "kotze2021case_report",
        "cardoso2020scientists_warning",
        "nagle1998delhi",
        "oye2014gene_drives",
        "fao2013edible_insects",
        "barrett2023farmed_insect_welfare",
        "stone1972trees",
        "favre2010living_property",
        "amendt2007bestpractice",
        "lugo2006insect_conservation_esa",
        "mikhalevich2020minds",
        "lahteenmaki2021insectfoodfeed",
        "lodge2016bioeconomics_invasive_species",
        "bowker1999sorting",
        "gieryn1983boundary_work",
        "losey2006economic_value_insects",
        "rose1985possession_property",
        "jasanoff2004states_of_knowledge",
        "desouzavalente2025invertebrate_sentience",
        "james2023gene_drive_policy",
        "osac2025entomological_evidence",
        "reddy2024insect_agriculture",
        "reddy2025insect_law",
        "shirey2025invertebrate_esa",
    }
    assert expected <= bib
    assert expected <= cited
