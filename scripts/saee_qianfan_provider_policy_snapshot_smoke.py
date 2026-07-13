#!/usr/bin/env python3
"""Verify the source-linked Qianfan policy snapshot remains review-only."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json"
GATE = ROOT / "docs/strategy/SAEE_QIANFAN_PROVIDER_POLICY_SNAPSHOT_RECOMMENDATION_GATE.md"
INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_QIANFAN_PROVIDER_POLICY_SNAPSHOT_SMOKE: FAIL " + message)


def main() -> None:
    data = json.loads(PROFILE.read_text(encoding="utf-8"))
    policy = data["official_policy_reference"]
    require(policy["url"].startswith("https://cloud.baidu.com/"), "official policy URL")
    require(policy["catalog_url"].startswith("https://cloud.baidu.com/"), "catalog URL")
    require(policy["catalog_last_updated"] == "2026-02-09", "catalog date")
    require(re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", policy["reviewed_on"]), "review date")
    require(len(policy["observed_clauses"]) == 3, "observed clause count")
    require(len(policy["unresolved_questions"]) == 3, "unresolved question count")
    review = data["review_status"]
    require(review["provider_retention_terms_verified"] is False, "retention remains unverified")
    require(review["data_processing_agreement_completed"] is False, "DPA remains open")
    require(review["privacy_legal_review_completed"] is False, "legal review remains open")
    require(review["blockers_closed_by_profile"] == 0, "profile cannot close blockers")
    text = PROFILE.read_text(encoding="utf-8") + GATE.read_text(encoding="utf-8")
    require("bce-v3/ALTAK-" not in text, "secret pattern")
    require("production approval" in text or "生产批准" in text, "production boundary")
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    entry = index["qianfan_provider_data_processing_v0_1"]
    require(entry["observed_policy_clause_count"] == 3, "index clause count")
    require(entry["retention_terms_verified"] is False and entry["dpa_completed"] is False, "index review boundary")
    llms = LLMS.read_text(encoding="utf-8")
    for token in (
        "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json",
        "docs/strategy/SAEE_QIANFAN_PROVIDER_POLICY_SNAPSHOT_RECOMMENDATION_GATE.md",
        "scripts/saee_qianfan_provider_policy_snapshot_smoke.py",
    ):
        require(token in llms, "llms path=" + token)
    print(
        "SAEE_QIANFAN_PROVIDER_POLICY_SNAPSHOT_SMOKE: PASS clauses=3 "
        "unresolved_questions=3 retention_verified=false dpa_completed=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
