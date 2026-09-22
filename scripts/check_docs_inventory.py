#!/usr/bin/env python3
"""Regenerate the project inventory and fail closed on any unportable doc link.

Three findings gate the exit code, and each prints its own diagnostic: a
*broken* link does not resolve on this machine, an *escaping* link resolves
outside the project root, and an *absolute* link is written as one machine's
filesystem path. The last two are portability defects that can be green on the
machine that wrote them and dead on the next checkout, so they fail the gate
without the filesystem being consulted at all.

The inventory is deterministic for a fixed tree, so running it twice without
changing anything rewrites the same bytes. That makes it safe to run in the
pipeline and meaningful to diff.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from legal_informatics.inventory import build_inventory
from legal_informatics.privacy_labels import render_labelled_json, write_labelled_json

INVENTORY_PATH = "output/data/project_inventory.json"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the inventory check."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT, help="project root directory")
    parser.add_argument("--output", type=Path, default=None, help="inventory path override")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the written inventory matches the tree without rewriting it",
    )
    return parser


def main() -> int:
    """Write or verify the inventory; return non-zero on drift or any link finding."""
    args = build_parser().parse_args()
    project_root = args.project_root.resolve()
    inventory = build_inventory(project_root)
    # The inventory declares its posture at write time, keyed by its canonical
    # path family; the check compares the on-disk file against exactly the
    # bytes the writer would produce now, privacy block included.
    rendered = render_labelled_json(project_root, INVENTORY_PATH, inventory, sort_keys=True)
    output = args.output or project_root / INVENTORY_PATH

    if args.check:
        if not output.is_file():
            print(f"inventory missing: {output.relative_to(project_root)}", file=sys.stderr)
            return 1
        if output.read_text(encoding="utf-8") != rendered:
            print("inventory is stale; run without --check to regenerate", file=sys.stderr)
            return 1
    else:
        written = write_labelled_json(project_root, INVENTORY_PATH, inventory, sort_keys=True)
        if output != written:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")

    for finding in inventory["broken_links"]:
        print(f"broken link: {finding}", file=sys.stderr)
    for finding in inventory["escaping_links"]:
        print(
            f"escaping link: {finding} -- resolves outside the project root, so it "
            "depends on what sits beside this checkout; point it inside the project "
            "or write it as a full URL",
            file=sys.stderr,
        )
    for finding in inventory["absolute_links"]:
        print(
            f"absolute link: {finding} -- names one machine's filesystem path, so it "
            "dies on every other checkout; rewrite it relative to the document or as "
            "a full URL",
            file=sys.stderr,
        )

    surfaces = inventory["surfaces"]
    summary = ", ".join(f"{name} {value['count']}" for name, value in sorted(surfaces.items()))
    print(f"inventory {inventory['status']}: {summary}")
    print(f"markdown files checked: {inventory['markdown_files_checked']}")
    return 0 if inventory["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
