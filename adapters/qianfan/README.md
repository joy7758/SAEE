# Qianfan + SAEE Adapter

Canonical implementation:

- Descriptor: `agent-interface/qianfan/saee-qianfan-agent-readiness-mcp.v0.1.json`
- Entry point: `scripts/saee_qianfan_readiness_mcp_stdio.py`
- Offline validation: `scripts/saee_qianfan_readiness_mcp_smoke.py`
- Bounded real-provider receipt validation: `scripts/saee_qianfan_readiness_live_receipt_smoke.py`

The evidence is limited to sanitized synthetic scenarios and provider model
roundtrips. It does not establish Qianfan-native MCP support, official Baidu
integration, customer validation, or production readiness.
