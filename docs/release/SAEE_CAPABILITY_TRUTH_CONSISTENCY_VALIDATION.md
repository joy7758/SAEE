# SAEE Capability Truth Consistency Validation v0.1

SAEE validates consistency among capability descriptions. It does not establish external trust, adoption, certification, or production readiness.

SAEE 验证能力描述之间的一致性，不建立外部信任、采用、认证或生产就绪结论。

## 1. 目的

Phase 10.9 对 Capability Object、Registry、Package、Alpha Release、Public Surface、MCP、HTTP 和 Capability Runtime 做本地只读交叉检查，防止同一操作在不同表面被描述为未来、已实现、公开服务或生产能力。

## 2. 单一能力真值

能力集合：

- `saee.agent-reliability`
- `saee.evidence-evaluation`

历史 Object / Registry ID `saee.evidence-adequacy` 显式映射到 `saee.evidence-evaluation`。该映射保留兼容性，不重命名历史公共概念。

## 3. 版本命名空间

| 命名空间 | 版本 |
|---|---|
| Capability Object / Registry | `0.1` |
| Capability Package contract | `1.0.0` |
| Alpha Release | `0.1.0` |
| MCP / HTTP Adapter | `0.1.0` |

这些是不同工件版本。验证器在各自命名空间内核对，不把它们错误压成一个数字。

## 4. 操作真值

```text
evaluate_agent_run = IMPLEMENTED
evaluate_evidence  = IMPLEMENTED
rehearse_agent     = CONTRACT_ONLY
```

实现状态来自 Package、Release、Public Surface 和 Runtime；MCP Tool 与 HTTP route 的操作集合必须完全相同。

## 5. Lifecycle 与协议

- Object / Registry：`LOCAL_PROTOTYPE`；
- Package：`local_contract_alpha`；
- Release：`ALPHA_PREPARATION`；
- Runtime：`local_alpha`；
- MCP：本地 stdio；
- HTTP：`127.0.0.1` localhost；
- 协议集合：`MCP`、`HTTP Contract`。

这些状态都归属于 Alpha/local/not-production，不代表公共互操作性。

## 6. 边界

验证器要求：公共服务、公共发布、生产、Marketplace、外部采用、客户验证和认证声明均为 false。任何单一表面升级都会产生稳定 conflict reason code。

## 7. 冲突测试

11 个 fixture 覆盖身份、版本、缺失操作、状态漂移、生产升级、Marketplace、公共 API、MCP 夸大、HTTP 公共绑定、外部采用和虚假认证。

## 8. 限制

- 只验证描述一致性，不重新运行模型或评估业务结果；
- 不证明实现无缺陷；
- 不建立外部信任、采用或生态支持；
- 不连接外部 Agent 或客户数据；
- 不发布或部署 Alpha；
- PASS 不授权 lifecycle promotion。
