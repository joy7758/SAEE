#!/usr/bin/env python3
"""Offline deterministic checks for the SAEE Agent-Native Tool Capability Gate v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "agent-interface/capabilities/saee-tool-capability-gate.v0.1.json"
REVIEW_PATH = ROOT / "docs/architecture/SAEE_AGENT_NATIVE_TOOL_CAPABILITY_GATE_REVIEW.md"
DISCOVERY_PATH = ROOT / "docs/architecture/SAEE_AGENT_DISCOVERY_VALIDATION.md"
CURRENT_MANIFEST_PATH = ROOT / "agent-interface/capabilities/saee-capability-manifest.v0.1.json"

FIXED_CLAIMS = {
    "RESOURCE_AUTHENTICITY",
    "AUTHORIZED_AGENT_ACTION",
    "HUMAN_OVERSIGHT",
    "EXECUTION_BOUNDARY",
}
REQUIRED_INPUTS = {"evidence_object", "accountability_claim", "evaluation_profile"}
REQUIRED_OUTPUTS = {
    "claim_assessment",
    "evidence_sufficiency_status",
    "missing_requirements",
    "reason_codes",
    "limitations",
    "boundary_statement",
}


class ToolCapabilityGateSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ToolCapabilityGateSmokeError(detail)


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


def validate_gate(gate: dict[str, Any]) -> dict[str, Any]:
    require(gate.get("saee_tool_capability_gate_v0_1") is True, "gate marker missing")
    require(gate.get("record_scope") == "phase_4_0_pre_implementation_gate_snapshot", "gate snapshot scope missing")
    require(gate.get("current_status_source") == "agent-interface/capabilities/saee-capability-manifest.v0.1.json", "current status source missing")
    require(gate.get("current_status_not_defined_by_this_gate") is True, "historical gate promoted to current truth")
    require(gate.get("gate_version") == "0.1", "gate version invalid")
    require(gate.get("gate_status") == "recommend_local_prototype_pending_explicit_approval", "gate status invalid")
    require(gate.get("tool_capability_recommended") is True, "candidate capability not recommended")
    require(gate.get("implementation_authorized") is False, "implementation authorization expanded")
    require(gate.get("recommended_stage") == "local_prototype", "recommended stage invalid")
    require(gate.get("mcp_authorized") is False, "top-level MCP authorization expanded")
    require(gate.get("api_authorized") is False, "top-level API authorization expanded")
    require(gate.get("production_ready") is False, "top-level production status promoted")

    candidate = gate.get("candidate_capability", {})
    require(candidate.get("capability_id") == "evaluate_evidence_adequacy", "candidate id invalid")
    require(set(candidate.get("inputs", [])) == REQUIRED_INPUTS, "candidate inputs invalid")
    require(set(candidate.get("outputs", [])) == REQUIRED_OUTPUTS, "candidate outputs invalid")
    require(set(candidate.get("fixed_claim_types", [])) == FIXED_CLAIMS, "fixed claim set invalid")
    for field in ("dynamic_profile_allowed", "network_required", "side_effects_allowed"):
        require(candidate.get(field) is False, f"candidate boundary expanded: {field}")

    options = gate.get("invocation_options", {})
    require(options.get("local_function", {}).get("recommended") is True, "local function direction missing")
    require(options.get("local_function", {}).get("authorized_for_implementation") is False, "local function implemented through gate")
    for name in ("cli_tool", "mcp_tool", "http_api"):
        require(options.get(name, {}).get("recommended") is False, f"unsupported option recommended: {name}")
        require(options.get(name, {}).get("authorized_for_implementation") is False, f"unsupported option authorized: {name}")

    contract = gate.get("minimum_contract", {})
    require(contract.get("max_input_bytes") == 1048576, "input limit missing")
    for field in (
        "claim_profile_match_required",
        "closed_json_required",
        "duplicate_keys_rejected",
        "prompt_strings_treated_as_inert_data",
        "mandatory_boundary_statement",
        "observation_reference_alignment_required_before_implementation",
    ):
        require(contract.get(field) is True, f"contract guard missing: {field}")
    require(contract.get("evidence_values_reflected") is False, "evidence reflection enabled")

    human = gate.get("human_control_boundary", {})
    require(human.get("supports_human_review") is True, "human review support missing")
    for field in ("approves", "rejects", "authorizes", "deploys", "certifies", "triggers_external_action"):
        require(human.get(field) is False, f"human authority boundary expanded: {field}")

    security = gate.get("security_boundary", {})
    for field in (
        "schema_validation_required",
        "input_size_limit_required",
        "nested_structure_limits_required",
        "prompt_injection_treated_as_data",
        "deterministic_evaluation_required",
        "fail_closed_required",
    ):
        require(security.get(field) is True, f"security requirement missing: {field}")
    for field in ("network_allowed", "subprocess_allowed", "dynamic_import_allowed", "external_execution_allowed", "persistence_default"):
        require(security.get(field) is False, f"security boundary expanded: {field}")

    compatibility = gate.get("compatibility_review", {})
    require(compatibility.get("capability_manifest_observation_references_required") is True, "manifest input fact missing")
    require(compatibility.get("existing_evaluator_consumes_observation_references") is False, "evaluator behavior overclaimed")
    require(compatibility.get("mapping_resolved") is False, "contract mismatch silently resolved")
    require(compatibility.get("resolution_required_before_implementation") is True, "resolution gate missing")

    authorization = gate.get("authorization", {})
    require(authorization and all(value is False for value in authorization.values()), "authorization boundary promoted")
    truth = gate.get("truth_boundary", {})
    require(truth and all(value is False for value in truth.values()), "truth boundary promoted")
    require(gate.get("recommended_next_pr") == "Implement SAEE Local Tool Capability Prototype v0.1", "next PR invalid")
    return copy.deepcopy(gate)


def expect_invalid(gate: dict[str, Any], label: str) -> None:
    try:
        validate_gate(gate)
    except ToolCapabilityGateSmokeError:
        return
    raise ToolCapabilityGateSmokeError(f"invalid gate accepted: {label}")


def main() -> None:
    for path in (GATE_PATH, REVIEW_PATH, DISCOVERY_PATH, CURRENT_MANIFEST_PATH):
        require(path.is_file(), f"missing required file: {path}")
    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib"}
    require(not imported_roots(Path(__file__)).intersection(forbidden_imports), "network or subprocess capability imported")
    require(not forbidden_execution_calls(Path(__file__)), "dynamic or external execution present")

    review = REVIEW_PATH.read_text(encoding="utf-8")
    discovery = DISCOVERY_PATH.read_text(encoding="utf-8")
    for marker in (
        "Capability Gate != Tool Implementation",
        "Invocation Design != Agent Deployment",
        "Tool Invocation != Human Authorization",
        "implementation_authorized=false",
        "mcp_authorized=false",
        "api_authorized=false",
    ):
        require(marker in review, f"review marker missing: {marker}")
    for marker in (
        "Future callable capability under review",
        "tool_capability_recommended=true",
        "phase4_0_gate_snapshot_implementation_authorized=false",
        "local_tool_prototype_implemented=true",
        "public_tool_available=false",
    ):
        require(marker in discovery, f"discovery gate marker missing: {marker}")

    current_manifest = read_json(CURRENT_MANIFEST_PATH)
    current_tool = current_manifest.get("local_tool_prototype", {})
    require(current_tool.get("status") == "implemented_local_offline_research_prototype", "current local prototype status missing")
    require(current_tool.get("public_tool_available") is False, "current local prototype promoted to public tool")

    gate = read_json(GATE_PATH)
    canonical = validate_gate(gate)
    invalid_cases: list[tuple[dict[str, Any], str]] = []
    mutation = copy.deepcopy(gate); mutation["implementation_authorized"] = True; invalid_cases.append((mutation, "implementation authorization"))
    mutation = copy.deepcopy(gate); mutation["invocation_options"]["mcp_tool"]["recommended"] = True; invalid_cases.append((mutation, "MCP recommendation"))
    mutation = copy.deepcopy(gate); mutation["mcp_authorized"] = True; invalid_cases.append((mutation, "top-level MCP authorization"))
    mutation = copy.deepcopy(gate); mutation["api_authorized"] = True; invalid_cases.append((mutation, "top-level API authorization"))
    mutation = copy.deepcopy(gate); mutation["production_ready"] = True; invalid_cases.append((mutation, "top-level production claim"))
    mutation = copy.deepcopy(gate); mutation["truth_boundary"]["tool_available"] = True; invalid_cases.append((mutation, "tool availability claim"))
    mutation = copy.deepcopy(gate); mutation["human_control_boundary"]["authorizes"] = True; invalid_cases.append((mutation, "authority expansion"))
    mutation = copy.deepcopy(gate); mutation["compatibility_review"]["mapping_resolved"] = True; invalid_cases.append((mutation, "silent compatibility resolution"))
    for mutation, label in invalid_cases:
        expect_invalid(mutation, label)

    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_gate(read_json(GATE_PATH))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "gate validation non-deterministic")

    print("SAEE_TOOL_CAPABILITY_GATE_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=5/5")
    print("tool_capability_recommended=true")
    print("implementation_authorized=false")
    print("mcp_authorized=false")
    print("api_authorized=false")
    print("tool_available=false")
    print("gate_record_historical=true")
    print("current_local_tool_prototype_implemented=true")
    print("public_tool_available=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (ToolCapabilityGateSmokeError, json.JSONDecodeError) as exc:
        print(f"SAEE_TOOL_CAPABILITY_GATE_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
