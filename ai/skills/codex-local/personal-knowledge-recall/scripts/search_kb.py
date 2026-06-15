#!/usr/bin/env python3
"""Search the personal knowledge base and print compact Markdown snippets."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


DEFAULT_KB = Path("/Users/justin/Personal/个人知识库")
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".txt", ".json"}

SCOPES = {
    "all": [
        "30-Agent-Index",
        "10-Knowledge-Cards",
        "20-Source-Cards",
        "40-Mental-Models",
        "50-Projects",
        "06-Ideas",
        "00-Agent-State/current-context.md",
    ],
    "index": ["30-Agent-Index"],
    "cards": ["10-Knowledge-Cards", "40-Mental-Models"],
    "sources": ["20-Source-Cards", "30-Agent-Index/sources.yaml"],
    "projects": ["50-Projects", "20-Source-Cards/project"],
    "ideas": ["06-Ideas"],
}


def resolve_kb(path: str | None) -> Path:
    if path:
        return Path(path).expanduser()
    env_path = os.environ.get("PERSONAL_KNOWLEDGE_BASE")
    if env_path:
        return Path(env_path).expanduser()
    cwd = Path.cwd()
    if (cwd / "AGENT_PROTOCOL.md").exists() and (cwd / "30-Agent-Index").exists():
        return cwd
    return DEFAULT_KB


def build_terms(query: str) -> list[str]:
    terms: list[str] = []
    compact = query.strip().lower()
    if compact:
        terms.append(compact)

    for token in re.findall(r"[A-Za-z0-9_#+./-]+|[\u4e00-\u9fff]{2,}", query.lower()):
        if len(token) >= 2 and token not in terms:
            terms.append(token)
        if re.fullmatch(r"[\u4e00-\u9fff]{5,}", token):
            for size in (2, 3, 4):
                for i in range(0, len(token) - size + 1):
                    piece = token[i : i + size]
                    if piece not in terms:
                        terms.append(piece)
    return terms


def iter_files(kb: Path, scope: str):
    for rel in SCOPES[scope]:
        path = kb / rel
        if path.is_file():
            yield path
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in TEXT_SUFFIXES:
                    yield child


def score_file(path: Path, terms: list[str]) -> tuple[int, list[str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0, []

    lower = text.lower()
    score = 0
    for term in terms:
        count = lower.count(term)
        if count:
            score += count * (4 if len(term) >= 4 else 1)

    if not score:
        return 0, []

    snippets: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        low_line = line.lower()
        if any(term in low_line for term in terms):
            clean = re.sub(r"\s+", " ", line).strip()
            if clean:
                snippets.append(f"L{line_no}: {clean[:220]}")
        if len(snippets) >= 4:
            break

    return score, snippets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Search query or candidate concept.")
    parser.add_argument("--kb", help="Personal knowledge base path.")
    parser.add_argument("--scope", choices=sorted(SCOPES), default="all")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    kb = resolve_kb(args.kb)
    if not (kb / "AGENT_PROTOCOL.md").exists():
        raise SystemExit(f"Knowledge base protocol not found: {kb}")

    terms = build_terms(args.query)
    results = []
    for path in iter_files(kb, args.scope):
        score, snippets = score_file(path, terms)
        if score:
            results.append((score, path, snippets))

    results.sort(key=lambda item: (-item[0], str(item[1])))

    print(f"# Personal knowledge search\n")
    print(f"- KB: `{kb}`")
    print(f"- Scope: `{args.scope}`")
    print(f"- Query: `{args.query}`")
    print(f"- Terms: {', '.join(f'`{t}`' for t in terms[:24])}\n")

    if not results:
        print("No strong matches. Try fewer or more concrete terms, then inspect indexes manually.")
        return 0

    for score, path, snippets in results[: args.limit]:
        rel = path.relative_to(kb)
        print(f"## {rel}  score={score}")
        for snippet in snippets:
            print(f"- {snippet}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
