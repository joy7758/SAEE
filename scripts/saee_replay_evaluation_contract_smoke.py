#!/usr/bin/env python3
"""Offline lineage and boundary gate for SAEE Phase 1.95 contracts."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-replay-evaluation-contract.v0.1.schema.json"
EXAMPLE_DIRECTORY = ROOT / "agent-interface/architecture/examples/replay-evaluation"
REPLAY_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json"
OBSERVATION_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json"
EVIDENCE_CASE_SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json"
FINAL_ARCHITECTURE_PATH = ROOT / "docs/architecture/FINAL_ARCHITECTURE_SPEC.md"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE1_95_REPLAY_EVALUATION_CONTRACT.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE1_95_REPLAY_EVALUATION_CONTRACT_RECOMMENDATION_GATE.md"

OBSERVATION_SCHEMA_SHA256 = "5e46e58163c14e6e9d7013c227cbc177cade5ec76c67d667fccdbafb9790cdd2"
EVIDENCE_CASE_SCHEMA_SHA256 = "e99ece1b5e37291775e344d871d6223089c84bd11065e7ef0f0fcfab353b121e"
REPLAY_SCHEMA_SHA256 = "aa7fcdcf7908a1f6f2bcd530ba7a8edfab1aa41d32fa964c422680dd36f61db1"
FINAL_ARCHITECTURE_SHA256 = "60f1e8c71172f8f8c214a57bdf2ac2162483e5eccd14b838c226cc89ede649a3"

EXPECTED_EXAMPLES = {
    "synthetic-replay-evaluation.json",
    "transformed-replay-evaluation.json",
    "consent-bound-replay-evaluation.json",
}

FALSE_BOUNDARIES = (
    "mapping_executed",
    "evaluation_input_generated",
    "replay_executed",
    "replay_generated_risk",
    "risk_probability_measured",
    "automatic_decision",
    "deployment_authorized",
    "architecture_implemented",
    "risk_model_implemented",
    "real_agent_executed",
    "customer_data_processed",
    "external_validation_completed",
    "customer_validated",
    "production_ready",
)


class ReplayEvaluationContractError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_CHECK_FAILED", detail)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def resolve_allowlisted(ref: str, directory: Path, code: str) -> Path:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(directory.resolve())
    except ValueError as exc:
        raise ReplayEvaluationContractError(code, ref) from exc
    if not path.is_file():
        raise ReplayEvaluationContractError(code, ref)
    return path


def required_lineage_edges(contract: dict[str, Any], replay_id: str, case_id: str) -> set[tuple[str, str, str, str, str]]:
    observation_ids = {item["observation_id"] for item in contract["source_observation_refs"]}
    required = {
        ("replay_contract", replay_id, "replay_evaluation_contract", contract["replay_evaluation_id"], "mapped_by"),
        ("replay_evaluation_contract", contract["replay_evaluation_id"], "evaluation_input", case_id, "binds_to"),
        ("evaluation_input", case_id, "derived_evidence_case", case_id, "derives_to"),
        ("derived_evidence_case", case_id, "evaluation_input", case_id, "reverse_lookup_anchor"),
    }
    required.update(
        ("observation_envelope", observation_id, "replay_contract", replay_id, "governed_by")
        for observation_id in observation_ids
    )
    return required


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    replay_path = resolve_allowlisted(
        contract["replay_contract_ref"],
        ROOT / "agent-interface/architecture/examples/replay",
        "REPLAY_EVALUATION_REPLAY_REF_INVALID",
    )
    if sha256_path(replay_path) != contract["replay_contract_digest"]:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_REPLAY_DIGEST_INVALID", contract["replay_evaluation_id"])
    replay = json.loads(replay_path.read_text(encoding="utf-8"))

    evaluation_input_path = resolve_allowlisted(
        contract["evaluation_input_ref"],
        ROOT / "agent-interface/architecture/examples/phase1_5_cases",
        "REPLAY_EVALUATION_INPUT_REF_INVALID",
    )
    if sha256_path(evaluation_input_path) != contract["evaluation_input_digest"]:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_INPUT_DIGEST_INVALID", contract["replay_evaluation_id"])
    evaluation_input = json.loads(evaluation_input_path.read_text(encoding="utf-8"))

    replay_sources = {
        (item["observation_id"], item["envelope_ref"], item["envelope_digest"])
        for item in replay["source_envelope_refs"]
    }
    contract_sources = {
        (item["observation_id"], item["envelope_ref"], item["envelope_digest"])
        for item in contract["source_observation_refs"]
    }
    if contract_sources != replay_sources:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_SOURCE_LINEAGE_MISMATCH", contract["replay_evaluation_id"])
    for source in contract["source_observation_refs"]:
        envelope_path = resolve_allowlisted(
            source["envelope_ref"],
            ROOT / "agent-interface/architecture/examples/observation",
            "REPLAY_EVALUATION_OBSERVATION_REF_INVALID",
        )
        if sha256_path(envelope_path) != source["envelope_digest"]:
            raise ReplayEvaluationContractError("REPLAY_EVALUATION_OBSERVATION_DIGEST_INVALID", source["observation_id"])

    if contract["consent_ref"] != replay["consent_ref"]:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_CONSENT_PROPAGATION_INVALID", contract["replay_evaluation_id"])
    if contract["data_use_permission_ref"] != replay["data_use_permission_ref"]:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_PERMISSION_PROPAGATION_INVALID", contract["replay_evaluation_id"])
    if contract["transformation_provenance_ref"] != replay["transformation_log"]["provenance_ref"]:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_PROVENANCE_PROPAGATION_INVALID", contract["replay_evaluation_id"])
    if contract["task_contract_ref"] != evaluation_input["task_contract"]["task_contract_id"]:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_TASK_BINDING_INVALID", contract["replay_evaluation_id"])
    if contract["environment_contract_ref"] != evaluation_input["environment_contract"]["environment_contract_id"]:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_ENVIRONMENT_BINDING_INVALID", contract["replay_evaluation_id"])

    source_ids = {item["observation_id"] for item in contract["source_observation_refs"]}
    if any(rule["source_observation_id"] not in source_ids for rule in contract["observation_mapping_rules"]):
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_MAPPING_SOURCE_UNBOUND", contract["replay_evaluation_id"])

    actual_edges = {
        (edge["from_type"], edge["from_ref"], edge["to_type"], edge["to_ref"], edge["relationship"])
        for edge in contract["lineage_edges"]
    }
    required_edges = required_lineage_edges(contract, replay["replay_id"], evaluation_input["case_id"])
    if not required_edges.issubset(actual_edges):
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_LINEAGE_INCOMPLETE", contract["replay_evaluation_id"])

    from saee_backend.services.saee_evidence_case import run_assurance_case_path

    derived = run_assurance_case_path(evaluation_input_path)["evidence_case_object"]
    if derived["identity"]["case_id"] != evaluation_input["case_id"]:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_DERIVED_CASE_UNBOUND", contract["replay_evaluation_id"])
    if json.dumps(derived, sort_keys=True).find(contract["replay_evaluation_id"]) >= 0:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_FROZEN_CASE_MUTATED", contract["replay_evaluation_id"])

    boundary = contract["truth_boundary"]
    require(boundary["contract_only"] is True, f"{contract['replay_evaluation_id']}: contract marker")
    require(all(boundary[field] is False for field in FALSE_BOUNDARIES), f"{contract['replay_evaluation_id']}: truth boundary")
    source = contract["failure_estimate_source"]
    require(source["source_type"] == "synthetic_rule_reference", "failure source type")
    require(source["source_ref"] == contract["task_contract_ref"], "failure source is not task-bound")
    require(source["generated_from_trace"] is False, "trace generated estimate")
    require(source["generated_by_replay"] is False, "Replay generated estimate")
    require(source["risk_probability_measured"] is False, "probability measurement claim")

    return {
        "replay_evaluation_id": contract["replay_evaluation_id"],
        "replay_id": replay["replay_id"],
        "evaluation_input_id": evaluation_input["case_id"],
        "derived_case_id": derived["identity"]["case_id"],
        "lineage_complete": True,
        "consent_propagated": True,
        "permission_propagated": True,
        "transformation_provenance_propagated": True,
        "replay_executed": False,
        "risk_generated": False,
        "deployment_authorized": False,
    }


def assert_semantic_negative(contract: dict[str, Any], expected_code: str) -> None:
    try:
        validate_contract(contract)
    except ReplayEvaluationContractError as exc:
        require(exc.code == expected_code, f"expected {expected_code}, got {exc.code}")
    else:
        raise ReplayEvaluationContractError("REPLAY_EVALUATION_NEGATIVE_ACCEPTED", expected_code)


def main() -> None:
    for path in (
        SCHEMA_PATH,
        EXAMPLE_DIRECTORY,
        REPLAY_SCHEMA_PATH,
        OBSERVATION_SCHEMA_PATH,
        EVIDENCE_CASE_SCHEMA_PATH,
        FINAL_ARCHITECTURE_PATH,
        DOC_PATH,
        GATE_PATH,
    ):
        require(path.exists(), f"missing required path: {path}")

    require(sha256_path(OBSERVATION_SCHEMA_PATH) == OBSERVATION_SCHEMA_SHA256, "Observation Envelope v0.1 changed")
    require(sha256_path(EVIDENCE_CASE_SCHEMA_PATH) == EVIDENCE_CASE_SCHEMA_SHA256, "Evidence Case v0.1 changed")
    require(sha256_path(REPLAY_SCHEMA_PATH) == REPLAY_SCHEMA_SHA256, "Replay Contract v0.1 changed")
    require(sha256_path(FINAL_ARCHITECTURE_PATH) == FINAL_ARCHITECTURE_SHA256, "FINAL_ARCHITECTURE_SPEC changed")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    replay_schema = json.loads(REPLAY_SCHEMA_PATH.read_text(encoding="utf-8"))
    evidence_case_schema = json.loads(EVIDENCE_CASE_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert_strict_objects(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    replay_validator = Draft202012Validator(replay_schema, format_checker=FormatChecker())
    evidence_case_validator = Draft202012Validator(evidence_case_schema, format_checker=FormatChecker())

    paths = sorted(EXAMPLE_DIRECTORY.glob("*.json"))
    require({path.name for path in paths} == EXPECTED_EXAMPLES, "expected exactly three Phase 1.95 examples")
    contracts: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []
    for path in paths:
        contract = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(contract)
        replay = json.loads((ROOT / contract["replay_contract_ref"]).read_text(encoding="utf-8"))
        evaluation_input = json.loads((ROOT / contract["evaluation_input_ref"]).read_text(encoding="utf-8"))
        replay_validator.validate(replay)
        evidence_case_validator.validate(evaluation_input)
        reports.append(validate_contract(contract))
        contracts.append(contract)

    base = contracts[0]
    schema_negatives = []
    no_consent = copy.deepcopy(base); no_consent.pop("consent_ref"); schema_negatives.append(no_consent)
    no_provenance = copy.deepcopy(base); no_provenance.pop("transformation_provenance_ref"); schema_negatives.append(no_provenance)
    no_input = copy.deepcopy(base); no_input.pop("evaluation_input_ref"); schema_negatives.append(no_input)
    replay_risk = copy.deepcopy(base); replay_risk["truth_boundary"]["replay_generated_risk"] = True; schema_negatives.append(replay_risk)
    deployment = copy.deepcopy(base); deployment["truth_boundary"]["deployment_authorized"] = True; schema_negatives.append(deployment)
    auto = copy.deepcopy(base); auto["truth_boundary"]["automatic_decision"] = True; schema_negatives.append(auto)
    measured = copy.deepcopy(base); measured["failure_estimate_source"]["risk_probability_measured"] = True; schema_negatives.append(measured)
    executable = copy.deepcopy(base); executable["observation_mapping_rules"][0]["executable"] = True; schema_negatives.append(executable)
    extra = copy.deepcopy(base); extra["unexpected"] = True; schema_negatives.append(extra)
    require(all(not validator.is_valid(item) for item in schema_negatives), "schema accepted a boundary negative")

    bad_consent = copy.deepcopy(base); bad_consent["consent_ref"] = "consent:mismatch"
    assert_semantic_negative(bad_consent, "REPLAY_EVALUATION_CONSENT_PROPAGATION_INVALID")
    bad_provenance = copy.deepcopy(base); bad_provenance["transformation_provenance_ref"] = "provenance:mismatch"
    assert_semantic_negative(bad_provenance, "REPLAY_EVALUATION_PROVENANCE_PROPAGATION_INVALID")
    bad_digest = copy.deepcopy(base); bad_digest["evaluation_input_digest"] = "0" * 64
    assert_semantic_negative(bad_digest, "REPLAY_EVALUATION_INPUT_DIGEST_INVALID")
    bad_lineage = copy.deepcopy(base); bad_lineage["lineage_edges"] = bad_lineage["lineage_edges"][:-1]
    assert_semantic_negative(bad_lineage, "REPLAY_EVALUATION_LINEAGE_INCOMPLETE")
    bad_source = copy.deepcopy(base); bad_source["source_observation_refs"][0]["observation_id"] = "observation:mismatch"
    assert_semantic_negative(bad_source, "REPLAY_EVALUATION_SOURCE_LINEAGE_MISMATCH")

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    require(not imported_roots(Path(__file__)).intersection(forbidden), "smoke imports external capability")
    canonical = json.dumps(reports, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = [validate_contract(contract) for contract in contracts]
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "non-deterministic result")

    print("SAEE_PHASE1_95_REPLAY_EVALUATION_CONTRACT_SMOKE: PASS")
    print("schema_valid_cases=3/3")
    print("schema_negative_cases=9/9")
    print("semantic_negative_cases=5/5")
    print("replay_contract_digest_integrity=3/3")
    print("evaluation_input_digest_integrity=3/3")
    print("source_observation_lineage=3/3")
    print("consent_propagation=3/3")
    print("data_use_permission_propagation=3/3")
    print("transformation_provenance_propagation=3/3")
    print("five_layer_lineage_integrity=3/3")
    print("derived_case_reverse_lookup=3/3")
    print("deterministic_runs=5/5")
    print("replay_risk_generation=false")
    print("automatic_decision=false")
    print("deployment_authorized=false")
    print("architecture_implemented=false")
    print("risk_model_implemented=false")
    print("real_agent_executed=false")
    print("network_calls=0")
    print("customer_data_processed=false")
    print("production_ready=false")
    print("observation_schema_modified=false")
    print("evidence_case_schema_modified=false")
    print("replay_contract_schema_modified=false")
    print("final_architecture_modified=false")


if __name__ == "__main__":
    main()
