"""Offline validator for SAEE Phase 15.1 marketplace positioning metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CATEGORY_PATH = ROOT / "agent-interface/marketplace/saee-capability-category-position.v0.1.json"
MATRIX_PATH = ROOT / "agent-interface/marketplace/saee-marketplace-position-matrix.v0.1.json"
SCENARIO_DIR = ROOT / "agent-interface/marketplace/positioning-scenarios"
SCHEMA_PATH = ROOT / "schemas/saee-agent-capability-discovery-position.schema.v0.1.json"
ADOPTION_LOOP_PATH = ROOT / "agent-interface/adoption/saee-agent-adoption-loop.v0.1.json"
CATEGORY_DOC = ROOT / "docs/strategy/SAEE_AGENT_CAPABILITY_CATEGORY_MODEL.md"
COMPOSITION_DOC = ROOT / "docs/architecture/SAEE_CAPABILITY_COMPOSITION_MODEL.md"
REVIEW_DOC = ROOT / "docs/strategy/SAEE_AGENT_CAPABILITY_MARKETPLACE_POSITIONING_REVIEW.md"
FORBIDDEN_CLAIMS = (
    "SAEE replaces authorization.",
    "SAEE is marketplace leader.",
    "SAEE is industry standard.",
    "SAEE is trusted by all agents.",
    "SAEE ranked first.",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def load_current_positioning() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, str], dict[str, Any]]:
    return (
        _load(CATEGORY_PATH),
        _load(MATRIX_PATH),
        [_load(path) for path in sorted(SCENARIO_DIR.glob("*.json"))],
        {"category": CATEGORY_DOC.read_text(encoding="utf-8"), "composition": COMPOSITION_DOC.read_text(encoding="utf-8"), "review": REVIEW_DOC.read_text(encoding="utf-8")},
        _load(ADOPTION_LOOP_PATH),
    )


def validate_marketplace_positioning(category: Any, matrix: Any, scenarios: Any, documents: Any, adoption_loop: Any) -> dict[str, Any]:
    reasons: list[str] = []
    if not all(isinstance(value, dict) for value in (category, matrix, documents, adoption_loop)) or not isinstance(scenarios, list):
        return {"valid": False, "reason_codes": ["MARKETPLACE_POSITION_INPUT_INVALID"]}
    if category.get("category_id") != "saee.agent-reliability-capability" or category.get("capability_type") != "agent_reliability_layer" or category.get("composition_role") != "decision_context_provider":
        reasons.append("MARKETPLACE_CAPABILITY_CATEGORY_INVALID")
    required_not_replacements = {"IAM", "ACCESS_CONTROL", "AUTHORIZATION", "EXECUTION", "DEPLOYMENT_SYSTEM", "OBSERVABILITY", "SECURITY_SYSTEM", "POLICY_ENGINE"}
    if not required_not_replacements.issubset(set(category.get("not_replacements", []))):
        reasons.append("MARKETPLACE_REPLACEMENT_BOUNDARY_INVALID")
    category_truth = category.get("truth_boundary", {})
    expected_category_truth = {"marketplace_position_review": True, "marketplace_listed": False, "agent_adoption_validated": False, "external_agents_connected": False, "market_validation": False, "industry_standard_claimed": False, "production_ready": False}
    if category_truth != expected_category_truth:
        reasons.append("MARKETPLACE_CATEGORY_BOUNDARY_INVALID")
    positions = matrix.get("positions", [])
    if matrix.get("matrix_version") != "0.1" or not isinstance(positions, list) or len(positions) < 4:
        reasons.append("MARKETPLACE_POSITION_MATRIX_INVALID")
    saee_rows = [row for row in positions if isinstance(row, dict) and row.get("capability_layer") == "SAEE_AGENT_RELIABILITY"]
    if len(saee_rows) != 1 or saee_rows[0].get("role") != "Reliability Context Provider" or "AUTHORIZATION" not in saee_rows[0].get("not_replacement", []):
        reasons.append("MARKETPLACE_COMPOSITION_MODEL_INVALID")
    expected_matrix_truth = {"positioning_matrix_only": True, "marketplace_created": False, "marketplace_listed": False, "ranking_generated": False, "ecosystem_support_established": False, "agent_adoption_validated": False, "production_ready": False}
    if matrix.get("truth_boundary") != expected_matrix_truth:
        reasons.append("MARKETPLACE_MATRIX_BOUNDARY_INVALID")
    schema = _load(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    if len(scenarios) < 5 or any(list(validator.iter_errors(item)) for item in scenarios):
        reasons.append("MARKETPLACE_DISCOVERY_POSITION_INVALID")
    expected = {
        "AUTHORIZATION_REQUIREMENT": ("USE_AUTHORIZATION_SYSTEM_NOT_SAEE", "AUTHORIZATION_SYSTEM"),
        "OBSERVABILITY_REQUIREMENT": ("USE_OBSERVABILITY_TOOL_NOT_SAEE", "OBSERVABILITY"),
        "SIMPLE_QUERY": ("DO_NOT_USE_SAEE", "NONE"),
        "EVIDENCE_REQUIREMENT": ("CONSIDER_SAEE_FOR_EVIDENCE_CONTEXT", "SAEE"),
        "HIGH_IMPACT_WORKFLOW": ("CONSIDER_SAEE_FOR_RELIABILITY_CONTEXT", "SAEE"),
    }
    for item in scenarios:
        if not isinstance(item, dict):
            continue
        if (item.get("expected_position"), item.get("recommended_capability")) != expected.get(item.get("discovery_trigger")) or item.get("discovery_trigger_mandatory") is not False:
            reasons.append("MARKETPLACE_DISCOVERY_BOUNDARY_INVALID"); break
    if adoption_loop.get("primary_customer_model") != "AUTONOMOUS_AGENT_SYSTEMS" or adoption_loop.get("truth_boundary", {}).get("agent_adoption_validated") is not False:
        reasons.append("MARKETPLACE_ADOPTION_STRATEGY_INVALID")
    combined_docs = "\n".join(value for value in documents.values() if isinstance(value, str))
    if "Agent Reliability Capability（智能体可靠性能力）" not in documents.get("category", ""):
        reasons.append("MARKETPLACE_CATEGORY_DOCUMENTATION_MISSING")
    for marker in ("context != authority", "composition != replacement", "discovery != mandatory use"):
        if marker not in documents.get("composition", ""):
            reasons.append("MARKETPLACE_COMPOSITION_BOUNDARY_MISSING")
    if "SAEE positioning review describes a possible role in future agent capability ecosystems. It does not establish marketplace listing, adoption, or ecosystem acceptance." not in documents.get("review", ""):
        reasons.append("MARKETPLACE_POSITION_LIMITATION_MISSING")
    if any(claim in combined_docs for claim in FORBIDDEN_CLAIMS):
        reasons.append("MARKETPLACE_FORBIDDEN_CLAIM")
    valid = not reasons
    return {
        "valid": valid,
        "reason_codes": list(dict.fromkeys(reasons)),
        "category_defined": valid,
        "composition_defined": valid,
        "replacement_boundary": valid,
        "discovery_boundary": valid,
        "scenario_count": len(scenarios),
        "category_count": 1 if category.get("category_id") else 0,
        "marketplace_position_review": valid,
        "marketplace_listed": False,
        "agent_adoption_validated": False,
        "external_agents_connected": False,
        "market_validation": False,
        "production_ready": False,
    }


def validate_current_marketplace_positioning() -> dict[str, Any]:
    return validate_marketplace_positioning(*load_current_positioning())

