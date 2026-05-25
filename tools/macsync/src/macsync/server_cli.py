from __future__ import annotations

import argparse
import subprocess

from macsync.server import build_gitea_compose, build_init_repo_commands


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="macsync-server")
    parser.add_argument("--git-root", default="/srv/git")
    parser.add_argument("--owner")
    parser.add_argument("--dry-run", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("repos", nargs="+")
    compose = sub.add_parser("compose")
    compose.add_argument("--http-port", type=int, default=3000)
    compose.add_argument("--ssh-port", type=int, default=2222)
    compose.add_argument("--data-dir", default="/srv/gitea")
    args = parser.parse_args(argv)

    if args.command == "init":
        commands = build_init_repo_commands(args.git_root, args.repos, owner=args.owner)
        for command in commands:
            print(" ".join(command))
            if not args.dry_run:
                subprocess.run(command, check=True)
    elif args.command == "compose":
        print(build_gitea_compose(args.http_port, args.ssh_port, args.data_dir))
    return 0


def entrypoint() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    entrypoint()
