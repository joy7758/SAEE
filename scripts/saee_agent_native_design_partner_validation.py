#!/usr/bin/env python3
"""Execute the controlled Qianfan multi-model Agent-native validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.agent_native_design_partner import build_result,run_validation


PLAN=ROOT/"agent-interface/commercial/saee-agent-native-design-partner-validation-plan.v1.0.json"
PHASE7_2_STATUS=ROOT/"agent-interface/reliability/benchmark-runs/v1.1/SAEE_PHASE7_2_EXECUTION_STATUS.json"
RECORDS=ROOT/"agent-interface/commercial/design-partner-validation/saee-agent-native-design-partner-records.v1.0.json"
RESULT=ROOT/"agent-interface/commercial/saee-agent-native-design-partner-validation-result.v1.0.json"
SCHEMA=ROOT/"schemas/saee-agent-native-design-partner-validation-result.schema.v1.0.json"
REPORT=ROOT/"docs/commercial/SAEE_AGENT_NATIVE_DESIGN_PARTNER_VALIDATION_REPORT_V1.md"


def progress(profile: str,model: str,status: str) -> None: print(f"agent_design_partner profile={profile} model={model} status={status}",flush=True)


def report(result: dict) -> str:
    return f"""# SAEE Agent-Native Design Partner Validation Report v1

## 结论

本次受控验证让三个外部推理模型分别扮演 AI Agent Platform、Governance Agent、Evaluation Agent，共执行 9 个三轮会话。它检验能力发现、非使用边界、组合方式和声明边界，不使用人工参与者。

```text
status={result['status']}
sessions_attempted={result['sessions_attempted']}
sessions_completed={result['sessions_completed']}
sessions_contract_failed={result['sessions_contract_failed']}
provider_rounds={result['provider_rounds']}
human_participants=0
```

## 可观察结果

- discovery_correct={result['discovery_correct']}/9
- non_use_boundary_correct={result['non_use_boundary_correct']}/9
- composition_correct={result['composition_correct']}/9
- claim_boundary_correct={result['claim_boundary_correct']}/9
- full_contract_pass={result['full_contract_pass']}/9
- recommendation_distribution={result['recommendation_distribution']}

这些计数描述受控提示下的结构化响应，不是模型排名、智能分数或市场采用率。

## 三轮任务

1. 发现：责任声明的证据是否充分时，能否识别 `saee-evidence-adequacy`。
2. 非使用：实时授权时，能否拒绝让 SAEE 承担 allow/deny，并选择授权策略引擎。
3. 组合：能否组合 Observability、SAEE Evidence Adequacy 和 Authorization Policy Engine，并拒绝安全、合规、部署批准声明。

## 当前依赖

- source_benchmark_reference={result['source_benchmark_reference']}
- phase7_2_dependency_complete={str(result['phase7_2_dependency_complete']).lower()}

当 Phase 7.2 未完成时，本结果是 provisional，只能证明验证协议可执行，不能关闭 Phase 8。

## 真值边界

- customer_contacted=false
- customer_data_used=false
- market_validation=false
- adoption_validated=false
- external_world_actions=false
- production_ready=false
"""


def main() -> int:
    key=os.environ.get("QIANFAN_API_KEY","")
    if not key: raise SystemExit("QIANFAN_API_KEY_MISSING")
    plan=json.loads(PLAN.read_text(encoding="utf-8")); status=json.loads(PHASE7_2_STATUS.read_text(encoding="utf-8"))
    records=run_validation(key,plan["partner_profiles"],progress=progress)
    phase_complete=status["execution_complete"] is True
    source="agent-interface/reliability/saee-extended-internal-reliability-benchmark-result.v1.1.json" if phase_complete else plan["source_benchmark"]
    result=build_result(records,phase_complete,source)
    errors=list(Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).iter_errors(result))
    if errors: raise ValueError(f"AGENT_DESIGN_PARTNER_RESULT_INVALID:{errors[0].message}")
    RECORDS.write_text(json.dumps({"records_version":"1.0","validation_id":result["validation_id"],"raw_provider_content_stored":False,"hidden_reasoning_stored":False,"records":records},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.write_text(report(result),encoding="utf-8")
    print("SAEE_AGENT_NATIVE_DESIGN_PARTNER_VALIDATION_RESULT")
    for key_name in ("status","sessions_attempted","sessions_completed","sessions_contract_failed","provider_rounds","discovery_correct","non_use_boundary_correct","composition_correct","claim_boundary_correct","full_contract_pass"): print(f"{key_name}={result[key_name]}")
    print("human_participants=0")
    print("market_validation=false")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
