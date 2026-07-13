"""Raw metric counts for the controlled SAEE evaluation prototype."""

from __future__ import annotations

from typing import Any


def _fraction(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator}"


def calculate_evaluation_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate declared raw counts without producing an overall score."""

    if not records:
        raise ValueError("evaluation records are required")

    unsupported = [record for record in records if record["reference_profile_support"] is False]
    supportable = [record for record in records if record["reference_profile_support"] is True]
    false_accountability = sum(
        1 for record in unsupported if record["adequacy_result"] == "PASS"
    )
    supported_accepted = sum(
        1 for record in supportable if record["adequacy_result"] == "PASS"
    )

    relationship_required = sum(record["required_relationship_count"] for record in records)
    relationship_valid = sum(record["valid_relationship_count"] for record in records)

    exact_missing_matches = 0
    missing_tp = 0
    missing_fp = 0
    missing_fn = 0
    for record in records:
        expected = set(record["reference_missing_requirements"])
        actual = set(record["missing_requirements"])
        exact_missing_matches += int(expected == actual)
        missing_tp += len(expected & actual)
        missing_fp += len(actual - expected)
        missing_fn += len(expected - actual)

    return {
        "saee_evaluation_metrics_v0_1": True,
        "scope": "controlled_synthetic_prototype_raw_counts",
        "false_accountability_rate": {
            "numerator_false_accountability_count": false_accountability,
            "denominator_reference_unsupported_claims": len(unsupported),
            "raw_fraction": _fraction(false_accountability, len(unsupported)),
            "formula": "unsupported_claims_incorrectly_accepted / all_reference_unsupported_claims",
        },
        "claim_support_coverage": {
            "numerator_supported_claims_accepted": supported_accepted,
            "denominator_reference_supportable_claims": len(supportable),
            "raw_fraction": _fraction(supported_accepted, len(supportable)),
            "formula": "reference_supportable_claims_marked_profile_satisfied / all_reference_supportable_claims",
        },
        "evidence_relationship_completeness": {
            "numerator_valid_required_relationships": relationship_valid,
            "denominator_required_relationships": relationship_required,
            "raw_fraction": _fraction(relationship_valid, relationship_required),
            "formula": "present_and_reference_valid_required_relationships / all_required_relationships_for_claim",
        },
        "missing_evidence_identification": {
            "exact_set_match_count": exact_missing_matches,
            "claim_attempt_count": len(records),
            "exact_set_match_fraction": _fraction(exact_missing_matches, len(records)),
            "item_true_positive_count": missing_tp,
            "item_false_positive_count": missing_fp,
            "item_false_negative_count": missing_fn,
            "formula": "exact_missing_set_matches / all_controlled_claim_attempts; item counts reported separately",
        },
        "overall_accuracy_score_emitted": False,
        "overall_performance_score_emitted": False,
        "system_superiority_score_emitted": False,
        "scientific_result_claimed": False,
        "external_validation_completed": False,
        "production_ready": False,
    }
