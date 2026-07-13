"""Local restore drill helpers for SAEE public-shell backups.

The drill restores copied backup files into an isolated drill directory and
checks that public-shell SQLite and request audit JSONL files are readable. It
never restores over live paths, never calls external services, and never
inspects private core materials.
"""

from __future__ import annotations

import json
import os
import shutil
import hashlib
import sqlite3
import stat
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from saee_backend.config import SETTINGS, SaeeBackendSettings


@dataclass(frozen=True)
class RestoreCheckResult:
    target: str
    source: str
    restored_path: str
    exists: bool
    copied: bool
    readable: bool
    integrity_checked: bool
    integrity_passed: bool
    expected_size_bytes: int
    actual_size_bytes: int
    expected_sha256: str
    actual_sha256: str
    record_count: int
    notes: str

    def as_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "source": self.source,
            "restored_path": self.restored_path,
            "exists": self.exists,
            "copied": self.copied,
            "readable": self.readable,
            "integrity_checked": self.integrity_checked,
            "integrity_passed": self.integrity_passed,
            "expected_size_bytes": self.expected_size_bytes,
            "actual_size_bytes": self.actual_size_bytes,
            "expected_sha256": self.expected_sha256,
            "actual_sha256": self.actual_sha256,
            "record_count": self.record_count,
            "notes": self.notes,
        }


def _safe_label(label: str | None) -> str:
    if not label:
        return "manual"
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in label.strip())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:64] or "manual"


def _drill_run_dir(settings: SaeeBackendSettings, label: str | None, now: datetime) -> Path:
    timestamp = now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(settings.restore_drill_dir) / f"{timestamp}-{_safe_label(label)}"


