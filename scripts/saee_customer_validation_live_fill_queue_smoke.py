#!/usr/bin/env python3
"""Smoke test the customer-validation live fill queue."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_customer_validation_live_fill_queue.py"
EVIDENCE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE / "customer_validation_live_fill_queue"
SUMMARY = OUT / "customer_validation_live_fill_queue.local.json"
REPORT = OUT / "customer_validation_live_fill_queue.md"
COPY_BLOCK = OUT / "customer_validation_live_fill_queue_copy_block.md"
BOUNDARY = OUT / "customer_validation_live_fill_queue_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_CUSTOMER_VALIDATION_LIVE_FILL_QUEUE_GATE.md"
ANSWER_INPUT = EVIDENCE / "customer_validation_answer_intake_helper/customer_validation_answers.human_filled.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_CUSTOMER_VALIDATION_LIVE_FILL_QUEUE_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must be a JSON object")
    return data


def main() -> None:
    answer_snapshot = ANSWER_INPUT.read_text(encoding="utf-8") if ANSWER_INPUT.exists() else None
    try:
        if ANSWER_INPUT.exists():
            ANSWER_INPUT.unlink()
        result = subprocess.run(
            [sys.executable, str(RUNNER)],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        require("SAEE_CUSTOMER_VALIDATION_LIVE_FILL_QUEUE: PASS" in result.stdout, "runner did not print PASS")
        for path in [SUMMARY, REPORT, COPY_BLOCK, BOUNDARY, GATE]:
            require(path.is_file(), f"missing {path.relative_to(ROOT)}")

        payload = read_json(SUMMARY)
        expected = {
            "customer_validation_live_fill_queue_v0_1": True,
            "status": "ready_for_real_customer_live_fill",
            "current_goal_blocker": "customer_validated",
            "answer_input_exists": False,
            "preflight_status": "hold_human_answer_sheet_missing",
            "customer_validated": False,
            "production_ready": False,
            "product_launched": False,
            "customer_contacted_by_codex": False,
            "private_core_exposed": False,
            "runtime_modified": False,
            "backend_modified": False,
            "kernel_modified": False,
            "api_schema_modified": False,
            "external_calls_made": False,
            "external_model_api_called": False,
            "blockers_closed_by_queue": 0,
        }
        for key, value in expected.items():
            require(payload.get(key) == value, f"{key} must be {value}")
        require(payload.get("queue_item_count", 0) > 0, "queue must include missing fields")
        require(payload.get("customer_answer_required_count", 0) > 0, "queue must include customer-answer fields")
        require(isinstance(payload.get("queue"), list), "queue must be a list")
        require(all(item.get("codex_may_prefill") is False for item in payload["queue"]), "Codex may not prefill queue items")

        combined = REPORT.read_text(encoding="utf-8") + "\n" + BOUNDARY.read_text(encoding="utf-8") + "\n" + GATE.read_text(encoding="utf-8")
        for token in [
            "customer_validation_live_fill_queue_v0_1: true",
            "customer_validated: false",
            "production_ready: false",
            "private_core_exposed: false",
            "answer: ready_for_real_customer_live_fill_no_validation_claim",
        ]:
            require(token in combined, f"docs missing token: {token}")

        copy_block = COPY_BLOCK.read_text(encoding="utf-8")
        for token in ["participant_role:", "current_evaluation_method:", "no_private_core_disclosed:"]:
            require(token in copy_block, f"copy block missing {token}")

        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        for token in [
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue.md",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue.local.json",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue_copy_block.md",
            "/phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_live_fill_queue/customer_validation_live_fill_queue_boundary_audit.md",
            "/docs/strategy/SAEE_CUSTOMER_VALIDATION_LIVE_FILL_QUEUE_GATE.md",
            "/scripts/saee_customer_validation_live_fill_queue.py",
            "/scripts/saee_customer_validation_live_fill_queue_smoke.py",
        ]:
            require(token in llms, f"llms.txt missing {token}")

        entry = read_json(ROOT / "agent-index.json").get("customer_validation_live_fill_queue_v0_1")
        require(isinstance(entry, dict), "agent-index missing live fill queue entry")
        for key in [
            "status",
            "current_goal_blocker",
            "answer_input_exists",
            "preflight_status",
            "queue_item_count",
            "customer_answer_required_count",
            "customer_validated",
            "production_ready",
            "product_launched",
            "customer_contacted_by_codex",
            "private_core_exposed",
            "runtime_modified",
            "backend_modified",
            "kernel_modified",
            "api_schema_modified",
            "external_calls_made",
            "blockers_closed_by_queue",
        ]:
            require(entry.get(key) == payload.get(key), f"agent-index {key} mismatch")

        status_text = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
        )
        for token in [
            "Customer Validation Live Fill Queue v0.1",
            "customer_validation_live_fill_queue_v0_1",
            "Current blocker: `customer_validated`",
            "customer_validated=false",
            "production_ready=false",
            "private_core_exposed=false",
        ]:
            require(token in status_text, f"status surfaces missing {token}")
    finally:
        if answer_snapshot is None:
            if ANSWER_INPUT.exists():
                ANSWER_INPUT.unlink()
        else:
            ANSWER_INPUT.parent.mkdir(parents=True, exist_ok=True)
            ANSWER_INPUT.write_text(answer_snapshot, encoding="utf-8")

    print("SAEE_CUSTOMER_VALIDATION_LIVE_FILL_QUEUE_SMOKE: PASS customer_validated=false")


if __name__ == "__main__":
    main()
