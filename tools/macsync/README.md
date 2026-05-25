# macsync

`macsync` is a personal Git-based sync manager for a small device cluster:

- one intranet Linux server running Gitea as the local GitHub
- multiple Mac nodes as working clients
- GitHub remains available as a normal `origin` remote

The goal is to self-host a lightweight local GitHub-like sync center without changing how normal Git works.

## Architecture

```text
                  GitHub / GitLab
                       ^
                       |
                    origin
                       |
MacBook  <---->  macsync remote  <---->  Mac mini
                       |
              Linux server / Gitea
```

Each managed repository keeps two remotes:

- `origin`: GitHub or another external Git host
- `macsync`: the intranet Gitea server

`macsync` never removes or rewrites `origin`.

## Programs

`macsync-server` runs on the Linux server. It helps generate Gitea deployment config and keeps low-level bare-repo commands available for fallback use.

`macsync` runs on each Mac node. It reads a local config file, maps remote repositories to local paths, and helps run safe Git sync commands.

## Install Scripts

Build single-file executable commands:

```bash
./scripts/build-bin.sh
```

This creates:

```text
dist/macsync
dist/macsync-server
```

Install the executable commands to `~/.local/bin`:

```bash
./scripts/install-bin.sh
```

Install on a Mac node:

```bash
./scripts/install-mac-node.sh /path/to/macsync
```

Install on the Linux server:

```bash
./scripts/install-server.sh /path/to/macsync
```

Both scripts install in user space by default:

```text
~/.local/share/macsync
~/.local/bin/macsync
~/.local/bin/macsync-server
```

They do not use `sudo`, do not write `/srv/git`, and do not start Gitea.

The `install-bin.sh` path is the recommended install route for normal command-line use. The older `install-mac-node.sh` and `install-server.sh` scripts remain available when you prefer an editable Python virtual environment install.

Run the isolated safety test:

```bash
PATH="$HOME/.local/bin:$PATH" ./scripts/e2e-temp-git-sync.sh
```

The test creates a temporary bare Git repository and two temporary clones under `/tmp`, then verifies `macsync handoff` and `macsync sync`.

## Server Setup With Gitea

On the Linux server:

```bash
macsync-server compose --http-port 3000 --ssh-port 2222 --data-dir /srv/gitea > docker-compose.yml
docker compose up -d
```

Then open:

```text
http://<server>:3000
```

Create your first admin user in the Gitea setup page, then create repositories such as:

```text
justin/DevTools
justin/CrossDataGen
justin/TrustMap-doc
```

Low-level bare repository fallback is still available:

```bash
macsync-server --dry-run init DevTools.git CrossDataGen.git
```

## Mac Node Config

Create `~/.config/macsync/config.yml`:

```bash
macsync init-config
```

Then edit the generated mapping file:

```yaml
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

  - name: TrustMap-doc
    path: ~/ICT/1-个人知识库/4-论文工作/1-TrustMap
    branch: main
    gitea_repo: TrustMap-doc
    github: git@github.com:justinzjj/TrustMap-doc.git
    ignore:
      - "**/.DS_Store"
```

Show what syncs where, including Gitea web URLs:

```bash
macsync list
```

Validate the mapping file:

```bash
macsync doctor
```

Add the intranet remote to each repo:

```bash
macsync setup-remotes --dry-run
macsync setup-remotes
```

## Daily Workflow

Start work on a Mac:

```bash
macsync sync
```

Leave a Mac and hand off work:

```bash
macsync handoff
```

Push both to the intranet hub and GitHub:

```bash
macsync backup
```

Check all managed repos:

```bash
macsync status
```

## Conflict Policy

`macsync sync` uses:

```bash
git pull --ff-only macsync <branch>
```

This is intentionally conservative. If histories diverge, `macsync` stops and lets Git show the conflict. Resolve it with normal Git commands, then run `macsync handoff` again.

## Ignore Policy

Git ignore rules remain the source of truth. Put files that should not replicate between Macs into each repository's `.gitignore`, such as:

```gitignore
.DS_Store
node_modules/
.venv/
dist/
build/
*.log
```

The `ignore` field in `config.yml` is reserved for future commands that initialize or audit `.gitignore`.

## Homebrew Install Plan

For local development:

```bash
brew install python
pipx install /path/to/macsync
```

For a real Homebrew tap, publish this repository and add `Formula/macsync.rb`. A draft formula is included in `packaging/homebrew/macsync.rb`.
