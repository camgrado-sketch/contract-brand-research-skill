#!/usr/bin/env python3
"""Audit Obsidian-style wiki links and relative Markdown image paths.

Usage:
    python audit_knowledge_links.py /path/to/vault

The script is read-only. It reports unresolved links and exits non-zero only when real
missing targets are found. Template placeholders in angle brackets are ignored.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

WIKILINK_RE = re.compile(r"!?\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def markdown_files(vault: Path) -> list[Path]:
    return sorted(path for path in vault.rglob("*.md") if ".git" not in path.parts)


def build_note_index(files: list[Path]) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for path in files:
        index.setdefault(path.stem.casefold(), []).append(path)
    return index


def is_placeholder(value: str) -> bool:
    stripped = value.strip()
    return not stripped or "<" in stripped or ">" in stripped or "示例" in stripped


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: audit_knowledge_links.py /path/to/vault", file=sys.stderr)
        return 2

    vault = Path(sys.argv[1]).expanduser().resolve()
    if not vault.is_dir():
        print(f"Error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    files = markdown_files(vault)
    index = build_note_index(files)
    missing: list[str] = []
    checked_links = 0
    checked_images = 0

    for source in files:
        text = source.read_text(encoding="utf-8", errors="replace")
        for raw_target in WIKILINK_RE.findall(text):
            target = raw_target.strip()
            if is_placeholder(target):
                continue
            checked_links += 1
            if target.casefold() not in index:
                missing.append(f"WIKILINK | {source.relative_to(vault)} | [[{target}]]")

        for raw_target in IMAGE_RE.findall(text):
            target = raw_target.strip().split(" ")[0]
            if target.startswith(("http://", "https://", "data:")) or is_placeholder(target):
                continue
            checked_images += 1
            candidate = (source.parent / target).resolve()
            if not candidate.exists():
                missing.append(f"IMAGE | {source.relative_to(vault)} | {target}")

    print(f"Markdown files: {len(files)}")
    print(f"Wiki links checked: {checked_links}")
    print(f"Relative images checked: {checked_images}")
    print(f"Unresolved references: {len(missing)}")
    for item in missing:
        print(item)

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
