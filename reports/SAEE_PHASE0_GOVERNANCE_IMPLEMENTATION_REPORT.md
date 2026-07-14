# SAEE Phase 0 Governance Implementation Report

## 1. 创建文件

Phase 0 新增 23 个文件：

- `governance/README.md`
- `governance/constitution/constitution-alignment.md`
- `governance/registry/asset-registry.json`
- `governance/registry/repository-registry.json`
- `governance/registry/capability-crosswalk.json`
- `governance/registry/mcp-registry.json`
- `governance/registry/product-registry.json`
- `governance/registry/external-system-registry.json`
- `governance/decisions/ADR-0001-canonical-source.md`
- `governance/decisions/ADR-0002-agent-evidence-boundary.md`
- `governance/decisions/ADR-0003-mcp-namespace.md`
- `governance/migration/migration-policy.md`
- `governance/migration/protected-assets.md`
- `governance/migration/forbidden-actions.md`
- `governance/codex/codex-governance-rules.md`
- `governance/codex/change-template.md`
- `governance/schemas/asset-registry.schema.json`
- `governance/schemas/capability.schema.json`
- `governance/schemas/mcp-entry.schema.json`
- `governance/schemas/product.schema.json`
- `scripts/saee_governance_registry_check.py`
- `tests/test_governance_registry.py`
- `reports/SAEE_PHASE0_GOVERNANCE_IMPLEMENTATION_REPORT.md`

治理启动指针同步加入 `AGENTS.md`、`README.md` 和 `llms.txt`。这些入口只包含
规则和路径，不复制动态能力、仓库、MCP、产品或外部系统状态。

## 2. 未修改内容

本次没有修改：

- evaluator、Evidence Adequacy、Capability Runtime 或业务逻辑；
- 任何现有 MCP server、tool name、namespace、transport 或 endpoint；
- `sites/saee-commercial` 网站代码和公开文案；
- 阿里云商品 `68657`、`68658` 的材料、价格或平台状态；
- Agent Evidence Receipt 源码、runtime、部署、签名、tenant、token 或计量；
- `agent-evidence-layer`、`agent-evidence`、POP、AOP、ARO 或其他仓库；
- Git remote、分支历史、已有 dirty changes 或外部系统。

Phase 0 开始前已存在 21 项 dirty entry。它们被记录为受保护输入，没有 reset、
restore、clean 或覆盖。

## 3. 资产注册范围

`asset-registry.json` 注册 12 个必要资产：

1. SAEE；
2. Agent Evidence Layer；
3. `agent-evidence`；
4. Agent Receipt Validator；
5. POP；
6. AOP；
7. ARO Audit；
8. Digital Biosphere Architecture；
9. SAEE Website；
10. Aliyun Product `68657`；
11. Aliyun Product `68658`；
12. `redcrag.cn`。

Asset Registry 只保存稳定身份、角色、位置、关系和迁移处置，不成为 capability
status 或 marketplace live-state 的第二真源。

## 4. 真源规则

```text
canonical_engineering_source=/Users/zhangbin/Documents/SAEE
canonical_source_scope=LOCAL_ONLY
canonical_git_remote=NOT_ESTABLISHED
canonical_capability_source=capability-package/manifest.json#canonical_inventory
capability_crosswalk_is_source=false
public_repository_inheritance=PROHIBITED_WITHOUT_EXPLICIT_DECISION
```

Repository Registry 记录 SAEE 为唯一 `canonical` 本地仓。Agent Evidence Layer
是 `external subsystem`，没有写成 `merged`。公开仓、网站 remote 和相邻协议仓
只能是 `reference` 或 `external`，不能因名称或 host 自动继承规范权威。

## 5. MCP 边界

MCP Registry 注册 5 个 surface：

- SAEE canonical 两工具本地 stdio；
- Qianfan compatibility wrapper；
- Capability Package internal MCP；
- legacy observed-trace MCP；
- Agent Evidence Receipt external-product MCP。

```text
saee.*=SAEE_ONLY
receipt.*=AGENT_EVIDENCE_RECEIPT_ONLY
canonical_saee_mcp=saee.agent_readiness_mcp_stdio
agent_evidence_receipt_mcp_is_saee_canonical=false
```

`canonical=true` 按 owner/namespace scope 判断。Agent Evidence Receipt MCP 可是
Receipt 产品自己的 canonical surface，但永远不因此成为 SAEE canonical MCP。
Phase 0 没有修改其现有三个未加前缀的 tool name。

