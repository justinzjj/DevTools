from pathlib import Path

from macsync.config import RepoConfig, append_repos_to_config
from macsync.git_ops import build_clone_commands
from macsync.gitea import parse_repo_names


def test_parse_repo_names_from_gitea_response():
    repos = parse_repo_names(
        [
            {"name": "DevTools", "full_name": "justin/DevTools"},
            {"name": "CrossDataGen", "full_name": "justin/CrossDataGen"},
        ]
    )

    assert repos == ["DevTools", "CrossDataGen"]


def test_append_repos_to_config_adds_missing_repos_only(tmp_path):
    config = tmp_path / "config.yml"
    config.write_text(
        """
sync_remote: macsync
github_remote: origin
gitea_host: codex-linux-wg
gitea_web_url: http://codex-linux-wg:3000
gitea_ssh_user: git
gitea_owner: justin
repos:
  - name: DevTools
    path: ~/ICT/DevTools
    branch: main
    gitea_repo: DevTools
""".strip(),
        encoding="utf-8",
    )

    added = append_repos_to_config(config, ["DevTools", "CrossDataGen"], Path("~/ICT/macsync"))

    text = config.read_text(encoding="utf-8")
    assert added == ["CrossDataGen"]
    assert text.count("name: DevTools") == 1
    assert "name: CrossDataGen" in text
    assert "path: ~/ICT/macsync/CrossDataGen" in text


def test_build_clone_commands_skips_existing_path(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    missing = tmp_path / "missing"
    repos = [
        RepoConfig(name="Existing", path=existing, branch="main", gitea_repo="Existing"),
        RepoConfig(name="Missing", path=missing, branch="main", gitea_repo="Missing"),
    ]

    commands = build_clone_commands(
        repos,
        sync_remote="macsync",
        gitea_host="codex-linux-wg",
        gitea_owner="justin",
        gitea_ssh_user="git",
    )

    assert commands == [
        (
            missing.parent,
            ["git", "clone", "--origin", "macsync", "git@codex-linux-wg:justin/Missing.git", str(missing)],
        )
    ]
