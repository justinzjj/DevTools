# Pi Skills And Packages

Use this reference for Pi skill discovery, package installation, and cross-harness skill sharing.

## Core Commands

```bash
pi install npm:@foo/pi-tools
pi install npm:@foo/pi-tools@1.2.3
pi install git:github.com/user/repo
pi install git:github.com/user/repo@v1
pi install https://github.com/user/repo
pi install /absolute/path/to/package
pi install ./relative/path/to/package

pi remove npm:@foo/pi-tools
pi uninstall npm:@foo/pi-tools
pi list
pi update
pi config
```

Use `-l` for project-local installs that write to `.pi/settings.json` and project-managed package directories. Without `-l`, Pi updates global settings under `~/.pi/agent/settings.json`.

## Where Pi Looks For Skills

Global skill locations:
- `~/.pi/agent/skills/`
- `~/.agents/skills/`

Project skill locations:
- `.pi/skills/`
- `.agents/skills/` in the current directory or ancestor directories

Additional skill sources:
- Pi packages that expose `skills/` or declare `pi.skills` in `package.json`
- Paths listed in the `skills` array in Pi settings
- Explicit CLI flags such as `--skill <path>`

Pi can also load Codex or Claude skills by adding those directories to Pi settings:

```json
{
  "skills": [
    "~/.claude/skills",
    "~/.codex/skills"
  ]
}
```

## Package Sources

Pi accepts these package source styles:

- `npm:@scope/pkg@1.2.3`
- `git:github.com/user/repo@v1`
- `git:git@github.com:user/repo@v1`
- `https://github.com/user/repo@v1`
- `ssh://git@github.com/user/repo@v1`
- Local paths such as `/absolute/path/to/package` or `./relative/path/to/package`

Package install locations:
- Global git packages: `~/.pi/agent/git/<host>/<path>`
- Project git packages: `.pi/git/<host>/<path>`
- Global npm packages: global npm context
- Project npm packages: `.pi/npm/`

Refs such as tags or commits pin a package and are skipped by `pi update`.

## Package Layout

Pi packages can declare resources in `package.json`:

```json
{
  "name": "my-pi-package",
  "keywords": ["pi-package"],
  "pi": {
    "extensions": ["./extensions"],
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"]
  }
}
```

If the `pi` manifest is missing, Pi can auto-discover conventional directories like `skills/`, `extensions/`, `prompts/`, and `themes/`.

## Security

Review third-party Pi packages and skills before installing them. Packages can run arbitrary code, and skills can instruct the model to execute commands or follow unsafe workflows.
