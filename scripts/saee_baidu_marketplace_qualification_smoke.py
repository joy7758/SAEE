#!/usr/bin/env python3
"""Validate the sanitized Baidu Marketplace qualification decision surface."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "agent-interface/ecosystem/saee-baidu-marketplace-qualification-matrix.v1.json"
PREFLIGHT = ROOT / "agent-interface/ecosystem/saee-baidu-official-entry-preflight.v1.json"
PLAN = ROOT / "agent-interface/ecosystem/saee-baidu-cloud-marketplace-entry-plan.v1.0.json"
GATE = ROOT / "docs/strategy/SAEE_BAIDU_MARKETPLACE_QUALIFICATION_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BAIDU_MARKETPLACE_QUALIFICATION_SMOKE: FAIL " + message)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    matrix = load(MATRIX)
    preflight = load(PREFLIGHT)
    plan = load(PLAN)
    gate = GATE.read_text(encoding="utf-8")
    criteria = {item["criterion_id"]: item for item in matrix["criteria"]}
    expected = {
        "company_qualification",
        "technical_and_support_team_at_least_10",
        "industry_service_experience_at_least_2_years",
        "online_support_at_least_5x8",
        "software_copyright_certificate",
        "dedicated_enterprise_verified_baidu_cloud_account",
        "marketplace_agreement_acceptance",
    }
    require(set(criteria) == expected, "criterion set")
    aggregate = matrix["aggregate"]
    require(aggregate == {
        "criterion_count": 7,
        "verified_count": 0,
        "partial_count": 1,
        "missing_count": 6,
        "qualification_complete": False,
    }, "aggregate")
    require(criteria["company_qualification"]["state"].startswith("partial_"), "company qualification boundary")
    require("age alone" in criteria["industry_service_experience_at_least_2_years"]["non_substitution"].lower(), "service evidence substitution")
    require("not staffed 5x8" in criteria["online_support_at_least_5x8"]["non_substitution"], "support substitution")
    require(matrix["decision"] == "do_not_recommend_currently", "decision")
    require(matrix["recommendation_gate_ref"] == str(GATE.relative_to(ROOT)), "gate discovery")
    require(matrix["truth_boundary"]["public_release_allowlist_included"] is False, "release allowlist boundary")
    for key in ("provider_qualification_accepted", "direct_marketplace_application_recommended", "marketplace_submission", "marketplace_listed", "customer_validated", "production_ready"):
        require(matrix["truth_boundary"][key] is False, key)
    require(preflight["qualification_matrix_ref"] == str(MATRIX.relative_to(ROOT)), "preflight discovery")
    require(plan["direct_marketplace_qualification"]["matrix_ref"] == str(MATRIX.relative_to(ROOT)), "plan discovery")
    require("answer: do_not_recommend" in gate and "audit_first_reframe=false" in gate, "recommendation gate")
    serialized = MATRIX.read_text(encoding="utf-8")
    require(re.search(r"(?<!\d)1[3-9]\d{9}(?!\d)", serialized) is None, "phone stored")
    require(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", serialized) is None, "email stored")
    require(re.search(r"(?<!\d)\d{17}[0-9Xx](?!\d)", serialized) is None, "identity number stored")
    print(
        "SAEE_BAIDU_MARKETPLACE_QUALIFICATION_SMOKE: PASS criteria=7 verified=0 "
        "partial=1 missing=6 recommendation=do_not_recommend marketplace_submission=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
