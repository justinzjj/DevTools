---
name: server-local-database-access
description: Use this skill whenever the user asks to query, inspect, debug, or use Justin's server_local PostgreSQL paper databases, including paper_collection_literature, paper_collection_control, CCF paper inventory, paperMiner topics, local PDFs, venue/year coverage, runtime ingest queues, worker status, or database access from another project. This skill should trigger even if the user only says "查一下本地文献库", "server_local 数据库", "paper_collection", "paperMiner", "采集队列", "论文库", or asks for SQL against the local paper collection.
---

# server_local Database Access

Use this skill to work with Justin's local PostgreSQL paper databases on `server_local`. The goal is to answer paper-library and runtime-status questions without rereading the long access guide every time.

## Source Of Truth

This skill is distilled from:

- `/Users/justin/ICT/1-个人知识库/4-论文工作/5-CrossDataGNN/2-文档/SERVER_LOCAL_DATABASE_ACCESS_GUIDE.md`

If connection details, row counts, or schemas look stale, reopen that guide first and treat it as authoritative.

## Connection Snapshot

Device:

- SSH alias: `server_local`
- LAN IP: `192.168.31.53`
- Hostname: `blockchain`
- Main repo on server: `/home/justin/workspace/paper-Collection`
- PostgreSQL container: `paper-collection-postgres`
- PostgreSQL port: `5432`

PostgreSQL:

- Host: `192.168.31.53`
- Port: `5432`
- User: `paper_admin`
- Password: `paper_local_dev`
- Main literature DB: `paper_collection_literature`
- Runtime/control DB: `paper_collection_control`

Prefer not to print the password in final user-facing answers unless the user explicitly asks for connection details. Use it in commands only when needed to complete the task.

## Choose The Right Database

Default to `paper_collection_literature` for:

- papers, titles, abstracts, DOI, OpenAlex, DBLP
- authors and keywords
- venues, CCF categories, yearly venue coverage
- local PDF records and `pdf_path`
- paperMiner topics and topic-based discovery

Use `paper_collection_control` only for:

- ingest request status
- queue backlog
- failed or retrying jobs
- worker heartbeats
- venue/year runtime progress

Avoid `paper_collection` unless the user explicitly asks for the old/default database. It is not the current main entry point.

## Access Methods

From local network with `psql`:

```bash
psql "host=192.168.31.53 port=5432 dbname=paper_collection_literature user=paper_admin password=paper_local_dev"
```

From the server itself:

```bash
ssh server_local
cd /home/justin/workspace/paper-Collection
docker ps --filter name=paper-collection-postgres
docker exec -it paper-collection-postgres psql -U paper_admin -d paper_collection_literature
```

For Python:

```python
import psycopg

conn = psycopg.connect(
    host="192.168.31.53",
    port=5432,
    dbname="paper_collection_literature",
    user="paper_admin",
    password="paper_local_dev",
)
```

## Safety And Performance Rules

Many tables are large. Start narrow, verify shape, then expand.

- Use `LIMIT` during exploration.
- Prefer indexed filters when possible:
  - `papers.doi`
  - `papers.year`
  - `papers.openalex_id`
  - `job_queue(status, available_at, priority, id)`
- Avoid pulling full tables into the local terminal.
- Avoid broad `ILIKE '%keyword%'` across `paper_keywords.keyword` unless the user accepts a slow query.
- For control DB queries, always filter or aggregate by `status`, `job_type`, `created_at`, `updated_at`, or `job_id`.
- For large exports, run on the server and write CSV files instead of streaming millions of rows over an interactive connection.
- Prefer read-only SQL unless the user explicitly asks to modify data and confirms the target database/table.

## Table Map

Main literature layer:

- `categories`: CCF/domain categories.
- `venues`: venue metadata, including `name`, `venue_type`, `ccf_rank`, `publisher`, `dblp_series`.
- `yearly_collections`: venue/year collection batches.
- `papers`: main paper entities, including `title`, `normalized_title`, `abstract`, `year`, `doi`, `dblp_key`, `openalex_id`, `pdf_url`, `pdf_path`, `raw_payload`.
- `paper_authors`: author list by `paper_id` and `author_order`.
- `paper_keywords`: keyword list by `paper_id` and `keyword_order`.
- `paper_metadata_sources`: provenance for fields, keyed by `paper_id` and `source_key`.

paperMiner layer:

- `paper_miner_topics`: unique `(domain, topic)` topic list.
- `paper_miner_papers`: deduplicated topic paper entities, including `venue`, `year`, `doi`, `abstract`, `pdf_path`, `local_pdf_exists`.
- `paper_miner_paper_topics`: many-to-many paper-topic relation.
- `paper_miner_keywords`: topic-layer keywords.
- `paper_miner_import_runs`: import batches.

