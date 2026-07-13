# SAEE Pilot Dataset Specification v0.1 推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE Pilot Dataset Specification v0.1
  target_customer_need: 在采集任何试点数据前获得严格、智能体可读且可验证的数据契约
  answer: recommend
  reasons_to_recommend:
    - 四类实体使用严格 JSON Schema 并显式绑定 episode
    - trace 固定为 observation-only，annotation 标签具有一致性约束
    - manifest 和 readiness 清单明确 dataset_exists=false 与 NOT_READY
    - smoke 只使用内存合成对象且不生成数据集
  reasons_not_to_recommend:
    - 不推荐把规范描述为数据可用、质量通过、标注完成或外部验证
  decomposition:
    - blocker: 数据来源、权限和隐私审查尚不存在
      subsystem: Global Sensing
      fix_task: 在未来 readiness review 中验证来源批准和数据治理证据
      acceptance_criteria: source、permission、privacy 三项均有文件化审批
      status: deferred
    - blocker: 跨实体 validation pipeline 和真实 pilot 尚未运行
      subsystem: Pareto Fitness Evaluation and Evolutionary Archive / Rollback Immune System
      fix_task: 先完成执行就绪审查，再决定是否授权合成 pilot
      acceptance_criteria: schema frozen、annotation approved、validation pipeline tested
      status: deferred
  final_decision: 推荐作为 specification_only 本地契约；数据集和试点执行仍为 NOT_READY
  evidence:
    docs:
      - docs/evaluation/SAEE_PILOT_DATASET_SPECIFICATION.md
      - docs/evaluation/SAEE_DATASET_QUALITY_CONTROL.md
      - docs/evaluation/SAEE_DATASET_READINESS_CHECKLIST.md
    tests:
      - scripts/saee_dataset_specification_smoke.py
    examples:
      - agent-interface/evaluation/saee-pilot-dataset-manifest.v0.1.json
```

## Required Design Check

1. 强化 `Global Sensing` 输入契约、`Pareto Fitness Evaluation` 和档案/回滚免疫系统。
2. 改善未来感知数据质量与选择可复查性，不执行世界、不新增分叉或变异。
3. 保留许可、隐私、供应链和权限边界：无采集、无网络、无未知代码、无真实身份、无权限扩大。
4. 不转向 audit-first：数据集规范只服务于 Digital Biosphere Evolution Engine 的受控评估子系统。

