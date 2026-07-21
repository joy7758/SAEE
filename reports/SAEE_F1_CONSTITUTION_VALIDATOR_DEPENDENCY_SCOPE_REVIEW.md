# SAEE F1 宪法校验依赖范围审查

日期：2026-07-17

## 0. 结论

`scripts/saee_development_constitution_smoke.py`（开发宪法校验器）必须进入完整、可独立自验证的 F1（基础锚点第一阶段）。只把校验器文件加入 F1 仍然不够；其最小新增闭包还需要四个完整核心对象和 `AGENTS.md`（智能体规则文件）中的一个精确主线段落。

当前六项隔离候选已经覆盖校验器所需的六个投影表面；指定 `HEAD`（当前提交）还可以原样继承能力清单、项目说明和编码智能体上下文。没有 P1（契约父基线第一阶段）对象是该校验器的直接依赖。

最小新增授权候选固定为六项：

1. 开发宪法校验器；
2. 开发宪法机器契约；
3. 开发宪法数据结构规范；
4. 开发宪法正文；
5. 开发宪法推荐门；
6. `AGENTS.md:47-80`（智能体规则文件第 47—80 行）的宪法主线段落。

```text
F1_CONSTITUTION_VALIDATOR_DEPENDENCY_SCOPE_REVIEW_STATUS=COMPLETE
CONSTITUTION_VALIDATOR_REQUIRED_FOR_F1=true
DIRECT_REPOSITORY_DEPENDENCY_OBJECT_COUNT=15
F1_REQUIRED_ALREADY_APPROVED_COUNT=6
HEAD_INHERIT_ONLY_COUNT=3
P1_ONLY_COUNT=0
SEPARATE_AUTHORIZATION_REQUIRED_COUNT=6
MINIMUM_ADDITIONAL_OBJECT_COUNT=6
F1_SELF_VALIDATION_READY=false
MAINLINE_DRIFT_DETECTED=false
```

## 1. 审查方法与边界

审查以校验器源码的固定路径常量、文件读取调用、仓库内导入和输出校验为依据。没有从报告文字反推依赖，也没有把当前工作树全部内容视为依赖。

校验器：

```text
scripts/saee_development_constitution_smoke.py
```

源码事实：

- 只导入 Python（蟒蛇编程语言）标准库：`copy`、`json`、`pathlib`、`typing` 和 `__future__`；
- 不导入任何仓库内 Python（蟒蛇编程语言）模块；
- 不启动子进程；
- 不访问网络；
- 不读取环境变量；
- 不写文件；
- 固定读取十四个其他仓库对象。

标准库属于运行环境前提，不是需要加入 F1 的仓库对象。

## 2. 分类规则

```text
A=F1_REQUIRED
B=HEAD_INHERIT_ONLY
C=P1_ONLY
D=SEPARATE_AUTHORIZATION_REQUIRED
```

- A：已经属于六项批准候选，而且是校验器直接依赖；
- B：指定 `HEAD`（当前提交）已经满足校验器要求，必须原样继承；
- C：仅属于九十九路径契约父基线，本次没有直接依赖命中；
- D：功能上必须进入完整 F1，但尚未得到本推进链的精确构造授权。

D 类不是“可选”，而是“必须但尚未授权”。获得精确人工授权后，才能在构造阶段转为 A 类。

## 3. Python（蟒蛇编程语言）依赖

| 对象 | `HEAD`（当前提交）状态 | 依赖原因 | 分类 | 判断 |
| --- | --- | --- | --- | --- |
| `scripts/saee_development_constitution_smoke.py` | 不存在 | 唯一开发宪法校验入口；没有它无法执行自验证 | D | 必须进入 F1，需单独授权 |

当前工作树参考文件 `SHA-256`（安全散列算法二百五十六位）：

```text
8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550
```

当前文件状态为 `AM`：文件相对 `HEAD`（当前提交）为新增，暂存版本与工作树版本又不一致。暂存版本校验器仍要求宪法版本 `1.1.0`，当前工作树版本要求 `1.1.1`。因此该散列仅用于范围识别，不自动成为授权目标。

