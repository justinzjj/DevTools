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
gitea_ssh_port:
gitea_owner: justin
repos:
  - name: ExampleRepo
    path: ~/ICT/path/to/ExampleRepo
    branch: main
    gitea_repo: ExampleRepo
    github: git@github.com:justinzjj/ExampleRepo.git
    ignore:
      - "**/.DS_Store"
workspaces:
  - name: personal-knowledge
    root: ~/ICT/1-个人知识库
    root_repo: personal-knowledge-root
    branch: main
    auto_discover_nested_git: true
    ignore:
      - "**/.DS_Store"
      - ".trash/**"
      - ".obsidian/workspace*"
      - "**/node_modules/**"
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
class WorkspaceConfig:
    name: str
    root: Path
    root_repo: str
    branch: str = "main"
    auto_discover_nested_git: bool = True
    ignore: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MacsyncConfig:
    sync_remote: str
    github_remote: str
    gitea_host: str
    gitea_web_url: str
    gitea_ssh_user: str
    gitea_ssh_port: int | None
    gitea_owner: str
    repos: list[RepoConfig]
    workspaces: list[WorkspaceConfig] = field(default_factory=list)


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
    workspaces = [
        WorkspaceConfig(
            name=str(item["name"]),
            root=Path(str(item["root"])).expanduser(),
            root_repo=str(item.get("root_repo", f"{item['name']}-root")),
            branch=str(item.get("branch", "main")),
            auto_discover_nested_git=_clean_bool(item.get("auto_discover_nested_git", "true")),
            ignore=list(item.get("ignore", [])),
        )
        for item in data.get("workspaces", [])
    ]
    return MacsyncConfig(
        sync_remote=str(data.get("sync_remote", "macsync")),
        github_remote=str(data.get("github_remote", "origin")),
        gitea_host=str(data["gitea_host"]),
        gitea_web_url=str(data.get("gitea_web_url", f"http://{data['gitea_host']}:3000")),
        gitea_ssh_user=str(data.get("gitea_ssh_user", "git")),
        gitea_ssh_port=_clean_optional_int(data.get("gitea_ssh_port")),
        gitea_owner=str(data["gitea_owner"]),
        repos=repos,
        workspaces=workspaces,
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
    if not config.repos and not config.workspaces:
        issues.append("no repos or workspaces configured")
    for repo in config.repos:
        if not repo.path.exists():
            issues.append(f"{repo.name}: missing local path: {repo.path}")
            continue
        if not (repo.path / ".git").exists():
            issues.append(f"{repo.name}: local path is not a git repository: {repo.path}")
    for workspace in config.workspaces:
        if not workspace.root.exists():
            issues.append(f"{workspace.name}: missing workspace root: {workspace.root}")
            continue
        if not (workspace.root / ".git").exists():
            issues.append(f"{workspace.name}: workspace root is not a git repository: {workspace.root}")
    return issues


def append_repos_to_config(config_path: str | Path, repo_names: list[str], base_path: str | Path) -> list[str]:
    path = Path(config_path).expanduser()
    config = load_config(path)
    existing = {repo.resolved_gitea_repo() for repo in config.repos}
    base_text = str(base_path)
    added = [name for name in repo_names if name not in existing]
    if not added:
        return []

    with path.open("a", encoding="utf-8") as handle:
        for name in added:
            handle.write(
                "\n"
                f"  - name: {name}\n"
                f"    path: {base_text.rstrip('/')}/{name}\n"
                "    branch: main\n"
                f"    gitea_repo: {name}\n"
            )
    return added


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


def _clean_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return int(text)


def _clean_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "on"}
