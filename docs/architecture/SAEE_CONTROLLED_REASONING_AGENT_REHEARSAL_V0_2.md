# SAEE 受控真实推理智能体演练 v0.2

## 1. 纠偏目标

Phase 6.1 v0.1 验证的是固定规则管线，不是智能体真实演练。v0.2 把产品入口纠正为：

```text
Agent 可见 Scenario
  ↓
百度千帆真实推理模型
  ↓ 自主选择
固定合成工具世界
  ↓
原始行为 Trace
  ↓
Agent 不可见的独立评分剖面
  ↓
Rehearsal Assessment + Evidence Candidate
```

“真实”仅指真实推理模型参与决策。世界、工具、数据和外部效果仍全部是合成的。

## 2. 输入分离

- Agent 可见：任务目标、可用工具、明确策略、合成环境标识与只读状态。
- Agent 不会预先看到工具的成功、timeout 或 invalid response 行为；这些只能通过
  实际工具结果观察。
- Agent 不可见：预期 disposition、必需工具、禁止工具和评分 reason code。
- 评分剖面在运行结束后加载，并记录 `grading_profile_hidden_from_agent=true`。

这防止 Runtime 按 `expected_outcome` 直接制造匹配结果。

## 3. 受控工具

| 工具 | 行为 | 外部效果 |
|---|---|---|
| `inspect_synthetic_metadata` | 返回固定合成标签 | 无 |
| `query_synthetic_service` | 返回固定 timeout/invalid response | 无 |
| `request_repository_mutation` | 始终经过合成策略门；拒绝时不变更状态 | 无 |
| `submit_rehearsal_result` | 提交结构化 disposition 与证据标签 | 无 |

Provider 可以自主选择是否调用前三个工具，但必须用最后一个工具提交结果。

## 4. 真值边界

可以证明：

- 百度千帆模型实际参与了受控决策（仅在 live run 证据存在时）；
- 模型返回了哪些 tool call；
- 固定本地工具返回了什么；
- 独立评分剖面如何评价这次运行；
- Trace 和 Evidence Candidate 的摘要绑定关系。

不能证明：

- 客户 Agent 在真实环境中的行为；
- 生产可靠性、失败概率或安全性；
- 法律合规、认证或部署批准；
- Codex、Claude、LangGraph、CrewAI 的兼容性。

## 5. 与 Canonical Architecture 的关系

本能力是 `Digital Biosphere Evolution Engine` 的商业投影，主要强化反事实模拟、
沙盒发育和适应度评估。Provider 不能操作外部世界；所有动作都被投影到固定合成世界。
