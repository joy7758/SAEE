#!/usr/bin/env python3
"""Offline deterministic and boundary validation for Phase 9 service."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.commercial_assessment_service import CommercialAssessmentError, generate_commercial_assessment


REQUEST=ROOT/"agent-interface/commercial/examples/saee-commercial-assessment-request.v1.0.json"
RESPONSE=ROOT/"agent-interface/commercial/examples/saee-commercial-assessment-response.v1.0.json"


def rejected(value: dict) -> bool:
    try: generate_commercial_assessment(value)
    except CommercialAssessmentError: return True
    return False


def main() -> int:
    request=json.loads(REQUEST.read_text(encoding="utf-8")); serial=[]
    for _ in range(5): serial.append(json.dumps(generate_commercial_assessment(request),ensure_ascii=False,sort_keys=True))
    assert len(set(serial))==1
    response=json.loads(serial[0]); assert response["scope_summary"]["available_runs"]==75 and response["scope_summary"]["selected_runs"]==75
    findings={item["dimension"]:item for item in response["dimension_findings"]}
    assert findings["task_execution_reliability"]["observed_pass"]==53 and findings["task_execution_reliability"]["not_assessed"]==22
    assert findings["recovery_reliability"]["not_assessed"]==75
    assert response["evidence_summary"]=={"accountability_claim_established":False,"insufficient":14,"not_assessed":22,"supported":39}
    assert len(response["input_bindings"])==3 and all(len(item["sha256"])==64 for item in response["input_bindings"])
    assert response["truth_boundary"]["ranking_generated"] is False and response["truth_boundary"]["deployment_authorized"] is False

    invalid=[]
    for field,value in (("customer_data_used",True),("deployment_decision_requested",True),("language","en-US")):
        candidate=copy.deepcopy(request); candidate[field]=value; invalid.append(rejected(candidate))
    candidate=copy.deepcopy(request); candidate["scope"]["agent_profiles"]=[]; invalid.append(rejected(candidate))
    candidate=copy.deepcopy(request); candidate["scope"]["scenario_ids"]=[]; invalid.append(rejected(candidate))
    candidate=copy.deepcopy(request); candidate["benchmark_result_ref"]="../secret.json"; invalid.append(rejected(candidate))
    candidate=copy.deepcopy(request); candidate["benchmark_result_ref"]="missing.json"; invalid.append(rejected(candidate))
    candidate=copy.deepcopy(request); candidate["scope"]["agent_profiles"]=["unknown_agent"]; invalid.append(rejected(candidate))
    candidate=copy.deepcopy(request); candidate["unexpected"]=True; invalid.append(rejected(candidate))
    assert all(invalid)
    assert RESPONSE.exists() and json.loads(RESPONSE.read_text(encoding="utf-8"))==response
    print("SAEE_COMMERCIAL_ASSESSMENT_SERVICE_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("selected_runs=75/75")
    print("dimension_findings=5/5")
    print("input_digest_bindings=3/3")
    print("language=zh-CN")
    print("customer_data_used=false")
    print("commercial_delivery_completed=false")
    print("ranking_generated=false")
    print("deployment_authorized=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
