#!/usr/bin/env python3
"""Scan the tracked tree for anything that must not ship in a public release.

Five findings gate the exit code, each reported with its own diagnostic:

* **credential** -- a private-key header, or an assignment that looks like an
  embedded API key, token, or password.
* **non_public_email** -- an email address other than the one this project's
  own metadata declares public (read from :data:`DECLARED_SOURCE`, never
  hardcoded here).
* **absolute_local_path** -- a machine-specific filesystem path
  (``/Users/...``, ``/Volumes/...``, ``/home/<user>/...``) that leaks this
  checkout's local layout and breaks on every other machine.
* **internal_hostname** -- ``localhost``, a loopback/private-range IP, or a
  ``.internal``/``.corp``/``.local`` address.
* **private_repo_reference** -- a reference to a repository this project's
  own ecosystem keeps private (declared in :data:`PRIVATE_REPO_SLUGS`, plus
  the generic ``*-private`` naming convention that ecosystem uses).

**large_binary** is reported the same way but as its own, separately-named
finding kind, since "must not ship" for a binary is a size judgment
(:data:`LARGE_BINARY_BYTES`) rather than a content match.

This module separates *which files* to scan (:func:`tracked_files`, one real
``git ls-files`` subprocess) from *what counts as a finding*
(:func:`scan_paths`, pure text/size checks over real files). Tests exercise
:func:`scan_paths` directly against small real fixture trees rather than
against a git repository, and :func:`check_release_boundary` is the
composition the CLI and the gate both call.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: Same declared source of truth :mod:`check_metadata_consistency` reads --
#: the one public author email this project declares, never a literal typed
#: here.
DECLARED_SOURCE = "CITATION.cff"

#: Above this size, a tracked file is a "large binary" finding regardless of
#: content. 2 MiB comfortably clears this project's real release artifacts
#: (the combined PDF is ~1.3 MB as of this gate's introduction) while still
#: catching an accidentally-committed video, database dump, or archive.
LARGE_BINARY_BYTES = 2 * 1024 * 1024

#: Extensions treated as binary for the size check; a large text file (a
#: rendered HTML export, a generated JSON report) is not the failure mode
#: this check exists for.
BINARY_EXTENSIONS = frozenset({".pdf", ".epub", ".png", ".jpg", ".jpeg", ".zip", ".db", ".sqlite", ".sqlite3", ".mp4", ".mov", ".tar", ".gz"})

#: Repositories this ecosystem keeps private. A reference to one inside a
#: public repo's tracked tree is a leak of internal project structure, not a
#: secret, but still not this project's to publish. Kept short and reviewed
#: by hand rather than derived, because "private" is a declared status, not a
#: computable property of a name.
PRIVATE_REPO_SLUGS = frozenset({"operator", "abliteration", "daf-jev", "daf-skills"})

#: The generic naming convention this ecosystem also uses for a private fork
#: or variant of an otherwise-public project (``AGEINT-private``,
#: ``BeeStack-private``, ...).
_PRIVATE_REPO_SUFFIX_RE = re.compile(r"\b[A-Za-z0-9_]+-private\b")

_CREDENTIAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(
        r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd)\b\s*[:=]\s*"
        r"['\"]?[A-Za-z0-9_\-/+=]{16,}['\"]?"
    ),
)

#: A bare 32-40 char hex string is the shape of many vendor API keys, but it
#: is also the shape of a pinned GitHub Actions commit SHA
#: (``uses: actions/checkout@<40-hex-sha>``) or a full git commit hash quoted
#: in prose, both legitimate and common in this project's own tracked tree.
#: Flagged separately from :data:`_CREDENTIAL_PATTERNS` and excluded from any
#: line carrying the pin/hash markers that make the false-positive case
#: identifiable, rather than dropped outright -- an embedded 40-hex-char
#: token with no such marker is still exactly the shape a real leaked
#: CourtListener-, GitHub-, or Zenodo-style key would have.
_HEX_TOKEN_RE = re.compile(r"\b[0-9a-f]{32,40}\b")
_HEX_TOKEN_ALLOWED_CONTEXT_RE = re.compile(r"uses:|actions/|commit|sha256|sha1|#\s*v?\d")

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

_ABSOLUTE_PATH_RE = re.compile(r"(?:/Users/[A-Za-z0-9_.-]+|/Volumes/[A-Za-z0-9_.-]+|/home/[A-Za-z0-9_.-]+)(?:/[^\s'\"`]*)?")

_INTERNAL_HOSTNAME_RE = re.compile(
    r"\b(localhost|127\.0\.0\.1|0\.0\.0\.0|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|"
    r"[A-Za-z0-9-]+\.(?:internal|corp|local))\b"
)

#: Files this scan does not read as text (binary formats it only size-checks).
_SKIP_TEXT_EXTENSIONS = BINARY_EXTENSIONS | {".ico", ".woff", ".woff2", ".ttf"}

#: This scanner's own module, excluded from its own text-content checks (not
#: from the symlink or size checks, which do not apply to it anyway). Its
#: docstrings illustrate the finding kinds with example path/hostname/repo
#: shapes, and its own pattern definitions necessarily spell out the literal
#: words they match (``_INTERNAL_HOSTNAME_RE`` must contain the text
#: "localhost" to detect it) -- both are the tool describing itself, not
#: tracked content that would leak on release, and excluding this one known
#: path is more honest than writing patterns that could no longer describe
#: what they do.
_SELF_EXCLUDED_RELATIVE_PATHS = frozenset({"scripts/check_release_boundary.py"})


def tracked_files(project_root: Path) -> list[Path]:
    """List every git-tracked file, relative to ``project_root``, as real paths on disk.

    Uses ``git ls-files`` rather than walking the filesystem, so an untracked
    scratch file (a local ``.venv``, a coverage cache) is never scanned or
    reported as if it would ship.
    """
    result = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "ls-files", "-z"],
        cwd=project_root,
        capture_output=True,
        check=True,
        text=False,
    )
    names = result.stdout.split(b"\0")
    return [project_root / name.decode("utf-8") for name in names if name]


def _declared_public_email(project_root: Path) -> str | None:
    """Read the one public author email this project declares, from ``CITATION.cff``."""
    import yaml

    path = project_root / DECLARED_SOURCE
    if not path.is_file():
        return None
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for author in payload.get("authors") or []:
        email = author.get("email")
        if email:
            return str(email)
    return None


def scan_paths(paths: list[Path], project_root: Path, public_email: str | None) -> list[str]:
    """Scan real files on disk for content that must not ship.

    Args:
        paths: Real files to scan, as absolute paths (or paths resolvable
            under ``project_root``).
        project_root: Root the reported locations are made relative to.
        public_email: The one email address that is not a finding; every
            other address found is reported. ``None`` disables the email
            check entirely rather than flagging every address as non-public.

    Returns:
        One message per finding, each prefixed with its kind
        (``credential:``, ``non_public_email:``, ``absolute_local_path:``,
        ``internal_hostname:``, ``private_repo_reference:``,
        ``tracked_symlink -> absolute_local_path:``,
        ``tracked_symlink -> internal_hostname:``, ``large_binary:``),
        ordered by path then kind.
    """
    findings: list[str] = []
    for path in sorted(paths):
        try:
            relative = path.relative_to(project_root)
        except ValueError:
            relative = path

        if path.is_symlink():
            # A symlink's target is itself a string this check must read: a
            # tracked symlink pointing outside the project (a local tool's
            # cache, a machine-specific home directory) leaks exactly the
            # kind of path this gate exists to catch, and `path.is_file()`
            # silently skips it when the target does not exist on this
            # machine -- the common case for a symlink nobody should have
            # tracked in the first place. A symlink whose target is a
            # relative, in-repo path (ordinary repo structure, e.g.
            # `output/web/figures -> ../figures`) is not itself a finding.
            target = str(path.readlink())
            for pattern_name, pattern in (
                ("absolute_local_path", _ABSOLUTE_PATH_RE),
                ("internal_hostname", _INTERNAL_HOSTNAME_RE),
            ):
                for match in pattern.finditer(target):
                    findings.append(f"{relative}: tracked_symlink -> {pattern_name}: {match.group(0)}")
            continue

        if not path.is_file():
            continue

        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > LARGE_BINARY_BYTES:
            findings.append(f"{relative}: large_binary: {size} bytes exceeds {LARGE_BINARY_BYTES} byte gate")

        if path.suffix.lower() in _SKIP_TEXT_EXTENSIONS:
            continue
        if relative.as_posix() in _SELF_EXCLUDED_RELATIVE_PATHS:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for pattern in _CREDENTIAL_PATTERNS:
            for match in pattern.finditer(text):
                line_number = text.count("\n", 0, match.start()) + 1
                findings.append(f"{relative}:{line_number}: credential: matched {pattern.pattern[:40]!r}...")

        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in _HEX_TOKEN_RE.finditer(line):
                if _HEX_TOKEN_ALLOWED_CONTEXT_RE.search(line):
                    continue
                findings.append(f"{relative}:{line_number}: credential: bare {len(match.group(0))}-char hex token")

        if public_email is not None:
            for match in _EMAIL_RE.finditer(text):
                address = match.group(0)
                if address != public_email:
                    line_number = text.count("\n", 0, match.start()) + 1
                    findings.append(f"{relative}:{line_number}: non_public_email: {address}")

        for match in _ABSOLUTE_PATH_RE.finditer(text):
            line_number = text.count("\n", 0, match.start()) + 1
            findings.append(f"{relative}:{line_number}: absolute_local_path: {match.group(0)}")

        for match in _INTERNAL_HOSTNAME_RE.finditer(text):
            line_number = text.count("\n", 0, match.start()) + 1
            findings.append(f"{relative}:{line_number}: internal_hostname: {match.group(0)}")

        for match in _PRIVATE_REPO_SUFFIX_RE.finditer(text):
            line_number = text.count("\n", 0, match.start()) + 1
            findings.append(f"{relative}:{line_number}: private_repo_reference: {match.group(0)}")
        for slug in sorted(PRIVATE_REPO_SLUGS):
            for match in re.finditer(rf"\bdocxology/{re.escape(slug)}\b", text):
                line_number = text.count("\n", 0, match.start()) + 1
                findings.append(f"{relative}:{line_number}: private_repo_reference: {match.group(0)}")

    return findings


def check_release_boundary(project_root: Path) -> list[str]:
    """Scan every git-tracked file in ``project_root`` for a public/private boundary finding."""
    public_email = _declared_public_email(project_root)
    paths = tracked_files(project_root)
    return scan_paths(paths, project_root, public_email)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the release-boundary scan."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="project root directory")
    return parser


def main() -> int:
    """Report boundary findings; return non-zero while any remain."""
    args = build_parser().parse_args()
    root = args.project_root.resolve()

    findings = check_release_boundary(root)
    for message in findings:
        print(f"release boundary: {message}", file=sys.stderr)
    print(f"release boundary: {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
