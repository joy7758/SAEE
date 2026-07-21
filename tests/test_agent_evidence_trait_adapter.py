"""Behavior and truth-boundary tests for the clean-room trait adapter."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.agent_evidence_trait_adapter import (
    EVENT_ID_DUPLICATE,
    EVENT_SEQUENCE_INVALID,
    INPUT_SCHEMA_INVALID,
    NORMALIZED_EVENT_COUNT_MISMATCH,
    PAYLOAD_TOO_LARGE,
    SOURCE_COMPLETENESS_COUNT_MISMATCH,
    adapt_agent_evidence_traits,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "agent-interface/integration/agent-evidence-compatibility/fixtures"
RESULT_SCHEMA = ROOT / "agent-interface/schemas/saee-agent-evidence-trait-adapter-result.v0.1.json"
SMOKE = ROOT / "scripts/saee_agent_evidence_trait_adapter_smoke.py"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AgentEvidenceTraitAdapterTest(unittest.TestCase):
    def test_01_pass_fixture_adapts_without_payload_copy(self) -> None:
        result = adapt_agent_evidence_traits(load("valid-pass.v0.1.json"))
        self.assertEqual(result["adapter_status"], "ADAPTED_WITH_SEMANTIC_LOSS")
        self.assertEqual(len(result["candidate_evidence"]), 2)
        self.assertTrue(all("payload" not in item for item in result["candidate_evidence"]))
        self.assertTrue(all(item["payload_digest"].startswith("sha256:") for item in result["candidate_evidence"]))

    def test_02_warn_is_preserved_and_never_promoted(self) -> None:
        result = adapt_agent_evidence_traits(load("valid-warn.v0.1.json"))
        self.assertEqual(result["integrity_context"]["upstream_verification_result"], "WARN")
        self.assertTrue(result["integrity_context"]["warn_preserved"])
        self.assertFalse(result["evaluation_routing"]["eligible_for_evidence_adequacy"])

    def test_03_source_completeness_mismatch_is_rejected(self) -> None:
        result = adapt_agent_evidence_traits(load("invalid-counts.v0.1.json"))
        self.assertIn(SOURCE_COMPLETENESS_COUNT_MISMATCH, result["reason_codes"])

    def test_04_normalized_count_must_equal_event_count(self) -> None:
        document = load("valid-pass.v0.1.json")
        document["source_completeness"]["normalized_event_count"] = 1
        document["source_completeness"]["source_event_count"] = 1
        result = adapt_agent_evidence_traits(document)
        self.assertIn(NORMALIZED_EVENT_COUNT_MISMATCH, result["reason_codes"])

    def test_05_event_sequence_must_be_contiguous(self) -> None:
        document = load("valid-pass.v0.1.json")
        document["events"][1]["event_index"] = 2
        self.assertIn(EVENT_SEQUENCE_INVALID, adapt_agent_evidence_traits(document)["reason_codes"])

    def test_06_event_ids_must_be_unique(self) -> None:
        document = load("valid-pass.v0.1.json")
        document["events"][1]["event_id"] = document["events"][0]["event_id"]
        self.assertIn(EVENT_ID_DUPLICATE, adapt_agent_evidence_traits(document)["reason_codes"])

    def test_07_large_payload_is_rejected(self) -> None:
        document = load("valid-pass.v0.1.json")
        document["events"][0]["payload"] = {"value": "x" * 5000}
        self.assertIn(PAYLOAD_TOO_LARGE, adapt_agent_evidence_traits(document)["reason_codes"])

    def test_08_open_input_is_rejected(self) -> None:
        document = load("valid-pass.v0.1.json")
        document["unexpected"] = True
        self.assertIn(INPUT_SCHEMA_INVALID, adapt_agent_evidence_traits(document)["reason_codes"])

    def test_09_adapter_is_deterministic_and_non_mutating(self) -> None:
        document = load("valid-pass.v0.1.json")
        original = copy.deepcopy(document)
        first = adapt_agent_evidence_traits(document)
        second = adapt_agent_evidence_traits(document)
        self.assertEqual(first, second)
        self.assertEqual(document, original)

    def test_10_result_matches_strict_schema(self) -> None:
        schema = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for name in ("valid-pass.v0.1.json", "valid-warn.v0.1.json", "invalid-counts.v0.1.json"):
            self.assertEqual(list(validator.iter_errors(adapt_agent_evidence_traits(load(name)))), [])

    def test_11_truth_boundary_remains_false(self) -> None:
        result = adapt_agent_evidence_traits(load("valid-pass.v0.1.json"))
        self.assertTrue(all(value is False for value in result["truth_boundary"].values()))
        self.assertFalse(result["integrity_context"]["cryptographic_verification_reperformed"])
        self.assertFalse(result["integrity_context"]["upstream_result_authorizes_action"])
        self.assertFalse(result["canonicalization"]["jcs_compatible"])

    def test_12_smoke_command_passes(self) -> None:
        run = subprocess.run(
            [sys.executable, str(SMOKE)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("SAEE_AGENT_EVIDENCE_TRAIT_ADAPTER_SMOKE: PASS", run.stdout)

    def test_13_signed_fixture_verifies_with_system_openssl(self) -> None:
        result = adapt_agent_evidence_traits(load("valid-signed.v0.1.json"))
        integrity = result["integrity_context"]
        self.assertEqual(integrity["local_ed25519_signature_check"], "PASS")
        self.assertEqual(integrity["local_ed25519_reason"], "verified_by_system_openssl")
        self.assertTrue(result["truth_boundary"]["local_crypto_subprocess_started"])
        self.assertFalse(result["truth_boundary"]["external_code_executed"])

    def test_14_signature_tamper_is_preserved_as_integrity_failure(self) -> None:
        document = load("valid-signed.v0.1.json")
        document["signature"]["signature_base64"] = (
            "A" + document["signature"]["signature_base64"][1:]
        )
        result = adapt_agent_evidence_traits(document)
        self.assertEqual(result["adapter_status"], "ADAPTED_WITH_SEMANTIC_LOSS")
        self.assertEqual(result["integrity_context"]["local_ed25519_signature_check"], "FAIL")
        self.assertIn("AE_ADAPTER_ED25519_VERIFICATION_FAILED", result["reason_codes"])
        self.assertFalse(result["evaluation_routing"]["eligible_for_evidence_adequacy"])


if __name__ == "__main__":
    unittest.main()
