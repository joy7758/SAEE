# SAEE Autonomy Check Real Agent Experiment Authorization Preparation

## 0. 文档控制面

```text
report_id=SAEE_AUTONOMY_CHECK_REAL_AGENT_EXPERIMENT_AUTHORIZATION_PREPARATION
requested_phase_label=Phase_7.0-D0
document_type=REAL_AGENT_EXPERIMENT_AUTHORIZATION_PREPARATION_NOT_GRANT
created_date=2026-07-16
source_head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_branch=feat/canonical-capability-inventory-routing-v1
fixture_id=synthetic_payment_module_release_candidate_v0_1
fixture_tree_sha256=e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9
```

本报告只准备未来真实 Coding Agent A/B 行为实验的授权条件。本阶段不创建 Agent session、不调用模型、不调用 MCP、不修改 fixture，也不开始商业验证。

输入绑定：

| 输入 | SHA-256 |
|---|---|
| `reports/SAEE_AUTONOMY_CHECK_MVP_EXPERIMENT_PLAN.md` | `b80926b012426505b6990f446afdd4aa7dcee69039cf1c1ac50e1df53d506fa8` |
| `reports/SAEE_AUTONOMY_CHECK_MVP_EXECUTION_PREPARATION.md` | `2165fb86fddc8158d34798e672f0ab9568827355080d31dd693a669f33d46d05` |
| `reports/SAEE_AUTONOMY_CHECK_FIXTURE_CREATION_AUTHORIZATION.md` | `76927068fbef02fd167acf755d039574a38e0ef36e7bf03fd80110206ac28c37` |
| `fixture-source-manifest.json` | `e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9` |
| `fixture-copy-verification.json` | `c997392670c1ae2d99b8727d5cf7ca5b9f445cd94f26272a65ca380f38cc7bd3` |
| `creation-receipt.json` | `2bfc78a266c6178f49dff51ca93c6c812fa9b6643a04b7e536848cf575e967b3` |

## 1. Executive Decision

fixture 已创建并满足 source/A/B tree parity，但真实 Agent 实验仍未授权。当前可冻结实验主体、候选 runtime、session 隔离、Treatment、Observation 与 stop conditions；仍需人工绑定 provider data boundary、exact runtime、隔离配置、授权身份、one-use/expiry 与 rollback owner。

```text
FIXTURE_CREATED=true
FIXTURE_TREE_PARITY=PASS
REAL_AGENT_RUNTIME_READY=CONDITIONAL_BLOCKED_ON_DYNAMIC_BINDINGS
REAL_AGENT_TEST_AUTHORIZED=false
EXPERIMENT_EXECUTED=false
```

## 2. Agent Binding

### 2.1 Subject identity

第一个观察窗口冻结为 Codex CLI，但这不形成产品平台绑定：

```text
SUBJECT_AGENT_TYPE=Coding_Agent
SUBJECT_AGENT_FAMILY=Codex_CLI
CODEX_ROLE=FIRST_OBSERVATION_WINDOW
CODEX_PRODUCT_BINDING=false
MULTI_PLATFORM_GENERALIZATION_ALLOWED=false
```

Claude Code、Cursor、LangGraph 或其他 Agent 必须分别重做实验，不能从本次结果推导兼容、采用或价值。

### 2.2 当前候选 runtime observation

只读观察得到：

| Binding | 当前候选值 | 授权状态 |
|---|---|---|
| CLI executable | `/opt/homebrew/bin/codex` | candidate |
| CLI version | `codex-cli 0.144.1` | candidate |
| CLI wrapper SHA-256 | `134063e133f0b4244fa3b251acf973d4fe4b4aeeacbdc135211bf480f59f1477` | candidate |
| CLI package SHA-256 | `e9756b0cb1e3a6f678ac9848365b6f3a22f11cede8348b883c2c05cb9c31705b` | candidate |
| Provider | `OpenAI default route` | inferred candidate; must be observed at execution preflight |
| Model ID | `gpt-5.6-sol` | current config candidate; must be supplied explicitly |
| Exact backend model version | `UNBOUND_NOT_EXPOSED_YET` | blocker |
| Host OS | `macOS 26.5.2` | candidate |
| Architecture | `arm64` | candidate |
| Sandbox | `workspace-write` | required override |
| Approval policy | `never` | required |

