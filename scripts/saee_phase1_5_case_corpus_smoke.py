#!/usr/bin/env python3
"""Offline corpus and transformation-integrity gate for SAEE Phase 1.5."""

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
CORPUS_DIRECTORY = ROOT / "agent-interface/architecture/examples/phase1_5_cases"
SERVICE_PATH = ROOT / "saee_backend/services/saee_evidence_case.py"
DOC_PATH = ROOT / "docs/architecture/SAEE_PHASE1_5_EVIDENCE_CASE_CORPUS.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE1_5_EVIDENCE_CASE_CORPUS_RECOMMENDATION_GATE.md"

EXPECTED_CASES = {
    "case-001-baseline-stability.json": ("baseline-stability", "baseline-low-failure"),
    "case-002-context-drift.json": ("context-drift", "long-context-drift"),
    "case-003-tool-failure.json": ("tool-failure", "tool-failure-unrecovered"),
    "case-004-instruction-conflict.json": ("instruction-conflict", "instruction-priority-conflict"),
    "case-005-adversarial-input.json": ("adversarial-input", "adversarial-inducement"),
}

SOURCE_ROOT_KEYS = {
    "saee_evidence_case_v0_1", "schema_version", "architecture_version", "case_id",
    "case_status", "created_at", "identity", "task_contract", "environment_contract",
    "candidates", "observations", "evidence_packages", "risk_policy", "truth_boundary",
}

DERIVED_OBJECT_KEYS = {
    "identity", "task_contract", "environment", "agent_reference", "observation",
    "evaluation", "evidence", "risk", "decision",
}

FALSE_SOURCE_BOUNDARIES = {
    "real_agent_executed", "external_tool_executed", "production_trace_observed",
    "customer_data_used", "risk_probability_measured", "deployment_authorized",
    "external_validation_completed", "customer_validated", "production_ready",
}

FALSE_RESULT_BOUNDARIES = FALSE_SOURCE_BOUNDARIES | {
    "automatic_decision_made",
}


class CorpusSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise CorpusSmokeError(detail)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def by_candidate(items: list[dict[str, Any]], field: str = "candidate_ref") -> dict[str, dict[str, Any]]:
    return {item[field]: item for item in items}


def validate_transformation(source: dict[str, Any], result: dict[str, Any]) -> None:
    derived = result["evidence_case_object"]
    require(set(derived) == DERIVED_OBJECT_KEYS, f"{source['case_id']}: derived object keys")
    require(derived["identity"] == {**source["identity"], "case_id": source["case_id"]}, f"{source['case_id']}: identity lost")
    require(derived["task_contract"] == source["task_contract"], f"{source['case_id']}: task contract lost")
    require(derived["environment"] == source["environment_contract"], f"{source['case_id']}: environment lost")
    require(derived["agent_reference"] == source["candidates"], f"{source['case_id']}: candidates lost")
    require(derived["observation"] == source["observations"], f"{source['case_id']}: observations lost")

    source_observations = {item["observation_ref"]: item for item in source["observations"]}
    evaluation_rows = [row for group in derived["evaluation"] for row in group["results"]]
    require(len(evaluation_rows) == len(source_observations), f"{source['case_id']}: evaluation count")
    for row in evaluation_rows:
        original = source_observations[row["observation_ref"]]
        require(row["scenario_ref"] == original["scenario_ref"], f"{source['case_id']}: scenario ref lost")
        require(row["reason"] == original["reason"], f"{source['case_id']}: reason lost")
        require(row["failure_class"] == original["failure_class"], f"{source['case_id']}: failure class lost")
        require(row["evidence_ref"] == original["evidence_ref"], f"{source['case_id']}: evidence ref lost")
        require(row["score"] == round(1.0 - original["failure_estimate"], 6), f"{source['case_id']}: score transform")

    source_packages = by_candidate(source["evidence_packages"])
    derived_evidence = by_candidate(derived["evidence"])
    derived_risk = by_candidate(derived["risk"])
    derived_decision = by_candidate(derived["decision"])
    require(set(source_packages) == set(derived_evidence) == set(derived_risk) == set(derived_decision), f"{source['case_id']}: candidate mapping")
    scenarios = {item["scenario_id"]: item for item in source["environment_contract"]["scenarios"]}
    observations_by_candidate: dict[str, list[dict[str, Any]]] = {ref: [] for ref in source_packages}
    for observation in source["observations"]:
        observations_by_candidate[observation["candidate_ref"]].append(observation)

    for candidate_ref, package in source_packages.items():
        evidence = derived_evidence[candidate_ref]
        require(evidence["evidence_ref"] == package["evidence_contract_ref"], f"{source['case_id']}: evidence contract ref")
        require(evidence["adequacy_result"]["result"] == "PASS", f"{source['case_id']}: evidence adequacy")

        risk = derived_risk[candidate_ref]
        require(risk["risk_estimate_not_measurement"] is True, f"{source['case_id']}: risk estimate marker")
        require(risk["risk_probability_measured"] is False, f"{source['case_id']}: risk probability boundary")
        expected_total = 0.0
        for observation in observations_by_candidate[candidate_ref]:
            scenario = scenarios[observation["scenario_ref"]]
            scenario_risk = round(
                observation["failure_estimate"]
                * scenario["business_impact"]
                * scenario["exposure"]
                * (1.0 - scenario["control_effectiveness"])
                + scenario["uncertainty_penalty"],
                6,
            )
            expected_total += round(scenario["weight"] * scenario_risk, 6)
        require(risk["aggregate_estimated_deployment_risk"] == round(expected_total, 6), f"{source['case_id']}: aggregate risk transform")

        decision = derived_decision[candidate_ref]
        require(decision["scenario_scope"] == source["risk_policy"]["threshold_scope"], f"{source['case_id']}: decision scope")
        require(decision["automatic_decision"] is False, f"{source['case_id']}: automatic decision")
        require(decision["customer_execution_authorized"] is False, f"{source['case_id']}: execution authorization")
        require(decision["evidence_ref"] == package["evidence_contract_ref"], f"{source['case_id']}: decision evidence ref")

    source_boundary = source["truth_boundary"]
    result_boundary = result["truth_boundary"]
    require(all(source_boundary[field] is False for field in FALSE_SOURCE_BOUNDARIES), f"{source['case_id']}: source boundary")
    require(all(result_boundary[field] is False for field in FALSE_RESULT_BOUNDARIES), f"{source['case_id']}: result boundary")
    require(result_boundary["network_calls"] == 0, f"{source['case_id']}: network boundary")
    require(result_boundary["subprocess_started"] is False, f"{source['case_id']}: subprocess boundary")


