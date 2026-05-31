from macsync.cli import main
import subprocess



def test_cli_exposes_version(capsys):
    exit_code = main(["version"])

    assert exit_code == 0
    assert "macsync" in capsys.readouterr().out


def test_cli_init_config_writes_template(tmp_path):
    config_path = tmp_path / "config.yml"

    exit_code = main(["--config", str(config_path), "init-config"])

    assert exit_code == 0
    assert "repos:" in config_path.read_text(encoding="utf-8")


def test_cli_reports_git_command_failure_without_traceback(monkeypatch, tmp_path, capsys):
    config = tmp_path / "config.yml"
    config.write_text(
        """
sync_remote: macsync
github_remote: origin
gitea_host: local-test
gitea_owner: justin
repos:
""".strip(),
        encoding="utf-8",
    )

    def fail_sync(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ["git", "pull", "--no-rebase", "macsync", "main"])

    monkeypatch.setattr("macsync.cli._sync", fail_sync)

    exit_code = main(["--config", str(config), "sync"])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "macsync command failed" in captured.err
    assert "Traceback" not in captured.err


def test_cli_workspace_discover_prints_root_and_nested_repos(tmp_path, capsys):
    root = tmp_path / "knowledge"
    nested = root / "4-paper" / "CrossDataGen"
    nested.mkdir(parents=True)
    (root / ".git").mkdir()
    (nested / ".git").mkdir()
    config = tmp_path / "config.yml"
    config.write_text(
        f"""
sync_remote: macsync
github_remote: origin
gitea_host: local-test
gitea_owner: justin
workspaces:
  - name: personal-knowledge
    root: {root}
    root_repo: personal-knowledge-root
    branch: main
    auto_discover_nested_git: true
repos:
""".strip(),
        encoding="utf-8",
    )

    exit_code = main(["--config", str(config), "workspace", "discover", "personal-knowledge"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "personal-knowledge-root" in output
    assert "CrossDataGen" in output
    assert str(nested) in output
