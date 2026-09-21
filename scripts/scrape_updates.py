#!/usr/bin/env python3
"""Thin orchestrator: scrape legal-update feeds via the legal_informatics engine.

All computation lives in :mod:`legal_informatics.legal_updates` (feed
registry validation, offline feed parsing, network discovery) and
:mod:`legal_informatics.legal_updates_ingestion` (idempotent ingestion of
discovered items). This script only bootstraps the path, dispatches one
mode behind argparse, prints every path it wrote, and returns an exit code.

Modes
-----
``describe``
    Load and validate the declarative feed registry, then write a
    deterministic discovery manifest skeleton (every declared feed, zero
    items). No socket opens; fully offline.
``parse``
    Offline discovery: parse local fixture bodies (one file per feed named
    ``<feed_id>.<poll_format>`` under ``--fixture-dir``) and write the
    discovery manifest. No socket opens.
``discover``
    Live discovery: poll each feed over the network (robots-gated) and write
    the discovery manifest. Explicit network opt-in.
``ingest``
    Ingest a discovery manifest into the idempotent state ledger (network
    fetch per item, robots-gated). Explicit network opt-in.

The feed registry defaults to ``config/legal_updates_feeds.yaml``; pass
``--config`` to point at any other declarative registry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENGINE_SRC = _PROJECT_ROOT.parent / "legal_informatics" / "src"
for _p in (_PROJECT_ROOT, _PROJECT_ROOT / "src", _ENGINE_SRC):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from legal_informatics.legal_updates import (  # noqa: E402
    UpdateDiscoveryError,
    build_discovery,
    discover_feed,
    load_feed_config,
    parse_feed,
    write_discovery,
)
from legal_informatics.legal_updates_ingestion import (  # noqa: E402
    STATE_FILENAME,
    UPDATE_STORE_RELPATH,
    UpdateIngestionError,
    apply_ingest,
)

DEFAULT_CONFIG_RELPATH = Path("config") / "legal_updates_feeds.yaml"
DEFAULT_MANIFEST_RELPATH = Path("output") / "data" / "legal_updates_discovery.json"

MODES = ("describe", "parse", "discover", "ingest")


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser shared by ``--help`` and every mode."""
    parser = argparse.ArgumentParser(
        prog="scrape_updates.py",
        description=(
            "Scrape legal-update feeds behind the legal_informatics engine "
            "(describe | parse | discover | ingest)."
        ),
    )
    parser.add_argument("mode", nargs="?", default="describe", choices=MODES, help="operation mode (default: describe)")
    parser.add_argument("--config", type=Path, default=_PROJECT_ROOT / DEFAULT_CONFIG_RELPATH, help="declarative feed registry YAML")
    parser.add_argument(
        "--output",
        type=Path,
        default=_PROJECT_ROOT / DEFAULT_MANIFEST_RELPATH,
        help="discovery manifest output path",
    )
    parser.add_argument("--fixture-dir", type=Path, default=None, help="directory of offline feed bodies for parse mode")
    parser.add_argument("--state", type=Path, default=None, help="ingestion state ledger override for ingest mode")
    parser.add_argument("--timeout", type=int, default=60, help="socket timeout in seconds for discover/ingest")
    return parser


def _load_items_offline(config: Path, fixture_dir: Path | None) -> list:
    """Parse one local fixture body per declared feed; strictly offline."""
    if fixture_dir is None:
        raise UpdateDiscoveryError("parse mode requires --fixture-dir with one body file per feed")
    feeds = load_feed_config(config)
    items = []
    for feed in feeds:
        body_path = fixture_dir / f"{feed.feed_id}.{feed.poll_format}"
        try:
            body = body_path.read_bytes()
        except OSError as exc:
            raise UpdateDiscoveryError(
                f"missing fixture body for feed {feed.feed_id}: expected {body_path}: {exc}"
            ) from exc
        items.extend(parse_feed(body, feed.poll_format, feed=feed))
    return items


def _write_manifest(feeds: list, items: list, output: Path) -> Path:
    """Build and persist the deterministic discovery manifest; return its path."""
    payload = build_discovery(feeds, items)
    return write_discovery(payload, output)


def _run_describe(config: Path, output: Path) -> int:
    """Validate the registry offline and write the manifest skeleton."""
    feeds = load_feed_config(config)
    written = _write_manifest(feeds, [], output)
    print(f"described {len(feeds)} feed(s) from {config}")
    print(f"wrote {written}")
    return 0


def _run_parse(config: Path, output: Path, fixture_dir: Path | None) -> int:
    """Parse offline fixture bodies and write the populated manifest."""
    feeds = load_feed_config(config)
    items = _load_items_offline(config, fixture_dir)
    written = _write_manifest(feeds, items, output)
    print(f"parsed {len(items)} update item(s) from {len(feeds)} feed(s)")
    print(f"wrote {written}")
    return 0


def _run_discover(config: Path, output: Path, timeout: int) -> int:
    """Poll each declared feed over the network and write the manifest."""
    feeds = load_feed_config(config)
    items = []
    for feed in feeds:
        items.extend(discover_feed(feed, timeout=timeout))
    written = _write_manifest(feeds, items, output)
    print(f"discovered {len(items)} update item(s) from {len(feeds)} feed(s)")
    print(f"wrote {written}")
    return 0


def _run_ingest(config: Path, output: Path, state: Path | None, timeout: int) -> int:
    """Ingest the items of a discovery manifest into the state ledger."""
    feeds = load_feed_config(config)
    try:
        manifest = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise UpdateIngestionError(f"cannot read the discovery manifest at {output}: {exc}") from exc
    items = [item for rows in manifest.get("updates", {}).values() for item in rows]
    records = apply_ingest(items, _PROJECT_ROOT, state_path=state, timeout=timeout)
    ledger = state if state is not None else _PROJECT_ROOT / UPDATE_STORE_RELPATH / STATE_FILENAME
    failed = sum(1 for record in records if record.get("status") == "failed")
    print(f"ingested {len(records)} update record(s) ({failed} failed) from {len(feeds)} declared feed(s)")
    print(f"wrote {ledger}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Dispatch one mode; convert engine errors into exit-code-1 messages."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.mode == "describe":
            return _run_describe(args.config, args.output)
        if args.mode == "parse":
            return _run_parse(args.config, args.output, args.fixture_dir)
        if args.mode == "discover":
            return _run_discover(args.config, args.output, args.timeout)
        return _run_ingest(args.config, args.output, args.state, args.timeout)
    except (UpdateDiscoveryError, UpdateIngestionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
