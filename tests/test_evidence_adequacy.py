import unittest
from unittest.mock import patch
from saee_backend.services.evidence_adequacy import (
    evaluate_evidence_adequacy,
    TRUTH_BOUNDARY,
)

def create_envelope(claim_type: str, evidence: dict) -> dict:
    return {
        "saee_evidence_adequacy_input_v0_1": True,
        "schema_version": "0.1.0",
        "claim_type": claim_type,
        "evidence": evidence,
        "truth_boundary": TRUTH_BOUNDARY,
    }

class EvidenceAdequacyTest(unittest.TestCase):
    def test_authorized_agent_action_happy_path(self):
        evidence = {
            "action": {
                "action_id": "action-123",
                "agent_id": "agent-456",
                "requested_scope": "scope-789",
                "timestamp": "2023-01-01T12:00:00Z",
            },
            "policy_decision": {
                "decision_id": "decision-111",
                "decision": "allow",
                "agent_id": "agent-456",
                "action_id": "action-123",
                "authority_scope": "scope-789",
                "valid_from": "2023-01-01T00:00:00Z",
                "valid_until": "2023-01-02T00:00:00Z",
            },
        }
        package = create_envelope("AUTHORIZED_AGENT_ACTION", evidence)
        result = evaluate_evidence_adequacy("AUTHORIZED_AGENT_ACTION", package)
        self.assertEqual(result["result"], "PASS")
        self.assertTrue(result["profile_requirements_satisfied"])
        self.assertFalse(result["reason_codes"])

    def test_human_oversight_happy_path(self):
        evidence = {
            "action": {
                "action_id": "action-123",
                "requested_scope": "scope-789",
                "timestamp": "2023-01-01T12:00:00Z",
            },
            "approval": {
                "human_identity": "human-1",
                "approval_context": {
                    "risk_summary": "low",
                    "evidence_refs": ["ref-1"],
                },
                "approved_scope": "scope-789",
                "approval_timestamp": "2023-01-01T11:00:00Z",
                "action_id": "action-123",
                "decision": "approved",
            },
        }
        package = create_envelope("HUMAN_OVERSIGHT", evidence)
        result = evaluate_evidence_adequacy("HUMAN_OVERSIGHT", package)
        self.assertEqual(result["result"], "PASS")
        self.assertTrue(result["profile_requirements_satisfied"])
        self.assertFalse(result["reason_codes"])

    def test_execution_boundary_happy_path(self):
        evidence = {
            "resource_binding": {
                "receipt_id": "receipt-123",
                "content_digest": "a"*64,
                "resolved_uri": "https://example.com/resource",
            },
            "execution_effect": {
                "effect_id": "effect-456",
                "resource_receipt_ref": "receipt-123",
                "content_digest": "a"*64,
                "resolved_uri": "https://example.com/resource",
                "sandbox_ref": "sandbox-789",
            },
            "causal_link": {
                "relation_type": "resource_to_execution_effect",
                "source_receipt_ref": "receipt-123",
                "target_effect_ref": "effect-456",
                "content_digest": "a"*64,
            },
        }
        package = create_envelope("EXECUTION_BOUNDARY", evidence)
        result = evaluate_evidence_adequacy("EXECUTION_BOUNDARY", package)
        self.assertEqual(result["result"], "PASS")
        self.assertTrue(result["profile_requirements_satisfied"])
        self.assertFalse(result["reason_codes"])

    @patch("saee_backend.services.evidence_adequacy.validate_resource_resolution_receipt")
    def test_resource_authenticity_happy_path(self, mock_validate):
        mock_validate.return_value = {"valid": True}
        evidence = {
            "resource_receipt": {
                "requested_resource": "req",
                "resolved_uri": "uri",
                "publisher_identity": "pub",
                "content_digest": "dig",
                "policy_decision_ref": "pol",
            }
        }
        package = create_envelope("RESOURCE_AUTHENTICITY", evidence)
        result = evaluate_evidence_adequacy("RESOURCE_AUTHENTICITY", package)
        self.assertEqual(result["result"], "PASS")
        self.assertTrue(result["profile_requirements_satisfied"])
        self.assertFalse(result["reason_codes"])

    def test_invalid_truth_boundary(self):
        evidence = {
            "action": {
                "action_id": "action-123",
                "agent_id": "agent-456",
                "requested_scope": "scope-789",
                "timestamp": "2023-01-01T12:00:00Z",
            },
            "policy_decision": {
                "decision_id": "decision-111",
                "decision": "allow",
                "agent_id": "agent-456",
                "action_id": "action-123",
                "authority_scope": "scope-789",
                "valid_from": "2023-01-01T00:00:00Z",
                "valid_until": "2023-01-02T00:00:00Z",
            },
        }
        package = create_envelope("AUTHORIZED_AGENT_ACTION", evidence)
        package["truth_boundary"] = {**TRUTH_BOUNDARY, "event_occurrence_proven": True}
        result = evaluate_evidence_adequacy("AUTHORIZED_AGENT_ACTION", package)
        self.assertEqual(result["result"], "FAIL")
        self.assertIn("EVIDENCE_INPUT_SCHEMA_INVALID", result["reason_codes"])

    def test_unknown_claim_type(self):
        evidence = {}
        package = create_envelope("UNKNOWN_CLAIM", evidence)
        result = evaluate_evidence_adequacy("UNKNOWN_CLAIM", package)
        self.assertEqual(result["result"], "FAIL")
        self.assertIn("EVIDENCE_PROFILE_UNKNOWN", result["reason_codes"])

    def test_missing_requirements(self):
        evidence = {
            "action": {
                "agent_id": "agent-456",
                "requested_scope": "scope-789",
                "timestamp": "2023-01-01T12:00:00Z",
            },
            "policy_decision": {
                "decision_id": "decision-111",
                "decision": "allow",
                "agent_id": "agent-456",
                "action_id": "action-123",
                "authority_scope": "scope-789",
                "valid_from": "2023-01-01T00:00:00Z",
                "valid_until": "2023-01-02T00:00:00Z",
            },
        }
        package = create_envelope("AUTHORIZED_AGENT_ACTION", evidence)
        result = evaluate_evidence_adequacy("AUTHORIZED_AGENT_ACTION", package)
        self.assertEqual(result["result"], "FAIL")
        self.assertIn("/action/action_id", result["missing_requirements"])
        self.assertIn("EVIDENCE_ACTION_ID_MISSING", result["reason_codes"])

    def test_specific_conditions(self):
        # Policy decision != "allow"
        evidence_policy_deny = {
            "action": {
                "action_id": "action-123",
                "agent_id": "agent-456",
                "requested_scope": "scope-789",
                "timestamp": "2023-01-01T12:00:00Z",
            },
            "policy_decision": {
                "decision_id": "decision-111",
                "decision": "deny",
                "agent_id": "agent-456",
                "action_id": "action-123",
                "authority_scope": "scope-789",
                "valid_from": "2023-01-01T00:00:00Z",
                "valid_until": "2023-01-02T00:00:00Z",
            },
        }
        package_deny = create_envelope("AUTHORIZED_AGENT_ACTION", evidence_policy_deny)
        result_deny = evaluate_evidence_adequacy("AUTHORIZED_AGENT_ACTION", package_deny)
        self.assertEqual(result_deny["result"], "FAIL")
        self.assertIn("EVIDENCE_POLICY_DECISION_NOT_ALLOW", result_deny["reason_codes"])

        # Approval decision != "approved"
        evidence_approval_denied = {
            "action": {
                "action_id": "action-123",
                "requested_scope": "scope-789",
                "timestamp": "2023-01-01T12:00:00Z",
            },
            "approval": {
                "human_identity": "human-1",
                "approval_context": {
                    "risk_summary": "low",
                    "evidence_refs": ["ref-1"],
                },
                "approved_scope": "scope-789",
                "approval_timestamp": "2023-01-01T11:00:00Z",
                "action_id": "action-123",
                "decision": "denied",
            },
        }
        package_denied = create_envelope("HUMAN_OVERSIGHT", evidence_approval_denied)
        result_denied = evaluate_evidence_adequacy("HUMAN_OVERSIGHT", package_denied)
        self.assertEqual(result_denied["result"], "FAIL")
        self.assertIn("EVIDENCE_APPROVAL_DECISION_NOT_APPROVED", result_denied["reason_codes"])

if __name__ == "__main__":
    unittest.main()
