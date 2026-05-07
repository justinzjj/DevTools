# Pi Configuration

Use this reference for providers, auth, and settings paths.

## Settings Files

- Global settings: `~/.pi/agent/settings.json`
- Project settings: `.pi/settings.json`

Project settings override global settings.

## Common Settings

Useful settings often mentioned in setup help:
- `defaultProvider`
- `defaultModel`
- `defaultThinkingLevel`
- `theme`
- `quietStartup`
- `skills`
- `enableSkillCommands`
- `npmCommand`

Example:

```json
{
  "defaultProvider": "openai",
  "defaultModel": "gpt-5",
  "skills": ["~/.codex/skills"]
}
```

## Provider Setup

Interactive login flow:
- Run `/login` in interactive Pi mode.
- Use `/logout` to clear credentials.

Credentials storage:
- Auth file: `~/.pi/agent/auth.json`
- Auth file entries override environment variables.

Common environment variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `AZURE_OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `GROQ_API_KEY`
- `MISTRAL_API_KEY`
- `XAI_API_KEY`

Example auth file:

```json
{
  "openai": { "type": "api_key", "key": "sk-..." },
  "anthropic": { "type": "api_key", "key": "sk-ant-..." }
}
```

## Provider Notes

- Pi supports subscription logins for providers such as ChatGPT Plus/Pro (Codex), Claude, GitHub Copilot, and Google Gemini CLI through `/login`.
- OpenAI Codex access in Pi is intended for personal subscription use; production use should typically go through the OpenAI Platform API instead.
- If the user prefers API keys over interactive login, prefer the documented environment variable or `auth.json` entry.

## Skill Commands

Pi can expose discovered skills as slash commands such as:

```bash
/skill:my-skill
/skill:pdf-tools extract
```

Arguments after the slash command are appended to the skill content as user input. If skill commands are disabled, enable them through Pi settings with:

```json
{
  "enableSkillCommands": true
}
```
