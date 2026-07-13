#!/usr/bin/env python3
"""Smoke check for the SAEE combined operations evidence profile."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_operations_evidence_profile import (
    DEFAULT_COMBINED_EVIDENCE,
    DEFAULT_EXTERNAL_ALERT_DELIVERY_EVIDENCE,
    DEFAULT_ON_CALL_EVIDENCE,
    DEFAULT_PRODUCTION_MONITORING_EVIDENCE,
    DEFAULT_PROFILE_JSON,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_profile,
)
from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_operations_evidence import (
    EXTERNAL_ALERT_DELIVERY_KEYS,
    FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS,
    PRODUCTION_MONITORING_KEYS,
)


PROFILE_SCRIPT = ROOT / "scripts/saee_operations_evidence_profile.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_OPERATIONS_EVIDENCE_PROFILE_SMOKE: FAIL: " + message)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_evidence(keys: tuple[str, ...], *, unsafe: bool = False) -> dict[str, object]:
    evidence = {
        "operations_evidence_type": "production_operations_evidence",
        "evidence_scope": "fixture_only_operations_source_for_profile_smoke",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_operations_evidence_profile_smoke.py",
        "source_boundary_violation_count": 0,
    }
    for key in (
        *PRODUCTION_MONITORING_KEYS,
        *EXTERNAL_ALERT_DELIVERY_KEYS,
        *ON_CALL_KEYS,
    ):
        evidence[key] = key in keys
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    evidence["external_model_api_called"] = False
    evidence["external_ai_assistant_tested"] = False
    evidence["codex_contacted_customer"] = False
    evidence["codex_contacted_vendor"] = False
    evidence["codex_inferred_missing_evidence"] = False
    if unsafe:
        evidence["production_ready"] = True
    return evidence


def go_no_go(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(path)})
    )


def main() -> None:
    require(PROFILE_SCRIPT.exists(), "profile script missing")
    for path in [
        DEFAULT_PRODUCTION_MONITORING_EVIDENCE,
        DEFAULT_EXTERNAL_ALERT_DELIVERY_EVIDENCE,
        DEFAULT_ON_CALL_EVIDENCE,
    ]:
        require(path.exists(), f"default source evidence missing: {path}")

    default_run = subprocess.run(
        [sys.executable, str(PROFILE_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_profile = json.loads(default_run.stdout)
    require(default_profile["profile_status"] == "hold", "default profile status hold")
    require(
        default_profile["production_monitoring_available_for_go_no_go"] is False,
        "default production monitoring unavailable",
    )
    require(
        default_profile["external_alert_delivery_available_for_go_no_go"] is False,
        "default external alert delivery unavailable",
    )
    require(
        default_profile["on_call_rotation_available_for_go_no_go"] is False,
        "default on-call unavailable",
    )
    require(
        default_profile["production_operations_ready"] is False,
        "default operations not ready",
    )
    require(default_profile["profile_satisfied_production_checks"] == 0, "default none satisfied")
    require(default_profile["profile_production_blocker_count"] == 24, "default 24 blockers")
    require(default_profile["operations_satisfied_blockers"] == [], "default satisfied list empty")
    require(default_profile["blockers_closed_by_profile"] == 0, "default closes no blockers")
    require(DEFAULT_PROFILE_JSON.exists(), "default profile JSON missing")
    require(DEFAULT_COMBINED_EVIDENCE.exists(), "default combined evidence missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        monitoring_path = tmp / "complete_monitoring_evidence.json"
        alert_path = tmp / "complete_alert_evidence.json"
        on_call_path = tmp / "complete_on_call_evidence.json"
        complete_profile_path = tmp / "complete_operations_profile.json"
        complete_combined_path = tmp / "complete_combined_operations_evidence.json"
        unsafe_monitoring_path = tmp / "unsafe_monitoring_evidence.json"
        unsafe_profile_path = tmp / "unsafe_operations_profile.json"
        unsafe_combined_path = tmp / "unsafe_combined_operations_evidence.json"

        write_json(monitoring_path, source_evidence(PRODUCTION_MONITORING_KEYS))
        write_json(alert_path, source_evidence(EXTERNAL_ALERT_DELIVERY_KEYS))
        write_json(on_call_path, source_evidence(ON_CALL_KEYS))
        write_json(unsafe_monitoring_path, source_evidence(PRODUCTION_MONITORING_KEYS, unsafe=True))

        complete_profile = build_profile(
            monitoring_path,
            alert_path,
            on_call_path,
            complete_profile_path,
            complete_combined_path,
        )
        unsafe_profile = build_profile(
            unsafe_monitoring_path,
            alert_path,
            on_call_path,
            unsafe_profile_path,
            unsafe_combined_path,
        )
        complete_go_no_go = go_no_go(complete_combined_path)

    require(complete_profile["profile_status"] == "pass", "complete fixture profile pass")
    require(
        complete_profile["production_monitoring_available_for_go_no_go"] is True,
        "complete profile production monitoring",
    )
    require(
        complete_profile["external_alert_delivery_available_for_go_no_go"] is True,
        "complete profile external alert delivery",
    )
    require(
        complete_profile["on_call_rotation_available_for_go_no_go"] is True,
        "complete profile on-call rotation",
    )
    require(
        complete_profile["production_operations_ready"] is True,
        "complete profile operations ready",
    )
    require(
        complete_profile["operations_satisfied_blockers"]
        == ["production_monitoring", "external_alert_delivery", "on_call_rotation"],
        "complete operations blockers satisfied",
    )
    require(
        complete_go_no_go["satisfied_production_checks"] == 3,
        "complete profile satisfies three go/no-go checks",
    )
    require(
        complete_go_no_go["production_blocker_count"] == 21,
        "complete profile leaves 21 blockers",
    )
    require(complete_go_no_go["commercial_status"] == "hold", "commercial remains hold")
    require(complete_go_no_go["production_ready"] is False, "production ready false")
    require(
        complete_profile["blockers_closed_by_profile"] == 0,
        "complete profile closes no blockers by itself",
    )
    require(unsafe_profile["profile_status"] == "stop", "unsafe profile stops")
    require(
        unsafe_profile["source_boundary_violation_count"] > 0,
        "unsafe profile records source violation",
    )
    require(
        unsafe_profile["production_operations_ready"] is False,
        "unsafe operations not ready",
    )

    subprocess.run(
        [sys.executable, str(PROFILE_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "operations_evidence_profile_v0_1: true",
        "profile_scope: combined_production_monitoring_external_alert_delivery_on_call_to_go_no_go",
        "default_profile_status: hold",
        "production_monitoring_available_for_go_no_go: false",
        "external_alert_delivery_available_for_go_no_go: false",
        "on_call_rotation_available_for_go_no_go: false",
        "production_operations_ready: false",
        "profile_production_blocker_count: 24",
        "blockers_closed_by_profile: 0",
        "answer: conditional",
        "recommend_for_human_go_no_go_review: true",
        "recommend_for_blocker_closure_by_profile_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_monitoring_deployment: false",
        "recommend_for_external_alert_enablement: false",
        "recommend_for_on_call_activation: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/OPERATIONS_EVIDENCE_PROFILE_V0_1.md",
        "/phase_b_product/commercial_readiness/operations_evidence/operations_evidence_profile.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/production_operations_evidence.combined_profile.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/operations_evidence_profile_report.md",
        "/docs/strategy/SAEE_OPERATIONS_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md",
        "/scripts/saee_operations_evidence_profile.py",
        "/scripts/saee_operations_evidence_profile_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("operations_evidence_profile_v0_1", {})
    expected = {
        "status": "local_combined_operations_profile_hold",
        "profile_scope": "combined_production_monitoring_external_alert_delivery_on_call_to_go_no_go",
        "production_monitoring_available_for_go_no_go": False,
        "external_alert_delivery_available_for_go_no_go": False,
        "on_call_rotation_available_for_go_no_go": False,
        "production_operations_ready": False,
        "profile_satisfied_production_checks": 0,
        "profile_production_blocker_count": 24,
        "blockers_closed_by_profile": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "alert_provider_contacted": False,
        "monitoring_vendor_contacted": False,
        "production_monitoring_deployed": False,
        "external_alert_delivery_enabled": False,
    }
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_OPERATIONS_EVIDENCE_PROFILE_SMOKE: PASS "
        "default_monitoring=false default_alert=false default_on_call=false "
        "default_blockers=24 complete_fixture_operations_ready=true "
        "complete_blockers=21 blockers_closed_by_profile=0"
    )


if __name__ == "__main__":
    main()
