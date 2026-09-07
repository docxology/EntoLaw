#!/usr/bin/env python3
"""Generate manuscript variables and persist them as JSON."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
for _p in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from src.manuscript_variables import compute_and_save  # noqa: E402


def main(project_root: Path = PROJECT_ROOT) -> Path:
    # Delegate the compute-and-save step to src.manuscript_variables so this
    # JSON-only entry point and the render-time z_ hydrator cannot drift apart.
    # This script deliberately does NOT inject tokens into the manuscript tree.
    _variables, path = compute_and_save(project_root)
    print(path)
    return path


if __name__ == "__main__":
    main()
