"""Shared output-writing helpers for the thin orchestrators in ``scripts/``.

CSV serialization lives here (importable and tested) so the scripts stay
thin: path bootstrap plus a single delegated call.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def flatten_cell(value: Any) -> Any:
    """Render list/tuple cell values as one ``"; "``-joined string."""
    if isinstance(value, (list, tuple)):
        return "; ".join(str(v) for v in value)
    return value


def write_csv(path: Path, rows: list[dict]) -> Path:
    """Write *rows* as CSV at *path*, creating parent directories first.

    An empty *rows* list produces an empty file. Multi-valued cells are
    flattened with :func:`flatten_cell`.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: flatten_cell(v) for k, v in row.items()})
    return path
