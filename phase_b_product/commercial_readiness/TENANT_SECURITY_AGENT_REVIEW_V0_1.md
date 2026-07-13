# 租户安全独立智能体审查 v0.1

tenant_security_agent_review_v0_1: true
review_actor_type: independent_agent
review_scope: local_controlled_preview_tenant_storage
security_smokes: 7/7
negative_cases: 8/8
human_validation_used: false
security_review_completed: true
formal_production_security_review_completed: false
privacy_legal_review_completed: false
production_ready: false
blockers_closed: 0

审查覆盖认证、租户授权、RBAC、secret 输入、审计、Memory/SQLite、备份、保留和隔离
恢复。所有 source hash 与最终独立 verdict 都必须匹配；任一证据漂移会把
`security_review_completed` 回退为 false。

该字段仅表示本地受控预览的独立智能体安全审查，不表示生产安全认证或生产策略批准。