def _path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _load_manifest(path: Path, settings: SaeeBackendSettings) -> dict[str, Any]:
    if not path.exists() or not path.is_file() or path.is_symlink():
        raise ValueError("backup manifest must be a regular non-symlink file")
    backup_root = Path(settings.backup_dir)
    if backup_root.is_symlink():
        raise ValueError("configured backup root must not be a symlink")
    resolved_root = backup_root.resolve()
    resolved_manifest = path.resolve()
    if not _path_within(resolved_manifest, resolved_root):
        raise ValueError("backup manifest must be inside the configured backup root")
    if resolved_manifest.parent == resolved_root:
        raise ValueError("backup manifest must be inside a dedicated backup run directory")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("backup_type") != "public_shell_local_backup":
        raise ValueError("backup manifest is not a public_shell_local_backup")
    declared_backup_dir = Path(str(manifest.get("backup_dir", ""))).resolve()
    if declared_backup_dir != resolved_manifest.parent:
        raise ValueError("backup manifest directory does not match its file location")
    allowed_targets = {
        (declared_backup_dir / "saee_mvp.sqlite3").resolve(),
        (declared_backup_dir / "request_audit.jsonl").resolve(),
    }
    copied_files = manifest.get("copied_files")
    if not isinstance(copied_files, list):
        raise ValueError("backup manifest copied_files must be a list")
    seen_targets: set[Path] = set()
    for copied in copied_files:
        if not isinstance(copied, dict):
            raise ValueError("backup manifest copied file entry must be an object")
        target = Path(str(copied.get("target", ""))).resolve()
        if target not in allowed_targets:
            raise ValueError("backup manifest target is outside the closed backup file set")
        if target in seen_targets:
            raise ValueError("backup manifest target entries must be unique")
        seen_targets.add(target)
        if copied.get("copied") is True:
            size = copied.get("size_bytes")
            digest = copied.get("sha256")
            if type(size) is not int or size < 0:
                raise ValueError("copied backup manifest size is invalid")
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise ValueError("copied backup manifest hash is invalid")
    return manifest


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_integrity_by_target(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for copied in manifest.get("copied_files", []):
        if not isinstance(copied, dict) or not copied.get("copied"):
            continue
        target_name = Path(str(copied.get("target", ""))).name
        if target_name == "saee_mvp.sqlite3":
            result["sqlite_experiments"] = copied
        elif target_name == "request_audit.jsonl":
            result["request_audit_jsonl"] = copied
    return result


def _integrity_check(target: Path, expected: dict[str, Any] | None) -> tuple[bool, bool, int, int, str, str]:
    if not expected:
        return False, False, 0, target.stat().st_size if target.exists() else 0, "", ""
    expected_size = int(expected.get("size_bytes") or 0)
    expected_sha256 = str(expected.get("sha256") or "")
    actual_size = target.stat().st_size if target.exists() else 0
    actual_sha256 = _sha256_file(target) if target.exists() and target.is_file() else ""
    checked = expected_size >= 0 and bool(expected_sha256)
    passed = checked and actual_size == expected_size and actual_sha256 == expected_sha256
    return checked, passed, expected_size, actual_size, expected_sha256, actual_sha256


def validate_restore_drill_report(report_path: str | Path) -> dict[str, Any]:
    """Validate a prior isolated public-shell restore drill report.

    This is evidence validation for controlled-preview preflight only. It does
    not run a restore drill, restore live paths, inspect private core, or claim
    production restore testing.
    """

    path = Path(report_path)
    result: dict[str, Any] = {
        "restore_drill_report_path": str(path),
        "restore_drill_report_configured": bool(str(report_path).strip()),
        "restore_drill_report_exists": path.exists(),
        "controlled_preview_restore_drill_passed": False,
        "production_restore_tested": False,
        "production_restore_policy_available": False,
        "restore_to_live_path": False,
        "private_core_restored": False,
        "credentials_restored": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "notes": "",
    }
    if not result["restore_drill_report_configured"]:
        result["notes"] = "restore drill report path not configured"
        return result
    if not path.exists() or not path.is_file() or path.is_symlink():
        result["notes"] = "restore drill report path missing, not a regular file, or symlink"
        return result
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["notes"] = f"restore drill report unreadable: {exc}"
        return result

    expected_false_flags = [
        "restore_to_live_path",
        "production_restore_tested",
        "production_restore_policy_available",
        "credentials_restored",
        "private_core_restored",
        "runtime_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "production_ready",
        "customer_validated",
        "product_launched",
    ]
    false_flags_safe = all(report.get(flag) is False for flag in expected_false_flags)
    passed = (
        report.get("restore_drill_type") == "public_shell_local_restore_drill"
        and report.get("status") == "pass"
        and int(report.get("copied_file_count", 0)) > 0
        and int(report.get("readable_file_count", 0)) == int(report.get("copied_file_count", -1))
        and int(report.get("integrity_passed_file_count", 0))
        == int(report.get("copied_file_count", -1))
        and report.get("restore_integrity_checks_passed") is True
        and false_flags_safe
    )
    result.update(
        {
            "controlled_preview_restore_drill_passed": passed,
            "production_restore_tested": False,
            "production_restore_policy_available": False,
            "restore_to_live_path": False,
            "private_core_restored": False,
            "credentials_restored": False,
            "runtime_modified": False,
            "kernel_modified": False,
            "api_schema_modified": False,
            "external_calls_made": False,
            "notes": "restore drill report valid for controlled-preview evidence"
            if passed
            else "restore drill report did not satisfy controlled-preview evidence checks",
        }
    )
    return result


def _copy_regular_file(source: Path, target: Path) -> bool:
    if not source.exists() or source.is_symlink():
        return False
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(source, flags)
    except OSError:
        return False
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            return False
        target.parent.mkdir(parents=True, exist_ok=True)
        with os.fdopen(descriptor, "rb", closefd=False) as source_handle:
            with target.open("xb") as target_handle:
                shutil.copyfileobj(source_handle, target_handle)
        return True
    finally:
        os.close(descriptor)


def _sqlite_check(source: Path, target: Path, expected_integrity: dict[str, Any] | None) -> RestoreCheckResult:
    copied = _copy_regular_file(source, target)
    if not copied:
        return RestoreCheckResult(
            target="sqlite_experiments",
            source=str(source),
            restored_path=str(target),
            exists=source.exists(),
            copied=False,
            readable=False,
            integrity_checked=False,
            integrity_passed=False,
            expected_size_bytes=0,
            actual_size_bytes=0,
            expected_sha256="",
            actual_sha256="",
            record_count=0,
            notes="sqlite backup file missing or not a regular file",
        )
    (
        integrity_checked,
        integrity_passed,
        expected_size_bytes,
        actual_size_bytes,
        expected_sha256,
        actual_sha256,
    ) = _integrity_check(target, expected_integrity)
    try:
        with sqlite3.connect(target) as conn:
            table = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'experiments'"
            ).fetchone()
            count = 0
            if table is not None:
                count = int(conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0])
    except sqlite3.Error as exc:
        return RestoreCheckResult(
            target="sqlite_experiments",
            source=str(source),
            restored_path=str(target),
            exists=True,
            copied=True,
            readable=False,
            integrity_checked=integrity_checked,
            integrity_passed=integrity_passed,
            expected_size_bytes=expected_size_bytes,
            actual_size_bytes=actual_size_bytes,
            expected_sha256=expected_sha256,
            actual_sha256=actual_sha256,
            record_count=0,
            notes=f"sqlite readability failed: {exc}",
        )
    return RestoreCheckResult(
        target="sqlite_experiments",
        source=str(source),
        restored_path=str(target),
        exists=True,
        copied=True,
        readable=True,
        integrity_checked=integrity_checked,
        integrity_passed=integrity_passed,
        expected_size_bytes=expected_size_bytes,
        actual_size_bytes=actual_size_bytes,
        expected_sha256=expected_sha256,
        actual_sha256=actual_sha256,
        record_count=count,
        notes="public-shell SQLite backup readable and integrity-checked in isolated drill directory"
        if integrity_passed
        else "public-shell SQLite backup readable but integrity check missing or failed",
    )


