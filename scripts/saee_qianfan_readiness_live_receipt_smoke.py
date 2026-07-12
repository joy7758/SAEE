#!/usr/bin/env python3
"""Validate sanitized, bounded receipts from real Qianfan product roundtrips."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = {
    "saee-qianfan-customer-service-live-validation.v0.1.json": {
        "score": 75,
        "readiness": "conditional",
        "missing_evidence": ["HUMAN_APPROVAL"],
    },
    "saee-qianfan-coding-agent-live-validation.v0.1.json": {
        "score": 50,
        "readiness": "replan",
        "missing_evidence": ["ROLLBACK_PLAN", "HUMAN_APPROVAL"],
    },
}
RECEIPT_DIR = ROOT / "agent-interface/qianfan/live-validation"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN = ("QIANFAN_API_KEY", "Authorization:", "Bearer ", "bce-v3/")
EXPECTED_TOOLS = ["saee.evaluate_agent_run", "saee.evaluate_evidence"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    provider_rounds = 0
    for filename, expected in RECEIPTS.items():
        path = RECEIPT_DIR / filename
        raw = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN:
            require(marker not in raw, f"{filename}: forbidden secret marker {marker!r}")
        receipt = json.loads(raw)
        result = receipt["result"]
        boundary = receipt["truth_boundary"]
        provider = receipt["provider_receipt"]

        require(receipt["status"] == "pass", f"{filename}: status")
        require(receipt["provider"] == "baidu_qianfan", f"{filename}: provider")
        require(receipt["model"] == "ernie-4.5-turbo-128k", f"{filename}: model")
        require(receipt["mcp_operation"] == "saee.evaluate_agent_run", f"{filename}: MCP operation")
        require(receipt["public_mcp_tools"] == EXPECTED_TOOLS, f"{filename}: public tools")
        require(result["score"] == expected["score"], f"{filename}: score")
        require(result["readiness"] == expected["readiness"], f"{filename}: readiness")
        require(result["missing_evidence"] == expected["missing_evidence"], f"{filename}: missing evidence")
        require(result["truth_boundary"]["deployment_authorized"] is False, f"{filename}: deployment boundary")
        require(result["truth_boundary"]["production_ready"] is False, f"{filename}: production boundary")
        require(boundary["external_provider_network_used"] is True, f"{filename}: provider network")
        require(boundary["external_world_actions"] == 0, f"{filename}: external actions")
        require(boundary["synthetic_fixture"] is True, f"{filename}: fixture boundary")
        require(boundary["official_qianfan_integration"] is False, f"{filename}: official integration")
        require(boundary["production_ready"] is False, f"{filename}: receipt production boundary")
        require(provider["round_count"] == 2, f"{filename}: provider round count")
        require(provider["host_canonical_summary_fallback"] is True, f"{filename}: canonical fallback")
        require(provider["provider_final_boundary_preserved"] is False, f"{filename}: provider final boundary record")
        require(SHA256.fullmatch(provider["provider_final_answer_sha256"]) is not None, f"{filename}: provider hash")
        require(SHA256.fullmatch(provider["delivered_final_answer_sha256"]) is not None, f"{filename}: delivered hash")
        provider_rounds += provider["round_count"]

    print(
        "SAEE_QIANFAN_LIVE_RECEIPT_SMOKE: PASS "
        f"live_scenarios={len(RECEIPTS)} provider_rounds={provider_rounds} "
        "external_world_actions=0 official_qianfan_integration=false production_ready=false"
    )


if __name__ == "__main__":
    main()
