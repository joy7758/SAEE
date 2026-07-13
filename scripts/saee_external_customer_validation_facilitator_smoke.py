#!/usr/bin/env python3
"""Smoke test for the external customer validation facilitator."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator"
SUMMARY = BASE / "external_customer_validation_facilitator.local.json"
AGENT_INDEX = ROOT / "agent-index.json"


REQUIRED = [
    SUMMARY,
    BASE / "README.md",
    BASE / "external_customer_validation_facilitator.md",
    BASE / "external_customer_validation_facilitator.html",
    BASE / "BOUNDARY_AUDIT.md",
    ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_FACILITATOR_GATE.md",
]


EXPECTED_FALSE = [
    "human_session_performed",
    "human_result_entered",
    "codex_may_contact_customer",
    "codex_may_run_external_session",
    "codex_may_infer_customer_feedback",
    "customer_contacted_by_codex",
    "customer_validated",
    "production_ready",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "external_model_api_called",
    "backend_call_required",
    "runtime_execution_required",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    for path in REQUIRED:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if data.get("external_customer_validation_facilitator_v0_1") is not True:
        fail("facilitator flag missing")
    if data.get("status") != "local_static_facilitator_ready_human_session_required":
        fail("unexpected facilitator status")
    if data.get("current_goal_blocker") != "customer_validated":
        fail("current_goal_blocker must be customer_validated")
    if data.get("human_session_required") is not True:
        fail("human_session_required must be true")
    if data.get("blockers_closed_by_facilitator") != 0:
        fail("blockers_closed_by_facilitator must be 0")
    for key in EXPECTED_FALSE:
        if data.get(key) is not False:
            fail(f"{key} must be false")

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    entry = index.get("external_customer_validation_facilitator_v0_1")
    if not entry:
        fail("agent-index missing external_customer_validation_facilitator_v0_1")
    for key in EXPECTED_FALSE:
        if entry.get(key) is not False:
            fail(f"agent-index {key} must be false")

    html = (BASE / "external_customer_validation_facilitator.html").read_text(encoding="utf-8")
    for required_text in [
        "SAEE 外部客户验证主持页",
        "打开筛选清单",
        "打开邀请草稿",
        "打开同意脚本",
        "打开访谈脚本",
        "打开反馈表",
        "打开录入工作台",
    ]:
        if required_text not in html:
            fail(f"facilitator html missing text: {required_text}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for item in [
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/README.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.md",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.html",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/external_customer_validation_facilitator.local.json",
        "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_facilitator/BOUNDARY_AUDIT.md",
    ]:
        if item not in llms:
            fail(f"llms.txt missing {item}")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED if path.suffix in {".md", ".html"})
    for needle in [
        "customer_validated=true",
        "production_ready=true",
        "product_launched=true",
        "private_core_exposed=true",
        "Codex may contact",
        "Codex runs the external session",
    ]:
        if needle in combined:
            fail(f"forbidden claim found: {needle}")

    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_FACILITATOR_SMOKE: PASS")


if __name__ == "__main__":
    main()
