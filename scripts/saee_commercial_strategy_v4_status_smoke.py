#!/usr/bin/env python3
"""Validate the final local/external truth split for commercial strategy v4."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "agent-interface/commercial/saee-commercial-strategy-v4-status.json"
DOC = ROOT / "docs/strategy/SAEE_COMMERCIAL_STRATEGY_V4_IMPLEMENTATION_STATUS.md"


class StatusSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise StatusSmokeError(detail)


def validate(value: dict) -> dict:
    require(value["saee_commercial_strategy_v4_status"] is True, "status marker missing")
    require(value["status"] == "agent_native_strategy_implemented_controlled_agent_preference_validated", "status invalid")
    require([item["phase"] for item in value["phases"]] == ["6.0", "6.1", "6.2", "6.3", "6.4", "6.5"], "phase order invalid")
    require(value["local_evidence"] == {
        "rehearsal_demo_cases": 4,
        "benchmark_cases": 20,
        "benchmark_categories": 5,
        "mcp_tools": 2,
        "controlled_reasoning_live_runs": 3,
        "controlled_reasoning_live_provider_rounds": 5,
        "controlled_reasoning_hidden_profile_matches": 3,
        "external_world_actions": 0,
        "stateful_business_live_runs": 1,
        "stateful_business_provider_rounds": 4,
        "state_transition_count": 3,
        "customer_adapter_contract_enabled": False,
        "agent_preference_calibration_iterations": 3,
        "agent_preference_synthetic_agents": 6,
        "agent_preference_provider_rounds": 18,
        "agent_preference_hidden_profile_matches": 6,
        "agent_preference_compose_with_saee": 3,
        "agent_preference_do_not_recommend_saee": 3,
        "mainline_guard_passed": True,
    }, "local evidence drift")
    require(value["recommendation"] == {"controlled_reasoning_synthetic_world_prototype": "recommend", "controlled_agent_preference_simulation": "recommend", "design_partner_demonstration": "conditional", "production_deployment_approval": "do_not_recommend"}, "recommendation scope invalid")
    truth = value["external_truth"]
    require(truth["interviews_conducted"] == 0, "interview overclaim")
    require(truth["controlled_qianfan_reasoning_model_validated"] is True, "controlled Qianfan truth hidden")
    require(truth["design_partner_protocol_human_approved"] is True, "protocol approval hidden")
    require(truth["human_participants_excluded_from_validation"] is True, "human exclusion hidden")
    require(truth["controlled_synthetic_agent_preference_observed"] is True, "agent preference hidden")
    require(truth["external_agent_recommendation_observed"] is True, "external Agent recommendation hidden")
    for field in ("feedback_collected", "customer_validated", "willingness_to_pay_validated", "real_customer_agent_validated", "standard_mcp_interoperability_validated", "market_fit_achieved", "production_ready"):
        require(truth[field] is False, f"external truth overclaim: {field}")
    require(value["next_product_action"] == "Use the validated Agent preference to position SAEE as a composable Agent Readiness Layer alongside Observability; do not add unrelated domains.", "next product action invalid")
    require(value["next_commercial_action"] == "Prioritize machine discovery and controlled Agent integration; no human participant is required for the current validation route.", "next commercial action invalid")
    return copy.deepcopy(value)


def main() -> None:
    for path in (STATUS, DOC):
        require(path.is_file(), f"required file missing: {path}")
    value = json.loads(STATUS.read_text(encoding="utf-8"))
    canonical = validate(value)
    invalid = []
    for field in ("customer_validated", "willingness_to_pay_validated", "real_customer_agent_validated", "standard_mcp_interoperability_validated", "market_fit_achieved", "production_ready"):
        item = copy.deepcopy(value); item["external_truth"][field] = True; invalid.append((item, field))
    item = copy.deepcopy(value); item["external_truth"]["interviews_conducted"] = 5; invalid.append((item, "fake interviews"))
    item = copy.deepcopy(value); item["recommendation"]["production_deployment_approval"] = "recommend"; invalid.append((item, "production recommendation"))
    for item, label in invalid:
        try:
            validate(item)
        except StatusSmokeError:
            continue
        raise StatusSmokeError(f"invalid status accepted: {label}")
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate(json.loads(STATUS.read_text(encoding="utf-8")))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "status non-deterministic")
    doc = DOC.read_text(encoding="utf-8")
    for marker in ("千帆受控推理和有状态业务演练完成", "千帆多智能体偏好验证完成；人工参与者已排除", "do_not_recommend", "customer_validated=false"):
        require(marker in doc, f"status document marker missing: {marker}")
    print("SAEE_COMMERCIAL_STRATEGY_V4_STATUS_SMOKE: PASS")
    print("phases=6/6")
    print("invalid_cases=8/8")
    print("deterministic_runs=5/5")
    print("controlled_reasoning_live_runs=3")
    print("external_world_actions=0")
    print("stateful_business_live_runs=1")
    print("state_transition_count=3")
    print("customer_adapter_contract_enabled=false")
    print("agent_preference_calibration_iterations=3")
    print("agent_preference_hidden_profile_matches=6/6")
    print("human_participants_excluded_from_validation=true")
    print("external_agent_recommendation_observed=true")
    print("design_partner_protocol_human_approved=true")
    print("interviews_conducted=0")
    print("customer_validated=false")
    print("willingness_to_pay_validated=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (StatusSmokeError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"SAEE_COMMERCIAL_STRATEGY_V4_STATUS_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
