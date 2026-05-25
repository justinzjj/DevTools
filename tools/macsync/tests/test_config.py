from pathlib import Path

from macsync.config import load_config


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
    assert loaded.gitea_owner == "justin"
    assert loaded.repos[0].name == "DevTools"
    assert loaded.repos[0].gitea_repo == "DevTools"
    assert loaded.repos[0].path == Path(home / "ICT/4-code/0-DevTools/DevTools")
