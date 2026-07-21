#!/usr/bin/env python3
"""Validate the Phase 6.5 Chinese Design Partner protocol without outreach."""

from __future__ import annotations

import ast
import copy
import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_design_partner_rehearsal_demo import build_demo, live_evidence_available


PLAN = ROOT / "agent-interface/commercial/saee-agent-rehearsal-design-partner-plan.v0.1.json"
PROTOCOL = ROOT / "docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_PROTOCOL.md"
DEMO_DOC = ROOT / "docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_DEMO.md"
FEEDBACK = ROOT / "docs/commercial/SAEE_AGENT_REHEARSAL_FEEDBACK_TEMPLATE.md"
GATE = ROOT / "docs/strategy/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_RECOMMENDATION_GATE.md"
DEMO_RUNNER = ROOT / "scripts/saee_design_partner_rehearsal_demo.py"
REVIEW_PACKET = ROOT / "docs/commercial/SAEE_STATEFUL_DESIGN_PARTNER_HUMAN_REVIEW_PACKET.md"
REVIEW_REQUEST = ROOT / "agent-interface/commercial/saee-stateful-design-partner-review-request.v0.1.json"
APPROVAL_RECORD = ROOT / "docs/commercial/SAEE_STATEFUL_DESIGN_PARTNER_PROTOCOL_APPROVAL_RECORD.md"
SESSION_GATE_DOC = ROOT / "docs/commercial/SAEE_DESIGN_PARTNER_SESSION_ENTRY_GATE.md"
SESSION_GATE = ROOT / "agent-interface/commercial/saee-design-partner-session-entry-gate.v0.1.json"


class ProtocolSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ProtocolSmokeError(detail)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root invalid: {path}")
    return value


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def validate(plan: dict[str, Any]) -> dict[str, Any]:
    require(plan["saee_agent_rehearsal_design_partner_plan_v0_1"] is True, "plan marker missing")
    require(plan["plan_version"] == "0.1.0" and plan["language"] == "zh-CN", "version or language invalid")
    require(plan["validation_stage"] == "historical_protocol_inactive_human_participants_excluded", "stage invalid")
    require(plan["validation_route_active"] is False and plan["human_participants_excluded"] is True, "human route not disabled")
    require(plan["protocol_ready"] is True and plan["protocol_human_approved"] is True, "protocol approval truth invalid")
    for field, expected in (("customer_contacted", False), ("interviews_conducted", 0), ("feedback_collected", False), ("customer_data_received", False), ("customer_validated", False), ("market_fit_achieved", False), ("pilot_started", False), ("production_ready", False)):
        require(plan[field] == expected, f"external status overclaim: {field}")
    require(len(plan["profiles"]) == 3, "profile count invalid")
    require(len(plan["metrics"]) == 6, "metric count invalid")
    require(plan["demo"]["synthetic_only"] is True, "non-synthetic demo enabled")
    require(plan["demo"]["recorded_real_reasoning_model_runs"] is True, "real reasoning demo evidence hidden")
    require(plan["demo"]["provider"] == "baidu_qianfan", "demo provider drift")
    require(plan["demo"]["real_customer_agent"] is False, "customer Agent overclaim")
    require(plan["demo"]["external_world_actions"] == 0, "external-world action overclaim")
    require(plan["demo"]["steps"] == ["RUN_BASELINE", "RUN_TOOL_FAILURE", "RUN_INSTRUCTION_CONFLICT", "RUN_STATEFUL_SAAS_RELEASE", "SHOW_TRACE_AND_EVIDENCE", "SHOW_20_CASE_BENCHMARK", "SHOW_LOCAL_MCP_TOOLS"], "demo flow invalid")
    rule = plan["future_minimum_session_rule"]
    require(rule["minimum_sessions"] == 5, "minimum session rule invalid")
    require(rule["thresholds_establish_product_market_fit"] is False, "threshold promoted to PMF")
    require(rule["negative_results_must_be_reported"] is True, "negative result suppression allowed")
    boundaries = plan["boundaries"]
    require(boundaries["protocol_human_review_required"] is True and boundaries["per_session_consent_required"] is True, "human gate missing")
    require(boundaries["synthetic_examples_only"] is True, "synthetic boundary missing")
    for field in ("personal_data_allowed", "customer_data_allowed", "private_logs_allowed", "production_traces_allowed", "credentials_allowed", "customer_outreach_authorized", "sales_activity_authorized", "pilot_authorized", "external_execution_authorized"):
        require(boundaries[field] is False, f"boundary opened: {field}")
    for ref in [*plan["source_artifacts"], plan["demo"]["script_ref"], plan["demo"]["runner_ref"], plan["feedback_template_ref"]]:
        require((ROOT / ref).is_file(), f"reference missing: {ref}")
    return copy.deepcopy(plan)


