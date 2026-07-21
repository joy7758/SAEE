# SAEE Autonomy Check MCP Exposure Evidence Collection Plan

## 0. 文档控制面

```text
report_id=SAEE_AUTONOMY_CHECK_MCP_EXPOSURE_EVIDENCE_COLLECTION_PLAN
requested_phase_label=Phase_7.0-D3.8
document_type=E3_EVIDENCE_COLLECTION_EXECUTION_PREPARATION_ONLY
created_date=2026-07-16
source_head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_branch=feat/canonical-capability-inventory-routing-v1
selected_evidence_level=E3_CONTRACT_COMPOSED
selected_proof_class=CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE
subject_group=GROUP_B
required_effective_tool=saee.evaluate_agent_run
```

本报告依据：

| 输入 | SHA-256 |
|---|---|
| `reports/SAEE_AUTONOMY_CHECK_MCP_EXPOSURE_EVIDENCE_AUTHORIZATION.md` | `d1f0ca53ad1907b7161b0c5b54c1e2e8cabdd25d89d6a690fa03d977905927df` |
| `reports/SAEE_AUTONOMY_CHECK_MCP_EXPOSURE_EVIDENCE_PLAN.md` | `0009737f1af65aa6fad9d4150da963f711661b6948865b45ac0c7971663676cb` |

本文件只准备未来 E3 evidence collection 的原子顺序、输入来源、比较规则、receipt
结构和停止条件。它不创建 authorization instance，不执行 resolved config inspection，
不启动本地 MCP server，不发送 MCP message，不创建 Agent session，不调用 model 或 SAEE
Tool，也不执行实验。

```text
COLLECTION_PLAN_ONLY=true
MCP_EXPOSURE_COLLECTION_EXECUTION_AUTHORIZED=false
HUMAN_COLLECTION_GRANT_REQUIRED=true
ATTEMPT_003_AUTHORIZATION_REUSABLE=false
```

## 1. Executive Decision

未来 E3 evidence collection 必须按以下固定顺序执行：

```text
Human one-use collection grant
        ↓
P0 Immutable input and location preimage
        ↓
P1 Codex resolved config inspection
        ↓
P2 Local MCP initialize + tools/list discovery
        ↓
P3 Canonical allowlist/server-set comparison
        ↓
P4 E3 composition receipt
        ↓
P5 Process cleanup and final gate receipt
        ↓
Human review before any Agent session
```

P1 与 P2 是独立 observation layers，必须保留各自 raw evidence。只有两者都通过且
Human Authority Owner 已接受 `CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE`，P3/P4
才可生成 E3 PASS。任一阶段失败都停止，不得 retry、修改输入或升级到 E4。

```text
RECOMMENDED_COLLECTION_SEQUENCE=P0_P1_P2_P3_P4_P5
CONFIG_AND_DISCOVERY_EVIDENCE_MUST_REMAIN_SEPARATE=true
AUTO_FALLBACK_TO_E4=false
AUTO_TRANSITION_TO_SESSION=false
```

## 2. E3 Evidence Definition

### 2.1 E3 回答的问题

E3 只回答：

> 在冻结的 Codex MCP allowlist contract 与冻结的 SAEE server runtime tool set 下，
> 预期提供给 B 组 Agent 的 effective MCP tool set 是否为
> `{saee.evaluate_agent_run}`？

E3 不回答：

- model 是否直接看到了该工具；
- Agent 是否理解或选择了该工具；
- Agent 是否调用了该工具；
- session startup 是否完全无漂移；
- SAEE 是否授权 Agent 行动；
- 该边界是否达到 production/security guarantee。

### 2.2 三个构成证据

E3 由三个不可互相替代的事实面组成：

```text
E3-C1=CODEX_RESOLVED_ALLOWLIST
E3-C2=RAW_MCP_SERVER_DISCOVERY
E3-C3=ALLOWLIST_COMPOSITION_CONTRACT
```

