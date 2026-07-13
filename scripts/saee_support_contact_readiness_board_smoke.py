#!/usr/bin/env python3
"""Smoke check for the SAEE support-contact readiness board."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOARD_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.local.json"
)
BOARD_MD = (
    ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.md"
)
BOARD_CSV = (
    ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.csv"
)
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_READINESS_BOARD_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_READINESS_BOARD_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_SUPPORT_CONTACT_READINESS_BOARD_SMOKE: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path | str) -> str:
    p = ROOT / path if isinstance(path, str) else path
    return p.read_text(encoding="utf-8")


def main() -> None:
    for path in [BOARD_JSON, BOARD_MD, BOARD_CSV, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path}")

    board = json.loads(read(BOARD_JSON))
    expected = {
        "support_contact_readiness_board_v0_1": True,
        "board_type": "saee_support_contact_readiness_board",
        "board_scope": "local_support_contact_blocker_readiness_review",
        "target_blocker_id": "support_contact",
        "human_review_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_human_closure_approval_required": True,
        "support_contact_blocker_satisfied": False,
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
        "support_contact_raw_value_exposed": False,
        "support_contact_raw_value_recorded": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    for key, expected_value in expected.items():
        require(board.get(key) == expected_value, f"{key} drift")
    require(board.get("blockers_closed_by_board") == 0, "board must close zero blockers")
    require(board.get("readiness_step_count") == 5, "readiness step count must be 5")
    require(isinstance(board.get("steps"), list), "steps must be a list")
    require(len(board["steps"]) == 5, "steps length must be 5")
    require(board.get("status", "").startswith("hold_"), "board status must be hold")

    combined = "\n".join([read(BOARD_MD), read(TOP_DOC), read(GATE)])
    required_tokens = [
        "Status:",
        "support_contact",
        "support_contact_configured: false",
        "support_contact_published: false",
        "support_contact_test_performed: false",
        "support_contact_raw_value_exposed: false",
        "support_contact_raw_value_recorded: false",
        "customer_contacted: false",
        "support_vendor_contacted: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blockers_closed_by_board: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: recommend",
        "recommend_for_local_human_review: true",
        "recommend_for_production: false",
    ]
    missing = [token for token in required_tokens if token not in combined]
    require(not missing, "missing doc tokens: " + ", ".join(missing))

    forbidden = [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "product_launched: true",
        "private_core_exposed: true",
        "support_contact_raw_value_exposed: true",
        "support_contact_raw_value_recorded: true",
        "support_contact_published: true",
    ]
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claims: " + ", ".join(found))

    llms = read("llms.txt")
    required_llms = [
        "/phase_b_product/commercial_readiness/SUPPORT_CONTACT_READINESS_BOARD_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.md",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_READINESS_BOARD_RECOMMENDATION_GATE.md",
        "/scripts/saee_support_contact_readiness_board.py",
        "/scripts/saee_support_contact_readiness_board_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads(read("agent-index.json"))
    entry = index.get("support_contact_readiness_board_v0_1", {})
    expected_index = {
        "status": "hold_human_first_owner_input_required",
        "support_contact_readiness_board_v0_1": True,
        "target_blocker_id": "support_contact",
        "blockers_closed_by_board": 0,
        "support_contact_blocker_satisfied": False,
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
        "support_contact_raw_value_exposed": False,
        "support_contact_raw_value_recorded": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    for key, expected_value in expected_index.items():
        require(entry.get(key) == expected_value, f"agent-index {key} drift")

    print(
        "SAEE_SUPPORT_CONTACT_READINESS_BOARD_SMOKE: PASS "
        f"status={board['status']} "
        "blockers_closed_by_board=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
