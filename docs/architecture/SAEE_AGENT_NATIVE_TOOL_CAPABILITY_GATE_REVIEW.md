# SAEE Agent-Native Tool Capability Gate Review v0.1

> Historical scope: this document and its machine Gate preserve the Phase 4.0 pre-implementation decision snapshot. After explicit Phase 4.1 approval, current implementation status is defined by `agent-interface/capabilities/saee-capability-manifest.v0.1.json`; this Gate must not be read as the current prototype availability record.

## 1. Purpose

This review determines whether SAEE should expose a callable capability for agent workflows.

本审查只决定候选能力、最小调用边界、安全约束和推荐实现顺序。它不创建 Tool、MCP、API、CLI endpoint、Agent Runtime 或外部集成。

```text
Capability Gate != Tool Implementation
Invocation Design != Agent Deployment
Tool Contract != Tool Availability
```

### Agent recommendation gate

如果潜在客户需要“让本地 Agent 判断一组证据是否满足指定责任声明剖面”，会推荐 SAEE 吗？

```text
answer=recommend
scope=local_deterministic_evidence_adequacy_prototype_direction_only
callable_tool_available=false
implementation_authorized=false
```

推荐原因：现有 evaluator、固定 profiles、稳定 reason codes、正反例和离线 smoke 已形成可复用函数基础。不推荐直接进入 MCP/API，因为输入限制、transport 安全、身份与多租户边界尚未验证。

### Required design check

1. 强化 `Pareto Fitness Evaluation`：把固定责任声明的证据充分性判断包装为可组合候选能力。
2. 改善 selection/composition，不扩大 sensing、执行或权限。
3. 保留许可、供应链、权限和未知代码不执行边界。
4. Evidence capability 仍是 Digital Biosphere Evolution Engine 的子系统投影，不把 SAEE 改写为 audit-first SDK。

## 2. Candidate Capability Analysis

### Candidate: `Evaluate Evidence Adequacy`

目的：对一个封闭、非可执行的本地证据对象，使用仓库固定 profile 判断其是否满足指定 accountability claim 的字段与关系要求。

概念输入：

- `evidence_object`
- `accountability_claim`
- `evaluation_profile`

概念输出：

- `claim_assessment`
- `evidence_sufficiency_status`
- `missing_requirements`
- `reason_codes`
- `limitations`
- mandatory `boundary_statement`

候选能力不得暴露或执行：

- authorization allow/deny；
- deployment decision；
- policy enforcement；
- Agent、Tool、Memory 或 Runtime control；
- unknown code、external URL 或 dynamic profile；
- legal、compliance 或 security conclusion。

### Existing implementation facts

- `saee_backend.services.evidence_adequacy.evaluate_evidence_adequacy()` 已是本地确定性函数；
- evaluator 只加载仓库控制的四个 profile，不接受调用者提交的任意 profile 代码；
- closed JSON parser 拒绝重复 key；
- evaluator 不联网、不启子进程、不执行候选代码；
-当前 CLI 是既有开发入口，不是本 Gate 创建的 Agent Tool endpoint。

### Contract alignment issue

现有 Capability Manifest 把 `observation_references` 列为必需逻辑输入，但 evaluator 不消费该字段。本 Gate 的最小 Tool contract 不得静默声称完全等同于 Manifest contract。下一 PR 必须选择并测试一种显式映射：

1. 把 Observation reference 作为 optional、non-evaluated provenance metadata；或
2. 在 Tool-specific contract 中明确声明只执行 Evidence Layer evaluation，并版本化与 Manifest 的差异。

在该映射被实现和测试前，`implementation_authorized=false`。

## 3. Invocation Options Analysis

| Option | Advantages | Risks | Security implications | Recommended stage |
|---|---|---|---|---|
| A. Local Function Tool | 最小 trust boundary；直接复用确定性 evaluator；无网络和外部认证；易做 hostile tests | Python 进程内调用可能被上游误解释为授权；需要固定输入上限和不可反射边界 | 只接受内存 JSON；固定 profile selector；无 side effects；fail closed | **First prototype** |
| B. CLI Tool | 现有 CLI 形态接近；进程隔离和退出码清晰；适合人工复现 | 文件路径、工作目录、stdout/stderr、subprocess 编排扩大边界 | 需要路径 allowlist、大小限制、稳定 JSON stdout、禁止任意文件和 shell interpolation | After Local Function |
| C. MCP Tool | Agent framework 易发现和组合；可声明机器契约 | 远程或宿主调用容易被误认为 production capability；工具链可能自动串联副作用 | 需要 transport、host、tool permission、input limit、tenant/identity 和 tool-result interpretation gate | Deferred |
| D. HTTP API | 跨语言、跨系统；可独立扩容 | 最大攻击面；认证、授权、租户隔离、限流、日志、数据治理、网络安全均未就绪 | 必须先有 production identity、RBAC、tenant isolation、operations 和 privacy/security evidence | Deferred longest |

