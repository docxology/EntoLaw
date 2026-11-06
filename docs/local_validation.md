# Local validation on the current runtime

The project pins Python3.15.2 and uses the engine's Pillow13 floor. Ruff uses
the reviewed current minor. Actions workflows and scheduled dependency-update
configuration are absent; independent local validation records the checks
that actually ran. Vulnerability alerts and any free internal dependency-graph
jobs are separate repository settings.

`config/local_validation.yaml` declares offline lock consistency, dependency
tree, lint, inventory, figures, module map, docs,
metadata, public-content boundary, actual hydration/render, web assets and
complete non-live tests. The render precedes tests that inspect those actual
outputs. The template is discovered through its declared environment contract. Run the installed engine runner:

```bash
.venv/bin/python -m legal_informatics.local_validation --project-root .
```

In a managed vault use its qualified offline test runner and repository
admission. Provision before the offline gate; the runner installs nothing and
fetches no source evidence. Preserve an existing environment before replacing
its pointer. Current-runtime provisioning uses the locked project and explicit
dev extra, with no interpreter downloads. The relative engine path in
`pyproject.toml` follows the owned Public/Private storage layout; a standalone
checkout must deliberately set its own engine source location and re-lock.
No machine-absolute source path belongs in the tracked configuration.

`output/data/local_validation_receipt.json` binds a passing result to the
actual interpreter, locked dependencies and source/config/docs/data bytes.
An offline gate proves neither current-source quote correspondence nor
vulnerability status. The separately authorized live quote oracle and dependency
audit retain their own results. A local receipt is not a hosted Actions run.

`config/manuscript_metadata.yaml` forbids formal publication. The actual local
render is written under `output/rendered/manuscript/`; historical DOI metadata
is retained and no new DOI or external manuscript release is created.

The enabled transmission bookends require QR and linear-barcode generators.
Both are declared runtime dependencies and are exercised by the actual local
render; their presence does not authorize publication.
