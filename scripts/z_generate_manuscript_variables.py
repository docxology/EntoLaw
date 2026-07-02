#!/usr/bin/env python3
"""Thin orchestrator: generate and inject manuscript variables for rendering.

Run automatically by the render pipeline *before* PDF/HTML rendering — the
``z_`` prefix is the name the renderer's hydration step looks for. It writes
``output/data/manuscript_variables.json`` and substitutes every ``{{TOKEN}}``
marker in ``manuscript/*.md`` into ``output/manuscript/`` via the shared
injection helper.

All computation lives in :mod:`src.manuscript_variables`; all injection lives
in :mod:`infrastructure.rendering.manuscript_injection`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
# The renderer passes TEMPLATE_REPO_ROOT so ``import infrastructure`` resolves
# even when this project is a symlink (projects/working/*) whose resolved path
# lies outside the template tree.
_SEARCH_ROOTS = [_PROJECT_ROOT, _PROJECT_ROOT / "src", _PROJECT_ROOT.parent.parent]
_template_root = os.environ.get("TEMPLATE_REPO_ROOT")
if _template_root:
    _SEARCH_ROOTS.append(Path(_template_root))
for _p in _SEARCH_ROOTS:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def compute_and_save(project_root: Path) -> tuple[dict[str, str], Path]:
    """Compute registry-derived manuscript variables and persist them as JSON.

    Single source of truth for the compute-and-save step. The plain
    ``generate_manuscript_variables`` script delegates here so the JSON-only
    entry point and this injection pipeline cannot silently drift apart.
    """
    from src.manuscript_variables import generate_variables, save_variables

    variables = generate_variables(project_root)
    out_path = project_root / "output" / "data" / "manuscript_variables.json"
    save_variables(variables, out_path)
    return variables, out_path


def main() -> int:
    from infrastructure.rendering.manuscript_injection import (
        write_resolved_manuscript_tree,
    )

    variables, out_path = compute_and_save(_PROJECT_ROOT)
    write_resolved_manuscript_tree(_PROJECT_ROOT, variables)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
