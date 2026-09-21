"""Tests for the ``scripts/scrape_updates.py`` thin orchestrator.

Every test is offline: only ``describe`` and ``parse`` modes run, both of
which are engine-level no-socket operations over fixture feed registries
and fixture feed bodies under ``tmp_path``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "scrape_updates.py"

FIXTURE_FEED = {
    "feed_id": "test-registry-feed",
    "provider": "Test Registry",
    "jurisdiction_tier": "local",
    "kind": "policy",
    "landing_url": "https://example.org/policy-updates",
    "poll_format": "rss",
}

FIXTURE_RSS_BODY = (
    "<rss><channel>"
    "<item><title>Policy Update One</title>"
    "<link>https://example.org/policy-updates/one</link>"
    "<pubDate>Tue, 10 Mar 2026 08:00:00 GMT</pubDate></item>"
    "</channel></rss>"
)


def _write_fixture_config(root: Path, **overrides) -> Path:
    """Write a minimal, valid declarative feed registry."""
    feed = {**FIXTURE_FEED, **overrides}
    config = root / "legal_updates_feeds.yaml"
    config.write_text(yaml.safe_dump({"feeds": [feed]}), encoding="utf-8")
    return config


def _run(*args: str) -> subprocess.CompletedProcess:
    """Run the orchestrator as a real subprocess with explicit exit codes."""
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_help_exits_zero() -> None:
    """--help exits 0 and prints the mode choices."""
    result = _run("--help")
    assert result.returncode == 0, result.stderr
    assert "describe" in result.stdout
    assert "ingest" in result.stdout


def test_describe_writes_deterministic_manifest(tmp_path: Path) -> None:
    """describe mode writes a byte-identical manifest on every run."""
    config = _write_fixture_config(tmp_path)
    out_a, out_b = tmp_path / "a.json", tmp_path / "b.json"
    run_a = _run("describe", "--config", str(config), "--output", str(out_a))
    assert run_a.returncode == 0, run_a.stderr
    assert run_a.stdout.strip().endswith(f"wrote {out_a}")
    run_b = _run("describe", "--config", str(config), "--output", str(out_b))
    assert run_b.returncode == 0, run_b.stderr
    assert out_a.read_bytes() == out_b.read_bytes()

    manifest = json.loads(out_a.read_text(encoding="utf-8"))
    assert manifest["item_count"] == 0
    assert manifest["updates"]["test-registry-feed"] == []
    assert manifest["feeds"][0]["feed_id"] == "test-registry-feed"
    assert manifest["generator"] == "legal_informatics.legal_updates.write_discovery"


def test_parse_mode_offline_fixture(tmp_path: Path) -> None:
    """parse mode turns local fixture bodies into manifest items offline."""
    config = _write_fixture_config(tmp_path)
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "test-registry-feed.rss").write_text(FIXTURE_RSS_BODY, encoding="utf-8")
    output = tmp_path / "manifest.json"

    result = _run("parse", "--config", str(config), "--fixture-dir", str(fixture_dir), "--output", str(output))
    assert result.returncode == 0, result.stderr
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["item_count"] == 1
    item = manifest["updates"]["test-registry-feed"][0]
    assert item["url"] == "https://example.org/policy-updates/one"
    assert item["title"] == "Policy Update One"


def test_malformed_feed_config_clear_error(tmp_path: Path) -> None:
    """A malformed registry fails with a one-line error, never a traceback."""
    bad = tmp_path / "bad.yaml"
    bad.write_text("feeds: [not_a_mapping_rows]\n", encoding="utf-8")
    result = _run("describe", "--config", str(bad), "--output", str(tmp_path / "out.json"))
    assert result.returncode == 1
    assert result.stderr.startswith("error: ")
    assert "Traceback" not in result.stderr
    assert not (tmp_path / "out.json").exists()


def test_missing_fixture_body_clear_error(tmp_path: Path) -> None:
    """parse mode without a body file for a declared feed fails cleanly."""
    config = _write_fixture_config(tmp_path)
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    result = _run("parse", "--config", str(config), "--fixture-dir", str(fixture_dir), "--output", str(tmp_path / "out.json"))
    assert result.returncode == 1
    assert result.stderr.startswith("error: ")
    assert "missing fixture body" in result.stderr


def test_script_registered_in_surface_docs() -> None:
    """The orchestrator is rostered in the scripts/ surface documentation."""
    docs_root = SCRIPT_PATH.parent
    for doc_name in ("AGENTS.md", "README.md"):
        text = (docs_root / doc_name).read_text(encoding="utf-8")
        assert "scrape_updates.py" in text, f"scripts/{doc_name} does not roster scrape_updates.py"
