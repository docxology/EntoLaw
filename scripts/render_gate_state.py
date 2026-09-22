#!/usr/bin/env python3
"""Run the gates declared in ``config/gate_state.yaml`` and write their results into TODO.md.

The gate-state block at the top of `TODO.md` used to be typed by hand: a human
ran the gates, read the counts off the terminal, and transcribed them under a
sentence asserting that every number came from that one session. The counts went
stale, the sentence did not, and three independent reviews caught the same
defect in two checkouts. Measured counts live in their generators; this is the
generator for that block.

Each declared gate is run as a real subprocess in the project root, and the
result column is text that command printed, matched by the `expect` patterns
declared beside it. A gate that exits non-zero, times out, or prints nothing a
pattern matches is rendered `FAILING` and makes this script exit 1 -- the block
reports the run it had, not the run it wanted.

``--check`` re-runs every gate and compares the fresh block against the one
committed in `TODO.md`, exiting non-zero on any difference and writing nothing.
That is only meaningful because the block is a pure function of the tree: it
carries no timestamp and no wall-clock duration, so an unchanged tree renders
byte-identically. `src/gate_state.py` documents that decision and what replaces
the date the old block carried.

Running the gates is as slow as the gates are; on a tree whose declaration
includes the full test suite this takes tens of minutes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from legal_informatics.gate_state import (
    GATE_STATE_CONFIG,
    GATE_STATE_DOCUMENT,
    GateStateError,
    load_gate_declarations,
    read_gate_state,
    render_gate_state,
    run_gates,
    write_gate_state,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the gate-state renderer."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT, help="project root directory")
    parser.add_argument(
        "--check",
        action="store_true",
        help="re-run the gates and verify the committed block matches, without rewriting it",
    )
    return parser


def main() -> int:
    """Render or verify the block; return non-zero on a failing gate or on drift."""
    args = build_parser().parse_args()
    root = args.project_root.resolve()

    try:
        gates = load_gate_declarations(root / GATE_STATE_CONFIG)
        results = run_gates(gates, root)
        block = render_gate_state(results)
        if args.check:
            committed = read_gate_state(root)
            if committed != block:
                print(
                    f"{GATE_STATE_DOCUMENT} gate state is stale; "
                    "run without --check to regenerate",
                    file=sys.stderr,
                )
                return 1
            print(f"gate state current: {GATE_STATE_DOCUMENT}")
        else:
            print(write_gate_state(root, block))
    except GateStateError as exc:
        print(f"gate state error: {exc}", file=sys.stderr)
        return 2

    failing = [result.command for result in results if not result.passed]
    for command in failing:
        print(f"FAILING gate: {command}", file=sys.stderr)
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
