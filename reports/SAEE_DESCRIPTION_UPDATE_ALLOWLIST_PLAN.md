# SAEE Description Update Allowlist Plan

```text
phase=6.0-F2A
report_type=Description_Update_Allowlist_Preparation
review_mode=PLAN_ONLY_NO_DESCRIPTION_UPDATE
analysis_date=2026-07-15
active_constitution=SAEE Development Constitution v1.1
```

## Executive Decision

Phase 6.0-F2A 已将未来的 Controlled Description Update 收敛为一个 section/field-level
allowlist。本计划不授权修改描述，也不改变任何 capability、schema、MCP contract、runtime
behavior、产品状态或权威。

建议的第一批 core allowlist 只有四个路径：

1. `README.md` — 仅当前顶部 Agent selection boundary、规范 pointer 和当前/历史 front-door
   disposition；
2. `llms.txt` — 仅 startup/current lookup block 和一条错误标为 canonical 的 legacy front-door
   label；
3. `.well-known/saee-capability-index.json` — 仅 current lookup/disposition metadata；保留旧 ID；
4. `saee_backend/services/qianfan_readiness_mcp_adapter.py` — 仅两个 Tool description 字符串和
   initialize boundary instruction 字符串。

`agent-index.json` 虽是必须分析的 Priority File，但结论为 **DENY**：其 capability ledger 已
与 manifest 9/9 对齐，其他区段属于 mixed history；本轮没有 capability fact change，不得修改。
`.mcp.json` 同样为 **DENY**：它的规范启动 route 已正确，且不含 description。

当前工作树不能直接进入 F2B。`llms.txt` 在 F2A 基线前已经 dirty，且改动位于 F2B 候选的
startup block 内。F2B 必须从人工确认的 immutable input 建立 isolated worktree/preimage；
不得在当前 dirty worktree 上叠加修改或用 destructive Git 命令“清理”。

```text
ALLOWLIST_CORE_PATH_COUNT=4
ALLOWLIST_CONDITIONAL_DECISION_COUNT=2
AGENT_INDEX_DISPOSITION=DENY
DOT_MCP_JSON_DISPOSITION=DENY
CURRENT_WORKTREE_F2B_EXECUTION_SAFE=false
F2B_EXECUTION_AUTHORIZED=false
DESCRIPTION_FACT_CHANGE_AUTHORIZED=false
MAINLINE_DRIFT_DETECTED=false
PROGRAM_MAINLINE_CHANGED=false
```

本任务是受控集成主线的 Agent-readable 支撑工作，不替代 SAEE / Agent Evidence Project
integration mainline。Phase 6.0-F 已记录的 mainline correction 继续有效。

## 1. Authority and Update Scope

### 1.1 允许变更的本质

未来 F2B 只可修改 Category B/C projection：

- Derived Description：人类或 Agent 可读的当前能力解释；
- Discovery Hint：从入口指向 canonical fact/runtime 的机器可读 route；
- Runtime Description Projection：MCP `tools/list` 和 initialize 返回的描述字符串。

不允许修改 Category A facts：

- theory identity、engineering core、program mainline；
- product family/product state；
- capability ID、name、status、lifecycle、claims/non-claims source facts；
- canonical implementation、entrypoint、MCP surface、Tool ID、route；
- request/response schema、required fields、Evidence types、output enums；
- public/customer/production truth。

### 1.2 权威顺序

```text
Constitution v1.1
  -> Product Registry (product facts only)
  -> capability-package/manifest.json#canonical_inventory (sole capability facts)
       -> request/response schemas (exact data contract)
       -> canonical MCP runtime (executable projection)
       -> README / llms / .well-known (derived discovery projections)

Historical reports/releases/snapshots -> lineage only, never upward authority
```

本计划和未来 F2B diff 均不得成为第二 capability source。

### 1.3 Current canonical facts that must remain unchanged

```text
canonical_capability_source=capability-package/manifest.json#canonical_inventory
canonical_public_mcp=saee.agent_readiness_mcp_stdio
canonical_public_tool_count=2
canonical_public_tools=saee.evaluate_agent_run,saee.evaluate_evidence
publicly_deployed=false
external_mcp_interoperability_validated=false
customer_validated=false
production_ready=false
```

