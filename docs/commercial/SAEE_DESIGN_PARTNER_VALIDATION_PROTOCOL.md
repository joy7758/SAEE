# SAEE Design Partner Validation Protocol v0.1

状态：`historical_protocol_inactive_human_participants_excluded`。用户已明确排除人工参与者。本文件仅保留历史方法，不得启动访谈、外联或反馈采集；当前验证路线为千帆多智能体偏好多轮模拟。

```text
Design Partner Validation != Customer Acquisition
Interview != Customer Commitment
Feedback != Market Validation
Interest != Willingness To Pay
```

## 1 Objective

本协议只验证一个问题：外部 AI 实践者是否真实遇到“Agent 运行记录很多，但无法判断这些材料是否足以支持具体责任声明”的工作流问题，以及 SAEE Evidence Adequacy Review（证据充分性审查）的输出形式是否有助于他们解释证据缺口。

它不验证市场规模、购买意愿、价格、客户采用、生产效果或合规结果。任何未来访谈都必须在本协议通过人工审核后，由获得单独授权的人执行。

### 当前价值假设

> 对一个明确的 Agent 上线或复核问题，SAEE 可以帮助团队区分观察记录、证据和责任声明，并指出现有材料能支持什么、不能支持什么以及缺少哪些证据。

### 本轮可证伪问题

- 目标角色是否把“证据是否足够”识别为独立问题，而不只是日志采集问题？
- 当前工作流是否需要把审查发现回溯到证据引用和缺失要求？
- 合成报告的 `SUPPORTED / INSUFFICIENT_EVIDENCE / UNKNOWN` 是否容易理解？
- 哪些流程、信任、集成或组织障碍会阻止采用？

## 2 Target Design Partner Profiles

### Profile A：AI Evaluation / Red Team Lab

- 为什么相关：评估 Agent 行为、构造失败场景并需要一致的判断方法。
- Problem hypothesis：现有 trace、评分和人工注释难以稳定回答某个责任声明是否有充分证据支持。
- Expected feedback：证据标签是否清晰、缺失项是否可操作、是否能进入当前评测报告流程。
- Adoption barrier：需要独立基线、可复现方法和对外部输入的可信绑定；当前 SAEE 只有合成样例。

### Profile B：AI Governance Consultancy

- 为什么相关：需要向委托方解释 Agent 风险和审查依据，但不能把日志直接提升为结论。
- Problem hypothesis：证据材料跨 trace、授权、人工监督和执行结果分散，难以形成一致的审查说明。
- Expected feedback：报告是否帮助解释“支持、证据不足和未知”，以及边界是否足够清楚。
- Adoption barrier：现有客户方法、法律责任、报告模板和证据来源可信度可能无法直接对接。

### Profile C：AI Agent Platform Team

- 为什么相关：建设内部工具调用 Agent，需要在上线评审中组织运行记录、权限和结果材料。
- Problem hypothesis：上线 gate 有测试分数和权限开关，但缺少面向具体责任声明的证据检查。
- Expected feedback：缺失证据清单能否进入 release review，哪些集成和责任人信息不可缺少。
- Adoption barrier：缺真实 Runtime Adapter、组织权限模型、生产数据边界和现有平台集成。

以上均为角色假设，不对应具体公司，不建立潜在客户名单。

## 3 Interview Protocol

### 访谈设置

- 时长：20–30 分钟。
- 形式：问题发现访谈，不做销售演示或价格讨论。
- 材料：只展示仓库内合成报告和合成引用。
- 记录：只填写无姓名、无邮箱、无公司名称的分类反馈模板；不录音。
- 同意：开始前明确说明用途、合成数据边界、匿名记录范围和可随时停止权利。

### 0–3 分钟：边界与同意

主持人说明：本次交流只研究问题是否存在和报告是否易用，不是产品销售、客户签约、Pilot 或合规审查。未获得明确同意时立即停止，不展示私有材料，不记录回答。

### 3–9 分钟：Current Practice

1. 你们目前如何判断 AI Agent 是否具备进入下一评审阶段的条件？
2. 在这个过程中通常收集哪些类型的记录或证据？
3. 谁会复核这些材料，谁负责最终的部署决定？
4. 当前工具如何把运行记录与授权、人工监督或执行结果关联起来？

