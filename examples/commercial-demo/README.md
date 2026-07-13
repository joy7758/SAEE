# SAEE Agent Readiness Assessment Demo

本 Demo 只编排既有本地资产，不创建新 Runtime，也不访问客户或外部系统。

```text
Agent
  ↓
Scenario
  ↓
Controlled Rehearsal / Existing Run Corpus
  ↓
Observation
  ↓
Commercial Assessment Service
  ↓
Chinese Readiness Report
```

## 1. 选择合成输入

使用既有 Phase 9 示例：

```text
agent-interface/commercial/examples/saee-commercial-assessment-request.v1.0.json
```

## 2. 生成结构化 Assessment

```bash
python3 scripts/saee_agent_cli.py generate-commercial-assessment \
  --input agent-interface/commercial/examples/saee-commercial-assessment-request.v1.0.json
```

或保存本地响应：

```bash
python3 scripts/saee_commercial_assessment_service.py \
  --input agent-interface/commercial/examples/saee-commercial-assessment-request.v1.0.json \
  --output /tmp/saee-commercial-assessment-response.json
```

## 3. 投影为客户可读报告

按照 `docs/commercial/SAEE_AGENT_READINESS_REPORT_TEMPLATE.md` 映射五个可靠性维度、Evidence Adequacy、失败类型和后续建议。当前未实现自动客户报告生成器；模板投影仍是独立包装步骤。

## 4. 验证

```bash
python3 scripts/saee_commercial_assessment_service_smoke.py
python3 scripts/saee_agent_readiness_productization_smoke.py
```

## 边界

```text
local_demo=true
synthetic_inputs=true
customer_data=false
commercial_delivery_completed=false
production_service=false
deployment_authorized=false
```

