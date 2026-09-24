"""CourtListener case-CANDIDATE register: load, build, render, check.

A candidate is a CourtListener opinion-search hit surfaced by one of the
declared queries in ``config/case_candidate_queries.yaml`` -- nothing about it
has been read, weighed, or admitted. Every row this module emits carries
``status: "candidate"`` and nothing this module does can change that value:
there is no function here that writes ``"verified"``. Promoting a candidate
into a real claim (a ``src/case_records.py`` entry, or a
``references.bib`` + ``data/claim_ledger.yaml`` pair) is a human decision made
elsewhere, after reading the opinion -- see ``docs/CASE_CANDIDATES.md``.

Its inputs (the query registry and the recorded responses) are read by
:mod:`src.case_candidate_cache`, whose public names are re-exported here.
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
from typing import Any

import yaml  # type: ignore[import-untyped]

from src.case_candidate_cache import (  # noqa: F401 - re-exported public names
    CACHE_DIR_RELPATH,
    QUERY_REGISTRY_RELPATH,
    CachedQueryResponse,
    CachedResult,
    CandidateQuery,
    CaseCandidateError,
    _cache_path,
    _candidate_key,
    _int_or_none,
    _load_cached_result,
    _str_or_none,
    build_cache_payload,
    known_issue_ids,
    load_all_cached_responses,
    load_cached_response,
    load_query_registry,
)

#: The one status value a candidate row may carry. Never "verified" -- that
#: word does not appear as a value anywhere in this module.
STATUS_CANDIDATE = "candidate"

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
    if len(queries) != len(responses) or any(
        q.query_id != r.query_id for q, r in zip(queries, responses)
    ):
        raise CaseCandidateError(
            "queries and responses must be the same length and order"
        )

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
        return [
            f"case candidate register missing: {path}; run without --check to generate it"
        ]
    if path.read_text(encoding="utf-8") != rendered:
        return [
            f"{path} is stale relative to config/case_candidate_queries.yaml and "
            "data/courtlistener_cache/; run without --check to regenerate"
        ]
    return []


# --------------------------------------------------------------------------
# Cache-payload shaping (used by the network-touching fetch script)
# --------------------------------------------------------------------------
