#!/usr/bin/env python3
"""Auto-bump YAML header versions by date or git commit.

Updates the header at the top of YAML files that looks like:
  # Description: ...
  # Version: ...
  # Last updated: ...
  # Update version/date whenever you change this file.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
from pathlib import Path
from typing import Iterable, Tuple

HEADER_PREFIXES = (
    "# Description:",
    "# Version:",
    "# Last updated:",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _git_short_hash(root: Path) -> str | None:
    try:
        return (
            subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                text=True,
            )
            .strip()
            or None
        )
    except Exception:
        return None


def _compute_version(mode: str, root: Path) -> Tuple[str, str]:
    date_str = _dt.date.today().strftime("%Y.%m.%d")
    if mode == "date":
        return date_str, date_str
    if mode == "git":
        short_hash = _git_short_hash(root)
        version = f"git-{short_hash}" if short_hash else "git-unknown"
        return version, date_str
    raise ValueError(f"Unknown mode: {mode}")


def _iter_yaml_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.yaml"):
        if ".venv" in path.parts:
            continue
        yield path


def _has_header(lines: list[str]) -> bool:
    return (
        len(lines) >= 3
        and lines[0].startswith(HEADER_PREFIXES[0])
        and lines[1].startswith(HEADER_PREFIXES[1])
        and lines[2].startswith(HEADER_PREFIXES[2])
    )


def _update_header(path: Path, version: str, date_str: str) -> bool:
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    if not _has_header(lines):
        return False
    lines[1] = f"# Version: {version}\n"
    lines[2] = f"# Last updated: {date_str}\n"
    new_text = "".join(lines)
    if new_text == text:
        return False
    path.write_text(new_text)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-bump YAML header versions.")
    parser.add_argument(
        "--mode",
        choices=["date", "git"],
        default="date",
        help="Version mode: date (YYYY.MM.DD) or git (git-<hash>).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing files.",
    )
    args = parser.parse_args()

    root = _repo_root()
    version, date_str = _compute_version(args.mode, root)

    changed = 0
    skipped = 0
    for path in _iter_yaml_files(root):
        if args.dry_run:
            if _has_header(path.read_text().splitlines(keepends=True)):
                print(f"DRY RUN: {path.relative_to(root)} -> {version} ({date_str})")
                changed += 1
            else:
                skipped += 1
            continue
        if _update_header(path, version, date_str):
            changed += 1
        else:
            skipped += 1

    print(f"Updated: {changed}, Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
