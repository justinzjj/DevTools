from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
from pathlib import Path

from macsync import __version__
from macsync.config import DEFAULT_CONFIG_PATH, MacsyncConfig, RepoConfig, append_repos_to_config, load_config, validate_config, write_default_config
from macsync.git_ops import GitRunner, build_clone_commands, build_handoff_commands, build_setup_remote_commands, build_sync_commands, inspect_repo, run_commands
from macsync.gitea import discover_repo_names
from macsync.workspace import apply_workspace_gitignore, build_workspace_repos, find_workspace, load_workspace_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="macsync")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH.expanduser()))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version")
    init_config = sub.add_parser("init-config")
    init_config.add_argument("--force", action="store_true")
    sub.add_parser("list")
    sub.add_parser("doctor")
    discover = sub.add_parser("discover")
    discover.add_argument("--token-env", default="MACSYNC_GITEA_TOKEN")
    adopt = sub.add_parser("adopt")
    adopt.add_argument("--base", required=True)
    adopt.add_argument("--repo", action="append", dest="repos")
    adopt.add_argument("--all", action="store_true")
    adopt.add_argument("--token-env", default="MACSYNC_GITEA_TOKEN")
    clone = sub.add_parser("clone")
    clone.add_argument("--repo", action="append", dest="repos")
    clone.add_argument("--all", action="store_true")
    clone.add_argument("--dry-run", action="store_true")
    sub.add_parser("status")
    setup = sub.add_parser("setup-remotes")
    setup.add_argument("--dry-run", action="store_true")
    sync = sub.add_parser("sync")
    sync.add_argument("--dry-run", action="store_true")
    sync.add_argument("--merge", action="store_true", help="Allow Git to create merge commits instead of requiring fast-forward only.")
    handoff = sub.add_parser("handoff")
    handoff.add_argument("--dry-run", action="store_true")
    handoff.add_argument("--message")
    backup = sub.add_parser("backup")
    backup.add_argument("--dry-run", action="store_true")
    workspace = sub.add_parser("workspace")
    workspace_sub = workspace.add_subparsers(dest="workspace_command", required=True)
    workspace_sub.add_parser("list")
    workspace_discover = workspace_sub.add_parser("discover")
    workspace_discover.add_argument("name")
    workspace_clone = workspace_sub.add_parser("clone")
    workspace_clone.add_argument("name")
    workspace_clone.add_argument("--dry-run", action="store_true")
    workspace_status = workspace_sub.add_parser("status")
    workspace_status.add_argument("name")
    workspace_setup = workspace_sub.add_parser("setup-remotes")
    workspace_setup.add_argument("name")
    workspace_setup.add_argument("--dry-run", action="store_true")
    workspace_sync = workspace_sub.add_parser("sync")
    workspace_sync.add_argument("name")
    workspace_sync.add_argument("--dry-run", action="store_true")
    workspace_sync.add_argument("--merge", action="store_true")
    workspace_handoff = workspace_sub.add_parser("handoff")
    workspace_handoff.add_argument("name")
    workspace_handoff.add_argument("--dry-run", action="store_true")
    workspace_handoff.add_argument("--message")
    workspace_apply_ignore = workspace_sub.add_parser("apply-ignore")
    workspace_apply_ignore.add_argument("name")

    args = parser.parse_args(argv)
    if args.command == "version":
        print(f"macsync {__version__}")
        return 0
    if args.command == "init-config":
        path = write_default_config(args.config, overwrite=args.force)
        print(f"wrote config template: {path}")
        return 0

    try:
        config = load_config(args.config)
        if args.command == "list":
            _print_repo_list(config)
        elif args.command == "doctor":
            return _doctor(config)
        elif args.command == "discover":
            _discover(config, token_env=args.token_env)
        elif args.command == "adopt":
            _adopt(args.config, config, base=args.base, selected=args.repos, all_repos=args.all, token_env=args.token_env)
        elif args.command == "clone":
            _clone(config, selected=args.repos, all_repos=args.all, dry_run=args.dry_run)
        elif args.command == "status":
            _print_status(config)
        elif args.command == "setup-remotes":
            _setup_remotes(config, dry_run=args.dry_run)
        elif args.command == "sync":
            _sync(config, dry_run=args.dry_run, merge=args.merge)
        elif args.command == "handoff":
            _handoff(config, dry_run=args.dry_run, message=args.message)
        elif args.command == "backup":
            _backup(config, dry_run=args.dry_run)
        elif args.command == "workspace":
            _workspace(config, args)
    except subprocess.CalledProcessError as error:
        command = " ".join(str(part) for part in error.cmd)
        print(f"macsync command failed with exit code {error.returncode}: {command}", file=sys.stderr)
        return error.returncode
    return 0


def entrypoint() -> None:
    raise SystemExit(main())


def _print_repo_list(config: MacsyncConfig) -> None:
    for repo in config.repos:
        from macsync.git_ops import build_gitea_ssh_url

        remote = build_gitea_ssh_url(
            repo,
            config.gitea_host,
            config.gitea_owner,
            config.gitea_ssh_user,
            config.gitea_ssh_port,
        )
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


def _discover(config: MacsyncConfig, token_env: str) -> None:
    token = os.environ.get(token_env)
    for name in discover_repo_names(config.gitea_web_url, config.gitea_owner, token=token):
        print(name)


