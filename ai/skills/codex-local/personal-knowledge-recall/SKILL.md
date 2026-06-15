---
name: personal-knowledge-recall
description: "Recall relevant prior knowledge from Justin's personal knowledge base before answering. Use when the user says or implies they have previously learned, saved, recorded, read, captured, or stored something in the personal knowledge base, including phrases such as 我之前学过, 我保存过, 我记录过, 我的个人知识库里有, 知识库中有没有, 以前的笔记, 之前看过, 之前沉淀过, 帮我从个人知识库找, 先查一下我的知识库, or when a new question should be grounded in already saved personal notes."
---

# Personal Knowledge Recall

## Overview

Use this skill as a lightweight recall layer over the personal knowledge base. Prefer the knowledge-base protocol and indexes over broad search, then answer with concise, cited pointers to the specific cards, source cards, or index files used.

Default personal knowledge base path: `/Users/justin/Personal/个人知识库`.

## Resolve The Knowledge Base

Resolve the path in this order:

1. A path explicitly provided by the user.
2. `PERSONAL_KNOWLEDGE_BASE`, if set.
3. The current working directory, if it contains `AGENT_PROTOCOL.md` and `30-Agent-Index/`.
4. `/Users/justin/Personal/个人知识库`.

If the resolved path does not contain `AGENT_PROTOCOL.md`, say the knowledge base was not found and ask for the correct path.

## Recall Workflow

1. Extract the user's concrete recall targets: concepts, technologies, domains, people, source names, project names, analogies, and Chinese aliases.
2. Read the smallest protocol surface first:
   - `AGENT_PROTOCOL.md`
   - `00-Agent-State/knowledge-state.yaml`
   - `00-Agent-State/current-context.md`, if it exists
3. Route through `30-Agent-Index/routes.yaml` when the request resembles analogy, source lookup, project memory lookup, explanation, comparison, or card creation.
4. Inspect only the relevant index files:
   - `30-Agent-Index/aliases.yaml` for alternate names and Chinese/English terms.
   - `30-Agent-Index/concepts.yaml` for likely knowledge cards.
   - `30-Agent-Index/sources.yaml` for papers, books, blogs, videos, docs, courses, and project sources.
   - `30-Agent-Index/relations.yaml` and `relation-vocabulary.yaml` for dependencies, analogies, contrasts, evidence, implementations, or project links.
5. Use `scripts/search_kb.py` for candidate discovery when indexes do not immediately identify the target:

```bash
python /Users/justin/.codex/skills/personal-knowledge-recall/scripts/search_kb.py "<query>" --scope all --limit 12
```

Use narrower scopes when useful: `index`, `cards`, `sources`, or `projects`.

6. Read the smallest useful set of matched files from:
   - `10-Knowledge-Cards/`
   - `20-Source-Cards/`
   - `40-Mental-Models/`
   - `50-Projects/`
   - `06-Ideas/` when the request asks about prior ideas, half-formed directions, possible projects, or "我之前想到过什么".
7. If matches are weak, run one broader `rg` pass over the knowledge base before concluding nothing was found.
8. Answer in the user's language. Distinguish direct knowledge-base evidence from inference.

## Answer Shape

For normal recall, answer with:

- The strongest retrieved knowledge, in plain language.
- Where it came from, using file paths and line references when available.
- Any uncertainty, stale status, or conflicting notes.
- A short suggestion for how to use the recalled knowledge in the current task.

When nothing strong is found, say so directly. Do not invent remembered knowledge. Offer to capture the current question or insight into the daily inbox only if that would help.

## Boundaries

- Do not bulk-load the whole knowledge base.
- Do not promote new cards or update indexes unless the user explicitly asks.
- Do not treat a search hit as truth. Read the underlying card or source before relying on it.
- Use status vocabulary from `knowledge-state.yaml` and cards when present: `captured`, `digested`, `candidate`, `active`, `mature`, `disputed`, `archived`.
- Treat `06-Ideas/` as tentative memory. Ideas are not established knowledge unless promoted into cards, projects, or source-backed notes.
