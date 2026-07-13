"""Controlled offline runner for the SAEE Evaluation Prototype v0.1.

This service materializes evidence conditions from researcher-authored synthetic
records and delegates every adequacy decision to the existing SAEE evaluator.
It does not execute agents, tools, resources, generated code, or external calls.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.evaluation_condition_generator import (
    CONDITION_IDS,
    generate_evidence_conditions,
)
from saee_backend.services.evaluation_metrics import calculate_evaluation_metrics
from saee_backend.services.evidence_adequacy import evaluate_evidence_adequacy


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "agent-interface/schemas/saee-evaluation-scenario.schema.json"
SCENARIO_DIRECTORY = ROOT / "agent-interface/evaluation/scenarios"
PROFILE_DIRECTORY = ROOT / "agent-interface/profiles/evidence-adequacy"
PROFILE_FILES = {
    "RESOURCE_AUTHENTICITY": "resource-authenticity.v0.1.json",
    "AUTHORIZED_AGENT_ACTION": "authorized-agent-action.v0.1.json",
    "HUMAN_OVERSIGHT": "human-oversight.v0.1.json",
    "EXECUTION_BOUNDARY": "execution-boundary.v0.1.json",
}
RESULT_BOUNDARY_KEYS = (
    "accountability_claim_established",
    "event_occurrence_proven",
    "identity_independently_verified",
    "authorization_externally_verified",
    "legal_finding_established",
    "production_ready",
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_scenario(scenario: Any, validator: Draft202012Validator) -> None:
    errors = sorted(
        validator.iter_errors(scenario),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        raise ValueError("evaluation scenario schema validation failed")
    claim_type = scenario["expected_claims"][0]
    if scenario["claim_evidence"]["claim_type"] != claim_type:
        raise ValueError("scenario expected claim and evidence claim must match")
    if set(scenario["reference_condition_expectations"]) != set(CONDITION_IDS):
        raise ValueError("scenario must define all four condition expectations")


def _relationship_count(claim_type: str) -> int:
    filename = PROFILE_FILES.get(claim_type)
    if filename is None:
        raise ValueError("unknown scenario claim type")
    profile = _read_json(PROFILE_DIRECTORY / filename)
    relationships = profile.get("required_relationships")
    if not isinstance(relationships, list) or not relationships:
        raise ValueError("canonical profile relationship declaration unavailable")
    return len(relationships)


def run_evaluation_prototype(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate each scenario under A/B/C/D using the canonical evaluator."""

    schema = _read_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    if len(scenarios) < 8:
        raise ValueError("at least eight synthetic evaluation scenarios are required")
    scenario_ids = [scenario.get("scenario_id") for scenario in scenarios]
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("evaluation scenario identifiers must be unique")

    records: list[dict[str, Any]] = []
    result_counts: Counter[str] = Counter()
    reference_result_matches = 0
    missing_identification_matches = 0
    relationship_identification_matches = 0
    boundary_violation_count = 0

    for scenario in sorted(scenarios, key=lambda item: item["scenario_id"]):
        _validate_scenario(scenario, validator)
        original = json.dumps(scenario, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        generated_conditions = generate_evidence_conditions(scenario)
        if json.dumps(scenario, ensure_ascii=False, sort_keys=True, separators=(",", ":")) != original:
            raise ValueError("condition generation mutated source scenario")

        claim_type = scenario["expected_claims"][0]
        required_relationship_count = _relationship_count(claim_type)
        expectations = scenario["reference_condition_expectations"]
        for condition in generated_conditions:
            condition_id = condition["condition_id"]
            reference = expectations[condition_id]
            evaluation = evaluate_evidence_adequacy(claim_type, condition["evidence_package"])
            reference_support = reference["profile_support_expected"]
            actual_support = evaluation["result"] == "PASS"
            result_match = actual_support == reference_support
            missing_match = evaluation["missing_requirements"] == reference["expected_missing_requirements"]
            relationship_match = evaluation["failed_relationships"] == reference["expected_failed_relationships"]
            boundary_violation = any(evaluation.get(key) is True for key in RESULT_BOUNDARY_KEYS)

            if evaluation["missing_requirements"]:
                valid_relationship_count = 0
            else:
                valid_relationship_count = required_relationship_count - len(evaluation["failed_relationships"])
            valid_relationship_count = max(0, valid_relationship_count)

            result_counts[evaluation["result"]] += 1
            reference_result_matches += int(result_match)
            missing_identification_matches += int(missing_match)
            relationship_identification_matches += int(relationship_match)
            boundary_violation_count += int(boundary_violation)
            records.append(
                {
                    "scenario_id": scenario["scenario_id"],
                    "scenario_class": scenario["scenario_class"],
                    "condition": condition_id,
                    "claim_type": claim_type,
                    "adequacy_result": evaluation["result"],
                    "reference_profile_support": reference_support,
                    "reference_result_match": result_match,
                    "missing_requirements": evaluation["missing_requirements"],
                    "reference_missing_requirements": reference["expected_missing_requirements"],
                    "missing_identification_match": missing_match,
                    "failed_relationships": evaluation["failed_relationships"],
                    "reference_failed_relationships": reference["expected_failed_relationships"],
                    "relationship_identification_match": relationship_match,
                    "reason_codes": evaluation["reason_codes"],
                    "required_relationship_count": required_relationship_count,
                    "valid_relationship_count": valid_relationship_count,
                    "false_accountability": reference_support is False and actual_support is True,
                    "accountability_claim_established": False,
                    "event_occurrence_proven": False,
                    "boundary_violation": boundary_violation,
                }
            )

    metrics = calculate_evaluation_metrics(records)
    total = len(records)
    return {
        "result_type": "SAEE_EVALUATION_PROTOTYPE_RESULT",
        "prototype_version": "0.1.0",
        "scope": "controlled_synthetic_offline_evidence_conditions",
        "scenario_count": len(scenarios),
        "condition_count": len(CONDITION_IDS),
        "conditions_tested": list(CONDITION_IDS),
        "evaluation_record_count": total,
        "result_counts": {"PASS": result_counts["PASS"], "FAIL": result_counts["FAIL"]},
        "reference_result_matches": f"{reference_result_matches}/{total}",
        "missing_identification_matches": f"{missing_identification_matches}/{total}",
        "relationship_identification_matches": f"{relationship_identification_matches}/{total}",
        "false_accountability_count": metrics["false_accountability_rate"]["numerator_false_accountability_count"],
        "boundary_violation_count": boundary_violation_count,
        "metrics": metrics,
        "scenario_results": records,
        "limitations": [
            "Controlled synthetic scenarios only; no real agent or external tool was run.",
            "Generated traces are researcher-authored records, not observed production traces.",
            "Metric counts describe this local prototype dataset and are not scientific performance results.",
            "No commercial or external baseline has been implemented or compared.",
            "A profile PASS does not establish an event, identity, authorization, causal fact, or legal finding.",
        ],
        "real_agent_executed": False,
        "production_trace_observed": False,
        "external_data_used": False,
        "external_validation_completed": False,
        "benchmark_superiority_claimed": False,
        "scientific_result_claimed": False,
        "network_accessed": False,
        "subprocess_started": False,
        "generated_code_executed": False,
        "external_tool_executed": False,
        "production_ready": False,
    }


def run_evaluation_prototype_path(input_path: Path) -> dict[str, Any]:
    """Load a closed scenario directory or one scenario file and run offline."""

    if input_path.is_dir():
        if input_path.resolve() != SCENARIO_DIRECTORY.resolve():
            raise ValueError("prototype directory input must be the canonical scenario directory")
        paths = sorted(path for path in input_path.glob("*.json") if path.is_file())
    else:
        if input_path.resolve().parent != SCENARIO_DIRECTORY.resolve() or input_path.suffix != ".json":
            raise ValueError("prototype file input must be a canonical scenario JSON")
        paths = [input_path]
    scenarios = [_read_json(path) for path in paths]
    return run_evaluation_prototype(scenarios)
