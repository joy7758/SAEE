#!/usr/bin/env python3
"""Negative and integration tests for the Baidu qualification evidence intake."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "agent-interface/ecosystem/saee-baidu-marketplace-qualification-evidence-intake.schema.v1.json"
TEMPLATE = ROOT / "agent-interface/ecosystem/saee-baidu-marketplace-qualification-evidence-intake.template.v1.json"
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from saee_baidu_marketplace_qualification_evidence_intake_validator import validate


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BAIDU_MARKETPLACE_QUALIFICATION_EVIDENCE_INTAKE_SMOKE: FAIL " + message)


def main() -> None:
    schema = load(SCHEMA)
    template = load(TEMPLATE)
    Draft202012Validator.check_schema(schema)
    require(validate(template) == [], "valid template")
    slots = template["evidence_slots"]
    require(len(slots) == 7, "slot count")
    require(template["aggregate"] == {"criterion_count": 7, "reference_present_count": 1, "not_provided_count": 6, "provider_accepted_count": 0}, "aggregate")
    negatives: list[dict] = []
    phone_like = "owner-held://certificate/" + "138" + "0013" + "8000"
    email_like = "owner-held://certificate/" + "person" + "@" + "example.com"
    for reference in (phone_like, email_like, "/Users/example/private.pdf", "https://example.invalid/private.pdf"):
        value = copy.deepcopy(template)
        value["evidence_slots"]["software_copyright_certificate"]["evidence_references"] = [reference]
        value["evidence_slots"]["software_copyright_certificate"]["intake_status"] = "reference_provided_for_review"
        negatives.append(value)
    empty = copy.deepcopy(template)
    empty["evidence_slots"]["company_qualification"]["evidence_references"] = []
    negatives.append(empty)
    missing = copy.deepcopy(template)
    missing["evidence_slots"]["company_qualification"]["evidence_references"] = ["repo://missing-evidence.json"]
    negatives.append(missing)
    accepted = copy.deepcopy(template)
    accepted["evidence_slots"]["company_qualification"]["provider_accepted"] = True
    negatives.append(accepted)
    aggregate = copy.deepcopy(template)
    aggregate["aggregate"]["reference_present_count"] = 2
    negatives.append(aggregate)
    for index, payload in enumerate(negatives, start=1):
        require(bool(validate(payload)), f"negative {index} accepted")
    require(all(slot["provider_accepted"] is False for slot in slots.values()), "provider acceptance boundary")
    require(template["truth_boundary"]["qualification_updated_by_intake"] is False, "qualification update boundary")
    print(
        "SAEE_BAIDU_MARKETPLACE_QUALIFICATION_EVIDENCE_INTAKE_SMOKE: PASS "
        "slots=7 references=1 negatives=8 raw_evidence=false personal_data=false "
        "provider_accepted=false qualification_updated=false marketplace_submission=false"
    )


if __name__ == "__main__":
    main()
