# SAEE Autonomy Check Preflight Separation Plan

## 0. 文档控制面

```text
report_id=SAEE_AUTONOMY_CHECK_PREFLIGHT_SEPARATION_PLAN
requested_phase_label=Phase_7.0-D3.2
document_type=PREFLIGHT_SEPARATION_PLAN_ONLY
created_date=2026-07-16
source_head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_branch=feat/canonical-capability-inventory-routing-v1
subject_cli=codex-cli_0.144.1
fixture_tree_sha256=e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9
```

本报告只设计 Attempt 003 之前的 preflight separation（预检查职责分离）。它不授权
Attempt 003，不创建 Agent session，不调用 model 或 MCP Tool，不执行实验，也不改变
fixture、Prompt、Trigger、model、provider、MCP projection 或 behavior metric。

输入证据：

| 输入 | SHA-256 |
|---|---|
| `reports/SAEE_AUTONOMY_CHECK_REAL_AGENT_EXECUTION_AUTHORIZATION.md` | `d35d99f3565f9ce10d4e4be044f2c4706fddd5153fb98fd126c4350e61271872` |
| `reports/SAEE_AUTONOMY_CHECK_RUNTIME_BINDING_PLAN.md` | `c5c8d48bc6c8cecd99d9becb5e63453a84ce768db81a88a94ab3e7df38ef6f13` |
| Attempt 001 `runtime-preflight-failure.json` | `87238e686d0897744d0e38dd9cb739009f4358bc664a9975e3aab8b5f1b9ed41` |
| Attempt 002 `runtime-preflight-repair-failure.json` | `60fa54a92d02c036dac5151b069292ebca91ad131b38a51e81216024f63a2d72` |
| Attempt 002 raw stderr | `25311193518f12899de88c33daaf29a07da1c255bbf2145e727f4299c3ca71a2` |
| Attempt 001 common runtime config | `3f3ddfa8f26320e3dd11a79bae0744f776e3fe7ce0a75667d7099e8ada88f081` |
| Attempt 002 repaired runtime config | `eed6f753ea02efe281ad2ff8c091bea8b10f747b4803f09638c43a5765460f41` |

> 注：Attempt 002 raw stderr 的实际证据 hash 在本报告验证时必须重新计算并与原文件绑定；
> 若表中值与实际 evidence 不一致，报告 validation 必须失败，不得人工忽略。

## 1. Executive Decision

Attempt 001 与 Attempt 002 证明原 preflight 把两个不同职责错误地压进同一命令：

1. runtime/exec configuration validation；
2. MCP configured exposure inspection。

当前 CLI 对这两类命令的 option surface 不相同。Attempt 003 必须拆为两个独立 gate，
使用不同的判定标准与证据文件；任何 gate 失败都停止，且不能自动启动 Session A。

```text
PREFLIGHT_SEPARATION_REQUIRED=true
RUNTIME_AND_MCP_GATE_COUPLING=REJECTED
ATTEMPT_003_AUTHORIZED=false
REAL_AGENT_TEST_AUTHORIZED=false
```

## 2. Attempt 001 Failure Analysis

### 2.1 Observed failure

```text
attempt_id=SAEE-AC-REAL-AGENT-20260716-001-preflight-attempt-001
failed_stage=A_ZERO_MCP_CONFIG_PARSE
configured_agents_max_depth=0
required_minimum=1
observed_error=agents.max_depth must be at least 1
```

### 2.2 Classification

这是 config value validity failure（配置值合法性失败），不是 MCP discovery 结果。
CLI 在输出 A 的 configured MCP list 之前即停止，因此不能从空输出推断 A 为 zero MCP。

### 2.3 Closed and preserved facts

- Attempt 001 已 consumed，保持 write-once evidence lineage；
- `agents.max_depth=0` 不得复用；
- Attempt 002 仅把该值改为 `1`；
- Attempt 001 的空 `group-a-mcp-list.json` 是 pre-output artifact，不是有效 zero-MCP proof。

## 3. Attempt 002 Failure Analysis

### 3.1 Observed failure

```text
attempt_id=SAEE-AC-REAL-AGENT-20260716-001-preflight-attempt-002
configured_agents_max_depth=1
repair_delta_only=true
failed_stage=A_ZERO_MCP_STRICT_CONFIG_COMPATIBILITY
observed_error=Error: `--strict-config` is not supported for `codex mcp`
```

### 3.2 Classification

这是 command-surface compatibility failure（子命令选项兼容性失败）。它不表示
`--strict-config` 无价值，也不表示 A 暴露了 MCP；它只证明 `codex mcp` 不能承担
`codex exec` 的 strict runtime validation 职责。

