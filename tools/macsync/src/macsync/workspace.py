from __future__ import annotations

from pathlib import Path

from macsync.config import RepoConfig, WorkspaceConfig


MANIFEST_PATH = Path(".macsync/workspace.yml")


class ManifestRepo:
    def __init__(self, name: str, path: Path, branch: str, gitea_repo: str):
        self.name = name
        self.path = path
        self.branch = branch
        self.gitea_repo = gitea_repo


def discover_nested_git_repos(root: Path) -> list[Path]:
    root = root.expanduser()
    nested: list[Path] = []
    for git_dir in root.rglob(".git"):
        repo_path = git_dir.parent
        if repo_path == root:
            continue
        nested.append(repo_path)
    return sorted(nested)


def build_workspace_repos(workspace: WorkspaceConfig) -> list[RepoConfig]:
    nested_paths = discover_nested_git_repos(workspace.root) if workspace.auto_discover_nested_git else []
    nested_ignores: list[str] = []
    for path in nested_paths:
        relative = path.relative_to(workspace.root).as_posix()
        nested_ignores.extend([relative, f"{relative}/**"])
    root_repo = RepoConfig(
        name=workspace.root_repo,
        path=workspace.root,
        branch=workspace.branch,
        gitea_repo=workspace.root_repo,
        ignore=[*workspace.ignore, *nested_ignores],
    )
    nested_repos = [
        RepoConfig(
            name=_repo_name_from_path(path),
            path=path,
            branch=workspace.branch,
            gitea_repo=_repo_name_from_path(path),
        )
        for path in nested_paths
    ]
    return [root_repo, *nested_repos]


def render_workspace_gitignore_block(workspace_name: str, patterns: list[str]) -> str:
    lines = [f"# >>> macsync workspace {workspace_name} >>>"]
    lines.extend(dict.fromkeys(patterns))
    lines.append(f"# <<< macsync workspace {workspace_name} <<<")
    return "\n".join(lines) + "\n"


def apply_workspace_gitignore(workspace: WorkspaceConfig) -> Path:
    repos = build_workspace_repos(workspace)
    root_repo = repos[0]
    gitignore = workspace.root / ".gitignore"
    block = render_workspace_gitignore_block(workspace.name, root_repo.ignore)
    existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    start = f"# >>> macsync workspace {workspace.name} >>>"
    end = f"# <<< macsync workspace {workspace.name} <<<"
    if start in existing and end in existing:
        before, rest = existing.split(start, 1)
        _, after = rest.split(end, 1)
        updated = before.rstrip() + "\n\n" + block + after.lstrip("\n")
    else:
        prefix = existing.rstrip()
        updated = f"{prefix}\n\n{block}" if prefix else block
    gitignore.write_text(updated, encoding="utf-8")
    write_workspace_manifest(workspace, repos[1:])
    return gitignore


def write_workspace_manifest(workspace: WorkspaceConfig, nested_repos: list[RepoConfig]) -> Path:
    manifest = workspace.root / MANIFEST_PATH
    manifest.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"workspace: {workspace.name}",
        "repos:",
    ]
    for repo in nested_repos:
        rel_path = repo.path.relative_to(workspace.root).as_posix()
        lines.extend(
            [
                f"  - name: {repo.name}",
                f"    path: {rel_path}",
                f"    branch: {repo.branch}",
                f"    gitea_repo: {repo.resolved_gitea_repo()}",
            ]
        )
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def load_workspace_manifest(root: Path) -> list[ManifestRepo]:
    manifest = root / MANIFEST_PATH
    if not manifest.exists():
        return []

    repos: list[ManifestRepo] = []
    current: dict[str, str] | None = None
    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            if current:
                repos.append(_manifest_repo_from_dict(current))
            current = {}
            body = stripped[2:]
            if body:
                key, value = body.split(":", 1)
                current[key.strip()] = value.strip()
            continue
        if current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip()
    if current:
        repos.append(_manifest_repo_from_dict(current))
    return repos


def find_workspace(workspaces: list[WorkspaceConfig], name: str) -> WorkspaceConfig:
    for workspace in workspaces:
        if workspace.name == name:
            return workspace
    available = ", ".join(workspace.name for workspace in workspaces) or "(none)"
    raise SystemExit(f"Unknown workspace: {name}. Available workspaces: {available}")


def _repo_name_from_path(path: Path) -> str:
    return path.name.replace(" ", "-")


def _manifest_repo_from_dict(item: dict[str, str]) -> ManifestRepo:
    return ManifestRepo(
        name=item["name"],
        path=Path(item["path"]),
        branch=item.get("branch", "main"),
        gitea_repo=item.get("gitea_repo", item["name"]),
    )
