#!/usr/bin/env python3
"""Smoke test the external customer-validation session kit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUTPUT_JSON = EVIDENCE_DIR / "external_customer_validation_session_kit.local.json"
OUTPUT_MD = EVIDENCE_DIR / "external_customer_validation_session_kit.md"
INTERVIEW_SCRIPT = EVIDENCE_DIR / "external_customer_validation_interview_script.md"
FEEDBACK_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_feedback_form.template.md"
FIELD_MAP = EVIDENCE_DIR / "external_customer_validation_field_mapping.csv"
BOUNDARY_AUDIT = EVIDENCE_DIR / "external_customer_validation_session_kit_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT_GATE.md"
RUNNER = ROOT / "scripts/saee_external_customer_validation_session_kit.py"


def fail(message: str) -> None:
    raise SystemExit("SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT_SMOKE: FAIL " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    required_files = [
        OUTPUT_JSON,
        OUTPUT_MD,
        INTERVIEW_SCRIPT,
        FEEDBACK_TEMPLATE,
        FIELD_MAP,
        BOUNDARY_AUDIT,
        GATE,
        RUNNER,
    ]
    for path in required_files:
        require(path.is_file(), f"missing required file {path.relative_to(ROOT)}")

    payload = read_json(OUTPUT_JSON)
    expected = {
        "external_customer_validation_session_kit_v0_1": True,
        "status": "ready_for_human_external_customer_validation_session",
        "kit_type": "manual_external_customer_validation_session_kit",
        "current_goal_blocker": "customer_validated",
        "remaining_blocker_count": 1,
        "session_kit_ready": True,
        "interview_script_ready": True,
        "feedback_form_ready": True,
        "field_mapping_ready": True,
        "required_real_external_sessions_min": 1,
        "target_session_count": 1,
        "human_action_required": True,
        "codex_may_contact_customer": False,
        "codex_may_run_external_pilot": False,
        "codex_may_collect_customer_data": False,
        "codex_may_infer_customer_feedback": False,
        "codex_may_run_validator_after_human_filled_input": True,
        "customer_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "production_ready": False,
        "product_launched": False,
        "customer_validated": False,
        "customer_contacted": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "public_sdk_released": False,
        "public_validation_claim_published": False,
        "testimonial_published": False,
        "case_study_published": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_session_kit": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(payload.get("field_mapping_count") == 15, "field mapping count must be 15")
    require(
        "session_id" in payload.get("session_fields", []),
        "session fields must include session_id",
    )
    require(
        "repeat_usage_intent_score" in payload.get("session_fields", []),
        "session fields must include repeat_usage_intent_score",
    )

    field_map_lines = FIELD_MAP.read_text(encoding="utf-8").strip().splitlines()
    require(len(field_map_lines) == 16, "field map must contain header plus 15 rows")
    for text, token in [
        (OUTPUT_MD.read_text(encoding="utf-8"), "external_customer_validation_session_kit_v0_1: true"),
        (OUTPUT_MD.read_text(encoding="utf-8"), "customer_validated: false"),
        (INTERVIEW_SCRIPT.read_text(encoding="utf-8"), "不会收集你的源码、密钥、生产数据或客户数据"),
        (INTERVIEW_SCRIPT.read_text(encoding="utf-8"), "部署、暂缓或重测"),
        (FEEDBACK_TEMPLATE.read_text(encoding="utf-8"), "secrets_collected: false"),
        (FEEDBACK_TEMPLATE.read_text(encoding="utf-8"), "production_ready_claim_made: false"),
        (BOUNDARY_AUDIT.read_text(encoding="utf-8"), "Codex may contact customer: false"),
        (GATE.read_text(encoding="utf-8"), "answer: ready_for_human_external_customer_validation_session"),
    ]:
        require(token in text, "missing session kit token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_kit.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_kit.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_interview_script.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_feedback_form.template.md",
        "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT_GATE.md",
        "/scripts/saee_external_customer_validation_session_kit.py",
        "/scripts/saee_external_customer_validation_session_kit_smoke.py",
    ]:
        require(token in llms, "llms.txt missing token: " + token)

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for token in [
        "external-customer-validation-session-kit-smoke:",
        "check-external-customer-validation-session-kit:",
        "scripts/saee_external_customer_validation_session_kit_smoke.py",
    ]:
        require(token in makefile, "Makefile missing token: " + token)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("external_customer_validation_session_kit_v0_1", {})
    require(isinstance(entry, dict), "agent-index entry must be object")
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_SESSION_KIT_SMOKE: PASS "
        "status=ready_for_human_external_customer_validation_session "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
