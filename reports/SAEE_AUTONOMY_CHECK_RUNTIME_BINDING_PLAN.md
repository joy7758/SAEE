# SAEE Autonomy Check Runtime Isolation & Binding Plan

## 0. 文档控制面

```text
report_id=SAEE_AUTONOMY_CHECK_RUNTIME_BINDING_PLAN
requested_phase_label=Phase_7.0-D1
document_type=RUNTIME_ISOLATION_BINDING_PLAN_ONLY
created_date=2026-07-16
source_head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_branch=feat/canonical-capability-inventory-routing-v1
fixture_id=synthetic_payment_module_release_candidate_v0_1
fixture_tree_sha256=e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9
```

本报告把未来真实 Agent paired experiment 的 runtime、A/B isolation、Trigger delivery、MCP projection 和 provider-key boundary 冻结为可执行计划。本阶段不创建 `CODEX_HOME`、session、runtime input、MCP config 或 evidence directory，不调用模型/MCP，也不执行实验。

输入绑定：

| 输入 | SHA-256 |
|---|---|
| `reports/SAEE_AUTONOMY_CHECK_REAL_AGENT_EXPERIMENT_AUTHORIZATION_PREPARATION.md` | `9f26ef67283a646b6d63fba1469c5d792fe1ee4754b322e5f2914c1392fd6757` |
| `reports/SAEE_AUTONOMY_CHECK_MVP_EXPERIMENT_PLAN.md` | `b80926b012426505b6990f446afdd4aa7dcee69039cf1c1ac50e1df53d506fa8` |
| `fixture-copy-verification.json` | `c997392670c1ae2d99b8727d5cf7ca5b9f445cd94f26272a65ca380f38cc7bd3` |
| `creation-receipt.json` | `2bfc78a266c6178f49dff51ca93c6c812fa9b6643a04b7e536848cf575e967b3` |

## 1. Executive Decision

runtime isolation 方案可闭合，但当前仍是 plan，不是执行授权。A/B 必须使用同一 Codex CLI/model/provider/sandbox，只允许以下 Treatment difference：

```text
A = Agent + Task + Fixture + zero MCP
B = Agent + Task + Fixture + generic Trigger + SAEE evaluate_agent_run only
```

当前全局 Codex 配置不能用于实验：它包含多个非 SAEE MCP、global user state，且默认 `danger-full-access`。直接使用会引入 Tool、权限、memory 和 key 污染。

```text
RUNTIME_ISOLATION_DESIGN=COMPLETE
RUNTIME_ENVIRONMENT_CREATED=false
REAL_AGENT_TEST_AUTHORIZED=false
```

## 2. Runtime Binding

### 2.1 Frozen candidate runtime

| Runtime field | Frozen candidate |
|---|---|
| Agent family | `Codex_CLI` |
| Product binding | `false`；first observation window only |
| CLI path | `/opt/homebrew/bin/codex` |
| CLI version | `codex-cli 0.144.1` |
| wrapper SHA-256 | `134063e133f0b4244fa3b251acf973d4fe4b4aeeacbdc135211bf480f59f1477` |
| package SHA-256 | `e9756b0cb1e3a6f678ac9848365b6f3a22f11cede8348b883c2c05cb9c31705b` |
| native binary SHA-256 | `29915529b97697def1a957b0505e770aa6a45744435d62fc263e98d7619e167a` |
| Provider | `OpenAI` candidate；必须在 authorization preflight 观察 |
| Model ID | `gpt-5.6-sol`；必须显式传入，禁止 fallback |
| Exact backend version | `UNBOUND_IF_PROVIDER_DOES_NOT_EXPOSE`；A/B 记录同一限制 |
| Host | `macOS 26.5.2`, `arm64` |
| Sandbox | `workspace-write` |
| Approval policy | `never` |
| Session mode | `ephemeral` |

future authorization preflight 必须重新计算三个 CLI hashes 并运行 `codex --version`。任一不一致时停止，不能自动升级 CLI、替换模型或切换 provider。

### 2.2 Common CLI restrictions

A/B command 都必须显式包含：

```text
--ephemeral
--ignore-user-config
--ignore-rules
--strict-config
--skip-git-repo-check
--sandbox workspace-write
--model gpt-5.6-sol
-c approval_policy="never"
-c shell_environment_policy.inherit="none"
-c tools.web_search=false
-c memories.enabled=false
-c agents.max_threads=1
-c agents.max_depth=0
--json
```

