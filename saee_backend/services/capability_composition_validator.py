"""Offline validator for SAEE Phase 16 capability composition strategy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "agent-interface/composition/saee-capability-composition-model.v0.1.json"
MATRIX_PATH = ROOT / "agent-interface/composition/saee-capability-interoperability-matrix.v0.1.json"
SCENARIO_DIR = ROOT / "agent-interface/composition/composition-scenarios"
CONTEXT_SCHEMA_PATH = ROOT / "schemas/saee-agent-decision-context.schema.v0.1.json"
SPEC_DOC = ROOT / "docs/architecture/SAEE_CAPABILITY_COMPOSITION_SPECIFICATION.md"
INTEGRATION_DOC = ROOT / "docs/architecture/SAEE_AGENT_CAPABILITY_ECOSYSTEM_INTEGRATION.md"
EXPECTED_LAYERS = {"SAEE_RELIABILITY", "OBSERVABILITY", "AUTHORIZATION", "POLICY_ENGINE", "EXECUTION_ENGINE"}
FORBIDDEN_CLAIMS = (
    "SAEE replaces IAM.",
    "SAEE replaces policy.",
    "SAEE controls execution.",
    "SAEE is universal authority.",
    "SAEE interoperability is established.",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def load_current_composition() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    return (
        _load(MODEL_PATH),
        _load(MATRIX_PATH),
        [_load(path) for path in sorted(SCENARIO_DIR.glob("*.json"))],
        {"specification": SPEC_DOC.read_text(encoding="utf-8"), "integration": INTEGRATION_DOC.read_text(encoding="utf-8")},
    )


def evaluate_composition_scenario(scenario: dict[str, Any]) -> tuple[str, str]:
    context = scenario["decision_context"]
    if context["authorization_context"]["provider"] == "SAEE":
        return "REJECTED_BOUNDARY_VIOLATION", "SAEE_AUTHORIZATION_CLAIM_REJECTED"
    if context["reliability_context"]["available"] and context["reliability_context"]["provider"] != "SAEE":
        return "REJECTED_BOUNDARY_VIOLATION", "OBSERVABILITY_NOT_RELIABILITY_CONTEXT"
    if "EXECUTION_ENGINE" in scenario["capabilities"] and not all(context[name]["available"] for name in ("observability_context", "reliability_context", "policy_context")):
        return "MISSING_CONTEXT_FLAGGED", "EXECUTION_CONTEXT_INCOMPLETE"
    if context["authorization_context"]["available"] and not context["reliability_context"]["available"]:
        return "ALLOWED_INCOMPLETE_CONTEXT", "RELIABILITY_CONTEXT_NOT_AVAILABLE"
    return "VALID_COMPOSITION", "COMPOSITION_BOUNDARIES_PRESERVED"


def validate_capability_composition(model: Any, matrix: Any, scenarios: Any, documents: Any) -> dict[str, Any]:
    reasons: list[str] = []
    if not all(isinstance(value, dict) for value in (model, matrix, documents)) or not isinstance(scenarios, list):
        return {"valid": False, "reason_codes": ["CAPABILITY_COMPOSITION_INPUT_INVALID"]}
    layers = model.get("capability_layers", [])
    if model.get("model_version") != "0.1" or model.get("capability_id") != "saee.agent-reliability" or model.get("role") != "decision_context_provider" or {item.get("layer_id") for item in layers if isinstance(item, dict)} != EXPECTED_LAYERS:
        reasons.append("CAPABILITY_COMPOSITION_MODEL_INVALID")
    expected_replacements = {"SAEE_NOT_AUTHORIZATION", "SAEE_NOT_POLICY_ENFORCEMENT", "SAEE_NOT_OBSERVABILITY", "SAEE_NOT_EXECUTION"}
    if set(model.get("replacement_boundary", [])) != expected_replacements:
        reasons.append("CAPABILITY_REPLACEMENT_BOUNDARY_INVALID")
    expected_model_truth = {"capability_composition_strategy": True, "external_agents_connected": False, "agent_adoption_validated": False, "marketplace_listed": False, "interoperability_claimed": False, "standards_claimed": False, "production_ready": False}
    if model.get("truth_boundary") != expected_model_truth:
        reasons.append("CAPABILITY_COMPOSITION_TRUTH_BOUNDARY_INVALID")
    if set(matrix.get("capabilities", [])) != {"SAEE", "OBSERVABILITY", "AUTHORIZATION", "POLICY_ENGINE", "EXECUTION_ENGINE"}:
        reasons.append("CAPABILITY_INTEROP_MATRIX_INVALID")
    relations = matrix.get("relations", [])
    required_relations = {"COMPLEMENT", "CONSUMES", "PROVIDES_CONTEXT", "NOT_REPLACEMENT"}
    if not isinstance(relations, list) or not required_relations.issubset({item.get("relation") for item in relations if isinstance(item, dict)}) or matrix.get("invalid_relation", {}).get("relation") != "INVALID":
        reasons.append("CAPABILITY_INTEROP_RELATIONS_INVALID")
    expected_matrix_truth = {"matrix_is_design_only": True, "external_interoperability_tested": False, "external_systems_connected": False, "standards_compliance_claimed": False, "production_ready": False}
    if matrix.get("truth_boundary") != expected_matrix_truth:
        reasons.append("CAPABILITY_INTEROP_BOUNDARY_INVALID")
    schema = _load(CONTEXT_SCHEMA_PATH)
    context_validator = Draft202012Validator(schema)
    required_scenario_keys = {"scenario_id", "description", "capabilities", "decision_context", "expected_result", "reason_codes", "truth_boundary"}
    if len(scenarios) < 5:
        reasons.append("CAPABILITY_COMPOSITION_SCENARIOS_INCOMPLETE")
    for scenario in scenarios:
        if not isinstance(scenario, dict) or set(scenario) != required_scenario_keys or list(context_validator.iter_errors(scenario.get("decision_context"))):
            reasons.append("CAPABILITY_DECISION_CONTEXT_INVALID"); continue
        truth = scenario.get("truth_boundary", {})
        if truth != {"synthetic_composition": True, "external_systems_connected": False, "interoperability_claimed": False, "execution_authorized": False, "production_ready": False}:
            reasons.append("CAPABILITY_COMPOSITION_SCENARIO_BOUNDARY_INVALID"); continue
        actual, code = evaluate_composition_scenario(scenario)
        if scenario.get("expected_result") != actual or code not in scenario.get("reason_codes", []):
            reasons.append("CAPABILITY_COMPOSITION_EXPECTATION_MISMATCH")
    combined_docs = "\n".join(value for value in documents.values() if isinstance(value, str))
    if "SAEE Reliability Context Provider" not in documents.get("specification", "") or "Execution Provider" not in documents.get("specification", ""):
        reasons.append("CAPABILITY_COMPOSITION_DOCUMENTATION_INCOMPLETE")
    required_statement = "SAEE participates as a reliability context provider in agent capability composition. It does not replace authorization, policy, observability, or execution systems."
    if required_statement not in documents.get("integration", ""):
        reasons.append("CAPABILITY_COMPOSITION_LIMITATION_MISSING")
    if any(claim in combined_docs for claim in FORBIDDEN_CLAIMS):
        reasons.append("CAPABILITY_COMPOSITION_FORBIDDEN_CLAIM")
    valid = not reasons
    return {
        "valid": valid,
        "reason_codes": list(dict.fromkeys(reasons)),
        "composition_model": valid,
        "boundary_model": valid,
        "interop_matrix": valid,
        "decision_context_separation": valid,
        "capability_layer_count": len(layers) if isinstance(layers, list) else 0,
        "scenario_count": len(scenarios),
        "capability_composition_strategy": valid,
        "external_agents_connected": False,
        "agent_adoption_validated": False,
        "marketplace_listed": False,
        "interoperability_claimed": False,
        "production_ready": False,
    }


def validate_current_capability_composition() -> dict[str, Any]:
    return validate_capability_composition(*load_current_composition())

