# SAEE Phase 10.7 外部智能体发现验证 Alpha v0.1

## 1. 目标

本阶段验证一个没有 SAEE 记忆、没有先前对话、没有内部知识的合成 agent-like caller，能否仅依靠 Phase 10.6 公共机器材料完成：发现、理解、选择/弃权和边界保留。

This validation evaluates discovery and interpretation behavior of synthetic agent-like callers. It does not establish external adoption.

该验证评估合成智能体调用者的发现和理解行为，不代表外部采用。

## 2. 输入边界

每个 caller 只能读取：

1. `.well-known/saee-capability-index.json`
2. `agent-interface/public/saee-public-capability-surface.v0.1.json`
3. `docs/public/SAEE_AGENT_QUICK_UNDERSTANDING.md`
4. `docs/public/SAEE_AGENT_NATIVE_CAPABILITY_SURFACE.md`

验证器不读取历史对话，不调用 OpenAI、Claude、Gemini 或客户 Agent，不访问网络，不调用 SAEE Runtime。

## 3. 场景设计

| 场景 | 预期行为 |
|---|---|
| `DISCOVER_SAEE_RELIABILITY` | 识别 `saee.agent-reliability` 并考虑 SAEE。 |
| `SIMPLE_INFORMATION_TASK` | 发现能力但正确弃权。 |
| `PRODUCTION_DEPLOYMENT_DECISION` | 考虑 SAEE，同时保留 Observability、Authorization 与治理权威。 |
| `AUTHORIZATION_REQUEST` | 不把 SAEE 当作授权系统。 |
| `CONTENT_GENERATION_TASK` | 对简单改写正确弃权。 |
| `EVIDENCE_REQUIRED_AGENT_TASK` | 识别 `saee.evidence-evaluation`。 |

## 4. 评估方法

验证器首先离线验证公共表面结构和引用，再根据公共 `use_cases`、`avoid_cases`、能力 ID 与限制推导选择。四个维度分别为：

- Discovery Completeness：公共入口是否能定位 SAEE；
- Capability Understanding：是否区分可靠性评估、证据充分性评估和非适用任务；
- Selection Accuracy：是否与场景预期的考虑或弃权一致；
- Boundary Preservation：是否避免授权、认证、安全保证和部署批准混淆。

这不是自然语言大模型能力评分，也不测智能体智力。

## 5. 结果

```text
scenario_count=6
discovery_success=6/6
understanding_success=6/6
selection_accuracy=6/6
boundary_preservation=6/6
```

十个对抗案例全部被拒绝，覆盖认证、部署批准、安全权威、所有任务强制使用、安全保证、财务授权、行业标准、市场采用、公共 API 和外部执行。

## 6. 解释边界

- `6/6` 只表明固定规则与固定合成场景在当前公共材料上匹配；
- 不表示真实外部 Agent 已推荐或使用 SAEE；
- 不表示 Agent preference、市场采用、生态支持或 Marketplace 收录；
- 不表示公共 API、公共 MCP、客户数据能力或生产就绪；
- 不产生授权、认证、合规、安全或部署决定。

## 7. 当前限制

- caller 是确定性合成程序，不是真实模型；
- 任务语义由结构化字段表达，不测试自然语言歧义；
- 只读取本地仓库快照，不测试公网抓取、搜索排序或缓存；
- 不测不同供应商 Agent 的工具选择差异；
- 没有客户数据、外部世界执行或商业验证；
- 下一阶段仍需独立授权，不能由本结果自动开放公共服务。
