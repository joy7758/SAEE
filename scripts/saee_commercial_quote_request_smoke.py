#!/usr/bin/env python3
"""Fail-closed smoke for the agent quote request contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from saee_commercial_quote_request_validator import validate_request

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "agent-interface/examples/commercial-quote-request.json"
SCHEMA = ROOT / "agent-interface/schemas/commercial-quote-request.schema.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_QUOTE_REQUEST_SMOKE: FAIL " + message)


def main() -> None:
    request = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    require(schema["additionalProperties"] is False, "unknown fields rejected")
    require(validate_request(request) == [], "valid request")
    priced = copy.deepcopy(request)
    priced["price"] = "99-499 USD/month"
    require(validate_request(priced), "price field rejected")
    paid = copy.deepcopy(request)
    paid["boundaries"]["payment"] = True
    require(validate_request(paid), "payment boundary rejected")
    mismatch = copy.deepcopy(request)
    mismatch["package_id"] = "pro_team_review"
    require(validate_request(mismatch), "package/scope mismatch rejected")
    print("SAEE_COMMERCIAL_QUOTE_REQUEST_SMOKE: PASS valid=true price_rejected=true payment_rejected=true mismatch_rejected=true quote_status=owner_pricing_review_required public_price_points_approved=false blockers_closed=0")


if __name__ == "__main__":
    main()
