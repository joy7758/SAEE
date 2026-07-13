#!/usr/bin/env python3
"""Deterministic checks for the synthetic Evidence Adequacy Benchmark v0.1."""

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

from saee_backend.services.evidence_adequacy_benchmark import (  # noqa: E402
    CLAIMS,
    LEVELS,
    run_evidence_adequacy_benchmark,
)


SCHEMA_PATH = ROOT / "agent-interface/schemas/evidence-adequacy-benchmark.schema.json"
DATASET_PATH = ROOT / "agent-interface/benchmarks/evidence-adequacy/benchmark.v0.1.json"
SERVICE_PATH = ROOT / "saee_backend/services/evidence_adequacy_benchmark.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"object required: {path}")
    return value


def main() -> None:
    schema = read_json(SCHEMA_PATH)
    dataset = read_json(DATASET_PATH)
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dataset))
    require(not errors, f"benchmark schema validation: {errors}")
    require(len(dataset["scenarios"]) == 12, "twelve scenarios required")
    require(
        Counter(item["evidence_level"] for item in dataset["scenarios"]) == Counter({level: 3 for level in LEVELS}),
        "three scenarios per level",
    )
    require(
        Counter(item["claim_type"] for item in dataset["scenarios"]) == Counter({claim: 3 for claim in CLAIMS}),
        "three scenarios per claim",
    )

    result = run_evidence_adequacy_benchmark(dataset)
    require(result["total_cases"] == 12, "total cases")
    require(result["result_counts"] == {"PASS": 5, "FAIL": 7}, "result counts")
    require(result["expected_result_matches"] == "12/12", "expected result matches")
    require(result["missing_evidence_accuracy"] == "12/12", "missing evidence accuracy")
    require(result["reason_code_accuracy"] == "12/12", "reason code accuracy")
    require(result["false_positive_count"] == 0, "false positive boundary")
    require(result["boundary_violation_count"] == 0, "boundary safety")
    require(result["level_coverage"]["LEVEL_0_TRACE_ONLY"]["coverage"] == "0/3", "trace-only coverage")
    require(result["level_coverage"]["LEVEL_1_RECEIPT"]["coverage"] == "1/3", "receipt coverage")
    require(
        result["level_coverage"]["LEVEL_2_RECEIPT_WITH_RELATIONSHIPS"]["coverage"] == "1/3",
        "relationship coverage",
    )
    require(
        result["level_coverage"]["LEVEL_3_COMPLETE_EVIDENCE_PACKAGE"]["coverage"] == "3/3",
        "complete package coverage",
    )
    require(all(not item["accountability_claim_established"] for item in result["scenario_results"]), "no claim elevation")
    require(all(not item["event_occurrence_proven"] for item in result["scenario_results"]), "no event proof")

    rows = {item["scenario_id"]: item for item in result["scenario_results"]}
    for scenario_id in (
        "eab-l1-action-receipt-mismatched-reference",
        "eab-l2-human-approval-after-action",
        "eab-l2-execution-digest-mismatch",
    ):
        row = rows[scenario_id]
        require(row["actual_result"] == "FAIL", f"semantic relationship failure: {scenario_id}")
        require(row["actual_missing_requirements"] == [], f"not a field-count failure: {scenario_id}")
        require(row["actual_reason_codes"], f"semantic reason required: {scenario_id}")

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = run_evidence_adequacy_benchmark(read_json(DATASET_PATH))
        require(
            json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical,
            "deterministic benchmark output",
        )

    false_positive_fixture = copy.deepcopy(dataset)
    target = next(item for item in false_positive_fixture["scenarios"] if item["scenario_id"] == "eab-l1-resource-receipt")
    target["expected_result"] = "FAIL"
    false_positive_result = run_evidence_adequacy_benchmark(false_positive_fixture)
    require(false_positive_result["false_positive_count"] == 1, "false positive metric detects expectation breach")

    invalid_extra = copy.deepcopy(dataset)
    invalid_extra["scenarios"][0]["undeclared"] = True
    require(
        list(Draft202012Validator(schema).iter_errors(invalid_extra)),
        "strict scenario rejects undeclared fields",
    )

    tree = ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    require(not imported_roots.intersection({"subprocess", "socket", "requests", "httpx", "urllib"}), "external capability import")

    print("SAEE_EVIDENCE_ADEQUACY_BENCHMARK_SMOKE: PASS")
    print("scenario_cases=12/12")
    print("claim_coverage_cases=4/4")
    print("level_0_cases=3/3")
    print("level_1_cases=3/3")
    print("level_2_cases=3/3")
    print("level_3_cases=3/3")
    print("semantic_relationship_failures=3/3")
    print("expected_result_matches=12/12")
    print("missing_evidence_accuracy=12/12")
    print("reason_code_accuracy=12/12")
    print("deterministic_runs=5/5")
    print("false_positive_count=0")
    print("boundary_violation_count=0")
    print("trace_only_accountability_claims_established=0")
    print("network_calls=0")
    print("subprocess_started=false")
    print("candidate_code_executed=false")
    print("benchmark_superiority_claimed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
