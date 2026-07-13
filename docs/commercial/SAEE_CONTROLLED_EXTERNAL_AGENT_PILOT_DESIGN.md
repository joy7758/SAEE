# SAEE Controlled External Agent Pilot Design v0.1

## 1. Purpose / 目的

This document defines the requirements for a possible future controlled external Agent Pilot. It does not authorize or execute a Pilot.

本文定义未来可能开展的受控外部智能体 Pilot（试点）所需条件，不授权也不执行试点。

```text
Pilot Design != Pilot Execution
Approval Gate != Approval Granted
Design Partner != Customer
Simulation != External Validation
```

## 2. Pilot Scope / 试点范围

未来试点仅可考虑：

- 合成数据或经过单独批准的受控证据；
- 有明确请求数量、大小、持续时间和用途边界的 Agent 工作流；
- 固定的 `saee.evidence-adequacy` 能力，不允许动态注册 Tool 或 Profile；
- 全程由明确责任人监督的证据充分性评估。

不得纳入：无限制生产 Agent、自动部署、外部副作用、未经控制的客户数据、跨 Tenant 数据或执行型内容。

## 3. Agent Eligibility Criteria / Agent 准入条件

未来候选 Agent 必须提供：

1. 身份声明；
2. 用途声明；
3. 能力描述；
4. 调用上下文。

这些声明只是待验证输入，不构成认证、信任、组织授权或调用许可。外部 Agent 必须通过独立身份、权限和安全控制后，才能被考虑进入真实试点。

## 4. Data Requirements / 数据要求

允许的数据类别：

- 已批准的证据对象；
- 已批准且不会自动获取的惰性引用；
- 合成数据集；
- 具有明确用途和范围的受控样本。

禁止的数据类别：

- 密码、API Key、Token、私钥及其他 secrets；
- hidden reasoning / chain-of-thought；
- 未经批准的个人数据或无限制客户数据；
- 可执行内容和不可信外部资源；
- 其他 Tenant 的数据。

当前 `data_collected=false`、`customer_data_allowed=false`。本设计不构成数据处理许可。

## 5. Environment Requirements / 环境要求

真实试点前必须提供：隔离环境、可复现配置、受限日志、最小权限、失败关闭、恢复与回滚能力。环境不得自动扩大权限、访问外部网络或产生外部副作用。

## 6. Approval Gates / 审批门

五道门均必须存在，并由相应责任主体提供可核验证据：

| Gate | Required evidence | Current status |
|---|---|---|
| Technical readiness | 固定契约、负例、可复现性和失败关闭证据 | `NOT_GRANTED` |
| Security review | 威胁模型、秘密处理、访问控制与事故响应 | `NOT_GRANTED` |
| Data approval | 数据来源、授权、用途、保留与删除边界 | `NOT_GRANTED` |
| Human responsibility assignment | 责任人、停止权和复核职责 | `NOT_GRANTED` |
| Execution authorization | 明确范围、期限与可撤销的最终人工批准 | `NOT_GRANTED` |

当前 `readiness_gate=HOLD`、`approval_granted=false`、`pilot_start_authorized=false`。门的定义不等于门已通过。

## 7. Evaluation Metrics / 评估指标

技术指标：Tool 调用正确性、契约符合性、边界保持能力。

证据指标：缺失证据识别、reason code 一致性。

人工指标：报告是否帮助授权人员理解证据缺口。

本阶段不把收入、市场契合度或商业成功定义为技术试点指标，也不把 `SUPPORTED` 解释为安全、合规或部署批准。

## 8. Exit Criteria / 退出条件

未来试点成功完成至少要求：执行可复现、越界可检测、生成受限证据结果、局限被记录。

下列任一事件触发失败和停止：未授权动作、数据边界违规、秘密暴露、把证据结果升级为未经支持的信任/批准/安全/合规声明。

## 9. Rollback Model / 回滚模型

真实试点前必须批准：停止条件、数据删除计划、访问撤销机制、产物保留策略，并指定终止权限责任人。当前这些控制仅为要求，`plans_approved=false`、`termination_authority_assigned=false`。

## 10. Current Truth Surface / 当前真值表面

```text
pilot_stage=design_only
external_agent_connected=false
pilot_executed=false
data_collected=false
approval_granted=false
customer_validated=false
external_validation_completed=false
production_enabled=false
production_ready=false
```

本文件可作为未来 Pilot 申请的输入，但不能替代真实实现证据、安全/隐私审查、数据授权或明确人工批准。

## 11. Controlled Pilot Simulation Reference / 受控 Pilot 模拟引用

Phase 5.3 使用以下本地离线资产验证本设计的治理逻辑：

- 状态机 Schema：`agent-interface/integration/saee-pilot-state-machine.schema.v0.1.json`；
- Gate 模型：`agent-interface/integration/pilot-gates.v0.1.json`；
- 合成场景：`agent-interface/integration/pilot-simulation/`；
- 纯内存模拟器：`saee_backend/services/pilot_simulator.py`；
- 评估器：`saee_backend/services/pilot_simulation_evaluator.py`；
- 机器结果：`agent-interface/integration/saee-controlled-pilot-simulation-result.v0.1.json`；
- 说明：`docs/commercial/SAEE_CONTROLLED_PILOT_SIMULATION.md`。

模拟通过不改变本设计中的审批门状态，不授权或执行真实 Pilot，也不构成外部 Agent、客户、数据删除或生产验证。

## 12. External Agent Pilot Readiness Review Reference / 外部 Agent Pilot 就绪性审查引用

Phase 5.4 通过以下只读资产区分已完成的设计证据和仍缺失的操作性证据：

- Readiness Schema：`agent-interface/integration/saee-external-agent-pilot-readiness.schema.v0.1.json`；
- 当前矩阵：`agent-interface/integration/saee-external-agent-pilot-readiness.v0.1.json`；
- 评估器：`saee_backend/services/external_agent_pilot_readiness.py`；
- 机器结果：`agent-interface/integration/saee-external-agent-pilot-readiness-result.v0.1.json`；
- 审查报告：`docs/commercial/SAEE_EXTERNAL_AGENT_PILOT_READINESS_REVIEW.md`。

当前结论固定为 `NOT_READY`。Readiness Review 不批准 Pilot，不改变五道审批门，也不提供执行授权、客户验证或生产就绪证明。
