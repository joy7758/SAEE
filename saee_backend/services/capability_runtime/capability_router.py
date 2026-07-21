"""Fixed local router for declared SAEE Capability Package operations."""

from __future__ import annotations

from typing import Any

from saee_backend.services.agent_run_capability import AgentRunCapabilityError, evaluate_agent_run as evaluate_rehearsal_run
from saee_backend.services.local_evidence_tool import evaluate_evidence_tool

from .capability_registry_loader import CAPABILITY_ID, load_capability_registry


def route_capability_request(request: dict[str, Any]) -> dict[str, Any]:
    """Route one validated request to an existing implementation or closed boundary."""

    registry = load_capability_registry()
    if request.get("capability_id") != CAPABILITY_ID:
        return {"status": "REJECTED", "result": {}, "reason_codes": ["CAPABILITY_ID_INVALID"]}
    operation = request.get("operation")
    if operation not in registry["operations"]:
        return {"status": "REJECTED", "result": {}, "reason_codes": ["CAPABILITY_OPERATION_UNDECLARED"]}
    payload = request.get("payload", {})
    if operation == "rehearse_agent":
        return {
            "status": "CONTRACT_ONLY",
            "result": {"operation": "rehearse_agent", "implementation_status": "CONTRACT_ONLY_NOT_IMPLEMENTED"},
            "reason_codes": ["CAPABILITY_OPERATION_CONTRACT_ONLY"],
        }
    if operation == "evaluate_rehearsal_run":
        if not isinstance(payload, dict) or set(payload) != {"rehearsal_run"} or not isinstance(payload.get("rehearsal_run"), dict):
            return {"status": "REJECTED", "result": {}, "reason_codes": ["CAPABILITY_PAYLOAD_INVALID"]}
        try:
            result = evaluate_rehearsal_run(payload["rehearsal_run"])
        except AgentRunCapabilityError as exc:
            return {"status": "REJECTED", "result": {}, "reason_codes": ["CAPABILITY_OPERATION_REJECTED"], "upstream_reason_code": exc.code}
        return {"status": "SUCCESS", "result": result, "reason_codes": []}
    result = evaluate_evidence_tool(payload)
    if result.get("tool_result") == "REJECTED_INPUT":
        return {"status": "REJECTED", "result": result, "reason_codes": ["CAPABILITY_OPERATION_REJECTED"]}
    return {"status": "SUCCESS", "result": result, "reason_codes": []}
