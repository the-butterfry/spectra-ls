#!/usr/bin/env python3
# Description: Discover WiiM/LinkPlay devices via pywiim and emit normalized JSON for MA target synthesis.
# Version: 2026.04.25.1
# Last updated: 2026-04-25

from __future__ import annotations

import argparse
import asyncio
import json
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
    from pywiim.discovery import discover_devices

    devices = await discover_devices(validate=validate, ssdp_timeout=ssdp_timeout)

    normalized: list[dict[str, str]] = []
    seen_ips: set[str] = set()
    for device in devices:
        row = _device_to_dict(device)
        ip = row.get("ip", "")
        if ip and ip in seen_ips:
            continue
        if ip:
            seen_ips.add(ip)
        normalized.append(row)

    return {
        "count": len(normalized),
        "devices": normalized,
        "validate": bool(validate),
        "ssdp_timeout": int(ssdp_timeout),
        "status": "ok",
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
