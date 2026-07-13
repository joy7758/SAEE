#!/usr/bin/env python3
"""Offline smoke for SAEE Pilot Execution Readiness Review v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.pilot_readiness import (  # noqa: E402
    PilotReadinessError,
    evaluate_pilot_readiness,
)


MATRIX_PATH = ROOT / "agent-interface/evaluation/saee-pilot-readiness-review.v0.1.json"
REVIEW_PATH = ROOT / "docs/evaluation/SAEE_PILOT_EXECUTION_READINESS_REVIEW.md"
BOUNDARY_PATH = ROOT / "docs/evaluation/SAEE_PILOT_READINESS_BOUNDARIES.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PILOT_EXECUTION_READINESS_REVIEW_RECOMMENDATION_GATE.md"
CLI_PATH = ROOT / "scripts/saee_agent_cli.py"
SERVICE_PATH = ROOT / "saee_backend/services/pilot_readiness.py"


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AssertionError(detail)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def make_go(document: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(document)
    for dimension in candidate["dimensions"].values():
        dimension["status"] = "READY"
        for requirement in dimension["requirements"]:
            requirement["satisfied"] = True
            if not requirement["evidence_refs"]:
                requirement["evidence_refs"] = [f"synthetic:{requirement['requirement_id']}"]
    candidate["pilot_status"] = "ready"
    candidate["decision"] = "GO"
    candidate["decision_reason"] = "Synthetic in-memory decision-path fixture with all requirements satisfied."
    candidate["missing_requirements"] = []
    return candidate


def make_conditional(document: dict[str, Any]) -> dict[str, Any]:
    candidate = make_go(document)
    target = next(item for item in candidate["dimensions"]["dataset"]["requirements"] if item["requirement_id"] == "dataset_sample_available")
    target["satisfied"] = False
    target["evidence_refs"] = []
    candidate["dimensions"]["dataset"]["status"] = "NOT_READY"
    candidate["pilot_status"] = "conditionally_ready"
    candidate["decision"] = "CONDITIONAL_GO"
    candidate["decision_reason"] = "Synthetic in-memory conditional path with one explicitly deferrable non-critical item."
    candidate["missing_requirements"] = ["dataset_sample_available"]
    return candidate


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def main() -> None:
    require(MATRIX_PATH.is_file(), "readiness matrix missing")
    source = read_json(MATRIX_PATH)
    result = evaluate_pilot_readiness(copy.deepcopy(source))
    require(result["result_type"] == "SAEE_PILOT_READINESS_RESULT", "result type")
    require(result["decision"] == "NO_GO", "current decision must be NO_GO")
    require(result["pilot_status"] == "not_ready", "current pilot status")
    require(result["dimension_statuses"] == {"dataset": "NOT_READY", "privacy": "NOT_READY", "technical": "READY", "annotation": "NOT_READY", "safety": "READY"}, "dimension statuses")
    require(len(result["missing_requirements"]) == 11, "missing requirement count")
    require(result["execution_authorized_by_review"] is False, "review must not authorize execution")

    require(evaluate_pilot_readiness(make_go(source))["decision"] == "GO", "GO path")
    require(evaluate_pilot_readiness(make_conditional(source))["decision"] == "CONDITIONAL_GO", "CONDITIONAL_GO path")

    invalid_cases: list[tuple[dict[str, Any], str]] = []
    started = copy.deepcopy(source); started["execution_started"] = True; invalid_cases.append((started, "PILOT_EXECUTION_WITHOUT_APPROVAL"))
    externally_validated = copy.deepcopy(source); externally_validated["external_validation_completed"] = True; invalid_cases.append((externally_validated, "PILOT_EXTERNAL_VALIDATION_UNSUPPORTED"))
    wrong_decision = copy.deepcopy(source); wrong_decision["decision"] = "GO"; invalid_cases.append((wrong_decision, "PILOT_READINESS_DECLARED_DECISION_MISMATCH"))
    wrong_dimension = copy.deepcopy(source); wrong_dimension["dimensions"]["dataset"]["status"] = "READY"; invalid_cases.append((wrong_dimension, "PILOT_READINESS_DIMENSION_STATUS_MISMATCH"))
    for candidate, expected in invalid_cases:
        try:
            evaluate_pilot_readiness(candidate)
        except PilotReadinessError as exc:
            require(exc.code == expected, f"reason code: expected {expected}, got {exc.code}")
        else:
            raise AssertionError(f"invalid case accepted: {expected}")

    for path in (REVIEW_PATH, BOUNDARY_PATH, GATE_PATH):
        require(path.is_file(), f"document missing: {path}")
    review = REVIEW_PATH.read_text(encoding="utf-8")
    for section in range(1, 5):
        require(f"## {section} " in review, f"review section {section}")
    for label in ("Dataset Readiness", "Privacy and Governance Readiness", "Technical Readiness", "Annotation Readiness", "Safety Readiness"):
        require(label in review, f"dimension documentation: {label}")
    boundary = BOUNDARY_PATH.read_text(encoding="utf-8")
    require("Readiness review determines whether prerequisites are satisfied for a future pilot. It does not demonstrate that a pilot has been executed or validated." in boundary, "English boundary")
    require("就绪审查用于判断未来试点启动条件是否满足，不证明试点已经执行或完成验证。" in boundary, "Chinese boundary")
    require("review-pilot-readiness" in CLI_PATH.read_text(encoding="utf-8"), "CLI command")

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    for path in (Path(__file__), SERVICE_PATH):
        require(not imported_roots(path).intersection(forbidden), f"external capability import: {path}")

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = evaluate_pilot_readiness(copy.deepcopy(source))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "non-deterministic result")

    print("SAEE_PILOT_READINESS_SMOKE: PASS")
    print("valid_cases=3/3")
    print("invalid_cases=4/4")
    print("decision_paths=3/3")
    print("required_dimensions=5/5")
    print("missing_requirements=11/11")
    print("deterministic_runs=5/5")
    print("current_decision=NO_GO")
    print("execution_started=false")
    print("execution_authorized_by_review=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("experiment_executed=false")
    print("external_validation_completed=false")
    print("scientific_result_claimed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()

