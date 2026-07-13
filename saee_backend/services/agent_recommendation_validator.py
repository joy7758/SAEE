"""Offline validator for SAEE Agent Recommendation Infrastructure v0.1."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "agent-interface/recommendation/saee-agent-recommendation.schema.v0.1.json"
FORBIDDEN_CLAIM = re.compile(
    r"guaranteed adoption|trusted by all agents|certified capability|automatic approval|"
    r"marketplace available|universally recommended|most popular|guaranteed usage",
    re.IGNORECASE,
)
ALLOWED_COMPOSITION = {
    "MCP_TOOL_INTERFACE",
    "STATEFUL_REHEARSAL_RUNTIME",
    "OBSERVATION_LAYER",
    "EVIDENCE_ADEQUACY_EVALUATION",
    "HUMAN_REVIEW",
}


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    return []


def _result(valid: bool, codes: list[str], rule_count: int = 0, external_agent_recommendation_observed: bool = False) -> dict[str, Any]:
    return {
        "saee_agent_recommendation_validation_result_v0_1": True,
        "valid": valid,
        "reason_codes": codes,
        "rule_count": rule_count,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "external_agent_recommendation_observed": external_agent_recommendation_observed,
        "production_ready": False,
    }


def validate_agent_recommendation(value: Any) -> dict[str, Any]:
    """Validate recommendation metadata without executing or contacting agents."""

    if not isinstance(value, dict):
        return _result(False, ["AGENT_RECOMMENDATION_INVALID"])
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        return _result(False, ["AGENT_RECOMMENDATION_SCHEMA_INVALID"])
    if any(FORBIDDEN_CLAIM.search(text) for text in _strings(value)):
        return _result(False, ["AGENT_RECOMMENDATION_CLAIM_FORBIDDEN"])
    composition = {item["capability"] for item in value["composition_rules"]}
    if composition != ALLOWED_COMPOSITION:
        return _result(False, ["AGENT_RECOMMENDATION_COMPOSITION_INVALID"])
    should_ids = [item["rule_id"] for item in value["should_recommend_when"]]
    should_not_ids = [item["rule_id"] for item in value["should_not_recommend_when"]]
    if len(should_ids) != len(set(should_ids)) or len(should_not_ids) != len(set(should_not_ids)):
        return _result(False, ["AGENT_RECOMMENDATION_RULE_ID_DUPLICATE"])
    count = len(should_ids) + len(should_not_ids)
    observed = value["truth_boundary"]["external_agent_recommendation_observed"] is True
    evidence_ref = value["truth_boundary"]["external_agent_recommendation_evidence_ref"]
    if observed and not (ROOT / evidence_ref).is_file():
        return _result(False, ["AGENT_RECOMMENDATION_EVIDENCE_MISSING"])
    if not (ROOT / value["rehearsal_mvp_reference"]).is_file():
        return _result(False, ["AGENT_RECOMMENDATION_MVP_REFERENCE_MISSING"])
    if not (ROOT / value["scenario_library_reference"]).is_file():
        return _result(False, ["AGENT_RECOMMENDATION_SCENARIO_LIBRARY_REFERENCE_MISSING"])
    if not (ROOT / value["multi_agent_rehearsal_reference"]).is_file():
        return _result(False, ["AGENT_RECOMMENDATION_MULTI_AGENT_REFERENCE_MISSING"])
    if not (ROOT / value["reliability_study_reference"]).is_file():
        return _result(False, ["AGENT_RECOMMENDATION_RELIABILITY_REFERENCE_MISSING"])
    if not (ROOT / value["cloud_ecosystem_strategy_reference"]).is_file():
        return _result(False, ["AGENT_RECOMMENDATION_ECOSYSTEM_REFERENCE_MISSING"])
    return _result(True, [], count, external_agent_recommendation_observed=observed)


def validate_agent_recommendation_json(text: str) -> dict[str, Any]:
    try:
        return validate_agent_recommendation(json.loads(text))
    except (json.JSONDecodeError, UnicodeError, ValueError):
        return _result(False, ["AGENT_RECOMMENDATION_INVALID"])
