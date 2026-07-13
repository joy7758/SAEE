#!/usr/bin/env python3
"""Fail-closed validator for sanitized Baidu qualification evidence references."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "agent-interface/ecosystem/saee-baidu-marketplace-qualification-evidence-intake.schema.v1.json"
TEMPLATE = ROOT / "agent-interface/ecosystem/saee-baidu-marketplace-qualification-evidence-intake.template.v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(payload: dict) -> list[str]:
    schema = load(SCHEMA)
    errors = ["SCHEMA_INVALID" for _ in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload)]
    if errors:
        return errors
    slots = payload["evidence_slots"]
    for slot in slots.values():
        references = slot["evidence_references"]
        if slot["intake_status"] == "not_provided" and references:
            errors.append("NOT_PROVIDED_HAS_REFERENCE")
        if slot["intake_status"] != "not_provided" and not references:
            errors.append("REFERENCE_STATUS_HAS_NO_REFERENCE")
        if slot["intake_status"] == "not_provided" and (slot["evidence_date"] is not None or slot["owner_reviewed"]):
            errors.append("NOT_PROVIDED_METADATA_PRESENT")
        for reference in references:
            if reference.startswith("repo://"):
                relative = reference.removeprefix("repo://")
                target = (ROOT / relative).resolve()
                try:
                    target.relative_to(ROOT)
                except ValueError:
                    errors.append("REPO_REFERENCE_ESCAPES_ROOT")
                    continue
                if not target.is_file():
                    errors.append("REPO_REFERENCE_MISSING")
    reference_present = sum(slot["intake_status"] != "not_provided" for slot in slots.values())
    not_provided = sum(slot["intake_status"] == "not_provided" for slot in slots.values())
    aggregate = payload["aggregate"]
    if aggregate["reference_present_count"] != reference_present or aggregate["not_provided_count"] != not_provided:
        errors.append("AGGREGATE_DRIFT")
    serialized = json.dumps(payload, ensure_ascii=False)
    if re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", serialized):
        errors.append("PHONE_VALUE_PRESENT")
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", serialized):
        errors.append("EMAIL_VALUE_PRESENT")
    if re.search(r"(?<!\d)\d{17}[0-9Xx](?!\d)", serialized):
        errors.append("IDENTITY_VALUE_PRESENT")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate sanitized Baidu Marketplace qualification evidence references")
    parser.add_argument("--input", type=Path, default=TEMPLATE)
    args = parser.parse_args()
    errors = validate(load(args.input))
    print(json.dumps({
        "status": "valid" if not errors else "invalid",
        "error_codes": errors,
        "qualification_updated": False,
        "marketplace_submission": False,
        "provider_qualification_accepted": False,
    }, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
