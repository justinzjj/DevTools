from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("~/.config/macsync/config.yml")
DEFAULT_CONFIG_TEMPLATE = """sync_remote: macsync
github_remote: origin
gitea_host: codex-linux-wg
gitea_web_url: http://codex-linux-wg:3000
gitea_ssh_user: git
gitea_owner: justin
repos:
  - name: ExampleRepo
    path: ~/ICT/path/to/ExampleRepo
    branch: main
    gitea_repo: ExampleRepo
    github: git@github.com:justinzjj/ExampleRepo.git
    ignore:
      - "**/.DS_Store"
"""


@dataclass(frozen=True)
class RepoConfig:
    name: str
    path: Path
    branch: str = "main"
    gitea_repo: str | None = None
    github: str | None = None
    ignore: list[str] = field(default_factory=list)

    def resolved_gitea_repo(self) -> str:
        return self.gitea_repo or self.name


@dataclass(frozen=True)
class MacsyncConfig:
    sync_remote: str
    github_remote: str
    gitea_host: str
    gitea_web_url: str
    gitea_ssh_user: str
    gitea_owner: str
    repos: list[RepoConfig]


def load_config(path: str | Path | None = None) -> MacsyncConfig:
    config_path = Path(path).expanduser() if path else DEFAULT_CONFIG_PATH.expanduser()
    data = _parse_simple_yaml(config_path.read_text(encoding="utf-8"))
    repos = [
        RepoConfig(
            name=str(item["name"]),
            path=Path(str(item["path"])).expanduser(),
            branch=str(item.get("branch", "main")),
            gitea_repo=item.get("gitea_repo"),
            github=item.get("github"),
            ignore=list(item.get("ignore", [])),
        )
        for item in data.get("repos", [])
    ]
    return MacsyncConfig(
        sync_remote=str(data.get("sync_remote", "macsync")),
        github_remote=str(data.get("github_remote", "origin")),
        gitea_host=str(data["gitea_host"]),
        gitea_web_url=str(data.get("gitea_web_url", f"http://{data['gitea_host']}:3000")),
        gitea_ssh_user=str(data.get("gitea_ssh_user", "git")),
        gitea_owner=str(data["gitea_owner"]),
        repos=repos,
    )


def write_default_config(path: str | Path, overwrite: bool = False) -> Path:
    config_path = Path(path).expanduser()
    if config_path.exists() and not overwrite:
        raise FileExistsError(f"config already exists: {config_path}")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(DEFAULT_CONFIG_TEMPLATE, encoding="utf-8")
    return config_path


def validate_config(config: MacsyncConfig) -> list[str]:
    issues: list[str] = []
    if not config.repos:
        issues.append("no repos configured")
    for repo in config.repos:
        if not repo.path.exists():
            issues.append(f"{repo.name}: missing local path: {repo.path}")
            continue
        if not (repo.path / ".git").exists():
            issues.append(f"{repo.name}: local path is not a git repository: {repo.path}")
    return issues


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the small YAML subset used by macsync config templates."""
    result: dict[str, Any] = {}
    current_list: str | None = None
    current_item: dict[str, Any] | None = None
    current_nested_list: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0:
            current_nested_list = None
            current_item = None
            if stripped.endswith(":"):
                key = stripped[:-1]
                result[key] = []
                current_list = key
            else:
                key, value = stripped.split(":", 1)
                result[key] = _clean_scalar(value)
                current_list = None
            continue

        if current_list is None:
            continue

        if indent == 2 and stripped.startswith("- "):
            current_item = {}
            result[current_list].append(current_item)
            body = stripped[2:]
            if body:
                key, value = body.split(":", 1)
                current_item[key] = _clean_scalar(value)
            continue

        if current_item is not None and indent == 4:
            if stripped.endswith(":"):
                current_nested_list = stripped[:-1]
                current_item[current_nested_list] = []
            else:
                key, value = stripped.split(":", 1)
                current_item[key] = _clean_scalar(value)
            continue

        if current_item is not None and current_nested_list and indent == 6 and stripped.startswith("- "):
            current_item[current_nested_list].append(_clean_scalar(stripped[2:]))

    return result


def _clean_scalar(value: str) -> str:
    cleaned = value.strip()
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (
        cleaned.startswith("'") and cleaned.endswith("'")
    ):
        return cleaned[1:-1]
    return cleaned