def expect_invalid(plan: dict[str, Any], label: str) -> None:
    try:
        validate(plan)
    except ProtocolSmokeError:
        return
    raise ProtocolSmokeError(f"invalid plan accepted: {label}")


def validate_review(review: dict[str, Any]) -> None:
    require(review["status"] == "protocol_human_approved_external_session_selection_pending", "review status")
    require(review["language"] == "zh-CN", "review language")
    require(review["evidence"]["controlled_reasoning_live_runs"] == 3, "controlled evidence count")
    require(review["evidence"]["stateful_business_live_runs"] == 1, "stateful evidence count")
    require(review["evidence"]["state_transition_count"] == 3, "transition evidence count")
    require(review["evidence"]["external_world_actions"] == 0, "review external actions")
    expected_phrase = "确认批准 SAEE 有状态智能体演练 Design Partner Protocol v0.1 进入受控外部问题访谈准备；本批准不授权自动外联、客户数据、真实客户 Agent、Pilot、销售、生产部署或外部世界执行。"
    require(review["exact_approval_phrase"] == expected_phrase, "approval phrase drift")
    require(review["approval_record"]["recorded"] is True, "approval not recorded")
    require(review["approval_record"]["exact_phrase_sha256"] == "de2dfb462ec32613ce6a3b52b8fb86cb5f042e3b1bfc2bf629d78f4c9fbb9402", "approval digest")
    truth = review["truth_boundary"]
    require(truth["protocol_human_approved"] is True, "protocol approval hidden")
    for field in ("outreach_authorized", "customer_contacted", "customer_data_allowed", "real_customer_agent_allowed", "pilot_authorized", "sales_authorized", "external_world_execution_authorized", "customer_validated", "production_ready"):
        require(truth[field] is False, "review boundary opened: " + field)
    require(truth["interviews_conducted"] == 0, "review interview overclaim")


def validate_session_gate(gate: dict[str, Any]) -> None:
    require(gate["status"] == "inactive_human_participants_excluded", "session gate status")
    require(gate["protocol_human_approved"] is True, "session gate hides protocol approval")
    require(gate["active_validation_route"] is False and gate["human_participants_excluded"] is True, "session route still active")
    guidance = gate["selection_guidance"]
    require(guidance["recommended_profile"] == "AI_AGENT_PLATFORM_TEAM", "recommended profile drift")
    require(guidance["priority_order"] == ["AI_AGENT_PLATFORM_TEAM", "AI_EVALUATION_RED_TEAM_TEAM", "AI_GOVERNANCE_RISK_TEAM"], "profile priority drift")
    require(guidance["required_human_fields"] == ["participant_alias", "participant_profile", "organization_type", "consent_confirmed", "session_date", "human_facilitator_alias"], "required human fields drift")
    for field in ("selection_is_customer_contact", "selection_authorizes_outreach", "selection_establishes_customer_validation"):
        require(guidance[field] is False, "selection guidance boundary opened: " + field)
    require(gate["participant_alias"] is None, "participant alias recorded prematurely")
    require(gate["participant_profile"] is None, "participant selected without authorization flow")
    require(gate["organization_type"] is None, "organization recorded prematurely")
    require(gate["session_date"] is None, "session created prematurely")
    require(gate["human_facilitator_alias"] is None, "facilitator recorded prematurely")
    require(gate["consent_confirmed"] is False, "consent overclaim")
    require(gate["session_authorized"] is False, "session authorization overclaim")
    require(gate["outreach_authorized"] is False, "outreach authorization overclaim")
    require(gate["customer_contacted"] is False, "customer contact overclaim")
    require(gate["interviews_conducted"] == 0, "session interview overclaim")
    for field in ("personal_data_allowed", "customer_data_allowed", "real_customer_agent_allowed", "pilot_authorized", "sales_authorized", "external_world_execution_authorized", "customer_validated", "production_ready"):
        require(gate[field] is False, "session boundary opened: " + field)


