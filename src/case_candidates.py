"""CourtListener case-CANDIDATE register: load, build, render, check.

A candidate is a CourtListener opinion-search hit surfaced by one of the
declared queries in ``config/case_candidate_queries.yaml`` -- nothing about it
has been read, weighed, or admitted. Every row this module emits carries
``status: "candidate"`` and nothing this module does can change that value:
there is no function here that writes ``"verified"``. Promoting a candidate
into a real claim (a ``src/case_records.py`` entry, or a
``references.bib`` + ``data/claim_ledger.yaml`` pair) is a human decision made
elsewhere, after reading the opinion -- see ``docs/CASE_CANDIDATES.md``.

Two data sources, both offline:

* ``config/case_candidate_queries.yaml`` -- the declared query registry
  (:func:`load_query_registry`).
* ``data/courtlistener_cache/<query_id>.json`` -- one recorded CourtListener
  Search API response per query, written by
  ``scripts/fetch_case_candidate_queries.py`` (the only network-touching
  script in this pair). Nothing in this module opens a socket.

:func:`build_candidate_register` combines them deterministically: the same
queries plus the same cached responses always produce the same register, byte
for byte via :func:`render_candidate_register`. That determinism is what lets
``scripts/generate_case_candidates.py --check`` detect drift between
``data/case_candidates.yaml`` and its declared inputs without re-fetching
anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml  # type: ignore[import-untyped]

#: The one status value a candidate row may carry. Never "verified" -- that
#: word does not appear as a value anywhere in this module.
STATUS_CANDIDATE = "candidate"

QUERY_REGISTRY_RELPATH = Path("config") / "case_candidate_queries.yaml"
CACHE_DIR_RELPATH = Path("data") / "courtlistener_cache"
REGISTER_RELPATH = Path("data") / "case_candidates.yaml"

SCHEMA_VERSION = "1.0"
GENERATOR = "scripts.generate_case_candidates"
REVIEW_STATUS = "candidate_register"
BOUNDARY = (
    "Every row here is status: candidate -- a CourtListener opinion-search hit "
    "surfaced by a query, not a reviewed legal authority. This register is "
    "generated (see `generator`) from `config/case_candidate_queries.yaml` and "
    "the recorded responses in `data/courtlistener_cache/`; it never feeds the "
    "manuscript, `references.bib`, or `data/claim_ledger.yaml`. Promoting a "
    "candidate into a claim is a human decision -- it requires reading the "
    "opinion, then adding it to `src/case_records.py` (or the claim ledger) "
    "with its own citation and verification. See `docs/CASE_CANDIDATES.md`."
)


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


@dataclass(frozen=True)
class CaseCandidate:
    """One deduplicated candidate row: a case surfaced by one or more queries."""

    candidate_id: str
    cluster_id: str | None
    case_name: str | None
    court: str | None
    date_filed: str | None
    url: str | None
    query_ids: tuple[str, ...]
    issue_ids: tuple[str, ...]
    status: str = STATUS_CANDIDATE

    def __post_init__(self) -> None:
        if self.status != STATUS_CANDIDATE:
            raise CaseCandidateError(
                f"candidate {self.candidate_id!r} carries status {self.status!r}; "
                f"only {STATUS_CANDIDATE!r} is a valid candidate status"
            )


@dataclass(frozen=True)
class QuerySummary:
    """One row of the register's ``queries`` section: a query and its outcome."""

    query_id: str
    text: str
    search_type: str
    issue_id: str
    hit_count: int | None
    approximate: bool
    fetched_at: str
    cache_file: str


@dataclass(frozen=True)
class CandidateRegister:
    """The full, deterministic content of ``data/case_candidates.yaml``."""

    schema_version: str
    generator: str
    review_status: str
    boundary: str
    queries: tuple[QuerySummary, ...]
    candidates: tuple[CaseCandidate, ...]


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


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


def load_cached_response(project_root: Path, query: CandidateQuery) -> CachedQueryResponse:
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
    results = tuple(_load_cached_result(row, path) for row in payload.get("results") or [])
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


def _candidate_key(result: CachedResult) -> str:
    """A stable dedup/sort key: the cluster id, or a fallback derived from the case.

    ``cluster_id`` is the provider's own stable identifier and is present on
    essentially every real opinion hit; the fallback exists only so a result
    the provider ever returns without one still produces a deterministic,
    non-colliding key rather than being silently dropped.
    """
    if result.cluster_id:
        return f"cl-{result.cluster_id}"
    basis = "|".join((result.case_name or "", result.court or "", result.date_filed or ""))
    import hashlib

    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    return f"nc-{digest}"