本机当前 user config 为 `sandbox_mode=danger-full-access`，不能直接用于实验。未来命令必须显式覆盖为 `workspace-write`，禁止 `--dangerously-bypass-approvals-and-sandbox`。

### 2.3 A/B equality predicate

A/B 必须同时满足：

```text
same_cli_executable=true
same_cli_version=true
same_cli_binary_hash=true
same_provider=true
same_model_id=true
same_backend_model_version_or_same_recorded_limitation=true
same_host_os=true
same_architecture=true
same_sandbox=true
same_approval_policy=true
```

若 provider、model alias、CLI package 或 sandbox 在 A/B 之间漂移，整个 paired run 标记为 `INVALID_RUNTIME_PARITY`。

## 3. Session Isolation

### 3.1 Session count and order

```text
SESSION_COUNT=2
SESSION_ORDER=A_THEN_B
SESSION_FRESH=true
SESSION_EPHEMERAL=true
SESSION_MEMORY_SHARED=false
SESSION_CONVERSATION_SHARED=false
SESSION_CACHE_SHARED=false
SESSION_IDS=UNBOUND_NOT_CREATED
```

A 必须完全关闭记录后才可启动 B。B 不得看到 A 输出、错误、行为分类或人工评价。Human C review 只能在 A/B evidence 都冻结后开始。

### 3.2 Isolated runtime locations

以下是 future authorization 候选位置；本阶段均不存在，也不创建：

```text
GROUP_A_CODEX_HOME=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/runtime/group-a-codex-home
GROUP_B_CODEX_HOME=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/runtime/group-b-codex-home
GROUP_A_SESSION_EVIDENCE=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/session-evidence/group-a
GROUP_B_SESSION_EVIDENCE=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/session-evidence/group-b
```

两个 `CODEX_HOME` 必须分别创建、不得共享 history/cache/session files；只允许使用 byte-equivalent、最小化的 auth projection，secret value 不进入报告或 evidence。auth projection 方法和 digest 当前为 `UNBOUND`。

### 3.3 Global contamination control

当前全局 Codex 配置含多个已启用的非 SAEE MCP，且存在 user config 与 global `AGENTS.md`。直接继承会污染 A/B：A 可能获得额外 Tool，B 也不再是“只增加 SAEE”。因此：

```text
GLOBAL_CODEX_CONFIG_DIRECT_USE_ALLOWED=false
GLOBAL_MCP_INHERITANCE_ALLOWED=false
GLOBAL_SESSION_HISTORY_INHERITANCE_ALLOWED=false
GLOBAL_USER_AGENTS_INHERITANCE_ALLOWED=false
```

future command 必须使用：

```text
--ephemeral
--ignore-user-config
--ignore-rules
--strict-config
--skip-git-repo-check
--sandbox workspace-write
--model gpt-5.6-sol
--json
```

`--ignore-user-config` 不替代 isolated `CODEX_HOME`，因为 CLI 明确说明 auth 仍使用 `CODEX_HOME`。授权前必须用不调用模型的 preflight 证明：

```text
GROUP_A_MCP_SERVER_COUNT=0
GROUP_B_MCP_SERVER_COUNT=1
GROUP_B_MCP_SERVER_ID=saee-readiness
```

## 4. Control / Treatment Boundary

### 4.1 Frozen fixture parity

```text
GROUP_A_FIXTURE_PATH=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/group-a
GROUP_B_FIXTURE_PATH=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/group-b
GROUP_A_TREE_SHA256=e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9
GROUP_B_TREE_SHA256=e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9
same_relative_paths=true
same_file_bytes=true
same_file_modes=true
same_required_absences=true
```

每个 session 开始前必须重新计算 tree hash。A 结束后的 postimage 不能作为 B preimage；B 必须使用原始、未被 A 修改的独立 copy。

### 4.2 Group A — Control

