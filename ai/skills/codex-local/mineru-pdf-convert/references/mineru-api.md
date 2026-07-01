# MinerU API Notes

This skill uses the MinerU precise API flow:

1. POST `https://mineru.net/api/v4/file-urls/batch` with file names, `data_id`, model version, formula parsing, and table parsing enabled.
2. PUT each PDF to the returned upload URL.
3. Poll `https://mineru.net/api/v4/extract-results/batch/{batch_id}` until a `full_zip_url` appears or the task fails/times out.
4. Download the result zip.
5. Prefer `full.md` from the zip; otherwise use the first Markdown file.

Local guardrails copied from the working 0-Cyber-Mentor implementation:

- Maximum file size: 200 MB.
- Maximum pages per file: 200.
- Maximum upload links per request: 50.
- Submission rate: 50 files/minute.
- Poll rate: 1000 requests/minute.
- Daily file upload limit: 5000.
- Daily priority pages: 1000.

The script records raw MinerU result metadata in `extraction.json`, but never records or prints the API token.
