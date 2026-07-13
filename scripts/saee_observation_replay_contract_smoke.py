#!/usr/bin/env python3
"""Offline integrity gate for SAEE Phase 1.9 Replay Contracts."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json"
EXAMPLE_DIRECTORY = ROOT / "agent-interface/architecture/examples/replay"
OBSERVATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json"
OBSERVATION_DIRECTORY = ROOT / "agent-interface/architecture/examples/observation"
EVIDENCE_CASE_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json"
FINAL_ARCHITECTURE_PATH = ROOT / "docs/architecture/FINAL_ARCHITECTURE_SPEC.md"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE1_9_OBSERVATION_REPLAY_CONTRACT.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE1_9_OBSERVATION_REPLAY_CONTRACT_RECOMMENDATION_GATE.md"

OBSERVATION_SCHEMA_SHA256 = "5e46e58163c14e6e9d7013c227cbc177cade5ec76c67d667fccdbafb9790cdd2"
EVIDENCE_CASE_SCHEMA_SHA256 = "e99ece1b5e37291775e344d871d6223089c84bd11065e7ef0f0fcfab353b121e"
FINAL_ARCHITECTURE_SHA256 = "60f1e8c71172f8f8c214a57bdf2ac2162483e5eccd14b838c226cc89ede649a3"

EXPECTED_EXAMPLES = {
    "synthetic-replay-case.json": "none_synthetic_source",
    "consent-replay-case.json": "none_synthetic_source",
    "transformed-replay-case.json": "summary_only_projection",
}

FORBIDDEN_COGNITIVE_CONTENT = (
    "hidden reasoning",
    "private chain of thought",
    "chain-of-thought",
    "internal model state",
    "raw prompt",
    "raw output",
)

FALSE_TRUTH_BOUNDARIES = (
    "replay_executed",
    "source_envelopes_authenticity_verified",
    "consent_verified",
    "data_use_permission_verified",
    "transformation_provenance_verified",
    "cognitive_boundary_verified",
    "observation_established_as_evidence",
    "replay_authorizes_execution",
    "deployment_authorized",
    "automatic_execution",
    "real_agent_executed",
    "customer_data_processed",
    "external_validation_completed",
    "customer_validated",
    "production_ready",
)


class ReplayContractError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ReplayContractError("REPLAY_CONTRACT_CHECK_FAILED", detail)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
            require(node.get("additionalProperties") is False, f"open object at {location}")
        for key, value in node.items():
            assert_strict_objects(value, f"{location}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            assert_strict_objects(value, f"{location}/{index}")


def validate_content_boundary(envelope: dict[str, Any]) -> None:
    for event in envelope["events"]:
        lowered = event["summary"].lower()
        for forbidden in FORBIDDEN_COGNITIVE_CONTENT:
            if forbidden in lowered:
                raise ReplayContractError("REPLAY_CONTENT_BOUNDARY_VIOLATION", forbidden)


def validate_replay_contract(
    contract: dict[str, Any],
    observation_validator: Draft202012Validator,
) -> dict[str, Any]:
    created_at = parse_time(contract["created_at"])
    starts_at = parse_time(contract["replay_window"]["starts_at"])
    ends_at = parse_time(contract["replay_window"]["ends_at"])
    if not created_at <= starts_at < ends_at:
        raise ReplayContractError("REPLAY_WINDOW_INVALID", contract["replay_id"])

    refs = contract["source_envelope_refs"]
    observation_ids = [item["observation_id"] for item in refs]
    envelope_refs = [item["envelope_ref"] for item in refs]
    if len(observation_ids) != len(set(observation_ids)) or len(envelope_refs) != len(set(envelope_refs)):
        raise ReplayContractError("REPLAY_SOURCE_REFERENCE_DUPLICATE", contract["replay_id"])

    resolved_observation_ids: list[str] = []
    for source in refs:
        path = (ROOT / source["envelope_ref"]).resolve()
        try:
            path.relative_to(OBSERVATION_DIRECTORY.resolve())
        except ValueError as exc:
            raise ReplayContractError("REPLAY_SOURCE_PATH_OUTSIDE_ALLOWLIST", source["envelope_ref"]) from exc
        if not path.is_file():
            raise ReplayContractError("REPLAY_SOURCE_ENVELOPE_MISSING", source["envelope_ref"])
        if sha256_path(path) != source["envelope_digest"]:
            raise ReplayContractError("REPLAY_SOURCE_DIGEST_INVALID", source["envelope_ref"])
        envelope = json.loads(path.read_text(encoding="utf-8"))
        errors = list(observation_validator.iter_errors(envelope))
        if errors:
            raise ReplayContractError("REPLAY_SOURCE_ENVELOPE_SCHEMA_INVALID", source["envelope_ref"])
        if envelope["observation_id"] != source["observation_id"]:
            raise ReplayContractError("REPLAY_SOURCE_OBSERVATION_ID_MISMATCH", source["envelope_ref"])
        validate_content_boundary(envelope)
        resolved_observation_ids.append(envelope["observation_id"])

    transformation = contract["transformation_log"]
    if transformation["method"] == "none_synthetic_source" and transformation["transformation_applied"] is not False:
        raise ReplayContractError("REPLAY_TRANSFORMATION_STATE_INVALID", contract["replay_id"])
    if transformation["method"] != "none_synthetic_source" and transformation["transformation_applied"] is not True:
        raise ReplayContractError("REPLAY_TRANSFORMATION_STATE_INVALID", contract["replay_id"])

    return {
        "replay_id": contract["replay_id"],
        "result": "PASS",
        "source_observation_ids": resolved_observation_ids,
        "consent_ref_present": bool(contract["consent_ref"]),
        "data_use_permission_ref_present": bool(contract["data_use_permission_ref"]),
        "transformation_provenance_present": bool(
            transformation["redaction_provenance_ref"] and transformation["provenance_ref"]
        ),
        "content_boundary_declared": all(
            contract["content_boundary"][field] is True
            for field in (
                "observable_behavior_only",
                "hidden_reasoning_excluded",
                "private_chain_of_thought_excluded",
                "internal_model_state_excluded",
                "raw_prompt_excluded",
                "raw_output_excluded",
            )
        ),
        "manual_start_required": contract["execution_policy"]["manual_start_required"],
        "replay_executed": False,
        "agent_executed": False,
        "network_accessed": False,
        "deployment_authorized": False,
    }


def main() -> None:
    for path in (
        SCHEMA_PATH,
        EXAMPLE_DIRECTORY,
        OBSERVATION_SCHEMA_PATH,
        OBSERVATION_DIRECTORY,
        EVIDENCE_CASE_SCHEMA_PATH,
        FINAL_ARCHITECTURE_PATH,
        DOC_PATH,
        GATE_PATH,
    ):
        require(path.exists(), f"missing required path: {path}")

    require(sha256_path(OBSERVATION_SCHEMA_PATH) == OBSERVATION_SCHEMA_SHA256, "Observation Envelope v0.1 changed")
    require(sha256_path(EVIDENCE_CASE_SCHEMA_PATH) == EVIDENCE_CASE_SCHEMA_SHA256, "Evidence Case v0.1 changed")
    require(sha256_path(FINAL_ARCHITECTURE_PATH) == FINAL_ARCHITECTURE_SHA256, "FINAL_ARCHITECTURE_SPEC changed")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    observation_schema = json.loads(OBSERVATION_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(observation_schema)
    assert_strict_objects(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    observation_validator = Draft202012Validator(observation_schema, format_checker=FormatChecker())

    paths = sorted(EXAMPLE_DIRECTORY.glob("*.json"))
    require({path.name for path in paths} == set(EXPECTED_EXAMPLES), "expected exactly three Replay cases")
    contracts: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    for path in paths:
        contract = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(contract)
        require(
            contract["transformation_log"]["method"] == EXPECTED_EXAMPLES[path.name],
            f"{path.name}: transformation method",
        )
        require(contract["consent_status"] == "synthetic_declared_only", f"{path.name}: consent status")
        require(contract["data_use_permission_status"] == "synthetic_declared_only", f"{path.name}: permission status")
        require(contract["content_boundary"]["independently_verified"] is False, f"{path.name}: content verification")
        require(contract["transformation_log"]["provenance_verified"] is False, f"{path.name}: provenance verification")
        policy = contract["execution_policy"]
        require(policy["manual_start_required"] is True, f"{path.name}: manual control")
        for field in (
            "automatic_replay_allowed", "agent_execution_allowed", "tool_execution_allowed",
            "network_access_allowed", "deployment_action_allowed",
        ):
            require(policy[field] is False, f"{path.name}: execution policy {field}")
        boundary = contract["truth_boundary"]
        require(boundary["contract_only"] is True, f"{path.name}: contract marker")
        require(all(boundary[field] is False for field in FALSE_TRUTH_BOUNDARIES), f"{path.name}: truth boundary")
        reports.append(validate_replay_contract(contract, observation_validator))
        contracts.append(contract)

    base = contracts[0]
    schema_negatives = []
    extra = copy.deepcopy(base); extra["unexpected"] = True; schema_negatives.append(extra)
    no_consent = copy.deepcopy(base); no_consent.pop("consent_ref"); schema_negatives.append(no_consent)
    no_permission = copy.deepcopy(base); no_permission.pop("data_use_permission_ref"); schema_negatives.append(no_permission)
    no_transform = copy.deepcopy(base); no_transform.pop("transformation_log"); schema_negatives.append(no_transform)
    hidden = copy.deepcopy(base); hidden["content_boundary"]["hidden_reasoning_excluded"] = False; schema_negatives.append(hidden)
    cot = copy.deepcopy(base); cot["content_boundary"]["private_chain_of_thought_excluded"] = False; schema_negatives.append(cot)
    internal = copy.deepcopy(base); internal["content_boundary"]["internal_model_state_excluded"] = False; schema_negatives.append(internal)
    raw_prompt = copy.deepcopy(base); raw_prompt["content_boundary"]["raw_prompt_excluded"] = False; schema_negatives.append(raw_prompt)
    raw_output = copy.deepcopy(base); raw_output["content_boundary"]["raw_output_excluded"] = False; schema_negatives.append(raw_output)
    deploy = copy.deepcopy(base); deploy["truth_boundary"]["deployment_authorized"] = True; schema_negatives.append(deploy)
    auto = copy.deepcopy(base); auto["execution_policy"]["automatic_replay_allowed"] = True; schema_negatives.append(auto)
    execute = copy.deepcopy(base); execute["execution_policy"]["agent_execution_allowed"] = True; schema_negatives.append(execute)
    replayed = copy.deepcopy(base); replayed["truth_boundary"]["replay_executed"] = True; schema_negatives.append(replayed)
    require(all(not validator.is_valid(item) for item in schema_negatives), "schema accepted boundary negative")

    semantic_negatives: list[tuple[dict[str, Any], str]] = []
    missing_source = copy.deepcopy(base)
    missing_source["source_envelope_refs"][0]["envelope_ref"] = "agent-interface/architecture/examples/observation/missing.json"
    semantic_negatives.append((missing_source, "REPLAY_SOURCE_ENVELOPE_MISSING"))
    bad_digest = copy.deepcopy(base); bad_digest["source_envelope_refs"][0]["envelope_digest"] = "0" * 64
    semantic_negatives.append((bad_digest, "REPLAY_SOURCE_DIGEST_INVALID"))
    bad_id = copy.deepcopy(base); bad_id["source_envelope_refs"][0]["observation_id"] = "observation:mismatch"
    semantic_negatives.append((bad_id, "REPLAY_SOURCE_OBSERVATION_ID_MISMATCH"))
    bad_window = copy.deepcopy(base)
    bad_window["replay_window"] = {"starts_at": "2026-07-11T15:06:00Z", "ends_at": "2026-07-11T15:01:00Z"}
    semantic_negatives.append((bad_window, "REPLAY_WINDOW_INVALID"))
    for invalid, expected in semantic_negatives:
        try:
            validate_replay_contract(invalid, observation_validator)
        except ReplayContractError as exc:
            require(exc.code == expected, f"expected {expected}, got {exc.code}")
        else:
            raise ReplayContractError("REPLAY_NEGATIVE_ACCEPTED", expected)

    source_envelope = json.loads(
        (OBSERVATION_DIRECTORY / "synthetic-observation.json").read_text(encoding="utf-8")
    )
    for phrase in ("hidden reasoning", "private chain of thought", "internal model state", "raw prompt", "raw output"):
        invalid_envelope = copy.deepcopy(source_envelope)
        invalid_envelope["events"][0]["summary"] = f"Synthetic boundary probe containing {phrase}."
        try:
            validate_content_boundary(invalid_envelope)
        except ReplayContractError as exc:
            require(exc.code == "REPLAY_CONTENT_BOUNDARY_VIOLATION", phrase)
        else:
            raise ReplayContractError("REPLAY_CONTENT_NEGATIVE_ACCEPTED", phrase)

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    require(not imported_roots(Path(__file__)).intersection(forbidden), "smoke imports external capability")

    canonical = json.dumps(reports, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = [validate_replay_contract(contract, observation_validator) for contract in contracts]
        require(
            json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical,
            "Replay Contract validation is not deterministic",
        )

    print("SAEE_PHASE1_9_OBSERVATION_REPLAY_CONTRACT_SMOKE: PASS")
    print("schema_valid_cases=3/3")
    print("schema_negative_cases=13/13")
    print("semantic_negative_cases=4/4")
    print("content_boundary_negative_cases=5/5")
    print("source_envelopes_exist=3/3")
    print("source_digest_integrity=3/3")
    print("source_observation_id_integrity=3/3")
    print("consent_required=3/3")
    print("data_use_permission_required=3/3")
    print("transformation_provenance_required=3/3")
    print("hidden_reasoning_excluded=3/3")
    print("raw_prompt_excluded=3/3")
    print("raw_output_excluded=3/3")
    print("manual_control_required=3/3")
    print("no_execution_authority=3/3")
    print("no_deployment_authority=3/3")
    print("deterministic_runs=5/5")
    print("replay_executed=false")
    print("observation_schema_modified=false")
    print("evidence_case_schema_modified=false")
    print("final_architecture_modified=false")
    print("real_agent_connected=false")
    print("network_calls=0")
    print("customer_data_processed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
