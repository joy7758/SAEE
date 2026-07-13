#!/usr/bin/env python3
"""Smoke check for the local-only Baidu Cloud handoff staging package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "phase_b_product/commercial_readiness/cloud_handoff/package_001"
SUMMARY = PACKAGE_DIR / "baidu_cloud_handoff_package.local.json"
REPORT = PACKAGE_DIR / "baidu_cloud_handoff_package.md"
MANIFEST = PACKAGE_DIR / "baidu_cloud_handoff_package_manifest.csv"
README = PACKAGE_DIR / "README.md"
AUDIT = PACKAGE_DIR / "baidu_cloud_handoff_package_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/BAIDU_CLOUD_HANDOFF_PACKAGE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_BAIDU_CLOUD_HANDOFF_PACKAGE_RECOMMENDATION_GATE.md"
RUNNER = ROOT / "scripts/saee_baidu_cloud_handoff_package.py"

FORBIDDEN_PREFIXES = (
    "files/saee_v1_0/",
    "files/saee_backend/",
    "files/kernel/",
    "files/kernel_v0_2/",
    "files/schemas/",
)
FORBIDDEN_EXACT = {
    "files/phase_b_product/landing/index.html",
    "files/phase_b_product/landing/app.js",
    "files/phase_b_product/landing/styles.css",
}


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_BAIDU_CLOUD_HANDOFF_PACKAGE_SMOKE: FAIL: {message}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    for path in [SUMMARY, REPORT, MANIFEST, README, AUDIT, TOP_DOC, GATE, RUNNER]:
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    expected = {
        "baidu_cloud_handoff_package_v0_1": True,
        "status": "local_package_ready_for_human_review",
        "package_id": "package_001",
        "cloud_target_id": "i-8xOwPKN3",
        "package_scope": "docs_and_readiness_files_only",
        "source_preflight_status": "ready_for_human_cloud_clear_confirmation",
        "packaged_file_count": 38,
        "expected_file_count": 38,
        "cloud_clear_required_before_sync": True,
        "destructive_cloud_operation_requires_separate_confirmation": True,
        "human_review_required": True,
        "human_cloud_clear_confirmation_required": True,
        "human_cloud_upload_confirmation_required": True,
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
        "blockers_closed_by_package": 0,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            fail(f"{key} must be {value!r}")

    files = data.get("files")
    if not isinstance(files, list) or len(files) != 38:
        fail("files must contain exactly 38 records")

    with MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        manifest_rows = list(csv.DictReader(handle))
    if len(manifest_rows) != 38:
        fail("package manifest CSV must contain exactly 38 records")

    for row in files:
        package_path = row.get("package_path", "")
        if not package_path.startswith("files/"):
            fail(f"package path must stay under files/: {package_path}")
        if package_path in FORBIDDEN_EXACT or package_path.startswith(FORBIDDEN_PREFIXES):
            fail(f"package includes forbidden path: {package_path}")
        destination = PACKAGE_DIR / package_path
        if not destination.is_file():
            fail(f"packaged file missing: {package_path}")
        if sha256_file(destination) != row.get("sha256"):
            fail(f"sha256 mismatch: {package_path}")

    docs = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, README, AUDIT, TOP_DOC, GATE])
    for token in [
        "cloud_clear_performed: false",
        "cloud_sync_performed: false",
        "cloud_upload_authorized: false",
        "cloud_delete_authorized: false",
        "packaged_file_count: 38",
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
    for forbidden in ["requests.", "httpx", "webbrowser.open", "baidupcs", "bypy"]:
        if forbidden in runner:
            fail(f"runner contains forbidden token: {forbidden}")

    print(
        "SAEE_BAIDU_CLOUD_HANDOFF_PACKAGE_SMOKE: PASS "
        f"status={data['status']} "
        f"packaged_file_count={data['packaged_file_count']} "
        "cloud_clear_performed=false cloud_sync_performed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
