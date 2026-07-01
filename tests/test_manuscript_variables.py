"""Token / citation / cross-reference closure between manuscript and code."""

from __future__ import annotations

import json
from pathlib import Path

from src import manuscript_variables as mv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "manuscript"


def test_all_manuscript_tokens_are_generated():
    generated = set(mv.generate_variables(PROJECT_ROOT))
    used = mv.manuscript_token_inventory(MANUSCRIPT)
    missing = sorted(used - generated)
    assert not missing, f"manuscript references undefined tokens: {missing}"


def test_all_manuscript_citations_are_in_bibliography():
    bib = mv.bibtex_key_inventory(MANUSCRIPT / "references.bib")
    cited = mv.manuscript_citation_inventory(MANUSCRIPT)
    missing = sorted(cited - bib)
    assert not missing, f"manuscript cites keys absent from references.bib: {missing}"


def test_all_crossrefs_resolve_to_declared_anchors():
    anchors = mv.manuscript_anchor_inventory(MANUSCRIPT)
    refs = mv.manuscript_crossref_inventory(MANUSCRIPT)
    missing = sorted(refs - anchors)
    assert not missing, f"unresolved cross-references: {missing}"


def test_role_anchors_match_role_registry():
    from src import roles

    anchors = mv.manuscript_anchor_inventory(MANUSCRIPT)
    for role in roles.all_roles():
        assert role.anchor in anchors, role.anchor


def test_variables_are_strings_and_nonempty():
    variables = mv.generate_variables(PROJECT_ROOT)
    assert variables["ROLE_COUNT"] == "8"
    for key, value in variables.items():
        assert isinstance(key, str) and isinstance(value, str)


def test_save_variables_roundtrip(tmp_path):
    variables = mv.generate_variables(PROJECT_ROOT)
    out = mv.save_variables(variables, tmp_path / "vars.json")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["STATUTE_COUNT"] == variables["STATUTE_COUNT"]


def test_config_hash_changes_with_config(tmp_path):
    assert mv._config_hash(tmp_path) == "N/A"
    (tmp_path / "manuscript").mkdir()
    (tmp_path / "manuscript" / "config.yaml").write_text("a: 1\n", encoding="utf-8")
    assert mv._config_hash(tmp_path) != "N/A"


def test_core_acronyms_are_defined_in_manuscript():
    text = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(MANUSCRIPT.glob("*.md"))
    )
    required_definitions = (
        "American Board of Forensic Entomology (ABFE)",
        "European Association for Forensic Entomology (EAFE)",
        "North American Forensic Entomology Association (NAFEA)",
        "National Institute of Standards and Technology (NIST)",
        "Organization of Scientific Area Committees (OSAC)",
        "Animal and Plant Health Inspection Service (APHIS)",
        "International Standards for Phytosanitary Measures (ISPMs)",
        "World Trade Organization (WTO)",
        "Agreement on the Application of Sanitary and Phytosanitary Measures (SPS Agreement)",
        "Convention on International Trade in Endangered Species of Wild Fauna and Flora (CITES)",
        "Endangered Species Act (ESA)",
        "U.S. Fish and Wildlife Service (FWS)",
        "Environmental Protection Agency (EPA)",
        "Food and Drug Administration (FDA)",
        "European Food Safety Authority (EFSA)",
        "Generally Recognized as Safe (GRAS)",
        "bovine spongiform encephalopathy (BSE)",
        "London School of Economics (LSE)",
        "Treaty on the Functioning of the European Union (TFEU)",
        "international humanitarian law (IHL)",
        "Biological Weapons Convention (BWC)",
        "Defense Advanced Research Projects Agency (DARPA)",
    )
    missing = [definition for definition in required_definitions if definition not in text]
    assert not missing, missing


def test_pdf_preamble_uses_narrower_side_margins():
    preamble = (MANUSCRIPT / "preamble.md").read_text(encoding="utf-8")
    assert "\\geometry{left=0.55in,right=0.55in,top=0.65in,bottom=0.65in}" in preamble
