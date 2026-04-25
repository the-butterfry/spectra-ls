#!/usr/bin/env python3
"""Description: Compare pinned pywiim version with upstream release for sync governance.
Version: 2026.04.25.2
Last updated: 2026-04-25
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _fetch_json(url: str, timeout: float = 10.0, token: str = "", retries: int = 1) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "spectra-ls-pywiim-sync-check",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=timeout) as resp:  # noqa: S310
                return json.loads(resp.read().decode("utf-8"))
        except URLError as exc:
            last_exc = exc
            if attempt >= retries:
                raise

    if last_exc is not None:
        raise last_exc


def _normalize_requirement_version(version: str) -> str:
    # Strip optional environment markers/extras fragments in simple requirement strings.
    return version.split(";", 1)[0].split(",", 1)[0].strip()


def _extract_pywiim_requirement(requirements: list[str]) -> tuple[str, str]:
    pattern = re.compile(r"^\s*pywiim\s*([=~!<>]{1,2})\s*(.+?)\s*$", re.IGNORECASE)
    for req in requirements:
        match = pattern.match(req)
        if match:
            op = match.group(1).strip()
            ver = _normalize_requirement_version(match.group(2))
            return (op, ver)
    return ("", "")


def _load_manifest_requirement(manifest_path: Path) -> tuple[str, str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    requirements = manifest.get("requirements") or []
    if not isinstance(requirements, list):
        return ("", "")
    return _extract_pywiim_requirement([str(r) for r in requirements])


def _normalize_version(v: str) -> tuple[int, ...]:
    parts = [int(x) for x in re.findall(r"\d+", v)]
    return tuple(parts) if parts else (0,)


def _latest_upstream_version(repo: str, timeout: float, token: str) -> tuple[str, str]:
    release_url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        release = _fetch_json(release_url, timeout=timeout, token=token)
        tag = str(release.get("tag_name") or "").strip()
        return (tag.lstrip("v"), release_url)
    except HTTPError as exc:
        # Fallback for repos that do not publish GitHub releases.
        if exc.code != 404:
            raise

    tags_url = f"https://api.github.com/repos/{repo}/tags?per_page=1"
    tags = _fetch_json(tags_url, timeout=timeout, token=token)
    if isinstance(tags, list) and tags:
        tag = str(tags[0].get("name") or "").strip()
        return (tag.lstrip("v"), tags_url)
    return ("", tags_url)


def _status(pinned: str, upstream: str) -> str:
    if not pinned or not upstream:
        return "unknown"
    p = _normalize_version(pinned)
    u = _normalize_version(upstream)
    if p == u:
        return "up_to_date"
    if p < u:
        return "behind"
    return "ahead"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check pinned pywiim version against upstream.")
    parser.add_argument(
        "--repo",
        default="mjcumming/pywiim",
        help="Upstream GitHub repo in owner/name format (default: mjcumming/pywiim).",
    )
    parser.add_argument(
        "--manifest",
        default="/mnt/homeassistant/custom_components/spectra_ls/manifest.json",
        help="Path to integration manifest.json with pinned requirements.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional path to write JSON report.",
    )
    parser.add_argument(
        "--fail-if-behind",
        action="store_true",
        help="Return non-zero when pinned version is behind upstream.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds for GitHub API calls (default: 10).",
    )
    parser.add_argument(
        "--github-token-env",
        default="GITHUB_TOKEN",
        help="Environment variable name containing a GitHub token (default: GITHUB_TOKEN).",
    )
    parser.add_argument(
        "--allow-nonexact-pin",
        action="store_true",
        help="Allow non-exact pywiim requirements (for example >=) without failing the check.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    token = os.environ.get(args.github_token_env, "").strip()

    try:
        requirement_op, pinned_raw = _load_manifest_requirement(manifest_path)
        pinned = pinned_raw.strip()
        upstream, source_url = _latest_upstream_version(args.repo, timeout=args.timeout, token=token)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        print(f"sync check failed: {exc}", file=sys.stderr)
        return 3

    if not pinned:
        print("pywiim requirement not found in manifest requirements", file=sys.stderr)
        return 5

    strict_pin_ok = requirement_op == "=="
    if not strict_pin_ok and not args.allow_nonexact_pin:
        print(
            f"pywiim requirement must be exact '=='. Found operator '{requirement_op or 'missing'}'",
            file=sys.stderr,
        )
        return 6

    status = _status(pinned, upstream)
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "repo": args.repo,
        "upstream_source": source_url,
        "manifest_path": str(manifest_path),
        "requirement_operator": requirement_op,
        "strict_pin_ok": strict_pin_ok,
        "pinned_version": pinned,
        "upstream_version": upstream,
        "status": status,
    }

    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered + "\n", encoding="utf-8")

    if args.fail_if_behind and status == "behind":
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
