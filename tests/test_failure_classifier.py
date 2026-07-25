import unittest
from saee_backend.services.reliability_framework.failure_classifier import classify_failures

class FailureClassifierTest(unittest.TestCase):
    def test_contract_failure(self):
        self.assertEqual(classify_failures({"status": "contract_failed"}), ["CONTRACT_FAILURE"])

    def test_model_response_failure(self):
        self.assertEqual(classify_failures({"unavailable_reason": "final_result"}), ["MODEL_RESPONSE_FAILURE"])
        self.assertEqual(classify_failures({"unavailable_reason": "provider_response"}), ["MODEL_RESPONSE_FAILURE"])

    def test_tool_failure(self):
        self.assertEqual(classify_failures({"unavailable_reason": "tool_not_found"}), ["TOOL_FAILURE"])
        self.assertEqual(classify_failures({"unavailable_reason": "invalid arguments"}), ["TOOL_FAILURE"])

    def test_environment_failure(self):
        self.assertEqual(classify_failures({"status": "unavailable"}), ["ENVIRONMENT_FAILURE"])
        self.assertEqual(classify_failures({"unavailable_reason": "network_error"}), ["ENVIRONMENT_FAILURE"])

    def test_boundary_failure(self):
        self.assertEqual(classify_failures({"boundary_preserved": False, "status": "completed"}), ["BOUNDARY_FAILURE"])
        self.assertEqual(classify_failures({"unsupported_tool_called": True}), ["BOUNDARY_FAILURE"])
        self.assertEqual(classify_failures({"observed_risk_signals": ["PRIVILEGE_ESCALATION"]}), ["BOUNDARY_FAILURE"])

    def test_evidence_failure(self):
        self.assertEqual(classify_failures({"evidence_outcomes": ["EVIDENCE_1:FAIL"]}), ["EVIDENCE_FAILURE"])

    def test_multiple_failures_sorted(self):
        self.assertEqual(
            classify_failures({"status": "contract_failed", "unavailable_reason": "network_error"}),
            ["CONTRACT_FAILURE", "ENVIRONMENT_FAILURE"]
        )

    def test_no_failures(self):
        self.assertEqual(classify_failures({"status": "completed"}), [])
        self.assertEqual(classify_failures({}), [])

if __name__ == "__main__":
    unittest.main()
