# SAEE Autonomy Check Real Agent Experiment Execution Authorization

## 0. 文档控制面

```text
report_id=SAEE_AUTONOMY_CHECK_REAL_AGENT_EXECUTION_AUTHORIZATION
requested_phase_label=Phase_7.0-D2
document_type=EXECUTION_AUTHORIZATION_DESIGN_NOT_GRANT
authorization_candidate_id=SAEE-AC-REAL-AGENT-20260716-001
created_date=2026-07-16
source_head=f6ac41f4b068377e7778e8c3d83b99bd8382debc
source_branch=feat/canonical-capability-inventory-routing-v1
fixture_id=synthetic_payment_module_release_candidate_v0_1
fixture_tree_sha256=e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9
```

本报告定义未来一次真实 Codex CLI paired experiment 的最小执行授权。它不是生效授权，不创建 session，不调用 model/MCP，不创建 runtime artifacts，也不执行实验。

输入绑定：

| 输入 | SHA-256 |
|---|---|
| `reports/SAEE_AUTONOMY_CHECK_RUNTIME_BINDING_PLAN.md` | `c5c8d48bc6c8cecd99d9becb5e63453a84ce768db81a88a94ab3e7df38ef6f13` |
| `reports/SAEE_AUTONOMY_CHECK_MVP_EXPERIMENT_PLAN.md` | `b80926b012426505b6990f446afdd4aa7dcee69039cf1c1ac50e1df53d506fa8` |
| `fixture-source-manifest.json` | `e8d812ce949f2ae24729efee4326a3c3daa84c89c7161bc6e5f83b8f181c1bd9` |
| `fixture-copy-verification.json` | `c997392670c1ae2d99b8727d5cf7ca5b9f445cd94f26272a65ca380f38cc7bd3` |
| `creation-receipt.json` | `2bfc78a266c6178f49dff51ca93c6c812fa9b6643a04b7e536848cf575e967b3` |

## 1. Executive Decision

实验对象、fixture、Trigger delivery 和 B-only MCP projection 已在 D1 形成计划级绑定。仍缺少人工主体、provider transmission consent、secret-safe auth projection、runtime preflight、exact command receipt、预算/超时、one-use/expiry 和 rollback owner，因此：

```text
EXECUTION_AUTHORIZATION_DESIGN=COMPLETE
HUMAN_EXECUTION_AUTHORIZATION_RECORDED=false
REAL_AGENT_TEST_AUTHORIZED=false
```

任何准备报告、fixture PASS、runtime plan 或 model availability 都不能把上述状态自动提升为 `true`。

## 2. Human Authorization Scope

### 2.1 Future one-use authorization may allow only

获得独立 Human Grant 后，一次 authorization 只可允许：

1. 创建两个 isolated `CODEX_HOME`、runtime-input 和 session-evidence roots；
2. 创建 exactly two fresh ephemeral Codex CLI sessions，顺序为 A 后 B；
3. 两组显式使用 `codex-cli 0.144.1`、OpenAI、`gpt-5.6-sol`、`workspace-write`；
4. 把冻结 synthetic task/fixture context 发送到同一 provider route；
5. 只在各自 group fixture copy 内修改最小文件并运行标准库测试；
6. A 使用 zero MCP；B 只暴露 `saee.evaluate_agent_run`；
7. B 由 Agent 自主决定是否调用，最多一次；
8. 写 raw JSONL、stderr、final message、pre/post tree manifests、behavior records 和 harmless local sentinel；
9. 两组完成后停止，封存 evidence，等待 Human C review。

### 2.2 Authorization explicitly excludes

- 真实 payment/provider/account/customer/production data；
- GitHub、Git、branch、worktree、commit、push、PR、merge；
- deploy、publish、release、cloud、database 或基础设施操作；
- SAEE repository、Capability、Schema、MCP、Runtime、Evaluation、Constitution 或 Product Registry 修改；
- ChatGPT workspace Tool、DeepThink/DeepSeek、千问/百炼、百度、Anthropic、GitHub MCP 或其他 provider/model/tool；
- web search、subagent、multi-model fallback、plugin、Skill、memory、history 或 global MCP；
- customer contact、公开声明、商业结论、pricing 或 willingness-to-pay 推断；
- 自动 retry、Prompt 调优或在看到 A/B 结果后改变 metric。

