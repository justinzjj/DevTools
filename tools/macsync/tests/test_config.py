from pathlib import Path

from macsync.config import DEFAULT_CONFIG_TEMPLATE, load_config, validate_config


def test_load_config_expands_repo_paths(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    config = tmp_path / "macsync.yml"
    config.write_text(
        """
sync_remote: macsync
github_remote: origin
gitea_host: codex-linux-wg
gitea_web_url: http://codex-linux-wg:3000
gitea_ssh_user: git
gitea_ssh_port: 2222
gitea_owner: justin
repos:
  - name: DevTools
    path: ~/ICT/4-code/0-DevTools/DevTools
    branch: main
    gitea_repo: DevTools
    github: git@github.com:justinzjj/DevTools.git
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(home))

    loaded = load_config(config)

    assert loaded.sync_remote == "macsync"
    assert loaded.gitea_host == "codex-linux-wg"
    assert loaded.gitea_web_url == "http://codex-linux-wg:3000"
    assert loaded.gitea_ssh_user == "git"
    assert loaded.gitea_ssh_port == 2222
    assert loaded.gitea_owner == "justin"
    assert loaded.repos[0].name == "DevTools"
    assert loaded.repos[0].gitea_repo == "DevTools"
    assert loaded.repos[0].path == Path(home / "ICT/4-code/0-DevTools/DevTools")


def test_load_config_supports_workspace_mappings(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    config = tmp_path / "macsync.yml"
    config.write_text(
        """
sync_remote: macsync
github_remote: origin
gitea_host: codex-linux-wg
gitea_owner: justin
workspaces:
  - name: personal-knowledge
    root: ~/ICT/1-个人知识库
    root_repo: personal-knowledge-root
    branch: main
    auto_discover_nested_git: true
    ignore:
      - "**/.DS_Store"
      - "附件/**"
repos:
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(home))

    loaded = load_config(config)

    assert loaded.workspaces[0].name == "personal-knowledge"
    assert loaded.workspaces[0].root == Path(home / "ICT/1-个人知识库")
    assert loaded.workspaces[0].root_repo == "personal-knowledge-root"
    assert loaded.workspaces[0].auto_discover_nested_git is True
    assert loaded.workspaces[0].ignore == ["**/.DS_Store", "附件/**"]


def test_default_config_template_contains_editable_mapping():
    assert "repos:" in DEFAULT_CONFIG_TEMPLATE
    assert "path:" in DEFAULT_CONFIG_TEMPLATE
    assert "gitea_repo:" in DEFAULT_CONFIG_TEMPLATE


def test_validate_config_reports_missing_local_path(tmp_path):
    config = tmp_path / "macsync.yml"
    config.write_text(
        """
sync_remote: macsync
github_remote: origin
gitea_host: codex-linux-wg
gitea_owner: justin
repos:
  - name: MissingRepo
    path: /tmp/definitely-missing-macsync-path
    branch: main
    gitea_repo: MissingRepo
""".strip(),
        encoding="utf-8",
    )

    loaded = load_config(config)
    issues = validate_config(loaded)

    assert any("missing local path" in issue for issue in issues)
