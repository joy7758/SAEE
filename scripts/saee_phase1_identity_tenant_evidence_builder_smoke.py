#!/usr/bin/env python3
"""Smoke check for the Phase 1 identity/tenant evidence builder."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.production_auth_evidence import (
    AUTH_IDP_KEYS,
    OAUTH_OIDC_KEYS,
    RBAC_KEYS,
    evaluate_production_auth_evidence,
)
from saee_backend.services.production_tenant_storage_evidence import (
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
    evaluate_production_tenant_storage_evidence,
)
from saee_backend.config import load_settings
from scripts.saee_phase1_identity_tenant_evidence_builder import (
    ALL_EVIDENCE_KEYS,
    DEFAULT_AUTH_OUTPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_TENANT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    INPUT_FORBIDDEN_TRUE_KEYS,
    INPUT_TEMPLATE_PATH,
    OUTPUT_DIR,
    build_from_input,
    write_template,
)


BUILDER_SCRIPT = ROOT / "scripts/saee_phase1_identity_tenant_evidence_builder.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_BUILDER_SMOKE: FAIL: " + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    evidence_review = {key: True for key in ALL_EVIDENCE_KEYS}
    source_notes = {
        key: f"Human-reviewed production evidence note for {key}."
        for key in ALL_EVIDENCE_KEYS
    }
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["production_ready"] = True
    return {
        "phase_1_identity_tenant_evidence_input_v0_1": True,
        "input_status": "human_filled_fixture_for_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-04",
        "evidence_source_notes": "Fixture-only complete input for deterministic smoke validation.",
        "evidence_review": evidence_review,
        "source_notes_by_key": source_notes,
        "boundary_review": boundary_review,
        "codex_inferred_missing_evidence": False,
        "codex_contacted_identity_provider": False,
        "codex_fetched_jwks": False,
        "codex_validated_production_tokens": False,
        "codex_ran_storage_migration": False,
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "storage_migration_executed": False,
        "customer_data_processed": False,
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
        "customer_contacted": False,
    }


def auth_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_auth_evidence(
        load_settings({"SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(path)})
    )


def tenant_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_tenant_storage_evidence(
        load_settings({"SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(path)})
    )


def main() -> None:
    require(BUILDER_SCRIPT.exists(), "builder script missing")

    template = write_template()
    require(INPUT_TEMPLATE_PATH.exists(), "input template missing")
    require(
        template["phase_1_identity_tenant_evidence_input_v0_1"] is True,
        "template flag missing",
    )
    require(len(template["evidence_review"]) == 33, "template must expose 33 evidence keys")
    require(
        all(value is False for value in template["evidence_review"].values()),
        "template evidence flags must default false",
    )
    require(
        all(value is False for value in template["boundary_review"].values()),
        "template boundary flags must default false",
    )

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
    require(default_summary["required_evidence_item_count"] == 33, "required item count")
    require(default_summary["auth_readiness_status"] == "hold", "default auth holds")
    require(
        default_summary["tenant_storage_readiness_status"] == "hold",
        "default tenant storage holds",
    )
    require(default_summary["blockers_closed_by_builder"] == 0, "builder closes no blockers")
    require(default_summary["production_ready"] is False, "default production ready false")
    require(default_summary["customer_validated"] is False, "default customer validated false")
    require(DEFAULT_OUTPUT_PATH.exists(), "default output missing")
    require(DEFAULT_AUTH_OUTPUT_PATH.exists(), "default auth output missing")
    require(DEFAULT_TENANT_OUTPUT_PATH.exists(), "default tenant output missing")

    default_auth = json.loads(DEFAULT_AUTH_OUTPUT_PATH.read_text(encoding="utf-8"))
    default_tenant = json.loads(DEFAULT_TENANT_OUTPUT_PATH.read_text(encoding="utf-8"))
    for key in AUTH_IDP_KEYS + OAUTH_OIDC_KEYS + RBAC_KEYS:
        require(default_auth.get(key) is False, f"default auth {key} false")
    for key in (
        TENANT_STORAGE_MODEL_KEYS
        + TENANT_ISOLATION_TEST_KEYS
        + TENANT_OPERATIONS_KEYS
        + TENANT_SECURITY_PRIVACY_KEYS
    ):
        require(default_tenant.get(key) is False, f"default tenant {key} false")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_input_path = tmp / "complete_phase1_input.json"
        complete_output_path = tmp / "complete_builder_output.json"
        complete_auth_path = tmp / "complete_auth_evidence.json"
        complete_tenant_path = tmp / "complete_tenant_evidence.json"
        unsafe_input_path = tmp / "unsafe_phase1_input.json"
        unsafe_output_path = tmp / "unsafe_builder_output.json"
        unsafe_auth_path = tmp / "unsafe_auth_evidence.json"
        unsafe_tenant_path = tmp / "unsafe_tenant_evidence.json"

        write_json(complete_input_path, complete_input())
        write_json(unsafe_input_path, complete_input(unsafe=True))

        complete_summary = build_from_input(
            complete_input_path,
            complete_output_path,
            complete_auth_path,
            complete_tenant_path,
        )
        unsafe_summary = build_from_input(
            unsafe_input_path,
            unsafe_output_path,
            unsafe_auth_path,
            unsafe_tenant_path,
        )
        complete_auth_readiness = auth_readiness(complete_auth_path)
        complete_tenant_readiness = tenant_readiness(complete_tenant_path)
        unsafe_auth_readiness = auth_readiness(unsafe_auth_path)
        unsafe_tenant_readiness = tenant_readiness(unsafe_tenant_path)

    require(complete_summary["status"] == "pass", "complete fixture summary pass")
    require(complete_summary["input_complete"] is True, "complete fixture input complete")
    require(complete_auth_readiness["status"] == "pass", "complete auth readiness pass")
    require(
        complete_tenant_readiness["status"] == "pass",
        "complete tenant storage readiness pass",
    )
    require(complete_summary["production_ready"] is False, "complete fixture no production claim")
    require(
        complete_summary["blockers_closed_by_builder"] == 0,
        "complete fixture does not close blockers",
    )
    require(unsafe_summary["status"] == "stop", "unsafe fixture stops")
    require(unsafe_summary["input_boundary_violation_count"] > 0, "unsafe violations recorded")
    require(unsafe_auth_readiness["status"] == "hold", "unsafe auth evidence must hold")
    require(unsafe_tenant_readiness["status"] == "hold", "unsafe tenant evidence must hold")

    for path in [
        OUTPUT_DIR / "README.md",
        DOC_PATH,
        GATE_PATH,
        OUTPUT_DIR / "phase_1_identity_tenant_evidence_builder_report.md",
    ]:
        require(path.exists(), f"{path} missing")

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            OUTPUT_DIR / "README.md",
            DOC_PATH,
            GATE_PATH,
            OUTPUT_DIR / "phase_1_identity_tenant_evidence_builder_report.md",
        ]
    )
    for token in [
        "phase_1_identity_tenant_evidence_builder_v0_1: true",
        "builder_scope: human_filled_phase_1_identity_tenant_evidence_to_go_no_go_inputs",
        "required_evidence_item_count: 33",
        "blockers_closed_by_builder: 0",
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
        "/phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_EVIDENCE_BUILDER_V0_1.md",
        "/docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/README.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_builder_report.md",
        "/scripts/saee_phase1_identity_tenant_evidence_builder.py",
        "/scripts/saee_phase1_identity_tenant_evidence_builder_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("phase_1_identity_tenant_evidence_builder_v0_1", {})
    expected_entry = {
        "status": "local_builder_available_default_hold",
        "phase_1_identity_tenant_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_phase_1_identity_tenant_evidence_to_go_no_go_inputs",
        "required_evidence_item_count": 33,
        "auth_required_evidence_item_count": 15,
        "tenant_required_evidence_item_count": 18,
        "default_output_status": "hold",
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "storage_migration_executed": False,
        "customer_data_processed": False,
    }
    for key, expected_value in expected_entry.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_pass=true unsafe_fixture_stop=true "
        "required_items=33 blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
