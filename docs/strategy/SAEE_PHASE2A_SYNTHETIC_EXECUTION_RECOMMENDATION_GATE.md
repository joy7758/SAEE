# SAEE Phase 2A Synthetic Execution Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: "SAEE Phase 2A Synthetic Assurance Pipeline Execution"
  target_customer_need: "验证冻结的保障契约能否在无外部副作用的本地合成环境中形成完成或终止生命周期输出。"
  answer: recommend
  reasons_to_recommend:
    - "每次运行前强制通过 Phase 2A Readiness Gate。"
    - "只接受三个仓库内允许列表 Replay Evaluation Contract，并校验路径和 SHA-256。"
    - "校验 Replay Contract 后加载既有 Evaluation Input，再使用本地合成 Case Builder；不执行 Mapping Rule 代码或 Observation 元数据重建。"
    - "Completed 与 Terminated 严格二选一，只有 Completed 路径产生 Evidence Case。"
    - "无 Agent、Tool、Network、客户数据、外部代码或依赖安装。"
  reasons_not_to_recommend:
    - "不适用于真实 Agent、真实客户数据、动态 Adapter 或生产环境。"
    - "不独立证明 Consent、Permission、Provenance、Result 或 Evidence 的外部真实性。"
  decomposition:
    - blocker: "固定 Evaluation Input 流水线尚未证明可执行"
      subsystem: "Sandbox Development / Pareto Fitness Evaluation"
      fix_task: "实现固定允许列表、本地合成、确定性的 Evaluation Input Pipeline Runner"
      acceptance_criteria: "completed_path_valid=true 且 termination_path_valid=true"
      status: fixed
    - blocker: "Runner 可能执行声明式 Mapping Rule 或外部输入"
      subsystem: "Sandbox Development"
      fix_task: "只使用固定内部 Profile，Mapping Rule 必须 executable=false，目录外输入必须拒绝"
      acceptance_criteria: "mapping_rules_executed_as_code=false 且 outside_allowlist_rejected=true"
      status: fixed
    - blocker: "真实 Agent、Adapter 和客户数据尚未授权"
      subsystem: "Global Sensing / Sandbox Development"
      fix_task: "保留给 Phase 2B 及后续独立审查"
      acceptance_criteria: "real_agent_executed=false、customer_data_processed=false、production_ready=false"
      status: deferred
  final_decision: "recommend，仅限本地合成、固定允许列表、以既有 Evaluation Input 为起点且无外部副作用的 Phase 2A 执行；未实现完整离线 Replay，不推荐用于真实 Agent、客户数据或生产环境。"
  evidence:
    docs:
      - "docs/architecture/SAEE_PHASE2A_SYNTHETIC_EXECUTION.md"
      - "docs/strategy/SAEE_PHASE2A_READINESS_GATE.md"
    tests:
      - "scripts/saee_phase2a_execution_smoke.py"
      - "scripts/saee_phase2a_readiness_gate.py"
    examples:
      - "agent-interface/architecture/examples/replay-evaluation/"
```

## Required Design Check

1. 强化子系统：Sandbox Development、Pareto Fitness Evaluation、Evolutionary Archive / Rollback Immune System。
2. 改善能力：受控转换、选择输入、完成/终止分叉和可重复归档。
3. 安全边界：无网络、无外部代码、无权限扩张、无客户数据、无真实 Agent。
4. Audit-first 风险：执行验证服务于 Deployment Assurance 和演化沙盒，不将审计重新定义为项目核心。
