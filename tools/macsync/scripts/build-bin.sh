#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT/build/zipapp"
DIST_DIR="$ROOT/dist"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/macsync-client/macsync" "$BUILD_DIR/macsync-server/macsync" "$DIST_DIR"

rsync -a "$ROOT/src/macsync/" "$BUILD_DIR/macsync-client/macsync/"
rsync -a "$ROOT/src/macsync/" "$BUILD_DIR/macsync-server/macsync/"

cat > "$BUILD_DIR/macsync-client/__main__.py" <<'PY'
from macsync.cli import entrypoint

entrypoint()
PY

cat > "$BUILD_DIR/macsync-server/__main__.py" <<'PY'
from macsync.server_cli import entrypoint

entrypoint()
PY

python3 -m zipapp "$BUILD_DIR/macsync-client" \
  --python "/usr/bin/env python3" \
  --output "$DIST_DIR/macsync"

python3 -m zipapp "$BUILD_DIR/macsync-server" \
  --python "/usr/bin/env python3" \
  --output "$DIST_DIR/macsync-server"

chmod +x "$DIST_DIR/macsync" "$DIST_DIR/macsync-server"

cat <<EOF
============================================================
macsync build succeeded
============================================================

Executable artifacts:
  $DIST_DIR/macsync
  $DIST_DIR/macsync-server

Quick check:
  "$DIST_DIR/macsync" version
  "$DIST_DIR/macsync-server" compose --data-dir /tmp/macsync-gitea-test

Install to your user bin with:
  "$ROOT/scripts/install-bin.sh"

Or install manually with:
  install -m 0755 "$DIST_DIR/macsync" "$HOME/.local/bin/macsync"
  install -m 0755 "$DIST_DIR/macsync-server" "$HOME/.local/bin/macsync-server"

If ~/.local/bin is not in PATH:
  export PATH="$HOME/.local/bin:\$PATH"
============================================================
EOF
