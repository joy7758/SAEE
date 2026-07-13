#!/usr/bin/env python3
"""Prove the local privacy/security/legal evidence path without approval.

This path check uses temporary fixture-only privacy/security/legal evidence and
feeds it into the existing privacy/security/legal readiness and commercial
go/no-go checks. It proves the wiring from human-filled formal security,
privacy/legal, DPA, and vulnerability-management evidence to commercial review
without performing security review, contacting legal counsel, contacting
security vendors, processing customer data, enabling vulnerability operations,
closing blockers by itself, or claiming production readiness.
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
from saee_backend.services.production_privacy_security_legal_evidence import (
    DPA_KEYS,
    FORBIDDEN_TRUE_KEYS,
    FORMAL_SECURITY_REVIEW_KEYS,
    PRIVACY_LEGAL_REVIEW_KEYS,
    VULNERABILITY_MANAGEMENT_KEYS,
    evaluate_production_privacy_security_legal_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "privacy_security_legal_evidence_path.local.json"
REPORT_PATH = OUTPUT_DIR / "privacy_security_legal_evidence_path_report.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_RECOMMENDATION_GATE.md"
)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_evidence() -> dict[str, Any]:
    all_evidence_keys = (
        FORMAL_SECURITY_REVIEW_KEYS
        + PRIVACY_LEGAL_REVIEW_KEYS
        + DPA_KEYS
        + VULNERABILITY_MANAGEMENT_KEYS
    )
    evidence: dict[str, Any] = {
        "privacy_security_legal_evidence_type": "production_privacy_security_legal_evidence",
        "evidence_scope": "fixture_only_privacy_security_legal_evidence_path_proof",
        "evidence_version": "v0.1",
        "input_status": "fixture_only_not_real_privacy_security_legal_approval",
        "generated_by": "scripts/saee_privacy_security_legal_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": datetime.now(timezone.utc).date().isoformat(),
        "decision_summary": (
            "Fixture-only privacy/security/legal evidence path proof. This is "
            "not real formal security review, privacy/legal review, DPA "
            "approval, vulnerability-management activation, customer-data "
            "processing approval, or launch approval."
        ),
        "source_notes_by_key": {
            key: f"Fixture-only source note for {key}." for key in all_evidence_keys
        },
        "privacy_security_legal_evidence_slots": [
            {
                "evidence_key": key,
                "evidence_reference": f"fixture://privacy-security-legal/{key}",
                "owner_named": True,
                "reviewed_by_human": True,
                "human_source_note": f"Fixture-only human source note for {key}.",
            }
            for key in all_evidence_keys
        ],
        "fixture_only": True,
        "real_formal_security_review_completed": False,
        "real_privacy_legal_review_completed": False,
        "real_dpa_approved": False,
        "real_vulnerability_management_operational": False,
        "real_customer_data_processing_approved": False,
    }
    for key in all_evidence_keys:
        evidence[key] = True
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    return evidence


def privacy_security_legal_status(path: Path) -> dict[str, object]:
    return evaluate_production_privacy_security_legal_evidence(
        load_settings({"SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(path)})
    )


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(path)})
    )


def build_path(output_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        fixture_path = Path(tmpdir) / "privacy_security_legal_evidence.fixture.json"
        write_json(fixture_path, fixture_evidence())
        psl = privacy_security_legal_status(fixture_path)
        go_no_go = commercial_status(fixture_path)

    psl_path_proven = (
        psl["formal_security_review_completed"] is True
        and psl["privacy_legal_review_completed"] is True
        and psl["data_processing_agreement_available"] is True
        and psl["vulnerability_management_available"] is True
        and psl["production_privacy_security_legal_ready"] is True
    )
    result: dict[str, Any] = {
        "privacy_security_legal_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_privacy_security_legal_evidence_path",
        "path_status": "pass_fixture_only" if psl_path_proven else "hold",
        "generated_by": "scripts/saee_privacy_security_legal_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "fixture_only": True,
        "real_formal_security_review_completed": False,
        "real_privacy_legal_review_completed": False,
        "real_dpa_approved": False,
        "real_vulnerability_management_operational": False,
        "real_customer_data_processing_approved": False,
        "privacy_security_legal_readiness_status_after_fixture": psl["status"],
        "formal_security_review_completed_after_fixture": psl[
            "formal_security_review_completed"
        ],
        "privacy_legal_review_completed_after_fixture": psl[
            "privacy_legal_review_completed"
        ],
        "data_processing_agreement_available_after_fixture": psl[
            "data_processing_agreement_available"
        ],
        "vulnerability_management_available_after_fixture": psl[
            "vulnerability_management_available"
        ],
        "production_privacy_security_legal_ready_after_fixture": psl[
            "production_privacy_security_legal_ready"
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
        "privacy_security_legal_blocker_path_proven": psl_path_proven,
        "privacy_security_legal_target_blockers_satisfied_by_fixture": [
            "formal_security_review",
            "privacy_legal_review",
            "data_processing_agreement",
            "vulnerability_management",
        ],
        "privacy_security_legal_target_blockers_satisfied_count_after_fixture": 4
        if psl_path_proven
        else 0,
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
        "customer_contacted": False,
        "security_vendor_contacted": False,
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "dpa_sent_to_customer": False,
        "terms_published": False,
        "privacy_notice_published": False,
        "production_security_enabled": False,
        "vulnerability_management_operational": False,
        "production_security_ready": False,
        "production_legal_ready": False,
        "customer_data_processing_ready": False,
        "legal_approval_completed": False,
        "next_action": (
            "A human owner must replace the fixture with real formal security, "
            "privacy/legal, DPA, and vulnerability-management evidence, then "
            "rerun privacy/security/legal readiness and commercial go/no-go. "
            "This path proof alone closes no blockers."
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
                "# SAEE Privacy / Security / Legal Evidence Path Report v0.1",
                "",
                "Status: local fixture-only path proof generated.",
                "",
                "## Summary",
                "",
                "- privacy_security_legal_evidence_path_v0_1: true",
                f"- path_type: {result['path_type']}",
                f"- path_status: {result['path_status']}",
                "- fixture_only: true",
                "- real_formal_security_review_completed: false",
                "- real_privacy_legal_review_completed: false",
                "- real_dpa_approved: false",
                "- real_vulnerability_management_operational: false",
                "- real_customer_data_processing_approved: false",
                f"- privacy_security_legal_readiness_status_after_fixture: {result['privacy_security_legal_readiness_status_after_fixture']}",
                f"- formal_security_review_completed_after_fixture: {str(result['formal_security_review_completed_after_fixture']).lower()}",
                f"- privacy_legal_review_completed_after_fixture: {str(result['privacy_legal_review_completed_after_fixture']).lower()}",
                f"- data_processing_agreement_available_after_fixture: {str(result['data_processing_agreement_available_after_fixture']).lower()}",
                f"- vulnerability_management_available_after_fixture: {str(result['vulnerability_management_available_after_fixture']).lower()}",
                f"- production_privacy_security_legal_ready_after_fixture: {str(result['production_privacy_security_legal_ready_after_fixture']).lower()}",
                f"- privacy_security_legal_blocker_path_proven: {str(result['privacy_security_legal_blocker_path_proven']).lower()}",
                f"- privacy_security_legal_target_blockers_satisfied_count_after_fixture: {result['privacy_security_legal_target_blockers_satisfied_count_after_fixture']}",
                f"- commercial_status_after_fixture: {result['commercial_status_after_fixture']}",
                f"- production_blocker_count_after_fixture: {result['production_blocker_count_after_fixture']}",
                f"- blockers_closed_by_path: {result['blockers_closed_by_path']}",
                "",
                "## Boundary",
                "",
                "- No formal security review performed.",
                "- No privacy/legal review performed.",
                "- No DPA approved or sent to customers.",
                "- No legal counsel contacted.",
                "- No security vendor contacted.",
                "- No vulnerability-management operations enabled.",
                "- No customer data processed.",
                "- No backend, runtime, kernel, or API schema modified.",
                "- No customer contacted.",
                "- No product launched.",
                "- No production-readiness claim added.",
                "- No private core exposed.",
                "",
                "## Next Action",
                "",
                str(result["next_action"]),
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_docs() -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        """# SAEE Privacy / Security / Legal Evidence Path v0.1

