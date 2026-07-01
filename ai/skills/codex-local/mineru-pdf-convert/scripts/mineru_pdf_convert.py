#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MINERU_FILE_URLS_BATCH_ENDPOINT = "https://mineru.net/api/v4/file-urls/batch"
MINERU_EXTRACT_RESULTS_BATCH_ENDPOINT = "https://mineru.net/api/v4/extract-results/batch"
MINERU_LIMITS = {
    "max_file_size_mb": 200,
    "max_pages_per_file": 200,
    "max_upload_links_per_request": 50,
    "submission_rate_files_per_minute": 50,
    "result_poll_rate_requests_per_minute": 1000,
    "daily_file_upload_limit": 5000,
    "daily_priority_pages": 1000,
}
SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_ENV = SKILL_ROOT / ".mineru.env"


def slugify_pdf_stem(path: Path) -> str:
    stem = path.stem.strip()
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", stem)
    slug = re.sub(r"_+", "_", slug).strip("._-")
    return slug or "paper"


def mineru_data_id(pdf_path: Path, max_length: int = 128) -> str:
    slug = slugify_pdf_stem(pdf_path)
    if len(slug) <= max_length:
        return slug
    digest = hashlib.sha1(slug.encode("utf-8")).hexdigest()[:10]
    prefix_length = max_length - len(digest) - 1
    return f"{slug[:prefix_length].rstrip('._-')}_{digest}"


def discover_pdfs(input_pdf: str | None, input_dir: str | None) -> list[Path]:
    if input_pdf:
        return [Path(input_pdf).expanduser()]
    assert input_dir is not None
    return sorted(Path(input_dir).expanduser().glob("*.pdf"))


