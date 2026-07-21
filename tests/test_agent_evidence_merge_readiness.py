"""Tests for the Agent Evidence source freeze and migration crosswalk."""

from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "saee_agent_evidence_merge_readiness_check.py"
SPEC = importlib.util.spec_from_file_location("saee_agent_evidence_merge_readiness_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class AgentEvidenceMergeReadinessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.freeze,
            cls.crosswalk,
            cls.compatibility,
            cls.integration_plan,
            cls.owner_decision,
        ) = CHECK.load_documents(ROOT)

    def test_01_documents_validate(self) -> None:
        self.assertEqual(
            CHECK.validate_documents(
                self.freeze,
                self.crosswalk,
                self.compatibility,
                self.integration_plan,
                self.owner_decision,
            ),
            [],
        )

    def test_02_three_customer_versions_are_exact(self) -> None:
        self.assertEqual(self.crosswalk["target_customer_versions"], CHECK.EXPECTED_VERSIONS)

    def test_03_license_gate_cannot_be_silently_revoked(self) -> None:
        freeze = copy.deepcopy(self.freeze)
        freeze["license"]["migration_grant_recorded"] = False
        errors = CHECK.validate_documents(
            freeze,
            self.crosswalk,
            self.compatibility,
            self.integration_plan,
            self.owner_decision,
        )
        self.assertTrue(any("migration grant" in error for error in errors))

    def test_04_source_copy_claim_is_rejected(self) -> None:
        freeze = copy.deepcopy(self.freeze)
        freeze["source_copy_performed"] = True
        errors = CHECK.validate_documents(
            freeze,
            self.crosswalk,
            self.compatibility,
            self.integration_plan,
            self.owner_decision,
        )
        self.assertTrue(any("source_copy_performed" in error for error in errors))

    def test_05_crosswalk_cannot_become_capability_source(self) -> None:
        crosswalk = copy.deepcopy(self.crosswalk)
        crosswalk["crosswalk_is_capability_source"] = True
        errors = CHECK.validate_documents(
            self.freeze,
            crosswalk,
            self.compatibility,
            self.integration_plan,
            self.owner_decision,
        )
        self.assertTrue(any("capability fact source" in error for error in errors))

    def test_06_invalid_migration_disposition_is_rejected(self) -> None:
        crosswalk = copy.deepcopy(self.crosswalk)
        crosswalk["mappings"][0]["disposition"] = "COPY_REPOSITORY"
        errors = CHECK.validate_documents(
            self.freeze,
            crosswalk,
            self.compatibility,
            self.integration_plan,
            self.owner_decision,
        )
        self.assertTrue(any("invalid disposition" in error for error in errors))

    def test_07_offline_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--offline"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SOURCE_PROVENANCE_FREEZE=PASS_TRACKED_HEAD_ONLY", result.stdout)

    def test_08_direct_schema_compatibility_claim_is_rejected(self) -> None:
        compatibility = copy.deepcopy(self.compatibility)
        compatibility["gate"]["direct_schema_compatibility"] = True
        errors = CHECK.validate_documents(
            self.freeze,
            self.crosswalk,
            compatibility,
            self.integration_plan,
            self.owner_decision,
        )
        self.assertTrue(any("direct_schema_compatibility" in error for error in errors))

    def test_09_merge_completion_cannot_be_claimed(self) -> None:
        plan = copy.deepcopy(self.integration_plan)
        plan["current_truth"]["merge_completed"] = True
        errors = CHECK.validate_documents(
            self.freeze,
            self.crosswalk,
            self.compatibility,
            plan,
            self.owner_decision,
        )
        self.assertTrue(any("merge_completed" in error for error in errors))

    def test_10_all_three_version_contracts_remain_incomplete(self) -> None:
        plan = copy.deepcopy(self.integration_plan)
        plan["version_completion_contracts"][0]["implementation_complete"] = True
        errors = CHECK.validate_documents(
            self.freeze,
            self.crosswalk,
            self.compatibility,
            plan,
            self.owner_decision,
        )
        self.assertTrue(any("implementation_complete" in error for error in errors))

    def test_11_owner_decision_must_preserve_bounded_scope(self) -> None:
        decision = copy.deepcopy(self.owner_decision)
        decision["selected_option"] = "APPROVE_UNBOUNDED_SOURCE_COPY"
        errors = CHECK.validate_documents(
            self.freeze,
            self.crosswalk,
            self.compatibility,
            self.integration_plan,
            decision,
        )
        self.assertTrue(any("selected_option" in error for error in errors))

    def test_12_selected_trait_integration_cannot_be_silently_regressed(self) -> None:
        plan = copy.deepcopy(self.integration_plan)
        plan["current_truth"]["selected_source_traits_integrated"] = False
        errors = CHECK.validate_documents(
            self.freeze,
            self.crosswalk,
            self.compatibility,
            plan,
            self.owner_decision,
        )
        self.assertTrue(any("selected_source_traits_integrated" in error for error in errors))

    def test_13_runtime_still_cannot_be_claimed_integrated(self) -> None:
        plan = copy.deepcopy(self.integration_plan)
        plan["current_truth"]["legacy_runtime_integrated"] = True
        errors = CHECK.validate_documents(
            self.freeze,
            self.crosswalk,
            self.compatibility,
            plan,
            self.owner_decision,
        )
        self.assertTrue(any("legacy_runtime_integrated" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
