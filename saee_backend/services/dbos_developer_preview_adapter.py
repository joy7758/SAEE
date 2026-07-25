"""Read-only DBOS Developer Preview adapter over existing SAEE evaluators.

This compatibility adapter accepts the bounded synthetic envelope produced by
the DBOS Multi-Agent Trust Demo. It does not create a new public capability or
an alternative evaluator. Reliability observations are delegated to the
existing Reliability Framework and risk/recommendation context is delegated to
``saee.evaluate_agent_run``.

The v0.1 DBOS fixture contains CREATED execution records and PENDING evidence
references, not completed runs or canonical verified evidence. The adapter
therefore fails closed: reliability and stability remain NOT_ASSESSED and the
evolution recommendation is held pending stronger source material.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from saee_backend.services.baidu_agent_readiness_service import evaluate_agent_run
from saee_backend.services.reliability_framework.assessment_adapter import (
    assess_reliability_run,
)


CONTRACT_VERSION = "dba.dbos-saee-developer-preview/v0.1"
ADAPTER_VERSION = "0.1.0"


class DBOSDeveloperPreviewInputError(ValueError):
    """Fail-closed input error with a stable machine-readable code."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _require_mapping(value: Any, pointer: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DBOSDeveloperPreviewInputError("DBOS_PREVIEW_INPUT_INVALID", pointer)
    return value


def _require_list(value: Any, pointer: str) -> list[Any]:
    if not isinstance(value, list):
        raise DBOSDeveloperPreviewInputError("DBOS_PREVIEW_INPUT_INVALID", pointer)
    return value


def _reference_id(value: Any, pointer: str) -> str:
    reference = _require_mapping(value, pointer)
    reference_id = reference.get("reference_id")
    if not isinstance(reference_id, str) or not reference_id:
        raise DBOSDeveloperPreviewInputError("DBOS_PREVIEW_REFERENCE_MISSING", pointer)
    return reference_id


def _validate_envelope(envelope: Mapping[str, Any]) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    if envelope.get("contract_version") != CONTRACT_VERSION:
        raise DBOSDeveloperPreviewInputError(
            "DBOS_PREVIEW_CONTRACT_UNSUPPORTED",
            str(envelope.get("contract_version")),
        )

    execution_history = [
        _require_mapping(item, f"/execution_history/{index}")
        for index, item in enumerate(_require_list(envelope.get("execution_history"), "/execution_history"))
    ]
    evidence_references = [
        _require_mapping(item, f"/evidence_references/{index}")
        for index, item in enumerate(_require_list(envelope.get("evidence_references"), "/evidence_references"))
    ]
    validation_results = [
        _require_mapping(item, f"/validation_results/{index}")
        for index, item in enumerate(_require_list(envelope.get("validation_results"), "/validation_results"))
    ]
    if not execution_history:
        raise DBOSDeveloperPreviewInputError("DBOS_PREVIEW_EXECUTION_HISTORY_EMPTY", "/execution_history")

    execution_ids: set[str] = set()
    for index, execution in enumerate(execution_history):
        execution_id = execution.get("execution_id")
        if not isinstance(execution_id, str) or not execution_id:
            raise DBOSDeveloperPreviewInputError("DBOS_PREVIEW_EXECUTION_ID_MISSING", str(index))
        if execution_id in execution_ids:
            raise DBOSDeveloperPreviewInputError("DBOS_PREVIEW_EXECUTION_ID_DUPLICATE", execution_id)
        execution_ids.add(execution_id)
        _reference_id(execution.get("entity_reference"), f"/execution_history/{index}/entity_reference")

    evidence_execution_ids: set[str] = set()
    for index, evidence in enumerate(evidence_references):
        if evidence.get("integrity_status") != "PENDING":
            raise DBOSDeveloperPreviewInputError(
                "DBOS_PREVIEW_EVIDENCE_STATUS_UNSUPPORTED",
                f"/evidence_references/{index}/integrity_status",
            )
        evidence_execution_ids.add(
            _reference_id(
                evidence.get("execution_reference"),
                f"/evidence_references/{index}/execution_reference",
            )
        )
    if not execution_ids.issubset(evidence_execution_ids):
        raise DBOSDeveloperPreviewInputError(
            "DBOS_PREVIEW_EVIDENCE_REFERENCE_INCOMPLETE",
            ",".join(sorted(execution_ids - evidence_execution_ids)),
        )

    if not validation_results or any(item.get("result") != "PASS" for item in validation_results):
        raise DBOSDeveloperPreviewInputError(
            "DBOS_PREVIEW_STRUCTURAL_VALIDATION_NOT_PASS",
            "/validation_results",
        )

    resource_information = _require_mapping(
        envelope.get("resource_information"),
        "/resource_information",
    )
    for field in (
        "model_call_count",
        "network_call_count",
        "tool_call_count",
        "external_side_effect_count",
    ):
        if resource_information.get(field) != 0:
            raise DBOSDeveloperPreviewInputError(
                "DBOS_PREVIEW_SYNTHETIC_BOUNDARY_VIOLATION",
                f"/resource_information/{field}",
            )

    return execution_history, evidence_references, validation_results


