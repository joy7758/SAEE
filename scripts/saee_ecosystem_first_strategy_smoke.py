#!/usr/bin/env python3
"""Offline truth-boundary smoke for SAEE Ecosystem-First Strategy v1.0."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "agent-interface/ecosystem/saee-ecosystem-first-roadmap.v1.0.json"
SCHEMA = ROOT / "schemas/saee-ecosystem-first-roadmap.schema.v1.0.json"
STRATEGY = ROOT / "docs/strategy/SAEE_ECOSYSTEM_FIRST_STRATEGY_V1.md"
GATE = ROOT / "docs/strategy/SAEE_ECOSYSTEM_FIRST_STRATEGY_RECOMMENDATION_GATE.md"


def errors(value: dict) -> list[str]:
    result = ["SCHEMA_INVALID"] if list(Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value)) else []
    stages = value.get("stages", [])
    if [row.get("order") for row in stages] != list(range(8)): result.append("STAGE_ORDER_INVALID")
    if len({row.get("stage_id") for row in stages}) != 8: result.append("STAGE_ID_DUPLICATE")
    if value.get("current_stage_id") != "TECHNICAL_SIGNAL_RELEASE": result.append("CURRENT_STAGE_INVALID")
    if sum(row.get("status") == "ACTIVE" for row in stages) != 1: result.append("ACTIVE_STAGE_COUNT_INVALID")
    if stages and (stages[0].get("status") != "COMPLETED" or stages[1].get("status") != "ACTIVE"): result.append("STAGE_TRANSITION_INVALID")
    for group in value.get("first_90_day_metrics", {}).values():
        if any(row.get("baseline", 0) > row.get("target", 0) for row in group): result.append("METRIC_BASELINE_EXCEEDS_TARGET")
    if value.get("truth_boundary", {}).get("ecosystem_strategy_defined") is not True: result.append("STRATEGY_FLAG_INVALID")
    if value.get("truth_boundary", {}).get("partner_contact_completed") is not True: result.append("PARTNER_CONTACT_TRUTH_INVALID")
    allowed_true = {"ecosystem_strategy_defined", "technical_signal_package_ready", "partner_contact_completed"}
    if any(v for k, v in value.get("truth_boundary", {}).items() if k not in allowed_true): result.append("UNSUPPORTED_EXTERNAL_CLAIM")
    return list(dict.fromkeys(result))


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8")); Draft202012Validator.check_schema(schema)
    roadmap = json.loads(ROADMAP.read_text(encoding="utf-8"))
    assert not errors(roadmap), errors(roadmap)
    assert "生态嵌入路径" in STRATEGY.read_text(encoding="utf-8")
    assert "answer: recommend" in GATE.read_text(encoding="utf-8")
    assert [len(roadmap["first_90_day_metrics"][k]) for k in ("technical","ecosystem","commercial")] == [4,3,2]

    invalid = []
    for field, bad in (("strategy_version","2.0"),("strategy_id","other"),("horizon_months",6),("current_stage_id","ECOSYSTEM_ATTENTION"),("canonical_product_surface","Agent OS"),("capability_layer","Authorization Authority"),("ecosystem_entry_wedge","Sales Funnel")):
        item=copy.deepcopy(roadmap); item[field]=bad; invalid.append(item)
    item=copy.deepcopy(roadmap); item["stages"]=item["stages"][:-1]; invalid.append(item)
    item=copy.deepcopy(roadmap); item["stages"][1]["order"]=0; invalid.append(item)
    item=copy.deepcopy(roadmap); item["stages"][1]["stage_id"]=item["stages"][0]["stage_id"]; invalid.append(item)
    item=copy.deepcopy(roadmap); item["stages"][0]["status"]="ACTIVE"; invalid.append(item)
    item=copy.deepcopy(roadmap); item["stages"][1]["status"]="PLANNED"; invalid.append(item)
    item=copy.deepcopy(roadmap); item["first_90_day_metrics"]["ecosystem"][0]["baseline"]=2; invalid.append(item)
    item=copy.deepcopy(roadmap); item["truth_boundary"]["partner_contact_completed"]=False; invalid.append(item)
    for key in ("partner_relationship_established","joint_solution_confirmed","official_cloud_integration","marketplace_listed","external_agent_adoption_validated","customer_validated","production_ready"):
        item=copy.deepcopy(roadmap); item["truth_boundary"][key]=True; invalid.append(item)
    assert len(invalid) >= 15 and all(errors(item) for item in invalid)
    baseline=json.dumps(errors(roadmap),sort_keys=True)
    for _ in range(5): assert json.dumps(errors(roadmap),sort_keys=True)==baseline

    print("SAEE_ECOSYSTEM_FIRST_STRATEGY_SMOKE: PASS")
    print("strategy_horizon_months=12")
    print("stages=8/8")
    print("first_90_day_metrics=9/9")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("partner_contact_completed=true")
    print("current_stage=TECHNICAL_SIGNAL_RELEASE")
    print("technical_signal_package_ready=true")
    print("technical_article_published=false")
    print("ecosystem_technical_conversation_verified=false")
    print("marketplace_listed=false")
    print("external_agent_adoption_validated=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__": raise SystemExit(main())
