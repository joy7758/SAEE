#!/usr/bin/env python3
"""Validate the fail-closed Baidu partner response tracker."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "agent-interface/ecosystem/saee-baidu-partner-response-tracker.v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BAIDU_PARTNER_RESPONSE_TRACKER_SMOKE: FAIL " + message)


def main() -> None:
    tracker = json.loads(TRACKER.read_text(encoding="utf-8"))
    receipt = json.loads((ROOT / tracker["submission_receipt_ref"]).read_text(encoding="utf-8"))
    response = tracker["response"]
    follow_up = tracker["follow_up"]
    boundary = tracker["truth_boundary"]

    require(receipt["truth_boundary"]["qianfan_partner_consultation_submitted"] is True, "source submission")
    require(tracker["status"] == "waiting_for_initial_baidu_response", "waiting status")
    require(response["received"] is False, "response state")
    for key in ("received_at", "channel", "source_reference", "redacted_summary", "baidu_decision"):
        require(response[key] is None, f"unproven response field {key}")
    require(follow_up["official_response_sla_published"] is False, "SLA claim")
    require(follow_up["due_at"] is None, "invented due date")
    require(follow_up["automated_follow_up_authorized"] is False, "follow-up authorization")
    require(follow_up["follow_up_sent"] is False, "follow-up send claim")
    transitions = {(item["from"], item["event"], item["to"]) for item in tracker["state_transition_contract"]}
    require(len(transitions) == 4, "transition count")
    require(("waiting_for_initial_baidu_response", "verified_baidu_response_received", "response_received_human_review_required") in transitions, "response transition")
    require(tracker["privacy"]["store_only_redacted_summary_and_source_reference"] is True, "privacy contract")
    for key in ("baidu_response_received", "baidu_partnership_approved", "official_qianfan_integration", "marketplace_submission", "marketplace_listed", "customer_validated", "production_ready"):
        require(boundary[key] is False, key)
    print(
        "SAEE_BAIDU_PARTNER_RESPONSE_TRACKER_SMOKE: PASS "
        "status=waiting_for_initial_baidu_response transitions=4 response_received=false "
        "follow_up_authorized=false marketplace_submission=false production_ready=false"
    )


if __name__ == "__main__":
    main()
