#!/usr/bin/env python3
"""Render all manuscript figures (matplotlib PNGs) for EntoLaw.

Thin orchestrator: all figure logic lives in :mod:`src.viz` (renderers and
the caption→renderer binding) and :mod:`legal_informatics.figure_bundle`
(the build pipeline). Prints each written path for manifest collection.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
for _p in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from src.viz import build_figures  # noqa: E402


def main(project_root: Path = PROJECT_ROOT) -> list[Path]:
    figures_dir = project_root / "output" / "figures"
    paths = list(build_figures(figures_dir))
    for path in paths:
        print(path)
    return paths


if __name__ == "__main__":
    main()
