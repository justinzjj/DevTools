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
    origin_ahead, origin_behind = _parse_divergence(
        runner.run(repo.path, ["rev-list", "--left-right", "--count", f"HEAD...{github_remote}/{repo.branch}"])
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


def build_setup_remote_commands(
    repo: RepoConfig,
    sync_remote: str,
    gitea_host: str,
    gitea_owner: str,
    gitea_ssh_user: str,
) -> list[list[str]]:
    url = f"{gitea_ssh_user}@{gitea_host}:{gitea_owner}/{repo.resolved_gitea_repo()}.git"
    return [["git", "remote", "add", sync_remote, url]]


def run_commands(cwd: Path, commands: list[list[str]], dry_run: bool = False) -> None:
    for command in commands:
        print(f"{cwd}: {' '.join(command)}")
        if not dry_run:
            subprocess.run(command, cwd=cwd, check=True)


def _parse_divergence(output: str) -> tuple[int, int]:
    left, right = output.strip().split()
    return int(left), int(right)
