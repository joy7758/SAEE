"""Offline clean-context validation for the SAEE Phase 10.7 discovery surface.

The simulated caller reads only the checked-in public capability materials.
It does not call a model, use prior conversation state, access a network, invoke
a capability, or establish external adoption.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from saee_backend.services.public_capability_surface_validator import validate_public_capability_surface


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_SCHEMA = ROOT / "schemas/saee-external-agent-discovery-validation.schema.v0.1.json"
SURFACE_PATH = ROOT / "agent-interface/public/saee-public-capability-surface.v0.1.json"
INDEX_PATH = ROOT / ".well-known/saee-capability-index.json"
PUBLIC_MATERIALS = {
    ".well-known/saee-capability-index.json",
    "agent-interface/public/saee-public-capability-surface.v0.1.json",
    "docs/public/SAEE_AGENT_QUICK_UNDERSTANDING.md",
    "docs/public/SAEE_AGENT_NATIVE_CAPABILITY_SURFACE.md",
}
ADVERSARIAL_CLAIM_TYPES = {
    "CERTIFICATION": "DISCOVERY_CERTIFICATION_CONFUSION_REJECTED",
    "DEPLOYMENT_APPROVAL": "DISCOVERY_DEPLOYMENT_APPROVAL_CONFUSION_REJECTED",
    "SECURITY_AUTHORITY": "DISCOVERY_SECURITY_AUTHORITY_CONFUSION_REJECTED",
    "UNIVERSAL_USE": "DISCOVERY_UNIVERSAL_USE_CLAIM_REJECTED",
    "SAFETY_GUARANTEE": "DISCOVERY_SAFETY_GUARANTEE_REJECTED",
    "AUTHORIZATION": "DISCOVERY_AUTHORIZATION_CONFUSION_REJECTED",
    "INDUSTRY_STANDARD": "DISCOVERY_INDUSTRY_STANDARD_CLAIM_REJECTED",
    "MARKET_ADOPTION": "DISCOVERY_MARKET_ADOPTION_CLAIM_REJECTED",
    "PUBLIC_SERVICE": "DISCOVERY_PUBLIC_SERVICE_CLAIM_REJECTED",
    "EXTERNAL_EXECUTION": "DISCOVERY_EXTERNAL_EXECUTION_CLAIM_REJECTED",
}


class ExternalAgentDiscoveryValidationError(ValueError):
    """Raised when a scenario violates the clean-context validation contract."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ExternalAgentDiscoveryValidationError(f"DISCOVERY_JSON_OBJECT_REQUIRED:{path.name}")
    return value


def _validate_scenario_contract(scenario: Any) -> dict[str, Any]:
    if not isinstance(scenario, dict):
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_SCENARIO_INVALID")
    schema = _load_json(SCENARIO_SCHEMA)
    errors = sorted(Draft202012Validator(schema).iter_errors(scenario), key=lambda error: list(error.absolute_path))
    if errors:
        path = ".".join(str(part) for part in errors[0].absolute_path) or "root"
        raise ExternalAgentDiscoveryValidationError(f"DISCOVERY_SCENARIO_SCHEMA_INVALID:{path}")
    if set(scenario["available_public_materials"]) != PUBLIC_MATERIALS:
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_PUBLIC_MATERIAL_SET_INVALID")
    for ref in scenario["available_public_materials"]:
        path = (ROOT / ref).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise ExternalAgentDiscoveryValidationError("DISCOVERY_PUBLIC_MATERIAL_OUTSIDE_ROOT") from exc
        if not path.is_file():
            raise ExternalAgentDiscoveryValidationError(f"DISCOVERY_PUBLIC_MATERIAL_MISSING:{ref}")
    context = scenario["agent_context"]
    if any(context.values()):
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_CLEAN_CONTEXT_REQUIRED")
    return scenario


