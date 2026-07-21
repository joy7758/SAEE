# SAEE Autonomy Check MCP Exposure Evidence Resolution Plan

## 0. 文档控制面

```text
report_id=SAEE_AUTONOMY_CHECK_MCP_EXPOSURE_EVIDENCE_PLAN
requested_phase_label=Phase_7.0-D3.6
document_type=MCP_EXPOSURE_EVIDENCE_RESOLUTION_PLAN_ONLY
created_date=2026-07-16
source_head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_branch=feat/canonical-capability-inventory-routing-v1
subject_cli=codex-cli_0.144.1
subject_group=GROUP_B
required_effective_tool=saee.evaluate_agent_run
```

本报告只解决 Attempt 003 暴露出的 MCP tool visibility（工具可见性）证据缺口。
它不授权新的 preflight attempt，不启动 MCP server，不执行 discovery handshake，不调用
MCP Tool，不创建 Agent session，不调用 model，也不执行 A/B 实验。

### 0.1 输入证据

| 输入 | SHA-256 |
|---|---|
| `reports/SAEE_AUTONOMY_CHECK_PREFLIGHT_SEPARATION_PLAN.md` | `820f6a947da92fe3ec4c695a97ca5943ce70d6ad708346d615fbe67abc462332` |
| `reports/SAEE_AUTONOMY_CHECK_REAL_AGENT_EXECUTION_AUTHORIZATION.md` | `d35d99f3565f9ce10d4e4be044f2c4706fddd5153fb98fd126c4350e61271872` |
| Attempt 003 `runtime-static-preflight.json` | `f978fc5f01c5f399628a95e35fa5d5bbba6b072ca5d41a0511870debbaf2b687` |
| Attempt 003 `group-a-mcp-list.json` | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |
| Attempt 003 `group-b-mcp-list.raw.txt` | `0a52ffaef8d56cf82857af6f56a1bcd171159b0e733fcbb455634ec212f62804` |
| Attempt 003 `group-b-mcp-list.json` | `3c65a17145d97fc5cb261d667141b7d544f67853ab6dcb75e067cd4db509ba2f` |
| Attempt 003 `mcp-exposure-assertions.json` | `c46d65a248672db44abed083ae68fa3ba1ec9a3d3b41df8638106f07e48cdd62` |
| Attempt 003 `cross-gate-consistency-receipt.json` | `653b57e5cb480e1c31efb0630892a7b7c7ef6d66191aa3189d83837d2d2eb468` |
| Frozen B `mcp-cli-projection.txt` | `d9fdfdc8c0a0aa2943dc1b8e1322ce4f3b915432ce1013a2d354ea73ff1c8ed3` |

### 0.2 当前冻结事实

```text
PREFLIGHT_ATTEMPT_003_STATUS=FAIL
RUNTIME_VALIDATION_STATUS=PASS
RUNTIME_STATIC_PREFLIGHT_STATUS=PASS
STRICT_EXEC_CONFIG_LIVE_PARSE_STATUS=DEFERRED_ACCEPTED_NOT_EXECUTED
MCP_EXPOSURE_VALIDATION_STATUS=FAIL
GROUP_A_ZERO_MCP_PROVEN=true
GROUP_B_ONE_SERVER_PROVEN=true
GROUP_B_ONE_TOOL_PROVEN=false
AUTHORIZATION_CONSUMED=true
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
EXPERIMENT_EXECUTED=false
```

## 1. Executive Decision

Attempt 003 的停止结论正确且必须保留。`codex mcp list --json` 的观察结果证明了
B 组配置中存在一个名为 `saee-readiness` 的 server，但该输出没有返回
`enabled_tools`，因此不能证明 Codex 最终只向 Agent 暴露
`saee.evaluate_agent_run`。

更重要的是，SAEE server 的原始 MCP `tools/list` 当前会声明两个工具：

```text
saee.evaluate_agent_run
saee.evaluate_evidence
```

