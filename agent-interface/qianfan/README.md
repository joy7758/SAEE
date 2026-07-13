# SAEE 百度千帆函数调用宿主
# SAEE Baidu Qianfan Function Host

这是一个显式启用、用户自带千帆凭据的本地宿主桥接器。百度千帆负责选择
function tool，桥接器把合法调用转发到 SAEE 固定 MCP stdio 服务。它不是千帆
原生 MCP，也不是通用智能体编排框架。

This is an opt-in local bring-your-own-Qianfan-credential host bridge. Qianfan
selects a function tool; the bridge forwards a valid call to the fixed SAEE MCP
stdio server. It is not Qianfan-native MCP and is not a generic agent
orchestrator.

## 固定调用链 / Fixed call chain

```text
Qianfan chat/completions function calling
→ scripts/saee_qianfan_mcp_host.py
→ scripts/saee_mcp_stdio.py
→ describe_saee / compare_observed_traces
→ schema-valid SAEE receipt
→ Qianfan final explanation
```

## 凭据 / Credential

运行进程只从 `QIANFAN_API_KEY` 环境变量读取密钥。密钥不会进入 prompt、MCP
环境、JSON-RPC、receipt、stdout、stderr 或证据文件。不要通过命令行参数传递
密钥。

The process reads the key only from `QIANFAN_API_KEY`. The key is excluded from
the prompt, MCP child environment, JSON-RPC, receipt, stdout, stderr, and
evidence files. Never pass it as a command-line argument.

## 本地运行 / Local run

```bash
set -a
source .env.local
set +a
python3 scripts/saee_qianfan_mcp_host.py
```

写入去密钥证据 / Write redacted evidence:

```bash
python3 scripts/saee_qianfan_mcp_host.py --write-evidence --evidence-dir agent_recommendation/agent_first_validation/run_005
```

## 非协商边界 / Non-negotiable boundary

- exactly two tools: `describe_saee`, `compare_observed_traces`;
- fixed `https://qianfan.baidubce.com/v2/chat/completions` endpoint and fixed local MCP argv;
- no endpoint, command, server, path, URL, or API-key CLI argument;
- the live validation sends only the explicitly approved sanitized numerical
  fixture;
- no candidate execution, trace capture, production monitoring, external-world
  action, authenticity certification, no-PII certification, customer validation,
  or production-readiness claim.

验证状态 / Validation status:

- `run_005` contains three live roundtrip directories with redacted transcripts;
- provider network was used, while SAEE MCP remains local stdio (`saee_mcp_network_used=false`);
- this is a user-supplied-credential host bridge, not Qianfan-native MCP.

官方接口依据 / Official API basis:

- <https://cloud.baidu.com/doc/qianfan-docs/s/qm8qxemze>
- <https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb>
- <https://intl.cloud.baidu.com/en/doc/qianfan/s/xm95lyys5-intl-en>
