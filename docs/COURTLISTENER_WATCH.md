# CourtListener watchlist and alerts

This project declares a small CourtListener watchlist
(`config/courtlistener_watch.yaml`) and alert registry
(`config/courtlistener_alerts.yaml`), read by the `legal_informatics` engine's
`courtlistener_watch` and `courtlistener_alert_sync` modules — the sibling
`legal_informatics` checkout carries the code; this project carries only the
declarative data below and the purpose each entry serves. Both surfaces are
the recurring counterpart of the one-shot fetch
[`CASE_CANDIDATES.md`](CASE_CANDIDATES.md) already documents
(`config/case_candidate_queries.yaml`, `scripts/fetch_case_candidate_queries.py`):
a candidate query answers "what does CourtListener have right now"; a watch
or alert answers "tell me when that changes."

## What each watch is for

| Watch id | Type | Legal issue | Tracks |
|---|---|---|---|
| `fifra-pesticide-opinions` | `o` (opinions) | `pesticide_registration_and_fifra` | New opinions applying FIFRA registration, labeling, or applicator compliance to a pesticide targeting insects. |
| `pollinator-esa-opinions` | `o` (opinions) | `pollinator_protection_esa` | New opinions applying the Endangered Species Act to a pollinator or insect taxon. |
| `forensic-entomology-oral-arguments` | `oa` (oral-argument audio) | `forensic_entomology_admissibility` | Oral arguments on Daubert admissibility of forensic-entomology testimony. |

Every watch's `issue_id`-equivalent purpose line names the
[`config/legal_issues.yaml`](../config/legal_issues.yaml) entry it tracks and
the [`config/case_candidate_queries.yaml`](../config/case_candidate_queries.yaml)
query it is the recurring counterpart of.

## What each alert is for

| Alert | Rate | Legal issue |
|---|---|---|
| `fifra-pesticide-registration` | weekly | `pesticide_registration_and_fifra` |
| `pollinator-esa-listing` | monthly | `pollinator_protection_esa` |
| `forensic-entomology-admissibility` | monthly | `forensic_entomology_admissibility` |

No docket alerts: no specific RECAP docket id is recorded anywhere in this
project's data or docs, and per the standing rule a docket alert is only ever
declared when one already is.

## Dry-run default

Every command below is offline and credential-free unless it carries
`--network`, `--list-live`, or `--apply`:

- Loading and validating either YAML file never opens a socket.
- Planning a watch (`build_watch_plan` / `write_watch_plan`) builds the exact
  request URL and its content hash without sending it.
- Loading and validating the alert registry never reads the live account;
  only `--list-live` (read-only, authenticated) and `--apply`
  (authenticated, creates only what's missing) do.

## No-delete guarantee

`courtlistener_alert_sync` has no delete path anywhere in its own module —
it never imports `courtlistener_alerts.delete_alert`. An alert the provider
account holds that this file does not declare (`undeclared_live`) is
reported for a human to look at, never removed. The watchlist side never
reaches the recap-fetch (PACER purchase) endpoint either: every watch above
reads free Search API results only.

## Rate budget

A `--network` watch run is bounded twice: each watch's own `max_pages`
(every watch above declares `1`), and the whole run's `--max-requests`
budget (default `12`), checked **before** each watch's first page request —
a watch with no budget left is skipped without a socket opening, and every
watch after a 429 is skipped rather than retried. A request count caps the work for one invocation. Plan the invocation
around the provider's current rate limits and any other requests using the
same account or network.

## Historical account observations

The 2026-09-25 receipt recorded creation of the declared alerts by
`sync_courtlistener_alerts.py --apply`. The first attempt hit the provider's per-minute limit
(HTTP 429); the idempotent re-run after the stated backoff created all three:

| Alert | CourtListener id |
|---|---|
| search `fifra-pesticide-registration` | 23334 |
| search `pollinator-esa-listing` | 23335 |
| search `forensic-entomology-admissibility` | 23336 |

The first `--network` watch run (2026-09-25) returned twenty hits each for
`fifra-pesticide-opinions` and `pollinator-esa-opinions`, and none for
`forensic-entomology-oral-arguments`. The empty result is a real answer, not an error.
Receipts and snapshots are under the gitignored `output/data/courtlistener/`.

## Running it

Neither `config/courtlistener.yaml` (the CourtListener client registry — base
URL, credential env-var name, throttle documentation) nor the executable
`scripts/run_courtlistener_watch.py` / `scripts/sync_courtlistener_alerts.py`
live in this project; both live in the `legal_informatics` engine. The engine ships
its registry as package data, resolved by
`legal_informatics.courtlistener_client.default_registry_path()` under any install
topology; `scripts/fetch_case_candidate_queries.py` loads it that way unless
`--registry` names another. From this project's root, set `ENGINE_ROOT` to the compatible engine
checkout used for provisioning. In the default checkout layout, use the
value shown below. Run the engine scripts with the project interpreter:

```bash
ENGINE_ROOT=../../Private/legal_informatics

# offline: build and write the credential-free query plan, no socket opens
.venv/bin/python "$ENGINE_ROOT/scripts/run_courtlistener_watch.py" \
  --project-root . \
  --config-path "$ENGINE_ROOT/config/courtlistener.yaml"

# opt-in: run every watch, write a content-addressed snapshot per watch,
# report result ids new since the previous run
.venv/bin/python "$ENGINE_ROOT/scripts/run_courtlistener_watch.py" \
  --project-root . \
  --config-path "$ENGINE_ROOT/config/courtlistener.yaml" \
  --network --max-requests 6

# offline: load and validate the alert registry only
.venv/bin/python "$ENGINE_ROOT/scripts/sync_courtlistener_alerts.py" \
  --project-root . \
  --config-path "$ENGINE_ROOT/config/courtlistener.yaml"

# read-only, authenticated: compute the real plan against the live account
# (requires COURTLISTENER_API_KEY)
.venv/bin/python "$ENGINE_ROOT/scripts/sync_courtlistener_alerts.py" \
  --project-root . \
  --config-path "$ENGINE_ROOT/config/courtlistener.yaml" \
  --list-live

# authenticated mutation: create only what plan_alert_sync finds missing
.venv/bin/python "$ENGINE_ROOT/scripts/sync_courtlistener_alerts.py" \
  --project-root . \
  --config-path "$ENGINE_ROOT/config/courtlistener.yaml" \
  --apply
```

Watch snapshots land under `output/data/courtlistener/watch/<id>/`; alert
plans and apply receipts land under `output/data/courtlistener/alerts/` —
both gitignored, both machine-generated. `tests/test_courtlistener_watch_and_alerts.py`
loads both declared registries through the engine's own validators offline,
on every test run, so a malformed row in either file fails the suite before
it ever reaches a socket.
