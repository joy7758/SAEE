from __future__ import annotations

import copy
import unittest

from saee_backend.services.baidu_agent_readiness_service import (
    ReadinessInputError,
    evaluate_agent_run,
    evaluate_evidence,
)


def evidence_item(
    index: int, evidence_type: str, present: bool = True
) -> dict:
    item = {
        "evidence_id": f"evidence:{index}:{evidence_type.lower()}",
        "evidence_type": evidence_type,
        "present": present,
    }
    if present:
        item["source_ref"] = f"https://example.com/evidence/{index}"
    else:
        item["source_ref"] = None
    return item


def evidence_request() -> dict:
    return {
        "request_id": "request:evidence:1",
        "evidence_bundle": {
            "items": [
                evidence_item(1, "TEST_RESULT"),
                evidence_item(2, "ROLLBACK_PLAN"),
                evidence_item(3, "PERMISSION_BOUNDARY"),
                evidence_item(4, "HUMAN_APPROVAL"),
            ]
        },
        "required_evidence_types": [
            "TEST_RESULT",
            "ROLLBACK_PLAN",
            "PERMISSION_BOUNDARY",
            "HUMAN_APPROVAL",
        ],
        "customer_data_included": False,
    }


def agent_run_request(high_impact: bool = False) -> dict:
    return {
        "request_id": "request:run:1",
        "agent_id": "agent:test-agent:1",
        "task": "Example task",
        "trace": {
            "events": [
                {
                    "event_id": "event:1:plan",
                    "event_type": "PLAN",
                    "summary": "Planning the task",
                    "external_effect": False,
                    "high_impact": False,
                },
                {
                    "event_id": "event:2:tool",
                    "event_type": "TOOL_CALL",
                    "summary": "Executing tool",
                    "external_effect": high_impact,
                    "high_impact": high_impact,
                },
            ]
        },
        "evidence": [
            evidence_item(1, "TEST_RESULT"),
            evidence_item(2, "ROLLBACK_PLAN"),
            evidence_item(3, "PERMISSION_BOUNDARY"),
            evidence_item(4, "HUMAN_APPROVAL"),
        ],
        "customer_data_included": False,
    }


