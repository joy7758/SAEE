#!/usr/bin/env python3
"""Smoke check for the SAEE local MVP tryout guide."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "phase_b_product/validation/LOCAL_MVP_TRYOUT_GUIDE_V0_1.md"
STATUS = ROOT / "phase_b_product/validation/local_mvp_tryout_status.json"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_MVP_TRYOUT_GUIDE_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit(message)


def require_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        fail(f"{key} must be false")


def main() -> None:
    for path in [DOC, STATUS, GATE]:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    data = json.loads(STATUS.read_text(encoding="utf-8"))
    if data.get("status") != "local_tryout_guide_available":
        fail("local MVP tryout guide status must be local_tryout_guide_available")
    if data.get("demo_url") != "http://127.0.0.1:8765/":
        fail("demo_url must point to the local static page")
    if data.get("api_endpoint") != "http://127.0.0.1:8000/experiment/run":
        fail("api_endpoint must point to the local experiment endpoint")
    if data.get("blockers_closed_by_guide") != 0:
        fail("local tryout guide must close zero blockers")

    for key in [
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "customer_data_allowed",
        "product_launched",
        "public_sdk_released",
        "external_calls_made",
        "external_ai_assistant_tested",
        "external_validation_claim",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
    ]:
        require_false(data, key)

    doc = DOC.read_text(encoding="utf-8")
    required_tokens = [
        "Run Demo Battle",
        "http://127.0.0.1:8765/",
        "POST http://127.0.0.1:8000/experiment/run",
        "Do not infer missing results",
        "It does not close any production blocker by itself",
    ]
    for token in required_tokens:
        if token not in doc:
            fail(f"tryout guide missing token: {token}")

    forbidden_tokens = [
        "production_ready: true",
        "customer_validated: true",
        "product_launched: true",
        "private_core_exposed: true",
    ]
    joined = doc + "\n" + GATE.read_text(encoding="utf-8") + "\n" + json.dumps(data)
    for token in forbidden_tokens:
        if token in joined:
            fail(f"forbidden token present: {token}")

    print(
        "SAEE_LOCAL_MVP_TRYOUT_GUIDE_SMOKE: PASS "
        "status=local_tryout_guide_available "
        "production_ready=false customer_validated=false blockers_closed_by_guide=0"
    )


if __name__ == "__main__":
    main()

