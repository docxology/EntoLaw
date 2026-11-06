"""Check the declared local research resources without changing them."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from legal_informatics.analysis_models import AnalysisError
from legal_informatics.research_integrity import validate_research_project


def main(argv: list[str] | None = None) -> int:
    """Run the explicitly selected local or owner-held research profile."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--declaration", type=Path)
    parser.add_argument("--include-retained", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = validate_research_project(args.project_root, args.declaration, include_retained=args.include_retained)
    except (AnalysisError, OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) if args.json
          else f"Research integrity: passed ({result['profile']}); external sources were not reverified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
