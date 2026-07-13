#!/usr/bin/env python3
"""Smoke check for the SAEE online experience human review record.

The human review record confirms the local static page was manually checked. It
must not imply public deployment, product launch, production readiness, customer
validation, backend calls, runtime execution, or private core exposure.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "phase_b_product/landing/online_experience_human_review.local.json"
REPORT = ROOT / "phase_b_product/landing/online_experience_human_review.md"
GATE = ROOT / "docs/strategy/SAEE_ONLINE_EXPERIENCE_HUMAN_REVIEW_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_ONLINE_EXPERIENCE_HUMAN_REVIEW_SMOKE: FAIL: {message}")


def read_text(path: Path) -> str:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require_tokens(name: str, text: str, tokens: list[str]) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        fail(f"{name} missing tokens: {', '.join(missing)}")


def main() -> None:
    summary = json.loads(read_text(SUMMARY))
    report = read_text(REPORT)
    gate = read_text(GATE)
    llms = read_text(LLMS)
    agent_index = json.loads(read_text(AGENT_INDEX))

    expected = {
        "online_experience_human_review_v0_1": True,
        "status": "human_review_confirmed_no_public_deploy",
        "human_review_confirmed": True,
        "manual_check_passed": True,
        "public_deploy_authorized": False,
        "public_deploy_performed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "user_upload_enabled": False,
        "backend_call_required": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "external_model_api_called": False,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            fail(f"summary {key} must be {value!r}")

    require_tokens(
        "online_experience_human_review.md",
        report,
        [
            "human_review_confirmed_no_public_deploy",
            "人工检查完毕，没有问题，确认",
            "It does not authorize public deployment.",
            "It does not launch the product.",
            "It does not claim production readiness.",
            "It does not claim customer validation.",
            "It does not expose private core.",
        ],
    )
    require_tokens(
        "SAEE_ONLINE_EXPERIENCE_HUMAN_REVIEW_GATE.md",
        gate,
        [
            "answer: human_review_confirmed_no_public_deploy",
            "public_deploy_authorized: false",
            "public_deploy_performed: false",
            "product_launched: false",
            "production_ready: false",
            "customer_validated: false",
            "private_core_exposed: false",
        ],
    )
    require_tokens(
        "llms.txt",
        llms,
        [
            "/phase_b_product/landing/online_experience_human_review.md",
            "/phase_b_product/landing/online_experience_human_review.local.json",
            "/docs/strategy/SAEE_ONLINE_EXPERIENCE_HUMAN_REVIEW_GATE.md",
            "/scripts/saee_online_experience_human_review_smoke.py",
        ],
    )

    entry = agent_index.get("online_experience_human_review_v0_1", {})
    for key, value in expected.items():
        if entry.get(key) != value:
            fail(f"agent-index online_experience_human_review_v0_1 {key} must be {value!r}")

    print(
        "SAEE_ONLINE_EXPERIENCE_HUMAN_REVIEW_SMOKE: PASS "
        "human_review_confirmed_no_public_deploy"
    )


if __name__ == "__main__":
    main()
