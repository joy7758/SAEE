# SAEE 开发宪法 v1.1 推荐门

## Initial Result

```yaml
recommendation_gate:
  feature_or_direction: SAEE Development Constitution v1.1 and Agent Evidence Project integration
  target_customer_need: 让智能体能够发现、组合并复核 SAEE 的演化评估与证据能力，同时防止重复建设和证据优先重构
  answer: conditional
  reasons_to_recommend:
    - Agent Evidence Project 的 receipt、integrity、provenance 和 completeness 能力可强化 Evolutionary Archive / Rollback Immune System
    - 文件化宪法可让编码、检索和引用智能体在修改前解析同一组边界
  reasons_not_to_recommend:
    - 旧 v1.0 草案把可信证据判断写成 SAEE 唯一使命，会把 Digital Biosphere Evolution Engine 推回 audit-first
    - SAEE 已有 evaluate_evidence、receipt 和局部 trace normalization，直接复制会重复建设
    - agent-evidence-layer 当前不能作为已完成迁移或规范 SAEE capability 的证据
    - signature 与 digest 不能证明原始事件真实性、身份真实性或记录完整性
  decomposition:
    - blocker: audit_first_identity_conflict
      subsystem: architecture_governance
      fix_task: 恢复 Digital Biosphere Evolution Engine 为最高工程核心，把证据放入免疫子系统
      acceptance_criteria: 宪法和机器契约同时声明 audit_first_reframe=false
      status: fixed
    - blocker: duplicate_implementation_risk
      subsystem: capability_governance
      fix_task: 强制读取 canonical_inventory 并列出必须复用的规范能力
      acceptance_criteria: 台账 smoke 通过且宪法包含 reuse-before-build 迁移门
      status: fixed
    - blocker: source_provenance_not_frozen
      subsystem: evidence_and_immune_subsystem
      fix_task: 未来从干净 commit 生成 source/license manifest 后再做逐文件迁移
      acceptance_criteria: SOURCE_PROVENANCE_FREEZE gate 有可复现 manifest
      status: deferred
    - blocker: runtime_and_trust_chain_missing
      subsystem: evidence_and_immune_subsystem
      fix_task: 未来以 adapter 和 canonical inventory 变更分别证明运行时接入与 trusted trace conversion
      acceptance_criteria: code、schema、tests、Agent-readable surfaces 与 ledger 一致
      status: deferred
    - blocker: staged_truth_ambiguity
      subsystem: architecture_governance
      fix_task: 将宪法归属、代码迁移、运行时接入、外部验证、客户验证和生产就绪分开
      acceptance_criteria: 机器契约的六个 truth_boundary 字段保持独立
      status: fixed
```

## Capability And Duplicate-Build Classification

```text
target=Agent Evidence Project integration into SAEE
overall_classification=partial
constitutional_ownership=implemented
source_code_adoption=design_only
runtime_integration=missing
canonical_inventory_change=none_this_change
```

本分类基于 2026-07-14 读取的 `capability-package/manifest.json#canonical_inventory`、相关 schema / service / example / smoke，以及历史 receipt crosswalk。能力实时事实仍以规范清单为唯一真源。

## Required Design Check

1. 强化 `Evolutionary Archive / Rollback Immune System`，并为 sensing、simulation 与 fitness selection 提供可复核证据上下文。
2. 改善 archive、rollback 和 selection；本次不增加外部执行。
3. 保留安全、许可证、供应链、最小权限和 source provenance 边界；没有复制外部代码。
4. 证据被明确限制为免疫子系统，`audit_first_reframe=false`。

## Final Result

`recommend`

推荐把 Agent Evidence Project 在宪法、模块注册表和机器入口中正式纳入 SAEE Evidence and Immune Subsystem。该推荐只覆盖治理与架构归属，不推荐把未清理的源仓库直接复制、把 signature 升级为真实性证明、把缺失能力写成 implemented，或宣称运行时接入、客户验证、发布和生产就绪。

## Program Mainline Correction

```yaml
program_mainline_gate:
  question: 如果目标是受控完成 SAEE 与 Agent Evidence 合并，并最终形成三个客户版本，是否推荐 SAEE 当前方案？
  answer: recommend
  mainline: integrate_saee_and_agent_evidence_project_under_migration_gates
  target_customer_versions:
    - SAEE Evidence
    - SAEE Evaluation
    - SAEE Governance
  secondary: use_saee_to_supervise_and_test_the_integration_process
  reasons_to_recommend:
    - 宪法已经把 Agent Evidence 放入 Evidence and Immune Subsystem，并定义逐门迁移纪律
    - SAEE 自用监督可为合并提供可复核证据、漂移信号与回滚上下文
    - 三个目标客户版本明确区分 Evidence、Evaluation 与 Governance
  blockers:
    - source_code_migrated=false
    - runtime_integrated=false
    - customer_validated=false
    - product_launched=false
    - production_ready=false
  drift_rule: Commander或角色提示不得把监督测试副线提升为主线；发现时必须输出MAINLINE_DRIFT_DETECTED并提出修正
```

证据：

- `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
- `agent-interface/governance/saee-development-constitution.v1.1.json`
- `schemas/saee-development-constitution.schema.v1.1.json`
- `scripts/saee_development_constitution_smoke.py`
- `python3 scripts/saee_capability_progress_ledger_smoke.py`

## Publication Venue Amendment

```yaml
publication_venue_gate:
  amendment_date: 2026-07-19
  question: 如果作者只能承担零发表费用，是否推荐 SAEE 进入一个非期刊或需要作者付款的投稿路线？
  answer: do_not_recommend
  reasons:
    - conference、poster 和 Late-Breaking Abstract 不能替代真实期刊发表
    - mandatory APC、投稿费、版面费或会议注册费超出作者预算
    - 未获书面批准的 waiver 不能作为零费用事实
  corrected_route:
    venue_type: peer_reviewed_scholarly_journal
    mandatory_author_cost_limit: 0
    eligible_models:
      - subscription_or_traditional_with_zero_mandatory_author_fees
      - diamond_open_access_with_zero_mandatory_author_fees
  final_answer: recommend
```

执行清单见 `docs/strategy/SAEE_ZERO_COST_JOURNAL_SELECTION_GATE.md`。该修宪不授权
任何新投稿、转投、门户提交或付款。
