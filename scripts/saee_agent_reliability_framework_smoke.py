#!/usr/bin/env python3
"""Offline deterministic smoke for Agent Reliability Framework v1.0."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.reliability_framework.assessment_adapter import assess_reliability_run
from saee_backend.services.reliability_framework.benchmark_adapter import adapt_recommendation_benchmark, adapt_reliability_study, adapt_stateful_business
from saee_backend.services.reliability_framework.failure_classifier import classify_failures
from saee_backend.services.reliability_framework.report_builder import build_reliability_report

ASSESSMENT_SCHEMA = ROOT / "schemas/saee-agent-reliability-assessment.schema.v1.0.json"
REPORT_SCHEMA = ROOT / "schemas/saee-agent-reliability-report.schema.v1.0.json"
TAXONOMY = ROOT / "agent-interface/reliability/saee-failure-taxonomy.v1.0.json"
MAPPING = ROOT / "agent-interface/reliability/saee-reliability-source-mapping.v1.0.json"
ASSESSMENT_EXAMPLE = ROOT / "agent-interface/reliability/examples/saee-reliability-assessment-security-example.v1.0.json"
REPORT_EXAMPLE = ROOT / "agent-interface/reliability/examples/saee-agent-reliability-report-example.v1.0.json"
FRAMEWORK_DIR = ROOT / "saee_backend/services/reliability_framework"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def main() -> int:
    assessment_schema, report_schema = load(ASSESSMENT_SCHEMA), load(REPORT_SCHEMA)
    Draft202012Validator.check_schema(assessment_schema); Draft202012Validator.check_schema(report_schema)
    assessment_validator, report_validator = Draft202012Validator(assessment_schema), Draft202012Validator(report_schema)
    example, report_example = load(ASSESSMENT_EXAMPLE), load(REPORT_EXAMPLE)
    assert not list(assessment_validator.iter_errors(example))
    assert not list(report_validator.iter_errors(report_example))

    taxonomy = load(TAXONOMY)
    ids = [item["id"] for item in taxonomy["failure_types"]]
    assert ids == ["CONTRACT_FAILURE", "MODEL_RESPONSE_FAILURE", "TOOL_FAILURE", "ENVIRONMENT_FAILURE", "BOUNDARY_FAILURE", "EVIDENCE_FAILURE"]
    entries = {item["id"]: item for item in taxonomy["failure_types"]}
    assert "agent unsafe" in entries["CONTRACT_FAILURE"]["does_not_imply"]
    assert "agent incapable" in entries["MODEL_RESPONSE_FAILURE"]["does_not_imply"]
    assert "security vulnerability" in entries["BOUNDARY_FAILURE"]["does_not_imply"]

    mapping = load(MAPPING)
    assert mapping["all_existing_studies_mapped"] is True and len(mapping["sources"]) == 6
    for source in mapping["sources"]:
        assert (ROOT / source["source_ref"]).is_file(), source

    security_ref = "agent-interface/reliability/saee-security-boundary-reliability-result.v0.3.json"
    security = load(ROOT / security_ref)
    security_assessments = adapt_reliability_study(security, source_ref=security_ref)
    assert len(security_assessments) == 15
    assert sum(item["dimensions"]["assessment_availability"]["status"] == "OBSERVED_PASS" for item in security_assessments) == 6
    unavailable = next(item for item in security_assessments if item["dimensions"]["assessment_availability"]["status"] == "OBSERVED_FAIL")
    assert unavailable["dimensions"]["boundary_reliability"]["status"] == "NOT_ASSESSED"
    assert unavailable["assessment_availability"]["assessment_unavailable_is_agent_failure"] is False

    coding_ref = "agent-interface/reliability/saee-agent-reliability-result.v0.1.json"
    assert len(adapt_reliability_study(load(ROOT / coding_ref), source_ref=coding_ref)) == 30
    business_ref = "agent-interface/rehearsal/saee-stateful-business-live-validation.v0.3.json"
    assert len(adapt_stateful_business(load(ROOT / business_ref), source_ref=business_ref)) == 1
    recommendation_ref = "agent-interface/recommendation/saee-agent-recommendation-benchmark-result.v0.1.json"
    recommendation_assessments = adapt_recommendation_benchmark(load(ROOT / recommendation_ref), source_ref=recommendation_ref)
    assert len(recommendation_assessments) == 4
    assert all(item["dimensions"]["task_execution_reliability"]["status"] == "NOT_ASSESSED" for item in recommendation_assessments)

    report = build_reliability_report(security_assessments, report_id="saee:reliability-report:security-v1", scope="local synthetic security boundary study")
    assert not list(report_validator.iter_errors(report))
    assert report["run_summary"] == {"attempted_assessments": 15, "successful_assessments": 6, "unavailable_assessments": 9, "assessment_availability_rate": 0.4}
    assert report["evidence_assessment"] == "NOT_ASSESSED"
    assert report["recommendation"] == "HUMAN_REVIEW_REQUIRED"

    contract_run = {"run_id": "run:test:01", "status": "contract_failed", "unavailable_reason": "security_contract_failed:SECURITY_FINAL_RESULT_INVALID", "missing_evidence": [], "evidence_outcomes": [], "repeated_tool_calls": 0, "observed_risk_signals": []}
    assert classify_failures(contract_run) == ["CONTRACT_FAILURE", "MODEL_RESPONSE_FAILURE"]
    contract_assessment = assess_reliability_run(contract_run, agent_profile="test_agent", scenario_id="synthetic:test", source_ref="agent-interface/reliability/saee-security-boundary-reliability-result.v0.3.json")
    assert contract_assessment["dimensions"]["task_execution_reliability"]["status"] == "NOT_ASSESSED"

    adequacy_input = load(ROOT / "agent-interface/examples/evidence-adequacy/authorized_agent_action_pass.json")
    evaluated = assess_reliability_run({"run_id": "run:test:02", "status": "completed", "unavailable_reason": None, "missing_evidence": [], "evidence_outcomes": [], "repeated_tool_calls": 0, "observed_risk_signals": []}, agent_profile="test_agent", scenario_id="synthetic:test", source_ref="agent-interface/examples/evidence-adequacy/authorized_agent_action_pass.json", claim_type="AUTHORIZED_AGENT_ACTION", adequacy_input=adequacy_input)
    assert evaluated["evidence_assessment"]["result"] == "PASS"

    invalid = []
    for field, value in (("leaderboard", True), ("ranking_generated", True), ("certification", True), ("intelligence_score_generated", True), ("production_ready", True), ("external_validation_completed", True)):
        candidate = copy.deepcopy(example); candidate["truth_boundary"][field] = value; invalid.append(bool(list(assessment_validator.iter_errors(candidate))))
    candidate = copy.deepcopy(example); candidate["dimensions"]["boundary_reliability"]["status"] = "SAFE"; invalid.append(bool(list(assessment_validator.iter_errors(candidate))))
    candidate = copy.deepcopy(example); candidate["failure_taxonomy"] = ["INTELLIGENCE_FAILURE"]; invalid.append(bool(list(assessment_validator.iter_errors(candidate))))
    candidate = copy.deepcopy(example); candidate["assessment_availability"]["assessment_availability_rate"] = 2; invalid.append(bool(list(assessment_validator.iter_errors(candidate))))
    candidate = copy.deepcopy(example); candidate["unexpected_score"] = 1; invalid.append(bool(list(assessment_validator.iter_errors(candidate))))
    candidate = copy.deepcopy(report_example); candidate["recommendation"] = "APPROVED"; invalid.append(bool(list(report_validator.iter_errors(candidate))))
    candidate = copy.deepcopy(report_example); candidate["recommendation"] = "CERTIFIED"; invalid.append(bool(list(report_validator.iter_errors(candidate))))
    candidate = copy.deepcopy(report_example); candidate["truth_boundary"]["safe"] = True; invalid.append(bool(list(report_validator.iter_errors(candidate))))
    candidate = copy.deepcopy(report_example); candidate["truth_boundary"]["best_agent"] = True; invalid.append(bool(list(report_validator.iter_errors(candidate))))
    candidate = copy.deepcopy(report_example); candidate["truth_boundary"]["production_ready"] = True; invalid.append(bool(list(report_validator.iter_errors(candidate))))
    assert len(invalid) >= 12 and all(invalid)

    canonical = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        rerun = build_reliability_report(copy.deepcopy(security_assessments), report_id="saee:reliability-report:security-v1", scope="local synthetic security boundary study")
        assert json.dumps(rerun, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "importlib"}
    for path in FRAMEWORK_DIR.glob("*.py"):
        assert not imported_roots(path).intersection(forbidden), path

    print("SAEE_AGENT_RELIABILITY_FRAMEWORK_SMOKE: PASS")
    print("schema_valid=true")
    print("failure_taxonomy_valid=true")
    print("existing_sources_mapped=6/6")
    print("report_schema_valid=true")
    print("security_assessments=15/15")
    print("assessment_available=6/15")
    print("assessment_unavailable=9/15")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("existing_evidence_adequacy_reused=true")
    print("ranking_generated=false")
    print("certification=false")
    print("intelligence_score_generated=false")
    print("production_ready=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