通过谓词：

```text
E3_PASS =
  E3_C1_PASS
  AND E3_C2_PASS
  AND E3_C3_PASS
  AND PROOF_CLASS_HUMAN_ACCEPTED
  AND CLEANUP_PASS
  AND NO_FORBIDDEN_ACTION
```

### 2.3 集合模型

预期输入：

```text
RESOLVED_ENABLED_TOOLS={saee.evaluate_agent_run}

RAW_SERVER_TOOL_SET={
  saee.evaluate_agent_run,
  saee.evaluate_evidence
}
```

组合：

```text
EXPECTED_EFFECTIVE_TOOL_SET=
RAW_SERVER_TOOL_SET ∩ RESOLVED_ENABLED_TOOLS
=
{saee.evaluate_agent_run}
```

成功时只能声明：

```text
MCP_EXPOSURE_EVIDENCE_LEVEL=E3_CONTRACT_COMPOSED
MCP_EXPOSURE_PROOF_CLASS=CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE
EXPECTED_EFFECTIVE_TOOL_COUNT=1
EXPECTED_EFFECTIVE_TOOL=saee.evaluate_agent_run
```

## 3. Config Inspection Source

### 3.1 Canonical experiment input

配置意图来源固定为：

```text
/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/
SAEE-AC-MVP-20260716-001/runtime-inputs/mcp-cli-projection.txt
```

当前观察 hash：

```text
MCP_CLI_PROJECTION_SHA256=
d9fdfdc8c0a0aa2943dc1b8e1322ce4f3b915432ce1013a2d354ea73ff1c8ed3
```

冻结内容：

```text
mcp_servers.saee-readiness.command="python3"
mcp_servers.saee-readiness.args=["/Users/zhangbin/Documents/SAEE/scripts/saee_agent_readiness_mcp_stdio.py"]
mcp_servers.saee-readiness.enabled_tools=["saee.evaluate_agent_run"]
```

执行前必须重新计算 hash 并与 human grant 绑定；本报告记录的 hash 是 preparation
observation，不代替 future preimage receipt。

### 3.2 Resolved inspection surface

未来授权应允许一个 exact、只读的 Codex inspection command：

```text
CODEX_HOME=<new-isolated-codex-home>
/opt/homebrew/bin/codex mcp get saee-readiness --json
```

实际 command/argument/env bytes 必须先写入 authorization instance。该命令是候选
inspection surface；本计划不预先声称当前 CLI 一定输出 `enabled_tools`。

必须保存：

- exact command vector；
- secret-free environment key allowlist；
- exit code；
- stdout raw bytes；
- stderr raw bytes；
- raw SHA-256；
- canonical parsed JSON；
- canonical SHA-256。

### 3.3 Config gate predicate

P1 只有同时满足以下条件才 PASS：

```text
configured_server_count=1
server_id=saee-readiness
command_literal=python3
args_exact=["/Users/zhangbin/Documents/SAEE/scripts/saee_agent_readiness_mcp_stdio.py"]
enabled_tools_field_present=true
enabled_tools_exact=["saee.evaluate_agent_run"]
enabled_tool_count=1
disabled_tools=ABSENT_OR_EMPTY
unknown_override_count=0
```

`codex mcp list --json` 已被 Attempt 003 证明不能输出 tool allowlist，因此不能用作 P1
fallback。若 `mcp get --json` 仍省略 `enabled_tools`：

```text
CONFIG_INSPECTION_STATUS=FAIL
STOP_REASON=RESOLVED_ENABLED_TOOLS_NOT_OBSERVABLE
```

不得从 projection 自述推断 resolved parse 已成功，也不得自动尝试其他 command。

### 3.4 Isolation requirement

未来 collection 必须使用新的 isolated `CODEX_HOME`，不能复用：

- Attempt 001/002/003 的 CODEX_HOME；
- Group A/B subject session homes；
- 用户全局 Codex home；
- 含历史 canary、session、memory 或 plugin 的目录。

