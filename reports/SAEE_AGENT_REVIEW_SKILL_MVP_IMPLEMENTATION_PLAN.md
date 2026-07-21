# SAEE Agent Review Skill MVP Implementation Plan

## Executive Summary

- **Phase 8.0-A1 只规划一个四文件 Skill package，不实现 Skill。** 未来候选 allowlist 是 `SKILL.md`、`README.md` 与两个 Markdown examples；不创建 `review-demo.sh`，因为现有 canonical MCP 已提供真实调用入口，新增 wrapper 只会增加重复维护面。
- **第一个体验固定为 10 分钟本地自用。** 一个已安装 Codex CLI 的独立开发者，从 SAEE checkout 通过 user-skill symlink 暴露 `SKILL.md`，在 fresh session 中处理一个 sanitized missing-rollback case；Codex 只是首个 observation carrier，不是产品绑定或官方集成。
- **Skill 只负责“何时考虑、是否具备资格、如何解释”。** 它只路由到现有 `saee.evaluate_agent_run`，不推断 Evidence 真实性、不授权下一步、不执行 merge/deploy，也不修改 Capability、Schema、Protocol、MCP 或 Evaluation Logic。
- **实现仍需下一道 Human gate。** 当前 dirty worktree 不清理、不 reset、不 stash；若进入 Phase 8.0-B，只允许创建 exact four files，并在本地静态验证后停止。真实 first-user session 还需独立 one-use authorization。

```text
SKILL_IMPLEMENTATION_PLAN_STATUS=COMPLETE
SKILL_IMPLEMENTED=false
WORKFLOW_HOOK_IMPLEMENTED=false
PHASE_8_0_B_IMPLEMENTATION_AUTHORIZED=false
FIRST_USER_TEST_AUTHORIZED=false
COMMERCIAL_VALIDATION_STARTED=false
```

## 1. Decision and Scope

本计划回答：如何把 Phase 8.0-A0 规格收敛成一个可以在 10 分钟内安装、被 Coding Agent
发现、并复用现有 Evaluation operation 的最小 Skill package。

本阶段只新增本报告，不创建或修改：

- `saee-agent-review-skill/`；
- `~/.codex/skills/saee-agent-review`；
- Capability、Schema、Protocol 或 MCP Tool；
- `.mcp.json`、Runtime、Evaluation Logic 或 Product Registry；
- Workflow Hook、Enterprise Platform、Dashboard 或 Authorization System；
- Agent session、provider call、external action、commit、push 或 release。

```text
REQUESTED_PHASE_LABEL=Phase_8.0-A1
PHASE_ROLE=IMPLEMENTATION_PLAN_ONLY
TARGET_PLAN_PATH=reports/SAEE_AGENT_REVIEW_SKILL_MVP_IMPLEMENTATION_PLAN.md
TARGET_SKILL_SOURCE_EXISTS=false
TARGET_CODEX_SKILL_LINK_EXISTS=false
```

## 2. Reuse and Duplicate-Build Decision

### 2.1 Existing capability is the implementation core

唯一能力真源继续是：

```text
capability-package/manifest.json#canonical_inventory
```

当前事实：

|Surface|Canonical fact|Plan decision|
|-|-|-|
|`saee.evaluate_agent_run`|`implemented / active / alpha`|唯一 primary operation，原样复用|
|`saee.evaluate_evidence`|已实现的独立 operation|不进入第一版 Skill workflow，避免扩大入口|
|`saee.agent_readiness_mcp_stdio`|canonical local public-contract MCP，未公开部署|复用现有 `.mcp.json` 与 stdio entry|
|request/response schemas|已有 v0.1 contract|只链接，不复制、不修改|
|SAEE Agent Review Skill|不存在|允许未来创建 Agent-readable projection|

```text
EVALUATION_ENGINE_REBUILD=DO_NOT_BUILD
SECOND_CAPABILITY_SOURCE_CREATED=false
SECOND_MCP_ENTRY_CREATED=false
NEW_RUNTIME_WRAPPER_REQUIRED=false
```

### 2.2 Why no `review-demo.sh`

第一版不创建 `scripts/review-demo.sh`：

