# SAEE Consent and Boundary Script

Read this before the human-run external customer or target-user session.

## Plain Consent Script

这次访谈的目的，是判断 SAEE 的本地演示和结果表达是否能帮助你理解多个 AI 智能体、工作流或策略版本的长期稳定性和部署前风险。

我只会记录摘要、评分和非敏感意见。请不要提供源码、密钥、生产数据、客户数据或内部机密流程。

你可以随时跳过问题或停止访谈。你的反馈只会作为 SAEE 商用准备的内部验证材料，除非另行获得你的明确许可，不会公开你的姓名、公司或原话。

SAEE 当前不是生产可用产品，也没有公开 SDK。本次访谈不会要求你上线使用，也不会形成采购承诺。

## Boundary Confirmation

Before continuing, confirm:

- Participant understands this is feedback, not a production rollout.
- Participant will not share secrets or production/customer data.
- Participant agrees that only summary feedback and scores may be recorded.
- Participant understands SAEE private core details will not be disclosed.

## Required Flags After Session

These flags must remain false unless a real issue occurred and is explicitly recorded:

```yaml
secrets_collected: false
production_data_collected: false
customer_data_uploaded: false
private_core_disclosed: false
production_ready_claim_made: false
```