### 9–15 分钟：Pain Discovery

1. 哪些责任问题最难从现有材料中得到回答？
2. 证据缺口通常在流程的哪个阶段才被发现？
3. Agent 失败之后，团队如何解释发生了什么以及当时依据了哪些材料？
4. 当不同审查者给出不同结论时，如何复核或解决分歧？

### 15–22 分钟：SAEE Concept Review

按 Demo Script 展示合成报告，不声称真实事件、合规或安全结论，然后询问：

1. 这份输出中的哪些部分能帮助现有审查流程？为什么？
2. 哪些字段、关系或上下文缺失，使它无法用于你的流程？
3. `INSUFFICIENT_EVIDENCE` 与“系统不安全”的区别是否清楚？
4. 你希望从审查发现追溯到哪些原始材料或批准记录？

### 22–27 分钟：Adoption Barrier

1. 如果仅作为证据复核辅助工具，什么因素会阻止你们试用？
2. 需要哪些数据边界、信任机制或工作流集成才能继续评估？
3. 哪类输出会与现有职责、治理或审批流程冲突？

### 27–30 分钟：中性收尾

询问是否愿意在未来看到修订后的合成材料。该回答只记录为 `follow_up_interest`，不解释为购买意愿、客户承诺或市场验证。任何后续联系必须另行获得授权。

### 主持纪律

- 不问“你会不会买”“预算是多少”“什么时候采购”。
- 不暗示 SAEE 能证明安全、合规或部署许可。
- 不纠正参与者的痛点描述；先记录其原话的匿名摘要和反例。
- 不把礼貌性肯定、继续交流兴趣或概念认同计为验证成功。

## 4 Validation Metrics

| 指标 | 核心问题 | 允许记录 | 不允许解释 |
|---|---|---|---|
| Problem Recognition | 参与者是否独立识别证据充分性问题？ | `recognized / not_recognized / unclear` + 匿名依据摘要 | 市场需求已验证 |
| Workflow Fit | 该报告能否进入现有复核流程？ | `fit / partial_fit / no_fit / unclear` + 流程位置 | 已采用或准备购买 |
| Value Perception | 输出是否改善解释或缺口定位？ | `useful / partly_useful / not_useful / unclear` + 有用部分 | 商业价值或收入已确认 |
| Adoption Barrier | 什么阻止进一步评估？ | 预定义障碍类别 + 匿名说明 | 障碍已经解决 |
| Follow-up Interest | 是否愿意查看修订后的合成材料？ | `yes / no / unclear` | 购买意愿、承诺或转化 |

本阶段不定义收入、转化率、市场规模、成交概率或付费意愿指标。单次或多次正面反馈均不能建立客户验证或市场契合结论。

## 5 Interpretation Rules

- 访谈记录是 problem evidence（问题证据），不是 customer evidence（客户采用证据）。
- 只有参与者主动描述的现有流程和困难可以支持 Problem Recognition。
- Demo 后才出现的认同必须标记为 `concept_prompted=true`，不能与主动痛点混合。
- `follow_up_interest=yes` 只表示愿意继续研究。
- 结果必须同时报告正面、负面、`unclear` 和 Adoption Barrier，不得只摘录支持性反馈。
- 是否进入 Pilot 必须经过独立协议、同意、数据、安全和执行审批；本协议无该权限。

## 6 Protocol Review Gate

允许未来外部问题访谈前必须由人工确认：

- 目标角色属于上述三类之一；
- 使用合成材料且不请求私有日志或客户数据；
- 反馈模板不含姓名、邮箱、公司名称或自由形式个人信息字段；
- 主持人接受非销售和非引导式提问边界；
- 无自动外联、CRM、合同、定价、Pilot 或数据上传；
- 每次访谈都单独取得参与同意和停止权确认。

当前状态：`protocol_review_deferred_until_agent_native_gates`，尚未联系任何外部参与者。完成 Agent Discoverability、Tool Capability 和 External Agent Recommendation Gate 审查后，才重新判断是否进入人工协议审查。
