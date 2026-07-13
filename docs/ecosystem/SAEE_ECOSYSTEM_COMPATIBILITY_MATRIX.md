# SAEE Ecosystem Compatibility Matrix v0.1

| Integration | Status | Evidence boundary |
|---|---|---|
| MCP stdio | `local_tested` | SAEE 本地 Adapter smoke；不代表第三方互操作。 |
| HTTP local | `local_tested` | `127.0.0.1` Adapter smoke；不是公共 API。 |
| LangGraph | `not_tested` | 未连接、未验证。 |
| CrewAI | `not_tested` | 未连接、未验证。 |
| OpenAI Agents | `not_tested` | 未连接、未验证。 |
| Claude ecosystem | `not_tested` | 未连接、未验证。 |
| Cloud marketplace | `submitted_review_in_progress` | 阿里云商品 `cmfw00074657` 已提交，状态为“审核中”“未上架”；不代表平台批准、正式上架、客户验证或生产就绪。 |

`local_tested` 只表示 SAEE 自身本地适配器通过仓库测试，不表示外部框架支持、采用或官方兼容认证。
