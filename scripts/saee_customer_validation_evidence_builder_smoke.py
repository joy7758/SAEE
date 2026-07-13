#!/usr/bin/env python3
"""Smoke check for the customer-validation evidence builder."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_customer_validation_evidence import (
    BOUNDARY_REVIEW_KEYS,
    CLAIM_PERMISSION_KEYS,
    CUSTOMER_VALUE_KEYS,
    FORBIDDEN_TRUE_KEYS,
    PILOT_RESULT_KEYS,
    evaluate_production_customer_validation_evidence,
)
from scripts.saee_customer_validation_evidence_builder import (
    DEFAULT_OUTPUT_PATH,
    INPUT_TEMPLATE_PATH,
    build_from_file,
    write_template,
)


BUILDER_DOC = ROOT / "phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_BUILDER_V0_1.md"
GATE_DOC = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"
BUILDER_SCRIPT = ROOT / "scripts/saee_customer_validation_evidence_builder.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_CUSTOMER_VALIDATION_EVIDENCE_BUILDER_SMOKE: FAIL: " + message)


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    review_keys = (
        PILOT_RESULT_KEYS
        + CUSTOMER_VALUE_KEYS
        + CLAIM_PERMISSION_KEYS
        + BOUNDARY_REVIEW_KEYS
    )
    return {
        "customer_validation_evidence_input_v0_1": True,
        "customer_validated": False,
        "customer_contacted": False,
        "product_launched": False,
        "production_ready": False,
        "private_core_exposed": False,
        "sessions": [
            {
                "session_id": "PILOT-20260704-001",
                "session_date": "2026-07-04",
                "participant_role": "AI platform lead",
                "team_type": "enterprise AI engineering",
                "current_evaluation_method": "manual LangSmith trace review",
                "candidate_count": 3,
                "saee_demo_surface_used": "local_mvp_demo",
                "understanding_score": 5,
                "trust_score": 4,
                "decision_influence_score": 4,
                "repeat_usage_intent_score": 4,
                "time_to_value_minutes": 12,
                "top_objection": "Needs production auth and support evidence before real use.",
                "evidence_missing": "External pilot and legal review evidence.",
                "willing_to_test_own_candidates": True,
                "boundary_flags": {
                    "secrets_collected": unsafe,
                    "production_data_collected": False,
                    "customer_data_uploaded": False,
                    "private_core_disclosed": False,
                    "production_ready_claim_made": False,
                },
                "notes": "Human-filled pilot result for local evidence conversion smoke.",
            }
        ],
        "aggregate_metrics": {
            "session_count": 1,
            "understanding_rate": 1.0,
            "trust_rate": 0.8,
            "decision_influence_rate": 0.8,
            "repeat_usage_intent": 0.8,
            "go_hold_pivot": "hold",
        },
        "evidence_review": {key: True for key in review_keys},
    }


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def readiness(path: Path) -> dict[str, object]:
    return evaluate_production_customer_validation_evidence(
        load_settings({"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(path)})
    )


def main() -> None:
    require(BUILDER_DOC.exists(), "builder doc missing")
    require(GATE_DOC.exists(), "builder gate missing")
    require(BUILDER_SCRIPT.exists(), "builder script missing")

    template = write_template()
    require(INPUT_TEMPLATE_PATH.exists(), "input template not written")
    require(template["customer_validation_evidence_input_v0_1"] is True, "template flag")
    require(
        all(value is False for value in template["evidence_review"].values()),
        "template review flags must default false",
    )

    default_summary = subprocess.run(
        [sys.executable, str(BUILDER_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_payload = json.loads(default_summary.stdout)
    require(default_payload["readiness_status"] == "hold", "default build must hold")
    require(default_payload["customer_validation_evidence_complete"] is False, "default complete false")
    require(default_payload["production_customer_validation_ready"] is False, "default ready false")
    require(default_payload["codex_contacted_customer"] is False, "codex contact false")
    require(DEFAULT_OUTPUT_PATH.exists(), "default output missing")

    default_evidence = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    for key in FORBIDDEN_TRUE_KEYS:
        require(default_evidence.get(key) is False, f"default forbidden {key} false")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_input_path = tmp / "complete_pilot_result.json"
        complete_output_path = tmp / "complete_customer_validation_evidence.json"
        unsafe_input_path = tmp / "unsafe_pilot_result.json"
        unsafe_output_path = tmp / "unsafe_customer_validation_evidence.json"
        write_json(complete_input_path, complete_input())
        write_json(unsafe_input_path, complete_input(unsafe=True))

        complete_evidence = build_from_file(complete_input_path, complete_output_path)
        complete_readiness = readiness(complete_output_path)
        complete_go_no_go = evaluate_commercial_go_no_go(
            load_settings(
                {"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(complete_output_path)}
            )
        )
        unsafe_evidence = build_from_file(unsafe_input_path, unsafe_output_path)
        unsafe_readiness = readiness(unsafe_output_path)

    require(complete_evidence["completed_session_count"] == 1, "complete session count")
    require(complete_evidence["input_boundary_violation_count"] == 0, "complete boundary clean")
    require(complete_readiness["status"] == "pass", "complete readiness pass")
    require(complete_readiness["customer_validation_evidence_complete"] is True, "complete evidence true")
    require(
        complete_readiness["production_customer_validation_ready"] is True,
        "complete production customer-validation evidence ready",
    )
    unsatisfied = {
        str(item["blocker_id"]) for item in complete_go_no_go["unsatisfied_blockers"]
    }
    require("pilot_results" not in unsatisfied, "pilot_results satisfied by complete evidence")
    require("customer_validated" not in unsatisfied, "customer_validated satisfied by complete evidence")
    require(complete_go_no_go["production_ready"] is False, "complete evidence does not make production ready")
    require(complete_go_no_go["customer_validated"] is False, "complete evidence does not claim customer validated")

    require(unsafe_evidence["input_boundary_violation_count"] > 0, "unsafe boundary detected")
    require(unsafe_readiness["status"] == "hold", "unsafe input must hold")
    require(
        unsafe_readiness["boundary_review_evidence_complete"] is False,
        "unsafe boundary review incomplete",
    )

    doc = BUILDER_DOC.read_text(encoding="utf-8")
    gate = GATE_DOC.read_text(encoding="utf-8")
    combined = doc + "\n" + gate
    for token in [
        "customer_validation_evidence_builder_v0_1: true",
        "builder_scope: human_filled_local_pilot_result_to_customer_validation_evidence",
        "production_customer_validation_ready_default: false",
        "customer_validated: false",
        "production_ready: false",
        "customer_contacted_by_codex: false",
        "external_calls_made: false",
        "private_core_exposed: false",
        "codex_inferred_missing_results: false",
        "answer: conditional",
        "recommend_for_customer_contact: false",
        "recommend_for_production_launch: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/CUSTOMER_VALIDATION_EVIDENCE_BUILDER_V0_1.md",
        "/docs/strategy/SAEE_CUSTOMER_VALIDATION_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.from_pilot.local.json",
        "/scripts/saee_customer_validation_evidence_builder.py",
        "/scripts/saee_customer_validation_evidence_builder_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("customer_validation_evidence_builder_v0_1", {})
    expected = {
        "status": "local_builder_available_default_hold",
        "customer_validation_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_local_pilot_result_to_customer_validation_evidence",
        "default_output_status": "hold",
        "production_customer_validation_ready_default": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "customer_contacted_by_codex": False,
        "external_calls_made": False,
        "codex_executed_pilot": False,
        "codex_inferred_missing_results": False,
        "codex_collected_customer_data": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_CUSTOMER_VALIDATION_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_human_input_pass=true unsafe_input_hold=true "
        "customer_validated=false production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
