#!/usr/bin/env python3
"""Validate the portable Contract Brand Research Skill repository.

The validator is deliberately dependency-free. It checks the required shared Skill files,
platform manifests, frontmatter, and that private configuration is not tracked.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "contract-brand-research"

REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / "config.example.yaml",
    ROOT / ".env",
    ROOT / "LICENSE",
    ROOT / ".codex-plugin" / "plugin.json",
    ROOT / ".claude-plugin" / "plugin.json",
    SKILL / "SKILL.md",
    SKILL / "references" / "phase1-interrogation.md",
    SKILL / "references" / "phase2-research.md",
    SKILL / "references" / "phase3-knowledge-sync.md",
    SKILL / "references" / "dimensions.md",
    SKILL / "references" / "evidence-standards.md",
    SKILL / "references" / "source-playbook.md",
    SKILL / "templates" / "research-note.md",
    SKILL / "templates" / "evidence-list.md",
    SKILL / "templates" / "pr-body.md",
    SKILL / "scripts" / "extract_official_pdf.sh",
    SKILL / "scripts" / "audit_knowledge_links.py",
]

FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)


def fail(message: str) -> None:
    print(f"FAIL: {message}")


def main() -> int:
    failures: list[str] = []

    for path in REQUIRED_FILES:
        if not path.is_file():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")

    skill_path = SKILL / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.match(text)
        if not match:
            failures.append("SKILL.md does not start with YAML frontmatter")
        else:
            frontmatter = match.group("body")
            for field in ("name:", "description:"):
                if field not in frontmatter:
                    failures.append(f"SKILL.md frontmatter missing {field}")
            if len(text.splitlines()) > 500:
                failures.append("SKILL.md exceeds 500 lines; move detail into references")

    for manifest_path in (ROOT / ".codex-plugin" / "plugin.json", ROOT / ".claude-plugin" / "plugin.json"):
        if manifest_path.is_file():
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                for key in ("name", "version", "description"):
                    if not data.get(key):
                        failures.append(f"{manifest_path.relative_to(ROOT)} missing {key}")
                if manifest_path.parent.name == ".codex-plugin" and data.get("skills") != "./skills/":
                    failures.append("Codex manifest must point skills to ./skills/")
            except json.JSONDecodeError as exc:
                failures.append(f"invalid JSON in {manifest_path.relative_to(ROOT)}: {exc}")

    try:
        tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
        if "config.yaml" in tracked:
            failures.append("config.yaml is tracked; use config.example.yaml only")
        for path in tracked:
            if path.endswith(".env") and path != ".env":
                failures.append(f"unexpected environment file tracked: {path}")
    except (OSError, subprocess.CalledProcessError):
        failures.append("could not inspect tracked files with git")

    if failures:
        for item in failures:
            fail(item)
        return 1

    print("PASS: repository structure and portability checks succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