新目录位置、初始 tree hash、允许文件和 cleanup policy 必须由 human grant 绑定。
不得复制 provider credential，除非只读 inspection 确实需要且另有明确授权；默认不需要
model/provider credential。

## 4. MCP Discovery Source

### 4.1 Server entrypoint

本地 discovery 的唯一 entrypoint 候选为：

```text
/Users/zhangbin/Documents/SAEE/scripts/saee_agent_readiness_mcp_stdio.py
```

相关事实源：

| Surface | 当前观察 SHA-256 | 作用 |
|---|---|---|
| `scripts/saee_agent_readiness_mcp_stdio.py` | `414e3aeae0a710284604863f9fb1cddbbda4ac4cb03e89d62fad87c7a8e4cfde` | stdio entrypoint |
| `saee_backend/services/qianfan_readiness_mcp_adapter.py` | `0203087c1e26c2a7c7cca28f5f2c5ffb4a7069d52c7c9b2b9adecf7ca5a06c86` | MCP protocol/tool implementation |
| `capability-package/manifest.json` | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` | canonical capability facts |
| `agent-index.json` | `1ac0a832019d48dd3f40ef7f594c96938d9394f793fee8de06d1d8a429c61740` | derived Agent-readable projection |

这些也是 preparation observations；future grant 必须重新计算并冻结 exact hashes。
`agent-index.json` 不能替代 canonical manifest。

### 4.2 Discovery protocol

未来 P2 只允许以下 JSON-RPC 序列：

```text
1. initialize
   protocolVersion=2025-11-25
   capabilities={}
   clientInfo.name=saee-autonomy-check-e3-preflight
   clientInfo.version=0.1

2. notifications/initialized

3. tools/list

4. close stdin

5. bounded process exit / forced cleanup on timeout
```

禁止发送任何其他 method，特别是：

```text
tools/call
resources/list
prompts/list
completion/complete
```

### 4.3 Discovery gate predicate

P2 必须验证：

```text
initialize_response_protocol_version=2025-11-25
server_name=saee-agent-readiness-capability
tools_capability_present=true
tools_list_request_count=1
raw_tool_count=2
raw_tool_ids_exact=[
  "saee.evaluate_agent_run",
  "saee.evaluate_evidence"
]
target_tool_present=true
unexpected_tool_count=0
tools_call_request_count=0
```

比较集合时以 tool identity 为主，raw order 仍作为 observation 保留。若原始顺序改变但集合
不变，必须记录 drift 并停止，由人工判断；不能在当前授权内忽略。

### 4.4 Process and network boundary

未来 discovery 只允许本地 stdio 子进程：

- no network；
- no provider/model；
- no fixture access；
- no write to SAEE repository；
- bounded wall time；
- stdout/stderr 只写入新 evidence root；
- exit 后验证无残留 child process；
- timeout 时终止并生成 failure/cleanup receipt。

协议 discovery 必须记为：

```text
MCP_SERVER_DISCOVERY_INVOKED=true
MCP_TOOL_INVOKED=false
```

它不是 SAEE operation 调用。

## 5. Allowlist Comparison Rules

### 5.1 输入不可混合

比较器只能读取：

1. P1 canonical resolved allowlist；
2. P2 canonical raw server tool set；
3. frozen allowlist contract identifier/version；
4. human-accepted proof class。

不得读取 session event、model output 或实验行为作为补证。

### 5.2 Exact comparison

必须执行：

```text
R = set(raw_server_tool_ids)
E = set(resolved_enabled_tools)
X = R intersection E
```

PASS 条件：

```text
R == {
  saee.evaluate_agent_run,
  saee.evaluate_evidence
}

E == {
  saee.evaluate_agent_run
}

X == {
  saee.evaluate_agent_run
}

