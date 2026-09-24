#!/usr/bin/env python3
"""Check that release metadata agrees across every file that declares it.

EntoLaw's version, title, license, keywords, author identity, and DOI are
each declared more than once -- ``pyproject.toml``, ``CITATION.cff``,
``codemeta.json``, ``.zenodo.json``, and ``docs/manuscript/config.yaml`` --
because each target platform (PyPI-style packaging, the citation-file
convention, CodeMeta harvesters, Zenodo, the rendered manuscript's own title
page) reads a different one. A metadata field that drifts between them is
invisible until a release: the DOI badge says one version, the citation
prompt another, the rendered cover a third. This gate compares them.

Nothing here hardcodes an expected value. ``CITATION.cff`` is read once as
the declared source of truth for each field; every other file that also
declares that field is checked against whatever ``CITATION.cff`` says, not
against a literal typed into this script. A deliberate version bump or a new
co-author changes ``CITATION.cff`` and every other file to match; it changes
nothing here.

A file that omits a field is not a violation: ``pyproject.toml`` carries no
license or keywords section in this project's schema, so those fields are
compared only across the files that declare them. Disagreement between two
files that both declare a field is.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: The one declared source of truth every other file's fields are checked
#: against. Not a value -- a filename. The DOI, version, etc. read from it are
#: whatever this checkout currently declares.
DECLARED_SOURCE = "CITATION.cff"


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _normalize_license(value: str) -> str:
    """Reduce a license field to its bare identifier.

    ``codemeta.json`` writes a full SPDX URL
    (``https://spdx.org/licenses/CC-BY-4.0``); ``CITATION.cff`` and
    ``.zenodo.json`` write the bare identifier. Both forms reduce to the
    identifier so the comparison is about the license, not the spelling.
    """
    return value.rstrip("/").rsplit("/", 1)[-1]


def _normalize_orcid(value: str) -> str:
    """Reduce an ORCID field (bare id or ``https://orcid.org/<id>``) to the bare id."""
    return value.rstrip("/").rsplit("/", 1)[-1]


def _author_from_cff(entry: dict[str, Any]) -> tuple[str, str]:
    given = str(entry.get("given-names", ""))
    family = str(entry.get("family-names", ""))
    return f"{given} {family}".strip(), str(entry.get("orcid") or "")


def _author_from_codemeta(entry: dict[str, Any]) -> tuple[str, str]:
    given = str(entry.get("givenName", ""))
    family = str(entry.get("familyName", ""))
    return f"{given} {family}".strip(), str(entry.get("@id") or "")


def _author_from_zenodo(entry: dict[str, Any]) -> tuple[str, str]:
    name = str(entry.get("name", ""))
    if "," in name:
        family, given = (part.strip() for part in name.split(",", 1))
        full = f"{given} {family}".strip()
    else:
        full = name.strip()
    return full, str(entry.get("orcid") or "")


def _author_from_pyproject(entry: dict[str, Any]) -> tuple[str, str]:
    # pyproject.toml's [project.authors] schema carries no ORCID field.
    return str(entry.get("name", "")).strip(), ""


def _author_from_manuscript_config(entry: dict[str, Any]) -> tuple[str, str]:
    # docs/manuscript/config.yaml already carries a full display name.
    return str(entry.get("name", "")).strip(), str(entry.get("orcid") or "")


def _doi_from_zenodo(data: dict[str, Any]) -> str | None:
    for related in data.get("related_identifiers", []) or []:
        if related.get("scheme") == "doi":
            identifier = related.get("identifier")
            return str(identifier) if identifier is not None else None
    return None


def collect_metadata(project_root: Path) -> dict[str, dict[str, Any]]:
    """Load every metadata file this project ships, keyed by its own filename.

    A file this project does not ship is simply absent from the returned
    mapping rather than an error -- every comparison below only compares
    fields both files in a pair actually declare.
    """
    files: dict[str, dict[str, Any]] = {}
    loaders: tuple[tuple[str, Any], ...] = (
        ("pyproject.toml", _load_toml),
        ("CITATION.cff", _load_yaml),
        ("codemeta.json", _load_json),
        (".zenodo.json", _load_json),
        ("docs/manuscript/config.yaml", _load_yaml),
    )
    for name, loader in loaders:
        path = project_root / name
        if path.is_file():
            files[name] = loader(path)
    return files


def check_metadata_consistency(project_root: Path) -> list[str]:
    """Compare version, title, license, keywords, authors, and DOI across every declared metadata file.

    Args:
        project_root: Project root directory holding the metadata files.

    Returns:
        One message per disagreement, ordered by field then file; empty when
        every file that declares a given field agrees with
        :data:`DECLARED_SOURCE` on it.

    Raises:
        FileNotFoundError: If :data:`DECLARED_SOURCE` is missing -- there is
            no source to check the rest against.
    """
    files = collect_metadata(project_root)
    cff = files.get(DECLARED_SOURCE)
    if cff is None:
        raise FileNotFoundError(f"declared metadata source not found: {project_root / DECLARED_SOURCE}")

    violations: list[str] = []

    def check_field(field: str, expected: str, actual_by_file: dict[str, str]) -> None:
        for filename in sorted(actual_by_file):
            actual = actual_by_file[filename]
            if actual != expected:
                violations.append(
                    f"{field} disagrees: {DECLARED_SOURCE} declares {expected!r}, {filename} declares {actual!r}"
                )

    pyproject = files.get("pyproject.toml", {}).get("project", {})
    codemeta = files.get("codemeta.json", {})
    zenodo = files.get(".zenodo.json", {})
    manuscript = files.get("docs/manuscript/config.yaml", {})
    manuscript_paper = manuscript.get("paper", {}) or {}
    manuscript_publication = manuscript.get("publication", {}) or {}
    manuscript_metadata = manuscript.get("metadata", {}) or {}

    # --- version: every file that ships metadata declares one -------------
    version_by_file: dict[str, str] = {}
    if "version" in pyproject:
        version_by_file["pyproject.toml"] = str(pyproject["version"])
    if "version" in codemeta:
        version_by_file["codemeta.json"] = str(codemeta["version"])
    if "version" in zenodo:
        version_by_file[".zenodo.json"] = str(zenodo["version"])
    if "version" in manuscript_paper:
        version_by_file["docs/manuscript/config.yaml"] = str(manuscript_paper["version"])
    check_field("version", str(cff.get("version", "")), version_by_file)

    # --- title: codemeta calls it `name`; pyproject's `name` is the package
    # slug, a different field, and is intentionally not compared here. ------
    check_field(
        "title",
        str(cff.get("title", "")),
        {
            **({"codemeta.json": str(codemeta["name"])} if "name" in codemeta else {}),
            **({".zenodo.json": str(zenodo["title"])} if "title" in zenodo else {}),
            **({"docs/manuscript/config.yaml": str(manuscript_paper["title"])} if "title" in manuscript_paper else {}),
        },
    )

    # --- license -------------------------------------------------------
    if cff.get("license"):
        check_field(
            "license",
            _normalize_license(str(cff["license"])),
            {
                **({"codemeta.json": _normalize_license(str(codemeta["license"]))} if codemeta.get("license") else {}),
                **({".zenodo.json": _normalize_license(str(zenodo["license"]))} if zenodo.get("license") else {}),
                **(
                    {"docs/manuscript/config.yaml": _normalize_license(str(manuscript_metadata["license"]))}
                    if manuscript_metadata.get("license")
                    else {}
                ),
            },
        )

    # --- keywords (order-insensitive) --------------------------------------
    expected_keywords = sorted(cff.get("keywords") or [])
    for filename, keywords_list in (
        ("codemeta.json", codemeta.get("keywords")),
        (".zenodo.json", zenodo.get("keywords")),
        ("docs/manuscript/config.yaml", manuscript.get("keywords")),
    ):
        if keywords_list is None:
            continue
        actual_keywords = sorted(keywords_list)
        if actual_keywords != expected_keywords:
            violations.append(
                f"keywords disagree: {DECLARED_SOURCE} declares {expected_keywords}, "
                f"{filename} declares {actual_keywords}"
            )

    # --- DOI: docs/manuscript/config.yaml's publication.doi is the concept
    # DOI, the same field CITATION.cff.doi declares (not version_doi). -------
    doi_by_file: dict[str, str] = {}
    if "identifier" in codemeta:
        doi_by_file["codemeta.json"] = str(codemeta["identifier"])
    zenodo_doi = _doi_from_zenodo(zenodo)
    if zenodo_doi is not None:
        doi_by_file[".zenodo.json"] = zenodo_doi
    if "doi" in manuscript_publication:
        doi_by_file["docs/manuscript/config.yaml"] = str(manuscript_publication["doi"])
    check_field("doi", str(cff.get("doi", "")), doi_by_file)

    # --- authors: full name, then ORCID where the file carries one --------
    expected_authors = [_author_from_cff(a) for a in (cff.get("authors") or [])]
    expected_names = [name for name, _orcid in expected_authors]
    expected_orcids = {_normalize_orcid(orcid) for _name, orcid in expected_authors if orcid}

    author_sources: dict[str, list[tuple[str, str]]] = {}
    if "pyproject.toml" in files:
        author_sources["pyproject.toml"] = [_author_from_pyproject(a) for a in pyproject.get("authors", [])]
    if "codemeta.json" in files:
        raw_author = codemeta.get("author", [])
        raw_authors = [raw_author] if isinstance(raw_author, dict) else raw_author
        author_sources["codemeta.json"] = [_author_from_codemeta(a) for a in raw_authors]
    if ".zenodo.json" in files:
        author_sources[".zenodo.json"] = [_author_from_zenodo(a) for a in zenodo.get("creators", [])]
    if "docs/manuscript/config.yaml" in files:
        author_sources["docs/manuscript/config.yaml"] = [
            _author_from_manuscript_config(a) for a in manuscript.get("authors", [])
        ]

    for filename in sorted(author_sources):
        actual = author_sources[filename]
        actual_names = [name for name, _orcid in actual]
        if actual_names != expected_names:
            violations.append(
                f"authors disagree: {DECLARED_SOURCE} declares {expected_names}, {filename} declares {actual_names}"
            )
        actual_orcids = {_normalize_orcid(orcid) for _name, orcid in actual if orcid}
        if actual_orcids and actual_orcids != expected_orcids:
            violations.append(
                f"author ORCIDs disagree: {DECLARED_SOURCE} declares {sorted(expected_orcids)}, "
                f"{filename} declares {sorted(actual_orcids)}"
            )

    return violations


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the metadata-consistency check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="project root directory")
    return parser


def main() -> int:
    """Report metadata disagreements; return non-zero while any remain."""
    args = build_parser().parse_args()
    root = args.project_root.resolve()

    try:
        violations = check_metadata_consistency(root)
    except FileNotFoundError as error:
        print(f"metadata consistency error: {error}", file=sys.stderr)
        return 2

    for message in violations:
        print(f"metadata consistency: {message}", file=sys.stderr)
    print(f"metadata consistency: {len(violations)} violations")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
