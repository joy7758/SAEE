#!/usr/bin/env python3
"""Validate the SAEE external-evaluation design without running experiments."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "agent-interface/evaluation/saee-external-evaluation-design.v0.1.json"
DESIGN_PATH = ROOT / "docs/evaluation/SAEE_EXTERNAL_EVALUATION_DESIGN.md"
BOUNDARY_PATH = ROOT / "docs/evaluation/EVALUATION_CLAIMS_BOUNDARY.md"
MAKEFILE_PATH = ROOT / "Makefile"
ROOT_KEYS = {
    "saee_external_evaluation_design_v0_1",
    "evaluation_version",
    "status",
    "research_objective",
    "research_questions",
    "scenarios",
    "evidence_conditions",
    "baselines",
    "metrics",
    "dataset_requirements",
    "annotation_protocol",
    "execution_phases",
    "references",
    "limitations",
    "claims_supported",
    "executed",
    "external_data_used",
    "real_agents_run",
    "opentelemetry_collectors_run",
    "external_code_executed",
    "external_validation_completed",
    "truth_boundary",
    "recommended_next_pr",
}
RESEARCH_QUESTIONS = {"RQ1", "RQ2", "RQ3"}
CONDITIONS = {
    "A_TRACE_ONLY",
    "B_TRACE_RECEIPT",
    "C_TRACE_RECEIPT_RELATIONSHIPS",
    "D_COMPLETE_SAEE_PACKAGE",
}
BASELINES = {
    "A_OBSERVABILITY_ONLY",
    "B_RECEIPT_LOG_BASED",
    "C_SAEE_ADEQUACY",
}
METRICS = {
    "FALSE_ACCOUNTABILITY_RATE",
    "MISSING_EVIDENCE_IDENTIFICATION_ACCURACY",
    "CLAIM_SUPPORT_COVERAGE",
    "EVIDENCE_RELATIONSHIP_COMPLETENESS",
}
PHASES = {
    "PHASE_1_DATASET_PREPARATION",
    "PHASE_2_BASELINE_IMPLEMENTATION",
    "PHASE_3_SAEE_EVALUATION",
    "PHASE_4_INDEPENDENT_VALIDATION",
}
REQUIRED_SECTIONS = {
    "## 1 Research Objective",
    "## 2 Research Questions",
    "## 3 Evaluation Scenario",
    "## 4 Evidence Conditions",
    "## 5 Baselines",
    "## 6 Metrics",
    "## 7 Dataset Requirements",
    "## 8 Annotation Protocol",
    "## 9 Threats to Validity",
    "## 10 Future Execution Plan",
}
TRUTH_KEYS = {
    "dataset_collected",
    "baseline_implemented",
    "experiment_executed",
    "results_available",
    "external_validation_completed",
    "independent_validation_completed",
    "benchmark_superiority_claimed",
    "production_effectiveness_claimed",
    "regulatory_evidence_claimed",
    "paper_submitted",
    "production_ready",
}
FORBIDDEN_SENTENCES = {
    "SAEE has been externally validated.",
    "SAEE improves production systems.",
    "SAEE outperforms other systems.",
    "External datasets have been evaluated.",
    "Baseline comparison completed.",
    "Evaluation completed.",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def validate_metadata(value: Any, *, check_paths: bool = True) -> list[str]:
    if not isinstance(value, dict) or set(value) != ROOT_KEYS:
        return ["EVALUATION_ROOT_FIELDS_INVALID"]
    errors: list[str] = []
    if (
        value.get("saee_external_evaluation_design_v0_1") is not True
        or value.get("evaluation_version") != "0.1"
        or value.get("status") != "design_only"
        or value.get("claims_supported") != ["evaluation_protocol_defined"]
        or value.get("recommended_next_pr") != "Implement SAEE Evaluation Prototype v0.1"
    ):
        errors.append("EVALUATION_STATUS_INVALID")
    false_flags = (
        "executed",
        "external_data_used",
        "real_agents_run",
        "opentelemetry_collectors_run",
        "external_code_executed",
        "external_validation_completed",
    )
    truth = value.get("truth_boundary")
    if (
        any(value.get(key) is not False for key in false_flags)
        or not isinstance(truth, dict)
        or set(truth) != TRUTH_KEYS
        or any(flag is not False for flag in truth.values())
    ):
        errors.append("EVALUATION_TRUTH_BOUNDARY_INVALID")
    questions = value.get("research_questions")
    if not isinstance(questions, list) or {item.get("rq_id") for item in questions if isinstance(item, dict)} != RESEARCH_QUESTIONS:
        errors.append("EVALUATION_RESEARCH_QUESTIONS_INVALID")
    scenarios = value.get("scenarios")
    if (
        not isinstance(scenarios, list)
        or len(scenarios) != 1
        or scenarios[0].get("scenario_id") != "code_agent_tool_execution"
        or scenarios[0].get("status") != "planned_not_executed"
    ):
        errors.append("EVALUATION_SCENARIO_INVALID")
    conditions = value.get("evidence_conditions")
    if not isinstance(conditions, list) or {item.get("condition_id") for item in conditions if isinstance(item, dict)} != CONDITIONS:
        errors.append("EVALUATION_CONDITIONS_INVALID")
    baselines = value.get("baselines")
    if (
        not isinstance(baselines, list)
        or {item.get("baseline_id") for item in baselines if isinstance(item, dict)} != BASELINES
        or any("not_implemented" not in item.get("status", "") and "not_executed" not in item.get("status", "") for item in baselines)
    ):
        errors.append("EVALUATION_BASELINES_INVALID")
    metrics = value.get("metrics")
    if (
        not isinstance(metrics, list)
        or {item.get("metric_id") for item in metrics if isinstance(item, dict)} != METRICS
        or any(not item.get("formula") or not item.get("interpretation_boundary") for item in metrics if isinstance(item, dict))
    ):
        errors.append("EVALUATION_METRICS_INVALID")
    phases = value.get("execution_phases")
    if (
        not isinstance(phases, list)
        or {item.get("phase_id") for item in phases if isinstance(item, dict)} != PHASES
        or any(item.get("status") != "planned_not_started" for item in phases if isinstance(item, dict))
    ):
        errors.append("EVALUATION_PHASES_INVALID")
    annotation = value.get("annotation_protocol")
    if (
        not isinstance(annotation, dict)
        or annotation.get("status") != "designed_not_executed"
        or annotation.get("annotators_per_item") != 2
        or annotation.get("independent_first_pass") is not True
        or annotation.get("adjudicator_required_for_disagreement") is not True
    ):
        errors.append("EVALUATION_ANNOTATION_PROTOCOL_INVALID")
    dataset = value.get("dataset_requirements")
    if not isinstance(dataset, dict) or dataset.get("acquisition_status") != "not_started":
        errors.append("EVALUATION_DATASET_STATUS_INVALID")
    if not isinstance(value.get("limitations"), list) or len(value["limitations"]) < 6:
        errors.append("EVALUATION_LIMITATIONS_INVALID")
    if check_paths:
        references = value.get("references")
        if not isinstance(references, list) or not references or not all(
            isinstance(path, str) and path and not path.startswith("/") and ".." not in Path(path).parts and (ROOT / path).is_file()
            for path in references
        ):
            errors.append("EVALUATION_REFERENCE_INVALID")
    return errors


def unsupported_claims(*texts: str) -> list[str]:
    corpus = "\n".join(texts)
    return sorted(sentence for sentence in FORBIDDEN_SENTENCES if sentence in corpus)


def main() -> None:
    metadata = read_json(METADATA_PATH)
    design = DESIGN_PATH.read_text(encoding="utf-8")
    boundary = BOUNDARY_PATH.read_text(encoding="utf-8")
    require(validate_metadata(metadata) == [], "valid evaluation design rejected")
    require(REQUIRED_SECTIONS.issubset(set(design.splitlines())), "required design section missing")
    require(unsupported_claims(json.dumps(metadata), design, boundary) == [], "unsupported result claim found")

    completed = copy.deepcopy(metadata)
    completed["status"] = "completed"
    require(
        validate_metadata(completed, check_paths=False) == ["EVALUATION_STATUS_INVALID"],
        "completed-status negative case",
    )
    missing_metric = copy.deepcopy(metadata)
    missing_metric["metrics"] = missing_metric["metrics"][:-1]
    require(
        validate_metadata(missing_metric, check_paths=False) == ["EVALUATION_METRICS_INVALID"],
        "missing-metric negative case",
    )
    external_validation = copy.deepcopy(metadata)
    external_validation["external_validation_completed"] = True
    require(
        validate_metadata(external_validation, check_paths=False) == ["EVALUATION_TRUTH_BOUNDARY_INVALID"],
        "external-validation negative case",
    )

    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    require("check-saee-evaluation-design:" in makefile, "evaluation design Makefile target missing")
    for marker in (
        "status=design_only",
        "executed=false",
        "external_data_used=false",
        "results_available=false",
        "external_validation_completed=false",
        "production_ready=false",
    ):
        require(marker in design or marker in boundary, f"truth marker missing: {marker}")
    require("inter-annotator agreement" in design.lower(), "agreement requirement missing")

    canonical = json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        current = read_json(METADATA_PATH)
        require(validate_metadata(current) == [], "deterministic metadata validation")
        require(
            json.dumps(current, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical,
            "deterministic metadata",
        )

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    require(
        not imported_roots.intersection({"subprocess", "socket", "requests", "httpx", "urllib"}),
        "forbidden external capability import",
    )

    print("SAEE_EVALUATION_DESIGN_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=3/3")
    print("deterministic_runs=5/5")
    print("required_sections=10/10")
    print("research_questions=3/3")
    print("evidence_conditions=4/4")
    print("baselines=3/3")
    print("primary_metrics=4/4")
    print(f"artifact_references={len(metadata['references'])}/{len(metadata['references'])}")
    print("unsupported_claims=0")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("dataset_collected=false")
    print("experiment_executed=false")
    print("results_available=false")
    print("external_validation_completed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
