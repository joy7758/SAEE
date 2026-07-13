#!/usr/bin/env python3
"""Build a local-only Baidu Cloud handoff staging package.

The package is built from the preflight safe-upload manifest only. It copies
documentation and readiness evidence into a local staging directory and writes
hash manifests for human review. It does not clear cloud storage, upload files,
call cloud APIs, open a browser, package runtime/backend/kernel/API/private-core
files, contact customers, or claim production readiness.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/cloud_handoff/baidu_cloud_handoff_preflight.local.json"
)
PACKAGE_DIR = ROOT / "phase_b_product/commercial_readiness/cloud_handoff/package_001"
FILES_DIR = PACKAGE_DIR / "files"
PACKAGE_JSON = PACKAGE_DIR / "baidu_cloud_handoff_package.local.json"
PACKAGE_MD = PACKAGE_DIR / "baidu_cloud_handoff_package.md"
PACKAGE_MANIFEST = PACKAGE_DIR / "baidu_cloud_handoff_package_manifest.csv"
PACKAGE_README = PACKAGE_DIR / "README.md"
PACKAGE_AUDIT = PACKAGE_DIR / "baidu_cloud_handoff_package_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/BAIDU_CLOUD_HANDOFF_PACKAGE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_BAIDU_CLOUD_HANDOFF_PACKAGE_RECOMMENDATION_GATE.md"

FORBIDDEN_PREFIXES = (
    "saee_v1_0/",
    "saee_backend/",
    "kernel/",
    "kernel_v0_2/",
    "schemas/",
)
FORBIDDEN_EXACT = {
    "phase_b_product/landing/index.html",
    "phase_b_product/landing/app.js",
    "phase_b_product/landing/styles.css",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_forbidden(rel: str) -> bool:
    return rel in FORBIDDEN_EXACT or any(rel.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)


def read_preflight() -> dict[str, Any]:
    data = json.loads(PREFLIGHT_JSON.read_text(encoding="utf-8"))
    if data.get("status") != "ready_for_human_cloud_clear_confirmation":
        raise SystemExit("preflight status is not ready_for_human_cloud_clear_confirmation")
    if data.get("cloud_target_id") != "i-8xOwPKN3":
        raise SystemExit("unexpected cloud target id")
    for key in [
        "cloud_clear_performed",
        "cloud_sync_performed",
        "cloud_upload_authorized",
        "cloud_delete_authorized",
        "production_ready",
        "private_core_exposed",
    ]:
        if data.get(key) is not False:
            raise SystemExit(f"preflight {key} must be false")
    return data


def prepare_package_dir() -> None:
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    FILES_DIR.mkdir(parents=True, exist_ok=True)


def copy_manifest_files(preflight: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in preflight.get("safe_upload_manifest", []):
        rel = row.get("path")
        if not isinstance(rel, str) or not rel:
            raise SystemExit("manifest row missing path")
        if row.get("safe_to_upload") is not True:
            raise SystemExit(f"manifest row is not safe_to_upload: {rel}")
        if is_forbidden(rel):
            raise SystemExit(f"manifest includes forbidden path: {rel}")
        source = ROOT / rel
        if not source.is_file():
            raise SystemExit(f"manifest source missing: {rel}")
        destination = FILES_DIR / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        rows.append(
            {
                "source_path": rel,
                "package_path": str(destination.relative_to(PACKAGE_DIR)),
                "size_bytes": destination.stat().st_size,
                "sha256": sha256_file(destination),
                "safe_to_upload": True,
            }
        )
    return rows


def write_manifest(rows: list[dict[str, Any]]) -> None:
    with PACKAGE_MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["source_path", "package_path", "size_bytes", "sha256", "safe_to_upload"],
        )
        writer.writeheader()
        writer.writerows(rows)


def build_payload(preflight: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "baidu_cloud_handoff_package_v0_1": True,
        "status": "local_package_ready_for_human_review",
        "package_id": "package_001",
        "cloud_target_id": preflight["cloud_target_id"],
        "package_scope": "docs_and_readiness_files_only",
        "source_preflight_status": preflight["status"],
        "source_preflight_path": str(PREFLIGHT_JSON.relative_to(ROOT)),
        "packaged_file_count": len(rows),
        "expected_file_count": preflight.get("safe_upload_candidate_count"),
        "manifest_path": str(PACKAGE_MANIFEST.relative_to(ROOT)),
        "files_root": str(FILES_DIR.relative_to(ROOT)),
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
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_baidu_cloud_handoff_package.py",
        "files": rows,
    }


def write_docs(payload: dict[str, Any]) -> None:
    table = "\n".join(
        "| {source_path} | {package_path} | {size_bytes} | {sha256} |".format(**row)
        for row in payload["files"]
    )
    content = f"""# SAEE Baidu Cloud Handoff Package v0.1

