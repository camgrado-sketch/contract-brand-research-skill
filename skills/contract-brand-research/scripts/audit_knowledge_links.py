#!/usr/bin/env python3
"""Read-only audit for Obsidian-style wiki links and Markdown image paths.

Usage:
    python audit_knowledge_links.py /path/to/vault

Supported references:
- [[Note Name]]
- [[folder/Note Name]]
- [[Note Name|Alias]]
- [[Note Name#Heading]]
- ![[folder/image.png]]
- ![alt](relative/image.png)

The tool reports missing targets and exits with status 1 only when unresolved references
are found. It ignores instructional placeholders such as [[<insert note>]].
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

WIKILINK_RE = re.compile(
    r"(?P<embed>!)?\[\[(?P<target>[^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]"
)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<target>[^)]+)\)")


@dataclass(frozen=True)
class MissingReference:
    kind: str
    source: Path
    target: str


def is_placeholder(value: str) -> bool:
    stripped = value.strip()
    return not stripped or "<" in stripped or ">" in stripped or "示例" in stripped


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def vault_files(vault: Path) -> list[Path]:
    return sorted(path for path in vault.rglob("*") if path.is_file() and ".git" not in path.parts)


def build_indexes(files: list[Path], vault: Path) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
    notes_by_stem: dict[str, list[Path]] = {}
    files_by_name: dict[str, list[Path]] = {}

    for path in files:
        files_by_name.setdefault(path.name.casefold(), []).append(path)
        if path.suffix.casefold() == ".md":
            notes_by_stem.setdefault(path.stem.casefold(), []).append(path)

    return notes_by_stem, files_by_name


def resolve_path_target(target: str, vault: Path, expect_markdown: bool) -> bool:
    candidate = (vault / target).resolve()
    if not is_within(candidate, vault):
        return False
    if candidate.is_file():
        return not expect_markdown or candidate.suffix.casefold() == ".md"
    if expect_markdown and not candidate.suffix:
        return candidate.with_suffix(".md").is_file()
    return False


def resolve_wikilink(
    target: str,
    is_embed: bool,
    vault: Path,
    notes_by_stem: dict[str, list[Path]],
    files_by_name: dict[str, list[Path]],
) -> bool:
    target = target.strip()
    if is_placeholder(target):
        return True

    if "/" in target or "\\" in target:
        normalized_target = target.replace("\\", "/")
        if resolve_path_target(normalized_target, vault, expect_markdown=not is_embed):
            return True
        if is_embed and not Path(normalized_target).suffix:
            return resolve_path_target(normalized_target, vault, expect_markdown=True)
        return False

    path_target = Path(target)
    if is_embed and path_target.suffix:
        return bool(files_by_name.get(path_target.name.casefold()))

    if not is_embed and path_target.suffix.casefold() == ".md":
        return bool(files_by_name.get(path_target.name.casefold()))

    return bool(notes_by_stem.get(target.casefold()))


def resolve_markdown_image(target: str, source: Path, vault: Path) -> bool:
    target = target.strip().split(" ", 1)[0]
    if target.startswith(("http://", "https://", "data:")) or is_placeholder(target):
        return True

    candidate = (source.parent / target).resolve()
    return is_within(candidate, vault) and candidate.is_file()


def audit_vault(vault: Path) -> tuple[int, int, list[MissingReference]]:
    vault = vault.expanduser().resolve()
    files = vault_files(vault)
    notes_by_stem, files_by_name = build_indexes(files, vault)
    missing: list[MissingReference] = []
    checked_wikilinks = 0
    checked_images = 0

    for source in (path for path in files if path.suffix.casefold() == ".md"):
        text = source.read_text(encoding="utf-8", errors="replace")
        for match in WIKILINK_RE.finditer(text):
            target = match.group("target").strip()
            if is_placeholder(target):
                continue
            checked_wikilinks += 1
            is_embed = bool(match.group("embed"))
            if not resolve_wikilink(target, is_embed, vault, notes_by_stem, files_by_name):
                missing.append(MissingReference("EMBED" if is_embed else "WIKILINK", source, target))

        for match in IMAGE_RE.finditer(text):
            target = match.group("target").strip()
            if is_placeholder(target):
                continue
            checked_images += 1
            if not resolve_markdown_image(target, source, vault):
                missing.append(MissingReference("IMAGE", source, target))

    return checked_wikilinks, checked_images, missing


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: audit_knowledge_links.py /path/to/vault", file=sys.stderr)
        return 2

    vault = Path(sys.argv[1]).expanduser().resolve()
    if not vault.is_dir():
        print(f"Error: vault does not exist: {vault}", file=sys.stderr)
        return 2

    checked_wikilinks, checked_images, missing = audit_vault(vault)
    markdown_count = sum(1 for path in vault_files(vault) if path.suffix.casefold() == ".md")

    print(f"Markdown files: {markdown_count}")
    print(f"Wiki links and embeds checked: {checked_wikilinks}")
    print(f"Relative Markdown images checked: {checked_images}")
    print(f"Unresolved references: {len(missing)}")
    for item in missing:
        print(f"{item.kind} | {item.source.relative_to(vault)} | {item.target}")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
