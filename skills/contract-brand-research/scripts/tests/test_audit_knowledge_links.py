#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "audit_knowledge_links.py"
SPEC = importlib.util.spec_from_file_location("audit_knowledge_links", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class WikiLinkAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault = Path(self.temp_dir.name)
        (self.vault / "folder").mkdir()
        (self.vault / "assets").mkdir()
        (self.vault / "folder" / "Note Name.md").write_text("# Note Name\n", encoding="utf-8")
        (self.vault / "Plain Note.md").write_text("# Plain Note\n", encoding="utf-8")
        (self.vault / "assets" / "image.png").write_bytes(b"fixture")
        (self.vault / "assets" / "relative.png").write_bytes(b"fixture")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def audit_note(self, content: str):
        (self.vault / "Source.md").write_text(content, encoding="utf-8")
        return AUDIT.audit_vault(self.vault)

    def test_plain_path_alias_heading_and_embed_resolve(self) -> None:
        checked_wikilinks, checked_images, missing = self.audit_note(
            "\n".join(
                [
                    "[[Plain Note]]",
                    "[[folder/Note Name]]",
                    "[[Note Name|Alias]]",
                    "[[Plain Note#Heading]]",
                    "![[assets/image.png]]",
                    "![[folder/Note Name]]",
                    "![relative](assets/relative.png)",
                ]
            )
        )
        self.assertEqual(checked_wikilinks, 6)
        self.assertEqual(checked_images, 1)
        self.assertEqual(missing, [])

    def test_missing_wikilink_is_reported(self) -> None:
        _, _, missing = self.audit_note("[[Missing Note]]")
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].kind, "WIKILINK")
        self.assertEqual(missing[0].target, "Missing Note")

    def test_missing_wikilink_returns_nonzero_exit_code(self) -> None:
        (self.vault / "Source.md").write_text("[[Missing Note]]", encoding="utf-8")
        with patch.object(sys, "argv", ["audit_knowledge_links.py", str(self.vault)]):
            self.assertEqual(AUDIT.main(), 1)

    def test_missing_embed_is_reported(self) -> None:
        _, _, missing = self.audit_note("![[assets/missing.png]]")
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].kind, "EMBED")

    def test_missing_extensionless_markdown_embed_is_reported(self) -> None:
        _, _, missing = self.audit_note("![[folder/Missing Note]]")
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].kind, "EMBED")
        self.assertEqual(missing[0].target, "folder/Missing Note")

    def test_relative_image_missing_and_existing(self) -> None:
        _, _, missing = self.audit_note("![ok](assets/relative.png)\n![missing](assets/missing.png)")
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].kind, "IMAGE")
        self.assertEqual(missing[0].target, "assets/missing.png")


if __name__ == "__main__":
    unittest.main()
