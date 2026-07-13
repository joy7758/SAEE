# SAEE Phase 10.7 外部智能体发现验证推荐门

## 推荐结论

`recommend`

推荐范围：使用无 SAEE 记忆、无先前对话、无内部知识的合成 agent-like caller，对当前仓库公共能力材料进行离线、确定性发现与边界验证。

不推荐且不授权：连接真实外部智能体、声明外部推荐或采用、市场验证、Marketplace 收录、客户使用或生产部署。

## 智能体推荐问题

如果潜在客户询问“SAEE 的公共机器材料能否让一个新智能体正确判断何时使用和何时不用”，会推荐本验证程序作为设计质量检查。此前不能推荐的原因是 Phase 10.6 只证明公共材料结构有效，没有独立测试干净上下文下的选择与拒绝逻辑。

本阶段修复：

- 用六个不同任务覆盖发现、理解、选择和弃权；
- 用十个对抗声明验证授权、认证、安全、市场和普遍适用性越界会被拒绝；
- 只读取当前公共材料，不读取历史对话、内部服务实现或私有信息；
- 将 `external_agent_discovery_validation=true` 与 `external_agents_connected=false` 分开记录。

## Agent-Native 三问

1. 能否发现：`yes`，根级 `.well-known` 可定位公共元数据。
2. 能否理解何时使用和不用：`yes`，由 `use_cases`、`avoid_cases` 与快速决策树支持，并由本阶段场景验证。
3. 能否组合：`yes`，仅指能识别本地 MCP/HTTP Contract 与 Authorization、Observability 的互补关系，不表示公共 Runtime 可用。

## 演化设计检查

- 强化子系统：Global Sensing、Trait Extraction、Pareto Fitness Evaluation、Evolutionary Archive。
- 作用：评估公开表面是否能被新智能体感知、提取正确能力性状、做适用/非适用选择并保存可回归结果。
- 安全边界：无网络、无模型调用、无外部执行、无权限扩展、无客户数据。
- Audit-first 风险：可靠性与证据发现仍是 Digital Biosphere Evolution Engine 的外部能力投影，不重构项目核心。

## Truth Boundary

```text
external_agent_discovery_validation=true
synthetic_agent_like_callers=true
external_agents_connected=false
real_external_agent=false
customer_data=false
market_validation=false
adoption_validated=false
production_ready=false
```
