#!/usr/bin/env python3
"""Generate local public-shell support/SLA evidence.

This runner converts existing controlled-preview support readiness checks into
a partial production-support evidence JSON file for human review. It does not
configure a support mailbox, contact customers, contact support vendors, start
an on-call rotation, approve SLA terms, modify backend behavior, or mark SAEE
production-ready.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_support_evidence import (
    CUSTOMER_SUPPORT_KEYS,
    FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS,
    SLA_KEYS,
    SUPPORT_CONTACT_KEYS,
    evaluate_production_support_evidence,
)
from saee_backend.services.support_readiness import evaluate_support_readiness


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUTPUT_PATH = OUTPUT_DIR / "support_evidence.local.json"
README_PATH = OUTPUT_DIR / "README.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_local_support_evidence() -> dict[str, Any]:
    readiness = evaluate_support_readiness(load_settings({}))

    require(
        readiness["support_readiness_type"] == "controlled_preview_support_readiness",
        "wrong support readiness type",
    )
    require(readiness["support_runbook_available"] is True, "runbook must be available")
    require(
        readiness["support_case_template_available"] is True,
        "case template must be available",
    )
    require(
        readiness["support_sla_draft_available"] is True,
        "SLA draft must be available",
    )
    require(
        readiness["support_response_targets_documented"] is True,
        "response targets must be documented",
    )
    require(
        readiness["support_contact_configured"] is False,
        "runner must not configure support contact",
    )
    require(
        readiness["customer_support_available"] is False,
        "runner must not claim customer support",
    )
    require(
        readiness["production_support_available"] is False,
        "runner must not claim production support",
    )
    require(readiness["sla_available"] is False, "runner must not claim SLA")
    require(
        readiness["on_call_rotation_available"] is False,
        "runner must not claim on-call rotation",
    )
    require(readiness["external_calls_made"] is False, "runner must not call external services")
    require(readiness["customer_contacted"] is False, "runner must not contact customers")
    return readiness


def build_evidence() -> dict[str, Any]:
    readiness = run_local_support_evidence()

    evidence: dict[str, Any] = {
        "support_evidence_type": "production_support_sla_evidence",
        "evidence_scope": "local_public_shell_support_process_dry_run",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_support_evidence_runner.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_support_readiness_helper": "saee_backend/services/support_readiness.py",
        "support_sla_on_call_review_packet_ready": True,
        "support_sla_on_call_approval_status": "not_approved",
        "support_sla_on_call_evidence_complete": False,
        "customer_facing_support_contact_configured": False,
        "support_contact_owner_named": False,
        "abuse_handling_path_defined": False,
        "customer_notice_route_defined": False,
        "support_contact_test_recorded": False,
        "staffed_support_process_defined": False,
        "case_triage_workflow_defined": True,
        "support_case_audit_trail_available": True,
        "handoff_to_engineering_defined": True,
        "customer_communication_template_approved": False,
        "support_process_dry_run_recorded": True,
        "human_approved_sla_terms": False,
        "severity_definitions_approved": False,
        "support_hours_approved": False,
        "response_targets_approved": False,
        "exclusions_approved": False,
        "legal_review_completed": False,
        "on_call_rotation_defined": False,
        "escalation_schedule_defined": False,
        "incident_commander_named": False,
        "local_public_shell_results": {
            "support_readiness_type": readiness["support_readiness_type"],
            "support_runbook_available": readiness["support_runbook_available"],
            "support_case_template_available": readiness["support_case_template_available"],
            "support_sla_draft_available": readiness["support_sla_draft_available"],
            "support_response_targets_documented": readiness[
                "support_response_targets_documented"
            ],
            "support_contact_configured": False,
            "customer_support_available": False,
            "production_support_available": False,
            "support_process_available": False,
            "sla_available": False,
            "on_call_rotation_available": False,
            "external_calls_made": False,
            "customer_contacted": False,
            "support_vendor_contacted": False,
        },
        "limitations": [
            "No customer-facing support contact is configured.",
            "No staffed support process is defined.",
            "No customer communication template has been approved.",
            "No human-approved SLA terms exist.",
            "No support hours, response targets, exclusions, or legal review are approved.",
            "No on-call rotation, escalation schedule, or incident commander is defined.",
            "This evidence is local public-shell evidence only and does not close the production launch gate.",
        ],
    }
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    evidence["backend_modified"] = False

    missing_expected = [
        key
        for key in SUPPORT_CONTACT_KEYS
        + CUSTOMER_SUPPORT_KEYS
        + SLA_KEYS
        + ON_CALL_KEYS
        + FORBIDDEN_TRUE_KEYS
        if key not in evidence
    ]
    require(not missing_expected, "evidence missing keys: " + ", ".join(missing_expected))
    return evidence


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Support Evidence

Status: local public-shell support process evidence, not production support
readiness.

This directory contains a generated local evidence JSON file for controlled
preview support materials. It records only what the local runner can prove.

It does not configure a customer-facing support contact, create a staffed
support desk, approve customer communication templates, approve SLA terms,
start on-call rotation, contact customers, contact support vendors, modify
runtime behavior, modify backend behavior, modify API schema, or expose private
core.

Primary file:

```text
support_evidence.local.json
support_sla_on_call_review_packet.local.json
support_sla_on_call_review_packet.md
support_contact_decision_packet.local.json
support_contact_decision_packet.md
support_contact_decision_input.template.json
support_contact_decision_packet_boundary_audit.md
support_contact_evidence_builder_output.local.json
production_support_sla_evidence.from_support_contact.local.json
support_contact_approval_input_prompt.local.json
support_contact_approval_input_prompt.md
support_contact_approval_input_prompt.html
support_contact_evidence_builder_report.md
support_contact_evidence_path.local.json
support_contact_evidence_path_report.md
customer_support_evidence_input.template.json
customer_support_approval_input_prompt.local.json
customer_support_approval_input_prompt.md
customer_support_approval_input_prompt.html
customer_support_evidence_builder_output.local.json
production_support_sla_evidence.from_customer_support.local.json
customer_support_evidence_builder_report.md
customer_support_evidence_path.local.json
customer_support_evidence_path_report.md
sla_evidence_input.template.json
sla_approval_input_prompt.local.json
sla_approval_input_prompt.md
sla_approval_input_prompt.html
sla_evidence_builder_output.local.json
production_support_sla_evidence.from_sla.local.json
sla_evidence_builder_report.md
sla_evidence_path.local.json
sla_evidence_path_report.md
on_call_evidence_input.template.json
on_call_approval_input_validation.local.json
on_call_approval_input_validation.md
on_call_approval_input_prompt.local.json
on_call_approval_input_prompt.md
on_call_approval_input_prompt.html
on_call_evidence_builder_output.local.json
production_support_sla_evidence.from_on_call.local.json
on_call_evidence_builder_report.md
on_call_evidence_path.local.json
on_call_evidence_path_report.md
support_sla_evidence_profile.local.json
production_support_sla_evidence.combined_profile.local.json
support_sla_evidence_profile_report.md
```

Generate it with:

```bash
python3 scripts/saee_support_evidence_runner.py
python3 scripts/saee_support_sla_on_call_review_packet.py
python3 scripts/saee_support_contact_decision_packet.py
python3 scripts/saee_support_contact_approval_input_prompt.py
python3 scripts/saee_support_contact_evidence_builder.py
python3 scripts/saee_support_contact_evidence_path.py
python3 scripts/saee_customer_support_approval_input_prompt.py
python3 scripts/saee_customer_support_evidence_builder.py
python3 scripts/saee_customer_support_evidence_path.py
python3 scripts/saee_sla_approval_input_prompt.py
python3 scripts/saee_sla_evidence_builder.py
python3 scripts/saee_sla_evidence_path.py
python3 scripts/saee_on_call_approval_input_validator.py
python3 scripts/saee_on_call_approval_input_prompt.py
python3 scripts/saee_on_call_evidence_builder.py
python3 scripts/saee_on_call_evidence_path.py
python3 scripts/saee_support_sla_evidence_profile.py
```

Boundary:

```yaml
evidence_scope: local_public_shell_support_process_dry_run
support_sla_on_call_review_packet_ready: true
support_sla_on_call_evidence_complete: false
support_sla_on_call_approval_status: not_approved
support_contact_available: false
support_contact_configured: false
customer_facing_support_contact_configured: false
support_contact_evidence_builder_available: true
support_contact_evidence_builder_status: local_builder_available_default_hold
support_contact_evidence_builder_closes_blockers: false
support_contact_approval_input_prompt_available: true
support_contact_approval_input_prompt_status: hold_human_support_contact_input_required
support_contact_approval_input_prompt_required_metadata_fields: 4
support_contact_approval_input_prompt_required_support_contact_evidence_items: 5
support_contact_approval_input_prompt_candidate_contact_slots: 2
support_contact_approval_input_prompt_html_available: true
local_static_support_contact_approval_input_prompt_html: true
browser_readable_support_contact_approval_input_prompt: true
plain_language_support_contact_approval_input_prompt_v0_2: true
support_contact_approval_input_prompt_ready_for_evidence_builder: false
support_contact_approval_input_prompt_builder_ready: false
support_contact_approval_input_prompt_closes_blockers: false
support_contact_evidence_path_available: true
support_contact_evidence_path_status: local_fixture_only_path_proof
support_contact_evidence_path_type: local_fixture_only_support_contact_evidence_path
support_contact_evidence_path_fixture_only: true
support_contact_evidence_path_real_contact_configured: false
support_contact_evidence_path_blocker_path_proven: true
support_contact_evidence_path_target_blockers_satisfied_count: 1
support_contact_evidence_path_production_blocker_count: 23
support_contact_evidence_path_closes_blockers: false
customer_support_evidence_builder_available: true
customer_support_evidence_builder_status: local_builder_available_default_hold
customer_support_evidence_builder_closes_blockers: false
customer_support_approval_input_prompt_available: true
customer_support_approval_input_prompt_status: hold_human_customer_support_input_required
customer_support_approval_input_prompt_required_metadata_fields: 4
customer_support_approval_input_prompt_required_customer_support_evidence_items: 6
customer_support_approval_input_prompt_html_available: true
local_static_customer_support_approval_input_prompt_html: true
browser_readable_customer_support_approval_input_prompt: true
plain_language_customer_support_approval_input_prompt_v0_2: true
customer_support_approval_input_prompt_ready_for_evidence_builder: false
customer_support_approval_input_prompt_builder_ready: false
customer_support_approval_input_prompt_closes_blockers: false
customer_support_evidence_path_available: true
customer_support_evidence_path_status: local_fixture_only_path_proof
customer_support_evidence_path_type: local_fixture_only_customer_support_evidence_path
customer_support_evidence_path_fixture_only: true
customer_support_evidence_path_real_support_configured: false
customer_support_evidence_path_blocker_path_proven: true
customer_support_evidence_path_target_blockers_satisfied_count: 1
customer_support_evidence_path_production_blocker_count: 23
customer_support_evidence_path_closes_blockers: false
sla_evidence_builder_available: true
sla_evidence_builder_status: local_builder_available_default_hold
sla_evidence_builder_closes_blockers: false
sla_approval_input_prompt_available: true
sla_approval_input_prompt_status: hold_human_sla_input_required
sla_approval_input_prompt_required_metadata_fields: 5
sla_approval_input_prompt_required_sla_evidence_items: 6
sla_approval_input_prompt_html_available: true
local_static_sla_approval_input_prompt_html: true
browser_readable_sla_approval_input_prompt: true
plain_language_sla_approval_input_prompt_v0_2: true
sla_approval_input_prompt_ready_for_evidence_builder: false
sla_approval_input_prompt_builder_ready: false
sla_approval_input_prompt_closes_blockers: false
sla_evidence_path_available: true
sla_evidence_path_status: local_fixture_only_path_proof
sla_evidence_path_type: local_fixture_only_sla_evidence_path
sla_evidence_path_fixture_only: true
sla_evidence_path_real_sla_terms_approved: false
sla_evidence_path_blocker_path_proven: true
sla_evidence_path_target_blockers_satisfied_count: 1
sla_evidence_path_production_blocker_count: 23
sla_evidence_path_closes_blockers: false
on_call_approval_input_validator_available: true
on_call_approval_input_validator_status: hold
on_call_approval_input_validator_builder_ready: false
on_call_approval_input_validator_closes_blockers: false
on_call_approval_input_prompt_available: true
on_call_approval_input_prompt_status: hold_human_on_call_input_required
on_call_approval_input_prompt_required_metadata_fields: 5
on_call_approval_input_prompt_required_on_call_evidence_items: 3
on_call_approval_input_prompt_html_available: true
local_static_on_call_approval_input_prompt_html: true
browser_readable_on_call_approval_input_prompt: true
plain_language_on_call_approval_input_prompt_v0_2: true
on_call_approval_input_prompt_ready_for_evidence_builder: false
on_call_approval_input_prompt_builder_ready: false
on_call_approval_input_prompt_closes_blockers: false
on_call_evidence_builder_available: true
on_call_evidence_builder_status: local_builder_available_default_hold
on_call_evidence_builder_closes_blockers: false
on_call_evidence_path_available: true
on_call_evidence_path_status: local_fixture_only_path_proof
on_call_evidence_path_type: local_fixture_only_on_call_evidence_path
on_call_evidence_path_fixture_only: true
on_call_evidence_path_real_on_call_rotation_started: false
on_call_evidence_path_blocker_path_proven: true
on_call_evidence_path_target_blockers_satisfied_count: 1
on_call_evidence_path_production_blocker_count: 23
on_call_evidence_path_closes_blockers: false
support_sla_evidence_profile_available: true
support_sla_evidence_profile_status: local_combined_support_sla_profile_hold
support_sla_evidence_profile_scope: combined_support_sla_evidence_profile_to_go_no_go
support_sla_evidence_profile_target_blockers_satisfied: 0
support_sla_evidence_profile_production_blocker_count: 24
support_sla_evidence_profile_closes_blockers: false
customer_support_available: false
production_support_available: false
support_process_available: false
sla_available: false
on_call_rotation_available: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
customer_contacted: false
support_vendor_contacted: false
```

The support / SLA / on-call review packet is a draft for human review only. It
does not configure a customer-facing support contact, create a staffed support
desk, approve customer communication templates, approve SLA terms, start
on-call rotation, contact customers, contact support vendors, or make SAEE
production-ready.

The support contact decision packet is a focused human-review surface for the
`support_contact` blocker. It maps the customer-facing support contact fields
that would later be required by production support/SLA evidence, but it does
not publish or configure a support contact, perform support-contact tests,
contact customers, contact support vendors, close blockers, or claim
production readiness.

Boundary invariant: this packet does not publish or configure a support contact.

The support contact evidence builder converts a human-filled support-contact
decision input into a production support/SLA evidence-shaped JSON file for the
`support_contact` group only. Its default output is hold. It does not publish
or configure a support contact, send support-contact tests, contact customers,
contact vendors, approve customer support, approve SLA terms, start on-call
rotation, close blockers, or make SAEE production-ready.

The support contact approval input prompt tells a human reviewer how to fill
the local support-contact decision input before validator use. It records the
required metadata fields, support-contact evidence keys, and candidate contact
slot fields, but it does not approve, configure, publish, or test a support
contact; contact customers or vendors; execute the evidence builder; close
blockers; or make SAEE production-ready.

The browser-readable support contact approval input prompt is available at
`support_contact_approval_input_prompt.html`. It gives the same human-only
approval path in plain Chinese, with no script, no form, no external link, no
support-contact publication, no customer contact, and no production-ready
claim.

The support contact evidence path uses fixture-only support-contact data to
prove the local wiring through the support-contact builder, support/SLA
profile, and commercial go/no-go. It does not publish or configure a support
contact, perform support-contact tests, contact customers or vendors, close
blockers, or make SAEE production-ready.

The customer support evidence builder converts a human-filled customer-support
process input into a production support/SLA evidence-shaped JSON file for the
`customer_support` group only. Its default output is hold. It does not staff
support, create support cases, send customer communications, contact customers,
contact vendors, approve SLA terms, start on-call rotation, close blockers, or
make SAEE production-ready.

The customer support approval input prompt tells a human reviewer how to fill
the local customer-support process input before validator use. It records the
required metadata fields and customer-support evidence keys, but it does not
approve, configure, publish, staff, or start customer support; create support
cases; send customer communications; execute the evidence builder; close
blockers; or make SAEE production-ready.

The browser-readable customer support approval input prompt is available at
`customer_support_approval_input_prompt.html`. It gives the same human-only
approval path in plain Chinese, with no script, no form, no external link, no
customer-support publication, no support-case creation, no customer contact,
and no production-ready claim.

The customer support evidence path uses fixture-only customer-support process
data to prove the local wiring through the customer-support builder,
support/SLA profile, and commercial go/no-go. It does not staff support,
create support cases, send customer communications, contact customers or
vendors, close blockers, or make SAEE production-ready.

The SLA evidence builder converts a human-filled SLA approval input into a
production support/SLA evidence-shaped JSON file for the `sla` group only. Its
default output is hold. It does not publish SLA terms, approve legal terms by
itself, contact customers, contact vendors, start support operations, start
on-call rotation, close blockers, or make SAEE production-ready.

The SLA approval input prompt tells a human reviewer how to fill the local SLA
approval input before validator use. It records the required metadata fields
and SLA evidence keys, but it does not approve or publish SLA terms, complete
legal review, publish support hours or response targets, start support
operations, execute the evidence builder, close blockers, or make SAEE
production-ready.

The SLA evidence path uses fixture-only SLA approval data to prove the local
wiring through the SLA builder, support/SLA profile, and commercial go/no-go.
It does not approve or publish SLA terms, contact customers or vendors, start
support operations, close blockers, or make SAEE production-ready.

The on-call approval input validator checks human-filled on-call evidence input
before builder use. It does not start on-call rotation, publish an escalation
schedule, assign an incident commander, contact customers or vendors, start
support operations, close blockers, or make SAEE production-ready.

The on-call approval input prompt tells a human reviewer how to fill the local
on-call evidence input before validator use. It records the required metadata
fields and on-call evidence keys, but it does not start on-call rotation,
publish escalation schedules, assign incident commanders, start support
operations, execute the evidence builder, close blockers, or make SAEE
production-ready.

The on-call evidence builder converts a human-filled on-call rotation input
into a production support/SLA evidence-shaped JSON file for the
`on_call_rotation` group only. Its default output is hold. It does not start
on-call rotation, publish an escalation schedule, assign an incident
commander, contact customers, contact vendors, close blockers, or make SAEE
production-ready.

The on-call evidence path uses fixture-only on-call rotation data to prove the
local wiring through the on-call builder, support/SLA profile, and commercial
go/no-go. It does not start on-call rotation, publish escalation schedules,
assign incident commanders, contact customers or vendors, close blockers, or
make SAEE production-ready.

The support/SLA evidence profile combines the local support-contact,
customer-support, SLA, and on-call evidence outputs for commercial go/no-go
review. Its default profile remains hold, satisfies zero production blockers,
and does not start support operations or make SAEE production-ready.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = build_evidence()
    OUTPUT_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readme()
    readiness = evaluate_production_support_evidence(
        load_settings({"SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(OUTPUT_PATH)})
    )
    print(
        "SAEE_SUPPORT_EVIDENCE_RUNNER: PASS "
        f"path={OUTPUT_PATH} "
        f"status={readiness['status']} "
        "local_public_shell_evidence=true "
        "production_support_available=false"
    )


if __name__ == "__main__":
    main()