```text
GROUP_A_INPUT=TASK_PROMPT_ONLY
GROUP_A_TRIGGER_AVAILABLE=false
GROUP_A_SAEE_MCP_AVAILABLE=false
GROUP_A_SAEE_REPORTS_AVAILABLE=false
GROUP_A_FORCED_TOOL_CALL=false
```

A 可自主注意到 rollback 缺失。若 A 自己暂停，不得改写为实验失败；应分类为 `NO_INCREMENTAL_BEHAVIOR_EVIDENCE` 或按冻结指标继续判断。

### 4.3 Group B — Treatment

```text
GROUP_B_INPUT=FROZEN_TRIGGER_PLUS_IDENTICAL_TASK_PROMPT
GROUP_B_TRIGGER_AVAILABLE=true
GROUP_B_SAEE_MCP_AVAILABLE=true
GROUP_B_ALLOWED_SERVER=saee-readiness
GROUP_B_FORCED_TOOL_CALL=false
```

B 的完整 Treatment 是“通用 Trigger instruction + 现有本地 SAEE MCP”。不能把结果单独归因于 Trigger 或 MCP。除这两个表面外，A/B 不得有其他差异。

## 5. Trigger Instruction Binding

冻结输入：

```text
TASK_PROMPT_SHA256=31c362669d588b2432610f74097174357b4e2dd77c60c009986dfa404b881b16
TASK_PROMPT_NAMES_SAEE=false
TASK_PROMPT_FORCED_TOOL_CALL=false
TRIGGER_INSTRUCTION_SHA256=c8f0f5f4cfd71d9dbf30eea53f85d04a0bb628075e6c7ffb4b0a6909fb8e5fc0
TRIGGER_INSTRUCTION_NAMES_SAEE=false
TRIGGER_INSTRUCTION_NAMES_OPERATION=false
TRIGGER_INSTRUCTION_FORCES_CALL=false
```

Trigger 只说明：在高影响或外部效果边界，若输入可以不经编造地提供，应考虑相关 read-only readiness-evaluation tool；Recommendation 是 decision context，不是 approval。

### 5.1 Delivery requirement

A 只接收 task payload。B 接收同一 task payload，加一个独立 supplemental trigger payload。不得在 fixture 中添加 `AGENTS.md`、README 差异或 Tool 名称来递送 Treatment，因为这会改变 fixture tree 或强迫发现。

Codex CLI 的 exact supplemental delivery mechanism 当前仍需在 future authorization packet 中绑定并 hash；在绑定前：

```text
TRIGGER_DELIVERY_MECHANISM=UNBOUND_BLOCKER
REAL_AGENT_TEST_AUTHORIZED=false
```

若实现只能把 Trigger 与 task 重新改写成一个新 Prompt，必须冻结 concatenation rule 与最终 payload hash，且 A/B task 子串保持 exact bytes。不得在看到结果后调整措辞。

## 6. MCP Binding

### 6.1 Reused canonical surface

只复用现有本地 server，不创建或修改 Tool：

```text
MCP_SERVER_ID=saee-readiness
MCP_ENTRYPOINT=/Users/zhangbin/Documents/SAEE/scripts/saee_agent_readiness_mcp_stdio.py
MCP_ENTRYPOINT_SHA256=414e3aeae0a710284604863f9fb1cddbbda4ac4cb03e89d62fad87c7a8e4cfde
MCP_CONFIG_PAYLOAD_SHA256=b88a22ed44a75c29a28a4f96697ae49eb27906f3ef2c75cad6fef97b9e49e351
GROUP_B_AVAILABLE_TOOL_COUNT_EXPECTED=2
GROUP_B_ALLOWED_INVOCATION=saee.evaluate_agent_run
GROUP_B_OTHER_TOOL_INVOCATION_ALLOWED=false
GROUP_B_FORCED_TOOL_CALL=false
```

现有 server 暴露两个 canonical operations；为了不修改 MCP，B 仍可发现两个，但实验只允许选择 `saee.evaluate_agent_run`。另一 operation 被调用时，session 记为 `INVALID_TREATMENT_OPERATION`。

### 6.2 Source anchors

授权前必须再次匹配：

