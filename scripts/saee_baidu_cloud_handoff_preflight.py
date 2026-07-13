#!/usr/bin/env python3
"""Generate a local-only Baidu Cloud handoff preflight packet.

This script records a safe handoff checklist for a possible future Baidu Cloud
sync. It does not clear cloud storage, upload files, call cloud APIs, open a
browser, package runtime code, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CLOUD_TARGET_ID = "i-8xOwPKN3"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/cloud_handoff"
SUMMARY_JSON = OUTPUT_DIR / "baidu_cloud_handoff_preflight.local.json"
REPORT_MD = OUTPUT_DIR / "baidu_cloud_handoff_preflight.md"
MANIFEST_CSV = OUTPUT_DIR / "baidu_cloud_upload_manifest.csv"
CLEAR_CHECKLIST_MD = OUTPUT_DIR / "baidu_cloud_clear_first_checklist.md"
BOUNDARY_AUDIT_MD = OUTPUT_DIR / "baidu_cloud_handoff_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/BAIDU_CLOUD_HANDOFF_PREFLIGHT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_BAIDU_CLOUD_HANDOFF_PREFLIGHT_RECOMMENDATION_GATE.md"

SAFE_UPLOAD_CANDIDATES = [
    "README.md",
    "PROJECT_STATUS.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "agent-readable.md",
    "llms.txt",
    "agent-index.json",
    "agent_recommendation/PRODUCT_FACTS.md",
    "agent_recommendation/PRODUCT_FACTS.json",
    "agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/RECOMMENDATION_DECISION_TREE.md",
    "agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md",
    "agent_recommendation/VALIDATION_RESULTS.md",
    "agent_recommendation/internal_self_play/SELF_PLAY_RESULTS.md",
    "phase_b_product/landing/for-ai-assistants.html",
    "phase_b_product/commercial_readiness/commercial_readiness_status.md",
    "phase_b_product/commercial_readiness/commercial_readiness_status.local.json",
    "phase_b_product/commercial_readiness/commercial_readiness_status.csv",
    "phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.md",
    "phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.local.json",
    "phase_b_product/commercial_readiness/CONTROLLED_TRIAL_QUICKSTART_V0_1.md",
    "phase_b_product/commercial_readiness/LOCAL_TRIAL_SESSION_MANAGER_V0_1.md",
    "phase_b_product/commercial_readiness/LOCAL_TRIAL_MAKE_TARGETS_V0_1.md",
    "phase_b_product/validation/LOCAL_TRIAL_PREFLIGHT_SNAPSHOT_V0_1.md",
    "phase_b_product/validation/local_trial_preflight_snapshot.local.json",
    "phase_b_product/validation/LOCAL_TRIAL_COLD_START_PREFLIGHT_V0_1.md",
    "phase_b_product/validation/local_trial_cold_start_preflight.local.json",
    "phase_b_product/validation/local_trial_cold_start_preflight.md",
    "phase_b_product/validation/LOCAL_TRIAL_HTTP_E2E_V0_1.md",
    "phase_b_product/validation/local_trial_http_e2e/local_trial_http_e2e.local.json",
    "phase_b_product/validation/local_trial_http_e2e/local_trial_http_e2e.md",
    "phase_b_product/validation/LOCAL_TRIAL_LIFECYCLE_PROOF_V0_1.md",
    "phase_b_product/validation/local_trial_lifecycle_proof/local_trial_lifecycle_proof.local.json",
    "phase_b_product/validation/local_trial_lifecycle_proof/local_trial_lifecycle_proof.md",
    "phase_b_product/validation/LOCAL_TRIAL_HANDOFF_PACKET_V0_1.md",
    "phase_b_product/validation/local_trial_handoff_packet.local.json",
    "phase_b_product/validation/local_trial_handoff_packet.md",
]

FORBIDDEN_PREFIXES = [
    "saee_v1_0/",
    "saee_backend/",
    "kernel/",
    "kernel_v0_2/",
    "schemas/",
    "phase_b_product/landing/index.html",
    "phase_b_product/landing/app.js",
    "phase_b_product/landing/styles.css",
]


def boundary_flags() -> dict[str, bool]:
    return {
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


def candidate_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in SAFE_UPLOAD_CANDIDATES:
        path = ROOT / rel
        forbidden = any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
        rows.append(
            {
                "path": rel,
                "exists": path.is_file(),
                "size_bytes": path.stat().st_size if path.is_file() else 0,
                "safe_to_upload": path.is_file() and not forbidden,
                "reason": "agent-readable documentation or local readiness evidence",
            }
        )
    return rows


def build_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    safe_count = sum(1 for row in rows if row["safe_to_upload"])
    missing = [row["path"] for row in rows if not row["exists"]]
    return {
        "baidu_cloud_handoff_preflight_v0_1": True,
        "status": "ready_for_human_cloud_clear_confirmation",
        "cloud_target_id": CLOUD_TARGET_ID,
        "handoff_scope": "docs_and_readiness_manifest_only_no_runtime_upload",
        "cloud_clear_required_before_sync": True,
        "destructive_cloud_operation_requires_separate_confirmation": True,
        "human_review_required": True,
        "human_cloud_clear_confirmation_required": True,
        "human_cloud_upload_confirmation_required": True,
        "safe_upload_candidate_count": safe_count,
        "candidate_count": len(rows),
        "missing_candidate_count": len(missing),
        "missing_candidates": missing,
        "forbidden_prefixes_excluded": FORBIDDEN_PREFIXES,
        "safe_upload_manifest": rows,
        "blockers_closed_by_preflight": 0,
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_baidu_cloud_handoff_preflight.py",
        "next_human_action": (
            "If Baidu Cloud sync is still desired, explicitly confirm cloud clear "
            "and upload scope before any destructive or external operation."
        ),
        **boundary_flags(),
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    with MANIFEST_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["path", "exists", "size_bytes", "safe_to_upload", "reason"],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_docs(payload: dict[str, Any]) -> None:
    rows = payload["safe_upload_manifest"]
    table = "\n".join(
        "| {path} | {exists} | {safe_to_upload} | {size_bytes} |".format(**row)
        for row in rows
    )
    summary = f"""# SAEE Baidu Cloud Handoff Preflight v0.1

