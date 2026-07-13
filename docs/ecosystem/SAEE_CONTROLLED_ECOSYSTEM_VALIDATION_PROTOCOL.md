# SAEE 受控生态验证协议 v0.1

## Purpose

为未来外部参与者定义可重复、最小权限、可记录的 SAEE 兼容性验证流程。

本协议验证 future external compatibility，不验证 adoption。当前没有参与者被邀请、联系或连接。

## Future participant categories

- `agent_framework`
- `cloud_platform`
- `developer`
- `research_group`

这些是未来分类，不代表任何组织或产品已经参与。

## Validation dimensions

### 1. Discovery Compatibility

参与者能否从 `.well-known`、Public Surface 和 Alpha Manifest 找到 SAEE？

### 2. Capability Understanding

参与者能否区分 `saee.agent-reliability`、`saee.evidence-evaluation` 以及不适用场景？

### 3. Invocation Compatibility

参与者能否在受控本地环境通过 MCP stdio、localhost HTTP 或通用 adapter pattern 调用现有 Runtime？

### 4. Result Interpretation

参与者能否正确理解 `SUPPORTED`、`INSUFFICIENT_EVIDENCE`、reason codes 与 Receipt，不把结果升级为认证或批准？

### 5. Boundary Preservation

参与者能否避免授权、认证、安全保证、生产、Marketplace 和采用越界？

## Future validation flow

```text
Explicitly authorized future participant
  -> protocol instance
  -> Alpha capability package
  -> local controlled integration test
  -> structured feedback without sensitive data
  -> bounded validation evidence
```

## Entry gate

本协议本身不授权外部验证。未来执行前仍需独立批准参与者、数据、环境、权限、保留策略和发布范围。
