#!/usr/bin/env python3
"""Verify the redacted live Qianfan host evidence package."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "agent_recommendation/agent_first_validation/run_005"
RECEIPT = ROOT / "agent-interface/examples/observed-trace-receipt.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_QIANFAN_MCP_HOST_EVIDENCE_SMOKE: FAIL " + message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    result = load(EVIDENCE / "validation_result.redacted.json")
    runs = load(EVIDENCE / "roundtrip_runs.local.json")
    crosswalk = load(EVIDENCE / "tool_schema_crosswalk.json")
    receipt = load(EVIDENCE / "receipt.json")
    canonical_receipt = load(RECEIPT)
    run_manifest = load(EVIDENCE / "roundtrip_evidence_manifest.json")
    negative = load(EVIDENCE / "negative_cases.local.json")
    require(result["status"] == "pass", "live result")
    require(result["provider"] == "baidu_qianfan", "provider")
    require(result["model"] == "ernie-4.5-turbo-128k", "model")
    require(result["provider_roundtrip_completed"] is True, "roundtrip")
    require(result["qianfan_tool_call_received"] is True, "provider tool call")
    require(result["mcp_tool_called"] is True, "MCP call")
    require(result["receipt_schema_valid"] is True, "receipt schema")
    require(result["request_hash_verified"] is True, "request hash")
    require(result["content_hash_verified"] is True, "content hash")
    require(result["secrets_redacted"] is True, "redaction")
    require(runs["roundtrip_runs"] == 3 and runs["successful_runs"] == 3, "3/3 runs")
    require(len(run_manifest["runs"]) == 3 and all(item["status"] == "pass" for item in run_manifest["runs"]), "per-run evidence")
    require(all(len(item[key]) == 64 for item in run_manifest["runs"] for key in ("final_answer_sha256", "receipt_sha256", "provider_transcript_sha256", "mcp_transcript_sha256")), "per-run hashes")
    require(runs["final_answer_sha256"] == [item["final_answer_sha256"] for item in run_manifest["runs"]], "aggregate hash crosswalk")
    canonical_bytes = (RECEIPT).read_bytes()
    for item in run_manifest["runs"]:
        directory = EVIDENCE / "roundtrips" / item["run_id"]
        per_result = load(directory / "validation_result.redacted.json")
        require(per_result["final_answer_sha256"] == item["final_answer_sha256"], f"final hash {item['run_id']}")
        require(hashlib.sha256((directory / "receipt.json").read_bytes()).hexdigest() == item["receipt_sha256"], f"receipt hash {item['run_id']}")
        require(hashlib.sha256((directory / "provider_transcript.redacted.jsonl").read_bytes()).hexdigest() == item["provider_transcript_sha256"], f"provider hash {item['run_id']}")
        require(hashlib.sha256((directory / "mcp_transcript.jsonl").read_bytes()).hexdigest() == item["mcp_transcript_sha256"], f"MCP hash {item['run_id']}")
        require((directory / "receipt.json").read_bytes() == canonical_bytes, f"receipt exact {item['run_id']}")
    require(negative["passed"] == negative["total"] == 13 and len(negative["cases"]) == 13, "case-level negatives")
    require(runs["winner"] == "candidate-alpha" and runs["winner_score"] == 0.719476, "winner")
    require(crosswalk["mcp_tool_names"] == ["describe_saee", "compare_observed_traces"], "MCP allowlist")
    require(crosswalk["qianfan_tool_names"] == ["describe_saee", "compare_observed_traces"], "Qianfan allowlist")
    require(receipt == canonical_receipt, "receipt exact match")
    for path in EVIDENCE.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            require("bce-v3/ALTAK-" not in text, f"secret pattern in {path.name}")
            require("Authorization: Bearer" not in text, f"authorization in {path.name}")
    provider_lines = [json.loads(line) for line in (EVIDENCE / "provider_transcript.redacted.jsonl").read_text(encoding="utf-8").splitlines()]
    mcp_lines = [json.loads(line) for line in (EVIDENCE / "mcp_transcript.jsonl").read_text(encoding="utf-8").splitlines()]
    provider_names = [call["name"] for row in provider_lines for call in row.get("tool_calls", [])]
    mcp_methods = [row["request"].get("method") for row in mcp_lines if row.get("request")]
    require(provider_names == ["describe_saee", "compare_observed_traces"], "provider call transcript")
    require("initialize" in mcp_methods and "tools/list" in mcp_methods and mcp_methods.count("tools/call") == 2, "MCP transcript")
    require(not re.search(r"run_agent|read_file|execute_command|private_core", " ".join(provider_names)), "forbidden tool transcript")
    print("SAEE_QIANFAN_MCP_HOST_EVIDENCE_SMOKE: PASS provider_roundtrips=3/3 tools=2 receipt_exact=true secret_leakage=0 negatives=13/13")


if __name__ == "__main__":
    main()
