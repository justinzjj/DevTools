---
name: ccf-paper-collection
description: Use this skill when the user wants to collect or update CCF conference or journal papers by category, rank, venue list, year range, or field requirements, and expects the full workflow including CCF scope confirmation, script reuse or adaptation, metadata enrichment, hard-case logging, statistics, and handoff documentation.
---

# CCF Paper Collection

Use this skill when the user asks for a reusable CCF paper-collection workflow or asks to execute a new collection task such as:

- collect CCF papers for a category and rank
- collect specific CCF conferences or journals
- collect papers for a given year range
- enrich abstracts, keywords, DOI, or venue metadata
- continue an unfinished CCF collection run

## Quick start

1. Read [docs/CCF_PAPER_COLLECTION_WORKFLOW.md](/Users/justin/ICT/4-code/paperCollection/docs/CCF_PAPER_COLLECTION_WORKFLOW.md).
2. Extract or infer:
   - `ccf_category`
   - `venue_type`
   - `ccf_rank`
   - `venues`
   - `start_year`
   - `end_year`
   - `required_fields`
3. If the venue list is not explicitly provided, verify the latest CCF directory before choosing venues.
4. Reuse existing scripts if the task matches current repository coverage.
5. Otherwise adapt the existing scripts into a new collector using the same schema and naming rules.
6. Run the collection in phases:
   - proceedings list collection
   - abstract/keyword enrichment
   - publisher-specific backfill
   - statistics and validation
   - README/handoff updates

## Existing repo assets

- Main network-A collector:
  - [scripts/fetch_ccf_network_a_papers.py](/Users/justin/ICT/4-code/paperCollection/scripts/fetch_ccf_network_a_papers.py)
- IEEE abstract backfill:
  - [scripts/fill_ieee_abstracts_with_playwright.py](/Users/justin/ICT/4-code/paperCollection/scripts/fill_ieee_abstracts_with_playwright.py)
- Edge automation profile prep:
  - [scripts/prepare_edge_automation_profile.py](/Users/justin/ICT/4-code/paperCollection/scripts/prepare_edge_automation_profile.py)
- Current workflow playbook:
  - [docs/CCF_PAPER_COLLECTION_WORKFLOW.md](/Users/justin/ICT/4-code/paperCollection/docs/CCF_PAPER_COLLECTION_WORKFLOW.md)

## Required operating rules

- Always keep output under `data/<分类>/<Venue>/<Year>.json`.
- Keep one stable JSON schema per task.
- Record field provenance in `metadata_sources`.
- Do not let hard cases block the whole run.
- Record unresolved items in `handoff/*hard_cases.json`.
- Update README and handoff after substantial progress.
- For current publisher-browser automation, do not attach Playwright directly to a live Edge profile.

## Publisher strategy

- `IEEE`: prefer API enrichment first, then use the Playwright backfill script with an isolated Edge profile.
- `USENIX`: prefer direct paper-page extraction.
- `ACM`: prefer API or public page extraction first; only add browser automation if really needed.

## Delivery checklist

Before finishing, make sure you have:

- written or updated year JSON files
- recomputed missing abstract/keyword counts
- updated a human-readable README
- updated or created a handoff note
- written hard cases to a dedicated JSON file if unresolved items remain

## When adapting to a new CCF task

Prefer this order:

1. confirm scope
2. design schema
3. map venue names to source endpoints
4. implement or adapt the base collector
5. enrich metadata
6. isolate hard cases
7. summarize results

If the task is not the already-supported network-A set, adapt the current scripts instead of starting from scratch unless the source ecosystem is completely different.
