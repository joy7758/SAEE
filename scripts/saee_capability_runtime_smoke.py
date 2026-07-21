#!/usr/bin/env python3
"""Offline deterministic smoke for Capability Service Local Runtime Alpha."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_rehearsal_runtime import run_task
from saee_backend.services.capability_runtime import invoke_capability
from saee_backend.services.capability_runtime import capability_invocation, capability_router
from saee_backend.services.capability_runtime.capability_registry_loader import load_capability_registry


SCENARIO = ROOT / "agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json"
EVIDENCE = ROOT / "agent-interface/capabilities/examples/valid_supported_request.json"
REQUEST_SCHEMA = ROOT / "schemas/saee-capability-invocation-request.schema.v0.1.json"
RESPONSE_SCHEMA = ROOT / "schemas/saee-capability-invocation-response.schema.v0.1.json"
RECEIPT_SCHEMA = ROOT / "schemas/saee-capability-invocation-receipt.schema.v0.1.json"
RUNTIME = ROOT / "saee_backend/services/capability_runtime"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def make_request(request_id: str, operation: str, payload: dict[str, Any], capability_id: str = "saee.agent-reliability") -> dict[str, Any]:
    return {
        "request_id": request_id,
        "capability_id": capability_id,
        "operation": operation,
        "payload": payload,
        "caller_context": {
            "caller_id": "caller:runtime-smoke",
            "caller_type": "LOCAL_TEST",
            "invoked_at": "2026-07-12T12:30:00Z",
            "customer_data_included": False,
            "network_access_requested": False,
            "external_world_action_requested": False,
        },
    }


def no_forbidden_runtime_calls() -> None:
    forbidden_imports = {"requests", "httpx", "urllib", "socket", "subprocess", "importlib"}
    forbidden_name_calls = {"eval", "exec", "compile", "__import__"}
    forbidden_attribute_calls = {"system", "popen", "Popen", "run"}
    for path in RUNTIME.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
        imports.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
        require(not imports.intersection(forbidden_imports), f"forbidden import in {path.name}")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    require(node.func.id not in forbidden_name_calls, f"forbidden execution call in {path.name}: {node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    require(node.func.attr not in forbidden_attribute_calls, f"forbidden execution call in {path.name}: {node.func.attr}")


def main() -> int:
    for path in (REQUEST_SCHEMA, RESPONSE_SCHEMA, RECEIPT_SCHEMA):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))

    registry = load_capability_registry()
    require(registry["package_operations_verified"] is True, "Package operation compatibility missing")
    require(registry["operations"] == {
        "evaluate_rehearsal_run": "implemented_local_offline_alpha",
        "evaluate_evidence": "implemented_local_offline_prototype",
        "rehearse_agent": "contract_only",
    }, "runtime operation set drifted")
    require(registry["hidden_operations"] == [], "hidden operation detected")

    run = run_task(SCENARIO)
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    requests = {
        "run": make_request("request:smoke-run", "evaluate_rehearsal_run", {"rehearsal_run": run}),
        "evidence": make_request("request:smoke-evidence", "evaluate_evidence", evidence),
        "contract": make_request("request:smoke-rehearse", "rehearse_agent", {"scenario_reference": "scenario:synthetic"}),
    }

    original_run = capability_router.evaluate_rehearsal_run
    original_evidence = capability_router.evaluate_evidence_tool
    calls = {"run": 0, "evidence": 0}

    def run_probe(value: dict[str, Any]) -> dict[str, Any]:
        calls["run"] += 1
        return original_run(value)

    def evidence_probe(value: dict[str, Any]) -> dict[str, Any]:
        calls["evidence"] += 1
        return original_evidence(value)

    capability_router.evaluate_rehearsal_run = run_probe
    capability_router.evaluate_evidence_tool = evidence_probe
    try:
        run_response = invoke_capability(requests["run"])
        evidence_response = invoke_capability(requests["evidence"])
    finally:
        capability_router.evaluate_rehearsal_run = original_run
        capability_router.evaluate_evidence_tool = original_evidence

    contract_response = invoke_capability(requests["contract"])
    require(run_response["status"] == "SUCCESS" and run_response["result"]["capability_id"] == "internal.saee.evaluate_rehearsal_run", "run operation failed")
    require(evidence_response["status"] == "SUCCESS" and evidence_response["result"]["tool_result"] == "SUCCESS", "evidence operation failed")
    require(contract_response["status"] == "CONTRACT_ONLY", "rehearse_agent boundary failed")
    require(calls == {"run": 1, "evidence": 1}, "canonical services were not reused exactly once")

    valid_responses = [run_response, evidence_response, contract_response]
    response_schema = json.loads(RESPONSE_SCHEMA.read_text(encoding="utf-8"))
    receipt_schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
    schema_registry = Registry().with_resource(receipt_schema["$id"], Resource.from_contents(receipt_schema))
    response_validator = Draft202012Validator(response_schema, registry=schema_registry)
    receipt_validator = Draft202012Validator(receipt_schema)
    for response in valid_responses:
        require(not list(response_validator.iter_errors(response)), "runtime response schema invalid")
        receipt = response["invocation_receipt"]
        require(not list(receipt_validator.iter_errors(receipt)), "receipt schema invalid")
        require(receipt["persistence_performed"] is False and receipt["sensitive_payload_recorded"] is False, "receipt boundary invalid")
        require(not set(receipt).intersection({"payload", "credentials", "chain_of_thought", "private_model_state"}), "receipt stores forbidden content")

    invalid_requests: list[Any] = []
    invalid_requests.append(None)
    candidate = copy.deepcopy(requests["evidence"]); candidate.pop("caller_context"); invalid_requests.append(candidate)
    candidate = copy.deepcopy(requests["evidence"]); candidate["extra"] = True; invalid_requests.append(candidate)
    candidate = copy.deepcopy(requests["evidence"]); candidate["caller_context"]["invoked_at"] = "not-time"; invalid_requests.append(candidate)
    candidate = copy.deepcopy(requests["evidence"]); candidate["request_id"] = "request:bad id"; invalid_requests.append(candidate)
    candidate = copy.deepcopy(requests["evidence"]); candidate["caller_context"]["customer_data_included"] = True; invalid_requests.append(candidate)
    candidate = copy.deepcopy(requests["evidence"]); candidate["caller_context"]["network_access_requested"] = True; invalid_requests.append(candidate)
    candidate = copy.deepcopy(requests["evidence"]); candidate["caller_context"]["external_world_action_requested"] = True; invalid_requests.append(candidate)
    candidate = copy.deepcopy(requests["evidence"]); candidate["payload"]["api_key"] = "synthetic-forbidden"; invalid_requests.append(candidate)
    invalid_requests.append(make_request("request:bad-operation", "delete_production", {}))
    invalid_requests.append(make_request("request:bad-capability", "evaluate_evidence", evidence, "saee.unknown"))
    invalid_requests.append(make_request("request:bad-run", "evaluate_rehearsal_run", {}))
    invalid_requests.append(make_request("request:bad-evidence", "evaluate_evidence", {}))
    candidate = copy.deepcopy(requests["evidence"]); candidate["payload"] = {"oversized": "x" * 1_000_001}; invalid_requests.append(candidate)
    candidate = copy.deepcopy(requests["evidence"]); candidate["payload"] = {"not_json": {1, 2}}; invalid_requests.append(candidate)

    rejected = [invoke_capability(item) for item in invalid_requests]
    require(all(item["status"] == "REJECTED" for item in rejected), "invalid request accepted")
    require(all(item["truth_boundary"]["production_ready"] is False for item in rejected), "invalid result changed truth boundary")
    require(any("CAPABILITY_OPERATION_UNDECLARED" in item["reason_codes"] for item in rejected), "undeclared operation reason missing")
    require(any("CAPABILITY_ID_INVALID" in item["reason_codes"] for item in rejected), "capability mismatch reason missing")
    require(any("CAPABILITY_SENSITIVE_INPUT_FORBIDDEN" in item["reason_codes"] for item in rejected), "secret input reason missing")
    require(rejected[3]["invocation_receipt"]["timestamp_source"] == "invalid_request_fallback", "invalid timestamp retained in receipt")

    original_route = capability_invocation.route_capability_request
    capability_invocation.route_capability_request = lambda _: (_ for _ in ()).throw(RuntimeError("synthetic internal failure"))
    try:
        failed = invoke_capability(requests["evidence"])
    finally:
        capability_invocation.route_capability_request = original_route
    require(failed["status"] == "FAILED" and failed["reason_codes"] == ["CAPABILITY_RUNTIME_FAILURE"], "internal failure did not fail closed")
    require("synthetic internal failure" not in json.dumps(failed), "private exception detail leaked")

    baseline = invoke_capability(requests["evidence"])
    canonical = json.dumps(baseline, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        require(json.dumps(invoke_capability(requests["evidence"]), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "runtime not deterministic")

    router_source = (RUNTIME / "capability_router.py").read_text(encoding="utf-8")
    require("from saee_backend.services.agent_run_capability import" in router_source, "existing Agent Run evaluator not reused")
    require("from saee_backend.services.local_evidence_tool import" in router_source, "existing Evidence evaluator adapter not reused")
    no_forbidden_runtime_calls()

    print("SAEE_CAPABILITY_RUNTIME_SMOKE: PASS")
    print("package_operations_verified=true")
    print("supported_operations=2/2")
    print("contract_only_operations=1/1")
    print("hidden_operations=0")
    print("canonical_agent_run_service_reused=true")
    print("canonical_evidence_service_reused=true")
    print("invocation_receipts=3/3")
    print(f"invalid_cases={len(invalid_requests)}/{len(invalid_requests)}")
    print("deterministic_runs=5/5")
    print("network_api_available=false")
    print("public_service=false")
    print("standard_mcp_transport=false")
    print("customer_data=false")
    print("external_world_actions=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