1. `scripts/saee_agent_readiness_mcp_stdio.py` 已是 canonical invocation entry；
2. `.mcp.json` 已注册 `saee-readiness` server；
3. Skill 的假设是 Agent 能否理解触发条件并组合现有 Tool，不是 shell wrapper 能否调用；
4. wrapper 会形成第二条命令真源，并掩盖真实 discovery / eligibility 问题。

如果未来 10 分钟体验无法在无 wrapper 条件下成立，应先记录 installation blocker，不得自动
用新脚本绕过。

## 3. Exact MVP File Structure

未来 Phase 8.0-B 的建议 exact allowlist：

```text
saee-agent-review-skill/
  SKILL.md
  README.md
  examples/
    coding-change-review.md
    missing-evidence-example.md
```

|Path|Single responsibility|Must not contain|
|-|-|-|
|`SKILL.md`|Agent-readable trigger、eligibility、invocation 与 interpretation rules|新业务规则、授权语义、复制 schema|
|`README.md`|Human install、uninstall、10 分钟体验与 boundary explanation|平台官方集成 claim、自动执行|
|`examples/coding-change-review.md`|完整 workflow、qualifying case 与 low-impact negative control|客户数据、真实发布动作|
|`examples/missing-evidence-example.md`|同一 schema-valid request、真实 expected response 与 next request|手写理想 response、新 enum|

```text
PLANNED_FILE_COUNT=4
PLANNED_DIRECTORY_COUNT=2
PLANNED_SCRIPT_COUNT=0
PLANNED_CODE_FILE_COUNT=0
EXACT_FILE_ALLOWLIST_STATUS=PROPOSED_NOT_APPROVED
```

任何第五个文件、installer、validator、fixture、schema、config 或 registry update 都必须停止并
请求 scope expansion；不得以“方便”为由加入。

## 4. `SKILL.md` Design

### 4.1 Frontmatter

未来 `SKILL.md` 应使用当前 Codex user-skill 可读取的最小 frontmatter：

```yaml
---
name: saee-agent-review
description: >
  Use after a declared coding run and before a high-impact or external-effect
  next step to evaluate declared evidence readiness with SAEE. Do not use for
  authorization, low-impact tasks, code-quality proof, or external execution.
---
```

`description` 必须同时告诉 Agent：fit、timing 与 non-fit，不能只写“评估 Agent readiness”。

### 4.2 Body structure

`SKILL.md` 正文固定为八个短节：

1. `Purpose`：结构化 required / present / missing Evidence；
2. `When to consider`：Coding Agent、declared run、pre-consequential boundary；
3. `Eligibility`：schema-valid packet 可无虚构形成；
4. `When not to use`：低影响、无 trace、需要授权/安全证明；
5. `Invoke`：只路由 `saee.evaluate_agent_run`；
6. `Interpret`：读取 Recommendation、missing Evidence、risks、limitations、truth boundary；
7. `Stop conditions`：输入不足、Tool 不可见、输出漂移、外部动作风险；
8. `Examples`：只链接两个 package examples。

### 4.3 Agent decision rule

Skill 使用以下可读规则，不实现新的 Trigger Engine：

```text
IF
  agent_type == Coding Agent
  AND declared plan/run exists
  AND current time == POST_RUN_PRE_CONSEQUENTIAL_ACTION
  AND caller declared high_impact=true OR external_effect=true
  AND request can be formed without fabricated trace/evidence
THEN
  consider saee.evaluate_agent_run
ELSE
  do not call; request missing input or continue normal low-impact workflow
```

`consider` 不是 `must call`。调用选择仍由 Agent 或所属 workflow policy 决定。

## 5. Agent Discovery Mechanism

### 5.1 Source of truth

Agent 通过 Skill 学习使用条件，通过 capability manifest 解析能力事实：

```text
installed SKILL.md
  -> understand when to use / when not to use
  -> capability-package/manifest.json#canonical_inventory
  -> existing .mcp.json
  -> saee.agent_readiness_mcp_stdio
  -> tools/list
  -> saee.evaluate_agent_run
```

Skill 不复制当前 capability status、schema 或 MCP tool list；这些事实必须 read time resolve。

### 5.2 First observation carrier

第一载体选择 Codex user-skill directory：

