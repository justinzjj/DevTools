---
name: "paper-pdf-zotero-pipeline"
description: "Use when the user wants to download academic papers as PDFs through institutional access, keep browser login isolated, store files in a structured local path, validate that downloads are real PDFs, and import them into Zotero. Trigger on requests about IEEE/ACM/Springer paper downloading, institutional login, Edge/Playwright browser automation, PDF collection pipelines, or Zotero import workflows."
---

# Paper PDF + Zotero Pipeline

Use this skill for the end-to-end workflow:

- accept a paper list or queue
- resolve DOI / landing page metadata
- download PDFs with institutional login when needed
- store them locally under a structured path
- verify every saved file is a real PDF
- import the result into Zotero

This workflow is designed for the exact failure modes that commonly show up with IEEE / ACM / Springer:

- login state disappearing when the browser profile is mishandled
- IEEE `stamp.jsp` pages returning HTML viewer shells instead of real PDFs
- stale `downloaded` states that actually point to non-PDF files
- Zotero MCP being read-only while the local Zotero connector is writable

## Core Rules

1. Never use the user’s live Edge or Chrome profile for automation.
2. Always use one isolated persistent browser profile and reuse it across login + download.
3. Always validate downloaded files by checking that the file starts with `%PDF-`.
4. Never claim Zotero import success without verifying that the created Zotero item has a PDF child attachment.
5. If Zotero MCP is read-only, switch to the local Zotero connector at `http://127.0.0.1:23119`.

## Safety

### Browser profile

- Use an isolated profile such as `.cache/edge-automation-profile`
- Do not copy a live in-use browser profile to worker directories
- If login cookies matter, close the isolated browser cleanly before reusing the same profile in an automated download worker

### Credentials

- Keep institutional credentials in a local ignored file, such as `.secrets/academic_login.json`
- Add `.secrets/` to `.gitignore`
- Do not print the password back to the user

Template fields that matter:

- `institution_name`
- `institution_aliases`
- `sso.provider`
- `sso.login_domains`
- `sso.shared_email`
- `sso.shared_password`
- `accounts[].institution_candidates`

Useful institution aliases for this workflow:

- `中国科学院`
- `Chinese Academy of Sciences`
- `CAS`
- `中国科学院大学`
- `University of Chinese Academy of Sciences`
- `UCAS`
- `Academy of Mathematics & Systems Science CAS`
- `Academy of Mathematics & Systems Science CAS (CST Cloud)`

Useful SSO hints:

- `中国科技云`
- `CSTCloud`
- `escience.cn`
- `passport.escience.cn`

## Repo-Aware Workflow

If the current repo already has a PDF runtime like `scripts/pdf_runtime/`, reuse it.

If it does not exist, scaffold equivalents for:

- queue ingestion
- DOI / landing-page resolution
- isolated-browser PDF downloading
- download status inspection
- Zotero connector import
- PDF integrity auditing

Recommended local locations:

- queue DB: `.cache/pdf-runtime/pdf_tasks.sqlite3`
- download root: `data/论文PDF/`
- isolated profile: `.cache/edge-automation-profile`
- credentials: `.secrets/academic_login.json`

## Local Path Convention

Store PDFs under:

```text
方向/期刊或会议/等级/年份_论文名.pdf
```

Requirements:

- sanitize `/ \\ : * ? " < > |`
- collapse duplicate whitespace
- cap overly long filenames and append a stable hash suffix

## Download Workflow

### Step 1: inspect the queue

Check current status counts first.

If the repo has a helper like `show_pdf_status.py`, use it.
Otherwise query the SQLite queue directly.

### Step 2: resolve metadata

Resolve DOI, publisher, landing page, and direct PDF hints before downloading.

When Crossref is used:

- do not trust venue-based publisher guesses over authoritative DOI metadata
- correct mismatches such as venue implying ACM while Crossref resolves to IEEE, or vice versa

