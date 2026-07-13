#!/usr/bin/env python3
"""Offline hostile validation for SAEE Local Tool Capability Prototype v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services import local_evidence_tool
from saee_backend.services.evidence_adequacy import evaluate_evidence_adequacy
from saee_backend.services.local_evidence_tool import BOUNDARY_STATEMENT, evaluate_evidence_tool
from saee_backend.services.local_tool_guard import MAX_INPUT_BYTES


REQUEST_SCHEMA_PATH = ROOT / "agent-interface/capabilities/saee-evaluate-evidence-tool.v0.1.schema.json"
OUTPUT_SCHEMA_PATH = ROOT / "agent-interface/capabilities/saee-evaluate-evidence-output.v0.1.schema.json"
EXAMPLE_ROOT = ROOT / "agent-interface/capabilities/examples"
DOC_PATH = ROOT / "docs/architecture/SAEE_LOCAL_TOOL_CAPABILITY.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_LOCAL_TOOL_CAPABILITY_RECOMMENDATION_GATE.md"
DEMO_PATH = ROOT / "scripts/saee_local_tool_demo.py"

EXAMPLES = {
    "supported": EXAMPLE_ROOT / "valid_supported_request.json",
    "insufficient": EXAMPLE_ROOT / "valid_insufficient_request.json",
    "unknown_claim": EXAMPLE_ROOT / "invalid_unknown_claim.json",
    "oversized_recipe": EXAMPLE_ROOT / "invalid_oversized_request.json",
    "missing_profile": EXAMPLE_ROOT / "invalid_missing_profile.json",
}

FORBIDDEN_OUTPUT_WORDS = {"APPROVED", "CERTIFIED", "SAFE", "COMPLIANT"}


class LocalToolSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise LocalToolSmokeError(detail)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root must be object: {path}")
    return value


def validate_schema(instance: Any, schema_path: Path) -> None:
    schema = read_json(schema_path)
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda error: list(error.absolute_path))
    require(not errors, f"schema rejection at {schema_path.name}: {errors[0].message if errors else ''}")


def schema_rejects(instance: Any, schema_path: Path) -> None:
    schema = read_json(schema_path)
    require(bool(list(Draft202012Validator(schema).iter_errors(instance))), f"invalid fixture accepted: {schema_path.name}")


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__", "open"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {
            "system",
            "popen",
            "run",
            "Popen",
            "write_text",
            "write_bytes",
            "open",
        }:
            found.add(node.func.attr)
    return found


def expect_rejected(request: Any, code: str) -> dict[str, Any]:
    result = evaluate_evidence_tool(request)
    require(result["tool_result"] == "REJECTED_INPUT", f"invalid request accepted: {code}")
    require(result["claim_assessment"] == "UNKNOWN", f"rejection assessment promoted: {code}")
    require(result["evidence_sufficiency_status"] == "UNKNOWN", f"rejection sufficiency promoted: {code}")
    require(result["reason_codes"] == [code], f"unstable rejection code: expected={code} actual={result['reason_codes']}")
    validate_schema(result, OUTPUT_SCHEMA_PATH)
    return result


def deep_request(base: dict[str, Any]) -> dict[str, Any]:
    request = copy.deepcopy(base)
    nested: dict[str, Any] = {"leaf": "synthetic"}
    for _ in range(40):
        nested = {"nested": nested}
    request["evidence_object"] = nested
    return request


def main() -> None:
    for path in (REQUEST_SCHEMA_PATH, OUTPUT_SCHEMA_PATH, DOC_PATH, GATE_PATH, DEMO_PATH, *EXAMPLES.values()):
        require(path.is_file(), f"missing required file: {path}")

    implementation_paths = (
        ROOT / "saee_backend/services/local_tool_guard.py",
        ROOT / "saee_backend/services/local_evidence_tool.py",
        DEMO_PATH,
        Path(__file__),
    )
    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "sqlite3", "smtplib"}
    for path in implementation_paths:
        require(not imported_roots(path).intersection(forbidden_imports), f"forbidden import in {path.name}")
        require(not forbidden_calls(path), f"external execution or persistence call in {path.name}: {forbidden_calls(path)}")

    document = DOC_PATH.read_text(encoding="utf-8")
    require(
        "SAEE tool capability evaluates evidence adequacy. It does not authorize actions or certify system safety." in document,
        "English boundary missing",
    )
    require("SAEE 工具能力评估证据充分性，不执行授权，也不认证系统安全。" in document, "Chinese boundary missing")

    supported_request = read_json(EXAMPLES["supported"])
    insufficient_request = read_json(EXAMPLES["insufficient"])
    validate_schema(supported_request, REQUEST_SCHEMA_PATH)
    validate_schema(insufficient_request, REQUEST_SCHEMA_PATH)
    schema_rejects(read_json(EXAMPLES["unknown_claim"]), REQUEST_SCHEMA_PATH)
    schema_rejects(read_json(EXAMPLES["missing_profile"]), REQUEST_SCHEMA_PATH)

    supported = evaluate_evidence_tool(supported_request)
    insufficient = evaluate_evidence_tool(insufficient_request)
    require(supported["tool_result"] == "SUCCESS", "supported request did not execute")
    require(supported["claim_assessment"] == "SUPPORTED", "supported assessment invalid")
    require(supported["evidence_sufficiency_status"] == "SUFFICIENT", "supported sufficiency invalid")
    require(insufficient["tool_result"] == "SUCCESS", "insufficient request was rejected instead of evaluated")
    require(insufficient["claim_assessment"] == "INSUFFICIENT_EVIDENCE", "insufficient assessment invalid")
    require(insufficient["evidence_sufficiency_status"] == "INSUFFICIENT", "insufficient status invalid")
    require(insufficient["missing_requirements"], "insufficient result missing evidence gaps")
    for result in (supported, insufficient):
        validate_schema(result, OUTPUT_SCHEMA_PATH)
        require(result["boundary_statement"] == BOUNDARY_STATEMENT, "boundary statement drifted")
        require(result["observation_not_used_as_evidence"] is True, "observation promoted to evidence")
        require(all(value is False for key, value in result["truth_boundary"].items() if key != "local_tool_prototype"), "truth boundary promoted")
        require(not FORBIDDEN_OUTPUT_WORDS.intersection({result["claim_assessment"], result["evidence_sufficiency_status"]}), "forbidden output label")

    direct_supported = evaluate_evidence_adequacy(
        supported_request["accountability_claim"],
        supported_request["evidence_object"],
    )
    direct_insufficient = evaluate_evidence_adequacy(
        insufficient_request["accountability_claim"],
        insufficient_request["evidence_object"],
    )
    require(direct_supported["result"] == "PASS" and supported["reason_codes"] == direct_supported["reason_codes"], "supported evaluator mapping drift")
    require(direct_insufficient["result"] == "FAIL", "insufficient evaluator baseline drift")
    require(insufficient["reason_codes"] == direct_insufficient["reason_codes"], "reason codes not preserved from evaluator")
    require(insufficient["missing_requirements"] == sorted(set(direct_insufficient["missing_requirements"])), "missing requirements not preserved")

    calls: list[tuple[str, Any]] = []
    original_evaluator = local_evidence_tool.evaluate_evidence_adequacy

    def evaluator_probe(claim: str, package: Any) -> dict[str, Any]:
        calls.append((claim, package))
        return direct_supported

    local_evidence_tool.evaluate_evidence_adequacy = evaluator_probe
    try:
        probed = local_evidence_tool.evaluate_evidence_tool(supported_request)
    finally:
        local_evidence_tool.evaluate_evidence_adequacy = original_evaluator
    require(len(calls) == 1, "canonical evaluator not called exactly once")
    require(calls[0][0] == "AUTHORIZED_AGENT_ACTION", "claim not passed to canonical evaluator")
    require(calls[0][1] == supported_request["evidence_object"], "evidence package not passed unchanged")
    require(probed["tool_result"] == "SUCCESS", "evaluator probe result not formatted")

    oversized_recipe = read_json(EXAMPLES["oversized_recipe"])
    oversized = copy.deepcopy(supported_request)
    oversized["observation_references"] = [
        "obs://synthetic/" + oversized_recipe["repeat_character"] * oversized_recipe["repeat_count"]
    ]
    require(len(json.dumps(oversized).encode("utf-8")) > MAX_INPUT_BYTES, "oversized recipe did not exceed limit")

    mismatch = copy.deepcopy(supported_request); mismatch["evaluation_profile"] = "human-oversight"
    unknown_profile = copy.deepcopy(supported_request); unknown_profile["evaluation_profile"] = "unknown-profile"
    missing_evidence = copy.deepcopy(supported_request); missing_evidence.pop("evidence_object")
    extra_field = copy.deepcopy(supported_request); extra_field["authorize"] = True
    invalid_evidence = copy.deepcopy(supported_request); invalid_evidence["evidence_object"] = {"synthetic": True}
    unsupported = copy.deepcopy(supported_request); unsupported["evidence_object"] = {"unsupported": {"set-value"}}

    invalid_cases = [
        (EXAMPLES["unknown_claim"].read_text(encoding="utf-8"), "TOOL_CLAIM_UNKNOWN"),
        (EXAMPLES["missing_profile"].read_text(encoding="utf-8"), "TOOL_PROFILE_UNKNOWN"),
        (unknown_profile, "TOOL_PROFILE_UNKNOWN"),
        (mismatch, "TOOL_CLAIM_PROFILE_MISMATCH"),
        (missing_evidence, "TOOL_EVIDENCE_OBJECT_REQUIRED"),
        (extra_field, "TOOL_INPUT_SCHEMA_INVALID"),
        (invalid_evidence, "EVIDENCE_INPUT_SCHEMA_INVALID"),
        (unsupported, "TOOL_INPUT_UNSUPPORTED_TYPE"),
        (deep_request(supported_request), "TOOL_INPUT_EXCESSIVE_NESTING"),
        ('{"evidence_object":' + "[" * 1200 + "null" + "]" * 1200 + ',"accountability_claim":"AUTHORIZED_AGENT_ACTION","evaluation_profile":"authorized-agent-action"}', "TOOL_INPUT_EXCESSIVE_NESTING"),
        (oversized, "TOOL_INPUT_TOO_LARGE"),
        ('{"accountability_claim":"AUTHORIZED_AGENT_ACTION",', "TOOL_INPUT_INVALID_JSON"),
        ('{"evidence_object":{"synthetic":true},"accountability_claim":"AUTHORIZED_AGENT_ACTION","accountability_claim":"AUTHORIZED_AGENT_ACTION","evaluation_profile":"authorized-agent-action"}', "TOOL_INPUT_DUPLICATE_KEY"),
    ]
    for request, code in invalid_cases:
        expect_rejected(request, code)

    serialized_surface = json.dumps([supported, insufficient], ensure_ascii=False, sort_keys=True)
    require("action:synthetic-inspection" not in serialized_surface, "evidence value reflected")
    require("obs://synthetic/example-001" not in serialized_surface, "observation reference value reflected")

    canonical = json.dumps(supported, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = evaluate_evidence_tool(EXAMPLES["supported"].read_bytes())
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "tool result non-deterministic")

    print("SAEE_LOCAL_TOOL_CAPABILITY_SMOKE: PASS")
    print("valid_cases=2/2")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=5/5")
    print("canonical_evaluator_reused=true")
    print("observation_not_used_as_evidence=true")
    print("evidence_values_reflected=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("persistence_performed=false")
    print("external_execution=false")
    print("mcp_available=false")
    print("api_available=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (LocalToolSmokeError, json.JSONDecodeError, OSError, SyntaxError) as exc:
        print(f"SAEE_LOCAL_TOOL_CAPABILITY_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
