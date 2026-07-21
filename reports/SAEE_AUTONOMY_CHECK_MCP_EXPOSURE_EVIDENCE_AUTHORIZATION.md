# SAEE Autonomy Check MCP Exposure Evidence Collection Authorization

## 0. 文档控制面

```text
report_id=SAEE_AUTONOMY_CHECK_MCP_EXPOSURE_EVIDENCE_AUTHORIZATION
requested_phase_label=Phase_7.0-D3.7
document_type=EVIDENCE_COLLECTION_AUTHORIZATION_DESIGN_ONLY
created_date=2026-07-16
source_head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_branch=feat/canonical-capability-inventory-routing-v1
subject_group=GROUP_B
required_effective_tool=saee.evaluate_agent_run
```

本报告依据：

| 输入 | SHA-256 |
|---|---|
| `reports/SAEE_AUTONOMY_CHECK_MCP_EXPOSURE_EVIDENCE_PLAN.md` | `0009737f1af65aa6fad9d4150da963f711661b6948865b45ac0c7971663676cb` |

本文件只设计未来 MCP exposure evidence collection（MCP 暴露证据采集）的授权边界。
它不是 human grant，不创建 authorization instance，不采集证据，不启动 MCP server，
不创建 Agent session，不调用 model 或 SAEE Tool，也不执行 A/B 实验。

```text
AUTHORIZATION_DESIGN_ONLY=true
EVIDENCE_COLLECTION_EXECUTION_AUTHORIZED=false
HUMAN_EXECUTION_GRANT_REQUIRED=true
ATTEMPT_003_AUTHORIZATION_REUSABLE=false
```

## 1. Executive Decision

MVP 推荐选择方案 A：`Contract Composed Evidence`（契约组合证据）。

```text
RECOMMENDED_MVP_OPTION=OPTION_A_CONTRACT_COMPOSED_EVIDENCE
RECOMMENDED_PROOF_CLASS=CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE
DIRECT_MODEL_VISIBLE_INTROSPECTION_REQUIRED_FOR_MVP=false
DIRECT_MODEL_VISIBLE_INTROSPECTION_STATUS=DEFERRED
```

方案 A 必须由三个独立证据面组成：

```text
Codex resolved enabled_tools allowlist
        +
raw MCP server discovery
        +
documented enabled_tools contract semantics
        ↓
expected effective one-tool exposure
```

它足以支持一次受控 MVP preflight，前提是 Human Authority Owner 明确接受其证据等级。
它不能被描述为 Agent/model 直接可见证据，也不能用于认证、生产或权限保证主张。

方案 B：`Direct Model-visible Introspection`（模型直接可见工具面检查）作为升级路径保留，
但本阶段不推荐。只有方案 A 无法闭合、实验结论依赖直接可见性，或未来 consequential
claim 明确要求更高证据等级时，才应单独设计和授权方案 B。

## 2. Evidence Strategy Selection

### 2.1 Option A — Contract Composed Evidence

#### 定义

方案 A 不把任一单层证据当成完整事实，而是组合：

1. Codex resolved configuration 确认 `enabled_tools` 被解析为 exact singleton；
2. 本地 MCP discovery 确认 server 实际提供规范的两个工具且目标工具存在；
3. allowlist contract 定义过滤关系；
4. canonical receipt 计算预期 effective tool set。

预期集合：

```text
RAW_SERVER_TOOL_SET={
  saee.evaluate_agent_run,
  saee.evaluate_evidence
}

RESOLVED_ENABLED_TOOLS={
  saee.evaluate_agent_run
}

EXPECTED_EFFECTIVE_TOOL_SET=
RAW_SERVER_TOOL_SET ∩ RESOLVED_ENABLED_TOOLS
=
{saee.evaluate_agent_run}
```

#### 优点

- 不创建 Agent session；
- 不调用 model/provider；
- 不发送实验 Prompt、Trigger 或 fixture；
- 不调用任何 SAEE business Tool；
- 可以分别审计配置解析与 server runtime truth；
- 成本、数据暴露和实验污染风险最低；
- 若失败，可以准确定位到 config、server 或 composition layer。