### Step 3: prepare the isolated browser

Use the `playwright` skill when browser interaction is needed.

Prefer commands like:

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export PWCLI="$CODEX_HOME/skills/playwright/scripts/playwright_cli.sh"
"$PWCLI" open https://ieeexplore.ieee.org --browser msedge --headed --persistent --profile .cache/edge-automation-profile
```

Open only the isolated profile. Never attach Playwright to the user’s normal Edge profile.

### Step 4: login handling

If institutional selection appears, try institution aliases instead of assuming the exact display name.

For this workflow, IEEE may show:

- `Academy of Mathematics & Systems Science CAS (CST Cloud)`

If login redirects to `escience.cn`, assume the shared institutional credentials from the local secrets file.

### Step 5: publisher-specific downloading

#### IEEE

- Prefer browser-context capture over raw HTTP requests
- `stamp.jsp` can return an HTML PDF viewer shell instead of a real PDF
- Direct request paths can trigger `418` or TLS disconnects
- Prefer watching actual browser `response` events and only accept bodies beginning with `%PDF-`

#### ACM

- `https://dl.acm.org/doi/pdf/<doi>` is often the best candidate
- Filter out noisy off-site resources when scraping page links

#### Springer

- Prefer the article or chapter landing page first
- Extract the actual PDF link from the page
- Do not rely only on guessed `content/pdf/<doi>.pdf` URLs

### Step 6: audit the downloaded files

After every batch, scan the local PDF directory and verify that each file begins with `%PDF-`.

If a file is not a real PDF:

- delete the bad file
- reset its queue status back to `awaiting_download`
- rerun the download

This check is mandatory. IEEE HTML viewer shells can masquerade as PDFs.

## Zotero Workflow

### First choice: local Zotero connector

If Zotero is running locally, check:

```bash
curl -sS http://127.0.0.1:23119/connector/ping
```

If it responds with `Zotero is running`, use it.

Useful endpoints:

- `/connector/getSelectedCollection`
- `/connector/saveItems`
- `/connector/saveAttachment`
- `/api/users/0/items/top`
- `/api/users/0/items/<key>/children`

### MCP fallback

If the exposed Zotero MCP is read-only, do not block on it. Use the local connector instead.

### Import rules

1. Query the currently selected Zotero collection via `/connector/getSelectedCollection`
2. Save the bibliographic item with `/connector/saveItems`
3. Save the local PDF bytes as a child attachment with `/connector/saveAttachment`
4. Query the created item again and verify that it now has a PDF child attachment

Important connector behavior:

- `saveItems` alone does not import local PDF bytes
- use a stable per-item connector-side `id`
- pass the same `sessionID` to `saveAttachment`
- set `parentItemID` in attachment metadata to the connector-side item `id`

### Classification when collection creation is unavailable

The local connector can write items and attachments, but it may not expose collection-tree creation.

If automatic collection creation is unavailable:

- import into the currently selected Zotero collection
- preserve the original category path in tags and in `extra`

Recommended tags:

- `方向:<方向>`
- `Venue:<venue>`
- `CCF:<rank>`
- `CollectionPath1:<part>`
- `CollectionPath2:<part>`
- `CollectionPath3:<part>`

Recommended `extra` lines:

- `Collection Path: <方向> / <venue> / <rank>`
- `Local PDF Path: <abs-path>`

## Verification Checklist

Before closing the task, verify:

- download queue shows the expected statuses
- every imported local file begins with `%PDF-`
- Zotero import status is recorded locally
- each created Zotero item has a PDF child attachment
- duplicates are detected by DOI or normalized title before importing again

## Preferred Output to the User

Report:

- how many papers were downloaded
- how many were imported to Zotero
- which collection received them
- any duplicates that were detected and skipped
- any residual manual cleanup needed

If temporary smoke-test items were created during debugging, disclose them clearly and avoid silently leaving junk in the user’s library.
