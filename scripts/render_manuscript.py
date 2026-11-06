# /// script
# requires-python = ">=3.15"
# ///
"""Render the declared manuscript locally; no release, upload or DOI operation.

How to run: .venv/bin/python scripts/render_manuscript.py
"""
from pathlib import Path

from legal_informatics.manuscript_render import render


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    receipt = render(root)
    if receipt["status"] != "rendered":
        raise RuntimeError("actual local manuscript rendering requires the declared template")
    print(root / "output/data/manuscript_render_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