PDF and topic tracking:

- `paper_pdf_files`: runtime downloaded or validated PDF records linked to main `papers.id`.
- `paper_source_entries`: external topic-list source rows and match status.
- `topic_tags`: topic tag definitions.
- `paper_topic_tags`: main-library paper-topic relations.

Runtime/control layer:

- `ingest_requests`: user/script collection requests.
- `ingest_request_targets`: venue/year targets generated from requests.
- `job_queue`: worker queue and status history.
- `job_attempts`: per-attempt worker records and errors.
- `venue_year_progress`: listing/enrichment progress by venue/year.
- `inventory_snapshots`: periodic inventory snapshots.
- `worker_heartbeats`: worker status.

## Common Queries

Connection smoke test:

```sql
SELECT current_database(), current_user, now();
```

Main paper join:

```sql
SELECT p.id, p.year, c.name AS category, v.name AS venue, p.title, p.doi
FROM papers p
JOIN yearly_collections yc ON yc.id = p.yearly_collection_id
JOIN venues v ON v.id = yc.venue_id
JOIN categories c ON c.id = yc.category_id
LIMIT 20;
```

Search title, abstract, or keywords:

```sql
SELECT DISTINCT
  p.id,
  p.year,
  v.name AS venue,
  p.title,
  p.doi,
  p.dblp_url,
  p.openalex_id
FROM papers p
JOIN yearly_collections yc ON yc.id = p.yearly_collection_id
JOIN venues v ON v.id = yc.venue_id
LEFT JOIN paper_keywords pk ON pk.paper_id = p.id
WHERE p.title ILIKE '%blockchain%'
   OR p.abstract ILIKE '%blockchain%'
   OR pk.keyword ILIKE '%blockchain%'
ORDER BY p.year DESC NULLS LAST, v.name
LIMIT 50;
```

Venue/year coverage:

```sql
SELECT
  v.name,
  yc.year,
  COUNT(*) AS papers
FROM papers p
JOIN yearly_collections yc ON yc.id = p.yearly_collection_id
JOIN venues v ON v.id = yc.venue_id
WHERE v.name ILIKE '%VLDB%'
GROUP BY v.name, yc.year
ORDER BY v.name, yc.year;
```

Authors for a paper:

```sql
SELECT p.id, p.title, a.author_order, a.author_name
FROM papers p
JOIN paper_authors a ON a.paper_id = p.id
WHERE p.id = 12345
ORDER BY a.author_order;
```

Keywords for a paper:

```sql
SELECT p.id, p.title, k.keyword_order, k.keyword
FROM papers p
JOIN paper_keywords k ON k.paper_id = p.id
WHERE p.id = 12345
ORDER BY k.keyword_order;
```

paperMiner topic papers and PDFs:

```sql
SELECT
  t.domain,
  t.topic,
  p.year,
  p.venue,
  p.title,
  p.doi,
  p.pdf_path,
  p.local_pdf_exists
FROM paper_miner_papers p
JOIN paper_miner_paper_topics pt ON pt.paper_id = p.id
JOIN paper_miner_topics t ON t.id = pt.topic_id
WHERE t.domain = '数据库'
  AND t.topic = '事务与并发控制'
ORDER BY p.year DESC NULLS LAST, p.venue, p.title
LIMIT 50;
```

Runtime queue summary in `paper_collection_control`:

```sql
SELECT job_type, status, COUNT(*) AS jobs
FROM job_queue
GROUP BY job_type, status
ORDER BY job_type, status;
```

Failed or retrying jobs in `paper_collection_control`:

```sql
SELECT
  id,
  job_type,
  status,
  attempts,
  left(last_error, 300) AS last_error,
  updated_at
FROM job_queue
WHERE status IN ('failed', 'retry_wait')
ORDER BY updated_at DESC
LIMIT 50;
```

## Response Pattern

When answering a user request:

1. State which database you will use and why.
2. Run or propose the smallest query that answers the question.
3. If the result depends on broad fuzzy search or large tables, mention the performance caveat briefly.
4. Summarize results in Chinese by default when the user asks in Chinese.
5. Include the exact SQL only when useful for reproducibility or when the user asks for it.

## Current Scale Reference

As of the 2026-06-11 source guide:

- `papers`: 460,395 rows.
- `paper_authors`: 2,060,246 rows.
- `paper_keywords`: 4,945,306 rows.
- `paper_metadata_sources`: 2,340,505 rows.
- `paper_pdf_files`: 3,053 rows.
- `job_queue`: 4,333,878 rows.
- `job_attempts`: 4,365,301 rows.

Treat these counts as orientation, not a substitute for live `COUNT(*)` when the user asks for current numbers.
