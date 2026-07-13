"""Generate controlled evidence conditions from a synthetic SAEE scenario.

The generator only removes fields from the scenario's declared claim package.
It never creates evidence values, mutates the input, accesses external systems,
or executes agent/tool code.
"""

from __future__ import annotations

import copy
from typing import Any


CONDITION_IDS = (
    "TRACE_ONLY",
    "TRACE_PLUS_RECEIPT",
    "TRACE_RECEIPT_RELATIONSHIPS",
    "COMPLETE_SAEE_PACKAGE",
)

CONDITION_LABELS = {
    "TRACE_ONLY": "Condition A: Trace Only",
    "TRACE_PLUS_RECEIPT": "Condition B: Trace + Receipt",
    "TRACE_RECEIPT_RELATIONSHIPS": "Condition C: Trace + Receipt + Evidence Relationships",
    "COMPLETE_SAEE_PACKAGE": "Condition D: Complete SAEE Evidence Package",
}

GENERATOR_TRUTH_BOUNDARY = {
    "source_scenario_modified": False,
    "missing_evidence_invented": False,
    "real_agent_executed": False,
    "production_trace_observed": False,
    "external_data_used": False,
    "external_validation_completed": False,
    "production_ready": False,
}


def _project(source: Any, keys: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(source, dict):
        return {}
    return {key: copy.deepcopy(source[key]) for key in keys if key in source}


def _leaf_paths(value: Any, prefix: str = "") -> set[str]:
    if isinstance(value, dict):
        paths: set[str] = set()
        for key, item in value.items():
            paths.update(_leaf_paths(item, f"{prefix}/{key}"))
        return paths
    if isinstance(value, list):
        paths = set()
        for index, item in enumerate(value):
            paths.update(_leaf_paths(item, f"{prefix}/{index}"))
        return paths
    return {prefix or "/"}


def _trace_only(claim_type: str, evidence: dict[str, Any]) -> dict[str, Any]:
    if claim_type == "RESOURCE_AUTHENTICITY":
        return {"resource_receipt": _project(evidence.get("resource_receipt"), ("requested_resource",))}
    if claim_type == "AUTHORIZED_AGENT_ACTION":
        return {"action": copy.deepcopy(evidence.get("action", {})), "policy_decision": {}}
    if claim_type == "HUMAN_OVERSIGHT":
        return {
            "action": copy.deepcopy(evidence.get("action", {})),
            "approval": _project(evidence.get("approval"), ("human_identity",)),
        }
    if claim_type == "EXECUTION_BOUNDARY":
        return {
            "resource_binding": _project(evidence.get("resource_binding"), ("receipt_id",)),
            "execution_effect": _project(evidence.get("execution_effect"), ("effect_id",)),
            "causal_link": {},
        }
    raise ValueError("unsupported evaluation claim type")


def _trace_plus_receipt(claim_type: str, evidence: dict[str, Any]) -> dict[str, Any]:
    if claim_type == "RESOURCE_AUTHENTICITY":
        return {"resource_receipt": copy.deepcopy(evidence.get("resource_receipt", {}))}
    if claim_type == "AUTHORIZED_AGENT_ACTION":
        return {
            "action": copy.deepcopy(evidence.get("action", {})),
            "policy_decision": _project(
                evidence.get("policy_decision"),
                ("decision_id", "decision", "agent_id", "action_id"),
            ),
        }
    if claim_type == "HUMAN_OVERSIGHT":
        return {
            "action": copy.deepcopy(evidence.get("action", {})),
            "approval": _project(
                evidence.get("approval"),
                ("human_identity", "approval_context", "decision"),
            ),
        }
    if claim_type == "EXECUTION_BOUNDARY":
        return {
            "resource_binding": copy.deepcopy(evidence.get("resource_binding", {})),
            "execution_effect": copy.deepcopy(evidence.get("execution_effect", {})),
            "causal_link": {},
        }
    raise ValueError("unsupported evaluation claim type")


def generate_evidence_conditions(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all four deterministic conditions without mutating ``scenario``."""

    source_package = scenario.get("claim_evidence")
    expected_claims = scenario.get("expected_claims")
    if not isinstance(source_package, dict) or not isinstance(expected_claims, list) or len(expected_claims) != 1:
        raise ValueError("closed synthetic scenario with one claim is required")
    claim_type = expected_claims[0]
    if source_package.get("claim_type") != claim_type or not isinstance(source_package.get("evidence"), dict):
        raise ValueError("scenario claim and claim evidence must match")

    source_evidence = source_package["evidence"]
    evidence_by_condition = {
        "TRACE_ONLY": _trace_only(claim_type, source_evidence),
        "TRACE_PLUS_RECEIPT": _trace_plus_receipt(claim_type, source_evidence),
        "TRACE_RECEIPT_RELATIONSHIPS": copy.deepcopy(source_evidence),
        "COMPLETE_SAEE_PACKAGE": copy.deepcopy(source_evidence),
    }
    source_paths = _leaf_paths(source_evidence)
    conditions: list[dict[str, Any]] = []
    for condition_id in CONDITION_IDS:
        generated_evidence = evidence_by_condition[condition_id]
        generated_paths = _leaf_paths(generated_evidence)
        if not generated_paths.issubset(source_paths | {
            "/policy_decision",
            "/approval",
            "/causal_link",
        }):
            raise ValueError("condition generator attempted to invent evidence")
        package = copy.deepcopy(source_package)
        package["evidence"] = generated_evidence
        conditions.append(
            {
                "condition_id": condition_id,
                "condition_label": CONDITION_LABELS[condition_id],
                "claim_type": claim_type,
                "evidence_package": package,
                "removed_evidence_paths": sorted(source_paths - generated_paths),
                "condition_equivalent_to_c_for_current_profile": condition_id == "COMPLETE_SAEE_PACKAGE",
                "truth_boundary": copy.deepcopy(GENERATOR_TRUTH_BOUNDARY),
            }
        )
    return conditions
