# SAEE F1 完整隔离构造报告

日期：2026-07-17

## 0. 结论

本次从指定 `HEAD`（当前提交）建立全新的独立隔离克隆，只应用六项 `F1-EA`（基础锚点精确对象）和六项 `F1-VD`（校验器依赖对象），形成完整 F1（基础锚点第一阶段）候选。

十二项目标内容及散列全部匹配统一 `1.1.1` 目标集合；开发宪法、治理、能力清单、能力真值四项校验全部通过；基于提交、路径集合、对象散列、继承对象、禁止内容和差异格式的 F1 自验证也通过。

按照“验证完成前保持为假”的要求，只有在上述检查全部完成后才记录：

```text
F1_COMPLETE_ISOLATED_CONSTRUCTION_STATUS=COMPLETE
F1_CANDIDATE_CREATED=true
F1_CANDIDATE_VALIDATED=true
F1_SELF_VALIDATION_PASS=true
F1_BASELINE_CREATED=false
F1_BASELINE_AUTHORIZED=false
MAINLINE_DRIFT_DETECTED=false
```

该候选仍然只是隔离工作树中的未暂存差异，不是 Git（版本控制系统）历史基线，不是 P1（契约父基线第一阶段），也不是主线合并。

## 1. 隔离来源

```text
SOURCE_REPOSITORY=/Users/zhangbin/Documents/SAEE
ISOLATED_WORKSPACE=/Users/zhangbin/Documents/SAEE-f1-complete-isolated-construction-001
EXPECTED_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
ACTUAL_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
DETACHED_HEAD=true
CLONE_NO_HARDLINKS=true
SOURCE_WORKTREE_IMPORTED=false
SOURCE_INDEX_IMPORTED=false
SOURCE_UNTRACKED_FILES_IMPORTED=false
```

隔离目录是重新创建的独立克隆，没有复用上一轮六对象候选，没有使用 `git worktree`（版本控制工作树）、符号链接或硬链接。

构造前：

```text
ISOLATED_WORKTREE_CLEAN=true
ISOLATED_INDEX_CLEAN=true
BASE_FILE_HASHES_MATCH=true
F1_CANDIDATE_CREATED=false
```

## 2. 授权依据

```text
F1_EA_APPROVED_OBJECTS=F1-EA-01;F1-EA-02;F1-EA-03;F1-EA-04;F1-EA-05;F1-EA-06R
F1_VD_APPROVED_OBJECTS=F1-VD-01;F1-VD-02;F1-VD-03;F1-VD-04;F1-VD-05;F1-VD-06
F1_VD_AUTHORIZATION_PACKAGE=reports/SAEE_F1_VALIDATOR_MINIMUM_ADDITIONAL_AUTHORIZATION_PACKAGE.md
F1_VD_AUTHORIZATION_PACKAGE_SHA256=44f23e9934481f73002099385922c151940f0af16a257a46d709144c599e5824
TARGET_VERSION_SET=1.1.1_ONLY
OLD_STAGED_1_1_0_ALLOWED=false
```

## 3. 构造对象

### 3.1 F1-EA（基础锚点精确对象）

| 对象 | 路径与范围 | 目标 `SHA-256`（安全散列算法二百五十六位） | 实际散列 | 结果 |
| --- | --- | --- | --- | --- |
| `F1-EA-01` | `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md:27-42` | `170f36930014500506291ae1fb21758f5da3b41dd9a227c4ad99bbab3243cfd4` | 相同 | 通过 |
| `F1-EA-02` | `.codex/current_state.md:9-11,21,31-32,46-47` | `b1f798824d7aa5884734032af43025a0da822be630afeb435b826c6e2cfd6f3f` | 相同 | 通过 |
| `F1-EA-03` | `.codex/rules.md:3-12,39-46` | `5ed8f0fd2e045e3f80b6c350a12499d5bceaf3e87cc4e0544af4b0981398420e` | 相同 | 通过 |
| `F1-EA-04` | `agent-index.json#development_constitution_v1_1` | `a1ff98c78b569b492501368d8983992d171532debfafa62d811160bd94de4f78` | 相同 | 通过 |
| `F1-EA-05` | `llms.txt:24-28` | `2f0fce7ef9eb350b52d8275d4c991e2cfe6101970bb3f7131c880b0b5e81d30d` | 相同 | 通过 |
| `F1-EA-06R` | `docs/product/SAEE_MODULE_REGISTRY.md:10,24` | `e92a20f6f9bc6de4b126d0aa024a767b8d69ce19c0b2e6f2d9dc184c2a9024ef` | 相同 | 通过 |

