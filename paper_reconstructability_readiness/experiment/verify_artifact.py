#!/usr/bin/env python3
"""Verify the canonical result manifest against falsifiable expectations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RESULT_PATH = ROOT / "results.v0.1.json"
EXPECTED_PATH = ROOT / "expected-results.v0.1.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require_equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> int:
    manifest = read_json(RESULT_PATH)
    result = manifest["result"]
    expected = read_json(EXPECTED_PATH)

    require_equal("dataset_id", result["dataset_id"], expected["dataset_id"])
    require_equal("repetitions", manifest["repetitions"], expected["repetitions"])
    require_equal("deterministic", manifest["deterministic"], expected["deterministic"])
    for key in (
        "total_pairs",
        "total_cases",
        "reconstructability_complete_cases",
        "semantic_positive_cases",
        "semantic_negative_cases",
        "matched_pairs_with_same_nominal_outcome",
        "matched_pairs_with_complete_reconstructability",
        "matched_pairs_with_identical_presence_vector",
        "matched_pairs_with_identical_json_shape",
        "matched_pairs_with_divergent_semantic_verdict",
        "semantic_expectation_matches",
        "reason_code_matches",
        "boundary_violation_count",
    ):
        require_equal(key, result[key], expected[key])

    for evaluator in (
        "field_complete_baseline",
        "type_and_shape_baseline",
        "decision_aware_ablation",
        "semantic_profile_evaluator",
    ):
        for key, value in expected[evaluator].items():
            require_equal(f"{evaluator}.{key}", result[evaluator][key], value)

    require_equal(
        "result hash determinism",
        len(set(manifest["result_sha256_by_run"])),
        1,
    )
    require_equal(
        "construct counterexample",
        result["claims"]["supports_bounded_construct_counterexample"],
        True,
    )
    require_equal(
        "presence-equivalence impossibility instances",
        result["claims"]["supports_presence_equivalence_impossibility_instances"],
        True,
    )
    for key in (
        "establishes_real_world_prevalence",
        "establishes_external_identity_or_authority",
        "establishes_production_readiness",
        "establishes_general_product_superiority",
    ):
        require_equal(f"claims.{key}", result["claims"][key], False)

    print("SAEE_RECONSTRUCTABILITY_ADEQUACY_ARTIFACT: PASS")
    print(f"pairs={result['total_pairs']}/{expected['total_pairs']}")
    print(f"cases={result['total_cases']}/{expected['total_cases']}")
    print(f"reconstructability_complete={result['reconstructability_complete_cases']}/{result['total_cases']}")
    print(f"pairwise_semantic_divergence={result['matched_pairs_with_divergent_semantic_verdict']}/{result['total_pairs']}")
    print(f"field_complete_false_supports={result['field_complete_baseline']['false_positive']}")
    print(f"type_and_shape_false_supports={result['type_and_shape_baseline']['false_positive']}")
    print(f"decision_aware_false_supports={result['decision_aware_ablation']['false_positive']}")
    print(f"semantic_profile_false_supports={result['semantic_profile_evaluator']['false_positive']}")
    print(f"deterministic_runs={manifest['repetitions']}/{expected['repetitions']}")
    print(f"canonical_result_sha256={manifest['canonical_result_sha256']}")
    print(f"boundary_violation_count={result['boundary_violation_count']}")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