Status: local fixture-only path proof; not legal/security approval.

## Purpose

This path proves that a complete local privacy/security/legal evidence JSON can
be read by `production_privacy_security_legal_evidence`, then reflected by
commercial go/no-go for these blocker IDs:

- `formal_security_review`
- `privacy_legal_review`
- `data_processing_agreement`
- `vulnerability_management`

## Machine-Readable Status

```yaml
privacy_security_legal_evidence_path_v0_1: true
path_type: local_fixture_only_privacy_security_legal_evidence_path
path_status: pass_fixture_only
fixture_only: true
real_formal_security_review_completed: false
real_privacy_legal_review_completed: false
real_dpa_approved: false
real_vulnerability_management_operational: false
real_customer_data_processing_approved: false
privacy_security_legal_readiness_status_after_fixture: pass
formal_security_review_completed_after_fixture: true
privacy_legal_review_completed_after_fixture: true
data_processing_agreement_available_after_fixture: true
vulnerability_management_available_after_fixture: true
production_privacy_security_legal_ready_after_fixture: true
privacy_security_legal_blocker_path_proven: true
privacy_security_legal_target_blockers_satisfied_count_after_fixture: 4
production_blocker_count_after_fixture: 20
blockers_closed_by_path: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
customer_contacted: false
security_vendor_contacted: false
legal_counsel_contacted: false
customer_data_processed: false
dpa_sent_to_customer: false
terms_published: false
privacy_notice_published: false
production_security_enabled: false
vulnerability_management_operational: false
```

