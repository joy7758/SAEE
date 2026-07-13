# SAEE v3.0 Deployment Assurance Evolution Proposal

状态：`accepted_projection_phase1_local_only`。

## Proposed change

在既有 L3 Engineering / Runtime / Experiment Layer 内新增一个非权威的 `Deployment Assurance Projection`，用九层 contract 把 Task、Environment、Observation、Evaluation、Evidence、Risk 和 Decision 串联。

## Why a proposal is required

原始九层方案包含 Governance、Agent Runtime 和 Post-deployment Feedback。如果直接作为 canonical core 实现，会产生四类风险：

1. 把 SAEE 推向 audit-first/governance-first；
2. 把外部 Agent execution 引入 SAEE；
3. 让 production feedback 反向修改 frozen scientific object；
4. 把当前不存在的持续监控能力写成产品事实。

因此必须先定义为 L3 projection，并保持所有权威和执行边界。

## Evolution-loop contribution

- `Global Sensing`：任务与获批反馈契约；
- `Ecological World Model`：业务 impact/exposure 与场景权重；
- `Counterfactual Simulation`：部署变化和故障分支；
- `Sandbox Development`：外部客户控制沙盒边界；
- `Pareto Fitness Evaluation`：能力、稳定、漂移、安全、成本；
- `Archive / Rollback Immune System`：证据、风险、决策和版本历史。

## Safety and identity resolution

- SAEE 只观察外部沙盒，不直接执行外部世界；
- external code 永不成为 genome；
- feedback 只进入 Global Sensing，不直接修改 L1/L2 或生产 Agent；
- governance/evidence 支撑闭环，不成为项目核心身份；
- 当前所有能力升级保持 `implemented=false`。

## Proposal decision

架构审查需要确认：

```text
Accepted: v3 is an L3 Deployment Assurance Projection on Evidence-Based Evaluation Architecture.
```

Phase 1 仅获准实现本地合成 Evidence Case Object、风险估计 reference slice 与 Decision Support。Runtime/Memory/Tool Trace adapter、post-deployment feedback、真实 Agent、外部数据和网站升级仍未获准。
