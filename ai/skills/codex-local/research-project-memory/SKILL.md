---
name: research-project-memory
description: Use when working in any paper, thesis, academic, literature, experiment, dataset, or research project, or when the current repository contains 99-项目记忆, 项目地图.md, Codex工作记忆.md, 项目基础盘点.md, Git仓库洞察.md, 98-材料, 0-记录, 0-随记.md, or 0-讨论.md. Also use when the user mentions project startup, unfamiliar existing projects, taking over a project, building project memory, project maps, git branches, subrepositories, new conversation context, daily research notes, discussion notes, reading papers, Zotero, next steps, wrap-up, sync-up, or avoiding repeated full-repo scans.
---

# Research Project Memory

## Purpose

Help Codex build and use a durable memory layer for research projects. The core outcome is not only note-taking; it is generating enough project memory that a future Codex conversation can understand the project quickly without repeating the same discovery work.

This skill is project-agnostic. It supports two modes:

- **Memory build mode**: for a new, unfamiliar, or inherited project. Do a bounded full traversal once, then create the memory files.
- **Memory use mode**: for later conversations. Read the memory layer first and avoid full traversal unless the task requires it.

Prefer local project conventions when they exist; otherwise create the standard structure below.

## Standard Structure

Use paths relative to the project root.

- `99-项目记忆/`: auto-use marker. If this directory exists and contains useful memory files, treat the repository as already built by this skill.
- `99-项目记忆/项目地图.md`: stable navigation map for Codex and future agents.
- `99-项目记忆/Codex工作记忆.md`: current understanding, assumptions, active goals, decisions, and handoff notes.
- `99-项目记忆/项目基础盘点.md`: first-pass inventory of an unfamiliar or newly opened project.
- `99-项目记忆/Git仓库洞察.md`: repository layout, current branch, important branches, remotes, submodules, nested repositories, worktrees, and branch-specific memory notes.
- `99-项目记忆/项目内工作流.md`: optional mature-project workflow guide that records project-specific routines, conventions, and entry points.
- `98-材料/`: long materials, meeting notes, reading notes, screenshots, excerpts, intermediate analysis, paper cards, experiment evidence.
- `98-材料/项目基础材料/`: detailed directory scans, extracted metadata, dependency summaries, paper lists, and other bulky discovery artifacts.
- `0-记录/每日记录.md`: daily plan and wrap-up.
- `0-记录/下一步.md`: latest route, priorities, blockers, and first next action.
- `0-随记.md`: concise research ideas, guesses, attempts, and pointers to detailed materials.
- `0-讨论.md`: concise discussion conclusions, decisions, disagreements, and action items.
- `0-讨论/讨论记录.md`: curated discussion details when a root entry is too short.

If a project already uses different names, map those files to the same roles and document the mapping in `99-项目记忆/项目地图.md`.

## Auto-Use In Built Projects

When starting work in any repository, quickly check whether the project has already been built by this skill.

Strong markers:

- `99-项目记忆/`
- `99-项目记忆/Codex工作记忆.md`
- `99-项目记忆/项目地图.md`
- `99-项目记忆/项目基础盘点.md`
- `99-项目记忆/Git仓库洞察.md`

If any strong marker exists:

1. Enter memory use mode before doing task-specific exploration.
2. Read the memory files listed in `项目地图.md` or the default startup order.
3. Give a short recap only when useful; for small tasks, silently use the memory and continue.
4. Do not rebuild or rescan the whole project unless the user asks, memory is missing/stale, or the task requires deeper inspection.

If no strong marker exists but the project looks like a research project, offer to build memory once.

## Finding The Project Root

When starting in a workspace:

1. Prefer the current working directory if it contains `99-项目记忆/`, `98-材料/`, `0-记录/`, `.git/`, `pyproject.toml`, `package.json`, or a project README.
2. If the current directory is a subfolder, search upward for `99-项目记忆/` or `.git/`.
3. If multiple candidate roots exist, choose the one containing the active research notes or ask a short clarifying question.
4. If memory files already exist, enter memory use mode and read them first.
5. If memory files do not exist, or the user asks to build/refresh the project memory, enter memory build mode.

## Memory Build Mode

Use this when opening an unfamiliar existing project, taking over someone else's project, creating memory for a new project, or refreshing stale memory.

The goal is to traverse enough of the project once to create durable navigation and context. This is the appropriate time to inspect the repository broadly. After memory is built, future sessions should start from the memory layer instead of repeating this scan.

### Bounded Traversal

