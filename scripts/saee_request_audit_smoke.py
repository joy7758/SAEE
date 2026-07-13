#!/usr/bin/env python3
"""Smoke check for SAEE request audit v0.1."""

from __future__ import annotations

import json
import tempfile
import sys
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.api.audit import build_request_audit_event, write_request_audit_event
from saee_backend.config import load_settings


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_REQUEST_AUDIT_SMOKE: FAIL: {message}")


def main() -> None:
    default = load_settings({})
    require(default.request_audit_enabled is False, "request audit must be disabled by default")
    require(default.readiness_payload()["request_audit_enabled"] is False, "ready payload must report disabled audit")

    event = build_request_audit_event(
        request_id="req-smoke",
        method="GET",
        path="/ready",
        status_code=200,
        duration_ms=12.3456,
        client_host="127.0.0.1",
    )
    require(event["body_recorded"] is False, "audit event must not record body")
    require(event["credentials_recorded"] is False, "audit event must not record credentials")
    require(event["private_core_recorded"] is False, "audit event must not record private core")
    require(event["tenant_boundary_checked"] is False, "default event must not claim tenant check")
    require(event["tenant_id_present"] is False, "default event must not claim tenant ID")
    require(event["tenant_id_hash_recorded"] is False, "default event must not record tenant hash")
    require(event["tenant_id_raw_recorded"] is False, "audit event must not record raw tenant ID")
    serialized = json.dumps(event).lower()
    forbidden = [
        "authorization",
        "cookie",
        "x-saee-api-key",
        "x-saee-tenant-id",
        "request_body",
        "response_body",
        "raw_tenant_id",
        "private_core_exposed",
    ]
    leaked = [token for token in forbidden if token in serialized]
    require(not leaked, "audit event leaked forbidden token: " + ", ".join(leaked))

    tenant_event = build_request_audit_event(
        request_id="req-tenant-smoke",
        method="POST",
        path="/experiment/run",
        status_code=200,
        duration_ms=18.0,
        tenant_audit_metadata={
            "tenant_boundary_checked": True,
            "tenant_id_present": True,
            "tenant_id_hash_recorded": True,
            "tenant_id_raw_recorded": False,
            "tenant_id_hash": sha256("tenant-alpha".encode("utf-8")).hexdigest(),
            "tenant_id_hash_algorithm": "sha256",
        },
    )
    require(tenant_event["tenant_boundary_checked"] is True, "tenant check metadata missing")
    require(tenant_event["tenant_id_present"] is True, "tenant present metadata missing")
    require(tenant_event["tenant_id_hash_recorded"] is True, "tenant hash metadata missing")
    require(tenant_event["tenant_id_raw_recorded"] is False, "raw tenant ID must remain absent")
    require(tenant_event["tenant_id_hash"] != "tenant-alpha", "tenant hash must not equal raw tenant ID")

    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "request_audit.jsonl"
        disabled = load_settings({"SAEE_REQUEST_AUDIT_PATH": str(log_path)})
        wrote = write_request_audit_event(event, disabled)
        require(wrote is False, "disabled audit must not write")
        require(not log_path.exists(), "disabled audit must not create file")

        enabled = load_settings(
            {
                "SAEE_REQUEST_AUDIT_ENABLED": "true",
                "SAEE_REQUEST_AUDIT_PATH": str(log_path),
            }
        )
        require(enabled.request_audit_enabled is True, "request audit must be configurable")
        require(
            enabled.readiness_payload()["request_audit_log_available"] is True,
            "ready payload must report audit availability when enabled",
        )
        wrote = write_request_audit_event(event, enabled)
        require(wrote is True, "enabled audit must write")
        lines = log_path.read_text(encoding="utf-8").splitlines()
        require(len(lines) == 1, "enabled audit must append one JSONL line")
        loaded = json.loads(lines[0])
        require(loaded["request_id"] == "req-smoke", "request_id must survive JSONL write")
        require(loaded["body_recorded"] is False, "JSONL event must preserve body boundary")
        require(loaded["credentials_recorded"] is False, "JSONL event must preserve credential boundary")
        require(loaded["private_core_recorded"] is False, "JSONL event must preserve private core boundary")
        require(loaded["tenant_id_raw_recorded"] is False, "JSONL event must preserve tenant raw boundary")

        wrote = write_request_audit_event(tenant_event, enabled)
        require(wrote is True, "enabled audit must write tenant metadata event")
        loaded_tenant = json.loads(log_path.read_text(encoding="utf-8").splitlines()[-1])
        require(loaded_tenant["tenant_boundary_checked"] is True, "tenant metadata must survive write")
        require(loaded_tenant["tenant_id_hash_recorded"] is True, "tenant hash flag must survive write")
        require("tenant-alpha" not in json.dumps(loaded_tenant), "raw tenant ID leaked into audit")

        bad_event = dict(event)
        bad_event["x-saee-tenant-id"] = "tenant-alpha"
        try:
            write_request_audit_event(bad_event, enabled)
        except ValueError:
            pass
        else:
            raise SystemExit("SAEE_REQUEST_AUDIT_SMOKE: FAIL: raw tenant header must be rejected")

    doc = (ROOT / "phase_b_product/commercial_readiness/REQUEST_AUDIT_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_REQUEST_AUDIT_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("request_audit_v0_1: true" in doc, "request audit doc missing state")
    require("production_monitoring_available: false" in doc, "request audit doc must not claim monitoring")
    require("request_body_recorded: false" in doc, "request audit doc must preserve body boundary")
    require("tenant_audit_metadata_available: true" in doc, "request audit doc missing tenant metadata state")
    require("tenant_id_raw_recorded: false" in doc, "request audit doc must preserve tenant raw boundary")
    require("credentials_recorded: false" in gate, "request audit gate must preserve credential boundary")
    require("tenant_audit_metadata_available: true" in gate, "request audit gate missing tenant metadata")
    require("answer: conditional" in gate, "request audit gate must remain conditional")

    print(
        "SAEE_REQUEST_AUDIT_SMOKE: PASS "
        "default_disabled=true "
        "jsonl_metadata=true "
        "request_body_recorded=false "
        "credentials_recorded=false "
        "tenant_audit_metadata_available=true "
        "tenant_id_raw_recorded=false "
        "production_monitoring_available=false"
    )


if __name__ == "__main__":
    main()