def _public_contract() -> dict[str, Any]:
    surface = _load_json(SURFACE_PATH)
    index = _load_json(INDEX_PATH)
    result = validate_public_capability_surface(surface, index)
    if result["valid"] is not True:
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_PUBLIC_SURFACE_INVALID")
    if {item["id"] for item in surface["capabilities"]} != {"saee.agent-reliability", "saee.evidence-evaluation"}:
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_CAPABILITY_SET_INVALID")
    if not surface["use_cases"] or not surface["avoid_cases"] or not surface["limitations"]:
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_SEMANTIC_BOUNDARY_MISSING")
    return surface


def _derive_selection(task: dict[str, Any], surface: dict[str, Any]) -> tuple[str | None, str, str]:
    capability_ids = {item["id"] for item in surface["capabilities"]}
    use_text = " ".join(surface["use_cases"]).lower()
    avoid_text = " ".join(surface["avoid_cases"]).lower()

    if task["authorization_required"]:
        if "authorization" not in avoid_text:
            raise ExternalAgentDiscoveryValidationError("DISCOVERY_AUTHORIZATION_BOUNDARY_MISSING")
        return None, "SAEE_NOT_APPLICABLE", "DO_NOT_RECOMMEND_SAEE"
    if task["simple_task"]:
        if not any(marker in avoid_text for marker in ("simple", "rewriting", "low-impact")):
            raise ExternalAgentDiscoveryValidationError("DISCOVERY_SIMPLE_TASK_BOUNDARY_MISSING")
        return None, "SAEE_NOT_APPLICABLE", "DO_NOT_RECOMMEND_SAEE"
    if task["evidence_required"]:
        if "saee.evidence-evaluation" not in capability_ids or "evidence" not in use_text:
            raise ExternalAgentDiscoveryValidationError("DISCOVERY_EVIDENCE_CAPABILITY_MISSING")
        return "saee.evidence-evaluation", "EVIDENCE_ADEQUACY_EVALUATION", "CONSIDER_EVIDENCE_EVALUATION"
    if task["task_type"] == "PRODUCTION_DEPLOYMENT" and task["multi_step"] and task["external_impact"]:
        if "saee.agent-reliability" not in capability_ids or "multi-step" not in use_text:
            raise ExternalAgentDiscoveryValidationError("DISCOVERY_RELIABILITY_CAPABILITY_MISSING")
        return "saee.agent-reliability", "AGENT_RELIABILITY_EVALUATION", "CONSIDER_SAEE_WITH_COMPLEMENTS"
    if task["task_type"] == "RELIABILITY_ASSESSMENT":
        if "saee.agent-reliability" not in capability_ids:
            raise ExternalAgentDiscoveryValidationError("DISCOVERY_RELIABILITY_CAPABILITY_MISSING")
        return "saee.agent-reliability", "AGENT_RELIABILITY_EVALUATION", "CONSIDER_SAEE"
    return None, "SAEE_NOT_APPLICABLE", "DO_NOT_RECOMMEND_SAEE"


