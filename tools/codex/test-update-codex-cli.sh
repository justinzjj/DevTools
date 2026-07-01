#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/update-codex-cli.sh"
TMP_ROOTS=()

cleanup() {
  local root
  for root in "${TMP_ROOTS[@]+"${TMP_ROOTS[@]}"}"; do
    rm -rf "$root"
  done
}
trap cleanup EXIT

fail() {
  printf 'not ok - %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  if [[ "$haystack" != *"$needle"* ]]; then
    fail "expected output to contain: $needle"
  fi
}

assert_file_equals() {
  local path="$1"
  local expected="$2"
  local actual
  actual="$(cat "$path")"
  if [[ "$actual" != "$expected" ]]; then
    fail "expected $path to be '$expected', got '$actual'"
  fi
}

make_fake_bin() {
  local root="$1"
  mkdir -p "$root/bin"

  cat >"$root/bin/codex" <<'FAKE_CODEX'
#!/usr/bin/env bash
set -euo pipefail
state_dir="${CODEX_FAKE_STATE_DIR:?}"
current_file="$state_dir/current"
latest_file="$state_dir/latest"
calls_file="$state_dir/calls"

case "${1:-}" in
  --version)
    printf 'codex-cli %s\n' "$(cat "$current_file")"
    ;;
  update)
    printf 'codex update\n' >>"$calls_file"
    cat "$latest_file" >"$current_file"
    printf 'Codex CLI %s installed successfully.\n' "$(cat "$current_file")"
    ;;
  doctor)
    shift
    if [[ "${1:-}" == "--summary" ]]; then
      printf 'codex doctor --summary\n' >>"$calls_file"
      printf 'Codex Doctor v%s\n' "$(cat "$current_file")"
    else
      exit 2
    fi
    ;;
  *)
    exit 2
    ;;
esac
FAKE_CODEX

  cat >"$root/bin/npm" <<'FAKE_NPM'
#!/usr/bin/env bash
set -euo pipefail
state_dir="${CODEX_FAKE_STATE_DIR:?}"
if [[ -f "$state_dir/npm_fail" ]]; then
  printf 'registry unavailable\n' >&2
  exit 1
fi
if [[ "$*" == "view @openai/codex version" ]]; then
  cat "$state_dir/latest"
  printf '\n'
  exit 0
fi
exit 2
FAKE_NPM

  chmod +x "$root/bin/codex" "$root/bin/npm"
}

run_case() {
  local name="$1"
  local current="$2"
  local latest="$3"
  local mode="$4"

  local root
  root="$(mktemp -d)"
  TMP_ROOTS+=("$root")
  make_fake_bin "$root"
  printf '%s' "$current" >"$root/current"
  printf '%s' "$latest" >"$root/latest"
  : >"$root/calls"

  local output
  local status
  set +e
  if [[ "$mode" == "check" ]]; then
    output="$(CODEX_FAKE_STATE_DIR="$root" PATH="$root/bin:$PATH" "$SCRIPT" --check --skip-doctor 2>&1)"
  else
    output="$(CODEX_FAKE_STATE_DIR="$root" PATH="$root/bin:$PATH" "$SCRIPT" --skip-doctor 2>&1)"
  fi
  status=$?
  set -e

  printf '%s\n' "$output" >"$root/output"
  printf '%s' "$status" >"$root/status"
  printf '%s\n' "$root"
}

test_check_mode_reports_up_to_date_without_update() {
  local root
  root="$(run_case "up-to-date" "1.2.3" "1.2.3" "check")"
  assert_file_equals "$root/status" "0"
  assert_contains "$(cat "$root/output")" "Codex CLI is already up to date"
  assert_file_equals "$root/calls" ""
}

test_stale_version_updates_and_verifies() {
  local root
  root="$(run_case "stale" "1.2.3" "1.2.4" "update")"
  assert_file_equals "$root/status" "0"
  assert_contains "$(cat "$root/output")" "Updating Codex CLI from 1.2.3 to 1.2.4"
  assert_file_equals "$root/current" "1.2.4"
  assert_file_equals "$root/calls" "codex update"
}

test_latest_lookup_failure_exits_nonzero() {
  local root
  root="$(mktemp -d)"
  TMP_ROOTS+=("$root")
  make_fake_bin "$root"
  printf '1.2.3' >"$root/current"
  printf '1.2.4' >"$root/latest"
  : >"$root/calls"
  : >"$root/npm_fail"

  if CODEX_FAKE_STATE_DIR="$root" PATH="$root/bin:$PATH" "$SCRIPT" --check --skip-doctor >/tmp/codex-update-test.out 2>&1; then
    fail "expected latest lookup failure to exit nonzero"
  fi
  assert_contains "$(cat /tmp/codex-update-test.out)" "Failed to query latest stable @openai/codex version"
}

test_check_mode_reports_up_to_date_without_update
test_stale_version_updates_and_verifies
test_latest_lookup_failure_exits_nonzero

printf 'ok - update-codex-cli tests passed\n'