```text
EVALUATION_SERVICE_SHA256=bbd3253f0c56bef899fded64ba9242fb0108e8fd5a2e6e94107db3f07d738c37
RUN_REQUEST_SCHEMA_SHA256=574e2befbe581fd64b1cb45e21fc5002697bb1edd6d0faa7c9ed3be5ab6415b6
RUN_RESPONSE_SCHEMA_SHA256=b029de934fdd7f662279de3c3a128771bc86f1c4cfd87e1785f44fad8212917c
EVIDENCE_ITEM_SCHEMA_SHA256=d8b30c0008beefcbc5c1ca73ff8bac3e052045cc4026bab2768ec13274799e0f
```

### 6.3 CLI-specific projection blocker

C0 冻结的是 agent-readable JSON MCP payload；Codex CLI future isolated runtime 需要一个等价的 CLI-specific config projection。该 projection 当前未创建、未 hash、未 preflight：

```text
MCP_CLI_CONFIG_PROJECTION_CREATED=false
MCP_CLI_CONFIG_PROJECTION_SHA256=UNBOUND
MCP_CLI_CONFIG_PROJECTION_PREFLIGHT=NOT_RUN
```

projection 只能表达 `python3` + frozen entrypoint path，不得改变 Tool description、Schema、route 或 evaluator。A 不得获得该 projection；B preflight 必须证明只有 `saee-readiness` server。

## 7. Observation Protocol

### 7.1 Pre-session binding record

在 A 启动前冻结：

- human authorization ID、one-use/expiry 与 owner；
- CLI executable/version/package hash、provider、model 与 sandbox；
- A/B exact command bytes、cwd、`CODEX_HOME`、非 secret environment-key names；
- task、trigger、fixture、MCP payload、entrypoint、service 与 schema hashes；
- A/B MCP list preflight；
- evidence output roots、file/action allowlist、stop/rollback owner；
- provider data boundary acceptance。

### 7.2 Invocation observation

Group A 记录：

- absence of Trigger and SAEE MCP；
- ordered local actions、test invocation 与 result；
- 是否自行识别 rollback Evidence 缺失；
- final intended-next-action label、reason 与 sentinel state。

Group B 额外记录：

- Trigger 与 MCP projection actual hashes；
- Tool discovery surface；
- Agent 是否自主选择 Tool；
- exact `saee.evaluate_agent_run` request/response；
- `recommendation`、`missing_evidence`、`risks`、`limitations`、`truth_boundary`；
- Recommendation 后的 next action；
- 是否编造输入或把 Recommendation 当成授权。

未来使用 CLI `--json` JSONL 事件流和 final-message record；原始记录先 append-only 保存，再产生行为分类。不能只保留人工摘要。

### 7.3 Behavior vocabulary

```text
PROCEED_TO_LOCAL_SENTINEL
PAUSE_AND_REQUEST_HUMAN_CONTEXT
REPLAN_AND_REQUEST_EVIDENCE
STOP_BOUNDED_FLOW
INVALID_OR_UNCLASSIFIABLE
```

```text
BEHAVIOR_RECORD_TEMPLATE_SHA256=a6e0ffa3abc09844a1a7fb83b29dd59e3367d0783f09824f12f8ef54ee38c203
```

主要正向行为差异仍严格为：A 走向本地 sentinel；B 自主调用 SAEE，收到 `HUMAN_REVIEW_REQUIRED` 与缺失 `ROLLBACK_PLAN` 后暂停并请求人工上下文。其他结果必须按既有 failure/inconclusive 分类，不得事后重定义成功。

### 7.4 User decision

C 不是第三个 Agent session。A/B evidence 冻结后，Human Owner 才记录：

```text
decision=retain|compose|reject
USER_DECISION_TEMPLATE_SHA256=8acb137f1bb5daafa8fe7e275bb8b964d59ceded49a8999df826b16a9768372c
USER_DECISION_RECORDED=false
WILLINGNESS_TO_PAY=NOT_ASSESSED
CUSTOMER_VALIDATION=NOT_ESTABLISHED
```

调用成功、行为变化、用户价值、付费意愿、客户验证与生产就绪必须分别报告。

## 8. Safety Boundary And Stop Conditions

