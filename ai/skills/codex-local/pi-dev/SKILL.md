---
name: pi-dev
description: Help Codex work with the Pi coding agent from pi.dev, including installation, updates, package management, skill discovery, settings, providers, and interoperability with Codex or Claude skill directories. Use when tasks mention pi.dev, the `pi` CLI, `pi install`, Pi packages, Pi skills, `~/.pi/agent`, `.pi/settings.json`, provider setup, or troubleshooting Pi configuration.
---

# Pi Dev

## Overview

Use this skill to answer Pi coding agent questions with current, concrete commands and file paths. Prefer official Pi docs, distinguish global vs project-local behavior, and call out security implications before recommending third-party packages or skills.

## Workflow

1. Classify the request before answering.
- Pi installation or update
- Pi package or skill install/remove/update
- Pi settings, model, or provider configuration
- Pi skill authoring or skill discovery
- Pi and Codex/Claude interoperability

2. Read only the needed reference file.
- Read [references/skills-and-packages.md](references/skills-and-packages.md) for `pi install`, package sources, skill locations, or sharing skills across harnesses.
- Read [references/configuration.md](references/configuration.md) for providers, auth, models, and `settings.json`.

3. Answer with exact scope and paths.
- Prefer explicit file paths such as `~/.pi/agent/settings.json`, `.pi/settings.json`, `~/.pi/agent/skills/`, and `.pi/skills/`.
- Explain whether a command changes global state or project-local state.
- When recommending installs, say whether they land in global npm, `~/.pi/agent/git/`, `.pi/git/`, or project settings.

4. Prefer the narrowest working change.
- Suggest `-l` for project-local installs when the user is working inside one repository.
- Use direct package sources or local paths when the user already has a repo in hand.
- Avoid inventing unsupported commands or settings names.

## Quick Rules

- Warn that third-party Pi packages and skills can execute arbitrary code or instruct the model to take privileged actions.
- If the request is about using Codex skills inside Pi, mention that Pi can load `~/.codex/skills` through the `skills` array in Pi settings.
- If the request is about building a distributable Pi package, prefer package manifests with a `pi` key in `package.json`, but mention that Pi can also auto-discover conventional `skills/`, `extensions/`, `prompts/`, and `themes/` directories.
- If the request is about authentication, prefer documented providers and exact env var names from the official provider docs.

## Common Tasks

### Install Or Update Pi Resources

- For Pi packages or shared skill bundles, start with the `pi install`, `pi list`, `pi update`, and `pi remove` flow in [references/skills-and-packages.md](references/skills-and-packages.md).
- Clarify whether the source is npm, git, URL, or local path.
- Recommend pinning versions or refs when reproducibility matters.

### Configure Providers Or Settings

- Use [references/configuration.md](references/configuration.md) for provider login, API key setup, auth file location, and key settings paths.
- When the user needs a one-off provider setup, give the smallest possible config snippet.

### Bridge Pi With Other Skill Systems

- If the user wants Pi to see Codex skills, point Pi settings at `~/.codex/skills`.
- If the user wants a Codex skill about Pi, keep the Codex skill concise and store deeper Pi docs under `references/`.
