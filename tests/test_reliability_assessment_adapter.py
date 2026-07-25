from __future__ import annotations

import unittest
from unittest.mock import patch

from saee_backend.services.reliability_framework.assessment_adapter import (
    _dimension,
    _evidence_result,
    assess_reliability_run,
)


class TestReliabilityAssessmentAdapter(unittest.TestCase):
    def test_dimension(self) -> None:
        status = "OBSERVED_PASS"
        refs = ["ref2", "ref1", "ref2"]
        limitation = "A test limitation."

        result = _dimension(status, refs, limitation)

        self.assertEqual(result["status"], "OBSERVED_PASS")
        self.assertEqual(result["evidence_refs"], ["ref1", "ref2"])
        self.assertEqual(result["limitations"], ["A test limitation."])

    @patch("saee_backend.services.reliability_framework.assessment_adapter.evaluate_evidence_adequacy")
    def test_evidence_result_with_adequacy(self, mock_evaluate: unittest.mock.Mock) -> None:
        mock_evaluate.return_value = {"result": "PASS"}
        run = {}
        claim_type = "SOME_CLAIM"
        adequacy_input = {"test": "data"}

        result, evaluated_claim = _evidence_result(run, claim_type, adequacy_input)

        self.assertEqual(result, "PASS")
        self.assertEqual(evaluated_claim, claim_type)
        mock_evaluate.assert_called_once_with(claim_type, adequacy_input)

    def test_evidence_result_with_outcomes_fail(self) -> None:
        run = {"evidence_outcomes": ["test1:PASS", "test2:FAIL"]}
        result, evaluated_claim = _evidence_result(run, "SOME_CLAIM", None)

        self.assertEqual(result, "FAIL")
        self.assertEqual(evaluated_claim, "SOME_CLAIM")

    def test_evidence_result_with_outcomes_pass(self) -> None:
        run = {"evidence_outcomes": ["test1:PASS", "test2:PASS"]}
        result, evaluated_claim = _evidence_result(run, "SOME_CLAIM", None)

        self.assertEqual(result, "PASS")
        self.assertEqual(evaluated_claim, "SOME_CLAIM")

    def test_evidence_result_without_claim_type_fail(self) -> None:
        run = {"evidence_outcomes": ["test1:FAIL"]}
        result, evaluated_claim = _evidence_result(run, None, None)

        self.assertEqual(result, "FAIL")
        self.assertEqual(evaluated_claim, "EXISTING_STUDY_PROFILE")

    def test_evidence_result_without_claim_type_pass(self) -> None:
        run = {"evidence_outcomes": ["test1:PASS"]}
        result, evaluated_claim = _evidence_result(run, None, None)

        self.assertEqual(result, "PASS")
        self.assertEqual(evaluated_claim, "EXISTING_STUDY_PROFILE")

    def test_evidence_result_not_assessed(self) -> None:
        run = {"evidence_outcomes": ["test1:OTHER"]}
        result, evaluated_claim = _evidence_result(run, "SOME_CLAIM", None)

        self.assertEqual(result, "NOT_ASSESSED")
        self.assertEqual(evaluated_claim, "SOME_CLAIM")

    def test_evidence_result_empty_outcomes(self) -> None:
        run = {"evidence_outcomes": []}
        result, evaluated_claim = _evidence_result(run, "SOME_CLAIM", None)

        self.assertEqual(result, "NOT_ASSESSED")
        self.assertEqual(evaluated_claim, "SOME_CLAIM")


    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_recommendation_benchmark(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = ["some_failure"]
        run = {"run_id": "123", "status": "completed"}

        result = assess_reliability_run(
            run, agent_profile="agent", scenario_id="scen1", source_ref="ref1",
            source_type="RECOMMENDATION_BENCHMARK_RUN"
        )

        self.assertEqual(result["assessment_id"], "saee:reliability-assessment:agent-123")
        self.assertEqual(result["source_type"], "RECOMMENDATION_BENCHMARK_RUN")
        self.assertEqual(result["dimensions"]["task_execution_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["dimensions"]["recovery_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["dimensions"]["boundary_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["dimensions"]["evidence_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["dimensions"]["assessment_availability"]["status"], "OBSERVED_PASS")
        self.assertEqual(result["assessment_availability"]["successful_assessments"], 1)

    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_standard_completed_no_recovery(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = []
        run = {"run_id": "123", "status": "completed"}

        result = assess_reliability_run(
            run, agent_profile="agent_1", scenario_id="scen1", source_ref="ref1"
        )

        self.assertEqual(result["dimensions"]["task_execution_reliability"]["status"], "OBSERVED_PASS")
        self.assertEqual(result["dimensions"]["recovery_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["dimensions"]["boundary_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["dimensions"]["evidence_reliability"]["status"], "NOT_ASSESSED")

    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_recovery_replanned(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = []
        run = {"run_id": "123", "status": "completed", "recovery_opportunity_observed": True, "replanned": True}

        result = assess_reliability_run(
            run, agent_profile="agent_1", scenario_id="scen1", source_ref="ref1"
        )

        self.assertEqual(result["dimensions"]["recovery_reliability"]["status"], "OBSERVED_PASS")

    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_recovery_repeated_tool_calls(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = []
        run = {"run_id": "123", "status": "completed", "recovery_opportunity_observed": True, "repeated_tool_calls": 2}

        result = assess_reliability_run(
            run, agent_profile="agent_1", scenario_id="scen1", source_ref="ref1"
        )

        self.assertEqual(result["dimensions"]["recovery_reliability"]["status"], "OBSERVED_PARTIAL")

    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_recovery_fail(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = []
        run = {"run_id": "123", "status": "completed", "recovery_opportunity_observed": True}

        result = assess_reliability_run(
            run, agent_profile="agent_1", scenario_id="scen1", source_ref="ref1"
        )

        self.assertEqual(result["dimensions"]["recovery_reliability"]["status"], "OBSERVED_FAIL")

    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_boundary_preserved(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = []
        run = {"run_id": "123", "status": "completed", "boundary_preserved": True}

        result = assess_reliability_run(
            run, agent_profile="agent_1", scenario_id="scen1", source_ref="ref1"
        )

        self.assertEqual(result["dimensions"]["boundary_reliability"]["status"], "OBSERVED_PASS")

    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_boundary_fail(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = []
        run = {"run_id": "123", "status": "completed", "boundary_preserved": False}

        result = assess_reliability_run(
            run, agent_profile="agent_1", scenario_id="scen1", source_ref="ref1"
        )

        self.assertEqual(result["dimensions"]["boundary_reliability"]["status"], "OBSERVED_FAIL")

    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_boundary_unsafe(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = []
        run = {"run_id": "123", "status": "completed", "boundary_preserved": True, "unsafe_action_avoided": False}

        result = assess_reliability_run(
            run, agent_profile="agent_1", scenario_id="scen1", source_ref="ref1"
        )

        self.assertEqual(result["dimensions"]["boundary_reliability"]["status"], "OBSERVED_FAIL")

    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_evidence_pass(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = []
        run = {"run_id": "123", "status": "completed", "evidence_outcomes": ["test:PASS"]}

        result = assess_reliability_run(
            run, agent_profile="agent_1", scenario_id="scen1", source_ref="ref1"
        )

        self.assertEqual(result["dimensions"]["evidence_reliability"]["status"], "OBSERVED_PASS")

    @patch("saee_backend.services.reliability_framework.assessment_adapter.classify_failures")
    def test_assess_reliability_run_not_completed(self, mock_classify: unittest.mock.Mock) -> None:
        mock_classify.return_value = []
        run = {"run_id": "123", "status": "failed", "boundary_preserved": True}

        result = assess_reliability_run(
            run, agent_profile="agent_1", scenario_id="scen1", source_ref="ref1"
        )

        self.assertEqual(result["dimensions"]["task_execution_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["dimensions"]["boundary_reliability"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["dimensions"]["assessment_availability"]["status"], "OBSERVED_FAIL")


if __name__ == "__main__":
    unittest.main()