### 3.3 Evidence interpretation

- Attempt 002 越过了 `agents.max_depth=0` 阻塞；
- A MCP list 没有产生有效 JSON；
- B preflight 未运行；
- model、MCP Tool、session 和 experiment 均未启动；
- 删除 `--strict-config` 后原地重跑会改变 gate semantics，因此被正确拒绝。

## 4. Separated Gate Architecture

```text
Immutable Input Recheck
        ↓
Gate R — Runtime Static Preflight
        ↓
Gate M-A — A Zero-MCP Exposure
        ↓
Gate M-B — B One-Server/One-Tool Exposure
        ↓
Cross-Gate Consistency Receipt
        ↓
Human Session Authorization
        ↓
Atomic Session A Startup Guard
```

Attempt 003 只可执行到 `Cross-Gate Consistency Receipt`。该 receipt 是 evidence，
不是 permission；它不能把 `REAL_AGENT_TEST_AUTHORIZED` 提升为 `true`。

## 5. Gate R — Runtime Validation Boundary

### 5.1 CLI identity and installation integrity

Attempt 003 必须重新验证且全部一致：

| Runtime surface | Expected value |
|---|---|
| CLI path | `/opt/homebrew/bin/codex` |
| CLI version | `codex-cli 0.144.1` |
| wrapper SHA-256 | `134063e133f0b4244fa3b251acf973d4fe4b4aeeacbdc135211bf480f59f1477` |
| package metadata SHA-256 | `e9756b0cb1e3a6f678ac9848365b6f3a22f11cede8348b883c2c05cb9c31705b` |
| native binary SHA-256 | `29915529b97697def1a957b0505e770aa6a45744435d62fc263e98d7619e167a` |

wrapper、package metadata 与 native binary 是三个不同 surface，不得用其中一个 hash
冒充另一个。任一漂移都停止并重新绑定 CLI。

### 5.2 Frozen runtime configuration

Attempt 003 的 common config candidate 固定为 Attempt 002 内容：

```text
approval_policy="never"
shell_environment_policy.inherit="none"
tools.web_search=false
memories.enabled=false
agents.max_threads=1
agents.max_depth=1
sandbox_workspace_write.network_access=false
```

必须进行两类无模型检查：

1. 使用标准 TOML parser 解析并断言 exact key/value allowlist；
2. 对 exact file bytes、行尾、mode 和 SHA-256 生成 receipt。

这只能证明 config artifact 正确，不能冒充 CLI 已在真实 `codex exec` startup 中加载它。

### 5.3 Model, provider and sandbox binding

Gate R 只验证静态 command contract：

```text
model=gpt-5.6-sol
provider=OpenAI
sandbox=workspace-write
approval_policy=never
fallback=false
web_search=false
shell_network=false
```

没有 model invocation 时，provider 只能标记为 `STATIC_BOUND`，不能标记为
`LIVE_PROVIDER_CONFIRMED`。live provider/model observation 属于后续 Session A evidence。

### 5.4 Environment and CODEX_HOME isolation

必须断言：

- A/B 使用各自 isolated `CODEX_HOME`；
- 除批准的 secret-safe `auth.json` projection 外无 global config/history/session/memory/plugin；
- two homes 不共享 writable state；
- environment key names 精确匹配 frozen allowlist，secret values 不进入证据；
- A/B CWD、TMPDIR 和 evidence root 不碰撞；
- SAEE repository 是只读依赖，不是 experiment workspace。

### 5.5 Gate R output vocabulary

Gate R 只能输出：

```text
RUNTIME_STATIC_PREFLIGHT_STATUS=PASS/FAIL
STRICT_EXEC_CONFIG_SUPPORT_SURFACE=ADVERTISED
STRICT_EXEC_CONFIG_LIVE_PARSE_STATUS=NOT_EXECUTED
LIVE_PROVIDER_CONFIRMED=false
```

在没有启动 `codex exec` 的情况下，不得输出
`STRICT_EXEC_CONFIG_LIVE_PARSE_STATUS=PASS`。

## 6. Gate M — MCP Exposure Validation Boundary

### 6.1 Scope

Gate M 只回答“subject Agent 将看到哪些 configured MCP surfaces”，不验证 model、sandbox
或 runtime behavior，也不启动 MCP server/Tool。

### 6.2 A exposure predicate

在 A isolated `CODEX_HOME` 下运行 configuration inspection，要求：

```text
command_family=codex mcp list --json
strict_config_argument=ABSENT_BY_EXPLICIT_ATTEMPT_003_AUTHORIZATION
configured_server_count=0
configured_server_ids=[]
```

exit code 非零、stdout 非规范 JSON、出现任何 server 或继承 global config 均为 FAIL。

