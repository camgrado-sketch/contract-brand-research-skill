#!/usr/bin/env python3
"""Build and validate a portable Manus release package from the canonical Skill source.

The generated archive contains exactly one top-level directory named after the Skill.
That directory contains SKILL.md and every bundled resource required at runtime.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "contract-brand-research"
SKILL_DIR = ROOT / "skills" / SKILL_NAME
CODEX_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
REQUIRED_PATHS = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/config.example.yaml",
    "references/dimensions.md",
    "references/evidence-standards.md",
    "references/phase1-interrogation.md",
    "references/phase2-research.md",
    "references/phase3-knowledge-sync.md",
    "references/source-playbook.md",
    "scripts/audit_knowledge_links.py",
    "scripts/extract_official_pdf.sh",
    "templates/evidence-list.md",
    "templates/pr-body.md",
    "templates/research-note.md",
)
EXCLUDED_PARTS = {"__pycache__", ".DS_Store"}
ALLOWED_TOP_LEVEL = {"SKILL.md", "agents", "references", "scripts", "templates"}
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def read_version() -> str:
    """Read the package version from the Codex manifest shared by release metadata."""
    data = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))
    version = data.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(".codex-plugin/plugin.json must contain a non-empty version")
    return version


def source_files() -> list[Path]:
    """Return sorted portable source files and reject unexpected generated artifacts."""
    missing = [relative for relative in REQUIRED_PATHS if not (SKILL_DIR / relative).is_file()]
    if missing:
        raise ValueError(f"missing required packaged resource(s): {', '.join(missing)}")

    files: list[Path] = []
    for path in sorted(SKILL_DIR.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(SKILL_DIR)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if relative.suffix in {".pyc", ".pyo"}:
            continue
        if relative.parts[0] not in ALLOWED_TOP_LEVEL:
            raise ValueError(f"unsupported file at Skill root: {relative.as_posix()}")
        files.append(path)
    return files


def archive_member(relative: Path) -> str:
    """Create a portable POSIX archive name rooted at the Skill directory."""
    return str(PurePosixPath(SKILL_NAME, *relative.parts))


def write_archive(output: Path) -> None:
    """Create a deterministic ZIP-compatible .skill or .zip archive."""
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in source_files():
            relative = source.relative_to(SKILL_DIR)
            info = zipfile.ZipInfo(archive_member(relative), date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def validate_archive(archive_path: Path) -> list[str]:
    """Return deterministic structural failures for a Manus release archive."""
    failures: list[str] = []
    if not archive_path.is_file():
        return [f"archive does not exist: {archive_path}"]

    try:
        with zipfile.ZipFile(archive_path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                failures.append(f"archive contains a corrupt member: {bad_member}")
            names = archive.namelist()
    except zipfile.BadZipFile:
        return [f"archive is not ZIP-compatible: {archive_path}"]

    expected_prefix = f"{SKILL_NAME}/"
    if not names:
        failures.append("archive is empty")
        return failures

    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            failures.append(f"archive contains unsafe path: {name}")
        if not name.startswith(expected_prefix):
            failures.append(f"archive member is outside the Skill root: {name}")
        if len(path.parts) < 2:
            failures.append(f"archive member lacks Skill root directory: {name}")

    members = set(names)
    for relative in REQUIRED_PATHS:
        member = f"{SKILL_NAME}/{relative}"
        if member not in members:
            failures.append(f"archive is missing required member: {member}")

    entry = f"{SKILL_NAME}/SKILL.md"
    if entry not in members:
        failures.append(f"archive does not expose Skill entry point: {entry}")

    forbidden = (".git/", "__pycache__/", ".DS_Store", ".pyc", ".pyo")
    for name in names:
        if any(marker in name for marker in forbidden):
            failures.append(f"archive includes generated or repository-only member: {name}")
    return failures


def default_output(version: str) -> Path:
    return ROOT / "dist" / f"{SKILL_NAME}-manus-v{version}.skill"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Output path; use a .skill extension for Manus release assets")
    parser.add_argument("--check", type=Path, metavar="ARCHIVE", help="Validate an existing release archive without rebuilding")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        failures = validate_archive(args.check)
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}")
            return 1
        print(f"PASS: Manus release archive is valid: {args.check}")
        return 0

    try:
        output = args.output or default_output(read_version())
        write_archive(output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: could not build Manus release archive: {exc}")
        return 1

    failures = validate_archive(output)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: built valid Manus release archive: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
