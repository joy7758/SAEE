# SAEE 外部资源解析收据推荐门

```yaml
feature_or_direction: external_resource_resolution_receipt_v0_1
answer: recommend
blocker_count: 0
scope: minimal_offline_synthetic_semantic_binding
agent_validation_primary: true
human_validation_used: false
```

## 客户推荐问题

如果潜在客户需要证明智能体请求的外部仓库、软件包、技能或工具，实际解析 URI、发布者声明、验证方法、内容摘要、授权策略、沙盒和执行效果之间是否形成闭合证据，是否推荐 SAEE 增加一个最小资源解析收据？

独立智能体回答：`recommend`，但仅限本地、合成、离线、非执行范围。

## 演化设计检查

1. 强化 `Global Sensing`、`Sandbox Development` 与 `Evolutionary Archive / Rollback Immune System`。
2. 改善外部资源观察、失败隔离、证据档案和回滚判断，不修改进化引擎核心。
3. 不联网、不执行外部资源、不安装依赖、不扩大权限、不复制外部代码为 genome。
4. 收据是免疫/证据子系统，不把 SAEE 重构成 audit-first 产品。

## 强制边界

```yaml
uri_dereferenced: false
network_accessed: false
publisher_identity_verified: false
external_resource_authenticity_verified: false
license_verified: false
malware_scanned: false
supply_chain_verified: false
install_performed: false
resource_imported: false
candidate_code_executed: false
subprocess_started: false
sandbox_execution_performed: false
execution_effect_observed: false
production_ready: false
```

发布者字段只记录声明身份及声明的验证方法。结构、内容摘要和收据摘要可在本地重算，但这不独立证明发布者身份、资源存在、内容来源、许可证、安全性或外部执行效果。

若后续扩展到真实发布者验证、联网解析、许可证确认、恶意代码扫描或真实执行效果，本推荐自动失效，必须重新过门。