1. Build a file inventory with `rg --files` when available.
2. Exclude obvious bulky or generated paths unless the user asks otherwise:
   - `.git/`, `.venv/`, `venv/`, `env/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`
   - `dist/`, `build/`, `target/`, `.next/`, `.cache/`
   - large binary/data/model outputs such as `*.pt`, `*.pth`, `*.ckpt`, `*.bin`, `*.zip`, `*.tar`, `*.gz`, `*.parquet`, `*.npy`, `*.npz`
3. Read high-signal text first:
   - README, docs, project notes, paper lists, abstracts, proposals, TODO files
   - `pyproject.toml`, `requirements*.txt`, `environment.yml`, `package.json`, Makefiles, scripts
   - main experiment, data, training, evaluation, analysis, and writing entry points
4. Run git repository insight if the project is inside a git repository.
5. Sample large directories instead of reading every file line by line. Record what was skipped and why.
6. If there are papers, PDFs, or Zotero-relevant files, index their names and locations; only extract content when the user's task needs it.
7. If project ownership or goals are unclear, write uncertainties explicitly instead of guessing.

### Memory Outputs

After traversal, create or update:

- `99-项目记忆/项目基础盘点.md`: what was found, what matters, what is uncertain, and what was skipped.
- `99-项目记忆/项目地图.md`: stable project navigation.
- `99-项目记忆/Codex工作记忆.md`: current interpretation, likely goals, active assumptions, and future handoff.
- `99-项目记忆/Git仓库洞察.md`: git layout, branches, nested repositories, and branch-aware notes.
- `0-记录/下一步.md`: recommended next steps for the user and Codex.

Put bulky raw inventories, command summaries, or long extracted notes under `98-材料/项目基础材料/` and link to them from `项目基础盘点.md`.

### `99-项目记忆/项目基础盘点.md`

```md
# 项目基础盘点

## 盘点日期

## 项目一句话理解

## 我检查了什么

## 关键发现

## 目录/文件角色

## 代码、实验、数据、写作入口

## Git 与子仓库

## 已有笔记和研究材料

## 不确定点

## 跳过或未展开的内容

## 建议下一步
```

## First-Time Project Setup

When the user starts a new research project or asks to build project memory:

1. Create missing directories: `99-项目记忆/`, `98-材料/`, `0-记录/`, and optionally `0-讨论/`.
2. Create missing files from the templates below.
3. Run memory build mode if this project does not already have reliable memory files.
4. Inspect high-signal files and the bounded inventory before writing summaries.
5. Write a concise initial project map, project inventory, git insight, working memory, and next-step file.
6. End by reporting which files were created and what Codex should read first in a future conversation.

### `99-项目记忆/项目地图.md`

```md
# 项目地图

## 项目一句话

## 当前研究目标

## 核心目录

## 重要入口文件

## 研究对象与数据

## 实验/代码入口

## 实验主线速查

## 论文主线速查

## 数据主线速查

## 写作主线速查

## Git 与子仓库

## 项目内工作流

## 写作与投稿材料

## 记忆文件怎么读
新对话优先读取：
1. `99-项目记忆/Codex工作记忆.md`
2. `99-项目记忆/项目地图.md`
3. `99-项目记忆/项目基础盘点.md`
4. `99-项目记忆/Git仓库洞察.md`
5. `99-项目记忆/项目内工作流.md`（如果存在）
6. `0-记录/下一步.md`
7. `0-记录/每日记录.md` 的最新日期
8. `0-随记.md` 和 `0-讨论.md` 的最新条目
```

### `99-项目记忆/Codex工作记忆.md`

```md
# Codex 工作记忆

## 当前目标

## 当前路线

## 已确认事实

## 关键决策

## 活跃假设

## 未解决问题

## 给新对话的接续提示
```

### `99-项目记忆/项目内工作流.md`

Create this when a project becomes mature enough to have local routines. Keep it short and practical; it should calibrate this global skill to the project's own habits.

```md
# 项目内工作流

## 每日启动

## 每日收尾

## 实验流程

## 论文阅读流程

## 数据处理流程

## 写作流程

## 本项目特殊约定
```

### `99-项目记忆/Git仓库洞察.md`

```md
# Git 仓库洞察

## 最近更新

## 当前仓库

## 当前分支

## 工作区状态

## 重要分支

## 远端

## 子模块与嵌套仓库

## Worktree

## 分支相关记忆

## 不确定点
```

### `0-记录/下一步.md`

```md
# 下一步

## 当前优先级

## 今天/最近第一步

## 阻塞

## 暂不做
```

### `0-记录/每日记录.md`

```md
# 每日记录

## YYYY-MM-DD

### 今日计划

### 今日总结

### 明天第一步
```

## New Conversation Startup

When the user starts, resumes, says "继续", asks Codex to reconnect context, or opens a research project:

