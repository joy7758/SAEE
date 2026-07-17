# Immune Governance Plane
# 免疫治理平面

Audit（审计）, Evidence（证据）, Governance（治理）, Sandbox（沙盒）, and Rollback（回滚） belong to the immune governance plane（免疫治理平面）.

They are not the evolution core.
它们不是演化核心。

## Purpose

The immune governance plane exists to:

- keep unsafe branches from spreading;
- preserve evidence for selection decisions;
- support lineage and rollback;
- maintain license, supply-chain, and permission boundaries;
- keep external trust possible without turning the whole project into an audit platform.

## Boundary

Audit may support selection, lineage, rollback, and external trust.
审计可以支持选择、谱系、回滚和外部信任。

Audit must not become the project identity.
审计不得成为项目身份。

## Agent Evidence Project Integration

`Agent Evidence Project`（历史产品名 `Agent Evidence Receipt`，历史源仓库
`agent-evidence-layer`）在 `SAEE Development Constitution v1.1` 下正式归属本平面，
其角色是 `SAEE Evidence and Immune Subsystem` 的 receipt、integrity、provenance
与 source-completeness 来源。

该归属强化 observation → evidence → fitness → archive → rollback 链路，但不产生
execution authority。当前 `constitutional_ownership=implemented`，同时保持
`source_code_migrated=false`、`runtime_integrated=false`、
`external_integration_validated=false`、`customer_validated=false` 和
`production_ready=false`。

未来迁移必须先复用规范能力清单中的现有 evidence / trace / receipt 能力，再通过
source provenance、schema crosswalk、internal adapter 与 ledger synchronization 门；
禁止把旧仓库整包复制为第二套证据栈。
