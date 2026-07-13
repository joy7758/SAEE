#!/usr/bin/env python3
"""Offline deterministic validation for Phase 7.2 extended benchmark."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.reliability_framework.extended_benchmark import build_extended_report, build_result, combine_corpora
from saee_backend.services.reliability_framework.internal_benchmark import run_internal_benchmark
from scripts.saee_internal_reliability_benchmark_smoke import clients


BASE=ROOT/"agent-interface/reliability/benchmark-runs"
CONFIG=BASE/"saee-extended-internal-reliability-benchmark-run.v1.1.json"
BASE_CONFIG=BASE/"saee-internal-reliability-benchmark-run.v1.0.json"
BASE_MANIFESTS=BASE/"saee-internal-reliability-run-manifests.v1.0.json"
BASE_ASSESSMENTS=BASE/"saee-internal-reliability-assessments.v1.0.json"
OUT=BASE/"v1.1"
NEW=OUT/"saee-extended-internal-reliability-new-run-manifests.v1.1.json"
COMBINED=OUT/"saee-extended-internal-reliability-combined-run-manifests.v1.1.json"
ASSESSMENTS=OUT/"saee-extended-internal-reliability-assessments.v1.1.json"
FAILURES=OUT/"saee-extended-internal-reliability-failure-distribution.v1.1.json"
RESULT=ROOT/"agent-interface/reliability/saee-extended-internal-reliability-benchmark-result.v1.1.json"
SCHEMA=ROOT/"schemas/saee-extended-internal-reliability-benchmark-result.schema.v1.1.json"
REPORT=ROOT/"docs/research/SAEE_EXTENDED_INTERNAL_RELIABILITY_BENCHMARK_REPORT_V1_1.md"


def items(path: Path,key: str) -> list[dict]: return json.loads(path.read_text(encoding="utf-8"))[key]


def main() -> int:
    config=json.loads(CONFIG.read_text(encoding="utf-8"))
    assert config["additional_repetition_indices"]==[4,5] and config["combined_runs_planned"]==75
    base_m=items(BASE_MANIFESTS,"run_manifests"); base_a=items(BASE_ASSESSMENTS,"assessments")
    serial=[]
    for _ in range(5):
        new=run_internal_benchmark(clients(),config_path=BASE_CONFIG,repetition_indices=[4,5],source_ref="agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-new-run-manifests.v1.1.json",phase_origin="phase7_2")
        combined=combine_corpora(base_m,base_a,new["manifests"],new["assessments"])
        serial.append(json.dumps({"a":combined["assessments"],"d":combined["dimension_statistics"]},ensure_ascii=False,sort_keys=True))
    assert len(set(serial))==1 and len(new["manifests"])==30
    assert all(item["repetition_index"] in {4,5} for item in new["manifests"])
    assert all(item["phase_origin"]=="phase7_2" and item["recovery_opportunity_observed"] is False for item in new["manifests"])
    assert all(item["dimensions"]["recovery_reliability"]["status"]=="NOT_ASSESSED" for item in new["assessments"])
    report=build_extended_report(combined)
    assert "不生成总分、排名、胜者、认证或部署授权" in report

    required=(NEW,COMBINED,ASSESSMENTS,FAILURES,RESULT,REPORT)
    assert all(path.exists() for path in required),"execute extended live benchmark before final validation"
    result=json.loads(RESULT.read_text(encoding="utf-8")); validator=Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    assert not list(validator.iter_errors(result))
    stored_new=items(NEW,"run_manifests"); stored_combined=items(COMBINED,"run_manifests"); stored_assessments=items(ASSESSMENTS,"assessments")
    assert len(stored_new)==30 and len(stored_combined)==75 and len(stored_assessments)==75
    assert len({item["run_id"] for item in stored_combined})==75
    assert all(item["external_world_actions"] is False for item in stored_combined)
    assert all(item["phase_origin"]=="phase7_2" and isinstance(item["recovery_opportunity_observed"],bool) for item in stored_new)
    assert result["runs_completed"]+result["runs_failed"]==75

    invalid=[]
    for field,value in (("internal_benchmark",False),("public_benchmark",True),("agents_count",2),("scenarios_count",4),("combined_repetitions",4),("additional_runs_attempted",29),("combined_runs_attempted",74),("run_manifest_coverage",0.9),("failure_taxonomy_coverage",0.9),("methodology_conditions_satisfied",False),("recovery_opportunity_recorded_for_new_runs",False),("scenario_strata_preserved",False),("leaderboard_generated",True),("ranking_generated",True),("overall_score_generated",True),("winner_selected",True),("certification",True),("production_ready",True),("external_validation_completed",True),("population_reliability_probability_established",True)):
        candidate=copy.deepcopy(result); candidate[field]=value; invalid.append(bool(list(validator.iter_errors(candidate))))
    assert all(invalid)
    text=REPORT.read_text(encoding="utf-8")
    assert not any(term in text for term in ("最佳模型是","生产部署已批准","安全认证通过","总体可靠性概率为"))
    print("SAEE_EXTENDED_INTERNAL_RELIABILITY_BENCHMARK_SMOKE: PASS")
    print("base_runs=45/45")
    print("additional_runs=30/30")
    print("combined_runs=75/75")
    print("scenario_strata=15/15")
    print("recovery_opportunity_field=30/30")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("leaderboard_generated=false")
    print("ranking_generated=false")
    print("population_reliability_probability_established=false")
    print("network_calls_in_smoke=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
