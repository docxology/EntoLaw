"""Cache I/O and shared record types for the CourtListener case-candidate register.

Split from :mod:`src.case_candidates` for the publication size gate. This half
owns everything that touches the recorded responses and the query registry --
the declared queries (``config/case_candidate_queries.yaml``), the per-query
cache files (``data/courtlistener_cache/<query_id>.json``), and the record
types they parse into. :mod:`src.case_candidates` builds, renders and checks
the register from these and re-exports every public name here, so callers
keep importing from ``src.case_candidates``. Nothing here opens a socket.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml  # type: ignore[import-untyped]

QUERY_REGISTRY_RELPATH = Path("config") / "case_candidate_queries.yaml"
CACHE_DIR_RELPATH = Path("data") / "courtlistener_cache"


class CaseCandidateError(ValueError):
    """Raised when the query registry, a cache file, or the register is malformed."""


@dataclass(frozen=True)
class CandidateQuery:
    """One declared query from ``config/case_candidate_queries.yaml``."""

    query_id: str
    text: str
    search_type: str
    issue_id: str
    note: str


@dataclass(frozen=True)
class CachedResult:
    """One normalized search-result row read back from a cache file."""

    cluster_id: str | None
    case_name: str | None
    court: str | None
    date_filed: str | None
    absolute_url: str | None
    docket_number: str | None
    citations: tuple[str, ...]


@dataclass(frozen=True)
class CachedQueryResponse:
    """One recorded CourtListener response, as written to the cache file."""

    query_id: str
    text: str
    search_type: str
    fetched_at: str
    hit_count: int | None
    approximate: bool
    results: tuple[CachedResult, ...]


def load_query_registry(project_root: Path) -> tuple[CandidateQuery, ...]:
    """Load and validate ``config/case_candidate_queries.yaml``.

    Args:
        project_root: This project's root directory.

    Returns:
        Every declared query, in file order.

    Raises:
        CaseCandidateError: If the file is missing, malformed, declares a
            duplicate ``query_id``, or a required field is missing/empty.
    """
    path = project_root / QUERY_REGISTRY_RELPATH
    if not path.is_file():
        raise CaseCandidateError(f"query registry not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, Mapping):
        raise CaseCandidateError(f"{path}: registry must be a mapping")
    rows = payload.get("queries")
    if not isinstance(rows, list) or not rows:
        raise CaseCandidateError(f"{path}: registry declares no queries")
    queries: list[CandidateQuery] = []
    seen: set[str] = set()
    for index, raw in enumerate(rows):
        if not isinstance(raw, Mapping):
            raise CaseCandidateError(f"{path}: query at index {index} is not a mapping")
        query_id = str(raw.get("query_id") or "").strip()
        text = str(raw.get("text") or "").strip()
        search_type = str(raw.get("search_type") or "").strip()
        issue_id = str(raw.get("issue_id") or "").strip()
        if not query_id or not text or not search_type or not issue_id:
            raise CaseCandidateError(
                f"{path}: query at index {index} is missing one of "
                "query_id/text/search_type/issue_id"
            )
        if query_id in seen:
            raise CaseCandidateError(f"{path}: query_id {query_id!r} declared twice")
        seen.add(query_id)
        queries.append(
            CandidateQuery(
                query_id=query_id,
                text=text,
                search_type=search_type,
                issue_id=issue_id,
                note=str(raw.get("note") or "").strip(),
            )
        )
    return tuple(queries)


def _cache_path(project_root: Path, query_id: str) -> Path:
    return project_root / CACHE_DIR_RELPATH / f"{query_id}.json"


def load_cached_response(
    project_root: Path, query: CandidateQuery
) -> CachedQueryResponse:
    """Load one recorded response for ``query`` from ``data/courtlistener_cache/``.

    Args:
        project_root: This project's root directory.
        query: The declared query the cache file must match.

    Returns:
        The cached response.

    Raises:
        CaseCandidateError: If the cache file is missing, malformed, or its
            recorded ``query_id``/``text`` disagrees with the declared query
            (a stale cache from a prior, differently-worded query).
    """
    import json

    path = _cache_path(project_root, query.query_id)
    if not path.is_file():
        raise CaseCandidateError(
            f"no cached response for query {query.query_id!r} at {path}; run "
            "scripts/fetch_case_candidate_queries.py --network first"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CaseCandidateError(f"cache file {path} is not valid JSON: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise CaseCandidateError(f"{path}: cache file must contain a JSON object")
    if str(payload.get("query_id") or "") != query.query_id:
        raise CaseCandidateError(
            f"{path}: cache file's query_id {payload.get('query_id')!r} does not match "
            f"the declared query {query.query_id!r}"
        )
    if str(payload.get("text") or "") != query.text:
        raise CaseCandidateError(
            f"{path}: cache file's recorded query text disagrees with "
            f"config/case_candidate_queries.yaml for {query.query_id!r} -- the query "
            "text changed since this response was fetched; re-run "
            "scripts/fetch_case_candidate_queries.py --network"
        )
    results = tuple(
        _load_cached_result(row, path) for row in payload.get("results") or []
    )
    return CachedQueryResponse(
        query_id=query.query_id,
        text=query.text,
        search_type=str(payload.get("search_type") or query.search_type),
        fetched_at=str(payload.get("fetched_at") or ""),
        hit_count=_int_or_none(payload.get("hit_count")),
        approximate=bool(payload.get("approximate", False)),
        results=results,
    )


def _load_cached_result(raw: Any, path: Path) -> CachedResult:
    if not isinstance(raw, Mapping):
        raise CaseCandidateError(f"{path}: a cached result is not a mapping")
    citations = raw.get("citations") or ()
    if isinstance(citations, str):
        citations = (citations,)
    return CachedResult(
        cluster_id=_str_or_none(raw.get("cluster_id")),
        case_name=_str_or_none(raw.get("case_name")),
        court=_str_or_none(raw.get("court")),
        date_filed=_str_or_none(raw.get("date_filed")),
        absolute_url=_str_or_none(raw.get("absolute_url")),
        docket_number=_str_or_none(raw.get("docket_number")),
        citations=tuple(str(c) for c in citations),
    )


def load_all_cached_responses(
    project_root: Path, queries: tuple[CandidateQuery, ...]
) -> tuple[CachedQueryResponse, ...]:
    """Load every query's cached response, in declared order."""
    return tuple(load_cached_response(project_root, query) for query in queries)


