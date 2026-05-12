---
name: crossdatagen-daily-research-workflow
description: Use when working in the CrossDataGen project and the user mentions daily startup, daily summary, morning plan, evening wrap-up, recording key guesses, updating notes, project memory, memory refresh, project audit, stale notes, skipped files, facts versus inference, discussion notes, continuing research from prior context, or discussing/reading a paper where a literature card, Zotero lookup, paper indexing, reading notes, or discussion summary should be maintained.
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
- `99-项目记忆/项目基础盘点.md`: what has been inspected, what was skipped, durable facts, confirmed route, Codex inferences, and known uncertainties.

## Morning Startup

When the user starts a day, resumes work, opens the project, or asks to continue:

1. Read `0-随记.md` and `0-讨论.md` first.
2. Read `99-项目记忆/Codex工作记忆.md` and `99-项目记忆/项目地图.md` if this is a new conversation, a new agent, or the user asks to reconnect context.
3. Read `99-项目记忆/项目基础盘点.md` if this is a new conversation, a new agent, the user asks to refresh context, or the memory seems stale.
4. Read `0-记录/下一步.md` and the latest entry in `0-记录/每日记录.md`.
5. Give the user a short state recap:
   - current direction
   - last important decision
   - current blocker
   - recommended first action today
6. Then begin the requested work.

Do not scan the whole repository unless the task requires code or experiment context beyond these memory files.

## Project Memory Audit

Use this when the user asks to initialize memory, refresh memory, rescan the project, check whether notes are stale, prepare a new agent handoff, or explicitly asks what has and has not been inspected.

This is different from daily startup. Daily startup reads memory first and avoids scanning. Project memory audit is the controlled moment to inspect files and update durable memory.

1. Read existing `99-项目记忆/Codex工作记忆.md`, `99-项目记忆/项目地图.md`, and `99-项目记忆/项目基础盘点.md` if present.
2. Build a bounded inventory with `rg --files` when available.
3. Focus on changed or high-signal files first:
   - `0-随记.md`, `0-讨论.md`, `0-记录/下一步.md`, `0-记录/每日记录.md`
   - files under `99-项目记忆/`
   - recent docs, experiment scripts, data-processing code, taxonomy files, prompts, paper notes, and evaluation summaries
4. Do not expand bulky/generated areas by default. Record skipped areas instead.
5. Update `99-项目记忆/项目基础盘点.md` with a dated audit section rather than rewriting history.
6. Update `99-项目记忆/项目地图.md` only for stable structure changes.
7. Update `99-项目记忆/Codex工作记忆.md` only for durable context a new agent should know.
8. Update `0-记录/下一步.md` when the audit changes current priorities, blockers, or the recommended first action.

### `99-项目记忆/项目基础盘点.md`

Use this shape when creating or refreshing the file:

```md
# 项目基础盘点

## YYYY-MM-DD 盘点

### 我检查了什么

### 已观察到的事实

### 用户已确认的路线/决定

### Codex 当前推断

### 跳过项

### 不确定点

### 对下一步的影响
```

## Facts, Confirmations, And Inferences

CrossDataGen contains many research judgments. Keep their status explicit:

- **已观察到的事实**: code, notes, experiment outputs, paper cards, logs, or file contents that were actually inspected.
- **用户已确认的路线/决定**: decisions the user explicitly confirmed in conversation or notes.
- **Codex 当前推断**: hypotheses inferred from context. These are useful but provisional and should be easy to overturn.

When updating `Codex工作记忆.md` or `项目基础盘点.md`, do not present Codex inference as confirmed fact. If a conclusion mixes evidence and inference, split it into both parts.

## Skipped Items

Some CrossDataGen areas are too large or low-signal for routine startup. Do not repeatedly scan them unless the task needs them. Instead, record the skipped path, reason, and when to revisit it.

Common examples:

- `out/bridge_flows_*`: generated experiment outputs; inspect when comparing or debugging that specific run.
- PDFs and large paper folders: index names first; extract content when discussing that paper.
- CSV/JSONL/parquet/data dumps: inspect schema or samples only when data quality, labels, or evaluation depends on them.
- caches, checkpoints, model outputs, and temporary artifacts: skip unless reproducing or debugging an experiment.

Use this format inside `项目基础盘点.md`:

```md
### 跳过项

- `path/or/pattern`: 跳过原因；什么时候需要重新看。
```

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
6. If today's work changed what has been inspected, skipped, confirmed, or inferred, update `99-项目记忆/项目基础盘点.md`.

End with a short report listing which files were updated and tomorrow's first step.

## Style Rules

- Prefer concise Chinese.
- Put conclusions before reasons.
- Avoid diary-style logs in root files.
- Use links instead of copying long material into root files.
- Preserve the user's existing notes; append or lightly add navigation, do not rewrite historical content unless asked.
- Keep `0-随记.md` and `0-讨论.md` as navigation pages, not warehouses.
- Separate observed facts, user-confirmed decisions, and Codex inferences.
- Record skipped bulky/generated areas instead of silently ignoring them.
- For memory refresh, append dated audit sections; do not erase older baselines unless the user asks.

## Trigger Phrases

Treat these as strong signals to use this skill:

- "早上开始", "今天开始", "打开项目", "继续昨天"
- "记录一下", "把这个猜想记下来", "保存到随记"
- "讨论记录", "把我们的讨论保存下来"
- "每日总结", "晚上整理", "收尾", "同步一下"
- "更新记忆", "新 agent 接上", "回忆项目"
- "刷新记忆", "重新盘点", "项目基础盘点", "哪些没看", "事实和推断分开"
- "讨论这篇论文", "读这篇论文", "论文卡片", "查一下 Zotero"

## Paper Discussion Workflow

When the user says they want to discuss or read a specific paper:

1. Identify the paper title, DOI, arXiv URL, or short name from the user's message.
2. Search Zotero first:
   - If found, extract title, authors, year, venue/DOI/URL, Zotero key, attachment keys, tags, and any notes.
   - If not found, tell the user clearly that it is not in the Zotero library yet, then still create a local card if enough bibliographic information is available.
3. Ensure a literature card exists under `98-材料/文献阅读存档/papers/YYYY_ShortTitle.md`.
   - Use `98-材料/文献阅读存档/01-单篇阅读卡片模板.md` or the existing card style.
   - Fill `## 0. 基本信息` and `## 0.1 Zotero 信息` from Zotero when available.
   - Keep a `### 1.1 我的随手一句话 / 阅读随记` area for the user's rough notes.
4. Add or update the paper in:
   - `98-材料/文献阅读存档/00-阅读总表.md`
   - `98-材料/文献阅读存档/02-主题索引.md` when its topic is clear
5. During discussion, capture useful points directly in the card:
   - the user's one-sentence intuition
   - important concepts and definitions
   - method/data/label details
   - questions and confusions
   - CrossDataGen relevance
   - concrete ideas for features, taxonomy, dataset construction, experiments, or writing
6. After the discussion ends or reaches a stable pause, append a concise discussion digest to the card:
   - date
   - what was clarified
   - remaining questions
   - usable ideas
   - next reading or experiment action
7. If the discussion changes the research route, also add a short pointer in `0-讨论.md` or `0-随记.md`, and update `0-记录/下一步.md` when needed.

Do not wait until the user writes polished notes. Rough remarks are valuable; preserve them first, then add a cleaned summary nearby.
