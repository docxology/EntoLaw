from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import patches

from . import interconnections, roles
from .viz_theme import ROLE_COLORS, _INK, _MUTED, _role_label, _save, _wrap_label


def role_interconnections(path: Path) -> Path:
    """Circular network of roles linked by interconnection themes."""
    role_list = list(roles.role_slugs())
    n = len(role_list)
    pos = {
        slug: (math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n))
        for i, slug in enumerate(role_list)
    }
    fig, ax = plt.subplots(figsize=(9.0, 8.0))
    ax.set_facecolor("#fbfcfe")
    theme_colors = {
        "definitional_problem": "#94a3b8",
        "expert_testimony_bridge": "#2563eb",
        "biotech_pivot": "#ea580c",
        "property_conservation_mirror": "#16a34a",
        "ancient_modern_rhyme": "#7c3aed",
    }
    for ti, link in enumerate(interconnections.all_interconnections()):
        color = theme_colors[link.slug]
        members = list(link.roles)
        for a in range(len(members)):
            for b in range(a + 1, len(members)):
                xa, ya = pos[members[a]]
                xb, yb = pos[members[b]]
                rad = 0.18 if (a + b + ti) % 2 == 0 else -0.18
                if link.slug == "definitional_problem":
                    rad = 0.08
                ax.add_patch(
                    patches.FancyArrowPatch(
                        (xa, ya),
                        (xb, yb),
                        arrowstyle="-",
                        connectionstyle=f"arc3,rad={rad}",
                        mutation_scale=1,
                        linewidth=0.9 if link.slug == "definitional_problem" else 2.0,
                        color=color,
                        alpha=0.16 if link.slug == "definitional_problem" else 0.55,
                        zorder=1,
                    )
                )
        legend_label = link.theme
        if link.slug == "definitional_problem":
            reach = (
                "all" if set(members) == set(role_list) else f"{len(members)} of {n}"
            )
            legend_label = f"{link.theme} (touches {reach} roles)"
        legend_text = _wrap_label(legend_label, 34).replace("\n", " ")
        if link.slug == "definitional_problem":
            ax.plot([], [], color=color, label=legend_text, linewidth=1.6, alpha=0.5)
        else:
            ax.plot([], [], color=color, label=legend_text, linewidth=2.4)
    degree = interconnections.role_link_degree()
    max_degree = max(degree.values())
    for slug in role_list:
        x, y = pos[slug]
        size = 390 + 210 * degree[slug] / max_degree
        ax.scatter(
            x,
            y,
            s=size,
            color=ROLE_COLORS[slug],
            zorder=3,
            edgecolors="white",
            linewidth=1.7,
        )
        label_x, label_y = x * 1.2, y * 1.2
        ax.annotate(
            _wrap_label(_role_label(slug), 13),
            (label_x, label_y),
            fontsize=8.2,
            ha="center",
            va="center",
            zorder=4,
            color=_INK,
            wrap=True,
            bbox=dict(
                boxstyle="round,pad=0.22", facecolor="white", edgecolor="#cbd5e1"
            ),
        )
        ax.text(
            x,
            y - 0.01,
            str(degree[slug]),
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="white",
            zorder=5,
        )
    ax.text(
        0,
        0,
        "status\nmigration",
        ha="center",
        va="center",
        fontsize=13,
        fontweight="bold",
        color=_INK,
        bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor="#cbd5e1"),
    )
    ax.text(
        0,
        -0.19,
        "node number = linked themes",
        ha="center",
        va="center",
        fontsize=7.2,
        color=_MUTED,
    )
    ax.set_title(
        "Interconnection themes across legal roles",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    ax.text(
        0,
        1.30,
        "Edge colour = shared theme; node size and number = how many themes touch that role.",
        ha="center",
        va="center",
        fontsize=8,
        color=_MUTED,
    )
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(0.86, 0.92),
        fontsize=7.6,
        frameon=False,
        labelspacing=1.15,
    )
    ax.set_xlim(-1.42, 1.85)
    ax.set_ylim(-1.34, 1.4)
    ax.set_axis_off()
    return _save(fig, path)


def architecture(path: Path) -> Path:
    """Three-column inputs → methods → outputs pipeline diagram."""
    from . import package_map

    stages = package_map.pipeline_stages()
    fig, ax = plt.subplots(figsize=(11.0, 6.2))
    ax.set_facecolor("#fbfcfe")
    col_x = [0.15, 0.5, 0.85]
    panel_colors = ["#e0f2fe", "#ecfdf5", "#fef3c7"]
    for ci, (label, nodes) in enumerate(stages):
        ax.add_patch(
            patches.FancyBboxPatch(
                (col_x[ci] - 0.13, 0.08),
                0.26,
                0.84,
                boxstyle="round,pad=0.02",
                facecolor=panel_colors[ci],
                edgecolor="#cbd5e1",
                linewidth=1.0,
                alpha=0.75,
            )
        )
        ax.text(col_x[ci], 0.95, label, ha="center", fontsize=12, fontweight="bold")
        for ni, node in enumerate(nodes):
            y = 0.85 - ni * 0.12
            ax.text(
                col_x[ci],
                y,
                node,
                ha="center",
                va="center",
                fontsize=8,
                bbox=dict(
                    boxstyle="round,pad=0.32",
                    facecolor="white",
                    edgecolor="#64748b",
                    linewidth=0.8,
                ),
            )
    ax.annotate(
        "",
        xy=(0.37, 0.43),
        xytext=(0.28, 0.43),
        arrowprops=dict(arrowstyle="-|>", lw=2, color="#334155"),
    )
    ax.annotate(
        "",
        xy=(0.72, 0.43),
        xytext=(0.63, 0.43),
        arrowprops=dict(arrowstyle="-|>", lw=2, color="#334155"),
    )
    ax.set_title("Package architecture: source registries to rendered outputs")
    ax.set_axis_off()
    return _save(fig, path)