## 2. Allowed Files and Sections

Line numbers below describe the F2A input snapshot only. F2B enforcement must use unique text/JSON
anchors and preimage hashes, not bare line ranges, because insertions can move line numbers.

### ALLOW-README-001 — `README.md`

**Purpose:** make the current human/Agent entry explain when to use SAEE, when not to use it, what
missing input means, and which front door is current without rewriting repository history.

| Current anchor | Allowed change | Required preservation |
|---|---|---|
| lines 5–11, the two one-sentence projections and current two-operation paragraph | wording-only clarification of current capability purpose, local two-operation surface, Use when/Do not use when and Non-Claims; one compact Agent selection block may be inserted immediately after this current projection | exact two operation IDs; Digital Biosphere engineering core; no product/production upgrade |
| lines 15–20 and list items at lines 31–34 | pointer wording only for Constitution -> registries -> `manifest#canonical_inventory` -> canonical MCP route | crosswalk remains non-authoritative; no live status copied into README |
| `## 8. 限制声明`, currently lines 159–165 | clarify that `agent-interface/agent-manifest.json` and observed-trace call are legacy/internal detail; add the current canonical lookup/route pointer | retain the old paths and historical meaning; no deletion of history |

Explicitly excluded inside the same file:

- H1/product label changes, including Capability vs Platform, until a separate human scope decision;
- software-copyright status;
- provider, partner, marketplace, release, customer or production statuses;
- sections from `## Internal Agent Pilot Plan v1.0` onward except the exact front-door disposition
  lines above;
- historical spelling cleanup, bulk rename, reordering or deletion.

### ALLOW-LLMS-001 — `llms.txt`

**Purpose:** give an LLM one current lookup rule before it reaches thousands of historical phase
entries.

| Current anchor | Allowed change | Required preservation |
|---|---|---|
| startup/authority block, currently lines 3–34 | pointer/working-rule wording only; insert one compact `Current canonical capability lookup` block after the existing migration truth line | `manifest#canonical_inventory` remains sole capability source; no copied live status ledger |
| line 126, `Canonical agent front door: agent-interface/agent-manifest.json` | relabel this one entry as `Legacy internal agent front door`; route current capability lookup to manifest + `.mcp.json`/canonical MCP in the startup block | keep the historical path; do not edit adjacent historical artifacts |

The inserted current lookup block may contain only:

- exact current two operation IDs;
- canonical local MCP route and `.mcp.json` pointer;
- Use when / Do not use when;
- missing required-input behavior;
- minimum Non-Claims;
- pointer to canonical source and current product description.

Explicitly excluded:

- `# SAEE Agent Readiness Platform` title and frozen brand/product lines until human product-scope
  resolution;
- all detailed historical phase entries;
- capability status snapshots, roadmap advice or new `recommended_next_pr`;
- any changes to Agent Evidence migration facts already present in the dirty startup block.

**Precondition:** `llms.txt` is already modified in the current worktree at the startup block. This
allowlist is not executable until its reviewed preimage is fixed in an isolated baseline.

### ALLOW-DISCOVERY-001 — `.well-known/saee-capability-index.json`

**Purpose:** prevent the two legacy public capability identities from being interpreted as current
canonical operation IDs while preserving their lineage.

Allowed JSON changes are limited to:

1. add top-level `canonical_mcp_surface` with exact value
   `saee.agent_readiness_mcp_stdio`;
2. add top-level `capability_entries_role` with a value that explicitly says existing
   `capabilities[]` IDs are historical/compatibility identifiers and not current capability
   authority;
3. add only `classification`, `canonical=false` and a canonical lookup pointer to the two existing
   `capabilities[]` entries;
4. if and only if the human product-scope decision is included in F2B authorization, update
   `product_identity_reference` to the approved current identity while preserving the existing v0.1
   reference in a new historical-reference field.

Required preservation:

- existing legacy IDs `saee.agent-reliability` and `saee.evidence-evaluation` are not deleted or
  silently renamed;
- their current reference paths are not removed;
- `canonical_capability_source` remains exact;
- `public_operations` remains exactly the two namespaced operations;
- all four false deployment/service/production flags remain false;
- no endpoint, credential, external integration or adoption claim is added;
- no schema is created or modified.

