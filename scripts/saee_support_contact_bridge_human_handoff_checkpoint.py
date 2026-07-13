#!/usr/bin/env python3
"""Create the human handoff checkpoint for support_contact bridge input.

This checkpoint is a local status surface. It tells a human reviewer exactly
which bridge input to fill and which local commands to run after filling it. It
does not fill the input, run validators on real input, run evidence builders,
configure support, publish contact details, send tests, close blockers, or
claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = (
    ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge"
)
OUT_JSON = BRIDGE_DIR / "support_contact_bridge_human_handoff_checkpoint.local.json"
OUT_MD = BRIDGE_DIR / "support_contact_bridge_human_handoff_checkpoint.md"
OUT_BOUNDARY = BRIDGE_DIR / "support_contact_bridge_human_handoff_checkpoint_boundary_audit.md"
TOP_DOC = (
    ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_BRIDGE_HUMAN_HANDOFF_CHECKPOINT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_SUPPORT_CONTACT_BRIDGE_HUMAN_HANDOFF_CHECKPOINT_RECOMMENDATION_GATE.md"
)

COMBINED_TEMPLATE = BRIDGE_DIR / "support_contact_human_input_bridge_input.template.json"
COMPLETION_GUIDE = BRIDGE_DIR / "support_contact_human_input_bridge_completion_guide.md"
COMPLETION_STATUS = BRIDGE_DIR / "support_contact_human_input_bridge_completion_status.local.json"
DRY_RUN = BRIDGE_DIR / "support_contact_bridge_validator_dry_run.local.json"

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
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "evidence_builder_executed",
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
    "blocker_closure_authorized",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_SUPPORT_CONTACT_BRIDGE_HUMAN_HANDOFF_CHECKPOINT: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_SUPPORT_CONTACT_BRIDGE_HUMAN_HANDOFF_CHECKPOINT: "
            f"FAIL {path} must contain a JSON object"
        )
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def required_paths() -> list[Path]:
    return [COMBINED_TEMPLATE, COMPLETION_GUIDE, COMPLETION_STATUS, DRY_RUN]


def build_payload() -> dict[str, Any]:
    missing = [rel(path) for path in required_paths() if not path.exists()]
    completion = read_json(COMPLETION_STATUS) if COMPLETION_STATUS.exists() else {}
    dry_run = read_json(DRY_RUN) if DRY_RUN.exists() else {}
    prerequisites_passed = (
        not missing
        and completion.get("status")
        in {"hold_combined_human_input_required", "ready_for_separate_validators"}
        and dry_run.get("status") == "pass_fixture_only"
        and dry_run.get("local_validators_invoked") is True
        and dry_run.get("first_owner_validator_validation_status") == "pass"
        and dry_run.get("support_contact_approval_validation_status") == "pass"
    )
    payload: dict[str, Any] = {
        "support_contact_bridge_human_handoff_checkpoint_v0_1": True,
        "checkpoint_type": "human_only_support_contact_bridge_handoff",
        "checkpoint_scope": "local_human_handoff_status_and_commands_only",
        "status": "ready_for_human_bridge_input" if prerequisites_passed else "hold_missing_prerequisite",
        "target_blocker_id": "support_contact",
        "missing_prerequisites": missing,
        "combined_input_template": rel(COMBINED_TEMPLATE),
        "human_filled_input_target": rel(
            BRIDGE_DIR / "support_contact_human_input_bridge_input.human_filled.local.json"
        ),
        "completion_guide": rel(COMPLETION_GUIDE),
        "completion_status": rel(COMPLETION_STATUS),
        "validator_dry_run_status": dry_run.get("status"),
        "validator_dry_run_fixture_only": dry_run.get("fixture_only") is True,
        "local_validators_invoked_in_fixture": dry_run.get("local_validators_invoked") is True,
        "first_owner_validator_fixture_status": dry_run.get(
            "first_owner_validator_validation_status"
        ),
        "support_contact_approval_validator_fixture_status": dry_run.get(
            "support_contact_approval_validation_status"
        ),
        "human_input_required": True,
        "human_real_input_required": True,
        "human_filled_input_present": (
            BRIDGE_DIR / "support_contact_human_input_bridge_input.human_filled.local.json"
        ).exists(),
        "ready_for_evidence_collection": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blockers_closed_by_checkpoint": 0,
        "next_human_action": (
            "Copy the combined template to the human-filled input path, fill all "
            "required support_contact fields, run the completion helper, then run "
            "the two local validators. Do not run evidence builders without a "
            "separate explicit human execution request."
        ),
        "post_fill_commands": [
            "cp phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.template.json phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json",
            "python3 scripts/saee_support_contact_human_input_bridge_completion_helper.py --combined-input phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json",
            "python3 scripts/saee_commercial_evidence_sprint_first_owner_input_validator.py --input phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.from_bridge.human_filled.local.json",
            "python3 scripts/saee_support_contact_approval_input_validator.py --input phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.from_bridge.human_filled.local.json",
        ],
        "forbidden_next_actions": [
            "run evidence builder without separate human execution request",
            "configure or publish support contact by Codex",
            "send support-contact tests by Codex",
            "contact customers or vendors",
            "close support_contact blocker",
            "claim product launch or production readiness",
        ],
        "generated_by": "scripts/saee_support_contact_bridge_human_handoff_checkpoint.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def shared_lines(payload: dict[str, Any]) -> str:
    return f"""support_contact_bridge_human_handoff_checkpoint_v0_1: true
