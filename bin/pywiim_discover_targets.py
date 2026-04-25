#!/usr/bin/env python3
# Description: Discover WiiM/LinkPlay devices via pywiim and emit normalized JSON for MA target synthesis.
# Version: 2026.04.25.2
# Last updated: 2026-04-25

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from typing import Any


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _device_to_dict(device: Any) -> dict[str, str]:
    """Normalize pywiim DiscoveredDevice-like object into portable dict fields."""
    return {
        "name": _as_str(getattr(device, "name", "")),
        "model": _as_str(getattr(device, "model", "")),
        "firmware": _as_str(getattr(device, "firmware", "")),
        "ip": _as_str(getattr(device, "ip", "")),
        "mac": _as_str(getattr(device, "mac", "")),
        "uuid": _as_str(getattr(device, "uuid", "")),
    }


async def _discover(validate: bool, ssdp_timeout: int) -> dict[str, Any]:
    normalized: list[dict[str, str]] = []

    try:
        from pywiim.discovery import discover_devices

        devices = await discover_devices(validate=validate, ssdp_timeout=ssdp_timeout)
        for device in devices:
            normalized.append(_device_to_dict(device))

        status = "ok"
        source = "pywiim.discovery"
    except Exception:
        discover_bin = os.environ.get("PYWIIM_WIIM_DISCOVER_BIN", "wiim-discover")
        cmd = [discover_bin, "--output", "json", "--ssdp-timeout", str(ssdp_timeout)]
        if not validate:
            cmd.append("--no-validate")

        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        stdout = (proc.stdout or "").strip()

        parsed_list: list[dict[str, Any]] = []
        if stdout:
            start = stdout.find("[")
            end = stdout.rfind("]")
            if start >= 0 and end >= start:
                snippet = stdout[start : end + 1]
                parsed = json.loads(snippet)
                if isinstance(parsed, list):
                    parsed_list = [item for item in parsed if isinstance(item, dict)]

        for item in parsed_list:
            normalized.append(
                {
                    "name": _as_str(item.get("name")),
                    "model": _as_str(item.get("model")),
                    "firmware": _as_str(item.get("firmware")),
                    "ip": _as_str(item.get("ip")),
                    "mac": _as_str(item.get("mac")),
                    "uuid": _as_str(item.get("uuid")),
                }
            )

        status = "ok" if len(normalized) > 0 or proc.returncode == 0 else "error"
        source = "wiim-discover"

    seen_ips: set[str] = set()
    deduped: list[dict[str, str]] = []
    for row in normalized:
        ip = row.get("ip", "")
        if ip and ip in seen_ips:
            continue
        if ip:
            seen_ips.add(ip)
        deduped.append(row)

    return {
        "count": len(deduped),
        "devices": deduped,
        "validate": bool(validate),
        "ssdp_timeout": int(ssdp_timeout),
        "status": status,
        "source": source,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover WiiM/LinkPlay devices via pywiim")
    parser.add_argument("--no-validate", action="store_true", help="Skip pywiim API validation for faster scans")
    parser.add_argument("--ssdp-timeout", type=int, default=5, help="SSDP discovery timeout seconds")
    args = parser.parse_args()

    validate = not bool(args.no_validate)
    ssdp_timeout = max(int(args.ssdp_timeout), 1)

    try:
        payload = asyncio.run(_discover(validate=validate, ssdp_timeout=ssdp_timeout))
        print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
        return 0
    except Exception as err:  # pragma: no cover - runtime safety path
        fallback = {
            "count": 0,
            "devices": [],
            "validate": bool(validate),
            "ssdp_timeout": int(ssdp_timeout),
            "status": "error",
            "error": str(err),
        }
        print(json.dumps(fallback, separators=(",", ":"), ensure_ascii=False))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
