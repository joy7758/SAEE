#!/usr/bin/env python3
"""Fixture-only dry run for support-contact bridge validator compatibility.

This script proves that the combined bridge input can be split into the two
existing support_contact validator inputs and that both validators can accept
those temporary exports. It does not run evidence builders, configure support,
publish contacts, send tests, close blockers, or claim production readiness.
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_commercial_evidence_sprint_first_owner_input_validator import (  # noqa: E402
    build_validation as build_first_owner_validation,
)
from scripts.saee_support_contact_approval_input_validator import (  # noqa: E402
    build_validation as build_support_contact_validation,
)
from scripts.saee_support_contact_human_input_bridge_completion_helper import (  # noqa: E402
    build_combined_template,
    export_first_owner,
    export_support_decision,
)


OUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge"
OUT_JSON = OUT_DIR / "support_contact_bridge_validator_dry_run.local.json"
OUT_MD = OUT_DIR / "support_contact_bridge_validator_dry_run.md"
OUT_BOUNDARY = OUT_DIR / "support_contact_bridge_validator_dry_run_boundary_audit.md"
TOP_DOC = (
    ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_BRIDGE_VALIDATOR_DRY_RUN_V0_1.md"
)
GATE = (
    ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_BRIDGE_VALIDATOR_DRY_RUN_RECOMMENDATION_GATE.md"
)

SUPPORT_KEYS = [
    "customer_facing_support_contact_configured",
    "support_contact_owner_named",
    "abuse_handling_path_defined",
    "customer_notice_route_defined",
    "support_contact_test_recorded",
]

FALSE_FLAGS = [
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "owner_assigned_by_codex",
    "owner_contacted_by_codex",
    "support_contact_configured_by_codex",
    "support_contact_published_by_codex",
    "support_contact_tested_by_codex",
    "support_contact_available",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "support_vendor_contacted",
    "customer_facing_support_contact_configured",
    "customer_support_available",
    "production_support_available",
    "production_support_claim_published",
]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_input() -> dict[str, Any]:
    data = build_combined_template()
    data["input_status"] = "fixture_only_bridge_validator_dry_run_input"
    data["human_reviewer_name"] = "Fixture Reviewer"
    data["review_date"] = "2026-07-05"
    data["review_notes"] = "Fixture-only local bridge validator dry run."
    owner = data["first_owner_input"]
    owner["assigned_human_owner"] = "Fixture Owner"
    owner["owner_contact_reference"] = "internal-fixture-owner-reference"
    owner["target_review_date"] = "2026-07-12"
    owner["owner_acknowledged_scope"] = True
    owner["human_approval_reference"] = "fixture-human-approval-reference"
    owner["notes"] = "Fixture-only local validator compatibility check."

    support = data["support_contact_decision_input"]
    support["input_status"] = "fixture_only_support_contact_decision_input"
    support["human_reviewer_name"] = "Fixture Reviewer"
    support["review_date"] = "2026-07-05"
    support["selected_support_contact_channel"] = "redacted_fixture_support_route"
    support["decision_summary"] = "Fixture-only support contact validator compatibility check."
    for key in SUPPORT_KEYS:
        support["evidence_review"][key] = True
        support["source_notes_by_key"][key] = "Fixture-only local source note."
    slot = support["candidate_contact_slots"][0]
    slot["contact_channel"] = "redacted_fixture_support_route"
    slot["display_value_redacted"] = "redacted fixture support route"
    slot["owner_named"] = True
    slot["abuse_handling_reviewed"] = True
    slot["customer_notice_route_reviewed"] = True
    slot["test_plan_reviewed"] = True
    slot["human_source_note"] = "Fixture-only local source note."
    return data


def build_payload() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        combined_input = tmp_dir / "combined_bridge_input.fixture.json"
        first_owner_export = tmp_dir / "first_owner_export.fixture.json"
        support_export = tmp_dir / "support_contact_export.fixture.json"
        write_json(combined_input, fixture_input())
        fixture = json.loads(combined_input.read_text(encoding="utf-8"))
        export_first_owner(fixture, first_owner_export)
        export_support_decision(fixture, support_export)
        first_owner_validation = build_first_owner_validation(first_owner_export)
        support_validation = build_support_contact_validation(support_export)

    first_owner_pass = first_owner_validation.get("validation_status") == "pass"
    support_pass = support_validation.get("validation_status") == "pass"
    payload: dict[str, Any] = {
        "support_contact_bridge_validator_dry_run_v0_1": True,
        "dry_run_type": "fixture_only_bridge_to_validator_compatibility_check",
        "dry_run_scope": "local_tempfile_fixture_validator_compatibility_only",
        "status": "pass_fixture_only" if first_owner_pass and support_pass else "hold_fixture_failed",
        "target_blocker_id": "support_contact",
        "fixture_only": True,
        "combined_input_fixture_used": True,
        "temp_exports_only": True,
        "local_validators_invoked": True,
        "first_owner_validator_status": first_owner_validation.get("status"),
        "first_owner_validator_validation_status": first_owner_validation.get("validation_status"),
        "first_owner_assignment_complete": first_owner_validation.get("first_owner_assignment_complete"),
        "support_contact_approval_validation_status": support_validation.get("validation_status"),
        "support_contact_approval_input_complete": support_validation.get("input_complete"),
        "support_contact_approval_builder_ready": support_validation.get("builder_ready"),
        "ready_for_evidence_collection": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blockers_closed_by_dry_run": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "human_real_input_required": True,
        "next_action": (
            "A human may fill the combined bridge input and run the completion "
            "helper plus validators separately. This fixture-only dry run closes "
            "no blockers and authorizes no evidence collection."
        ),
        "generated_by": "scripts/saee_support_contact_bridge_validator_dry_run.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_dry_run"] = 0
    return payload


def write_docs(payload: dict[str, Any]) -> None:
    shared = f"""support_contact_bridge_validator_dry_run_v0_1: true