#### 限制

- 不直接读取 model-visible tool list；
- 依赖 Codex 对 `enabled_tools` 的 contract semantics；
- 不能证明未来 session startup 没有发生额外漂移；
- 不能证明 model 实际理解、选择或调用该工具；
- 只能支持 MVP preflight，不支持 production isolation guarantee。

### 2.2 Option B — Direct Model-visible Introspection

#### 定义

方案 B 要求 Codex-native surface 直接输出准备交付给 model/Agent 的最终工具集合，而不是：

- 原始配置文件；
- configured server inventory；
- raw MCP `tools/list`；
- 由操作者推导的 expected set。

#### 优点

- 最接近 Agent 实际决策输入；
- 可直接证明 final tool count 与 identity；
- 减少对配置合并和过滤实现的间接推理。

#### 风险与成本

- 当前尚未证明存在可靠的无模型 Codex introspection surface；
- 若必须启动 session/model，会扩大授权、费用和数据处理边界；
- discovery session 可能污染或预热 A/B subject environment；
- 需要额外的 runtime binding、session isolation 和 evidence schema；
- 容易把“验证工具面”扩展成新的基础设施开发任务；
- 可能延迟 MVP 的核心行为实验，却不增加第一轮商业假设的必要信息。

### 2.3 比较结论

| 维度 | 方案 A：Contract composed | 方案 B：Direct model-visible |
|---|---|---|
| Config intent | 直接绑定 | 可能隐含 |
| Raw server truth | 直接 discovery | 可能由 runtime 隐含 |
| Effective tool set | 契约组合推导 | 直接观察目标 |
| Model invocation | 不需要 | 可能需要 |
| Agent session | 不需要 | 可能需要 |
| 实验污染风险 | 低 | 中至高 |
| 授权复杂度 | 低至中 | 高 |
| MVP 适配度 | 推荐 | 暂缓 |
| Production guarantee | 不足 | 仍需额外运行时控制证据 |

```text
OPTION_A_SELECTED_FOR_MVP=true
OPTION_B_SELECTED_FOR_MVP=false
OPTION_B_DEFER_REASON=HIGHER_SCOPE_NOT_REQUIRED_FOR_FIRST_BEHAVIOR_EXPERIMENT
```

## 3. Recommended MVP Choice

### 3.1 选择原则

当前实验只需证明：A/B 环境的预期 MCP exposure 已达到可审计、可重复且足以开始
行为观察的最低证据标准。它不需要证明 Codex 所有内部序列化细节，也不支持外部保证。

因此方案 A 被选为：

```text
MVP_PREFLIGHT_EVIDENCE_STANDARD=SUFFICIENT_IF_EXPLICITLY_ACCEPTED_BY_HUMAN_OWNER
```

Human Authority Owner 必须在未来 one-use grant 中明确接受：

```text
ACCEPT_PROOF_CLASS_CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE=true
```

缺少该字段时，不能把组合 receipt 提升为 `GROUP_B_ONE_TOOL_PROVEN=true`。

### 3.2 不允许的语义升级

即使方案 A 全部通过，也只能输出：

```text
MCP_EXPOSURE_PROOF_CLASS=CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE
EXPECTED_EFFECTIVE_TOOL_COUNT=1
EXPECTED_EFFECTIVE_TOOL=saee.evaluate_agent_run
MVP_PREFLIGHT_MCP_BOUNDARY_ACCEPTED=true
```

不得输出：

```text
MODEL_VISIBLE_TOOL_COUNT_DIRECTLY_OBSERVED=1
AGENT_CAN_ONLY_SEE_SAEE_EVALUATE_AGENT_RUN=true
RUNTIME_ISOLATION_GUARANTEED=true
PRODUCTION_MCP_BOUNDARY_PROVEN=true
SECURITY_CERTIFIED=true
```

### 3.3 升级到方案 B 的条件

只有以下任一条件成立，才建议重新评估方案 B：