len(X) == 1
```

还必须验证：

```text
E subset_of R=true
saee.evaluate_evidence in R=true
saee.evaluate_evidence in E=false
saee.evaluate_evidence in X=false
unknown_tool in R=false
unknown_tool in E=false
```

### 5.3 Denylist and override rule

若 resolved config 存在 non-empty `disabled_tools`、未知 policy override 或第二个 config
source，本批次必须停止。不得尝试在 composition step 推断优先级。

### 5.4 Proof classification

P3/P4 receipt 必须包含：

```text
evidence_level=E3_CONTRACT_COMPOSED
proof_class=CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE
direct_model_visible_observation=false
production_boundary_proven=false
authorization_boundary_proven=false
```

任何输出把 E3 写成 E4 都视为 validation failure。

## 6. Hash and Receipt Strategy

### 6.1 Evidence root

future grant 必须绑定一个新的、此前不存在的 evidence root，例如：

```text
<experiment-root>/session-evidence/preflight/
e3-mcp-exposure/<authorization-id>/execution-001/
```

具体路径不能由执行者临时决定；必须由 Human Authority Owner 在授权实例中最终绑定。
Attempt 003 evidence 保持只读，不复制、覆盖或重命名。

### 6.2 Planned artifacts

| 顺序 | Artifact | 内容 |
|---|---|---|
| P0-1 | `authorization-receipt.json` | one-use grant、owner、expiry、scope |
| P0-2 | `preimage-receipt.json` | input paths、hashes、modes、locations |
| P1-1 | `resolved-mcp-config.raw.json` | Codex inspection stdout 原始 bytes |
| P1-2 | `resolved-mcp-config.stderr.txt` | inspection stderr 原始 bytes |
| P1-3 | `resolved-mcp-config.canonical.json` | 规范化 resolved server/allowlist |
| P1-4 | `config-inspection-receipt.json` | P1 predicates 与结果 |
| P2-1 | `mcp-discovery-requests.jsonl` | exact allowed JSON-RPC requests |
| P2-2 | `mcp-discovery-responses.raw.jsonl` | server 原始 responses |
| P2-3 | `mcp-discovery.stderr.txt` | server stderr |
| P2-4 | `mcp-tools-list.canonical.json` | 规范化 raw tool set |
| P2-5 | `mcp-discovery-receipt.json` | P2 predicates 与结果 |
| P3-1 | `allowlist-comparison.json` | R、E、X 和 exact assertions |
| P4-1 | `e3-composition-receipt.json` | proof level/class 与 final predicate |
| P5-1 | `cleanup-receipt.json` | process exit、residual process check |
| P5-2 | `collection-final-status.json` | PASS/FAIL、stop reason、next gate |

### 6.3 Serialization and hashing

所有 JSON/canonical JSONL 必须：

- UTF-8；
- recursive lexicographic key ordering；
- compact deterministic separators；
- stable final newline；
- 不包含 secret values；
- raw evidence 与 canonical evidence 分开保存；
- receipt 引用前序 artifact SHA-256；
- append-only，失败文件不得覆盖。

“deterministic hash 3/3”表示对同一冻结文件重复读取并计算三次 SHA-256，三次一致；
它不授权重复运行 config inspection 或 MCP discovery。

### 6.4 Receipt chain

```text
authorization-receipt hash
        ↓
preimage-receipt hash
        ↓
config-inspection-receipt hash
        ↓
mcp-discovery-receipt hash
        ↓
allowlist-comparison hash
        ↓
e3-composition-receipt hash
        ↓
cleanup-receipt hash
        ↓
