# 租户智能体审查证据采纳器 v0.1

tenant_agent_review_evidence_v0_1: true
review_actor_type: independent_agent
review_scope: local_controlled_preview
human_validation_used: false
agent_validation_primary: true
negative_cases: 10/10
blockers_closed: 0

采纳器只接受：

- 绑定式租户授权 profile 与独立智能体最终 verdict；
- 租户 Secret 边界 profile 与独立智能体最终 verdict。

四份输入必须来自同一快照。采纳器重算完整 source manifest，固定检查 `14/14`
和 `24/24`，核对最终轮 blocker 为 0，并拒绝任何生产、安全、隐私状态变成 true。
任何一个输入异常时，两个 review 字段整体保持 false，不允许部分晋级。

通过后只表示本地 controlled preview 的独立智能体代码审查完成；正式安全审查、
隐私/法律审查、生产 OIDC/JWKS、生产租户授权和生产租户隔离仍未完成。
