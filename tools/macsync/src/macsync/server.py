from __future__ import annotations


def build_init_repo_commands(git_root: str, repos: list[str], owner: str | None = None) -> list[list[str]]:
    root = git_root.rstrip("/")
    commands = [["mkdir", "-p", root]]
    for repo in repos:
        commands.append(["git", "init", "--bare", f"{root}/{repo}"])
    if owner:
        commands.append(["chown", "-R", owner, root])
    return commands


def build_gitea_compose(http_port: int = 3000, ssh_port: int = 2222, data_dir: str = "/srv/gitea") -> str:
    return f"""services:
  gitea:
    image: gitea/gitea:latest
    container_name: macsync-gitea
    environment:
      - USER_UID=1000
      - USER_GID=1000
    restart: unless-stopped
    volumes:
      - {data_dir}:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "{http_port}:3000"
      - "{ssh_port}:22"
"""
