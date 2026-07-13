#!/usr/bin/env python3
"""Smoke test the exact human batch-builder approval intake."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_evidence_builder_batch_approval_intake.py"
OUT = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request"
INTAKE = OUT / "batch_approval_intake.local.json"
EXACT_PHRASE = (
    "批准本地批量证据 builder 执行：仅运行 production_monitoring、"
    "production_restore_policy、formal_security_review、pricing_page 四个 builder，"
    "不关闭 blocker，不联系任何人，不发布，不声明生产可用。"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_APPROVAL_INTAKE_SMOKE: FAIL " + message)


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(RUNNER), *args], cwd=ROOT, text=True, capture_output=True, check=True)


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain object")
    return data


def main() -> None:
    default = run()
    require("waiting_for_exact_human_batch_builder_execution_approval_phrase" in default.stdout, "default must wait")
    data = read_json(INTAKE)
    require(data.get("human_approval_record_written") is False, "default must not write approval")
    require(data.get("builder_execution_authorized") is False, "default must not authorize execution")
    require(data.get("builders_executed") == 0, "default must execute zero builders")

    with tempfile.TemporaryDirectory() as tmp:
        approved = Path(tmp) / "approved.local.json"
        result = run(
            "--phrase", EXACT_PHRASE,
            "--reviewer", "smoke-human",
            "--approval-reference", "smoke-batch-approval",
            "--write-human-approved",
            "--human-approved-output", str(approved),
        )
        require("exact_human_batch_builder_execution_approval_recorded_no_execution" in result.stdout, "exact phrase must record approval")
        require(approved.is_file(), "approval record missing")
        record = read_json(approved)
        require(record.get("batch_builder_execution_approved") is True, "approval must be true")
        require(record.get("builder_execution_authorized") is True, "execution approval must be recorded")
        require(record.get("builders_executed") == 0, "approval intake must execute zero builders")
        require(record.get("blockers_closed") == 0, "approval intake must close zero blockers")

        rejected = Path(tmp) / "rejected.local.json"
        result = run(
            "--phrase", "批准执行",
            "--reviewer", "smoke-human",
            "--approval-reference", "smoke-rejected",
            "--write-human-approved",
            "--human-approved-output", str(rejected),
        )
        require("waiting_for_exact_human_batch_builder_execution_approval_phrase" in result.stdout, "generic phrase must be rejected")
        require(not rejected.exists(), "generic phrase must not write record")

    # Restore canonical waiting state after fixture checks.
    run()
    data = read_json(INTAKE)
    require(data.get("status") == "waiting_for_exact_human_batch_builder_execution_approval_phrase", "canonical intake must end waiting")
    require(data.get("builders_executed") == 0, "canonical intake must execute zero builders")

    for name in ["batch_approval.template.json", "batch_approval_copy_card.md", "batch_approval_copy_card.html", "batch_approval_boundary_audit.md"]:
        require((OUT / name).is_file(), f"missing {name}")
    index = read_json(ROOT / "agent-index.json").get("commercial_evidence_builder_batch_approval_intake_v0_1", {})
    require(index.get("human_approval_record_written") is False, "agent-index must end waiting")
    require(index.get("builders_executed") == 0, "agent-index must execute zero builders")

    runner_text = RUNNER.read_text(encoding="utf-8")
    for forbidden in ["subprocess", "os.system", "requests.", "urllib.", "httpx."]:
        require(forbidden not in runner_text, f"intake contains forbidden execution path {forbidden}")
    print(
        "SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_APPROVAL_INTAKE_SMOKE: PASS "
        "status=waiting_for_exact_human_batch_builder_execution_approval_phrase "
        "builders_executed=0 blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
