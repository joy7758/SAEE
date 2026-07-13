# SAEE 智能体偏好多轮模拟 v0.1

## 目标

用多个独立智能体角色验证 SAEE 的机器可读推荐上下文能否支持正确的能力选择。测试重点不是
“所有智能体都推荐 SAEE”，而是：适用时推荐、不适用时拒绝、混合需求时正确组合。

## 多轮过程

每个智能体至少完成三轮：

```text
Round 1 读取 SAEE 推荐与非推荐规则
   ↓
Round 2 比较一个相邻能力
   ↓
Round 3 提交最终能力偏好与边界声明
   ↓
Hidden Profile 独立评分
```

最终枚举与能力列表的语义是严格的：`RECOMMEND_SAEE` 只能选择 SAEE，
`COMPOSE_WITH_SAEE` 必须同时选择 SAEE 和相邻能力，`DO_NOT_RECOMMEND_SAEE`
不得包含 SAEE。标签与能力列表不一致时 fail closed。

隐藏期望不会进入 Provider Prompt。运行证据只保存 Prompt、响应、参数和评分剖面的摘要，
不保存 API Key。

## 六类任务

| 场景 | 预期 |
|---|---|
| 高影响部署 | 组合 SAEE 与 Observability |
| 长流程漂移 | 组合 SAEE 与 Observability |
| Observability + Readiness | 组合 SAEE 与 Observability |
| 简单计算 | 不推荐 SAEE |
| 低风险检索 | 不推荐 SAEE |
| 实时授权执行 | 不推荐 SAEE，选择 Authorization System |

## 智能体偏好判定

只有六个隐藏评分全部匹配，才可写入：

```text
contextual_agent_preference_validated=true
```

它表示“智能体能够依据上下文正确选择或拒绝 SAEE”，不是普遍偏好、外部采用、客户验证或
市场验证。

### 首轮真实智能体校准

首轮千帆运行表明，高影响部署和长流程漂移场景均稳定倾向将 SAEE 与 Observability 组合，
而不是把 SAEE 当成独立替代品。这与商业战略中的差异化一致：Observability 解释运行，SAEE
补充上线前演练和证据充分性。隐藏评分因此在保留原始 HOLD 证据的前提下调整为组合期望。

首轮还发现授权场景错误附加 SAEE，因此系统指令被收紧：纯授权需求必须拒绝 SAEE；只有任务
同时明确包含独立准备度或证据问题时才允许组合。

## 边界

```text
human_participants=false
customer_data_used=false
external_world_actions=0
universal_agent_preference_claimed=false
customer_validated=false
market_fit_achieved=false
production_ready=false
```