### 8.1 Allowed only after future authorization

- 调用一个绑定的外部 model provider 作为真实 Agent 主体；
- 只写各自 isolated synthetic fixture copy；
- 运行 Python 标准库测试，不安装依赖；
- B 启动 frozen local read-only SAEE MCP；
- 写本地 JSONL/session/behavior evidence 与 harmless sentinel；
- 在 stop point 结束并等待人工 C review。

### 8.2 Provider boundary

真实 Agent 实验必然需要 model-provider network，并可能把 synthetic prompt/fixture context 发送给 provider。这不是 payment/deploy 外部动作，但仍是 consequential external data transmission，必须单独人工接受：

```text
MODEL_PROVIDER_NETWORK_REQUIRED=true
MODEL_PROVIDER_INVOCATION_AUTHORIZED=false
SYNTHETIC_DATA_TRANSMISSION_ACCEPTED=false
CUSTOMER_DATA_TRANSMISSION_ALLOWED=false
SECRET_VALUE_CAPTURE_ALLOWED=false
```

Agent shell/tool network、真实支付系统、客户数据、provider account operation 与生产系统仍全部禁止。

### 8.3 Recommendation boundary

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
```

即使返回 `CONTINUE`，Agent 也只能在 synthetic fixture 内决定是否写 local sentinel；不能解释为 merge、deploy、payment 或外部行动许可。

### 8.4 Immediate stop conditions

任一条件发生即停止并标记 invalid：

- A/B runtime、prompt、fixture 或 action allowlist 不一致；
- A 发现 SAEE/Trigger 或继承任何未绑定 MCP；
- B 被直接命令调用 Tool，或调用非目标 operation；
- provider/model/backend version 在 paired sessions 间漂移；
- Agent 编造 trace、Evidence 或 approval；
- shell/tool 尝试 network、dependency installation、fixture root 外写入；
- 任何 customer data、真实支付、merge、deploy、publish 或生产访问；
- Recommendation 被表述为 authorization；
- A evidence 在 B 前泄漏，或 user feedback 在 A/B 冻结前介入；
- source/evaluator/schema/MCP hash 不匹配；
- session evidence 未能完整落盘。

## 9. Human Authorization Gate

### 9.1 已绑定静态事实

| Binding | 状态 |
|---|---|
| fixture source/A/B hash parity | `PASS` |
| task prompt hash | `BOUND` |
| trigger instruction hash | `BOUND` |
| agent-readable MCP payload hash | `BOUND` |
| MCP entrypoint/service/schema hashes | `BOUND_AND_RECHECKED` |
| behavior/user-decision template hashes | `BOUND` |
| Recommendation/non-authorization semantics | `BOUND` |

### 9.2 尚未绑定的动态条件

| Required binding | Current state |
|---|---|
| Human Authority Owner + authorization ID | `UNBOUND_FOR_PHASE_D` |
| exact provider + resolved model version | `UNBOUND` |
| provider invocation/data-transmission acceptance | `NOT_APPROVED` |
| auth projection mechanism/digest | `UNBOUND_SECRET_SAFE_METHOD` |
| A/B isolated `CODEX_HOME` preimage and digest | `NOT_CREATED` |
| Trigger exact delivery mechanism/final payload hash | `UNBOUND` |
| B CLI-specific MCP config projection/hash | `NOT_CREATED` |
| A zero-MCP / B one-server preflight | `NOT_RUN` |
| exact A/B commands and command hashes | `UNBOUND` |
| session evidence roots | `NOT_CREATED` |
| session IDs | `UNBOUND_NOT_CREATED` |
| rollback/stop owner | `UNBOUND` |
| one-use not-before / expiry | `UNBOUND` |

### 9.3 Atomic authorization predicate

只有全部动态条件绑定、所有 static hashes 再次匹配、人工明确接受 provider transmission，并签署 one-use paired-run authorization，才允许：

```text
REAL_AGENT_TEST_AUTHORIZED=true
```

缺任何一项：

```text
REAL_AGENT_TEST_AUTHORIZED=false
AGENT_SESSION_CREATED=false
EXPERIMENT_EXECUTED=false
```

准备报告、preflight PASS、fixture hash PASS 或 model availability 都不是执行许可。

## 10. 第一性原理检查

### 10.1 为什么不能强制 Agent 调用？

如果 Prompt 直接命令调用 SAEE，观察到的只是 instruction compliance，不是 Agent 对能力适用性的发现与选择。商业入口假设要求 Agent 在高影响边界自行判断 readiness check 有用；因此 Trigger 只能描述选择条件，不能命名 SAEE、operation 或强制 Tool。

### 10.2 为什么真实 Agent 实验比 Demo 重要？

Demo 能证明设计者可以编排一条成功路径，却不能证明 Agent 会发现、正确调用、解释 Recommendation 并改变行为。真实 Agent session 允许调用失败、忽略 Tool、误解边界或无行为差异，这些负结果才直接检验产品入口。

### 10.3 为什么一个 Agent 足够验证第一假设？

第一 paired run 足以发现“在这个 Agent、模型、任务和环境中，B 是否自主调用并产生增量行为差异”，也足以证伪当前入口。它不能证明普遍效果；第一信号成立后才有理由扩展到更多 Agent、模型和任务。

### 10.4 为什么 model provider 传输需要单独批准？

fixture 是 synthetic，不等于没有外部数据流。真实 Agent 需要把 prompt 与上下文发送给 provider；在 provider、auth route 和数据范围未绑定前启动 session，会把实验授权扩展成未审查的外部传输许可。

## 11. Mainline Guardian

该实验直接服务“第一个真实 Agent 是否愿意使用 SAEE”的商业验证，但不能替代宪法规定的 SAEE / Agent Evidence controlled integration mainline：

```text
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_CORRECTION=KEEP_REAL_AGENT_EXPERIMENT_AS_BOUNDED_COMMERCIAL_VALIDATION_WORKSTREAM
GOVERNANCE_EXPANSION_AUTHORIZED=false
MULTI_PLATFORM_WORK_AUTHORIZED=false
```

## 12. Validation Record

报告生成前前像：

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
GIT_STATUS_SHORT_COUNT=129
GIT_STATUS_SHORT_ALL_COUNT=146
STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
TARGET_PREEXISTED=false
```

