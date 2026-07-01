#!/usr/bin/env bash
set -euo pipefail

PACKAGE_NAME="@openai/codex"
RUN_UPDATE=1
RUN_DOCTOR=1

usage() {
  cat <<'USAGE'
Usage: update-codex-cli.sh [--check] [--skip-doctor]

Checks the installed Codex CLI against the stable @openai/codex npm release.
By default, updates through the official `codex update` command when the local
version differs from the stable latest version.

Options:
  --check        Only report whether an update is available.
  --skip-doctor  Skip `codex doctor --summary` after the version check/update.
  -h, --help    Show this help.
USAGE
}

log() {
  printf '==> %s\n' "$*"
}

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

require_command() {
  local name="$1"
  command -v "$name" >/dev/null 2>&1 || die "Required command not found: $name"
}

extract_codex_version() {
  local output="$1"
  local version
  version="$(printf '%s\n' "$output" | awk '/codex-cli / {print $2; exit}')"
  [[ -n "$version" ]] || die "Could not parse Codex CLI version from: $output"
  printf '%s\n' "$version"
}

current_codex_version() {
  extract_codex_version "$(codex --version)"
}

latest_stable_version() {
  local version
  if ! version="$(npm view "$PACKAGE_NAME" version 2>/tmp/codex-update-npm.err)"; then
    printf '%s\n' "Failed to query latest stable $PACKAGE_NAME version" >&2
    cat /tmp/codex-update-npm.err >&2 || true
    exit 1
  fi
  [[ -n "$version" ]] || die "Latest stable $PACKAGE_NAME version was empty"
  printf '%s\n' "$version"
}

run_doctor_summary() {
  log "Running codex doctor --summary"
  set +e
  codex doctor --summary
  local status=$?
  set -e
  if [[ "$status" -ne 0 ]]; then
    log "codex doctor reported warnings or failures; version update verification already passed"
  fi
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --check)
      RUN_UPDATE=0
      ;;
    --skip-doctor)
      RUN_DOCTOR=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
  shift
done

require_command codex
require_command npm

current_version="$(current_codex_version)"
latest_version="$(latest_stable_version)"

log "Codex CLI current version: $current_version"
log "Codex CLI stable latest:   $latest_version"

if [[ "$current_version" == "$latest_version" ]]; then
  log "Codex CLI is already up to date ($current_version)"
  if [[ "$RUN_DOCTOR" -eq 1 ]]; then
    run_doctor_summary
  fi
  exit 0
fi

if [[ "$RUN_UPDATE" -eq 0 ]]; then
  log "Codex CLI update available: $current_version -> $latest_version"
  exit 1
fi

log "Updating Codex CLI from $current_version to $latest_version"
codex update

updated_version="$(current_codex_version)"
log "Codex CLI version after update: $updated_version"

if [[ "$updated_version" != "$latest_version" ]]; then
  die "Codex update finished, but version is $updated_version instead of $latest_version"
fi

if [[ "$RUN_DOCTOR" -eq 1 ]]; then
  run_doctor_summary
fi

log "Codex CLI update verified at $updated_version"