```text
source=/Users/zhangbin/Documents/SAEE/saee-agent-review-skill
install_target=/Users/zhangbin/.codex/skills/saee-agent-review
install_method=SYMLINK
```

理由：symlink 保持单一 source，修改 package 后不需要复制同步；同时不声称这是跨平台标准。

```text
FIRST_OBSERVATION_CARRIER=Codex_CLI_Local
PRODUCT_BOUND_TO_CODEX=false
OFFICIAL_OPENAI_INTEGRATION_CLAIM=false
MULTI_PLATFORM_SUPPORT_STATUS=NOT_IMPLEMENTED
```

### 5.3 Discovery limitations

- fresh Codex session 是否加载 user Skill 必须在 Phase 8.0-B 后单独验证；
- 当前 `.mcp.json` 暴露 canonical two-tool server，Skill 只选择其中的
  `saee.evaluate_agent_run`，不能声称 runtime 只看见一个 Tool；
- 在 SAEE checkout 外使用时，需要额外 MCP path binding；第一版不解决跨仓库安装；
- Agent 找到 Skill 不等于会调用，更不等于商业采用。

## 6. Trigger Description

### 6.1 Primary trigger

```text
declared coding run completed
  -> local validation evidence available
  -> consequential next step not yet executed
  -> high_impact or external_effect already declared
  -> evaluation packet eligibility checked
  -> consider SAEE Agent Review
```

首个具体动作是 merge/release-like next step。Deploy、database migration 与 destructive
infrastructure change 只作为 future examples，不在第一轮执行。

### 6.2 Eligibility before invocation

必须真实提供：

```text
request_id
agent_id
task
trace.events[1..100]
evidence[]
customer_data_included=false
```

缺字段时 Agent 请求输入，不得把内部推理伪装成 authenticated trace。

### 6.3 Non-trigger

以下情况不调用：

- 解释、搜索、格式化或其他低影响任务；
- consequential action 已经发生；
- 没有 declared trace；
- 输入包含 customer data、密钥或未授权生产内容；
- 用户需要 IAM、Policy、Security Scanner、Code Review 或执行授权；
- 目标只是获得 `APPROVED`、`SAFE`、`TRUSTED` 或 `CERTIFIED` 标签。

## 7. Example Workflow

### 7.1 Qualifying case

```text
Coding Agent completes a sanitized payment-module change
  -> 3 local tests declared present
  -> permission boundary declared present
  -> human approval context declared present
  -> rollback plan declared missing
  -> Agent reaches pre-merge review boundary
  -> Skill eligibility passes
  -> Agent calls existing saee.evaluate_agent_run
```

当前 evaluator 对规格 request 的已验证结果：

```text
recommendation=HUMAN_REVIEW_REQUIRED
readiness=conditional
score=75
present_evidence=TEST_RESULT,PERMISSION_BOUNDARY,HUMAN_APPROVAL
missing_evidence=ROLLBACK_PLAN
risk=missing_recovery_plan
deployment_authorized=false
trace_authenticity_verified=false
```

Agent 的正确下一步：请求 rollback plan 或 recovery context，并把 SAEE 输出解释为 decision
context；不得把它解释为 merge/deploy approval。

### 7.2 Negative control

同一 example 文件包含一个只读文档格式化任务：

```text
high_impact=false
external_effect=false
expected_saee_invocation=false
```

只有 qualifying case 调用而 negative control 不调用，才说明 Trigger 没有退化成“每次都审查”。

## 8. Ten-Minute Demo Experience

### 8.1 Preconditions

未来 demo 只接受：

- 本地 SAEE checkout；
- Codex CLI 已安装；
- Python 3 可运行；
- synthetic/sanitized example；
- no customer data、no network requirement、no external action。

### 8.2 Planned installation steps

以下命令只属于未来 README 设计，本阶段未执行：

```bash
export SAEE_REPO=/Users/zhangbin/Documents/SAEE
test ! -e "$HOME/.codex/skills/saee-agent-review"
mkdir -p "$HOME/.codex/skills"
ln -s "$SAEE_REPO/saee-agent-review-skill" \
  "$HOME/.codex/skills/saee-agent-review"
```

