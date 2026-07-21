#!/usr/bin/env python3
"""Offline deterministic validation for SAEE Agent Readiness Architecture v1.0."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "agent-interface/architecture/saee-agent-readiness-architecture.v1.json"
DOC_PATH = ROOT / "docs/architecture/SAEE_AGENT_READINESS_ARCHITECTURE_V1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_AGENT_READINESS_ARCHITECTURE_RECOMMENDATION_GATE.md"

LAYER_IDS = ["AGENT_WORLD", "AGENT_REHEARSAL", "EVIDENCE_INTELLIGENCE", "AGENT_NATIVE_INTERFACE"]
FLOW = ["AGENT", "REHEARSAL", "TRACE", "EVIDENCE", "SAEE_EVALUATION", "CAPABILITY_SERVICE", "AGENT_ECONOMY"]
TRUE_RUNTIME_FIELDS = {
    "agent_rehearsal_runtime_implemented",
    "agent_adapter_implemented",
    "scenario_runner_implemented",
    "controlled_environment_implemented",
    "trace_collector_implemented",
    "evidence_export_from_rehearsal_implemented",
}
FALSE_TRUTH_FIELDS = {
    "public_api_available",
    "public_mcp_available",
    "external_agent_tested",
    "customer_validated",
    "production_ready",
}


class ArchitectureSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ArchitectureSmokeError(detail)


def read_manifest() -> dict[str, Any]:
    value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "architecture manifest root must be object")
    return value


def local_ref_exists(ref: str) -> bool:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def validate(manifest: dict[str, Any]) -> dict[str, Any]:
    expected_keys = {
        "saee_agent_readiness_architecture_v1", "architecture_version", "status", "scope",
        "identity", "authority_model", "layers", "canonical_product_flow", "asset_reclassification",
        "current_truth", "roadmap", "entrypoints", "recommended_next_pr",
    }
    require(set(manifest) == expected_keys, "architecture manifest fields changed")
    require(manifest["saee_agent_readiness_architecture_v1"] is True, "manifest marker missing")
    require(manifest["architecture_version"] == "1.0", "architecture version invalid")
    require(manifest["status"] == "phase6_5_controlled_qianfan_agent_preference_validated", "architecture status invalid")
    require(manifest["scope"] == "l3_commercial_product_projection", "commercial projection scope invalid")

    identity = manifest["identity"]
    require(identity["canonical_engineering_core"] == "Digital Biosphere Evolution Engine", "engineering core reframed")
    require(identity["commercial_direction"] == "Agent Readiness Infrastructure", "commercial direction drift")
    require(identity["product_entry"] == "Agent Rehearsal Engine", "product entry drift")
    require(identity["technical_moat"] == "Evidence Intelligence", "technical moat drift")
    require(identity["audit_first_reframe"] is False, "audit-first reframe detected")
    require(identity["generic_agent_framework_reframe"] is False, "generic Agent framework reframe detected")

    authority = manifest["authority_model"]
    require(local_ref_exists(authority["canonical_specification"]), "canonical specification missing")
    require(local_ref_exists(authority["existing_product_projection"]), "v3 projection missing")
    for field in ("commercial_projection_is_canonical_authority", "canonical_architecture_replaced", "scientific_object_modified", "meta_protocol_modified"):
        require(authority[field] is False, f"canonical authority boundary violated: {field}")

    layers = manifest["layers"]
    require([layer["layer_id"] for layer in layers] == LAYER_IDS, "four-layer order invalid")
    require([layer["order"] for layer in layers] == [1, 2, 3, 4], "layer order values invalid")
    rehearsal = layers[1]
    require(rehearsal["current_status"] == "stateful_multi_step_qianfan_rehearsal_validated_in_synthetic_business_world", "rehearsal runtime status invalid")
    require(rehearsal["run_task_available"] is True, "run_task unavailable")
    require(rehearsal["real_world_execution_allowed"] is False, "real-world execution enabled")
    evidence = layers[2]
    require(evidence["governance_control_plane_ref"] == "SAEE Governance and Evidence Control Plane v0.1", "control-plane reclassification missing")
    require(evidence["safety_or_compliance_certification"] is False, "evidence promoted to certification")
    interface = layers[3]
    require(interface["current_status"] == "local_prototype_only", "interface status overclaimed")
    require(interface["public_service_available"] is False, "public service falsely available")
    require(interface["external_agent_compatibility_validated"] is False, "external compatibility overclaimed")

    require(manifest["canonical_product_flow"] == FLOW, "canonical product flow drift")
    classification = manifest["asset_reclassification"]
    require(classification["phase4_and_phase5_assets"] == "SAEE Governance and Evidence Control Plane v0.1", "Phase 4/5 assets not reclassified")
    for field in ("control_plane_is_rehearsal_runtime", "synthetic_simulation_is_real_agent_rehearsal", "local_mcp_is_public_capability_service"):
        require(classification[field] is False, f"asset overclaim: {field}")

    truth = manifest["current_truth"]
    require(truth["architecture_reunified"] is True, "architecture reunification not recorded")
    require(TRUE_RUNTIME_FIELDS.issubset(truth), "runtime truth fields missing")
    require(all(truth[field] is True for field in TRUE_RUNTIME_FIELDS), "implemented local Runtime hidden")
    require(truth["evaluate_rehearsal_run_available"] is True, "Agent Capability Alpha hidden")
    require(truth["controlled_external_reasoning_model_rehearsal_validated"] is True, "controlled reasoning rehearsal hidden")
    require(truth["controlled_reasoning_live_runs"] == 3, "controlled reasoning live run count invalid")
    require(truth["grading_profiles_hidden_from_agent"] is True, "grading profile separation missing")
    require(truth["external_world_actions"] == 0, "external-world action overclaim")
    require(truth["stateful_business_rehearsal_validated"] is True, "stateful business rehearsal hidden")
    require(truth["stateful_business_live_runs"] == 1, "stateful live run count invalid")
    require(truth["state_transition_count"] == 3, "state transition count invalid")
    require(truth["customer_controlled_adapter_contract_available"] is True, "customer Adapter contract hidden")
    require(truth["customer_controlled_adapter_enabled"] is False, "customer Adapter enabled")
    require(truth["agent_callable_runtime"] is True, "local Agent-callable Runtime hidden")
    require(truth["scenario_benchmark_implemented"] is True, "Scenario Benchmark hidden")
    require(truth["scenario_benchmark_case_count"] == 20, "Scenario Benchmark count invalid")
    require(truth["evaluate_rehearsal_run_mcp_tool_registered"] is True, "MCP Tool registration hidden")
    require(truth["standard_mcp_transport_available"] is False, "standard MCP transport overclaimed")
    require(truth["mcp_interoperability_validated"] is False, "MCP interoperability overclaimed")
    require(truth["design_partner_protocol_ready"] is True, "Design Partner protocol hidden")
    require(truth["design_partner_protocol_human_approved"] is True, "protocol approval missing")
    require(truth["design_partner_interviews_conducted"] == 0, "interview count overclaimed")
    require(truth["agent_preference_simulation_validated"] is True, "Agent preference validation hidden")
    require(truth["agent_preference_synthetic_agents"] == 6, "Agent preference count invalid")
    require(truth["agent_preference_provider_rounds"] == 18, "Agent preference round count invalid")
    require(truth["agent_preference_matched_profiles"] == 6, "Agent preference grading incomplete")
    require(truth["human_participants_excluded_from_validation"] is True, "human participant exclusion hidden")
    require(truth["external_reasoning_agent_recommendation_observed"] is True, "external reasoning Agent recommendation hidden")
    require(FALSE_TRUTH_FIELDS.issubset(truth), "truth fields missing")
    require(all(truth[field] is False for field in FALSE_TRUTH_FIELDS), "unimplemented capability promoted")

    roadmap = manifest["roadmap"]
    require([item["phase"] for item in roadmap] == ["6.0", "6.1", "6.2", "6.3", "6.4", "6.5"], "roadmap order invalid")
    require(roadmap[0]["status"] == "completed_documentation_and_truth_alignment", "Phase 6.0 completion boundary invalid")
    require(roadmap[1]["status"] == "stateful_multi_step_qianfan_business_rehearsal_validated_customer_agent_pending", "Phase 6.1 completion invalid")
    require(roadmap[2]["status"] == "completed_local_offline_alpha", "Phase 6.2 status invalid")
    require(roadmap[3]["status"] == "completed_local_20_case_synthetic_benchmark", "Phase 6.3 status invalid")
    require(roadmap[4]["status"] == "completed_local_in_memory_capability_no_standard_transport", "Phase 6.4 status invalid")
    require(roadmap[5]["status"] == "controlled_qianfan_multi_agent_preference_validated_human_participants_excluded", "Phase 6.5 status invalid")

    for key, ref in manifest["entrypoints"].items():
        if key == "validation_command":
            continue
        require(local_ref_exists(ref), f"entrypoint missing: {key}")
    require(manifest["recommended_next_pr"] == "Controlled Agent-Native integration based on validated SAEE plus Observability composition", "next action invalid")
    return copy.deepcopy(manifest)


def expect_invalid(manifest: dict[str, Any], label: str) -> None:
    try:
        validate(manifest)
    except ArchitectureSmokeError:
        return
    raise ArchitectureSmokeError(f"invalid architecture accepted: {label}")


def forbidden_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"run", "Popen", "system", "popen"}:
            found.add(node.func.attr)
    return found


def main() -> None:
    for path in (MANIFEST_PATH, DOC_PATH, GATE_PATH):
        require(path.is_file(), f"required file missing: {path}")
    require(not forbidden_calls(Path(__file__)), "dynamic or external execution detected")

    doc = DOC_PATH.read_text(encoding="utf-8")
    for marker in (
        "Digital Biosphere Evolution Engine",
        "Agent Rehearsal Engine",
        "SAEE Governance and Evidence Control Plane v0.1",
        "百度千帆真实推理",
        "有状态、多步骤的 SaaS 发布世界",
    ):
        require(marker in doc, f"architecture marker missing: {marker}")

    manifest = read_manifest()
    canonical = validate(manifest)
    invalid: list[tuple[dict[str, Any], str]] = []
    mutation = copy.deepcopy(manifest); mutation["identity"]["canonical_engineering_core"] = "Evidence Audit SDK"; invalid.append((mutation, "audit-first core"))
    mutation = copy.deepcopy(manifest); mutation["layers"].pop(1); invalid.append((mutation, "missing rehearsal layer"))
    mutation = copy.deepcopy(manifest); mutation["layers"][1]["run_task_available"] = False; invalid.append((mutation, "hidden run_task"))
    mutation = copy.deepcopy(manifest); mutation["current_truth"]["agent_rehearsal_runtime_implemented"] = False; invalid.append((mutation, "hidden runtime"))
    mutation = copy.deepcopy(manifest); mutation["current_truth"]["controlled_reasoning_live_runs"] = 0; invalid.append((mutation, "hidden live reasoning runs"))
    mutation = copy.deepcopy(manifest); mutation["current_truth"]["stateful_business_live_runs"] = 0; invalid.append((mutation, "hidden stateful live run"))
    mutation = copy.deepcopy(manifest); mutation["current_truth"]["customer_controlled_adapter_enabled"] = True; invalid.append((mutation, "customer Adapter enabled"))
    mutation = copy.deepcopy(manifest); mutation["current_truth"]["production_ready"] = True; invalid.append((mutation, "fake production"))
    mutation = copy.deepcopy(manifest); mutation["asset_reclassification"]["control_plane_is_rehearsal_runtime"] = True; invalid.append((mutation, "control plane promoted"))
    mutation = copy.deepcopy(manifest); mutation["current_truth"]["evaluate_rehearsal_run_available"] = False; invalid.append((mutation, "hidden Alpha"))
    mutation = copy.deepcopy(manifest); mutation["current_truth"]["scenario_benchmark_case_count"] = 3; invalid.append((mutation, "benchmark count regression"))
    mutation = copy.deepcopy(manifest); mutation["current_truth"]["standard_mcp_transport_available"] = True; invalid.append((mutation, "MCP transport overclaim"))
    mutation = copy.deepcopy(manifest); mutation["current_truth"]["design_partner_protocol_human_approved"] = False; invalid.append((mutation, "hidden protocol approval"))
    mutation = copy.deepcopy(manifest); mutation["canonical_product_flow"].remove("REHEARSAL"); invalid.append((mutation, "rehearsal bypass"))
    for item, label in invalid:
        expect_invalid(item, label)

    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate(read_manifest())
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "validation is non-deterministic")

    print("SAEE_AGENT_READINESS_ARCHITECTURE_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("product_layers=4/4")
    print("canonical_architecture_replaced=false")
    print("agent_rehearsal_runtime_implemented=true")
    print("controlled_external_reasoning_model_rehearsal_validated=true")
    print("controlled_reasoning_live_runs=3")
    print("external_world_actions=0")
    print("stateful_business_rehearsal_validated=true")
    print("stateful_business_live_runs=1")
    print("state_transition_count=3")
    print("customer_controlled_adapter_enabled=false")
    print("evaluate_rehearsal_run_available=true")
    print("scenario_benchmark_case_count=20")
    print("evaluate_rehearsal_run_mcp_tool_registered=true")
    print("standard_mcp_transport_available=false")
    print("design_partner_protocol_ready=true")
    print("design_partner_protocol_human_approved=true")
    print("design_partner_interviews_conducted=0")
    print("agent_preference_simulation_validated=true")
    print("agent_preference_synthetic_agents=6")
    print("agent_preference_provider_rounds=18")
    print("agent_preference_matched_profiles=6/6")
    print("human_participants_excluded_from_validation=true")
    print("recommended_next_action=controlled_agent_native_integration")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (ArchitectureSmokeError, json.JSONDecodeError) as exc:
        print(f"SAEE_AGENT_READINESS_ARCHITECTURE_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