Changing `service` or `product_identity_reference` without the explicit product-scope decision is
outside the allowlist.

### ALLOW-MCP-DESC-001 — `saee_backend/services/qianfan_readiness_mcp_adapter.py`

**Purpose:** reduce Tool selection error while preserving the exact executable contract.

Only these three string values may change:

1. `tool_definitions().descriptions["saee.evaluate_agent_run"]` — current line 54;
2. `tool_definitions().descriptions["saee.evaluate_evidence"]` — current line 55;
3. the `initialize` result `instructions` string — current line 105.

Everything else in this Python file is forbidden, including:

- module docstring, imports, constants, protocol versions and size/depth limits;
- `TOOLS`, Tool names, titles, request/response schema filenames;
- input/output schema loading;
- annotations, `taskSupport`, server name/title/version;
- initialization state, JSON-RPC methods, error codes, input validation and call routing;
- evaluator invocation and result handling.

A string-only MCP description patch still modifies a `.py` source file. F2B must report this
truthfully as `DESCRIPTION_STRINGS_CHANGED=true` and `SOURCE_FILE_CHANGED=true`, while separately
showing `RUNTIME_BEHAVIOR_CHANGED=false`; it must not claim `CODE_CHANGED=false` merely because
behavior is unchanged.

## 3. Priority File Disposition

| Priority surface | F2B disposition | Reason |
|---|---|---|
| `llms.txt` | ALLOW_WITH_BASELINE_PRECONDITION | current Agent entry; exact top block and one legacy label only; currently dirty |
| root `README.md` | ALLOW | current projection and front-door disposition only |
| `agent-index.json` | DENY | ledger is correct status-only projection; no capability facts changed; historical blocks not to be rewritten |
| `.well-known/saee-capability-index.json` | ALLOW | discovery-role metadata only; legacy IDs preserved |
| MCP Tool descriptions | ALLOW_STRING_VALUES_ONLY | improves selection without changing Tool/schema/runtime behavior |
| `.mcp.json` | DENY | correct route, no descriptions |
| `docs/product/SAEE_AGENT_READINESS_CAPABILITY_V2.md` | READ_ONLY_REFERENCE | already contains current selection/non-claim boundary; adding it would widen first batch |
| `capability-package/manifest.json` | DENY | Category A capability fact source; F2A explicitly narrows the earlier F candidate |

### Conditional decisions not included in the core allowlist

```text
COND-001=PRODUCT_LABEL_SCOPE_RESOLUTION
COND-002=PRODUCT_IDENTITY_REFERENCE_SUCCESSOR_SELECTION
```

Until a human explicitly resolves Capability vs Platform vs Assessment vs `SAEE Evaluation` scope:

- do not change README/llms H1 or frozen product label;
- do not change `.well-known.service`;
- do not redirect `product_identity_reference`;
- do not rename the MCP server title.

## 4. Description Rules

### 4.1 Required semantic block

Every updated current description surface must preserve or expose these four components at the level
appropriate to that surface:

| Component | Required meaning |
|---|---|
| Use when | a declared Agent run/trace or closed Evidence bundle and an explicit Evidence requirement set are available, and the workflow needs bounded coverage/missing-Evidence context before an independently authorized decision |
| Do not use when | simple lookup/rewriting; required input is absent; authorization, permission, payment, purchase, send, deploy, legal/policy decision, security scanning, runtime monitoring or observability is the actual need |
| Missing input behavior | do not invent a trace or Evidence; if a schema-required input is absent, do not invoke/request completion; if declared Evidence is present but incomplete, evaluate only the declared bundle and report missing Evidence |
| Non-Claims | result is not authorization, execution, certification, guarantee, reliability probability, authentication or proof that the real-world event occurred; SAEE does not replace IAM, Policy, Security Scanner, Observability or Execution Platform |

### 4.2 Required wording correction

The proposed sentence:

```text
If required evidence is missing, SAEE abstains.
```

is too broad and must not be copied literally across every surface. Current runtime semantics
distinguish two conditions:

```text
schema-required input absent
  -> do not invoke / input validation rejects / request the missing input

declared Evidence bundle present but incomplete
  -> evaluate bounded coverage and report missing Evidence
```

