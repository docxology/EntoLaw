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
    (1900, 1949, "1900-1949"),
    (1950, 1969, "1950-1969"),
    (1970, 2009, "1970-2009"),
    (2010, 9999, "2010+"),
)
_FOCAL_CALLOUTS = {
    "hittite_laws_bees": ("Hittite\nbee theft", (0, 12)),
    "mishnah_bava_batra5_3_beehive": ("Mishnah\nbeehive sale", (0, -22)),
    "lex_salica_bees": ("Salic\nbee theft", (22, 42)),
    "songci1247": ("Song Ci\nsickle", (34, 18)),
    "justinian533": ("Justinian\nInstitutes", (70, -2)),
    "edictum_rothari_bees": ("Rothari\nhives", (26, 14)),
    "fleta1290_bees": ("Fleta\nbees", (-20, -24)),
    "menabrea1846_animal_judgments": ("Menabrea\ninsect trial", (42, 20)),
    "bergeret1855_infanticide": ("Bergeret\ninfanticide", (-70, -16)),
    "evans1884_bugs_beasts": ("Evans\n1884", (-18, -28)),
    "megnin1894": ("Megnin\ncadavers", (-36, 28)),
    "destructive_insects1877": ("UK pest\norders", (-52, 18)),
    "federal_insecticide1910": ("Insecticide\nAct", (-32, 20)),
    "plant_quarantine1912": ("Plant\nquarantine", (32, -22)),
    "india_destructive_insects1914": ("India pest\nAct", (42, 18)),
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

    fig = plt.figure(figsize=(14.2, 9.2), constrained_layout=True)
    grid = fig.add_gridspec(
        3,
        2,
        height_ratios=(1.0, 1.62, 2.0),
        width_ratios=(1.1, 1.0),
    )
    ax_bands = fig.add_subplot(grid[0, :])
    ax_pre1950 = fig.add_subplot(grid[1, :])
    ax_1950s = fig.add_subplot(grid[2, 0])
    ax_recent = fig.add_subplot(grid[2, 1], sharey=ax_1950s)

    _plot_date_bands(ax_bands, citations)
    _plot_citation_strip(
        ax_pre1950,
        [entry for entry in citations if entry.year < 1950],
        xlim=(min(entry.year for entry in citations) - 25, 1950),
        title="Pre-1950 legal-historical, regulatory, and scientific foundations",
        annotate_focal=True,
    )
    _plot_citation_strip(
        ax_1950s,
        [entry for entry in citations if 1950 <= entry.year < 2010],
        xlim=(1950, 2010),
        title="1950-2009 scholarship, statutes, and case-law consolidation",
        annotate_focal=False,
    )
    _plot_citation_strip(
        ax_recent,
        [entry for entry in citations if entry.year >= 2010],
        xlim=(2010, max(entry.year for entry in citations) + 1),
        title="2010+ current law, official sources, and live scholarship",
        annotate_focal=False,
    )
    ax_recent.tick_params(labelleft=False)
    handles, labels = _legend_items((ax_pre1950, ax_1950s, ax_recent))
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
    colors = ["#d8b4fe", "#c4b5fd", "#fbbf24", "#f97316", "#f59e0b", "#93c5fd", "#34d399", "#2563eb"]
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
    ax.set_title(f"Every bibliography entry with a parseable source year (n={len(citations)})")


def _plot_citation_strip(
    ax: plt.Axes,
    citations: list[CitationDate],
    *,
    xlim: tuple[int, int],
    title: str,
    annotate_focal: bool,
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
    if annotate_focal:
        _annotate_focal_sources(ax, citations, y_lookup)
    ax.set_yticks(range(len(_FAMILY_ORDER)))
    ax.set_yticklabels([family.title() for family in _FAMILY_ORDER], fontsize=8)
    ax.set_xlim(*xlim)
    ax.set_ylim(-0.65, len(_FAMILY_ORDER) - 0.35)
    ax.xaxis.set_major_formatter(FuncFormatter(_format_year))
    xlabel = "Source date (negative years are BCE)" if xlim[0] < 0 else "Source date"
    ax.set_xlabel(xlabel)
    ax.set_title(title)


def _annotate_focal_sources(
    ax: plt.Axes,
    citations: list[CitationDate],
    y_lookup: dict[str, int],
) -> None:
    labeled = [entry for entry in citations if entry.key in _FOCAL_CALLOUTS]
    for entry in labeled:
        label, offset = _FOCAL_CALLOUTS[entry.key]
        ax.annotate(
            label,
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


def _legend_items(axes: tuple[plt.Axes, ...]) -> tuple[list[object], list[str]]:
    handles: list[object] = []
    labels: list[str] = []
    seen: set[str] = set()
    for ax in axes:
        for handle, label in zip(*ax.get_legend_handles_labels(), strict=True):
            if label in seen:
                continue
            seen.add(label)
            handles.append(handle)
            labels.append(label)
    return handles, labels


def _stable_jitter(key: str) -> float:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return ((int(digest[:2], 16) / 255) - 0.5) * 0.48


def _format_year(value: float, _position: int) -> str:
    year = int(value)
    if year < 0:
        return f"{abs(year)} BCE"
    return str(year)
