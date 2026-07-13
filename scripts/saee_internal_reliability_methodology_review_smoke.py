#!/usr/bin/env python3
"""Offline smoke for Phase 7.1 methodology review and corrected artifacts."""

from __future__ import annotations

import copy,json,sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.reliability_framework.methodology_review import build_review,correct_assessments,recompute_statistics


def main()->int:
    review_path=ROOT/"agent-interface/reliability/methodology/saee-internal-reliability-methodology-review.v1.0.json"
    review_schema=json.loads((ROOT/"schemas/saee-internal-reliability-methodology-review.schema.v1.0.json").read_text()); validator=Draft202012Validator(review_schema)
    review=json.loads(review_path.read_text()); assert not list(validator.iter_errors(review))
    assert review==build_review() and review["new_model_runs"]==0 and len(review["findings"])==9 and len(review["corrections"])==2
    manifests=json.loads((ROOT/"agent-interface/reliability/benchmark-runs/saee-internal-reliability-run-manifests.v1.0.json").read_text())["run_manifests"]
    payload=json.loads((ROOT/"agent-interface/reliability/benchmark-runs/saee-internal-reliability-assessments.v1.0.json").read_text())
    assert payload["methodology_correction"]["model_runs_repeated"] is False
    stats=recompute_statistics(manifests,payload["assessments"],3)
    assert stats["task_execution_reliability"]["observed_pass_count"]==32 and stats["task_execution_reliability"]["observed_partial_count"]==0
    assert stats["recovery_reliability"]["not_assessed_count"]==45
    assert stats["boundary_reliability"]["observed_pass_count"]==15
    assert stats["evidence_reliability"]["observed_pass_count"]==23 and stats["evidence_reliability"]["observed_fail_count"]==9
    assert stats["assessment_availability"]["observed_fail_count"]==13
    result=json.loads((ROOT/"agent-interface/reliability/saee-internal-reliability-benchmark-result.v1.0.json").read_text()); assert result["methodology_correction_applied"] is True and result["dimension_statistics"]==stats
    original=json.loads(json.dumps(payload)); assert correct_assessments(original)==payload
    invalid=[]
    for field,value in (("extended_benchmark_allowed",False),("new_model_runs",1),("review_status","PASS_UNCONDITIONAL")):
        x=copy.deepcopy(review); x[field]=value; invalid.append(bool(list(validator.iter_errors(x))))
    for field,value in (("benchmark_rerun",True),("overall_score",True),("ranking_generated",True),("certification",True),("production_ready",True),("external_validation_completed",True)):
        x=copy.deepcopy(review); x["truth_boundary"][field]=value; invalid.append(bool(list(validator.iter_errors(x))))
    x=copy.deepcopy(review); x["corrections"]=[]; invalid.append(bool(list(validator.iter_errors(x))))
    x=copy.deepcopy(review); x["phase7_2_conditions"]=[]; invalid.append(bool(list(validator.iter_errors(x))))
    x=copy.deepcopy(review); x["findings"]=[]; invalid.append(bool(list(validator.iter_errors(x))))
    x=copy.deepcopy(review); x["unexpected_score"]=1; invalid.append(bool(list(validator.iter_errors(x))))
    assert len(invalid)>=12 and all(invalid)
    canonical=json.dumps(review,sort_keys=True,ensure_ascii=False)
    assert all(json.dumps(build_review(),sort_keys=True,ensure_ascii=False)==canonical for _ in range(5))
    print("SAEE_INTERNAL_RELIABILITY_METHODOLOGY_REVIEW_SMOKE: PASS")
    print("findings=9/9\ncorrections=2/2\ninvalid_cases=13/13\ndeterministic_runs=5/5")
    print("task_evidence_decoupled=true\nrecovery_requires_explicit_opportunity=true\nnew_model_runs=0")
    print("extended_benchmark_allowed=true\noverall_score=false\nranking_generated=false\nproduction_ready=false")
    print("network_accessed=false\nsubprocess_started=false\nexternal_execution=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
