# 智能体支持问题上报契约 v0.1

这是 SAEE 商业预览的机器可读支持入口。它用于让客户智能体提交一条脱敏的、可检索的问题摘要，
并得到明确的 owner 支持通道状态；它不是生产客服系统，也不会自动联系任何人。

## 调用

```bash
python3 scripts/saee_agent_support_case_validator.py
```

默认读取 `agent-interface/examples/agent-support-case-request.json`。替换 `--input` 可验证同结构请求。

## 必须保持的边界

- `contact_mode` 固定为 `agent_receipt_only`。
- `summary` 只允许短文本；不得包含 URL、代码、日志、密钥、邮箱、手机号或客户记录。
- `evidence_refs` 只能引用仓库中稳定的契约 ID，不填写路径、网址或秘密。
- `support_status` 固定为 `owner_support_channel_required`。
- `external_dispatch_performed=false`、`customer_contacted=false`、`production_ready=false`、`blockers_closed=0`。

通过验证后，智能体应把回执交给项目 owner 决定是否进入现有人工支持证据路径；验证器本身不派发。
