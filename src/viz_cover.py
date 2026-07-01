from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import patches

from . import metrics, roles
from .viz_theme import ROLE_COLORS, _INK, _MUTED, _save, _wrap_label


def _draw_butterfly(ax: plt.Axes, x: float, y: float, scale: float, color: str) -> None:
    wing = dict(facecolor=color, edgecolor="white", linewidth=1.0, alpha=0.9)
    ax.add_patch(patches.Ellipse((x - 0.035 * scale, y + 0.018 * scale), 0.09 * scale, 0.14 * scale, angle=28, **wing))
    ax.add_patch(patches.Ellipse((x + 0.035 * scale, y + 0.018 * scale), 0.09 * scale, 0.14 * scale, angle=-28, **wing))
    ax.add_patch(patches.Ellipse((x - 0.032 * scale, y - 0.045 * scale), 0.07 * scale, 0.10 * scale, angle=-18, **wing))
    ax.add_patch(patches.Ellipse((x + 0.032 * scale, y - 0.045 * scale), 0.07 * scale, 0.10 * scale, angle=18, **wing))
    for side in (-1, 1):
        ax.plot([x, x + side * 0.055 * scale], [y, y + 0.055 * scale], color="#f8fafc", linewidth=0.7, alpha=0.7)
        ax.plot([x, x + side * 0.045 * scale], [y - 0.02 * scale, y - 0.07 * scale], color="#f8fafc", linewidth=0.7, alpha=0.7)
    ax.add_patch(patches.FancyBboxPatch((x - 0.007 * scale, y - 0.075 * scale), 0.014 * scale, 0.15 * scale, boxstyle="round,pad=0.003", facecolor=_INK, edgecolor=_INK))
    ax.plot([x, x - 0.05 * scale], [y + 0.07 * scale, y + 0.12 * scale], color=_INK, linewidth=1.0)
    ax.plot([x, x + 0.05 * scale], [y + 0.07 * scale, y + 0.12 * scale], color=_INK, linewidth=1.0)


def _draw_bee(ax: plt.Axes, x: float, y: float, scale: float) -> None:
    ax.add_patch(patches.Ellipse((x, y), 0.15 * scale, 0.07 * scale, facecolor="#f59e0b", edgecolor=_INK, linewidth=1.0))
    for dx in (-0.035, 0.0, 0.035):
        ax.plot([x + dx * scale, x + dx * scale], [y - 0.032 * scale, y + 0.032 * scale], color=_INK, linewidth=1.2)
    ax.add_patch(patches.Circle((x + 0.085 * scale, y + 0.005 * scale), 0.027 * scale, facecolor=_INK, edgecolor=_INK))
    ax.add_patch(patches.Circle((x + 0.095 * scale, y + 0.014 * scale), 0.005 * scale, facecolor="#f8fafc", edgecolor="#f8fafc"))
    ax.add_patch(patches.Ellipse((x - 0.02 * scale, y + 0.055 * scale), 0.09 * scale, 0.045 * scale, angle=18, facecolor="#dbeafe", edgecolor="#93c5fd", alpha=0.85))
    ax.add_patch(patches.Ellipse((x + 0.03 * scale, y + 0.052 * scale), 0.08 * scale, 0.04 * scale, angle=-20, facecolor="#dbeafe", edgecolor="#93c5fd", alpha=0.85))
    for dy in (-0.025, 0, 0.025):
        ax.plot([x - 0.03 * scale, x - 0.09 * scale], [y + dy * scale, y + (dy - 0.035) * scale], color=_INK, linewidth=0.8)
    ax.plot([x - 0.08 * scale, x - 0.12 * scale], [y, y - 0.012 * scale], color=_INK, linewidth=0.8)


def _draw_mosquito(ax: plt.Axes, x: float, y: float, scale: float) -> None:
    ax.add_patch(patches.Ellipse((x, y), 0.16 * scale, 0.025 * scale, angle=-12, facecolor="#64748b", edgecolor=_INK, linewidth=0.8))
    ax.add_patch(patches.Circle((x + 0.085 * scale, y - 0.02 * scale), 0.018 * scale, facecolor=_INK, edgecolor=_INK))
    ax.plot([x + 0.10 * scale, x + 0.18 * scale], [y - 0.02 * scale, y - 0.055 * scale], color=_INK, linewidth=0.8)
    ax.add_patch(patches.Ellipse((x - 0.015 * scale, y + 0.038 * scale), 0.11 * scale, 0.035 * scale, angle=25, facecolor="#e0f2fe", edgecolor="#7dd3fc", alpha=0.85))
    ax.add_patch(patches.Ellipse((x + 0.035 * scale, y + 0.032 * scale), 0.10 * scale, 0.03 * scale, angle=-20, facecolor="#e0f2fe", edgecolor="#7dd3fc", alpha=0.85))
    for dx in (-0.05, -0.015, 0.02):
        ax.plot([x + dx * scale, x + (dx - 0.07) * scale], [y - 0.005 * scale, y - 0.085 * scale], color=_INK, linewidth=0.7)
        ax.plot([x + dx * scale, x + (dx + 0.055) * scale], [y - 0.005 * scale, y - 0.09 * scale], color=_INK, linewidth=0.7)


def _draw_beetle(ax: plt.Axes, x: float, y: float, scale: float, color: str) -> None:
    ax.add_patch(patches.Ellipse((x, y), 0.12 * scale, 0.17 * scale, facecolor=color, edgecolor=_INK, linewidth=1.0))
    ax.add_patch(patches.Circle((x, y + 0.1 * scale), 0.038 * scale, facecolor=_INK, edgecolor=_INK))
    ax.plot([x, x], [y - 0.08 * scale, y + 0.075 * scale], color="white", linewidth=1.0, alpha=0.7)
    for dx, dy in ((-0.028, 0.025), (0.030, 0.010), (-0.020, -0.038)):
        ax.add_patch(patches.Circle((x + dx * scale, y + dy * scale), 0.008 * scale, facecolor="#fef3c7", edgecolor="none", alpha=0.8))
    for side in (-1, 1):
        for dy in (-0.04, 0.0, 0.04):
            ax.plot([x + side * 0.05 * scale, x + side * 0.105 * scale], [y + dy * scale, y + (dy - 0.04) * scale], color=_INK, linewidth=0.8)