### 3.2 F1-VD（校验器依赖对象）

| 对象 | 路径与范围 | 目标 `SHA-256`（安全散列算法二百五十六位） | 实际散列 | 结果 |
| --- | --- | --- | --- | --- |
| `F1-VD-01` | `scripts/saee_development_constitution_smoke.py` 全文件 | `8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550` | 相同 | 通过 |
| `F1-VD-02` | `agent-interface/governance/saee-development-constitution.v1.1.json` 全文件 | `df200d13ec90ce5dd57cedb4ceab83b1c2a5b751b68af35a1a749f39db15f8a0` | 相同 | 通过 |
| `F1-VD-03` | `schemas/saee-development-constitution.schema.v1.1.json` 全文件 | `dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86` | 相同 | 通过 |
| `F1-VD-04` | `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` 全文件 | `37d9adb3049c5fdd871460f6756240a177264e4442cc38252786e9d7c86f378c` | 相同 | 通过 |
| `F1-VD-05` | `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` 全文件 | `1bc493e03e3158e2d984308a78efa80cde131a5b9ee2142449695c807433ee9c` | 相同 | 通过 |
| `F1-VD-06` | `AGENTS.md:47-80` | `0ff92cee0427e6e6b3e207544c153a6bab82f214d3998e16b224f58d46da8c42` | 相同 | 通过 |

```text
F1_EA_TARGET_HASHES_MATCH=true
F1_VD_TARGET_HASHES_MATCH=true
TARGET_VERSION_1_1_1_COHERENT=true
OLD_STAGED_1_1_0_INCLUDED=false
```

## 4. 精确差异路径

构造及校验完成后，差异路径严格为：

```text
.codex/current_state.md
.codex/rules.md
AGENTS.md
agent-index.json
agent-interface/governance/saee-development-constitution.v1.1.json
docs/architecture/IMMUNE_GOVERNANCE_PLANE.md
docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
docs/product/SAEE_MODULE_REGISTRY.md
docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md
llms.txt
schemas/saee-development-constitution.schema.v1.1.json
scripts/saee_development_constitution_smoke.py
```

```text
CHANGED_PATH_COUNT=12
CHANGED_PATH_SET_MATCH=true
UNAUTHORIZED_PATH_CHANGED=false
VALIDATOR_GENERATED_PATH_COUNT=0
```

三个非授权整文件对象仍按精确范围构造：

```text
CURRENT_AGENT_INDEX_WHOLE_FILE_COPIED=false
CURRENT_LLMS_WHOLE_FILE_COPIED=false
CURRENT_MODULE_REGISTRY_WHOLE_FILE_COPIED=false
CURRENT_AGENTS_WHOLE_FILE_COPIED=false
```

## 5. 继承对象验证

以下对象从指定 `HEAD`（当前提交）原样继承：

```text
capability-package/manifest.json=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
README.md=20c727ac05fe7b17c1b82d25525b29d7efdf412b45abf74062a044ce6289e711
.codex/context.md=47f8c87024d8e07d830bad11f3025961feee799c0cc35333bc1dab37c9951e10
```

```text
HEAD_INHERITED_OBJECTS_MATCH=true
CURRENT_WORKSPACE_P1_VARIANTS_IMPORTED=false
```

## 6. 必需校验

### 6.1 开发宪法校验

执行：

```text
python3 scripts/saee_development_constitution_smoke.py
```

结果：

```text
CONSTITUTION_VALIDATION_EXIT_CODE=0
CONSTITUTION_VALIDATION_PASS=true
schema_cases=1/1
negative_cases=7/7
deterministic_runs=10/10
evolution_subsystems=9/9
canonical_reuse_routes=3/3
program_mainline=saee_agent_evidence_integration
target_customer_versions=3/3
source_code_migrated=false
runtime_integrated=false
production_ready=false
```

### 6.2 治理校验

执行：

```text
python3 scripts/saee_governance_registry_check.py
```

结果：

```text
GOVERNANCE_VALIDATION_EXIT_CODE=0
GOVERNANCE_VALIDATION_PASS=true
registries=6/6
schemas=4/4
assets=12
repositories=9
capabilities=9
mcp_entries=5
products=4
```

### 6.3 能力清单校验

执行：

```text
python3 scripts/saee_canonical_capability_inventory_smoke.py
```

结果：

