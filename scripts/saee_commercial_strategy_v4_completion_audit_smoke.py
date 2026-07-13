#!/usr/bin/env python3
"""Validate the SAEE commercial strategy v4 completion audit offline."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "agent-interface/commercial/saee-commercial-strategy-v4-completion-audit.json"
DOC = ROOT / "docs/strategy/SAEE_COMMERCIAL_STRATEGY_V4_COMPLETION_AUDIT.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_STRATEGY_V4_COMPLETION_AUDIT_RECOMMENDATION_GATE.md"
EXPECTED_REPORT_DIGEST = "086c6a4160c34ee4142b7030d35c30a4d7845a9c69082169ef08e21db00df891"


class AuditError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AuditError(detail)


def validate(value: dict) -> dict:
    require(value["saee_commercial_strategy_v4_completion_audit"] is True, "marker")
    require(value["language"] == "zh-CN", "language")
    require(value["source_report"]["sha256"] == EXPECTED_REPORT_DIGEST, "report digest")
    require(value["audit_outcome"] == "agent_native_strategy_implementation_complete_controlled_agent_preference_validated", "outcome")
    require(value["identity_alignment"]["engineering_core"] == "Digital Biosphere Evolution Engine", "core identity")
    require(value["identity_alignment"]["audit_first_reframe"] is False, "audit-first reframe")
    phases = value["phase_audit"]
    require([item["phase"] for item in phases] == ["6.0", "6.1", "6.2", "6.3", "6.4", "6.5"], "phase order")
    require(all(item["evidence_refs"] for item in phases), "phase evidence missing")
    for item in phases:
        for ref in item["evidence_refs"]:
            require((ROOT / ref).is_file(), "missing evidence ref: " + ref)
    require(phases[-1]["status"] == "CONTROLLED_QIANFAN_AGENT_PREFERENCE_VALIDATED", "phase 6.5 status")
    require(len(value["external_evidence_gaps"]) == 6, "external gap count")
    decision = value["completion_decision"]
    require(decision["report_architecture_implemented_locally"] is True, "local architecture hidden")
    require(decision["external_commercial_validation_complete"] is False, "external validation overclaim")
    require(decision["phase_6_5_controlled_agent_preference_validated"] is True, "phase 6.5 evidence hidden")
    require(decision["human_participant_validation_required"] is False, "human validation reintroduced")
    require(decision["agent_native_strategy_implementation_complete"] is True, "Agent-native strategy completion hidden")
    require(decision["commercial_strategy_goal_complete"] is True, "goal completion hidden")
    business = value["business_model_audit"]
    for field in ("pricing_validated", "willingness_to_pay_validated", "revenue_validated"):
        require(business[field] is False, "business overclaim: " + field)
    extension = value["recommendation_extension"]
    require(extension["external_agent_recommendation_observed"] is True, "external recommendation evidence hidden")
    require(extension["controlled_synthetic_agent_preference_observed"] is True, "controlled preference hidden")
    require(extension["automatic_recommendation_implemented"] is False, "automatic recommendation overclaim")
    require(extension["human_participant_validation_path_excluded"] is True, "human path not excluded")
    require(extension["establishes_customer_validation"] is False, "Agent simulation promoted to customer validation")
    action = value["next_authorized_action"]
    require(action["recommended_capability_positioning"] == "SAEE as a composable Agent Readiness Layer alongside Observability", "positioning drift")
    require(action["human_participant_required"] is False, "human participant required")
    for field in ("automatic_outreach_authorized", "customer_data_authorized", "real_customer_agent_authorized", "pilot_authorized", "sales_authorized", "external_world_execution_authorized"):
        require(action[field] is False, "action boundary opened: " + field)
    truth = value["truth_boundary"]
    require(truth["controlled_synthetic_agent_preference_observed"] is True, "Agent preference truth hidden")
    require(truth["human_participants_used"] is False, "human participant truth invalid")
    require(truth["interviews_conducted"] == 0, "interview overclaim")
    for field in ("customer_contacted", "feedback_collected", "customer_validated", "market_fit_achieved", "product_launched", "production_ready"):
        require(truth[field] is False, "truth overclaim: " + field)
    return copy.deepcopy(value)


def main() -> int:
    for path in (AUDIT, DOC, GATE):
        require(path.is_file(), "missing file: " + str(path))
    value = json.loads(AUDIT.read_text(encoding="utf-8"))
    canonical = validate(value)
    invalid = []
    mutation = copy.deepcopy(value); mutation["completion_decision"]["commercial_strategy_goal_complete"] = False; invalid.append(mutation)
    mutation = copy.deepcopy(value); mutation["completion_decision"]["external_commercial_validation_complete"] = True; invalid.append(mutation)
    mutation = copy.deepcopy(value); mutation["business_model_audit"]["revenue_validated"] = True; invalid.append(mutation)
    mutation = copy.deepcopy(value); mutation["recommendation_extension"]["external_agent_recommendation_observed"] = False; invalid.append(mutation)
    mutation = copy.deepcopy(value); mutation["recommendation_extension"]["automatic_recommendation_implemented"] = True; invalid.append(mutation)
    mutation = copy.deepcopy(value); mutation["completion_decision"]["human_participant_validation_required"] = True; invalid.append(mutation)
    mutation = copy.deepcopy(value); mutation["next_authorized_action"]["automatic_outreach_authorized"] = True; invalid.append(mutation)
    mutation = copy.deepcopy(value); mutation["truth_boundary"]["customer_validated"] = True; invalid.append(mutation)
    mutation = copy.deepcopy(value); mutation["truth_boundary"]["interviews_conducted"] = 1; invalid.append(mutation)
    for item in invalid:
        try:
            validate(item)
        except AuditError:
            continue
        raise AuditError("invalid audit accepted")
    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate(json.loads(AUDIT.read_text(encoding="utf-8")))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "non-deterministic")
    imports = set()
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    require(not imports.intersection({"socket", "subprocess", "requests", "urllib", "httpx"}), "external import")
    text = DOC.read_text(encoding="utf-8")
    for marker in ("commercial_strategy_goal_complete=true", "Phase 6 逐项审计", "智能体最终偏好", "后续边界"):
        require(marker in text, "doc marker: " + marker)
    print("SAEE_COMMERCIAL_STRATEGY_V4_COMPLETION_AUDIT_SMOKE: PASS")
    print("phases=6/6")
    print("phase_evidence_refs_valid=true")
    print("external_evidence_gaps=6/6")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("report_architecture_implemented_locally=true")
    print("external_commercial_validation_complete=false")
    print("phase_6_5_controlled_agent_preference_validated=true")
    print("human_participant_validation_required=false")
    print("agent_native_strategy_implementation_complete=true")
    print("commercial_strategy_goal_complete=true")
    print("automatic_outreach_authorized=false")
    print("customer_validated=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
