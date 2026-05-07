---
name: crossdatagen-daily-research-workflow
description: Use when working in the CrossDataGen project and the user mentions daily startup, daily summary, morning plan, evening wrap-up, recording key guesses, updating notes, project memory, discussion notes, or continuing research from prior context.
---

# CrossDataGen Daily Research Workflow

## Core Principle

Keep the user's daily entry points short and useful. Put only the summary, decision, and next action in the root notes; move details, long reasoning, links, code references, and evidence into supporting files.

## Project Files

Use these paths relative to the CrossDataGen project root:

- `0-随记.md`: daily idea entry point. Record concise hypotheses, route changes, key attempts, and pointers to details.
- `0-讨论.md`: daily discussion entry point. Record discussion conclusions, disagreements, decisions, and action items.
- `0-记录/每日记录.md`: morning plan and evening summary. Keep each day concise, ideally within 300 Chinese characters for the day's practical summary.
- `0-记录/下一步.md`: current technical route, near-term tasks, and open blockers. Keep only the latest actionable state.
- `0-讨论/讨论记录.md`: more detailed but still curated discussion notes.
- `98-材料/`: long materials, excerpts, meeting notes, screenshots, code links, intermediate analysis.
- `99-项目记忆/Codex工作记忆.md`: agent memory for future conversations.
- `99-项目记忆/项目地图.md`: project structure and navigation map.

## Morning Startup

When the user starts a day, resumes work, opens the project, or asks to continue:

1. Read `0-随记.md` and `0-讨论.md` first.
2. Read `99-项目记忆/Codex工作记忆.md` and `99-项目记忆/项目地图.md` if this is a new conversation, a new agent, or the user asks to reconnect context.
3. Read `0-记录/下一步.md` and the latest entry in `0-记录/每日记录.md`.
4. Give the user a short state recap:
   - current direction
   - last important decision
   - current blocker
   - recommended first action today
5. Then begin the requested work.

Do not scan the whole repository unless the task requires code or experiment context beyond these memory files.

## During Work

When the user asks to record a key idea, guess, attempt, result, route change, or discussion:

1. Add a short entry to `0-随记.md` for research ideas and attempts, or `0-讨论.md` for discussion outcomes.
2. If the content needs more than a short paragraph, create or update a file in `98-材料/` and link to it from the root entry.
3. If the content changes the technical route, update `0-记录/下一步.md`.
4. If it changes how future agents should understand the project, update `99-项目记忆/Codex工作记忆.md` or `99-项目记忆/项目地图.md`.

Root entries should follow this shape:

```md
## YYYY-MM-DD
一句核心结论。详细内容见：[材料标题](98-材料/example.md)
下一步：具体动作。
```

## Evening Wrap-Up

When the user asks to summarize, wrap up, sync, close the day, or prepare tomorrow:

1. Update `0-记录/每日记录.md` with:
   - morning plan if missing
   - evening summary
   - tomorrow's first action
2. Update `0-记录/下一步.md` if priorities, route, blockers, or technical assumptions changed.
3. Add concise root-level summaries to `0-随记.md` and/or `0-讨论.md` only when there is a decision worth seeing tomorrow.
4. Move or link long material into `98-材料/`.
5. Update `99-项目记忆/` so a new agent can continue without rereading the whole repository.

End with a short report listing which files were updated and tomorrow's first step.

## Style Rules

- Prefer concise Chinese.
- Put conclusions before reasons.
- Avoid diary-style logs in root files.
- Use links instead of copying long material into root files.
- Preserve the user's existing notes; append or lightly add navigation, do not rewrite historical content unless asked.
- Keep `0-随记.md` and `0-讨论.md` as navigation pages, not warehouses.

## Trigger Phrases

Treat these as strong signals to use this skill:

- "早上开始", "今天开始", "打开项目", "继续昨天"
- "记录一下", "把这个猜想记下来", "保存到随记"
- "讨论记录", "把我们的讨论保存下来"
- "每日总结", "晚上整理", "收尾", "同步一下"
- "更新记忆", "新 agent 接上", "回忆项目"
