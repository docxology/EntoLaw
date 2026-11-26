# ISA — EntoLaw

The Ideal State Artifact for the EntoLaw project: a source-anchored,
reproducible field map of entomological law.

## Problem

The intersection of insects and law is a genuinely transdisciplinary field with
no master statute, no professional society spanning it, and no comprehensive
treatise. Existing surveys mix prose summaries with anecdotes that rot as
statutes are recodified and holdings distinguished, and they state colourful
statistics with no machine-checkable link to a source.

## Vision

A registry-first, claim-sourced reference in which (a) the field is organized by
the eight legal **roles** an insect occupies; (b) every count in the prose is
generated from source-of-truth registries; (c) every legal proposition is cited
to a primary authority; and (d) every externally-sourced numeral is bound to a
quotable, re-checkable source. The map and the territory cannot drift apart.

## Out of scope

- Adjudicating unsettled law or offering legal advice.
- Exhaustively enumerating every case, statute, or species — registries are
  curated to anchor each role with its leading authorities.
- Live network access in the default test run (reserved for the `-m live` oracle).

## Principles

- Thin orchestrator: business logic lives in `src/`; scripts and prose consume it.
- No hard-coded statistic: tokens or claim-ledger, never a bare literal.
- Honesty boundary: offline gates prove shape/attribution; the live oracle
  proves correspondence (see `docs/ACCURACY_METHODOLOGY.md`).
- No mocks: real data, real files, injectable validators for error paths.

## Goal & Criteria

- [x] Eight legal roles encoded as the manuscript spine (`src/roles.py`).
- [x] Registries for cases, statutes, species, institutions, timeline, and
  interconnections, all validated against controlled vocabularies.
- [x] Manuscript with token closure, citation closure, and cross-reference
  closure; abstract → conclusion plus a methods section documenting the contract.
- [x] Claim ledger with a fail-closed offline oracle and a live oracle; 20
  shipped entries live-verified, source checks last run through 2026-06-30.
- [x] Deterministic matplotlib figures, one per caption, plus a cover.
- [x] `src/` test coverage ≥ 90% with no mocks; combined PDF + HTML render
  through the template.

## Test Strategy

Registry-content invariants; citation-grammar parsing; validation with injected
real bad data; token/citation/cross-reference closure against the manuscript;
no-hard-coded-statistic gate with a negative control; figure ↔ caption
totality; determinism of registry-derived variables; and a `-m live` claim
oracle.

## Verification

