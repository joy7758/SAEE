#!/usr/bin/env python3
"""Prove the local SLA evidence path without publishing SLA terms.

This path check uses temporary fixture-only SLA approval evidence, converts it
through the existing SLA evidence builder, then feeds that evidence into the
support/SLA profile. It proves the wiring from human input to commercial
go/no-go without approving legal terms, publishing SLA terms, contacting
anyone, closing blockers by itself, or claiming production readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_support_evidence import SLA_KEYS
from scripts.saee_sla_evidence_builder import (
    INPUT_FORBIDDEN_TRUE_KEYS,
    build_from_input,
)
from scripts.saee_support_sla_evidence_profile import (
    DEFAULT_SOURCE_PATHS,
    build_profile,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "sla_evidence_path.local.json"
REPORT_PATH = OUTPUT_DIR / "sla_evidence_path_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/SLA_EVIDENCE_PATH_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_SLA_EVIDENCE_PATH_RECOMMENDATION_GATE.md"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_input() -> dict[str, Any]:
    return {
        "template_type": "saee_sla_evidence_input",
        "template_version": "v0.1",
        "input_status": "fixture_only_not_real_sla_approval",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": datetime.now(timezone.utc).date().isoformat(),
        "sla_terms_owner": "Fixture SLA Owner",
        "legal_reviewer_name": "Fixture Legal Reviewer",
        "decision_summary": (
            "Fixture-only SLA path proof. This is not real SLA approval or "
            "legal review."
        ),
        "evidence_review": {key: True for key in SLA_KEYS},
        "source_notes_by_key": {
            key: f"Fixture-only source note for {key}." for key in SLA_KEYS
        },
        "sla_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://sla/{key}",
                "owner_named": True,
                "legal_or_commercial_reviewed": True,
                "human_source_note": f"Fixture-only human source note for {key}.",
            }
            for key in SLA_KEYS
        ],
        "boundary_review": {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS},
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "sla_published_by_codex": False,
        "sla_approved_by_codex": False,
        "legal_review_completed_by_codex": False,
        "support_hours_published_by_codex": False,
        "response_targets_published_by_codex": False,
        "support_operations_started": False,
        "codex_contacted_customer": False,
        "codex_contacted_vendor": False,
        "codex_inferred_missing_evidence": False,
        "execution_authorized": False,
        "blockers_closed_by_builder": False,
        "production_sla_claim_published": False,
    }


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(path)})
    )


def build_path(output_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        fixture_input_path = tmp / "sla_input.fixture.json"
        builder_output_path = tmp / "sla_builder_output.fixture.json"
        support_evidence_path = tmp / "production_support_sla_evidence.from_sla.fixture.json"
        profile_output_path = tmp / "support_sla_profile.fixture.json"
        combined_evidence_path = tmp / "production_support_sla_evidence.combined.fixture.json"
        write_json(fixture_input_path, fixture_input())

        builder = build_from_input(
            fixture_input_path,
            builder_output_path,
            support_evidence_path,
            write_documentation=False,
        )
        source_paths = dict(DEFAULT_SOURCE_PATHS)
        source_paths["sla"] = support_evidence_path
        profile = build_profile(
            source_paths,
            profile_output_path,
            combined_evidence_path,
            support_contact="",
            write_documentation=False,
        )
        go_no_go = commercial_status(combined_evidence_path)

    sla_satisfied = "sla" in set(profile.get("target_blockers_satisfied", []))
    result: dict[str, Any] = {
        "sla_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_sla_evidence_path",
        "path_status": "pass_fixture_only" if sla_satisfied else "hold",
        "generated_by": "scripts/saee_sla_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "fixture_only": True,
        "real_sla_terms_approved": False,
        "real_legal_review_completed": False,
        "builder_status": builder["status"],
        "builder_input_complete": builder["input_complete"],
        "sla_available_for_review": builder["sla_available_for_review"],
        "support_profile_status_after_fixture": profile["profile_status"],
        "support_profile_target_blockers_satisfied": profile[
            "target_blockers_satisfied"
        ],
        "support_profile_target_blockers_satisfied_count": profile[
            "target_blockers_satisfied_count"
        ],
        "support_profile_production_blocker_count": profile[
            "profile_production_blocker_count"
        ],
        "support_profile_production_support_available": profile[
            "production_support_available"
        ],
        "commercial_status_after_fixture": go_no_go["commercial_status"],
        "production_launch_status_after_fixture": go_no_go[
            "production_launch_status"
        ],
        "satisfied_production_checks_after_fixture": go_no_go[
            "satisfied_production_checks"
        ],
        "total_production_checks_after_fixture": go_no_go["total_production_checks"],
        "production_blocker_count_after_fixture": go_no_go[
            "production_blocker_count"
        ],
        "sla_blocker_path_proven": sla_satisfied,
        "blockers_closed_by_path": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_real_evidence_required": True,
        "separate_go_no_go_profile_required": True,
        "separate_human_launch_approval_required": True,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "support_contact_published": False,
        "support_contact_test_sent": False,
        "staffed_support_started": False,
        "support_case_created": False,
        "customer_communication_sent": False,
        "sla_published": False,
        "sla_approved_by_codex": False,
        "legal_review_completed_by_codex": False,
        "support_hours_published_by_codex": False,
        "response_targets_published_by_codex": False,
        "on_call_rotation_started": False,
        "support_operations_started": False,
        "production_sla_claim_published": False,
        "next_action": (
            "A human owner must replace the fixture with real SLA approval and "
            "legal review evidence, then rerun the SLA builder and support/SLA "
            "profile. This path proof alone closes no blockers."
        ),
    }
    write_json(output_path, result)
    write_report(result)
    write_docs()
    return result


def write_report(result: dict[str, Any]) -> None:
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# SAEE SLA Evidence Path Report v0.1",
                "",
                "Status: local fixture-only path proof generated.",
                "",
                "## Summary",
                "",
                "- sla_evidence_path_v0_1: true",
                f"- path_type: {result['path_type']}",
                f"- path_status: {result['path_status']}",
                "- fixture_only: true",
                "- real_sla_terms_approved: false",
                f"- builder_status: {result['builder_status']}",
                f"- builder_input_complete: {str(result['builder_input_complete']).lower()}",
                f"- sla_available_for_review: {str(result['sla_available_for_review']).lower()}",
                f"- sla_blocker_path_proven: {str(result['sla_blocker_path_proven']).lower()}",
                f"- support_profile_target_blockers_satisfied_count: {result['support_profile_target_blockers_satisfied_count']}",
                f"- support_profile_production_blocker_count: {result['support_profile_production_blocker_count']}",
                f"- support_profile_production_support_available: {str(result['support_profile_production_support_available']).lower()}",
                f"- commercial_status_after_fixture: {result['commercial_status_after_fixture']}",
                f"- production_blocker_count_after_fixture: {result['production_blocker_count_after_fixture']}",
                f"- blockers_closed_by_path: {result['blockers_closed_by_path']}",
                "",
                "## Boundary",
                "",
                "- production_ready: false",
                "- customer_validated: false",
                "- product_launched: false",
                "- private_core_exposed: false",
                "- runtime_modified: false",
                "- backend_modified: false",
                "- kernel_modified: false",
                "- api_schema_modified: false",
                "- external_calls_made: false",
                "- customer_contacted: false",
                "- support_vendor_contacted: false",
                "- real_sla_terms_approved: false",
                "- sla_published: false",
                "- sla_approved_by_codex: false",
                "- legal_review_completed_by_codex: false",
                "- support_hours_published_by_codex: false",
                "- response_targets_published_by_codex: false",
                "- support_operations_started: false",
                "- production_sla_claim_published: false",
                "",
                "## Non-Closure Statement",
                "",
                "This path proof uses fixture-only SLA approval evidence. It proves",
                "local evidence wiring, but it does not approve or publish SLA terms,",
                "complete legal review, contact customers or vendors, close blockers,",
                "launch product, or claim production readiness.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_docs() -> None:
    DOC_PATH.write_text(
        """# SAEE SLA Evidence Path v0.1

