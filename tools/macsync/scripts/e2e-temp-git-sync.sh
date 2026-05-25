#!/usr/bin/env bash
set -euo pipefail

ROOT="${MACSYNC_E2E_ROOT:-$(mktemp -d "${TMPDIR:-/tmp}/macsync-e2e.XXXXXX")}"
MACSYNC_BIN="${MACSYNC_BIN:-macsync}"
GIT_USER_NAME="${GIT_USER_NAME:-macsync-test}"
GIT_USER_EMAIL="${GIT_USER_EMAIL:-macsync-test@example.invalid}"

mkdir -p "$ROOT"
BARE="$ROOT/server/demo.git"
NODE_A="$ROOT/node-a/demo"
NODE_B="$ROOT/node-b/demo"
CONFIG_A="$ROOT/node-a/config.yml"
CONFIG_B="$ROOT/node-b/config.yml"

mkdir -p "$(dirname "$BARE")" "$ROOT/node-a" "$ROOT/node-b"
git init --bare "$BARE" >/dev/null

git clone "$BARE" "$NODE_A" >/dev/null
git -C "$NODE_A" config user.name "$GIT_USER_NAME"
git -C "$NODE_A" config user.email "$GIT_USER_EMAIL"
printf "hello from node-a\n" > "$NODE_A/README.md"
git -C "$NODE_A" add README.md
git -C "$NODE_A" commit -m "initial test commit" >/dev/null
git -C "$NODE_A" push origin main >/dev/null 2>&1 || git -C "$NODE_A" push origin master >/dev/null

git clone "$BARE" "$NODE_B" >/dev/null
git -C "$NODE_B" config user.name "$GIT_USER_NAME"
git -C "$NODE_B" config user.email "$GIT_USER_EMAIL"

BRANCH="$(git -C "$NODE_A" branch --show-current)"
git -C "$NODE_A" remote add macsync "$BARE"
git -C "$NODE_B" remote add macsync "$BARE"

cat > "$CONFIG_A" <<EOF
sync_remote: macsync
github_remote: origin
gitea_host: local-test
gitea_web_url: http://local-test:3000
gitea_ssh_user: git
gitea_owner: justin
repos:
  - name: demo
    path: $NODE_A
    branch: $BRANCH
    gitea_repo: demo
EOF

cat > "$CONFIG_B" <<EOF
sync_remote: macsync
github_remote: origin
gitea_host: local-test
gitea_web_url: http://local-test:3000
gitea_ssh_user: git
gitea_owner: justin
repos:
  - name: demo
    path: $NODE_B
    branch: $BRANCH
    gitea_repo: demo
EOF

printf "handoff line\n" >> "$NODE_A/README.md"
"$MACSYNC_BIN" --config "$CONFIG_A" handoff --message "wip: e2e handoff" >/dev/null
"$MACSYNC_BIN" --config "$CONFIG_B" sync >/dev/null

grep -q "handoff line" "$NODE_B/README.md"

cat <<EOF
macsync temporary Git sync test passed.
  root: $ROOT
  branch: $BRANCH
  node-a: $NODE_A
  node-b: $NODE_B
EOF

