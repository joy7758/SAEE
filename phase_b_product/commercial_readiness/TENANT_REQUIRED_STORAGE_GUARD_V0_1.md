# 租户必填存储守卫 v0.1

tenant_required_storage_guard_v0_1: true
scope: controlled_preview_storage_defense_in_depth
requires_factory_configured_store: true
memory_store_guard_available: true
sqlite_store_guard_available: true
memory_store_unscoped_operations_denied: true
sqlite_store_unscoped_operations_denied: true
unscoped_operation_cases: 7/7
default_local_unscoped_mode_preserved: true
production_tenant_storage_isolated: false
production_data_migration_authorized: false
blockers_closed: 0

当 `SAEE_REQUIRE_TENANT_ID=true` 时，通过存储工厂创建的 store 要求所有 create、save、exists、get 和 list 操作携带合法 `tenant_id`。
`get_runs` 和 `get_metrics` 同样直接覆盖；应用运行时只通过 `create_experiment_store()` 创建 store，未使用的默认全局 store 已移除。
这补充 API 请求边界，但不代替生产授权、安全审查、隐私审查或数据库迁移证明。

`cross_tenant_write_denial_tests_passed` 在该本地证据中仅表示租户键分区阻止一个租户覆盖另一个租户的同名记录，不表示授权层已经拒绝恶意主体；`tenant_authorization_enabled=false`。

脱敏证据：`phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json`。
