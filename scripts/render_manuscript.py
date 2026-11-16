# /// script
# requires-python = ">=3.15"
# ///
"""Render the declared manuscript locally; no release, upload or DOI operation.

How to run: .venv/bin/python scripts/render_manuscript.py
"""
import os
import sys
from pathlib import Path

from legal_informatics.manuscript_render import render


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from src.manuscript_variables import build_epoch

    # Pin xelatex /CreationDate, the build stamp and every timestamp the
    # template derives from SOURCE_DATE_EPOCH, so clean rebuilds are byte-stable.
    epoch = build_epoch(root)
    if epoch is None:
        raise RuntimeError("rendering requires docs/manuscript/config.yaml with a declared paper.date")
    os.environ["SOURCE_DATE_EPOCH"] = str(epoch)
    receipt = render(root)
    if receipt["status"] != "rendered":
        raise RuntimeError("actual local manuscript rendering requires the declared template")
    print(root / "output/data/manuscript_render_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