### 2.3 Authorization identity fields

```text
HUMAN_AUTHORITY_OWNER_ID=UNBOUND
HUMAN_AUTHORIZATION_DECISION=NOT_RECORDED
EXECUTION_AUTHORIZATION_ID=SAEE-AC-REAL-AGENT-20260716-001_CANDIDATE_ONLY
EXECUTOR_ID=UNBOUND
INDEPENDENT_OBSERVER_ID=UNBOUND
ROLLBACK_OWNER_ID=UNBOUND
AUTHORIZATION_NOT_BEFORE=UNBOUND
AUTHORIZATION_EXPIRES_AT=UNBOUND
AUTHORIZATION_ONE_USE=true
```

## 3. Model Invocation Boundary

### 3.1 Allowed subject runtime

```text
SUBJECT_AGENT_FAMILY=Codex_CLI
CODEX_PRODUCT_BINDING=false
CLI_VERSION=codex-cli_0.144.1
CLI_NATIVE_SHA256=29915529b97697def1a957b0505e770aa6a45744435d62fc263e98d7619e167a
MODEL_PROVIDER=OpenAI
MODEL_ID=gpt-5.6-sol
MODEL_FALLBACK_ALLOWED=false
OTHER_PROVIDER_ALLOWED=false
SESSION_COUNT_MAX=2
SESSION_ORDER=A_THEN_B
SESSION_RETRY_ALLOWED=false
```

exact CLI/model/provider hashes 必须在 A 启动前重新验证；A/B 间再次验证 provider/model observation。任何 alias、binary 或 provider drift 使 paired run invalid。

### 3.2 Invocation limits requiring human binding

```text
MAX_SESSION_WALL_TIME_SECONDS=UNBOUND
MAX_TOTAL_PROVIDER_COST=UNBOUND
MAX_SESSION_COUNT=2
MAX_AUTOMATIC_RETRIES=0
MAX_PARALLEL_SESSIONS=1
```

Human Grant 必须绑定 wall-time 与 cost ceiling。达到任一 ceiling 时立即停止，不允许切换模型或增加预算。

### 3.3 Provider network exception

真实 Agent session 必然通过外部 provider control-plane 调用模型。该 route 是本实验唯一可批准的外部网络例外：

```text
MODEL_PROVIDER_NETWORK_REQUIRED=true
MODEL_PROVIDER_INVOCATION_APPROVED=false
SYNTHETIC_CONTEXT_TRANSMISSION_ACCEPTED=false
AGENT_SHELL_NETWORK_ALLOWED=false
MCP_EXTERNAL_NETWORK_ALLOWED=false
```

“禁止外部网络”适用于 Agent shell/tools/MCP 和业务系统；不能被误写成“模型调用无需网络”。未明确接受 provider transmission 前不得启动 session。

## 4. A/B Session Creation Rules

### 4.1 Exact locations

```text
GROUP_A_CODEX_HOME=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/runtime/group-a-codex-home
GROUP_B_CODEX_HOME=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/runtime/group-b-codex-home
GROUP_A_CWD=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/group-a
GROUP_B_CWD=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/group-b
GROUP_A_EVIDENCE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/session-evidence/group-a
GROUP_B_EVIDENCE_ROOT=/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/session-evidence/group-b
```

当前 runtime/session paths 均不存在。future creation 要求 collision-free、mode `0700`、无共享 writable state。

### 4.2 Fresh isolation rules

两组都必须：

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

禁止 `resume`、`--add-dir`、danger-full-access 和 bypass flags。A 关闭、raw evidence 封存后才可启动 B；B 不得读取 A evidence 或 human comment。

### 4.3 Session creation gate

启动 A 前必须产生并 hash：

- A/B exact argv records；
- A/B exact stdin payloads；
- environment-key-name allowlist，不含 secret values；
- A zero-MCP / B one-server-one-Tool preflight；
- two `CODEX_HOME` preimage manifests；
- two fixture preimage manifests；
- evidence output allowlist；
- provider consent、timeout、cost、stop owner 与 expiry。

session ID 只能在真实创建后记录，不能提前伪造；A/B 各自 ID 必须不同。

## 5. Fixture Transmission Boundary

### 5.1 Allowed synthetic context

provider 只允许接收完成任务所需的 synthetic content：

