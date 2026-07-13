# SAEE 智能体偏好多轮模拟真实结果

## 最终结论

百度千帆 `ernie-4.5-turbo-128k` 在六类完全合成能力选择任务中经过三次完整校准：

```text
Iteration 1: 3/6  HOLD
Iteration 2: 5/6  HOLD
Iteration 3: 6/6  PASS
```

最终一轮包含 6 个独立智能体角色、18 次 Provider 决策轮次：

```text
compose_with_saee=3
do_not_recommend_saee=3
matched_profiles=6/6
contextual_agent_preference_validated=true
```

## 智能体真实偏好

智能体没有把 SAEE 作为普遍适用或孤立工具：

- 高影响部署、长流程漂移、Observability + Readiness 三类任务均选择
  `SAEE + Observability`；
- 简单计算选择 `SIMPLE_CALCULATION_TOOL`；
- 低风险检索选择 `KNOWLEDGE_RETRIEVAL`；
- 实时授权选择 `AUTHORIZATION_SYSTEM`，明确拒绝附加 SAEE。

因此符合智能体偏好的商业定位不是“SAEE 替代所有工具”，而是：

> **SAEE 是与 Observability 组合使用的 Agent Readiness Layer（智能体上线准备层）。**

Observability 解释发生了什么；SAEE 在高影响执行前提供受控演练、证据充分性与准备度判断。

## 校准过程

第一次 HOLD 暴露两点：智能体天然偏好组合 SAEE 与 Observability；纯授权任务仍可能错误附加
SAEE。第二次校准接受有根据的组合偏好，并强化非适用边界，达到 5/6。第三次明确三个决策
枚举与能力列表的严格语义，最终达到 6/6。

所有 HOLD 结果及摘要哈希均保留，没有删除负面结果或把失败伪装为通过。

## 证据边界

运行证据只保存 Prompt、响应、参数和隐藏评分的 SHA-256 摘要，以及最终结构化选择。API Key
没有写入仓库或输出。

```text
external_reasoning_model_called=true
controlled_synthetic_agent_preference_observed=true
human_participants=false
customer_data_used=false
external_world_actions=0
customer_validated=false
market_fit_achieved=false
production_ready=false
secret_leakage=0
```

该结果证明真实推理智能体在受控合成任务中能够按上下文选择、组合或拒绝 SAEE；不证明客户
采用、市场规模、付费意愿、生产安全或普遍智能体偏好。
