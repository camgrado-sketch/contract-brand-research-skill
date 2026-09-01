#!/usr/bin/env python3
"""Validate the portable Contract Brand Research Skill repository.

The validator is dependency-free and intentionally checks only deterministic repository
properties. It does not claim that a plugin has been installed into Codex or Claude Code.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "contract-brand-research"
CODEX_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
OPENAI_METADATA = SKILL / "agents" / "openai.yaml"
MANUS_PACKAGE_SCRIPT = ROOT / "scripts" / "package_manus_skill.py"
MANUS_PACKAGE_TEST = ROOT / "scripts" / "tests" / "test_package_manus_skill.py"

REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / "claude.md",
    ROOT / ".env",
    ROOT / "LICENSE",
    ROOT / ".gitignore",
    ROOT / ".github" / "workflows" / "validate.yml",
    ROOT / ".github" / "workflows" / "release-manus-skill.yml",
    ROOT / "docs" / "codex-install-verification.md",
    CODEX_MANIFEST,
    CLAUDE_MANIFEST,
    SKILL / "SKILL.md",
    SKILL / "references" / "config.example.yaml",
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
    SKILL / "scripts" / "audit_dbs_sync.py",
    SKILL / "scripts" / "tests" / "test_audit_knowledge_links.py",
    SKILL / "scripts" / "tests" / "test_audit_dbs_sync.py",
    SKILL / "scripts" / "tests" / "test_validate_repo.py",
    SKILL / "scripts" / "tests" / "fixtures" / "openai_wrong_level.yaml",
    OPENAI_METADATA,
    MANUS_PACKAGE_SCRIPT,
    MANUS_PACKAGE_TEST,
]

FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
FIELD_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9_-]*):\s*(?P<value>.*)$")
LOCAL_RESOURCE_RE = re.compile(r"`((?:references|templates|scripts)/[^`\s]+)`")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
OPENAI_INTERFACE_FIELDS = {"display_name", "short_description", "default_prompt"}


def parse_simple_yaml(text: str) -> dict[str, str]:
    """Parse the flat SKILL.md frontmatter only; not used for nested YAML files."""
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        match = FIELD_RE.match(line)
        if match:
            values[match.group("key")] = match.group("value").strip().strip('"')
    return values


def parse_quoted_string(raw: str, line_number: int, failures: list[str]) -> str | None:
    if not raw.startswith('"') or not raw.endswith('"'):
        failures.append(f"openai.yaml line {line_number} must use a double-quoted string")
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        failures.append(f"openai.yaml line {line_number} contains an invalid quoted string")
        return None
    if not isinstance(value, str) or not value:
        failures.append(f"openai.yaml line {line_number} must contain a non-empty string")
        return None
    return value


def parse_openai_interface(path: Path, failures: list[str]) -> dict[str, str]:
    """Parse the supported OpenAI metadata structure with strict YAML hierarchy checks.

    Expected shape:
        interface:
          display_name: "..."
          short_description: "..."
          default_prompt: "..."
    """
    if not path.is_file():
        return {}

    values: dict[str, str] = {}
    saw_interface = False
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line == "interface:":
            if saw_interface:
                failures.append("openai.yaml contains more than one interface block")
            saw_interface = True
            continue
        if raw_line.startswith(" "):
            if not saw_interface:
                failures.append(f"openai.yaml line {line_number} is nested before interface")
                continue
            if not raw_line.startswith("  ") or raw_line.startswith("   "):
                failures.append(f"openai.yaml line {line_number} must be indented exactly two spaces under interface")
                continue
            match = FIELD_RE.match(raw_line[2:])
            if not match:
                failures.append(f"openai.yaml line {line_number} must be a key/value pair under interface")
                continue
            key = match.group("key")
            if key not in OPENAI_INTERFACE_FIELDS:
                failures.append(f"openai.yaml interface contains unsupported field: {key}")
                continue
            if key in values:
                failures.append(f"openai.yaml interface repeats field: {key}")
                continue
            value = parse_quoted_string(match.group("value").strip(), line_number, failures)
            if value is not None:
                values[key] = value
            continue
        failures.append(f"openai.yaml line {line_number} must be the top-level interface key")

    if not saw_interface:
        failures.append("openai.yaml must contain a top-level interface block")
    missing = OPENAI_INTERFACE_FIELDS - set(values)
    if missing:
        failures.append(f"openai.yaml interface missing fields: {', '.join(sorted(missing))}")
    return values


def validate_skill_frontmatter(failures: list[str]) -> None:
    skill_path = SKILL / "SKILL.md"
    if not skill_path.is_file():
        return

    text = skill_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        failures.append("SKILL.md does not start with YAML frontmatter")
        return

    fields = parse_simple_yaml(match.group("body"))
    allowed = {"name", "description"}
    unexpected = sorted(set(fields) - allowed)
    if unexpected:
        failures.append(f"SKILL.md frontmatter contains unsupported fields: {', '.join(unexpected)}")
    if set(fields) != allowed:
        failures.append("SKILL.md frontmatter must contain exactly name and description")
    if not SKILL_NAME_RE.fullmatch(fields.get("name", "")):
        failures.append("SKILL.md name must be lowercase kebab-case and at most 64 characters")
    description = fields.get("description", "")
    if not 20 <= len(description) <= 1024:
        failures.append("SKILL.md description must contain 20–1024 characters")
    if len(text.splitlines()) > 500:
        failures.append("SKILL.md exceeds 500 lines; move detail into references")

    for resource in LOCAL_RESOURCE_RE.findall(text):
        resource_path = SKILL / resource
        if not resource_path.is_file():
            failures.append(f"SKILL.md references missing local resource: {resource}")


def load_json(path: Path, failures: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}


def validate_manifests(failures: list[str]) -> None:
    codex = load_json(CODEX_MANIFEST, failures) if CODEX_MANIFEST.is_file() else {}
    claude = load_json(CLAUDE_MANIFEST, failures) if CLAUDE_MANIFEST.is_file() else {}

    for label, data in (("Codex", codex), ("Claude", claude)):
        for key in ("name", "version", "description"):
            if not isinstance(data.get(key), str) or not data[key].strip():
                failures.append(f"{label} manifest missing non-empty {key}")
        if data.get("version") and not SEMVER_RE.fullmatch(data["version"]):
            failures.append(f"{label} manifest version is not semantic versioning")

    if codex and claude and codex.get("version") != claude.get("version"):
        failures.append("Codex and Claude manifests must declare the same release version")

    if codex:
        author = codex.get("author")
        interface = codex.get("interface")
        if not isinstance(author, dict) or not isinstance(author.get("name"), str) or not author["name"].strip():
            failures.append("Codex manifest missing author.name")
        if not isinstance(interface, dict):
            failures.append("Codex manifest missing interface object")
        else:
            developer = interface.get("developerName")
            if not isinstance(developer, str) or not developer.strip():
                failures.append("Codex manifest missing interface.developerName")
            elif isinstance(author, dict) and author.get("name") != developer:
                failures.append("Codex manifest author.name and interface.developerName must match")
        skills_path = codex.get("skills")
        if not isinstance(skills_path, str) or not (ROOT / skills_path).is_dir():
            failures.append("Codex manifest skills must point to an existing directory")


def validate_openai_metadata(failures: list[str], metadata_path: Path = OPENAI_METADATA) -> None:
    metadata = parse_openai_interface(metadata_path, failures)
    if not metadata:
        return

    codex = load_json(CODEX_MANIFEST, failures) if CODEX_MANIFEST.is_file() else {}
    interface = codex.get("interface", {}) if isinstance(codex, dict) else {}
    if interface:
        if metadata.get("display_name") != interface.get("displayName"):
            failures.append("openai.yaml interface.display_name must match Codex interface.displayName")
        if metadata.get("short_description") != interface.get("shortDescription"):
            failures.append("openai.yaml interface.short_description must match Codex interface.shortDescription")
    if "$contract-brand-research" not in metadata.get("default_prompt", ""):
        failures.append("openai.yaml interface.default_prompt must include $contract-brand-research")


def validate_manus_release_packaging(failures: list[str]) -> None:
    if not MANUS_PACKAGE_SCRIPT.is_file():
        return
    script = MANUS_PACKAGE_SCRIPT.read_text(encoding="utf-8")
    for marker in ("SKILL.md", "zipfile.ZipFile", "validate_archive", "contract-brand-research"):
        if marker not in script:
            failures.append(f"Manus package builder is missing required marker: {marker}")


def validate_git_hygiene(failures: list[str]) -> None:
    if (ROOT / "config.example.yaml").exists():
        failures.append("root config.example.yaml must be removed; use Skill-packaged references/config.example.yaml")
    try:
        tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    except (OSError, subprocess.CalledProcessError):
        failures.append("could not inspect tracked files with git")
        return

    if "config.yaml" in tracked:
        failures.append("config.yaml is tracked; configuration must remain private")
    for path in tracked:
        if path.endswith(".env") and path != ".env":
            failures.append(f"unexpected environment file tracked: {path}")


def main() -> int:
    failures: list[str] = []
    for path in REQUIRED_FILES:
        if not path.is_file():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")

    validate_skill_frontmatter(failures)
    validate_manifests(failures)
    validate_openai_metadata(failures)
    validate_manus_release_packaging(failures)
    validate_git_hygiene(failures)

    if failures:
        for item in failures:
            print(f"FAIL: {item}")
        return 1

    print("PASS: repository structure, packaged resources, and platform metadata checks succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
