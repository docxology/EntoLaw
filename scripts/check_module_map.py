#!/usr/bin/env python3
"""Check, or regenerate, the public-surface column of the ``src/`` module map.

``--check`` reports every module missing from ``src/AGENTS.md``, every listed
name a module no longer defines, and every imported name a row omits. ``--write``
rewrites the surface cells from the source tree and leaves the role prose alone.

The role column is never generated: it states why a module exists, and no static
analysis produces that.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from legal_informatics.module_map import (
    MODULE_MAP_PATH,
    ModuleMapError,
    check_module_map,
    imported_surface,
    rewrite_surfaces,
    source_modules,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the module-map check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT, help="project root directory")
    parser.add_argument("--write", action="store_true", help="rewrite the surface cells before reporting")
    return parser


def main() -> int:
    """Report module-map drift; return non-zero while any remains."""
    args = build_parser().parse_args()
    root = args.project_root.resolve()

    try:
        if args.write:
            path = root / MODULE_MAP_PATH
            defined = source_modules(root)
            surface = imported_surface(root, defined)
            body = rewrite_surfaces(path.read_text(encoding="utf-8"), surface, defined)
            path.write_text(body, encoding="utf-8")
            print(f"rewrote surface cells: {MODULE_MAP_PATH}")
        violations = check_module_map(root)
    except ModuleMapError as error:
        print(f"module map error: {error}", file=sys.stderr)
        return 2

    for message in violations:
        print(f"module map: {message}", file=sys.stderr)
    print(f"module map: {len(violations)} violations")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
