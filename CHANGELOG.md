# Changelog

All notable changes to EntoLaw are documented here.

## [Unreleased] — DRAFT pending proofreading

Publication-packaging preparation only. **Not published**: no tag, no GitHub
release, no Zenodo upload has been made for this entry. See
[`PROOFREADING.md`](PROOFREADING.md) for what the owner reads before that
happens, and `TODO.md`'s generated gate-state block (re-run
`uv run python scripts/render_gate_state.py` for the current pass/fail — this
entry does not repeat it; `--check` re-runs every gate and fails when the
committed block disagrees).

Derived from `git log --oneline v1.0.0..HEAD` and the registries; no count in
this entry is hand-typed where a generator can be re-run instead
(`uv run python scripts/run_inventory.py`, `scripts/render_gate_state.py`).

### Changed

- Became a thin orchestrator of the `legal_informatics` engine: shared
  module-map, docs-inventory, and gate-state machinery is now consumed from
  the engine as an editable dependency rather than carried locally.
- Completed the `docs/` and manuscript compliance audit (docs-audit
  2026-08-29).
- Stood up this project's declared gates (`config/gate_state.yaml`) and made
  them pass.
- Fixed a version-metadata drift: `pyproject.toml` declared `0.1.0` while
  `CITATION.cff`, `codemeta.json`, and `.zenodo.json` already declared
  `1.0.0`. All five metadata files (adding `docs/manuscript/config.yaml`) now
  agree, enforced going forward by `scripts/check_metadata_consistency.py`.
- Removed leaked machine-specific absolute filesystem paths (home-directory
  and external-volume paths naming a specific development machine) from
  tracked documentation (`README.md`, `docs/REVIEW_PROTOCOL.md`, and nine
  fleet-generated `AGENTS.md` files), found and enforced going forward by
  `scripts/check_release_boundary.py`.
- `{{PYTHON_VERSION}}` now resolves through the engine's
  `legal_informatics.manuscript_variables.receipt_python_version`, which
  prefers the interpreter recorded in `output/data/quality_receipt.json`
  (the environment the quality gate actually ran under) and falls back to
  the running interpreter only when no receipt exists, instead of a bare
  `platform.python_version()` call that named whichever interpreter happened
  to hydrate the variables. Adopting the helper required declaring this
  project's (empty) extensions to the engine in the new
  `config/manuscript_variables.yaml` — the engine refuses to import without
  one.
- Maintenance pass: refreshed the CI action pins to `actions/checkout` v7.0.1,
  `astral-sh/setup-uv` v10.3.2, and `actions/setup-python` v7.1.0 (same
  inputs, same runner), and corrected stale references — `docs/README.md`
  still said `v0.1.0`, `docs/manuscript/MANUSCRIPT_STATUS.md` named a
  nonexistent `resolve_manuscript_dir` resolver and a "legacy" location
  identical to the current one, and `TODO.md`/`PROOFREADING.md` both still
  claimed the committed gate-state block predated the last two declared gates.

### Added

- `scripts/check_metadata_consistency.py` — new declared gate; fails when
  version, title, license, keywords, authors, ORCID, or DOI disagree across
  `pyproject.toml`, `CITATION.cff`, `codemeta.json`, `.zenodo.json`, and
  `docs/manuscript/config.yaml`, reading `CITATION.cff` as the one declared
  source rather than a value hardcoded in the check.
- `scripts/check_release_boundary.py` — new declared gate; scans every
  git-tracked file for credentials, non-public emails, absolute local paths,
  internal hostnames, private-repo references, leaked local-tool symlinks,
  and oversized binaries.
- `PROOFREADING.md` — the checklist the owner reads before release.

### Fixed

- Untracked the machine-local `.codegraph` symlink and added it to
  `.gitignore` (`65f9a55`), then dropped the boundary check's exemption for it
  now that the live tree scans clean (`1e8c4f3`). This clears the one finding
  `scripts/check_release_boundary.py` used to report; the boundary is covered
  by `tests/test_release_boundary.py`.

## [0.1.0] — 2026-06-25

Initial release: a source-anchored, reproducible field map of entomological law.

### Added

- Eight-role spine (`src/roles.py`) and registries for cases, statutes,
  species, institutions, timeline, and interconnections.
- `manuscript_variables` token generation, `claim_ledger` with offline + live
  oracles, cross-registry `validation`, and `package_map` self-description.
- Deterministic matplotlib figure layer (`viz`, `figure_bundle`) — ten captioned
  figures plus a cover.
- Modular claim-sourced manuscript (abstract → conclusion + methods), with token,
  citation, and cross-reference closure.
- Claim ledger with 20 live-verified external statistics (ESA invertebrate
  definition; Hallmann 2017 biomass decline; 2026 PNAS protection gap; UK
  Sentience Act scope; invasive-species, novel-food, and welfare sources; and
  others), with source checks last run through 2026-06-30.
- Test suite (no mocks): registry invariants, citation parsing, injectable
  validators, closure gates, no-hard-coded-statistic gate with negative control,
  figure totality, determinism, and a `-m live` claim oracle. `src/` coverage ≈ 97%.
- End-to-end render verified through the template (combined PDF + HTML).