## 6. Agent Evidence 关系

ADR-0002 固定关系：

```text
relationship=SAEE_SUBPROJECT
subsystem=SAEE_EVIDENCE_AND_IMMUNE_SUBSYSTEM
shared_contract_infrastructure=ELIGIBLE_AFTER_GATES
source_code_migrated=false
runtime_integrated=false
marketplace_transferred=false
production_ready=false
```

共享范围仅限未来经过 provenance、license、version 和 compatibility 检查的 schema
crosswalk、canonicalization/digest 语义、validation envelope、reason code 和负面
fixture。Phase 0 没有复制实现。

## 7. Capability 映射

Capability Crosswalk 映射 9 项：

- `saee.evaluate_agent_run`；
- `saee.evaluate_evidence`；
- `evidence.receipt`；
- `evidence.validation`；
- `capability.registry`；
- `mcp.discovery`；
- `saee.otel_sdk_or_otlp_ingestion`；
- `saee.external_identity_binding`；
- `saee.delegation_binding`。

最后三项固定为 `missing`。Crosswalk 不改变 canonical inventory，不把文档或
adapter 的存在推断为 capability implementation。

## 8. Validator 结果

通过：

```text
python3 scripts/saee_governance_registry_check.py
SAEE_GOVERNANCE_REGISTRY_CHECK: PASS
registries=6/6
schemas=4/4
assets=12
repositories=9
capabilities=9
mcp_entries=5
products=4
production_ready=false
```

```text
python3 -m unittest tests/test_governance_registry.py
Ran 8 tests
OK
```

另外通过：

- `python3 scripts/saee_capability_progress_ledger_smoke.py`；
- `python3 scripts/saee_development_constitution_smoke.py`；
- `git diff --check`。

仓库已有的 `make check` 已执行，但在第一项 `scripts/mainline_guard.py` 中被任务前
既有 dirty file `.codex/context.md` 阻塞：`codex_context_check.py` 仍要求旧短语
`AI agent long-term stability evaluation`，而既有 v1.1 identity change 已替换该
短语。Phase 0 禁止修改、restore 或清理这个任务前文件，因此该失败按原样保留，
不通过扩大本次 scope 修复。

## 9. 风险

1. Canonical Git remote 仍未建立。
2. Phase 0 baseline 之前已有 v1.1 constitution、Alibaba repair 和其他未提交改动；
   必须保持提交隔离。
3. `make check` 的旧 context expectation 与既有 v1.1 identity change 漂移。
4. Agent Evidence Layer 仍有大量 dirty source 和未建立 remote，不能开始代码迁移。
5. MCP usage/caller evidence 仍为 unknown，不能 deprecate legacy/compatibility surface。
6. 网站和 marketplace 是投影/外部状态，尚未由 Phase 0 registry 自动同步。
7. External product runtime 只有 bounded alpha evidence，不是 SAEE production runtime。

## 10. 下一阶段建议

下一阶段只能在以下前置条件满足后进入 `PHASE1_CAPABILITY_ALIGNMENT`：

1. 单独处理并提交或明确处置任务前 v1.1 constitution changes；
2. 修复 `.codex/context.md` 与 `codex_context_check.py` 的身份契约漂移；
3. 决定 canonical Git remote/public mirror 关系；
4. 为 Agent Evidence Layer 冻结 clean commit、provenance、license 和 backup；
5. 建立 MCP caller/usage ledger；
6. 为任何 capability merge 重新执行 Agent Recommendation Gate。

Phase 1 才可提出 capability alignment；它仍不能自动授权仓库合并、MCP rename、
runtime deployment、marketplace mutation 或生产声明。

## Final status

```text
PHASE0_STATUS=COMPLETE
CANONICAL_SOURCE=LOCAL_ONLY
CANONICAL_GIT_REMOTE=NOT_ESTABLISHED
ARCHITECTURE_REWRITE=NOT_STARTED
BUSINESS_LOGIC_CHANGE=NONE
MCP_CHANGE=NONE
WEBSITE_CHANGE=NONE
MARKETPLACE_CHANGE=NONE
AGENT_EVIDENCE_RUNTIME_CHANGE=NONE
PRODUCTION_READY=false
NEXT_PHASE=PHASE1_CAPABILITY_ALIGNMENT
NEXT_PHASE_GATE=HOLD_UNTIL_PREEXISTING_GOVERNANCE_AND_MAINLINE_DRIFT_RESOLVED
```
