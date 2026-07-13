#!/usr/bin/env python3
"""Smoke check for the local-only Baidu Cloud handoff preflight packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "phase_b_product/commercial_readiness/cloud_handoff/baidu_cloud_handoff_preflight.local.json"
REPORT = ROOT / "phase_b_product/commercial_readiness/cloud_handoff/baidu_cloud_handoff_preflight.md"
MANIFEST = ROOT / "phase_b_product/commercial_readiness/cloud_handoff/baidu_cloud_upload_manifest.csv"
CHECKLIST = ROOT / "phase_b_product/commercial_readiness/cloud_handoff/baidu_cloud_clear_first_checklist.md"
AUDIT = ROOT / "phase_b_product/commercial_readiness/cloud_handoff/baidu_cloud_handoff_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/BAIDU_CLOUD_HANDOFF_PREFLIGHT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_BAIDU_CLOUD_HANDOFF_PREFLIGHT_RECOMMENDATION_GATE.md"
RUNNER = ROOT / "scripts/saee_baidu_cloud_handoff_preflight.py"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_BAIDU_CLOUD_HANDOFF_PREFLIGHT_SMOKE: FAIL: {message}")


def main() -> None:
    for path in [SUMMARY, REPORT, MANIFEST, CHECKLIST, AUDIT, TOP_DOC, GATE, RUNNER]:
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    expected = {
        "baidu_cloud_handoff_preflight_v0_1": True,
        "status": "ready_for_human_cloud_clear_confirmation",
        "cloud_target_id": "i-8xOwPKN3",
        "handoff_scope": "docs_and_readiness_manifest_only_no_runtime_upload",
        "cloud_clear_required_before_sync": True,
        "destructive_cloud_operation_requires_separate_confirmation": True,
        "human_review_required": True,
        "human_cloud_clear_confirmation_required": True,
        "human_cloud_upload_confirmation_required": True,
        "blockers_closed_by_preflight": 0,
        "cloud_clear_performed": False,
        "cloud_sync_performed": False,
        "cloud_upload_authorized": False,
        "cloud_delete_authorized": False,
        "external_calls_made": False,
        "browser_opened_by_script": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "landing_page_interaction_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "customer_contacted": False,
        "customer_validated": False,
        "production_ready": False,
        "public_sdk_released": False,
        "payment_provider_configured": False,
        "paid_trial_enabled": False,
        "external_ai_assistant_tested": False,
        "external_validation_claim": False,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            fail(f"{key} must be {value!r}")

    manifest = data.get("safe_upload_manifest")
    if not isinstance(manifest, list) or not manifest:
        fail("safe_upload_manifest must be a non-empty list")
    if data.get("safe_upload_candidate_count", 0) < 20:
        fail("safe_upload_candidate_count must be at least 20")
    forbidden_prefixes = tuple(data.get("forbidden_prefixes_excluded") or [])
    for row in manifest:
        path = row.get("path", "")
        if row.get("safe_to_upload") and path.startswith(forbidden_prefixes):
            fail(f"safe manifest includes forbidden path: {path}")

    docs = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, CHECKLIST, AUDIT, TOP_DOC, GATE])
    for token in [
        "cloud_clear_performed: false",
        "cloud_sync_performed: false",
        "cloud_upload_authorized: false",
        "cloud_delete_authorized: false",
        "production_ready: false",
        "private_core_exposed: false",
        "No cloud clear was performed.",
        "No cloud sync was performed.",
    ]:
        if token not in docs:
            fail(f"missing token: {token}")
    for token in [
        "cloud_clear_performed: true",
        "cloud_sync_performed: true",
        "cloud_upload_authorized: true",
        "cloud_delete_authorized: true",
        "production_ready: true",
        "private_core_exposed: true",
    ]:
        if token in docs:
            fail(f"forbidden true claim: {token}")

    runner = RUNNER.read_text(encoding="utf-8")
    for forbidden in ["requests.", "httpx", "webbrowser.open", "baidupcs", "bypy", "shutil.rmtree"]:
        if forbidden in runner:
            fail(f"runner contains forbidden token: {forbidden}")

    print(
        "SAEE_BAIDU_CLOUD_HANDOFF_PREFLIGHT_SMOKE: PASS "
        f"status={data['status']} "
        f"safe_upload_candidate_count={data['safe_upload_candidate_count']} "
        "cloud_clear_performed=false cloud_sync_performed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
