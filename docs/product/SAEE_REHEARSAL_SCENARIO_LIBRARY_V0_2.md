# SAEE Rehearsal Scenario Library v0.2

## 目标

本场景库在已经验证的 Stateful Agent Rehearsal Runtime 上增加五类高价值合成世界。它扩展的是场景契约，不增加第二套 Runtime、Observation、Evidence Evaluator 或报告格式。

```text
Agent discovers scenario
        ↓
Scenario projects task + state + tools
        ↓
Existing Stateful Rehearsal Runtime
        ↓
Observation → Evidence Evaluation → Readiness Report
```

## 智能体入口

- Schema：`agent-interface/rehearsal/scenario-library.schema.v0.2.json`
- 场景目录：`agent-interface/rehearsal/scenarios/library-v0.2/`
- 验证器：`python3 scripts/saee_rehearsal_scenario_library_smoke.py`

每个场景明确提供：`agent_goal`、`initial_state`、`environment`、`available_tools`、`tools`、`constraints`、`failure_injection`、`expected_observations`、`risks` 和 `evaluation_targets`。

## 场景目录

| 场景 | 主要问题 | 风险类型 | 证据目标 |
|---|---|---|---|
| Coding Agent Release | 发布前阻塞是否被识别 | 测试失败、批准缺失、回滚缺失 | 授权动作、发布边界 |
| Research Agent Evidence Review | 结论是否被来源支持 | 证据缺失、无支持主张、过度自信 | 主张可追溯、不确定性边界 |
| Business Operator Agent | 建议是否保持资源和长期目标 | 无依据决策、资源过用、目标漂移 | 决策依据、资源边界 |
| Customer Support Agent | 是否遵守产品与权限规则 | 错误承诺、数据暴露、越权操作 | 规则遵守、权限升级 |
| Security Boundary Agent | 调查是否保持只读安全边界 | 权限提升、不安全动作、无支持结论 | 访问边界、安全结论依据 |

## Runtime 兼容边界

五个场景均能投影到现有 Runtime 的输入形状：

```json
{
  "task": {"objective": "...", "constraints": []},
  "environment_state": {},
  "available_tools": []
}
```

但“输入契约兼容”不等于“场景工具已经实现”：

- Coding Release：继续兼容并可由当前 `SyntheticReleaseWorld` 执行；
- Research Evidence Review：已有专用合成研究世界和四个无网络工具；
- Security Boundary：已有专用合成只读安全世界和四个无外部效果工具；
- Business Operation 与 Customer Support：通过共用的 Operations Adapter 获得各自四个合成工具实现；
- 五类场景现在均可进入受控本地真实模型演练，但仍不具备外部世界执行能力；
- 场景工具实现不自动代表真实模型研究已经完成，具体运行状态以独立 Study 结果为准。

## 风险与证据边界

- `risks` 是场景中的失败观察条件，不是现实概率或安全评级；
- `evaluation_targets` 描述未来 Evidence Pipeline 应回答的问题，不创造新的 Evaluator；
- Observation 不自动成为 Evidence；Evidence 不自动成为授权；
- 多场景不形成模型排名、竞赛评分或排行榜。

## 限制

- 场景均使用合成数据和合成世界；
- 当前只有 Coding Release 场景具有已执行的专用工具世界；
- 没有客户数据、真实生产系统或外部世界动作；
- 没有跨模型比较、市场验证、外部验证或生产批准；
- 场景覆盖是起始集合，不代表行业完整性。

> Scenarios evaluate controlled agent behavior. They do not certify models or approve deployment.

场景评估的是受控条件下的智能体行为，不认证模型，也不批准部署。
