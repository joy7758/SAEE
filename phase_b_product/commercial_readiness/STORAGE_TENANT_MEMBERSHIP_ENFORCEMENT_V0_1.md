# 存储层租户成员资格守卫 v0.1

storage_tenant_membership_enforcement_v0_1: true
scope: factory_configured_controlled_preview_allowlist_membership_enforcement
membership_scope: configured_preview_allowlist_not_identity_authentication
allowed_tenant_snapshot_requires_restart: true
production_tenant_storage_isolated: false
tenant_authorization_enabled: false
blockers_closed: 0

该守卫面向智能体绕过 HTTP API、直接调用 SAEE service/storage 的场景。启用 `SAEE_REQUIRE_TENANT_ID=true` 后，factory 创建的 memory/SQLite store 必须同时获得 `SAEE_ALLOWED_TENANT_IDS` 的不可变启动快照，并对所有存储操作执行成员资格校验。

它不认证调用者身份，不代替 JWT/OIDC/RBAC、密钥隔离、数据库 row-level security、正式安全复核、隐私/法律复核或生产多租户隔离。

API 与 storage 都复用 `saee_backend.config.tenant_id_format_valid`；API 只保留面向请求者的错误文案，不复制正则或格式函数。
