#!/usr/bin/env python3
"""Fetch declared CourtListener opinion-search queries into the response cache.

The only network-touching script in the case-candidate pair. It loads
``config/case_candidate_queries.yaml`` (via :mod:`src.case_candidates`) and,
for each query not already cached (or every query with ``--force``), performs
exactly one CourtListener Search API request through the engine's own
:mod:`legal_informatics.courtlistener_client` and
:mod:`legal_informatics.courtlistener_search` modules -- this script builds no
HTTP request of its own. Each response is written, unmodified in shape, to
``data/courtlistener_cache/<query_id>.json``.

Without ``--network`` nothing is fetched: the script only lists what it would
fetch and how many requests that is, so a caller can check the count against
a rate budget before spending it.

The credential (``COURTLISTENER_API_KEY`` by default, named by the engine's
own ``config/courtlistener.yaml``) is read from the environment at request
time by the engine client and travels on the wire only -- this script never
reads, prints, or writes it.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENGINE_ROOT = _PROJECT_ROOT.parent / "legal_informatics"
_ENGINE_SRC = _ENGINE_ROOT / "src"
for _p in (_PROJECT_ROOT, _PROJECT_ROOT / "src", _ENGINE_SRC):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from legal_informatics.courtlistener_client import (  # noqa: E402
    CourtListenerError,
    CourtListenerRequestError,
    load_courtlistener_config,
)
from legal_informatics.courtlistener_search import (  # noqa: E402
    build_search_query,
    fetch_search_page,
)
from src.case_candidates import (  # noqa: E402
    CaseCandidateError,
    CandidateQuery,
    build_cache_payload,
    load_query_registry,
)

CACHE_DIR_RELPATH = Path("data") / "courtlistener_cache"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=_PROJECT_ROOT, help="EntoLaw project root")
    parser.add_argument(
        "--engine-root",
        type=Path,
        default=_ENGINE_ROOT,
        help="legal_informatics engine root (holds config/courtlistener.yaml)",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="QUERY_ID",
        help="fetch only this query_id (repeatable); default: every query missing a cache file",
    )
    parser.add_argument("--force", action="store_true", help="refetch even a query that is already cached")
    parser.add_argument(
        "--network",
        action="store_true",
        help="perform the live requests; without this flag nothing is fetched",
    )
    return parser


def _pending(queries: tuple[CandidateQuery, ...], cache_dir: Path, only: list[str], force: bool) -> list[CandidateQuery]:
    selected = [q for q in queries if not only or q.query_id in only]
    if force:
        return selected
    return [q for q in selected if not (cache_dir / f"{q.query_id}.json").is_file()]


def main() -> int:
    """List or perform the pending fetches; return non-zero on error."""
    args = build_parser().parse_args()
    root = args.project_root.resolve()
    engine_root = args.engine_root.resolve()
    cache_dir = root / CACHE_DIR_RELPATH

    try:
        queries = load_query_registry(root)
    except CaseCandidateError as exc:
        print(f"query registry error: {exc}", file=sys.stderr)
        return 2

    pending = _pending(queries, cache_dir, args.only, args.force)
    if not pending:
        print("nothing to fetch: every declared query is already cached (use --force to refetch)")
        return 0

    if not args.network:
        print(f"{len(pending)} query/queries would be fetched (1 request each; pass --network to fetch):")
        for query in pending:
            print(f"  {query.query_id}: {query.text!r} (issue: {query.issue_id})")
        return 0

    try:
        config = load_courtlistener_config(engine_root / "config" / "courtlistener.yaml")
    except CourtListenerError as exc:
        print(f"cannot load the engine's CourtListener registry: {exc}", file=sys.stderr)
        return 2

    cache_dir.mkdir(parents=True, exist_ok=True)
    fetched = 0
    for query in pending:
        try:
            search_query = build_search_query(
                config.base_url,
                query.text,
                search_type=query.search_type,
                stat_toggles={"published": True},
            )
            page = fetch_search_page(config, search_query, api_key_env=config.api_key_env)
        except CourtListenerRequestError as exc:
            status = f" HTTP {exc.http_status}" if exc.http_status is not None else ""
            print(f"fetch failed for {query.query_id} ({exc.failure_kind}{status}): {exc}", file=sys.stderr)
            if exc.retry_after is not None:
                print(f"provider backoff: Retry-After {exc.retry_after:g}s", file=sys.stderr)
            if exc.wait_until is not None:
                print(f"provider backoff: wait_until {exc.wait_until}", file=sys.stderr)
            print(f"stopping after {fetched} successful fetch(es); {len(pending) - fetched} query/queries not attempted", file=sys.stderr)
            return 2
        except CourtListenerError as exc:
            print(f"fetch failed for {query.query_id}: {exc}", file=sys.stderr)
            return 2

        fetched_at = datetime.now(timezone.utc).isoformat()
        payload = build_cache_payload(query, page, fetched_at)
        cache_path = cache_dir / f"{query.query_id}.json"
        cache_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        fetched += 1
        print(
            f"fetched {query.query_id}: {len(payload['results'])} result(s) of "
            f"{'~' if payload['approximate'] else ''}{payload['hit_count']} -> {cache_path}"
        )

    print(f"fetched {fetched} of {len(pending)} pending query/queries ({len(queries)} declared total)")
    print("re-run scripts/generate_case_candidates.py to rebuild data/case_candidates.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
