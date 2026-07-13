"""Offline validator for SAEE Phase 15 agent-native adoption strategy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
LOOP_PATH = ROOT / "agent-interface/adoption/saee-agent-adoption-loop.v0.1.json"
SIGNALS_PATH = ROOT / "agent-interface/adoption/saee-agent-adoption-signals.v0.1.json"
SCENARIO_DIR = ROOT / "agent-interface/adoption/agent-adoption-scenarios"
SCHEMA_PATH = ROOT / "schemas/saee-agent-invocation-trigger.schema.v0.1.json"
CUSTOMER_DOC = ROOT / "docs/strategy/SAEE_AGENT_CUSTOMER_MODEL.md"
RECOMMENDATION_DOC = ROOT / "docs/architecture/SAEE_AGENT_CAPABILITY_RECOMMENDATION_LOGIC.md"
REVIEW_DOC = ROOT / "docs/strategy/SAEE_AGENT_NATIVE_ADOPTION_STRATEGY_REVIEW.md"
ALLOWED_SIGNALS = {"capability_discovered", "capability_invoked", "result_interpreted", "repeat_invocation_pattern"}
FORBIDDEN_INTERPRETATIONS = {"market_adoption", "customer_success", "industry_acceptance"}
LOOP_STAGES = {"trigger", "discovery", "understanding", "invocation", "interpretation", "reuse_signal"}
FORBIDDEN_CLAIMS = (
    "Humans are the primary customer.",
    "SAEE required for all agents.",
    "SAEE trusted by all agents.",
    "SAEE market adoption is validated.",
    "SAEE certification established.",
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path.name)
    return value


def load_current_strategy() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    return (
        _load(LOOP_PATH),
        _load(SIGNALS_PATH),
        [_load(path) for path in sorted(SCENARIO_DIR.glob("*.json"))],
        {"customer": CUSTOMER_DOC.read_text(encoding="utf-8"), "recommendation": RECOMMENDATION_DOC.read_text(encoding="utf-8"), "review": REVIEW_DOC.read_text(encoding="utf-8")},
    )


def validate_agent_native_adoption_strategy(loop: Any, signals: Any, scenarios: Any, documents: Any) -> dict[str, Any]:
    reasons: list[str] = []
    if not all(isinstance(value, dict) for value in (loop, signals, documents)) or not isinstance(scenarios, list):
        return {"valid": False, "reason_codes": ["AGENT_ADOPTION_STRATEGY_INPUT_INVALID"]}
    stages = loop.get("loop_stages", {})
    if loop.get("strategy_version") != "0.1" or loop.get("primary_customer_model") != "AUTONOMOUS_AGENT_SYSTEMS" or not isinstance(stages, dict) or set(stages) != LOOP_STAGES:
        reasons.append("AGENT_CUSTOMER_MODEL_INVALID")
    loop_truth = loop.get("truth_boundary", {})
    expected_truth = {"agent_native_strategy_review": True, "agent_adoption_validated": False, "external_agents_connected": False, "customer_validation": False, "market_validation": False, "production_ready": False}
    if loop_truth != expected_truth:
        reasons.append("AGENT_ADOPTION_STRATEGY_BOUNDARY_INVALID")
    signal_items = signals.get("signals", [])
    if signals.get("signal_version") != "0.1" or not isinstance(signal_items, list) or {item.get("signal_type") for item in signal_items if isinstance(item, dict)} != ALLOWED_SIGNALS:
        reasons.append("AGENT_ADOPTION_SIGNAL_MODEL_INVALID")
    for item in signal_items if isinstance(signal_items, list) else []:
        if not isinstance(item, dict) or set(item) != {"signal_type", "meaning", "evidence_source", "limitations"} or not item.get("limitations"):
            reasons.append("AGENT_ADOPTION_SIGNAL_MODEL_INVALID"); break
    if set(signals.get("forbidden_interpretations", [])) != FORBIDDEN_INTERPRETATIONS or signals.get("truth_boundary") != {"signals_are_behavioral_observations": True, "agent_adoption_validated": False, "customer_validation": False, "market_validation": False, "production_ready": False}:
        reasons.append("AGENT_ADOPTION_SIGNAL_BOUNDARY_INVALID")
    schema = _load(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    if len(scenarios) < 5 or any(list(validator.iter_errors(item)) for item in scenarios):
        reasons.append("AGENT_INVOCATION_TRIGGER_MODEL_INVALID")
    expected_actions = {"SIMPLE_LOOKUP": "DO_NOT_USE_SAEE", "AUTHORIZATION_TASK": "COMPOSE_WITH_SEPARATE_AUTHORITY"}
    for item in scenarios:
        if not isinstance(item, dict):
            continue
        expected = expected_actions.get(item.get("trigger_type"), "CONSIDER_SAEE")
        if item.get("expected_action") != expected or item.get("mandatory_usage") is not False:
            reasons.append("AGENT_RECOMMENDATION_BOUNDARY_INVALID"); break
    combined_docs = "\n".join(value for value in documents.values() if isinstance(value, str))
    if "Autonomous Agent Systems（自主智能体系统）" not in documents.get("customer", ""):
        reasons.append("AGENT_CUSTOMER_MODEL_DOCUMENTATION_MISSING")
    for marker in ("recommendation != requirement", "recommendation != authorization", "recommendation != trust"):
        if marker not in documents.get("recommendation", ""):
            reasons.append("AGENT_RECOMMENDATION_BOUNDARY_MISSING")
    if "This strategy models how future agents may discover and use SAEE capabilities. It does not establish current agent adoption." not in documents.get("review", ""):
        reasons.append("AGENT_ADOPTION_LIMITATION_MISSING")
    if any(claim in combined_docs for claim in FORBIDDEN_CLAIMS):
        reasons.append("AGENT_ADOPTION_FORBIDDEN_CLAIM")
    valid = not reasons
    return {
        "valid": valid,
        "reason_codes": list(dict.fromkeys(reasons)),
        "agent_customer_model": valid,
        "trigger_model": valid,
        "recommendation_boundary": valid,
        "adoption_signal_boundary": valid,
        "scenario_count": len(scenarios),
        "signal_count": len(signal_items) if isinstance(signal_items, list) else 0,
        "agent_native_strategy_review": valid,
        "agent_adoption_validated": False,
        "external_agents_connected": False,
        "customer_validation": False,
        "market_validation": False,
        "production_ready": False,
    }


def validate_current_agent_native_adoption_strategy() -> dict[str, Any]:
    return validate_agent_native_adoption_strategy(*load_current_strategy())

