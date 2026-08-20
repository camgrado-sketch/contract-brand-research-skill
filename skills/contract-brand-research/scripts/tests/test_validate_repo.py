#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts" / "validate_repo.py"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "openai_wrong_level.yaml"

SPEC = importlib.util.spec_from_file_location("validate_repo", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class OpenAIMetadataValidationTests(unittest.TestCase):
    def test_current_openai_metadata_passes_hierarchy_validation(self) -> None:
        failures: list[str] = []
        VALIDATOR.validate_openai_metadata(failures)
        self.assertEqual(failures, [])

    def test_wrong_top_level_fixture_fails_hierarchy_validation(self) -> None:
        failures: list[str] = []
        VALIDATOR.validate_openai_metadata(failures, FIXTURE_PATH)
        self.assertTrue(
            any("must contain a top-level interface block" in message for message in failures),
            failures,
        )


if __name__ == "__main__":
    unittest.main()