def _audit_check(source: Path, target: Path, expected_integrity: dict[str, Any] | None) -> RestoreCheckResult:
    copied = _copy_regular_file(source, target)
    if not copied:
        return RestoreCheckResult(
            target="request_audit_jsonl",
            source=str(source),
            restored_path=str(target),
            exists=source.exists(),
            copied=False,
            readable=False,
            integrity_checked=False,
            integrity_passed=False,
            expected_size_bytes=0,
            actual_size_bytes=0,
            expected_sha256="",
            actual_sha256="",
            record_count=0,
            notes="request audit backup file missing or not a regular file",
        )
    (
        integrity_checked,
        integrity_passed,
        expected_size_bytes,
        actual_size_bytes,
        expected_sha256,
        actual_sha256,
    ) = _integrity_check(target, expected_integrity)
    lines = target.read_text(encoding="utf-8").splitlines()
    parsed = 0
    for line in lines:
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            return RestoreCheckResult(
                target="request_audit_jsonl",
                source=str(source),
                restored_path=str(target),
                exists=True,
                copied=True,
                readable=False,
                integrity_checked=integrity_checked,
                integrity_passed=integrity_passed,
                expected_size_bytes=expected_size_bytes,
                actual_size_bytes=actual_size_bytes,
                expected_sha256=expected_sha256,
                actual_sha256=actual_sha256,
                record_count=parsed,
                notes=f"request audit JSONL readability failed: {exc}",
            )
        parsed += 1
    return RestoreCheckResult(
        target="request_audit_jsonl",
        source=str(source),
        restored_path=str(target),
        exists=True,
        copied=True,
        readable=True,
        integrity_checked=integrity_checked,
        integrity_passed=integrity_passed,
        expected_size_bytes=expected_size_bytes,
        actual_size_bytes=actual_size_bytes,
        expected_sha256=expected_sha256,
        actual_sha256=actual_sha256,
        record_count=parsed,
        notes="public-shell request audit backup readable and integrity-checked in isolated drill directory"
        if integrity_passed
        else "public-shell request audit backup readable but integrity check missing or failed",
    )


def _source_by_target(manifest_path: Path) -> dict[str, Path]:
    backup_dir = manifest_path.resolve().parent
    return {
        "sqlite_experiments": backup_dir / "saee_mvp.sqlite3",
        "request_audit_jsonl": backup_dir / "request_audit.jsonl",
    }


def run_public_shell_restore_drill(
    manifest_path: Path,
    settings: SaeeBackendSettings = SETTINGS,
    *,
    label: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Restore public-shell backup files into an isolated drill directory."""

    created_at = now or datetime.now(timezone.utc)
    manifest = _load_manifest(manifest_path, settings)
    drill_dir = _drill_run_dir(settings, label, created_at)
    drill_dir.mkdir(parents=True, exist_ok=False)

    sources = _source_by_target(manifest_path)
    integrity_by_target = _manifest_integrity_by_target(manifest)
    checks = [
        _sqlite_check(
            sources["sqlite_experiments"],
            drill_dir / "restored_saee_mvp.sqlite3",
            integrity_by_target.get("sqlite_experiments"),
        ),
        _audit_check(
            sources["request_audit_jsonl"],
            drill_dir / "restored_request_audit.jsonl",
            integrity_by_target.get("request_audit_jsonl"),
        ),
    ]
    copied_count = sum(1 for check in checks if check.copied)
    readable_count = sum(1 for check in checks if check.readable)
    integrity_checked_count = sum(1 for check in checks if check.integrity_checked)
    integrity_passed_count = sum(1 for check in checks if check.integrity_passed)
    missing_count = sum(1 for check in checks if not check.exists)
    status = (
        "pass"
        if copied_count > 0
        and copied_count == readable_count
        and copied_count == integrity_checked_count
        and copied_count == integrity_passed_count
        else "hold"
    )

    report: dict[str, Any] = {
        "restore_drill_type": "public_shell_local_restore_drill",
        "created_at": created_at.astimezone(timezone.utc).isoformat(),
        "source_manifest_path": str(manifest_path),
        "source_manifest_bound_to_configured_backup_root": True,
        "source_manifest_directory_bound": True,
        "source_backup_dir": str(manifest["backup_dir"]),
        "restore_drill_dir": str(drill_dir),
        "label": _safe_label(label),
        "checks": [check.as_dict() for check in checks],
        "copied_file_count": copied_count,
        "readable_file_count": readable_count,
        "integrity_checked_file_count": integrity_checked_count,
        "integrity_passed_file_count": integrity_passed_count,
        "restore_integrity_checks_passed": copied_count > 0 and copied_count == integrity_passed_count,
        "missing_file_count": missing_count,
        "local_restore_drill_completed": True,
        "restore_to_live_path": False,
        "production_restore_tested": False,
        "production_restore_policy_available": False,
        "tenant_restore_available": False,
        "request_body_inspected": False,
        "response_body_inspected": False,
        "credentials_inspected": False,
        "credentials_restored": False,
        "private_core_inspected": False,
        "private_core_restored": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "status": status,
        "next_action": "use as local restore-readiness evidence only; production restore policy remains separate",
    }
    report_path = drill_dir / "RESTORE_DRILL_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path)
    return report