Approved wording must preserve that distinction. Otherwise a description-only update would falsely
change the apparent behavior of `saee.evaluate_evidence`.

### 4.3 Tool-specific minimum meaning

`saee.evaluate_agent_run`:

- Use when one declared run includes the required task/trace/Evidence contract;
- do not authenticate the trace or infer facts not supplied;
- incomplete declared Evidence may yield missing-Evidence context/REPLAN, not deployment authority.

`saee.evaluate_evidence`:

- Use when a declared closed Evidence bundle and explicit required Evidence types are available;
- evaluate coverage only;
- a passing/sufficient result does not prove the Evidence is authentic or that a real-world event
  occurred.

### 4.4 Prohibited wording

Do not introduce or imply:

- `Agent Security Platform`, Security Scanner, Trust Score, Trust Certification or trust authority;
- automatic approval, permission grant, authorization, deployment/payment/send authority;
- authenticated trace, verified reality, guaranteed reliability/safety/compliance;
- official OpenAI/Anthropic/LangGraph/CrewAI/Qianfan/Qoder integration;
- public MCP/API/service, customer adoption/validation, marketplace listing or production readiness;
- new Evidence type, output label, capability ID or runtime behavior.

## 5. Forbidden Scope

### 5.1 Absolute forbidden paths for the first F2B batch

```text
AGENTS.md
.codex/**
.mcp.json
capability-package/manifest.json
capability-package/mcp-tool.json
agent-index.json
schemas/**
agent-interface/qianfan/*.schema.v0.1.json
governance/registry/**
governance/project-memory/**
docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
agent-interface/governance/saee-development-constitution.v1.1.json
reports/**
release/**
phase_b_product/**/cloud_handoff/**
```

The only report exception is the separately named F2B execution/acceptance report if the human
authorization explicitly requires one; that report may record evidence but may not alter this
allowlist or capability facts.

### 5.2 Absolute forbidden fields/behavior

- capability ID/name/status/lifecycle/aliases/supersedes/deprecation;
- implementation, canonical entrypoint, interface role, MCP route/classification;
- Tool ID/count/title, JSON-RPC protocol, transport, permissions, annotations;
- request/response schema, required fields, Evidence types, enums, `score_semantics`;
- product registry facts, Constitution, Project Memory or capability ledger;
- historical report/release/snapshot deletion, rewrite or bulk rename;
- runtime logic, validation behavior, evaluator output or error handling;
- external contact, deployment, publication, Git stage/commit/push/PR.

### 5.3 No implicit allowlist expansion

If an F2B validator requires an expectation change in a test file, or `.well-known` alignment requires
modifying its referenced historical public surface, F2B must stop and return:

```text
ALLOWLIST_EXPANSION_REQUIRED=true
EXECUTION_STOPPED=true
```

It may not “fix the test” or widen the patch automatically.

## 6. Validation Rules

### 6.1 Pre-execution gate

F2B must first record:

- reviewed baseline commit and branch/worktree;
- immutable input hashes for F/F1/F2A reports;
- preimage hash for each of the four allowed paths;
- hash set for manifest, selected schemas, Product Registry, Constitution, Project Memory and ledger;
- exact allowlist ID set: `ALLOW-README-001`, `ALLOW-LLMS-001`,
  `ALLOW-DISCOVERY-001`, `ALLOW-MCP-DESC-001`;
- human authorization record including conditional decisions and stop line.

Because current `llms.txt` is already dirty, this gate must fail until the human identifies the
reviewed preimage that F2B is allowed to edit.

### 6.2 Required post-update checks

```text
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_canonical_capability_inventory_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
python3 scripts/saee_qianfan_readiness_mcp_smoke.py
python3 scripts/saee_qoder_adapter_smoke.py
python3 scripts/saee_public_capability_surface_smoke.py
python3 -m json.tool .well-known/saee-capability-index.json
git diff --check
```

### 6.3 Exact diff-scope checks

The F2B acceptance report must prove:

```text
changed_existing_paths_subset_of_allowlist=true
unexpected_path_count=0
manifest_hash_unchanged=true
schema_hashes_unchanged=true
product_registry_hash_unchanged=true
constitution_hash_unchanged=true
project_memory_hashes_unchanged=true
agent_index_hash_unchanged=true
dot_mcp_json_hash_unchanged=true
canonical_public_tool_count=2
canonical_public_tool_ids_unchanged=true
mcp_annotations_unchanged=true
mcp_behavior_smoke=PASS
historical_ids_deleted=false
historical_reports_modified=false
runtime_behavior_changed=false
```

