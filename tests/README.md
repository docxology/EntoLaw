# Tests

Run the [declared local gate](../docs/local_validation.md) for acceptance.
It renders the manuscript before testing the rendered outputs and enforces
the branch coverage floor for `src/`. For a focused offline check, use the
same project environment with
`.venv/bin/python -m pytest -m 'not live' tests/test_case_candidates.py`.

The separately authorized live suite fetches claim-ledger sources.
`test_registry_analysis.py` checks the selected registry frame, including
partition counts, duplicate and unknown-role rejection, and the provenance
digests attached to the figure.
