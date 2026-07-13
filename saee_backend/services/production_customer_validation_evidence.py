"""Production customer validation evidence readiness checks.

This module validates a local evidence JSON file for future production
customer-validation review. It does not contact customers, run pilot sessions,
collect customer data, publish validation claims, launch product, change API
schema, modify runtime behavior, or inspect private core.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from saee_backend.config import SaeeBackendSettings


ProductionCustomerValidationEvidenceStatus = Literal["pass", "hold", "stop"]
ProductionCustomerValidationEvidenceSeverity = Literal["info", "blocker"]

PILOT_RESULT_KEYS = (
    "at_least_one_human_approved_pilot_session_completed",
    "pilot_result_template_completed",
    "feedback_form_completed",
    "success_criteria_applied",
    "boundary_flags_reviewed",
    "pilot_result_reviewed_by_human",
)
CUSTOMER_VALUE_KEYS = (
    "customer_role_and_segment_recorded",
    "pain_point_fit_observed",
    "deployment_decision_value_observed",
    "recommendation_output_understood",
    "failure_summary_usefulness_observed",
    "go_hold_pivot_decision_recorded",
)
CLAIM_PERMISSION_KEYS = (
    "real_customer_or_target_user_feedback_recorded",
    "permission_to_use_feedback_recorded",
    "customer_problem_fit_reviewed",
    "decision_usefulness_observed",
    "claim_scope_approved",
    "customer_validation_record_approved_by_human",
    "reviewer_approved_validation_claim",
)
BOUNDARY_REVIEW_KEYS = (
    "no_private_core_disclosed",
    "no_customer_secrets_collected",
    "no_customer_upload_required",
    "no_production_ready_claim_added",
    "no_public_launch_claim_added",
    "negative_feedback_recorded",
)
FORBIDDEN_TRUE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "customer_contacted_by_codex",
    "automated_customer_contact",
    "unsolicited_customer_contact",
    "customer_data_collected",
    "customer_data_processing_started",
    "customer_secrets_collected",
    "user_upload_enabled",
    "product_market_fit_claimed",
    "revenue_validated",
    "production_readiness_claimed",
    "public_validation_claim_published",
    "testimonial_published",
    "case_study_published",
    "paid_pilot_completed",
)


@dataclass(frozen=True)
class ProductionCustomerValidationEvidenceFinding:
    check_id: str
    severity: ProductionCustomerValidationEvidenceSeverity
    passed: bool
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "check_id": self.check_id,
            "severity": self.severity,
            "passed": self.passed,
            "message": self.message,
        }


def _finding(
    check_id: str,
    severity: ProductionCustomerValidationEvidenceSeverity,
    passed: bool,
    message: str,
) -> ProductionCustomerValidationEvidenceFinding:
    return ProductionCustomerValidationEvidenceFinding(
        check_id=check_id,
        severity=severity,
        passed=passed,
        message=message,
    )


def _all_true(data: dict[str, object], keys: tuple[str, ...]) -> bool:
    return all(data.get(key) is True for key in keys)


def _missing_true_keys(data: dict[str, object], keys: tuple[str, ...]) -> list[str]:
    return [key for key in keys if data.get(key) is not True]


def _read_evidence(path_value: str) -> tuple[bool, bool, dict[str, object]]:
    if not path_value:
        return False, False, {}
    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_file():
        return False, False, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True, False, {}
    if not isinstance(data, dict):
        return True, False, {}
    return True, True, data


def evaluate_production_customer_validation_evidence(
    settings: SaeeBackendSettings,
) -> dict[str, object]:
    """Return deterministic production customer-validation evidence readiness.

    A `pass` means a local evidence file is internally complete enough for
    human production launch review to consider the validation blockers
    satisfied. It is not a public customer-validation claim, product launch,
    customer contact action, product-market-fit claim, revenue validation, or
    production-readiness approval.
    """

    path_configured = bool(settings.production_customer_validation_evidence_path)
    file_exists, file_parseable, data = _read_evidence(
        settings.production_customer_validation_evidence_path
    )
    correct_type = (
        data.get("customer_validation_evidence_type")
        == "production_customer_validation_evidence"
    )
    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    pilot_results_evidence_complete = _all_true(data, PILOT_RESULT_KEYS)
    customer_value_evidence_complete = _all_true(data, CUSTOMER_VALUE_KEYS)
    claim_permission_evidence_complete = _all_true(data, CLAIM_PERMISSION_KEYS)
    boundary_review_evidence_complete = _all_true(data, BOUNDARY_REVIEW_KEYS)
    customer_validation_evidence_complete = (
        pilot_results_evidence_complete
        and customer_value_evidence_complete
        and claim_permission_evidence_complete
        and boundary_review_evidence_complete
        and not forbidden_true
    )

    findings = [
        _finding(
            "customer_validation_evidence_path_configured",
            "blocker",
            path_configured,
            "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH must point to local customer-validation evidence",
        ),
        _finding(
            "customer_validation_evidence_file_exists",
            "blocker",
            file_exists,
            "customer-validation evidence file must exist locally",
        ),
        _finding(
            "customer_validation_evidence_file_parseable",
            "blocker",
            file_parseable,
            "customer-validation evidence file must be parseable JSON",
        ),
        _finding(
            "customer_validation_evidence_type_valid",
            "blocker",
            correct_type,
            "customer_validation_evidence_type must be production_customer_validation_evidence",
        ),
        _finding(
            "pilot_results_evidence_complete",
            "blocker",
            pilot_results_evidence_complete,
            "pilot-results evidence must be complete",
        ),
        _finding(
            "customer_value_evidence_complete",
            "blocker",
            customer_value_evidence_complete,
            "customer value evidence must be complete",
        ),
        _finding(
            "claim_permission_evidence_complete",
            "blocker",
            claim_permission_evidence_complete,
            "claim permission and human approval evidence must be complete",
        ),
        _finding(
            "boundary_review_evidence_complete",
            "blocker",
            boundary_review_evidence_complete,
            "boundary review evidence must be complete",
        ),
        _finding(
            "boundary_non_claims",
            "blocker",
            not forbidden_true,
            "customer-validation evidence must not claim customer validation, production readiness, public launch, revenue validation, product-market fit, external calls, customer contact by Codex, user uploads, customer secrets, private-core exposure, or code modification",
        ),
        _finding(
            "no_external_actions",
            "info",
            True,
            "readiness check only reads a local evidence file and performs no external action",
        ),
    ]

    blocking_failures = [
        finding
        for finding in findings
        if finding.severity == "blocker" and not finding.passed
    ]
    status: ProductionCustomerValidationEvidenceStatus
    if forbidden_true:
        status = "stop"
    elif blocking_failures:
        status = "hold"
    else:
        status = "pass"

    return {
        "production_customer_validation_evidence_type": "production_customer_validation_evidence_readiness",
        "production_customer_validation_evidence_readiness_v0_1": True,
        "status": status,
        "customer_validation_evidence_path_configured": path_configured,
        "customer_validation_evidence_file_exists": file_exists,
        "customer_validation_evidence_file_parseable": file_parseable,
        "customer_validation_evidence_type_valid": correct_type,
        "pilot_results_evidence_complete": pilot_results_evidence_complete,
        "customer_value_evidence_complete": customer_value_evidence_complete,
        "claim_permission_evidence_complete": claim_permission_evidence_complete,
        "boundary_review_evidence_complete": boundary_review_evidence_complete,
        "customer_validation_evidence_complete": customer_validation_evidence_complete,
        "production_customer_validation_ready": customer_validation_evidence_complete,
        "pilot_results_missing_evidence": _missing_true_keys(data, PILOT_RESULT_KEYS),
        "customer_value_missing_evidence": _missing_true_keys(data, CUSTOMER_VALUE_KEYS),
        "claim_permission_missing_evidence": _missing_true_keys(
            data, CLAIM_PERMISSION_KEYS
        ),
        "boundary_review_missing_evidence": _missing_true_keys(
            data, BOUNDARY_REVIEW_KEYS
        ),
        "boundary_violation_count": len(forbidden_true),
        "boundary_violations": forbidden_true,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted_by_codex": False,
        "automated_customer_contact": False,
        "unsolicited_customer_contact": False,
        "customer_data_collected": False,
        "customer_data_processing_started": False,
        "customer_secrets_collected": False,
        "user_upload_enabled": False,
        "product_market_fit_claimed": False,
        "revenue_validated": False,
        "production_readiness_claimed": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "paid_pilot_completed": False,
        "findings": [finding.as_dict() for finding in findings],
        "blocker_count": len(blocking_failures),
        "next_action": "human launch review may use this evidence only after all other production blockers are resolved"
        if status == "pass"
        else "complete pilot-result, customer-value, claim-permission, and boundary-review evidence before launch review",
    }