def build_candidate_register(
    queries: tuple[CandidateQuery, ...],
    responses: tuple[CachedQueryResponse, ...],
) -> CandidateRegister:
    """Build the deterministic register from declared queries and cached responses.

    Args:
        queries: Declared queries, in file order.
        responses: One cached response per query, same order and length as
            ``queries`` (see :func:`load_all_cached_responses`).

    Returns:
        The full register: a query-outcome summary, and a candidates list
        deduplicated by :func:`_candidate_key` with every surfacing query id
        and mapped issue id merged in, sorted by candidate id for a stable
        byte-for-byte rendering.

    Raises:
        CaseCandidateError: If ``queries`` and ``responses`` disagree in
            length or order.
    """
    if len(queries) != len(responses) or any(q.query_id != r.query_id for q, r in zip(queries, responses)):
        raise CaseCandidateError("queries and responses must be the same length and order")

    query_by_id = {q.query_id: q for q in queries}
    summaries = tuple(
        QuerySummary(
            query_id=r.query_id,
            text=r.text,
            search_type=r.search_type,
            issue_id=query_by_id[r.query_id].issue_id,
            hit_count=r.hit_count,
            approximate=r.approximate,
            fetched_at=r.fetched_at,
            cache_file=str(CACHE_DIR_RELPATH / f"{r.query_id}.json"),
        )
        for r in responses
    )

    merged: dict[str, CaseCandidate] = {}
    for response in responses:
        query = query_by_id[response.query_id]
        for result in response.results:
            key = _candidate_key(result)
            existing = merged.get(key)
            if existing is None:
                merged[key] = CaseCandidate(
                    candidate_id=key,
                    cluster_id=result.cluster_id,
                    case_name=result.case_name,
                    court=result.court,
                    date_filed=result.date_filed,
                    url=result.absolute_url,
                    query_ids=(query.query_id,),
                    issue_ids=(query.issue_id,),
                )
            else:
                merged[key] = CaseCandidate(
                    candidate_id=key,
                    cluster_id=existing.cluster_id or result.cluster_id,
                    case_name=existing.case_name or result.case_name,
                    court=existing.court or result.court,
                    date_filed=existing.date_filed or result.date_filed,
                    url=existing.url or result.absolute_url,
                    query_ids=_merge_sorted(existing.query_ids, (query.query_id,)),
                    issue_ids=_merge_sorted(existing.issue_ids, (query.issue_id,)),
                )
    candidates = tuple(merged[key] for key in sorted(merged))
    return CandidateRegister(
        schema_version=SCHEMA_VERSION,
        generator=GENERATOR,
        review_status=REVIEW_STATUS,
        boundary=BOUNDARY,
        queries=summaries,
        candidates=candidates,
    )


def _merge_sorted(existing: tuple[str, ...], new: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(existing) | set(new)))


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


def _register_payload(register: CandidateRegister) -> dict[str, Any]:
    return {
        "schema_version": register.schema_version,
        "generator": register.generator,
        "review_status": register.review_status,
        "boundary": register.boundary,
        "queries": [
            {
                "query_id": q.query_id,
                "text": q.text,
                "search_type": q.search_type,
                "issue_id": q.issue_id,
                "hit_count": q.hit_count,
                "approximate": q.approximate,
                "fetched_at": q.fetched_at,
                "cache_file": q.cache_file,
            }
            for q in register.queries
        ],
        "candidates": [
            {
                "candidate_id": c.candidate_id,
                "cluster_id": c.cluster_id,
                "case_name": c.case_name,
                "court": c.court,
                "date_filed": c.date_filed,
                "url": c.url,
                "query_ids": list(c.query_ids),
                "issue_ids": list(c.issue_ids),
                "status": c.status,
            }
            for c in register.candidates
        ],
    }


def render_candidate_register(register: CandidateRegister) -> str:
    """Render the register to deterministic YAML text.

    Field order is fixed by :func:`_register_payload` (``sort_keys=False``),
    so the same register always renders to the same bytes -- what
    ``scripts/generate_case_candidates.py --check`` diffs against.
    """
    return yaml.safe_dump(
        _register_payload(register),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


def write_candidate_register(project_root: Path, register: CandidateRegister) -> Path:
    """Write the rendered register to ``data/case_candidates.yaml``; return its path."""
    path = project_root / REGISTER_RELPATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_candidate_register(register), encoding="utf-8")
    return path


def generate_register(project_root: Path) -> CandidateRegister:
    """Load every declared input and build the register; no I/O to ``data/case_candidates.yaml``."""
    queries = load_query_registry(project_root)
    responses = load_all_cached_responses(project_root, queries)
    return build_candidate_register(queries, responses)


def check_register(project_root: Path) -> list[str]:
    """Compare the on-disk register against what the declared inputs would produce now.

    Returns:
        A single-item list describing the drift, or an empty list when
        ``data/case_candidates.yaml`` already matches. Mirrors the
        ``--check`` contract of ``scripts/check_module_map.py`` and
        ``scripts/check_docs_inventory.py``: nothing is rewritten here.
    """
    path = project_root / REGISTER_RELPATH
    register = generate_register(project_root)
    rendered = render_candidate_register(register)
    if not path.is_file():
        return [f"case candidate register missing: {path}; run without --check to generate it"]
    if path.read_text(encoding="utf-8") != rendered:
        return [
            f"{path} is stale relative to config/case_candidate_queries.yaml and "
            "data/courtlistener_cache/; run without --check to regenerate"
        ]
    return []


# --------------------------------------------------------------------------
# Cache-payload shaping (used by the network-touching fetch script)
# --------------------------------------------------------------------------


def build_cache_payload(query: CandidateQuery, page: Any, fetched_at: str) -> dict[str, Any]:
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
