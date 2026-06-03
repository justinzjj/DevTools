# Repository Protocol Reference

## Knowledge Base Path Resolution

Resolve the knowledge base path in this order:

1. A path explicitly provided by the user.
2. The current working directory, if it contains `AGENT_PROTOCOL.md` and `30-Agent-Index/`.
3. The `PERSONAL_KNOWLEDGE_BASE` environment variable, if available.
4. A previously documented local path in the conversation or project context.

## Key Files

- `AGENT_PROTOCOL.md`: read-first protocol.
- `00-Agent-State/knowledge-state.yaml`: lazy reminder and consolidation state.
- `00-Agent-State/current-context.md`: current working context.
- `00-Inbox/daily/`: raw daily capture.
- `01-Daily-Digest/`: daily or batch digest.
- `02-Review-Queue/`: human review before durable promotion.
- `03-Promotion-Candidates/`: structured candidates.
- `04-Import-Staging/`: project import staging.
- `10-Knowledge-Cards/`: formal knowledge cards.
- `20-Source-Cards/`: source cards for papers, repos, posts, videos, books, docs, courses, datasets, conversations, and projects.
- `30-Agent-Index/`: agent-readable indexes and relation graph.
- `40-Mental-Models/`: stable cross-domain models.
- `50-Projects/`: external project links and import history.
- `templates/`: card, workflow, and import templates.

## Lifecycle

```text
Daily Inbox
  -> Daily Digest
  -> Promotion Candidates
  -> Review Queue
  -> Knowledge Cards / Source Cards / Relations / Mental Models
```

## Status Semantics

- `captured`: recent rough context.
- `digested`: processed background.
- `candidate`: useful idea, analogy, or future card.
- `active`: formal usable knowledge.
- `mature`: stable explanatory frame.
- `disputed`: useful but contested or uncertain.
- `archived`: low-priority historical knowledge.

Status does not forbid use. It tells the agent how to frame the information.

## Relation Vocabulary

Relations are open vocabulary. `relation-vocabulary.yaml` explains relation semantics. `relations.yaml` stores edges. New formal relation types need a vocabulary entry with Chinese name, meaning, typical use, inverse when useful, examples, and boundary notes.

## Import Package

External project extraction should produce a package shaped like:

```yaml
package_type: personal-knowledge-import
version: 1
source_project:
  name:
  path:
  repo:
  extracted_at:
items:
  - kind: concept_candidate
    title:
    summary:
    suggested_id:
    domains: []
    evidence:
      - file:
        quote_or_summary:
    proposed_relations: []
    import_target:
      - promotion-candidates
import_notes:
  duplicate_risk: unknown
  needs_human_review: true
```

## Zotero Paper Import

When Zotero is the paper source, use it as a read-only evidence layer unless the user explicitly asks to modify Zotero. Import lightweight paper memory rather than dense literature-review notes by default.

Recommended flow:

1. Narrow the scope by collection, tag, search query, star/important marker, non-empty child notes, or explicit user selection.
2. Read parent metadata, creators, year/date, DOI, URL, citation key, Zotero key, tags, collections, child notes, and attachment presence.
3. Treat `/unread` only as a status tag, not as evidence of reading.
4. Stage output under `04-Import-Staging/zotero/<YYYY-MM-DD>-<scope>/`.
5. Put draft paper cards and `zotero-import-package.yaml` in staging.
6. Put the human review summary in `02-Review-Queue/`.
7. Promote to `20-Source-Cards/paper/` and `30-Agent-Index/sources.yaml` only after approval.

Draft paper cards should answer:

- What is this material?
- Why might the user want to retrieve it later?
- Which direction/method/failure mode does it represent?
- What Zotero evidence points back to it?
- What should happen next: leave as memory, compare, reread, or promote into formal knowledge?
