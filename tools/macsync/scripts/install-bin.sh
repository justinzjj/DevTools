#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="${MACSYNC_PREFIX:-$HOME/.local}"
BIN_DIR="$PREFIX/bin"

"$ROOT/scripts/build-bin.sh" >/dev/null
mkdir -p "$BIN_DIR"
install -m 0755 "$ROOT/dist/macsync" "$BIN_DIR/macsync"
install -m 0755 "$ROOT/dist/macsync-server" "$BIN_DIR/macsync-server"

MACSYNC_VERSION="$("$BIN_DIR/macsync" version)"

cat <<EOF
============================================================
macsync install succeeded
============================================================

Installed commands:
  $BIN_DIR/macsync
  $BIN_DIR/macsync-server

Verification:
  $MACSYNC_VERSION

Try:
  macsync version
  macsync init-config
  macsync list

If ~/.local/bin is not in PATH:
  export PATH="$BIN_DIR:\$PATH"
============================================================
EOF