### 6.3 B exposure predicate

在 B isolated `CODEX_HOME` 下，仅注入冻结 projection：

```text
mcp_server_count=1
mcp_server_id=saee-readiness
enabled_tool_count=1
enabled_tool=saee.evaluate_agent_run
other_server_count=0
other_enabled_tool_count=0
```

必须绑定：

```text
MCP_CLI_PROJECTION_SHA256=d9fdfdc8c0a0aa2943dc1b8e1322ce4f3b915432ce1013a2d354ea73ff1c8ed3
```

`codex mcp list --json` 只能读取 configured exposure；不得使用 `get` 启动 server，
不得调用 Tool，不得读取 SAEE 其他 operation。

### 6.4 A/B equivalence

Gate M 的 A/B 命令必须除 B-only MCP projection、isolated home 和 evidence path 外 byte-equivalent。
不得把 runtime strict arguments 混入 MCP inspection，也不得让 B 继承更多权限、插件或工具。

### 6.5 Gate M output vocabulary

```text
MCP_EXPOSURE_PREFLIGHT_STATUS=PASS/FAIL
GROUP_A_ZERO_MCP_PROVEN=true/false
GROUP_B_ONE_TOOL_PROVEN=true/false
MCP_SERVER_STARTED=false
MCP_INVOKED=false
```

运行 CLI 的 `mcp list` 子命令不等于调用 MCP server/Tool；证据必须明确区分二者。

## 7. Strict Config Handling

### 7.1 Observed command-support matrix

| Command surface | `--strict-config` advertised | Observed conclusion |
|---|---:|---|
| `codex exec --help` | yes | exec surface 支持该 option |
| `codex mcp --help` | no | 不得传入 |
| `codex mcp list --help` | no | 不得传入 |
| `codex doctor --help` | no | 不能替代 strict exec proof |

Attempt 002 已提供直接运行证据：给 `codex mcp` 传入该 option 会被 CLI 拒绝。

### 7.2 Help-path canary limitation

本阶段的无 session 探针观察到：

```text
codex exec --strict-config -c agents.max_depth=0 --help -> exit 0
codex exec --strict-config -c agents.max_depth=1 --help -> exit 0
codex exec --strict-config -c definitely_unknown_config_key=1 --help -> exit 0
```

因此 help path 在配置解析前返回，不能作为 strict config validation。报告不得把“选项出现在
help”升级为“runtime config 已通过”。

### 7.3 No silent downgrade rule

- `--strict-config` 必须保留在后续真实 `codex exec` A/B command；
- 它只从 `codex mcp list` inspection command 中移除，且该变化必须由 Attempt 003 Human Grant 明示；
- MCP gate 以 isolated home、exact projection hash、canonical JSON 和 exact exposure predicate
  替代不受支持的 option，不以宽松成功替代严格证明；
- 若 Human Owner 不接受这种职责分离，Attempt 003 保持 BLOCKED。

### 7.4 Atomic Session A startup guard

当前 CLI 没有已证实的 provider-free、可真正完成 strict `codex exec` config parse 的独立命令。
因此 full runtime parse 只能保留为后续 Session A 的原子启动 guard：

1. 必须先获得独立 session/model authorization；
2. actual A command 继续携带 `--strict-config` 和冻结 config；
3. 任何 config error 在首个有效 model event 前停止并封存；
4. 一旦出现 provider/model event，即视为 Session A 已创建，不能伪装成 preflight；
5. Attempt 003 preflight authorization 本身不得越过该边界。

## 8. Attempt 003 Rules

### 8.1 Required order

```text
1. New one-use Attempt 003 authorization record
2. Preserve Attempt 001/002 read-only
3. Recheck fixture and all frozen input hashes
4. Gate R static validation
5. Gate M-A zero-MCP inspection
6. Seal Gate M-A raw output
7. Gate M-B one-server/one-Tool inspection
8. Seal Gate M-B raw output
9. Cross-gate consistency receipt
10. Stop for Human Review
```

### 8.2 Immutable bindings

Attempt 003 不得改变：

- fixture tree `e8d812ce...c1bd9`；
- task Prompt `31c36266...1b16`；
- Trigger `c8f0f5f4...e5fc0`；
- B stdin `26b87949...5147`；
- MCP projection `d9fdfdc8...c8ed3`；
- `OpenAI` / `gpt-5.6-sol`；
- `workspace-write` / `approval_policy=never`；
- A zero MCP / B only `saee.evaluate_agent_run`；
- behavior labels、metric 和 stop conditions。

### 8.3 Stop conditions

以下任一出现即 consume Attempt 003 并停止：

