#!/usr/bin/env python3
"""Run five real loopback HTTP calls against the local Capability Adapter."""

from __future__ import annotations

import json
import sys
import threading
from http.client import HTTPConnection
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_rehearsal_runtime import run_task
from saee_backend.services.capability_http_adapter import create_local_http_server


SCENARIO = ROOT / "agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json"
EVIDENCE = ROOT / "agent-interface/capabilities/examples/valid_supported_request.json"


def envelope(request_id: str, operation: str, payload: dict[str, Any], capability_id: str = "saee.agent-reliability") -> dict[str, Any]:
    return {"request_id": request_id, "capability_id": capability_id, "operation": operation, "payload": payload}


def post(port: int, path: str, value: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    connection = HTTPConnection("127.0.0.1", port, timeout=5)
    connection.request("POST", path, body=json.dumps(value, ensure_ascii=False).encode("utf-8"), headers={"Content-Type": "application/json"})
    response = connection.getresponse()
    body = json.loads(response.read().decode("utf-8"))
    connection.close()
    return response.status, body


def main() -> int:
    run = run_task(SCENARIO)
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cases = [
        ("VALID_EVALUATE_REHEARSAL_RUN", "/capabilities/evaluate-rehearsal-run", envelope("request:http-demo-run", "evaluate_rehearsal_run", {"rehearsal_run": run})),
        ("VALID_EVALUATE_EVIDENCE", "/capabilities/evaluate-evidence", envelope("request:http-demo-evidence", "evaluate_evidence", evidence)),
        ("CONTRACT_ONLY_REHEARSE_AGENT", "/capabilities/rehearse-agent", envelope("request:http-demo-rehearse", "rehearse_agent", {"agent_reference": "agent:synthetic", "scenario_reference": "scenario:synthetic", "consent_scope": "local_controlled_synthetic_only"})),
        ("INVALID_OPERATION", "/capabilities/evaluate-evidence", envelope("request:http-demo-operation", "delete_production", {})),
        ("INVALID_CAPABILITY", "/capabilities/evaluate-evidence", envelope("request:http-demo-capability", "evaluate_evidence", evidence, "saee.unknown")),
    ]
    server = create_local_http_server(0)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        results = []
        for case_id, path, value in cases:
            http_status, response = post(port, path, value)
            results.append({"case_id": case_id, "http_status": http_status, "status": response["status"], "operation": response["operation"], "reason_codes": response["reason_codes"], "receipt_id": response["invocation_receipt"]["receipt_id"]})
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print(json.dumps({"result_type": "SAEE_LOCAL_HTTP_CAPABILITY_DEMO", "bind_address": "127.0.0.1", "cases": results}, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