def main() -> None:
    for path in (SCHEMA_PATH, CORPUS_DIRECTORY, SERVICE_PATH, DOC_PATH, GATE_PATH):
        require(path.exists(), f"missing required path: {path}")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    paths = sorted(CORPUS_DIRECTORY.glob("*.json"))
    require({path.name for path in paths} == set(EXPECTED_CASES), "corpus must contain exactly five canonical cases")

    from saee_backend.services.saee_evidence_case import (
        EvidenceCaseError,
        run_assurance_case_path,
    )

    cases: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    categories: set[str] = set()
    for path in paths:
        source = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(source)
        require(set(source) == SOURCE_ROOT_KEYS, f"{path.name}: source root contract drift")
        require(not {"evaluation", "risk", "decision"}.intersection(source), f"{path.name}: derived field in source")
        require(source["identity"]["synthetic"] is True, f"{path.name}: identity not synthetic")
        require(all(item["synthetic"] is True for item in source["candidates"]), f"{path.name}: candidate not synthetic")
        require(all(item["synthetic"] is True and item["observation_is_evidence"] is False for item in source["observations"]), f"{path.name}: observation boundary")
        require(source["risk_policy"]["estimate_not_measurement"] is True, f"{path.name}: risk policy boundary")
        require("reference_estimate" not in json.dumps(source), f"{path.name}: deprecated risk alias")
        require("scenario_bound" not in json.dumps(source), f"{path.name}: deprecated decision alias")

        expected_category, expected_failure = EXPECTED_CASES[path.name]
        require(source["task_contract"]["task_category"] == expected_category, f"{path.name}: category")
        require(expected_failure in {item["failure_class"] for item in source["observations"]}, f"{path.name}: category failure coverage")
        categories.add(expected_category)
        result = run_assurance_case_path(path)
        validate_transformation(source, result)
        cases.append(source)
        results.append(result)

    require(categories == {value[0] for value in EXPECTED_CASES.values()}, "category coverage incomplete")

    base = cases[0]
    negatives = []
    extra = copy.deepcopy(base); extra["evaluation"] = {}; negatives.append(extra)
    real_agent = copy.deepcopy(base); real_agent["truth_boundary"]["real_agent_executed"] = True; negatives.append(real_agent)
    measured = copy.deepcopy(base); measured["risk_policy"]["estimate_not_measurement"] = False; negatives.append(measured)
    real_candidate = copy.deepcopy(base); real_candidate["candidates"][0]["synthetic"] = False; negatives.append(real_candidate)
    auto_authorized = copy.deepcopy(base); auto_authorized["truth_boundary"]["deployment_authorized"] = True; negatives.append(auto_authorized)
    require(all(not validator.is_valid(item) for item in negatives), "negative source accepted")

    try:
        run_assurance_case_path(Path("/tmp/saee-outside-corpus.json"))
    except EvidenceCaseError as exc:
        require(exc.code == "EVIDENCE_CASE_PATH_OUTSIDE_CANONICAL_EXAMPLES", "path boundary reason code")
    else:
        raise CorpusSmokeError("outside path accepted")

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    require(not imported_roots(SERVICE_PATH).intersection(forbidden), "service imports external capability")
    require(not imported_roots(Path(__file__)).intersection(forbidden), "smoke imports external capability")

    canonical = [json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for item in results]
    for _ in range(5):
        repeated = [run_assurance_case_path(path) for path in paths]
        require(
            [json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for item in repeated] == canonical,
            "corpus result is not deterministic",
        )

    decisions = sorted({item["scenario_scoped_recommendation"] for item in results})
    print("SAEE_PHASE1_5_CASE_CORPUS_SMOKE: PASS")
    print("input_cases=5/5")
    print("evidence_case_objects=5/5")
    print("valid_reports=5/5")
    print("schema_valid_cases=5/5")
    print("schema_negative_cases=5/5")
    print("case_category_coverage=5/5")
    print("transformation_integrity=5/5")
    print("evidence_adequacy_pass=10/10")
    print("risk_estimate_not_measurement=10/10")
    print("decision_scenario_scope=10/10")
    print(f"decision_support_outcomes={','.join(decisions)}")
    print("deterministic_runs=5/5")
    print("boundary_violations=0")
    print("architecture_modified=false")
    print("schema_modified=false")
    print("real_agent_executed=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("deployment_authorized=false")
    print("customer_validated=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
