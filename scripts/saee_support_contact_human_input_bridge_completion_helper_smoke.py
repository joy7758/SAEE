#!/usr/bin/env python3
"""Smoke check for support contact bridge completion helper v0.1."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_contact_human_input_bridge_completion_helper.py"
BRIDGE_DIR = (
    ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge"
)
TEMPLATE = BRIDGE_DIR / "support_contact_human_input_bridge_input.template.json"
STATUS_JSON = BRIDGE_DIR / "support_contact_human_input_bridge_completion_status.local.json"
STATUS_MD = BRIDGE_DIR / "support_contact_human_input_bridge_completion_status.md"
GUIDE = BRIDGE_DIR / "support_contact_human_input_bridge_completion_guide.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_COMPLETION_HELPER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_COMPLETION_HELPER_RECOMMENDATION_GATE.md"
)

PASS_PREFIX = "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_COMPLETION_HELPER_SMOKE: PASS"
FAIL_PREFIX = "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_COMPLETION_HELPER_SMOKE: FAIL "


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(FAIL_PREFIX + message)


def run_helper(*args: str) -> None:
    subprocess.run([sys.executable, str(RUNNER), *args], cwd=ROOT, check=True, text=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fill_fixture(template: dict) -> dict:
    data = json.loads(json.dumps(template))
    data["input_status"] = "human_filled_fixture_for_local_export_test"
    data["human_reviewer_name"] = "Fixture Reviewer"
    data["review_date"] = "2026-07-05"
    data["review_notes"] = "Fixture-only local smoke test input."
    owner = data["first_owner_input"]
    owner["assigned_human_owner"] = "Fixture Owner"
    owner["owner_contact_reference"] = "internal-fixture-owner-ref"
    owner["target_review_date"] = "2026-07-12"
    owner["owner_acknowledged_scope"] = True
    owner["human_approval_reference"] = "fixture-approval-ref"
    support = data["support_contact_decision_input"]
    support["human_reviewer_name"] = "Fixture Reviewer"
    support["review_date"] = "2026-07-05"
    support["selected_support_contact_channel"] = "redacted_support_route_candidate"
    support["decision_summary"] = "Fixture-only support contact input export test."
    for key in [
        "customer_facing_support_contact_configured",
        "support_contact_owner_named",
        "abuse_handling_path_defined",
        "customer_notice_route_defined",
        "support_contact_test_recorded",
    ]:
        support["evidence_review"][key] = True
        support["source_notes_by_key"][key] = "Fixture-only local source note."
    slot = support["candidate_contact_slots"][0]
    slot["contact_channel"] = "redacted_support_route_candidate"
    slot["display_value_redacted"] = "support route redacted"
    slot["owner_named"] = True
    slot["abuse_handling_reviewed"] = True
    slot["customer_notice_route_reviewed"] = True
    slot["test_plan_reviewed"] = True
    slot["human_source_note"] = "Fixture-only local source note."
    return data


def check_default_status() -> None:
    data = read_json(STATUS_JSON)
    expected = {
        "support_contact_human_input_bridge_completion_helper_v0_1": True,
        "helper_type": "saee_support_contact_human_input_bridge_completion_helper",
        "helper_scope": "local_combined_human_input_template_and_export_helper",
        "status": "hold_combined_human_input_required",
        "target_blocker_id": "support_contact",
        "combined_input_export_performed": False,
        "ready_for_first_owner_validator": False,
        "ready_for_support_contact_approval_input_validator": False,
        "ready_for_evidence_collection": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blockers_closed_by_helper": 0,
        "human_input_required": True,
        "human_review_required": True,
        "requires_separate_validators": True,
        "requires_separate_evidence_collection_request": True,
        "requires_separate_blocker_closure_approval": True,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
    }
    for key, value in expected.items():
        require(data.get(key) == value, f"{key} must be {value}")


def snapshot_files(paths: list[Path]) -> dict[Path, str | None]:
    return {
        path: path.read_text(encoding="utf-8") if path.exists() else None
        for path in paths
    }


def restore_files(snapshot: dict[Path, str | None]) -> None:
    for path, content in snapshot.items():
        if content is None:
            if path.exists():
                path.unlink()
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def main() -> int:
    mutable_paths = [TEMPLATE, STATUS_JSON, STATUS_MD, GUIDE, TOP_DOC, GATE]
    snapshot = snapshot_files(mutable_paths)
    try:
        run_helper()
        for path in mutable_paths:
            require(path.is_file(), f"missing {path.relative_to(ROOT)}")
        check_default_status()
        template = read_json(TEMPLATE)
        require(
            template.get("template_type") == "saee_support_contact_human_input_bridge_combined_input",
            "combined template type changed",
        )
        require(template.get("target_blocker_id") == "support_contact", "target blocker changed")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fixture = tmp_path / "bridge_input.fixture.json"
            first_owner_output = tmp_path / "first_owner_export.json"
            support_output = tmp_path / "support_contact_export.json"
            fixture.write_text(
                json.dumps(fill_fixture(template), indent=2) + "\n", encoding="utf-8"
            )
            run_helper(
                "--combined-input",
                str(fixture),
                "--first-owner-output",
                str(first_owner_output),
                "--support-contact-output",
                str(support_output),
            )
            ready = read_json(STATUS_JSON)
            require(ready.get("status") == "ready_for_separate_validators", "fixture export status")
            require(ready.get("combined_input_export_performed") is True, "fixture export flag")
            require(ready.get("ready_for_first_owner_validator") is True, "first owner validator flag")
            require(
                ready.get("ready_for_support_contact_approval_input_validator") is True,
                "support validator flag",
            )
            require(ready.get("ready_for_evidence_collection") is False, "evidence must remain false")
            require(ready.get("blockers_closed_by_helper") == 0, "blocker closure must remain zero")
            require(first_owner_output.is_file(), "first owner export missing")
            require(support_output.is_file(), "support contact export missing")

        run_helper()
        check_default_status()

        combined = "\n".join(
            path.read_text(encoding="utf-8") for path in [STATUS_MD, GUIDE, TOP_DOC, GATE]
        )
        for token in [
            "support_contact_human_input_bridge_completion_helper_v0_1: true",
            "status: hold_combined_human_input_required",
            "helper_scope: local_combined_human_input_template_and_export_helper",
            "combined_input_export_performed: false",
            "ready_for_first_owner_validator: false",
            "ready_for_support_contact_approval_input_validator: false",
            "ready_for_evidence_collection: false",
            "evidence_collection_authorized: false",
            "execution_authorized: false",
            "blockers_closed_by_helper: 0",
            "production_ready: false",
            "customer_validated: false",
            "product_launched: false",
            "private_core_exposed: false",
            "answer: recommend",
            "recommend_for_combined_input_template: true",
            "recommend_for_local_validator_input_export: true",
            "recommend_for_running_validators: false",
            "recommend_for_evidence_collection: false",
            "recommend_for_automatic_execution: false",
            "recommend_for_blocker_closure: false",
            "recommend_for_product_launch: false",
            "recommend_for_production_readiness_claim: false",
        ]:
            require(token in combined, "missing doc token " + token)

        print(
            PASS_PREFIX
            + " status=hold_combined_human_input_required "
            + "combined_input_export_performed=false blockers_closed_by_helper=0 production_ready=false"
        )
        return 0
    finally:
        restore_files(snapshot)


if __name__ == "__main__":
    raise SystemExit(main())
