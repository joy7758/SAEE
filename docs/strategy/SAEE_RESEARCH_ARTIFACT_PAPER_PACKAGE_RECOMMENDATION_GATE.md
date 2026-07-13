# SAEE Research Artifact Paper Package v0.1 推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE Research Artifact Paper Package v0.1
  target_customer_need: 为未来学术论文组织本地、可检索、可复查的支持材料
  answer: recommend
  reasons_to_recommend:
    - PR-1 至 PR-6.5 的文件、命令、合成结果和限制均有仓库真源
    - artifact package 只重组既有研究材料，不修改 evaluator、schema 或运行时
    - manifest、实验表和图规格均保留 synthetic/offline/local 边界
  reasons_not_to_recommend:
    - 不推荐把该包表述为论文投稿、发表、第三方复现、标准兼容或生产验证
  decomposition:
    - blocker: 研究成果分散，未来论文无法从单一入口发现
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: 建立研究概览、结构、架构、实验、图规格、清单和机器 manifest
      acceptance_criteria: 所有引用路径存在且 research artifact smoke 通过
      status: fixed
    - blocker: 本地回归结果容易被误写为外部科学结论
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: 在每个研究面和 manifest 中固定 truth boundary
      acceptance_criteria: unsupported_claims=0 且 publication_status=not_submitted
      status: fixed
    - blocker: 尚无 clean-room 复现、版本矩阵和第三方验证
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: 未来独立任务处理，不在本 PR 扩展
      acceptance_criteria: external_validation=false 与 production_ready=false 保持不变
      status: deferred
  final_decision: 推荐作为本地论文支持材料包；禁止升级为投稿、发表、外部验证或商业宣传
  evidence:
    docs:
      - docs/research-artifact/SAEE_RESEARCH_ARTIFACT_OVERVIEW.md
      - docs/research-artifact/SAEE_EXPERIMENT_SUMMARY.md
      - docs/research-artifact/PAPER_ARTIFACT_CHECKLIST.md
    tests:
      - scripts/saee_research_artifact_smoke.py
    examples:
      - agent-interface/research-artifact/saee-artifact-manifest.v0.1.json
```

## Required Design Check

1. 强化 `Evolutionary Archive / Rollback Immune System`，让证据研究分支的来源、实验与边界可回查。
2. 改善 archive 和 rollback，不改变感知、分叉、变异、选择或沙盒执行语义。
3. 保留安全、许可证、供应链和权限边界：无网络、无外部数据、无外部代码执行、无权限扩大。
4. 不把 SAEE 推回 audit-first framing：所有文档都说明证据层只是数字生物圈进化引擎的免疫子系统。
