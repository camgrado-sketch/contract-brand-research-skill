#!/usr/bin/env python3
"""Tests for the deterministic Manus release package builder."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "package_manus_skill.py"
SPEC = importlib.util.spec_from_file_location("package_manus_skill", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load package builder: {MODULE_PATH}")
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)


class ManusReleasePackageTests(unittest.TestCase):
    def test_builder_creates_single_skill_root_with_required_entry_and_resources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "contract-brand-research-manus.skill"
            PACKAGE.write_archive(archive_path)
            self.assertEqual(PACKAGE.validate_archive(archive_path), [])

            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()

            self.assertIn("contract-brand-research/SKILL.md", names)
            self.assertIn("contract-brand-research/agents/openai.yaml", names)
            self.assertIn("contract-brand-research/references/phase1-interrogation.md", names)
            self.assertIn("contract-brand-research/scripts/audit_knowledge_links.py", names)
            self.assertIn("contract-brand-research/templates/research-note.md", names)
            self.assertTrue(all(name.startswith("contract-brand-research/") for name in names))
            self.assertFalse(any(".git/" in name or "__pycache__/" in name for name in names))

    def test_validator_rejects_nested_repository_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "wrong-layout.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("repository-main/skills/contract-brand-research/SKILL.md", "---\nname: test\ndescription: test\n---\n")

            failures = PACKAGE.validate_archive(archive_path)

        self.assertTrue(any("outside the Skill root" in failure for failure in failures))
        self.assertTrue(any("does not expose Skill entry point" in failure for failure in failures))

    def test_validator_rejects_missing_skill_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "missing-entry.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("contract-brand-research/references/phase1-interrogation.md", "placeholder")

            failures = PACKAGE.validate_archive(archive_path)

        self.assertTrue(any("does not expose Skill entry point" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
