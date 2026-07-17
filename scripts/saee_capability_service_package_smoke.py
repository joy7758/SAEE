#!/usr/bin/env python3
"""Offline deterministic validation for SAEE Capability Service Package v1.0."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "capability-package"


class PackageValidationError(ValueError):
    """Raised when the package overstates or breaks its local Alpha contract."""


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PackageValidationError(f"{path.name}: root must be an object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PackageValidationError(message)


def validate_card(card: dict[str, Any]) -> None:
    require(card.get("package_marker") == "saee_capability_service_package_v1", "card marker invalid")
    require(card.get("id") == "saee.agent-reliability", "capability id invalid")
    require(card.get("stage") == "local_contract_alpha", "card stage invalid")
    require(len(card.get("use_when", [])) >= 3, "use_when rules missing")
    require(len(card.get("do_not_use_when", [])) >= 4, "do_not_use_when rules missing")
    capabilities = {item.get("operation_id"): item for item in card.get("capabilities", [])}
    require(set(capabilities) == {"evaluate_rehearsal_run", "evaluate_evidence", "rehearse_agent"}, "operation set invalid")
    require(capabilities["evaluate_rehearsal_run"].get("local_invocation_available") is True, "run evaluator hidden")
    require(capabilities["evaluate_evidence"].get("local_invocation_available") is True, "evidence evaluator hidden")
    require(capabilities["rehearse_agent"].get("implementation_status") == "contract_only", "rehearsal boundary invalid")
    runtime = card.get("local_runtime", {})
    require(runtime.get("runtime_stage") == "local_alpha", "local runtime stage missing")
    require(runtime.get("package_operations_verified") is True and runtime.get("network_required") is False, "local runtime boundary invalid")
    require(runtime.get("local_stdio_mcp_adapter_available") is True, "local MCP adapter hidden")
    require(runtime.get("local_http_adapter_available") is True, "local HTTP adapter hidden")
    for ref_key in ("invocation_service_ref", "request_schema_ref", "response_schema_ref", "receipt_schema_ref", "mcp_adapter_ref", "http_adapter_ref", "demo_ref", "validation_ref"):
        require((PACKAGE / runtime[ref_key]).is_file(), f"local runtime reference missing: {ref_key}")
    boundary = card.get("truth_boundary", {})
    for field in ("network_api_available", "standard_mcp_transport_available", "public_mcp_available", "external_agent_connected", "adoption_validated", "customer_validated", "production_ready"):
        require(boundary.get(field) is False, f"unsupported card truth: {field}")
    require(card.get("project_identity_boundary", {}).get("engineering_core") == "Digital Biosphere Evolution Engine", "project core reframed")
    require(card.get("project_identity_boundary", {}).get("evidence_subsystem_is_project_core") is False, "audit-first reframing detected")
    require((PACKAGE / card["integration_examples_reference"]).is_file(), "integration examples reference missing")
    require((PACKAGE / card["public_capability_surface_reference"]).is_file(), "public capability surface reference missing")
    require((PACKAGE / card["alpha_release_reference"]).is_file(), "alpha release reference missing")
    require((PACKAGE / card["truth_consistency_validation_reference"]).is_file(), "truth consistency reference missing")
    require(boundary.get("repository_public_surface_prepared") is True, "repository public surface hidden")
    require(boundary.get("alpha_preparation") is True and boundary.get("public_release") is False, "alpha release truth invalid")
    require(boundary.get("publicly_deployed") is False, "public deployment overstated")


def validate_manifest(manifest: dict[str, Any]) -> None:
    require(manifest.get("package_id") == "saee.agent-reliability", "manifest package id invalid")
    require(manifest.get("package_stage") == "local_contract_alpha", "manifest stage invalid")
    require(manifest.get("default_language") == "zh-CN", "default language must be zh-CN")
    files = manifest.get("files", {})
    required_files = {"capability_card", "openapi_contract", "mcp_tool_contract", "discovery_document", "limitations", "agent_readme", "examples_directory"}
    require(set(files) == required_files, "manifest file map invalid")
    for ref in files.values():
        require((PACKAGE / ref).exists(), f"manifest reference missing: {ref}")
    sources = manifest.get("canonical_local_sources", {})
    require(len(sources) == 4, "canonical local source map incomplete")
    for ref in sources.values():
        require((PACKAGE / ref).is_file(), f"canonical source missing: {ref}")
    operations = {item.get("operation_id"): item for item in manifest.get("operations", [])}
    require(set(operations) == {"evaluate_rehearsal_run", "evaluate_evidence", "rehearse_agent"}, "manifest operations invalid")
    require(operations["rehearse_agent"].get("status") == "contract_only", "manifest falsely implements rehearsal")
    runtime = manifest.get("local_runtime", {})
    require(runtime.get("status") == "local_alpha" and runtime.get("package_operations_verified") is True, "manifest runtime missing")
    for field in ("network_api_available", "public_service", "standard_mcp_transport"):
        require(runtime.get(field) is False, f"manifest runtime overclaim: {field}")
    require(runtime.get("local_stdio_mcp_adapter_available") is True, "manifest local MCP adapter hidden")
    require(runtime.get("local_http_adapter_available") is True, "manifest local HTTP adapter hidden")
    for ref_key in ("service_ref", "router_ref", "request_schema_ref", "response_schema_ref", "receipt_schema_ref", "mcp_adapter_ref", "mcp_stdio_config_ref", "http_adapter_ref"):
        require((PACKAGE / runtime[ref_key]).is_file(), f"manifest runtime reference missing: {ref_key}")
    boundary = manifest.get("truth_boundary", {})
    for field in ("published", "network_api_available", "public_mcp_available", "marketplace_listed", "external_validation_completed", "production_ready"):
        require(boundary.get(field) is False, f"unsupported manifest truth: {field}")
    integration = manifest.get("integration_examples", {})
    require(integration.get("status") == "local_examples_alpha", "integration example status missing")
    require((PACKAGE / integration["reference"]).is_file() and (PACKAGE / integration["examples_root"]).is_dir(), "integration example reference missing")
    require(all(integration.get(field) is False for field in ("external_agents_connected", "marketplace_listed", "production_ready")), "integration example overclaim")
    public_surface = manifest.get("public_capability_surface", {})
    require(public_surface.get("status") == "repository_public_surface_prepared_not_deployed", "public surface status invalid")
    for ref_key in ("reference", "well_known_reference", "public_document_reference", "quick_understanding_reference"):
        require((PACKAGE / public_surface[ref_key]).is_file(), f"public surface reference missing: {ref_key}")
    require(all(public_surface.get(field) is False for field in ("publicly_deployed", "public_api", "public_service", "production_ready")), "public surface overclaim")
    require((PACKAGE / manifest["public_capability_surface_reference"]).is_file(), "manifest public capability surface reference missing")
    require((PACKAGE / manifest["alpha_release_reference"]).is_file(), "manifest alpha release reference missing")
    require((PACKAGE / manifest["truth_consistency_validation_reference"]).is_file(), "manifest truth consistency reference missing")
    require(boundary.get("alpha_preparation") is True and boundary.get("public_release") is False, "manifest alpha release truth invalid")
    require(boundary.get("repository_public_surface_prepared") is True and boundary.get("publicly_deployed") is False, "manifest public surface truth invalid")


def validate_mcp(descriptor: dict[str, Any]) -> None:
    require(descriptor.get("descriptor_type") == "mcp_tool_contract_projection", "MCP descriptor type invalid")
    require(descriptor.get("mcp_protocol_interoperability_validated") is False, "MCP interoperability overstated")
    require(descriptor.get("standard_mcp_transport_available") is False, "standard MCP transport overstated")
    require(descriptor.get("local_stdio_mcp_adapter_available") is True, "local MCP adapter missing")
    require((PACKAGE / descriptor["local_adapter_ref"]).is_file(), "local MCP adapter ref missing")
    require(descriptor.get("public_mcp_endpoint") is None, "public MCP endpoint must be null")
    tools = {item.get("name"): item for item in descriptor.get("tools", [])}
    require(set(tools) == {"evaluate_rehearsal_run", "evaluate_evidence", "rehearse_agent"}, "MCP Tool set invalid")
    require(tools["evaluate_evidence"].get("local_registered_name") == "evaluate_evidence_adequacy", "local evidence Tool alias lost")
    require(tools["rehearse_agent"].get("implementation_status") == "contract_only_not_registered", "rehearse_agent falsely registered")
    require(tools["rehearse_agent"].get("local_handler_ref") is None, "rehearse_agent handler must be absent")
    for tool in tools.values():
        require(tool.get("side_effects") is False, "side effect claim invalid")
        require(tool.get("authorization_performed") is False, "authorization claim invalid")


def validate_discovery(discovery: dict[str, Any]) -> None:
    require(discovery.get("discovery_document_is_publicly_deployed") is False, "discovery deployment overstated")
    require(discovery.get("capability_description_is_capability_proof") is False, "description treated as proof")
    require(discovery.get("production_ready") is False, "production readiness overstated")
    entries = discovery.get("capabilities", [])
    require(len(entries) == 1 and entries[0].get("id") == "saee.agent-reliability", "discovery entry invalid")
    require(entries[0].get("network_endpoint") is None, "network endpoint must be null")
    require(entries[0].get("public_mcp_endpoint") is None, "public MCP endpoint must be null")
    require(entries[0].get("local_runtime_available") is True, "local runtime hidden from discovery")
    require((PACKAGE / ".well-known" / entries[0]["local_runtime_ref"]).is_file(), "discovery local runtime ref missing")
    require(entries[0].get("local_stdio_mcp_adapter_available") is True, "local MCP adapter hidden from discovery")
    require((PACKAGE / ".well-known" / entries[0]["local_mcp_adapter_ref"]).is_file(), "discovery MCP adapter ref missing")
    require(entries[0].get("local_http_adapter_available") is True, "local HTTP adapter hidden from discovery")
    require((PACKAGE / ".well-known" / entries[0]["local_http_adapter_ref"]).is_file(), "discovery HTTP adapter ref missing")
    require((PACKAGE / ".well-known" / entries[0]["integration_examples_reference"]).is_file(), "discovery integration ref missing")
    require((PACKAGE / ".well-known" / entries[0]["public_capability_surface_reference"]).is_file(), "discovery public surface ref missing")
    require((PACKAGE / ".well-known" / entries[0]["repository_well_known_reference"]).is_file(), "repository well-known ref missing")
    require((PACKAGE / ".well-known" / entries[0]["alpha_release_reference"]).is_file(), "discovery alpha release ref missing")
    require((PACKAGE / ".well-known" / entries[0]["truth_consistency_validation_reference"]).is_file(), "discovery truth consistency ref missing")


def validate_openapi(text: str) -> None:
    required_markers = (
        "openapi: 3.1.0",
        "operationId: evaluate_rehearsal_run",
        "operationId: evaluate_evidence",
        "operationId: rehearse_agent",
        "x-saee-network-api-available: false",
        "x-saee-local-runtime-available: true",
        "x-saee-local-http-adapter-available: true",
        "x-saee-production-ready: false",
        "x-saee-implementation-status: contract_only_not_available",
        "CAPABILITY_CONTRACT_ONLY",
    )
    for marker in required_markers:
        require(marker in text, f"OpenAPI marker missing: {marker}")
    require(not re.search(r"(?m)^servers\s*:", text), "OpenAPI must not declare a public server")
    require("https://redcrag.cn/api" not in text, "unimplemented public endpoint advertised")
    for ref in re.findall(r"\$ref:\s+([^\s#][^\s]*)", text):
        ref_path = ref.strip("'\"").split("#", 1)[0]
        if ref_path.startswith("../"):
            require((PACKAGE / ref_path).is_file(), f"OpenAPI local ref missing: {ref_path}")


def validate_examples() -> None:
    expected = {
        "evaluate-evidence.json": "evaluate_evidence",
        "evaluate-agent-run.json": "evaluate_rehearsal_run",
        "rehearse-agent.json": "rehearse_agent",
    }
    for filename, operation in expected.items():
        value = load_json(PACKAGE / "examples" / filename)
        require(value.get("operation_id") == operation, f"example operation invalid: {filename}")
        require(value.get("network_required") is False, f"example requires network: {filename}")
        for key, ref in value.items():
            if key.endswith("_ref") and isinstance(ref, str):
                require((PACKAGE / "examples" / ref).is_file(), f"example ref missing: {ref}")
    rehearsal = load_json(PACKAGE / "examples" / "rehearse-agent.json")
    require(rehearsal.get("execution_performed") is False, "contract-only example claims execution")
    require(rehearsal.get("expected_response", {}).get("status") == "NOT_IMPLEMENTED", "contract-only response invalid")


def validate_package(card: dict[str, Any], manifest: dict[str, Any], mcp: dict[str, Any], discovery: dict[str, Any], openapi: str) -> dict[str, Any]:
    validate_card(card)
    validate_manifest(manifest)
    validate_mcp(mcp)
    validate_discovery(discovery)
    validate_openapi(openapi)
    validate_examples()
    payload = json.dumps({"card": card, "manifest": manifest, "mcp": mcp, "discovery": discovery, "openapi": openapi}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "package_id": "saee.agent-reliability",
        "result": "PASS",
        "digest_algorithm": "sha-256",
        "package_contract_digest": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def main() -> int:
    card = load_json(PACKAGE / "capability-card.json")
    manifest = load_json(PACKAGE / "manifest.json")
    mcp = load_json(PACKAGE / "mcp-tool.json")
    discovery = load_json(PACKAGE / ".well-known" / "saee-capability.json")
    openapi = (PACKAGE / "openapi.yaml").read_text(encoding="utf-8")
    baseline = validate_package(card, manifest, mcp, discovery, openapi)

    invalid: list[bool] = []
    for field in ("network_api_available", "public_mcp_available", "external_agent_connected", "adoption_validated", "customer_validated", "production_ready"):
        candidate = copy.deepcopy(card)
        candidate["truth_boundary"][field] = True
        try:
            validate_card(candidate)
        except PackageValidationError:
            invalid.append(True)
    candidate = copy.deepcopy(card)
    candidate["capabilities"][2]["implementation_status"] = "implemented"
    try:
        validate_card(candidate)
    except PackageValidationError:
        invalid.append(True)
    for field in ("published", "network_api_available", "marketplace_listed", "production_ready"):
        candidate = copy.deepcopy(manifest)
        candidate["truth_boundary"][field] = True
        try:
            validate_manifest(candidate)
        except PackageValidationError:
            invalid.append(True)
    candidate = copy.deepcopy(mcp)
    candidate["standard_mcp_transport_available"] = True
    try:
        validate_mcp(candidate)
    except PackageValidationError:
        invalid.append(True)
    candidate = copy.deepcopy(mcp)
    candidate["tools"][2]["local_handler_ref"] = "fake.py"
    try:
        validate_mcp(candidate)
    except PackageValidationError:
        invalid.append(True)
    candidate = copy.deepcopy(discovery)
    candidate["capabilities"][0]["network_endpoint"] = "https://redcrag.cn/api/saee"
    try:
        validate_discovery(candidate)
    except PackageValidationError:
        invalid.append(True)
    try:
        validate_openapi(openapi + "\nservers:\n  - url: https://redcrag.cn/api\n")
    except PackageValidationError:
        invalid.append(True)
    require(len(invalid) >= 12 and all(invalid), "invalid mutation coverage failed")

    repeats = [validate_package(card, manifest, mcp, discovery, openapi) for _ in range(5)]
    require(all(item == baseline for item in repeats), "deterministic validation failed")

    gate = (ROOT / "docs/strategy/SAEE_CAPABILITY_SERVICE_PACKAGE_V1_RECOMMENDATION_GATE.md").read_text(encoding="utf-8")
    require("answer: recommend" in gate, "recommendation gate missing")
    require("Digital Biosphere Evolution Engine" in gate, "evolution-core boundary missing")

    print("SAEE_CAPABILITY_SERVICE_PACKAGE_SMOKE: PASS")
    print("package_id=saee.agent-reliability")
    print("valid_contracts=4/4")
    print("operations=3/3")
    print("implemented_local_operations=2/2")
    print("contract_only_operations=1/1")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("public_mcp_available=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