class BaiduAgentReadinessServiceTest(unittest.TestCase):
    def test_evaluate_evidence_sufficient(self) -> None:
        request = evidence_request()
        response = evaluate_evidence(request)
        self.assertEqual(response["evidence_quality"], "SUFFICIENT")
        self.assertEqual(response["coverage_score"], 100)
        self.assertEqual(len(response["missing_evidence"]), 0)

    def test_evaluate_evidence_partial(self) -> None:
        request = evidence_request()
        # Remove two required items, coverage is 50%
        request["evidence_bundle"]["items"][2]["present"] = False
        request["evidence_bundle"]["items"][2]["source_ref"] = None
        request["evidence_bundle"]["items"][3]["present"] = False
        request["evidence_bundle"]["items"][3]["source_ref"] = None

        response = evaluate_evidence(request)
        self.assertEqual(response["evidence_quality"], "PARTIAL")
        self.assertEqual(response["coverage_score"], 50)
        self.assertEqual(len(response["missing_evidence"]), 2)

    def test_evaluate_evidence_insufficient(self) -> None:
        request = evidence_request()
        # Remove three required items, coverage is 25% (< 50%)
        for i in range(1, 4):
            request["evidence_bundle"]["items"][i]["present"] = False
            request["evidence_bundle"]["items"][i]["source_ref"] = None

        response = evaluate_evidence(request)
        self.assertEqual(response["evidence_quality"], "INSUFFICIENT")
        self.assertEqual(response["coverage_score"], 25)
        self.assertEqual(len(response["missing_evidence"]), 3)

    def test_evaluate_agent_run_continue(self) -> None:
        request = agent_run_request(high_impact=True)
        response = evaluate_agent_run(request)
        self.assertEqual(response["readiness"], "continue")
        self.assertEqual(response["recommendation"], "CONTINUE")
        self.assertEqual(response["score"], 100)

    def test_evaluate_agent_run_conditional(self) -> None:
        request = agent_run_request(high_impact=True)
        # Remove one item: score = 75%
        request["evidence"][1]["present"] = False
        request["evidence"][1]["source_ref"] = None

        response = evaluate_agent_run(request)
        self.assertEqual(response["readiness"], "conditional")
        self.assertEqual(response["recommendation"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(response["score"], 75)

    def test_evaluate_agent_run_replan(self) -> None:
        request = agent_run_request(high_impact=True)
        # Remove two items: score = 50%
        request["evidence"][1]["present"] = False
        request["evidence"][1]["source_ref"] = None
        request["evidence"][2]["present"] = False
        request["evidence"][2]["source_ref"] = None

        response = evaluate_agent_run(request)
        self.assertEqual(response["readiness"], "replan")
        self.assertEqual(response["recommendation"], "REPLAN")
        self.assertEqual(response["score"], 50)

    def test_evaluate_agent_run_stop(self) -> None:
        request = agent_run_request(high_impact=True)
        # Remove three items: score = 25%
        request["evidence"][1]["present"] = False
        request["evidence"][1]["source_ref"] = None
        request["evidence"][2]["present"] = False
        request["evidence"][2]["source_ref"] = None
        request["evidence"][3]["present"] = False
        request["evidence"][3]["source_ref"] = None

        response = evaluate_agent_run(request)
        self.assertEqual(response["readiness"], "stop")
        self.assertEqual(response["recommendation"], "STOP")
        self.assertEqual(response["score"], 25)

    def test_evaluate_agent_run_base_requirements(self) -> None:
        # Base requirements means no high_impact/external_effect events.
        # Only TEST_RESULT is required.
        request = agent_run_request(high_impact=False)
        # Remove everything except TEST_RESULT
        request["evidence"][1]["present"] = False
        request["evidence"][1]["source_ref"] = None
        request["evidence"][2]["present"] = False
        request["evidence"][2]["source_ref"] = None
        request["evidence"][3]["present"] = False
        request["evidence"][3]["source_ref"] = None

        response = evaluate_agent_run(request)
        self.assertEqual(response["readiness"], "continue")
        self.assertEqual(response["recommendation"], "CONTINUE")
        self.assertEqual(response["score"], 100)
        self.assertEqual(response["required_evidence"], ["TEST_RESULT"])

    def test_duplicate_evidence_id(self) -> None:
        request = evidence_request()
        # Duplicate evidence id
        request["evidence_bundle"]["items"][1]["evidence_id"] = request["evidence_bundle"]["items"][0]["evidence_id"]
        with self.assertRaisesRegex(ReadinessInputError, "READINESS_EVIDENCE_ID_DUPLICATE"):
            evaluate_evidence(request)

    def test_duplicate_evidence_type(self) -> None:
        request = evidence_request()
        # Duplicate evidence type
        request["evidence_bundle"]["items"][1]["evidence_type"] = request["evidence_bundle"]["items"][0]["evidence_type"]
        with self.assertRaisesRegex(ReadinessInputError, "READINESS_EVIDENCE_TYPE_DUPLICATE"):
            evaluate_evidence(request)

    def test_schema_validation_error(self) -> None:
        request = evidence_request()
        # Missing required key
        del request["customer_data_included"]
        with self.assertRaisesRegex(ReadinessInputError, "READINESS_EVIDENCE_REQUEST_INVALID"):
            evaluate_evidence(request)

    def test_truth_boundary_values(self) -> None:
        request = evidence_request()
        response = evaluate_evidence(request)
        truth_boundary = response["truth_boundary"]
        self.assertTrue(truth_boundary["local_alpha"])
        self.assertFalse(truth_boundary["agent_executed_by_saee"])
        self.assertFalse(truth_boundary["deployment_authorized"])

if __name__ == "__main__":
    unittest.main()