def _draw_pin(ax: plt.Axes, x: float, y: float, scale: float = 1.0) -> None:
    ax.add_patch(patches.Circle((x, y), 0.008 * scale, facecolor="#f8fafc", edgecolor=_INK, linewidth=0.7, zorder=5))
    ax.plot([x, x], [y - 0.012 * scale, y - 0.07 * scale], color="#64748b", linewidth=0.6, zorder=4)


def cover(path: Path) -> Path:
    m = metrics.compute()
    fig, ax = plt.subplots(figsize=(13.6, 7.4))
    fig.patch.set_facecolor("#f6f1e8")
    ax.set_facecolor("#f6f1e8")
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(
        patches.Rectangle(
            (0, 0),
            1,
            1,
            facecolor="#f6f1e8",
            edgecolor="none",
            zorder=-5,
        )
    )
    ax.add_patch(
        patches.FancyBboxPatch(
            (0.035, 0.07),
            0.93,
            0.84,
            boxstyle="round,pad=0.016",
            facecolor="#fffaf2",
            edgecolor="#b7c2d0",
            linewidth=1.6,
        )
    )

    ax.add_patch(patches.Rectangle((0.064, 0.11), 0.006, 0.75, facecolor="#94a3b8", edgecolor="none", alpha=0.55))
    for y in (0.18, 0.31, 0.44, 0.57, 0.70, 0.83):
        ax.plot([0.07, 0.935], [y, y + 0.018 * math.sin(y * 20)], color="#e3dccf", linewidth=0.8, zorder=0)
    for x in (0.25, 0.43, 0.61, 0.79):
        ax.plot([x, x + 0.045], [0.12, 0.87], color="#ece4d7", linewidth=0.7, zorder=0)

    ax.add_patch(
        patches.FancyBboxPatch(
            (0.545, 0.205),
            0.37,
            0.55,
            boxstyle="round,pad=0.010",
            facecolor="#f8fafc",
            edgecolor="#cbd5e1",
            linewidth=1.15,
            alpha=0.96,
        )
    )
    ax.text(0.73, 0.725, "specimen-to-doctrine map", ha="center", va="center", fontsize=8.7, color=_MUTED)

    _draw_butterfly(ax, 0.18, 0.58, 0.78, ROLE_COLORS["protected"])
    _draw_bee(ax, 0.34, 0.30, 0.62)
    _draw_mosquito(ax, 0.72, 0.61, 0.92)
    _draw_beetle(ax, 0.82, 0.37, 0.78, ROLE_COLORS["defendant"])
    for x, y, s in ((0.18, 0.65, 0.76), (0.34, 0.35, 0.60), (0.72, 0.69, 0.80), (0.82, 0.47, 0.75)):
        _draw_pin(ax, x, y, s)

    links = (
        (0.39, 0.61, 0.61, 0.61, "witness", "threat"),
        (0.41, 0.325, 0.67, 0.325, "property", "moral_patient"),
        (0.46, 0.49, 0.56, 0.68, "invention", "protected"),
    )
    for x1, y1, x2, y2, left, right in links:
        ax.plot([x1, x2], [y1, y2], color="#b8c4d2", linewidth=1.0)
        ax.add_patch(patches.Circle((x1, y1), 0.012, facecolor=ROLE_COLORS[left], edgecolor="white"))
        ax.add_patch(patches.Circle((x2, y2), 0.012, facecolor=ROLE_COLORS[right], edgecolor="white"))

    ax.text(0.088, 0.82, "Entomological Law", ha="left", va="center", fontsize=34, fontweight="bold", color=_INK)
    ax.text(
        0.09,
        0.75,
        "A field map of insects as evidence, threat, property,\nproduct, patient, and weapon",
        ha="left",
        va="center",
        fontsize=14.5,
        style="italic",
        color=_MUTED,
    )
    ax.text(0.09, 0.665, "FIELD RECORD", ha="left", va="center", fontsize=8.5, color="#9ca3af", fontweight="bold")
    ax.text(
        0.09,
        0.445,
        f"{m.role_count} mapped roles / {m.case_count} cases / {m.statute_count} instruments\n"
        f"{m.species_count} taxa / {m.milestone_count} milestones across {m.timeline_span_years} years",
        ha="left",
        va="center",
        fontsize=12.3,
        color=_INK,
    )
    ax.text(
        0.09,
        0.37,
        "source-owned registries compile figures, claims, and rendered manuscript",
        ha="left",
        va="center",
        fontsize=9.4,
        color=_MUTED,
    )
    ax.text(0.075, 0.205, "registered roles in this release", ha="left", va="center", fontsize=8.2, color="#64748b")
    for i, role in enumerate(roles.all_roles()):
        x = 0.075 + i * 0.107
        ax.add_patch(
            patches.FancyBboxPatch(
                (x, 0.135),
                0.092,
                0.045,
                boxstyle="round,pad=0.003",
                facecolor=ROLE_COLORS[role.slug],
                edgecolor="#ffffff",
                linewidth=0.8,
            )
        )
        ax.text(
            x + 0.046,
            0.105,
            _wrap_label(role.title, 11),
            ha="center",
            va="top",
            fontsize=6.2,
            color=_MUTED,
        )
    return _save(fig, path)