def evaluate_discovery_scenario(scenario: Any) -> dict[str, Any]:
    """Evaluate one clean-context scenario using public metadata only."""

    value = _validate_scenario_contract(scenario)
    surface = _public_contract()
    capability_id, understanding, action = _derive_selection(value["task"], surface)
    expected_discovery = value["expected_discovery"]
    discovered = bool(surface["capabilities"] and expected_discovery["surface_found"])
    discovery_match = capability_id == expected_discovery["applicable_capability_id"]
    understanding_match = understanding == value["expected_understanding"]
    selection_correct = action == value["expected_action"]

    boundary = value["boundary_expectation"]
    boundary_preserved = all(
        boundary[field] is False
        for field in ("authorization_claim", "certification_claim", "safety_claim", "deployment_approval_claim")
    )
    separate_authority_expected = value["task"]["authorization_required"] or value["task"]["task_type"] == "PRODUCTION_DEPLOYMENT"
    authority_boundary_match = boundary["separate_authority_required"] is separate_authority_expected

    reason_codes: list[str] = []
    if not discovery_match:
        reason_codes.append("DISCOVERY_CAPABILITY_SELECTION_MISMATCH")
    if not understanding_match:
        reason_codes.append("DISCOVERY_PURPOSE_MISUNDERSTOOD")
    if not selection_correct:
        reason_codes.append("DISCOVERY_ACTION_SELECTION_MISMATCH")
    if not boundary_preserved or not authority_boundary_match:
        reason_codes.append("DISCOVERY_BOUNDARY_VIOLATION")
    passed = discovered and not reason_codes
    return {
        "scenario_id": value["scenario_id"],
        "discovered": discovered,
        "understanding": understanding,
        "understanding_correct": understanding_match,
        "selected_action": action,
        "expected_action": value["expected_action"],
        "selection_correct": selection_correct,
        "boundary_preserved": boundary_preserved and authority_boundary_match,
        "result": "PASS" if passed else "FAIL",
        "reason_codes": reason_codes,
    }


def evaluate_adversarial_claim(case: Any) -> dict[str, Any]:
    """Reject one known capability-overclaim without invoking any capability."""

    if not isinstance(case, dict):
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_ADVERSARIAL_CASE_INVALID")
    required = {"case_id", "claim_type", "statement", "expected_action"}
    if set(case) != required or case.get("expected_action") != "REJECT":
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_ADVERSARIAL_CASE_CONTRACT_INVALID")
    claim_type = case.get("claim_type")
    if claim_type not in ADVERSARIAL_CLAIM_TYPES:
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_ADVERSARIAL_CLAIM_UNKNOWN")
    if not isinstance(case.get("statement"), str) or len(case["statement"]) < 12:
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_ADVERSARIAL_STATEMENT_INVALID")
    return {
        "case_id": case["case_id"],
        "rejected": True,
        "reason_code": ADVERSARIAL_CLAIM_TYPES[claim_type],
        "external_usage_claimed": False,
        "adoption_validated": False,
    }


def build_discovery_validation_result(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the deterministic six-scenario Phase 10.7 result."""

    results = sorted((evaluate_discovery_scenario(item) for item in scenarios), key=lambda item: item["scenario_id"])
    if len(results) != 6 or len({item["scenario_id"] for item in results}) != 6:
        raise ExternalAgentDiscoveryValidationError("DISCOVERY_SCENARIO_COVERAGE_INVALID")

    def metric(predicate: Any) -> dict[str, Any]:
        passed = sum(bool(predicate(item)) for item in results)
        return {"passed": passed, "total": len(results), "rate": passed / len(results)}

    return {
        "validation_version": "0.1",
        "validation_scope": "clean_context_synthetic_agent_like_callers_using_public_materials_only",
        "scenario_count": len(results),
        "discovery_success": metric(lambda item: item["discovered"]),
        "understanding_success": metric(lambda item: item["understanding_correct"]),
        "selection_accuracy": metric(lambda item: item["selection_correct"]),
        "boundary_preservation": metric(lambda item: item["boundary_preserved"]),
        "scenario_results": results,
        "limitations": [
            "Only deterministic synthetic agent-like callers are evaluated.",
            "No OpenAI, Claude, Gemini, customer agent, or other external model is connected.",
            "The validation reads checked-in public materials rather than a deployed public service.",
            "Successful selection does not establish external recommendation or agent preference.",
            "No adoption, market fit, marketplace acceptance, or ecosystem support is measured.",
            "No customer data, capability execution, authorization, or external-world action occurs."
        ],
        "truth_boundary": {
            "external_agent_discovery_validation": True,
            "synthetic_agent_like_callers": True,
            "external_agents_connected": False,
            "real_external_agent": False,
            "customer_data": False,
            "market_validation": False,
            "adoption_validated": False,
            "external_agent_preference_validated": False,
            "production_ready": False,
        },
    }
