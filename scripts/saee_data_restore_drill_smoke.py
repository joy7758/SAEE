#!/usr/bin/env python3
"""Smoke check for SAEE data restore drill v0.1."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.data_backup import create_public_shell_backup
from saee_backend.services.data_restore_drill import run_public_shell_restore_drill
from saee_backend.storage.sqlite_store import SQLiteExperimentStore


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_DATA_RESTORE_DRILL_SMOKE: FAIL: {message}")


def main() -> None:
    default_ready = load_settings({}).readiness_payload()
    require(
        default_ready["restore_drill_available"] is True,
        "ready payload must expose restore drill availability",
    )
    require(
        default_ready["restore_drill_default_automatic"] is False,
        "restore drill must not be automatic by default",
    )
    require(
        default_ready["production_restore_policy_available"] is False,
        "ready payload must not claim production restore policy",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        db_path = tmp / "saee.sqlite3"
        audit_path = tmp / "request_audit.jsonl"
        backup_dir = tmp / "backups"
        drill_dir = tmp / "restore_drills"

        SQLiteExperimentStore(db_path)
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT INTO experiments (experiment_id, result_json, created_at, updated_at)
                VALUES ('restore-exp', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            )
        audit_path.write_text(
            json.dumps(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "request_id": "req-restore",
                    "method": "GET",
                    "path": "/ready",
                    "status_code": 200,
                    "duration_ms": 1.0,
                    "body_recorded": False,
                    "credentials_recorded": False,
                    "private_core_recorded": False,
                }
            )
            + "\n",
            encoding="utf-8",
        )

        settings = load_settings(
            {
                "SAEE_STORAGE_BACKEND": "sqlite",
                "SAEE_STORAGE_PATH": str(db_path),
                "SAEE_REQUEST_AUDIT_PATH": str(audit_path),
                "SAEE_BACKUP_DIR": str(backup_dir),
                "SAEE_RESTORE_DRILL_DIR": str(drill_dir),
            }
        )
        backup_manifest = create_public_shell_backup(settings, label="restore-smoke")
        report = run_public_shell_restore_drill(
            Path(backup_manifest["manifest_path"]),
            settings,
            label="restore-smoke",
        )
        report_path = Path(report["report_path"])
        require(report_path.exists(), "restore drill report must exist")
        require(report["restore_drill_type"] == "public_shell_local_restore_drill", "type mismatch")
        require(report["status"] == "pass", "restore drill must pass with readable copied files")
        require(report["copied_file_count"] == 2, "must copy both backup files")
        require(report["readable_file_count"] == 2, "must read both copied files")
        require(report["integrity_checked_file_count"] == 2, "must check backup integrity for both files")
        require(report["integrity_passed_file_count"] == 2, "must pass backup integrity for both files")
        require(report["restore_integrity_checks_passed"] is True, "restore integrity checks must pass")
        for check in report["checks"]:
            require(check["integrity_checked"] is True, "each restore check must include integrity check")
            require(check["integrity_passed"] is True, "each restore check must pass integrity")
            require(len(check["expected_sha256"]) == 64, "expected sha256 must be recorded")
            require(check["expected_sha256"] == check["actual_sha256"], "sha256 must match restored file")
        require(report["restore_to_live_path"] is False, "must not restore into live paths")
        require(report["production_restore_tested"] is False, "must not claim production restore")
        require(
            report["production_restore_policy_available"] is False,
            "must not claim production restore policy",
        )
        require(report["tenant_restore_available"] is False, "must not claim tenant restore")
        require(report["credentials_restored"] is False, "must not restore credentials")
        require(report["private_core_restored"] is False, "must not restore private core")
        require(report["runtime_modified"] is False, "must not modify runtime")
        require(report["kernel_modified"] is False, "must not modify kernel")
        require(report["api_schema_modified"] is False, "must not modify API schema")
        require(report["external_calls_made"] is False, "must not make external calls")
        require(report["production_ready"] is False, "must not claim production readiness")

        tampered_manifest = create_public_shell_backup(settings, label="restore-tamper")
        tampered_audit = Path(tampered_manifest["backup_dir"]) / "request_audit.jsonl"
        tampered_audit.write_text(tampered_audit.read_text(encoding="utf-8") + "{}\n", encoding="utf-8")
        tampered_report = run_public_shell_restore_drill(
            Path(tampered_manifest["manifest_path"]),
            settings,
            label="restore-tamper",
        )
        require(tampered_report["status"] == "hold", "tampered backup must not pass restore drill")
        require(
            tampered_report["restore_integrity_checks_passed"] is False,
            "tampered backup must fail integrity checks",
        )
        require(
            tampered_report["integrity_passed_file_count"] < tampered_report["copied_file_count"],
            "tampered backup must reduce integrity pass count",
        )

        forged_dir = tmp / "forged-source"
        forged_dir.mkdir()
        forged_manifest = dict(backup_manifest)
        forged_manifest.pop("manifest_path", None)
        forged_manifest["backup_dir"] = str(forged_dir)
        forged_path = tmp / "forged-manifest.json"
        forged_path.write_text(json.dumps(forged_manifest), encoding="utf-8")
        try:
            run_public_shell_restore_drill(forged_path, settings, label="forged-outside")
        except ValueError:
            forged_outside_rejected = True
        else:
            forged_outside_rejected = False
        require(forged_outside_rejected, "manifest outside configured backup root must fail")

        mismatched_run = backup_dir / "20990101T000000Z-forged"
        mismatched_run.mkdir()
        mismatched_path = mismatched_run / "BACKUP_MANIFEST.json"
        mismatched_path.write_text(json.dumps(forged_manifest), encoding="utf-8")
        try:
            run_public_shell_restore_drill(mismatched_path, settings, label="forged-mismatch")
        except ValueError:
            mismatched_directory_rejected = True
        else:
            mismatched_directory_rejected = False
        require(mismatched_directory_rejected, "manifest backup_dir mismatch must fail")

    doc = (ROOT / "phase_b_product/commercial_readiness/DATA_RESTORE_DRILL_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_DATA_RESTORE_DRILL_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("data_restore_drill_v0_1: true" in doc, "restore drill doc missing state")
    require(
        "restore_drill_default_automatic: false" in doc,
        "restore drill doc must preserve manual default",
    )
    require(
        "production_restore_policy_available: false" in doc,
        "restore drill doc must not claim production restore policy",
    )
    require(
        "restore_integrity_checks_passed: true" in doc,
        "restore drill doc missing integrity state",
    )
    require("answer: conditional" in gate, "restore drill gate must remain conditional")

    print(
        "SAEE_DATA_RESTORE_DRILL_SMOKE: PASS "
        "local_restore_drill=true "
        "restore_integrity_checks_passed=true "
        "forged_manifest_rejected=true "
        "restore_to_live_path=false "
        "production_restore_policy_available=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
