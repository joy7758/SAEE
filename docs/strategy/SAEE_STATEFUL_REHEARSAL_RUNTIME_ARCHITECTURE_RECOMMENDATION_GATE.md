# SAEE Stateful Rehearsal Runtime Architecture v0.1 推荐门

## 问题

如果潜在客户需要让真实模型智能体在无真实副作用的有状态世界中演练，我会推荐当前程序吗？

## 结论

`recommend`

仅推荐为架构规范和已有千帆单供应商受控 Runtime 的扩展设计。OpenAI、火山方舟和 Anthropic Adapter 尚未由本规范实现。

## 推荐理由

- 复用现有有状态千帆演练与 Evidence Adequacy，不重复创建 Runtime/Evaluator；
- 明确真实模型与合成世界的边界；
- Provider Gateway 与 Model Vendor 分离；
- 只记录可观察动作，不记录隐藏推理；
- 五类场景和五个模拟工具均保持无外部副作用；
- 报告禁止认证、安全与自动批准语言。

## 尚未推荐为产品能力的阻塞

| 阻塞 | 状态 | 后续任务 |
|---|---|---|
| OpenAI Adapter 未实现 | deferred | Stateful Rehearsal Runtime MVP |
| Volcengine Ark Adapter 未实现 | deferred | Gateway-aware Adapter MVP |
| Anthropic 未配置/未测试 | deferred | 另行凭据和 provider gate |
| Kimi 当前目录模型不可调用 | observed limitation | 等待可用模型或接入点 |
| 多 Provider 同场景运行未执行 | deferred | Cross-provider controlled rehearsal |

## 演化设计检查

1. 强化：Ecological World Model、Counterfactual Simulation、Sandbox Development、Pareto Fitness Evaluation、Evolutionary Archive。
2. 改善：真实模型在合成世界中的分叉、失败注入、恢复与选择观察。
3. 安全：Provider 网络 allowlist；模拟工具；无客户数据、生产执行、真实金融动作或权限扩大。
4. 叙事：Evidence 是免疫子系统；本设计不把 SAEE 改造成审计 SDK 或通用多 Agent 框架。

最终边界：`Architecture Design != Multi-provider Runtime Implemented`。

