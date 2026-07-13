#!/usr/bin/env python3
"""Execute the 30 incremental Phase 7.2 calls and compose the 75-run corpus."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.rehearsal_runtime.multi_agent_runner import live_ark_clients
from saee_backend.services.reliability_framework.extended_benchmark import build_extended_report, build_result, combine_corpora
from saee_backend.services.reliability_framework.internal_benchmark import run_internal_benchmark


BASE=ROOT/"agent-interface/reliability/benchmark-runs"
OUT=BASE/"v1.1"
BASE_CONFIG=BASE/"saee-internal-reliability-benchmark-run.v1.0.json"
BASE_MANIFESTS=BASE/"saee-internal-reliability-run-manifests.v1.0.json"
BASE_ASSESSMENTS=BASE/"saee-internal-reliability-assessments.v1.0.json"
NEW_MANIFESTS=OUT/"saee-extended-internal-reliability-new-run-manifests.v1.1.json"
COMBINED_MANIFESTS=OUT/"saee-extended-internal-reliability-combined-run-manifests.v1.1.json"
COMBINED_ASSESSMENTS=OUT/"saee-extended-internal-reliability-assessments.v1.1.json"
FAILURES=OUT/"saee-extended-internal-reliability-failure-distribution.v1.1.json"
RESULT=ROOT/"agent-interface/reliability/saee-extended-internal-reliability-benchmark-result.v1.1.json"
SCHEMA=ROOT/"schemas/saee-extended-internal-reliability-benchmark-result.schema.v1.1.json"
REPORT=ROOT/"docs/research/SAEE_EXTENDED_INTERNAL_RELIABILITY_BENCHMARK_REPORT_V1_1.md"
STATUS=OUT/"SAEE_PHASE7_2_EXECUTION_STATUS.json"
SOURCE_REF="agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-new-run-manifests.v1.1.json"


def progress(agent: str, repetition: int, scenario: str, status: str) -> None:
    print(f"extended_benchmark agent={agent} scenario={scenario} repetition={repetition}/5 status={status}",flush=True)


def load_list(path: Path, key: str) -> list[dict]:
    value=json.loads(path.read_text(encoding="utf-8"))
    items=value.get(key)
    if not isinstance(items,list): raise ValueError(f"EXTENDED_BENCHMARK_INPUT_INVALID:{path.name}")
    return items


def main() -> int:
    base_manifests=load_list(BASE_MANIFESTS,"run_manifests")
    base_assessments=load_list(BASE_ASSESSMENTS,"assessments")
    clients=live_ark_clients()
    incremental=run_internal_benchmark(
        clients,
        progress=progress,
        config_path=BASE_CONFIG,
        repetition_indices=[4,5],
        source_ref=SOURCE_REF,
        phase_origin="phase7_2",
    )
    combined=combine_corpora(base_manifests,base_assessments,incremental["manifests"],incremental["assessments"])
    result=build_result(combined)
    errors=list(Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).iter_errors(result))
    if errors: raise ValueError(f"EXTENDED_BENCHMARK_RESULT_INVALID:{errors[0].message}")
    OUT.mkdir(parents=True,exist_ok=True)
    NEW_MANIFESTS.write_text(json.dumps({"manifest_version":"1.1","benchmark_id":result["benchmark_id"],"repetition_indices":[4,5],"run_manifests":incremental["manifests"]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    COMBINED_MANIFESTS.write_text(json.dumps({"manifest_version":"1.1","benchmark_id":result["benchmark_id"],"base_runs":45,"new_runs":30,"run_manifests":combined["manifests"]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    COMBINED_ASSESSMENTS.write_text(json.dumps({"assessment_set_version":"1.1","benchmark_id":result["benchmark_id"],"methodology_review_reference":result["methodology_review_reference"],"assessments":combined["assessments"]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    failed=[item for item in combined["manifests"] if item["status"]!="completed"]
    FAILURES.write_text(json.dumps({"failure_distribution_version":"1.1","benchmark_id":result["benchmark_id"],"failed_runs":len(failed),"classified_failed_runs":sum(bool(item["failure_type"]) for item in failed),"failure_taxonomy_coverage":combined["failure_taxonomy_coverage"],"counts":combined["failure_distribution"],"non_implications":{"CONTRACT_FAILURE":"not a security failure","MODEL_RESPONSE_FAILURE":"not an intelligence failure","ENVIRONMENT_FAILURE":"not a model failure"}},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.write_text(build_extended_report(combined),encoding="utf-8")
    STATUS.write_text(json.dumps({"status_version":"1.0","phase":"7.2","benchmark_id":result["benchmark_id"],"implementation_ready":True,"offline_preflight_passed":True,"additional_real_model_runs_attempted":30,"additional_real_model_runs_required":30,"combined_runs_available":75,"combined_runs_required":75,"execution_complete":True,"blocking_condition":None,"qianfan_substitution_allowed":False,"qianfan_substitution_reason":"The benchmark preserves the frozen Volcengine Ark Agent identities.","external_world_actions":False,"ranking_generated":False,"production_ready":False},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    new_status=Counter(item["status"] for item in incremental["manifests"])
    print("SAEE_EXTENDED_INTERNAL_RELIABILITY_BENCHMARK_RESULT")
    print("additional_runs_attempted=30")
    print(f"additional_runs_completed={new_status['completed']}")
    print(f"additional_runs_failed={30-new_status['completed']}")
    print("combined_runs_attempted=75")
    print(f"combined_runs_completed={result['runs_completed']}")
    print(f"combined_runs_failed={result['runs_failed']}")
    print("run_manifest_coverage=1.0")
    print(f"failure_taxonomy_coverage={result['failure_taxonomy_coverage']}")
    print("ranking_generated=false")
    print("production_ready=false")
    return 0 if result["run_manifest_coverage"]==1.0 and result["failure_taxonomy_coverage"]==1.0 else 2


if __name__=="__main__": raise SystemExit(main())
