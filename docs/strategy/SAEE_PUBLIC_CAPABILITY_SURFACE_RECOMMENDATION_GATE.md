# SAEE 公共能力表面推荐门 v0.1

## 推荐结论

`recommend`

推荐范围仅限仓库内、公开安全、机器可读的能力说明与发现元数据。该结论不推荐也不授权公网 API、公共服务、市场上架、客户接入或生产部署。

## 智能体推荐问题

如果潜在客户需要让智能体发现并判断 SAEE 是否适合证据充分性或可靠性评估，我会推荐本仓库的公共能力表面，因为它明确给出适用条件、非适用条件、输入输出边界和本地调用契约。

此前不能无条件推荐的原因：

- 现有信息分散在 `llms.txt`、`agent-index.json`、Capability Object、Registry 与 Package 中；
- 缺少统一的公开安全机器入口；
- 缺少对公开声明、秘密值、私有路径和虚假生产端点的专用离线验证。

本阶段通过公共元数据、快速理解指南、根级 `.well-known` 入口和 fail-closed 验证器修复这些缺口。

## Agent-Native 三问

1. 智能体能否发现？`yes`，通过 `.well-known/saee-capability-index.json`。
2. 智能体能否理解何时使用和何时不用？`yes`，通过结构化 `use_cases`、`avoid_cases` 和快速决策指南。
3. 智能体能否通过稳定契约组合？`yes`，元数据引用已有 MCP 与 HTTP Contract；但仅表示本地契约可组合，不表示公共服务可用。

## 演化设计检查

- 强化子系统：Global Sensing、Trait Extraction、Evolutionary Archive。
- 改进内容：提高外部智能体对能力表面的感知、性状提取与可检索归档能力。
- 边界：不执行外部世界、不扩大权限、不引入未知依赖、不复制外部代码。
- Audit-first 风险：通过显式声明 Digital Biosphere Evolution Engine 为工程核心，并把可靠性/证据能力标记为对外能力投影，避免把项目重构成审计 SDK。

## Truth Boundary

```text
public_capability_surface=true
repository_public_surface_prepared=true
publicly_deployed=false
public_api=false
public_service=false
marketplace_listed=false
external_agents_connected=false
customer_data=false
production_ready=false
```
