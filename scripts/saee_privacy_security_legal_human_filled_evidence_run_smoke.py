#!/usr/bin/env python3
"""Smoke check for the privacy/security/legal human-filled evidence run."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
SUMMARY_PATH = EVIDENCE_DIR / "privacy_security_legal_human_filled_evidence_run_summary.local.json"
PROFILE_PATH = (
    EVIDENCE_DIR
    / "privacy_security_legal_evidence_profile.from_formal_privacy_dpa_vulnerability_human_filled.local.json"
)
DEFAULT_EVIDENCE_PATH = EVIDENCE_DIR / "privacy_security_legal_evidence.local.json"

FALSE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "customer_contacted",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "security_vendor_contacted",
    "legal_counsel_contacted",
    "customer_data_processed",
    "customer_data_processing_started",
    "dpa_sent_to_customer",
    "terms_published",
    "privacy_notice_published",
    "production_security_enabled",
    "vulnerability_management_operational",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRIVACY_SECURITY_LEGAL_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: FAIL "
            + message
        )


def read_json(path: Path) -> dict[str, object]:
    require(path.exists(), f"missing {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            "SAEE_PRIVACY_SECURITY_LEGAL_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: FAIL "
            f"invalid JSON {path.relative_to(ROOT)}: {exc}"
        ) from exc
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must be object")
    return data


def main() -> None:
    summary = read_json(SUMMARY_PATH)
    profile = read_json(PROFILE_PATH)
    default_evidence = read_json(DEFAULT_EVIDENCE_PATH)

    require(summary["run_status"] == "pass", "run_status must be pass")
    require(summary["validation_status"] == "pass", "validation_status must be pass")
    require(
        summary["formal_security_review_validation_status"] == "pass",
        "formal security validation must pass",
    )
    require(
        summary["privacy_legal_dpa_validation_status"] == "pass",
        "privacy/legal/DPA validation must pass",
    )
    require(
        summary["vulnerability_management_validation_status"] == "pass",
        "vulnerability-management validation must pass",
    )
    require(
        summary["privacy_security_legal_profile_status"] == "pass",
        "profile status must be pass",
    )
    require(
        summary["production_privacy_security_legal_ready"] is True,
        "privacy/security/legal evidence must be ready for go/no-go review",
    )
    require(
        summary["privacy_security_legal_satisfied_blockers"]
        == [
            "formal_security_review",
            "privacy_legal_review",
            "data_processing_agreement",
            "vulnerability_management",
        ],
        "privacy/security/legal satisfied blockers must match the four target blockers",
    )
    require(
        summary[
            "support_data_ops_operations_privacy_security_legal_production_blocker_count"
        ]
        == 12,
        "combined blocker count must be 12",
    )
    require(
        profile["support_contact_used_for_go_no_go"] == "joy7758@gmail.com",
        "support contact used for local go/no-go must be recorded",
    )
    require(
        default_evidence["formal_security_review_report"] is False,
        "default privacy/security/legal evidence must remain unpromoted",
    )

    for key in FALSE_KEYS:
        require(summary.get(key) is False, f"summary {key} must be false")
        require(profile.get(key) is False, f"profile {key} must be false")

    for path_text in summary["input_files"] + summary["output_files"]:
        path = Path(str(path_text))
        require(path.exists(), f"referenced evidence file missing: {path}")

    print(
        "SAEE_PRIVACY_SECURITY_LEGAL_HUMAN_FILLED_EVIDENCE_RUN_SMOKE: PASS "
        "privacy_security_legal_profile_status=pass production_blockers=12 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