```text
REPOSITORY_LOCAL_PYTHON_DEPENDENCY_COUNT=1
EXTERNAL_PYTHON_PACKAGE_DEPENDENCY_COUNT=0
NETWORK_DEPENDENCY_COUNT=0
```

## 4. 数据结构规范与机器契约依赖

| 对象 | `HEAD`（当前提交）状态 | 依赖原因 | 分类 | 判断 |
| --- | --- | --- | --- | --- |
| `schemas/saee-development-constitution.schema.v1.1.json` | 不存在 | 校验根结构封闭性、字段覆盖和宪法版本 | D | 必须进入 F1，需单独授权 |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | 不存在 | 被校验的机器宪法事实源 | D | 必须进入 F1，需单独授权 |

当前工作树参考散列：

```text
schemas/saee-development-constitution.schema.v1.1.json=dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86
agent-interface/governance/saee-development-constitution.v1.1.json=df200d13ec90ce5dd57cedb4ceab83b1c2a5b751b68af35a1a749f39db15f8a0
```

两者当前也处于 `AM` 状态。暂存版本声明 `1.1.0`，当前工作树版本声明 `1.1.1`。数据结构规范中的 `$schema`（数据结构规范标识）是声明性 URI（统一资源标识符）；校验器只解析本地 JSON（轻量数据交换格式），不会访问该地址，也没有外部 `$ref`（外部引用）依赖。

## 5. 宪法文件依赖

| 对象 | `HEAD`（当前提交）状态 | 依赖原因 | 分类 | 判断 |
| --- | --- | --- | --- | --- |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | 不存在 | 校验工程核心、证据归属、分阶段真值、主线和纠偏令牌 | D | 必须进入 F1，需单独授权 |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | 不存在 | 校验初始条件性推荐与最终推荐闭环 | D | 必须进入 F1，需单独授权 |
| `AGENTS.md:47-80` | `HEAD` 中不存在该段落 | 校验 `Constitutional Program Mainline` 和三个客户版本目标令牌 | D | 只需精确段落授权，禁止整文件复制 |

当前工作树参考散列：

```text
docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md=37d9adb3049c5fdd871460f6756240a177264e4442cc38252786e9d7c86f378c
docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md=1bc493e03e3158e2d984308a78efa80cde131a5b9ee2142449695c807433ee9c
AGENTS.md:47-80=0ff92cee0427e6e6b3e207544c153a6bab82f214d3998e16b224f58d46da8c42
```

`AGENTS.md`（智能体规则文件）在 `HEAD`（当前提交）中已经具备校验器要求的前三个令牌，但缺少：

```text
Constitutional Program Mainline
SAEE Evidence / SAEE Evaluation / SAEE Governance
```

因此只需要当前第 47—80 行的精确段落，不需要重新授权或复制整个文件。

## 6. 能力清单依赖

| 对象 | `HEAD`（当前提交）状态 | 依赖原因 | 分类 | 判断 |
| --- | --- | --- | --- | --- |
| `capability-package/manifest.json#canonical_inventory` | 存在且包含三个预期能力编号 | 校验宪法复用路线确实存在于规范能力清单 | B | 从 `HEAD` 原样继承 |

`HEAD`（当前提交）对象散列：

```text
fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
```

已经确认包含：

```text
saee.evaluate_evidence
saee.general_trace_normalization
saee.trusted_trace_to_evidence_conversion
```

当前主工作区中的能力清单存在其他未提交变化，但开发宪法校验不需要这些变化。F1 必须继承 `HEAD`（当前提交）版本，不能带入 P1（契约父基线第一阶段）、M03-M06（第三至第六里程碑）或其他能力事实变化。

## 7. 说明表面与配置对象依赖

### 7.1 已由六项候选覆盖

| 对象 | 已批准对象 | 分类 | 校验状态 |
| --- | --- | --- | --- |
| `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md` | `F1-EA-01` | A | 所需令牌已匹配 |
| `.codex/current_state.md` | `F1-EA-02` | A | 所需令牌已匹配 |
| `.codex/rules.md` | `F1-EA-03` | A | 所需令牌已匹配 |
| `agent-index.json#development_constitution_v1_1` | `F1-EA-04` | A | 所需字段已匹配 |
| `llms.txt:24-28` | `F1-EA-05` | A | 所需令牌已匹配 |
| `docs/product/SAEE_MODULE_REGISTRY.md` | `F1-EA-06R` | A | 所需令牌已匹配 |

