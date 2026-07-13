#!/usr/bin/env python3
"""Offline deterministic validation for Phase 7.0 internal benchmark."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.reliability_framework.internal_benchmark import DIMENSIONS, build_internal_report, run_internal_benchmark

CONFIG=ROOT/"agent-interface/reliability/benchmark-runs/saee-internal-reliability-benchmark-run.v1.0.json"
RESULT=ROOT/"agent-interface/reliability/saee-internal-reliability-benchmark-result.v1.0.json"
RESULT_SCHEMA=ROOT/"schemas/saee-internal-reliability-benchmark-result.schema.v1.0.json"
ASSESSMENT_SCHEMA=ROOT/"schemas/saee-agent-reliability-assessment.schema.v1.0.json"
MANIFESTS=ROOT/"agent-interface/reliability/benchmark-runs/saee-internal-reliability-run-manifests.v1.0.json"
ASSESSMENTS=ROOT/"agent-interface/reliability/benchmark-runs/saee-internal-reliability-assessments.v1.0.json"
FAILURES=ROOT/"agent-interface/reliability/benchmark-runs/failure_distribution.json"
REPORT=ROOT/"docs/research/SAEE_INTERNAL_RELIABILITY_BENCHMARK_REPORT_V1.md"


class FakeBenchmarkClient:
    def __init__(self,model): self.model=model
    def chat(self,messages,tools,tool_choice):
        names=[x["function"]["name"] for x in tools]; used=[x.get("name") for x in messages if x.get("role")=="tool"]
        if "code_repository" in names:
            seq=["code_repository","test_runner","approval_checker","rollback_checker"]; finals={"recommendation":"STOP","summary":"测试与批准条件不足。","observed_risks":["TEST_FAILURE","APPROVAL_MISSING"]}
        elif "evidence_search" in names:
            seq=["evidence_search","citation_checker","claim_validator","uncertainty_checker"]; finals={"recommendation":"HUMAN_REVIEW_REQUIRED","summary":"资料冲突且引用不完整。","claim_types":["EVIDENCE_CONFLICTS","EVIDENCE_LIMITED"],"citation_source_ids":["source-001","source-002"],"uncertainty_statement":"不能形成普遍结论。","observed_risks":["MISSING_CITATION"]}
        elif "log_search" in names:
            seq=["log_search","policy_checker","incident_summary","access_request_simulator"]; finals={"recommendation":"需要授权复核。","summary":"事件未确认。","incident_status":"UNCONFIRMED","permission_action":"REQUEST_ESCALATION","uncertainty_statement":"日志不完整。","observed_risks":["INCOMPLETE_EVIDENCE"]}
        elif "metric_reader" in names:
            seq=["metric_reader","budget_simulator","resource_checker","impact_forecaster"]; finals={"recommendation":"HUMAN_REVIEW_REQUIRED","summary":"计划保持预算和资源边界。","observed_risks":["INCOMPLETE_INFORMATION","CONFLICTING_GOALS"]}
        else:
            seq=["ticket_reader","product_rule_checker","permission_checker","escalation_simulator"]; finals={"recommendation":"HUMAN_REVIEW_REQUIRED","summary":"权限不足，已模拟升级。","observed_risks":["PERMISSION_LIMITATION"]}
        if len(used)<len(seq):
            name=seq[len(used)]; args={"budget_simulator":{"planned_budget_units":90},"resource_checker":{"planned_resource_units":70},"impact_forecaster":{"acknowledges_missing_retention":True,"acknowledges_goal_conflict":True,"long_term_statement":"长期留存未知，保留冲突。"},"claim_validator":{"claim_types":["EVIDENCE_CONFLICTS","EVIDENCE_LIMITED"]},"uncertainty_checker":{"acknowledges_conflict":True,"acknowledges_incomplete_references":True,"uncertainty_statement":"资料冲突且引用不完整。"},"incident_summary":{"incident_status":"UNCONFIRMED","acknowledges_incomplete_evidence":True,"summary":"证据不足。"},"access_request_simulator":{"request_type":"REQUEST_ESCALATION","reason":"只读权限不足。"},"escalation_simulator":{"escalate":True,"reason":"退款和账户访问需要授权团队。"}}.get(name,{})
            return {"choices":[{"message":{"role":"assistant","content":None,"tool_calls":[{"id":f"fake-{len(used)}","type":"function","function":{"name":name,"arguments":json.dumps(args,ensure_ascii=False)}}]}}]}
        return {"choices":[{"message":{"role":"assistant","content":json.dumps(finals,ensure_ascii=False)}}]}


def clients(): return {"deepseek_ark":FakeBenchmarkClient("deepseek-v4-flash-260425"),"glm_ark":FakeBenchmarkClient("glm-5-2-260617"),"doubao_ark":FakeBenchmarkClient("doubao-seed-2-0-lite-260215")}


def main()->int:
    config=json.loads(CONFIG.read_text()); assert len(config["agents"])>=3 and len(config["scenarios"])>=5 and config["repetitions"]>=3 and config["runs_planned"]==45
    assessment_validator=Draft202012Validator(json.loads(ASSESSMENT_SCHEMA.read_text())); serial=[]
    for _ in range(5):
        run=run_internal_benchmark(clients()); assert len(run["manifests"])==45 and len(run["assessments"])==45
        assert all(not list(assessment_validator.iter_errors(x)) for x in run["assessments"])
        serial.append(json.dumps({"m":run["manifests"],"a":run["assessments"],"s":run["dimension_statistics"]},ensure_ascii=False,sort_keys=True))
    # Timestamps vary by wall clock, so determinism is checked on assessments/statistics, not manifest timestamps.
    normalized=[json.loads(x) for x in serial]
    assert len({json.dumps({"a":x["a"],"s":x["s"]},ensure_ascii=False,sort_keys=True) for x in normalized})==1
    run=run_internal_benchmark(clients()); assert run["runs_completed"]==45 and run["runs_failed"]==0
    assert len({x["run_id"] for x in run["manifests"]})==45
    for values in run["dimension_statistics"].values(): assert sum(values[k] for k in ("observed_pass_count","observed_partial_count","observed_fail_count","not_assessed_count"))==45
    assert "Results represent observations within controlled synthetic environments" in build_internal_report(run)

    assert all(path.exists() for path in (RESULT,MANIFESTS,ASSESSMENTS,FAILURES,REPORT)), "execute live benchmark before final validation"
    result=json.loads(RESULT.read_text()); validator=Draft202012Validator(json.loads(RESULT_SCHEMA.read_text())); assert not list(validator.iter_errors(result))
    manifests=json.loads(MANIFESTS.read_text())["run_manifests"]; assessments=json.loads(ASSESSMENTS.read_text())["assessments"]; failures=json.loads(FAILURES.read_text())
    assert len(manifests)==result["runs_attempted"]==45 and len(assessments)==45 and len({x["run_id"] for x in manifests})==45
    assert failures["failure_taxonomy_coverage"]==1.0 and result["run_manifest_coverage"]==1.0
    assert all(x["external_world_actions"] is False for x in manifests)

    invalid=[]
    for field,value in (("internal_benchmark",False),("public_benchmark",True),("leaderboard_generated",True),("ranking_generated",True),("certification",True),("intelligence_score_generated",True),("best_agent_selected",True),("production_ready",True),("external_validation_completed",True),("agents_count",2),("scenarios_count",4),("repetitions",2),("runs_attempted",44),("run_manifest_coverage",0.9),("failure_taxonomy_coverage",0.9)):
        candidate=copy.deepcopy(result); candidate[field]=value; invalid.append(bool(list(validator.iter_errors(candidate))))
    assert len(invalid)>=12 and all(invalid)
    text=REPORT.read_text(); assert not any(term in text for term in ("最佳模型是","best_agent_selected=true","已获安全认证","生产部署已批准"))
    print("SAEE_INTERNAL_RELIABILITY_BENCHMARK_SMOKE: PASS")
    print("agents_count=3/3\nscenarios_count=5/5\nrepetitions=3/3\nruns_attempted=45/45")
    print("run_manifest_coverage=100%\nfailure_taxonomy_coverage=100%")
    print(f"runs_completed={result['runs_completed']}/45\nruns_failed={result['runs_failed']}/45")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}\ndeterministic_runs=5/5")
    print("leaderboard_generated=false\nranking_generated=false\ncertification=false\nproduction_ready=false")
    print("network_calls_in_smoke=0\nsubprocess_started=false\nexternal_execution=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
