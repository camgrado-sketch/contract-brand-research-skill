#!/usr/bin/env python3
"""Tests for the Obsidian DBS sync compliance auditor."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "audit_dbs_sync.py"
SPEC = importlib.util.spec_from_file_location("audit_dbs_sync", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class DBSAuditTests(unittest.TestCase):
    def test_valid_dbs_card_passes(self) -> None:
        content = """---
domain: design-business-support
module: foundation
evidence_status: to-validate
research_candidate_route: 应进入
research_candidate_workflow_status: 待人工确认
research_candidate_missing_evidence: []
tags:
  - brand/test
source:
  - "[[Internal Note]]"
  - https://example.com
---
# Valid Card
"""
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            failures: list = []
            AUDIT.audit_file(Path(f.name), failures)
            self.assertEqual(failures, [])

    def test_invalid_candidate_consistency_is_reported(self) -> None:
        # Route is '应进入' but missing evidence is listed
        content = """---
research_candidate_route: 应进入
research_candidate_workflow_status: 待人工确认
research_candidate_missing_evidence: ["品牌对象"]
---
"""
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            failures: list = []
            AUDIT.audit_file(Path(f.name), failures)
            self.assertTrue(any("route '应进入' must have empty missing_evidence" in f.message for f in failures))

    def test_mixed_source_is_reported(self) -> None:
        content = """---
source: "[[Internal Note]] and some text"
---
"""
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            failures: list = []
            AUDIT.audit_file(Path(f.name), failures)
            self.assertTrue(any("WikiLinks in 'source' must be isolated" in f.message for f in failures))

    def test_approved_tag_status_is_forbidden_for_ai(self) -> None:
        content = """---
domain: design-business-support
tag_review_status: approved
---
"""
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            failures: list = []
            AUDIT.audit_file(Path(f.name), failures)
            self.assertTrue(any("must not set tag_review_status to 'approved'" in f.message for f in failures))


if __name__ == "__main__":
    unittest.main()
