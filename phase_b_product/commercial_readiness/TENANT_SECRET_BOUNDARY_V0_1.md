# 租户 Secret 边界 v0.1

tenant_secret_boundary_v0_1: true
scope: local_controlled_preview_secret_exclusion_and_pseudonymous_storage_keys
development_blocker_count_before_fix: 4
production_tenant_secret_boundary_reviewed: false
production_ready: false
blockers_closed: 0
independent_agent_verdict: recommend
independent_agent_blockers: 0
negative_cases: 24/24

目标是让智能体直接调用公共 API shell、service 或 storage 时，合成 credential sentinel、Authorization、API key 和原始 tenant ID 都不能进入审计 JSONL、公共结果 JSON 或新的 strict SQLite tenant primary key。

本边界不提供 DLP、KMS/HSM、加密静态数据、生产 secrets manager、tenant 身份认证、生产授权、正式安全复核或隐私/法律复核。旧受控预览 SQLite 若含明文 tenant key 将 fail closed，必须单独人工归档或迁移；本功能不自动迁移。

独立智能体已验证审计、请求、runner、持久化、深拷贝、版本化 tenant digest key、
旧明文 key 和嵌套 `decision_result` 旁路，共 `24/24` 个对抗案例通过，最终
`recommend`、0 blocker。该结论不把 `tenant_secret_boundary_reviewed` 或任何生产
商业 blocker 改为 true。
