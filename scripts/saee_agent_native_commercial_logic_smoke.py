#!/usr/bin/env python3
"""Offline consistency checks for SAEE Agent-Native Commercial Logic v2.0."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LOGIC_PATH = ROOT / "agent-interface/commercial/saee-agent-native-commercial-logic.v2.json"
STRATEGY_PATH = ROOT / "docs/strategy/SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2_RECOMMENDATION_GATE.md"
AGENTS_PATH = ROOT / "AGENTS.md"
READABLE_PATH = ROOT / "docs/architecture/AGENT_READABLE_LAYER.md"
COMMERCIAL_BOUNDARY_PATH = ROOT / "docs/strategy/COMMERCIALIZATION_BOUNDARY.md"
PRODUCT_BOUNDARY_PATH = ROOT / "docs/strategy/PRODUCT_BOUNDARY.md"
DESIGN_PARTNER_PROTOCOL_PATH = ROOT / "docs/commercial/SAEE_DESIGN_PARTNER_VALIDATION_PROTOCOL.md"
DESIGN_PARTNER_PLAN_PATH = ROOT / "agent-interface/commercial/saee-design-partner-validation-plan.v0.1.json"
README_PATH = ROOT / "README.md"
LLMS_PATH = ROOT / "llms.txt"
AGENT_INDEX_PATH = ROOT / "agent-index.json"
CANONICAL_METADATA_PATH = ROOT / "docs/canonical/SAEE_CANONICAL_METADATA.yaml"
PROJECT_STATUS_PATH = ROOT / "PROJECT_STATUS.md"
AGENT_READABLE_ENTRY_PATH = ROOT / "agent-readable.md"

FALSE_TRUTH_FIELDS = {
    "customer_contacted",
    "feedback_collected",
    "human_participants_used",
    "customer_validated",
    "market_fit_achieved",
    "product_launched",
    "production_ready",
}

TRUE_TRUTH_FIELDS = {
    "external_agent_recommendation_validated",
    "controlled_synthetic_agent_preference_validated",
}

EXPECTED_GATE_IDS = {"AGENT_DISCOVERY", "AGENT_UNDERSTANDING", "AGENT_COMPOSITION"}

EXPECTED_PRIORITY_ORDER = [
    "AGENT_NATIVE_CAPABILITY_MANIFEST",
    "MACHINE_DISCOVERABILITY",
    "AGENT_TOOL_CAPABILITY",
    "CONTROLLED_MULTI_AGENT_PREFERENCE_VALIDATION",
    "CONTROLLED_AGENT_NATIVE_INTEGRATION",
    "AGENT_ECONOMY_OPTIONAL_FUTURE",
]


class AgentNativeLogicSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AgentNativeLogicSmokeError(detail)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    require(isinstance(value, dict), f"JSON root must be object: {path}")
    return value


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_execution_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen", "run", "Popen"}:
            found.add(node.func.attr)
    return found


def validate_logic(logic: dict[str, Any]) -> dict[str, Any]:
    require(logic.get("saee_agent_native_commercial_logic_v2") is True, "logic marker missing")
    require(logic.get("logic_version") == "2.0.0", "logic version invalid")
    require(logic.get("status") == "active_repository_decision_principle", "logic not active")

    identity = logic.get("project_identity", {})
    require(identity.get("engineering_core") == "Digital Biosphere Evolution Engine", "engineering core reframed")
    require(identity.get("commercial_capability_surface") == "SAEE Evidence Capability Layer", "capability surface invalid")
    require(identity.get("audit_first_reframe") is False, "audit-first reframe enabled")

    positioning = logic.get("positioning", {})
    require(
        positioning.get("english")
        == "SAEE provides machine-verifiable evidence adequacy evaluation for agent accountability workflows.",
        "English positioning drift",
    )
    require(
        positioning.get("chinese") == "SAEE 为智能体责任工作流提供机器可验证的证据充分性评估能力。",
        "Chinese positioning drift",
    )

    flow = logic.get("primary_flow", [])
    require(len(flow) == 5 and flow[0] == "AGENT_DISCOVERS_CAPABILITY", "agent-native flow invalid")
    require(flow[-1] == "HUMAN_AUTHORIZES_ONLY_CONSEQUENTIAL_EXTERNAL_ACTION", "external-action authority missing")
    require(flow[-2] == "AGENT_SELECTS_REJECTS_OR_COMPOSES_CAPABILITY", "Agent decision priority missing")

    gates = logic.get("mandatory_decision_gate", [])
    require({gate.get("gate_id") for gate in gates} == EXPECTED_GATE_IDS, "three-question gate incomplete")
    require(all(gate.get("required_answer") == "yes" for gate in gates), "gate answer policy weakened")

    required_surfaces = {"README.md", "agent-index.json", "llms.txt", "capability_manifest", "schema_registry", "cli_or_tool_interface"}
    require(set(logic.get("first_class_discovery_surfaces", [])) == required_surfaces, "discovery surfaces incomplete")
    require(logic.get("priority_order") == EXPECTED_PRIORITY_ORDER, "agent-native priority order invalid")

    authority = set(logic.get("human_authority_required_for", []))
    require(
        authority
        == {
            "EXTERNAL_CONTACT",
            "CUSTOMER_OR_PERSONAL_DATA",
            "PERMISSION_EXPANSION",
            "PRICING_OR_CONTRACT",
            "PILOT_APPROVAL",
            "PRODUCTION_DEPLOYMENT",
            "COMMERCIAL_OR_COMPLIANCE_CLAIMS",
        },
        "human authority boundary incomplete",
    )

    route = logic.get("current_route", {})
    require(route.get("design_partner_validation_protocol") == "historical_inactive_human_participants_excluded", "human validation route active")
    require(route.get("capability_manifest") == "implemented_with_controlled_agent_preference_evidence", "manifest route status invalid")
    require(route.get("next_stage") == "CONTROLLED_AGENT_NATIVE_INTEGRATION", "next stage invalid")
    require(route.get("external_agent_recommendation_test") == "validated_controlled_qianfan_synthetic_context", "Agent preference evidence hidden")
    require(route.get("commercial_adoption") == "not_started", "commercial adoption overclaimed")

    truth = logic.get("truth_boundary", {})
    require(set(truth) == FALSE_TRUTH_FIELDS | TRUE_TRUTH_FIELDS, "truth boundary shape invalid")
    require(all(truth[field] is False for field in FALSE_TRUTH_FIELDS), "truth boundary promoted")
    require(all(truth[field] is True for field in TRUE_TRUTH_FIELDS), "Agent preference truth hidden")
    require(logic.get("next_action") == "Controlled Agent-Native integration using SAEE with Observability", "next action invalid")
    return copy.deepcopy(logic)


def expect_invalid(logic: dict[str, Any], label: str) -> None:
    try:
        validate_logic(logic)
    except AgentNativeLogicSmokeError:
        return
    raise AgentNativeLogicSmokeError(f"invalid logic accepted: {label}")


def main() -> None:
    required_paths = (
        LOGIC_PATH,
        STRATEGY_PATH,
        GATE_PATH,
        AGENTS_PATH,
        READABLE_PATH,
        COMMERCIAL_BOUNDARY_PATH,
        PRODUCT_BOUNDARY_PATH,
        DESIGN_PARTNER_PROTOCOL_PATH,
        DESIGN_PARTNER_PLAN_PATH,
        README_PATH,
        LLMS_PATH,
        AGENT_INDEX_PATH,
        CANONICAL_METADATA_PATH,
        PROJECT_STATUS_PATH,
        AGENT_READABLE_ENTRY_PATH,
    )
    for path in required_paths:
        require(path.is_file(), f"missing required file: {path}")

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib"}
    require(not imported_roots(Path(__file__)).intersection(forbidden_imports), "network or subprocess capability imported")
    require(not forbidden_execution_calls(Path(__file__)), "dynamic or external execution present")

    strategy_text = STRATEGY_PATH.read_text(encoding="utf-8")
    agents_text = AGENTS_PATH.read_text(encoding="utf-8")
    for marker in (
        "SAEE Evidence Capability Layer",
        "Can an AI agent discover this capability?",
        "Can an AI agent understand when to use it?",
        "Can an AI agent compose this capability into workflows?",
        "Agent Recommendation != Human Authorization",
        "Design Partner Validation Protocol             historical_inactive_human_participants_excluded",
        "Agent-Native Capability Manifest v0.1           implemented_with_preference_evidence",
        "External Agent Recommendation Test              validated_controlled_qianfan_synthetic_context",
    ):
        require(marker in strategy_text, f"strategy marker missing: {marker}")
    for marker in (
        "## Agent-Native Commercial Decision Principle",
        "Can an AI agent discover this capability?",
        "Can an AI agent understand when to use it and when not to use it?",
        "Can an AI agent compose it into a workflow through a stable contract?",
    ):
        require(marker in agents_text, f"AGENTS marker missing: {marker}")

    design_protocol = DESIGN_PARTNER_PROTOCOL_PATH.read_text(encoding="utf-8")
    require("historical_protocol_inactive_human_participants_excluded" in design_protocol, "Design Partner protocol still active")
    design_plan = read_json(DESIGN_PARTNER_PLAN_PATH)
    require(
        design_plan.get("next_step")
        == "No human session; use controlled Qianfan multi-Agent preference validation and controlled Agent-native integration",
        "Design Partner machine route not updated",
    )

    readme_text = README_PATH.read_text(encoding="utf-8")
    llms_text = LLMS_PATH.read_text(encoding="utf-8")
    canonical_text = CANONICAL_METADATA_PATH.read_text(encoding="utf-8")
    status_text = PROJECT_STATUS_PATH.read_text(encoding="utf-8")
    agent_readable_entry_text = AGENT_READABLE_ENTRY_PATH.read_text(encoding="utf-8")
    agent_index = read_json(AGENT_INDEX_PATH)
    index_entry = agent_index.get("saee_agent_native_commercial_logic_v2", {})
    require(index_entry.get("status") == "active_repository_decision_principle", "agent index logic status missing")
    require(index_entry.get("next_stage") == "CONTROLLED_AGENT_NATIVE_INTEGRATION", "agent index next stage drift")
    for surface_name, surface_text in (
        ("README", readme_text),
        ("llms", llms_text),
        ("canonical metadata", canonical_text),
        ("project status", status_text),
        ("agent-readable entry", agent_readable_entry_text),
    ):
        require("SAEE Evidence Capability Layer" in surface_text, f"{surface_name} positioning missing")
        require("CONTROLLED_AGENT_NATIVE_INTEGRATION" in surface_text or "Controlled Agent-native Integration" in surface_text or "controlled Agent-native integration" in surface_text, f"{surface_name} next stage missing")

    logic = read_json(LOGIC_PATH)
    canonical = validate_logic(logic)
    invalid_cases: list[tuple[dict[str, Any], str]] = []
    for field in sorted(FALSE_TRUTH_FIELDS):
        mutation = copy.deepcopy(logic)
        mutation["truth_boundary"][field] = True
        invalid_cases.append((mutation, field))
    for field in sorted(TRUE_TRUTH_FIELDS):
        mutation = copy.deepcopy(logic)
        mutation["truth_boundary"][field] = False
        invalid_cases.append((mutation, field + " hidden"))
    mutation = copy.deepcopy(logic)
    mutation["project_identity"]["audit_first_reframe"] = True
    invalid_cases.append((mutation, "audit-first reframe"))
    mutation = copy.deepcopy(logic)
    mutation["current_route"]["next_stage"] = "HUMAN_DESIGN_PARTNER_INTERVIEW"
    invalid_cases.append((mutation, "human-first next stage"))
    mutation = copy.deepcopy(logic)
    mutation["mandatory_decision_gate"] = mutation["mandatory_decision_gate"][:2]
    invalid_cases.append((mutation, "missing composition gate"))
    for mutation, label in invalid_cases:
        expect_invalid(mutation, label)

    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_logic(read_json(LOGIC_PATH))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "logic validation non-deterministic")

    print("SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=5/5")
    print("mandatory_agent_questions=3/3")
    print("first_class_discovery_surfaces=6/6")
    print("agent_native_priority_order=6/6")
    print("design_partner_protocol=historical_inactive_human_participants_excluded")
    print("external_agent_recommendation_validated=true")
    print("controlled_synthetic_agent_preference_validated=true")
    print("human_participants_used=false")
    print("next_stage=CONTROLLED_AGENT_NATIVE_INTEGRATION")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("customer_contacted=false")
    print("customer_validated=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (AgentNativeLogicSmokeError, json.JSONDecodeError) as exc:
        print(f"SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
