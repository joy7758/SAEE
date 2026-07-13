# SAEE Phase 1.98 Run Termination Contract Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: "SAEE Evaluation Run Termination Contract v0.1"
  target_customer_need: "诚实记录一次预留或已启动的评测为什么没有产生完整结果与 Evidence Case。"
  answer: recommend
  reasons_to_recommend:
    - "明确区分 Evaluation Outcome Failure 与 Runtime Failure。"
    - "人工停止、Runtime失败和输入拒绝均保留 Input、Replay Evaluation、Operator 与 Stop Authority lineage。"
    - "Partial Result 被明确排除在 Evidence、Risk 和 Decision 之外。"
    - "终止路径强制 no fake evidence，不伪造 Result 或 Evidence Case。"
  reasons_not_to_recommend:
    - "不适用于真实 Runtime、真实客户数据或生产治理。"
    - "不独立验证 Partial Result、Stop Authority、Consent 或 Permission 的外部真实性。"
  decomposition:
    - blocker: "Evaluation Run v0.1 只能记录完成路径"
      subsystem: "Evolutionary Archive / Rollback Immune System"
      fix_task: "增加独立 Termination Contract，记录人工停止、Runtime失败和输入拒绝"
      acceptance_criteria: "三类终止样例通过 lineage 与状态检查"
      status: fixed
    - blocker: "终止路径可能伪造 Evidence 引用"
      subsystem: "Evolutionary Archive / Rollback Immune System"
      fix_task: "强制 evidence_case_produced=false 且引用为 null"
      acceptance_criteria: "no_fake_evidence=3/3"
      status: fixed
    - blocker: "真实离线回放的数据和权限材料尚未验证"
      subsystem: "Sandbox Development"
      fix_task: "保留为 Phase 2 独立人工授权与验证任务"
      acceptance_criteria: "本阶段 real runtime、customer data 与 production 状态全部为 false"
      status: deferred
  final_decision: "recommend，仅限本地合成、不可执行、可离线验证的 Run Termination 记录；不推荐用于真实 Runtime 或生产环境。"
  evidence:
    docs:
      - "docs/architecture/SAEE_PHASE1_98_RUN_TERMINATION_CONTRACT.md"
    tests:
      - "scripts/saee_run_termination_contract_smoke.py"
    examples:
      - "agent-interface/architecture/examples/run-termination/"
```

## Required Design Check

1. 强化子系统：Evolutionary Archive / Rollback Immune System。
2. 改善能力：失败归档、人工停止、拒绝记录与回滚定位。
3. 安全边界：无网络、无外部代码、无权限扩张、无客户数据、无真实 Runtime 或 Agent。
4. Audit-first 风险：本功能保持为 Deployment Assurance 的免疫/证据子系统，不改变 SAEE 核心身份。
