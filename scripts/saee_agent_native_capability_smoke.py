#!/usr/bin/env python3
"""Offline deterministic validation for the SAEE Agent-Native Capability Manifest v0.1."""

from __future__ import annotations

import ast
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "agent-interface/capabilities/saee-capability-manifest.v0.1.json"
BOUNDARY_PATH = ROOT / "docs/architecture/SAEE_AGENT_NATIVE_CAPABILITY_BOUNDARY.md"
USAGE_GUIDE_PATH = ROOT / "docs/architecture/SAEE_AGENT_USAGE_GUIDE.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_AGENT_NATIVE_CAPABILITY_MANIFEST_RECOMMENDATION_GATE.md"

ROOT_KEYS = {
    "saee_agent_native_capability_manifest_v0_1",
    "capability_version",
    "capability_id",
    "name",
    "category",
    "stage",
    "identity",
    "description",
    "should_use",
    "should_not_use",
    "input_contract",
    "output_contract",
    "composition_model",
    "existing_local_evaluation",
    "local_tool_prototype",
    "invocation_evaluation",
    "external_discovery_tested",
    "external_discovery_test",
    "capability_registry_specification",
    "discovery",
    "truth_boundary",
    "recommended_next_pr",
}

REQUIRED_INPUTS = {"observation_references", "evidence_object", "accountability_claim", "evaluation_profile"}
REQUIRED_OUTPUTS = {"claim_assessment", "evidence_sufficiency_status", "missing_requirements", "reason_codes", "limitations", "boundary_statement"}
REQUIRED_NON_USE_RULES = {
    "NO_REAL_TIME_AUTHORIZATION_ENFORCEMENT",
    "NO_MALWARE_DETECTION",
    "NO_LEGAL_OR_COMPLIANCE_CERTIFICATION",
    "NO_DEPLOYMENT_APPROVAL",
    "NO_RUNTIME_SAFETY_BLOCKING",
}
REQUIRED_REPLACEMENTS = {"OBSERVABILITY", "AUTHORIZATION_SYSTEM", "POLICY_ENGINE", "SECURITY_MONITORING"}
TRUTH_FIELDS = {
    "capability_behavior_independently_validated_by_manifest",
    "external_agent_discovery_validated",
    "market_adoption_established",
    "automated_recommendation_implemented",
    "authorization_enforcement_implemented",
    "security_certification_provided",
    "legal_determination_provided",
    "deployment_approval_provided",
    "mcp_added_by_manifest",
    "api_added_by_manifest",
    "production_ready",
}

FORBIDDEN_AFFIRMATIVE_PATTERNS = (
    re.compile(r"\bSAEE\s+(?:guarantees?|certifies?|approves?|enforces?)\s+(?:safety|security|compliance|authorization|deployment)", re.IGNORECASE),
    re.compile(r"\bSAEE\s+(?:is|has been)\s+(?:safe|compliant|certified|approved|production[- ]ready)\b", re.IGNORECASE),
    re.compile(r"SAEE(?:保证|认证|批准|执行)(?:安全|合规|授权|部署)", re.IGNORECASE),
)


class CapabilityManifestSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise CapabilityManifestSmokeError(detail)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    require(isinstance(value, dict), f"JSON root must be object: {path}")
    return value


