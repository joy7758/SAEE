#!/usr/bin/env python3
"""Smoke check for the SAEE support-contact preflight."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_support_contact_preflight import (  # noqa: E402
    DOC_PATH,
    GATE_PATH,
    OUTPUT_JSON,
    OUTPUT_MD,
    evaluate,
)


FALSE_FLAGS = [
    "support_contact_published",
    "support_contact_test_performed",
    "customer_contacted",
    "support_vendor_contacted",
    "customer_support_available",
    "production_support_available",
    "support_process_available",
    "sla_available",
    "on_call_rotation_available",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "production_ready",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
]


def fail(message: str) -> None:
    raise SystemExit("SAEE_SUPPORT_CONTACT_PREFLIGHT_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def check_common(data: dict[str, object]) -> None:
    require(data.get("support_contact_preflight_v0_1") is True, "preflight flag true")
    require(data.get("blocker_target") == "support_contact", "wrong blocker target")
    require(data.get("human_review_required") is True, "human review required")
    require(
        data.get("separate_execution_approval_required") is True,
        "separate execution approval required",
    )
    require(data.get("raw_support_contact_value_recorded") is False, "raw value not recorded")
    require(data.get("raw_support_contact_value_exposed") is False, "raw value not exposed")
    require(data.get("blockers_closed_by_preflight") == 0, "no blocker closure")
    for flag in FALSE_FLAGS:
        require(data.get(flag) is False, f"{flag} must be false")


def main() -> None:
    for path in [DOC_PATH, GATE_PATH]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    run = subprocess.run(
        [sys.executable, "scripts/saee_support_contact_preflight.py", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    output = json.loads(run.stdout)
    check_common(output)
    require(OUTPUT_JSON.exists(), "output json missing")
    require(OUTPUT_MD.exists(), "output markdown missing")

    written = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    check_common(written)
    require(
        written.get("status") in {"hold_missing_candidate", "ready_for_human_review"},
        "written status must be hold or ready",
    )

    missing = evaluate({})
    check_common(missing)
    require(missing["status"] == "hold_missing_candidate", "missing fixture hold")
    require(missing["support_contact_candidate_configured"] is False, "missing fixture unconfigured")
    require(missing["support_contact_available_for_review"] is False, "missing fixture unavailable")

    configured = evaluate({"SAEE_SUPPORT_CONTACT": "support@example.invalid"})
    check_common(configured)
    require(configured["status"] == "ready_for_human_review", "configured fixture ready")
    require(configured["support_contact_candidate_configured"] is True, "configured fixture true")
    require(configured["support_contact_available_for_review"] is True, "configured fixture available")
    require(
        configured["support_contact_candidate_value_redacted"] == "<configured-redacted>",
        "configured fixture must redact value",
    )
    require(
        "support@example.invalid" not in json.dumps(configured),
        "configured fixture must not expose raw contact",
    )

    combined = "\n".join(
        [
            DOC_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
            OUTPUT_MD.read_text(encoding="utf-8"),
            json.dumps(written),
        ]
    )
    required_tokens = [
        "support_contact_published: false",
        "support_contact_test_performed: false",
        "customer_contacted: false",
        "production_support_available: false",
        "production_ready: false",
        "blockers_closed_by_preflight: 0",
    ]
    for token in required_tokens:
        require(token in combined, f"missing token: {token}")
    forbidden_tokens = [
        "support_contact_published: true",
        "\"support_contact_published\": true",
        "support_contact_test_performed: true",
        "\"support_contact_test_performed\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "production_support_available: true",
        "\"production_support_available\": true",
        "production_ready: true",
        "\"production_ready\": true",
        "blockers_closed_by_preflight: 1",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden claim found: " + ", ".join(found))

    print("SAEE_SUPPORT_CONTACT_PREFLIGHT_SMOKE: PASS")


if __name__ == "__main__":
    main()