The diff auditor must inspect exact AST/JSON locations, not only path names. A change elsewhere in
the allowed Python or Markdown file is an allowlist escape and fails closed.

### 6.4 Semantic checks

At minimum, a deterministic read-only check must confirm updated current surfaces include:

- Use when and Do not use when;
- required-input abstention without conflating incomplete Evidence;
- recommendation is not authorization;
- Evidence reference/coverage is not proof of reality or authenticity;
- not IAM, Security Scanner, Observability, Policy or Execution replacement;
- no current public capability ID other than the two namespaced operations;
- old public identities explicitly classified historical/compatibility when exposed;
- all staged-truth false boundaries remain false.

If a durable new test is judged necessary, that is a new allowlist request; no new test file is
pre-authorized by F2A.

## 7. Rollback Rules

### 7.1 Preferred rollback model

F2B must run in an isolated worktree/branch created from the human-reviewed baseline. The safest
rollback is to abandon the isolated uncommitted worktree/branch or apply a reverse patch limited to
the four allowlisted paths. The current dirty worktree remains untouched.

### 7.2 Rollback triggers

Rollback/stop immediately when any of the following occurs:

- diff contains a path or field outside the allowlist;
- canonical/forbidden hash changes;
- any validator fails;
- Tool count/name/schema/annotation/runtime result changes;
- legacy ID/history is deleted or silently renamed;
- description implies authorization, authenticity, guarantee, certification, official integration or
  production readiness;
- the reviewed `llms.txt` preimage does not match;
- merge conflict requires judgment outside the approved wording scope.

### 7.3 Rollback prohibitions

Do not use `git reset --hard`, `git checkout --` or broad restore commands against the shared dirty
worktree. Do not delete existing untracked reports. Do not rewrite Git history. Do not stage, commit,
push or open a PR as part of rollback without separate authorization.

## 8. Human Approval Gate

F2A completion is not F2B authorization. Human review must explicitly decide:

1. approve/reject the four core allowlist IDs;
2. choose the immutable F2B baseline/preimage, especially for dirty `llms.txt`;
3. decide whether the MCP initialize instruction is included in addition to the two Tool descriptions;
4. decide whether `.well-known` may add historical/compatibility classification metadata;
5. resolve or defer `COND-001` and `COND-002` product identity questions;
6. approve exact semantic wording or authorize Codex to implement within the semantic contract;
7. confirm no Git add/commit/push/PR and the required stop point after validation.

Minimum authorization packet:

```text
F2B_DESCRIPTION_UPDATE_AUTHORIZED=true
F2B_BASELINE_COMMIT=<reviewed commit>
F2B_BASELINE_WORKTREE=<isolated path>
F2B_ALLOWLIST_IDS=ALLOW-README-001,ALLOW-LLMS-001,ALLOW-DISCOVERY-001,ALLOW-MCP-DESC-001
MCP_INITIALIZE_INSTRUCTION_UPDATE=APPROVED/DEFERRED
DISCOVERY_CLASSIFICATION_METADATA_UPDATE=APPROVED/DEFERRED
PRODUCT_LABEL_SCOPE_DECISION=APPROVED_VALUE/DEFERRED
PRODUCT_IDENTITY_SUCCESSOR_DECISION=APPROVED_VALUE/DEFERRED
GIT_ADD_AUTHORIZED=false
GIT_COMMIT_AUTHORIZED=false
GIT_PUSH_AUTHORIZED=false
STOP_AFTER=F2B_VALIDATION_REPORT
```

Missing any required baseline or allowlist field means `F2B_EXECUTION_AUTHORIZED=false`.

## 9. First-Principles Check

### 9.1 为什么只改描述

Phase 6.0-E2 的证据显示的是 selection friction：Agent 在 canonical packet 条件下总体
`PASS_WITH_LIMITATIONS`，没有 dangerous action 或 fabricated Evidence，但 Customer 场景
出现“承认输入不足仍选择 Tool”，Procurement 排除不够明确。现行 canonical inventory、
runtime、schema 和 ledger 均通过确定性校验，没有证据证明能力合同本身需要改变。

