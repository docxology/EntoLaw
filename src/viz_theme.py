from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from . import roles  # noqa: E402

_DPI = 150
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_INK = "#111827"
_MUTED = "#5b6472"
_GRID = "#d8dee9"
_PANEL = "#f8fafc"
_ACCENT = "#b42318"
ROLE_COLORS: dict[str, str] = {
    "witness": "#1f77b4",
    "threat": "#d62728",
    "protected": "#2ca02c",
    "property": "#9467bd",
    "invention": "#ff7f0e",
    "defendant": "#8c564b",
    "moral_patient": "#e377c2",
    "weapon": "#7f7f7f",
}

EVIDENCE_KIND_COLORS: dict[str, str] = {
    "cases": "#2563eb",
    "statutes": "#059669",
    "species": "#f59e0b",
    "milestones": "#7c3aed",
}

JURISDICTION_COLORS: dict[str, str] = {
    "US-federal": "#1d4ed8",
    "US-state": "#0f766e",
    "EU": "#7c3aed",
    "UK": "#be123c",
    "India": "#c2410c",
    "USSR": "#b91c1c",
    "international": "#334155",
    "Canada": "#dc2626",
    "England & Wales": "#9333ea",
    "U.S. patent": "#ea580c",
    "U.S. Supreme Court": "#0f172a",
    "U.S. federal appellate": "#2563eb",
    "U.S. state": "#0f766e",
}

CATEGORY_COLORS: dict[str, str] = {
    "forensic": "#2563eb",
    "quarantine": "#dc2626",
    "conservation": "#16a34a",
    "property": "#9333ea",
    "biotech_ip": "#ea580c",
    "food": "#f59e0b",
    "welfare": "#db2777",
    "public_health": "#0891b2",
    "warfare": "#475569",
}

ANCHOR_COLORS: dict[str, str] = {
    "witness": ROLE_COLORS["witness"],
    "threat": ROLE_COLORS["threat"],
    "protected": ROLE_COLORS["protected"],
    "property": ROLE_COLORS["property"],
    "invention": ROLE_COLORS["invention"],
    "defendant": ROLE_COLORS["defendant"],
    "welfare": ROLE_COLORS["moral_patient"],
    "weapon": ROLE_COLORS["weapon"],
    "interconnections": "#334155",
}


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.patch.set_facecolor("white")
    fig.savefig(path, dpi=_DPI, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)
    return path


def _role_label(slug: str) -> str:
    return roles.find(slug).title


def _wrap_label(label: str, width: int = 18) -> str:
    return "\n".join(textwrap.wrap(label.replace("_", " "), width=width))


def _style_axes(ax: plt.Axes, *, grid_axis: str = "x") -> None:
    ax.set_facecolor(_PANEL)
    ax.tick_params(colors=_MUTED, labelsize=8)
    ax.xaxis.label.set_color(_MUTED)
    ax.yaxis.label.set_color(_MUTED)
    ax.title.set_color(_INK)
    ax.title.set_fontweight("bold")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#cbd5e1")
    ax.grid(axis=grid_axis, color=_GRID, linestyle="-", linewidth=0.6, alpha=0.65)
    ax.set_axisbelow(True)


def _annotate_bars(ax: plt.Axes, values: list[int], *, horizontal: bool) -> None:
    for i, value in enumerate(values):
        if horizontal:
            ax.annotate(
                str(value),
                (value, i),
                textcoords="offset points",
                xytext=(5, 0),
                va="center",
                ha="left",
                fontsize=8,
                color=_INK,
            )
        else:
            ax.annotate(
                str(value),
                (i, value),
                textcoords="offset points",
                xytext=(0, 4),
                ha="center",
                fontsize=8,
                color=_INK,
            )
