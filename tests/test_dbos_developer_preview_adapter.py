from __future__ import annotations

import copy
import unittest

from saee_backend.services.dbos_developer_preview_adapter import (
    DBOSDeveloperPreviewInputError,
    evaluate_dbos_developer_preview,
)


def ref(reference_id: str) -> dict[str, str]:
    return {"reference_id": reference_id}


def envelope() -> dict:
    executions = []
    evidence = []
    for index, role in enumerate(("research", "analysis", "review"), start=1):
        execution_id = f"execution:{index}:{role}"
        executions.append(
            {
                "execution_id": execution_id,
                "entity_reference": ref(f"entity:{role}"),
                "status": "CREATED",
            }
        )
        evidence.append(
            {
                "evidence_id": f"evidence:{index}:{role}",
                "execution_reference": ref(execution_id),
                "integrity_status": "PENDING",
            }
        )
    return {
        "contract_version": "dba.dbos-saee-developer-preview/v0.1",
        "source_demo_id": "DBOS-MULTI-AGENT-TRUST-DEMO-V0.1",
        "execution_history": executions,
        "evidence_references": evidence,
        "validation_results": [{"result": "PASS"} for _ in range(9)],
        "resource_information": {
            "model_call_count": 0,
            "network_call_count": 0,
            "tool_call_count": 0,
            "external_side_effect_count": 0,
        },
    }


class DBOSDeveloperPreviewAdapterTest(unittest.TestCase):
    def test_fail_closed_evaluation_reuses_existing_saee_context(self) -> None:
        result = evaluate_dbos_developer_preview(envelope())
        self.assertEqual(result["reliability_assessment"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["stability_assessment"]["status"], "NOT_ASSESSED")
        self.assertEqual(result["risk_assessment"]["risk_signals"], ["insufficient_test_evidence"])
        self.assertEqual(result["evolution_recommendation"]["status"], "HOLD")
        self.assertEqual(result["evolution_recommendation"]["source_readiness_recommendation"], "STOP")

    def test_output_does_not_claim_authority_or_evidence_truth(self) -> None:
        result = evaluate_dbos_developer_preview(envelope())
        boundary = result["truth_boundary"]
        self.assertTrue(boundary)
        self.assertFalse(any(boundary.values()))
        self.assertTrue(result["evolution_recommendation"]["advisory_only"])
        self.assertIsNone(result["evolution_recommendation"]["recommended_change"])

    def test_evaluation_is_deterministic(self) -> None:
        self.assertEqual(
            evaluate_dbos_developer_preview(envelope()),
            evaluate_dbos_developer_preview(envelope()),
        )

    def test_rejects_unsupported_contract(self) -> None:
        value = envelope()
        value["contract_version"] = "unknown/v9"
        with self.assertRaisesRegex(DBOSDeveloperPreviewInputError, "DBOS_PREVIEW_CONTRACT_UNSUPPORTED"):
            evaluate_dbos_developer_preview(value)

    def test_rejects_non_pass_structural_validation(self) -> None:
        value = envelope()
        value["validation_results"][0]["result"] = "FAIL"
        with self.assertRaisesRegex(DBOSDeveloperPreviewInputError, "DBOS_PREVIEW_STRUCTURAL_VALIDATION_NOT_PASS"):
            evaluate_dbos_developer_preview(value)

    def test_rejects_unreferenced_execution(self) -> None:
        value = envelope()
        value["evidence_references"].pop()
        with self.assertRaisesRegex(DBOSDeveloperPreviewInputError, "DBOS_PREVIEW_EVIDENCE_REFERENCE_INCOMPLETE"):
            evaluate_dbos_developer_preview(value)

    def test_rejects_external_side_effect_claim(self) -> None:
        value = envelope()
        value["resource_information"]["external_side_effect_count"] = 1
        with self.assertRaisesRegex(DBOSDeveloperPreviewInputError, "DBOS_PREVIEW_SYNTHETIC_BOUNDARY_VIOLATION"):
            evaluate_dbos_developer_preview(value)

    def test_does_not_mutate_input(self) -> None:
        value = envelope()
        before = copy.deepcopy(value)
        evaluate_dbos_developer_preview(value)
        self.assertEqual(value, before)


if __name__ == "__main__":
    unittest.main()
