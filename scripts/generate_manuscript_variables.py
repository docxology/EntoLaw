#!/usr/bin/env python3
"""Generate manuscript variables and persist them as JSON."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
for _p in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from src.manuscript_variables import generate_variables, save_variables  # noqa: E402


def main(project_root: Path = PROJECT_ROOT) -> Path:
    variables = generate_variables(project_root)
    path = project_root / "output" / "data" / "manuscript_variables.json"
    save_variables(variables, path)
    print(path)
    return path


if __name__ == "__main__":
    main()
