#!/usr/bin/env python3
"""Validate a no-price, no-payment agent quote request."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "agent-interface/schemas/commercial-quote-request.schema.json"
EXAMPLE = ROOT / "agent-interface/examples/commercial-quote-request.json"

FORBIDDEN_KEYS = {"amount", "bank", "card", "currency", "customer_email", "email", "invoice", "price", "sales_offer", "secret", "token", "url"}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def forbidden(value: Any, found: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                found.append(str(key))
            forbidden(child, found)
    elif isinstance(value, list):
        for child in value:
            forbidden(child, found)


def validate_request(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["request must be an object"]
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(data)]
    found: list[str] = []
    forbidden(data, found)
    if found:
        errors.append("forbidden quote fields: " + ", ".join(sorted(set(found))))
    if isinstance(data.get("package_id"), str) and isinstance(data.get("evaluation_scope"), str):
        expected = {"controlled_preview": "controlled_preview", "pro_team_review": "team_review", "enterprise_private_review": "enterprise_private_review"}[data["package_id"]] if data["package_id"] in {"controlled_preview", "pro_team_review", "enterprise_private_review"} else None
        if expected and data["evaluation_scope"] != expected:
            errors.append("evaluation_scope does not match package_id")
    for key, value in (data.get("boundaries") or {}).items():
        if value is not False:
            errors.append(f"boundary must remain false: {key}")
    return sorted(set(errors))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(EXAMPLE))
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"request_valid": False, "errors": [str(exc)]}, ensure_ascii=False))
        raise SystemExit(2) from exc
    errors = validate_request(data)
    result = {
        "contract_id": "saee-commercial-quote-response-v0.1",
        "request_valid": not errors,
        "request_sha256": hashlib.sha256(canonical(data).encode("utf-8")).hexdigest(),
        "quote_status": "owner_pricing_review_required",
        "public_price_points_approved": False,
        "payment_enabled": False,
        "customer_contacted": False,
        "production_ready": False,
        "blockers_closed": 0,
        "errors": errors,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif errors:
        print("SAEE_COMMERCIAL_QUOTE_REQUEST_VALIDATOR: FAIL " + " | ".join(errors))
    else:
        print("SAEE_COMMERCIAL_QUOTE_REQUEST_VALIDATOR: PASS request_valid=true quote_status=owner_pricing_review_required payment_enabled=false blockers_closed=0")
    raise SystemExit(0 if not errors else 2)


if __name__ == "__main__":
    main()
