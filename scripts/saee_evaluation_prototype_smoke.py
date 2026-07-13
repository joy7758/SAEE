#!/usr/bin/env python3
"""Validate the controlled SAEE Evaluation Prototype v0.1 offline."""

from __future__ import annotations

import ast
import copy
import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.evaluation_condition_generator import (
    CONDITION_IDS,
    generate_evidence_conditions,
)  # noqa: E402
from saee_backend.services.saee_evaluation_prototype import (
    run_evaluation_prototype_path,
)  # noqa: E402


SCHEMA_PATH = ROOT / "agent-interface/schemas/saee-evaluation-scenario.schema.json"
SCENARIO_DIRECTORY = ROOT / "agent-interface/evaluation/scenarios"
RESULT_PATH = ROOT / "agent-interface/evaluation/results/prototype-results.v0.1.json"
PROTOTYPE_SOURCE = ROOT / "saee_backend/services/saee_evaluation_prototype.py"
GENERATOR_SOURCE = ROOT / "saee_backend/services/evaluation_condition_generator.py"
METRICS_SOURCE = ROOT / "saee_backend/services/evaluation_metrics.py"
CLI_SOURCE = ROOT / "scripts/saee_agent_cli.py"
CLAIMS = {
    "RESOURCE_AUTHENTICITY",
    "AUTHORIZED_AGENT_ACTION",
    "HUMAN_OVERSIGHT",
    "EXECUTION_BOUNDARY",
}
FORBIDDEN_IMPORTS = {"subprocess", "socket", "requests", "httpx", "urllib"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def stored_summary(result: dict) -> dict:
    metrics = result["metrics"]
    return {
        "scenario_count": result["scenario_count"],
        "condition_count": result["condition_count"],
        "conditions_tested": result["conditions_tested"],
        "evaluation_record_count": result["evaluation_record_count"],
        "result_counts": result["result_counts"],
        "reference_result_matches": result["reference_result_matches"],
        "missing_identification_matches": result["missing_identification_matches"],
        "relationship_identification_matches": result["relationship_identification_matches"],
        "false_accountability_count": result["false_accountability_count"],
        "boundary_violation_count": result["boundary_violation_count"],
        "raw_metrics": {
            "false_accountability": {
                "numerator": metrics["false_accountability_rate"]["numerator_false_accountability_count"],
                "denominator": metrics["false_accountability_rate"]["denominator_reference_unsupported_claims"],
                "raw_fraction": metrics["false_accountability_rate"]["raw_fraction"],
            },
            "claim_support_coverage": {
                "numerator": metrics["claim_support_coverage"]["numerator_supported_claims_accepted"],
                "denominator": metrics["claim_support_coverage"]["denominator_reference_supportable_claims"],
                "raw_fraction": metrics["claim_support_coverage"]["raw_fraction"],
            },
            "evidence_relationship_completeness": {
                "numerator": metrics["evidence_relationship_completeness"]["numerator_valid_required_relationships"],
                "denominator": metrics["evidence_relationship_completeness"]["denominator_required_relationships"],
                "raw_fraction": metrics["evidence_relationship_completeness"]["raw_fraction"],
            },
            "missing_evidence_identification": {
                "exact_set_matches": metrics["missing_evidence_identification"]["exact_set_match_count"],
                "claim_attempts": metrics["missing_evidence_identification"]["claim_attempt_count"],
                "item_true_positive_count": metrics["missing_evidence_identification"]["item_true_positive_count"],
                "item_false_positive_count": metrics["missing_evidence_identification"]["item_false_positive_count"],
                "item_false_negative_count": metrics["missing_evidence_identification"]["item_false_negative_count"],
            },
        },
    }


def main() -> None:
    schema = read_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    scenario_paths = sorted(SCENARIO_DIRECTORY.glob("*.json"))
    require(len(scenario_paths) >= 8, "at least eight scenario files required")
    scenarios = [read_json(path) for path in scenario_paths]
    for scenario in scenarios:
        require(not list(validator.iter_errors(scenario)), f"valid scenario rejected: {scenario['scenario_id']}")
    require(
        Counter(scenario["expected_claims"][0] for scenario in scenarios)
        == Counter({claim: 2 for claim in CLAIMS}),
        "claim coverage must be two scenarios per claim",
    )

    invalid_extra = copy.deepcopy(scenarios[0])
    invalid_extra["undeclared"] = True
    require(bool(list(validator.iter_errors(invalid_extra))), "undeclared scenario field accepted")
    invalid_missing_claim = copy.deepcopy(scenarios[0])
    del invalid_missing_claim["expected_claims"]
    require(bool(list(validator.iter_errors(invalid_missing_claim))), "missing expected claim accepted")

    original = json.dumps(scenarios[0], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    conditions = generate_evidence_conditions(scenarios[0])
    require(tuple(condition["condition_id"] for condition in conditions) == CONDITION_IDS, "condition order")
    require(len(conditions) == 4, "four evidence conditions required")
    require(
        json.dumps(scenarios[0], ensure_ascii=False, sort_keys=True, separators=(",", ":")) == original,
        "condition generator modified source scenario",
    )
    require(all(condition["truth_boundary"]["missing_evidence_invented"] is False for condition in conditions), "invention boundary")

    result = run_evaluation_prototype_path(SCENARIO_DIRECTORY)
    require(result["scenario_count"] == len(scenarios), "scenario result count")
    require(result["condition_count"] == 4, "condition result count")
    require(result["evaluation_record_count"] == len(scenarios) * 4, "evaluation record count")
    total = result["evaluation_record_count"]
    require(result["reference_result_matches"] == f"{total}/{total}", "reference result mismatch")
    require(result["missing_identification_matches"] == f"{total}/{total}", "missing identification mismatch")
    require(result["relationship_identification_matches"] == f"{total}/{total}", "relationship identification mismatch")
    require("false_accountability_rate" in result["metrics"], "false accountability metric missing")
    require(result["boundary_violation_count"] == 0, "truth boundary violation")
    require(result["metrics"]["overall_accuracy_score_emitted"] is False, "overall accuracy forbidden")
    require(result["metrics"]["system_superiority_score_emitted"] is False, "superiority score forbidden")

    stored = read_json(RESULT_PATH)
    for key, value in stored_summary(result).items():
        require(stored.get(key) == value, f"stored result drift: {key}")
    require(stored.get("scientific_result_claimed") is False, "scientific result boundary")
    require(stored.get("external_validation_completed") is False, "external validation boundary")

    prototype_source = PROTOTYPE_SOURCE.read_text(encoding="utf-8")
    require(
        "from saee_backend.services.evidence_adequacy import evaluate_evidence_adequacy" in prototype_source,
        "existing Evidence Adequacy evaluator must be reused",
    )
    require("def _relationship_passes" not in prototype_source, "relationship logic duplicated")
    require("run-evaluation-prototype" in CLI_SOURCE.read_text(encoding="utf-8"), "CLI command missing")
    for path in (Path(__file__), PROTOTYPE_SOURCE, GENERATOR_SOURCE, METRICS_SOURCE):
        require(not imported_roots(path).intersection(FORBIDDEN_IMPORTS), f"external capability import: {path}")

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = run_evaluation_prototype_path(SCENARIO_DIRECTORY)
        require(
            json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical,
            "prototype result is not deterministic",
        )

    print("SAEE_EVALUATION_PROTOTYPE_SMOKE: PASS")
    print(f"scenario_cases={len(scenarios)}/{len(scenarios)}")
    print("schema_negative_cases=2/2")
    print("claim_coverage=4/4")
    print("condition_levels=4/4")
    print(f"evaluation_records={total}/{total}")
    print(f"reference_result_matches={result['reference_result_matches']}")
    print(f"missing_identification_matches={result['missing_identification_matches']}")
    print(f"relationship_identification_matches={result['relationship_identification_matches']}")
    print("deterministic_runs=5/5")
    print("false_accountability_metric_present=true")
    print(f"false_accountability_count={result['false_accountability_count']}")
    print(f"boundary_violation_count={result['boundary_violation_count']}")
    print("existing_evidence_adequacy_reused=true")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("real_agent_executed=false")
    print("external_data_used=false")
    print("external_validation_completed=false")
    print("scientific_result_claimed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