# --------------------------------------------------------------------------
# Building
# --------------------------------------------------------------------------


def _str_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------
# Rendering / persistence
# --------------------------------------------------------------------------


def build_cache_payload(
    query: CandidateQuery, page: Any, fetched_at: str
) -> dict[str, Any]:
    """Shape one fetched CourtListener search page into a cache-file payload.

    Pure and offline: ``page`` is an already-fetched
    :class:`legal_informatics.courtlistener_search.SearchPage` (or anything
    duck-typed the same way -- ``count``, ``approximate_count``, ``results``
    with ``cluster_id``/``case_name``/``court``/``date_filed``/``absolute_url``/
    ``docket_number``/``citations`` attributes). No socket opens here; this
    only reshapes an object the caller already fetched.

    Args:
        query: The declared query the page answers.
        page: The fetched, normalized search page.
        fetched_at: An ISO-8601 UTC timestamp supplied by the caller (kept
            out of this function so it stays a pure transform of its inputs).

    Returns:
        A JSON-serializable dict, written verbatim by the fetch script to
        ``data/courtlistener_cache/<query_id>.json``.
    """
    return {
        "query_id": query.query_id,
        "text": query.text,
        "search_type": query.search_type,
        "fetched_at": fetched_at,
        "hit_count": page.count,
        "approximate": bool(page.approximate_count),
        "results": [
            {
                "cluster_id": result.cluster_id,
                "case_name": result.case_name,
                "court": result.court,
                "date_filed": result.date_filed,
                "absolute_url": result.absolute_url,
                "docket_number": result.docket_number,
                "citations": list(result.citations or ()),
            }
            for result in page.results
        ],
    }


def _candidate_key(result: CachedResult) -> str:
    """A stable dedup/sort key: the cluster id, or a fallback derived from the case.

    ``cluster_id`` is the provider's own stable identifier and is present on
    essentially every real opinion hit; the fallback exists only so a result
    the provider ever returns without one still produces a deterministic,
    non-colliding key rather than being silently dropped.
    """
    if result.cluster_id:
        return f"cl-{result.cluster_id}"
    basis = "|".join(
        (result.case_name or "", result.court or "", result.date_filed or "")
    )
    import hashlib

    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    return f"nc-{digest}"


def known_issue_ids(project_root: Path) -> frozenset[str]:
    """Every ``issue_id`` declared in ``config/legal_issues.yaml``.

    Used by tests to assert every query's ``issue_id`` maps to a real,
    declared legal issue rather than a typo.
    """
    import json

    path = project_root / "config" / "legal_issues.yaml"
    text = path.read_text(encoding="utf-8")
    # legal_issues.yaml is a JSON array written with a `.yaml` extension (see
    # its own header comment); JSON is valid YAML, but parsing it as JSON
    # here keeps this reader independent of any YAML-specific quirk.
    rows = json.loads(text[text.index("[") :])
    return frozenset(str(row["issue_id"]) for row in rows)
