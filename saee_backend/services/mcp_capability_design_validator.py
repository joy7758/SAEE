"""Offline validator for SAEE MCP Capability Prototype Design v0.1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "agent-interface/mcp/saee-mcp-capability-mapping.schema.v0.1.json"
EXPECTED_TOOL_NAME = "evaluate_evidence_adequacy"
EXPECTED_OBJECT_ID = "saee:capability:evidence-adequacy:0.1"
EXPECTED_INPUT_FIELDS = {
    "evidence_object": ("evidence_object", True),
    "accountability_claim": ("accountability_claim", True),
    "evaluation_profile": ("evaluation_profile", True),
    "observation_references": ("observation_references", False),
}
EXPECTED_OUTPUT_FIELDS = {
    "claim_assessment",
    "evidence_sufficiency_status",
    "missing_requirements",
    "reason_codes",
    "limitations",
    "boundary_statement",
}
BOUNDARY_ENGLISH = "SAEE MCP exposure would provide evidence adequacy evaluation capability. It would not provide authorization, deployment approval, or certification."
BOUNDARY_CHINESE = "SAEE 的 MCP 暴露提供证据充分性评估能力，不提供授权、部署批准或认证。"

MCP_DESIGN_INVALID = "MCP_DESIGN_INVALID"
MCP_DESIGN_IMPLEMENTATION_STATUS_INVALID = "MCP_DESIGN_IMPLEMENTATION_STATUS_INVALID"
MCP_DESIGN_SERVER_AVAILABILITY_FORBIDDEN = "MCP_DESIGN_SERVER_AVAILABILITY_FORBIDDEN"
MCP_DESIGN_PRODUCTION_CLAIM_FORBIDDEN = "MCP_DESIGN_PRODUCTION_CLAIM_FORBIDDEN"
MCP_DESIGN_TOOL_NAME_INVALID = "MCP_DESIGN_TOOL_NAME_INVALID"
MCP_DESIGN_BOUNDARY_INVALID = "MCP_DESIGN_BOUNDARY_INVALID"
MCP_DESIGN_SCHEMA_INVALID = "MCP_DESIGN_SCHEMA_INVALID"
MCP_DESIGN_REFERENCE_MISSING = "MCP_DESIGN_REFERENCE_MISSING"
MCP_DESIGN_CAPABILITY_OBJECT_MISMATCH = "MCP_DESIGN_CAPABILITY_OBJECT_MISMATCH"
MCP_DESIGN_CONTRACT_MISMATCH = "MCP_DESIGN_CONTRACT_MISMATCH"
MCP_DESIGN_FIELD_MAPPING_INVALID = "MCP_DESIGN_FIELD_MAPPING_INVALID"


def _result(value: Any, valid: bool, reasons: list[str], resolved_reference_count: int = 0) -> dict[str, Any]:
    return {
        "saee_mcp_capability_design_validation_result_v0_1": True,
        "design_valid": valid,
        "capability_object_id": value.get("capability_object_id", "") if isinstance(value, dict) else "",
        "mcp_tool_name": value.get("mcp_tool_name", "") if isinstance(value, dict) else "",
        "implementation_status": value.get("implementation_status", "") if isinstance(value, dict) else "",
        "reason_codes": reasons,
        "resolved_reference_count": resolved_reference_count,
        "server_available": False,
        "public_endpoint_available": False,
        "external_agents_connected": False,
        "mcp_compatibility_completed": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "production_ready": False,
    }


def _safe_ref(value: dict[str, Any], *path: str) -> str | None:
    current: Any = value
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current if isinstance(current, str) else None


def _reference_exists(ref: str) -> bool:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def _field_mapping_valid(value: dict[str, Any]) -> bool:
    input_mapping = value.get("input_mapping")
    output_mapping = value.get("output_mapping")
    if not isinstance(input_mapping, dict) or not isinstance(output_mapping, dict):
        return False
    field_mappings = input_mapping.get("field_mappings", [])
    if not isinstance(field_mappings, list) or len(field_mappings) != len(EXPECTED_INPUT_FIELDS):
        return False
    observed: dict[str, tuple[Any, Any]] = {}
    for mapping in field_mappings:
        if not isinstance(mapping, dict) or not isinstance(mapping.get("mcp_field"), str):
            return False
        observed[mapping["mcp_field"]] = (mapping.get("saee_field"), mapping.get("required"))
    output_fields = output_mapping.get("response_fields", [])
    return observed == EXPECTED_INPUT_FIELDS and set(output_fields) == EXPECTED_OUTPUT_FIELDS


def _boundary_document_valid(ref: str) -> bool:
    try:
        text = (ROOT / ref).read_text(encoding="utf-8")
    except OSError:
        return False
    return BOUNDARY_ENGLISH in text and BOUNDARY_CHINESE in text


def validate_mcp_capability_design(value: Any) -> dict[str, Any]:
    """Validate one design mapping without starting an MCP runtime."""

    if not isinstance(value, dict):
        return _result(value, False, [MCP_DESIGN_INVALID])
    if value.get("server_available") is not False or value.get("public_endpoint_available") is not False:
        return _result(value, False, [MCP_DESIGN_SERVER_AVAILABILITY_FORBIDDEN])
    if value.get("production_ready") is not False:
        return _result(value, False, [MCP_DESIGN_PRODUCTION_CLAIM_FORBIDDEN])
    if value.get("implementation_status") != "design_only":
        return _result(value, False, [MCP_DESIGN_IMPLEMENTATION_STATUS_INVALID])
    tool_metadata = value.get("tool_metadata")
    if value.get("mcp_tool_name") != EXPECTED_TOOL_NAME or not isinstance(tool_metadata, dict) or tool_metadata.get("name") != EXPECTED_TOOL_NAME:
        return _result(value, False, [MCP_DESIGN_TOOL_NAME_INVALID])

    boundaries = value.get("boundaries")
    if not isinstance(boundaries, dict) or any(
        boundaries.get(field) is not False
        for field in (
            "authorization_provided",
            "deployment_approval_provided",
            "certification_provided",
            "runtime_blocking_provided",
            "legal_judgment_provided",
        )
    ) or boundaries.get("human_authority_required") is not True:
        return _result(value, False, [MCP_DESIGN_BOUNDARY_INVALID])

    refs = [
        _safe_ref(value, "capability_object_ref"),
        _safe_ref(value, "input_mapping", "schema_ref"),
        _safe_ref(value, "output_mapping", "schema_ref"),
        _safe_ref(value, "boundaries", "boundary_contract_ref"),
    ]
    if any(ref is None or not _reference_exists(ref) for ref in refs):
        return _result(value, False, [MCP_DESIGN_REFERENCE_MISSING])

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    schema_errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: list(error.absolute_path))
    if schema_errors:
        return _result(value, False, [MCP_DESIGN_SCHEMA_INVALID])

    capability_object = json.loads((ROOT / refs[0]).read_text(encoding="utf-8"))
    if (
        value["capability_object_id"] != EXPECTED_OBJECT_ID
        or capability_object.get("object_id") != value["capability_object_id"]
        or capability_object.get("identity", {}).get("version") != value["mapping_version"]
        or capability_object.get("lifecycle", {}).get("state") != value["lifecycle_mapping"]["capability_object_state"]
    ):
        return _result(value, False, [MCP_DESIGN_CAPABILITY_OBJECT_MISMATCH])
    if (
        capability_object.get("contracts", {}).get("input", {}).get("schema_ref") != refs[1]
        or capability_object.get("contracts", {}).get("output", {}).get("schema_ref") != refs[2]
        or value["input_mapping"]["schema_version"] != value["mapping_version"]
        or value["output_mapping"]["schema_version"] != value["mapping_version"]
    ):
        return _result(value, False, [MCP_DESIGN_CONTRACT_MISMATCH])
    if not _field_mapping_valid(value):
        return _result(value, False, [MCP_DESIGN_FIELD_MAPPING_INVALID])
    if not _boundary_document_valid(refs[3]):
        return _result(value, False, [MCP_DESIGN_BOUNDARY_INVALID])
    return _result(value, True, [], resolved_reference_count=len(refs))


def validate_mcp_capability_design_json(text: str) -> dict[str, Any]:
    """Parse and validate one design mapping JSON document."""

    try:
        value = json.loads(text)
    except (json.JSONDecodeError, UnicodeError, ValueError):
        return _result({}, False, [MCP_DESIGN_INVALID])
    return validate_mcp_capability_design(value)
