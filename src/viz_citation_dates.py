from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from .viz_citation_date_records import (
    DATE_BANDS,
    FAMILY_COLORS,
    FAMILY_ORDER,
    FOCAL_CALLOUTS,
    PRE_2000_BRIDGE_CALLOUT_KEYS,
    SOURCE_FAMILIES,
)
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
        return SOURCE_FAMILIES.get(self.entry_type.lower(), "other sources")


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
    ax_pre1700 = fig.add_subplot(grid[1, :])
    ax_1700_to_1999 = fig.add_subplot(grid[2, 0])
    ax_recent = fig.add_subplot(grid[2, 1], sharey=ax_1700_to_1999)

    _plot_date_bands(ax_bands, citations)
    _plot_citation_strip(
        ax_pre1700,
        [entry for entry in citations if entry.year < 1700],
        xlim=(min(entry.year for entry in citations) - 25, 1700),
        title="Pre-1700 legal-historical, regulatory, and scientific foundations",
        annotate_focal=True,
        annotate_keys=None,
    )
    _plot_citation_strip(
        ax_1700_to_1999,
        [entry for entry in citations if 1700 <= entry.year < 2000],
        xlim=(1700, 2000),
        title="1700-1999 scholarship, statutes, and case-law consolidation",
        annotate_focal=True,
        annotate_keys=PRE_2000_BRIDGE_CALLOUT_KEYS,
    )
    _plot_citation_strip(
        ax_recent,
        [entry for entry in citations if entry.year >= 2000],
        xlim=(2000, max(entry.year for entry in citations) + 1),
        title="2000+ current law, official sources, and live scholarship",
        annotate_focal=False,
        annotate_keys=None,
    )
    ax_recent.tick_params(labelleft=False)
    handles, labels = _legend_items((ax_pre1700, ax_1700_to_1999, ax_recent))
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
        for start, end, _label in DATE_BANDS
    ]
    labels = [label for _start, _end, label in DATE_BANDS]
    colors = [
        "#d8b4fe",
        "#c4b5fd",
        "#fbbf24",
        "#f97316",
        "#f59e0b",
        "#93c5fd",
        "#34d399",
        "#14b8a6",
        "#2563eb",
    ]
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
    annotate_keys: set[str] | None,
) -> None:
    _style_axes(ax, grid_axis="x")
    y_lookup = {family: i for i, family in enumerate(FAMILY_ORDER)}
    for family in FAMILY_ORDER:
        family_entries = [entry for entry in citations if entry.family == family]
        if not family_entries:
            continue
        xs = [entry.year for entry in family_entries]
        ys = [y_lookup[family] + _stable_jitter(entry.key) for entry in family_entries]
        ax.scatter(
            xs,
            ys,
            s=54,
            color=FAMILY_COLORS[family],
            edgecolor="white",
            linewidth=0.6,
            alpha=0.9,
            label=family,
        )
    if annotate_focal:
        _annotate_focal_sources(ax, citations, y_lookup, annotate_keys)
    ax.set_yticks(range(len(FAMILY_ORDER)))
    ax.set_yticklabels([family.title() for family in FAMILY_ORDER], fontsize=8)
    ax.set_xlim(*xlim)
    ax.set_ylim(-0.65, len(FAMILY_ORDER) - 0.35)
    ax.xaxis.set_major_formatter(FuncFormatter(_format_year))
    xlabel = "Source date (negative years are BCE)" if xlim[0] < 0 else "Source date"
    ax.set_xlabel(xlabel)
    ax.set_title(title)


def _annotate_focal_sources(
    ax: plt.Axes,
    citations: list[CitationDate],
    y_lookup: dict[str, int],
    annotation_keys: set[str] | None,
) -> None:
    allowed = FOCAL_CALLOUTS.keys() if annotation_keys is None else annotation_keys
    labeled = [entry for entry in citations if entry.key in allowed]
    for entry in labeled:
        label, offset = FOCAL_CALLOUTS[entry.key]
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
