#!/usr/bin/env python3
"""Thin orchestrator: rebuild the case-candidate register from cached responses.

All computation lives in :mod:`src.case_candidates`. This script only
bootstraps the path, loads ``config/case_candidate_queries.yaml`` and the
recorded responses under ``data/courtlistener_cache/``, and either writes
``data/case_candidates.yaml`` or, with ``--check``, verifies it is already
current without rewriting it. No socket opens here or in
``src.case_candidates`` -- the only network-touching step is
``scripts/fetch_case_candidate_queries.py``, run separately and ahead of this
one.

Every row this writes carries ``status: candidate``. This script has no path
that promotes a candidate into ``src/case_records.py``, ``references.bib``, or
``data/claim_ledger.yaml`` -- see ``docs/CASE_CANDIDATES.md``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
for _p in (_PROJECT_ROOT, _PROJECT_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from src.case_candidates import (  # noqa: E402
    CaseCandidateError,
    check_register,
    generate_register,
    write_candidate_register,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=_PROJECT_ROOT, help="project root directory")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify data/case_candidates.yaml matches its declared inputs without rewriting it",
    )
    return parser


def main() -> int:
    """Rebuild or check the register; return non-zero on error or drift."""
    args = build_parser().parse_args()
    root = args.project_root.resolve()
    try:
        if args.check:
            findings = check_register(root)
            for message in findings:
                print(f"case candidates: {message}", file=sys.stderr)
            print(f"case candidates: {len(findings)} drift finding(s)")
            return 1 if findings else 0
        register = generate_register(root)
        written = write_candidate_register(root, register)
    except CaseCandidateError as exc:
        print(f"case candidate register error: {exc}", file=sys.stderr)
        return 2
    print(
        f"wrote {written} ({len(register.candidates)} candidate(s) from "
        f"{len(register.queries)} query/queries)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
