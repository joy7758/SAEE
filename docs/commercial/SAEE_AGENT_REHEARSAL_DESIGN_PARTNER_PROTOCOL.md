# SAEE 智能体演练设计伙伴验证协议 v0.1

状态：`historical_protocol_inactive_human_participants_excluded`。

用户已明确排除人工参与者。本协议仅作为历史边界记录，不再是当前商业战略完成条件，
不得据此创建或启动任何访谈会话。当前验证路线为千帆多智能体偏好多轮模拟。

## 1. 验证目标

本协议验证外部 AI 实践者是否认为以下工作流解决真实问题：

> 在 Agent 上线或获得更高权限前，先在受控场景中演练，保留 Trace，检查责任
> 证据是否充分，再由人类负责人决定下一步。

它不验证市场规模、收入、合规、系统安全或生产效果，也不执行客户招募。

```text
Protocol Ready != External Validation
Interview Interest != Purchase Intent
Synthetic Rehearsal != Customer Agent Result
Evidence Assessment != Deployment Approval
```

## 2. 目标角色

### A. 企业 AI Agent 平台或应用团队

- 假设：已有功能测试和日志，但上线评审缺少可重放场景、责任证据和统一解释；
- 重点验证：是否愿意把“上线前演练”加入 release gate；
- 主要障碍：真实 Adapter、私有环境、权限与组织责任。

### B. AI 评测、安全测试或红队团队

- 假设：能发现失败，但难以把 Trace、policy 和证据缺口组织成决策材料；
- 重点验证：场景分类、失败/弃权/拒绝差异是否有用；
- 主要障碍：Benchmark 外部效度和自定义场景成本。

### C. AI 治理、风险或内部审计团队

- 假设：制度要求存在，但缺少 Agent 真实行为到责任声明的证据链；
- 重点验证：`SUPPORTED` 与“安全/合规/批准”的边界是否清楚；
- 主要障碍：证据来源可信度、法律责任和现有流程衔接。

不建立具体公司名单，不收集姓名、邮箱或公司名称。

## 3. 访谈与演示流程（30 分钟）

### 0–3 分钟：同意与边界

逐字说明：

> 本次只展示百度千帆真实推理模型在完全合成世界中的已记录运行，不会接收贵方日志、
> Agent、凭据或客户数据。SAEE 不认证安全或合规，也不批准上线。你可以随时停止。

未明确同意则停止。

### 3–10 分钟：先问现状，不展示 SAEE

1. 你们目前如何决定一个 Agent 可以进入上线评审？
2. 是否有受控演练，还是主要依赖测试集、Demo 和生产日志？
3. 工具 timeout、上下文漂移、越权请求分别怎样处理？
4. 出现争议时，谁需要看到哪些证据？

主持人必须记录问题是否由参与者主动提出，不能用 SAEE 术语引导答案。

### 10–20 分钟：运行演示

按 `SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_DEMO.md`：

1. 正常完成；
2. 工具 timeout 后弃权；
3. 指令冲突后拒绝；
4. 有状态 SaaS 发布世界中收集三类证据并停止部署；
5. 查看真实 Provider tool call、State Transition、隐藏评分与 Evidence Candidate；
6. 调用 `evaluate_agent_run`；
7. 查看 20 场景 Benchmark；
8. 展示两个 MCP Tool。

### 20–27 分钟：价值与障碍

1. 哪一个输出能进入你们现有上线评审？
2. 哪个场景最接近真实风险，哪个完全不相关？
3. 还缺哪些环境、工具、记忆或审批信息？
4. 如果只允许客户控制沙箱，集成障碍是什么？
5. 什么情况下你不会使用 SAEE？

### 27–30 分钟：中性下一步

询问是否愿意在另一份单独审批的协议下评审自定义合成场景。只记录
`follow_up_protocol_interest`，不解释为采购、Pilot 承诺或付费意愿。

## 4. 验证指标

| 指标 | 允许值 | 解释边界 |
|---|---|---|
| Problem Recognition | recognized / not_recognized / unclear | 不等于市场验证 |
| Rehearsal Workflow Fit | fit / partial / no_fit / unclear | 不等于采用 |
| Evidence Output Value | useful / partial / not_useful / unclear | 不等于愿意付费 |
| Scenario Relevance | high / mixed / low / unclear | 不等于外部效度 |
| Integration Feasibility | feasible / conditional / infeasible / unclear | 不等于集成完成 |
| Follow-up Protocol Interest | yes / no / unclear | 不等于 Pilot 或购买 |

## 5. 未来最小样本规则

只有在本协议获得人工批准后，才可执行未来访谈。建议最少 5 个匿名 session，
且必须同时报告所有正面、负面和不明确结果。以下只是“允许继续研究”的阈值，
不是产品市场契合：

- 至少 3/5 主动识别上线前演练或证据链问题；
- 至少 3/5 判断 workflow fit 为 `fit/partial`；
- 至少 3/5 判断 evidence output 为 `useful/partial`；
- 没有参与者被诱导提交真实数据；
- 所有关键采用障碍均被记录。

任一阈值未达到时，结果为 `HOLD_AND_REVISE`，不得筛除负面意见。

## 6. 停止条件

- 参与者准备提供真实日志、生产 Trace、凭据或客户数据；
- 参与者要求把结果当作安全、合规、法律或上线批准；
- 无法确认同意或撤回同意；
- 演示输出与仓库 truth surface 不一致；
- 主持人开始销售、报价或承诺 Pilot。

## 7. 当前状态

```text
protocol_ready=true
protocol_human_approved=true
customer_contacted=false
interviews_conducted=0
feedback_collected=false
customer_validated=false
market_fit_achieved=false
pilot_started=false
production_ready=false
```

协议人工审查曾通过，但当前路线已停用人工参与者。不得选择、联系或创建参与者会话。