collection-final-status hash
```

如果链中任一引用 hash 不一致，最终 gate 必须 FAIL。

## 7. Atomic Execution Sequence

### P0 — Authorization and preimage

1. 验证新 authorization ID、owner、expiry、one-use；
2. 验证 Human Owner 接受 E3 proof class；
3. 验证 evidence root、CODEX_HOME 与 historical roots 无碰撞；
4. 重新计算并绑定 projection、CLI、entrypoint、adapter、manifest hashes；
5. 记录 repo HEAD/status，但不清理当前 dirty worktree；
6. 生成 preimage receipt；
7. 任一失败立即停止。

### P1 — Config inspection

1. 使用 exact authorized environment；
2. 执行一次 resolved config inspection；
3. 原样保存 stdout/stderr/exit code；
4. 规范化解析；
5. 执行 config gate predicates；
6. FAIL 时不进入 P2。

### P2 — Local discovery

1. 从 exact frozen entrypoint 启动一个本地 stdio process；
2. 发送且只发送三条允许 message；
3. 原样保存 responses/stderr；
4. 关闭 stdin 并终止 process；
5. 验证 cleanup；
6. 规范化 tool set；
7. 执行 discovery predicates；
8. FAIL 时不进入 P3。

### P3 — Comparison

1. 加载 P1/P2 canonical outputs；
2. 计算 R、E、X；
3. 执行 exact assertions；
4. 输出 comparison receipt；
5. 任一 assertion false 即停止。

### P4 — E3 composition

只有 P0/P1/P2/P3 与 cleanup 全部 PASS 才生成 E3 receipt。该 receipt 只表示 E3
contract-composed proof，不授权 session。

### P5 — Final close

1. 再次确认无残留 process；
2. 三次重算所有 artifact hashes；
3. 验证 receipt chain；
4. 写入 one-use authorization consumption receipt；
5. 输出 final status；
6. 停止并交给 Human review。

## 8. Evidence Confidence Boundary

### 8.1 E3 足以支持什么

E3 PASS 可以支持：

- 一个受控 MVP preflight 的 MCP exposure contract 接受；
- 进入下一道 Human Runtime Final Gate review；
- 把 B 组预期 effective tool set 记录为 exact singleton；
- 后续实验的因果边界说明。

### 8.2 E3 不支持什么

E3 PASS 不支持：

- `MODEL_VISIBLE_TOOL_COUNT_DIRECTLY_OBSERVED=1`；
- Agent discovery/adoption 已验证；
- SAEE Tool 已调用；
- Agent 行为已经改变；
- production runtime isolation guarantee；
- security certification；
- permission、authorization 或 execution control claim；
- commercial validation 已开始或完成。

### 8.3 Validation completion predicate

未来只有全部 predicate 满足，才可输出：

```text
MCP_EXPOSURE_VALIDATION_COMPLETE=true
MCP_EXPOSURE_EVIDENCE_LEVEL=E3_CONTRACT_COMPOSED
MCP_EXPOSURE_PROOF_CLASS=CONTRACT_COMPOSED_NOT_DIRECT_MODEL_VISIBLE
GROUP_B_EXPECTED_EFFECTIVE_TOOL_COUNT=1
GROUP_B_EXPECTED_EFFECTIVE_TOOL=saee.evaluate_agent_run
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_TOOL_INVOKED=false
EXPERIMENT_EXECUTED=false
```

当前 preparation 阶段不满足该 predicate，所以保持 false。

## 9. Stop Conditions

以下任一条件成立立即 fail-closed：

1. 缺少新的 one-use human grant；
2. authorization 过期、已 consumed 或 owner 不匹配；
3. 未明确接受 E3 proof class；
4. evidence root、CODEX_HOME 或 process location collision；
5. projection、CLI、entrypoint、adapter 或 manifest hash 漂移；
6. resolved inspection command/arguments 与授权不一致；
7. config inspection 非零退出、非 JSON 或省略 `enabled_tools`；
8. resolved server/tool/denylist predicate 不满足；
9. 尝试用 `codex mcp list` 或其他 command 自动 fallback；
10. local discovery initialization 失败或 protocol version 漂移；
11. raw tool count/identity/order 与冻结事实不一致；
12. 发送了任何非 allowlisted MCP method；
13. 发送或尝试发送 `tools/call`；
14. 读取 fixture、Prompt、Trigger 或 provider credential；
15. 创建 Agent session 或调用 model/provider；
16. 需要修改 MCP implementation、Capability、Schema、Runtime 或 Evaluation；
17. discovery process 超时或无法证明 cleanup；
18. canonical serialization/hash 3/3 不稳定；
19. receipt chain 断裂；
20. E3 被错误标记为 E4 direct model-visible evidence；
21. 试图自动进入 Session A/B 或行为分析。

失败输出必须包括 exact stop reason，并保持：

```text
MCP_EXPOSURE_VALIDATION_COMPLETE=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_TOOL_INVOKED=false
EXPERIMENT_EXECUTED=false
```

## 10. First-Principles Review

### 10.1 为什么 E3 足够支持 MVP？

第一轮 MVP 需要一个低权限、可复现的实验入口，而不是对 Codex 内部实现做生产级证明。
E3 分别观察 resolved config 与 server runtime truth，再按公开 allowlist contract 组合，足以
判断实验环境是否满足预先约定的最小 exposure boundary。它提供了可审计因果前提，同时
没有引入 session/model 这一新的实验变量。

### 10.2 为什么不能把配置等同于模型可见？

配置只表达 intent。它还会经过 CLI parse、config merge、allowlist/denylist、server
discovery、runtime registration 与 model-facing serialization。E3 也只到 contract-composed
expected exposure；没有 direct observation 就必须保持
`DIRECT_MODEL_VISIBLE_OBSERVATION=false`。

### 10.3 为什么证据等级必须显式声明？

同一句“只暴露一个工具”在 E1、E3、E4 下含义不同。若不写证据等级，配置意图会被
传播成 runtime fact，再被传播成 model-visible guarantee。显式等级让实验结论、商业声明
和授权强度保持匹配，也让未来升级证据时知道缺少哪一层。

## 11. No-Experiment and Product Boundary

本计划及下一 evidence collection 只属于 preflight evidence lane：

```text
AGENT_SESSION_ALLOWED=false
MODEL_INVOCATION_ALLOWED=false
SAEE_TOOL_CALL_ALLOWED=false
FIXTURE_TRANSMISSION_ALLOWED=false
EXPERIMENT_EXECUTION_ALLOWED=false
BEHAVIOR_ANALYSIS_ALLOWED=false
COMMERCIAL_VALIDATION_ALLOWED=false
```

继续冻结：

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
```

