#!/usr/bin/env python3
"""Offline integrity smoke for SAEE Pilot Dataset Specification v0.1."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "agent-interface/evaluation/dataset-specification"
MANIFEST_PATH = ROOT / "agent-interface/evaluation/saee-pilot-dataset-manifest.v0.1.json"
SPEC_PATH = ROOT / "docs/evaluation/SAEE_PILOT_DATASET_SPECIFICATION.md"
QUALITY_PATH = ROOT / "docs/evaluation/SAEE_DATASET_QUALITY_CONTROL.md"
READINESS_PATH = ROOT / "docs/evaluation/SAEE_DATASET_READINESS_CHECKLIST.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PILOT_DATASET_SPECIFICATION_RECOMMENDATION_GATE.md"

SCHEMA_PATHS = {
    "task": SCHEMA_DIR / "task-record.schema.json",
    "trace": SCHEMA_DIR / "trace-record.schema.json",
    "bundle": SCHEMA_DIR / "evidence-bundle.schema.json",
    "annotation": SCHEMA_DIR / "annotation-record.schema.json",
}

FALSE_BOUNDARIES = (
    "dataset_exists", "data_collected", "data_source_selected", "annotations_started",
    "annotations_completed", "external_data_used", "production_data_used",
    "personal_data_processed", "real_agent_executed", "experiment_executed",
    "external_validation_completed", "scientific_result_claimed", "production_ready",
)


class DatasetSpecificationError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise DatasetSpecificationError(code, detail)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(document: dict[str, Any]) -> dict[str, Any]:
    require(document.get("saee_pilot_dataset_manifest_v0_1") is True, "DATASET_IDENTITY_INVALID", "root marker")
    require(document.get("specification_version") == "0.1", "DATASET_VERSION_INVALID", "version")
    require(document.get("dataset_status") == "specification_only", "DATASET_STATUS_INVALID", "status")
    for field in FALSE_BOUNDARIES:
        require(document.get(field) is False, "DATASET_BOUNDARY_INVALID", f"{field} must be false")
    require(document.get("primary_unit") == "evidence_evaluation_episode", "DATASET_UNIT_INVALID", "primary unit")
    entities = document.get("entities")
    require(isinstance(entities, list) and len(entities) == 4, "DATASET_ENTITIES_INVALID", "four entities")
    require(len({item.get("entity_id") for item in entities}) == 4, "DATASET_ENTITIES_INVALID", "unique entities")
    for item in entities:
        require((ROOT / item["schema_ref"]).is_file(), "DATASET_SCHEMA_MISSING", item["schema_ref"])
    quality = document.get("quality_requirements")
    require(isinstance(quality, dict) and set(quality) == {"structural", "evidence_consistency", "annotation", "leakage_prevention"}, "DATASET_QUALITY_INVALID", "quality groups")
    readiness = document.get("readiness")
    require(isinstance(readiness, dict), "DATASET_READINESS_INVALID", "readiness")
    require(readiness.get("current_status") == "NOT_READY", "DATASET_READINESS_INVALID", "current status")
    require(readiness.get("ready_requires") == readiness.get("unmet_requirements"), "DATASET_READINESS_INVALID", "all requirements unmet")
    require(document.get("recommended_next_pr") == "Add SAEE Pilot Execution Readiness Review v0.1", "DATASET_NEXT_PR_INVALID", "next PR")
    return document


def synthetic_records() -> dict[str, dict[str, Any]]:
    digest_a = "a" * 64
    digest_b = "b" * 64
    episode = "episode-synthetic-001"
    task = {
        "saee_task_record_v0_1": True, "schema_version": "0.1.0", "episode_id": episode,
        "task_id": "task-synthetic-001", "task_description": "Inspect one synthetic local resource without execution.",
        "task_category": "resource_access", "risk_level": "low", "allowed_actions": ["inspect_metadata"],
        "constraints": ["no network", "no external execution"], "data_origin": "synthetic_controlled",
    }
    trace = {
        "saee_trace_record_v0_1": True, "schema_version": "0.1.0", "episode_id": episode,
        "trace_id": "trace-synthetic-001", "task_id": task["task_id"], "timestamp": "2026-01-01T00:00:00Z",
        "agent_action": {"agent_id": "agent-synthetic-001", "action_id": "action-synthetic-001", "action_type": "resource_access"},
        "tool_call": {"tool_call_id": "tool-call-synthetic-001", "tool_name": "metadata-reader", "parameter_digest": digest_a},
        "resource_reference": {"requested_resource": "pkg:synthetic-tool", "resolved_resource_ref": "resource-synthetic-001"},
        "status": "observed", "truth_boundary": {"trace_is_evidence": False, "event_authenticity_verified": False, "authorization_verified": False},
    }
    bundle = {
        "saee_evidence_bundle_record_v0_1": True, "schema_version": "0.1.0", "episode_id": episode,
        "evidence_bundle_id": "bundle-synthetic-001", "task_id": task["task_id"], "trace_refs": [trace["trace_id"]],
        "resource_receipts": ["receipt-synthetic-001"],
        "authorization_records": [{"authorization_id": "authorization-synthetic-001", "policy_decision_ref": "policy-synthetic-001", "action_ref": "action-synthetic-001", "decision": "allow", "scope": "inspect_metadata", "valid_from": "2026-01-01T00:00:00Z", "valid_until": "2026-01-01T00:10:00Z"}],
        "human_oversight_records": [{"oversight_id": "oversight-synthetic-001", "annotator_safe_identity_hash": digest_b, "action_ref": "action-synthetic-001", "decision": "not_applicable", "approved_scope": "inspect_metadata", "timestamp": "2026-01-01T00:00:00Z"}],
        "execution_effects": [{"effect_id": "effect-synthetic-001", "action_ref": "action-synthetic-001", "status": "denied_no_effect", "sandbox_ref": "sandbox-synthetic-001", "effect_digest": digest_a}],
        "causal_relationships": [{"relationship_id": "relationship-synthetic-001", "relationship_type": "action_to_authorization", "source_ref": "action-synthetic-001", "target_ref": "authorization-synthetic-001", "declared_status": "declared_valid"}],
        "limitations": ["Synthetic in-memory schema fixture only."],
    }
    annotation = {
        "saee_annotation_record_v0_1": True, "schema_version": "0.1.0", "episode_id": episode,
        "annotation_id": "annotation-synthetic-001", "evidence_bundle_ref": bundle["evidence_bundle_id"],
        "claim_type": "AUTHORIZED_AGENT_ACTION", "label": "SUPPORTED", "missing_evidence": [],
        "invalid_relationship": [], "annotator_id_hash": digest_a, "confidence": 0.8,
        "annotation_round": "primary", "uncertainty_reason": "",
    }
    return {"task": task, "trace": trace, "bundle": bundle, "annotation": annotation}


def validate_schema_contracts() -> None:
    records = synthetic_records()
    validators: dict[str, Draft202012Validator] = {}
    for name, path in SCHEMA_PATHS.items():
        schema = read_json(path)
        Draft202012Validator.check_schema(schema)
        require(schema.get("additionalProperties") is False, "DATASET_SCHEMA_NOT_STRICT", name)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        validator.validate(records[name])
        validators[name] = validator

    episode_ids = {record["episode_id"] for record in records.values()}
    require(len(episode_ids) == 1, "DATASET_EPISODE_LINK_INVALID", "episode ids")
    require(records["trace"]["task_id"] == records["task"]["task_id"], "DATASET_EPISODE_LINK_INVALID", "task ref")
    require(records["trace"]["trace_id"] in records["bundle"]["trace_refs"], "DATASET_EPISODE_LINK_INVALID", "trace ref")
    require(records["annotation"]["evidence_bundle_ref"] == records["bundle"]["evidence_bundle_id"], "DATASET_EPISODE_LINK_INVALID", "bundle ref")

    negatives = []
    extra = copy.deepcopy(records["task"]); extra["unexpected"] = True; negatives.append(("task", extra))
    trace_claim = copy.deepcopy(records["trace"]); trace_claim["truth_boundary"]["trace_is_evidence"] = True; negatives.append(("trace", trace_claim))
    supported_missing = copy.deepcopy(records["annotation"]); supported_missing["missing_evidence"] = ["/policy_decision_ref"]; negatives.append(("annotation", supported_missing))
    unknown_without_reason = copy.deepcopy(records["annotation"]); unknown_without_reason["label"] = "UNKNOWN"; negatives.append(("annotation", unknown_without_reason))
    for name, candidate in negatives:
        require(not validators[name].is_valid(candidate), "DATASET_SCHEMA_NEGATIVE_ACCEPTED", name)


def validate_documents(manifest: dict[str, Any]) -> None:
    for path in (SPEC_PATH, QUALITY_PATH, READINESS_PATH, GATE_PATH):
        require(path.is_file(), "DATASET_DOCUMENT_MISSING", str(path))
    for relative in manifest["documents"].values():
        require((ROOT / relative).is_file(), "DATASET_DOCUMENT_MISSING", relative)
    spec = SPEC_PATH.read_text(encoding="utf-8")
    for section in range(1, 10):
        require(f"## {section} " in spec, "DATASET_SECTION_MISSING", str(section))
    require("Trace records observations and are not evidence by themselves." in spec, "DATASET_TRACE_BOUNDARY_MISSING", "trace principle")
    quality = QUALITY_PATH.read_text(encoding="utf-8")
    for heading in ("Structural checks", "Evidence consistency checks", "Annotation quality", "Leakage prevention"):
        require(f"## {heading}" in quality, "DATASET_QUALITY_SECTION_MISSING", heading)
    readiness = READINESS_PATH.read_text(encoding="utf-8")
    require("当前状态：`NOT_READY`" in readiness, "DATASET_READINESS_INVALID", "checklist status")

    source = Path(__file__).read_text(encoding="utf-8")
    imports = {node.names[0].name.split(".")[0] for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Import)}
    imports.update(node.module.split(".")[0] for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ImportFrom) and node.module)
    require(not imports.intersection({"socket", "subprocess", "urllib", "requests", "httpx"}), "DATASET_EXTERNAL_CAPABILITY_IMPORT", "forbidden import")


def main() -> None:
    source = read_json(MANIFEST_PATH)
    validated = validate_manifest(copy.deepcopy(source))
    validate_schema_contracts()
    validate_documents(validated)

    invalid_cases: list[tuple[dict[str, Any], str]] = []
    wrong_status = copy.deepcopy(source); wrong_status["dataset_status"] = "ready"; invalid_cases.append((wrong_status, "DATASET_STATUS_INVALID"))
    exists = copy.deepcopy(source); exists["dataset_exists"] = True; invalid_cases.append((exists, "DATASET_BOUNDARY_INVALID"))
    ready = copy.deepcopy(source); ready["readiness"]["current_status"] = "READY"; invalid_cases.append((ready, "DATASET_READINESS_INVALID"))
    for candidate, expected in invalid_cases:
        try:
            validate_manifest(candidate)
        except DatasetSpecificationError as exc:
            require(exc.code == expected, "DATASET_REASON_CODE_UNSTABLE", f"{expected}/{exc.code}")
        else:
            raise DatasetSpecificationError("DATASET_NEGATIVE_ACCEPTED", expected)

    canonical = json.dumps(validate_manifest(copy.deepcopy(source)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = json.dumps(validate_manifest(copy.deepcopy(source)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        require(repeated == canonical, "DATASET_NON_DETERMINISTIC", "manifest validation")

    print("SAEE_DATASET_SPECIFICATION_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=3/3")
    print("schema_valid_cases=4/4")
    print("schema_negative_cases=4/4")
    print("entity_types=4/4")
    print("deterministic_runs=5/5")
    print("dataset_status=specification_only")
    print("current_readiness=NOT_READY")
    print("dataset_exists=false")
    print("data_collected=false")
    print("annotations_completed=false")
    print("external_data_used=false")
    print("production_data_used=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("external_validation_completed=false")
    print("scientific_result_claimed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()

