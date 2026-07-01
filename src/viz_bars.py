from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from . import cases, claim_ledger, metrics, roles, species
from .viz_theme import (
    ANCHOR_COLORS,
    CATEGORY_COLORS,
    EVIDENCE_KIND_COLORS,
    JURISDICTION_COLORS,
    ROLE_COLORS,
    _ACCENT,
    _INK,
    _MUTED,
    _PANEL,
    _PROJECT_ROOT,
    _annotate_bars,
    _save,
    _style_axes,
    _wrap_label,
)


def roles_overview(path: Path) -> Path:
    """Grouped bar of each role's case / statute / species / milestone counts."""
    coverage = metrics.role_coverage_matrix()
    role_list = roles.all_roles()
    kinds = ("cases", "statutes", "species", "milestones")
    x = range(len(role_list))
    width = 0.2
    fig, ax = plt.subplots(figsize=(12.4, 6.3))
    _style_axes(ax, grid_axis="y")
    group_totals = [sum(coverage[r.slug][kind] for kind in kinds) for r in role_list]
    max_value = max(max(coverage[r.slug][kind] for kind in kinds) for r in role_list)
    for xi, total in zip(x, group_totals):
        if total == 0:
            ax.axvspan(xi - 0.1, xi + 0.75, color="#f1f5f9", zorder=0)
    for i, kind in enumerate(kinds):
        values = [coverage[r.slug][kind] for r in role_list]
        bars = ax.bar(
            [xi + i * width for xi in x],
            values,
            width=width,
            label=kind.capitalize(),
            color=EVIDENCE_KIND_COLORS[kind],
            edgecolor="white",
            linewidth=0.6,
            alpha=0.94,
        )
        for bar, value in zip(bars, values):
            if value:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    value + 0.09,
                    str(value),
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    color=_INK,
                )
    for xi, role, total in zip(x, role_list, group_totals):
        role_counts = coverage[role.slug]
        dominant = max(kinds, key=lambda kind: role_counts[kind])
        label = dominant.replace("milestones", "history")
        ax.text(
            xi + 1.5 * width,
            max_value + 0.78,
            f"{label}\ntotal {total}",
            ha="center",
            va="bottom",
            fontsize=7,
            color=_MUTED,
        )
    ax.set_xticks([xi + 1.5 * width for xi in x])
    ax.set_xticklabels([_wrap_label(r.title, 12) for r in role_list], fontsize=8)
    ax.set_ylabel("Registry entries")
    ax.set_title("Evidence profile of each legal role")
    ax.set_ylim(0, max_value + 1.75)
    ax.legend(fontsize=8, ncols=4, loc="upper center", bbox_to_anchor=(0.5, 1.14))
    return _save(fig, path)