因此，单独启动 server 并读取原始 `tools/list` 虽然能证明 runtime server 事实，
却会得到“两工具集合”，不能单独闭合“一工具 Agent 可见面”。

本报告推荐最小可信方法为：

```text
Codex resolved allowlist evidence
        +
raw MCP server discovery evidence
        +
documented allowlist semantics
        ↓
contract-composed effective exposure proof
```

该方法必须明确标记为 `CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE`。如果人工审查要求
“直接观测 model-visible tool surface”，则必须另开一个 Codex-native、无业务任务的
tool-surface introspection 授权；不能把 contract-composed proof 冒充 direct proof。

```text
RECOMMENDED_RESOLUTION=CONTRACT_COMPOSED_EFFECTIVE_EXPOSURE_PROOF
RAW_SERVER_TOOLS_LIST_ALONE_SUFFICIENT=false
CONFIG_PROJECTION_ALONE_SUFFICIENT=false
DIRECT_MODEL_VISIBLE_PROOF_AVAILABLE_NOW=false
MCP_EXPOSURE_VALIDATION_COMPLETE=false
```

## 2. Failure Analysis

### 2.1 已证明的事实

Attempt 003 已可信证明：

- Group A 的 configured MCP server 集合为空；
- Group B 的 configured MCP server 数量为 `1`；
- Group B server identity 为 `saee-readiness`；
- projection bytes 与冻结 hash 一致；
- runtime static gate 已通过；
- 没有启动 session、model 或 MCP Tool。

### 2.2 未证明的事实

Attempt 003 未证明：

- Codex 是否成功解析并应用 `enabled_tools`；
- Codex 的 effective Agent-facing tool count 是否为 `1`；
- 唯一 Agent-facing tool identity 是否为 `saee.evaluate_agent_run`；
- `saee.evaluate_evidence` 是否已在 Codex exposure layer 被过滤；
- live `codex exec` 启动时的实际 model-visible tool surface。

### 2.3 根因

失败不是 server 缺失，也不是 tool 缺失，而是 observation surface（观察表面）选错：

```text
codex mcp list --json
        ↓
configured server inventory
        ≠
resolved enabled_tools projection
        ≠
raw server tools/list
        ≠
effective Agent-visible tool surface
```

Attempt 003 把 configured server inventory 当成了能够输出 tool projection 的接口。
实际输出省略 `enabled_tools`，所以 tool count 与 tool identity 必须保持 `UNPROVEN`。

### 2.4 为什么 server 存在不等于 tool 已证明

MCP server identity 只回答“Codex 配置指向哪个进程”。它不回答：

1. 该进程运行时声明哪些 tools；
2. Codex 是否应用 allowlist/denylist；
3. 过滤后 Agent 最终看到哪些 tools；
4. live session 是否加载了与 preflight 相同的配置。

所以：

```text
ONE_SERVER_PROVEN=true
```

不能推出：

```text
ONE_TOOL_PROVEN=true
```

## 3. Evidence Layers

### 3.1 分层地图

| Layer | 回答的问题 | 当前证据 | 当前结论 | 单独是否足够 |
|---|---|---|---|---|
| L0 Canonical capability fact | SAEE server 拥有哪些规范 operations？ | `capability-package/manifest.json` | 两个规范工具 | 否 |
| L1 Config projection intent | 实验希望 Codex 允许哪个工具？ | `mcp-cli-projection.txt` | allowlist 意图为一个工具 | 否 |
| L2 Codex configured server inventory | Codex 配置看到几个 server？ | `codex mcp list --json` | A=0，B=1 | 否 |
| L3 Codex resolved exposure contract | Codex 实际解析出的 `enabled_tools` 是什么？ | 尚无 | 未证明 | 与 L4/语义组合后可形成 contract proof |
| L4 Raw server discovery | server 启动后原始 `tools/list` 返回什么？ | 代码与 smoke 表明两个；本批次未 live discovery | live 未证明 | 否 |
| L5 Effective Agent-visible surface | allowlist 过滤后 Agent 实际看到什么？ | 尚无直接 observation | 未证明 | 是，最高强度 |
| L6 Tool invocation | Agent 是否调用以及调用了什么？ | 未执行实验 | 不适用 | 不是 preflight 可见性证明的替代品 |

