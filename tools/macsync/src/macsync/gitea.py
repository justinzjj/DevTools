from __future__ import annotations

import json
import urllib.request


def parse_repo_names(payload: list[dict]) -> list[str]:
    return [str(item["name"]) for item in payload if "name" in item]


def discover_repo_names(web_url: str, owner: str, token: str | None = None) -> list[str]:
    url = f"{web_url.rstrip('/')}/api/v1/users/{owner}/repos"
    request = urllib.request.Request(url)
    if token:
        request.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return parse_repo_names(payload)
