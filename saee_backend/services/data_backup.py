"""Local public-shell backup helpers for the SAEE MVP API shell.

Backups apply only to public-shell SQLite experiment reports and request audit
JSONL metadata. This module does not inspect request bodies, response bodies,
credentials, runtime internals, kernel logic, or private core materials.
"""

from __future__ import annotations

import json
import shutil
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from saee_backend.config import SETTINGS, SaeeBackendSettings


@dataclass(frozen=True)
class BackupCopyResult:
    source: str
    target: str
    exists: bool
    copied: bool
    size_bytes: int
    sha256: str
    notes: str

    def as_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "target": self.target,
            "exists": self.exists,
            "copied": self.copied,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "notes": self.notes,
        }


def _safe_label(label: str | None) -> str:
    if not label:
        return "manual"
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in label.strip())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:64] or "manual"


def _backup_run_dir(settings: SaeeBackendSettings, label: str | None, now: datetime) -> Path:
    timestamp = now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(settings.backup_dir) / f"{timestamp}-{_safe_label(label)}"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_if_present(source: Path, target: Path, notes: str) -> BackupCopyResult:
    if not source.exists():
        return BackupCopyResult(
            source=str(source),
            target=str(target),
            exists=False,
            copied=False,
            size_bytes=0,
            sha256="",
            notes=f"{notes}; source does not exist",
        )
    if not source.is_file() or source.is_symlink():
        return BackupCopyResult(
            source=str(source),
            target=str(target),
            exists=True,
            copied=False,
            size_bytes=0,
            sha256="",
            notes=f"{notes}; source is not a regular file",
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    size_bytes = target.stat().st_size
    sha256 = _sha256_file(target)
    return BackupCopyResult(
        source=str(source),
        target=str(target),
        exists=True,
        copied=True,
        size_bytes=size_bytes,
        sha256=sha256,
        notes=notes,
    )


def create_public_shell_backup(
    settings: SaeeBackendSettings = SETTINGS,
    *,
    label: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Create a manual local backup for public-shell data only."""

    created_at = now or datetime.now(timezone.utc)
    backup_dir = _backup_run_dir(settings, label, created_at)
    backup_dir.mkdir(parents=True, exist_ok=False)

    copies = [
        _copy_if_present(
            Path(settings.storage_path),
            backup_dir / "saee_mvp.sqlite3",
            "public-shell SQLite experiment reports only",
        ),
        _copy_if_present(
            Path(settings.request_audit_path),
            backup_dir / "request_audit.jsonl",
            "public-shell request audit metadata only",
        ),
    ]

    copied_files = [copy.as_dict() for copy in copies]
    manifest: dict[str, Any] = {
        "backup_type": "public_shell_local_backup",
        "created_at": created_at.astimezone(timezone.utc).isoformat(),
        "backup_dir": str(backup_dir),
        "label": _safe_label(label),
        "storage_backend": settings.storage_backend,
        "source_storage_path": settings.storage_path,
        "source_request_audit_path": settings.request_audit_path,
        "copied_files": copied_files,
        "copied_file_count": sum(1 for copy in copies if copy.copied),
        "backup_integrity_manifest_available": True,
        "backup_file_hash_algorithm": "sha256",
        "default_automatic_backup": False,
        "restore_tested": False,
        "production_backup_policy_available": False,
        "tenant_backup_available": False,
        "request_body_inspected": False,
        "request_body_extracted": False,
        "response_body_inspected": False,
        "response_body_extracted": False,
        "credentials_inspected": False,
        "credentials_copied": False,
        "private_core_inspected": False,
        "private_core_copied": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "next_action": "store backup artifact according to a human-approved local handling policy",
    }
    manifest_path = backup_dir / "BACKUP_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest
