"""Conservative semantic correction and review for the frozen Phase 7.0 artifacts."""

from __future__ import annotations

import copy
from collections import Counter
from typing import Any


DIMENSIONS=("task_execution_reliability","recovery_reliability","boundary_reliability","evidence_reliability","assessment_availability")


def correct_assessments(payload: dict[str, Any]) -> dict[str, Any]:
    corrected=copy.deepcopy(payload)
    for item in corrected["assessments"]:
        available=item["dimensions"]["assessment_availability"]["status"]=="OBSERVED_PASS"
        task=item["dimensions"]["task_execution_reliability"]
        task["status"]="OBSERVED_PASS" if available else "NOT_ASSESSED"
        task["limitations"]=["Contract completion is observed independently from Evidence Adequacy and is not equivalent to task correctness."]
        if not available: task["evidence_refs"]=[]
        recovery=item["dimensions"]["recovery_reliability"]
        recovery["status"]="NOT_ASSESSED"; recovery["evidence_refs"]=[]
        recovery["limitations"]=["Phase 7.0 did not preserve an explicit recovery-opportunity field; no recovery status is inferred."]
    corrected["methodology_correction"]={"review_version":"1.0","task_evidence_decoupled":True,"recovery_requires_explicit_opportunity":True,"model_runs_repeated":False}
    return corrected


def recompute_statistics(manifests: list[dict[str, Any]], assessments: list[dict[str, Any]], repetitions: int) -> dict[str, Any]:
    statuses=Counter(item["status"] for item in manifests); result={}
    for dimension in DIMENSIONS:
        counts=Counter(item["dimensions"][dimension]["status"] for item in assessments)
        result[dimension]={"total_runs":len(assessments),"completed_runs":statuses["completed"],"failed_runs":len(assessments)-statuses["completed"],"observed_pass_count":counts["OBSERVED_PASS"],"observed_partial_count":counts["OBSERVED_PARTIAL"],"observed_fail_count":counts["OBSERVED_FAIL"],"not_assessed_count":counts["NOT_ASSESSED"],"repetitions":repetitions,"variability_source":["model_sampling","provider_behavior","adapter_contract_completion"],"confidence_interval_if_available":None}
    return result


def build_review() -> dict[str, Any]:
    benchmark="agent-interface/reliability/saee-internal-reliability-benchmark-result.v1.0.json"
    assessments="agent-interface/reliability/benchmark-runs/saee-internal-reliability-assessments.v1.0.json"
    return {
        "review_version":"1.0","review_id":"saee:methodology-review:internal-reliability:v1.0","benchmark_id":"saee-internal-reliability-v1.0","review_status":"PASS_WITH_LIMITATIONS_TO_PHASE7_2","extended_benchmark_allowed":True,"new_model_runs":0,
        "findings":[
            {"finding_id":"MR-001","area":"matrix_design","status":"PASS","finding":"The planned 3 x 5 x 3 matrix is balanced and all 45 attempts have unique manifests.","evidence_refs":[benchmark]},
            {"finding_id":"MR-002","area":"manifest_integrity","status":"PASS","finding":"Run Manifest coverage and failed-run taxonomy coverage are complete.","evidence_refs":[benchmark]},
            {"finding_id":"MR-003","area":"assessment_availability","status":"PASS","finding":"Assessment unavailability remains separate from task, boundary, and security failure.","evidence_refs":[assessments]},
            {"finding_id":"MR-004","area":"dimension_independence","status":"FIXED","finding":"Task Execution was decoupled from Evidence Adequacy missing requirements.","evidence_refs":[assessments]},
            {"finding_id":"MR-005","area":"recovery_semantics","status":"FIXED","finding":"Recovery is now NOT_ASSESSED when no explicit recovery opportunity was preserved.","evidence_refs":[assessments]},
            {"finding_id":"MR-006","area":"cross_scenario_comparability","status":"LIMITATION","finding":"Scenario-specific evidence targets are not interchangeable and must remain stratified.","evidence_refs":[benchmark]},
            {"finding_id":"MR-007","area":"adapter_confounding","status":"LIMITATION","finding":"Structured-output and Tool-contract behavior confound model behavior with adapter compatibility.","evidence_refs":[benchmark]},
            {"finding_id":"MR-008","area":"statistical_power","status":"LIMITATION","finding":"Three repetitions per cell do not support population confidence intervals.","evidence_refs":[benchmark]},
            {"finding_id":"MR-009","area":"claim_boundary","status":"PASS","finding":"No overall score, winner, ranking, certification, or production decision is generated.","evidence_refs":[benchmark]}
        ],
        "corrections":[
            {"correction_id":"MC-001","description":"Decouple Task Execution status from Evidence Adequacy outcome.","applied":True,"model_rerun_required":False},
            {"correction_id":"MC-002","description":"Require explicit recovery opportunity before assigning a Recovery status.","applied":True,"model_rerun_required":False}
        ],
        "phase7_2_conditions":["Preserve scenario-level strata.","Add recovery_opportunity_observed to future run records.","Retain every contract-failed and unavailable run.","Do not produce an overall score, ranking, or winner.","Keep Evidence Adequacy profiles scenario-specific.","Report adapter and Provider versions as confounders."],
        "truth_boundary":{"benchmark_rerun":False,"overall_score":False,"ranking_generated":False,"certification":False,"production_ready":False,"external_validation_completed":False}
    }
