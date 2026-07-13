#!/usr/bin/env python3
"""Offline smoke test for SAEE MCP Capability Prototype Design v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.mcp_capability_design_validator import (  # noqa: E402
    MCP_DESIGN_BOUNDARY_INVALID,
    MCP_DESIGN_FIELD_MAPPING_INVALID,
    MCP_DESIGN_IMPLEMENTATION_STATUS_INVALID,
    MCP_DESIGN_PRODUCTION_CLAIM_FORBIDDEN,
    MCP_DESIGN_REFERENCE_MISSING,
    MCP_DESIGN_SERVER_AVAILABILITY_FORBIDDEN,
    MCP_DESIGN_TOOL_NAME_INVALID,
    validate_mcp_capability_design,
)


SCHEMA_PATH = ROOT / "agent-interface/mcp/saee-mcp-capability-mapping.schema.v0.1.json"
EXAMPLE_PATH = ROOT / "agent-interface/mcp/examples/saee-evaluate-evidence-mcp-tool-design.v0.1.json"
SERVICE_PATH = ROOT / "saee_backend/services/mcp_capability_design_validator.py"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _expect_invalid(value: dict, reason: str) -> None:
    result = validate_mcp_capability_design(value)
    assert result["design_valid"] is False, reason
    assert result["reason_codes"] == [reason], result


def _assert_no_forbidden_runtime_imports() -> None:
    tree = ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))
    forbidden = {"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & forbidden), f"forbidden runtime import: {sorted(imported & forbidden)}"


def main() -> int:
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    value = _load(EXAMPLE_PATH)
    schema_errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: list(error.absolute_path))
    assert not schema_errors, schema_errors[0].message if schema_errors else ""

    valid = validate_mcp_capability_design(value)
    assert valid["design_valid"] is True
    assert valid["reason_codes"] == []
    assert valid["resolved_reference_count"] == 4

    fake_server = copy.deepcopy(value)
    fake_server["server_available"] = True
    _expect_invalid(fake_server, MCP_DESIGN_SERVER_AVAILABILITY_FORBIDDEN)

    fake_endpoint = copy.deepcopy(value)
    fake_endpoint["public_endpoint_available"] = True
    _expect_invalid(fake_endpoint, MCP_DESIGN_SERVER_AVAILABILITY_FORBIDDEN)

    fake_production = copy.deepcopy(value)
    fake_production["production_ready"] = True
    _expect_invalid(fake_production, MCP_DESIGN_PRODUCTION_CLAIM_FORBIDDEN)

    implemented = copy.deepcopy(value)
    implemented["implementation_status"] = "implemented"
    _expect_invalid(implemented, MCP_DESIGN_IMPLEMENTATION_STATUS_INVALID)

    wrong_tool = copy.deepcopy(value)
    wrong_tool["mcp_tool_name"] = "approve_deployment"
    _expect_invalid(wrong_tool, MCP_DESIGN_TOOL_NAME_INVALID)

    broken_contract = copy.deepcopy(value)
    broken_contract["input_mapping"]["schema_ref"] = "agent-interface/capabilities/missing.v0.1.schema.json"
    _expect_invalid(broken_contract, MCP_DESIGN_REFERENCE_MISSING)

    broken_object = copy.deepcopy(value)
    broken_object["capability_object_ref"] = "agent-interface/registry/objects/missing.v0.1.json"
    _expect_invalid(broken_object, MCP_DESIGN_REFERENCE_MISSING)

    authorization_claim = copy.deepcopy(value)
    authorization_claim["boundaries"]["authorization_provided"] = True
    _expect_invalid(authorization_claim, MCP_DESIGN_BOUNDARY_INVALID)

    certification_claim = copy.deepcopy(value)
    certification_claim["boundaries"]["certification_provided"] = True
    _expect_invalid(certification_claim, MCP_DESIGN_BOUNDARY_INVALID)

    mismatched_field = copy.deepcopy(value)
    mismatched_field["input_mapping"]["field_mappings"][0]["saee_field"] = "accountability_claim"
    _expect_invalid(mismatched_field, MCP_DESIGN_FIELD_MAPPING_INVALID)

    serialized = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        rerun = validate_mcp_capability_design(value)
        assert json.dumps(rerun, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == serialized

    _assert_no_forbidden_runtime_imports()
    assert all(valid[field] is False for field in (
        "server_available",
        "public_endpoint_available",
        "external_agents_connected",
        "mcp_compatibility_completed",
        "network_accessed",
        "subprocess_started",
        "external_execution",
        "production_ready",
    ))

    print("SAEE_MCP_CAPABILITY_DESIGN_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=10/10")
    print("deterministic_runs=5/5")
    print("resolved_references=4/4")
    print("capability_object_mapping_valid=true")
    print("input_output_mapping_valid=true")
    print("boundary_claims_rejected=true")
    print("implementation_status=design_only")
    print("server_available=false")
    print("public_endpoint_available=false")
    print("external_agents_connected=false")
    print("mcp_compatibility_completed=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