1. Codex resolved configuration 无法输出或证明 `enabled_tools`；
2. raw discovery 与 canonical capability facts 不一致；
3. Human Authority Owner 不接受 contract-composed proof；
4. A/B session startup 发现与组合证据冲突的工具面；
5. 后续外部主张要求 direct model-visible evidence；
6. 可用的无模型 introspection 已被独立证明不会创建 session 或调用 provider。

方案 B 不得作为方案 A 失败后的自动 fallback；必须重新设计、重新授权。

## 4. Evidence Confidence Level

### 4.1 等级定义

| Level | 名称 | 证据构成 | 可支持的结论 |
|---|---|---|---|
| E0 | Intent only | projection file | 只证明配置意图 |
| E1 | Server configured | configured server inventory | 只证明 server 注册 |
| E2 | Runtime discovered | raw initialize + `tools/list` | 证明 server 原始工具集合 |
| E3 | Contract composed | resolved allowlist + raw discovery + contract | 证明预期 effective exposure |
| E4 | Direct Agent-visible | Codex-native final tool-surface observation | 证明最终输入工具集合 |
| E5 | Session behavior | frozen session events and invocation receipt | 证明 Agent 实际发现/调用行为 |

### 4.2 当前与目标等级

当前 Attempt 003：

```text
CURRENT_CONFIG_CONFIDENCE=E1_SERVER_CONFIGURED
CURRENT_GROUP_A_CONFIDENCE=E1_ZERO_SERVER_CONFIG_PROVEN
CURRENT_GROUP_B_ONE_TOOL_CONFIDENCE=UNPROVEN
```

下一 evidence collection batch 的目标：

```text
TARGET_CONFIDENCE=E3_CONTRACT_COMPOSED
E4_DIRECT_AGENT_VISIBLE_TARGETED=false
E5_SESSION_BEHAVIOR_TARGETED=false
```

### 4.3 MVP 可接受性

```text
E3_SUITABLE_FOR_CONTROLLED_MVP_PREFLIGHT=true
E3_SUITABLE_FOR_PRODUCTION_GUARANTEE=false
E3_SUITABLE_FOR_SECURITY_OR_AUTHORIZATION_CLAIM=false
E3_REQUIRES_HUMAN_ACCEPTANCE=true
```

该等级判断是实验 gate recommendation，不是 SAEE 对外授权或认证。

## 5. Authorization Scope

### 5.1 当前报告不授予执行权

```text
MCP_EVIDENCE_COLLECTION_GRANT_CREATED=false
MCP_EVIDENCE_COLLECTION_EXECUTION_AUTHORIZED=false
NEW_AUTHORIZATION_ID=UNASSIGNED
```

未来采集必须创建新的 one-use human authorization。Attempt 003 已 consumed，不可复用、
续期或原地修改。

### 5.2 建议允许的未来动作

未来授权 allowlist 只能包含：

1. 校验冻结输入、hash、CLI identity 与 isolation location；
2. 在新 isolated `CODEX_HOME` 中执行只读 resolved MCP config inspection；
3. 在新本地进程中执行 MCP `initialize`；
4. 发送 `notifications/initialized`；
5. 执行一次 MCP `tools/list`；
6. 终止该本地 server process；
7. 生成 canonical evidence receipts 与 deterministic hashes；
8. 对 E1-E3 predicate 做 fail-closed evaluation。

### 5.3 建议禁止的未来动作

未来授权必须显式禁止：

- `tools/call`；
- 调用 `saee.evaluate_agent_run`；
- 调用 `saee.evaluate_evidence`；
- 创建 Session A、Session B 或 discovery Agent session；
- 调用 OpenAI provider/model；
- 发送 fixture、task Prompt 或 Trigger；
- 修改 MCP implementation、Capability、Schema、Runtime 或 Evaluation；
- 修改 frozen projection 以适配结果；
- retry、fallback、command substitution 或自动切换方案 B；
- git add、commit、push、branch 或 worktree；
- 进入行为分析或商业结论。

### 5.4 必须绑定的动态事实

未来 authorization instance 至少必须绑定：

