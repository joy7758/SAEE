#!/usr/bin/env python3
"""Offline boundary smoke for SAEE External Evaluation Pilot Preparation v0.1."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "agent-interface/evaluation/saee-pilot-preparation.v0.1.json"
PREPARATION_PATH = ROOT / "docs/evaluation/SAEE_EXTERNAL_EVALUATION_PILOT_PREPARATION.md"
CODEBOOK_PATH = ROOT / "docs/evaluation/SAEE_ANNOTATION_CODEBOOK.md"
PRIVACY_PATH = ROOT / "docs/evaluation/SAEE_PILOT_PRIVACY_CHECKLIST.md"
SAFETY_PATH = ROOT / "docs/evaluation/SAEE_PILOT_EXECUTION_SAFETY_GATE.md"
RECOMMENDATION_PATH = ROOT / "docs/strategy/SAEE_EXTERNAL_EVALUATION_PILOT_PREPARATION_RECOMMENDATION_GATE.md"

FALSE_BOUNDARIES = (
    "pilot_executed",
    "dataset_collected",
    "data_source_selected",
    "real_agent_executed",
    "annotations_started",
    "annotations_completed",
    "annotators_recruited",
    "personal_data_processed",
    "network_accessed",
    "subprocess_started",
    "external_code_executed",
    "external_validation_completed",
    "scientific_result_claimed",
    "production_ready",
)

REQUIRED_LABELS = {
    "SUPPORTED",
    "INSUFFICIENT_EVIDENCE",
    "INVALID_RELATIONSHIP",
    "UNKNOWN",
}


class PreparationError(ValueError):
    """Stable preparation validation failure."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise PreparationError(code, detail)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_metadata(document: dict[str, Any]) -> dict[str, Any]:
    require(document.get("saee_pilot_preparation_v0_1") is True, "PILOT_IDENTITY_INVALID", "root marker")
    require(document.get("preparation_version") == "0.1", "PILOT_VERSION_INVALID", "version must be 0.1")
    require(document.get("status") == "preparation_only", "PILOT_STATUS_INVALID", "status must remain preparation_only")
    for field in FALSE_BOUNDARIES:
        require(document.get(field) is False, "PILOT_EXECUTION_BOUNDARY_INVALID", f"{field} must be false")

    scenario = document.get("scenario")
    require(isinstance(scenario, dict), "PILOT_SCENARIO_INVALID", "scenario object required")
    require(scenario.get("scenario_id") == "code_agent_tool_execution", "PILOT_SCENARIO_INVALID", "scenario id")
    require(scenario.get("status") == "proposed_not_executed", "PILOT_SCENARIO_INVALID", "scenario status")

    inputs = document.get("required_inputs")
    require(isinstance(inputs, list) and len(inputs) == 7, "PILOT_INPUTS_INVALID", "seven required inputs")
    require(all(item.get("required_fields") for item in inputs), "PILOT_INPUTS_INVALID", "required fields missing")

    options = document.get("data_source_options")
    require(isinstance(options, list) and len(options) == 3, "PILOT_SOURCE_OPTIONS_INVALID", "three source options")
    require(all(item.get("status") == "option_not_selected" for item in options), "PILOT_SOURCE_SELECTED", "no source may be selected")

    annotation = document.get("annotation_protocol")
    require(isinstance(annotation, dict), "PILOT_ANNOTATION_INVALID", "annotation protocol required")
    require(set(annotation.get("labels", [])) == REQUIRED_LABELS, "PILOT_ANNOTATION_INVALID", "label set")
    require(annotation.get("status") == "draft_not_approved_not_started", "PILOT_ANNOTATION_INVALID", "annotation status")

    readiness = document.get("readiness_criteria")
    require(isinstance(readiness, dict), "PILOT_READINESS_INVALID", "readiness object required")
    require(readiness.get("current_assessment") == "NOT_READY", "PILOT_READINESS_INVALID", "current assessment")
    require(len(readiness.get("ready_requires", [])) >= 5, "PILOT_READINESS_INVALID", "ready requirements")
    require(readiness.get("unmet_requirements") == readiness.get("ready_requires"), "PILOT_READINESS_INVALID", "all requirements remain unmet")

    require(document.get("recommended_next_pr") == "Add SAEE Pilot Dataset Specification v0.1", "PILOT_NEXT_PR_INVALID", "next PR")
    return document