这些 config values 在 runtime creation preflight 中必须由 `--strict-config` 接受；若当前 CLI 不支持任一限制，不能静默删除，必须回到人工审查。

严格禁止：

```text
--dangerously-bypass-approvals-and-sandbox
--dangerously-bypass-hook-trust
codex exec resume
--add-dir
danger-full-access
```

### 2.3 Runtime parity predicate

```text
same_cli_path=true
same_cli_version=true
same_cli_hashes=true
same_provider=true
same_model_id=true
same_backend_version_or_same_recorded_limitation=true
same_host=true
same_sandbox=true
same_approval_policy=true
same_common_cli_restrictions=true
```

## 3. A/B Environment

### 3.1 Bound fixture roots

```text
GROUP_A_CWD=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/group-a
GROUP_B_CWD=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/group-b
GROUP_A_TREE_SHA256=e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9
GROUP_B_TREE_SHA256=e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9
```

每个 session 启动前独立重算 hash。A 的 postimage 不能复制给 B；B 必须保持 C3 创建的独立初始像。

### 3.2 Environment matrix

| Surface | A — Control | B — Treatment |
|---|---|---|
| CLI/model/provider | frozen identical | frozen identical |
| sandbox/approval | `workspace-write` / `never` | identical |
| fixture tree | group-a frozen hash | group-b same frozen hash |
| task payload | exact frozen payload | exact same payload |
| Trigger | absent | frozen generic Trigger prefix |
| MCP server count | `0` | `1` |
| enabled MCP Tool count | `0` | `1` |
| enabled MCP Tool | none | `saee.evaluate_agent_run` |
| inherited user MCP/plugins/memory | none | none |
| web/search/other provider tools | disabled | disabled |
| external shell/tool network | prohibited | prohibited |
| model-provider control-plane | same authorized OpenAI route | same |

### 3.3 Non-treatment environment equality

授权前必须冻结并比较：locale、timezone、shell、`PATH` policy、Python path/version、environment-key names、fixture file modes、test command、stop rules 与 evidence format。secret values 不进入 comparison record。

## 4. CODEX_HOME Isolation

### 4.1 Exact future paths

```text
GROUP_A_CODEX_HOME=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/runtime/group-a-codex-home
GROUP_B_CODEX_HOME=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/runtime/group-b-codex-home
GROUP_A_SESSION_EVIDENCE=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/session-evidence/group-a
GROUP_B_SESSION_EVIDENCE=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/session-evidence/group-b
```

当前四个位置均不存在。本计划不创建。

### 4.2 Creation rules

future runtime-creation authorization 只允许：

- 分别创建两个 mode `0700` 的 `CODEX_HOME`；
- 创建 byte-equivalent minimal auth projection；
- 不复制 global `config.toml`、`AGENTS.md`、history、sessions、memories、plugins、skills、hooks、MCP 或 caches；
- 分别创建两个 mode `0700` session-evidence root；
- evidence 只记录 auth mode/provider/credential-source ID，不记录 secret value 或 raw-secret digest；
- A/B auth projection 必须使用同一 provider/account route，但物理文件不共享写入。

### 4.3 Preimage and contamination checks

执行前要求：

```text
GROUP_A_CODEX_HOME_PREEXISTED=false
GROUP_B_CODEX_HOME_PREEXISTED=false
GROUP_A_SESSION_EVIDENCE_PREEXISTED=false
GROUP_B_SESSION_EVIDENCE_PREEXISTED=false
GLOBAL_CONFIG_COPIED=false
GLOBAL_AGENTS_COPIED=false
GLOBAL_HISTORY_COPIED=false
GLOBAL_MCP_COPIED=false
SHARED_WRITABLE_CODEX_HOME=false
```

collision 或意外文件一律 fail closed；不得 clean、merge、覆盖或重用旧 session root。

## 5. Session Isolation

### 5.1 Fresh paired-session rules

```text
SESSION_COUNT=2
SESSION_ORDER=A_THEN_B
SESSION_EPHEMERAL=true
SESSION_RESUME_ALLOWED=false
SESSION_IDS=UNBOUND_NOT_CREATED
A_OUTPUT_VISIBLE_TO_B=false
USER_FEEDBACK_BEFORE_B_CLOSE=false
SUBAGENT_DELEGATION_ALLOWED=false
MULTI_MODEL_FALLBACK_ALLOWED=false
```

A 必须结束、保存 raw JSONL、final message 与 fixture postimage 后封存。B 启动前不得生成 A/B comparison，不得给 B 提供 A 的行为或人工评价。

