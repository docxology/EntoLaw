from __future__ import annotations

from pathlib import Path

from scripts import check_release_boundary as crb

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_EMAIL = "daniel@activeinference.institute"


def _join(*parts: str) -> str:
    """Assemble a fixture string from pieces, none of which alone matches this gate's own patterns.

    This test file is itself part of the tracked tree this gate scans, so its
    negative-control fixtures cannot contain a literal secret-, path-, or
    hostname-shaped substring -- that would make this file the very finding
    it exists to catch. Every "bad" example below is built at import time
    from split pieces instead of typed as one contiguous literal, so the
    string this gate would need to match only exists once the test runs, not
    in this file's own source text.
    """
    return "".join(parts)




def test_live_tracked_tree_has_no_boundary_findings():
    """The real checkout's tracked tree carries no credential/path/email/hostname leak.

    No exemptions: the one finding that used to be tolerated here (a tracked
    ``.codegraph`` symlink into a machine-local cache) was untracked on
    2026-09-24, so any finding now is a new leak and fails.
    """
    assert crb.check_release_boundary(PROJECT_ROOT) == []


def test_tracked_files_lists_only_git_tracked_paths():
    """tracked_files() reflects `git ls-files`, not every file on disk (e.g. .venv, __pycache__)."""
    paths = crb.tracked_files(PROJECT_ROOT)
    assert paths
    # A tracked entry is a real file or a real (possibly dangling) symlink;
    # never something `git ls-files` would not itself have printed.
    assert all(path.is_file() or path.is_symlink() for path in paths)
    relative = {p.relative_to(PROJECT_ROOT) for p in paths}
    assert Path("README.md") in relative
    assert Path("pyproject.toml") in relative
    # Never a scratch/build artifact this project's own .gitignore excludes.
    assert not any(".venv" in p.parts for p in relative)
    assert not any("__pycache__" in p.parts for p in relative)


def test_clean_fixture_tree_has_no_findings(tmp_path):
    """Negative control's control arm: a small tree with nothing to flag reports nothing."""
    (tmp_path / "README.md").write_text(
        f"# Widget\n\nContact: {PUBLIC_EMAIL}\n\nSee ../sibling/README.md.\n",
        encoding="utf-8",
    )
    findings = crb.scan_paths([tmp_path / "README.md"], tmp_path, PUBLIC_EMAIL)
    assert findings == []


def test_private_key_header_is_caught(tmp_path):
    header = _join("-----BEGIN ", "RSA PRIVATE KEY", "-----")
    footer = _join("-----END ", "RSA PRIVATE KEY", "-----")
    (tmp_path / "notes.md").write_text(
        f"accidentally pasted:\n{header}\nMIIExample==\n{footer}\n", encoding="utf-8"
    )
    findings = crb.scan_paths([tmp_path / "notes.md"], tmp_path, PUBLIC_EMAIL)
    assert any(f.split(": ", 1)[1].startswith("credential:") for f in findings)


def test_aws_access_key_id_is_caught(tmp_path):
    fake_key_id = _join("AKIA", "ABCDEFGHIJKLMNOP")
    (tmp_path / "config.md").write_text(f"export AWS_ACCESS_KEY_ID={fake_key_id}\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "config.md"], tmp_path, PUBLIC_EMAIL)
    assert any("credential:" in f for f in findings)


def test_assigned_secret_is_caught(tmp_path):
    fake_secret = _join("sk-", "abcdefghijklmnopqrstuvwx")
    (tmp_path / "config.md").write_text(f'api_key: "{fake_secret}"\n', encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "config.md"], tmp_path, PUBLIC_EMAIL)
    assert any("credential:" in f for f in findings)


