"""Offline runner for the synthetic SAEE Evidence Adequacy Benchmark v0.1.

The runner measures local profile behavior against declared synthetic
expectations. It does not measure model intelligence, agent performance,
runtime speed, product superiority, legal validity, or event occurrence.
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.evidence_adequacy import evaluate_evidence_adequacy


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "agent-interface/schemas/evidence-adequacy-benchmark.schema.json"
FIXTURE_ROOT = ROOT / "agent-interface/examples/evidence-adequacy"
BENCHMARK_FILENAME = "benchmark.v0.1.json"
SCHEMA_VERSION = "0.1.0"

ALLOWED_FIXTURES = {
    "agent-interface/examples/evidence-adequacy/resource_authenticity_pass.json",
    "agent-interface/examples/evidence-adequacy/authorized_agent_action_pass.json",
    "agent-interface/examples/evidence-adequacy/human_oversight_pass.json",
    "agent-interface/examples/evidence-adequacy/execution_boundary_pass.json",
}

LEVELS = (
    "LEVEL_0_TRACE_ONLY",
    "LEVEL_1_RECEIPT",
    "LEVEL_2_RECEIPT_WITH_RELATIONSHIPS",
    "LEVEL_3_COMPLETE_EVIDENCE_PACKAGE",
)

CLAIMS = (
    "RESOURCE_AUTHENTICITY",
    "AUTHORIZED_AGENT_ACTION",
    "HUMAN_OVERSIGHT",
    "EXECUTION_BOUNDARY",
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_dataset(dataset: Any) -> None:
    schema = _read_json(SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dataset),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        raise ValueError("benchmark schema validation failed")
    scenario_ids = [scenario["scenario_id"] for scenario in dataset["scenarios"]]
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("benchmark scenario identifiers must be unique")
    if Counter(scenario["evidence_level"] for scenario in dataset["scenarios"]) != Counter({level: 3 for level in LEVELS}):
        raise ValueError("benchmark evidence-level distribution must be 3 per level")
    if Counter(scenario["claim_type"] for scenario in dataset["scenarios"]) != Counter({claim: 3 for claim in CLAIMS}):
        raise ValueError("benchmark claim distribution must be 3 per claim")


def _pointer_parent(document: dict[str, Any], pointer: str) -> tuple[dict[str, Any], str]:
    segments = pointer.split("/")[1:]
    if not segments:
        raise ValueError("root mutation is not allowed")
    current: Any = document
    for segment in segments[:-1]:
        if not isinstance(current, dict) or segment not in current:
            raise ValueError("mutation path does not exist")
        current = current[segment]
    if not isinstance(current, dict):
        raise ValueError("mutation parent must be an object")
    return current, segments[-1]


def _materialize(inputs: dict[str, Any]) -> dict[str, Any]:
    fixture_ref = inputs["fixture_ref"]
    if fixture_ref not in ALLOWED_FIXTURES:
        raise ValueError("benchmark fixture is not allowlisted")
    fixture_path = (ROOT / fixture_ref).resolve()
    if fixture_path.parent != FIXTURE_ROOT.resolve() or not fixture_path.is_file():
        raise ValueError("benchmark fixture path is outside the canonical fixture directory")
    package = copy.deepcopy(_read_json(fixture_path))
    if not isinstance(package, dict):
        raise ValueError("benchmark fixture must be an object")

    for mutation in inputs["mutations"]:
        parent, key = _pointer_parent(package, mutation["path"])
        operation = mutation["operation"]
        if operation == "add":
            if key in parent:
                raise ValueError("add mutation target already exists")
            parent[key] = copy.deepcopy(mutation["value"])
        elif operation == "replace":
            if key not in parent:
                raise ValueError("replace mutation target does not exist")
            parent[key] = copy.deepcopy(mutation["value"])
        elif operation == "remove":
            if key not in parent:
                raise ValueError("remove mutation target does not exist")
            del parent[key]
        else:
            raise ValueError("unsupported benchmark mutation")
    return package


def run_evidence_adequacy_benchmark(dataset: Any) -> dict[str, Any]:
    """Run all scenarios and return separated, non-promotional metrics."""

    _validate_dataset(dataset)
    scenario_results: list[dict[str, Any]] = []
    result_counts: Counter[str] = Counter()
    claim_totals: Counter[str] = Counter()
    claim_passes: Counter[str] = Counter()
    level_totals: Counter[str] = Counter()
    level_passes: Counter[str] = Counter()
    expected_result_matches = 0
    missing_matches = 0
    reason_matches = 0
    false_positive_count = 0
    boundary_violation_count = 0

    for scenario in dataset["scenarios"]:
        package = _materialize(scenario["evidence_inputs"])
        if package.get("claim_type") != scenario["claim_type"]:
            raise ValueError("benchmark fixture claim type mismatch")
        evaluation = evaluate_evidence_adequacy(scenario["claim_type"], package)
        actual = evaluation["result"]
        expected = scenario["expected_result"]
        result_match = actual == expected
        missing_match = evaluation["missing_requirements"] == scenario["expected_missing_requirements"]
        reason_match = evaluation["reason_codes"] == scenario["expected_reason_codes"]
        false_positive = expected == "FAIL" and actual == "PASS"
        boundary_violation = any(
            evaluation.get(key) is True
            for key in (
                "accountability_claim_established",
                "event_occurrence_proven",
                "identity_independently_verified",
                "authorization_externally_verified",
                "legal_finding_established",
                "production_ready",
            )
        )

        result_counts[actual] += 1
        claim_totals[scenario["claim_type"]] += 1
        level_totals[scenario["evidence_level"]] += 1
        if actual == "PASS":
            claim_passes[scenario["claim_type"]] += 1
            level_passes[scenario["evidence_level"]] += 1
        expected_result_matches += int(result_match)
        missing_matches += int(missing_match)
        reason_matches += int(reason_match)
        false_positive_count += int(false_positive)
        boundary_violation_count += int(boundary_violation)

        scenario_results.append(
            {
                "scenario_id": scenario["scenario_id"],
                "claim_type": scenario["claim_type"],
                "evidence_level": scenario["evidence_level"],
                "expected_result": expected,
                "actual_result": actual,
                "expected_result_match": result_match,
                "missing_requirements_match": missing_match,
                "reason_codes_match": reason_match,
                "actual_missing_requirements": evaluation["missing_requirements"],
                "actual_reason_codes": evaluation["reason_codes"],
                "false_positive": false_positive,
                "accountability_claim_established": False,
                "event_occurrence_proven": False,
            }
        )

    total = len(scenario_results)
    return {
        "saee_evidence_adequacy_benchmark_result_v0_1": True,
        "benchmark_version": SCHEMA_VERSION,
        "benchmark_id": dataset["benchmark_id"],
        "scope": dataset["scope"],
        "total_cases": total,
        "result_counts": {"PASS": result_counts["PASS"], "FAIL": result_counts["FAIL"]},
        "claim_coverage": {
            claim: f"{claim_passes[claim]}/{claim_totals[claim]}" for claim in CLAIMS
        },
        "level_coverage": {
            level: {
                "passed": level_passes[level],
                "total": level_totals[level],
                "coverage": f"{level_passes[level]}/{level_totals[level]}",
            }
            for level in LEVELS
        },
        "expected_result_matches": f"{expected_result_matches}/{total}",
        "missing_evidence_accuracy": f"{missing_matches}/{total}",
        "reason_code_accuracy": f"{reason_matches}/{total}",
        "false_positive_count": false_positive_count,
        "boundary_violation_count": boundary_violation_count,
        "scenario_results": scenario_results,
        "limitations": [
            "Synthetic benchmark only; no underlying event occurrence is proven.",
            "Counts describe local profile behavior and are not model or product performance scores.",
            "A profile PASS does not establish legal accountability, certification, or external validity.",
            "Reserved .invalid example hosts are synthetic identifiers and are never accessed.",
        ],
        "event_occurrence_proven": False,
        "legal_accountability_established": False,
        "external_validation_claimed": False,
        "benchmark_superiority_claimed": False,
        "certification_claimed": False,
        "network_accessed": False,
        "subprocess_started": False,
        "candidate_code_executed": False,
        "production_ready": False,
    }


def run_evidence_adequacy_benchmark_path(input_path: Path) -> dict[str, Any]:
    path = input_path / BENCHMARK_FILENAME if input_path.is_dir() else input_path
    if path.name != BENCHMARK_FILENAME:
        raise ValueError("benchmark input must be benchmark.v0.1.json or its containing directory")
    return run_evidence_adequacy_benchmark(_read_json(path))