status: {payload['status']}
checkpoint_scope: local_human_handoff_status_and_commands_only
target_blocker_id: support_contact
combined_input_template: {payload['combined_input_template']}
human_filled_input_target: {payload['human_filled_input_target']}
validator_dry_run_status: {payload['validator_dry_run_status']}
validator_dry_run_fixture_only: {str(payload['validator_dry_run_fixture_only']).lower()}
local_validators_invoked_in_fixture: {str(payload['local_validators_invoked_in_fixture']).lower()}
human_input_required: true
human_real_input_required: true
human_filled_input_present: {str(payload['human_filled_input_present']).lower()}
ready_for_evidence_collection: false
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blockers_closed_by_checkpoint: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false"""


def write_docs(payload: dict[str, Any]) -> None:
    shared = shared_lines(payload)
    commands = "\n".join(f"{i}. `{cmd}`" for i, cmd in enumerate(payload["post_fill_commands"], 1))
    forbidden = "\n".join(f"- {item}" for item in payload["forbidden_next_actions"])
    OUT_MD.write_text(
        f"""# Support Contact Bridge Human Handoff Checkpoint

{shared}

## Purpose

This checkpoint gives the human reviewer one current handoff surface for the
`support_contact` bridge input. It points to the combined template, the intended
human-filled copy path, and the local commands to run after a human has filled
the input.

## Human Steps

{commands}

## Forbidden Actions

{forbidden}

This checkpoint does not fill human input, run validators against real human
input, run evidence builders, configure or publish support contact details,
send tests, contact customers or vendors, close blockers, launch product, or
claim production readiness.
""",
        encoding="utf-8",
    )
    OUT_BOUNDARY.write_text(
        f"""# Support Contact Bridge Human Handoff Checkpoint Boundary Audit

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
- blockers_closed_by_checkpoint: 0
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Support Contact Bridge Human Handoff Checkpoint v0.1

{shared}

## Agent Recommendation Gate

recommendation_gate:
  feature_or_direction: support_contact_bridge_human_handoff_checkpoint
  target_customer_need: make the next support_contact human input step unambiguous
  agent_answer: recommend
  reason: This is a local handoff checkpoint that improves commercial-readiness process clarity without executing evidence collection or changing product behavior.
  recommend_for_human_handoff: true
  recommend_for_real_evidence: false
  recommend_for_evidence_collection: false
  recommend_for_automatic_execution: false
  recommend_for_blocker_closure: false
  recommend_for_product_launch: false
  recommend_for_production_readiness_claim: false

## Boundary

This checkpoint does not fill human input, configure support, publish support
contact details, send tests, contact customers or vendors, run evidence
builders, close blockers, launch product, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Support Contact Bridge Human Handoff Checkpoint Recommendation Gate

answer: recommend
recommend_for_human_handoff: true
recommend_for_real_evidence: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The checkpoint makes the next human-only `support_contact` step explicit after
the fixture-only validator dry run passed. It is useful because it reduces
operator ambiguity while preserving all execution and production boundaries.

## Boundary

{shared}
""",
        encoding="utf-8",
    )


def main() -> int:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_docs(payload)
    print(
        "SAEE_SUPPORT_CONTACT_BRIDGE_HUMAN_HANDOFF_CHECKPOINT: PASS "
        f"status={payload['status']} human_input_required=true "
        "evidence_collection_authorized=false blockers_closed_by_checkpoint=0 "
        "production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
