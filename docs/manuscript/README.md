# Entomological Law manuscript

Daniel Ari Friedman’s field map follows eight legal roles from forensic evidence and
regulated threats through conservation, property, invention, defendants, welfare,
and the law of biological weapons. The final sections explain the connections,
methods, evidence limits and bibliography.

Start with the [abstract](00_abstract.md), [introduction](01_introduction.md)
and [methods](11_methods.md). The [render configuration](config.yaml) sets the
section order and output formats. It travels with the [preamble](preamble.md)
and [bibliography](references.bib).

Edit these numbered sources and keep registry-derived values as tokens.
The renderer hydrates them into `output/manuscript/` and generates the
opening and closing transmission bookends. The checked-in files under
`output/` include historical evidence and published artifacts.

Use the [native gate](../local_validation.md) with the shared engine, or
the [pinned public replay](../local_validation.md#replay-the-public-snapshot)
to build PDF, HTML and EPUB from the checked-in variables and figures.

## Opening graphical abstract

The [local gate](../local_validation.md) builds and checks the opening figure
through the installed engine. For a focused run before hydration, use the
project's locked Python from the project root.

```bash
.venv/bin/python -m legal_informatics.muckraker.domain_cli graphical-abstract --project-root .
.venv/bin/python -m legal_informatics.muckraker.domain_cli graphical-abstract --project-root . --check
```

The current local gate runs both steps before hydration. The opening chapter links to the verified figure and provides the dated instrument and entity evidence in text.
