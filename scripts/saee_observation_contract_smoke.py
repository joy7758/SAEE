#!/usr/bin/env python3
"""Offline contract and boundary gate for SAEE Phase 1.75 observations."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json"
EXAMPLE_DIRECTORY = ROOT / "agent-interface/architecture/examples/observation"
CASE_PATH = ROOT / "agent-interface/architecture/examples/phase1_5_cases/case-001-baseline-stability.json"
EVIDENCE_CASE_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json"
FINAL_ARCHITECTURE_PATH = ROOT / "docs/architecture/FINAL_ARCHITECTURE_SPEC.md"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE1_75_OBSERVATION_CONTRACT.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE1_75_OBSERVATION_CONTRACT_RECOMMENDATION_GATE.md"

EVIDENCE_CASE_SCHEMA_SHA256 = "e99ece1b5e37291775e344d871d6223089c84bd11065e7ef0f0fcfab353b121e"
FINAL_ARCHITECTURE_SHA256 = "60f1e8c71172f8f8c214a57bdf2ac2162483e5eccd14b838c226cc89ede649a3"

EXPECTED_EXAMPLES = {
    "synthetic-observation.json": ("synthetic_generator", "synthetic_environment"),
    "runtime-observation.json": ("runtime_adapter_declaration", "runtime_observation"),
    "tool-trace-observation.json": ("tool_trace_adapter_declaration", "tool_trace_observation"),
}

DERIVED_CASE_KEYS = {
    "identity", "task_contract", "environment", "agent_reference", "observation",
    "evaluation", "evidence", "risk", "decision",
}


class ObservationContractError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ObservationContractError("OBSERVATION_CONTRACT_CHECK_FAILED", detail)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def assert_strict_objects(node: Any, location: str = "root") -> None:
    if isinstance(node, dict):
        if node.get("type") == "object":
            require(node.get("additionalProperties") is False, f"open object schema at {location}")
        for key, value in node.items():
            assert_strict_objects(value, f"{location}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            assert_strict_objects(value, f"{location}/{index}")


def validate_semantics(envelope: dict[str, Any]) -> None:
    events = envelope["events"]
    sequences = [item["sequence"] for item in events]
    if sequences != list(range(len(events))):
        raise ObservationContractError("OBSERVATION_SEQUENCE_INVALID", "events must be contiguous from zero")
    event_ids = [item["event_id"] for item in events]
    if len(event_ids) != len(set(event_ids)):
        raise ObservationContractError("OBSERVATION_EVENT_ID_DUPLICATE", "event IDs must be unique")
    seen: set[str] = set()
    timestamps: list[datetime] = []
    for event in events:
        if event.get("parent_event_id") not in (None, "") and event["parent_event_id"] not in seen:
            raise ObservationContractError("OBSERVATION_PARENT_INVALID", event["event_id"])
        if sha256_text(event["summary"]) != event["summary_digest"]:
            raise ObservationContractError("OBSERVATION_SUMMARY_DIGEST_INVALID", event["event_id"])
        seen.add(event["event_id"])
        timestamps.append(parse_time(event["timestamp"]))
    if timestamps != sorted(timestamps):
        raise ObservationContractError("OBSERVATION_TIME_ORDER_INVALID", "event timestamps")
    if parse_time(envelope["created_at"]) > timestamps[0]:
        raise ObservationContractError("OBSERVATION_CREATED_AT_INVALID", "created_at after first event")


def integrate_by_reference(envelope: dict[str, Any], source_case: dict[str, Any]) -> dict[str, Any]:
    """Bind one envelope by stable ID without treating its trace as evidence."""

    from saee_backend.services.saee_evidence_case import evaluate_assurance_case

    candidate = copy.deepcopy(source_case)
    target = candidate["observations"][0]
    target["observation_ref"] = envelope["observation_id"]
    target["reason"] = envelope["events"][0]["summary"]
    target["failure_class"] = envelope["events"][0]["event_type"]
    return evaluate_assurance_case(candidate)


def main() -> None:
    for path in (SCHEMA_PATH, EXAMPLE_DIRECTORY, CASE_PATH, EVIDENCE_CASE_SCHEMA_PATH, FINAL_ARCHITECTURE_PATH, DOC_PATH, GATE_PATH):
        require(path.exists(), f"missing required path: {path}")

    require(sha256_path(EVIDENCE_CASE_SCHEMA_PATH) == EVIDENCE_CASE_SCHEMA_SHA256, "Evidence Case v0.1 schema changed")
    require(sha256_path(FINAL_ARCHITECTURE_PATH) == FINAL_ARCHITECTURE_SHA256, "FINAL_ARCHITECTURE_SPEC changed")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert_strict_objects(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    paths = sorted(EXAMPLE_DIRECTORY.glob("*.json"))
    require({path.name for path in paths} == set(EXPECTED_EXAMPLES), "expected exactly three examples")

    envelopes: list[dict[str, Any]] = []
    source_case = json.loads(CASE_PATH.read_text(encoding="utf-8"))
    integration_results: list[dict[str, Any]] = []
    for path in paths:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(envelope)
        validate_semantics(envelope)
        expected_producer, expected_source = EXPECTED_EXAMPLES[path.name]
        require(envelope["producer"]["type"] == expected_producer, f"{path.name}: producer type")
        require(envelope["source"]["source_type"] == expected_source, f"{path.name}: source type")
        require(envelope["producer"]["adapter_implemented"] is False, f"{path.name}: adapter claim")
        require(envelope["source"]["receive_only"] is True, f"{path.name}: receive-only")
        require(envelope["source"]["external_execution_by_saee"] is False, f"{path.name}: execution boundary")
        require(envelope["source"]["raw_content_included"] is False, f"{path.name}: raw content")
        require(envelope["authorization"]["independently_verified"] is False, f"{path.name}: authorization verification")
        require(envelope["authorization"]["authorization_inferred_from_trace"] is False, f"{path.name}: trace authorization")
        require(envelope["sanitization"]["independently_verified"] is False, f"{path.name}: sanitization verification")
        require(all(item["observation_is_evidence"] is False for item in envelope["events"]), f"{path.name}: observation became evidence")
        require(all(item["authorization_inferred"] is False for item in envelope["events"]), f"{path.name}: event inferred authorization")
        require(all(item["deployment_decision_inferred"] is False for item in envelope["events"]), f"{path.name}: event inferred decision")
        boundary = envelope["truth_boundary"]
        require(boundary["observation_only"] is True, f"{path.name}: observation marker")
        for field in (
            "evidence_established", "trace_authenticity_verified", "authorization_proven",
            "deployment_authorized", "automatic_decision", "real_agent_executed_by_saee",
            "network_accessed", "production_ready",
        ):
            require(boundary[field] is False, f"{path.name}: truth boundary {field}")

        result = integrate_by_reference(envelope, source_case)
        derived = result["evidence_case_object"]
        require(set(derived) == DERIVED_CASE_KEYS, f"{path.name}: Evidence Case top-level drift")
        require(any(item["observation_ref"] == envelope["observation_id"] for item in derived["observation"]), f"{path.name}: observation reference lost")
        evaluation_rows = [row for group in derived["evaluation"] for row in group["results"]]
        require(any(item["observation_ref"] == envelope["observation_id"] for item in evaluation_rows), f"{path.name}: evaluation reference lost")
        require(envelope["trace_id"] not in json.dumps(derived, ensure_ascii=False), f"{path.name}: trace copied into Evidence Case")
        require(result["truth_boundary"]["deployment_authorized"] is False, f"{path.name}: deployment authority")
        require(result["truth_boundary"]["automatic_decision_made"] is False, f"{path.name}: automatic decision")
        envelopes.append(envelope)
        integration_results.append(result)

    base = envelopes[0]
    schema_negatives = []
    extra = copy.deepcopy(base); extra["unexpected"] = True; schema_negatives.append(extra)
    evidence = copy.deepcopy(base); evidence["truth_boundary"]["evidence_established"] = True; schema_negatives.append(evidence)
    authenticity = copy.deepcopy(base); authenticity["truth_boundary"]["trace_authenticity_verified"] = True; schema_negatives.append(authenticity)
    authorization = copy.deepcopy(base); authorization["truth_boundary"]["authorization_proven"] = True; schema_negatives.append(authorization)
    deployment = copy.deepcopy(base); deployment["truth_boundary"]["deployment_authorized"] = True; schema_negatives.append(deployment)
    event_evidence = copy.deepcopy(base); event_evidence["events"][0]["observation_is_evidence"] = True; schema_negatives.append(event_evidence)
    event_authorization = copy.deepcopy(base); event_authorization["events"][0]["authorization_inferred"] = True; schema_negatives.append(event_authorization)
    event_decision = copy.deepcopy(base); event_decision["events"][0]["deployment_decision_inferred"] = True; schema_negatives.append(event_decision)
    execution = copy.deepcopy(base); execution["source"]["external_execution_by_saee"] = True; schema_negatives.append(execution)
    raw_content = copy.deepcopy(base); raw_content["source"]["raw_content_included"] = True; schema_negatives.append(raw_content)
    require(all(not validator.is_valid(item) for item in schema_negatives), "schema accepted a boundary negative")

    semantic_negatives: list[tuple[dict[str, Any], str]] = []
    bad_digest = copy.deepcopy(base); bad_digest["events"][0]["summary_digest"] = "0" * 64
    semantic_negatives.append((bad_digest, "OBSERVATION_SUMMARY_DIGEST_INVALID"))
    bad_sequence = copy.deepcopy(base); bad_sequence["events"][0]["sequence"] = 1
    semantic_negatives.append((bad_sequence, "OBSERVATION_SEQUENCE_INVALID"))
    bad_parent = copy.deepcopy(base); bad_parent["events"][0]["parent_event_id"] = "event:missing"
    semantic_negatives.append((bad_parent, "OBSERVATION_PARENT_INVALID"))
    for invalid, expected in semantic_negatives:
        try:
            validate_semantics(invalid)
        except ObservationContractError as exc:
            require(exc.code == expected, f"expected {expected}, got {exc.code}")
        else:
            raise ObservationContractError("OBSERVATION_NEGATIVE_ACCEPTED", expected)

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    require(not imported_roots(Path(__file__)).intersection(forbidden), "smoke imports external capability")

    canonical = [json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for item in integration_results]
    for _ in range(5):
        repeated = [integrate_by_reference(envelope, source_case) for envelope in envelopes]
        require(
            [json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for item in repeated] == canonical,
            "integration is not deterministic",
        )

    print("SAEE_PHASE1_75_OBSERVATION_CONTRACT_SMOKE: PASS")
    print("schema_valid_examples=3/3")
    print("schema_negative_cases=10/10")
    print("semantic_negative_cases=3/3")
    print("summary_digest_valid=4/4")
    print("observation_not_evidence=3/3")
    print("trace_not_authorization=3/3")
    print("no_deployment_authority=3/3")
    print("receive_only_sources=3/3")
    print("integration_cases=3/3")
    print("observation_reference_integrity=3/3")
    print("evidence_case_top_level_stable=3/3")
    print("deterministic_runs=5/5")
    print("evidence_case_schema_modified=false")
    print("final_architecture_modified=false")
    print("adapter_implemented_by_phase1_75_contract=false")
    print("real_agent_connected=false")
    print("network_calls=0")
    print("deployment_authorized=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