```text
authorization_id=<new-human-assigned-id>
human_authority_owner_id=human-owner-001
authorization_one_use=true
expires_at=<required>
codex_home=<new-isolated-path>
evidence_root=<new-isolated-path>
cli_path=/opt/homebrew/bin/codex
cli_version=codex-cli_0.144.1
projection_sha256=d9fdfdc8c0a0aa2943dc1b8e1322ce4f3b915432ce1013a2d354ea73ff1c8ed3
resolved_config_command=<exact-command-and-arguments>
mcp_entrypoint=<exact-path-and-sha256>
discovery_timeout_seconds=<bounded-value>
cleanup_owner=<required>
accept_proof_class_contract_composed_not_direct_model_visible=true
```

CLI、entrypoint、manifest 和 authorization input 的 hash 必须在实际采集前重新计算并写入
preimage receipt；本计划不提前冻结可能漂移的 hash 值。

### 5.5 必须区分的状态

未来证据不得继续用一个 `MCP_INVOKED` 混合表达不同动作。必须分别记录：

```text
MCP_CONFIG_INSPECTION_EXECUTED=true/false
MCP_SERVER_DISCOVERY_INVOKED=true/false
MCP_TOOL_INVOKED=true/false
AGENT_SESSION_CREATED=true/false
MODEL_INVOKED=true/false
```

执行 `initialize`/`tools/list` 后：

```text
MCP_SERVER_DISCOVERY_INVOKED=true
MCP_TOOL_INVOKED=false
```

当前计划阶段全部仍为 false。

## 6. Expected Evidence Artifacts

未来授权若获批准，建议只生成以下 append-only evidence：

| Artifact | 目的 |
|---|---|
| `authorization-receipt.json` | 绑定 one-use grant、owner、expiry 与 scope |
| `preimage-receipt.json` | 绑定 CLI、projection、entrypoint、manifest 与 location hashes |
| `resolved-mcp-config.raw.json` | 保存 Codex config inspection 原始输出 |
| `resolved-mcp-config.canonical.json` | 保存规范化 resolved allowlist |
| `mcp-initialize-response.json` | 证明本地 server protocol initialization |
| `mcp-tools-list.raw.json` | 保存 server 原始 tools/list |
| `mcp-tools-list.canonical.json` | 规范化原始工具集合 |
| `effective-exposure-composition.json` | 记录集合组合与 proof class |
| `evidence-collection-status.json` | 记录 PASS/FAIL 与 stop reason |
| `cleanup-receipt.json` | 证明 discovery process 已终止 |

所有 JSON 必须采用 UTF-8、recursive lexicographic key ordering、stable final newline，
并进行三次 deterministic SHA-256 重算。原始输出不得被规范化文件覆盖。

## 7. Stop Conditions

以下任一项成立都必须停止，并保持
`MCP_EXPOSURE_VALIDATION_COMPLETE=false`：

1. 新 human authorization 缺失、过期、identity 不符或已 consumed；
2. Attempt 003 被尝试复用；
3. frozen projection hash 漂移；
4. CLI、entrypoint、manifest 或 location binding 漂移；
5. resolved config inspection 不输出 `enabled_tools`；
6. resolved `enabled_tools` 不是 exact singleton `saee.evaluate_agent_run`；
7. 出现额外 MCP server、override 或 denylist conflict；
8. raw server discovery 不返回规范两工具集合；
9. raw server 缺少 `saee.evaluate_agent_run`；
10. 任何步骤尝试发送 `tools/call`；
11. 任何步骤创建 Agent session 或调用 model/provider；
12. 需要修改 MCP implementation、Capability、Schema、Runtime 或 Evaluation；
13. 无法终止 discovery process 或证明 cleanup；
14. canonical serialization/hash 不稳定；
15. 有人试图把 E3 receipt 标记为 E4 direct observation；
16. 需要自动 fallback 到方案 B。

失败结果必须保留，不能覆盖或删除：

```text
EVIDENCE_COLLECTION_STATUS=FAIL
MCP_EXPOSURE_VALIDATION_COMPLETE=false
GROUP_B_ONE_TOOL_PROVEN=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_TOOL_INVOKED=false
EXPERIMENT_EXECUTED=false
```