def test_bare_hex_token_is_caught(tmp_path):
    # A synthetic 40-char hex string in the shape of a vendor API key --
    # never a real credential value, which this check must never embed
    # anywhere (see AGENTS.md's credential-handling rules).
    fake_token = "".join(f"{i % 16:x}" for i in range(40))
    (tmp_path / "notes.md").write_text(f"my key is {fake_token} today\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "notes.md"], tmp_path, PUBLIC_EMAIL)
    assert any("credential:" in f and "hex token" in f for f in findings)


def test_pinned_github_action_sha_is_not_a_false_positive(tmp_path):
    """A 40-hex-char pinned Actions SHA is legitimate CI hygiene, not a leaked credential."""
    fake_sha = "".join(f"{(i * 7) % 16:x}" for i in range(40))
    (tmp_path / "ci.yml").write_text(f"- uses: actions/checkout@{fake_sha} # v6.0.3\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "ci.yml"], tmp_path, PUBLIC_EMAIL)
    assert findings == []


def test_non_public_email_is_caught(tmp_path):
    other_email = _join("someoneelse", "@example.com")
    (tmp_path / "notes.md").write_text(f"cc: {other_email}\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "notes.md"], tmp_path, PUBLIC_EMAIL)
    assert any(f"non_public_email: {other_email}" in f for f in findings)


def test_public_email_itself_is_not_flagged(tmp_path):
    (tmp_path / "notes.md").write_text(f"contact: {PUBLIC_EMAIL}\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "notes.md"], tmp_path, PUBLIC_EMAIL)
    assert findings == []


def test_absolute_local_path_is_caught(tmp_path):
    fake_path = _join("/Users/", "someone/Documents/GitHub/template")
    (tmp_path / "notes.md").write_text(f"cd {fake_path}\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "notes.md"], tmp_path, PUBLIC_EMAIL)
    assert any("absolute_local_path:" in f for f in findings)


def test_internal_hostname_is_caught(tmp_path):
    fake_ip = _join("192.168.", "1.5")
    (tmp_path / "notes.md").write_text(f"dashboard: http://{fake_ip}:8080/status\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "notes.md"], tmp_path, PUBLIC_EMAIL)
    assert any("internal_hostname:" in f for f in findings)


def test_private_repo_reference_is_caught(tmp_path):
    fake_repo = _join("docxology", "/operator")
    (tmp_path / "notes.md").write_text(f"see {fake_repo} for the control plane\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "notes.md"], tmp_path, PUBLIC_EMAIL)
    assert any(f"private_repo_reference: {fake_repo}" in f for f in findings)


def test_private_repo_suffix_convention_is_caught(tmp_path):
    fake_repo = _join("AGEINT", "-private")
    (tmp_path / "notes.md").write_text(f"see {fake_repo} for the internal fork\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "notes.md"], tmp_path, PUBLIC_EMAIL)
    assert any(f"private_repo_reference: {fake_repo}" in f for f in findings)


def test_tracked_symlink_to_absolute_local_path_is_caught(tmp_path):
    """A tracked symlink pointing outside the project (e.g. a local tool cache) is flagged."""
    fake_target = _join("/Users/", "someone/.omo/codegraph/projects/Widget-abc123")
    link = tmp_path / ".codegraph"
    link.symlink_to(fake_target)
    findings = crb.scan_paths([link], tmp_path, PUBLIC_EMAIL)
    assert any(
        f.startswith(".codegraph: tracked_symlink -> absolute_local_path:") and fake_target in f
        for f in findings
    )


def test_self_exclusion_covers_only_this_scanners_own_module():
    """The self-exclusion is exactly one path, not a blanket exemption that could hide a real leak."""
    assert crb._SELF_EXCLUDED_RELATIVE_PATHS == {"scripts/check_release_boundary.py"}


def test_tracked_symlink_within_project_is_not_flagged(tmp_path):
    """A symlink whose target is a relative, in-repo path is ordinary repo structure, not a leak."""
    (tmp_path / "figures").mkdir()
    link = tmp_path / "web_figures"
    link.symlink_to("figures")
    findings = crb.scan_paths([link], tmp_path, PUBLIC_EMAIL)
    assert findings == []


def test_large_binary_is_caught(tmp_path):
    big = tmp_path / "archive.zip"
    big.write_bytes(b"0" * (crb.LARGE_BINARY_BYTES + 1))
    findings = crb.scan_paths([big], tmp_path, PUBLIC_EMAIL)
    assert any("large_binary:" in f for f in findings)


def test_small_binary_is_not_flagged(tmp_path):
    small = tmp_path / "cover.png"
    small.write_bytes(b"0" * 1024)
    findings = crb.scan_paths([small], tmp_path, PUBLIC_EMAIL)
    assert findings == []


def test_public_email_disabled_when_declared_source_missing(tmp_path):
    """No CITATION.cff to read: email checking is off, never treated as 'flag everything'."""
    other_email = _join("anyone", "@example.com")
    (tmp_path / "notes.md").write_text(f"cc: {other_email}\n", encoding="utf-8")
    findings = crb.scan_paths([tmp_path / "notes.md"], tmp_path, public_email=None)
    assert findings == []


def test_main_exits_clean_on_the_live_tree(capsys, monkeypatch):
    """The thin CLI entrypoint (argv parsing, printing, exit code) reports a clean tree."""
    monkeypatch.setattr("sys.argv", ["check_release_boundary.py"])
    code = crb.main()
    captured = capsys.readouterr()
    assert code == 0, captured.err
    assert "release boundary: 0 findings" in captured.out