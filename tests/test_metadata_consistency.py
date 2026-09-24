from __future__ import annotations

import json
from pathlib import Path

from scripts import check_metadata_consistency as cmc

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_live_tree_metadata_is_consistent():
    """The real checkout's version/title/license/keywords/authors/DOI agree."""
    violations = cmc.check_metadata_consistency(PROJECT_ROOT)
    assert violations == []


def _write_consistent_tree(root: Path) -> None:
    (root / "docs" / "manuscript").mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text(
        "[project]\n"
        'name = "widget"\n'
        'version = "1.0.0"\n'
        "authors = [\n"
        '    {name = "Ada Lovelace", email = "ada@example.org"},\n'
        "]\n",
        encoding="utf-8",
    )
    (root / "CITATION.cff").write_text(
        "cff-version: 1.2.0\n"
        "title: Widget\n"
        "version: 1.0.0\n"
        "doi: 10.5281/zenodo.1234567\n"
        "license: CC-BY-4.0\n"
        "keywords:\n"
        "  - widgets\n"
        "  - gears\n"
        "authors:\n"
        "  - given-names: Ada\n"
        "    family-names: Lovelace\n"
        "    orcid: 0000-0000-0000-0001\n",
        encoding="utf-8",
    )
    (root / "codemeta.json").write_text(
        json.dumps(
            {
                "name": "Widget",
                "version": "1.0.0",
                "identifier": "10.5281/zenodo.1234567",
                "license": "https://spdx.org/licenses/CC-BY-4.0",
                "keywords": ["gears", "widgets"],
                "author": [
                    {
                        "@id": "https://orcid.org/0000-0000-0000-0001",
                        "givenName": "Ada",
                        "familyName": "Lovelace",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / ".zenodo.json").write_text(
        json.dumps(
            {
                "title": "Widget",
                "version": "1.0.0",
                "license": "CC-BY-4.0",
                "keywords": ["widgets", "gears"],
                "creators": [{"name": "Lovelace, Ada", "orcid": "0000-0000-0000-0001"}],
                "related_identifiers": [
                    {"identifier": "10.5281/zenodo.1234567", "relation": "isVersionOf", "scheme": "doi"}
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "docs" / "manuscript" / "config.yaml").write_text(
        "paper:\n"
        "  title: Widget\n"
        "  version: 1.0.0\n"
        "authors:\n"
        "  - name: Ada Lovelace\n"
        "    orcid: 0000-0000-0000-0001\n"
        "publication:\n"
        "  doi: 10.5281/zenodo.1234567\n"
        "keywords:\n"
        "  - widgets\n"
        "  - gears\n"
        "metadata:\n"
        "  license: CC-BY-4.0\n",
        encoding="utf-8",
    )


def test_consistent_fixture_tree_has_no_violations(tmp_path):
    """Negative control's control arm: a tree built to agree reports nothing."""
    _write_consistent_tree(tmp_path)
    assert cmc.check_metadata_consistency(tmp_path) == []


def test_version_disagreement_is_caught(tmp_path):
    """Negative control: a bumped CITATION.cff version with a stale pyproject.toml is flagged."""
    _write_consistent_tree(tmp_path)
    (tmp_path / "CITATION.cff").write_text(
        (tmp_path / "CITATION.cff").read_text(encoding="utf-8").replace("version: 1.0.0", "version: 2.0.0"),
        encoding="utf-8",
    )
    violations = cmc.check_metadata_consistency(tmp_path)
    assert any("version disagrees" in v and "pyproject.toml" in v for v in violations)


def test_doi_disagreement_is_caught(tmp_path):
    """Negative control: a codemeta.json identifier that drifts from CITATION.cff's DOI is flagged."""
    _write_consistent_tree(tmp_path)
    codemeta_path = tmp_path / "codemeta.json"
    payload = json.loads(codemeta_path.read_text(encoding="utf-8"))
    payload["identifier"] = "10.5281/zenodo.9999999"
    codemeta_path.write_text(json.dumps(payload), encoding="utf-8")

    violations = cmc.check_metadata_consistency(tmp_path)
    assert any("doi disagrees" in v and "codemeta.json" in v for v in violations)


def test_license_disagreement_is_caught_across_url_and_bare_forms(tmp_path):
    """Negative control: license mismatch is caught even though codemeta.json writes a URL form."""
    _write_consistent_tree(tmp_path)
    zenodo_path = tmp_path / ".zenodo.json"
    payload = json.loads(zenodo_path.read_text(encoding="utf-8"))
    payload["license"] = "MIT"
    zenodo_path.write_text(json.dumps(payload), encoding="utf-8")

    violations = cmc.check_metadata_consistency(tmp_path)
    assert any("license disagrees" in v and ".zenodo.json" in v for v in violations)


def test_keyword_set_disagreement_is_caught(tmp_path):
    """Negative control: a dropped keyword is flagged even though order differs harmlessly elsewhere."""
    _write_consistent_tree(tmp_path)
    zenodo_path = tmp_path / ".zenodo.json"
    payload = json.loads(zenodo_path.read_text(encoding="utf-8"))
    payload["keywords"] = ["widgets"]
    zenodo_path.write_text(json.dumps(payload), encoding="utf-8")

    violations = cmc.check_metadata_consistency(tmp_path)
    assert any("keywords disagree" in v and ".zenodo.json" in v for v in violations)


def test_author_orcid_disagreement_is_caught(tmp_path):
    """Negative control: a mistyped ORCID on one file is flagged without pyproject.toml (no ORCID field) flagging."""
    _write_consistent_tree(tmp_path)
    codemeta_path = tmp_path / "codemeta.json"
    payload = json.loads(codemeta_path.read_text(encoding="utf-8"))
    payload["author"][0]["@id"] = "https://orcid.org/0000-0000-0000-9999"
    codemeta_path.write_text(json.dumps(payload), encoding="utf-8")

    violations = cmc.check_metadata_consistency(tmp_path)
    assert any("author ORCIDs disagree" in v and "codemeta.json" in v for v in violations)
    assert not any("pyproject.toml" in v and "author" in v for v in violations)


def test_manuscript_config_version_disagreement_is_caught(tmp_path):
    """Negative control: the rendered manuscript's own title page drifting from CITATION.cff is flagged."""
    _write_consistent_tree(tmp_path)
    manuscript_path = tmp_path / "docs" / "manuscript" / "config.yaml"
    manuscript_path.write_text(
        manuscript_path.read_text(encoding="utf-8").replace("version: 1.0.0", "version: 0.9.0"),
        encoding="utf-8",
    )
    violations = cmc.check_metadata_consistency(tmp_path)
    assert any("version disagrees" in v and "docs/manuscript/config.yaml" in v for v in violations)


def test_missing_declared_source_raises(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "widget"\nversion = "1.0.0"\n', encoding="utf-8")
    try:
        cmc.check_metadata_consistency(tmp_path)
        raise AssertionError("expected FileNotFoundError")
    except FileNotFoundError as exc:
        assert "CITATION.cff" in str(exc)


def test_main_returns_zero_on_the_live_tree(capsys, monkeypatch):
    """The thin CLI entrypoint (argv parsing, printing, exit code) over the live tree."""
    monkeypatch.setattr("sys.argv", ["check_metadata_consistency.py"])
    code = cmc.main()
    captured = capsys.readouterr()
    assert code == 0
    assert "metadata consistency: 0 violations" in captured.out
