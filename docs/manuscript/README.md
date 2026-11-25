# manuscript

Manuscript/documentation sources of the parent project.

Part of `EntoLaw`.

## Contents
Files: `00_abstract.md`, `01_introduction.md`, `02_witness.md`, `03_threat.md`, `04_protected.md`, `05_property.md`, `06_invention.md`, `07_defendant.md`, `08_welfare.md`, `09_weapon.md`, `10_interconnections.md`, `11_methods.md`, `12_conclusion.md`, `99_references.md`, `AGENTS.md`, `README.md`, `config.yaml`, `preamble.md`, `references.bib`

## Usage
- See [the project README](../../README.md) for how this directory is produced and used.

## Opening graphical abstract

The [local gate](../local_validation.md) builds and checks the opening figure
through the installed engine. For a focused run before hydration, use the
project's locked Python from the project root.

```bash
.venv/bin/python -m legal_informatics.muckraker.domain_cli graphical-abstract --project-root .
.venv/bin/python -m legal_informatics.muckraker.domain_cli graphical-abstract --project-root . --check
```

The current local gate runs both steps before hydration. The opening chapter links to the verified figure and provides the dated instrument and entity evidence in text.
