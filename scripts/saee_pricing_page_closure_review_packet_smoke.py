#!/usr/bin/env python3
"""Smoke test the pricing-page closure review packet."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_pricing_page_closure_review_packet.py"
BILLING_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
SUMMARY = BILLING_DIR / "pricing_page_closure_review_packet.local.json"
REPORT = BILLING_DIR / "pricing_page_closure_review_packet.md"
CSV = BILLING_DIR / "pricing_page_closure_review_packet.csv"
BOUNDARY = BILLING_DIR / "pricing_page_closure_review_packet_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRICING_PAGE_CLOSURE_REVIEW_PACKET_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRICING_PAGE_CLOSURE_REVIEW_PACKET_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_PRICING_PAGE_CLOSURE_REVIEW_PACKET_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic only
        fail(f"{path.relative_to(ROOT)} must be valid JSON: {exc}")
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_PRICING_PAGE_CLOSURE_REVIEW_PACKET: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, CSV, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "pricing_page_closure_review_packet_v0_1": True,
        "review_type": "local_pricing_page_closure_review_packet_no_publication_no_closure",
        "status": "ready_for_human_matrix_update_review_no_publication",
        "target_blocker_id": "pricing_page",
        "source_builder_status": "pass",
        "builder_ready": True,
        "pricing_page_evidence_complete_for_review": True,
        "pricing_page_required_key_count": 5,
        "pricing_page_complete_key_count": 5,
        "pricing_page_missing_key_count": 0,
        "ready_for_human_matrix_update_review": True,
        "separate_matrix_update_request_required": True,
        "separate_publication_approval_required": True,
        "separate_payment_enablement_approval_required": True,
        "recommended_human_decision": "approve_for_separate_matrix_update_request",
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
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")

    rows = payload.get("pricing_page_key_rows", [])
    require(len(rows) == 5, "must review five pricing-page keys")
    require(all(row.get("complete") is True for row in rows), "all pricing-page keys must be complete")
    require(all(row.get("value") is True for row in rows), "all pricing-page values must be true")
    non_publication = payload.get("non_publication_boundary", {})
    for key in [
        "pricing_page_available",
        "pricing_page_published",
        "customer_facing_pricing_page_created",
        "checkout_enabled",
        "customer_payment_collected",
        "revenue_validated",
    ]:
        require(non_publication.get(key) is False, f"non_publication_boundary {key} must be false")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "pricing_page_closure_review_packet_v0_1: true",
        "ready_for_human_matrix_update_review_no_publication",
        "pricing_page_published=false",
        "checkout_enabled=false",
        "customer_payment_collected=false",
        "revenue_validated=false",
        "blocker_closure_authorized=false",
        "blockers_closed_by_packet=0",
        "answer: ready_for_human_matrix_update_review_no_publication",
    ]:
        require(token in combined, f"docs missing token: {token}")
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "pricing_page_published=true",
        "checkout_enabled=true",
        "customer_payment_collected=true",
        "revenue_validated=true",
        "blockers_closed_by_packet=1",
        "blocker_closure_authorized=true",
        "development_permission_granted=true",
        "execution_authorized=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/PRICING_PAGE_CLOSURE_REVIEW_PACKET_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.csv",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet_boundary_audit.md",
        "/docs/strategy/SAEE_PRICING_PAGE_CLOSURE_REVIEW_PACKET_GATE.md",
        "/scripts/saee_pricing_page_closure_review_packet.py",
        "/scripts/saee_pricing_page_closure_review_packet_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    agent_index = read_json(ROOT / "agent-index.json")
    entry = agent_index.get("pricing_page_closure_review_packet_v0_1")
    require(isinstance(entry, dict), "agent-index missing entry")
    for key in [
        "status",
        "target_blocker_id",
        "pricing_page_evidence_complete_for_review",
        "ready_for_human_matrix_update_review",
        "recommended_human_decision",
        "separate_matrix_update_request_required",
        "separate_publication_approval_required",
        "pricing_page_published_by_codex",
        "pricing_page_published",
        "checkout_enabled",
        "customer_payment_collected",
        "revenue_validated",
        "blocker_closure_authorized",
        "blockers_closed_by_packet",
        "canonical_gap_matrix_modified",
        "customer_validated",
        "production_ready",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")
    require(entry.get("make_target") == "make check-pricing-page-closure-review-packet", "make target mismatch")

    status_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Pricing Page Closure Review Packet v0.1",
        "pricing_page_closure_review_packet_v0_1",
        "ready_for_human_matrix_update_review_no_publication",
        "pricing_page_evidence_complete_for_review=true",
        "ready_for_human_matrix_update_review=true",
        "pricing_page_published=false",
        "checkout_enabled=false",
        "blockers_closed_by_packet=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print("SAEE_PRICING_PAGE_CLOSURE_REVIEW_PACKET_SMOKE: PASS")


if __name__ == "__main__":
    main()
