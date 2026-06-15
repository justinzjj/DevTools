---
name: daily-work-entry
description: "Operate Justin's personal knowledge base as a daily work assistant. Use whenever the user says or implies 今日开工, 每日开始, 整理遗留, 今天做什么, 安排今天, 工作入口, morning brief, daily work entry, 收工, 今日总结, wrap up, 记录一个点子, 我有个想法, 突然想到, or wants a historically aware assistant for daily work and idea capture."
---

# Daily Work Entry

## Overview

Use this skill as a lightweight daily work and idea-capture companion for Justin's personal knowledge base.

Default personal knowledge base path: `/Users/justin/Personal/个人知识库`.

This skill does not replace `personal-knowledge-agent`. It routes high-frequency daily work actions through the repository's human-readable front stage:

- `05-Daily-Workspace/`
- `06-Ideas/`
- `00-Agent-State/work-state.yaml`
- `00-Agent-State/idea-state.yaml`

## Resolve The Knowledge Base

Resolve the path in this order:

1. A path explicitly provided by the user.
2. `PERSONAL_KNOWLEDGE_BASE`, if set.
3. The current working directory, if it contains `AGENT_PROTOCOL.md` and `30-Agent-Index/`.
4. `/Users/justin/Personal/个人知识库`.

If the resolved path does not contain `AGENT_PROTOCOL.md`, say the knowledge base was not found and ask for the correct path.

## Mode Selection

- **morning-start-mode**: 今日开工, 每日开始, 整理遗留, 今天做什么, 安排今天, 工作入口, morning brief, daily work entry.
- **daily-wrap-mode**: 收工, 今日总结, 晚上整理, wrap up, daily wrap.
- **idea-capture-mode**: 记录一个点子, 记个点子, 点子记录, 我有个想法, 突然想到, idea capture.
- **idea-promote-mode**: 展开这个点子, 推进这个点子, 点子详情, 把点子变成项目, promote idea.

## Standard Read Order

1. `AGENT_PROTOCOL.md`
2. `00-Agent-State/work-state.yaml`
3. `00-Agent-State/idea-state.yaml`
4. `00-Agent-State/current-context.md`
5. `00-Agent-State/conversation-lanes.yaml`
6. `30-Agent-Index/routes.yaml`
7. Recent files under `05-Daily-Workspace/daily/`
8. `06-Ideas/inbox.md` and `06-Ideas/idea-index.yaml` when ideas matter
9. `50-Projects/common-repositories.yaml` when the work mentions DevTools, TrustMap, CrossDataGen, or common repositories
10. `50-Projects/project-links.yaml` when work or ideas are project-linked
11. `01-Daily-Digest/` and `02-Review-Queue/` only when knowledge backlog affects today's work

Use `scripts/search_kb.py` for candidate discovery when the user asks about prior related ideas, projects, or knowledge:

```bash
python /Users/justin/.codex/skills/daily-work-entry/scripts/search_kb.py "<query>" --scope all --limit 12
```

## Morning Start Mode

Produce a compact morning brief:

- `历史遗留`: open loops and yesterday/today carryover.
- `当前重点`: active projects, active focus, and review pressure.
- `今日建议优先级`: 3-5 ordered priorities with reasons.
- `今日计划`: concrete tasks that fit the day.
- `阻塞与风险`: blockers, stale context, missing decisions.
- `先做第一步`: one immediate action.

If today's workspace file does not exist, create it from `templates/workflow/daily-workspace.md`. Update `00-Agent-State/work-state.yaml` when active focus, open loops, blockers, or next steps change.

## Daily Wrap Mode

Update the current daily workspace with:

- completed work
- work notes
- unfinished tasks
- blockers
- tomorrow carryover
- ideas captured today

Then update `00-Agent-State/work-state.yaml` so the next morning brief starts from accurate open loops.

## Idea Capture Mode

Append to `06-Ideas/inbox.md` using:

```md
### HH:MM - <short title>

- Raw:
- Related Projects:
- Possible Direction:
- Next Step:
- Status: captured
```

Keep it low-friction. Do not turn every idea into a formal card.

Update `06-Ideas/idea-index.yaml` only when the idea has a stable title, obvious project relation, or should be reviewed later. Update `00-Agent-State/idea-state.yaml` when it should appear in `needs_review`.

## Idea Promote Mode

Promote only when the idea is recurring, actionable, project-linked, or explicitly approved.

Create `06-Ideas/ideas/<idea-id>.md` from `templates/workflow/idea-card.md` and include:

- one-sentence idea
- original trigger
- why it might matter
- related knowledge or projects
- validation questions
- next experiment
- status log

If the idea should become durable knowledge, put the promotion decision through `02-Review-Queue/` unless the user explicitly authorizes direct promotion.

## Boundaries

- Keep work rhythm separate from knowledge consolidation.
- Treat ideas as tentative until promoted.
- Do not modify formal knowledge cards, source cards, or indexes unless the user asks for durable promotion.
- Do not invent prior context. If a route or search is weak, say that the knowledge base did not surface a strong match.