- CLI/version/wrapper/package/native hash drift；
- common config 不等于 Attempt 002 repaired config；
- help/support matrix 与当前 CLI 不一致；
- A output 不是 exact zero MCP；
- B output 不是 exact one server/one Tool；
- any MCP server/Tool 被启动或调用；
- fixture、Prompt、Trigger、stdin 或 projection hash drift；
- isolated home 继承 global state；
- command exit 非零、raw evidence 缺失或 canonical assertion 失败；
- 任何 session/model/provider invocation 开始。

禁止自动 repair、retry、fallback 或在同一 authorization 下改变 validation method。

## 9. Human Authorization Requirements

Attempt 003 Human Grant 必须显式绑定：

```text
ATTEMPT_003_AUTHORIZATION_ID=<new-one-use-id>
ATTEMPT_003_PREFLIGHT_ONLY=true
ALLOW_RUNTIME_MCP_PREFLIGHT_SEPARATION=true
ALLOW_MCP_LIST_WITHOUT_STRICT_CONFIG=true
KEEP_STRICT_CONFIG_ON_FUTURE_CODEX_EXEC=true
ACCEPT_STRICT_EXEC_LIVE_PARSE_DEFERRED_TO_SESSION_START=true/false
KEEP_ALL_EXPERIMENT_INPUTS_UNCHANGED=true
SESSION_CREATION_AUTHORIZED=false
MODEL_INVOCATION_AUTHORIZED=false
MCP_TOOL_INVOCATION_AUTHORIZED=false
RETRY_AUTHORIZED=false
HUMAN_AUTHORITY_OWNER_ID=<bound>
```

缺任何字段或 residual-risk decision 为 `false` 时：

```text
ATTEMPT_003_AUTHORIZED=false
```

Attempt 003 PASS 后仍需独立 Human Session Grant；preflight validator、SAEE Recommendation
或 MCP exposure PASS 都不是 authorization。

## 10. Evidence Plan

Attempt 003 未来只可新增：

```text
attempt-003-authorization-record.json
runtime-static-preflight.json
group-a-mcp-list.json
group-a-mcp-list.stderr.txt
group-b-mcp-list.json
group-b-mcp-list.stderr.txt
mcp-exposure-assertions.json
cross-gate-consistency-receipt.json
attempt-003-status.txt
```

所有 JSON 使用 UTF-8、recursive lexicographic key order、final LF 和 deterministic SHA-256。
raw stdout/stderr 先封存，summary 后生成；失败 artifact 不覆盖、不删除。

## 11. 第一性原理检查

### 11.1 为什么运行验证和 MCP 验证必须分离？

因为二者回答不同问题：runtime gate 证明 subject command 的身份、权限和配置边界；MCP gate
证明 Agent 能发现的 Tool surface。把它们耦合后，一个不支持的 CLI option 会同时遮蔽两个
结论，既不能证明 runtime，也不能证明 MCP exposure。

### 11.2 为什么失败比不透明成功更有价值？

Attempt 001/002 给出了可定位、可复现的 command-semantics evidence。若删除参数后继续，得到的
“成功”无法说明 strict config 是否生效，也无法证明 A/B 只有一个 treatment variable；这种成功
不能支撑行为或商业判断。

### 11.3 为什么不能为了跑通实验降低验证标准？

实验目标是判断 SAEE exposure 是否改变 Agent 行为。若为了启动 session 改变权限、Tool surface
或 runtime validation，结果将同时受多个变量影响。更快得到不可归因结果，不比没有结果更有价值。

## 12. Mainline And Product Boundary

当前 Constitution 把 SAEE / Agent Evidence controlled integration 定义为 program mainline；本实验是
secondary testing lane。它可产生 product-entry evidence，但不能取代主线或批准自身执行：

```text
MAINLINE_DRIFT_DETECTED=true
PROGRAM_MAINLINE=saee_agent_evidence_integration
CURRENT_WORK_CLASS=SECONDARY_CONTROLLED_EXPERIMENT_PREPARATION
NEW_RUNTIME_CAPABILITY_CLAIM=false
```

两次 preflight failure 不能被扩展为“SAEE 已具备 runtime assurance 产品能力”；当前只证明
内部 fail-closed 实验流程发现了两个 CLI integration blockers。

## 13. Final Status

```text
PREFLIGHT_SEPARATION_PLAN_STATUS=COMPLETE
ATTEMPT_003_AUTHORIZED=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
EXPERIMENT_EXECUTED=false
CODE_CHANGED=false
MCP_CHANGED=false
FIXTURE_CHANGED=false
PROMPT_CHANGED=false
TRIGGER_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_PREFLIGHT_SEPARATION_PLAN
```