def pdf_page_count(pdf_path: Path) -> int | None:
    pdfinfo = shutil.which("pdfinfo")
    if not pdfinfo:
        return None
    result = subprocess.run(
        [pdfinfo, str(pdf_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def output_is_converted(pdf_path: Path, output_dir: Path) -> bool:
    paper_dir = output_dir / slugify_pdf_stem(pdf_path)
    paper_md = paper_dir / "paper.md"
    extraction_json = paper_dir / "extraction.json"
    if not paper_md.exists() or not extraction_json.exists():
        return False
    try:
        metadata = json.loads(extraction_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return metadata.get("status") == "converted"


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_token(token_env: str, config_file: Path | None = None) -> str | None:
    token = os.environ.get(token_env)
    if token:
        return token
    env_file = config_file or DEFAULT_PRIVATE_ENV
    return load_env_file(env_file).get(token_env) or load_env_file(env_file).get("MINERU_TOKEN")


def build_preflight(
    pdfs: list[Path],
    output_dir: Path,
    *,
    max_files_per_run: int,
    max_file_size_mb: int,
    max_pages_per_file: int,
    daily_page_budget: int,
    skip_existing: bool,
) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    eligible_count = 0
    skipped_count = 0
    blocked_count = 0
    total_known_pages = 0

    for pdf in pdfs:
        size_bytes = pdf.stat().st_size if pdf.exists() else 0
        size_mb = size_bytes / (1024 * 1024)
        page_count = pdf_page_count(pdf) if pdf.exists() else None
        if page_count is not None:
            total_known_pages += page_count
        converted = output_is_converted(pdf, output_dir)
        reasons: list[str] = []
        status = "eligible"
        eligible = True

        if not pdf.exists():
            status = "blocked"
            eligible = False
            reasons.append("input PDF does not exist")
        elif skip_existing and converted:
            status = "skipped"
            eligible = False
            skipped_count += 1
            reasons.append("existing converted output found")
        else:
            if size_mb > max_file_size_mb:
                status = "blocked"
                eligible = False
                reasons.append(f"file size exceeds MinerU limit: {size_mb:.2f}MB > {max_file_size_mb}MB")
            if page_count is not None and page_count > max_pages_per_file:
                status = "blocked"
                eligible = False
                reasons.append(f"page count exceeds MinerU limit: {page_count} > {max_pages_per_file}")

        if eligible:
            eligible_count += 1
        elif status == "blocked":
            blocked_count += 1

        files.append(
            {
                "pdf_path": str(pdf),
                "paper_id": slugify_pdf_stem(pdf),
                "size_bytes": size_bytes,
                "size_mb": round(size_mb, 3),
                "page_count": page_count,
                "existing_converted": converted,
                "status": status,
                "eligible": eligible,
                "reasons": reasons,
            }
        )

    global_reasons: list[str] = []
    if eligible_count > max_files_per_run:
        global_reasons.append(f"eligible PDF count exceeds --max-files-per-run: {eligible_count} > {max_files_per_run}")
    if daily_page_budget > 0 and total_known_pages > daily_page_budget:
        global_reasons.append(f"known page count exceeds --daily-page-budget: {total_known_pages} > {daily_page_budget}")

    if global_reasons:
        for file_info in files:
            if file_info["eligible"]:
                file_info["eligible"] = False
                file_info["status"] = "blocked"
                file_info["reasons"] = list(file_info["reasons"]) + global_reasons
        blocked_count += eligible_count
        eligible_count = 0

    return {
        "backend": "mineru",
        "eligible_count": eligible_count,
        "skipped_count": skipped_count,
        "blocked_count": blocked_count,
        "total_known_pages": total_known_pages,
        "global_reasons": global_reasons,
        "files": files,
    }


def request_json(method: str, url: str, *, headers: dict[str, str], payload: dict[str, Any] | None = None, timeout: int = 60) -> tuple[int, dict[str, Any]]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
            return response.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {"text": text}
        return exc.code, payload


def put_file_to_presigned_url(upload_url: str, pdf_path: Path, timeout: int = 180) -> tuple[int, str]:
    parsed = urllib.parse.urlparse(upload_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return 0, "invalid upload URL"
    target = parsed.path or "/"
    if parsed.query:
        target = f"{target}?{parsed.query}"
    connection_class = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    body = pdf_path.read_bytes()
    connection = connection_class(parsed.netloc, timeout=timeout)
    try:
        # Do not send Content-Type: OSS pre-signed URLs include signed headers.
        connection.request("PUT", target, body=body, headers={"Content-Length": str(len(body))})
        response = connection.getresponse()
        text = response.read().decode("utf-8", errors="replace")
        return response.status, text
    finally:
        connection.close()


def mineru_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "*/*",
    }


def result_data(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        return payload["data"]
    return {}


def find_nested_value(data: Any, keys: set[str]) -> Any | None:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in keys:
                return value
            found = find_nested_value(value, keys)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = find_nested_value(item, keys)
            if found is not None:
                return found
    return None


def select_full_markdown_from_zip(zip_path: Path, output_dir: Path) -> str:
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        preferred = [name for name in names if name.endswith("full.md")]
        fallback = [name for name in names if name.lower().endswith(".md")]
        candidates = preferred or fallback
        if not candidates:
            raise RuntimeError("MinerU result zip does not contain a markdown file")
        markdown_name = candidates[0]
        markdown = archive.read(markdown_name).decode("utf-8")
        archive.extractall(output_dir)
        return markdown


def save_markdown_result(
    pdf_path: Path,
    output_dir: Path,
    markdown: str,
    raw_result: dict[str, Any],
) -> dict[str, Any]:
    paper_id = slugify_pdf_stem(pdf_path)
    paper_dir = output_dir / paper_id
    assets_dir = paper_dir / "assets"
    paper_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(exist_ok=True)
    paper_md = paper_dir / "paper.md"
    extraction_json = paper_dir / "extraction.json"
    extraction_log = paper_dir / "extraction.log"

    paper_md.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    metadata = {
        "backend": "mineru",
        "status": "converted",
        "pdf_path": str(pdf_path),
        "paper_id": paper_id,
        "paper_md_path": str(paper_md),
        "assets_dir": str(assets_dir),
        "page_count": pdf_page_count(pdf_path),
        "text_chars": len(markdown),
        "converted_at": datetime.now(timezone.utc).isoformat(),
        "raw_result": raw_result,
    }
    extraction_json.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    extraction_log.write_text(
        "\n".join(["backend=mineru", "status=converted", f"pdf_path={pdf_path}", f"paper_md_path={paper_md}"]) + "\n",
        encoding="utf-8",
    )
    return metadata


def convert_pdf_with_mineru(
    pdf_path: Path,
    output_dir: Path,
    *,
    token_env: str,
    config_file: Path | None,
    model_version: str,
    poll_interval: float,
    poll_timeout: float,
) -> dict[str, Any]:
    token = load_token(token_env, config_file)
    if not token:
        return {
            "pdf_path": str(pdf_path),
            "status": "failed",
            "backend": "mineru",
            "error": f"{token_env} is required; set it in the environment or {DEFAULT_PRIVATE_ENV}",
        }

    data_id = mineru_data_id(pdf_path)
    headers = mineru_headers(token)
    create_payload = {
        "files": [{"name": pdf_path.name, "data_id": data_id}],
        "model_version": model_version,
        "enable_formula": True,
        "enable_table": True,
    }
    create_status, create_json = request_json("POST", MINERU_FILE_URLS_BATCH_ENDPOINT, headers=headers, payload=create_payload, timeout=60)
    if create_status >= 400 or create_json.get("code") not in (0, "0", None):
        return {
            "pdf_path": str(pdf_path),
            "status": "failed",
            "backend": "mineru",
            "http_status": create_status,
            "error": "failed to request MinerU upload URL",
            "response": create_json,
        }

    data = result_data(create_json)
    file_urls = data.get("file_urls")
    batch_id = data.get("batch_id")
    if not isinstance(file_urls, list) or not file_urls:
        return {
            "pdf_path": str(pdf_path),
            "status": "failed",
            "backend": "mineru",
            "error": "MinerU upload URL response did not include file_urls",
            "response": create_json,
        }

    upload_status, upload_text = put_file_to_presigned_url(str(file_urls[0]), pdf_path)
    if upload_status not in (200, 201, 204):
        return {
            "pdf_path": str(pdf_path),
            "status": "failed",
            "backend": "mineru",
            "http_status": upload_status,
            "error": "failed to upload PDF to MinerU upload URL",
            "response_text": upload_text[:500],
        }
    if not batch_id:
        return {
            "pdf_path": str(pdf_path),
            "status": "submitted",
            "backend": "mineru",
            "response": create_json,
            "error": "file uploaded but MinerU response did not include batch_id",
        }

    deadline = time.monotonic() + poll_timeout
    last_payload: dict[str, Any] | None = None
    full_zip_url: str | None = None
    final_state: str | None = None
    while time.monotonic() < deadline:
        poll_status, poll_json = request_json(
            "GET",
            f"{MINERU_EXTRACT_RESULTS_BATCH_ENDPOINT}/{batch_id}",
            headers=headers,
            timeout=60,
        )
        last_payload = poll_json
        data = result_data(poll_json)
        state = find_nested_value(data, {"state"})
        final_state = str(state) if state is not None else final_state
        found_zip = find_nested_value(data, {"full_zip_url"})
        if isinstance(found_zip, str) and found_zip:
            full_zip_url = found_zip
            break
        err_msg = find_nested_value(data, {"err_msg"})
        if poll_status >= 400 or state == "failed" or err_msg:
            return {
                "pdf_path": str(pdf_path),
                "status": "failed",
                "backend": "mineru",
                "batch_id": batch_id,
                "http_status": poll_status,
                "error": str(err_msg or "MinerU task failed"),
                "response": last_payload,
            }
        time.sleep(poll_interval)

    if not full_zip_url:
        return {
            "pdf_path": str(pdf_path),
            "status": "submitted",
            "backend": "mineru",
            "batch_id": batch_id,
            "state": final_state,
            "error": "MinerU task did not finish before poll timeout",
            "response": last_payload,
        }

    paper_id = slugify_pdf_stem(pdf_path)
    paper_dir = output_dir / paper_id
    assets_dir = paper_dir / "assets"
    paper_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(exist_ok=True)
    zip_path = paper_dir / "mineru-result.zip"
    with urllib.request.urlopen(full_zip_url, timeout=180) as remote:
        zip_path.write_bytes(remote.read())
    markdown = select_full_markdown_from_zip(zip_path, assets_dir)
    return save_markdown_result(
        pdf_path=pdf_path,
        output_dir=output_dir,
        markdown=markdown,
        raw_result={"batch_id": batch_id, "full_zip_url": full_zip_url, "state": final_state},
    )


def preflight_result(file_info: dict[str, Any]) -> dict[str, Any]:
    reasons = file_info.get("reasons")
    reason_text = "; ".join(str(reason) for reason in reasons) if isinstance(reasons, list) else ""
    return {
        "pdf_path": file_info.get("pdf_path"),
        "paper_id": file_info.get("paper_id"),
        "status": file_info.get("status"),
        "backend": "preflight",
        "error": reason_text,
    }


def print_manifest(manifest: dict[str, Any]) -> None:
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert PDFs to Markdown with MinerU.")
    parser.add_argument("--input-pdf", help="Single PDF to convert.")
    parser.add_argument("--input-dir", help="Directory of PDFs to convert.")
    parser.add_argument("--output-dir", default="mineru-md", help="Output directory. Defaults to ./mineru-md.")
    parser.add_argument("--backend", choices=["mineru"], default="mineru", help="Compatibility option; this skill uses the MinerU precise API.")
    parser.add_argument("--token-env", default="MINERU_TOKEN", help="Environment variable containing the MinerU token.")
    parser.add_argument("--config-file", type=Path, help="Optional .env-style token file. Defaults to the skill-private .mineru.env.")
    parser.add_argument("--model-version", default="vlm", choices=["pipeline", "vlm", "MinerU-HTML"], help="MinerU precise API model version.")
    parser.add_argument("--poll-interval", type=float, default=5.0, help="Polling interval in seconds.")
    parser.add_argument("--poll-timeout", type=float, default=900.0, help="Maximum polling time in seconds.")
    parser.add_argument("--max-files-per-run", type=int, default=MINERU_LIMITS["max_upload_links_per_request"], help="Maximum eligible PDFs in one run.")
    parser.add_argument("--daily-page-budget", type=int, default=MINERU_LIMITS["daily_priority_pages"], help="Maximum known pages to process; use 0 to disable.")
    parser.add_argument("--max-file-size-mb", type=int, default=MINERU_LIMITS["max_file_size_mb"], help="Maximum PDF size.")
    parser.add_argument("--max-pages-per-file", type=int, default=MINERU_LIMITS["max_pages_per_file"], help="Maximum PDF pages.")
    parser.add_argument("--force", action="store_true", help="Re-convert even when converted output exists.")
    parser.add_argument("--dry-run", action="store_true", help="Print a manifest without calling MinerU or writing outputs.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.input_pdf and not args.input_dir:
        parser.error("one of --input-pdf or --input-dir is required")

    pdfs = discover_pdfs(args.input_pdf, args.input_dir)
    output_dir = Path(args.output_dir).expanduser()
    preflight = build_preflight(
        pdfs,
        output_dir,
        max_files_per_run=args.max_files_per_run,
        max_file_size_mb=args.max_file_size_mb,
        max_pages_per_file=args.max_pages_per_file,
        daily_page_budget=args.daily_page_budget,
        skip_existing=not args.force,
    )
    planned_outputs = [
        {
            "pdf_path": str(pdf),
            "paper_dir": str(output_dir / slugify_pdf_stem(pdf)),
            "paper_md_path": str(output_dir / slugify_pdf_stem(pdf) / "paper.md"),
            "extraction_json_path": str(output_dir / slugify_pdf_stem(pdf) / "extraction.json"),
        }
        for pdf in pdfs
    ]

    if args.dry_run:
        print_manifest(
            {
                "operation": "mineru_pdf_convert",
                "dry_run": True,
                "backend": "mineru",
                "inputs": {"input_pdf": args.input_pdf, "input_dir": args.input_dir, "pdf_count": len(pdfs)},
                "output_dir": args.output_dir,
                "planned_outputs": planned_outputs,
                "preflight": preflight,
                "side_effects": "none",
                "api": {
                    "upload_endpoint": MINERU_FILE_URLS_BATCH_ENDPOINT,
                    "result_endpoint": MINERU_EXTRACT_RESULTS_BATCH_ENDPOINT,
                    "requires_token": True,
                    "token_env": args.token_env,
                    "model_versions": ["pipeline", "vlm", "MinerU-HTML"],
                    "selected_model_version": args.model_version,
                    "limits": MINERU_LIMITS,
                },
                "credential_env": args.token_env,
            }
        )
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    submit_delay = 60 / MINERU_LIMITS["submission_rate_files_per_minute"]
    poll_interval = max(args.poll_interval, 60 / MINERU_LIMITS["result_poll_rate_requests_per_minute"])
    last_submission_at: float | None = None
    for file_info in preflight["files"]:
        if not file_info.get("eligible"):
            results.append(preflight_result(file_info))
            continue
        pdf = Path(str(file_info["pdf_path"]))
        if last_submission_at is not None:
            elapsed = time.monotonic() - last_submission_at
            if elapsed < submit_delay:
                time.sleep(submit_delay - elapsed)
        result = convert_pdf_with_mineru(
            pdf,
            output_dir,
            token_env=args.token_env,
            config_file=args.config_file,
            model_version=args.model_version,
            poll_interval=poll_interval,
            poll_timeout=args.poll_timeout,
        )
        last_submission_at = time.monotonic()
        results.append(result)

    manifest = {
        "operation": "mineru_pdf_convert",
        "dry_run": False,
        "backend": "mineru",
        "inputs": {"input_pdf": args.input_pdf, "input_dir": args.input_dir, "pdf_count": len(pdfs)},
        "output_dir": args.output_dir,
        "preflight": preflight,
        "summary": {
            "converted": sum(1 for result in results if result.get("status") == "converted"),
            "skipped": sum(1 for result in results if result.get("status") == "skipped"),
            "blocked": sum(1 for result in results if result.get("status") == "blocked"),
            "failed": sum(1 for result in results if result.get("status") == "failed"),
            "submitted": sum(1 for result in results if result.get("status") == "submitted"),
        },
        "results": results,
    }
    (output_dir / "extraction_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print_manifest(manifest)
    return 0 if manifest["summary"]["failed"] == 0 and manifest["summary"]["blocked"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
