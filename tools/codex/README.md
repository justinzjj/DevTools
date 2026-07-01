# Codex CLI Update

This directory fixes the repeatable update flow for the local Codex CLI.

## Command

```bash
tools/codex/update-codex-cli.sh
```

The script checks the installed `codex --version` against the stable npm
release for `@openai/codex`. If the local version differs, it runs the official
`codex update` command and verifies the resulting version.

## Useful Modes

```bash
tools/codex/update-codex-cli.sh --check
tools/codex/update-codex-cli.sh --skip-doctor
bash tools/codex/test-update-codex-cli.sh
```

Policy:

- Track stable `@openai/codex` `latest`.
- Do not install `alpha` releases by default.
- Treat `codex doctor --summary` as diagnostic output; version verification is
  based on the post-update `codex --version`.
- Keep older standalone releases in `~/.codex/packages/standalone/releases` for
  manual rollback unless explicitly cleaned up.
