"""Create deterministic, non-persistent invocation metadata receipts."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "schemas/saee-capability-invocation-receipt.schema.v0.1.json"
RUNTIME_VERSION = "0.1.0-local-alpha"
KNOWN_OPERATIONS = {"evaluate_agent_run", "evaluate_evidence", "rehearse_agent"}
REQUEST_ID_PATTERN = re.compile(r"^request:[A-Za-z0-9._:-]{1,120}$")


def _canonical_digest(value: Any) -> str:
    try:
        payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError):
        payload = json.dumps({"unserializable_type": type(value).__name__}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _valid_rfc3339(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def create_invocation_receipt(request: Any, status: str, result: dict[str, Any]) -> dict[str, Any]:
    """Bind request/result digests without retaining either payload."""

    request_map = request if isinstance(request, dict) else {}
    raw_request_id = request_map.get("request_id")
    request_id = raw_request_id if isinstance(raw_request_id, str) and REQUEST_ID_PATTERN.fullmatch(raw_request_id) else "request:invalid"
    raw_operation = request_map.get("operation")
    operation = raw_operation if raw_operation in KNOWN_OPERATIONS else "UNKNOWN"
    caller_context = request_map.get("caller_context")
    declared_time = caller_context.get("invoked_at") if isinstance(caller_context, dict) else None
    if _valid_rfc3339(declared_time):
        timestamp = declared_time
        timestamp_source = "caller_declared"
    else:
        timestamp = "1970-01-01T00:00:00Z"
        timestamp_source = "invalid_request_fallback"
    request_digest = _canonical_digest(request)
    result_digest = _canonical_digest(result)
    receipt_seed = {
        "request_digest": request_digest,
        "result_digest": result_digest,
        "status": status,
        "runtime_version": RUNTIME_VERSION,
    }
    receipt = {
        "receipt_id": f"receipt:sha256:{_canonical_digest(receipt_seed)}",
        "request_id": request_id,
        "request_digest": f"sha256:{request_digest}",
        "capability_id": "saee.agent-reliability",
        "operation": operation,
        "timestamp": timestamp,
        "timestamp_source": timestamp_source,
        "status": status,
        "runtime_version": RUNTIME_VERSION,
        "result_ref": f"inline-result:sha256:{result_digest}",
        "persistence_performed": False,
        "sensitive_payload_recorded": False,
    }
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(receipt)
    return receipt
