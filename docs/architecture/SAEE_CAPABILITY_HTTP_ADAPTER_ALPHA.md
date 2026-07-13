# SAEE Local HTTP Capability Adapter Alpha v0.1

> SAEE HTTP Adapter is a localhost transport layer for declared capabilities. It does not provide public API access or production execution.

> SAEE HTTP Adapter 是已声明能力的本地 HTTP 调用层，不提供公网 API 或生产执行能力。

## 架构

```text
HTTP Client -> 127.0.0.1 Adapter -> invoke_capability -> Canonical SAEE Service
```

HTTP 与 MCP 是并列运输层；二者都不能直接导入 evaluator，也不能改变 Capability Runtime 的结果。

## 固定端点

| Endpoint | Operation |
|---|---|
| `POST /capabilities/evaluate-agent-run` | `evaluate_agent_run` |
| `POST /capabilities/evaluate-evidence` | `evaluate_evidence` |
| `POST /capabilities/rehearse-agent` | `rehearse_agent`，返回 `CONTRACT_ONLY` |

路径与 body operation 不一致会拒绝，不会执行 body 指定的另一个能力。没有 health、admin、debug、文件上传或隐藏 endpoint。

## 边界

Server 构造器只接受端口，不接受 host；绑定常量为 `127.0.0.1`。请求和 payload 只在内存中处理，不写入文件、不记录日志。调用者使用本契约即声明 payload 不含客户数据；这不是技术上的数据分类证明。

```text
runtime_stage=local_alpha
http_adapter_available=true
bind_address=127.0.0.1
network_public_access=false
public_service=false
customer_data=false
external_world_actions=false
oauth_available=false
multi_tenant=false
production_ready=false
```

