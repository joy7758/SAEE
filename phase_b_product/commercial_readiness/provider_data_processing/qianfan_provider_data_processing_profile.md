# Qianfan Provider Data-Processing Inventory

本文件是千帆数据流盘点，不是 DPA、法务批准或生产就绪证明。

- provider: `baidu_qianfan`
- model: `ernie-4.5-turbo-128k`
- observed runs: `3`
- provider network used: `true`
- SAEE MCP network used: `false`
- API key in transcripts: `false`
- blockers closed by profile: `0`

## Sent data

- `system_instruction_for_bounded_tool selection`
- `sanitized numerical observed-trace fixture`
- `MCP-derived JSON Schema tool definitions for exactly two tools`
- `tool result messages returned by the fixed local MCP adapter`
- `final-answer fact prompt containing receipt fields`

## Not sent

- `QIANFAN_API_KEY`
- `candidate source code`
- `local filesystem paths or arbitrary URLs`
- `shell commands or raw logs`
- `customer records or production data`
- `SAEE private evolution internals`

## Official reference

- https://cloud.baidu.com/doc/qianfan/s/emh4stmvj
- https://cloud.baidu.com/doc/qianfan/s/Umleypdhw (agreement catalog)
- Official text remains independent-agent review input; retention/DPA/production approval are not inferred.

## Unresolved policy questions

- explicit retention period, deletion mechanism, and backup cycle for the selected API mode
- DPA, security annex, and cross-border/data-processing terms for commercial use
- applicable agreement version, priority, and enterprise-plan terms
