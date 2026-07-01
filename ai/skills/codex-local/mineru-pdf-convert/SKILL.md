---
name: mineru-pdf-convert
description: Convert PDF files into Markdown with MinerU's precise API, including extracted assets, formulas, tables, per-paper metadata, dry-run manifests, and batch directory processing. Use when the user asks to use MinerU, parse/convert/extract PDFs to Markdown, process paper PDFs, convert a Zotero PDF attachment to Markdown, or batch-convert a folder of PDFs for research reading or corpus building.
---

# MinerU PDF Convert

## Quick Start

Use the bundled script from any project:

```bash
python3 /Users/justin/.codex/skills/mineru-pdf-convert/scripts/mineru_pdf_convert.py \
  --input-pdf path/to/paper.pdf \
  --output-dir mineru-md
```

For a folder:

```bash
python3 /Users/justin/.codex/skills/mineru-pdf-convert/scripts/mineru_pdf_convert.py \
  --input-dir path/to/pdfs \
  --output-dir mineru-md
```

Run a preflight first when converting more than one PDF or when token/network cost matters:

```bash
python3 /Users/justin/.codex/skills/mineru-pdf-convert/scripts/mineru_pdf_convert.py \
  --input-dir path/to/pdfs \
  --output-dir mineru-md \
  --dry-run
```

## Workflow

1. Resolve the PDF path(s). For Zotero requests, use the Zotero skill/helper to retrieve attachment file URLs or paths, then pass the local PDF path to this script.
2. Run `--dry-run` for batch jobs, large PDFs, or uncertain paths. Inspect `preflight.files` for blocked/skipped files.
3. Run the real conversion without `--dry-run`.
4. Check the JSON summary printed to stdout and the written `extraction_manifest.json`.
5. Open the generated `paper.md` and confirm the Markdown is non-empty before using it for downstream analysis.

## Outputs

Each PDF creates:

```text
<output-dir>/<pdf-stem-slug>/
├── paper.md
├── extraction.json
├── extraction.log
├── mineru-result.zip
└── assets/
```

The script skips an existing converted output unless `--force` is supplied. A converted output requires both `paper.md` and `extraction.json` with `"status": "converted"`.

## Credentials

The script reads the MinerU token from `MINERU_TOKEN` first. If the environment variable is absent, it reads the skill-private file:

```text
/Users/justin/.codex/skills/mineru-pdf-convert/.mineru.env
```

Do not print, summarize, or quote the token. Dry-run manifests intentionally include only the credential environment variable name.

## Options

- Use `--model-version vlm` by default. Other accepted values are `pipeline` and `MinerU-HTML`.
- Use `--poll-timeout 900` by default; increase it for large or slow documents.
- Use `--daily-page-budget 0` to disable the local daily page budget check.
- Use `--force` to overwrite a previously converted PDF folder.

## Reference

Read `references/mineru-api.md` only when adjusting limits, endpoint behavior, or failure handling.
