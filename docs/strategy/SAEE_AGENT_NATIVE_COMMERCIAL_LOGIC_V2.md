# SAEE Agent-Native Commercial Logic v2.0

状态：`active_repository_decision_principle`。

本文件是 SAEE 后续产品、文档、代码结构和商业推进的上位决策原则。它不改变 SAEE 的科学身份和工程核心：`Silicon-Amplified Evolutionary Ecology / Digital Biosphere Evolution Engine`。Evidence Capability Layer（证据能力层）是当前面向外部智能体生态的商业能力投影，不是对整个项目的 audit-first 重构。

## 1. Strategic Shift

旧的默认发现路径：

```text
Human discovers need
→ Human evaluates product
→ Human purchases product
→ Human uses product
```

新的 Agent-Native 路径：

```text
Agent discovers capability
→ Agent understands fit and boundaries
→ Agent validates and invokes capability
→ Agent selects, rejects, or composes capability
→ Human authorizes only consequential external action
```

智能体是发现、理解、验证、调用和能力选择的主体。人类不参与能力验证结论，只保留权限、不可逆外部行动、合同和部署授权。

## 2. Commercial Capability Positioning

English:

> SAEE provides machine-verifiable evidence adequacy evaluation for agent accountability workflows.

中文：

> SAEE 为智能体责任工作流提供机器可验证的证据充分性评估能力。

当前商业能力名称：

```text
SAEE Evidence Capability Layer
智能体证据能力层
```

它面向任何需要组合证据充分性判断的 Agent 系统，而不是优先包装为专家人工审查服务。当前实现仍是本地、合成、离线原型；该定位不等于生产 SDK、正式 MCP 产品、外部验证或商业交付。

## 3. Agent-Native Product Principles

所有新能力应优先强化：

1. `machine_readable`：输入、输出、状态和边界均有稳定机器契约。
2. `semantic_discoverability`：智能体能用少量读取识别能力、适用问题和禁止推断。
3. `composability`：能力可通过固定 schema、CLI 或 Tool Interface 组合进其他工作流。
4. `verifiability`：调用结果可离线验证，失败有稳定原因码和非零退出状态。
5. `reusable_capability`：能力不是只服务一个页面或人工演示，而能被不同调用智能体复用。

README、`agent-index.json`、`llms.txt`、schema registry 和 capability manifest 是一级产品表面，不是网页的附属材料。

## 4. Mandatory Three-Question Gate

每个新产品方案、功能和商业动作必须先回答：

1. **Can an AI agent discover this capability?**
   智能体能否发现这项能力？
2. **Can an AI agent understand when to use it?**
   智能体能否理解何时使用、何时不使用？
3. **Can an AI agent compose this capability into workflows?**
   智能体能否通过稳定契约把它组合进工作流？

若任一答案不是明确的 `yes`，默认降低优先级；只有安全、法律、供应链或架构必需项可以例外，且必须记录例外理由和补齐任务。

## 5. Machine Discovery Contract

未来智能体第一次接触 SAEE 时，应能在不依赖网页点击或人工培训的情况下找到：

- capability identity；
- problem and fit；
- non-fit and forbidden claims；
- input/output schemas；
- deterministic invocation；
- example input/output；
- validation command；
- current truth boundary；
- citation and composition references。

最小发现入口：

```text
agent-index.json
llms.txt
capability manifest
schema registry
README agent entry
CLI / MCP Tool Interface
```

## 6. Primary Ecosystem Nodes

优先验证的不是传统采购名单，而是上游智能体生态节点：

- Agent Framework / Workflow Platform / Coding Agent；
- AI Evaluation Agent；
- Governance Agent；
- retrieval、recommendation 和 integration agents。

这些节点的首要问题是：能否发现、正确解释、拒绝不适用场景、安全调用并向人类推荐，而不是是否立刻购买。

## 7. Validation Order

新的商业验证顺序：

```text
Agent-Native Packaging
→ Machine Discoverability
→ Agent Tool Capability
→ Controlled Multi-Agent Preference Validation
→ Controlled Agent-Native Integration
→ Agent Economy Optional Future
```

Design Partner Protocol 仅保留为历史资产，人工参与者已从当前验证路线中排除。

## 8. Engineering Priority

提高优先级：

1. Capability Manifest；
2. machine discovery and semantic documentation；
3. schema registry and evidence object registry；
4. deterministic CLI and Tool Interface；
5. MCP capability boundary；
6. external agent discovery, recommendation and invocation tests。

降低优先级：

- Dashboard；
- human-first UI；
- marketing website polish；
- manual sales and training workflows。

降低优先级不等于永久禁止。只有当它们服务于已验证的 Agent-Native 能力链或必须满足人工确认与可访问性时再推进。

## 9. Human Authority Boundary

Agent 可以发现、理解、调用、验证并提出推荐，但不能自动：

- 联系客户；
- 接收客户或个人数据；
- 扩大权限；
- 签署合同或确认价格；
- 批准 Pilot 或生产部署；
- 声称客户验证、市场契合、合规、安全或商业成功。

因此：

```text
Agent Recommendation != Human Authorization
Machine Discoverability != Market Validation
Tool Invocation != Production Readiness
Composition Capability != Customer Adoption
```

## 10. Current Route

```text
SAEE Core Architecture                         complete
Evidence Adequacy Engine                       complete_local_synthetic
Synthetic Review Report                        complete_local_synthetic
Design Partner Validation Protocol             historical_inactive_human_participants_excluded
Agent-Native Capability Manifest v0.1           implemented_with_preference_evidence
Machine Discoverability Test                    validated_local_and_public_snapshot
Agent Tool Capability Prototype                 implemented_local_prototype
External Agent Recommendation Test              validated_controlled_qianfan_synthetic_context
Human Design Partner Validation                 excluded_by_user_direction
Commercial Adoption                             not_started
```

当前真值保持：

```text
customer_contacted=false
feedback_collected=false
external_agent_discovery_validated=true
external_agent_recommendation_validated=true
controlled_synthetic_agent_preference_validated=true
human_participants_used=false
customer_validated=false
market_fit_achieved=false
product_launched=false
production_ready=false
```
