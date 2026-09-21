"""Cross-repo contract check: this project against the legal_informatics engine.

This project depends on the ``legal_informatics`` engine as an ordinary
editable dependency (see ``pyproject.toml``'s ``[tool.uv.sources]``), the same
pattern the UC_Biopower exemplar consumer uses. The engine states what it
promises along three non-Python-signature axes -- provenance strings,
config-default filenames, and its importable module set -- in
``legal_informatics.engine_contract`` (read that module's docstring for why).
This file is where *this* project states which of those promises it actually
relies on, and fails the moment the installed engine's declaration moves out
from under it.

This never reads the engine's source at all, only its installed
``engine_contract`` module, so it works identically whether
``legal_informatics`` is an editable sibling checkout (as it is here today)
or an ordinary ``site-packages`` install with no sibling in sight. If the
engine package is not importable at all -- missing dependency, a version that
predates this contract -- every test below skips with a stated reason rather
than erroring at collection or silently passing.

What this catches, concretely: ``scripts/scrape_updates.py`` and its test
assert the discovery manifest's ``generator`` field equals
``legal_informatics.legal_updates.write_discovery`` by literal value, and
``config/scope.yaml`` depends on the engine continuing to resolve that exact
relative filename into this project. A future engine release that changes
either is caught here first, with a message that names the file to update.

What this does **not** catch: a module that still exists and still exports the
same top-level name, but whose function signature, return shape, or behavior
changed underneath it. This is presence-only, by design -- see the closing
note on ``test_every_imported_engine_module_is_in_the_declared_public_surface``.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

try:
    from legal_informatics import engine_contract
except ImportError as _import_error:  # pragma: no cover - exercised only when the engine is absent/stale
    engine_contract = None
    _IMPORT_ERROR_REASON = str(_import_error)
else:
    _IMPORT_ERROR_REASON = ""

pytestmark = pytest.mark.skipif(
    engine_contract is None,
    reason=(
        "legal_informatics.engine_contract is not importable "
        f"({_IMPORT_ERROR_REASON or 'unknown import failure'}); the engine dependency may be "
        "missing, unsynced, or older than the version that added this contract module -- "
        "skipping rather than failing the suite on something this project's own change did not break"
    ),
)


#: The provenance strings this project's own tests currently assert on by
#: literal value (``tests/test_thin_orchestrator.py``). Declaring the
#: expectation here too means a future engine release that changes one of
#: these values is caught in this single, fast, obviously-about-the-contract
#: test, not only in whichever scattered test happens to assert on it.
DEPENDED_ON_GENERATORS: dict[str, str] = {
    "legal_updates.write_discovery": "legal_informatics.legal_updates.write_discovery",
}

#: This project ships its own ``config/scope.yaml`` (see
#: ``legal_informatics.corpus_analysis.DEFAULT_SCOPE_PATH`` resolving into it
#: via ``project_paths.project_root()``) and depends on the engine continuing
#: to resolve that exact relative filename.
DEPENDED_ON_CONFIG_DEFAULT = ("scope", "config/scope.yaml")


@pytest.mark.parametrize("key", sorted(DEPENDED_ON_GENERATORS))
def test_generator_string_matches_declared_contract(key: str) -> None:
    """The engine's declared provenance string still matches what this project expects.

    Fails if the installed engine's ``PROVENANCE_GENERATORS[key]`` no longer
    equals the value this project's own tests assert on -- the exact
    cross-repo regression class the engine contract exists to prevent.
    """
    assert key in engine_contract.PROVENANCE_GENERATORS, (
        f"legal_informatics.engine_contract no longer declares {key!r} at all -- "
        "either it was removed/renamed, or this project's expectation is stale"
    )
    declared = engine_contract.PROVENANCE_GENERATORS[key].value
    expected = DEPENDED_ON_GENERATORS[key]
    assert declared == expected, (
        f"legal_informatics.engine_contract.PROVENANCE_GENERATORS[{key!r}] is now {declared!r}; "
        f"this project's tests still expect {expected!r}. Update tests/test_thin_orchestrator.py "
        "(which asserts the old value) in the same change that bumps the engine pin."
    )


def test_scope_config_default_matches_declared_contract() -> None:
    """The engine still resolves ``config/scope.yaml`` the way this project's own file expects."""
    name, expected_relative_path = DEPENDED_ON_CONFIG_DEFAULT
    assert name in engine_contract.CONFIG_DEFAULTS, (
        f"legal_informatics.engine_contract no longer declares a {name!r} config default"
    )
    entry = engine_contract.CONFIG_DEFAULTS[name]
    assert entry.relative_path == expected_relative_path, (
        f"engine_contract.CONFIG_DEFAULTS[{name!r}] now names {entry.relative_path!r}; "
        f"this project ships its own config at {expected_relative_path!r} and depends on the "
        "engine continuing to resolve that exact relative path from the consumer's project root."
    )


def _imported_legal_informatics_modules() -> set[str]:
    """Every ``legal_informatics.<module>`` name this project's own tree imports.

    Reads only this project's own ``src/``, ``scripts/``, and ``tests/`` --
    never the engine's tree -- so this works the same whether
    ``legal_informatics`` is a sibling checkout or a package install.
    """
    modules: set[str] = set()
    for root_name in ("src", "scripts", "tests"):
        root = PROJECT_ROOT / root_name
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module == "legal_informatics":
                        modules.update(alias.name for alias in node.names)
                    elif node.module.startswith("legal_informatics."):
                        modules.add(node.module.split(".", 2)[1])
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("legal_informatics.") and alias.name != "legal_informatics":
                            modules.add(alias.name.split(".", 2)[1])
    return modules


def test_every_imported_engine_module_is_in_the_declared_public_surface() -> None:
    """Every ``legal_informatics.<module>`` this project imports still ships.

    ``engine_contract.PUBLIC_MODULES`` reflects the *installed* engine's own
    package directory (see its docstring), so this fails the moment a future
    engine release drops or renames a module this project still imports by
    name -- before pytest collection fails module-by-module on the import
    statements themselves, and with a message that says which module and why.

    What this does **not** catch: a module that still exists and still
    exports the same top-level name, but whose function signature, return
    shape, or behavior changed underneath it. This is presence-only, by
    design (see ``engine_contract.PUBLIC_MODULES``' docstring) -- it is not a
    substitute for this project's own tests actually exercising the imported
    functions, which they do, elsewhere in this suite.
    """
    imported = _imported_legal_informatics_modules()
    assert imported, "expected this project's own tree to import at least one legal_informatics module"
    missing = sorted(imported - engine_contract.PUBLIC_MODULES)
    assert not missing, (
        "these legal_informatics modules are imported somewhere in this project but are no "
        f"longer in the installed engine's declared public surface: {missing}"
    )