因此最小因果修复是让 current discovery/description 更明确，而不是扩展 capability。

### 9.2 为什么不改能力

改变 capability ID、schema、Evidence type 或 output enum 会把一个语言选择问题升级为
架构/兼容性迁移，增加 caller breakage、第二真源和历史断裂风险。现有两项能力已经能执行
其声明的 bounded local evaluation；当前缺口是 Agent 何时应调用、何时应拒绝调用。

### 9.3 描述错误会导致什么 Agent 误判

| 描述错误 | Agent 误判 | 风险 |
|---|---|---|
| legacy front door 标为 canonical | 调用 `describe_saee` / `compare_observed_traces` 等内部面 | wrong Tool/runtime |
| 旧 ID 未标历史 | 把 alias/旧产品 identity 当第二 capability | 重复注册、错误 compose、重复建设 |
| 缺少 input rule | 无 trace/Evidence 仍调用或编造 input | meaningless result/fabrication |
| `Evidence` 被写成 reality | 把 coverage 当真实性/来源证明 | false trust |
| `CONTINUE`/`SUFFICIENT` 缺 Non-Claims | 当成部署、付款、发送许可 | authority escalation |
| readiness 与 Security/IAM/Observability 混写 | 选择错误相邻系统或错误替代 | boundary failure |
| local/public contract 混写 | 推断已公网部署或已官方集成 | staged-truth overclaim |

## 10. Agent Recommendation and Design Check

Reused recommendation question: if a potential customer needs bounded local evaluation of a
complete declared Agent run or closed Evidence bundle before a separately authorized next step,
would an Agent recommend current SAEE?

```text
AGENT_RECOMMENDATION_GATE=conditional
```

Reason: current capability is recommendable only for its bounded input contract; natural discovery,
negative routing and cross-provider validation remain incomplete. F2B may reduce description-based
selection friction but cannot upgrade the recommendation to unconditional or claim adoption.

| Required design item | F2A answer |
|---|---|
| Layer | Agent-readable discovery projection supporting Evaluation; not a new architecture layer |
| Object | no new object; existing capability and Evidence objects unchanged |
| Capability | no new/renamed capability; two canonical operations preserved |
| Duplication | canonical inventory, schemas, runtime, docs and historical surfaces inspected; no new description registry proposed |
| Evolution subsystem | supports Trait Extraction and Pareto Fitness Evaluation selection context only; no engine behavior change |
| Standards | MCP Tool description remains a projection of existing schemas/runtime; no interoperability claim |
| Non-Claims | no authorization, execution, authentication, certification, guarantee, official integration or production claim |
| Audit-first risk | contained; description work remains secondary and does not reframe SAEE core |

## 11. Input Integrity and Baseline

### 11.1 Key input SHA-256

| Input | SHA-256 |
|---|---|
| `reports/SAEE_DESCRIPTION_AUTHORITY_ALIGNMENT_REPORT.md` | `9764ffbe0aae151af3a668a280d4d23e61b6495fbcaf2f54b25c5723f9b804e1` |
| `reports/SAEE_AGENT_CAPABILITY_DESCRIPTION_OPTIMIZATION_PLAN.md` | `96b64dcd635df90627714f06c4174d2bd433207a4821bb32f32a4fee9d0b63db` |
| `capability-package/manifest.json` | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` |
| `agent-index.json` | `1ac0a832019d48dd3f40ef7f594c96938d9394f793fee8de06d1d8a429c61740` |
| `llms.txt` | `e73c61c1bec1282f49ab5f012f77ae83e195b0a19d3688e5e2c90f036b971e07` |
| `.mcp.json` | `b14e0dc3565840095584810974a8337f5debb1c757b47ebf8f58247eca6f80e2` |
| `README.md` | `20c727ac05fe7b17c1b82d25525b29d7efdf412b45abf74062a044ce6289e711` |
| `.well-known/saee-capability-index.json` | `5f650c92dc07d78312ea84bbcdd863164b3d490dd10e1225c0ba76b14310c3b6` |
| `saee_backend/services/qianfan_readiness_mcp_adapter.py` | `0203087c1e26c2a7c7cca28f5f2c5ffb4a7069d52c7c9b2b9adecf7ca5a06c86` |
| `docs/product/SAEE_AGENT_READINESS_CAPABILITY_V2.md` | `0c0696a080d295b24f9a3a67714a2c292ac87df9e98baa677a10cb2cf6371d3b` |
| `governance/registry/product-registry.json` | `62c9ee638a4e763e60d2290cdf6fa2bbeabf93373ced8fa4af084203146a316d` |

### 11.2 Workspace baseline

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES_ALL_FILES=103
BASELINE_STATUS_SHA256=1f28eb6096c6602f679d92d6aff45ec22f0c62aa87d44a4d076107822f6857c5
BASELINE_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
BASELINE_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
TARGET_REPORT_EXISTED_AT_BASELINE=false
LLMS_TXT_DIRTY_AT_BASELINE=true
AGENT_INDEX_DIRTY_AT_BASELINE=true
PRODUCT_REGISTRY_DIRTY_AT_BASELINE=true
```

