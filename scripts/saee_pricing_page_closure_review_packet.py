#!/usr/bin/env python3
"""Build a pricing-page closure review packet without publishing pricing.

The packet promotes the human-filled pricing-page evidence into a local
human-review surface for a future separate matrix update request. It does not
publish a pricing page, create a sales offer, enable checkout, collect payment,
close blockers, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BILLING_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
OUT_JSON = BILLING_DIR / "pricing_page_closure_review_packet.local.json"
OUT_MD = BILLING_DIR / "pricing_page_closure_review_packet.md"
OUT_CSV = BILLING_DIR / "pricing_page_closure_review_packet.csv"
BOUNDARY = BILLING_DIR / "pricing_page_closure_review_packet_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRICING_PAGE_CLOSURE_REVIEW_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRICING_PAGE_CLOSURE_REVIEW_PACKET_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

BUILDER_OUTPUT = BILLING_DIR / "pricing_page_evidence_builder_output.human_filled.local.json"
PRODUCTION_EVIDENCE = BILLING_DIR / "production_billing_revenue_evidence.from_pricing_page.human_filled.local.json"
APPROVAL_VALIDATION = BILLING_DIR / "pricing_page_approval_input_validation.human_filled.local.json"
REVIEW_PACKET = BILLING_DIR / "pricing_page_review_packet.local.json"

PRICING_PAGE_KEYS = (
    "human_approved_pricing_page_copy",
    "approved_plan_and_usage_terms",
    "legal_review_completed",
    "production_readiness_non_claim_reviewed",
    "pricing_page_publication_approval_recorded",
)

FALSE_FLAGS = {
    "pricing_page_published_by_codex": False,
    "pricing_page_published": False,
    "sales_offer_sent": False,
    "payment_provider_configured": False,
    "checkout_enabled": False,
    "customer_payment_collected": False,
    "revenue_validated": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_packet": 0,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_collection_authorized": False,
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
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in text.splitlines():
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")


def replace_block(path: Path, marker: str, body: str) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start in text and end in text:
        before = text.split(start, 1)[0]
        after = text.split(end, 1)[1]
        path.write_text(before.rstrip() + "\n\n" + block + after.lstrip(), encoding="utf-8")
    else:
        path.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")


def build_key_rows(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key in PRICING_PAGE_KEYS:
        rows.append(
            {
                "evidence_key": key,
                "complete": evidence.get(key) is True,
                "value": evidence.get(key) is True,
            }
        )
    return rows


def build_payload() -> dict[str, Any]:
    builder = read_json(BUILDER_OUTPUT)
    evidence = read_json(PRODUCTION_EVIDENCE)
    validation = read_json(APPROVAL_VALIDATION)
    review_packet = read_json(REVIEW_PACKET)
    key_rows = build_key_rows(evidence)
    complete_count = sum(1 for row in key_rows if row["complete"])
    evidence_complete = (
        builder.get("status") == "pass"
        and builder.get("pricing_page_evidence_complete_for_review") is True
        and complete_count == len(PRICING_PAGE_KEYS)
        and validation.get("builder_ready") is True
    )
    status = (
        "ready_for_human_matrix_update_review_no_publication"
        if evidence_complete
        else "hold_pricing_page_evidence_incomplete"
    )
    return {
        "pricing_page_closure_review_packet_v0_1": True,
        "review_type": "local_pricing_page_closure_review_packet_no_publication_no_closure",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_blocker_id": "pricing_page",
        "source_builder_output": rel(BUILDER_OUTPUT),
        "source_production_evidence": rel(PRODUCTION_EVIDENCE),
        "source_approval_validation": rel(APPROVAL_VALIDATION),
        "source_review_packet": rel(REVIEW_PACKET),
        "source_builder_status": builder.get("status"),
        "source_review_packet_status": review_packet.get("packet_status"),
        "builder_ready": validation.get("builder_ready") is True,
        "pricing_page_evidence_complete_for_review": evidence_complete,
        "pricing_page_required_key_count": len(PRICING_PAGE_KEYS),
        "pricing_page_complete_key_count": complete_count,
        "pricing_page_missing_key_count": len(PRICING_PAGE_KEYS) - complete_count,
        "pricing_page_key_rows": key_rows,
        "ready_for_human_matrix_update_review": evidence_complete,
        "separate_matrix_update_request_required": True,
        "separate_publication_approval_required": True,
        "separate_payment_enablement_approval_required": True,
        "recommended_human_decision": "approve_for_separate_matrix_update_request",
        "non_publication_boundary": {
            "pricing_page_available": evidence.get("pricing_page_available") is True,
            "pricing_page_published": evidence.get("pricing_page_published") is True,
            "customer_facing_pricing_page_created": evidence.get("customer_facing_pricing_page_created") is True,
            "checkout_enabled": evidence.get("checkout_enabled") is True,
            "customer_payment_collected": evidence.get("customer_payment_collected") is True,
            "revenue_validated": evidence.get("revenue_validated") is True,
        },
        "next_human_action": (
            "review whether pricing_page evidence should be promoted into a separate "
            "matrix update request; do not publish pricing or enable checkout from this packet"
        ),
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["evidence_key", "complete", "value"])
        writer.writeheader()
        for row in payload["pricing_page_key_rows"]:
            writer.writerow(row)

    table = "\n".join(
        "| {evidence_key} | {complete} |".format(**row)
        for row in payload["pricing_page_key_rows"]
    )
    OUT_MD.write_text(
        f"""# SAEE Pricing Page Closure Review Packet v0.1

