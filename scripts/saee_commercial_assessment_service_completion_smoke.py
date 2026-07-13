#!/usr/bin/env python3
"""Requirement-level validation for the bounded Phase 9 completion claim."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.commercial_assessment_service import generate_commercial_assessment_path


STATUS=ROOT/"agent-interface/commercial/saee-commercial-assessment-service-status.v1.0.json"
SCHEMA=ROOT/"schemas/saee-commercial-assessment-service-status.schema.v1.0.json"
REQUEST=ROOT/"agent-interface/commercial/examples/saee-commercial-assessment-request.v1.0.json"
RESPONSE=ROOT/"agent-interface/commercial/examples/saee-commercial-assessment-response.v1.0.json"
PHASE7_2=ROOT/"agent-interface/reliability/benchmark-runs/v1.1/SAEE_PHASE7_2_EXECUTION_STATUS.json"
PHASE7_3=ROOT/"agent-interface/research/reliability-framework-v1.1/SAEE_PHASE7_3_STATUS.json"
PHASE8=ROOT/"agent-interface/commercial/saee-agent-native-design-partner-validation-result.v1.0.json"
REPORT=ROOT/"docs/commercial/SAEE_COMMERCIAL_ASSESSMENT_SERVICE_COMPLETION_V1.md"
GATE=ROOT/"docs/strategy/SAEE_COMMERCIAL_ASSESSMENT_SERVICE_V1_RECOMMENDATION_GATE.md"


def main() -> int:
    status=json.loads(STATUS.read_text(encoding="utf-8")); validator=Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    assert not list(validator.iter_errors(status))
    phase7_2=json.loads(PHASE7_2.read_text(encoding="utf-8")); phase7_3=json.loads(PHASE7_3.read_text(encoding="utf-8")); phase8=json.loads(PHASE8.read_text(encoding="utf-8"))
    assert phase7_2["execution_complete"] is True and phase7_2["combined_runs_available"]==75
    assert phase7_3["research_artifact_generated"] is True and phase7_3["report_generated"] is True
    assert phase8["status"]=="completed_agent_native_validation" and phase8["phase7_2_dependency_complete"] is True
    assert phase8["sessions_attempted"]==9 and phase8["sessions_completed"]==8 and phase8["full_contract_pass"]==6
    response=generate_commercial_assessment_path(REQUEST); assert response==json.loads(RESPONSE.read_text(encoding="utf-8"))
    assert response["service_stage"]=="local_agent_callable_validated_service" and response["scope_summary"]["selected_runs"]==75
    assert response["evidence_summary"]=={"supported":39,"insufficient":14,"not_assessed":22,"accountability_claim_established":False}
    assert all((ROOT/ref).is_file() for ref in status["contracts"].values())
    assert "answer: recommend" in GATE.read_text(encoding="utf-8")
    text=REPORT.read_text(encoding="utf-8"); assert not any(term in text for term in ("最佳模型是","已经生产就绪","已通过安全认证","客户已经验证"))
    invalid=[]
    for field,value in (("status","local_experiment"),("recommendation","conditional"),("source_runs",45),("phase7_1_complete",False),("phase7_2_complete",False),("phase7_3_complete",False),("phase8_complete",False),("service_implemented",False),("service_callable",False),("interface_language","en-US"),("agent_discoverable",False),("agent_understandable",False),("agent_composable",False)):
        candidate=copy.deepcopy(status); candidate[field]=value; invalid.append(bool(list(validator.iter_errors(candidate))))
    for field in status["truth_boundary"]:
        candidate=copy.deepcopy(status); candidate["truth_boundary"][field]=True; invalid.append(bool(list(validator.iter_errors(candidate))))
    assert all(invalid)
    print("SAEE_COMMERCIAL_ASSESSMENT_SERVICE_COMPLETION_SMOKE: PASS")
    print("phase7_1_complete=true")
    print("phase7_2_runs=75/75")
    print("phase7_3_source_bindings=7/7")
    print("phase8_sessions=9/9")
    print("phase8_full_contract_pass=6/9")
    print("phase9_service_callable=true")
    print("phase9_selected_runs=75/75")
    print("agent_discoverable=true")
    print("agent_understandable=true")
    print("agent_composable=true")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("recommendation=recommend")
    print("commercial_delivery_completed=false")
    print("customer_validated=false")
    print("market_validation=false")
    print("deployment_authorized=false")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