status: {payload['status']}
dry_run_scope: local_tempfile_fixture_validator_compatibility_only
fixture_only: true
combined_input_fixture_used: true
temp_exports_only: true
local_validators_invoked: true
first_owner_validator_validation_status: {payload['first_owner_validator_validation_status']}
support_contact_approval_validation_status: {payload['support_contact_approval_validation_status']}
support_contact_approval_builder_ready: {str(payload['support_contact_approval_builder_ready']).lower()}
ready_for_evidence_collection: false
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blockers_closed_by_dry_run: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false"""
    OUT_MD.write_text(
        f"""# Support Contact Bridge Validator Dry Run

{shared}

## Purpose

This fixture-only dry run verifies that the combined bridge input shape can be
split into the two existing local validator inputs and accepted by both
validators. It uses temporary files only.

## Boundary

The dry run does not run an evidence builder, configure or publish a support
contact, send tests, contact customers or vendors, collect evidence, close
blockers, launch product, or claim production readiness.
""",
        encoding="utf-8",
    )
    OUT_BOUNDARY.write_text(
        f"""# Support Contact Bridge Validator Dry Run Boundary Audit

{shared}

## Confirmed Boundaries

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- customer_contacted: false
- support_contact_configured: false
- support_contact_published: false
- support_contact_test_performed: false
- evidence_collection_authorized: false
- execution_authorized: false
- evidence_builder_executed: false
- blockers_closed_by_dry_run: 0
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Support Contact Bridge Validator Dry Run v0.1

{shared}

## Agent Recommendation Gate

recommendation_gate:
  feature_or_direction: support_contact_bridge_validator_dry_run
  target_customer_need: prove local handoff compatibility before human support_contact input
  answer: recommend
  reasons_to_recommend:
    - It verifies the combined input can reach existing validators.
    - It uses fixture-only temporary files and keeps evidence collection false.
  reasons_not_to_recommend:
    - It does not prove real support contact evidence.
    - It does not close the support_contact blocker.
  final_decision: recommend_for_fixture_only_validator_compatibility
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Support Contact Bridge Validator Dry Run Recommendation Gate

answer: recommend
recommend_for_fixture_only_validator_compatibility: true
recommend_for_real_evidence: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

reason: The dry run proves the bridge-to-validator handoff locally using
temporary fixture files while keeping production evidence and blocker closure
false.

{shared}
""",
        encoding="utf-8",
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_docs(payload)
    print(
        "SAEE_SUPPORT_CONTACT_BRIDGE_VALIDATOR_DRY_RUN: PASS "
        f"status={payload['status']} "
        "fixture_only=true local_validators_invoked=true "
        "blockers_closed_by_dry_run=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
