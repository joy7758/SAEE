#!/usr/bin/env python3
"""Offline and loopback-only smoke for Local HTTP Capability Adapter Alpha."""

from __future__ import annotations

import ast
import copy
import json
import sys
import threading
from http.client import HTTPConnection
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_rehearsal_runtime import run_task
from saee_backend.services.capability_http_adapter import create_local_http_server, process_http_request
from saee_backend.services.capability_http_adapter import http_request_handler


SCENARIO = ROOT / "agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json"
EVIDENCE = ROOT / "agent-interface/capabilities/examples/valid_supported_request.json"
REQUEST_SCHEMA = ROOT / "schemas/saee-capability-http-request.schema.v0.1.json"
RESPONSE_SCHEMA = ROOT / "schemas/saee-capability-http-response.schema.v0.1.json"
ADAPTER_DIR = ROOT / "saee_backend/services/capability_http_adapter"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def envelope(request_id: str, operation: str, payload: dict[str, Any], capability_id: str = "saee.agent-reliability") -> dict[str, Any]:
    return {"request_id": request_id, "capability_id": capability_id, "operation": operation, "payload": payload}


def http_post(port: int, path: str, body: Any, content_type: str = "application/json") -> tuple[int, dict[str, Any]]:
    connection = HTTPConnection("127.0.0.1", port, timeout=5)
    encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
    connection.request("POST", path, encoded, {"Content-Type": content_type})
    response = connection.getresponse()
    value = json.loads(response.read().decode("utf-8"))
    headers = dict(response.getheaders())
    connection.close()
    require(headers.get("Cache-Control") == "no-store" and headers.get("X-Content-Type-Options") == "nosniff", "security headers missing")
    require("Access-Control-Allow-Origin" not in headers, "CORS unexpectedly enabled")
    return response.status, value


