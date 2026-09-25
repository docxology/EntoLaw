"""Derived cross-tabs over the CourtListener case-CANDIDATE register.

Pure aggregation, nothing else: every function here reads
``data/case_candidates.yaml`` (through :mod:`src.case_candidates`) and
``config/legal_issues.yaml``, and returns counts. No function writes
anything, opens a socket, or changes a candidate's ``status`` -- that stays
``"candidate"`` all the way through, exactly as :mod:`src.case_candidates`
guarantees. Nothing here promotes a candidate to a claim; see
``docs/CASE_CANDIDATES.md`` for what promotion actually requires.

Two cross-tabs, both keyed for the figure layer (:mod:`src.viz`):

- :func:`candidates_by_issue_and_court_level` -- one row per declared legal
  issue (``config/legal_issues.yaml`` order), one column per
  :data:`COURT_LEVELS` bucket. A candidate found under more than one issue is
  counted once per issue it was found under (the register itself records
  every surfacing issue on the row), so column totals can exceed the
  register's row count; that is a property of the crosstab, not a bug.
- :func:`candidates_by_decade` -- one bucket per filing decade, from
  ``date_filed``.

Court level is derived from the court name string alone, conservatively: a
name that does not clearly say "supreme", "appeal(s)/appellate", or a known
trial-court name (district, superior, bankruptcy, common pleas) is bucketed
``"other/unknown"`` rather than guessed. Some real institutions this
misclassifies (e.g. a state's historic "Court of Appeals" acting as its
supreme court) are a known, documented limitation of a name-only rule -- see
the caveat on the figure this feeds.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import case_candidates as cc

LEGAL_ISSUES_RELPATH = Path("config") / "legal_issues.yaml"

#: Court-level buckets, in the figure's column order.
COURT_LEVELS: tuple[str, ...] = ("supreme", "appellate", "trial", "other_unknown")

#: Reader-facing label per bucket key (the underscore stays out of prose).
COURT_LEVEL_LABELS: dict[str, str] = {
    "supreme": "Supreme",
    "appellate": "Appellate",
    "trial": "Trial",
    "other_unknown": "Other/unknown",
}

_TRIAL_COURT_NAMES: tuple[str, ...] = (
    "district court",
    "superior court",
    "court of common pleas",
    "bankruptcy court",
)


def court_level(court: str | None) -> str:
    """Bucket a court name into a coarse level, conservatively.

    Checks, in order: a "supreme court" name; an "appeal"/"appellate" name
    (covers "Court of Appeals", "Court of ... Patent Appeals", "Appellate
    Court", and an "Appellate Division" naming a trial-court parent); a known
    trial-court name (district, superior, common pleas, bankruptcy). Anything
    else -- including a body that is not a court at all, like an attorney
    general's opinion reporter -- stays ``"other_unknown"``.

    Args:
        court: The candidate's recorded ``court`` string, or ``None``.

    Returns:
        One of :data:`COURT_LEVELS`.
    """
    if not court:
        return "other_unknown"
    lowered = court.lower()
    if "supreme court" in lowered:
        return "supreme"
    if "appeal" in lowered or "appellate" in lowered:
        return "appellate"
    if any(name in lowered for name in _TRIAL_COURT_NAMES):
        return "trial"
    return "other_unknown"


def _declared_issue_ids(project_root: Path) -> tuple[str, ...]:
    """Every ``issue_id`` from ``config/legal_issues.yaml``, in file order.

    Parsed the same way :func:`src.case_candidate_cache.known_issue_ids`
    parses it (the file is a JSON array written with a ``.yaml`` extension),
    but ordered rather than a frozenset, since the figure's row order should
    match the declared issue order. A project with no candidate pipeline
    declared at all -- no ``config/legal_issues.yaml`` -- resolves to no
    issues rather than raising, the same "absent means empty" convention
    :func:`src.claim_ledger.load_claims` uses for a missing
    ``data/claim_ledger.yaml``. A file that exists but is malformed still
    raises: only absence is treated as "not configured here."
    """
    path = project_root / LEGAL_ISSUES_RELPATH
    if not path.is_file():
        return ()
    text = path.read_text(encoding="utf-8")
    rows = json.loads(text[text.index("[") :])
    return tuple(str(row["issue_id"]) for row in rows)


def _register_candidates(project_root: Path) -> tuple[cc.CaseCandidate, ...]:
    """The register's candidates, or ``()`` when no candidate pipeline is
    declared for this project (no ``config/case_candidate_queries.yaml`` --
    e.g. a scratch project a test builds to exercise unrelated manuscript
    variables). A *declared but broken* registry still raises through
    :func:`src.case_candidates.generate_register`, unchanged.
    """
    if not (project_root / cc.QUERY_REGISTRY_RELPATH).is_file():
        return ()
    return cc.generate_register(project_root).candidates


def candidates_by_issue_and_court_level(
    project_root: Path,
) -> dict[str, dict[str, int]]:
    """Cross-tab: declared legal issue -> court-level bucket -> candidate count.

    Every declared issue appears as a row, including one with zero
    candidates; every :data:`COURT_LEVELS` bucket appears as a column for
    every row, including a zero cell -- callers can index the full grid
    without a ``KeyError``.

    Args:
        project_root: This project's root directory.

    Returns:
        ``{issue_id: {court_level: count}}``, issue rows in
        ``config/legal_issues.yaml`` order.
    """
    issue_ids = _declared_issue_ids(project_root)
    grid: dict[str, dict[str, int]] = {
        issue_id: {level: 0 for level in COURT_LEVELS} for issue_id in issue_ids
    }
    for candidate in _register_candidates(project_root):
        level = court_level(candidate.court)
        for issue_id in candidate.issue_ids:
            if issue_id in grid:
                grid[issue_id][level] += 1
    return grid


def _decade_label(date_filed: str | None) -> str:
    """A ``"YYYYs"`` decade label for a ``date_filed`` string, or ``"unknown"``."""
    if not date_filed or len(date_filed) < 4 or not date_filed[:4].isdigit():
        return "unknown"
    year = int(date_filed[:4])
    return f"{(year // 10) * 10}s"


def candidates_by_decade(project_root: Path) -> dict[str, int]:
    """Candidate counts by filing decade, each candidate counted once.

    Unlike the issue crosstab, a candidate contributes exactly one count here
    regardless of how many issues or queries surfaced it -- this is a
    register-wide distribution, not a per-issue one. A candidate with a
    missing or unparseable ``date_filed`` is bucketed ``"unknown"`` rather
    than dropped, so this function's total always equals the register's
    candidate count.

    Args:
        project_root: This project's root directory.

    Returns:
        ``{decade_label: count}``, e.g. ``{"1910s": 1, ..., "unknown": 0}``,
        keys sorted chronologically with ``"unknown"`` last if present.
    """
    counts: dict[str, int] = {}
    for candidate in _register_candidates(project_root):
        label = _decade_label(candidate.date_filed)
        counts[label] = counts.get(label, 0) + 1
    ordered = {k: counts[k] for k in sorted(k for k in counts if k != "unknown")}
    if "unknown" in counts:
        ordered["unknown"] = counts["unknown"]
    return ordered


def total_candidate_count(project_root: Path) -> int:
    """Total candidate rows in the register right now."""
    return len(_register_candidates(project_root))


def issue_count_with_candidates(project_root: Path) -> int:
    """Number of declared legal issues with at least one surfaced candidate."""
    grid = candidates_by_issue_and_court_level(project_root)
    return sum(1 for levels in grid.values() if sum(levels.values()) > 0)


def declared_legal_issue_count(project_root: Path) -> int:
    """Total legal issues declared in ``config/legal_issues.yaml``."""
    return len(_declared_issue_ids(project_root))


def declared_query_count(project_root: Path) -> int:
    """Total candidate queries declared in ``config/case_candidate_queries.yaml``.

    ``0`` when the file is absent (no candidate pipeline declared for this
    project); a present-but-malformed file still raises.
    """
    if not (project_root / cc.QUERY_REGISTRY_RELPATH).is_file():
        return 0
    return len(cc.load_query_registry(project_root))


__all__ = [
    "COURT_LEVELS",
    "COURT_LEVEL_LABELS",
    "candidates_by_decade",
    "candidates_by_issue_and_court_level",
    "court_level",
    "declared_legal_issue_count",
    "declared_query_count",
    "issue_count_with_candidates",
    "total_candidate_count",
]