def validate_documents(document: dict[str, Any]) -> None:
    paths = [PREPARATION_PATH, CODEBOOK_PATH, PRIVACY_PATH, SAFETY_PATH, RECOMMENDATION_PATH]
    require(all(path.is_file() for path in paths), "PILOT_DOCUMENT_MISSING", "required document")

    preparation = PREPARATION_PATH.read_text(encoding="utf-8")
    for number in range(1, 10):
        require(f"## {number} " in preparation, "PILOT_SECTION_MISSING", f"section {number}")
    require("当前评估为 `NOT_READY`" in preparation, "PILOT_READINESS_INVALID", "explicit current boundary")

    codebook = CODEBOOK_PATH.read_text(encoding="utf-8")
    for label in REQUIRED_LABELS:
        require(f"`{label}`" in codebook, "PILOT_CODEBOOK_INVALID", label)
    for token in ("定义", "正例", "反例", "决策规则"):
        require(codebook.count(token) >= 4, "PILOT_CODEBOOK_INVALID", token)

    privacy = PRIVACY_PATH.read_text(encoding="utf-8")
    for token in ("Data ownership", "Consent requirements", "Personal data handling", "Sensitive information review", "Retention policy", "Deletion process", "Access control", "Audit record"):
        require(token in privacy, "PILOT_PRIVACY_CHECKLIST_INVALID", token)

    safety = SAFETY_PATH.read_text(encoding="utf-8")
    for token in ("数据权限", "未知外部代码", "不受控网络", "审计轨迹", "人工监督", "无法用固定环境"):
        require(token in safety, "PILOT_SAFETY_GATE_INVALID", token)
    require("状态：`stop`" in safety, "PILOT_SAFETY_GATE_INVALID", "stop status")

    for key, relative in document["documents"].items():
        require((ROOT / relative).is_file(), "PILOT_DOCUMENT_MISSING", key)

    forbidden_affirmations = (
        '"pilot_executed": true',
        '"dataset_collected": true',
        '"annotations_completed": true',
        '"external_validation_completed": true',
        '"scientific_result_claimed": true',
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    require(not any(token in combined for token in forbidden_affirmations), "PILOT_UNSUPPORTED_CLAIM", "affirmative result claim")


def main() -> None:
    source = read_json(METADATA_PATH)
    validated = validate_metadata(copy.deepcopy(source))
    validate_documents(validated)

    invalid_cases: list[tuple[dict[str, Any], str]] = []
    wrong_status = copy.deepcopy(source)
    wrong_status["status"] = "ready"
    invalid_cases.append((wrong_status, "PILOT_STATUS_INVALID"))
    executed = copy.deepcopy(source)
    executed["pilot_executed"] = True
    invalid_cases.append((executed, "PILOT_EXECUTION_BOUNDARY_INVALID"))
    ready = copy.deepcopy(source)
    ready["readiness_criteria"]["current_assessment"] = "READY"
    invalid_cases.append((ready, "PILOT_READINESS_INVALID"))

    for candidate, expected_code in invalid_cases:
        try:
            validate_metadata(candidate)
        except PreparationError as exc:
            require(exc.code == expected_code, "PILOT_REASON_CODE_UNSTABLE", f"expected {expected_code}, got {exc.code}")
        else:
            raise PreparationError("PILOT_NEGATIVE_ACCEPTED", expected_code)

    canonical = json.dumps(validate_metadata(copy.deepcopy(source)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = json.dumps(validate_metadata(copy.deepcopy(source)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        require(repeated == canonical, "PILOT_NON_DETERMINISTIC", "metadata validation drift")

    print("SAEE_PILOT_PREPARATION_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=3/3")
    print("deterministic_runs=5/5")
    print("required_sections=9/9")
    print("required_inputs=7/7")
    print("data_source_options=3/3")
    print("annotation_labels=4/4")
    print("checklist_documents=3/3")
    print("current_readiness=NOT_READY")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("pilot_executed=false")
    print("dataset_collected=false")
    print("annotations_completed=false")
    print("external_validation_completed=false")
    print("scientific_result_claimed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()

