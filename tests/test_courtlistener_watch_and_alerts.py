"""Offline validation of this project's CourtListener watch and alert registries.

Both `config/courtlistener_watch.yaml` and `config/courtlistener_alerts.yaml`
are read here through the engine's own validators
(`legal_informatics.courtlistener_watch.load_watchlist` and
`legal_informatics.courtlistener_alert_sync.load_alert_registry`) — never a
project-local re-parse of the YAML shape — so a malformed row (a typo'd
field, an unbalanced query, an unknown search type, a duplicate id) fails
this suite before it ever reaches a script or a socket. No network access:
loading and validating either registry is offline by construction.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from legal_informatics.courtlistener_alert_sync import (
    ALERT_KINDS,
    load_alert_registry,
)
from legal_informatics.courtlistener_search import validate_query_operators
from legal_informatics.courtlistener_watch import WATCH_TYPES, load_watchlist

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WATCHLIST_PATH = PROJECT_ROOT / "config" / "courtlistener_watch.yaml"
ALERTS_PATH = PROJECT_ROOT / "config" / "courtlistener_alerts.yaml"
LEGAL_ISSUES_PATH = PROJECT_ROOT / "config" / "legal_issues.yaml"


def _known_issue_ids() -> set[str]:
    entries = yaml.safe_load(LEGAL_ISSUES_PATH.read_text(encoding="utf-8"))
    return {entry["issue_id"] for entry in entries}


def test_watchlist_loads_and_declares_at_least_one_watch():
    watches = load_watchlist(WATCHLIST_PATH)
    assert len(watches) >= 1
    ids = [watch.watch_id for watch in watches]
    assert len(ids) == len(set(ids)), f"duplicate watch ids: {ids}"
    for watch in watches:
        assert watch.search_type in WATCH_TYPES
        assert watch.q.strip(), f"watch {watch.watch_id!r} has a blank query"
        assert watch.purpose and watch.purpose.strip(), (
            f"watch {watch.watch_id!r} declares no purpose; every entry must state one "
            "(see docs/COURTLISTENER_WATCH.md)"
        )
        # The loader already runs this on load; asserted again here so the
        # requirement is visible from this test alone.
        validate_query_operators(watch.q)


def test_every_watch_purpose_names_a_legal_issue_this_project_actually_declares():
    """Every watch is a recurring counterpart of a declared legal issue, never a free-floating query."""
    known = _known_issue_ids()
    watches = load_watchlist(WATCHLIST_PATH)
    for watch in watches:
        matched = [issue_id for issue_id in known if issue_id in (watch.purpose or "")]
        assert matched, (
            f"watch {watch.watch_id!r}'s purpose names no known config/legal_issues.yaml "
            f"issue_id; known ids: {sorted(known)}"
        )


def test_alert_registry_loads_and_has_no_docket_alerts():
    registry = load_alert_registry(ALERTS_PATH)
    assert registry.search_alerts
    assert registry.docket_alerts == (), (
        "this project records no specific RECAP docket id anywhere in its data or docs; "
        "a docket alert is only ever declared when one already is"
    )
    for alert in registry.declared:
        assert alert.kind in ALERT_KINDS
        assert alert.purpose and alert.purpose.strip(), (
            "an alert declares no purpose; every entry must state one (see docs/COURTLISTENER_WATCH.md)"
        )
    for alert in registry.search_alerts:
        assert alert.rate in ("rt", "dly", "wly", "mly")
        assert alert.query.strip()


def test_total_declared_alerts_stays_within_the_shared_six_alert_budget():
    """This project's own slice of the cross-project six-alert budget (see docs/COURTLISTENER_WATCH.md)."""
    registry = load_alert_registry(ALERTS_PATH)
    assert len(registry.declared) <= 3
