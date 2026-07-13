#!/usr/bin/env python3
"""Smoke test the bounded commercial evidence-builder batch request."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_evidence_builder_batch_request.py"
OUT = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request"
SUMMARY = OUT / "batch_request.local.json"
EXACT_PHRASE = (
    "批准本地批量证据 builder 执行：仅运行 production_monitoring、"
    "production_restore_policy、formal_security_review、pricing_page 四个 builder，"
    "不关闭 blocker，不联系任何人，不发布，不声明生产可用。"
)


def fail(message: str) -> None:
    raise SystemExit("SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_REQUEST_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain object")
    return data


def main() -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER)], cwd=ROOT, text=True, capture_output=True, check=True
    )
    require("SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_REQUEST: PASS" in completed.stdout, "runner did not pass")
    for path in [SUMMARY, OUT / "README.md", OUT / "batch_request.md", OUT / "batch_request.html", OUT / "BOUNDARY_AUDIT.md"]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    data = read_json(SUMMARY)
    require(data.get("status") == "ready_for_exact_human_batch_builder_execution_approval", "unexpected status")
    require(data.get("target_count") == 4, "target_count must be 4")
    require(data.get("ready_target_count") == 4, "ready_target_count must be 4")
    require(data.get("target_blocker_ids") == ["production_monitoring", "production_restore_policy", "formal_security_review", "pricing_page"], "target order mismatch")
    require(data.get("exact_human_approval_phrase") == EXACT_PHRASE, "exact phrase mismatch")
    require(data.get("human_approval_recorded") is False, "approval must remain false")
    require(data.get("batch_execution_authorized") is False, "execution must remain unauthorized")
    require(data.get("builders_executed_by_request") == 0, "request must execute zero builders")
    require(data.get("blockers_closed_by_request") == 0, "request must close zero blockers")
    for item in data.get("targets", []):
        require(item.get("validator_passed") is True, "validator must pass")
        require(item.get("builder_ready") is True, "builder must be ready")
        require(item.get("builder_still_hold") is True, "builder output must remain hold")
        require(item.get("execution_authorized") is False, "target execution must remain false")

    index = read_json(ROOT / "agent-index.json").get("commercial_evidence_builder_batch_request_v0_1", {})
    require(index.get("target_count") == 4, "agent-index target_count mismatch")
    require(index.get("human_approval_recorded") is False, "agent-index approval must remain false")

    combined = "\n".join((OUT / name).read_text(encoding="utf-8") for name in ["README.md", "batch_request.md", "batch_request.html", "BOUNDARY_AUDIT.md"])
    for token in [EXACT_PHRASE, "batch_execution_authorized: false", "builders_executed_by_request: 0", "production_ready: false"]:
        require(token in combined, f"missing token {token}")
    runner_text = RUNNER.read_text(encoding="utf-8")
    for forbidden in ["subprocess", "os.system", "requests.", "urllib.", "httpx."]:
        require(forbidden not in runner_text, f"runner contains forbidden execution path {forbidden}")

    print(
        "SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_REQUEST_SMOKE: PASS "
        "targets=4 human_approval_recorded=false builders_executed=0 blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