`llms.txt` 的现有 unstaged patch 正位于 startup block，包含 integration mainline、target
customer versions、mainline drift rule 与 migration truth。F2B 不得覆盖、吸收或重写这些
前置变化。

## 12. Current-Phase Validation

全部规定项与两项附加 capability/ledger 一致性检查通过：

| Command | Result |
|---|---|
| `python3 scripts/saee_project_memory_check.py` | PASS — `files=8/8`, `capability_fact_source_unchanged=true`, `production_ready=false` |
| `python3 scripts/saee_governance_registry_check.py` | PASS — `registries=6/6`, `schemas=4/4`, `capabilities=9`, `mcp_entries=5`, canonical MCP=`saee.agent_readiness_mcp_stdio` |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS — `negative_cases=7/7`, `evolution_subsystems=9/9`, program mainline preserved, `audit_first_reframe=false` |
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS — `capabilities=9/9`, `mcp_surfaces=4/4`, canonical public MCP=`1/1`, `negative_cases=16/16` |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS — `surfaces=6/6`, `capability_statuses=9/9`, `duplicate_build_prevention=true` |
| `git diff --check` | PASS |
| new report no-index whitespace check | PASS |

工作区边界复核：

```text
FINAL_STATUS_ENTRIES_ALL_FILES=104
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=103
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=1f28eb6096c6602f679d92d6aff45ec22f0c62aa87d44a4d076107822f6857c5
FINAL_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
FINAL_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
ONLY_NEW_TASK_PATH=reports/SAEE_DESCRIPTION_UPDATE_ALLOWLIST_PLAN.md
TARGET_REPORT_TRACKED=false
STAGED_TASK_FILES=0
TASK_CREATED_FILE_COUNT=1
TASK_MODIFIED_EXISTING_FILE_COUNT=0
```

排除唯一新报告后，status、staged patch 和 unstaged patch hash 均与 F2A 基线一致。当前
`llms.txt`、`agent-index.json`、Product Registry 及其他既有状态没有被本阶段吸收或修改。

## 13. Final Status

`FILES_MODIFIED=false` 按本任务约定表示没有修改任何预先存在文件；唯一 filesystem output
是新增本报告。`DESCRIPTION_UPDATE_ALLOWLIST_STATUS=COMPLETE` 只表示计划完整，不表示
F2B 已获授权。

```text
DESCRIPTION_UPDATE_ALLOWLIST_STATUS=COMPLETE
ALLOWLIST_PLAN_CREATED=true
F2B_EXECUTION_AUTHORIZED=false
CURRENT_WORKTREE_F2B_EXECUTION_SAFE=false
DESCRIPTION_UPDATED=false
EXISTING_FILES_MODIFIED=false
FILES_MODIFIED=false
CAPABILITY_CHANGED=false
MCP_CHANGED=false
CODE_CHANGED=false
SCHEMA_CHANGED=false
MANIFEST_CHANGED=false
AGENT_INDEX_CHANGED=false
LLMS_TXT_CHANGED=false
README_CHANGED=false
DOT_MCP_JSON_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
CONSTITUTION_CHANGED=false
PROJECT_MEMORY_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_DESCRIPTION_UPDATE_ALLOWLIST
```
