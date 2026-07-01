"""Shared fixtures for the EntoLaw suite."""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project_root() -> Path:
    """Return the EntoLaw project root."""
    return PROJECT_ROOT