def _bar(
    path: Path,
    labels,
    values,
    title: str,
    ylabel: str,
    colors=None,
    *,
    sort_by_value: bool = False,
) -> Path:
    values = list(values)
    labels = list(labels)
    if colors is None:
        colors = ["#334155"] * len(values)
    else:
        colors = list(colors)
    if sort_by_value:
        rows = sorted(zip(labels, values, colors), key=lambda row: (-row[1], str(row[0])))
        labels, values, colors = map(list, zip(*rows))
    fig_height = max(4.2, 1.4 + 0.42 * len(labels))
    fig, ax = plt.subplots(figsize=(8.8, fig_height))
    _style_axes(ax, grid_axis="x")
    y = list(range(len(values)))
    ax.barh(y, values, color=colors, edgecolor="white", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([_wrap_label(str(label), 22) for label in labels], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel(ylabel)
    ax.set_title(title)
    ax.set_xlim(0, max(values + [1]) * 1.22)
    _annotate_bars(ax, values, horizontal=True)
    return _save(fig, path)


def cases_by_role(path: Path) -> Path:
    """Bar of case counts per role."""
    counts = cases.counts_by_role()
    role_list = roles.all_roles()
    return _bar(
        path,
        [r.title for r in role_list],
        [counts[r.slug] for r in role_list],
        "Registered cases by legal role",
        "Cases",
        colors=[ROLE_COLORS[r.slug] for r in role_list],
    )


def cases_by_jurisdiction(path: Path) -> Path:
    """Bar of case counts per jurisdiction."""
    m = metrics.compute()
    items = [(k, v) for k, v in m.cases_by_jurisdiction.items() if v > 0]
    return _bar(
        path,
        [k for k, _ in items],
        [v for _, v in items],
        "Registered cases by jurisdiction",
        "Cases",
        colors=[JURISDICTION_COLORS.get(k, "#475569") for k, _ in items],
        sort_by_value=True,
    )


def statutes_by_category(path: Path) -> Path:
    """Bar of statute counts per category."""
    m = metrics.compute()
    items = [(k, v) for k, v in m.statutes_by_category.items() if v > 0]
    return _bar(
        path,
        [k for k, _ in items],
        [v for _, v in items],
        "Statutes and treaties by category",
        "Instruments",
        colors=[CATEGORY_COLORS.get(k, "#0f766e") for k, _ in items],
        sort_by_value=True,
    )


def statutes_by_jurisdiction(path: Path) -> Path:
    """Bar of statute counts per jurisdiction."""
    m = metrics.compute()
    items = [(k, v) for k, v in m.statutes_by_jurisdiction.items() if v > 0]
    return _bar(
        path,
        [k for k, _ in items],
        [v for _, v in items],
        "Statutes and treaties by jurisdiction",
        "Instruments",
        colors=[JURISDICTION_COLORS.get(k, "#0369a1") for k, _ in items],
        sort_by_value=True,
    )


def species_by_role(path: Path) -> Path:
    """Bar of taxa counts per role."""
    counts = species.counts_by_role()
    role_list = roles.all_roles()
    return _bar(
        path,
        [r.title for r in role_list],
        [counts[r.slug] for r in role_list],
        "Insect taxa by legal role",
        "Taxa",
        colors=[ROLE_COLORS[r.slug] for r in role_list],
    )


def role_coverage(path: Path) -> Path:
    """Heatmap of roles against evidence kinds."""
    coverage = metrics.role_coverage_matrix()
    role_list = roles.all_roles()
    kinds = ("cases", "statutes", "species", "milestones")
    grid = [[coverage[r.slug][k] for k in kinds] for r in role_list]
    row_totals = [sum(row) for row in grid]
    col_totals = [sum(row[j] for row in grid) for j in range(len(kinds))]
    total = sum(row_totals)
    summary_grid = [row + [row_total] for row, row_total in zip(grid, row_totals)]
    summary_grid.append(col_totals + [total])
    fig, ax = plt.subplots(figsize=(9.0, 6.9))
    ax.set_facecolor(_PANEL)
    im = ax.imshow(summary_grid, cmap="YlGnBu", aspect="auto")
    xlabels = [k.capitalize() for k in kinds] + ["Total"]
    ylabels = [r.title for r in role_list] + ["Total"]
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels)
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels, fontsize=8)
    midpoint = max(max(row) for row in summary_grid) / 2
    ax.set_xticks([x - 0.5 for x in range(1, len(xlabels))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(ylabels))], minor=True)
    ax.grid(which="minor", color="white", linewidth=1.4)
    ax.tick_params(which="minor", bottom=False, left=False)
    for i in range(len(ylabels)):
        for j in range(len(xlabels)):
            value = summary_grid[i][j]
            is_total = i == len(ylabels) - 1 or j == len(xlabels) - 1
            ax.text(
                j,
                i,
                str(value),
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold" if is_total or value == max(summary_grid[i]) else "normal",
                color="white" if value > midpoint else _INK,
            )
    ax.set_title("Role coverage matrix with evidence totals")
    fig.colorbar(im, ax=ax, shrink=0.7, label="Entries")
    return _save(fig, path)


def claim_ledger_coverage(path: Path) -> Path:
    coverage = claim_ledger.claim_coverage_by_anchor(_PROJECT_ROOT)
    labels = [anchor.removeprefix("sec:").replace("_", " ") for anchor in coverage]
    values = list(coverage.values())
    colors = [
        ANCHOR_COLORS.get(anchor.removeprefix("sec:"), _ACCENT)
        if value
        else "#d0d7de"
        for anchor, value in coverage.items()
    ]
    fig, ax = plt.subplots(figsize=(9.4, 7.1))
    _style_axes(ax, grid_axis="x")
    y = list(range(len(values)))
    ax.barh(y, values, color=colors, edgecolor="white", linewidth=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels([_wrap_label(label, 18) for label in labels], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Quote-backed claim-ledger entries")
    ax.set_title("Live-checkable claim coverage by manuscript section")
    ax.set_xlim(0, max(values + [1]) + 1.2)
    ax.axvline(1, color="#94a3b8", linewidth=0.9, linestyle="--", alpha=0.75)
    _annotate_bars(ax, values, horizontal=True)
    ax.text(
        0.99,
        0.02,
        f"{sum(values)} verified entries",
        ha="right",
        va="bottom",
        fontsize=8,
        color=_MUTED,
        transform=ax.transAxes,
    )
    return _save(fig, path)