不得把本次发现注册为 `Agent Capability Drift` 新 capability、MCP assurance product、
security layer 或 enterprise governance service。

按仓库 `AGENTS.md`，当前 Constitutional Program Mainline 是 SAEE 与 Agent Evidence
Project 的受控合并。本实验仍是次级验证路线：

```text
MAINLINE_DRIFT_DETECTED=true
DRIFT_CLASS=SECONDARY_EXPERIMENT_LANE_NOT_CONSTITUTIONAL_MAINLINE
DRIFT_CORRECTION=TIMEBOX_E3_COLLECTION_AND_DO_NOT_EXPAND_SCOPE
```

## 12. Recommendation

下一步只建议 Human review 本计划，并在接受 exact paths、commands、hashes、timeout、owner
与 E3 proof class 后，另行创建 one-use collection authorization instance。

```text
RECOMMEND_E3_COLLECTION=true
E3_COLLECTION_EXECUTION_AUTHORIZED=false
E4_INTROSPECTION_AUTHORIZED=false
SESSION_AUTHORIZED=false
NEXT_GATE_AFTER_FUTURE_E3_PASS=HUMAN_RUNTIME_FINAL_GATE_REVIEW
```

## 13. Final Status

```text
MCP_EXPOSURE_COLLECTION_PLAN_STATUS=COMPLETE
MCP_EXPOSURE_VALIDATION_COMPLETE=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
EXPERIMENT_EXECUTED=false
CODE_CHANGED=false
MCP_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_MCP_EXPOSURE_COLLECTION_PLAN
```
