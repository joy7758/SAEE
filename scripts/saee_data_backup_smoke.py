#!/usr/bin/env python3
"""Smoke check for SAEE data backup v0.1."""

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
from saee_backend.storage.sqlite_store import SQLiteExperimentStore


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_DATA_BACKUP_SMOKE: FAIL: {message}")


def main() -> None:
    default_ready = load_settings({}).readiness_payload()
    require(default_ready["data_backup_available"] is True, "ready payload must expose backup availability")
    require(default_ready["backup_default_automatic"] is False, "backup must not be automatic by default")
    require(default_ready["restore_tested"] is False, "restore must remain untested by default")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        db_path = tmp / "saee.sqlite3"
        audit_path = tmp / "request_audit.jsonl"
        backup_dir = tmp / "backups"

        SQLiteExperimentStore(db_path)
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT INTO experiments (experiment_id, result_json, created_at, updated_at)
                VALUES ('backup-exp', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            )
        audit_path.write_text(
            json.dumps(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "request_id": "req-backup",
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
            }
        )
        manifest = create_public_shell_backup(settings, label="smoke")
        manifest_path = Path(manifest["manifest_path"])
        require(manifest_path.exists(), "manifest must exist")
        require(Path(manifest["backup_dir"]).exists(), "backup directory must exist")
        require((Path(manifest["backup_dir"]) / "saee_mvp.sqlite3").exists(), "sqlite copy must exist")
        require((Path(manifest["backup_dir"]) / "request_audit.jsonl").exists(), "audit copy must exist")
        require(manifest["backup_type"] == "public_shell_local_backup", "backup type mismatch")
        require(manifest["copied_file_count"] == 2, "must copy both backup files")
        require(
            manifest["backup_integrity_manifest_available"] is True,
            "backup manifest must include integrity metadata",
        )
        require(manifest["backup_file_hash_algorithm"] == "sha256", "backup hash algorithm must be sha256")
        for copied_file in manifest["copied_files"]:
            require(copied_file["copied"] is True, "each expected smoke file must be copied")
            require(copied_file["size_bytes"] > 0, "copied file size must be recorded")
            require(len(copied_file["sha256"]) == 64, "copied file sha256 must be recorded")
        require(manifest["default_automatic_backup"] is False, "backup must remain manual")
        require(manifest["restore_tested"] is False, "backup smoke must not claim restore testing")
        require(manifest["production_backup_policy_available"] is False, "must not claim production backup")
        require(manifest["tenant_backup_available"] is False, "must not claim tenant backup")
        require(manifest["request_body_inspected"] is False, "must not inspect request bodies")
        require(manifest["credentials_copied"] is False, "must not copy credentials")
        require(manifest["private_core_copied"] is False, "must not copy private core")
        require(manifest["runtime_modified"] is False, "must not modify runtime")
        require(manifest["kernel_modified"] is False, "must not modify kernel")
        require(manifest["api_schema_modified"] is False, "must not modify API schema")
        require(manifest["external_calls_made"] is False, "must not make external calls")
        require(manifest["production_ready"] is False, "must not claim production readiness")

    doc = (ROOT / "phase_b_product/commercial_readiness/DATA_BACKUP_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_DATA_BACKUP_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("data_backup_v0_1: true" in doc, "backup doc missing state")
    require("backup_default_automatic: false" in doc, "backup doc must preserve manual default")
    require("backup_integrity_manifest_available: true" in doc, "backup doc missing integrity state")
    require("restore_tested: false" in doc, "backup doc must not claim restore testing")
    require("production_ready: false" in doc, "backup doc must not claim production")
    require("answer: conditional" in gate, "backup gate must remain conditional")

    print(
        "SAEE_DATA_BACKUP_SMOKE: PASS "
        "manual_backup=true "
        "public_shell_only=true "
        "backup_integrity_manifest=true "
        "restore_tested=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