def _reliability_assessments(execution_history: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    assessments: list[dict[str, Any]] = []
    for execution in execution_history:
        execution_id = str(execution["execution_id"])
        entity_id = _reference_id(execution["entity_reference"], f"{execution_id}/entity_reference")
        status = str(execution.get("status", "UNKNOWN"))
        run = {
            "run_id": execution_id,
            "status": "completed" if status == "COMPLETED" else "not_completed",
            "unavailable_reason": f"DBOS execution record status is {status}; no execution result is inferred.",
            "evidence_outcomes": [],
            "observed_risk_signals": [],
            "repeated_tool_calls": 0,
        }
        assessments.append(
            assess_reliability_run(
                run,
                agent_profile=entity_id,
                scenario_id="dbos-multi-agent-trust-demo:v0.1",
                source_ref=f"dbos-envelope#{execution_id}",
            )
        )
    return assessments


def _readiness_context(execution_history: list[Mapping[str, Any]]) -> dict[str, Any]:
    events = [
        {
            "event_id": f"event:dbos-preview-{index:02d}",
            "event_type": "CHECK",
            "summary": (
                f"DBOS execution record {execution.get('execution_id')} has status "
                f"{execution.get('status', 'UNKNOWN')}; no execution result is inferred."
            )[:500],
            "external_effect": False,
            "high_impact": False,
        }
        for index, execution in enumerate(execution_history, start=1)
    ]
    return evaluate_agent_run(
        {
            "request_id": "request:dbos-multi-agent-trust-demo-v0.1",
            "agent_id": "agent:dbos-multi-agent-trust-demo-v0.1",
            "task": "Assess the declared DBOS Developer Preview envelope without executing or authorizing change.",
            "trace": {"events": events},
            "evidence": [],
            "customer_data_included": False,
        }
    )



def _build_reliability_assessment(completed_observations: int, reliability: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "OBSERVED" if completed_observations else "NOT_ASSESSED",
        "completed_execution_observations": completed_observations,
        "role_assessments": reliability,
        "limitation": "CREATED execution records are not completed runs or proof of task correctness.",
    }


def _build_stability_assessment() -> dict[str, Any]:
    return {
        "status": "NOT_ASSESSED",
        "repeated_completed_run_groups": 0,
        "limitation": "Stability requires repeated completed observations for the same governed subject.",
    }


def _build_risk_assessment(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "RISKS_IDENTIFIED" if readiness["risks"] else "NO_RISK_SIGNAL_IDENTIFIED",
        "risk_signals": readiness["risks"],
        "missing_required_evidence": readiness["missing_evidence"],
        "source_operation": readiness["operation"],
        "score": readiness["score"],
        "score_semantics": readiness["score_semantics"],
    }


def _build_evolution_recommendation(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "HOLD",
        "recommended_change": None,
        "recommended_next_step": "collect_completed_execution_and_verified_evidence_before_evolution_review",
        "source_readiness_recommendation": readiness["recommendation"],
        "advisory_only": True,
        "decision_authority": False,
        "execution_authority": False,
    }


def _build_source_material_summary(
    execution_history: list[Mapping[str, Any]],
    evidence_references: list[Mapping[str, Any]],
    validation_results: list[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "execution_record_count": len(execution_history),
        "pending_evidence_reference_count": len(evidence_references),
        "structural_validation_pass_count": len(validation_results),
    }


def _build_truth_boundary() -> dict[str, bool]:
    return {
        "new_public_capability_created": False,
        "dbos_state_modified": False,
        "saee_execution_authority": False,
        "fitness_score_generated": False,
        "stability_established": False,
        "evidence_truth_established": False,
        "automatic_evolution": False,
        "permission_granted": False,
        "customer_validated": False,
        "production_ready": False,
    }


def evaluate_dbos_developer_preview(envelope: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate one bounded DBOS preview envelope without modifying DBOS state."""

    envelope = _require_mapping(envelope, "/")
    execution_history, evidence_references, validation_results = _validate_envelope(envelope)
    reliability = _reliability_assessments(execution_history)
    readiness = _readiness_context(execution_history)
    completed_observations = sum(
        item["dimensions"]["task_execution_reliability"]["status"] == "OBSERVED_PASS"
        for item in reliability
    )
    return {
        "evaluation_version": ADAPTER_VERSION,
        "evaluation_id": "saee:dbos-developer-preview:multi-agent-trust-demo-v0.1",
        "input_contract_version": CONTRACT_VERSION,
        "source_demo_id": envelope.get("source_demo_id"),
        "reliability_assessment": _build_reliability_assessment(completed_observations, reliability),
        "stability_assessment": _build_stability_assessment(),
        "risk_assessment": _build_risk_assessment(readiness),
        "evolution_recommendation": _build_evolution_recommendation(readiness),
        "source_material_summary": _build_source_material_summary(
            execution_history, evidence_references, validation_results
        ),
        "reused_implementations": [
            "saee_backend.services.reliability_framework.assessment_adapter.assess_reliability_run",
            "saee_backend.services.baidu_agent_readiness_service.evaluate_agent_run",
        ],
        "limitations": [
            "DBOS structural Validation is not SAEE evaluation and is not Evidence truth.",
            "No trace authenticity, identity binding, or scientific correctness is established.",
            "The result is recommendation context, not a Decision, Authorization, Permission, or Command.",
        ],
        "truth_boundary": _build_truth_boundary(),
    }
