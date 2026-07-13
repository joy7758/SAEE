# SAEE Tenant-Required Storage Guard Recommendation Gate

answer: recommend
recommend_for_controlled_preview_defense_in_depth: true
recommend_for_production_tenant_isolation_claim: false
recommend_for_production_data_migration: false
recommend_for_blocker_closure: false

independent_agent_review_round_1: conditional
independent_agent_review_round_1_blockers: 3

## Agent recommendation

如果潜在客户要求受控预览在内部调用绕过 API 时仍不能无租户读写，我会推荐此守卫。
当 `SAEE_REQUIRE_TENANT_ID=true` 时，存储工厂生成的 memory/SQLite store 会在键生成、查询和列表层拒绝缺失 `tenant_id`。

## Evolution design check

- strengthened subsystem: `Evolutionary Archive / Rollback Immune System`
- improvement: 防止无租户记录进入档案，也防止无租户读取跨越租户边界。
- safety: 默认本地模式保持兼容；只有显式租户必填配置启用双层拒绝。
- boundary: 不迁移生产数据、不处理客户数据、不声称正式安全或隐私审查完成。

`production_tenant_storage_isolated=false`、`production_data_migration_authorized=false`、`blockers_closed=0`。

## Round 1 remediation

- 移除未使用的默认非严格全局 store；应用运行时通过 factory 读取显式配置。
- 对 `create/save/exists/get/get_runs/get_metrics/list` 七个无租户路径逐项做 strict 负向测试。
- 将 write-denial 解释限定为存储键分区，不声称授权层拒绝；保留 `tenant_authorization_enabled=false`。
- `generated_at` 改为真实 UTC 生成日期。

## Round 2 independent agent verdict

- independent_agent_review_round_2: `recommend`
- independent_agent_review_round_2_blockers: `0`
- recommendation_scope: `controlled_preview_storage_defense_in_depth`
- evidence: `agent_recommendation/tenant_required_storage_guard/run_001/independent_agent_validation.local.json`

三项 round 1 blocker 已全部修复。该结论不关闭 `tenant_storage_isolation`，也不证明租户授权、row-level security、生产多租户隔离或正式安全/隐私复核。
