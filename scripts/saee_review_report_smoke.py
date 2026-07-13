#!/usr/bin/env python3
"""Offline deterministic checks for the local synthetic evidence review report prototype."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.review_report_generator import (
    ReviewReportError,
    generate_review_report,
    load_json,
    render_review_report_markdown,
    validate_report,
)


SCHEMA_PATH = ROOT / "agent-interface/commercial/saee-evidence-review-report.schema.json"
CASE_PATH = ROOT / "agent-interface/commercial/review-cases/synthetic-code-agent-review-case.json"
SERVICE_PATH = ROOT / "saee_backend/services/review_report_generator.py"
EXAMPLE_PATH = ROOT / "docs/commercial/SAEE_SYNTHETIC_EVIDENCE_REVIEW_REPORT_EXAMPLE.md"
TRACEABILITY_PATH = ROOT / "docs/commercial/SAEE_REVIEW_REPORT_TRACEABILITY.md"
BOUNDARIES_PATH = ROOT / "docs/commercial/SAEE_REVIEW_REPORT_BOUNDARIES.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_REVIEW_REPORT_PROTOTYPE_RECOMMENDATION_GATE.md"


class ReviewReportSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ReviewReportSmokeError(detail)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_execution_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen", "run", "Popen"}:
            found.add(node.func.attr)
    return found


def expect_invalid_report(report: dict[str, Any], label: str) -> None:
    try:
        validate_report(report)
    except ReviewReportError:
        return
    raise ReviewReportSmokeError(f"invalid report accepted: {label}")


def main() -> None:
    required_paths = (SCHEMA_PATH, CASE_PATH, SERVICE_PATH, EXAMPLE_PATH, TRACEABILITY_PATH, BOUNDARIES_PATH, GATE_PATH)
    for path in required_paths:
        require(path.is_file(), f"missing required file: {path}")

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "pip"}
    for path in (SERVICE_PATH, Path(__file__)):
        require(not imported_roots(path).intersection(forbidden_imports), f"network or subprocess import: {path}")
        require(not forbidden_execution_calls(path), f"dynamic or external execution: {path}")

    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    case = load_json(CASE_PATH)
    report = generate_review_report(case)
    require(not list(validator.iter_errors(report)), "generated report is not schema-valid")
    require(render_review_report_markdown(report) == EXAMPLE_PATH.read_text(encoding="utf-8"), "human-readable example drifted from generator")

    source_evidence = set(case["evidence_package_references"])
    summary_evidence = set(report["evidence_summary"]["evidence_package_references"])
    claim_evidence = {ref for item in report["claim_assessments"] for ref in item["supporting_evidence"]}
    require(summary_evidence == source_evidence, "evidence summary references not preserved")
    require(claim_evidence.issubset(source_evidence), "claim evidence reference not declared by source")
    require(bool(report["limitations"]) and len(report["limitations"]) >= 4, "limitations missing")
    require(report["truth_boundary"]["synthetic_report"] is True, "synthetic boundary missing")
    for field in (
        "customer_data_used",
        "external_validation_completed",
        "security_certification_claimed",
        "regulatory_compliance_claimed",
        "legal_judgment_made",
        "automated_decision_made",
        "deployment_authorized",
        "customer_accepted",
        "commercial_service_delivered",
        "production_ready",
    ):
        require(report["truth_boundary"][field] is False, f"truth boundary promoted: {field}")

    invalid_cases: list[tuple[dict[str, Any], str]] = []
    mutation = copy.deepcopy(report)
    mutation["claim_assessments"][0]["assessment"] = "APPROVED"
    invalid_cases.append((mutation, "APPROVED assessment"))
    for label, text in (
        ("certification claim", "The system is certified."),
        ("approval claim", "The system has been approved."),
        ("safety claim", "The system is safe."),
        ("compliance claim", "The system is compliant."),
    ):
        mutation = copy.deepcopy(report)
        mutation["claim_assessments"][0]["assessment_statement"] = text
        invalid_cases.append((mutation, label))
    for mutation, label in invalid_cases:
        expect_invalid_report(mutation, label)

    canonical = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = generate_review_report(load_json(CASE_PATH))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "generator is non-deterministic")

    boundary_text = BOUNDARIES_PATH.read_text(encoding="utf-8")
    require(
        "This prototype demonstrates evidence review reporting using synthetic scenarios. It is not a commercial service, certification process, or production assessment."
        in boundary_text,
        "English boundary statement missing",
    )
    require(
        "该原型使用合成场景展示证据审查报告生成，不是商业服务、认证流程或生产评估。" in boundary_text,
        "Chinese boundary statement missing",
    )

    print("SAEE_REVIEW_REPORT_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=5/5")
    print("evidence_references_preserved=true")
    print("limitations_included=true")
    print("forbidden_claims_rejected=4/4")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("customer_data_used=false")
    print("commercial_service_delivered=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (ReviewReportSmokeError, ReviewReportError, json.JSONDecodeError) as exc:
        print(f"SAEE_REVIEW_REPORT_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
