"""Data retention helpers for the SAEE MVP API shell.

Retention applies only to public-shell SQLite experiment rows and request audit
JSONL metadata. It never inspects private core, runtime internals, request
bodies, response bodies, or credentials.
"""

from __future__ import annotations

import json
import os
import sqlite3
import stat
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from saee_backend.config import SETTINGS, SaeeBackendSettings


@dataclass(frozen=True)
class RetentionTargetResult:
    target: str
    path: str
    exists: bool
    eligible_records: int
    deleted_records: int
    applied: bool
    notes: str

    def as_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "path": self.path,
            "exists": self.exists,
            "eligible_records": self.eligible_records,
            "deleted_records": self.deleted_records,
            "applied": self.applied,
            "notes": self.notes,
        }


def cutoff_timestamp(retention_days: int, now: datetime | None = None) -> datetime:
    base = now or datetime.now(timezone.utc)
    return base - timedelta(days=retention_days)


def sqlite_cutoff_string(cutoff: datetime) -> str:
    return cutoff.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _sqlite_retention(
    db_path: Path,
    cutoff: datetime,
    apply: bool,
) -> RetentionTargetResult:
    if not db_path.exists():
        return RetentionTargetResult(
            target="sqlite_experiments",
            path=str(db_path),
            exists=False,
            eligible_records=0,
            deleted_records=0,
            applied=False,
            notes="sqlite database does not exist",
        )
    try:
        mode = db_path.lstat().st_mode
    except OSError:
        mode = 0
    if db_path.is_symlink() or not stat.S_ISREG(mode):
        return RetentionTargetResult(
            target="sqlite_experiments",
            path=str(db_path),
            exists=True,
            eligible_records=0,
            deleted_records=0,
            applied=False,
            notes="sqlite database must be a regular non-symlink file",
        )
    cutoff_value = sqlite_cutoff_string(cutoff)
    flags = (os.O_RDWR if apply else os.O_RDONLY) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(db_path, flags)
    except OSError:
        return RetentionTargetResult(
            target="sqlite_experiments",
            path=str(db_path),
            exists=True,
            eligible_records=0,
            deleted_records=0,
            applied=False,
            notes="sqlite database could not be opened without following links",
        )
    conn: sqlite3.Connection | None = None
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise ValueError("sqlite retention target is not a regular file")
        conn = sqlite3.connect(db_path)
        current_stat = db_path.lstat()
        if (
            db_path.is_symlink()
            or current_stat.st_dev != opened_stat.st_dev
            or current_stat.st_ino != opened_stat.st_ino
        ):
            return RetentionTargetResult(
                target="sqlite_experiments",
                path=str(db_path),
                exists=True,
                eligible_records=0,
                deleted_records=0,
                applied=False,
                notes="sqlite database path changed during boundary validation",
            )
        with conn:
            table = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'experiments'"
            ).fetchone()
            if table is None:
                return RetentionTargetResult(
                    target="sqlite_experiments",
                    path=str(db_path),
                    exists=True,
                    eligible_records=0,
                    deleted_records=0,
                    applied=False,
                    notes="experiments table does not exist",
                )
            eligible = conn.execute(
                "SELECT COUNT(*) FROM experiments WHERE updated_at < ?",
                (cutoff_value,),
            ).fetchone()[0]
            deleted = 0
            if apply and eligible:
                cursor = conn.execute(
                    "DELETE FROM experiments WHERE updated_at < ?",
                    (cutoff_value,),
                )
                deleted = cursor.rowcount if cursor.rowcount is not None else 0
    finally:
        if conn is not None:
            conn.close()
        os.close(descriptor)
    return RetentionTargetResult(
        target="sqlite_experiments",
        path=str(db_path),
        exists=True,
        eligible_records=int(eligible),
        deleted_records=int(deleted),
        applied=apply,
        notes="public-shell experiment rows only",
    )


def _parse_audit_timestamp(line: str) -> datetime | None:
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return None
    raw = event.get("timestamp")
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _audit_retention(
    audit_path: Path,
    cutoff: datetime,
    apply: bool,
) -> RetentionTargetResult:
    if not audit_path.exists():
        return RetentionTargetResult(
            target="request_audit_jsonl",
            path=str(audit_path),
            exists=False,
            eligible_records=0,
            deleted_records=0,
            applied=False,
            notes="request audit file does not exist",
        )
    try:
        mode = audit_path.lstat().st_mode
    except OSError:
        mode = 0
    if audit_path.is_symlink() or not stat.S_ISREG(mode):
        return RetentionTargetResult(
            target="request_audit_jsonl",
            path=str(audit_path),
            exists=True,
            eligible_records=0,
            deleted_records=0,
            applied=False,
            notes="request audit path must be a regular non-symlink file",
        )
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(audit_path, flags)
    with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    kept: list[str] = []
    eligible = 0
    for line in lines:
        timestamp = _parse_audit_timestamp(line)
        if timestamp is not None and timestamp.astimezone(timezone.utc) < cutoff:
            eligible += 1
            continue
        kept.append(line)
    deleted = 0
    if apply and eligible:
        descriptor, temporary = tempfile.mkstemp(
            prefix=audit_path.name + ".retention.",
            dir=audit_path.parent,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write("\n".join(kept) + ("\n" if kept else ""))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, audit_path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        deleted = eligible
    return RetentionTargetResult(
        target="request_audit_jsonl",
        path=str(audit_path),
        exists=True,
        eligible_records=eligible,
        deleted_records=deleted,
        applied=apply,
        notes="public-shell request metadata only",
    )


def evaluate_data_retention(
    settings: SaeeBackendSettings = SETTINGS,
    *,
    apply: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    retention_configured = settings.retention_days > 0
    effective_apply = apply and retention_configured and not settings.retention_dry_run
    targets: list[RetentionTargetResult] = []
    if retention_configured:
        cutoff = cutoff_timestamp(settings.retention_days, now)
        targets.append(_sqlite_retention(Path(settings.storage_path), cutoff, effective_apply))
        targets.append(_audit_retention(Path(settings.request_audit_path), cutoff, effective_apply))
        cutoff_value = cutoff.isoformat()
    else:
        cutoff_value = None

    eligible_total = sum(target.eligible_records for target in targets)
    deleted_total = sum(target.deleted_records for target in targets)
    return {
        "retention_type": "public_shell_data_retention",
        "retention_policy_configured": retention_configured,
        "retention_days": settings.retention_days,
        "dry_run": settings.retention_dry_run or not apply,
        "apply_requested": apply,
        "apply_effective": effective_apply,
        "cutoff_timestamp": cutoff_value,
        "targets": [target.as_dict() for target in targets],
        "eligible_records": eligible_total,
        "deleted_records": deleted_total,
        "request_body_inspected": False,
        "credentials_inspected": False,
        "private_core_inspected": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "production_ready": False,
        "status": "pass" if retention_configured else "hold",
        "next_action": (
            "set SAEE_RETENTION_DAYS before controlled preview"
            if not retention_configured
            else "review dry-run counts before setting SAEE_RETENTION_DRY_RUN=false and passing --apply"
        ),
    }
