from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from .viz_theme import _INK, _save, _style_axes

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_REFERENCES_BIB = _PROJECT_ROOT / "manuscript" / "references.bib"
_ENTRY_RE = re.compile(
    r"@(?P<entry_type>[A-Za-z]+)\{(?P<key>[^,\s]+),(?P<body>.*?)(?=\n@|\Z)",
    re.S,
)
_YEAR_RE = re.compile(r"\byear\s*=\s*[\{\"](?P<year>-?\d{1,4})", re.I)


@dataclass(frozen=True)
class CitationDate:
    key: str
    entry_type: str
    year: int

    @property
    def family(self) -> str:
        return _SOURCE_FAMILIES.get(self.entry_type.lower(), "other sources")


_SOURCE_FAMILIES = {
    "article": "scholarship",
    "book": "books and treatises",
    "case": "case reports",
    "incollection": "books and treatises",
    "institutes": "primary law",
    "misc": "official and web",
    "patent": "primary law",
    "statute": "primary law",
}
_FAMILY_ORDER = (
    "primary law",
    "case reports",
    "books and treatises",
    "scholarship",
    "official and web",
    "other sources",
)
_FAMILY_COLORS = {
    "primary law": "#7c3aed",
    "case reports": "#0f766e",
    "books and treatises": "#b45309",
    "scholarship": "#2563eb",
    "official and web": "#64748b",
    "other sources": "#111827",
}
_DATE_BANDS = (
    (-9999, 999, "before 1000 CE"),
    (1000, 1499, "1000-1499"),
    (1500, 1699, "1500-1699"),
    (1700, 1899, "1700-1899"),
    (1900, 1969, "1900-1969"),
    (1970, 2009, "1970-2009"),
    (2010, 9999, "2010+"),
)
_EARLY_LABELS = {
    "hittite_laws_bees": "Hittite\nbee theft",
    "mishnah_bava_batra5_3_beehive": "Mishnah\nbeehive sale",
    "lex_salica_bees": "Salic\nbee theft",
    "justinian533": "Justinian\nInstitutes",
    "edictum_rothari_bees": "Rothari\nhives",
    "fleta1290_bees": "Fleta\nbees",
}


def bibliography_dates(path: Path = _REFERENCES_BIB) -> tuple[CitationDate, ...]:
    text = path.read_text(encoding="utf-8")
    entries: list[CitationDate] = []
    for match in _ENTRY_RE.finditer(text):
        year_match = _YEAR_RE.search(match.group("body"))
        if year_match is None:
            continue
        entries.append(
            CitationDate(
                key=match.group("key"),
                entry_type=match.group("entry_type"),
                year=int(year_match.group("year")),
            )
        )
    return tuple(sorted(entries, key=lambda entry: (entry.year, entry.key)))


def citation_dates(path: Path) -> Path:
    citations = bibliography_dates()
    if not citations:
        raise ValueError("No parseable citation years found in references.bib")

    fig = plt.figure(figsize=(13.4, 7.4), constrained_layout=True)
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=(1.0, 2.35),
        width_ratios=(1.1, 1.0),
    )
    ax_bands = fig.add_subplot(grid[0, :])
    ax_early = fig.add_subplot(grid[1, 0])
    ax_late = fig.add_subplot(grid[1, 1], sharey=ax_early)

    _plot_date_bands(ax_bands, citations)
    _plot_citation_strip(
        ax_early,
        [entry for entry in citations if entry.year < 1800],
        xlim=(min(entry.year for entry in citations) - 25, 1800),
        title="Early and received texts",
        annotate_early=True,
    )
    _plot_citation_strip(
        ax_late,
        [entry for entry in citations if entry.year >= 1800],
        xlim=(1800, max(entry.year for entry in citations) + 10),
        title="Modern scholarship, cases, and official sources",
        annotate_early=False,
    )
    ax_late.tick_params(labelleft=False)
    handles, labels = ax_late.get_legend_handles_labels()
    if handles:
        fig.legend(
            handles,
            labels,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.06),
            ncol=3,
            frameon=False,
            fontsize=8,
        )
    return _save(fig, path)


def _plot_date_bands(ax: plt.Axes, citations: tuple[CitationDate, ...]) -> None:
    _style_axes(ax, grid_axis="y")
    counts = [
        sum(start <= entry.year <= end for entry in citations)
        for start, end, _label in _DATE_BANDS
    ]
    labels = [label for _start, _end, label in _DATE_BANDS]
    colors = ["#ede9fe", "#ddd6fe", "#c4b5fd", "#bfdbfe", "#93c5fd", "#60a5fa", "#2563eb"]
    bars = ax.bar(labels, counts, color=colors, edgecolor="white", linewidth=1)
    for bar, count in zip(bars, counts, strict=True):
        ax.annotate(
            str(count),
            (bar.get_x() + bar.get_width() / 2, count),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            va="bottom",
            fontsize=8,
            color=_INK,
        )
    ax.set_ylabel("Citations")
    ax.set_title("Bibliography entries by source date band")


def _plot_citation_strip(
    ax: plt.Axes,
    citations: list[CitationDate],
    *,
    xlim: tuple[int, int],
    title: str,
    annotate_early: bool,
) -> None:
    _style_axes(ax, grid_axis="x")
    y_lookup = {family: i for i, family in enumerate(_FAMILY_ORDER)}
    for family in _FAMILY_ORDER:
        family_entries = [entry for entry in citations if entry.family == family]
        if not family_entries:
            continue
        xs = [entry.year for entry in family_entries]
        ys = [y_lookup[family] + _stable_jitter(entry.key) for entry in family_entries]
        ax.scatter(
            xs,
            ys,
            s=54,
            color=_FAMILY_COLORS[family],
            edgecolor="white",
            linewidth=0.6,
            alpha=0.9,
            label=family,
        )
    if annotate_early:
        _annotate_early_sources(ax, citations, y_lookup)
    ax.set_yticks(range(len(_FAMILY_ORDER)))
    ax.set_yticklabels([family.title() for family in _FAMILY_ORDER], fontsize=8)
    ax.set_xlim(*xlim)
    ax.set_ylim(-0.65, len(_FAMILY_ORDER) - 0.35)
    ax.xaxis.set_major_formatter(FuncFormatter(_format_year))
    ax.set_xlabel("Source date (negative years are BCE)")
    ax.set_title(title)


def _annotate_early_sources(
    ax: plt.Axes,
    citations: list[CitationDate],
    y_lookup: dict[str, int],
) -> None:
    offsets = ((0, 12), (0, -20), (24, 10), (-24, -22), (30, 14), (-30, -24))
    labeled = [entry for entry in citations if entry.key in _EARLY_LABELS]
    for index, entry in enumerate(labeled):
        offset = offsets[index % len(offsets)]
        ax.annotate(
            _EARLY_LABELS[entry.key],
            (entry.year, y_lookup[entry.family] + _stable_jitter(entry.key)),
            textcoords="offset points",
            xytext=offset,
            ha="center",
            va="bottom" if offset[1] >= 0 else "top",
            fontsize=6.4,
            color=_INK,
            bbox=dict(
                boxstyle="round,pad=0.14",
                facecolor="white",
                edgecolor="#cbd5e1",
                alpha=0.88,
            ),
            arrowprops=dict(arrowstyle="-", color="#cbd5e1", linewidth=0.6),
        )


def _stable_jitter(key: str) -> float:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return ((int(digest[:2], 16) / 255) - 0.5) * 0.48


def _format_year(value: float, _position: int) -> str:
    year = int(value)
    if year < 0:
        return f"{abs(year)} BCE"
    return str(year)
