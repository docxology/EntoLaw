from __future__ import annotations

import posixpath
import re
from html.parser import HTMLParser
from pathlib import Path

import yaml

from src import claim_ledger as cl
from src import manuscript_variables as mv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIZE_GATE_MARKER = "entolaw-size-ok:"


class _ImageSourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "img":
            return
        attrs_by_name = dict(attrs)
        src = attrs_by_name.get("src")
        if src:
            self.sources.append(src)


def _pure_loc(path: Path) -> int:
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def _bib_entries() -> dict[str, str]:
    text = (PROJECT_ROOT / "manuscript" / "references.bib").read_text(
        encoding="utf-8"
    )
    entries: dict[str, str] = {}
    for match in re.finditer(r"@\w+\{\s*([^,]+),([\s\S]*?)(?=\n@\w+\{|\Z)", text):
        entries[match.group(1)] = match.group(2)
    return entries


def test_current_cited_scholarship_has_real_bibliographic_metadata():
    cited = mv.manuscript_citation_inventory(PROJECT_ROOT / "manuscript")
    entries = _bib_entries()
    offenders: list[str] = []
    for key in sorted(cited):
        body = entries.get(key, "")
        year_match = re.search(r"year\s*=\s*\{(\d{4})\}", body)
        is_current = bool(year_match and int(year_match.group(1)) >= 2020)
        is_scholarship = body.lstrip().startswith(
            (
                "author = {",
                "author = {{",
            )
        ) and ("journal =" in body or "publisher =" in body)
        if not (is_current and is_scholarship):
            continue
        has_source_pointer = any(
            token in body for token in ("doi = {", "howpublished = {\\url{")
        )
        if "author = {{Authors}}" in body or not has_source_pointer:
            offenders.append(key)
    assert not offenders, (
        "current cited scholarship needs real authors and a DOI/URL pointer: "
        f"{offenders}"
    )


def test_manuscript_title_uses_subtitle_for_scope():
    config = yaml.safe_load(
        (PROJECT_ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    )
    title = config["paper"]["title"]
    subtitle = config["paper"]["subtitle"]
    assert ":" not in title
    assert "the eight" not in title.lower()
    assert subtitle


def test_rendered_web_export_has_no_raw_manuscript_markers():
    web_dir = PROJECT_ROOT / "output" / "web"
    assert web_dir.exists(), "rendered web output is missing"
    offenders: list[str] = []
    for path in sorted(web_dir.glob("*.html")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in ("{{", "}}", "[@", "@fig:"):
            if marker in text:
                offenders.append(f"{path.relative_to(PROJECT_ROOT)} contains {marker}")
    assert not offenders


def test_rendered_web_export_self_serves_figure_assets():
    web_dir = PROJECT_ROOT / "output" / "web"
    assert web_dir.exists(), "rendered web output is missing"
    missing: list[str] = []
    for path in sorted(web_dir.glob("*.html")):
        parser = _ImageSourceParser()
        parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
        for src in parser.sources:
            if src.startswith(("http://", "https://", "data:")):
                continue
            served_path = posixpath.normpath(posixpath.join("/", src)).lstrip("/")
            target = web_dir / served_path
            if not target.exists() or target.stat().st_size == 0:
                missing.append(
                    f"{path.relative_to(PROJECT_ROOT)} -> {src} "
                    f"(served as {served_path})"
                )
    assert not missing, f"web export has missing or empty served figures: {missing}"


def test_rendered_bibliography_does_not_use_truncated_legal_labels():
    bibliography = PROJECT_ROOT / "output" / "pdf" / "_combined_manuscript.bbl"
    assert bibliography.exists(), "rendered bibliography is missing"
    text = bibliography.read_text(encoding="utf-8")
    truncated_labels = {
        "ces",
        "cit",
        "nag",
        "ppa",
        "uks",
    }
    offenders = [
        label for label in sorted(truncated_labels) if f"\\bibitem[{label}(" in text
    ]
    assert not offenders, (
        "legal/statutory bibliography entries need institutional labels, not "
        f"BibTeX key fragments: {offenders}"
    )


def test_source_modules_stay_under_publication_size_gate():
    oversized: list[str] = []
    for path in sorted((PROJECT_ROOT / "src").glob("*.py")):
        first_lines = "\n".join(path.read_text(encoding="utf-8").splitlines()[:5])
        if SIZE_GATE_MARKER in first_lines:
            continue
        pure_loc = _pure_loc(path)
        if pure_loc > 250:
            oversized.append(f"{path.relative_to(PROJECT_ROOT)}:{pure_loc}")
    assert not oversized, (
        f"oversized source modules require split or {SIZE_GATE_MARKER}: {oversized}"
    )


def test_size_gate_marker_is_not_a_ruff_noqa_directive():
    source_text = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted((PROJECT_ROOT / "src").glob("*.py"))
    )
    assert "# noqa: SIZE_OK" not in source_text
    assert SIZE_GATE_MARKER in source_text


def test_new_current_status_and_policy_gap_claims_are_ledgered():
    claim_ids = {
        c.claim_id for c in cl.load_claims(PROJECT_ROOT / "data" / "claim_ledger.yaml")
    }
    assert {
        "north-american-insect-protection-gap-2026",
        "eu-authorised-insect-novel-foods-2026",
        "new-world-screwworm-spread-2026",
    } <= claim_ids
