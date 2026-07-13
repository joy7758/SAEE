# SAEE Internal Agent Pilot Plan v1.0

## 目标

在任何外部生态验证之前，用 SAEE 自身的内部 Agent 工作流建立可重复的内部价值验证路径。

```text
Agent Task
    ↓
Scenario Definition
    ↓
SAEE Rehearsal
    ↓
Observation
    ↓
Reliability Evaluation
    ↓
Evidence Evaluation
    ↓
Recommendation
```

当前计划已经产生第一批内部执行结果：`agent-interface/pilot/saee-internal-agent-pilot-execution-result.v1.0.json`。

```text
internal_agent_pilot=true
pilot_executed=true
real_internal_execution=true
external_validation=false
external_participants=false
customer_data=false
production_execution=false
adoption_validated=false
production_ready=false
```

## 场景

| 场景 | Agent 类型 | 主要检查 |
|---|---|---|
| `CODE_CHANGE_WORKFLOW` | `coding_agent` | execution、evidence、recovery、boundary |
| `RESEARCH_WORKFLOW` | `research_agent` | evidence、traceability、boundary |
| `AUTOMATION_WORKFLOW` | `automation_agent` | execution、recovery、tool usage、boundary |
| `AGENT_DELEGATION_WORKFLOW` | `evaluation_agent` | delegation、evidence、traceability、boundary |

## 与旧创始人自测的关系

仓库已有 `internal_founder_pilot_evidence_run`，它属于商业准备台账中的历史创始人自测记录。本计划不删除、不重写该事实，也不把它解释为四场景 Agent Pilot、外部验证或客户验证。

## 建议语义

- `CONTINUE`：现有内部证据支持继续当前受控工作流。
- `REPLAN`：发现可修复缺口，应先调整任务或场景。
- `HUMAN_REVIEW_REQUIRED`：涉及重大外部动作或权限时需要独立授权；不是主要能力偏好验证方式。
- `STOP`：存在禁止边界或证据无法支持继续。

## Agent 入口

- Plan：`agent-interface/pilot/saee-internal-agent-pilot-plan.v0.1.json`
- Scenario schema：`schemas/saee-internal-agent-pilot.schema.v0.1.json`
- Evidence schema：`schemas/saee-internal-pilot-evidence.schema.v0.1.json`
- Planner：`saee_backend/services/internal_agent_pilot.py`
- Validator：`saee_backend/services/internal_agent_pilot_validator.py`
- Validation：`python3 scripts/saee_internal_agent_pilot_smoke.py`
- Execution result：`agent-interface/pilot/saee-internal-agent-pilot-execution-result.v1.0.json`
- Execution validation：`python3 scripts/saee_internal_agent_pilot_execution_smoke.py`

## 限制

- 没有实际运行 Codex、本地 Agent 或多模型 Agent。
- 没有真实 Pilot 结果、改进对照或因果结论。
- 内部 Pilot 将来即使执行，也不证明外部价值、生态采用或市场需求。
- 任何外部世界动作仍需独立明确授权。
