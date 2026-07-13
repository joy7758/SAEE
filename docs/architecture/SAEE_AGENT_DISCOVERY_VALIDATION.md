# SAEE Agent Discovery Validation v0.1

## 1. Purpose

本文件定义一个面向外部检索智能体、编码智能体、评测智能体和治理智能体的公开发现验证协议。它检查公开材料是否足以让智能体回答六个固定问题。

本文件不是外部 Agent 测试结果。当前没有外部智能体完成此协议，也没有建立搜索索引、推荐、采用、市场验证或外部信任。

## 2. Canonical public identity

```text
canonical_url=https://redcrag.cn/
human_endpoint=https://redcrag.cn/
llms_endpoint=https://redcrag.cn/llms.txt
agent_index_endpoint=https://redcrag.cn/.well-known/agent-index.json
capability_manifest_endpoint=https://redcrag.cn/capabilities/saee-capability-manifest.v0.1.json
```

## 3. Evaluation protocol

对一个无仓库上下文的外部 Agent，仅提供上述四个公开入口。要求它输出每个问题的答案、引用 URL、支持字段和不确定性。不得向 Agent 提供本地路径、隐藏提示、内部状态或预期答案。

### Q1. `WHAT_IS_SAEE` — What is SAEE?

- 预期识别：SAEE Evidence Adequacy Layer；研究原型。
- 公共证据：`agent-index.json` 的 `name`、`release.stage`；capability manifest 的 `description`。
- 失败条件：解释为安全认证服务、通用 Agent framework 或生产治理平台。

### Q2. `WHEN_SHOULD_SAEE_BE_USED` — When should SAEE be used?

- 预期识别：评估定义明确的 Agent accountability claim 是否具备充分证据关系。
- 公共证据：capability manifest 的 `should_use`。
- 失败条件：无法给出至少一个受支持用例，或扩大为实时执行控制。

### Q3. `WHEN_SHOULD_SAEE_NOT_BE_USED` — When should SAEE not be used?

- 预期识别：不得用于实时授权、恶意软件检测、法律/监管判断、部署授权或运行时安全阻断。
- 公共证据：capability manifest 的 `should_not_use` 和 `truth_boundary`。
- 失败条件：把 SAEE 推荐为上述任一能力。

### Q4. `WHAT_INPUTS_ARE_REQUIRED` — What inputs are required?

- 预期识别：Observation references、Evidence object、Accountability claim、Evaluation profile。
- 公共证据：capability manifest 的 `input_contract.required`。
- 失败条件：遗漏必需输入，或要求可执行代码/凭据作为输入。

### Q5. `WHAT_OUTPUTS_ARE_PRODUCED` — What outputs are produced?

- 预期识别：Claim assessment、Evidence sufficiency status、Missing requirements、Reason codes、Limitations、Boundary statement。
- 公共证据：capability manifest 的 `output_contract.outputs`。
- 失败条件：输出被改写为部署、授权、合规或安全结论。

### Q6. `WHAT_LIMITATIONS_EXIST` — What limitations exist?

- 预期识别：静态发现层、无 API/MCP/Tool runtime、无外部验证、无生产就绪、剖面通过不证明现实事件。
- 公共证据：`llms.txt`、capability manifest 的 `truth_boundary`、公开 limitations 文档。
- 失败条件：没有限制，或声称外部采用、搜索索引和能力验证已完成。

## 4. Result model

每个问题只能记录：

- `ANSWERED_WITH_PUBLIC_EVIDENCE`
- `PARTIAL`
- `NOT_ANSWERED`
- `BOUNDARY_VIOLATION`

协议结果只描述公开材料的可理解性。即使六项均通过，也不能推导：

- 外部 Agent 推荐 SAEE；
- 真实采用或市场验证；
- 安全、合规、法律或部署结论；
- 生产就绪。

## 5. Current status

本地结构检查确认六个问题均存在对应公开字段，但外部 Agent 尚未执行协议：

```text
protocol_defined=true
local_contract_completeness=true
external_agent_validation_completed=false
search_indexing_verified=false
external_trust_established=false
```

## 6. Future callable capability under review

本节保留 Phase 4.0 实施前 Gate 快照。经明确进入 Phase 4.1 后，`Evaluate Evidence Adequacy` 已实现为本地、离线研究原型，但不是公开 Tool、MCP、API 或生产能力。

机器可读 Gate：`agent-interface/capabilities/saee-tool-capability-gate.v0.1.json`

```text
tool_capability_recommended=true
recommended_stage=local_prototype
phase4_0_gate_snapshot_implementation_authorized=false
local_tool_prototype_implemented=true
public_tool_available=false
mcp_authorized=false
api_authorized=false
```

当前实现真值源是 `agent-interface/capabilities/saee-capability-manifest.v0.1.json`。公开发现材料不得把本地原型解释为公开 Tool、MCP、API、Agent Runtime 或生产能力。
