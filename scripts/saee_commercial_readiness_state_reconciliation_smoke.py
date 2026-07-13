#!/usr/bin/env python3
"""Smoke check for commercial readiness state reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_readiness_state_reconciliation.py"
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_readiness_state_reconciliation"
OUTPUT_JSON = OUTPUT_DIR / "commercial_readiness_state_reconciliation.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_readiness_state_reconciliation.md"
BOUNDARY_AUDIT = OUTPUT_DIR / "commercial_readiness_state_reconciliation_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION_SMOKE: FAIL: " + message)


def read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain an object")
    return data


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require(
        "SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION: PASS" in result.stdout,
        "runner did not print PASS",
    )
    for path in [OUTPUT_JSON, OUTPUT_MD, BOUNDARY_AUDIT, GATE]:
        require(path.exists(), f"{path} missing")

    payload = read_json(OUTPUT_JSON)
    expected = {
        "commercial_readiness_state_reconciliation_v0_1": True,
        "status": "hold_customer_validation_required_after_local_evidence_reconciliation",
        "canonical_gap_audit_open_blocker_count": 24,
        "local_human_evidence_lanes_passed": True,
        "manual_check_completed": True,
        "overlay_remaining_blocker_count": 1,
        "current_goal_blocker": "customer_validated",
        "customer_validation_path_ready": True,
        "customer_validation_workbench_ready": True,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "customer_contacted": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_reconciliation": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(
        payload.get("overlay_remaining_blockers") == ["customer_validated"],
        "remaining blocker list must be customer_validated only",
    )
    require(
        payload.get("canonical_gap_audit_first_priority") == "support_contact",
        "canonical first priority should preserve source gap audit context",
    )

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUTPUT_MD, BOUNDARY_AUDIT, GATE]
    )
    required_tokens = [
        "hold_customer_validation_required_after_local_evidence_reconciliation",
        "manual_check_completed: true",
        "current_goal_blocker: `customer_validated`",
        "production_ready: false",
        "customer_validated: false",
        "blockers_closed_by_reconciliation: 0",
        "No customer validation claimed.",
    ]
    for token in required_tokens:
        require(token in combined, "missing token " + token)
    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "blocker_closure_authorized: true",
        '"blocker_closure_authorized": true',
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden true claim found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/commercial_readiness_state_reconciliation/commercial_readiness_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/commercial_readiness_state_reconciliation/commercial_readiness_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/commercial_readiness_state_reconciliation/commercial_readiness_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_commercial_readiness_state_reconciliation.py",
        "/scripts/saee_commercial_readiness_state_reconciliation_smoke.py",
    ]:
        require(path in llms, "llms.txt missing " + path)

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("commercial_readiness_state_reconciliation_v0_1")
    require(isinstance(entry, dict), "agent-index entry missing")
    for key, value in expected.items():
        if key == "commercial_readiness_state_reconciliation_v0_1":
            continue
        require(entry.get(key) == value, f"agent-index {key} must be {value!r}")
    require(
        entry.get("overlay_remaining_blockers") == ["customer_validated"],
        "agent-index remaining blocker list mismatch",
    )

    print("SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION_SMOKE: PASS")


if __name__ == "__main__":
    main()
