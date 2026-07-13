# SAEE Design Partner 单次会话入口门 v0.1

状态：`inactive_human_participants_excluded`。

用户已明确排除人工参与者。本入口门已停用，仅保留历史审计字段；不得填写、授权或创建
任何人工会话。当前验证入口为 `SAEE Agent Preference Multi-Round Simulation v0.1`。

协议已经人工批准，但这不授权联系任何参与者。进入第一次会话前，人工必须填写：

1. 匿名参与者代号，例如 `participant-001`；
2. 参与者画像：Agent 平台团队、评测/红队团队或治理/风险团队；
3. 组织类型，不填写组织名称；
4. 已确认愿意参加问题访谈；
5. 单次会话日期和人工主持人代号。

## 首个参与者画像推荐

推荐优先选择：

```text
AI_AGENT_PLATFORM_TEAM
```

排序：

1. `AI_AGENT_PLATFORM_TEAM`：最直接验证“Agent 上线前先演练”能否进入现有 release gate，
   对应商业战略第一阶段的 Agent Readiness Assessment；
2. `AI_EVALUATION_RED_TEAM_TEAM`：适合验证场景设计、失败分类和证据输出能否进入评测流程；
3. `AI_GOVERNANCE_RISK_TEAM`：适合验证责任声明和治理解释，但距离第一产品入口稍远。

该排序只是选择建议，不代表任何组织已经同意、被联系、成为客户或验证了市场需求。

不得填写姓名、邮箱、电话、公司名称、客户日志、凭据或真实 Agent 数据。

当前真值：

```text
participant_selected=false
consent_confirmed=false
session_authorized=false
outreach_authorized=false
customer_contacted=false
interviews_conducted=0
```

只有人工另行提供上述非个人化字段并明确授权单次会话后，才可生成 session 文件；仍不得
自动发邮件、消息或执行客户 Agent。

人工确认时需要提供以下六项非个人化字段：

```text
participant_alias=participant-001
participant_profile=AI_AGENT_PLATFORM_TEAM
organization_type=<组织类型，不填写名称>
consent_confirmed=true
session_date=<RFC 3339 日期时间>
human_facilitator_alias=<人工主持人代号>
```

其中 `consent_confirmed=true` 只能在人类已经确认对方愿意参加后填写。选择画像本身仍保持：

```text
selection_is_customer_contact=false
selection_authorizes_outreach=false
selection_establishes_customer_validation=false
```
