#!/usr/bin/env python3
"""Generate local public-shell customer-validation evidence.

This runner converts existing pilot-validation readiness materials into a
partial production customer-validation evidence JSON file for human review. It
does not contact customers, run pilot sessions, collect customer data, publish
validation claims, create testimonials, create case studies, validate revenue,
modify backend behavior, modify API schema, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.pilot_validation_readiness import (
    evaluate_pilot_validation_readiness,
)
from saee_backend.services.production_customer_validation_evidence import (
    BOUNDARY_REVIEW_KEYS,
    CLAIM_PERMISSION_KEYS,
    CUSTOMER_VALUE_KEYS,
    FORBIDDEN_TRUE_KEYS,
    PILOT_RESULT_KEYS,
    evaluate_production_customer_validation_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUTPUT_PATH = OUTPUT_DIR / "customer_validation_evidence.local.json"
README_PATH = OUTPUT_DIR / "README.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_local_customer_validation_evidence() -> dict[str, Any]:
    readiness = evaluate_pilot_validation_readiness(load_settings({}))
    require(
        readiness["pilot_validation_readiness_type"]
        == "controlled_pilot_validation_readiness",
        "wrong pilot validation readiness type",
    )
    require(readiness["status"] == "hold", "pilot validation readiness must hold")
    require(
        readiness["first_user_test_plan_available"] is True,
        "first-user test plan must be available",
    )
    require(readiness["feedback_form_available"] is True, "feedback form must be available")
    require(
        readiness["success_criteria_available"] is True,
        "success criteria must be available",
    )
    require(
        readiness["pilot_result_template_available"] is True,
        "pilot result template must be available",
    )
    require(readiness["pilot_sessions_completed"] == 0, "runner must not run pilots")
    require(
        readiness["pilot_results_recorded"] is False,
        "runner must not record pilot results",
    )
    require(
        readiness["customer_permission_recorded"] is False,
        "runner must not record customer permission",
    )
    require(readiness["customer_contacted"] is False, "runner must not contact customers")
    require(
        readiness["customer_validated"] is False,
        "runner must not claim customer validation",
    )
    require(
        readiness["external_calls_made"] is False,
        "runner must not make external calls",
    )
    return readiness


def build_evidence() -> dict[str, Any]:
    readiness = run_local_customer_validation_evidence()

    evidence: dict[str, Any] = {
        "customer_validation_evidence_type": "production_customer_validation_evidence",
        "evidence_scope": "local_public_shell_customer_validation_review_packet",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_customer_validation_evidence_runner.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_pilot_validation_helper": (
            "saee_backend/services/pilot_validation_readiness.py"
        ),
        "first_user_test_plan_available": True,
        "feedback_form_available": True,
        "success_criteria_available": True,
        "pilot_result_template_available": True,
        "pilot_session_protocol_available": True,
        "at_least_one_human_approved_pilot_session_completed": False,
        "pilot_result_template_completed": False,
        "feedback_form_completed": False,
        "success_criteria_applied": False,
        "boundary_flags_reviewed": True,
        "pilot_result_reviewed_by_human": False,
        "customer_role_and_segment_recorded": False,
        "pain_point_fit_observed": False,
        "deployment_decision_value_observed": False,
        "recommendation_output_understood": False,
        "failure_summary_usefulness_observed": False,
        "go_hold_pivot_decision_recorded": False,
        "real_customer_or_target_user_feedback_recorded": False,
        "permission_to_use_feedback_recorded": False,
        "customer_problem_fit_reviewed": False,
        "decision_usefulness_observed": False,
        "claim_scope_approved": False,
        "customer_validation_record_approved_by_human": False,
        "reviewer_approved_validation_claim": False,
        "no_private_core_disclosed": True,
        "no_customer_secrets_collected": True,
        "no_customer_upload_required": True,
        "no_production_ready_claim_added": True,
        "no_public_launch_claim_added": True,
        "negative_feedback_recorded": False,
        "local_public_shell_results": {
            "pilot_validation_status": readiness["pilot_validation_status"],
            "first_user_test_plan_available": True,
            "feedback_form_available": True,
            "success_criteria_available": True,
            "pilot_result_template_available": True,
            "pilot_session_protocol_available": True,
            "pilot_sessions_completed": 0,
            "pilot_results_recorded": False,
            "customer_permission_recorded": False,
            "customer_contacted": False,
            "customer_validated": False,
            "product_market_fit_claimed": False,
            "revenue_validated": False,
            "production_readiness_claimed": False,
            "user_upload_enabled": False,
            "customer_data_processing_ready": False,
            "external_calls_made": False,
        },
        "limitations": [
            "No human-approved pilot session has been completed.",
            "No completed pilot result, feedback form, or applied success criteria exists.",
            "No real customer or target-user feedback has been recorded.",
            "No permission to use feedback has been recorded.",
            "No claim scope or customer-validation record has been approved by a human reviewer.",
            "No negative feedback has been recorded because no real pilot feedback exists.",
            "This evidence is local public-shell evidence only and does not close the production launch gate.",
        ],
    }
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False

    missing_expected = [
        key
        for key in (
            PILOT_RESULT_KEYS
            + CUSTOMER_VALUE_KEYS
            + CLAIM_PERMISSION_KEYS
            + BOUNDARY_REVIEW_KEYS
            + FORBIDDEN_TRUE_KEYS
        )
        if key not in evidence
    ]
    require(not missing_expected, "evidence missing keys: " + ", ".join(missing_expected))
    return evidence


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Customer Validation Evidence

Status: local public-shell customer-validation review evidence, not customer
validation and not production readiness.

This directory contains a generated local evidence JSON file for future
pilot-result and customer-validation review. It records only what the local
runner can prove from existing first-user and pilot-readiness materials.

It does not contact customers, run pilot sessions, collect customer data,
collect customer secrets, enable uploads, record real customer feedback,
publish validation claims, create testimonials, create case studies, validate
revenue, modify runtime behavior, modify backend behavior, modify API schema,
or expose private core.

Primary file:

```text
customer_validation_evidence.local.json
```

Generate it with:

```bash
python3 scripts/saee_customer_validation_evidence_runner.py
```

Boundary:

```yaml
evidence_scope: local_public_shell_customer_validation_review_packet
first_user_test_plan_available: true
feedback_form_available: true
success_criteria_available: true
pilot_result_template_available: true
pilot_sessions_completed: 0
pilot_results_recorded: false
customer_permission_recorded: false
real_customer_or_target_user_feedback_recorded: false
permission_to_use_feedback_recorded: false
customer_validation_evidence_complete: false
production_customer_validation_ready: false
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
customer_contacted_by_codex: false
automated_customer_contact: false
customer_data_collected: false
user_upload_enabled: false
public_validation_claim_published: false
testimonial_published: false
case_study_published: false
paid_pilot_completed: false
```
""",
        encoding="utf-8",
    )


def write_outputs() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = build_evidence()
    OUTPUT_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readme()
    return evidence


def main() -> None:
    write_outputs()
    readiness = evaluate_production_customer_validation_evidence(
        load_settings(
            {"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(OUTPUT_PATH)}
        )
    )
    require(
        readiness["status"] == "hold",
        "partial local customer validation evidence must hold",
    )
    require(
        readiness["production_customer_validation_ready"] is False,
        "partial local evidence must not claim customer validation readiness",
    )
    print(
        "SAEE_CUSTOMER_VALIDATION_EVIDENCE_RUNNER: PASS "
        f"path={OUTPUT_PATH.relative_to(ROOT)} "
        f"status={readiness['status']} "
        "local_public_shell_evidence=true "
        "production_customer_validation_ready=false"
    )


if __name__ == "__main__":
    main()
