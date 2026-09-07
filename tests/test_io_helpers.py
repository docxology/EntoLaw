from __future__ import annotations

from src.io_helpers import flatten_cell, write_csv


def test_write_csv_writes_header_rows_and_flattens_sequences(tmp_path):
    out = write_csv(
        tmp_path / "nested" / "roles_inventory.csv",
        [
            {"slug": "defendant", "statutes": ["us-esa-9", "mbta"]},
            {"slug": "vector", "statutes": "us-aphis-quarantine"},
        ],
    )

    text = out.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0] == "slug,statutes"
    assert lines[1] == "defendant,us-esa-9; mbta"
    assert lines[2] == "vector,us-aphis-quarantine"


def test_write_csv_empty_rows_writes_empty_file(tmp_path):
    out = write_csv(tmp_path / "empty_inventory.csv", [])

    assert out.exists()
    assert out.read_text(encoding="utf-8") == ""


def test_flatten_cell_joins_sequences_and_passes_scalars_through():
    assert flatten_cell(["a", "b"]) == "a; b"
    assert flatten_cell(("a", "b")) == "a; b"
    assert flatten_cell("solo") == "solo"
    assert flatten_cell(3) == 3