Gate 结论：只推荐 Option A 的本地原型方向。B/C/D 均未授权。

## 4. Minimum Tool Contract

### Conceptual request

```json
{
  "tool_contract_version": "0.1",
  "evidence_object": {},
  "accountability_claim": "RESOURCE_AUTHENTICITY",
  "evaluation_profile": "resource-authenticity.v0.1"
}
```

Rules：

- `accountability_claim` 只能是四个固定 claim 之一；
- `evaluation_profile` 是仓库固定 profile ID，不接受文件路径、URL、代码或任意 profile JSON；
- profile 必须与 claim 一一匹配；
- `evidence_object` 必须是 closed JSON object；
- 原型建议 `max_input_bytes=1048576`，超限 fail closed；
- 不接受凭据、客户记录、未知代码或可执行载荷；
- Prompt-like strings are inert evidence data and are never interpreted as instructions。

### Conceptual response

```json
{
  "claim_assessment": "PASS_OR_FAIL",
  "evidence_sufficiency_status": "PROFILE_REQUIREMENTS_STATUS",
  "missing_requirements": [],
  "reason_codes": [],
  "limitations": [],
  "boundary_statement": "This result does not authorize, approve, reject, deploy, certify, or establish the real-world claim."
}
```

Response 不反射完整 evidence values，不包含凭据，不触发后续工具，不创建 deployment 或 authorization status。

## 5. Agent Usage Rules

Agent SHOULD call the future local prototype when：

- evidence adequacy needs evaluation for a defined claim；
- an accountability claim must be checked against one fixed local profile；
- missing evidence fields or relationships must be identified；
- the result will remain bounded decision support。

Agent SHOULD NOT call it when：

- runtime blocking or safety enforcement is required；
- an authorization decision is required；
- security monitoring or malware detection is required；
- a legal or compliance conclusion is required；
- deployment approval or automatic rejection is required；
- arbitrary remote evidence or dynamic profile execution is requested。

## 6. Human Control Boundary

SAEE output supports human review.

It does not：

- approve；
- reject；
- authorize；
- deploy；
- certify；
- contact users；
- trigger consequential external actions。

```text
Tool Invocation != Human Authorization
Evaluation Output != Deployment Approval
Profile PASS != Accountability Claim Established
```

人类或获授权治理系统保留证据真实性判断、风险解释、策略决定、法律判断和部署权限。

## 7. Security Analysis

| Risk | Required mitigation before implementation |
|---|---|
| Malformed evidence | closed JSON parsing；duplicate-key rejection；existing evidence shape validation；stable error code |
| Oversized input | byte limit before JSON parsing；nested structure limits；fail closed without partial evaluation |
| Prompt injection inside evidence | treat all strings as inert data；never concatenate into prompts or execute instructions |
| False interpretation | mandatory limitations and boundary statement；do not emit SAFE/APPROVED/COMPLIANT labels |
| Unauthorized automation | no side-effect callbacks；no automatic tool chaining；result cannot grant authority |
| Dynamic profile substitution | enum-only repository profile selector；claim/profile match check；no path or URL input |
| Data leakage | no evidence value reflection；no network；no telemetry payload；no persistence by default |
| Non-determinism | fixed evaluator and profiles；stable ordering；at least five identical-run checks |

All validation failures must return a structured FAIL/error and must not fall back to permissive behavior.

## 8. Implementation Recommendation

```text
tool_capability_recommended=true
recommended_first_implementation=local_function_tool_prototype
implementation_authorized=false
mcp_authorized=false
api_authorized=false
production_integration_authorized=false
```

推荐下一 PR：`Implement SAEE Local Tool Capability Prototype v0.1`，但必须由下一轮 Gate 审核明确批准后才可实施。

下一 PR 的最低验收条件：

1. 只包装现有 evaluator，不修改 evaluator 语义；
2. claim/profile 固定映射；
3. 1 MiB 输入上限和 nested input guards；
4. prompt-injection strings treated as data；
5. deterministic positive/negative/adversarial tests；
6. no network、subprocess、file path、dynamic import or external execution；
7. output preserves human authority boundary；
8. Manifest/Tool contract 差异被显式解决。

MCP、HTTP API 和生产集成继续延期。