### 5.2 Future command shape

两个命令使用同一 common restrictions，只改变 `CODEX_HOME`、CWD、evidence output path，以及 B-only Trigger/MCP projection：

```text
A:
CODEX_HOME=<GROUP_A_CODEX_HOME> codex exec <COMMON_RESTRICTIONS> \
  -C <GROUP_A_CWD> \
  --output-last-message <GROUP_A_SESSION_EVIDENCE>/final-message.txt \
  - < <TASK_PAYLOAD>

B:
CODEX_HOME=<GROUP_B_CODEX_HOME> codex exec <COMMON_RESTRICTIONS> \
  <B_ONLY_MCP_PROJECTION> \
  -C <GROUP_B_CWD> \
  --output-last-message <GROUP_B_SESSION_EVIDENCE>/final-message.txt \
  - < <TRIGGER_PLUS_TASK_PAYLOAD>
```

`--json` stdout 必须写到各自 `events.jsonl`，stderr 写到各自 `stderr.log`。exact argv、stdin、environment-key names 与 redirection paths 在 human authorization 前形成 canonical command record 并 hash；当前不创建这些记录。

### 5.3 Evidence isolation

raw event logs append-only 保存，不允许只保留 summary。session 结束后记录：session ID、start/end、CLI/provider/model、actual prompt hash、MCP preflight、Tool calls、test result、final behavior label、sentinel state、boundary violations 与 post-session tree hash。

## 6. Trigger Delivery Binding

### 6.1 Selected delivery mechanism

冻结为：

```text
TRIGGER_DELIVERY_MODE=USER_PROMPT_PREFIX
TRIGGER_SYSTEM_MESSAGE_INJECTION=false
TRIGGER_SKILL_LOADING=false
TRIGGER_AGENTS_MD_INJECTION=false
TRIGGER_FIXTURE_MUTATION=false
TRIGGER_NAMES_SAEE=false
TRIGGER_NAMES_OPERATION=false
TRIGGER_FORCES_CALL=false
```

选择 user-prompt prefix 的原因：Codex CLI 对 stdin user prompt 有稳定、可 hash 的入口；不依赖隐藏 system/developer channel、Skill 或文件差异。

### 6.2 Byte composition

```text
TASK_PROMPT_SHA256=31c362669d588b2432610f74097174357b4e2dd77c60c009986dfa404b881b16
TASK_PROMPT_BYTES=914
TRIGGER_INSTRUCTION_SHA256=c8f0f5f4cfd71d9dbf30eea53f85d04a0bb628075e6c7ffb4b0a6909fb8e5fc0
TRIGGER_INSTRUCTION_BYTES=801
```

A stdin：exact task payload including its one final LF。

B stdin composition：

```text
TRIGGER_PAYLOAD_WITH_ONE_FINAL_LF
+
ONE_ADDITIONAL_LF
+
TASK_PAYLOAD_WITH_ONE_FINAL_LF
```

```text
GROUP_A_STDIN_SHA256=31c362669d588b2432610f74097174357b4e2dd77c60c009986dfa404b881b16
GROUP_A_STDIN_BYTES=914
GROUP_B_STDIN_SHA256=26b87949a9fe405554652a27062eabb2de99f60e05c54132a04bab7ae8825147
GROUP_B_STDIN_BYTES=1716
```

future runtime-input creation 必须从 C0 frozen payload 提取，不得人工重打字。创建后重新验证三个 hash；任何差异阻止 session。

### 6.3 Non-forcing proof

Trigger 只要求“consider whether an available read-only readiness-evaluation tool is relevant”。它不包含 SAEE、Tool ID、operation ID 或“must call”。B 未调用时必须记录 `INVOCATION_HYPOTHESIS_FAILED`，不能通过补 Prompt 重跑同一 attempt。

## 7. MCP Projection Binding

### 7.1 Selected projection

B-only CLI config projection 冻结为以下三行 UTF-8/LF/final newline payload：

```text
mcp_servers.saee-readiness.command="python3"
mcp_servers.saee-readiness.args=["/Users/zhangbin/Documents/SAEE/scripts/saee_agent_readiness_mcp_stdio.py"]
mcp_servers.saee-readiness.enabled_tools=["saee.evaluate_agent_run"]
```

