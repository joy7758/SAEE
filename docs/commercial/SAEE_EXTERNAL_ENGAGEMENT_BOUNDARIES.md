# SAEE External Engagement Boundaries v0.1

## 核心边界

```text
Design Partner Validation != Customer Acquisition
Interview != Customer Commitment
Feedback != Market Validation
Interest != Willingness To Pay
```

## Before Consent

- 不请求或接收客户数据、私有日志、生产 traces、凭据或个人信息。
- 不记录姓名、邮箱、公司名称或联系方式。
- 不展示为参与者定制的报告，不创建 CRM、合同、价格或销售机会。
- 说明研究目的、合成材料范围、匿名记录方式、停止权和非销售性质。
- 未得到明确同意时不得开始或保留任何回答。

## During Validation

- 只展示仓库内 synthetic examples，除非未来存在单独且明确的数据审批；本协议不提供该审批。
- 不录音，不上传文件，不要求屏幕共享私有系统。
- 只记录角色类别、组织类型类别和不含身份信息的工作流反馈。
- 不引导参与者表达购买、预算、采购时间或客户承诺。
- 发现私有、生产或个人信息时立即停止记录并要求对方不要发送。

## After Validation

- 反馈只能用于修订问题假设、报告结构和采用障碍清单。
- 任何后续联系都需要单独授权；`follow_up_interest=yes` 不是联系授权。
- 不得把反馈升级为客户验证、市场契合、收入机会或客户采用结论。
- 若未来考虑 Pilot，必须单独通过 Pilot、隐私、数据、安全、执行和停止权限审批。

## 当前真值

```text
validation_stage=protocol_only
customer_contacted=false
feedback_collected=false
customer_data_received=false
personal_data_stored=false
pilot_started=false
customer_validated=false
market_fit_achieved=false
revenue_opportunity_confirmed=false
```
