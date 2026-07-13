#!/usr/bin/env python3
"""Execute and persist the fixed Phase 7.0 internal benchmark."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.rehearsal_runtime.multi_agent_runner import live_ark_clients
from saee_backend.services.reliability_framework.internal_benchmark import DIMENSIONS, build_internal_report, run_internal_benchmark

BASE=ROOT/"agent-interface/reliability/benchmark-runs"
MANIFESTS=BASE/"saee-internal-reliability-run-manifests.v1.0.json"
ASSESSMENTS=BASE/"saee-internal-reliability-assessments.v1.0.json"
FAILURES=BASE/"failure_distribution.json"
RESULT=ROOT/"agent-interface/reliability/saee-internal-reliability-benchmark-result.v1.0.json"
SCHEMA=ROOT/"schemas/saee-internal-reliability-benchmark-result.schema.v1.0.json"
REPORT=ROOT/"docs/research/SAEE_INTERNAL_RELIABILITY_BENCHMARK_REPORT_V1.md"


def progress(agent: str, repetition: int, scenario: str, status: str) -> None:
    print(f"internal_benchmark agent={agent} scenario={scenario} repetition={repetition}/3 status={status}",flush=True)


def main() -> int:
    run=run_internal_benchmark(live_ark_clients(),progress=progress)
    failed=[item for item in run["manifests"] if item["status"]!="completed"]
    classified=sum(bool(item["failure_type"]) for item in failed)
    taxonomy_coverage=classified/len(failed) if failed else 1.0
    MANIFESTS.write_text(json.dumps({"manifest_version":"1.0","benchmark_id":run["config"]["benchmark_id"],"run_manifests":run["manifests"]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    ASSESSMENTS.write_text(json.dumps({"assessment_set_version":"1.0","benchmark_id":run["config"]["benchmark_id"],"assessments":run["assessments"]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    FAILURES.write_text(json.dumps({"failure_distribution_version":"1.0","benchmark_id":run["config"]["benchmark_id"],"failed_runs":run["runs_failed"],"classified_failed_runs":classified,"failure_taxonomy_coverage":taxonomy_coverage,"counts":run["failure_distribution"],"non_implications":{"CONTRACT_FAILURE":"not a security failure","MODEL_RESPONSE_FAILURE":"not an intelligence failure"}},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    result={"benchmark_version":"1.0","benchmark_id":run["config"]["benchmark_id"],"internal_benchmark":True,"public_benchmark":False,"agents_count":len(run["config"]["agents"]),"scenarios_count":len(run["config"]["scenarios"]),"repetitions":run["config"]["repetitions"],"runs_attempted":len(run["manifests"]),"runs_completed":run["runs_completed"],"runs_failed":run["runs_failed"],"run_manifest_coverage":len(run["manifests"])/run["config"]["runs_planned"],"failure_taxonomy_coverage":taxonomy_coverage,"dimensions_evaluated":list(DIMENSIONS),"dimension_statistics":run["dimension_statistics"],"failure_distribution_reference":"agent-interface/reliability/benchmark-runs/failure_distribution.json","run_manifests_reference":"agent-interface/reliability/benchmark-runs/saee-internal-reliability-run-manifests.v1.0.json","assessments_reference":"agent-interface/reliability/benchmark-runs/saee-internal-reliability-assessments.v1.0.json","report_reference":"docs/research/SAEE_INTERNAL_RELIABILITY_BENCHMARK_REPORT_V1.md","methodology_review_reference":"agent-interface/reliability/methodology/saee-internal-reliability-methodology-review.v1.0.json","methodology_correction_applied":True,"leaderboard_generated":False,"ranking_generated":False,"certification":False,"intelligence_score_generated":False,"best_agent_selected":False,"production_ready":False,"external_validation_completed":False}
    errors=list(Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(result))
    if errors: raise ValueError(f"benchmark result invalid: {errors[0].message}")
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.write_text(build_internal_report(run),encoding="utf-8")
    print("SAEE_INTERNAL_RELIABILITY_BENCHMARK_RESULT")
    for key in ("runs_attempted","runs_completed","runs_failed","run_manifest_coverage","failure_taxonomy_coverage"): print(f"{key}={result[key]}")
    print("leaderboard_generated=false\nranking_generated=false\nproduction_ready=false")
    return 0 if result["run_manifest_coverage"]==1 and result["failure_taxonomy_coverage"]==1 else 2


if __name__=="__main__": raise SystemExit(main())