```text
MCP_CLI_PROJECTION_SHA256=d9fdfdc8c0a0aa2943dc1b8e1322ce4f3b915432ce1013a2d354ea73ff1c8ed3
MCP_CLI_PROJECTION_BYTES=223
MCP_ENTRYPOINT_SHA256=414e3aeae0a710284604863f9fb1cddbbda4ac4cb03e89d62fad87c7a8e4cfde
```

projection 通过三个 B-only `-c` arguments 传入，不写 SAEE repository `.mcp.json`，也不修改 server。local CLI binary 包含 `enabled_tools` config surface；runtime preflight 仍必须由 `--strict-config` 证明该 projection 被当前版本接受。

### 7.2 Exposure predicate

使用 isolated `CODEX_HOME` 进行不调用模型的 preflight：

```text
A: codex mcp list --json -> configured_server_count=0
B: codex mcp list --json <B_ONLY_PROJECTION> -> configured_server_count=1
B.server=saee-readiness
B.enabled_tools=[saee.evaluate_agent_run]
B.other_enabled_tools=[]
```

若 B 看到第二个 SAEE operation、global MCP、remote MCP 或任何非 SAEE server，则停止；不得用“Agent 不会调用”替代暴露隔离。

### 7.3 No capability change

该 filter 是实验 runtime exposure，不是 MCP/Capability/Product 变更。canonical server、Tool description、Schema、route 与 evaluator 保持原样。

## 8. API Key And Provider Boundary

### 8.1 Only one provider route

```text
SUBJECT_PROVIDER=OpenAI
SUBJECT_MODEL=gpt-5.6-sol
OTHER_MODEL_PROVIDER_ALLOWED=false
MULTI_PROVIDER_ROUTING_ALLOWED=false
PROVIDER_FALLBACK_ALLOWED=false
EXTERNAL_AGENT_ORCHESTRATION_ALLOWED=false
```

ChatGPT workspace Tool、DeepThink/DeepSeek、千问/百炼、百度千帆、Anthropic、GitHub MCP 与其他 provider/tool keys 全部不得进入 A/B process、shell environment、MCP config 或 fixture。

### 8.2 Credential isolation

- 只允许 Human Owner 选择并绑定一种 Codex/OpenAI auth route；
- A/B 使用同一 credential-source ID 与 provider account route；
- raw credential、token、key、cookie 与 secret digest 不写入 report/log；
- Agent-generated shell environment 不继承 provider keys；
- `shell_environment_policy.inherit=none` 必须 preflight；
- evidence 只记录 key names absent/present boolean，不记录 value；
- auth failure 直接停止，不切换其他 provider 或凭据。

### 8.3 External transmission gate

真实 Codex session 会把 synthetic prompt/fixture context 发送给 OpenAI provider。必须在 Human Authorization 中明确：

```text
MODEL_PROVIDER_INVOCATION_APPROVED=true
SYNTHETIC_CONTEXT_TRANSMISSION_ACCEPTED=true
CUSTOMER_DATA_TRANSMISSION_ALLOWED=false
REAL_PAYMENT_DATA_TRANSMISSION_ALLOWED=false
```

在该 gate 生效前，`MODEL_INVOKED=false`。

## 9. Stop Conditions

任一条件发生即停止且不启动/继续 session：

1. CLI version/hash、provider、model、host 或 sandbox parity 失败；
2. 任一 `CODEX_HOME`/evidence root collision 或共享写入；
3. global config、AGENTS、history、memory、plugin、hook、MCP 或 cache 被继承；
4. A MCP count 非零；
5. B 不是 exactly one server + exactly one enabled Tool；
6. task、Trigger、B stdin 或 MCP projection hash 不匹配；
7. A/B fixture preimage hash 不匹配；
8. exact command record、provider data gate、one-use/expiry 或 owner 未绑定；
9. Agent 尝试 subagent、多模型、web、network、dependency install 或 fixture 外写入；
10. 任何真实 payment、customer data、merge、deploy、publish 或生产访问；
11. A evidence 向 B 泄漏，或 A/B 冻结前注入 user feedback；
12. Recommendation 被解释为 authorization；
13. JSONL/session evidence 不完整；
14. auth 失败后发生 provider fallback。

停止后保留 attempt evidence，不调整 Prompt/Trigger 以“挽救”结果。

## 10. Human Authorization Preconditions

进入 session creation 前仍须人工绑定：

