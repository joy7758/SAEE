# SAEE External Evaluation Pilot Preparation v0.1 推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE External Evaluation Pilot Preparation v0.1
  target_customer_need: 在任何真实试点前获得可检索、可停止、可复核的准备规范
  answer: recommend
  reasons_to_recommend:
    - 数据对象、三种候选来源、标注标签、隐私许可清单和停止门均文件化
    - 当前 readiness 明确为 NOT_READY，不把准备材料升级为实验结果
    - 所有验证离线确定，不运行真实智能体或外部代码
  reasons_not_to_recommend:
    - 不推荐依据本准备包启动真实试点或声称外部验证
  decomposition:
    - blocker: 数据源和权限尚未选择或批准
      subsystem: Global Sensing
      fix_task: 未来单独定义并审批 pilot dataset specification
      acceptance_criteria: 数据来源、所有权、许可、隐私、保留和删除均有证据
      status: deferred
    - blocker: 码本、环境和复现步骤尚未完成 pilot 审批与测试
      subsystem: Pareto Fitness Evaluation and Evolutionary Archive / Rollback Immune System
      fix_task: 在执行前冻结环境、审批码本并完成受控预演
      acceptance_criteria: readiness 的所有 ready_requires 均有文件化证据
      status: deferred
  final_decision: 推荐作为 preparation_only 内部研究准备包；真实试点仍为 NOT_READY，且不授权数据采集、智能体执行或外部验证声明
  evidence:
    docs:
      - docs/evaluation/SAEE_EXTERNAL_EVALUATION_PILOT_PREPARATION.md
      - docs/evaluation/SAEE_ANNOTATION_CODEBOOK.md
      - docs/evaluation/SAEE_PILOT_PRIVACY_CHECKLIST.md
      - docs/evaluation/SAEE_PILOT_EXECUTION_SAFETY_GATE.md
    tests:
      - scripts/saee_pilot_preparation_smoke.py
    examples:
      - agent-interface/evaluation/saee-pilot-preparation.v0.1.json
```

## Required Design Check

1. 强化未来 `Global Sensing` 输入治理、`Pareto Fitness Evaluation` 和 `Evolutionary Archive / Rollback Immune System` 的可复查性。
2. 改善未来感知、选择和档案准备，但不新增分叉、变异或外部执行能力。
3. 保留安全、许可、供应链和权限边界：无数据采集、无网络、无安装、无未知代码、无权限扩大。
4. 不转向 audit-first：该准备包只是 Digital Biosphere Evolution Engine 的证据/免疫子系统研究协议。

