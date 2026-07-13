# SAEE 智能体报价申请契约 v0.1

这是一个不带价格、不收款、不联系客户的商业化预报价入口。智能体只能
提交方案范围、租户标识和预估用量，回执固定为
`owner_pricing_review_required`。

- Schema：`agent-interface/schemas/commercial-quote-request.schema.json`
- Response schema：`agent-interface/schemas/commercial-quote-response.schema.json`
- 示例：`agent-interface/examples/commercial-quote-request.json`
- 校验：`python3 scripts/saee_commercial_quote_request_validator.py`

内部草案中的价格占位符不会进入该契约。通过校验不等于价格批准、销售报价、
支付配置、客户联系、生产就绪或阻塞关闭。
