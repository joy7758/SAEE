"""Tests for the SAEE Phase 0 governance registry boundary."""

from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "saee_governance_registry_check.py"
SPEC = importlib.util.spec_from_file_location("saee_governance_registry_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class GovernanceRegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.documents, cls.schemas = CHECK.load_documents(ROOT)

    def test_01_registry_loads(self) -> None:
        self.assertEqual(set(self.documents), set(CHECK.REGISTRY_FILES))
        self.assertEqual(len(self.documents["assets"]["assets"]), 12)

    def test_02_registry_schemas_pass(self) -> None:
        self.assertEqual(
            CHECK.validate_schema_documents(self.documents, self.schemas), []
        )

    def test_03_saee_canonical_source_exists(self) -> None:
        canonical = [
            item
            for item in self.documents["repositories"]["repositories"]
            if item["canonicality"] == "canonical"
        ]
        self.assertEqual(len(canonical), 1)
        self.assertEqual(canonical[0]["name"], "saee")
        self.assertIsNone(canonical[0]["remote"])
        self.assertEqual(
            self.documents["capabilities"]["canonical_capability_source"],
            "capability-package/manifest.json#canonical_inventory",
        )

    def test_04_agent_evidence_boundary_is_independent_at_runtime(self) -> None:
        product = next(
            item
            for item in self.documents["products"]["products"]
            if item["id"] == "agent-evidence-receipt"
        )
        self.assertEqual(product["relationship"], "saee_subproject")
        self.assertNotEqual(product["runtime_owner"], "SAEE")
        self.assertFalse(product["source_code_migrated"])
        self.assertFalse(product["runtime_integrated"])

    def test_05_mcp_canonical_namespaces_do_not_conflict(self) -> None:
        canonical = [
            item for item in self.documents["mcp"]["entries"] if item["canonical"]
        ]
        scopes = {(item["owner"], item["namespace"]) for item in canonical}
        self.assertEqual(len(scopes), len(canonical))
        saee = [item for item in canonical if item["owner"] == "SAEE"]
        self.assertEqual(len(saee), 1)
        self.assertEqual(saee[0]["namespace"], "saee.*")

    def test_06_forbidden_production_state_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.documents)
        mutated["products"]["products"][0]["production_ready"] = True
        errors = CHECK.validate_documents(mutated, self.schemas)
        self.assertTrue(any("production_ready" in error for error in errors))

    def test_07_otlp_implementation_promotion_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.documents)
        entry = next(
            item
            for item in mutated["capabilities"]["capabilities"]
            if item["capability"] == "saee.otel_sdk_or_otlp_ingestion"
        )
        entry["status"] = "implemented"
        errors = CHECK.validate_documents(mutated, self.schemas)
        self.assertTrue(any("otel_sdk_or_otlp_ingestion" in error for error in errors))

    def test_08_validator_command_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SAEE_GOVERNANCE_REGISTRY_CHECK: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
