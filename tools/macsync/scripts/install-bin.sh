#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="${MACSYNC_PREFIX:-$HOME/.local}"
BIN_DIR="$PREFIX/bin"
ZSH_PATH_BLOCK_START="# >>> macsync user-local bin >>>"
ZSH_PATH_BLOCK_END="# <<< macsync user-local bin <<<"

"$ROOT/scripts/build-bin.sh" >/dev/null
mkdir -p "$BIN_DIR"
install -m 0755 "$ROOT/dist/macsync" "$BIN_DIR/macsync"
install -m 0755 "$ROOT/dist/macsync-server" "$BIN_DIR/macsync-server"

MACSYNC_VERSION="$("$BIN_DIR/macsync" version)"
PATH_STATUS="already available in current PATH"
SHELL_NOTE=""

ensure_zsh_path_block() {
  local target_file="$1"
  mkdir -p "$(dirname "$target_file")"
  touch "$target_file"
  if grep -Fq "$ZSH_PATH_BLOCK_START" "$target_file"; then
    return
  fi
  cat >> "$target_file" <<'EOF'

# >>> macsync user-local bin >>>
# Make user-installed command line tools available in zsh.
# macsync installs zipapp executables into ~/.local/bin.
typeset -U path PATH
path=("$HOME/.local/bin" $path)
export PATH
# <<< macsync user-local bin <<<
EOF
}

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    ensure_zsh_path_block "$HOME/.zshrc"
    ensure_zsh_path_block "$HOME/.zprofile"
    PATH_STATUS="added to ~/.zshrc and ~/.zprofile"
    SHELL_NOTE="Run this in the current terminal: source ~/.zshrc && rehash"
    ;;
esac

cat <<EOF
============================================================
macsync install succeeded
============================================================

Installed commands:
  $BIN_DIR/macsync
  $BIN_DIR/macsync-server

Verification:
  $MACSYNC_VERSION

PATH setup:
  $BIN_DIR is $PATH_STATUS

Try:
  macsync version
  macsync init-config
  macsync list

${SHELL_NOTE}
============================================================
EOF
