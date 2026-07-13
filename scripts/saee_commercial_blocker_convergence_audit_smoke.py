#!/usr/bin/env python3
"""Smoke test the commercial blocker convergence audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/commercial_blocker_convergence_audit"
SUMMARY = OUT / "commercial_blocker_convergence_audit.local.json"
REPORT = OUT / "commercial_blocker_convergence_audit.md"
BOUNDARY = OUT / "commercial_blocker_convergence_audit_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_BLOCKER_CONVERGENCE_AUDIT_GATE.md"
RUNNER = ROOT / "scripts/saee_commercial_blocker_convergence_audit.py"


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_BLOCKER_CONVERGENCE_AUDIT_SMOKE: FAIL " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    for path in [SUMMARY, REPORT, BOUNDARY, GATE, RUNNER]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "commercial_blocker_convergence_audit_v0_1": True,
        "audit_type": "local_status_convergence_only",
        "status": "current_action_blocker_converged_to_customer_validated",
        "legacy_original_blocker_count": 24,
        "legacy_priority_blocker_count": 24,
        "legacy_matrix_preserved": True,
        "legacy_matrix_overwritten": False,
        "local_human_evidence_lane_count": 7,
        "local_human_evidence_lanes_passed": True,
        "current_actionable_blocker_count_after_local_human_evidence": 1,
        "current_goal_blocker": "customer_validated",
        "customer_validation_session_entry_exists": False,
        "post_session_processor_status": "hold_human_session_entry_missing",
        "post_session_processor_ready": False,
        "production_ready": False,
        "product_launched": False,
        "customer_validated": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "public_sdk_released": False,
        "blockers_closed_by_convergence_audit": 0,
        "development_permission_granted": False,
        "execution_authorized": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(
        payload.get("current_actionable_blockers_after_local_human_evidence")
        == ["customer_validated"],
        "current blocker list must be customer_validated only",
    )

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, GATE])
    for token in [
        "commercial_blocker_convergence_audit_v0_1: true",
        "Legacy matrix preserved: true",
        "Legacy matrix overwritten: false",
        "customer_validated",
        "production_ready: false",
        "product_launched: false",
        "private_core_exposed: false",
        "blockers_closed_by_convergence_audit: 0",
    ]:
        require(token in combined, f"missing report token: {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/commercial_blocker_convergence_audit/commercial_blocker_convergence_audit.md",
        "/phase_b_product/commercial_readiness/commercial_blocker_convergence_audit/commercial_blocker_convergence_audit.local.json",
        "/phase_b_product/commercial_readiness/commercial_blocker_convergence_audit/commercial_blocker_convergence_audit_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_BLOCKER_CONVERGENCE_AUDIT_GATE.md",
        "/scripts/saee_commercial_blocker_convergence_audit.py",
        "/scripts/saee_commercial_blocker_convergence_audit_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("commercial_blocker_convergence_audit_v0_1")
    require(isinstance(entry, dict), "agent-index missing commercial_blocker_convergence_audit_v0_1")
    for key, value in expected.items():
        if key in entry:
            require(entry.get(key) == value, f"agent-index {key} must be {value}")
    require(entry.get("current_goal_blocker") == "customer_validated", "agent-index current blocker changed")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Commercial Blocker Convergence Audit v0.1",
        "commercial_blocker_convergence_audit_v0_1",
        "Current actionable blocker after local human evidence inspection: `customer_validated`",
        "production_ready=false",
        "customer_validated=false",
        "private_core_exposed=false",
    ]:
        require(token in status_text, f"status surface missing {token}")

    print(
        "SAEE_COMMERCIAL_BLOCKER_CONVERGENCE_AUDIT_SMOKE: PASS "
        "legacy_blockers=24 current_blocker=customer_validated production_ready=false"
    )


if __name__ == "__main__":
    main()