baidu_cloud_handoff_package_v0_1: true
status: {payload["status"]}
package_id: {payload["package_id"]}
cloud_target_id: {payload["cloud_target_id"]}
package_scope: {payload["package_scope"]}
packaged_file_count: {payload["packaged_file_count"]}
expected_file_count: {payload["expected_file_count"]}
cloud_clear_required_before_sync: true
destructive_cloud_operation_requires_separate_confirmation: true
cloud_clear_performed: false
cloud_sync_performed: false
cloud_upload_authorized: false
cloud_delete_authorized: false
blockers_closed_by_package: 0
production_ready: false
private_core_exposed: false

## Purpose

This local package stages the docs-and-readiness files approved by the Baidu
Cloud handoff preflight manifest. It is for human review before any possible
future cloud operation.

## Package Manifest

| Source path | Package path | Size bytes | SHA-256 |
| --- | --- | ---: | --- |
{table}

## Boundary

- No cloud clear was performed.
- No cloud sync was performed.
- No cloud upload is authorized by this package.
- No cloud delete is authorized by this package.
- Runtime, backend, kernel, API schema, landing interaction, and private-core
  files are excluded from the package scope.
- Production readiness, customer validation, product launch, and blocker
  closure remain false.
"""
    PACKAGE_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    PACKAGE_README.write_text(
        """# Baidu Cloud Handoff Package 001

This directory is a local staging package only. It was generated from the
Baidu Cloud handoff preflight safe-upload manifest.

It does not clear cloud storage, upload files, call cloud APIs, open a browser,
or authorize cloud deletion/upload. A separate explicit human confirmation is
required before any Baidu Cloud operation.
""",
        encoding="utf-8",
    )
    PACKAGE_AUDIT.write_text(
        """# Baidu Cloud Handoff Package Boundary Audit

- No cloud clear performed.
- No cloud sync performed.
- No cloud API called.
- No browser automation used.
- No runtime files packaged.
- No backend files packaged.
- No kernel files packaged.
- No API schema files packaged.
- No landing page interaction files packaged.
- No private core exposed.
- No product launched.
- No customer contacted.
- No production-ready claim added.
- No blocker closed.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Baidu Cloud Handoff Package Recommendation Gate

answer: recommend_for_human_cloud_handoff_review_only

reason: The local package stages only documentation and readiness evidence from
the preflight safe-upload manifest. It does not authorize cloud clear, upload,
or any production action.

boundary:
  cloud_clear_performed: false
  cloud_sync_performed: false
  cloud_upload_authorized: false
  cloud_delete_authorized: false
  runtime_modified: false
  backend_modified: false
  kernel_modified: false
  api_schema_modified: false
  private_core_exposed: false
  product_launched: false
  customer_contacted: false
  production_ready: false

next_action: Human must review the package and explicitly confirm cloud clear
and upload scope before any Baidu Cloud operation.
""",
        encoding="utf-8",
    )


def main() -> None:
    preflight = read_preflight()
    prepare_package_dir()
    rows = copy_manifest_files(preflight)
    if len(rows) != preflight.get("safe_upload_candidate_count"):
        raise SystemExit("packaged file count does not match preflight safe_upload_candidate_count")
    write_manifest(rows)
    payload = build_payload(preflight, rows)
    PACKAGE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_docs(payload)
    print(
        "SAEE_BAIDU_CLOUD_HANDOFF_PACKAGE: PASS "
        f"status={payload['status']} "
        f"packaged_file_count={payload['packaged_file_count']} "
        "cloud_clear_performed=false cloud_sync_performed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