def main() -> int:
    Draft202012Validator.check_schema(json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8")))
    Draft202012Validator.check_schema(json.loads(RESPONSE_SCHEMA.read_text(encoding="utf-8")))
    run = run_task(SCENARIO)
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    requests = {
        "run": envelope("request:http-smoke-run", "evaluate_rehearsal_run", {"rehearsal_run": run}),
        "evidence": envelope("request:http-smoke-evidence", "evaluate_evidence", evidence),
        "rehearse": envelope("request:http-smoke-rehearse", "rehearse_agent", {"agent_reference": "agent:synthetic", "scenario_reference": "scenario:synthetic", "consent_scope": "local_controlled_synthetic_only"}),
    }

    original_invoke = http_request_handler.invoke_capability
    delegated = 0
    def probe(value: Any) -> dict[str, Any]:
        nonlocal delegated
        delegated += 1
        return original_invoke(value)
    http_request_handler.invoke_capability = probe
    try:
        direct = {
            "run": process_http_request("/capabilities/evaluate-rehearsal-run", requests["run"], invoked_at="2026-07-12T15:00:00Z"),
            "evidence": process_http_request("/capabilities/evaluate-evidence", requests["evidence"], invoked_at="2026-07-12T15:00:00Z"),
            "rehearse": process_http_request("/capabilities/rehearse-agent", requests["rehearse"], invoked_at="2026-07-12T15:00:00Z"),
        }
    finally:
        http_request_handler.invoke_capability = original_invoke
    require(delegated == 3, "HTTP Adapter did not delegate exactly once per request")
    require(direct["run"][0] == 200 and direct["run"][1]["status"] == "SUCCESS", "run endpoint failed")
    require(direct["evidence"][0] == 200 and direct["evidence"][1]["status"] == "SUCCESS", "evidence endpoint failed")
    require(direct["rehearse"][0] == 501 and direct["rehearse"][1]["status"] == "CONTRACT_ONLY", "rehearse boundary failed")

    server = create_local_http_server(0)
    require(server.server_address[0] == "127.0.0.1", "server not bound to localhost")
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        http_run = http_post(port, "/capabilities/evaluate-rehearsal-run", requests["run"])
        http_evidence = http_post(port, "/capabilities/evaluate-evidence", requests["evidence"])
        http_rehearse = http_post(port, "/capabilities/rehearse-agent", requests["rehearse"])
        bad_type = http_post(port, "/capabilities/evaluate-evidence", requests["evidence"], "text/plain")
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
    require((http_run[0], http_evidence[0], http_rehearse[0], bad_type[0]) == (200, 200, 501, 415), "loopback HTTP mapping invalid")

    invalid: list[tuple[int, dict[str, Any]]] = []
    invalid.append(process_http_request("/hidden", requests["evidence"], invoked_at="2026-07-12T15:00:00Z"))
    invalid.append(process_http_request("/capabilities/evaluate-evidence", None, invoked_at="2026-07-12T15:00:00Z"))
    candidate = copy.deepcopy(requests["evidence"]); candidate["extra"] = True; invalid.append(process_http_request("/capabilities/evaluate-evidence", candidate, invoked_at="2026-07-12T15:00:00Z"))
    candidate = copy.deepcopy(requests["evidence"]); candidate["operation"] = "evaluate_rehearsal_run"; invalid.append(process_http_request("/capabilities/evaluate-evidence", candidate, invoked_at="2026-07-12T15:00:00Z"))
    candidate = copy.deepcopy(requests["evidence"]); candidate["capability_id"] = "saee.unknown"; invalid.append(process_http_request("/capabilities/evaluate-evidence", candidate, invoked_at="2026-07-12T15:00:00Z"))
    invalid.append(process_http_request("/capabilities/evaluate-rehearsal-run", envelope("request:bad-run", "evaluate_rehearsal_run", {}), invoked_at="2026-07-12T15:00:00Z"))
    invalid.append(process_http_request("/capabilities/evaluate-evidence", envelope("request:bad-evidence", "evaluate_evidence", {}), invoked_at="2026-07-12T15:00:00Z"))
    candidate = copy.deepcopy(requests["evidence"]); candidate["payload"]["api_key"] = "synthetic-forbidden"; invalid.append(process_http_request("/capabilities/evaluate-evidence", candidate, invoked_at="2026-07-12T15:00:00Z"))
    candidate = copy.deepcopy(requests["evidence"]); candidate["request_id"] = "bad"; invalid.append(process_http_request("/capabilities/evaluate-evidence", candidate, invoked_at="2026-07-12T15:00:00Z"))
    candidate = copy.deepcopy(requests["evidence"]); candidate["operation"] = "BAD"; invalid.append(process_http_request("/capabilities/evaluate-evidence", candidate, invoked_at="2026-07-12T15:00:00Z"))
    candidate = copy.deepcopy(requests["evidence"]); candidate["payload"] = {f"k{i}": i for i in range(33)}; invalid.append(process_http_request("/capabilities/evaluate-evidence", candidate, invoked_at="2026-07-12T15:00:00Z"))
    invalid.append((bad_type[0], bad_type[1]))
    require(len(invalid) >= 12 and all(status >= 400 and response["status"] == "REJECTED" for status, response in invalid), "invalid HTTP request accepted")

    baseline = process_http_request("/capabilities/evaluate-evidence", requests["evidence"], invoked_at="2026-07-12T15:00:00Z")
    canonical = json.dumps(baseline, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        require(json.dumps(process_http_request("/capabilities/evaluate-evidence", requests["evidence"], invoked_at="2026-07-12T15:00:00Z"), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "HTTP Adapter non-deterministic")

    imported = set()
    combined_source = ""
    for path in ADAPTER_DIR.glob("*.py"):
        source = path.read_text(encoding="utf-8"); combined_source += source
        tree = ast.parse(source)
        imported.update(node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    require("from saee_backend.services.capability_runtime import invoke_capability" in combined_source, "Runtime delegation import missing")
    require(not any(module.endswith(("agent_run_capability", "evidence_adequacy", "local_evidence_tool")) for module in imported), "direct evaluator import detected")
    require("0.0.0.0" not in combined_source, "public bind address found")
    require("open(" not in combined_source and "Path.write" not in combined_source, "persistence call found")

    print("SAEE_CAPABILITY_HTTP_ADAPTER_SMOKE: PASS")
    print("http_adapter=true")
    print("localhost_binding=true")
    print("endpoints=3/3")
    print("runtime_delegation=3/3")
    print("supported_operations=2/2")
    print("contract_only_operations=1/1")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("direct_evaluator_imports=0")
    print("request_persisted=false")
    print("payload_persisted=false")
    print("network_public_access=false")
    print("public_service=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
