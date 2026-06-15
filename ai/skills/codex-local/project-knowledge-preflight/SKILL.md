---
name: project-knowledge-preflight
description: "Prepare prior personal knowledge before starting or scoping a new project, feature, research direction, implementation plan, repo, or experiment. Use when the user says they are opening/starting a new project or direction and implies personal prior knowledge may be relevant, including phrases such as 开启一个新的项目, 开新项目, 新方向, 项目前置知识, 我之前学过, 我保存过相关知识, 先从个人知识库调上下文, 这个项目需要用到我以前的知识, before we implement check my knowledge base, or when project planning should be grounded in saved personal notes."
---

# Project Knowledge Preflight

## Overview

Use this skill before planning or implementing a new project when the user's saved personal knowledge may contain prerequisites, patterns, source memory, or prior decisions. Produce a compact preflight brief, then continue with the user's actual project task using that brief as context.

Default personal knowledge base path: `/Users/justin/Personal/个人知识库`.

## Resolve Context

1. Identify the current project root from the workspace.
2. Resolve the personal knowledge base path in this order:
   - A path explicitly provided by the user.
   - `PERSONAL_KNOWLEDGE_BASE`, if set.
   - `/Users/justin/Personal/个人知识库`.
3. Read the personal knowledge base entry points:
   - `AGENT_PROTOCOL.md`
   - `00-Agent-State/knowledge-state.yaml`
   - `00-Agent-State/current-context.md`, if present
   - `30-Agent-Index/routes.yaml`

If the project objective is too vague to search meaningfully, ask one concise clarifying question. Otherwise make a reasonable search plan and proceed.

## Preflight Search Workflow

1. Extract search facets from the user's project description:
   - domain and problem type
   - implementation stack or tools
   - concepts and aliases in Chinese and English
   - expected artifacts, datasets, sources, or papers
   - risks, constraints, evaluation criteria, and analogies
2. Search indexes before broad content:
   - `30-Agent-Index/aliases.yaml`
   - `30-Agent-Index/concepts.yaml`
   - `30-Agent-Index/sources.yaml`
   - `30-Agent-Index/questions.yaml`
   - `30-Agent-Index/relations.yaml`
   - `30-Agent-Index/relation-vocabulary.yaml`
   - `50-Projects/common-repositories.yaml` when the project mentions DevTools, TrustMap, CrossDataGen, or common repositories.
3. Use the bundled search helper for candidate discovery:

```bash
python /Users/justin/.codex/skills/project-knowledge-preflight/scripts/search_kb.py "<project/domain/query>" --scope all --limit 15
python /Users/justin/.codex/skills/project-knowledge-preflight/scripts/search_kb.py "<tool/source/query>" --scope sources --limit 10
python /Users/justin/.codex/skills/project-knowledge-preflight/scripts/search_kb.py "<similar project/query>" --scope projects --limit 10
```

4. Read only the likely files from:
   - `10-Knowledge-Cards/`
   - `20-Source-Cards/`
   - `40-Mental-Models/`
   - `50-Projects/`
   - `06-Ideas/` when saved ideas may shape the new project or research direction.
5. Follow relation links for prerequisites, analogies, contrasts, evidence, implementations, and known failure modes.
6. If there are no strong matches, say that the knowledge base did not surface useful prior context and proceed with ordinary project discovery.

## Preflight Brief

Before doing the main project work, produce a short brief with:

- `Relevant Prior Knowledge`: the 3-7 most useful cards, concepts, or source memories.
- `Reusable Patterns`: methods, design moves, snippets, workflows, or mental models that may transfer.
- `Risks And Gaps`: stale notes, disputed ideas, missing prerequisites, or areas needing fresh research.
- `How This Changes The Plan`: concrete implications for the project approach.
- `Files Consulted`: concise paths to cards, source cards, and indexes read.

Then continue into the user's requested project planning, coding, writing, or research task. Keep the brief compact; it is a launchpad, not a literature review.

## Boundaries

- Do not modify the personal knowledge base during preflight unless the user explicitly asks.
- Do not import the current project into the knowledge base; use the broader `personal-knowledge-agent` project extract/import workflows for that.
- Do not treat snippets from the search helper as sufficient evidence. Read matched files before relying on them.
- Prefer status-aware language: `mature` and `active` notes can guide plans; `candidate`, `captured`, or `digested` notes are useful but tentative; `disputed` notes require naming uncertainty.
- Treat idea hits as inspiration or prior intent, not as validated project knowledge. Name them separately under risks, gaps, or possible directions when useful.