```text
CAPABILITY_INVENTORY_VALIDATION_EXIT_CODE=0
CAPABILITY_INVENTORY_VALIDATION_PASS=true
capabilities=9/9
mcp_surfaces=4/4
canonical_public_mcp_surfaces=1/1
negative_cases=16/16
required_coverage=24/24
deterministic_runs=5/5
```

### 6.4 能力真值校验

执行：

```text
python3 scripts/saee_capability_truth_consistency_smoke.py
```

结果：

```text
CAPABILITY_TRUTH_VALIDATION_EXIT_CODE=0
CAPABILITY_TRUTH_VALIDATION_PASS=true
sources_checked=8/8
valid_cases=1/1
invalid_cases=11/11
deterministic_runs=5/5
conflicts_detected=false
```

## 7. F1 自验证

自验证方法：

```text
F1_SELF_VALIDATION_METHOD=EXACT_SCOPE_HASH_AND_VALIDATOR_CLOSURE
```

验证条件：

1. `HEAD`（当前提交）精确匹配；
2. 差异路径数量等于十二；
3. 差异路径集合逐字匹配授权清单；
4. 十二项目标散列全部匹配；
5. 三个继承对象散列匹配；
6. 四项校验退出码全部为零；
7. 禁止内容扫描没有发现 P1、M03-M06、目标完整性、状态完整性或可信基础设施增量；
8. `git diff --check`（差异格式检查）通过；
9. 校验前后路径集合不变。

首次自验证脚本对整个状态输出使用去首尾空白操作，误删第一行状态位后的路径前导点，把 `.codex/current_state.md` 错误解析为 `codex/current_state.md`。这是检查脚本的解析假阴性，不是候选路径错误。修正为只删除末尾换行后重新执行，结果为：

```text
STATUS_PARSER_CORRECTED=true
HEAD_MATCH=true
CHANGED_PATH_COUNT=12
CHANGED_PATH_SET_MATCH=true
DIFF_CHECK_PASS=true
FORBIDDEN_ADDITION_MATCH_COUNT=0
F1_SELF_VALIDATION_PASS=true
```

## 8. 排除边界

```text
P1_CREATED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
NINETY_NINE_PATH_PATCH_INCLUDED=false
M03_M06_CREATED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
M03_M06_INCLUDED=false
TRUST_INFRASTRUCTURE_CHANGED=false
TRUST_INFRASTRUCTURE_INCLUDED=false
GOAL_INTEGRITY_INCLUDED=false
STATE_INTEGRITY_INCLUDED=false
NEW_CAPABILITY_CREATED=false
PUBLIC_CAPABILITY_CHANGED=false
PUBLIC_MCP_CHANGED=false
PUBLIC_CAPABILITY_SCHEMA_CHANGED=false
MAINLINE_GUARD_EXECUTED=false
```

`scripts/mainline_guard.py`（主线守卫）不属于本次明确要求的五项校验，而且历史上存在写入跟踪文件的副作用风险，因此本次未运行。当前结果只证明完整 F1 隔离候选及其请求范围内的自验证成立，不证明整个脏主工作区、P1、合并准备或提交准备成立。

## 9. 主工作区保护

本次主工作区只新增本报告。十二项候选内容全部存在于独立隔离目录。

状态常量中的 `CODE_CHANGED=false`、`MCP_CHANGED=false` 和 `SCHEMA_CHANGED=false` 均指主工作区及公开能力契约没有被本次构造修改。隔离候选内部真实新增了开发宪法校验器和开发宪法数据结构规范对象，记录如下：

```text
MAIN_WORKSPACE_CODE_CHANGED=false
MAIN_WORKSPACE_MCP_CHANGED=false
MAIN_WORKSPACE_SCHEMA_CHANGED=false
ISOLATED_CANDIDATE_VALIDATOR_FILE_ADDED=true
ISOLATED_CONSTITUTION_SCHEMA_OBJECT_ADDED=true
PUBLIC_CAPABILITY_SCHEMA_CHANGED=false
```

没有执行：

```text
git add
git commit
git push
merge
```

## 10. 最终状态

```text
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
F1_CANDIDATE_CREATED=true
F1_CANDIDATE_VALIDATED=true
F1_CONSTRUCTION_EXECUTED=true
F1_BASELINE_CREATED=false
F1_BASELINE_AUTHORIZED=false
P1_CREATED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_CREATED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
MERGE_EXECUTED=false
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_COMPLETE_F1_ISOLATED_CANDIDATE
```