`uv run pytest tests/` → 142 passed (re-verified 2026-07-02 after this session's changes).
`scripts/run_inventory.py` → 0 validation errors. `scripts/03_render_pdf.py
--project working/EntoLaw` → combined PDF + 14 HTML sections, no unresolved
tokens.

**Published (2026-07-02):** `uv run python -m infrastructure.publishing.transmission_page_check output/pdf/EntoLaw_combined.pdf` → `OK: begin page 1, end page 42, 42 pages total`. Concept DOI `10.5281/zenodo.21137276` and version DOI `10.5281/zenodo.21137277` both resolve (`curl -sI https://doi.org/...` → `302` to `zenodo.org`). Live Zenodo record confirmed `related_identifiers` cross-linking to `github.com/docxology/EntoLaw` and its `v1.0.0` release. GitHub release `v1.0.0` confirmed via `gh release view` with the DOI-bearing PDF attached. Both pushes' CI runs confirmed `success` via `gh run list --json status,conclusion`.

## Decisions

- 2026-07-02: Redesigned `src/viz_cover.py` end-to-end — the prior layout had
  two real overlap bugs (title/subtitle text overrunning into the
  "specimen-to-doctrine map" panel; a butterfly glyph's antenna overlapping
  the "FIELD RECORD" label). New layout moves all 4 insect glyphs into the
  right panel as a labelled 2×2 "specimen board" (role-tagged, matched to a
  real manuscript narrative: monarch→protected, mosquito→threat,
  honeybee→property, weevil→defendant) and adds a verbatim, contiguous
  3-sentence pull-quote from `00_abstract.md`. Verified verbatim
  character-for-character after an Advisor-flagged near-miss (original draft
  skip-spliced a non-contiguous 4th question).
- 2026-07-02: `src/viz_network.py` — the role-interconnections figure's
  caption always claimed "5 recurring themes... edge bundles share a theme
  colour" but the legend only showed 4; the 5th theme
  (`definitional_problem`) was drawn faint-gray with no legend entry. Added
  it to the legend so the figure matches its own caption.
- 2026-07-02: `src/viz_timeline.py` — fixed two real annotation-collision
  bugs (Plant Quarantine Act / Kirstin Lobato exoneration boxes overlapped;
  the "evidence + property" era-band label overlapped the 1972 BWC point)
  via explicit offset/position tuning, not a generic collision solver —
  timeboxed per R9 rather than building general layout avoidance.
  Recurrence risk if new milestones land in the same year windows.
- 2026-07-02: `src/viz_bars.py` — replaced role-coverage heatmap's stock
  `YlGnBu` colormap with a brand-consistent blue scale
  (`_COVERAGE_CMAP`). Checked `src/figure_caption_records.py` first for
  colour-word claims tied to that figure (none) per the
  `gotcha-colormap-swap-falsifies-colour-word-captions` pattern — safe swap.
- 2026-07-02: Moved Figure 7 (role_interconnections) and Figure 12
  (citation_dates) from deep in the manuscript into `01_introduction.md` as
  an early preview (now Figures 2 and 4), per user request. Embeds were
  *moved*, not duplicated — `10_interconnections.md` and `11_methods.md`
  keep the analytical prose and reference the figures in plain descriptive
  text.
  - refined: first attempt used pandoc-crossref `@fig:` tokens for the
    back-references. This broke `test_rendered_web_export_has_no_raw_manuscript_markers`
    because the project also renders each section as a *standalone* HTML
    page, and pandoc-crossref cannot resolve a figure ID defined in a
    different file when rendering one section in isolation. Reverted to
    plain prose ("the interconnections network figure at the start of this
    reference"), matching the manuscript's pre-existing house style — `@fig:`
    was never used as a pure cross-reference anywhere else in this
    manuscript, only as a same-paragraph image-embed label.
- Effort: E4 (Deep). Capabilities invoked this run: FirstPrinciples,
  IterativeDepth, SystemsThinking, RootCauseAnalysis, ApertureOscillation,
  FeedbackMemoryConsult, ReReadCheck (thinking, 7 ≥ floor 6); Forge,
  Advisor (delegation, 2 = floor 2). Advisor called at the VERIFY
  commitment boundary; caught the pull-quote non-contiguity issue before
  it shipped.

## Changelog

- conjectured: cross-file `@fig:` pandoc-crossref references would resolve
  gracefully (or at worst degrade to "??") in every rendered output format.
- refuted_by: `test_rendered_web_export_has_no_raw_manuscript_markers`
  failing on `output/web/manuscript__10_interconnections.html` and
  `manuscript__11_methods.html` — pandoc-crossref left the literal
  `@fig:citation_dates` / `@fig:role_interconnections` text in the
  standalone per-section HTML, since that render has no access to the
  figure's defining file.
- learned: pandoc-crossref cross-references only resolve reliably when the
  referencing and defining content are combined into one pandoc invocation.
  Any manuscript in this template that also ships standalone per-section
  HTML must treat cross-file `@fig:`/`@tbl:`/`@eq:` references as unsafe and
  use plain descriptive prose instead; same-file references are unaffected.
- criterion_now: figure relocations that cross section-file boundaries must
  replace the old embed with plain prose, never a crossref token, unless the
  project drops standalone per-section rendering as a supported output.

## Decisions (continued — 2026-07-02, second pass)

- Bigger cover-art fonts (title 28→31pt, subtitle/stats/pull-quote/panel
  labels scaled proportionally); re-verified no new overlaps at the larger
  sizes via rasterized-page inspection.
- Condensed `11_methods.md` from 4 subsections to 2 ("Token closure" +
  "Claim ledger, validation, and reproducibility") specifically to pull the
  Contents page back under one page (it was one line — the Conclusion
  entry — over budget). Page count 38→37 pre-bookends.
- Rewrote the architecture figure's caption (`figure_caption_records.py`
  `architecture` entry): "...to reproducible outputs: {N} registries feed..."
  read as a garden-path list where "N registries" appeared to enumerate the
  outputs rather than start a new clause. New phrasing: "How {N} source-owned
  registries become reproducible outputs. Pure generator methods — ... —
  turn registry data into...".
- Added a verified-verbatim William Blake epigraph (`blake1790_marriage` —
  Project Gutenberg #45315, confirmed live before citing) after "'Entomological
  law' is not a claim that insects should have one code" in `12_conclusion.md`.
- Added `johnson2023honeybeebiology` (Johnson, *Honey Bee Biology*, Princeton
  UP, 2023, ISBN 9780691204888) at the *animus revertendi* swarming/absconding
  sentence in `05_property.md` — the one place the manuscript states a
  biological fact a biology textbook, not a legal citation, should ground.
- **Publication (real, production, irreversible):** fixed a schema mismatch
  in `config.yaml` (`authors[].affiliations:` list → the metadata-export
  tool's expected `authors[].affiliation:` string) that was silently
  dropping "Active Inference Institute" from `CITATION.cff`/`.zenodo.json`.
  Added `LICENSE` (CC-BY-4.0, fetched verbatim), `.gitignore` (untracked 125
  accidentally-committed `__pycache__`/`.egg-info`/`.coverage` files),
  `.github/workflows/ci.yml` (test/lint/live-claims jobs; validated with
  `actionlint` and dry-run-tested in a fully isolated clone before trusting
  it). Fixed `tests/test_render_hydration.py`, which hard-assumed a sibling
  template checkout only present on the dev machine — would have failed on
  every standalone GitHub Actions run; now `skipif`s cleanly when absent.
  Enabled `publication.transmission_bookends` (the template's existing
  begin/end DOI-pairing page system) rather than hand-rolling a colophon.
  Created `docxology/EntoLaw` (public), pushed, minted a real Zenodo DOI via
  `scripts/publish_project_release.py --production --reserve-doi-first`
  (concept DOI `10.5281/zenodo.21137276`, version DOI `10.5281/zenodo.21137277`).
  The script's own GitHub-release step 403'd (`GITHUB_TOKEN` in `.env` lacks
  release-creation scope, unlike the `gh` CLI's own login) *after* the Zenodo
  deposit had already gone live — created the release manually via `gh
  release create` instead. Caught and cleared a stale dry-run's placeholder
  DOI (`10.5281/zenodo.1000001`) that had backfilled into
  `output/data/publication_ledger.json` and was rendering as fake "State:
  published" data on the bookend pages *before* the real publish ran — see
  Changelog entry below.
- **Known residual issue (2026-07-02, second session):** the live Zenodo
  record's description still opens with the redundant restated-title text
  ("A Source-Anchored Map of Entomological Law There is no statute…")
  because the underlying `strip_leading_abstract_heading()` bug (see
  root-repo `CHANGELOG.md`) wasn't caught until after publish. The user
  hand-removed the literal word "Abstract:" via the Zenodo web UI but the
  subtitle text remains glued onto the abstract body. The code bug is now
  fixed (`infrastructure/prose/markdown.py`), but Zenodo published-record
  metadata can't be patched over the API (404) — cleaning up the live
  description needs another manual web-UI edit or a `--new-version`
  republish. Not done in this session; flagged, not silently left unstated.

## Changelog (continued)

- conjectured: a dry-run (`--dry-run`) of `publish_project_release.py`
  writes only to its own throwaway output location and leaves no trace a
  subsequent real render could pick up.
- refuted_by: the *first* pre-publish render after the dry-run showed
  "State: published" with the dry-run's placeholder DOI
  (`10.5281/zenodo.1000001`) on the transmission-bookend pages — because
  `load_publication_ledger()` backfills `output/data/publication_ledger.json`
  from `RELEASE_RECEIPT.json` (including dry-run receipts) the first time
  it's read, and that ledger then persists across renders regardless of the
  `dry_run: true` flag on the backfilled entry.
- learned: a dry-run of this release tooling is not side-effect-free for a
  project's own `output/`. Delete
  `<repo_root>/output/<qualified_project_name>/release_bundle/` and the
  project's own `output/data/publication_ledger.json` between a dry-run
  rehearsal and the real publish, or the bookend pages will render fabricated
  "published" state built from placeholder data.
- criterion_now: before any real `--reserve-doi-first` run, verify
  `output/data/publication_ledger.json` is absent or contains only entries
  with real (non-`dry_run`) receipts; a `dry_run: true` entry backfilled into
  the ledger is guilty of contaminating the next honest render until proven
  otherwise.
