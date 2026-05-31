#!/usr/bin/env bash
set -euo pipefail

ROOT="${MACSYNC_E2E_ROOT:-$(mktemp -d "${TMPDIR:-/tmp}/macsync-workspace-e2e.XXXXXX")}"
MACSYNC_BIN="${MACSYNC_BIN:-macsync}"
GIT_USER_NAME="${GIT_USER_NAME:-macsync-test}"
GIT_USER_EMAIL="${GIT_USER_EMAIL:-macsync-test@example.invalid}"
LOG_DIR="${MACSYNC_E2E_LOG_DIR:-$ROOT/logs}"
LOG_FILE="$LOG_DIR/workspace-e2e-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$ROOT" "$LOG_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "============================================================"
echo "macsync workspace e2e started"
echo "============================================================"
echo "root: $ROOT"
echo "log:  $LOG_FILE"
echo "bin:  $MACSYNC_BIN"

SERVER="$ROOT/server"
NODE_A="$ROOT/node-a/1-个人知识库"
NODE_B="$ROOT/node-b/1-个人知识库"
CONFIG_A="$ROOT/node-a/config.yml"
CONFIG_B="$ROOT/node-b/config.yml"
ROOT_BARE="$SERVER/personal-knowledge-root.git"
NESTED_BARE="$SERVER/CrossDataGen.git"
NESTED_REL="4-论文工作/4-CrossDataGen/1-实验/CrossDataGen"

mkdir -p "$SERVER" "$(dirname "$NODE_A")" "$(dirname "$NODE_B")"
git init --bare "$ROOT_BARE" >/dev/null
git init --bare "$NESTED_BARE" >/dev/null

git clone "$ROOT_BARE" "$NODE_A" >/dev/null
git -C "$NODE_A" config user.name "$GIT_USER_NAME"
git -C "$NODE_A" config user.email "$GIT_USER_EMAIL"
git -C "$NODE_A" remote add macsync "$ROOT_BARE"
mkdir -p "$NODE_A/0-每日记录" "$NODE_A/附件" "$NODE_A/$(dirname "$NESTED_REL")"
printf "day one\n" > "$NODE_A/0-每日记录/today.md"
printf "binary-like attachment placeholder\n" > "$NODE_A/附件/large.txt"
git -C "$NODE_A" add -A
git -C "$NODE_A" commit -m "initial workspace root" >/dev/null
BRANCH="$(git -C "$NODE_A" branch --show-current)"
git -C "$NODE_A" push macsync "$BRANCH" >/dev/null

git clone "$NESTED_BARE" "$NODE_A/$NESTED_REL" >/dev/null
git -C "$NODE_A/$NESTED_REL" config user.name "$GIT_USER_NAME"
git -C "$NODE_A/$NESTED_REL" config user.email "$GIT_USER_EMAIL"
git -C "$NODE_A/$NESTED_REL" remote add macsync "$NESTED_BARE"
printf "print('hello workspace')\n" > "$NODE_A/$NESTED_REL/main.py"
git -C "$NODE_A/$NESTED_REL" add main.py
git -C "$NODE_A/$NESTED_REL" commit -m "initial nested project" >/dev/null
git -C "$NODE_A/$NESTED_REL" push macsync "$BRANCH" >/dev/null

cat > "$CONFIG_A" <<EOF
sync_remote: macsync
github_remote: origin
gitea_host: local-test
gitea_web_url: http://local-test:3000
gitea_ssh_user: git
gitea_owner: justin
workspaces:
  - name: personal-knowledge
    root: $NODE_A
    root_repo: personal-knowledge-root
    branch: $BRANCH
    auto_discover_nested_git: true
    ignore:
      - "**/.DS_Store"
      - "附件/**"
repos:
EOF

cat > "$CONFIG_B" <<EOF
sync_remote: macsync
github_remote: origin
gitea_host: local-test
gitea_web_url: http://local-test:3000
gitea_ssh_user: git
gitea_owner: justin
workspaces:
  - name: personal-knowledge
    root: $NODE_B
    root_repo: personal-knowledge-root
    branch: $BRANCH
    auto_discover_nested_git: true
    ignore:
      - "**/.DS_Store"
      - "附件/**"
repos:
EOF

echo "[node-a] discover workspace"
"$MACSYNC_BIN" --config "$CONFIG_A" workspace discover personal-knowledge

echo "[node-a] apply ignore and handoff root/nested"
printf "handoff root line\n" >> "$NODE_A/0-每日记录/today.md"
printf "print('node a change')\n" >> "$NODE_A/$NESTED_REL/main.py"
"$MACSYNC_BIN" --config "$CONFIG_A" workspace handoff personal-knowledge --message "wip: workspace e2e handoff"

echo "[node-b] clone root and nested repositories"
git clone "$ROOT_BARE" "$NODE_B" >/dev/null
git -C "$NODE_B" config user.name "$GIT_USER_NAME"
git -C "$NODE_B" config user.email "$GIT_USER_EMAIL"
git -C "$NODE_B" remote add macsync "$ROOT_BARE"
mkdir -p "$NODE_B/$(dirname "$NESTED_REL")"
git clone "$NESTED_BARE" "$NODE_B/$NESTED_REL" >/dev/null
git -C "$NODE_B/$NESTED_REL" config user.name "$GIT_USER_NAME"
git -C "$NODE_B/$NESTED_REL" config user.email "$GIT_USER_EMAIL"
git -C "$NODE_B/$NESTED_REL" remote add macsync "$NESTED_BARE"

echo "[node-b] sync workspace"
"$MACSYNC_BIN" --config "$CONFIG_B" workspace sync personal-knowledge

grep -Fq "handoff root line" "$NODE_B/0-每日记录/today.md"
grep -Fq "node a change" "$NODE_B/$NESTED_REL/main.py"
grep -Fq "4-论文工作/4-CrossDataGen/1-实验/CrossDataGen" "$NODE_A/.gitignore"
grep -Fq "4-论文工作/4-CrossDataGen/1-实验/CrossDataGen/**" "$NODE_A/.gitignore"
if git -C "$NODE_A" ls-files -s "$NESTED_REL" | grep -q "160000"; then
  echo "ERROR: workspace root committed nested repository as a gitlink"
  exit 1
fi

echo "============================================================"
echo "macsync workspace e2e passed"
echo "============================================================"
echo "root: $ROOT"
echo "log:  $LOG_FILE"
echo "branch: $BRANCH"
