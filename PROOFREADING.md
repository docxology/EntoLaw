# PROOFREADING — before publishing this release

What the owner reads and decides before this release ships (no tag, no
GitHub release, no Zenodo upload — see `CHANGELOG.md`'s `[Unreleased]`
entry and `TODO.md`). Packaging preparation is done; this list is what
remains.

## 1. Read the manuscript prose

Every section under `docs/manuscript/`, in order:
`00_abstract.md` → `01_introduction.md` → `02_witness.md` → `03_threat.md` →
`04_protected.md` → `05_property.md` → `06_invention.md` →
`07_defendant.md` → `08_welfare.md` → `09_weapon.md` →
`10_interconnections.md` → `11_methods.md` → `12_conclusion.md`. Read the
source Markdown (with unresolved `{{TOKEN}}` placeholders), not the rendered
PDF, so edits land in the file that generates the output.

## 2. Decide whether this release needs a version bump

`CITATION.cff`, `codemeta.json`, `.zenodo.json`, `docs/manuscript/config.yaml`,
and `pyproject.toml` all currently declare `1.0.0` — the version already
published in the last release (`v1.0.0`, DOI `10.5281/zenodo.21137277`).
Since that tag, `git log --oneline v1.0.0..HEAD` shows a real architecture
change (this project became a thin orchestrator of the `legal_informatics`
engine) plus the gate/docs work in `CHANGELOG.md`'s `[Unreleased]` entry.
Decide: does this warrant bumping to `1.1.0` (or later) before the next
tag, or is it correctly still `1.0.0`-labeled content with no user-facing
change? If bumping, update the version in all five files listed above (or
re-run `scripts/check_metadata_consistency.py` after editing one — it will
name every file that still disagrees) and set a new `date-released` /
`paper.date`.

## 3. ~~Untrack the `.codegraph` symlink~~ (done 2026-09-24)

The machine-local `.codegraph` symlink was untracked and added to `.gitignore`;
`uv run python scripts/check_release_boundary.py` reports `0 findings`, and the
boundary tests now allow no exemptions.

## 4. Regenerate the gate-state block

`TODO.md`'s gate-state block was generated before this session added
`scripts/check_metadata_consistency.py` and `scripts/check_release_boundary.py`
to `config/gate_state.yaml`, so it still shows the old 4-gate state. Run
`uv run python scripts/render_gate_state.py` (full suite; budget tens of
minutes) and confirm all 6 declared gates pass — the boundary gate will not
until step 3 above is done.

## 5. Re-run the live claim-ledger oracle

`uv run pytest -m live` was not run as part of this packaging pass (network
access was out of scope for this unit). Confirm the claim ledger's 20
external sources still resolve and still say what the manuscript quotes
before treating the release as accurate as of its publish date.

## 6. Re-check the known Zenodo description residual

ISA.md's Decisions log records that the live Zenodo record's description
still carried redundant restated-title text after the last publish, fixed in
code (`markdown.py`'s `strip_leading_abstract_heading()`) but never patched
on the already-published record (Zenodo metadata isn't editable over the
API after the fact). If this release mints a new Zenodo version, confirm the
new deposit's description renders cleanly; if it doesn't, a manual web-UI
edit is still the only way to fix the existing `v1.0.0` record's text.

## 7. Confirm the `[Unreleased]` changelog entry before it gets a version and date

`CHANGELOG.md`'s `[Unreleased]` section was drafted from `git log` and this
session's own changes. Read it against the actual diff being published,
correct anything that drifted, then replace `[Unreleased] — DRAFT pending
proofreading` with the real version number (see step 2) and release date
once everything above is resolved.

## 8. Only then: publish

Tag, `gh release create`, and (if a new version) mint the Zenodo DOI via the
project's own publishing tooling. None of that is done by this packaging
pass.