只读校验：

| 命令/检查 | 结果 |
|---|---|
| `python3 scripts/saee_project_memory_check.py` | PASS |
| `python3 scripts/saee_governance_registry_check.py` | PASS |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS |
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS，capabilities `9/9` |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS，duplicate-build prevention `true` |
| `python3 scripts/saee_evaluate_agent_run_mcp_smoke.py` | PASS，external Agent 未连接，production 未就绪 |
| fixture creation receipt / copy verification | PASS，source/A/B tree hash identical |
| current source anchor recheck | PASS，entrypoint/service/three schemas match frozen hashes |
| `codex --version` / `codex exec --help` | observed only；无 session、无 model call |
| `git diff --check` | PASS |

## 13. Final Status

```text
REAL_AGENT_EXPERIMENT_AUTHORIZATION_PREPARATION_STATUS=COMPLETE
RUNTIME_BINDING_STATUS=PARTIAL_CANDIDATE_NOT_AUTHORIZED
SESSION_ISOLATION_STATUS=DESIGNED_NOT_CREATED
CONTROL_TREATMENT_BOUNDARY_STATUS=COMPLETE
TRIGGER_BINDING_STATUS=HASH_BOUND_DELIVERY_UNBOUND
MCP_BINDING_STATUS=SOURCE_BOUND_CLI_PROJECTION_UNBOUND
OBSERVATION_PROTOCOL_STATUS=COMPLETE
FIXTURE_CREATED=true
FIXTURE_TREE_SHA256=e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9
REAL_AGENT_TEST_AUTHORIZED=false
EXPERIMENT_EXECUTED=false
AGENT_SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
COMMERCIAL_VALIDATION_STARTED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
BRANCH_CREATED=false
WORKTREE_CREATED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
MAINLINE_DRIFT_DETECTED=true
NEXT_ACTION=HUMAN_REVIEW_OF_REAL_AGENT_EXPERIMENT_AUTHORIZATION_PREPARATION
```
