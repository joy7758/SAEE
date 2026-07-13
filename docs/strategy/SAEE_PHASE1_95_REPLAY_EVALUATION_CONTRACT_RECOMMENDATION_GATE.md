# SAEE Phase 1.95 Replay Evaluation Contract Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: "SAEE Replay Evaluation Contract v0.1"
  target_customer_need: "在不执行真实回放的前提下，保存 Observation 治理上下文到 Evaluation Input 的可追溯绑定。"
  answer: recommend
  reasons_to_recommend:
    - "严格绑定本地 Replay Contract、Observation Envelope 与 Evaluation Input 的路径、标识和 SHA-256。"
    - "Consent、数据使用权限和转换来源必须显式传播，避免隐藏转换。"
    - "声明性映射不可执行，且明确禁止 Replay 生成 Risk、自动 Decision 或部署授权。"
    - "离线、确定性、合成范围可被独立重复验证。"
  reasons_not_to_recommend:
    - "不适用于真实 Replay、真实客户数据、生产部署或外部真实性证明。"
    - "不验证 Consent、Permission、Provenance 或 Observation 的外部有效性。"
  decomposition:
    - blocker: "真实 Replay 与客户数据治理尚未实现和验证"
      subsystem: "Sandbox Development / Evolutionary Archive"
      fix_task: "保留为 Phase 2 Consent-First Offline Replay 的独立人工授权任务"
      acceptance_criteria: "本阶段所有执行、客户数据和生产状态均保持 false"
      status: deferred
    - blocker: "真实风险概率模型尚未实现"
      subsystem: "Pareto Fitness Evaluation"
      fix_task: "仅保存 synthetic_rule_reference，不从 Trace 或 Replay 生成 Risk"
      acceptance_criteria: "risk_probability_measured=false 且 replay_generated_risk=false"
      status: fixed
    - blocker: "转换链可能隐式丢失治理引用"
      subsystem: "Evolutionary Archive / Rollback Immune System"
      fix_task: "强制校验 Consent、Permission、Transformation 和五层 Lineage"
      acceptance_criteria: "三份样例全部通过传播与溯源完整性检查"
      status: fixed
  final_decision: "recommend，仅限本地合成、契约定义、不可执行的内部保障组件；不推荐用于真实 Replay 或生产环境。"
  evidence:
    docs:
      - "docs/architecture/SAEE_PHASE1_95_REPLAY_EVALUATION_CONTRACT.md"
    tests:
      - "scripts/saee_replay_evaluation_contract_smoke.py"
    examples:
      - "agent-interface/architecture/examples/replay-evaluation/"
```

## Required Design Check

1. 强化子系统：Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）。
2. 改善能力：来源链归档、回滚定位和受控选择输入的可追溯性。
3. 边界：无网络、无外部代码、无权限扩张、无客户数据、无真实 Replay。
4. Audit-first 风险：通过把本功能限定为 Deployment Assurance 的档案/证据子系统而避免；不改变 SAEE 核心身份。
