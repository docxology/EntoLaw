"""Manuscript variable generation for the EntoLaw project.

Generates a flat ``dict[str, str]`` of ``UPPERCASE_KEY → value`` for
``{{TOKEN}}`` substitution in manuscript markdown. Every prose number in the
manuscript that references the field (counts of roles, cases, statutes,
species, institutions, milestones, interconnections) is generated here so the
manuscript and the registries cannot drift. The closure test
``tests/test_manuscript_variables.py::test_all_manuscript_tokens_are_generated``
fails CI if any prose token is unbacked.
"""

from __future__ import annotations

import hashlib
import json
import platform
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import (
    cases,
    figure_captions,
    institutions,
    interconnections,
    metrics,
    package_map,
    roles,
    species,
    statutes,
)


def generate_variables(project_root: Path) -> dict[str, str]:
    """Generate the full manuscript variable set."""
    from . import claim_ledger

    m = metrics.compute()
    variables: dict[str, str] = {}

    # ── Headline registry counts (single source of truth) ──────────────────
    variables["ROLE_COUNT"] = str(m.role_count)
    variables["CASE_COUNT"] = str(m.case_count)
    variables["ROLES_WITH_CASE_LAW"] = str(m.roles_with_case_law)
    variables["STATUTE_COUNT"] = str(m.statute_count)
    variables["CATEGORY_COUNT"] = str(m.category_count)
    variables["SPECIES_COUNT"] = str(m.species_count)
    variables["INSTITUTION_COUNT"] = str(m.institution_count)
    variables["MILESTONE_COUNT"] = str(m.milestone_count)
    variables["TIMELINE_SPAN_YEARS"] = str(m.timeline_span_years)
    variables["INTERCONNECTION_COUNT"] = str(m.interconnection_count)
    variables["REGISTRY_COUNT"] = str(len(package_map.REGISTRIES))
    variables["CLAIM_LEDGER_COUNT"] = str(claim_ledger.claim_count(project_root))
    variables["JURISDICTION_COUNT"] = str(
        sum(1 for v in m.statutes_by_jurisdiction.values() if v > 0)
    )
    variables["FIGURE_COUNT"] = str(package_map.figure_count())

    # ── Per-role evidence counts (e.g. WITNESS_CASE_COUNT) ─────────────────
    coverage = metrics.role_coverage_matrix()
    for role in roles.all_roles():
        prefix = role.slug.upper()
        cov = coverage[role.slug]
        variables[f"{prefix}_CASE_COUNT"] = str(cov["cases"])
        variables[f"{prefix}_STATUTE_COUNT"] = str(cov["statutes"])
        variables[f"{prefix}_SPECIES_COUNT"] = str(cov["species"])
        variables[f"{prefix}_MILESTONE_COUNT"] = str(cov["milestones"])

    # ── Key citation anchors (string-typed; never re-typed in prose) ───────
    variables["DAUBERT_CITATION"] = cases.find("daubert").citation
    variables["FRYE_CITATION"] = cases.find("frye").citation
    variables["ALMOND_CITATION"] = cases.find("almond_alliance").citation
    variables["HOMEBUILDERS_CITATION"] = cases.find("home_builders_babbitt").citation
    variables["CHAKRABARTY_CITATION"] = cases.find("chakrabarty").citation
    variables["KEARRY_CITATION"] = cases.find("kearry_pattinson").citation
    variables["GOFF_CITATION"] = cases.find("goff_kilts").citation
    variables["ESA_CITATION"] = statutes.find("esa").citation
    variables["PPA_CITATION"] = statutes.find("plant_protection_act").citation
    variables["LACEY_CITATION"] = statutes.find("lacey_act_injurious").citation
    variables["NOVEL_FOOD_CITATION"] = statutes.find("eu_novel_food").citation
    variables["SENTIENCE_ACT_CITATION"] = statutes.find("uk_sentience_act").citation
    variables["BWC_CITATION"] = statutes.find("bwc").citation
    variables["CESA_FISH_CITATION"] = statutes.find("cesa_fish_definition").citation

    # ── Tables (markdown blocks for {{TOKEN}} substitution) ────────────────
    variables["ROLE_TABLE"] = roles.role_table_markdown()
    variables["CASE_TABLE"] = cases.case_table_markdown()
    variables["STATUTE_TABLE"] = statutes.statute_table_markdown()
    variables["SPECIES_TABLE"] = species.species_table_markdown()
    variables["INTERCONNECTION_TABLE"] = (
        interconnections.interconnection_table_markdown()
    )

    # ── Institution counts by role (used in prose) ─────────────────────────
    variables["FORENSIC_INSTITUTION_COUNT"] = str(len(institutions.by_role("witness")))

    # ── Figure captions (resolve {TOKEN} against the above) ────────────────
    variables.update(figure_captions.caption_tokens(variables))

    # ── Provenance ─────────────────────────────────────────────────────────
    variables["CONFIG_HASH"] = _config_hash(project_root)
    variables["GENERATION_TIMESTAMP"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    variables["PYTHON_VERSION"] = platform.python_version()
    variables["PLATFORM"] = f"{platform.system()} {platform.machine()}"

    # ── Publication metadata (for colophon / back-matter tokens) ───────────
    pub = _load_publication_config(project_root)
    variables["PUBLICATION_DOI"] = pub.get("doi") or "not yet minted"
    variables["PUBLICATION_REPO"] = pub.get("github_repository", "")
    variables["PUBLICATION_VERSION"] = pub.get("version", "")
    variables["PUBLICATION_LICENSE"] = pub.get("license", "")

    return variables


def save_variables(variables: dict[str, str], output_path: Path) -> Path:
    """Persist ``variables`` as sorted JSON at ``output_path``."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(variables, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_path


def _config_hash(project_root: Path) -> str:
    """Return the short sha256 of ``manuscript/config.yaml`` or ``"N/A"``."""
    config = project_root / "manuscript" / "config.yaml"
    if not config.exists():
        return "N/A"
    return hashlib.sha256(config.read_bytes()).hexdigest()[:16]


def _load_publication_config(project_root: Path) -> dict[str, str]:
    """Flatten the ``publication``/``paper``/``metadata`` blocks of
    ``manuscript/config.yaml`` into the fields the colophon needs."""
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.exists():
        return {}
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    publication = raw.get("publication") or {}
    paper = raw.get("paper") or {}
    metadata = raw.get("metadata") or {}
    return {
        "doi": publication.get("doi", ""),
        "github_repository": publication.get("github_repository", ""),
        "version": paper.get("version", ""),
        "license": metadata.get("license", ""),
    }


# ── Manuscript inventories (token / anchor / citation closure) ─────────────

_SKIP_FILES = {"AGENTS.md", "README.md", "SYNTAX.md"}
_PANDOC_CROSSREF_PREFIXES: frozenset[str] = frozenset(
    {"sec", "fig", "tbl", "eq", "lst", "thm", "lem", "def", "exm"}
)
_CODE_SPAN_PATTERN = re.compile(r"`[^`]*`")


def manuscript_token_inventory(manuscript_dir: Path) -> set[str]:
    """Return every ``{{TOKEN}}`` reference found in the manuscript markdown."""
    tokens: set[str] = set()
    pattern = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
    for path in sorted(manuscript_dir.glob("*.md")):
        if path.name in _SKIP_FILES:
            continue
        for match in pattern.finditer(path.read_text(encoding="utf-8")):
            tokens.add(match.group(1))
    return tokens


def manuscript_anchor_inventory(manuscript_dir: Path) -> set[str]:
    """Return local Pandoc anchors (``{#sec:...}``, ``{#fig:...}``) declared."""
    anchors: set[str] = set()
    prefixes = "|".join(sorted(_PANDOC_CROSSREF_PREFIXES))
    anchor_pattern = re.compile(
        rf"\{{#((?:{prefixes}):[A-Za-z0-9_:-]+)(?:\s+[^}}]*)?\}}"
    )
    for path in sorted(manuscript_dir.glob("*.md")):
        if path.name in _SKIP_FILES:
            continue
        text = _CODE_SPAN_PATTERN.sub("", path.read_text(encoding="utf-8"))
        anchors.update(anchor_pattern.findall(text))
    return anchors


def manuscript_crossref_inventory(manuscript_dir: Path) -> set[str]:
    """Return local Pandoc cross-reference keys (``@sec:...``, ``@fig:...``)."""
    refs: set[str] = set()
    prefixes = "|".join(sorted(_PANDOC_CROSSREF_PREFIXES))
    key_pattern = re.compile(rf"(?<![A-Za-z0-9_])@((?:{prefixes}):[A-Za-z0-9_:-]+)")
    for path in sorted(manuscript_dir.glob("*.md")):
        if path.name in _SKIP_FILES:
            continue
        text = _CODE_SPAN_PATTERN.sub("", path.read_text(encoding="utf-8"))
        refs.update(key_pattern.findall(text))
    return refs


def manuscript_citation_inventory(manuscript_dir: Path) -> set[str]:
    """Return every BibTeX ``[@key]`` reference in the manuscript markdown."""
    keys: set[str] = set()
    citation_pattern = re.compile(r"\[@[^\]]+\]")
    key_pattern = re.compile(r"@([A-Za-z][A-Za-z0-9_:-]*)")
    for path in sorted(manuscript_dir.glob("*.md")):
        if path.name in _SKIP_FILES:
            continue
        text = _CODE_SPAN_PATTERN.sub("", path.read_text(encoding="utf-8"))
        for bracket in citation_pattern.finditer(text):
            for cite in key_pattern.findall(bracket.group(0)):
                prefix = cite.split(":", 1)[0] if ":" in cite else ""
                if prefix in _PANDOC_CROSSREF_PREFIXES:
                    continue
                keys.add(cite)
    return keys


def bibtex_key_inventory(bib_path: Path) -> set[str]:
    """Return every ``@type{key,...`` BibTeX entry key in ``bib_path``."""
    if not bib_path.exists():
        return set()
    pattern = re.compile(r"@\w+\{\s*([A-Za-z][A-Za-z0-9_:-]*)\s*,")
    return set(pattern.findall(bib_path.read_text(encoding="utf-8")))
