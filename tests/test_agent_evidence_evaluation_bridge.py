"""Tests for the bounded Agent Evidence to SAEE Evaluation bridge."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.agent_evidence_evaluation_bridge import (
    ADEQUACY_NOT_SATISFIED,
    BINDING_DIGEST_MISMATCH,
    BINDING_EVENT_UNKNOWN,
    DECLARED_BINDING_REQUIRES_REVIEW,
    ED25519_NOT_VERIFIED,
    INPUT_SCHEMA_INVALID,
    SOURCE_AUTHENTICITY_UNVERIFIED,
    UPSTREAM_NOT_PASS,
    route_agent_evidence_to_evaluation,
)
from saee_backend.services.agent_evidence_trait_adapter import (
    adapt_agent_evidence_traits,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "agent-interface/integration/agent-evidence-compatibility/fixtures"
ADEQUACY_EXAMPLES = ROOT / "agent-interface/examples/evidence-adequacy"
RESULT_SCHEMA = ROOT / "agent-interface/schemas/saee-agent-evidence-evaluation-bridge-result.v0.1.json"
SMOKE = ROOT / "scripts/saee_agent_evidence_evaluation_bridge_smoke.py"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def bridge_input(source_fixture: str = "valid-signed.v0.1.json") -> dict:
    adapter = adapt_agent_evidence_traits(load_json(FIXTURES / source_fixture))
    return {
        "saee_agent_evidence_evaluation_bridge_input_v0_1": True,
        "schema_version": "0.1.0",
        "adapter_result": adapter,
        "claim_type": "EXECUTION_BOUNDARY",
        "adequacy_package": load_json(ADEQUACY_EXAMPLES / "execution_boundary_pass.json"),
        "binding": {
            "adapter_receipt_digest": adapter["adapter_receipt_digest"],
            "event_ids": [item["event_id"] for item in adapter["candidate_evidence"]],
            "binding_status": "declared_only_not_independently_verified",
        },
        "truth_boundary": {
            "source_event_authenticity_verified": False,
            "binding_independently_verified": False,
            "authorization_verified": False,
            "action_authorized": False,
            "production_ready": False,
        },
    }


class AgentEvidenceEvaluationBridgeTest(unittest.TestCase):
    def test_01_signed_integrity_and_adequacy_pass_stop_at_human_review(self) -> None:
        result = route_agent_evidence_to_evaluation(bridge_input())
        self.assertEqual(result["bridge_status"], "ROUTED")
        self.assertEqual(result["decision"], "HUMAN_REVIEW")
        self.assertEqual(result["adequacy_result"]["result"], "PASS")
        self.assertEqual(
            result["reason_codes"],
            [DECLARED_BINDING_REQUIRES_REVIEW, SOURCE_AUTHENTICITY_UNVERIFIED],
        )
        self.assertTrue(result["saee_evaluator_called"])

    def test_02_unsigned_integrity_cannot_reach_human_review(self) -> None:
        result = route_agent_evidence_to_evaluation(
            bridge_input("valid-pass.v0.1.json")
        )
        self.assertEqual(result["bridge_status"], "ROUTED")
        self.assertEqual(result["decision"], "REPLAN")
        self.assertIn(ED25519_NOT_VERIFIED, result["reason_codes"])

    def test_03_upstream_warn_is_preserved_as_replan(self) -> None:
        result = route_agent_evidence_to_evaluation(
            bridge_input("valid-warn.v0.1.json")
        )
        self.assertEqual(result["decision"], "REPLAN")
        self.assertIn(UPSTREAM_NOT_PASS, result["reason_codes"])
        self.assertEqual(result["integrity_summary"]["upstream_result"], "WARN")

    def test_04_adequacy_failure_is_replan(self) -> None:
        document = bridge_input()
        del document["adequacy_package"]["evidence"]["causal_link"]
        result = route_agent_evidence_to_evaluation(document)
        self.assertEqual(result["bridge_status"], "ROUTED")
        self.assertEqual(result["decision"], "REPLAN")
        self.assertIn(ADEQUACY_NOT_SATISFIED, result["reason_codes"])
        self.assertEqual(result["adequacy_result"]["result"], "FAIL")

    def test_05_binding_digest_mismatch_rejects_before_evaluator(self) -> None:
        document = bridge_input()
        document["binding"]["adapter_receipt_digest"] = "sha256:" + "0" * 64
        result = route_agent_evidence_to_evaluation(document)
        self.assertEqual(result["bridge_status"], "REJECTED")
        self.assertEqual(result["decision"], "REPLAN")
        self.assertIn(BINDING_DIGEST_MISMATCH, result["reason_codes"])
        self.assertFalse(result["saee_evaluator_called"])

    def test_06_unknown_bound_event_rejects_before_evaluator(self) -> None:
        document = bridge_input()
        document["binding"]["event_ids"] = ["event:unknown"]
        result = route_agent_evidence_to_evaluation(document)
        self.assertIn(BINDING_EVENT_UNKNOWN, result["reason_codes"])
        self.assertFalse(result["saee_evaluator_called"])

    def test_07_open_input_is_rejected(self) -> None:
        document = bridge_input()
        document["unexpected"] = True
        result = route_agent_evidence_to_evaluation(document)
        self.assertEqual(result["reason_codes"], [INPUT_SCHEMA_INVALID])
        self.assertFalse(result["saee_evaluator_called"])

    def test_08_result_is_strict_deterministic_and_non_authoritative(self) -> None:
        document = bridge_input()
        original = copy.deepcopy(document)
        first = route_agent_evidence_to_evaluation(document)
        second = route_agent_evidence_to_evaluation(document)
        schema = load_json(RESULT_SCHEMA)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        self.assertEqual(list(validator.iter_errors(first)), [])
        self.assertEqual(first, second)
        self.assertEqual(document, original)
        self.assertTrue(all(value is False for value in first["truth_boundary"].values()))
        self.assertFalse(first["adequacy_result"]["accountability_claim_established"])

    def test_09_smoke_command_passes(self) -> None:
        run = subprocess.run(
            [sys.executable, str(SMOKE)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("SAEE_AGENT_EVIDENCE_EVALUATION_BRIDGE_SMOKE: PASS", run.stdout)


if __name__ == "__main__":
    unittest.main()
