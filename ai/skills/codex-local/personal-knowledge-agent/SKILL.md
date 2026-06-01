---
name: personal-knowledge-agent
description: "Use when working with an agent-first personal knowledge base: answering questions from a knowledge graph, capturing new learning, daily consolidation, promoting knowledge cards, creating Source Cards for papers/GitHub/blogs/videos/books/docs/courses/datasets/projects, extracting knowledge from other project repositories, importing project knowledge packages, finding analogies to existing knowledge, or enabling cross-repository agent queries."
---

# Personal Knowledge Agent

## Overview

Use this skill to operate an agent-first personal knowledge base. Prefer the repository protocol over ad hoc search: read state, route through indexes, inspect relation vocabulary, read only the needed cards, answer or transform knowledge, then write new learning back into the cache layer.

Resolve the knowledge base path in this order:

1. A path explicitly provided by the user.
2. The current working directory, if it contains `AGENT_PROTOCOL.md` and `30-Agent-Index/`.
3. The `PERSONAL_KNOWLEDGE_BASE` environment variable, if available.
4. A previously documented local path in the conversation or project context.

If the user is in another repository and asks to extract or import knowledge, treat that repository as the source project and the resolved personal knowledge base as the destination unless they specify another path.

For full repository conventions, read `references/repository-protocol.md` when working on anything beyond a one-off answer.

## Mode Selection

- **answer-mode**: The user asks a knowledge question, asks for explanation, or asks how a new idea connects to prior knowledge.
- **capture-mode**: The user shares a new insight, question, link, excerpt, or raw learning and wants it saved.
- **consolidate-mode**: The user asks to整理今天, daily consolidate, summarize pending days, or handle lazy reminders.
- **promote-mode**: The user asks to turn cache/digest/import output into formal cards, source cards, relations, or indexes.
- **source-mode**: The user shares a paper, GitHub repo, blog, video, book, documentation, course, dataset, conversation, or project material.
- **analogy-mode**: The user asks what something resembles, how it relates to known knowledge, where an analogy breaks, or what mental model applies.
- **project-extract-mode**: The user is in another project and asks to extract durable knowledge from that project.
- **project-import-mode**: The user asks to import an extraction package or project-derived knowledge into the personal knowledge base.
- **bridge-mode**: Another repository or project asks to query the personal knowledge base.

## Standard Read Order

When inside the personal knowledge base:

1. Read `AGENT_PROTOCOL.md`.
2. Read `00-Agent-State/knowledge-state.yaml`.
3. Read `00-Agent-State/current-context.md`.
4. Use `30-Agent-Index/routes.yaml` to classify the task.
5. Use `30-Agent-Index/aliases.yaml`, `concepts.yaml`, `sources.yaml`, `questions.yaml`, `relations.yaml`, and `relation-vocabulary.yaml` only as needed.
6. Read the smallest useful set of cards from `10-Knowledge-Cards/`, `20-Source-Cards/`, and `40-Mental-Models/`.

When outside the personal knowledge base:

1. Identify the current project root.
2. If extracting knowledge, inspect local memory/docs/discussions first.
3. If querying personal knowledge, read the personal knowledge base protocol and indexes before broad search.

## Answer Mode

For user questions:

1. Route the question before searching widely.
2. Resolve aliases and likely concepts.
3. Follow relations and relation vocabulary for analogies, prerequisites, contrasts, evidence, implementations, and project links.
4. Use status as context:
   - `mature`: stable explanatory frame.
   - `active`: normal reference.
   - `candidate`: useful idea or analogy.
   - `captured` or `digested`: recent context.
   - `disputed`: name the disagreement or uncertainty.
   - `archived`: retrieve only when relevant.
5. Answer in the user's language unless they ask otherwise.
6. Capture new questions, insights, and relation candidates into today's daily inbox unless the user asks not to.

## Capture Mode

Append to `00-Inbox/daily/YYYY-MM-DD.md`. Keep capture low-friction:

```md
## HH:MM - <short title>

### Raw

### Candidate Concepts

### Candidate Sources

### Candidate Relations

### Follow-Up Questions
```

Do not over-polish daily inbox entries. Preserve enough raw context to reconstruct the user's thinking later.

## Consolidate Mode

Use lazy, catch-up consolidation:

1. Read `00-Agent-State/knowledge-state.yaml`.
2. Identify pending dates and matching daily inbox files.
3. If there is a backlog, ask for approval before large consolidation.
4. For multi-day backlog, split work conceptually into digest, concept candidates, source candidates, relation candidates, project/import candidates, and review output.
5. Write:
   - `01-Daily-Digest/YYYY-MM-DD.md`
   - `03-Promotion-Candidates/YYYY-MM-DD-candidates.yaml`
   - `02-Review-Queue/YYYY-MM-DD-review.md` when durable changes are proposed.
6. Update `knowledge-state.yaml` after completing consolidation.

## Promote Mode

Promote candidates only when stable enough or explicitly approved. Durable promotion may create or update:

- `10-Knowledge-Cards/`
- `20-Source-Cards/`
- `30-Agent-Index/`
- `40-Mental-Models/`
- `50-Projects/`

Before adding new formal relation types, update `30-Agent-Index/relation-vocabulary.yaml` with semantic meaning and typical use.

## Source Mode

Treat external materials as Source Cards. Source types include:

- `paper`
- `github-repo`
- `blog-post`
- `video`
- `book`
- `documentation`
- `course`
- `dataset`
- `conversation`
- `project`

A Source Card should record what the material contributes to the knowledge graph: concepts, claims, implementations, examples, contradictions, analogies, evidence, reusable methods, and open questions.

For papers, include DOI and Zotero key when available. For repositories, include repo URL/path, language, notable modules, and evidence files. For videos, include transcript path or timestamps when available.

## Analogy Mode

When the user asks how a new idea relates to existing knowledge:

1. Identify the new idea's mechanism, constraints, incentives, data flow, or failure mode.
2. Search relation graph and mental models before broad text search.
3. Return:
   - closest analogies
   - why the analogy works
   - where it breaks
   - useful prior cards or source cards
   - candidate relations to capture

## Project Extract Mode

Run this in an external project when the user asks to extract knowledge.

Prefer these inputs:

- `99-项目记忆/`
- `0-讨论.md`
- `0-记录/`
- `docs/`
- design docs, meeting notes, research notes, README files
- relevant git history and code files when they contain durable decisions or patterns

Extract concepts, decisions, methods, patterns, lessons, failure modes, source candidates, relation candidates, and evidence paths. Generate a `knowledge-import-package.yaml` using the template in the personal knowledge base.

## Project Import Mode

Run this in the personal knowledge base when importing project-derived knowledge:

1. Stage incoming files under `04-Import-Staging/projects/<project-name>/`.
2. Check `50-Projects/imported-projects.yaml` for prior imports.
3. Detect duplicate or near-duplicate concepts by id, title, aliases, and summaries.
4. Generate an import review file.
5. Register the project in `50-Projects/project-links.yaml`.
6. Promote approved items into cards, sources, relations, indexes, or mental models.

## Bridge Mode

When another repository queries the personal knowledge base:

1. Read the personal knowledge base `AGENT_PROTOCOL.md`.
2. Use index files as the public interface.
3. Return concise, cited pointers to card/source paths.
4. Avoid bulk-loading the entire knowledge base.