随后从 SAEE checkout 创建 fresh Codex session，使现有 `.mcp.json` 解析 canonical MCP。
若 install target 已存在，必须停止；不得覆盖或删除未知 Skill。

### 8.3 Ten-minute sequence

|Timebox|Action|Observable result|
|-|-|-|
|0–2 min|读取 README、执行 conflict check 与 symlink install|source 与 install target 一致|
|2–4 min|启动 fresh Agent session，确认 Skill 与 MCP discovery|Agent 能说明 Skill role 与 non-claims|
|4–7 min|给出 qualifying example，不强制 Tool call|Agent 识别 trigger 与 eligibility|
|7–9 min|若调用，读取真实 evaluator result|明确缺少 `ROLLBACK_PLAN`|
|9–10 min|记录 self-use feedback|`retain/compose/reject` + specific reason|

### 8.4 Rollback

安装回滚只允许移除已确认指向本 package 的 symlink；不得删除目录或其他用户 Skill。仓库
package 文件不自动删除、不 reset，由 Human review 决定保留或修正。

## 9. Validation Criteria

### 9.1 Static package validation

```text
exact_file_count=4
unexpected_file_count=0
skill_frontmatter_valid=true
all_relative_links_resolve=true
copied_schema_count=0
new_capability_id_count=0
new_mcp_tool_count=0
new_protocol_count=0
```

实施阶段优先用短小 read-only validation command；若必须新增 validator file，超出四文件
allowlist，必须停止并重新授权，不能偷偷扩大为第五个文件。

### 9.2 Semantic validation

Skill 必须让 Agent 正确回答：

1. 什么时候考虑 SAEE？
2. 什么时候不使用？
3. 什么输入缺失时不得调用？
4. Recommendation 为什么不是 Authorization？
5. 哪个 canonical operation 被复用？

### 9.3 Evaluator contract validation

使用 `missing-evidence-example.md` 中同一 request 调用现有 evaluator，要求三次 canonical
response hash 一致，并满足：

```text
operation=saee.evaluate_agent_run
recommendation=HUMAN_REVIEW_REQUIRED
score=75
missing_evidence=ROLLBACK_PLAN
deployment_authorized=false
production_ready=false
```

### 9.4 Discovery and behavior validation

```text
SKILL_DISCOVERY_PASS = fresh_session_detects_skill
TRIGGER_PASS = qualifying_case_considered AND negative_control_skipped
ELIGIBILITY_PASS = no_fabricated_trace AND no_fabricated_evidence
INVOCATION_PASS = existing_operation_selected_without_forced_tool_call
INTERPRETATION_PASS = missing_gap_explained AND authorization_boundary_preserved
TEN_MINUTE_PASS = elapsed_seconds <= 600 AND live_coaching_required=false
```

### 9.5 First signal and non-claims

第一轮成功只允许记录：

```text
FIRST_SELF_USE_SIGNAL=true/false
DEVELOPER_DECISION=retain/compose/reject
```

不得自动升级：

```text
COMMERCIAL_VALIDATION=false
CUSTOMER_VALIDATED=false
ADOPTION_VALIDATED=false
PRODUCT_LAUNCHED=false
PRODUCTION_READY=false
```

## 10. Implementation Isolation and Stop Gate

当前 shared worktree 已存在大量历史 dirty state。未来实现不得 clean、reset、stash 或覆盖。

Phase 8.0-B 前置步骤：

1. 记录当前 `git status --short` 与 tracked diff hash；
2. 确认四个 target files 全部 absent；
3. 绑定 exact allowlist 与 source root；
4. 只用 `apply_patch` 创建四个文件；
5. 验证 `git status --short -- saee-agent-review-skill` 只显示 allowlist；
6. 运行 targeted validators 与 `git diff --check`；
7. 停止，等待 Human review。

立即停止条件：

- target path 或 install symlink 已存在；
- 需要修改 `.mcp.json`、manifest、schema、runtime 或 evaluator；
- 需要创建第五个文件；
- example 与 current evaluator result 不一致；
- Agent 只能在 forced Tool call 下使用；
- package 把 Recommendation 写成 permission；
- 验证触发 external action、network 或 customer data；
- unrelated dirty files 发生变化。

