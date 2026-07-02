from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from . import roles, timeline
from .viz_theme import ROLE_COLORS, _INK, _role_label, _save, _style_axes


def timeline_figure(path: Path) -> Path:
    """Scatter of milestones by year, lane and colour by role."""
    milestones = timeline.all_milestones()
    role_order = list(roles.role_slugs())
    fig, ax = plt.subplots(figsize=(13.4, 6.4))
    _style_axes(ax, grid_axis="x")
    eras = (
        (-1700, 500, "ancient\napiculture law", "#fff7ed", 0.5),
        (500, 1800, "pre-modern\nproperty, trials + silk", "#f8fafc", 0.5),
        (1800, 1970, "evidence\n+ property", "#eef6ff", 0.16),
        (1970, 2027, "modern regulation\n+ welfare", "#f0fdf4", 0.5),
    )
    for start, end, label, color, label_frac in eras:
        ax.axvspan(start, end, color=color, alpha=0.8, zorder=0)
        label_y = len(role_order) - (1.75 if start >= 1970 else 0.35)
        ax.text(
            start + (end - start) * label_frac,
            label_y,
            label,
            ha="center",
            va="top",
            fontsize=7.5,
            color="#5b6472",
        )
    key_labels = {
        "Hittite Laws on bees and hives": "Hittite\nhives",
        "Mishnah on beehives and nuisance": "Mishnah\nbees",
        "Salic Law on stolen bees": "Salic\nbee theft",
        "Justinian on bee property": "Roman\nbees",
        "Rothari on hives and bee trees": "Rothari\nhives",
        "The Sickle Murder": "Sickle\nMurder",
        "Fleta on bee occupation": "Fleta\nbees",
        "Weevils of St-Julien (sequel)": "weevils\npreserve",
        "Virginia silk-input mandate": "VA silk\ninputs",
        "Blackstone on hived bees": "Blackstone\nbees",
        "UK Destructive Insects Act": "UK pest\norders",
        "Plant Quarantine Act": "US plant\nquarantine",
        "Biological Weapons Convention": "BWC",
        "Diamond v. Chakrabarty": "Chakrabarty",
        "Monarch proposal and screwworm detection": "monarch\n+ screwworm",
        "Kirstin Lobato exoneration": "Lobato\nexoneration",
    }
    label_offsets = {
        "Hittite Laws on bees and hives": (0, 15),
        "Mishnah on beehives and nuisance": (0, -18),
        "Salic Law on stolen bees": (-30, 15),
        "Justinian on bee property": (36, 25),
        "Rothari on hives and bee trees": (0, -18),
        "UK Destructive Insects Act": (0, 13),
        "Plant Quarantine Act": (-38, -22),
        "Kirstin Lobato exoneration": (30, 18),
        "Biological Weapons Convention": (30, 9),
    }
    for y in range(len(role_order)):
        ax.axhline(y, color="#e5e7eb", linewidth=0.7, zorder=0)
    for ms in milestones:
        y = role_order.index(ms.role)
        ax.scatter(
            ms.year,
            y,
            color=ROLE_COLORS[ms.role],
            s=82,
            zorder=3,
            edgecolors="white",
            linewidth=0.8,
        )
        if ms.title in key_labels:
            xytext = label_offsets.get(ms.title, (0, 9))
            ax.annotate(
                f"{ms.year}\n{key_labels[ms.title]}",
                (ms.year, y),
                textcoords="offset points",
                xytext=xytext,
                fontsize=7,
                ha="center",
                va="bottom" if xytext[1] >= 0 else "top",
                color=_INK,
                bbox=dict(
                    boxstyle="round,pad=0.18",
                    facecolor="white",
                    edgecolor="#cbd5e1",
                    alpha=0.9,
                ),
            )
    ax.set_yticks(range(len(role_order)))
    ax.set_yticklabels([_role_label(s) for s in role_order], fontsize=8)
    ax.set_xlabel("Year")
    ax.set_title("Milestones by legal role")
    ax.set_ylim(-0.7, len(role_order) - 0.15)
    ax.set_xlim(timeline.span()[0] - 40, timeline.span()[1] + 70)
    return _save(fig, path)
