#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PREFIX="${MACSYNC_PREFIX:-$HOME/.local}"
APP_HOME="${MACSYNC_APP_HOME:-$PREFIX/share/macsync}"
VENV_DIR="$APP_HOME/venv"
SRC_DIR="$APP_HOME/src"
BIN_DIR="$PREFIX/bin"

mkdir -p "$APP_HOME" "$BIN_DIR"
rm -rf "$SRC_DIR"
mkdir -p "$SRC_DIR"

rsync -a --delete \
  --exclude ".git/" \
  --exclude ".venv/" \
  --exclude "__pycache__/" \
  --exclude ".pytest_cache/" \
  "$SOURCE_DIR"/ "$SRC_DIR"/

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install "$SRC_DIR" >/dev/null

ln -sf "$VENV_DIR/bin/macsync" "$BIN_DIR/macsync"
ln -sf "$VENV_DIR/bin/macsync-server" "$BIN_DIR/macsync-server"

cat <<EOF
macsync Mac node installed.
  source: $SRC_DIR
  binary: $BIN_DIR/macsync
  server helper: $BIN_DIR/macsync-server

Add this to PATH if needed:
  export PATH="$BIN_DIR:\$PATH"
EOF