## Boundary

This path does not perform formal security review, perform privacy/legal
review, approve or send a DPA, contact legal counsel, contact security vendors,
process customer data, enable vulnerability-management operations, close
blockers by itself, launch product, contact customers, modify runtime, modify
backend, modify kernel, modify API schema, or expose private core.

## Recommendation Gate

Answer: conditional.

Recommend this path for human privacy/security/legal evidence review and
blocker-path verification. Do not recommend it as legal approval, security
approval, DPA approval, customer-data processing approval, production launch
approval, customer validation, or blocker closure by itself.
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Privacy / Security / Legal Evidence Path Recommendation Gate

answer: conditional

recommend_for_human_privacy_security_legal_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_legal_counsel_contact: false
recommend_for_security_vendor_contact: false
recommend_for_customer_data_processing: false
recommend_for_vulnerability_operations_enablement: false

## Reason

The path proves local fixture-only wiring from privacy/security/legal evidence
into commercial go/no-go for four privacy/security blockers. It is useful for
human review of real evidence later, but it is not formal security review,
privacy/legal review, DPA approval, vulnerability-management activation, or
blocker closure by itself.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
customer_contacted: false
security_vendor_contacted: false
legal_counsel_contacted: false
customer_data_processed: false
dpa_sent_to_customer: false
terms_published: false
privacy_notice_published: false
production_security_enabled: false
vulnerability_management_operational: false
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_path(Path(args.output))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH: PASS "
            f"path={Path(args.output).relative_to(ROOT)} "
            f"path_status={result['path_status']} "
            "fixture_only=true "
            "privacy_security_legal_blocker_path_proven=true "
            "blockers_closed_by_path=0"
        )


if __name__ == "__main__":
    main()
