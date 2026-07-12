#!/usr/bin/env python3
"""Run the complete local acceptance suite for the Baidu entry plan."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    "scripts/saee_baidu_cloud_marketplace_entry_plan_smoke.py",
    "scripts/saee_qianfan_readiness_mcp_smoke.py",
    "scripts/saee_qianfan_readiness_host_smoke.py",
    "scripts/saee_qianfan_readiness_live_receipt_smoke.py",
    "scripts/saee_baidu_partner_consultation_application_smoke.py",
    "scripts/saee_baidu_publication_package_smoke.py",
    "scripts/saee_cloud_entry_package_smoke.py",
    "scripts/saee_public_baseline_audit.py",
    "scripts/saee_baidu_goal_completion_audit.py",
]


def main() -> None:
    receipts = []
    for command in COMMANDS:
        completed = subprocess.run([sys.executable, command], cwd=ROOT, capture_output=True, text=True)
        if completed.returncode != 0:
            raise SystemExit(f"SAEE_BAIDU_ENTRY_ACCEPTANCE: FAIL command={command} output={completed.stdout}{completed.stderr}")
        receipts.append({"command": command, "result": completed.stdout.strip()})
    gate = json.loads((ROOT / "agent-interface/ecosystem/saee-baidu-external-action-authorization-gate.v1.json").read_text(encoding="utf-8"))
    if gate["authorization"]["approved"] is not True or gate["truth_boundary"]["marketplace_submission"] is not False:
        raise SystemExit("SAEE_BAIDU_ENTRY_ACCEPTANCE: FAIL external authorization boundary")
    report = {
        "acceptance_id": "saee-baidu-entry-local-v1",
        "status": "phases_0_to_3_local_complete_real_qianfan_synthetic_roundtrip_phase_4_company_input_gate",
        "checks": receipts,
        "truth_boundary": {
            "real_qianfan_product_roundtrip": True,
            "qianfan_live_synthetic_scenario_count": 2,
            "github_release_created": False,
            "baidu_partner_contacted": False,
            "marketplace_submission": False,
            "customer_validated": False,
            "production_ready": False,
            "external_action_authorized": True,
            "external_action_authorization_scope_limited": True,
        },
    }
    output = ROOT / "output/SAEE_BAIDU_ENTRY_LOCAL_ACCEPTANCE_V1.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "SAEE_BAIDU_ENTRY_ACCEPTANCE: PASS local_phases_complete=4 checks=9 "
        "real_qianfan_product_roundtrip=true github_release=false "
        "marketplace_submission=false production_ready=false"
    )


if __name__ == "__main__":
    main()
