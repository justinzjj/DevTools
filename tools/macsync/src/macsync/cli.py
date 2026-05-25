from __future__ import annotations

import argparse
import socket
import subprocess
import sys
from pathlib import Path

from macsync import __version__
from macsync.config import DEFAULT_CONFIG_PATH, MacsyncConfig, RepoConfig, load_config, validate_config, write_default_config
from macsync.git_ops import GitRunner, build_handoff_commands, build_setup_remote_commands, inspect_repo, run_commands


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="macsync")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH.expanduser()))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version")
    init_config = sub.add_parser("init-config")
    init_config.add_argument("--force", action="store_true")
    sub.add_parser("list")
    sub.add_parser("doctor")
    sub.add_parser("status")
    setup = sub.add_parser("setup-remotes")
    setup.add_argument("--dry-run", action="store_true")
    sync = sub.add_parser("sync")
    sync.add_argument("--dry-run", action="store_true")
    handoff = sub.add_parser("handoff")
    handoff.add_argument("--dry-run", action="store_true")
    handoff.add_argument("--message")
    backup = sub.add_parser("backup")
    backup.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "version":
        print(f"macsync {__version__}")
        return 0
    if args.command == "init-config":
        path = write_default_config(args.config, overwrite=args.force)
        print(f"wrote config template: {path}")
        return 0

    config = load_config(args.config)
    if args.command == "list":
        _print_repo_list(config)
    elif args.command == "doctor":
        return _doctor(config)
    elif args.command == "status":
        _print_status(config)
    elif args.command == "setup-remotes":
        _setup_remotes(config, dry_run=args.dry_run)
    elif args.command == "sync":
        _sync(config, dry_run=args.dry_run)
    elif args.command == "handoff":
        _handoff(config, dry_run=args.dry_run, message=args.message)
    elif args.command == "backup":
        _backup(config, dry_run=args.dry_run)
    return 0


def entrypoint() -> None:
    raise SystemExit(main())


def _print_repo_list(config: MacsyncConfig) -> None:
    for repo in config.repos:
        remote = f"{config.gitea_ssh_user}@{config.gitea_host}:{config.gitea_owner}/{repo.resolved_gitea_repo()}.git"
        web = f"{config.gitea_web_url.rstrip('/')}/{config.gitea_owner}/{repo.resolved_gitea_repo()}"
        print(f"{repo.name}\n  remote: {remote}\n  web:    {web}\n  local:  {repo.path}\n  branch: {repo.branch}")


def _print_status(config: MacsyncConfig) -> None:
    runner = GitRunner()
    for repo in config.repos:
        status = inspect_repo(repo, runner, sync_remote=config.sync_remote, github_remote=config.github_remote)
        print(
            f"{status.name}: branch={status.branch} dirty={status.dirty_count} "
            f"{config.sync_remote}=+{status.sync_ahead}/-{status.sync_behind} "
            f"{config.github_remote}=+{status.origin_ahead}/-{status.origin_behind}"
        )


def _doctor(config: MacsyncConfig) -> int:
    issues = validate_config(config)
    if not issues:
        print("macsync config ok")
        return 0
    for issue in issues:
        print(f"ISSUE: {issue}")
    return 1


def _setup_remotes(config: MacsyncConfig, dry_run: bool) -> None:
    for repo in config.repos:
        commands = build_setup_remote_commands(
            repo,
            config.sync_remote,
            config.gitea_host,
            config.gitea_owner,
            config.gitea_ssh_user,
        )
        run_commands(repo.path, commands, dry_run=dry_run)


def _sync(config: MacsyncConfig, dry_run: bool) -> None:
    for repo in config.repos:
        commands = [
            ["git", "fetch", config.sync_remote],
            ["git", "pull", "--ff-only", config.sync_remote, repo.branch],
        ]
        run_commands(repo.path, commands, dry_run=dry_run)


def _handoff(config: MacsyncConfig, dry_run: bool, message: str | None) -> None:
    host = socket.gethostname().split(".")[0]
    msg = message or f"wip: handoff from {host}"
    for repo in config.repos:
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=repo.path, text=True, stdout=subprocess.PIPE, check=True).stdout.strip())
        commands = build_handoff_commands(repo, dirty=dirty, sync_remote=config.sync_remote, message=msg)
        run_commands(repo.path, commands, dry_run=dry_run)


def _backup(config: MacsyncConfig, dry_run: bool) -> None:
    for repo in config.repos:
        commands = [
            ["git", "push", config.sync_remote, repo.branch],
            ["git", "push", config.github_remote, repo.branch],
        ]
        run_commands(repo.path, commands, dry_run=dry_run)


if __name__ == "__main__":
    entrypoint()
