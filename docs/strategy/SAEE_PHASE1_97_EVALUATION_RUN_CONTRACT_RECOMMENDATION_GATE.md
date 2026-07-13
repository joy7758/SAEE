# SAEE Phase 1.97 Evaluation Run Contract Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: "SAEE Evaluation Run Contract v0.1"
  target_customer_need: "在不接入真实 Evaluator Runtime 的前提下，回答某个 Evidence Case 来自哪个输入、哪次运行和哪些声明版本。"
  answer: recommend
  reasons_to_recommend:
    - "Input、Replay Evaluation、Result 和 Evidence Case 均有摘要绑定。"
    - "Evaluator、Grader、Criteria 版本必须显式记录，重复运行必须保持版本与结果一致。"
    - "Run 与 Evidence Case 支持通过独立契约索引双向查询。"
    - "严格关闭真实 Runtime、Agent、工具、网络、风险概率、自动决策和部署权限。"
  reasons_not_to_recommend:
    - "不适用于真实 Evaluator Runtime、真实 Agent、客户数据或生产部署。"
    - "不独立证明 Evaluator、Grader、Criteria、Result 或 Evidence Artifact 的外部真实性。"
  decomposition:
    - blocker: "Evaluation Input 到 Evidence Case 缺少运行实例溯源"
      subsystem: "Evolutionary Archive / Rollback Immune System"
      fix_task: "增加 Evaluation Run、Result 和 Evidence Case 的显式 lineage 与摘要绑定"
      acceptance_criteria: "三份合成 Run Contract 全部通过正向 lineage 和 Evidence 反查"
      status: fixed
    - blocker: "真实 Evaluator Runtime 尚未实现和验证"
      subsystem: "Sandbox Development"
      fix_task: "本阶段限定为本地合成生命周期记录，真实 Runtime 留待独立阶段"
      acceptance_criteria: "real_evaluator_runtime_executed=false 且 real_agent_executed=false"
      status: deferred
    - blocker: "版本引用没有外部真实性材料"
      subsystem: "Evolutionary Archive / Rollback Immune System"
      fix_task: "明确记录版本但保留 provenance independently verified=false"
      acceptance_criteria: "不得把声明版本描述为外部验证来源"
      status: fixed
  final_decision: "recommend，仅限本地合成、不可执行、可离线验证的 Evaluation Run 溯源契约；不推荐用于真实 Runtime 或生产环境。"
  evidence:
    docs:
      - "docs/architecture/SAEE_PHASE1_97_EVALUATION_RUN_CONTRACT.md"
    tests:
      - "scripts/saee_evaluation_run_contract_smoke.py"
    examples:
      - "agent-interface/architecture/examples/evaluation-run/"
```

## Required Design Check

1. 强化子系统：Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）。
2. 改善能力：运行来源归档、版本比较、重复运行复核和结果回滚定位。
3. 安全边界：无外部代码、无网络、无权限扩张、无客户数据、无真实 Evaluator Runtime 或 Agent。
4. Audit-first 风险：功能保持为 Deployment Assurance 的档案/证据子系统，不改变 SAEE 核心身份。