### 3.2 Config projection

冻结 projection 声明：

```text
mcp_servers.saee-readiness.enabled_tools=["saee.evaluate_agent_run"]
```

OpenAI Codex 配置参考把 `enabled_tools` 定义为 MCP server 暴露工具的 allow list，
而 `disabled_tools` 是在其后应用的 deny list：
[OpenAI Codex Configuration Reference](https://developers.openai.com/codex/config-reference/)。

但 projection file 只能证明实验输入意图。只有当 Codex resolved configuration 重新输出
并确认 exact value 后，才能证明 CLI 对该字段完成了解析绑定。

### 3.3 Server discovery

仓库当前实现和 smoke contract 一致表明，原始 SAEE server `tools/list` 是：

```text
RAW_SERVER_TOOL_SET={
  saee.evaluate_agent_run,
  saee.evaluate_evidence
}
```

未来 live discovery 应使用标准 MCP 只读序列：

```text
initialize
↓
notifications/initialized
↓
tools/list
↓
process termination and receipt
```

这会启动本地 MCP server 并发送 protocol discovery message，但不得发送 `tools/call`。
证据术语必须区分：

```text
MCP_SERVER_DISCOVERY_INVOKED=true
MCP_TOOL_INVOKED=false
```

### 3.4 Effective Agent-visible surface

若 Codex resolved allowlist 为：

```text
RESOLVED_ENABLED_TOOLS={saee.evaluate_agent_run}
```

且 raw server tool set 为上述两项，则按照 allowlist contract，预期有效集合为：

```text
EXPECTED_EFFECTIVE_TOOL_SET=
RAW_SERVER_TOOL_SET ∩ RESOLVED_ENABLED_TOOLS
=
{saee.evaluate_agent_run}
```

这是 contract-composed proof。它比配置文件自述强，也比 raw `tools/list` 单独证据强，
但仍不是 live model-visible list 的直接观测。

## 4. Recommended Resolution

### 4.1 最小可信方法

建议下一次仅证据批次按以下顺序执行：

#### Step E1 — Immutable input recheck

重新绑定：

- consumed Attempt 003 receipt；
- B projection exact bytes/hash；
- CLI path/version/hash；
- MCP entrypoint hash；
- capability manifest hash；
- isolated CODEX_HOME 与新 evidence root。

任何漂移立即停止，不得在原授权内修复。

#### Step E2 — Codex resolved configuration inspection

在新的隔离 CODEX_HOME 中，使用单独批准的只读配置检查：

```text
codex mcp get saee-readiness --json
```

预期必须可观察并精确满足：

```text
server_id=saee-readiness
server_count=1
enabled_tools=["saee.evaluate_agent_run"]
disabled_tools=[] OR ABSENT
command=python3
args=["/Users/zhangbin/Documents/SAEE/scripts/saee_agent_readiness_mcp_stdio.py"]
```

这里的命令只是候选 inspection surface，不预先宣称当前 CLI 一定会输出
`enabled_tools`。如果输出仍然省略该字段：

```text
RESOLVED_ALLOWLIST_STATUS=UNPROVEN
STOP=true
```

不得从输入 projection 反推 CLI 已成功解析。

#### Step E3 — Raw MCP discovery

在新的隔离 discovery process 中启动冻结 entrypoint，只执行 MCP initialize 与
`tools/list`，验证：

```text
raw_tool_count=2
raw_tool_ids=[
  "saee.evaluate_agent_run",
  "saee.evaluate_evidence"
]
target_tool_present=true
tools_call_sent=false
```

若 server 返回集合与规范事实不一致，立即停止。不得修改 server、schema 或 projection。

#### Step E4 — Contract composition receipt

只有 E2 与 E3 都通过，才生成：

```text
proof_class=CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE
resolved_allowlist_count=1
raw_server_tool_count=2
expected_effective_tool_count=1
expected_effective_tool=saee.evaluate_agent_run
```

是否允许据此把 preflight gate 记为
`GROUP_B_ONE_TOOL_PROVEN=true`，必须由 Human Authority Owner 在新授权中明确接受
`proof_class=CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE`。没有这项接受，状态保持 false。

### 4.2 为什么不只选择原始 `tools/list`

原始 `tools/list` 预计会返回两个工具。它证明 server runtime truth，却不观察 Codex 的
allowlist filtering，所以不能回答 B 组 Agent-facing surface 是否为一个工具。

```text
RAW_DISCOVERY_ONLY=REJECTED_AS_SUFFICIENT
```

### 4.3 为什么不只读取 projection

projection 能证明 intent，但不能证明：

- CLI 接受了字段；
- 字段未被其他层覆盖；
- server 确实拥有目标 tool；
- runtime filter 与文档 contract 一致应用。

```text
PROJECTION_ONLY=REJECTED_AS_SUFFICIENT
```

### 4.4 Direct proof escalation

如果实验审查坚持 L5 direct observation，则应先单独设计一个 Codex-native
tool-surface introspection probe。候选命令必须先证明它输出的是 model-visible tool list，
而不是 Prompt 文本或 config inventory。

在没有这种无模型接口时，只剩两种合规选择：

1. 人工接受 `CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE` 作为 preflight 标准；
2. 另行授权一次 discovery-only Codex session/model invocation，并确保它不复用或污染
   A/B subject sessions。

第二种选择会扩大成本、数据和 session scope，当前不授权，也不是本报告默认建议。

## 5. Authorization Requirement

Attempt 003 authorization 已 consumed，不能复用。任何 E1-E4 执行都需要新的 one-use
human authorization，至少绑定：

```text
new_authorization_id=<required>
human_authority_owner_id=human-owner-001
authorization_one_use=true
resolved_config_inspection_allowed=true
local_mcp_server_discovery_allowed=true
mcp_tools_call_allowed=false
agent_session_creation_allowed=false
model_invocation_allowed=false
experiment_execution_allowed=false
```

还必须绑定：

- 新 isolated `CODEX_HOME`；
- 新 preflight evidence root；
- projection、CLI、entrypoint、manifest 的 exact SHA-256；
- allowed commands 与 exact arguments；
- discovery process timeout；
- process cleanup owner；
- stdout/stderr/canonical receipt 的保存位置；
- `CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE` 是否被接受为 gate proof；
- 失败后禁止 retry、fallback、command substitution 和原地修复。

### 5.1 术语修正

下一批必须分开记录：

```text
MCP_CONFIG_INSPECTION_EXECUTED=true/false
MCP_SERVER_DISCOVERY_INVOKED=true/false
MCP_TOOL_INVOKED=true/false
MODEL_INVOKED=true/false
SESSION_CREATED=true/false
```

不得再用单一 `MCP_INVOKED` 同时表达 discovery 与 `tools/call`。

## 6. Stop Conditions

以下任一条件成立都必须立即 fail-closed：

1. 新授权缺失、过期、已 consumed 或 identity 不匹配；
2. frozen projection、CLI、entrypoint 或 manifest hash 漂移；
3. `codex mcp get --json` 不输出 `enabled_tools`；
4. resolved allowlist 不是 exact singleton `saee.evaluate_agent_run`；
5. 出现第二个 configured server；
6. 出现 `disabled_tools` 冲突或未知 override；
7. raw server discovery 不返回规范两工具集合；
8. discovery 过程尝试 `tools/call`；
9. 需要 model/session 才能继续但没有单独授权；
10. 无法保持新 evidence root 与历史 attempt artifacts 隔离；
11. 需要修改 MCP implementation、Capability、Schema、Runtime 或 Evaluation；
12. 任何人试图把 contract proof 记录为 direct model-visible proof。

失败时输出必须保留：

```text
MCP_EXPOSURE_VALIDATION_COMPLETE=false
GROUP_B_ONE_TOOL_PROVEN=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_TOOL_INVOKED=false
EXPERIMENT_EXECUTED=false
```

## 7. Experiment Boundary

本报告及其建议的下一 preflight 批次都不进入 Agent session。允许的未来动作仅限：

- Codex resolved MCP configuration inspection；
- 本地 MCP server initialize 与 `tools/list` discovery；
- canonical evidence receipt 生成；
- fail-closed evaluation。

明确禁止：

- 创建 Session A 或 Session B；
- 调用 OpenAI provider/model；
- 发送业务 Prompt 或 Trigger；
- 调用 `saee.evaluate_agent_run` 或 `saee.evaluate_evidence`；
- 修改 fixture 或 A/B conditions；
- 修改 SAEE MCP server、Capability、Schema、Runtime 或 Evaluation；
- 启动商业验证结论。

```text
EXPERIMENT_BOUNDARY=PREFLIGHT_EVIDENCE_ONLY
SESSION_TRANSITION_ALLOWED=false
```

## 8. First-Principles Review

### 8.1 为什么工具可见性比配置更重要？

Agent 的行为由它实际可见、可理解、可调用的 tool surface 决定，而不是由操作者希望
暴露什么决定。若配置写了一项但 Agent 看见两项，实验变量已经改变；若配置写了一项但
Agent看不见任何工具，B 组也没有获得预期 exposure。因果判断必须绑定可见事实。

### 8.2 为什么不能假设 MCP projection 等于实际暴露？

projection 还要经过 CLI 解析、配置合并、allowlist/denylist、server discovery、runtime
registration 和 model-facing serialization。任何一层都可能省略、覆盖或拒绝字段。
Attempt 003 已经实际证明 configured server listing 不会自动给出 tool projection。

### 8.3 为什么失败证据比假成功更有价值？

假成功会让后续行为变化被错误归因给 SAEE；失败证据则准确指出缺少哪个 observation
surface，并阻止实验在不可解释条件下消耗授权。对商业验证而言，“当前无法证明”是可行动
信息，而“按意图推测成功”会污染产品判断。

## 9. Product and Mainline Boundary

本阶段只修复实验基础设施证据，不创建新的 SAEE 产品能力。不得把本次发现扩展为新的
runtime assurance、MCP certification 或 enterprise governance 产品线。

按仓库 `AGENTS.md`，当前 Constitutional Program Mainline 是 SAEE 与 Agent Evidence
Project 的受控合并。本 Autonomy Check 实验属于次级 dogfooding/commercial observation
lane，不能取代该主线：

```text
MAINLINE_DRIFT_DETECTED=true
DRIFT_CLASS=SECONDARY_EXPERIMENT_LANE_NOT_CONSTITUTIONAL_MAINLINE
DRIFT_CORRECTION=TIMEBOX_EVIDENCE_RESOLUTION_AND_DO_NOT_EXPAND_PRODUCT_SCOPE
```

该标记不阻塞本次 plan-only 报告，但阻止继续增加治理层、协议层或新 capability。

## 10. Recommendation

下一步只建议人工审查并决定是否授权一个新的、one-use 的 MCP exposure evidence batch。
推荐接受的执行范围是 E1-E4；推荐的证据强度标记是：

```text
RECOMMENDED_PROOF_CLASS=CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE
```

若人工不能接受该 proof class，则不要启动 A/B session；先另行设计并授权 L5 direct
tool-surface introspection。无论选择哪条路线，Attempt 003 都保持 consumed/failed，不能覆盖。

## 11. Final Status

```text
MCP_EXPOSURE_EVIDENCE_PLAN_STATUS=COMPLETE
MCP_EXPOSURE_VALIDATION_COMPLETE=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
EXPERIMENT_EXECUTED=false
CODE_CHANGED=false
MCP_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_MCP_EXPOSURE_EVIDENCE_PLAN
```
