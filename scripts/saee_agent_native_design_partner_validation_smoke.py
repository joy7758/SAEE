#!/usr/bin/env python3
"""Offline validation of the Phase 8 Agent-native protocol and stored run."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.agent_native_design_partner import build_result,digest,run_session


PLAN=ROOT/"agent-interface/commercial/saee-agent-native-design-partner-validation-plan.v1.0.json"
RECORDS=ROOT/"agent-interface/commercial/design-partner-validation/saee-agent-native-design-partner-records.v1.0.json"
RESULT=ROOT/"agent-interface/commercial/saee-agent-native-design-partner-validation-result.v1.0.json"
SCHEMA=ROOT/"schemas/saee-agent-native-design-partner-validation-result.schema.v1.0.json"
REPORT=ROOT/"docs/commercial/SAEE_AGENT_NATIVE_DESIGN_PARTNER_VALIDATION_REPORT_V1.md"


class FakeClient:
    def chat(self,messages):
        round_index=sum(item["role"]=="user" for item in messages)
        value={1:{"discovered_capability":"saee-evidence-adequacy","should_use_saee":True,"reason_codes":["EVIDENCE_ADEQUACY_NEEDED"]},2:{"use_saee_for_authorization":False,"alternative":"authorization_policy_engine","boundary_preserved":True},3:{"recommendation":"RECOMMEND_FOR_CONTROLLED_INTEGRATION","components":["observability","saee_evidence_adequacy","authorization_policy_engine"],"claims_not_made":["safety","compliance","deployment_approval"],"reason_codes":["COMPOSABLE_WITH_BOUNDARIES"]}}[round_index]
        return json.dumps(value,ensure_ascii=False),digest(value)


def main() -> int:
    plan=json.loads(PLAN.read_text(encoding="utf-8")); serial=[]
    for _ in range(5):
        records=[run_session(FakeClient(),profile,model) for profile in plan["partner_profiles"] for model in plan["models"]]
        serial.append(json.dumps(build_result(records,False,plan["source_benchmark"]),ensure_ascii=False,sort_keys=True))
    assert len(set(serial))==1
    preflight=json.loads(serial[0]); assert preflight["full_contract_pass"]==9 and preflight["provider_rounds"]==27 and preflight["status"]=="provisional_dependency_open"
    assert all(path.exists() for path in (RECORDS,RESULT,REPORT)),"execute controlled live validation before final smoke"
    result=json.loads(RESULT.read_text(encoding="utf-8")); validator=Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    assert not list(validator.iter_errors(result))
    stored=json.loads(RECORDS.read_text(encoding="utf-8")); records=stored["records"]
    assert len(records)==9 and result["sessions_attempted"]==9 and result["sessions_completed"]+result["sessions_contract_failed"]==9
    assert result["provider_rounds"]<=27 and result["human_participants"]==0
    assert stored["raw_provider_content_stored"] is False and stored["hidden_reasoning_stored"] is False
    assert all(len(item["response_digests"])==item["provider_rounds"] for item in records)
    assert result["market_validation"] is False and result["adoption_validated"] is False and result["production_ready"] is False
    invalid=[]
    for field,value in (("sessions_attempted",8),("partner_profiles",2),("models",2),("human_participants",1),("customer_contacted",True),("customer_data_used",True),("market_validation",True),("adoption_validated",True),("production_ready",True)):
        candidate=copy.deepcopy(result); candidate[field]=value; invalid.append(bool(list(validator.iter_errors(candidate))))
    candidate=copy.deepcopy(result); candidate["status"]="completed_agent_native_validation"; candidate["phase7_2_dependency_complete"]=False; invalid.append(bool(list(validator.iter_errors(candidate))))
    assert all(invalid)
    print("SAEE_AGENT_NATIVE_DESIGN_PARTNER_VALIDATION_SMOKE: PASS")
    print("sessions=9/9")
    print(f"sessions_completed={result['sessions_completed']}/9")
    print(f"sessions_contract_failed={result['sessions_contract_failed']}/9")
    print(f"provider_rounds={result['provider_rounds']}/27")
    print(f"discovery_correct={result['discovery_correct']}/9")
    print(f"non_use_boundary_correct={result['non_use_boundary_correct']}/9")
    print(f"composition_correct={result['composition_correct']}/9")
    print(f"claim_boundary_correct={result['claim_boundary_correct']}/9")
    print(f"full_contract_pass={result['full_contract_pass']}/9")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("human_participants=0")
    print("raw_provider_content_stored=false")
    print("hidden_reasoning_stored=false")
    print("market_validation=false")
    print("adoption_validated=false")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
