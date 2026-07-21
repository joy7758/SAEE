#!/usr/bin/env python3
"""Reproduce the matched-pair reconstructability/adequacy study.

The script reads only local, allowlisted fixtures and canonical profile files.
It makes no network call, starts no subprocess, and executes no candidate code.
The output is a controlled construct-validation result, not a production,
authorization, legal, safety, or real-world readiness claim.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = EXPERIMENT_ROOT / "dataset.v0.1.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.evidence_adequacy import (  # noqa: E402
    PROFILE_FILES,
    evaluate_evidence_adequacy,
)


CLAIMS = (
    "RESOURCE_AUTHENTICITY",
    "AUTHORIZED_AGENT_ACTION",
    "HUMAN_OVERSIGHT",
    "EXECUTION_BOUNDARY",
)
ALLOWED_FIXTURES = {
    "agent-interface/examples/evidence-adequacy/resource_authenticity_pass.json",
    "agent-interface/examples/evidence-adequacy/authorized_agent_action_pass.json",
    "agent-interface/examples/evidence-adequacy/human_oversight_pass.json",
    "agent-interface/examples/evidence-adequacy/execution_boundary_pass.json",
}
PROFILE_ROOT = ROOT / "agent-interface/profiles/evidence-adequacy"
EVALUATOR_SNAPSHOT_COMMIT = "be6ab57878dc7346da733e2f3b134aa3d3049af8"
SNAPSHOT_COMPONENT_SHA256 = {
    "saee_backend/services/evidence_adequacy.py": "d11b8e06d7197706ec103fb211c0578647c29dfc1fe1ae1bb16a98005b0c2688",
    "agent-interface/profiles/evidence-adequacy/authorized-agent-action.v0.1.json": "df9d3e0d6b4335b700f7d9b10b60444ebb50e58c4fa0a781035684b8f49a61d3",
    "agent-interface/profiles/evidence-adequacy/execution-boundary.v0.1.json": "88b51b1e6cc7b6ed8ca3d74dc37b11d4dfc759b8900bbe16ec199feeefa29f5d",
    "agent-interface/profiles/evidence-adequacy/human-oversight.v0.1.json": "a042466816ad000be78b28d1b7152efcc4d0be2df6094fe34e957b9897afa86e",
    "agent-interface/profiles/evidence-adequacy/resource-authenticity.v0.1.json": "193076004f732063c1192af8ed1207fd1fc1a23ce52a87ece1c7a76103602e4f",
    "agent-interface/examples/evidence-adequacy/authorized_agent_action_pass.json": "ca1d3977ee630fc05ce37cf6122f6dc39a5f293e131ed3fc73976c2740eb1467",
    "agent-interface/examples/evidence-adequacy/execution_boundary_pass.json": "de0340017692e92a0b2bc5a0f38d8c75f7d79b6ef4e3b309a2028afabab32903",
    "agent-interface/examples/evidence-adequacy/human_oversight_pass.json": "b4be8c51d1e30be22ef8d32d8cbe7863246f01f22b82566dd0e09421c12cb2d8",
    "agent-interface/examples/evidence-adequacy/resource_authenticity_pass.json": "2c980cb54a57bb974482b8de3d754d06d3e8292f663bb8c31c8f1f6cc53e377c",
}
BOUNDARY_KEYS = (
    "accountability_claim_established",
    "event_occurrence_proven",
    "identity_independently_verified",
    "authorization_externally_verified",
    "legal_finding_established",
    "production_ready",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_snapshot_components() -> dict[str, str]:
    actual = {
        reference: file_sha256(ROOT / reference)
        for reference in SNAPSHOT_COMPONENT_SHA256
    }
    if actual != SNAPSHOT_COMPONENT_SHA256:
        raise ValueError("evaluator/profile/fixture snapshot does not match the pinned pre-study hashes")
    return actual


def json_shape(value: Any) -> Any:
    """Return a value-insensitive JSON key/type signature.

    Booleans are separated from integers even though ``bool`` subclasses
    ``int`` in Python. Arrays retain length and element signatures so this is a
    stronger baseline than required-field presence, but it still ignores the
    semantic relations among values.
    """

    if isinstance(value, dict):
        return {
            "type": "object",
            "properties": {key: json_shape(item) for key, item in sorted(value.items())},
        }
    if isinstance(value, list):
        return {"type": "array", "length": len(value), "items": [json_shape(item) for item in value]}
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if value is None:
        return "null"
    raise TypeError(f"unsupported JSON value type: {type(value)!r}")


def resolve(document: Any, pointer: str) -> tuple[bool, Any]:
    current = document
    for segment in pointer.split("/")[1:]:
        if not isinstance(current, dict) or segment not in current:
            return False, None
        current = current[segment]
    return current not in (None, "", [], {}), current


def pointer_parent(document: dict[str, Any], pointer: str) -> tuple[dict[str, Any], str]:
    segments = pointer.split("/")[1:]
    if not segments:
        raise ValueError("root mutation is not allowed")
    current: Any = document
    for segment in segments[:-1]:
        if not isinstance(current, dict) or segment not in current:
            raise ValueError(f"mutation path does not exist: {pointer}")
        current = current[segment]
    if not isinstance(current, dict):
        raise ValueError(f"mutation parent is not an object: {pointer}")
    return current, segments[-1]


def apply_mutations(package: dict[str, Any], mutations: list[dict[str, Any]]) -> dict[str, Any]:
    result = copy.deepcopy(package)
    for mutation in mutations:
        parent, key = pointer_parent(result, mutation["path"])
        if mutation.get("operation") != "replace" or key not in parent:
            raise ValueError("only replacement of existing fields is permitted")
        parent[key] = copy.deepcopy(mutation["value"])
    return result


def load_fixture(reference: str) -> dict[str, Any]:
    if reference not in ALLOWED_FIXTURES:
        raise ValueError(f"fixture is not allowlisted: {reference}")
    path = (ROOT / reference).resolve()
    expected_parent = (ROOT / "agent-interface/examples/evidence-adequacy").resolve()
    if path.parent != expected_parent or not path.is_file():
        raise ValueError(f"fixture path escaped the canonical directory: {reference}")
    value = read_json(path)
    if not isinstance(value, dict):
        raise ValueError("fixture must be a JSON object")
    return value


def load_required_fields(claim_type: str) -> list[str]:
    profile_filename = PROFILE_FILES[claim_type]
    profile_path = (PROFILE_ROOT / profile_filename).resolve()
    if profile_path.parent != PROFILE_ROOT.resolve():
        raise ValueError("profile path escaped the canonical directory")
    profile = read_json(profile_path)
    return profile["required_evidence_fields"]


def reconstructability(package: dict[str, Any], required_fields: list[str]) -> dict[str, Any]:
    evidence = package.get("evidence", {})
    present = [path for path in required_fields if resolve(evidence, path)[0]]
    missing = [path for path in required_fields if path not in present]
    score = len(present) / len(required_fields)
    return {
        "required_operands": len(required_fields),
        "present_operands": len(present),
        "score": round(score, 6),
        "complete": score == 1.0,
        "missing_operands": missing,
    }


def decision_aware_ablation_support(
    claim_type: str,
    package: dict[str, Any],
    *,
    structurally_complete: bool,
) -> bool:
    """Apply only explicit nominal-decision checks, not relation predicates."""

    if not structurally_complete:
        return False
    evidence = package["evidence"]
    if claim_type == "AUTHORIZED_AGENT_ACTION":
        return evidence["policy_decision"].get("decision") == "allow"
    if claim_type == "HUMAN_OVERSIGHT":
        return evidence["approval"].get("decision") == "approved"
    return True


def confusion(rows: list[dict[str, Any]], prediction_key: str) -> dict[str, Any]:
    tp = sum(row["expected_semantic_adequacy"] and row[prediction_key] for row in rows)
    fp = sum(not row["expected_semantic_adequacy"] and row[prediction_key] for row in rows)
    tn = sum(not row["expected_semantic_adequacy"] and not row[prediction_key] for row in rows)
    fn = sum(row["expected_semantic_adequacy"] and not row[prediction_key] for row in rows)

    def ratio(numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 6) if denominator else 0.0

    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    specificity = ratio(tn, tn + fp)
    return {
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "balanced_accuracy": round((recall + specificity) / 2, 6),
        "f1": ratio(2 * precision * recall, precision + recall),
    }


def validate_dataset(dataset: Any) -> None:
    if not isinstance(dataset, dict) or dataset.get("dataset_version") != "0.1.0":
        raise ValueError("unsupported dataset")
    pairs = dataset.get("pairs")
    if not isinstance(pairs, list) or len(pairs) != 16:
        raise ValueError("dataset must contain 16 matched pairs")
    pair_ids = [pair.get("pair_id") for pair in pairs]
    if len(set(pair_ids)) != 16 or any(not isinstance(value, str) for value in pair_ids):
        raise ValueError("pair identifiers must be unique strings")
    counts = Counter(pair.get("claim_type") for pair in pairs)
    if counts != Counter({claim: 4 for claim in CLAIMS}):
        raise ValueError("dataset must contain four pairs per claim type")
    for pair in pairs:
        if pair.get("fixture_ref") not in ALLOWED_FIXTURES:
            raise ValueError("dataset references a non-allowlisted fixture")
        mutations = pair.get("invalid_mutations")
        if not isinstance(mutations, list) or not mutations:
            raise ValueError("each pair must declare at least one invalid mutation")
        if any(mutation.get("operation") != "replace" for mutation in mutations):
            raise ValueError("dataset permits replacement mutations only")


def run_once(dataset: dict[str, Any]) -> dict[str, Any]:
    validate_dataset(dataset)
    rows: list[dict[str, Any]] = []
    pair_checks: list[dict[str, Any]] = []
    boundary_violation_count = 0

    for pair in dataset["pairs"]:
        base = load_fixture(pair["fixture_ref"])
        if base.get("claim_type") != pair["claim_type"]:
            raise ValueError(f"fixture claim mismatch for {pair['pair_id']}")
        invalid = apply_mutations(base, pair["invalid_mutations"])
        required_fields = load_required_fields(pair["claim_type"])
        base_shape = json_shape(base["evidence"])
        pair_rows: list[dict[str, Any]] = []

        for variant, package, expected in (
            ("valid", base, True),
            ("relation_invalid", invalid, False),
        ):
            reconstruction = reconstructability(package, required_fields)
            presence_vector = [
                resolve(package["evidence"], path)[0] for path in required_fields
            ]
            shape_matches_canonical = json_shape(package["evidence"]) == base_shape
            structurally_complete = reconstruction["complete"] and shape_matches_canonical
            evaluation = evaluate_evidence_adequacy(pair["claim_type"], package)
            semantic_support = evaluation["result"] == "PASS"
            reason_codes_match = (
                evaluation["reason_codes"] == []
                if expected
                else evaluation["reason_codes"] == pair["expected_invalid_reason_codes"]
            )
            boundary_violation = any(evaluation.get(key) is True for key in BOUNDARY_KEYS)
            boundary_violation_count += int(boundary_violation)
            row = {
                "case_id": f"{pair['pair_id']}:{variant}",
                "pair_id": pair["pair_id"],
                "claim_type": pair["claim_type"],
                "condition": pair["condition"],
                "variant": variant,
                "nominal_outcome": pair["nominal_outcome"],
                "bounded_reconstructability": reconstruction,
                "required_field_presence_vector": presence_vector,
                "evidence_shape_sha256": stable_hash(json_shape(package["evidence"])),
                "field_complete_baseline_support": reconstruction["complete"],
                "type_and_shape_baseline_support": structurally_complete,
                "decision_aware_ablation_support": decision_aware_ablation_support(
                    pair["claim_type"],
                    package,
                    structurally_complete=structurally_complete,
                ),
                "semantic_profile_support": semantic_support,
                "expected_semantic_adequacy": expected,
                "semantic_expectation_match": semantic_support == expected,
                "reason_codes": evaluation["reason_codes"],
                "reason_codes_match": reason_codes_match,
                "failed_relationships": evaluation["failed_relationships"],
                "boundary_violation": boundary_violation,
            }
            pair_rows.append(row)
            rows.append(row)

        pair_checks.append(
            {
                "pair_id": pair["pair_id"],
                "same_nominal_outcome": pair_rows[0]["nominal_outcome"] == pair_rows[1]["nominal_outcome"],
                "both_reconstructability_complete": all(
                    row["bounded_reconstructability"]["complete"] for row in pair_rows
                ),
                "identical_required_field_presence_vector": (
                    pair_rows[0]["required_field_presence_vector"]
                    == pair_rows[1]["required_field_presence_vector"]
                ),
                "identical_json_shape": (
                    pair_rows[0]["evidence_shape_sha256"]
                    == pair_rows[1]["evidence_shape_sha256"]
                ),
                "semantic_verdict_diverges": (
                    pair_rows[0]["semantic_profile_support"]
                    != pair_rows[1]["semantic_profile_support"]
                ),
            }
        )

    field_baseline = confusion(rows, "field_complete_baseline_support")
    type_and_shape_baseline = confusion(rows, "type_and_shape_baseline_support")
    decision_aware_ablation = confusion(rows, "decision_aware_ablation_support")
    semantic_profile = confusion(rows, "semantic_profile_support")
    result = {
        "saee_reconstructability_adequacy_study_result_v0_1": True,
        "dataset_id": dataset["dataset_id"],
        "dataset_version": dataset["dataset_version"],
        "study_design": dataset["study_design"],
        "total_pairs": len(pair_checks),
        "total_cases": len(rows),
        "claim_pair_counts": dict(sorted(Counter(row["claim_type"] for row in rows if row["variant"] == "valid").items())),
        "reconstructability_complete_cases": sum(
            row["bounded_reconstructability"]["complete"] for row in rows
        ),
        "semantic_positive_cases": sum(row["expected_semantic_adequacy"] for row in rows),
        "semantic_negative_cases": sum(not row["expected_semantic_adequacy"] for row in rows),
        "matched_pairs_with_same_nominal_outcome": sum(item["same_nominal_outcome"] for item in pair_checks),
        "matched_pairs_with_complete_reconstructability": sum(
            item["both_reconstructability_complete"] for item in pair_checks
        ),
        "matched_pairs_with_identical_presence_vector": sum(
            item["identical_required_field_presence_vector"] for item in pair_checks
        ),
        "matched_pairs_with_identical_json_shape": sum(
            item["identical_json_shape"] for item in pair_checks
        ),
        "matched_pairs_with_divergent_semantic_verdict": sum(
            item["semantic_verdict_diverges"] for item in pair_checks
        ),
        "semantic_expectation_matches": sum(row["semantic_expectation_match"] for row in rows),
        "reason_code_matches": sum(row["reason_codes_match"] for row in rows),
        "field_complete_baseline": field_baseline,
        "type_and_shape_baseline": type_and_shape_baseline,
        "decision_aware_ablation": decision_aware_ablation,
        "semantic_profile_evaluator": semantic_profile,
        "false_support_reduction_on_designed_negatives": (
            field_baseline["false_positive"] - semantic_profile["false_positive"]
        ),
        "boundary_violation_count": boundary_violation_count,
        "pair_checks": pair_checks,
        "case_results": rows,
        "claims": {
            "supports_bounded_construct_counterexample": (
                all(item["both_reconstructability_complete"] for item in pair_checks)
                and all(item["semantic_verdict_diverges"] for item in pair_checks)
            ),
            "supports_presence_equivalence_impossibility_instances": (
                all(item["identical_required_field_presence_vector"] for item in pair_checks)
                and all(item["semantic_verdict_diverges"] for item in pair_checks)
            ),
            "establishes_real_world_prevalence": False,
            "establishes_external_identity_or_authority": False,
            "establishes_production_readiness": False,
            "establishes_general_product_superiority": False,
        },
        "execution_boundary": {
            "network_accessed": False,
            "external_resource_read": False,
            "subprocess_started": False,
            "candidate_code_executed": False,
        },
        "limitations": [
            "The study uses authored synthetic fixtures and isolated mutations; rates are construct-validation results, not population estimates.",
            "Bounded reconstructability is operationalized as complete presence of the operands declared by each SAEE evidence profile; it is not the eight-property Load-Bearing Evidence metric.",
            "Semantic profile PASS supports only the named closed-package profile and does not authorize an action or establish external truth.",
            "The same canonical pass fixture is reused within a claim type to isolate one semantic condition per pair.",
        ],
    }
    return result


def run_repeated(dataset: dict[str, Any], repetitions: int) -> dict[str, Any]:
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    component_hashes = verify_snapshot_components()
    runs = [run_once(dataset) for _ in range(repetitions)]
    hashes = [stable_hash(run) for run in runs]
    return {
        "experiment_run_manifest_v0_1": True,
        "dataset_sha256": stable_hash(dataset),
        "artifact_provenance": {
            "evaluator_snapshot_commit": EVALUATOR_SNAPSHOT_COMMIT,
            "component_sha256": component_hashes,
            "snapshot_hashes_match": True,
        },
        "repetitions": repetitions,
        "result_sha256_by_run": hashes,
        "deterministic": len(set(hashes)) == 1,
        "canonical_result_sha256": hashes[0],
        "result": runs[0],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    dataset_path = args.dataset.resolve()
    if dataset_path != DEFAULT_DATASET.resolve():
        raise ValueError("only the canonical dataset.v0.1.json is accepted")
    manifest = run_repeated(read_json(dataset_path), args.repetitions)
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        output_path = args.output.resolve()
        if output_path.parent != EXPERIMENT_ROOT.resolve():
            raise ValueError("output must remain inside the experiment directory")
        output_path.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
