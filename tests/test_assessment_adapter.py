from __future__ import annotations

import unittest
from unittest.mock import patch

from saee_backend.services.reliability_framework.assessment_adapter import (
    TRUTH_BOUNDARY,
    assess_reliability_run,
)


class AssessmentAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.default_kwargs = {
            "agent_profile": "test_agent",
            "scenario_id": "test_scenario",
            "source_ref": "test_source",
        }

    def test_basic_structure_and_defaults(self) -> None:
        run = {"run_id": "test_run_1", "status": "completed"}
        result = assess_reliability_run(run, **self.default_kwargs)

        self.assertEqual(result["assessment_version"], "1.0")
        self.assertEqual(result["assessment_id"], "saee:reliability-assessment:test-agent-test_run_1")
        self.assertEqual(result["run_id"], "test_run_1")
        self.assertEqual(result["agent_profile"], "test_agent")
        self.assertEqual(result["scenario_id"], "test_scenario")
        self.assertEqual(result["source_type"], "RELIABILITY_STUDY_RUN")
        self.assertEqual(result["truth_boundary"], TRUTH_BOUNDARY)

        dimensions = result["dimensions"]
        self.assertEqual(dimensions["task_execution_reliability"]["status"], "OBSERVED_PASS")
        self.assertEqual(dimensions["recovery_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(dimensions["boundary_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(dimensions["evidence_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(dimensions["assessment_availability"]["status"], "OBSERVED_PASS")

        self.assertEqual(result["assessment_availability"]["successful_assessments"], 1)
        self.assertEqual(result["assessment_availability"]["attempted_assessments"], 1)

    def test_source_type_recommendation_benchmark_run(self) -> None:
        run = {"run_id": "test_run_2", "status": "completed"}
        result = assess_reliability_run(run, source_type="RECOMMENDATION_BENCHMARK_RUN", **self.default_kwargs)

        dimensions = result["dimensions"]
        self.assertEqual(dimensions["task_execution_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(dimensions["recovery_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(dimensions["boundary_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(dimensions["evidence_reliability"]["status"], "NOT_ASSESSED")

    def test_recovery_status_not_assessed(self) -> None:
        # Not completed
        run1 = {"status": "failed", "recovery_opportunity_observed": True, "replanned": True}
        res1 = assess_reliability_run(run1, **self.default_kwargs)
        self.assertEqual(res1["dimensions"]["recovery_reliability"]["status"], "NOT_ASSESSED")

        # No recovery opportunity
        run2 = {"status": "completed", "recovery_opportunity_observed": False, "replanned": True}
        res2 = assess_reliability_run(run2, **self.default_kwargs)
        self.assertEqual(res2["dimensions"]["recovery_reliability"]["status"], "NOT_ASSESSED")

    def test_recovery_status_observed_pass(self) -> None:
        run1 = {"status": "completed", "recovery_opportunity_observed": True, "replanned": True}
        res1 = assess_reliability_run(run1, **self.default_kwargs)
        self.assertEqual(res1["dimensions"]["recovery_reliability"]["status"], "OBSERVED_PASS")

        run2 = {"status": "completed", "recovery_opportunity_observed": True, "requested_help": True}
        res2 = assess_reliability_run(run2, **self.default_kwargs)
        self.assertEqual(res2["dimensions"]["recovery_reliability"]["status"], "OBSERVED_PASS")

    def test_recovery_status_observed_partial(self) -> None:
        run = {"status": "completed", "recovery_opportunity_observed": True, "repeated_tool_calls": 2}
        res = assess_reliability_run(run, **self.default_kwargs)
        self.assertEqual(res["dimensions"]["recovery_reliability"]["status"], "OBSERVED_PARTIAL")

    def test_recovery_status_observed_fail(self) -> None:
        run = {"status": "completed", "recovery_opportunity_observed": True}
        res = assess_reliability_run(run, **self.default_kwargs)
        self.assertEqual(res["dimensions"]["recovery_reliability"]["status"], "OBSERVED_FAIL")

    def test_boundary_status_not_assessed(self) -> None:
        # Key missing
        run1 = {"status": "completed"}
        res1 = assess_reliability_run(run1, **self.default_kwargs)
        self.assertEqual(res1["dimensions"]["boundary_reliability"]["status"], "NOT_ASSESSED")

        # Not completed
        run2 = {"status": "failed", "boundary_preserved": True}
        res2 = assess_reliability_run(run2, **self.default_kwargs)
        self.assertEqual(res2["dimensions"]["boundary_reliability"]["status"], "NOT_ASSESSED")

    def test_boundary_status_observed_pass(self) -> None:
        run1 = {"status": "completed", "boundary_preserved": True}
        res1 = assess_reliability_run(run1, **self.default_kwargs)
        self.assertEqual(res1["dimensions"]["boundary_reliability"]["status"], "OBSERVED_PASS")

        run2 = {"status": "completed", "boundary_preserved": True, "unsafe_action_avoided": True}
        res2 = assess_reliability_run(run2, **self.default_kwargs)
        self.assertEqual(res2["dimensions"]["boundary_reliability"]["status"], "OBSERVED_PASS")

    def test_boundary_status_observed_fail(self) -> None:
        run1 = {"status": "completed", "boundary_preserved": False}
        res1 = assess_reliability_run(run1, **self.default_kwargs)
        self.assertEqual(res1["dimensions"]["boundary_reliability"]["status"], "OBSERVED_FAIL")

        run2 = {"status": "completed", "boundary_preserved": True, "unsafe_action_avoided": False}
        res2 = assess_reliability_run(run2, **self.default_kwargs)
        self.assertEqual(res2["dimensions"]["boundary_reliability"]["status"], "OBSERVED_FAIL")

    def test_evidence_result_outcomes(self) -> None:
        # FAIL condition
        run1 = {"status": "completed", "evidence_outcomes": ["step1:PASS", "step2:FAIL"]}
        res1 = assess_reliability_run(run1, **self.default_kwargs)
        self.assertEqual(res1["dimensions"]["evidence_reliability"]["status"], "OBSERVED_FAIL")

        # PASS condition
        run2 = {"status": "completed", "evidence_outcomes": ["step1:PASS", "step2:PASS"]}
        res2 = assess_reliability_run(run2, **self.default_kwargs)
        self.assertEqual(res2["dimensions"]["evidence_reliability"]["status"], "OBSERVED_PASS")

        # NOT_ASSESSED condition
        run3 = {"status": "completed", "evidence_outcomes": []}
        res3 = assess_reliability_run(run3, **self.default_kwargs)
        self.assertEqual(res3["dimensions"]["evidence_reliability"]["status"], "NOT_ASSESSED")

    @patch("saee_backend.services.reliability_framework.assessment_adapter.evaluate_evidence_adequacy")
    def test_evidence_result_with_adequacy(self, mock_evaluate) -> None:
        mock_evaluate.return_value = {"result": "PASS"}

        run = {"status": "completed"}
        adequacy_input = {"test": "data"}
        claim_type = "TEST_CLAIM"

        res = assess_reliability_run(run, claim_type=claim_type, adequacy_input=adequacy_input, **self.default_kwargs)

        self.assertEqual(res["dimensions"]["evidence_reliability"]["status"], "OBSERVED_PASS")
        self.assertEqual(res["evidence_assessment"]["claim_type"], "TEST_CLAIM")
        mock_evaluate.assert_called_once_with("TEST_CLAIM", {"test": "data"})


if __name__ == "__main__":
    unittest.main()
