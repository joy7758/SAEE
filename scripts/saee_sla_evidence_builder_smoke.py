#!/usr/bin/env python3
"""Smoke check for the SAEE SLA evidence builder."""

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
from saee_backend.services.production_support_evidence import (
    CUSTOMER_SUPPORT_KEYS,
    ON_CALL_KEYS,
    SLA_KEYS,
    SUPPORT_CONTACT_KEYS,
    evaluate_production_support_evidence,
)
from scripts.saee_sla_evidence_builder import (
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SUPPORT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    INPUT_FORBIDDEN_TRUE_KEYS,
    REPORT_PATH,
    build_from_input,
)


BUILDER_SCRIPT = ROOT / "scripts/saee_sla_evidence_builder.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_SLA_EVIDENCE_BUILDER_SMOKE: FAIL: " + message)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    evidence_review = {key: True for key in SLA_KEYS}
    source_notes = {
        key: f"Human-reviewed SLA source note for {key}." for key in SLA_KEYS
    }
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["production_ready"] = True
    return {
        "template_type": "saee_sla_evidence_input",
        "template_version": "v0.1",
        "input_status": "human_filled_fixture_for_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-04",
        "sla_terms_owner": "Fixture Commercial Owner",
        "legal_reviewer_name": "Fixture Legal Reviewer",
        "decision_summary": "Fixture-only SLA evidence for deterministic smoke validation.",
        "evidence_review": evidence_review,
        "source_notes_by_key": source_notes,
        "boundary_review": boundary_review,
        "sla_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://sla/{key}",
                "owner_named": True,
                "legal_or_commercial_reviewed": True,
                "human_source_note": f"Fixture-only human source note for {key}.",
            }
            for key in SLA_KEYS
        ],
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
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "sla_published_by_codex": False,
        "sla_approved_by_codex": False,
        "legal_review_completed_by_codex": False,
        "support_hours_published_by_codex": False,
        "response_targets_published_by_codex": False,
        "support_operations_started": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "execution_authorized": False,
        "blockers_closed_by_builder": False,
        "production_sla_claim_published": False,
    }


def support_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_support_evidence(
        load_settings({"SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(path)})
    )


def main() -> None:
    require(BUILDER_SCRIPT.exists(), "builder script missing")

    default_run = subprocess.run(
        [sys.executable, str(BUILDER_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_summary = json.loads(default_run.stdout)
    require(default_summary["status"] == "hold", "default builder status must hold")
    require(default_summary["input_complete"] is False, "default input must be incomplete")
    require(
        default_summary["sla_available_for_review"] is False,
        "default SLA must not be available",
    )
    require(
        default_summary["production_support_available"] is False,
        "default production support must be false",
    )
    require(default_summary["blockers_closed_by_builder"] == 0, "no default closure")
    require(DEFAULT_INPUT_PATH.exists(), "default input template missing")
    require(DEFAULT_OUTPUT_PATH.exists(), "default output missing")
    require(DEFAULT_SUPPORT_OUTPUT_PATH.exists(), "default support evidence missing")

    default_evidence = json.loads(DEFAULT_SUPPORT_OUTPUT_PATH.read_text(encoding="utf-8"))
    for key in SUPPORT_CONTACT_KEYS + CUSTOMER_SUPPORT_KEYS + SLA_KEYS + ON_CALL_KEYS:
        require(default_evidence.get(key) is False, f"default evidence {key} false")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_input_path = tmp / "complete_sla_input.json"
        complete_output_path = tmp / "complete_builder_output.json"
        complete_support_path = tmp / "complete_support_evidence.json"
        unsafe_input_path = tmp / "unsafe_sla_input.json"
        unsafe_output_path = tmp / "unsafe_builder_output.json"
        unsafe_support_path = tmp / "unsafe_support_evidence.json"

        write_json(complete_input_path, complete_input())
        write_json(unsafe_input_path, complete_input(unsafe=True))

        complete_summary = build_from_input(
            complete_input_path,
            complete_output_path,
            complete_support_path,
            write_documentation=False,
        )
        unsafe_summary = build_from_input(
            unsafe_input_path,
            unsafe_output_path,
            unsafe_support_path,
            write_documentation=False,
        )
        complete_readiness = support_readiness(complete_support_path)
        unsafe_readiness = support_readiness(unsafe_support_path)

    require(complete_summary["status"] == "pass", "complete fixture summary pass")
    require(complete_summary["input_complete"] is True, "complete fixture input complete")
    require(
        complete_summary["sla_available_for_review"] is True,
        "complete fixture SLA available",
    )
    require(
        complete_summary["production_support_available"] is False,
        "complete fixture still not production support",
    )
    require(complete_readiness["sla_available"] is True, "complete readiness SLA available")
    require(complete_readiness["status"] == "hold", "complete support readiness still hold")
    require(complete_readiness["support_contact_available"] is False, "support contact false")
    require(complete_readiness["customer_support_available"] is False, "customer support false")
    require(complete_readiness["on_call_rotation_available"] is False, "on-call false")
    require(
        complete_summary["blockers_closed_by_builder"] == 0,
        "complete fixture closes no blockers",
    )
    require(unsafe_summary["status"] == "stop", "unsafe fixture stops")
    require(unsafe_summary["input_boundary_violation_count"] > 0, "unsafe violations")
    require(unsafe_readiness["sla_available"] is False, "unsafe SLA remains unavailable")

    subprocess.run(
        [sys.executable, str(BUILDER_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "sla_evidence_builder_v0_1: true",
        "builder_scope: human_filled_sla_approval_to_production_support_evidence",
        "required_evidence_item_count: 6",
        "blockers_closed_by_builder: 0",
        "production_support_available: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "recommend_for_production_launch: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/SLA_EVIDENCE_BUILDER_V0_1.md",
        "/docs/strategy/SAEE_SLA_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/support_evidence/sla_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/support_evidence/sla_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/production_support_sla_evidence.from_sla.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/sla_evidence_builder_report.md",
        "/scripts/saee_sla_evidence_builder.py",
        "/scripts/saee_sla_evidence_builder_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("sla_evidence_builder_v0_1", {})
    expected = {
        "status": "local_builder_available_default_hold",
        "builder_scope": "human_filled_sla_approval_to_production_support_evidence",
        "sla_available_for_review": False,
        "production_support_available": False,
        "support_contact_available": False,
        "customer_support_available": False,
        "on_call_rotation_available": False,
        "blockers_closed_by_builder": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_SLA_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_sla_available=true "
        "production_support_available=false blockers_closed_by_builder=0"
    )


if __name__ == "__main__":
    main()
