"""Deterministic candidate extraction from closed synthetic OTel-style events.

This module does not import an OpenTelemetry SDK and does not claim protocol
compliance. It never performs network access, resource lookup, tool execution,
or identity/authorization verification. Trace attributes remain observations.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from saee_backend.services.evidence_adequacy import (
    TRUTH_BOUNDARY as ADEQUACY_TRUTH_BOUNDARY,
    evaluate_evidence_adequacy,
)


SCHEMA_VERSION = "0.1.0"
TRACE_SOURCE = "synthetic_opentelemetry_style"

OTEL_INPUT_SCHEMA_INVALID = "OTEL_INPUT_SCHEMA_INVALID"
OTEL_AGENT_ID_REQUIRED = "OTEL_AGENT_ID_REQUIRED"
OTEL_ACTION_CONTEXT_REQUIRED = "OTEL_ACTION_CONTEXT_REQUIRED"
OTEL_AUTHORIZATION_CLAIM_UNBOUND = "OTEL_AUTHORIZATION_CLAIM_UNBOUND"

INPUT_KEYS = {
    "saee_synthetic_otel_event_v0_1",
    "schema_version",
    "trace_source",
    "trace_event_id",
    "observed_timestamp",
    "attributes",
}

ATTRIBUTE_KEYS = {
    "agent.id",
    "action.type",
    "tool.name",
    "resource.reference",
    "human.id",
    "sandbox.id",
    "status",
    "authorization.claimed",
    "policy.decision_ref",
}

TRUTH_BOUNDARY = {
    "trace_is_evidence": False,
    "identity_authenticity_verified": False,
    "authorization_validity_verified": False,
    "resource_authenticity_verified": False,
    "human_approval_authenticity_verified": False,
    "accountability_claim_established": False,
    "opentelemetry_compliance_claimed": False,
    "production_ready": False,
}

LIMITATIONS = [
    "trace observations do not establish identity authenticity",
    "trace observations do not establish authorization validity",
    "trace observations do not establish resource authenticity",
    "candidate extraction does not establish an accountability claim",
]


class _DuplicateKeyError(ValueError):
    pass


def _closed_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError("duplicate JSON key")
        result[key] = value
    return result


def _timestamp_valid(value: Any) -> bool:
    if not isinstance(value, str) or re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})",
        value,
    ) is None:
        return False
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _reference(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/#-]{0,255}", value) is not None


def _base_mapping(event: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "saee_otel_candidate_evidence_mapping_v0_1": True,
        "schema_version": SCHEMA_VERSION,
        "trace_source": TRACE_SOURCE,
        "trace_event_id": "invalid-trace-event",
        "observed_timestamp": "1970-01-01T00:00:00Z",
        "candidate_evidence_fields": {},
        "missing_evidence_requirements": [],
        "mapping_confidence": "insufficient",
        "trace_mapping_result": "FAIL",
        "reason_codes": [OTEL_INPUT_SCHEMA_INVALID],
        "limitations": list(LIMITATIONS),
        "truth_boundary": dict(TRUTH_BOUNDARY),
    }
    if isinstance(event, dict):
        if _reference(event.get("trace_event_id")):
            payload["trace_event_id"] = event["trace_event_id"]
        if _timestamp_valid(event.get("observed_timestamp")):
            payload["observed_timestamp"] = event["observed_timestamp"]
    return payload


def _input_valid(event: Any) -> bool:
    if not isinstance(event, dict) or set(event) != INPUT_KEYS:
        return False
    attributes = event.get("attributes")
    if (
        event.get("saee_synthetic_otel_event_v0_1") is not True
        or event.get("schema_version") != SCHEMA_VERSION
        or event.get("trace_source") != TRACE_SOURCE
        or not _reference(event.get("trace_event_id"))
        or not _timestamp_valid(event.get("observed_timestamp"))
        or not isinstance(attributes, dict)
        or not set(attributes).issubset(ATTRIBUTE_KEYS)
    ):
        return False
    for key, value in attributes.items():
        if key == "authorization.claimed":
            if not isinstance(value, bool):
                return False
        elif key == "status":
            if value not in {"success", "error", "unknown"}:
                return False
        elif key == "resource.reference":
            if not isinstance(value, str) or not value or len(value) > 512:
                return False
        elif not _reference(value):
            return False
    return True


def map_otel_candidate(event: Any) -> dict[str, Any]:
    """Map one closed synthetic event into non-authoritative candidate fields."""

    mapping = _base_mapping(event if isinstance(event, dict) else None)
    if not _input_valid(event):
        return mapping

    attributes = event["attributes"]
    mapping["reason_codes"] = []
    mapping["trace_event_id"] = event["trace_event_id"]
    mapping["observed_timestamp"] = event["observed_timestamp"]
    candidate: dict[str, Any] = {
        "action_id": event["trace_event_id"],
        "timestamp": event["observed_timestamp"],
    }

    field_map = {
        "agent.id": ("observed_agent_id", "agent_id"),
        "action.type": ("observed_action_type", "action_type"),
        "resource.reference": ("observed_resource_reference", "resource_reference"),
        "tool.name": ("observed_tool_name", "tool_name"),
        "human.id": (None, "human_identity_claim"),
        "sandbox.id": (None, "sandbox_reference"),
        "status": (None, "status_observation"),
    }
    for attribute, (observed_key, candidate_key) in field_map.items():
        if attribute in attributes:
            candidate[candidate_key] = attributes[attribute]
            if observed_key is not None:
                mapping[observed_key] = attributes[attribute]
    mapping["candidate_evidence_fields"] = candidate

    reasons: list[str] = []
    if "agent.id" not in attributes:
        reasons.append(OTEL_AGENT_ID_REQUIRED)
    if "action.type" not in attributes and "tool.name" not in attributes:
        reasons.append(OTEL_ACTION_CONTEXT_REQUIRED)
    if attributes.get("authorization.claimed") is True and "policy.decision_ref" not in attributes:
        reasons.append(OTEL_AUTHORIZATION_CLAIM_UNBOUND)

    mapping["reason_codes"] = reasons
    if reasons:
        rejected = _base_mapping()
        rejected["reason_codes"] = reasons
        return rejected
    elif "resource.reference" in attributes and "tool.name" in attributes:
        mapping["trace_mapping_result"] = "PASS"
        mapping["mapping_confidence"] = "complete_observation"
    else:
        mapping["trace_mapping_result"] = "PARTIAL"
        mapping["mapping_confidence"] = "partial_observation"
    return mapping


def _candidate_package(claim_type: str, mapping: dict[str, Any]) -> dict[str, Any]:
    candidate = mapping["candidate_evidence_fields"]
    timestamp = candidate.get("timestamp")
    action_id = candidate.get("action_id")
    agent_id = candidate.get("agent_id")
    action_type = candidate.get("action_type") or candidate.get("tool_name")
    resource = candidate.get("resource_reference")

    if claim_type == "RESOURCE_AUTHENTICITY":
        receipt: dict[str, Any] = {}
        if agent_id is not None:
            receipt["agent_id"] = agent_id
        if resource is not None:
            receipt["requested_resource"] = resource
        evidence = {"resource_receipt": receipt}
    elif claim_type == "AUTHORIZED_AGENT_ACTION":
        action = {key: value for key, value in {
            "action_id": action_id,
            "agent_id": agent_id,
            "requested_scope": action_type,
            "timestamp": timestamp,
        }.items() if value is not None}
        evidence = {"action": action, "policy_decision": {}}
    elif claim_type == "HUMAN_OVERSIGHT":
        action = {key: value for key, value in {
            "action_id": action_id,
            "requested_scope": action_type,
            "timestamp": timestamp,
        }.items() if value is not None}
        approval = {key: value for key, value in {
            "human_identity": candidate.get("human_identity_claim"),
            "action_id": action_id,
        }.items() if value is not None}
        evidence = {"action": action, "approval": approval}
    else:
        resource_binding = {key: value for key, value in {
            "resolved_uri": resource,
        }.items() if value is not None}
        execution_effect = {key: value for key, value in {
            "effect_id": action_id,
            "resolved_uri": resource,
            "sandbox_ref": candidate.get("sandbox_reference"),
        }.items() if value is not None}
        evidence = {
            "resource_binding": resource_binding,
            "execution_effect": execution_effect,
            "causal_link": {},
        }
    return {
        "saee_evidence_adequacy_input_v0_1": True,
        "schema_version": SCHEMA_VERSION,
        "claim_type": claim_type,
        "evidence": evidence,
        "truth_boundary": dict(ADEQUACY_TRUTH_BOUNDARY),
    }


def evaluate_trace_candidate(claim_type: str, event: Any) -> dict[str, Any]:
    """Map a trace candidate and evaluate it without truth elevation."""

    mapping = map_otel_candidate(event)
    package = _candidate_package(claim_type, mapping)
    adequacy = evaluate_evidence_adequacy(claim_type, package)
    missing = [path.rsplit("/", 1)[-1] for path in adequacy["missing_requirements"]]
    mapping["missing_evidence_requirements"] = list(dict.fromkeys(missing))
    return {
        "saee_otel_candidate_evidence_evaluation_v0_1": True,
        "schema_version": SCHEMA_VERSION,
        "claim_type": claim_type,
        "trace_mapping_result": mapping["trace_mapping_result"],
        "mapping": mapping,
        "adequacy_result": adequacy["result"],
        "adequacy_evaluation": adequacy,
        "missing_requirements": adequacy["missing_requirements"],
        "explanation": "Trace observation is insufficient by itself to establish the selected accountability claim.",
        "accountability_claim_established": False,
        "network_accessed": False,
        "external_resource_read": False,
        "subprocess_started": False,
        "candidate_code_executed": False,
        "opentelemetry_compliance_claimed": False,
        "production_ready": False,
    }


def evaluate_trace_candidate_json(claim_type: str, text: str) -> dict[str, Any]:
    try:
        event = json.loads(text, object_pairs_hook=_closed_object)
    except (json.JSONDecodeError, UnicodeError, _DuplicateKeyError, ValueError):
        event = None
    return evaluate_trace_candidate(claim_type, event)