这些对象已在隔离候选中按对象级或行级构造，不需要再次扩大授权，也不能换成当前主工作区整文件。

### 7.2 可从 `HEAD`（当前提交）继承

| 对象 | `HEAD`（当前提交）散列 | 所需令牌状态 | 分类 |
| --- | --- | --- | --- |
| `README.md`（项目说明） | `20c727ac05fe7b17c1b82d25525b29d7efdf412b45abf74062a044ce6289e711` | 两项均存在 | B |
| `.codex/context.md`（编码智能体上下文） | `47f8c87024d8e07d830bad11f3025961feee799c0cc35333bc1dab37c9951e10` | 两项均存在 | B |

当前 `README.md`（项目说明）存在 P1（契约父基线第一阶段）名称迁移变化，但这些变化不是宪法校验依赖，必须继续排除。

### 7.3 配置边界

校验器没有读取环境配置、用户配置、网络配置或运行时配置。机器配置性质的直接对象只有：

- 开发宪法机器契约；
- 开发宪法数据结构规范；
- 规范能力清单；
- `agent-index.json#development_constitution_v1_1`（智能体索引中的开发宪法对象）。

## 8. P1（契约父基线第一阶段）判断

```text
P1_DIRECT_DEPENDENCY_COUNT=0
P1_OBJECT_REQUIRED_FOR_CONSTITUTION_VALIDATION=false
```

内部 `evaluate_rehearsal_run`（内部排演运行评估）名称迁移、公开投影、九十九路径补丁及其测试都不是开发宪法校验器的直接或传递依赖。不得以“让校验通过”为理由把 P1 内容带入 F1。

## 9. 当前工作树参考闭环

为验证依赖识别没有遗漏，本次只读执行当前工作树中的开发宪法校验器：

```text
python3 scripts/saee_development_constitution_smoke.py
```

结果：

```text
CURRENT_WORKTREE_REFERENCE_VALIDATION_EXIT_CODE=0
CURRENT_WORKTREE_REFERENCE_VALIDATION_PASS=true
schema_cases=1/1
negative_cases=7/7
deterministic_runs=10/10
evolution_subsystems=9/9
canonical_reuse_routes=3/3
```

该结果只证明当前脏工作树中存在一个可运行的 `1.1.1` 参考闭包，不证明这组内容已经获准进入 F1，也不证明隔离候选已经自验证。

## 10. 最小后续授权范围

下一步若继续，只需为以下六项生成精确授权包：

```text
F1-VD-01=scripts/saee_development_constitution_smoke.py
F1-VD-02=agent-interface/governance/saee-development-constitution.v1.1.json
F1-VD-03=schemas/saee-development-constitution.schema.v1.1.json
F1-VD-04=docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
F1-VD-05=docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md
F1-VD-06=AGENTS.md:47-80
```

精确授权包必须：

1. 选择一致的 `1.1.1` 内容集合；
2. 记录每个完整文件或精确段落的目标散列；
3. 不复用当前暂存区的 `1.1.0` 版本；
4. 不复制整个当前 `AGENTS.md`（智能体规则文件）；
5. 不加入 README（项目说明）、能力清单或编码智能体上下文的当前工作区变化；
6. 不加入 P1、M03-M06、九十九路径补丁或可信基础设施材料。

```text
MINIMUM_ADDITIONAL_AUTHORIZATION_PACKAGE_REQUIRED=true
MINIMUM_ADDITIONAL_AUTHORIZATION_PACKAGE_CREATED=false
MINIMUM_ADDITIONAL_OBJECT_COUNT=6
```

## 11. 最终状态

```text
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
F1_BASELINE_AUTHORIZED=false
F1_CONSTITUTION_DEPENDENCY_ADDITION_AUTHORIZED=false
F1_SELF_VALIDATION_READY=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_F1_VALIDATOR_MINIMUM_ADDITIONAL_SCOPE
```
