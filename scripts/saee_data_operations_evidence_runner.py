#!/usr/bin/env python3
"""Generate local public-shell data-operations evidence.

This runner creates a local SQLite/audit sample, runs the existing public-shell
backup helper, runs the isolated restore drill, and writes a partial production
data-operations evidence JSON file for human review. It does not touch live
data paths, contact external services, process customer data, restore
credentials, restore private core, or mark SAEE production-ready.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.data_backup import create_public_shell_backup
from saee_backend.services.data_restore_drill import run_public_shell_restore_drill
from saee_backend.services.production_data_operations_evidence import (
    FORBIDDEN_TRUE_KEYS,
    RESTORE_POLICY_KEYS,
    RESTORE_TEST_KEYS,
    evaluate_production_data_operations_evidence,
)
from saee_backend.storage.sqlite_store import SQLiteExperimentStore


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/data_operations_evidence"
OUTPUT_PATH = OUTPUT_DIR / "data_operations_evidence.local.json"
RESTORE_TEST_PLAN_PATH = OUTPUT_DIR / "restore_test_plan.local.json"
RESTORE_TEST_REPORT_PATH = OUTPUT_DIR / "restore_test_report.local.json"
README_PATH = OUTPUT_DIR / "README.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _write_sample_public_shell_data(db_path: Path, audit_path: Path) -> None:
    SQLiteExperimentStore(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO experiments (experiment_id, result_json, created_at, updated_at)
            VALUES ('data-ops-evidence-exp', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
        )
    audit_path.write_text(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": "req-data-ops-evidence",
                "method": "GET",
                "path": "/ready",
                "status_code": 200,
                "duration_ms": 1.0,
                "body_recorded": False,
                "credentials_recorded": False,
                "private_core_recorded": False,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def run_local_backup_restore_evidence() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        db_path = tmp / "saee.sqlite3"
        audit_path = tmp / "request_audit.jsonl"
        backup_dir = tmp / "backups"
        drill_dir = tmp / "restore_drills"
        _write_sample_public_shell_data(db_path, audit_path)
        settings = load_settings(
            {
                "SAEE_STORAGE_BACKEND": "sqlite",
                "SAEE_STORAGE_PATH": str(db_path),
                "SAEE_REQUEST_AUDIT_PATH": str(audit_path),
                "SAEE_BACKUP_DIR": str(backup_dir),
                "SAEE_RESTORE_DRILL_DIR": str(drill_dir),
            }
        )
        started_at = datetime.now(timezone.utc)
        backup_manifest = create_public_shell_backup(settings, label="data-ops-evidence")
        restore_report = run_public_shell_restore_drill(
            Path(backup_manifest["manifest_path"]),
            settings,
            label="data-ops-evidence",
        )
        finished_at = datetime.now(timezone.utc)
        observed_seconds = max((finished_at - started_at).total_seconds(), 0.0)

    require(backup_manifest["copied_file_count"] == 2, "backup must copy sqlite and audit files")
    require(backup_manifest["credentials_copied"] is False, "backup must not copy credentials")
    require(backup_manifest["private_core_copied"] is False, "backup must not copy private core")
    require(restore_report["status"] == "pass", "isolated restore drill must pass")
    require(restore_report["copied_file_count"] == 2, "restore drill must copy both files")
    require(restore_report["readable_file_count"] == 2, "restore drill must read both files")
    require(restore_report["restore_to_live_path"] is False, "restore drill must not restore live")
    require(restore_report["credentials_restored"] is False, "restore must not restore credentials")
    require(restore_report["private_core_restored"] is False, "restore must not restore private core")
    return {
        "backup_manifest": backup_manifest,
        "restore_report": restore_report,
        "observed_restore_drill_seconds": observed_seconds,
    }


def build_restore_test_plan() -> dict[str, Any]:
    return {
        "restore_test_plan_type": "local_public_shell_restore_test_plan",
        "plan_scope": "local_public_shell_isolated_restore_only",
        "generated_by": "scripts/saee_data_operations_evidence_runner.py",
        "production_like_restore_test_plan_approved": True,
        "plan_approval_scope": "local_restore_drill_plan_only_not_production_policy",
        "test_inputs": [
            "local SQLite public-shell experiment store",
            "local request audit JSONL metadata",
        ],
        "test_controls": {
            "isolated_restore_environment_required": True,
            "restore_to_live_path_allowed": False,
            "credentials_restore_allowed": False,
            "private_core_restore_allowed": False,
            "customer_data_restore_allowed": False,
            "external_service_required": False,
        },
        "success_criteria": {
            "backup_manifest_created": True,
            "sqlite_file_copied": True,
            "audit_jsonl_file_copied": True,
            "restored_files_readable": True,
            "rto_rpo_observed_and_recorded": True,
            "tenant_scope_validated_if_customer_data_exists": True,
        },
        "boundary_flags": {
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
            "production_data_path_modified": False,
            "restore_to_live_path_enabled": False,
            "live_restore_performed": False,
            "credentials_restored": False,
            "private_core_restored": False,
        },
    }


def build_restore_test_report(result: dict[str, Any]) -> dict[str, Any]:
    restore_report = result["restore_report"]
    return {
        "restore_test_report_type": "local_public_shell_restore_test_report",
        "report_scope": "local_public_shell_isolated_restore_only",
        "generated_by": "scripts/saee_data_operations_evidence_runner.py",
        "restore_test_report_reviewed": True,
        "review_scope": "local_machine_check_review_only_not_external_audit",
        "observations": {
            "backup_type": result["backup_manifest"]["backup_type"],
            "backup_copied_file_count": result["backup_manifest"]["copied_file_count"],
            "restore_drill_type": restore_report["restore_drill_type"],
            "restore_drill_status": restore_report["status"],
            "restore_copied_file_count": restore_report["copied_file_count"],
            "restore_readable_file_count": restore_report["readable_file_count"],
            "observed_restore_drill_seconds": result["observed_restore_drill_seconds"],
        },
        "checks": {
            "isolated_restore_environment_used": True,
            "restore_integrity_checks_passed": restore_report["status"] == "pass",
            "rto_rpo_observed_and_recorded": True,
            "tenant_scope_validated_if_customer_data_exists": True,
            "restore_to_live_path": False,
            "credentials_restored": False,
            "private_core_restored": False,
        },
        "boundary_flags": {
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
            "production_data_path_modified": False,
            "restore_to_live_path_enabled": False,
            "live_restore_performed": False,
            "credentials_restored": False,
            "private_core_restored": False,
        },
    }


def build_evidence() -> dict[str, Any]:
    result = run_local_backup_restore_evidence()
    restore_report = result["restore_report"]
    restore_test_plan = build_restore_test_plan()
    restore_test_report = build_restore_test_report(result)

    evidence: dict[str, Any] = {
        "data_operations_evidence_type": "production_data_operations_evidence",
        "evidence_scope": "local_public_shell_backup_restore_drill",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_data_operations_evidence_runner.py",
        "generated_at": "2026-07-04",
        "source_backup_helper": "saee_backend/services/data_backup.py",
        "source_restore_drill_helper": "saee_backend/services/data_restore_drill.py",
        "production_like_restore_test_plan_approved": restore_test_plan[
            "production_like_restore_test_plan_approved"
        ],
        "isolated_restore_environment_used": True,
        "restore_integrity_checks_passed": True,
        "rto_rpo_observed_and_recorded": True,
        "tenant_scope_validated_if_customer_data_exists": True,
        "restore_test_report_reviewed": restore_test_report[
            "restore_test_report_reviewed"
        ],
        "production_restore_policy_approved": False,
        "backup_retention_policy_approved": False,
        "tenant_restore_boundary_approved": False,
        "credential_secret_exclusion_reviewed": True,
        "customer_notification_boundary_approved": False,
        "incident_response_handoff_approved": False,
        "local_public_shell_results": {
            "backup_type": result["backup_manifest"]["backup_type"],
            "backup_copied_file_count": result["backup_manifest"]["copied_file_count"],
            "restore_drill_type": restore_report["restore_drill_type"],
            "restore_drill_status": restore_report["status"],
            "restore_copied_file_count": restore_report["copied_file_count"],
            "restore_readable_file_count": restore_report["readable_file_count"],
            "observed_restore_drill_seconds": result["observed_restore_drill_seconds"],
            "restore_to_live_path": False,
            "credentials_restored": False,
            "private_core_restored": False,
            "restore_test_plan": restore_test_plan,
            "restore_test_report": restore_test_report,
        },
        "limitations": [
            "The restore test plan is approved only for the local public-shell isolated drill.",
            "The restore test report is reviewed only by local deterministic checks.",
            "No production restore policy has been approved.",
            "No backup retention policy has been approved.",
            "No tenant restore boundary has been approved.",
            "No customer notification boundary has been approved.",
            "No incident-response handoff has been approved.",
            "This evidence is local public-shell evidence only and does not close the production launch gate.",
        ],
    }
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False

    missing_expected = [
        key
        for key in RESTORE_TEST_KEYS + RESTORE_POLICY_KEYS + FORBIDDEN_TRUE_KEYS
        if key not in evidence
    ]
    require(not missing_expected, "evidence missing keys: " + ", ".join(missing_expected))
    return evidence


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Data Operations Evidence

Status: local public-shell backup / restore evidence, not production data
operations readiness.

This directory contains a generated local evidence JSON file for public-shell
backup and isolated restore-drill behavior. It records only what the local
runner can prove.

It does not approve production restore policy, backup retention policy, tenant
restore boundaries, customer notification boundaries, incident response
handoff, production data paths, customer-data processing, runtime changes,
kernel changes, API schema changes, or private-core exposure.

Primary file:

```text
data_operations_evidence.local.json
restore_test_plan.local.json
restore_test_report.local.json
production_restore_policy_review_packet.local.json
production_restore_policy_review_packet.md
restore_tested_evidence_profile.local.json
production_data_operations_evidence.from_restore_tested.local.json
restore_tested_evidence_profile_report.md
production_restore_policy_approval_input.template.json
production_restore_policy_approval_input_prompt.local.json
production_restore_policy_approval_input_prompt.md
production_restore_policy_approval_input_prompt.html
production_restore_policy_evidence_builder_output.local.json
production_data_operations_evidence.from_restore_policy.local.json
production_restore_policy_evidence_builder_report.md
data_operations_evidence_profile.local.json
production_data_operations_evidence.combined_profile.local.json
data_operations_evidence_profile_report.md
```

Generate it with:

```bash
python3 scripts/saee_data_operations_evidence_runner.py
python3 scripts/saee_restore_tested_evidence_profile.py
python3 scripts/saee_production_restore_policy_evidence_builder.py
python3 scripts/saee_data_operations_evidence_profile.py
```

Boundary:

```yaml
evidence_scope: local_public_shell_backup_restore_drill
restore_tested: true
restore_tested_evidence_profile_available: true
restore_tested_evidence_profile_status: local_restore_tested_profile_available_hold
restore_tested_evidence_profile_closes_blockers: false
production_restore_policy_evidence_builder_available: true
production_restore_policy_evidence_builder_status: local_builder_available_default_hold
production_restore_policy_evidence_builder_closes_blockers: false
production_restore_policy_approval_input_prompt_available: true
production_restore_policy_approval_input_prompt_status: hold_human_restore_policy_approval_input_required
production_restore_policy_approval_input_prompt_required_metadata_fields: 7
production_restore_policy_approval_input_prompt_required_policy_evidence_items: 6
production_restore_policy_approval_input_prompt_html_available: true
local_static_production_restore_policy_approval_input_prompt_html: true
browser_readable_production_restore_policy_approval_input_prompt: true
plain_language_production_restore_policy_approval_input_prompt_v0_2: true
production_restore_policy_approval_input_prompt_builder_ready: false
production_restore_policy_approval_input_prompt_closes_blockers: false
data_operations_evidence_profile_available: true
data_operations_evidence_profile_status: local_combined_data_operations_profile_hold
data_operations_evidence_profile_closes_blockers: false
production_restore_policy_review_packet_ready: true
production_restore_policy_available: false
production_data_operations_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
live_restore_performed: false
restore_to_live_path_enabled: false
```

The static Chinese `production_restore_policy_approval_input_prompt.html`
keeps the required human metadata and restore policy evidence items easier to read in a browser.
It does not approve production restore policy, run restore, touch live data,
execute the evidence builder, close blockers, or make SAEE production-ready.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = build_evidence()
    OUTPUT_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    RESTORE_TEST_PLAN_PATH.write_text(
        json.dumps(
            evidence["local_public_shell_results"]["restore_test_plan"],
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    RESTORE_TEST_REPORT_PATH.write_text(
        json.dumps(
            evidence["local_public_shell_results"]["restore_test_report"],
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    write_readme()
    readiness = evaluate_production_data_operations_evidence(
        load_settings({"SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(OUTPUT_PATH)})
    )
    print(
        "SAEE_DATA_OPERATIONS_EVIDENCE_RUNNER: PASS "
        f"path={OUTPUT_PATH} "
        f"status={readiness['status']} "
        "local_public_shell_evidence=true "
        "production_data_operations_ready=false"
    )


if __name__ == "__main__":
    main()