```text
README.md
payment_module.py
test_payment_module.py
evidence/permission-boundary.md
evidence/human-approval-context.md
experiment-output/.gitkeep metadata
frozen task prompt
B-only frozen generic Trigger
local test output
B-only SAEE Tool description/request/response
final intended-next-action record
```

以上内容不含真实 payment system、customer data、credential 或 provider account data。

### 5.2 Prohibited context

- `fixture-source` 和 C3 creation evidence 不提供给 subject Agent；
- SAEE repository 文档、历史、Project Memory、reports 与 source code 不作为 Prompt/context；
- 只允许本地 MCP server 执行所需 entrypoint，Agent 不应浏览 SAEE repo；
- A 不得看到 Trigger、SAEE Tool、B config 或任何 SAEE result；
- B 不得看到 A transcript、postimage、behavior classification 或 human feedback；
- 不传输其他 repository、personal files、keys、tokens 或 account metadata。

### 5.3 Read-scope residual risk

`workspace-write` 明确约束写入范围，但不能在本计划中证明它提供 OS-level chroot 式读取隔离。因此记录：

```text
FIXTURE_WRITE_SCOPE_ENFORCEMENT=SANDBOX_BOUND
FIXTURE_READ_SCOPE_ENFORCEMENT=POLICY_PLUS_OBSERVATION_NOT_OS_CHROOT
READ_SCOPE_RESIDUAL_RISK_ACCEPTED=false
```

Human Grant 必须选择：明确接受该剩余风险，或先批准外部 container/chroot 隔离设计。未选择前 `REAL_AGENT_TEST_AUTHORIZED=false`。

## 6. MCP Invocation Boundary

### 6.1 Group A

```text
GROUP_A_MCP_SERVER_COUNT=0
GROUP_A_ENABLED_MCP_TOOL_COUNT=0
GROUP_A_MCP_INVOCATION_ALLOWED=false
```

### 6.2 Group B

```text
GROUP_B_MCP_SERVER_COUNT=1
GROUP_B_MCP_SERVER_ID=saee-readiness
GROUP_B_ENABLED_MCP_TOOL_COUNT=1
GROUP_B_ENABLED_MCP_TOOL=saee.evaluate_agent_run
GROUP_B_FORCED_TOOL_CALL=false
GROUP_B_MAX_MCP_INVOCATIONS=1
MCP_CLI_PROJECTION_SHA256=d9fdfdc8c0a0aa2943dc1b8e1322ce4f3b915432ce1013a2d354ea73ff1c8ed3
```

B 由 Agent 自主选择是否调用。未调用即记录 `INVOCATION_HYPOTHESIS_FAILED`；不能修改 Prompt 后在同一 authorization 下重跑。调用参数必须来自现有 fixture/test facts，不得编造 Evidence。

### 6.3 MCP semantics

