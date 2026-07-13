#!/usr/bin/env python3
"""Smoke check for SAEE data retention v0.1."""

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
from saee_backend.services.data_retention import evaluate_data_retention
from saee_backend.storage.sqlite_store import SQLiteExperimentStore


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_DATA_RETENTION_SMOKE: FAIL: {message}")


def write_audit(path: Path) -> None:
    old_event = {
        "timestamp": "2000-01-01T00:00:00+00:00",
        "request_id": "req-old",
        "method": "GET",
        "path": "/ready",
        "status_code": 200,
        "duration_ms": 1.0,
        "body_recorded": False,
        "credentials_recorded": False,
        "private_core_recorded": False,
    }
    new_event = dict(old_event)
    new_event["timestamp"] = datetime.now(timezone.utc).isoformat()
    new_event["request_id"] = "req-new"
    path.write_text(json.dumps(old_event) + "\n" + json.dumps(new_event) + "\n", encoding="utf-8")


def count_rows(db_path: Path) -> int:
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]


def main() -> None:
    default_report = evaluate_data_retention(load_settings({}))
    require(default_report["status"] == "hold", "default retention must hold")
    require(default_report["retention_policy_configured"] is False, "default retention must be unconfigured")
    require(default_report["deleted_records"] == 0, "default retention must not delete")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "saee.sqlite3"
        audit_path = Path(tmpdir) / "request_audit.jsonl"
        SQLiteExperimentStore(db_path)
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT INTO experiments (experiment_id, result_json, created_at, updated_at)
                VALUES ('old-exp', NULL, '2000-01-01 00:00:00', '2000-01-01 00:00:00')
                """
            )
            conn.execute(
                """
                INSERT INTO experiments (experiment_id, result_json, created_at, updated_at)
                VALUES ('new-exp', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
            )
        write_audit(audit_path)

        dry_settings = load_settings(
            {
                "SAEE_RETENTION_DAYS": "30",
                "SAEE_STORAGE_PATH": str(db_path),
                "SAEE_REQUEST_AUDIT_PATH": str(audit_path),
            }
        )
        dry_report = evaluate_data_retention(dry_settings)
        require(dry_report["status"] == "pass", "configured retention must pass")
        require(dry_report["apply_effective"] is False, "default retention must be dry run")
        require(dry_report["eligible_records"] == 2, "dry run must find two eligible records")
        require(dry_report["deleted_records"] == 0, "dry run must not delete")
        require(count_rows(db_path) == 2, "dry run must preserve sqlite rows")

        apply_settings = load_settings(
            {
                "SAEE_RETENTION_DAYS": "30",
                "SAEE_RETENTION_DRY_RUN": "false",
                "SAEE_STORAGE_PATH": str(db_path),
                "SAEE_REQUEST_AUDIT_PATH": str(audit_path),
            }
        )
        apply_report = evaluate_data_retention(apply_settings, apply=True)
        require(apply_report["apply_effective"] is True, "apply must be effective only when dry run false")
        require(apply_report["deleted_records"] == 2, "apply must delete two eligible records")
        require(count_rows(db_path) == 1, "apply must keep only one sqlite row")
        remaining_audit = audit_path.read_text(encoding="utf-8")
        require("req-old" not in remaining_audit, "old audit line must be removed")
        require("req-new" in remaining_audit, "new audit line must remain")
        require(apply_report["request_body_inspected"] is False, "retention must not inspect request bodies")
        require(apply_report["credentials_inspected"] is False, "retention must not inspect credentials")
        require(apply_report["private_core_inspected"] is False, "retention must not inspect private core")

        symlink_audit_target = Path(tmpdir) / "symlink-audit-target.jsonl"
        symlink_audit_target.write_text(
            json.dumps({"timestamp": "2000-01-01T00:00:00+00:00"}) + "\n",
            encoding="utf-8",
        )
        symlink_audit = Path(tmpdir) / "symlink-audit.jsonl"
        symlink_audit.symlink_to(symlink_audit_target)
        symlink_settings = load_settings(
            {
                "SAEE_RETENTION_DAYS": "30",
                "SAEE_RETENTION_DRY_RUN": "false",
                "SAEE_STORAGE_PATH": str(Path(tmpdir) / "missing.sqlite3"),
                "SAEE_REQUEST_AUDIT_PATH": str(symlink_audit),
            }
        )
        symlink_report = evaluate_data_retention(symlink_settings, apply=True)
        require(symlink_report["deleted_records"] == 0, "audit symlink must not delete")
        require(
            "2000-01-01" in symlink_audit_target.read_text(encoding="utf-8"),
            "audit symlink target must remain unchanged",
        )

        symlink_db_target = Path(tmpdir) / "symlink-db-target.sqlite3"
        SQLiteExperimentStore(symlink_db_target)
        with sqlite3.connect(symlink_db_target) as conn:
            conn.execute(
                "INSERT INTO experiments (experiment_id, result_json, created_at, updated_at) "
                "VALUES ('symlink-old', NULL, '2000-01-01 00:00:00', '2000-01-01 00:00:00')"
            )
        symlink_db = Path(tmpdir) / "symlink-db.sqlite3"
        symlink_db.symlink_to(symlink_db_target)
        symlink_db_settings = load_settings(
            {
                "SAEE_RETENTION_DAYS": "30",
                "SAEE_RETENTION_DRY_RUN": "false",
                "SAEE_STORAGE_PATH": str(symlink_db),
                "SAEE_REQUEST_AUDIT_PATH": str(Path(tmpdir) / "missing-audit.jsonl"),
            }
        )
        symlink_db_report = evaluate_data_retention(symlink_db_settings, apply=True)
        require(symlink_db_report["deleted_records"] == 0, "SQLite symlink must not delete")
        require(count_rows(symlink_db_target) == 1, "SQLite symlink target must remain unchanged")

        directory_settings = load_settings(
            {
                "SAEE_RETENTION_DAYS": "30",
                "SAEE_RETENTION_DRY_RUN": "false",
                "SAEE_STORAGE_PATH": str(Path(tmpdir) / "missing-db.sqlite3"),
                "SAEE_REQUEST_AUDIT_PATH": str(Path(tmpdir)),
            }
        )
        directory_report = evaluate_data_retention(directory_settings, apply=True)
        require(directory_report["deleted_records"] == 0, "directory path must fail closed")

    doc = (ROOT / "phase_b_product/commercial_readiness/DATA_RETENTION_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_DATA_RETENTION_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("data_retention_v0_1: true" in doc, "retention doc missing state")
    require("retention_default_dry_run: true" in doc, "retention doc must preserve dry-run default")
    require("production_ready: false" in doc, "retention doc must not claim production")
    require("answer: conditional" in gate, "retention gate must remain conditional")

    print(
        "SAEE_DATA_RETENTION_SMOKE: PASS "
        "default_hold=true "
        "dry_run_safe=true "
        "apply_requires_dry_run_false=true "
        "symlink_paths_rejected=true non_regular_paths_rejected=true "
        "request_body_inspected=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
