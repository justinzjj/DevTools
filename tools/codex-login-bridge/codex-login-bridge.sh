#!/usr/bin/env bash
set -euo pipefail

HOST="${CODEX_TUNNEL_HOST:-server_local}"
LOCAL_PORT="${CODEX_TUNNEL_LOCAL_PORT:-1455}"
REMOTE_HOST="${CODEX_TUNNEL_REMOTE_HOST:-127.0.0.1}"
REMOTE_PORT="${CODEX_TUNNEL_REMOTE_PORT:-1455}"
CONTROL_DIR="${CODEX_TUNNEL_CONTROL_DIR:-$HOME/.ssh/codex-tunnels}"
CONTROL_PATH="$CONTROL_DIR/%r@%h:%p-codex-${LOCAL_PORT}"
LOG_DIR="${CODEX_TUNNEL_LOG_DIR:-$HOME/Library/Logs}"
LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.justin.codex-login-tunnel.plist"
SCRIPT_PATH="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/$(basename -- "${BASH_SOURCE[0]}")"

usage() {
  cat <<USAGE
Usage: $(basename "$0") <start|stop|restart|status|test|install-launchd|uninstall-launchd>

Keeps the Codex/VS Code OAuth callback tunnel available:
  localhost:${LOCAL_PORT} -> ${HOST}:${REMOTE_HOST}:${REMOTE_PORT}

Environment overrides:
  CODEX_TUNNEL_HOST          default: server_local
  CODEX_TUNNEL_LOCAL_PORT    default: 1455
  CODEX_TUNNEL_REMOTE_HOST   default: 127.0.0.1
  CODEX_TUNNEL_REMOTE_PORT   default: 1455
USAGE
}

is_listening() {
  lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN 2>/dev/null | grep -q 'ssh'
}

show_listener() {
  lsof -nP -iTCP:"$LOCAL_PORT" -sTCP:LISTEN 2>/dev/null || true
}

start() {
  mkdir -p "$CONTROL_DIR"

  if is_listening; then
    echo "Codex login tunnel already listening on localhost:${LOCAL_PORT}."
    show_listener
    return 0
  fi

  echo "Starting Codex login tunnel: localhost:${LOCAL_PORT} -> ${HOST}:${REMOTE_HOST}:${REMOTE_PORT}"
  ssh -fN \
    -M -S "$CONTROL_PATH" \
    -o ExitOnForwardFailure=yes \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -o TCPKeepAlive=yes \
    -L "${LOCAL_PORT}:${REMOTE_HOST}:${REMOTE_PORT}" \
    "$HOST"

  show_listener
}

stop() {
  if ssh -S "$CONTROL_PATH" -O check "$HOST" >/dev/null 2>&1; then
    ssh -S "$CONTROL_PATH" -O exit "$HOST" >/dev/null 2>&1 || true
  fi

  local pids
  pids="$(lsof -tiTCP:"$LOCAL_PORT" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "$pids" | xargs kill
  fi

  echo "Codex login tunnel stopped if it was running."
}

status() {
  if is_listening; then
    echo "Codex login tunnel is running."
    show_listener
  else
    echo "Codex login tunnel is not running."
    return 1
  fi
}

test_tunnel() {
  start >/dev/null
  status

  echo
  echo "Checking whether ${HOST} is currently running a Codex login callback server..."
  if ssh "$HOST" "lsof -nP -iTCP:${REMOTE_PORT} -sTCP:LISTEN 2>/dev/null || ss -ltnp 2>/dev/null | grep ':${REMOTE_PORT} ' || true" | grep -q .; then
    echo "Remote callback server is listening. Testing HTTP path through the tunnel..."
    curl -sS -i --max-time 4 "http://127.0.0.1:${LOCAL_PORT}/" | sed -n '1,8p'
  else
    echo "Remote callback server is not listening right now."
    echo "That is normal unless 'codex login' or the VS Code login flow is currently waiting for a browser callback."
  fi
}

install_launchd() {
  mkdir -p "$(dirname "$LAUNCH_AGENT")" "$LOG_DIR"

  cat > "$LAUNCH_AGENT" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.justin.codex-login-tunnel</string>
  <key>ProgramArguments</key>
  <array>
    <string>$SCRIPT_PATH</string>
    <string>start</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>60</integer>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/codex-login-tunnel.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/codex-login-tunnel.err.log</string>
</dict>
</plist>
PLIST

  launchctl unload "$LAUNCH_AGENT" >/dev/null 2>&1 || true
  launchctl load "$LAUNCH_AGENT"
  echo "Installed launch agent: $LAUNCH_AGENT"
  echo "It will check/start the tunnel every 60 seconds after you log in."
}

uninstall_launchd() {
  launchctl unload "$LAUNCH_AGENT" >/dev/null 2>&1 || true
  rm -f "$LAUNCH_AGENT"
  echo "Removed launch agent: $LAUNCH_AGENT"
}

case "${1:-}" in
  -h|--help|help) usage ;;
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) status ;;
  test) test_tunnel ;;
  install-launchd) install_launchd ;;
  uninstall-launchd) uninstall_launchd ;;
  *) usage; exit 2 ;;
esac
