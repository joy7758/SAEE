#!/usr/bin/env python3
"""Offline regression gate for the SAEE Phase 1 synthetic vertical slice."""

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
SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json"
EXAMPLE_PATH = ROOT / "agent-interface/architecture/examples/saee-evidence-case-synthetic-001.json"
SERVICE_PATH = ROOT / "saee_backend/services/saee_evidence_case.py"
CLI_PATH = ROOT / "scripts/saee_agent_cli.py"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE1_SYNTHETIC_VERTICAL_SLICE.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE1_SYNTHETIC_VERTICAL_SLICE_RECOMMENDATION_GATE.md"


class Phase1SmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise Phase1SmokeError(detail)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def candidate(result: dict[str, Any], ref: str) -> dict[str, Any]:
    return next(item for item in result["candidate_results"] if item["candidate_ref"] == ref)


def main() -> None:
    for path in (SCHEMA_PATH, EXAMPLE_PATH, SERVICE_PATH, CLI_PATH, DOC_PATH, GATE_PATH):
        require(path.is_file(), f"missing required file: {path}")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    case = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    validator.validate(case)
    require(schema.get("additionalProperties") is False, "root schema must be strict")

    schema_negatives = []
    extra = copy.deepcopy(case); extra["unexpected"] = True; schema_negatives.append(extra)
    real_agent = copy.deepcopy(case); real_agent["truth_boundary"]["real_agent_executed"] = True; schema_negatives.append(real_agent)
    measured = copy.deepcopy(case); measured["truth_boundary"]["risk_probability_measured"] = True; schema_negatives.append(measured)
    authorized = copy.deepcopy(case); authorized["truth_boundary"]["deployment_authorized"] = True; schema_negatives.append(authorized)
    observation_claim = copy.deepcopy(case); observation_claim["observations"][0]["observation_is_evidence"] = True; schema_negatives.append(observation_claim)
    require(all(not validator.is_valid(item) for item in schema_negatives), "schema accepted a forbidden boundary")

    from saee_backend.services.saee_evidence_case import (
        EvidenceCaseError,
        evaluate_assurance_case,
        run_assurance_case_path,
    )

    result = run_assurance_case_path(EXAMPLE_PATH)
    require(result["candidate_count"] == 2, "candidate count")
    require(result["scenario_count"] == 2, "scenario count")
    require(result["evaluation_record_count"] == 4, "evaluation record count")
    require(
        set(result["evidence_case_object"]) == {
            "identity", "task_contract", "environment", "agent_reference", "observation",
            "evaluation", "evidence", "risk", "decision",
        },
        "Evidence Case Object nine-part contract",
    )
    require(result["lowest_estimated_risk_candidate_ref"] == "candidate:synthetic-b", "lowest-risk candidate")
    require(result["scenario_scoped_recommendation"] == "DEPLOY_LIMITED", "scenario recommendation")

    a = candidate(result, "candidate:synthetic-a")
    b = candidate(result, "candidate:synthetic-b")
    require(a["evidence_adequacy"]["result"] == "PASS", "candidate A evidence adequacy")
    require(b["evidence_adequacy"]["result"] == "PASS", "candidate B evidence adequacy")
    require(a["risk_estimate"]["aggregate_estimated_deployment_risk"] == 0.1734, "candidate A risk")
    require(b["risk_estimate"]["aggregate_estimated_deployment_risk"] == 0.131, "candidate B risk")
    require(a["decision_support"]["recommendation"] == "RETEST", "candidate A decision")
    require(b["decision_support"]["recommendation"] == "DEPLOY_LIMITED", "candidate B decision")
    require(
        all(
            set(("score", "reason", "failure_class", "evidence_ref")).issubset(item)
            for row in result["candidate_results"]
            for item in row["evaluation_results"]
        ),
        "evaluation output contract",
    )

    semantic_negatives: list[tuple[dict[str, Any], str]] = []
    weights = copy.deepcopy(case); weights["environment_contract"]["scenarios"][0]["weight"] = 0.4
    semantic_negatives.append((weights, "EVIDENCE_CASE_SCENARIO_WEIGHTS_INVALID"))
    missing = copy.deepcopy(case); missing["observations"][-1]["candidate_ref"] = "candidate:synthetic-c"
    semantic_negatives.append((missing, "EVIDENCE_CASE_OBSERVATION_MATRIX_INCOMPLETE"))
    thresholds = copy.deepcopy(case); thresholds["risk_policy"]["deploy_limited_threshold"] = 0.3
    semantic_negatives.append((thresholds, "EVIDENCE_CASE_THRESHOLDS_INVALID"))
    unbound = copy.deepcopy(case); unbound["observations"][0]["evidence_ref"] = "evidence-contract:synthetic-b"
    semantic_negatives.append((unbound, "EVIDENCE_CASE_OBSERVATION_EVIDENCE_UNBOUND"))
    for invalid, expected_code in semantic_negatives:
        try:
            evaluate_assurance_case(invalid)
        except EvidenceCaseError as exc:
            require(exc.code == expected_code, f"expected {expected_code}, got {exc.code}")
        else:
            raise Phase1SmokeError(f"semantic negative accepted: {expected_code}")

    inadequate = copy.deepcopy(case)
    inadequate["evidence_packages"][1]["claim_evidence"]["evidence"].pop("policy_decision")
    inadequate_result = evaluate_assurance_case(inadequate)
    inadequate_b = candidate(inadequate_result, "candidate:synthetic-b")
    require(inadequate_b["evidence_adequacy"]["result"] == "FAIL", "inadequate evidence must fail")
    require(inadequate_b["decision_support"]["recommendation"] == "RETEST", "adequacy failure must force RETEST")

    boundary = result["truth_boundary"]
    for field in (
        "real_agent_executed", "external_tool_executed", "production_trace_observed",
        "customer_data_used", "risk_probability_measured", "automatic_decision_made",
        "deployment_authorized", "external_validation_completed", "customer_validated", "production_ready",
    ):
        require(boundary[field] is False, f"truth boundary promoted: {field}")
    require(boundary["network_calls"] == 0, "network calls")
    require(boundary["subprocess_started"] is False, "subprocess started")
    require(boundary["existing_evidence_adequacy_reused"] is True, "adequacy reuse marker")

    service_source = SERVICE_PATH.read_text(encoding="utf-8")
    require("from saee_backend.services.evidence_adequacy import evaluate_evidence_adequacy" in service_source, "existing adequacy evaluator not reused")
    require("run-assurance-case" in CLI_PATH.read_text(encoding="utf-8"), "CLI command missing")
    doc = DOC_PATH.read_text(encoding="utf-8")
    for token in ("SAEE Evidence Case Object", "Risk Estimate", "Decision Support", "Score + Reason + Failure Class + Evidence Reference"):
        require(token in doc, f"documentation token missing: {token}")

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    require(not imported_roots(SERVICE_PATH).intersection(forbidden), "service imports external capability")
    require(not imported_roots(Path(__file__)).intersection(forbidden), "smoke imports external capability")

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = evaluate_assurance_case(copy.deepcopy(case))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "non-deterministic result")

    print("SAEE_PHASE1_SYNTHETIC_VERTICAL_SLICE_SMOKE: PASS")
    print("schema_valid_cases=1/1")
    print("schema_negative_cases=5/5")
    print("semantic_negative_cases=4/4")
    print("candidate_cases=2/2")
    print("scenario_cases=2/2")
    print("evaluation_records=4/4")
    print("evidence_adequacy_pass=2/2")
    print("evidence_adequacy_fail_closed=1/1")
    print("risk_estimates=2/2")
    print("decision_support_cases=2/2")
    print("candidate_a_risk=0.1734")
    print("candidate_a_action=RETEST")
    print("candidate_b_risk=0.131")
    print("candidate_b_action=DEPLOY_LIMITED")
    print("lowest_estimated_risk_candidate=candidate:synthetic-b")
    print("deterministic_runs=5/5")
    print("existing_evidence_adequacy_reused=true")
    print("risk_probability_measured=false")
    print("automatic_decision_made=false")
    print("real_agent_executed=false")
    print("customer_data_used=false")
    print("deployment_authorized=false")
    print("customer_validated=false")
    print("production_ready=false")
    print("network_calls=0")
    print("subprocess_started=false")


if __name__ == "__main__":
    main()
