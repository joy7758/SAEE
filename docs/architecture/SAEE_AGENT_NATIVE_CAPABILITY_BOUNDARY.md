# SAEE Agent-Native Capability Boundary v0.1

## Canonical Boundary

> SAEE provides evidence adequacy evaluation capability. It does not provide authorization enforcement, security certification, or legal determination.

> SAEE 提供证据充分性评估能力，不提供授权执行、安全认证或法律判断能力。

## Capability Scope

SAEE Evidence Adequacy Layer 判断一个封闭的本地证据包是否满足指定责任声明剖面的字段和关系要求。它可以输出：

- `PASS / FAIL` profile result；
- missing requirements；
- invalid or inconsistent relationships；
- stable reason codes；
- truth boundaries and limitations。

`PASS` 只表示固定本地剖面要求得到满足，不证明事件真实发生、身份真实、授权在外部系统有效或系统可以部署。

## Non-Capabilities

SAEE 不提供：

- real-time authorization enforcement；
- Agent、Tool 或 Memory 控制；
- runtime safety blocking；
- malware detection 或未知代码分析；
- security certification；
- regulatory compliance conclusion；
- legal determination；
- production deployment approval；
- observability、tracing、policy engine 或 security monitoring 替代能力。

## Composition Boundary

```text
Observation Layer
  ↓ candidate references, not Evidence
Evidence Layer
  ↓ claim assessment, missing requirements, reason codes
Governance Layer
  ↓ human-owned interpretation and authorization
```

SAEE 位于 Evidence Layer 的证据充分性评估位置。它可以消费 Observation 引用并向 Governance Layer 提供决策支持，但不会把 Observation 自动升级为 Evidence，也不会替 Governance Layer 做决定。

## Manifest Truth Boundary

Capability Manifest 描述当前契约，不证明契约行为已经由外部智能体独立验证，不建立市场采用，不增加 MCP、API、Runtime Integration 或自动推荐能力。