| Required item | Current status |
|---|---|
| Human Authority Owner + authorization ID | `UNBOUND_FOR_D_RUNTIME_EXECUTION` |
| exact CLI/model/provider recheck | `CANDIDATE_ONLY` |
| provider invocation/transmission acceptance | `NOT_APPROVED` |
| exact two `CODEX_HOME` preimages | `NOT_CREATED` |
| secret-safe auth projection | `UNBOUND` |
| common CLI config strict preflight | `NOT_RUN` |
| Trigger/runtime input files and actual hashes | `NOT_CREATED` |
| B MCP projection actual argv/preflight | `NOT_RUN` |
| A zero-MCP / B one-Tool proof | `NOT_RUN` |
| exact command records/hashes | `UNBOUND` |
| session evidence roots | `NOT_CREATED` |
| stop/rollback owner | `UNBOUND` |
| one-use not-before / expiry | `UNBOUND` |

所有条件闭合前：

```text
REAL_AGENT_TEST_AUTHORIZED=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
EXPERIMENT_EXECUTED=false
```

## 11. 第一性原理检查

### 11.1 为什么实验环境比模型选择更重要？

第一实验不比较模型能力，而比较同一 Agent 在有无 SAEE exposure 时的行为。模型再强，如果 A/B 权限、Tool、memory、Prompt delivery 或 provider key 不同，结果就不能归因。环境把唯一变量限制为 Treatment，是可证伪性的前提。

### 11.2 为什么多模型测试应该后置？

加入第二个模型会同时增加模型差异、provider 行为、Tool 适配和样本需求。在一个 Agent 上连“是否调用、是否改变行为”都未观察到前，多模型只扩大成本与解释空间；第一信号成立后再逐 Agent 复现实验，才能测试泛化。

### 11.3 为什么因果归因需要最小变量？

若 B 同时拥有更多权限、其他 MCP、不同 Prompt channel 或备用模型，B 的行为变化有多种解释。最小变量使可能结论收敛到：完整 B Treatment 是否产生增量行为差异；即便结果为零或失败，也能产生可信信息。

### 11.4 为什么 B 需要 Tool-level filter？

只限制 server 仍可能暴露另一个 SAEE operation，Agent 的选择就不再唯一对应本实验 target。`enabled_tools` 让 B 只发现 `saee.evaluate_agent_run`，同时避免修改 canonical MCP server。

## 12. Mainline Guardian

该工作直接支持第一个真实 Agent 使用 SAEE 的商业验证，但仍是受控支线，不替代宪法规定的 SAEE / Agent Evidence integration mainline：

```text
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_CORRECTION=KEEP_RUNTIME_EXPERIMENT_AS_BOUNDED_COMMERCIAL_VALIDATION_WORKSTREAM
MULTI_MODEL_TEST_AUTHORIZED=false
MULTI_PLATFORM_TEST_AUTHORIZED=false
```

## 13. Validation Record

报告生成前前像：

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
GIT_STATUS_SHORT_COUNT=130
GIT_STATUS_SHORT_ALL_COUNT=147
STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
TARGET_PREEXISTED=false
RUNTIME_PATHS_PREEXISTED=false
SESSION_EVIDENCE_PATHS_PREEXISTED=false
```

只读检查：

| 命令/检查 | 结果 |
|---|---|
| `python3 scripts/saee_project_memory_check.py` | PASS |
| `python3 scripts/saee_governance_registry_check.py` | PASS |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS |
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS，capabilities `9/9` |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS，duplicate-build prevention `true` |
| fixture evidence recheck | PASS，source/A/B `e8d812ce...c1bd9` |
| C0 payload extraction/hash recheck | PASS，task/Trigger frozen hashes reproduce |
| B stdin composition hash | PASS，`26b87949...5147` |
| local CLI `enabled_tools` surface inspection | present；未创建 config、未运行 session |
| B MCP projection hash | PASS，`d9fdfdc8...c8ed3` |
| `git diff --check` | PASS |

## 14. Final Status

```text
RUNTIME_BINDING_PLAN_STATUS=COMPLETE
RUNTIME_BINDING_EXECUTED=false
RUNTIME_ENVIRONMENT_CREATED=false
CODEX_HOME_CREATED=false
TRIGGER_DELIVERY_BINDING_STATUS=COMPLETE_PLAN_ONLY
MCP_PROJECTION_BINDING_STATUS=COMPLETE_PLAN_ONLY
API_KEY_BOUNDARY_STATUS=COMPLETE_PLAN_ONLY
REAL_AGENT_TEST_AUTHORIZED=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
EXPERIMENT_EXECUTED=false
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
NEXT_ACTION=HUMAN_REVIEW_OF_RUNTIME_BINDING_PLAN
```