## 8. No Experiment Boundary

本阶段与未来方案 A evidence collection 都是 preflight evidence lane，不是 Agent 实验。

```text
NO_EXPERIMENT_BOUNDARY=true
SESSION_A_CREATION_ALLOWED=false
SESSION_B_CREATION_ALLOWED=false
MODEL_INVOCATION_ALLOWED=false
FIXTURE_TRANSMISSION_ALLOWED=false
TASK_PROMPT_DELIVERY_ALLOWED=false
TRIGGER_DELIVERY_ALLOWED=false
SAEE_TOOL_CALL_ALLOWED=false
BEHAVIOR_ANALYSIS_ALLOWED=false
COMMERCIAL_VALIDATION_ALLOWED=false
```

即使方案 A 采集通过，也只能回到 Human Session Authorization gate。它不能自动创建
Session A/B，不能自动消费此前的 real-agent authorization，也不能提前判断实验成功。

继续冻结：

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
```

## 9. First-Principles Review

### 9.1 为什么配置不是事实？

配置是操作者表达的期望。它还要经过解析、合并、过滤、server discovery、runtime
registration 与 model-facing serialization。只有在相应观察层取得 evidence，才能说明
该期望已成为某一层的事实。把 intent 写入文件不会自动证明 runtime behavior。

### 9.2 为什么工具可见性必须单独证明？

Agent 根据实际可见工具做选择。server 数量、server 原始工具集合和最终 Agent-facing
工具集合是三个不同对象。若 B 组实际看到多余工具，行为变化就无法唯一归因于冻结的
SAEE exposure；若目标工具不可见，B 组也没有获得实验处理变量。

### 9.3 为什么 MVP 不应该过早追求完全模型可见？

第一轮 MVP 的商业问题是 SAEE exposure 是否改变 Agent 行为，而不是证明 Codex 内部
所有工具序列化细节。E3 契约组合证据能以更小权限、更低成本和更少污染闭合受控 preflight。
在 E3 尚未尝试前直接扩大到 model/session，会增加混杂变量，却不一定提高第一轮决策价值。

这不意味着忽略 direct visibility；它只是把 E4 放到 E3 失败或更高主张确实需要时执行。

## 10. Product and Mainline Boundary

本报告不注册 `Agent Capability Drift`，不创建 runtime assurance capability，不扩展 MCP
协议，也不形成新的 enterprise product claim。该观察只作为实验工程发现保留。

仓库 `AGENTS.md` 规定的 Constitutional Program Mainline 仍是 SAEE 与 Agent Evidence
Project 的受控合并。Autonomy Check 是次级实验路线：

```text
MAINLINE_DRIFT_DETECTED=true
DRIFT_CLASS=SECONDARY_EXPERIMENT_LANE_NOT_CONSTITUTIONAL_MAINLINE
DRIFT_CORRECTION=COMPLETE_MINIMUM_EVIDENCE_GATE_WITHOUT_PRODUCT_EXPANSION
```

本次 plan-only 报告可继续，但任何 capability、protocol、governance 或 product expansion
必须停止并回到主线审查。

## 11. Recommendation

人工审查应只决定两件事：

1. 是否接受方案 A 的 `CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE` 证据等级用于 MVP；
2. 是否允许下一阶段创建一个新的、one-use、只读/只发现的 evidence collection grant。

推荐决定：

```text
RECOMMEND_OPTION_A_FOR_MVP=true
RECOMMEND_OPTION_B_NOW=false
RECOMMEND_NEW_ONE_USE_COLLECTION_AUTHORIZATION=true
AUTO_TRANSITION_TO_EVIDENCE_COLLECTION=false
AUTO_TRANSITION_TO_AGENT_SESSION=false
```

## 12. Final Status

```text
MCP_EXPOSURE_EVIDENCE_AUTHORIZATION_STATUS=COMPLETE
MCP_EXPOSURE_VALIDATION_COMPLETE=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
EXPERIMENT_EXECUTED=false
CODE_CHANGED=false
MCP_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_MCP_EXPOSURE_EVIDENCE_AUTHORIZATION
```
