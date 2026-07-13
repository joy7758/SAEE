# SAEE Capability Service Local Runtime Alpha v0.1

## 1. 目标

Phase 10.2 为 Phase 10.1 已声明能力增加一个本地、稳定、只读的调用层：

```text
Agent-like Local Caller
  -> Invocation Contract
  -> Capability Router
  -> Existing SAEE Service
  -> Bounded Result
  -> Inline Invocation Receipt
```

它不增加新的 evaluator，不接入外部 Agent，不监听端口。

> SAEE Capability Runtime is a local invocation layer for declared capabilities. It does not provide public access or production execution.

> SAEE Capability Runtime 是已声明能力的本地调用层，不提供公网访问或生产执行能力。

## 2. Capability Package 与 Capability Runtime

| 层 | 回答的问题 | Phase 10.2 状态 |
|---|---|---|
| Capability Package | SAEE 是什么、何时使用、契约是什么 | 机器可读、本地文件 |
| Capability Runtime | 如何通过统一请求调用已有本地能力 | 本地 Alpha |
| Public API / MCP Transport | 如何被网络客户端访问 | 未提供 |

## 3. Router

`capability_registry_loader.py` 读取 Package 的 Manifest、Capability Card 和 MCP Tool 描述，确认三个表面完全一致。任何未声明操作、隐藏操作或 Capability ID 漂移都以失败闭合处理。

固定操作：

| 操作 | 路由 | 状态 |
|---|---|---|
| `evaluate_agent_run` | `agent_run_capability.evaluate_agent_run()` | 已实现、本地离线 |
| `evaluate_evidence` | `local_evidence_tool.evaluate_evidence_tool()` | 已实现、本地离线 |
| `rehearse_agent` | 不调用 handler | `CONTRACT_ONLY_NOT_IMPLEMENTED` |

## 4. Invocation Contract

请求必须提供稳定 `request_id`、Capability ID、操作、payload 和调用者上下文。调用者必须显式声明：没有客户数据、没有网络请求、没有外部世界动作。

响应状态只有：

- `SUCCESS`：本地调用完成；不等于任务成功。
- `REJECTED`：请求、能力、操作或 payload 被拒绝。
- `FAILED`：预留的内部失败状态，不包含私密异常内容。
- `CONTRACT_ONLY`：能力仅有契约，没有实现。

## 5. Invocation Receipt

Receipt 只返回：ID、请求摘要、Capability ID、操作、调用者声明时间、状态、Runtime 版本和结果摘要引用。它不保存 payload、密钥、凭据、chain of thought（思维链）或私有模型状态，也不写入磁盘。

调用者声明时间被原样绑定，`timestamp_source=caller_declared`；它不是可信时间戳或外部时间证明。

## 6. 安全与演化边界

- 无网络监听或公网 API；
- 无标准 MCP transport；
- 无子进程、shell、动态导入、插件或外部代码执行；
- 无客户数据；
- 无外部世界动作；
- 无授权、认证、排名或部署批准；
- 不修改数字生物圈进化引擎核心；
- 强化 Trait Extraction、Sandbox Development 和 Evolutionary Archive / Rollback Immune System。

## 7. 本地使用

```bash
python3 scripts/saee_capability_runtime_demo.py
python3 scripts/saee_capability_runtime_smoke.py
```

## 8. 当前真值

```text
runtime_stage=local_alpha
package_operations_verified=true
network_api_available=false
public_service=false
standard_mcp_transport=false
customer_data=false
external_world_actions=false
production_ready=false
```