def _adopt(
    config_path: str,
    config: MacsyncConfig,
    base: str,
    selected: list[str] | None,
    all_repos: bool,
    token_env: str,
) -> None:
    if all_repos:
        token = os.environ.get(token_env)
        repo_names = discover_repo_names(config.gitea_web_url, config.gitea_owner, token=token)
    else:
        repo_names = selected or []
    if not repo_names:
        raise SystemExit("No repositories selected. Use --all or --repo <name>.")
    added = append_repos_to_config(config_path, repo_names, base)
    if not added:
        print("No new repositories added.")
        return
    for name in added:
        print(f"added mapping: {name}")


def _clone(config: MacsyncConfig, selected: list[str] | None, all_repos: bool, dry_run: bool) -> None:
    repos = config.repos
    if not all_repos and selected:
        wanted = set(selected)
        repos = [repo for repo in repos if repo.name in wanted or repo.resolved_gitea_repo() in wanted]
    elif not all_repos and not selected:
        raise SystemExit("No repositories selected. Use --all or --repo <name>.")

    commands = build_clone_commands(
        repos,
        sync_remote=config.sync_remote,
        gitea_host=config.gitea_host,
        gitea_owner=config.gitea_owner,
        gitea_ssh_user=config.gitea_ssh_user,
        gitea_ssh_port=config.gitea_ssh_port,
    )
    if not commands:
        print("No missing repositories to clone.")
        return
    for cwd, command in commands:
        cwd.mkdir(parents=True, exist_ok=True)
        run_commands(cwd, [command], dry_run=dry_run)


def _setup_remotes(config: MacsyncConfig, dry_run: bool) -> None:
    for repo in config.repos:
        commands = build_setup_remote_commands(
            repo,
            config.sync_remote,
            config.gitea_host,
            config.gitea_owner,
            config.gitea_ssh_user,
            config.gitea_ssh_port,
        )
        run_commands(repo.path, commands, dry_run=dry_run)


def _sync(config: MacsyncConfig, dry_run: bool, merge: bool) -> None:
    for repo in config.repos:
        commands = build_sync_commands(repo, config.sync_remote, merge=merge)
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


def _workspace(config: MacsyncConfig, args: argparse.Namespace) -> None:
    if args.workspace_command == "list":
        for workspace in config.workspaces:
            print(f"{workspace.name}\n  root:      {workspace.root}\n  root repo: {workspace.root_repo}\n  branch:    {workspace.branch}")
        return

    workspace = find_workspace(config.workspaces, args.name)
    repos = build_workspace_repos(workspace)
    workspace_config = MacsyncConfig(
        sync_remote=config.sync_remote,
        github_remote=config.github_remote,
        gitea_host=config.gitea_host,
        gitea_web_url=config.gitea_web_url,
        gitea_ssh_user=config.gitea_ssh_user,
        gitea_ssh_port=config.gitea_ssh_port,
        gitea_owner=config.gitea_owner,
        repos=repos,
        workspaces=[],
    )

    if args.workspace_command == "discover":
        for repo in repos:
            print(f"{repo.name}\n  local:  {repo.path}\n  branch: {repo.branch}\n  gitea:  {repo.resolved_gitea_repo()}")
    elif args.workspace_command == "clone":
        _workspace_clone(config, workspace, dry_run=args.dry_run)
    elif args.workspace_command == "status":
        _print_status(workspace_config)
    elif args.workspace_command == "setup-remotes":
        _setup_remotes(workspace_config, dry_run=args.dry_run)
    elif args.workspace_command == "sync":
        _sync(workspace_config, dry_run=args.dry_run, merge=args.merge)
    elif args.workspace_command == "handoff":
        gitignore = apply_workspace_gitignore(workspace)
        print(f"workspace ignore applied: {gitignore}")
        _handoff(workspace_config, dry_run=args.dry_run, message=args.message)
    elif args.workspace_command == "apply-ignore":
        gitignore = apply_workspace_gitignore(workspace)
        print(f"workspace ignore applied: {gitignore}")


def _workspace_clone(config: MacsyncConfig, workspace, dry_run: bool) -> None:
    root_repo = RepoConfig(
        name=workspace.root_repo,
        path=workspace.root,
        branch=workspace.branch,
        gitea_repo=workspace.root_repo,
    )
    root_commands = build_clone_commands(
        [root_repo],
        sync_remote=config.sync_remote,
        gitea_host=config.gitea_host,
        gitea_owner=config.gitea_owner,
        gitea_ssh_user=config.gitea_ssh_user,
        gitea_ssh_port=config.gitea_ssh_port,
    )
    for cwd, command in root_commands:
        cwd.mkdir(parents=True, exist_ok=True)
        run_commands(cwd, [command], dry_run=dry_run)

    manifest_repos = [
        RepoConfig(
            name=item.name,
            path=workspace.root / item.path,
            branch=item.branch,
            gitea_repo=item.gitea_repo,
        )
        for item in load_workspace_manifest(workspace.root)
    ]
    nested_commands = build_clone_commands(
        manifest_repos,
        sync_remote=config.sync_remote,
        gitea_host=config.gitea_host,
        gitea_owner=config.gitea_owner,
        gitea_ssh_user=config.gitea_ssh_user,
        gitea_ssh_port=config.gitea_ssh_port,
    )
    if not root_commands and not nested_commands:
        print("No missing workspace repositories to clone.")
        return
    for cwd, command in nested_commands:
        cwd.mkdir(parents=True, exist_ok=True)
        run_commands(cwd, [command], dry_run=dry_run)


if __name__ == "__main__":
    entrypoint()
