from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import matplotlib.pyplot as plt
from matplotlib import patches

from . import metrics, roles
from .viz_theme import ROLE_COLORS, _INK, _MUTED, _save, _wrap_label

#: Which pinned specimen stands for which registered role on the cover board.
#: Chosen for narrative fit with the manuscript: the monarch is the field's
#: own protected-subject example, the honeybee swarm is the classic property
#: dispute, the mosquito is the recurring regulated-threat/gene-drive vector,
#: and the weevil is the historical animal-trial defendant.
_SPECIMEN_ROLES = {"butterfly": "protected", "mosquito": "threat", "bee": "property", "beetle": "defendant"}


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


def _draw_specimen_card(ax: plt.Axes, *, draw_fn: Callable[..., None], draw_kwargs: dict[str, Any], x: float, y: float, scale: float, role: roles.LegalRole) -> None:
    """One pinned specimen: glyph, pin, and a role-tagged caption tick."""
    _draw_pin(ax, x, y + 0.145 * scale, scale=1.15)
    draw_fn(ax, x, y, scale, **draw_kwargs)
    tick_y = y - 0.135 * scale
    ax.plot([x - 0.05, x - 0.05], [tick_y + 0.006, tick_y - 0.006], color=ROLE_COLORS[role.slug], linewidth=2.2, solid_capstyle="round")
    ax.text(x - 0.035, tick_y, role.title, ha="left", va="center", fontsize=8.6, color=_INK)


def cover(path: Path) -> Path:
    m = metrics.compute()
    role_by_slug = {r.slug: r for r in roles.all_roles()}
    fig, ax = plt.subplots(figsize=(13.6, 7.4))
    fig.patch.set_facecolor("#f6f1e8")
    ax.set_facecolor("#f6f1e8")
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor="#f6f1e8", edgecolor="none", zorder=-5))
    ax.add_patch(patches.FancyBboxPatch((0.035, 0.07), 0.93, 0.84, boxstyle="round,pad=0.016", facecolor="#fffaf2", edgecolor="#b7c2d0", linewidth=1.6))
    ax.add_patch(patches.Rectangle((0.064, 0.11), 0.006, 0.75, facecolor="#94a3b8", edgecolor="none", alpha=0.55))

    # --- Left column: masthead typography -------------------------------
    left_x = 0.09
    ax.text(left_x, 0.862, "FIELD RECORD  ·  REGISTRY-FIRST REFERENCE", ha="left", va="center", fontsize=9.6, color="#9ca3af", fontweight="bold")
    ax.text(left_x - 0.002, 0.80, "Entomological Law", ha="left", va="center", fontsize=31, fontweight="bold", color=_INK)
    ax.text(left_x, 0.723, "A field map of insects as evidence, threat, property,\nproduct, patient, and weapon", ha="left", va="center", fontsize=14.2, style="italic", color=_MUTED, linespacing=1.5)
    ax.plot([left_x, left_x + 0.415], [0.652, 0.652], color="#d8cdb8", linewidth=1.0)
    ax.text(
        left_x,
        0.598,
        f"{m.role_count} mapped roles / {m.case_count} cases / {m.statute_count} instruments\n"
        f"{m.species_count} taxa / {m.milestone_count} milestones across {m.timeline_span_years} years",
        ha="left",
        va="center",
        fontsize=13.0,
        color=_INK,
        linespacing=1.55,
    )
    ax.text(left_x, 0.518, "source-owned registries compile figures, claims,\nand rendered manuscript", ha="left", va="center", fontsize=10.3, color=_MUTED, linespacing=1.4)

    # Pull-quote: a contiguous, verbatim excerpt of the abstract's opening
    # questions (not a paraphrase, and not a skip-and-splice) — an editorial
    # hook, not a new claim.
    ax.text(left_x, 0.425, "“", ha="left", va="center", fontsize=34, color="#d8cdb8", fontweight="bold")
    ax.text(left_x + 0.025, 0.405, "Can a fly testify? Who owns a swarm?\nIs a bumblebee a fish?", ha="left", va="center", fontsize=13.4, style="italic", color="#3f3a33", linespacing=1.6)

    ax.text(left_x - 0.015, 0.205, "registered roles in this release", ha="left", va="center", fontsize=9.4, color="#64748b")
    for i, role in enumerate(roles.all_roles()):
        x = left_x - 0.015 + i * 0.107
        ax.add_patch(patches.FancyBboxPatch((x, 0.135), 0.092, 0.045, boxstyle="round,pad=0.003", facecolor=ROLE_COLORS[role.slug], edgecolor="#ffffff", linewidth=0.8))
        ax.text(x + 0.046, 0.105, _wrap_label(role.title, 11), ha="center", va="top", fontsize=7.1, color=_MUTED)

    # --- Right panel: the specimen-to-doctrine board ---------------------
    panel_x0, panel_y0, panel_w, panel_h = 0.548, 0.205, 0.367, 0.55
    ax.add_patch(patches.FancyBboxPatch((panel_x0, panel_y0), panel_w, panel_h, boxstyle="round,pad=0.010", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.15, alpha=0.97, zorder=1))
    for frac in (0.30, 0.45, 0.60, 0.75, 0.90):
        yy = panel_y0 + 0.05 + frac * (panel_h - 0.10)
        ax.plot([panel_x0 + 0.02, panel_x0 + panel_w - 0.02], [yy, yy], color="#e7edf3", linewidth=0.7, zorder=1)
    panel_cx = panel_x0 + panel_w / 2
    ax.text(panel_cx, panel_y0 + panel_h - 0.045, "specimen-to-doctrine map", ha="center", va="center", fontsize=10.0, color=_MUTED, zorder=3)
    ax.plot([panel_cx - 0.11, panel_cx + 0.11], [panel_y0 + panel_h - 0.075, panel_y0 + panel_h - 0.075], color="#cbd5e1", linewidth=0.8, zorder=3)

    col_x = (panel_cx - 0.093, panel_cx + 0.093)
    row_y = (panel_y0 + panel_h - 0.205, panel_y0 + 0.145)
    specimens: tuple[tuple[str, Callable[..., None], dict[str, Any], float, float, float], ...] = (
        ("butterfly", _draw_butterfly, dict(color=ROLE_COLORS["protected"]), col_x[0], row_y[0], 0.46),
        ("mosquito", _draw_mosquito, {}, col_x[1], row_y[0], 0.50),
        ("bee", _draw_bee, {}, col_x[0], row_y[1], 0.44),
        ("beetle", _draw_beetle, dict(color=ROLE_COLORS["defendant"]), col_x[1], row_y[1], 0.48),
    )
    for name, draw_fn, kwargs, x, y, scale in specimens:
        role = role_by_slug[_SPECIMEN_ROLES[name]]
        _draw_specimen_card(ax, draw_fn=draw_fn, draw_kwargs=kwargs, x=x, y=y, scale=scale, role=role)

    return _save(fig, path)