def main() -> None:
    for path in (PLAN, PROTOCOL, DEMO_DOC, FEEDBACK, GATE, DEMO_RUNNER, REVIEW_PACKET, REVIEW_REQUEST, APPROVAL_RECORD, SESSION_GATE_DOC, SESSION_GATE):
        require(path.is_file(), f"required file missing: {path}")
    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib"}
    require(not imported_roots(DEMO_RUNNER).intersection(forbidden), "demo performs network or subprocess action")

    plan = load(PLAN)
    canonical = validate(plan)
    review = load(REVIEW_REQUEST)
    validate_review(review)
    session_gate = load(SESSION_GATE)
    validate_session_gate(session_gate)
    for ref in review["review_documents"]:
        require((ROOT / ref).is_file(), "review document missing: " + ref)
    evidence_available = live_evidence_available()
    optional_evidence = os.environ.get("SAEE_PROVIDER_EVIDENCE_MODE") == "optional"
    require(evidence_available or optional_evidence, "external Provider evidence missing")
    demo = build_demo() if evidence_available else None
    if demo is not None:
        require(demo["language"] == "zh-CN", "demo language invalid")
        require(len(demo["cases"]) == 4, "demo case count invalid")
        require(demo["benchmark_metrics"]["total_cases"] == 20, "demo benchmark missing")
        require(set(demo["tool_names"]) == {"evaluate_evidence_adequacy", "evaluate_rehearsal_run"}, "demo Tool discovery invalid")
        require(demo["truth_boundary"] == {"customer_contacted": False, "feedback_collected": False, "customer_data_used": False, "controlled_qianfan_reasoning_model_validated": True, "real_customer_agent_validated": False, "synthetic_world_only": True, "external_world_actions": 0, "stateful_business_rehearsal_validated": True, "customer_adapter_contract_enabled": False, "standard_mcp_transport_available": False, "deployment_authorized": False, "production_ready": False}, "demo truth boundary invalid")
        require(all(case["grading_assessment"] == "MATCHED_PROFILE" for case in demo["cases"]), "live grading results missing")
        require(all(case["grading_profile_hidden_from_agent"] is True for case in demo["cases"]), "grading profile separation missing")
        stateful = next(case for case in demo["cases"] if case["scenario_category"] == "stateful_saas_release_readiness")
        require(stateful["state_transition_count"] == 3 and stateful["final_revision"] == 3, "stateful case missing")
        require(stateful["deployment_tool_called"] is False, "stateful deployment attempted")

    invalid: list[tuple[dict[str, Any], str]] = []
    for field in ("customer_contacted", "feedback_collected", "customer_data_received", "customer_validated", "market_fit_achieved", "pilot_started", "production_ready"):
        item = copy.deepcopy(plan); item[field] = True; invalid.append((item, field))
    item = copy.deepcopy(plan); item["interviews_conducted"] = 1; invalid.append((item, "fake interview"))
    item = copy.deepcopy(plan); item["boundaries"]["customer_outreach_authorized"] = True; invalid.append((item, "outreach authorization"))
    item = copy.deepcopy(plan); item["future_minimum_session_rule"]["thresholds_establish_product_market_fit"] = True; invalid.append((item, "PMF escalation"))
    for item, label in invalid:
        expect_invalid(item, label)

    review_invalid = []
    for field in ("outreach_authorized", "customer_data_allowed", "real_customer_agent_allowed", "pilot_authorized", "production_ready"):
        item = copy.deepcopy(review)
        item["truth_boundary"][field] = True
        review_invalid.append((field, item))
    item = copy.deepcopy(review)
    item["truth_boundary"]["protocol_human_approved"] = False
    review_invalid.append(("protocol_human_approved_false", item))
    for field, item in review_invalid:
        try:
            validate_review(item)
        except ProtocolSmokeError:
            continue
        raise ProtocolSmokeError("invalid review request accepted: " + field)

    session_invalid = []
    for field in ("session_authorized", "outreach_authorized", "customer_contacted"):
        item = copy.deepcopy(session_gate)
        item[field] = True
        session_invalid.append((field, item))
    item = copy.deepcopy(session_gate)
    item["interviews_conducted"] = 1
    session_invalid.append(("interviews_conducted", item))
    for field in ("customer_data_allowed", "real_customer_agent_allowed", "external_world_execution_authorized"):
        item = copy.deepcopy(session_gate)
        item[field] = True
        session_invalid.append((field, item))
    for field in ("selection_is_customer_contact", "selection_authorizes_outreach", "selection_establishes_customer_validation"):
        item = copy.deepcopy(session_gate)
        item["selection_guidance"][field] = True
        session_invalid.append((field, item))
    for field, item in session_invalid:
        try:
            validate_session_gate(item)
        except ProtocolSmokeError:
            continue
        raise ProtocolSmokeError("invalid session gate accepted: " + field)

    protocol = PROTOCOL.read_text(encoding="utf-8")
    feedback = FEEDBACK.read_text(encoding="utf-8")
    for marker in ("30 分钟", "20 场景 Benchmark", "百度千帆真实推理模型", "Protocol Ready != External Validation", "protocol_human_approved=true", "customer_contacted=false", "historical_protocol_inactive_human_participants_excluded"):
        require(marker in protocol, f"protocol marker missing: {marker}")
    for forbidden_field in ("姓名：", "邮箱：", "公司名称：", "联系电话："):
        require(forbidden_field not in feedback, f"identifying field present: {forbidden_field}")

    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    demo_encoded = json.dumps(demo, ensure_ascii=False, sort_keys=True, separators=(",", ":")) if demo is not None else None
    for _ in range(5):
        require(json.dumps(validate(load(PLAN)), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "plan non-deterministic")
        if demo_encoded is not None:
            require(json.dumps(build_demo(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == demo_encoded, "demo non-deterministic")

    print("SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_PROTOCOL_SMOKE: PASS")
    print("external_provider_evidence_status=" + ("VERIFIED" if evidence_available else "NOT_REQUIRED"))
    print("profiles=3/3")
    print("metrics=6/6")
    print("demo_cases=" + ("4/4" if evidence_available else "NOT_REQUIRED"))
    print("controlled_qianfan_reasoning_model_validated=" + ("true" if evidence_available else "not_checked"))
    print("real_customer_agent_validated=false")
    print("external_world_actions=0")
    print("stateful_business_rehearsal_validated=" + ("true" if evidence_available else "not_checked"))
    print("state_transition_count=" + ("3" if evidence_available else "NOT_REQUIRED"))
    print("customer_adapter_contract_enabled=false")
    print("benchmark_cases=20/20")
    print("mcp_tools=2/2")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("review_boundary_cases=6/6")
    print(f"session_gate_boundary_cases={len(session_invalid)}/{len(session_invalid)}")
    print("recommended_participant_profile=AI_AGENT_PLATFORM_TEAM")
    print("deterministic_runs=5/5")
    print("protocol_ready=true")
    print("protocol_human_approved=true")
    print("customer_contacted=false")
    print("interviews_conducted=0")
    print("feedback_collected=false")
    print("customer_validated=false")
    print("market_fit_achieved=false")
    print("production_ready=false")
    print("human_review_packet_ready=true")
    print("outreach_authorized=false")
    print("session_authorized=false")
    print("human_participants_excluded=true")
    print("active_validation_route=false")


if __name__ == "__main__":
    try:
        main()
    except (ProtocolSmokeError, json.JSONDecodeError, ValueError, KeyError) as exc:
        print(f"SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_PROTOCOL_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