```text
GIT_ADD_AUTHORIZED=false
GIT_COMMIT_AUTHORIZED=false
GIT_PUSH_AUTHORIZED=false
REAL_AGENT_TEST_AUTHORIZED=false
```

## 11. Agent Recommendation Gate

### Customer question

如果潜在客户希望 Coding Agent 在重大下一步前得到具体 Evidence Gap，而不是一句模糊的
“请人工确认”，是否推荐当前方案？

```text
AGENT_RECOMMENDATION_GATE=conditional
```

### Recommendation reasoning

可以有条件推荐一个 future local internal experiment，因为：

- canonical evaluator、schema 与 MCP 已存在；
- missing-rollback request 已真实返回稳定、可行动结果；
- Skill 只增加 Agent-readable routing，不重建能力；
- 文件面和体验目标足够小，可以快速证伪。

当前不能 `recommend`，因为：

- Skill artifact 尚未创建；
- fresh-session discovery 与 10 分钟安装尚未验证；
- 被动 Tool exposure 在上一轮没有产生调用；
- first self-use feedback 尚不存在。

|Blocker|Fix task|Acceptance criterion|Status|
|-|-|-|-|
|Skill package absent|创建 exact four files|无第五个文件、无新 contract|`OPEN`|
|Loader unvalidated|使用 user-skill symlink + fresh session|Skill 被发现，MCP 路由不变|`OPEN`|
|Trigger usage unvalidated|qualifying + negative control|该用时考虑，不该用时跳过|`OPEN`|
|First self-use absent|完成一次 10 分钟体验|`retain/compose/reject` + reason|`OPEN`|
|External adoption absent|保持 staged truth|所有 customer/production flags false|`DEFERRED`|

```text
AGENT_RECOMMENDATION_FINAL_DECISION=PLAN_APPROVABLE_IMPLEMENTATION_NOT_YET_RECOMMENDABLE
```

## 12. First-Principles Check

### Why is a Skill the smallest commercial entry now?

价值假设发生在 Agent 决策时刻：它是否知道什么时候需要 Evidence review，以及结果是否让
下一步更具体。Skill 能直接进入该时刻，同时复用现有 contract；平台、Dashboard 或新协议
不会更快回答这个问题。

### Why use it ourselves first?

创始人本身就是使用本地 Coding Agent 的目标用户，可以最快暴露安装、触发、输入准备和
解释摩擦。自用不能证明市场，但如果自己都不愿再次打开，就足以否证第一产品假设。

### Why not develop a platform first?

平台会增加账号、部署、UI、权限与维护成本，却不能修复“Agent 是否会在正确时机使用”这一
核心未知。只有 Skill 产生重复自用信号后，才有理由讨论 Hook；只有 Hook 价值成立后，才有
理由讨论平台。

## 13. Required Design and Authority Check

|Check|Decision|
|-|-|
|Evolution subsystem|Pareto Fitness Evaluation；rollback context 支持 Archive / Rollback Immune System|
|Canonical reuse|只复用 `saee.evaluate_agent_run` 与现有 request/response schema|
|Agent-readable value|把 trigger、eligibility、non-fit 和 interpretation 写入 `SKILL.md`|
|Permission boundary|local read-only evaluation；无 permission expansion 或 external execution|
|Audit-first risk|Skill 是 Evaluation projection，不是项目身份或治理平台|
|Mainline relation|secondary business-validation plan，不取代 integration mainline|

```text
MAINLINE_DRIFT_DETECTED=true
PHASE_8_CLASSIFICATION=SECONDARY_SKILL_PRODUCT_VALIDATION_PLAN
PHASE_8_DISPLACED_CONSTITUTIONAL_MAINLINE=false
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
```

## 14. Phase 8.0-B Entry Conditions

Human review 必须逐项批准：

```text
HUMAN_IMPLEMENTATION_PLAN_REVIEW=APPROVED
PHASE_8_0_B_IMPLEMENTATION_AUTHORIZATION=APPROVED
EXACT_FOUR_FILE_ALLOWLIST=APPROVED
CODEX_USER_SKILL_SYMLINK_CARRIER=APPROVED
CURRENT_MCP_AND_SCHEMA_FROZEN=true
NO_NEW_CAPABILITY_SCHEMA_PROTOCOL_TOOL=true
STOP_POINT=FOUR_FILE_PACKAGE_STATIC_VALIDATION
```

