# Tools

## Codex Login Bridge

`codex-login-bridge.sh` keeps the OAuth callback tunnel available when Codex or the VS Code plugin runs on `server_local`, but the login browser opens on this Mac.

It forwards:

```text
localhost:1455 -> server_local:127.0.0.1:1455
```

Common commands:

```bash
tools/codex-login-bridge/codex-login-bridge.sh --help
tools/codex-login-bridge/codex-login-bridge.sh status
tools/codex-login-bridge/codex-login-bridge.sh start
tools/codex-login-bridge/codex-login-bridge.sh test
tools/codex-login-bridge/codex-login-bridge.sh restart
tools/codex-login-bridge/codex-login-bridge.sh stop
```

Auto-start on macOS:

```bash
tools/codex-login-bridge/codex-login-bridge.sh install-launchd
tools/codex-login-bridge/codex-login-bridge.sh uninstall-launchd
```

If login lands on `http://localhost:1455/auth/callback?...` and does not finish, run:

```bash
tools/codex-login-bridge/codex-login-bridge.sh restart
```

Then start the Codex or VS Code login flow again. The `code=...` value in the callback URL is one-time sensitive data, so avoid sharing it.