def iter_text(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_text(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_text(child)


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


def local_ref_exists(ref: str) -> bool:
    if "#" in ref:
        ref = ref.split("#", 1)[0]
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.exists()


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    require(set(manifest) == ROOT_KEYS, "unexpected or missing root field")
    require(manifest["saee_agent_native_capability_manifest_v0_1"] is True, "manifest marker missing")
    require(manifest["capability_version"] == "0.1", "capability version invalid")
    require(manifest["capability_id"] == "saee-evidence-adequacy", "capability id invalid")
    require(manifest["name"] == "SAEE Evidence Adequacy Layer", "capability name invalid")
    require(manifest["category"] == "agent accountability evidence evaluation", "category invalid")
    require(manifest["stage"] == "research_prototype", "stage overclaimed")

    identity = manifest["identity"]
    require(identity["engineering_core"] == "Digital Biosphere Evolution Engine", "engineering core reframed")
    require(identity["evidence_subsystem_is_project_core"] is False, "evidence subsystem promoted to project core")
    description = manifest["description"]
    require(description["capability_description_is_capability_validation"] is False, "description promoted to proof")

    for text in iter_text({"description": description, "should_use": manifest["should_use"]}):
        for pattern in FORBIDDEN_AFFIRMATIVE_PATTERNS:
            require(pattern.search(text) is None, f"forbidden affirmative claim: {text}")

    should_use = manifest["should_use"]
    require(isinstance(should_use, list) and len(should_use) >= 3, "SHOULD_USE coverage missing")
    require(all(set(item) == {"rule_id", "intent", "required_conditions", "expected_outputs"} for item in should_use), "SHOULD_USE shape invalid")
    require(len({item["rule_id"] for item in should_use}) == len(should_use), "duplicate SHOULD_USE rule")

    should_not_use = manifest["should_not_use"]
    require(isinstance(should_not_use, list) and len(should_not_use) >= 5, "SHOULD_NOT_USE coverage missing")
    require({item["rule_id"] for item in should_not_use} == REQUIRED_NON_USE_RULES, "SHOULD_NOT_USE rules incomplete")
    require(all(set(item) == {"rule_id", "request", "reason", "use_instead"} for item in should_not_use), "SHOULD_NOT_USE shape invalid")

    input_contract = manifest["input_contract"]
    inputs = input_contract["inputs"]
    require({item["name"] for item in inputs} == REQUIRED_INPUTS, "input contract incomplete")
    required_by_name = {item["name"]: item.get("required") for item in inputs}
    require(required_by_name["observation_references"] is False, "observation reference boundary invalid")
    require(all(required_by_name[name] is True for name in REQUIRED_INPUTS - {"observation_references"}), "required tool input weakened")
    require(set(input_contract["forbidden_input_classes"]) == {"UNKNOWN_EXECUTABLE_CODE", "UNAPPROVED_CUSTOMER_DATA", "CREDENTIALS_OR_SECRETS", "ARBITRARY_EXTERNAL_URL", "DYNAMIC_PROFILE_CODE"}, "forbidden input classes incomplete")
    for item in inputs:
        for ref in item.get("example_refs", []):
            require(local_ref_exists(ref), f"input example missing: {ref}")
        if "profile_registry_ref" in item:
            require(local_ref_exists(item["profile_registry_ref"]), "profile registry missing")

    output_contract = manifest["output_contract"]
    require({item["name"] for item in output_contract["outputs"]} == REQUIRED_OUTPUTS, "output contract incomplete")
    require(local_ref_exists(output_contract["existing_cli_result_ref"]), "CLI result documentation missing")
    require(local_ref_exists(output_contract["human_readable_projection_ref"]), "human-readable projection missing")

    composition = manifest["composition_model"]
    require(composition["flow"] == ["OBSERVATION_LAYER", "EVIDENCE_LAYER", "GOVERNANCE_LAYER"], "composition flow invalid")
    require({item["layer"] for item in composition["layers"]} == set(composition["flow"]), "composition layer details incomplete")
    require(set(composition["does_not_replace"]) == REQUIRED_REPLACEMENTS, "replacement boundary incomplete")
    require(composition["automatic_governance_decision"] is False, "automatic governance enabled")

    local = manifest["existing_local_evaluation"]
    require(local["implemented_before_manifest"] is True, "existing capability provenance missing")
    for field in ("network_required", "server_required", "candidate_code_executed", "manifest_adds_tool_capability", "manifest_adds_mcp", "manifest_adds_api"):
        require(local[field] is False, f"manifest behavior expanded: {field}")
    require(local["success_exit_code"] == 0 and local["failure_exit_code"] == 2, "exit contract invalid")

    tool = manifest["local_tool_prototype"]
    require(tool["status"] == "implemented_local_offline_research_prototype", "local tool status invalid")
    require(tool["public_tool_available"] is False, "local tool promoted to public availability")
    require(tool["observation_references_required"] is False, "observation references made mandatory")
    require(tool["observation_not_used_as_evidence"] is True, "observation promoted to evidence")
    for field in (
        "network_required",
        "persistence_enabled",
        "mcp_available",
        "api_available",
        "authorization_performed",
        "deployment_authorized",
        "production_ready",
    ):
        require(tool[field] is False, f"local tool boundary expanded: {field}")
    for field in ("request_schema", "output_schema", "adapter", "guard", "documentation", "examples"):
        require(local_ref_exists(tool[field]), f"local tool reference missing: {field}")

    invocation = manifest["invocation_evaluation"]
    require(invocation["status"] == "available_as_local_prototype", "invocation evaluation status invalid")
    require(invocation["caller_cases"] == 4 and invocation["valid_cases"] == 1 and invocation["invalid_cases"] == 3, "invocation case counts invalid")
    require(invocation["all_expected_outcomes_matched"] is True, "invocation outcomes incomplete")
    require(invocation["synthetic_callers_only"] is True, "synthetic caller boundary missing")
    for field in (
        "external_agents_tested",
        "agent_intelligence_measured",
        "adoption_validated",
        "public_tool_available",
        "mcp_used",
        "api_used",
        "network_accessed",
        "production_ready",
    ):
        require(invocation[field] is False, f"invocation boundary expanded: {field}")
    for field in ("scenario_schema", "synthetic_callers", "evaluator", "machine_result", "documentation"):
        require(local_ref_exists(invocation[field]), f"invocation reference missing: {field}")

    require(manifest["external_discovery_tested"] is True, "external discovery test status missing")
    discovery_test = manifest["external_discovery_test"]
    require(discovery_test["status"] == "implemented_local_synthetic_public_snapshot_evaluation", "external discovery status invalid")
    require(discovery_test["caller_cases"] == 4 and discovery_test["valid_cases"] == 1 and discovery_test["invalid_cases"] == 3, "external discovery counts invalid")
    require(discovery_test["all_expected_outcomes_matched"] is True, "external discovery outcomes incomplete")
    require(discovery_test["synthetic_callers_only"] is True, "external discovery synthetic boundary missing")
    require(discovery_test["checked_in_public_snapshot_used"] is True, "public snapshot provenance missing")
    require(discovery_test["live_snapshot_hash_match_confirmed"] is True, "live snapshot match missing")
    require(discovery_test["known_public_surface_gap_count"] == 3, "public surface gaps hidden")
    for field in (
        "external_agents_tested",
        "external_agents_validated",
        "adoption_validated",
        "public_agent_recommendation_validated",
        "marketplace_ready",
        "public_tool_available",
        "offline_evaluation_network_accessed",
        "production_ready",
    ):
        require(discovery_test[field] is False, f"external discovery boundary expanded: {field}")
    for field in ("scenario_schema", "synthetic_callers", "evaluator", "machine_result", "documentation"):
        require(local_ref_exists(discovery_test[field]), f"external discovery reference missing: {field}")

    registry = manifest["capability_registry_specification"]
    require(registry["status"] == "implemented_local_machine_readable_specification", "registry specification status invalid")
    require(registry["registry_specification_version"] == "0.1", "registry specification version invalid")
    require(registry["registry_capability_id"] == "saee.evidence-adequacy", "registry capability id invalid")
    require(registry["manifest_capability_id_alias"] == manifest["capability_id"], "registry alias mismatch")
    require(registry["capability_version"] == manifest["capability_version"], "registry capability version mismatch")
    require(registry["lifecycle_state"] == "LOCAL_PROTOTYPE", "registry lifecycle overclaimed")
    require(registry["registry_entry_available_local"] is True, "local registry entry missing")
    require(registry["known_public_surface_gap_count"] == 3, "registry migration gaps hidden")
    for field in (
        "public_registry_available",
        "marketplace_available",
        "public_tool_available",
        "external_validation_completed",
        "adoption_validated",
        "production_ready",
        "historical_records_rewritten",
        "public_metadata_migrated",
    ):
        require(registry[field] is False, f"registry boundary expanded: {field}")
    for field in ("registry_schema", "capability_card", "validator", "documentation", "migration_notes"):
        require(local_ref_exists(registry[field]), f"registry reference missing: {field}")

    for ref_key, ref in manifest["discovery"].items():
        if ref_key == "validation_command":
            continue
        require(local_ref_exists(ref), f"discovery reference missing: {ref_key}={ref}")

    truth = manifest["truth_boundary"]
    require(set(truth) == TRUTH_FIELDS, "truth boundary shape invalid")
    require(all(value is False for value in truth.values()), "truth boundary promoted")
    require(manifest["recommended_next_pr"] == "Controlled Agent-Native integration based on validated SAEE plus Observability composition", "next action invalid")
    return copy.deepcopy(manifest)


def expect_invalid(manifest: dict[str, Any], label: str) -> None:
    try:
        validate_manifest(manifest)
    except CapabilityManifestSmokeError:
        return
    raise CapabilityManifestSmokeError(f"invalid manifest accepted: {label}")


def main() -> None:
    for path in (MANIFEST_PATH, BOUNDARY_PATH, USAGE_GUIDE_PATH, GATE_PATH):
        require(path.is_file(), f"missing required file: {path}")

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib"}
    require(not imported_roots(Path(__file__)).intersection(forbidden_imports), "network or subprocess capability imported")
    require(not forbidden_execution_calls(Path(__file__)), "dynamic or external execution present")

    boundary_text = BOUNDARY_PATH.read_text(encoding="utf-8")
    guide_text = USAGE_GUIDE_PATH.read_text(encoding="utf-8")
    require(
        "SAEE provides evidence adequacy evaluation capability. It does not provide authorization enforcement, security certification, or legal determination."
        in boundary_text,
        "English boundary missing",
    )
    require(
        "SAEE 提供证据充分性评估能力，不提供授权执行、安全认证或法律判断能力。" in boundary_text,
        "Chinese boundary missing",
    )
    for marker in (
        "Do I need to evaluate evidence sufficiency",
        "Do not use SAEE.",
        "Do I have an evidence object, a defined accountability claim",
        "SAEE cannot evaluate.",
        "SAEE may evaluate",
        "Observation != Evidence",
    ):
        require(marker in guide_text, f"usage decision marker missing: {marker}")

    manifest = read_json(MANIFEST_PATH)
    canonical = validate_manifest(manifest)
    invalid_cases: list[tuple[dict[str, Any], str]] = []
    mutation = copy.deepcopy(manifest); mutation["stage"] = "production"; invalid_cases.append((mutation, "production stage"))
    mutation = copy.deepcopy(manifest); mutation["should_use"] = []; invalid_cases.append((mutation, "missing SHOULD_USE"))
    mutation = copy.deepcopy(manifest); mutation["should_not_use"] = []; invalid_cases.append((mutation, "missing SHOULD_NOT_USE"))
    mutation = copy.deepcopy(manifest); mutation["input_contract"]["inputs"][0]["required"] = True; invalid_cases.append((mutation, "observation reference promoted"))
    mutation = copy.deepcopy(manifest); mutation["input_contract"]["inputs"][1]["required"] = False; invalid_cases.append((mutation, "required input weakened"))
    mutation = copy.deepcopy(manifest); mutation["description"]["english"] = "SAEE guarantees safety."; invalid_cases.append((mutation, "safety guarantee"))
    mutation = copy.deepcopy(manifest); mutation["composition_model"]["automatic_governance_decision"] = True; invalid_cases.append((mutation, "automatic governance"))
    mutation = copy.deepcopy(manifest); mutation["existing_local_evaluation"]["manifest_adds_mcp"] = True; invalid_cases.append((mutation, "MCP expansion"))
    mutation = copy.deepcopy(manifest); mutation["local_tool_prototype"]["mcp_available"] = True; invalid_cases.append((mutation, "local tool MCP expansion"))
    mutation = copy.deepcopy(manifest); mutation["local_tool_prototype"]["public_tool_available"] = True; invalid_cases.append((mutation, "public availability overclaim"))
    mutation = copy.deepcopy(manifest); mutation["invocation_evaluation"]["external_agents_tested"] = True; invalid_cases.append((mutation, "external Agent overclaim"))
    mutation = copy.deepcopy(manifest); mutation["invocation_evaluation"]["public_tool_available"] = True; invalid_cases.append((mutation, "invocation public Tool overclaim"))
    mutation = copy.deepcopy(manifest); mutation["external_discovery_tested"] = False; invalid_cases.append((mutation, "external discovery status removed"))
    mutation = copy.deepcopy(manifest); mutation["external_discovery_test"]["external_agents_validated"] = True; invalid_cases.append((mutation, "external Agent validation overclaim"))
    mutation = copy.deepcopy(manifest); mutation["external_discovery_test"]["marketplace_ready"] = True; invalid_cases.append((mutation, "marketplace overclaim"))
    mutation = copy.deepcopy(manifest); mutation["capability_registry_specification"]["public_registry_available"] = True; invalid_cases.append((mutation, "public registry overclaim"))
    mutation = copy.deepcopy(manifest); mutation["capability_registry_specification"]["lifecycle_state"] = "PRODUCTION_CAPABILITY"; invalid_cases.append((mutation, "registry lifecycle overclaim"))
    mutation = copy.deepcopy(manifest); mutation["capability_registry_specification"]["adoption_validated"] = True; invalid_cases.append((mutation, "registry adoption overclaim"))
    mutation = copy.deepcopy(manifest); mutation["truth_boundary"]["production_ready"] = True; invalid_cases.append((mutation, "production claim"))
    for mutation, label in invalid_cases:
        expect_invalid(mutation, label)

    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_manifest(read_json(MANIFEST_PATH))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "manifest validation non-deterministic")

    print("SAEE_AGENT_NATIVE_CAPABILITY_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=5/5")
    print(f"should_use_rules={len(manifest['should_use'])}/{len(manifest['should_use'])}")
    print(f"should_not_use_rules={len(manifest['should_not_use'])}/{len(manifest['should_not_use'])}")
    print("input_contracts=4/4")
    print("output_contracts=6/6")
    print("composition_layers=3/3")
    print("forbidden_claims_rejected=1/1")
    print("manifest_adds_mcp=false")
    print("manifest_adds_api=false")
    print("manifest_adds_tool_capability=false")
    print("local_tool_prototype_implemented=true")
    print("public_tool_available=false")
    print("invocation_evaluation_available_as_local_prototype=true")
    print("external_agents_tested=false")
    print("external_discovery_tested=true")
    print("external_agents_validated=false")
    print("marketplace_ready=false")
    print("capability_registry_specification_available=true")
    print("registry_lifecycle_state=LOCAL_PROTOTYPE")
    print("public_registry_available=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (CapabilityManifestSmokeError, json.JSONDecodeError) as exc:
        print(f"SAEE_AGENT_NATIVE_CAPABILITY_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