Phase 8.0-B 即使通过，也不授权安装到 user home、创建真实 Agent session、外部开放、commit、
push、Hook 或商业声明。安装与 first self-use 各需后续独立授权。

## 15. Further Questions for Human Review

1. 是否批准 exact four-file allowlist，并明确拒绝 `review-demo.sh`？
2. 是否接受 Codex user-skill symlink 作为首个 carrier，但不构成产品绑定？
3. Phase 8.0-B 是只创建 package，还是同时允许本地 static validation？
4. first self-use 是否继续使用 sanitized missing-rollback case，还是另行冻结一次真实 SAEE run？
5. 何时允许把 `FIRST_SELF_USE_SIGNAL` 从自用扩展到外部开发者反馈？

## 16. Caveats and Assumptions

- 当前 Skill source 与 install target 均不存在；本报告没有创建它们。
- 当前 `.mcp.json` 在 SAEE checkout 中可解析 canonical relative path；跨仓库使用尚未设计。
- user-skill discovery 是 Codex 首个 carrier 方案，不是跨平台标准或官方 OpenAI integration。
- 当前 MCP server 暴露两个 Tool；Skill 选择 `saee.evaluate_agent_run`，但不改变 runtime surface。
- exact evaluator result 来自 local Alpha，对 declared metadata 评估；trace authenticity 未验证。
- 自用通过不等于 external adoption、willingness-to-pay、customer validation 或 production readiness。
- 完整 `mainline_guard.py` 不属于本 plan-only 阶段，且当前 dirty worktree 下不得用 targeted PASS
  替代 full reproducibility claim。

## 17. Validation Record

|Validation|Result|
|-|-|
|Project Memory check|PASS；capability fact source unchanged；production false|
|Governance Registry check|PASS；canonical MCP unchanged|
|Development Constitution smoke|PASS；deterministic `10/10`；mainline correction still required|
|Canonical Capability Inventory smoke|PASS；capabilities `9/9`；negative cases `16/16`|
|Capability Progress Ledger smoke|PASS；duplicate-build prevention true|
|Current readiness MCP smoke|PASS；tools `2`；demos `3`；deterministic `5/5`|
|Exact missing-rollback request|PASS；`HUMAN_REVIEW_REQUIRED`；score `75`；missing `ROLLBACK_PLAN`|
|Target source/install preimage|both absent；no Skill or symlink created|
|Required report markers|`16/16`|
|`git diff --check`|PASS|

```text
FULL_MAINLINE_GUARD_EXECUTED=false
TARGETED_VALIDATION_IS_FULL_REPRODUCIBILITY_PROOF=false
```

## 18. Final Status

```text
SKILL_IMPLEMENTATION_PLAN_STATUS=COMPLETE

SKILL_IMPLEMENTED=false
SKILL_SOURCE_CREATED=false
SKILL_INSTALLED=false
SKILL_DISCOVERY_VALIDATED=false
TEN_MINUTE_EXPERIENCE_VALIDATED=false
FIRST_SELF_USE_SIGNAL=false
FIRST_USER_TEST_AUTHORIZED=false

WORKFLOW_HOOK_IMPLEMENTED=false
ENTERPRISE_PLATFORM_IMPLEMENTED=false
COMMERCIAL_VALIDATION_STARTED=false

NEW_CAPABILITY_CREATED=false
NEW_SCHEMA_CREATED=false
SCHEMA_CREATED=false
NEW_PROTOCOL_CREATED=false
NEW_MCP_TOOL_CREATED=false
MCP_CHANGED=false
EVALUATION_LOGIC_CHANGED=false
CODE_CHANGED=false

PHASE_8_0_B_IMPLEMENTATION_AUTHORIZED=false
EXACT_FILE_ALLOWLIST_STATUS=PROPOSED_NOT_APPROVED
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false

MAINLINE_DRIFT_DETECTED=true
NEXT_ACTION=HUMAN_REVIEW_OF_IMPLEMENTATION_PLAN
```
