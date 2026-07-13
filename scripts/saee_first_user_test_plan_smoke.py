#!/usr/bin/env python3
"""Validate the SAEE first-user test plan boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def require_tokens(relpath: str, tokens: list[str]) -> None:
    text = read(relpath)
    missing = [token for token in tokens if token not in text]
    if missing:
        raise SystemExit(f"{relpath} missing required tokens: {', '.join(missing)}")


def reject_tokens(relpath: str, tokens: list[str]) -> None:
    text = read(relpath)
    found = [token for token in tokens if token in text]
    if found:
        raise SystemExit(f"{relpath} contains forbidden tokens: {', '.join(found)}")


def main() -> None:
    required_files = [
        "docs/strategy/SAEE_FIRST_USER_TEST_RECOMMENDATION_GATE.md",
        "phase_b_product/validation/README.md",
        "phase_b_product/validation/SAEE_FIRST_USER_TEST_PLAN.md",
        "phase_b_product/validation/FIRST_USER_FEEDBACK_FORM.md",
        "phase_b_product/validation/FIRST_USER_SUCCESS_CRITERIA.md",
        "phase_b_product/validation/PILOT_RESULT_TEMPLATE.json",
    ]
    missing_files = [relpath for relpath in required_files if not (ROOT / relpath).is_file()]
    if missing_files:
        raise SystemExit("missing first-user test files: " + ", ".join(missing_files))

    require_tokens(
        "docs/strategy/SAEE_FIRST_USER_TEST_RECOMMENDATION_GATE.md",
        [
            "recommendation_gate",
            "SAEE First User Test Plan",
            "answer: recommend",
            "customer_validated: false",
            "product_launched: false",
            "user_upload_enabled: false",
            "private_core_exported: false",
        ],
    )
    require_tokens(
        "phase_b_product/validation/SAEE_FIRST_USER_TEST_PLAN.md",
        [
            "Goal = Validate decision usefulness of SAEE output",
            "understanding_rate",
            "trust_rate",
            "decision_influence_rate",
            "repeat_usage_intent",
            "Do not record secrets",
            "customer_validated: false",
        ],
    )
    require_tokens(
        "phase_b_product/validation/FIRST_USER_FEEDBACK_FORM.md",
        [
            "understanding_score",
            "trust_score",
            "decision_influence_score",
            "repeat_usage_intent_score",
            "Do not collect secrets",
        ],
    )
    require_tokens(
        "phase_b_product/validation/FIRST_USER_SUCCESS_CRITERIA.md",
        [
            "Go Criteria",
            "Hold Criteria",
            "Pivot Criteria",
            "product_market_fit_claimed: false",
            "production_readiness_claimed: false",
        ],
    )
    require_tokens(
        "phase_b_product/validation/PILOT_RESULT_TEMPLATE.json",
        [
            "\"pilot_result_template_v0_1\": true",
            "\"customer_validated\": false",
            "\"customer_contacted\": false",
            "\"product_launched\": false",
            "\"production_ready\": false",
            "\"private_core_exposed\": false",
            "\"secrets_collected\": false",
            "\"production_data_collected\": false",
            "\"customer_data_uploaded\": false",
            "\"private_core_disclosed\": false",
        ],
    )

    forbidden = [
        "customer_validated: true",
        "product_launched: true",
        "production_deployed: true",
        "user_upload_enabled: true",
        "private_core_exported: true",
        "api_contract_modified: true",
        "decision_engine_modified: true",
        "saee_v1_0/kernel",
        "selection_engine",
        "mutation_engine",
        "fitness_engine",
        "lineage_engine",
    ]
    for relpath in required_files:
        reject_tokens(relpath, forbidden)

    print(
        "SAEE_FIRST_USER_TEST_PLAN_SMOKE: PASS "
        "plan=true feedback_form=true success_criteria=true "
        "customer_validated=false product_launched=false"
    )


if __name__ == "__main__":
    main()