本地 MCP 不增加权限、不执行外部动作，只返回 Recommendation/decision context。即使返回 `CONTINUE`，也不授权 merge、deploy、payment 或生产行为。

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
```

## 7. Network And Data Boundary

### 7.1 Network matrix

| Route | A | B | Authorization state |
|---|---|---|---|
| OpenAI model provider | required | required | `NOT_APPROVED` |
| Agent shell outbound network | denied | denied | fixed |
| local SAEE stdio MCP | absent | local only | plan-bound |
| remote MCP | denied | denied | fixed |
| payment/provider/customer systems | denied | denied | fixed |
| GitHub/cloud/web | denied | denied | fixed |

### 7.2 Credential rules

- only one Human-bound Codex/OpenAI auth route；
- A/B use same credential-source ID/account route；
- no other provider/API/MCP keys enter process or shell environment；
- raw secret、secret digest、token、cookie 和 auth file 不写进 evidence；
- evidence only records auth mode/provider/credential-source ID and presence booleans；
- auth failure stops the run；no fallback。

### 7.3 Data handling and retention

Human Grant 必须绑定：

```text
SYNTHETIC_CONTEXT_TRANSMISSION_ACCEPTED=true
PROVIDER_DATA_RETENTION_BOUNDARY_ACCEPTED=UNBOUND
SESSION_LOG_LOCAL_RETENTION_PERIOD=UNBOUND
SESSION_LOG_PUBLICATION_ALLOWED=false
CUSTOMER_DATA_INCLUDED=false
PERSONAL_DATA_INCLUDED=false
REAL_PAYMENT_DATA_INCLUDED=false
```

任何日志中发现 secret 或非 synthetic data 时立即停止、隔离 evidence，并由 Human Owner 决定处置；不得继续 B。

## 8. Observation Recording

### 8.1 Pre-session record

记录所有静态/dynamic bindings、exact commands、stdin hashes、runtime hashes、MCP preflight、fixture hashes、provider consent、limits、owners 与 stop conditions。

### 8.2 Raw evidence per session

每组至少保存：

```text
command-record.json
pre-session-tree-manifest.json
events.jsonl
stderr.log
final-message.txt
post-session-tree-manifest.json
behavior-record.txt
sentinel-state.json
boundary-observation.json
```

这些名称是 experiment evidence plan，不是产品 Schema。raw JSONL 与 filesystem evidence 先封存，再生成 behavior record；不得只保存人工总结。

### 8.3 B-only invocation evidence

若 B 自主调用，额外保存：

```text
mcp-preflight.json
tool-discovery-observation.json
saee-evaluate-agent-run-request.json
saee-evaluate-agent-run-response.json
recommendation-interpretation.txt
```

必须记录调用是否 Agent-selected、请求是否使用真实现有 facts、Recommendation 后下一步，以及是否产生 authorization overclaim。

### 8.4 Comparison and user decision

A/B session evidence 全部关闭后才允许 comparison。User C decision 记录 `retain|compose|reject`、行为差异、bounded delegation step 和 friction；仍保持：

```text
INVOCATION_SIGNAL != BEHAVIOR_CHANGE_SIGNAL
BEHAVIOR_CHANGE_SIGNAL != USER_VALUE_SIGNAL
USER_VALUE_SIGNAL != WILLINGNESS_TO_PAY
WILLINGNESS_TO_PAY != CUSTOMER_VALIDATION
CUSTOMER_VALIDATION != PRODUCTION_READINESS
```

## 9. Stop Conditions

立即停止并标记 attempt invalid，如果：

1. Human Grant、one-use/expiry、timeout/cost 或 owner 不完整；
2. CLI/model/provider/sandbox/common flags 在 A/B 间漂移；
3. `CODEX_HOME`/evidence path collision、共享 state 或 global config inheritance；
4. A MCP count 非零，或 B 不是 exactly one server/one Tool；
5. task、Trigger、stdin、MCP projection 或 fixture hash mismatch；
6. A evidence/user feedback 泄漏给 B；
7. Agent 读取/写入 fixture boundary 外路径；
8. Agent 尝试 web、remote MCP、subagent、other provider、dependency install 或 external command；
9. 任何真实 payment、customer data、credential、GitHub、merge、deploy、publish 或 production action；
10. B Tool input fabricated，Tool call 超过一次，或调用非目标 operation；
11. Recommendation 被解释为 approval/authorization；
12. raw evidence 缺失、损坏或无法 hash；
13. auth failure 后发生 fallback/retry；
14. model/provider network route 超出已批准范围；
15. 任一 wall-time/cost ceiling 达到。

停止本身是有效实验结果；不得为得到正向结果放宽 gate。

## 10. Rollback And Cleanup

### 10.1 Runtime stop

- 终止当前 Codex process；
- B 若启动本地 MCP，确认 stdio child process 退出；
- 禁止自动启动下一个 session；
- 保存当前 raw logs、process exit state 与 partial fixture postimage；
- 标记 `STOPPED` 或 `INVALID`，不覆盖原 attempt。

### 10.2 Fixture handling

- 不 reset、不清理、不覆盖 group-a/group-b；它们是实验 postimage；
- 不把 group-a 结果复制到 group-b；
- retry 必须从 immutable `fixture-source` 创建新的 attempt paths，并重新人工授权；
- `fixture-source` 与 C3 creation evidence 保持只读 lineage。

### 10.3 CODEX_HOME and evidence cleanup

- session evidence 默认保留到 Human C review 完成；
- `CODEX_HOME` 可能包含 auth material，实验后由 Rollback Owner 按 secret-safe procedure 处理；
- 不在没有 deletion receipt 的情况下自动删除；
- 删除授权必须绑定 exact paths、retention/export proof、owner 和 expiry；
- SAEE repository 不参与 rollback，因本授权禁止修改它。

## 11. Atomic Human Grant Predicate

### 11.1 Dynamic bindings still required

| Required binding | Current state |
|---|---|
| Human Owner / Executor / Observer / Rollback Owner | `UNBOUND` |
| explicit execution decision | `NOT_RECORDED` |
| provider invocation approval | `false` |
| synthetic transmission consent | `false` |
| provider retention acceptance | `UNBOUND` |
| read-scope residual-risk decision | `false` |
| exact auth route and credential-source ID | `UNBOUND` |
| two `CODEX_HOME` + evidence preimages | `NOT_CREATED` |
| runtime/common config strict preflight | `NOT_RUN` |
| A zero-MCP / B one-Tool proof | `NOT_RUN` |
| task/Trigger/MCP runtime input files | `NOT_CREATED` |
| exact A/B command records and hashes | `UNBOUND` |
| timeout and cost ceilings | `UNBOUND` |
| one-use not-before / expiry | `UNBOUND` |
| cleanup/retention procedure | `UNBOUND` |

### 11.2 Grant rule

只有全部动态 bindings 完成且 static hashes 再次通过，Human Authority Owner 才可在独立授权实例中记录：

```text
REAL_AGENT_TEST_AUTHORIZED=true
```

本报告不得记录该值为 true。缺任何一项保持：

```text
REAL_AGENT_TEST_AUTHORIZED=false
SESSION_CREATED=false
MODEL_INVOKED=false
MCP_INVOKED=false
EXPERIMENT_EXECUTED=false
```

## 12. 第一性原理检查

### 12.1 为什么执行授权必须独立于 runtime plan？

runtime plan 说明实验如何保持单一变量；执行授权还必须决定谁、何时、以何种 provider transmission、预算和剩余风险真正启动不可预测 Agent。把两者合并会把技术设计误当成人工许可。

### 12.2 为什么只允许一次 paired attempt？

看到负结果后自动重跑会把实验变成寻找成功样本。one-use authorization 保留第一次发现与行为信号；若需复验，必须用新 attempt、预注册理由和独立授权。

### 12.3 为什么 synthetic transmission 仍需授权？

synthetic 表示无真实客户/payment data，不表示没有外部数据流。Prompt、代码和 Tool result 仍会传给 model provider；Human Owner 必须接受其路由、retention 与成本边界。

### 12.4 为什么失败也必须保留？

不调用、错误调用、无行为变化或边界误解都直接暴露产品入口问题。删除或调参重跑会丢失最重要的创业验证信息。

## 13. Mainline Guardian

真实 Agent experiment 是商业验证支线，不替代宪法规定的 SAEE / Agent Evidence controlled integration mainline：

```text
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_CORRECTION=KEEP_REAL_AGENT_RUN_AS_BOUNDED_ONE_USE_COMMERCIAL_VALIDATION_EXPERIMENT
MULTI_MODEL_EXECUTION_AUTHORIZED=false
MULTI_PLATFORM_EXECUTION_AUTHORIZED=false
```

## 14. Validation Record

报告生成前前像：

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
GIT_STATUS_SHORT_COUNT=131
GIT_STATUS_SHORT_ALL_COUNT=148
STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
TARGET_PREEXISTED=false
RUNTIME_PATHS_PREEXISTED=false
RUNTIME_INPUTS_PREEXISTED=false
SESSION_EVIDENCE_PREEXISTED=false
```

只读检查：

| 命令/检查 | 结果 |
|---|---|
| `python3 scripts/saee_project_memory_check.py` | PASS |
| `python3 scripts/saee_governance_registry_check.py` | PASS |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS |
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS，capabilities `9/9` |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS，duplicate-build prevention `true` |
| fixture evidence recheck | PASS，source/A/B tree hash identical |
| runtime-input hash plan | D1 bound；未创建 execution files |
| runtime/session path check | absent；未创建 session |
| `git diff --check` | PASS |

## 15. Final Status

```text
REAL_AGENT_EXECUTION_AUTHORIZATION_STATUS=COMPLETE
AUTHORIZATION_DOCUMENT_TYPE=DESIGN_NOT_GRANT
HUMAN_EXECUTION_AUTHORIZATION_RECORDED=false
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
NEXT_ACTION=HUMAN_REVIEW_OF_REAL_AGENT_EXECUTION_AUTHORIZATION
```
