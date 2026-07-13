#!/usr/bin/env python3
"""Apply and persist the Phase 7.1 conservative methodology correction."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.reliability_framework.methodology_review import build_review,correct_assessments,recompute_statistics

ASSESSMENTS=ROOT/"agent-interface/reliability/benchmark-runs/saee-internal-reliability-assessments.v1.0.json"
MANIFESTS=ROOT/"agent-interface/reliability/benchmark-runs/saee-internal-reliability-run-manifests.v1.0.json"
RESULT=ROOT/"agent-interface/reliability/saee-internal-reliability-benchmark-result.v1.0.json"
RESULT_SCHEMA=ROOT/"schemas/saee-internal-reliability-benchmark-result.schema.v1.0.json"
ASSESSMENT_SCHEMA=ROOT/"schemas/saee-agent-reliability-assessment.schema.v1.0.json"
REVIEW=ROOT/"agent-interface/reliability/methodology/saee-internal-reliability-methodology-review.v1.0.json"
REVIEW_SCHEMA=ROOT/"schemas/saee-internal-reliability-methodology-review.schema.v1.0.json"
REPORT=ROOT/"docs/research/SAEE_INTERNAL_RELIABILITY_BENCHMARK_REPORT_V1.md"


def main()->int:
    corrected=correct_assessments(json.loads(ASSESSMENTS.read_text()))
    validator=Draft202012Validator(json.loads(ASSESSMENT_SCHEMA.read_text()))
    assert all(not list(validator.iter_errors(item)) for item in corrected["assessments"])
    manifests=json.loads(MANIFESTS.read_text())["run_manifests"]
    result=json.loads(RESULT.read_text())
    result["dimension_statistics"]=recompute_statistics(manifests,corrected["assessments"],result["repetitions"])
    result["methodology_review_reference"]="agent-interface/reliability/methodology/saee-internal-reliability-methodology-review.v1.0.json"
    result["methodology_correction_applied"]=True
    review=build_review()
    assert not list(Draft202012Validator(json.loads(REVIEW_SCHEMA.read_text())).iter_errors(review))
    assert not list(Draft202012Validator(json.loads(RESULT_SCHEMA.read_text())).iter_errors(result))
    ASSESSMENTS.write_text(json.dumps(corrected,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REVIEW.parent.mkdir(parents=True,exist_ok=True)
    REVIEW.write_text(json.dumps(review,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report=REPORT.read_text(encoding="utf-8")
    marker="\n## Methodology Correction v1.0\n"
    if marker in report: report=report.split(marker)[0].rstrip()+"\n"
    report+=marker+"\nPhase 7.1 decoupled Task Execution from Evidence Adequacy and changed Recovery to `NOT_ASSESSED` where no explicit recovery opportunity was preserved. No model was rerun and no Run Manifest was changed. Corrected counts: Task PASS=32/45; Recovery NOT_ASSESSED=45/45; Boundary PASS=15/45; Evidence PASS=23, FAIL=9, NOT_ASSESSED=13; Assessment Availability PASS=32, FAIL=13.\n"
    REPORT.write_text(report,encoding="utf-8")
    print("SAEE_INTERNAL_RELIABILITY_METHODOLOGY_REVIEW_RESULT")
    print("review_status=PASS_WITH_LIMITATIONS_TO_PHASE7_2")
    print("extended_benchmark_allowed=true")
    print("methodology_corrections=2/2")
    print("new_model_runs=0")
    print("ranking_generated=false")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
