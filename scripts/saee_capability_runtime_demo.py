#!/usr/bin/env python3
"""Demonstrate five local Capability Runtime routing outcomes."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_rehearsal_runtime import run_task
from saee_backend.services.capability_runtime import invoke_capability


SCENARIO = ROOT / "agent-interface/rehearsal/scenarios/baseline-metadata-inspection.json"
EVIDENCE = ROOT / "agent-interface/capabilities/examples/valid_supported_request.json"


def request(request_id: str, operation: str, payload: dict[str, object], *, capability_id: str = "saee.agent-reliability") -> dict[str, object]:
    return {
        "request_id": request_id,
        "capability_id": capability_id,
        "operation": operation,
        "payload": payload,
        "caller_context": {
            "caller_id": "caller:saee-runtime-demo",
            "caller_type": "LOCAL_AGENT",
            "invoked_at": "2026-07-12T12:00:00Z",
            "customer_data_included": False,
            "network_access_requested": False,
            "external_world_action_requested": False,
        },
    }


def main() -> int:
    run = run_task(SCENARIO)
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cases = {
        "VALID_EVALUATE_AGENT_RUN": request("request:demo-run", "evaluate_agent_run", {"rehearsal_run": run}),
        "VALID_EVALUATE_EVIDENCE": request("request:demo-evidence", "evaluate_evidence", evidence),
        "CONTRACT_ONLY_REHEARSE_AGENT": request("request:demo-rehearse", "rehearse_agent", {"scenario_reference": "scenario:synthetic"}),
        "INVALID_OPERATION": request("request:demo-operation", "delete_production", {}),
        "INVALID_CAPABILITY": request("request:demo-capability", "evaluate_evidence", copy.deepcopy(evidence), capability_id="saee.unknown"),
    }
    output = []
    for case_id, invocation in cases.items():
        response = invoke_capability(invocation)
        output.append({
            "case_id": case_id,
            "operation": response["operation"],
            "status": response["status"],
            "reason_codes": response["reason_codes"],
            "receipt_id": response["invocation_receipt"]["receipt_id"],
            "production_ready": response["truth_boundary"]["production_ready"],
        })
    print(json.dumps({"result_type": "SAEE_CAPABILITY_RUNTIME_DEMO", "cases": output}, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