baidu_cloud_handoff_preflight_v0_1: true
status: {payload["status"]}
cloud_target_id: {payload["cloud_target_id"]}
handoff_scope: {payload["handoff_scope"]}
cloud_clear_required_before_sync: true
destructive_cloud_operation_requires_separate_confirmation: true
cloud_clear_performed: false
cloud_sync_performed: false
cloud_upload_authorized: false
cloud_delete_authorized: false
safe_upload_candidate_count: {payload["safe_upload_candidate_count"]}
candidate_count: {payload["candidate_count"]}
missing_candidate_count: {payload["missing_candidate_count"]}
blockers_closed_by_preflight: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This local preflight records a safe, agent-readable handoff plan for a possible
future Baidu Cloud sync target. It does not clear cloud storage, upload files,
call cloud APIs, open a browser, package runtime code, expose private core, or
claim production readiness.

## Upload Scope

The default upload scope is documentation and readiness evidence only. It
excludes runtime, backend, kernel, API schema, private core, and landing-page
interaction files.

## Candidate Manifest

| Path | Exists | Safe to upload | Size bytes |
| --- | --- | --- | ---: |
{table}

## Boundary

- No cloud clear was performed.
- No cloud sync was performed.
- No cloud upload is authorized by this file.
- No cloud delete is authorized by this file.
- No backend, runtime, kernel, API schema, landing interaction, or private core
  file is included in the safe manifest.
- Production readiness, customer validation, product launch, and blocker
  closure remain false.
"""
    REPORT_MD.write_text(summary, encoding="utf-8")
    TOP_DOC.write_text(summary, encoding="utf-8")

    CLEAR_CHECKLIST_MD.write_text(
        f"""# Baidu Cloud Clear-First Checklist

cloud_target_id: {CLOUD_TARGET_ID}
cloud_clear_required_before_sync: true
cloud_clear_performed: false
cloud_sync_performed: false

## Human-only checklist

- [ ] Confirm that the cloud target is the intended Baidu Cloud destination.
- [ ] Confirm that clearing existing cloud contents is still desired.
- [ ] Confirm that clearing the cloud target will not remove unrelated files.
- [ ] Confirm the upload scope before syncing anything.
- [ ] Keep runtime, backend, kernel, API schema, and private core out of the
      default cloud handoff package.

This checklist does not authorize or perform deletion. A separate explicit
human confirmation is required before any destructive cloud action.
""",
        encoding="utf-8",
    )
    BOUNDARY_AUDIT_MD.write_text(
        """# Baidu Cloud Handoff Boundary Audit

- No cloud clear performed.
- No cloud sync performed.
- No cloud API called.
- No browser automation used.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No landing page interaction modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No production-ready claim added.
- No blocker closed.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Baidu Cloud Handoff Preflight Recommendation Gate

answer: recommend_for_human_review_only

reason: The preflight creates a local docs-and-readiness manifest for possible
Baidu Cloud handoff while requiring separate human confirmation before cloud
clear or upload.

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

next_action: Human must explicitly confirm destructive cloud clear and upload
scope before any Baidu Cloud operation.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = candidate_rows()
    payload = build_payload(rows)
    SUMMARY_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_docs(payload)
    print(
        "SAEE_BAIDU_CLOUD_HANDOFF_PREFLIGHT: PASS "
        f"status={payload['status']} "
        f"safe_upload_candidate_count={payload['safe_upload_candidate_count']} "
        "cloud_clear_performed=false cloud_sync_performed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
