from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from macsync.config import RepoConfig


@dataclass(frozen=True)
class RepoStatus:
    name: str
    path: Path
    branch: str
    dirty_count: int
    sync_ahead: int
    sync_behind: int
    origin_ahead: int
    origin_behind: int


class GitRunner:
    def run(self, cwd: Path, args: list[str]) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout


def inspect_repo(
    repo: RepoConfig,
    runner: GitRunner,
    sync_remote: str,
    github_remote: str,
) -> RepoStatus:
    branch = runner.run(repo.path, ["rev-parse", "--abbrev-ref", "HEAD"]).strip()
    dirty_count = len([line for line in runner.run(repo.path, ["status", "--porcelain"]).splitlines() if line])
    sync_ahead, sync_behind = _parse_divergence(
        runner.run(repo.path, ["rev-list", "--left-right", "--count", f"HEAD...{sync_remote}/{repo.branch}"])
    )
    origin_ahead, origin_behind = _safe_parse_divergence(
        runner,
        repo.path,
        ["rev-list", "--left-right", "--count", f"HEAD...{github_remote}/{repo.branch}"],
    )
    return RepoStatus(
        name=repo.name,
        path=repo.path,
        branch=branch,
        dirty_count=dirty_count,
        sync_ahead=sync_ahead,
        sync_behind=sync_behind,
        origin_ahead=origin_ahead,
        origin_behind=origin_behind,
    )


def build_handoff_commands(
    repo: RepoConfig,
    dirty: bool,
    sync_remote: str,
    message: str,
) -> list[list[str]]:
    commands: list[list[str]] = []
    if dirty:
        commands.extend(
            [
                ["git", "add", "-A"],
                ["git", "commit", "-m", message],
            ]
        )
    commands.append(["git", "push", sync_remote, repo.branch])
    return commands


def build_sync_commands(repo: RepoConfig, sync_remote: str, merge: bool = False) -> list[list[str]]:
    pull_command = ["git", "pull", sync_remote, repo.branch]
    if merge:
        pull_command.insert(2, "--no-rebase")
    else:
        pull_command.insert(2, "--ff-only")
    return [
        ["git", "fetch", sync_remote],
        pull_command,
    ]


def build_setup_remote_commands(
    repo: RepoConfig,
    sync_remote: str,
    gitea_host: str,
    gitea_owner: str,
    gitea_ssh_user: str,
    gitea_ssh_port: int | None = None,
) -> list[list[str]]:
    url = build_gitea_ssh_url(repo, gitea_host, gitea_owner, gitea_ssh_user, gitea_ssh_port)
    return [["git", "remote", "add", sync_remote, url]]


def build_gitea_ssh_url(
    repo: RepoConfig,
    gitea_host: str,
    gitea_owner: str,
    gitea_ssh_user: str,
    gitea_ssh_port: int | None = None,
) -> str:
    repo_path = f"{gitea_owner.strip('/')}/{repo.resolved_gitea_repo()}.git"
    if gitea_ssh_port:
        return f"ssh://{gitea_ssh_user}@{gitea_host}:{gitea_ssh_port}/{repo_path}"
    return f"{gitea_ssh_user}@{gitea_host}:{repo_path}"


def build_clone_commands(
    repos: list[RepoConfig],
    sync_remote: str,
    gitea_host: str,
    gitea_owner: str,
    gitea_ssh_user: str,
    gitea_ssh_port: int | None = None,
) -> list[tuple[Path, list[str]]]:
    commands: list[tuple[Path, list[str]]] = []
    for repo in repos:
        if repo.path.exists():
            continue
        remote = build_gitea_ssh_url(repo, gitea_host, gitea_owner, gitea_ssh_user, gitea_ssh_port)
        commands.append(
            (
                repo.path.parent,
                ["git", "clone", "--origin", sync_remote, remote, str(repo.path)],
            )
        )
    return commands


def run_commands(cwd: Path, commands: list[list[str]], dry_run: bool = False) -> None:
    for command in commands:
        print(f"{cwd}: {' '.join(command)}")
        if not dry_run:
            subprocess.run(command, cwd=cwd, check=True)


def _parse_divergence(output: str) -> tuple[int, int]:
    left, right = output.strip().split()
    return int(left), int(right)


def _safe_parse_divergence(runner: GitRunner, cwd: Path, args: list[str]) -> tuple[int, int]:
    try:
        return _parse_divergence(runner.run(cwd, args))
    except Exception:
        return 0, 0