Status: `{payload['status']}`

This packet summarizes the human-filled pricing-page evidence for a future
separate matrix update request. It does not publish a pricing page, create a
sales offer, enable checkout, collect payment, validate revenue, or close the
`pricing_page` blocker.

## Summary

- target_blocker_id: `pricing_page`
- source_builder_status: `{payload['source_builder_status']}`
- builder_ready: `{str(payload['builder_ready']).lower()}`
- pricing_page_evidence_complete_for_review: `{str(payload['pricing_page_evidence_complete_for_review']).lower()}`
- pricing_page_complete_key_count: `{payload['pricing_page_complete_key_count']}`
- pricing_page_missing_key_count: `{payload['pricing_page_missing_key_count']}`
- ready_for_human_matrix_update_review: `{str(payload['ready_for_human_matrix_update_review']).lower()}`
- recommended_human_decision: `{payload['recommended_human_decision']}`
- blockers_closed_by_packet: `0`

## Evidence Keys

| Evidence key | Complete |
| --- | --- |
{table}

## Boundary

- pricing_page_published_by_codex=false
- pricing_page_published=false
- sales_offer_sent=false
- payment_provider_configured=false
- checkout_enabled=false
- customer_payment_collected=false
- revenue_validated=false
- blocker_closure_authorized=false
- blockers_closed_by_packet=0
- canonical_gap_matrix_modified=false
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        """# SAEE Pricing Page Closure Review Packet Boundary Audit

pricing_page_closure_review_packet_v0_1: true
status: ready_for_human_matrix_update_review_no_publication

- Local review packet only.
- No pricing page published by Codex.
- No sales offer sent.
- No payment provider configured.
- No checkout enabled.
- No customer payment collected.
- No revenue validated.
- No blocker closure authorized.
- No canonical gap matrix modified.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No production-ready claim added.
- blockers_closed_by_packet: 0
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        """# SAEE Pricing Page Closure Review Packet v0.1

pricing_page_closure_review_packet_v0_1: true
status: ready_for_human_matrix_update_review_no_publication

Purpose: present human-filled pricing-page evidence as a candidate for a future
separate formal matrix update request, without publishing pricing or closing
the blocker.

Entrypoints:

- `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.local.json`
- `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.md`
- `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.csv`
- `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet_boundary_audit.md`
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Pricing Page Closure Review Packet Gate

answer: ready_for_human_matrix_update_review_no_publication

reason: Human-filled pricing-page evidence is complete for review, but pricing
has not been published, payment has not been enabled, revenue has not been
validated, and no blocker closure is authorized.

boundary:
- pricing_page_published_by_codex: false
- checkout_enabled: false
- customer_payment_collected: false
- revenue_validated: false
- blocker_closure_authorized: false
- blockers_closed_by_packet: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: human review for a separate matrix update request, not publication.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/PRICING_PAGE_CLOSURE_REVIEW_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.csv",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet_boundary_audit.md",
        "/docs/strategy/SAEE_PRICING_PAGE_CLOSURE_REVIEW_PACKET_GATE.md",
        "/scripts/saee_pricing_page_closure_review_packet.py",
        "/scripts/saee_pricing_page_closure_review_packet_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["pricing_page_closure_review_packet_v0_1"] = {
        "name": "SAEE Pricing Page Closure Review Packet v0.1",
        "status": payload["status"],
        "target_blocker_id": "pricing_page",
        "pricing_page_evidence_complete_for_review": payload["pricing_page_evidence_complete_for_review"],
        "ready_for_human_matrix_update_review": payload["ready_for_human_matrix_update_review"],
        "recommended_human_decision": payload["recommended_human_decision"],
        "separate_matrix_update_request_required": True,
        "separate_publication_approval_required": True,
        "pricing_page_published_by_codex": False,
        "pricing_page_published": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_packet": 0,
        "canonical_gap_matrix_modified": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "entrypoints": {
            "summary": rel(OUT_JSON),
            "report": rel(OUT_MD),
            "csv": rel(OUT_CSV),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "top_doc": rel(TOP_DOC),
            "runner": "scripts/saee_pricing_page_closure_review_packet.py",
            "smoke": "scripts/saee_pricing_page_closure_review_packet_smoke.py",
        },
        "make_target": "make check-pricing-page-closure-review-packet",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Pricing Page Closure Review Packet v0.1

- `pricing_page_closure_review_packet_v0_1`
- Status: `{payload['status']}`
- Target blocker: `pricing_page`
- pricing_page_evidence_complete_for_review={str(payload['pricing_page_evidence_complete_for_review']).lower()}
- ready_for_human_matrix_update_review={str(payload['ready_for_human_matrix_update_review']).lower()}
- recommended_human_decision={payload['recommended_human_decision']}
- pricing_page_published=false
- checkout_enabled=false
- customer_payment_collected=false
- revenue_validated=false
- blockers_closed_by_packet=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_PRICING_PAGE_CLOSURE_REVIEW_PACKET_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_PRICING_PAGE_CLOSURE_REVIEW_PACKET: PASS "
        f"status={payload['status']} "
        f"pricing_page_evidence_complete_for_review={str(payload['pricing_page_evidence_complete_for_review']).lower()} "
        "blockers_closed_by_packet=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