1. If `99-项目记忆/` does not exist, or it lacks useful content, offer to build the project memory and enter memory build mode when appropriate.
2. If memory exists, read `99-项目记忆/Codex工作记忆.md`, `99-项目记忆/项目地图.md`, `99-项目记忆/项目基础盘点.md`, and `99-项目记忆/Git仓库洞察.md` if present.
3. Read `0-记录/下一步.md` and the latest entry in `0-记录/每日记录.md`.
4. Skim the latest sections of `0-随记.md` and `0-讨论.md` if present.
5. Give a short recap:
   - current goal
   - last important decision
   - active blocker or uncertainty
   - recommended first action
6. Then start the requested work.

Only read code, papers, datasets, or full directories when the immediate task needs them.

## Root Entry Discipline

Treat `0-随记.md` and `0-讨论.md` as navigation pages, not warehouses.

- Put short conclusions, decisions, and links there.
- Move long reasoning, raw notes, excerpts, tables, screenshots, logs, paper analysis, and discussion transcripts into `98-材料/`.
- If an entry needs more than one short paragraph, create a supporting file and link it.
- Keep root entries useful for tomorrow's startup: what changed, why it matters, and what to do next.

Good root entry shape:

```md
## YYYY-MM-DD
一句核心结论。详细内容见：[材料标题](98-材料/example.md)
下一步：具体动作。
```

## Project-Local Workflow

For mature projects, ensure the project has either `99-项目记忆/项目内工作流.md` or an equivalent local workflow file linked from `项目地图.md`.

Use this file to capture project-specific routines that the global skill cannot know:

- how to start the day in this project
- how to run or inspect experiments
- how paper cards, reading indexes, and topic indexes are organized
- how data, labels, prompts, results, and writing drafts are named
- which generated outputs are usually skipped
- what local conventions override the generic defaults in this skill

When local workflow conflicts with this global skill, prefer the project-local workflow unless the user says otherwise.

## Git Repository Insight

Use this during memory build mode, memory refresh, and whenever the user asks about branches, subrepositories, submodules, worktrees, or repository state.

Prefer read-only git commands. Useful signals:

- current repository root and current branch
- `git status --short --branch`
- `git branch --list --all`
- `git remote -v`
- `git submodule status --recursive` when `.gitmodules` exists
- `git worktree list` when worktrees may be relevant
- nested repositories: directories below the project that contain their own `.git` directory or gitfile

Rules:

1. Do not switch branches, check out commits, pull, push, rebase, merge, or modify git state just to build memory.
2. Record branch information as observation, not instruction. Knowing a branch exists does not mean entering it.
3. If nested repositories or submodules exist, list their paths, current branches if readable, and their relationship to the parent project.
4. If the user later enters another branch, keep using this skill in that branch and append branch-specific observations to `Git仓库洞察.md` and `Codex工作记忆.md`.
5. Keep cross-branch facts separate from branch-specific facts. Do not overwrite project-wide memory with a branch-local assumption.
6. If the working tree has uncommitted changes, mention that memory reflects the current branch and dirty state.
7. If git is unavailable or the directory is not a git repository, write that explicitly and continue with file-based project memory.

When updating `Git仓库洞察.md`, include the date and branch name for branch-specific notes:

```md
## 分支相关记忆

### YYYY-MM-DD `branch-name`
- 观察：
- 与主线差异：
- 对当前研究/实现的影响：
```

## Daily Research Recording

When the user asks to record an idea, guess, attempt, result, route change, or observation:

1. Add a short dated entry to `0-随记.md`.
2. Put long evidence, reasoning, tables, screenshots, excerpts, or raw logs under `98-材料/` and link to it.
3. Update `0-记录/下一步.md` if priorities, blockers, or the first next action changed.
4. Update `99-项目记忆/Codex工作记忆.md` if a future agent must remember it.

Root entries should stay short and link to detail files:

```md
## YYYY-MM-DD
一句核心结论。详细内容见：[材料标题](98-材料/example.md)
下一步：具体动作。
```

## Discussion Recording

When the user asks to save a discussion, meeting, supervision feedback, brainstorm, disagreement, or decision:

1. Add a concise conclusion to `0-讨论.md`.
2. If the discussion has useful detail, create or update `0-讨论/讨论记录.md` or a dated file in `98-材料/讨论记录/`.
3. Extract decisions, changed assumptions, and action items into `0-记录/下一步.md`.
4. Promote only durable context into `99-项目记忆/Codex工作记忆.md`.

Capture rough remarks first. Add a cleaned digest nearby instead of waiting for polished notes.

## Evening Wrap-Up Or Sync

When the user says "收尾", "同步一下", "每日总结", "整理一下", "更新记忆", or prepares to stop:

1. Update `0-记录/每日记录.md` with today's plan if missing, summary, and tomorrow's first step.
2. Update `0-记录/下一步.md` with current route, priorities, blockers, and immediate next action.
3. Add root summaries to `0-随记.md` or `0-讨论.md` only for decisions worth seeing tomorrow.
4. Move or link long details into `98-材料/`.
5. Update `99-项目记忆/Codex工作记忆.md` and `项目地图.md` when the project structure, direction, or handoff context changed.
6. End with files updated and the next starting point.

## Refreshing Existing Memory

When the user asks to rebuild, refresh, rescan, or says the project memory is stale:

1. Read the current `99-项目记忆/` files first.
2. Run bounded traversal again, focusing on files changed since the last memory update when git history or timestamps are useful.
3. Update `项目基础盘点.md` with a dated refresh section instead of erasing the old baseline.
4. Update `项目地图.md` only for stable structural changes.
5. Update `Git仓库洞察.md` if branch, submodule, nested repository, remote, worktree, or dirty-state context changed.
6. Update `Codex工作记忆.md` and `0-记录/下一步.md` with the current state.

## Paper Reading And Zotero

When discussing or reading a paper:

1. Identify the title, DOI, arXiv URL, Zotero key, or short name.
2. Search local Zotero first when available.
3. Ensure a paper card exists under `98-材料/文献阅读存档/papers/YYYY_ShortTitle.md`.
   - Use `98-材料/文献阅读存档/01-单篇阅读卡片模板.md` when present.
   - Fill basic bibliographic fields and Zotero metadata when available.
   - Keep a clearly named area for rough user notes, such as `### 我的随手一句话 / 阅读随记`.
4. Add or update:
   - `98-材料/文献阅读存档/00-阅读总表.md`
   - `98-材料/文献阅读存档/02-主题索引.md` when the topic is clear
5. During discussion, capture useful points directly in the card:
   - basic bibliographic information and Zotero metadata
   - the user's one-sentence intuition
   - important concepts and definitions
   - method, data, labels, assumptions, and limitations
   - relation to the current project
   - questions and confusions
   - usable ideas for taxonomy, dataset construction, experiments, evaluation, or writing
   - next reading or experiment action
6. After the discussion ends or reaches a stable pause, append a concise discussion digest to the card:
   - date
   - what was clarified
   - remaining questions
   - usable ideas
   - next action
7. If the paper changes the research route, add a short pointer in `0-随记.md` or `0-讨论.md` and update `0-记录/下一步.md`.

If Zotero does not contain the paper, say so clearly and still create a local card when enough bibliographic information is available.

Do not wait for polished notes. Preserve rough remarks first, then add a cleaned summary nearby.

## Style Rules

- Prefer concise Chinese unless the project is primarily English.
- Put conclusions before reasons.
- Keep root files as navigation pages, not warehouses.
- Keep `0-随记.md` and `0-讨论.md` especially lean: short conclusion, link, next action.
- Link to details instead of copying long material into root notes.
- Make `项目地图.md` more than a directory tree; include experiment, paper, data, and writing mainline quick references when they exist.
- For mature projects, maintain or link `99-项目记忆/项目内工作流.md`.
- Preserve historical notes; append or lightly add navigation unless the user asks for restructuring.
- Write memory for the next Codex instance, not for publication.
- Include concrete dates in daily records.
- During first-pass project takeover, distinguish observed facts from inferred goals.
- Do not hide skipped areas; list them so the next agent knows the limits of the memory.
- Treat git branch and subrepository context as part of the project memory, but keep all git inspection read-only unless the user explicitly asks for a git operation.

## Strong Trigger Phrases

- "新项目初始化", "建设项目记忆", "项目地图", "Codex 工作记忆"
- "打开一个陌生项目", "接手项目", "帮我盘点这个项目", "遍历所有并建设记忆"
- "快速了解这个项目", "给这个项目建基础记忆", "项目基础盘点"
- "看看当前分支", "项目有哪些分支", "子仓库", "子模块", "nested repo", "worktree"
- "新对话接上", "快速熟悉项目", "不要全仓库扫描", "恢复上下文"
- "今天开始", "继续昨天", "早上开始", "打开项目"
- "记录一下", "保存到随记", "把这个猜想记下来"
- "讨论记录", "把我们的讨论保存下来", "导师反馈"
- "每日总结", "晚上整理", "收尾", "同步一下", "更新记忆"
- "读这篇论文", "讨论这篇论文", "论文卡片", "查 Zotero", "阅读总表", "主题索引"
- "项目内工作流", "实验主线", "论文主线", "数据主线", "写作主线"
