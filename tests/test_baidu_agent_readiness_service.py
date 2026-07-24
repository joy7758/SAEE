import unittest
import copy

from saee_backend.services.baidu_agent_readiness_service import (
    ReadinessInputError,
    evaluate_evidence,
    evaluate_agent_run,
)

class BaiduAgentReadinessServiceTest(unittest.TestCase):
    def setUp(self):
        self.valid_evidence_request = {
            "request_id": "request:evidence-test-1",
            "evidence_bundle": {
                "items": [
                    {
                        "evidence_id": "evidence:test-result-1",
                        "evidence_type": "TEST_RESULT",
                        "present": True,
                        "source_ref": "https://example.com/test-result"
                    },
                    {
                        "evidence_id": "evidence:rollback-plan-1",
                        "evidence_type": "ROLLBACK_PLAN",
                        "present": False,
                        "source_ref": None
                    }
                ]
            },
            "required_evidence_types": ["TEST_RESULT", "ROLLBACK_PLAN"],
            "customer_data_included": False
        }

        self.valid_agent_run_request = {
            "request_id": "request:run-test-1",
            "agent_id": "agent:test-1",
            "task": "Perform automated tests",
            "trace": {
                "events": [
                    {
                        "event_id": "event:plan-1",
                        "event_type": "PLAN",
                        "summary": "Start testing",
                        "external_effect": False,
                        "high_impact": False
                    }
                ]
            },
            "evidence": [
                {
                    "evidence_id": "evidence:test-result-1",
                    "evidence_type": "TEST_RESULT",
                    "present": True,
                    "source_ref": "https://example.com/test-result"
                }
            ],
            "customer_data_included": False
        }

    def test_evaluate_evidence_partial(self):
        response = evaluate_evidence(self.valid_evidence_request)
        self.assertEqual(response["evidence_quality"], "PARTIAL")
        self.assertEqual(response["coverage_score"], 50)
        self.assertEqual(response["missing_evidence"], ["ROLLBACK_PLAN"])

    def test_evaluate_evidence_sufficient(self):
        req = copy.deepcopy(self.valid_evidence_request)
        req["evidence_bundle"]["items"][1]["present"] = True
        req["evidence_bundle"]["items"][1]["source_ref"] = "link"
        response = evaluate_evidence(req)
        self.assertEqual(response["evidence_quality"], "SUFFICIENT")
        self.assertEqual(response["coverage_score"], 100)
        self.assertEqual(response["missing_evidence"], [])

    def test_evaluate_evidence_insufficient(self):
        req = copy.deepcopy(self.valid_evidence_request)
        req["evidence_bundle"]["items"][0]["present"] = False
        req["evidence_bundle"]["items"][0]["source_ref"] = None
        req["evidence_bundle"]["items"][1]["present"] = False
        req["evidence_bundle"]["items"][1]["source_ref"] = None
        response = evaluate_evidence(req)
        self.assertEqual(response["evidence_quality"], "INSUFFICIENT")
        self.assertEqual(response["coverage_score"], 0)

    def test_evaluate_agent_run_continue(self):
        response = evaluate_agent_run(self.valid_agent_run_request)
        self.assertEqual(response["readiness"], "continue")
        self.assertEqual(response["score"], 100)
        self.assertEqual(response["recommendation"], "CONTINUE")

    def test_evaluate_agent_run_high_impact_stop(self):
        req = copy.deepcopy(self.valid_agent_run_request)
        req["trace"]["events"][0]["high_impact"] = True
        response = evaluate_agent_run(req)
        self.assertEqual(response["readiness"], "stop")
        self.assertEqual(response["score"], 25)
        self.assertEqual(response["recommendation"], "STOP")

    def test_evaluate_agent_run_high_impact_replan(self):
        req = copy.deepcopy(self.valid_agent_run_request)
        req["trace"]["events"][0]["high_impact"] = True
        req["evidence"].append({
            "evidence_id": "evidence:rollback-plan-1",
            "evidence_type": "ROLLBACK_PLAN",
            "present": True,
            "source_ref": "link"
        })
        response = evaluate_agent_run(req)
        self.assertEqual(response["readiness"], "replan")
        self.assertEqual(response["score"], 50)
        self.assertEqual(response["recommendation"], "REPLAN")

    def test_evaluate_agent_run_high_impact_conditional(self):
        req = copy.deepcopy(self.valid_agent_run_request)
        req["trace"]["events"][0]["high_impact"] = True
        req["evidence"].extend([
            {
                "evidence_id": "evidence:rollback-plan-1",
                "evidence_type": "ROLLBACK_PLAN",
                "present": True,
                "source_ref": "link"
            },
            {
                "evidence_id": "evidence:permission-boundary-1",
                "evidence_type": "PERMISSION_BOUNDARY",
                "present": True,
                "source_ref": "link"
            }
        ])
        response = evaluate_agent_run(req)
        self.assertEqual(response["readiness"], "conditional")
        self.assertEqual(response["score"], 75)
        self.assertEqual(response["recommendation"], "HUMAN_REVIEW_REQUIRED")

    def test_evaluate_agent_run_high_impact_continue(self):
        req = copy.deepcopy(self.valid_agent_run_request)
        req["trace"]["events"][0]["high_impact"] = True
        req["evidence"].extend([
            {
                "evidence_id": "evidence:rollback-plan-1",
                "evidence_type": "ROLLBACK_PLAN",
                "present": True,
                "source_ref": "link"
            },
            {
                "evidence_id": "evidence:permission-boundary-1",
                "evidence_type": "PERMISSION_BOUNDARY",
                "present": True,
                "source_ref": "link"
            },
            {
                "evidence_id": "evidence:human-approval-1",
                "evidence_type": "HUMAN_APPROVAL",
                "present": True,
                "source_ref": "link"
            }
        ])
        response = evaluate_agent_run(req)
        self.assertEqual(response["readiness"], "continue")
        self.assertEqual(response["score"], 100)
        self.assertEqual(response["recommendation"], "CONTINUE")

    def test_evaluate_agent_run_duplicate_evidence_id(self):
        req = copy.deepcopy(self.valid_agent_run_request)
        req["evidence"].append(req["evidence"][0])
        with self.assertRaisesRegex(ReadinessInputError, "READINESS_EVIDENCE_ID_DUPLICATE"):
            evaluate_agent_run(req)

    def test_evaluate_agent_run_duplicate_evidence_type(self):
        req = copy.deepcopy(self.valid_agent_run_request)
        new_evidence = copy.deepcopy(req["evidence"][0])
        new_evidence["evidence_id"] = "evidence:test-result-2"
        req["evidence"].append(new_evidence)
        with self.assertRaisesRegex(ReadinessInputError, "READINESS_EVIDENCE_TYPE_DUPLICATE"):
            evaluate_agent_run(req)

    def test_evaluate_evidence_schema_validation_error(self):
        req = copy.deepcopy(self.valid_evidence_request)
        req["request_id"] = "invalid-id"
        with self.assertRaisesRegex(ReadinessInputError, "READINESS_EVIDENCE_REQUEST_INVALID"):
            evaluate_evidence(req)

    def test_evaluate_agent_run_schema_validation_error(self):
        req = copy.deepcopy(self.valid_agent_run_request)
        req["agent_id"] = "invalid-id"
        with self.assertRaisesRegex(ReadinessInputError, "READINESS_AGENT_RUN_REQUEST_INVALID"):
            evaluate_agent_run(req)

if __name__ == "__main__":
    unittest.main()