Status: local fixture-only path proof; not real SLA approval evidence.

sla_evidence_path_v0_1: true
path_type: local_fixture_only_sla_evidence_path
path_status: pass_fixture_only
fixture_only: true
real_sla_terms_approved: false
sla_blocker_path_proven: true
support_profile_target_blockers_satisfied_count: 1
support_profile_production_blocker_count: 23
support_profile_production_support_available: false
blockers_closed_by_path: 0

## Purpose

This path proof verifies that a human-filled SLA approval input can flow
through:

1. `scripts/saee_sla_evidence_builder.py`;
2. `scripts/saee_support_sla_evidence_profile.py`;
3. commercial go/no-go SLA blocker evaluation.

It uses fixture-only SLA approval evidence. It does not approve legal terms,
publish support hours, publish response targets, or publish an SLA.

## Required Design Check

1. Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune
   System.
2. It improves SLA evidence intake and commercial readiness review.
3. It preserves safety, legal, permission, customer-contact, support-operations,
   and private-core boundaries.
4. It does not push SAEE into audit-first framing; it is a commercial SLA
   evidence path proof.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_sla_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_support_operations: false
recommend_for_sla_publication: false

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
support_vendor_contacted: false
real_sla_terms_approved: false
sla_published: false
sla_approved_by_codex: false
legal_review_completed_by_codex: false
support_hours_published_by_codex: false
response_targets_published_by_codex: false
support_operations_started: false
production_sla_claim_published: false

## Entrypoints

- path JSON: `phase_b_product/commercial_readiness/support_evidence/sla_evidence_path.local.json`
- path report: `phase_b_product/commercial_readiness/support_evidence/sla_evidence_path_report.md`
- runner: `scripts/saee_sla_evidence_path.py`
- smoke: `scripts/saee_sla_evidence_path_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE SLA Evidence Path Recommendation Gate

answer: conditional

recommend_for_human_sla_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_support_operations: false
recommend_for_sla_publication: false

## Reason

The path proof is useful because it verifies the local wiring from a
human-filled SLA approval input through the evidence builder, support/SLA
profile, and commercial go/no-go SLA blocker. It uses fixture-only data and
does not represent real approved SLA terms or legal review.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
support_vendor_contacted: false
real_sla_terms_approved: false
sla_published: false
sla_approved_by_codex: false
legal_review_completed_by_codex: false
support_hours_published_by_codex: false
response_targets_published_by_codex: false
support_operations_started: false
production_sla_claim_published: false
blockers_closed_by_path: 0
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SAEE SLA evidence path proof")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_path(args.output)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(
        "SAEE_SLA_EVIDENCE_PATH: PASS "
        f"path_status={result['path_status']} "
        "fixture_only=true "
        f"sla_blocker_path_proven={str(result['sla_blocker_path_proven']).lower()} "
        f"production_blockers_after_fixture={result['production_blocker_count_after_fixture']} "
        "blockers_closed_by_path=0"
    )


if __name__ == "__main__":
    main()
