"""Local synthetic, receive-only Observation Adapter prototype for SAEE Phase 2B."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
INPUT_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-synthetic-external-observation.v0.1.schema.json"
OBSERVATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json"
PROVENANCE_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-adapter-provenance-contract.v0.1.schema.json"

ADAPTER_ID = "adapter:saee-local-synthetic-observation-v0.1"
ADAPTER_VERSION = "0.1.0-prototype"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_CONTENT_KEYS = {
    "raw_prompt",
    "raw_output",
    "hidden_reasoning",
    "private_chain_of_thought",
    "internal_model_state",
    "customer_data",
}


class SyntheticObservationAdapterError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class InputSnapshot:
    payload: bytes
    digest: str


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_snapshot_once(path: Path) -> InputSnapshot:
    payload = path.read_bytes()
    return InputSnapshot(payload=payload, digest=hashlib.sha256(payload).hexdigest())


def require_local_path(path: Path, code: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SyntheticObservationAdapterError(code, str(path)) from exc
    return resolved


def local_ref(path: Path) -> str:
    return str(require_local_path(path, "ADAPTER_OUTPUT_PATH_OUTSIDE_ROOT").relative_to(ROOT.resolve()))


def find_forbidden_content_keys(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_CONTENT_KEYS:
                found.append(key)
            found.extend(find_forbidden_content_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_forbidden_content_keys(child))
    return sorted(set(found))


def load_validator(path: Path) -> Draft202012Validator:
    schema = json.loads(path.read_bytes())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_value(validator: Draft202012Validator, value: dict[str, Any], code: str) -> None:
    errors = sorted(validator.iter_errors(value), key=lambda item: list(item.path))
    if errors:
        path = ".".join(str(part) for part in errors[0].path) or "root"
        raise SyntheticObservationAdapterError(code, f"{path}: {errors[0].message}")


def parse_input_snapshot(snapshot: InputSnapshot) -> dict[str, Any]:
    try:
        value = json.loads(snapshot.payload)
    except json.JSONDecodeError as exc:
        raise SyntheticObservationAdapterError("ADAPTER_INPUT_JSON_INVALID", str(exc)) from exc
    if not isinstance(value, dict):
        raise SyntheticObservationAdapterError("ADAPTER_INPUT_SCHEMA_INVALID", "root must be object")
    forbidden = find_forbidden_content_keys(value)
    if forbidden:
        raise SyntheticObservationAdapterError("ADAPTER_CONTENT_BOUNDARY_VIOLATION", ",".join(forbidden))
    validate_value(load_validator(INPUT_SCHEMA_PATH), value, "ADAPTER_INPUT_SCHEMA_INVALID")
    return value


def build_observation_envelope(source: dict[str, Any]) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for source_event in source["events"]:
        summary = source_event["observable_behavior_summary"]
        event = {
            "event_id": source_event["event_id"],
            "sequence": source_event["sequence"],
            "timestamp": source_event["timestamp"],
            "event_type": source_event["event_type"],
            "summary": summary,
            "digest_algorithm": "sha256",
            "summary_digest": hashlib.sha256(summary.encode("utf-8")).hexdigest(),
            "payload_included": False,
            "observation_is_evidence": False,
            "authorization_inferred": False,
            "deployment_decision_inferred": False,
        }
        if "parent_event_id" in source_event:
            event["parent_event_id"] = source_event["parent_event_id"]
        events.append(event)

    envelope = {
        "saee_observation_envelope_v0_1": True,
        "schema_version": "0.1.0",
        "observation_id": source["observation_id"],
        "trace_id": source["trace_id"],
        "created_at": source["created_at"],
        "producer": {
            "producer_id": "producer:saee-local-synthetic-observation-adapter",
            "type": "runtime_adapter_declaration",
            "version": ADAPTER_VERSION,
            "adapter_implemented": False,
        },
        "source": {
            "source_type": "runtime_observation",
            "runtime_ref": source["runtime_ref"],
            "adapter_ref": ADAPTER_ID,
            "receive_only": True,
            "external_execution_by_saee": False,
            "raw_content_included": False,
        },
        "authorization": {
            "status": "synthetic_declared_only",
            "authorization_ref": source["authorization_ref"],
            "scope": source["authorization_scope"],
            "independently_verified": False,
            "authorization_inferred_from_trace": False,
        },
        "sanitization": {
            "status": "synthetic_no_raw_content",
            "method": "synthetic_generation",
            "raw_content_excluded": True,
            "independently_verified": False,
        },
        "events": events,
        "privacy": {
            "retention_ref": source["retention_ref"],
            "deletion_ref": source["deletion_ref"],
            "personal_data_included": False,
            "retention_verified": False,
            "deletion_verified": False,
        },
        "truth_boundary": {
            "observation_only": True,
            "evidence_established": False,
            "trace_authenticity_verified": False,
            "authorization_proven": False,
            "deployment_authorized": False,
            "automatic_decision": False,
            "real_agent_executed_by_saee": False,
            "network_accessed": False,
            "production_ready": False,
        },
    }
    validate_value(load_validator(OBSERVATION_SCHEMA_PATH), envelope, "ADAPTER_OUTPUT_SCHEMA_INVALID")
    return envelope


def build_provenance(
    source: dict[str, Any],
    input_ref: str,
    input_digest: str,
    output_ref: str,
    output_digest: str,
) -> dict[str, Any]:
    provenance = {
        "saee_adapter_provenance_contract_v0_1": True,
        "schema_version": "0.1.0",
        "adapter_provenance_id": f"adapter-provenance:{source['observation_id']}:prototype",
        "adapter_id": ADAPTER_ID,
        "adapter_version": ADAPTER_VERSION,
        "implementation_status": "prototype",
        "producer_type": "synthetic_observation_adapter",
        "source_schema_ref": "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json",
        "input_snapshot_ref": input_ref,
        "input_snapshot_digest": input_digest,
        "output_envelope_ref": output_ref,
        "output_envelope_digest": output_digest,
        "digest_algorithm": "sha256",
        "process_same_bytes": True,
        "read_once_verified": True,
        "adapter_receive_only": True,
        "produces_observation": True,
        "produces_evidence": False,
        "produces_risk": False,
        "produces_decision": False,
        "network_accessed": False,
        "external_execution": False,
        "validation_status": "prototype_binding_validated",
        "truth_boundary": {
            "record_scope": "local_implementation_record",
            "adapter_identity_independently_verified": False,
            "adapter_behavior_independently_verified": False,
            "input_snapshot_authenticity_independently_verified": False,
            "output_envelope_authenticity_independently_verified": False,
            "observation_is_evidence": False,
            "risk_probability_measured": False,
            "decision_authorized": False,
            "termination_authority": False,
            "customer_data_processed": False,
            "production_ready": False,
        },
    }
    validate_value(load_validator(PROVENANCE_SCHEMA_PATH), provenance, "ADAPTER_PROVENANCE_SCHEMA_INVALID")
    return provenance


def rejected_result(code: str, detail: str) -> dict[str, Any]:
    return {
        "adapter_result": "reject",
        "reason_code": code,
        "reason": detail,
        "observation_envelope": None,
        "adapter_provenance": None,
        "evidence": None,
        "risk": None,
        "decision": None,
        "termination_contract": None,
    }


def accepted_result(envelope: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any]:
    return {
        "adapter_result": "accepted",
        "reason_code": None,
        "reason": None,
        "observation_envelope": envelope,
        "adapter_provenance": provenance,
        "evidence": None,
        "risk": None,
        "decision": None,
        "termination_contract": None,
    }


def run_adapter_file(
    input_path: Path,
    expected_input_digest: str,
    output_envelope_path: Path,
    output_provenance_path: Path,
) -> dict[str, Any]:
    """Read the input exactly once, process the same bytes, and write bounded local outputs."""
    try:
        resolved_input = require_local_path(input_path, "ADAPTER_INPUT_PATH_OUTSIDE_ROOT")
        resolved_output = require_local_path(output_envelope_path, "ADAPTER_OUTPUT_PATH_OUTSIDE_ROOT")
        resolved_provenance = require_local_path(output_provenance_path, "ADAPTER_OUTPUT_PATH_OUTSIDE_ROOT")
        if not SHA256_PATTERN.fullmatch(expected_input_digest):
            raise SyntheticObservationAdapterError("ADAPTER_EXPECTED_DIGEST_INVALID", expected_input_digest)

        snapshot = read_snapshot_once(resolved_input)
        if snapshot.digest != expected_input_digest:
            raise SyntheticObservationAdapterError("ADAPTER_SNAPSHOT_DIGEST_MISMATCH", resolved_input.name)

        source = parse_input_snapshot(snapshot)
        envelope = build_observation_envelope(source)
        envelope_bytes = canonical_json_bytes(envelope)
        envelope_digest = hashlib.sha256(envelope_bytes).hexdigest()
        provenance = build_provenance(
            source=source,
            input_ref=local_ref(resolved_input),
            input_digest=snapshot.digest,
            output_ref=local_ref(resolved_output),
            output_digest=envelope_digest,
        )
        provenance_bytes = canonical_json_bytes(provenance)

        resolved_output.write_bytes(envelope_bytes)
        resolved_provenance.write_bytes(provenance_bytes)
        return accepted_result(envelope, provenance)
    except SyntheticObservationAdapterError as exc:
        return rejected_result(exc.code, exc.detail)
