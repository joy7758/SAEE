# SAEE External Evaluation Design v0.1 推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE External Evaluation Design v0.1
  target_customer_need: 为更接近真实智能体的证据充分性研究建立严谨且不越界的实验协议
  answer: recommend
  reasons_to_recommend:
    - 研究问题、实验单位、四种证据条件、三类 baseline 和四项主指标均已明确
    - 数据许可、隐私、标注、一致性、统计和独立验证都设置了未来执行门
    - 元数据和 smoke 强制所有执行与外部结果状态为 false
  reasons_not_to_recommend:
    - 不推荐把设计文档描述为已完成真实实验或外部验证
  decomposition:
    - blocker: 论文只说明需要外部评估，没有可执行协议
      subsystem: Global Sensing and Evolutionary Archive / Rollback Immune System
      fix_task: 固定 Code Agent Tool Execution 场景、条件、baseline、指标和阶段门
      acceptance_criteria: 10 个协议章节和机器元数据通过离线 smoke
      status: fixed
    - blocker: 真实数据来源、许可、隐私和标注尚未完成
      subsystem: Global Sensing
      fix_task: 后续原型与数据准备任务必须逐门审批
      acceptance_criteria: 当前 dataset_collected=false 和 external_data_used=false
      status: deferred
    - blocker: baseline 和 SAEE 外部比较尚未执行
      subsystem: Pareto Fitness Evaluation
      fix_task: 后续实现共享输入契约的评估原型
      acceptance_criteria: 当前 baseline_implemented=false、results_available=false
      status: deferred
  final_decision: 推荐作为 design_only 研究协议；不授权数据采集、真实智能体执行、外部比较或结果声明
  evidence:
    docs:
      - docs/evaluation/SAEE_EXTERNAL_EVALUATION_DESIGN.md
      - docs/evaluation/EVALUATION_CLAIMS_BOUNDARY.md
    tests:
      - scripts/saee_evaluation_design_smoke.py
    examples:
      - agent-interface/evaluation/saee-external-evaluation-design.v0.1.json
```

## Required Design Check

1. 强化 `Global Sensing`、`Pareto Fitness Evaluation` 和 `Evolutionary Archive / Rollback Immune System` 的未来评估方法，但当前不摄取外部信号。
2. 改善未来感知、选择与档案决策；本 PR 只建立协议，不改变运行时或演化机制。
3. 保留安全、许可、隐私、供应链和权限边界：无网络、无外部数据、无真实智能体、无未知代码执行、无权限扩大。
4. 不把 SAEE 改写成 audit-first 平台：协议评估的是证据子系统，不重构 Digital Biosphere Evolution Engine 的核心定位。
