# Local validation on the current runtime

The project pins Python 3.15.2 and uses the engine's Pillow 13 floor. Ruff uses
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
its pointer. With the pinned interpreter, compatible engine source and uv cache already
available, provision the environment from the project root in a separate step:

```bash
uv sync --locked --offline --extra dev --no-python-downloads
```

The render also needs the declared template, Pandoc and XeLaTeX. Set
`LEGAL_INFORMATICS_TEMPLATE_ROOT` to an approved template checkout when discovery cannot
find it. The relative engine path in
`pyproject.toml` follows the owned Public/Private storage layout; a standalone
checkout must deliberately set its own engine source location and re-lock.
The coding-review and graphical-abstract build and check steps run as modules
of that installed engine. Provision an engine that supplies those commands
before running the gate. An unavailable declared module stops the gate before
artifact generation. No machine-absolute source path belongs in the tracked
configuration.

`output/data/local_validation_receipt.json` binds a passing result to the
actual interpreter, locked dependencies and source/config/docs/data bytes.
Verify the receipt against the current inputs and per-step diagnostics:

```bash
.venv/bin/python -m legal_informatics.local_validation --project-root . --verify-receipt
```
An offline gate proves neither current-source quote correspondence nor
vulnerability status. The separately authorized live quote oracle and dependency
audit retain their own results. A local receipt is not a hosted Actions run.

`config/manuscript_metadata.yaml` forbids formal publication. The actual local
render is written under `output/rendered/manuscript/`; historical DOI metadata
is retained and no new DOI or external manuscript release is created.

The enabled transmission bookends require QR and linear-barcode generators.
Both are declared runtime dependencies and are exercised by the actual local
render; their presence does not authorize publication.

## Replay the public snapshot

Use a disposable EntoLaw checkout under `projects/working/EntoLaw` in
[Template at commit `87704feae0a4490ef7dad9c931d268e8c30273c2`](https://github.com/docxology/template/tree/87704feae0a4490ef7dad9c931d268e8c30273c2).
The replay starts from the numbered Markdown, config, preamble and bibliography
in `docs/manuscript/`. It substitutes the checked-in values in
`output/data/manuscript_variables.json`, uses the checked-in figures and prepares copies under
`output/manuscript/`. Run it in the disposable checkout because it rewrites
generated files there. The figure registry binds
each labelled image to its local file and resolved manuscript caption.

Provision the pinned Template environment with `uv sync --locked` before
running the replay. Have compatible Pandoc, pandoc-crossref, XeLaTeX and
BibTeX available on `PATH`. From the Template root, with the EntoLaw checkout
already in place:

```bash
uv run --no-sync python - <<'PY'
import json
import re
from pathlib import Path

from infrastructure.rendering.manuscript_injection import (
    substitute_manuscript_text,
    write_resolved_manuscript_tree,
)

project = Path("projects/working/EntoLaw").resolve(strict=True)
variables_path = project / "output/data/manuscript_variables.json"
variables = json.loads(variables_path.read_text(encoding="utf-8"))
for section in sorted((project / "docs/manuscript").glob("[0-9]*.md")):
    _, missing = substitute_manuscript_text(section.read_text(encoding="utf-8"), variables)
    if missing:
        raise SystemExit(f"{section.name} is missing snapshot values for {sorted(set(missing))}")
resolved = write_resolved_manuscript_tree(project, variables)
figures = project / "output/figures"
image = re.compile(r"!\[([^\]\n]+)\]\(([^)\s]+)\)\s*\{#(fig:[\w.:-]+)")
registry = {}
for section in sorted(resolved.glob("[0-9]*.md")):
    for caption, target, label in image.findall(section.read_text(encoding="utf-8")):
        figure = (section.parent / target).resolve(strict=True)
        filename = figure.relative_to(figures).as_posix()
        registry[label] = {"filename": filename, "alt_text": caption}
(figures / "figure_registry.json").write_text(
    json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
PY
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/EntoLaw --skip-manuscript-hydration
web=projects/working/EntoLaw/output/web
if [ -L "$web/figures" ]; then
    test "$(readlink "$web/figures")" = ../figures || exit 1
    unlink "$web/figures"
    cp -R "$web/../figures" "$web/figures"
fi
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/EntoLaw
```

The copy step replaces the archived web export’s figure symlink inside the
disposable checkout. Stage 04 requires regular files for its output inventory.

Look for `output/pdf/EntoLaw_combined.pdf`, `output/web/index.html` and
`output/epub/EntoLaw_combined.epub` in the disposable checkout. Use fresh
outputs when inspecting the render because the repository also carries
historical exports under `output/`. This replay validates the authored
sources against a fixed public snapshot. Registry recomputation, current-law
review, source retrieval and publication are separate activities.
