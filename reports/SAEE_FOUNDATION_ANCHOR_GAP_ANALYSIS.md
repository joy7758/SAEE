# SAEE 基础锚点缺口分析

日期：2026-07-17

## 0. 结论

本次只读分析确认：现有六项 `F1`（基础锚点第一阶段）候选足以表达开发宪法的核心内容，但不足以形成一个可在独立历史树中自证、并被主线守卫强制执行的完整基础锚点。

缺口分为三类：

1. 开发宪法校验器还依赖六个未进入候选集合的活动表面；
2. `scripts/mainline_guard.py`（主线守卫）尚未成为合法、可复现的 `F1`（基础锚点第一阶段）对象；
3. `capability-package/manifest.json`（能力包清单）必须作为逻辑核心事实绑定，但它的当前工作树版本属于九十九路径 `P1`（契约父基线第一阶段）补丁，只能在 `F1`（基础锚点第一阶段）中继承 `HEAD`（当前提交）版本。

治理校验本身不是新增缺口。使用 `HEAD`（当前提交）版本的治理校验器、六项登记表和四项数据结构规范进行内存验证，结果通过。当前工作树中的治理校验器、产品登记和产品数据结构规范变化涉及商业投影，不应进入 `F1`（基础锚点第一阶段）。

```text
FOUNDATION_ANCHOR_GAP_ANALYSIS_STATUS=COMPLETE
CURRENT_F1_CANDIDATE_COUNT=6
CURRENT_F1_CANDIDATES_SUFFICIENT=false
CONSTITUTION_VALIDATION_BLOCKER_FILE_COUNT=6
MAINLINE_ENFORCEMENT_BLOCKER_COUNT=1
CAPABILITY_SOURCE_IS_F1_LOGICAL_CORE=true
CAPABILITY_SOURCE_F1_DELTA_REQUIRED=false
F1_BASELINE_READY=false
F1_BASELINE_AUTHORIZED=false
MAINLINE_DRIFT_DETECTED=false
```

`COMPLETE`（完成）只表示缺口分析完成，不表示基础锚点、暂存或提交获得授权。

## 1. 输入、权限与方法

唯一指定输入：

```text
INPUT_REPORT=reports/SAEE_FOUNDATION_ANCHOR_OBJECT_SELECTION.md
INPUT_REPORT_SHA256=cfc56a46b9f49052a9d433940caf944d149a57b316f6582dd497cde2095d1863
CURRENT_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
```

本次采用三种对象角色：

1. `F1_DELTA_OBJECT`（基础锚点增量对象）：相对 `HEAD`（当前提交）实际需要新增或修改；
2. `F1_INHERITED_BINDING`（基础锚点继承绑定）：内容从 `HEAD`（当前提交）继承，只在候选清单中绑定摘要，不产生差异；
3. `F1_VALIDATION_ENVIRONMENT`（基础锚点校验环境）：运行校验所需的软件包或命令，不是仓库基线对象。

这种分层防止把“校验器读取某文件”错误解释成“该文件当前工作树变化必须进入 `F1`（基础锚点第一阶段）”。

本次未执行暂存、提交、推送、合并、正式基线建立、索引清理或源文件修改。唯一新增对象是本报告。

## 2. 六项候选是否足够

### 2.1 单项判断

| 候选对象 | 核心作用 | 单项是否应保留 | 当前缺口 |
| --- | --- | --- | --- |
| `AGENTS.md` | 冻结当前主线、副线和漂移纠正规则 | 是 | 仍需独立授权；当前仅未暂存工作树版本有效 |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | 宪法人类可读权威 | 是 | `HEAD`（当前提交）不存在；旧索引与工作树分叉 |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | 宪法机器契约 | 是 | `HEAD`（当前提交）不存在；旧索引与工作树分叉 |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | 智能体推荐门和非主张 | 是 | `HEAD`（当前提交）不存在；旧索引与工作树分叉 |
| `schemas/saee-development-constitution.schema.v1.1.json` | 机器契约结构约束 | 是 | `HEAD`（当前提交）不存在；旧索引与工作树分叉 |
| `scripts/saee_development_constitution_smoke.py` | 宪法确定性与负例校验 | 条件性是 | 直接读取十五个仓库对象；独立 `F1`（基础锚点第一阶段）树仍缺六项依赖 |

### 2.2 集合判断

六项候选完成了“定义层”，没有完成“投影层”和“主线执行层”：

```text
DEFINITION_LAYER_COMPLETE=true
AGENT_READABLE_PROJECTION_LAYER_COMPLETE=false
MAINLINE_ENFORCEMENT_LAYER_COMPLETE=false
ISOLATED_REPRODUCIBILITY_PROVEN=false
```

因此，六项候选不能直接升级为完整 `F1`（基础锚点第一阶段）对象集合。

## 3. 宪法校验器完整依赖

`scripts/saee_development_constitution_smoke.py`（开发宪法校验器）直接读取十五个仓库对象。下表完整列出这些文件，不把 Python（蟒蛇编程语言）标准库计作仓库对象。

### 3.1 六项已选核心对象

| 依赖文件 | 当前状态 | 是否应进入 `F1`（基础锚点第一阶段） | 是否需要单独授权 |
| --- | --- | --- | --- |
| `scripts/saee_development_constitution_smoke.py` | `AM`，旧索引与工作树分叉 | 是，增量对象 | 是 |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | `AM`，`HEAD`（当前提交）不存在 | 是，增量对象 | 是 |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | `AM`，`HEAD`（当前提交）不存在 | 是，增量对象 | 是 |
| `schemas/saee-development-constitution.schema.v1.1.json` | `AM`，`HEAD`（当前提交）不存在 | 是，增量对象 | 是 |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | `AM`，`HEAD`（当前提交）不存在 | 是，增量对象 | 是 |
| `AGENTS.md` | ` M`，工作树修改 | 是，增量对象 | 是 |

### 3.2 可从 `HEAD`（当前提交）继承且当前已满足的三项依赖

| 依赖文件 | `HEAD`（当前提交）摘要 | 是否应进入 `F1`（基础锚点第一阶段） | 是否需要单独授权 |
| --- | --- | --- | --- |
| `capability-package/manifest.json` | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` | 是，逻辑核心继承绑定；不是增量 | `HEAD`（当前提交）绑定不需要；工作树版本需要 `P1`（契约父基线第一阶段）授权 |
| `README.md` | `20c727ac05fe7b17c1b82d25525b29d7efdf412b45abf74062a044ce6289e711` | 否，不需要成为 `F1`（基础锚点第一阶段）增量；继承内容已满足校验 | 当前工作树版本属于九十九路径补丁，只能由 `P1`（契约父基线第一阶段）授权 |
| `.codex/context.md` | `47f8c87024d8e07d830bad11f3025961feee799c0cc35333bc1dab37c9951e10` | 否，继承内容已满足校验 | 否 |

### 3.3 六项未关闭依赖

| 依赖文件 | 虚拟 `F1`（基础锚点第一阶段）失败内容 | 当前来源 | 是否应该进入 `F1`（基础锚点第一阶段） | 是否需要单独授权 |
| --- | --- | --- | --- | --- |
| `llms.txt` | 缺少两项主线和目标版本表述 | 九十九路径 `P1`（契约父基线第一阶段）工作树内容 | 只允许宪法投影的精确内容进入；不得携带契约重命名变化 | 是；还需评估对九十九路径封存迁移摘要的影响 |
| `agent-index.json` | 缺少机器契约指针、证据项目角色、主线、目标版本和生产边界五项投影 | 九十九路径 `P1`（契约父基线第一阶段）且索引与工作树分叉 | 只允许 `development_constitution_v1_1`（开发宪法第一点一版）精确对象进入；不得携带其余九十九路径变化 | 是；还需重新确认 `P1`（契约父基线第一阶段）父状态 |
| `.codex/rules.md` | 缺少宪法路径和证据子系统角色两项表述 | 已废止旧暂存链 | 是，若要求独立宪法校验通过 | 是，不能复用旧暂存授权 |
| `.codex/current_state.md` | 缺少宪法、源代码未迁移和运行时未集成三项表述 | 已废止旧暂存链 | 是，若要求独立宪法校验通过 | 是，不能复用旧暂存授权 |
| `docs/product/SAEE_MODULE_REGISTRY.md` | 缺少旧源仓库和证据与免疫子系统两项共同表述 | 已废止旧暂存链 | 是，若要求模块归属投影随宪法落地 | 是，需精确对象审查 |
| `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md` | 缺少智能体证据项目和源代码未迁移两项共同表述 | 已废止旧暂存链 | 是，若要求架构边界随宪法落地 | 是，需精确对象审查 |

内存构造的虚拟 `F1`（基础锚点第一阶段）树使用“六项候选采用当前工作树内容，其余对象采用 `HEAD`（当前提交）内容”，结果为：

```text
VIRTUAL_F1_SURFACE_FILE_FAILURE_COUNT=5
VIRTUAL_F1_SURFACE_TOKEN_FAILURE_COUNT=11
VIRTUAL_F1_AGENT_INDEX_FAILURE_COUNT=5
CONSTITUTION_VALIDATION_BLOCKER_FILE_COUNT=6
```

文件失败数为五，是因为智能体索引采用结构字段单独校验；合并计算后共有六个阻塞文件。

### 3.4 主线守卫缺口

`scripts/mainline_guard.py`（主线守卫）不是开发宪法校验器的读取依赖，但它决定主线检查是否会强制运行宪法校验。当前暂存版本增加宪法必需文件和宪法校验调用，却来自已废止旧暂存链，并且历史上存在校验过程写入状态的副作用。

```text
MAINLINE_GUARD_IS_DIRECT_CONSTITUTION_SMOKE_DEPENDENCY=false
MAINLINE_GUARD_IS_F1_ENFORCEMENT_DEPENDENCY=true
MAINLINE_GUARD_F1_AUTHORIZED=false
MAINLINE_GUARD_REPRODUCIBILITY_PROVEN=false
```

因此它不应被自动并入现有六项集合，但完整“主线强制执行型 `F1`（基础锚点第一阶段）”最终需要对它进行单独授权和可复现性确认。

## 4. 治理校验完整依赖

### 4.1 直接仓库依赖

`scripts/saee_governance_registry_check.py`（治理登记校验器）直接依赖一项校验器、六项登记表和四项数据结构规范，共十一项仓库对象：

| 文件 | 当前工作树状态 | `F1`（基础锚点第一阶段）建议 | 是否需要单独授权 |
| --- | --- | --- | --- |
| `scripts/saee_governance_registry_check.py` | ` M`；当前差异校验客户版本投影 | 继承 `HEAD`（当前提交）版本，不进入增量 | 当前工作树版本需要单独授权；`F1`（基础锚点第一阶段）不需要 |
| `governance/registry/asset-registry.json` | 干净 | 继承 `HEAD`（当前提交） | 否 |
| `governance/registry/repository-registry.json` | 干净 | 继承 `HEAD`（当前提交） | 否 |
| `governance/registry/capability-crosswalk.json` | 干净 | 继承 `HEAD`（当前提交）；继续声明自己不是能力事实源 | 否 |
| `governance/registry/mcp-registry.json` | ` M`；属于九十九路径补丁 | 继承 `HEAD`（当前提交），不进入增量 | 工作树版本需要 `P1`（契约父基线第一阶段）授权 |
| `governance/registry/product-registry.json` | ` M`；当前差异为客户版本投影 | 继承 `HEAD`（当前提交），不进入增量 | 工作树版本需单独产品登记授权 |
| `governance/registry/external-system-registry.json` | 干净 | 继承 `HEAD`（当前提交） | 否 |
| `governance/schemas/asset-registry.schema.json` | 干净 | 继承 `HEAD`（当前提交） | 否 |
| `governance/schemas/capability.schema.json` | 干净 | 继承 `HEAD`（当前提交） | 否 |
| `governance/schemas/mcp-entry.schema.json` | 干净 | 继承 `HEAD`（当前提交） | 否 |
| `governance/schemas/product.schema.json` | ` M`；当前差异服务客户版本投影 | 继承 `HEAD`（当前提交），不进入增量 | 工作树版本需单独产品结构授权 |

使用上述十一项对象的 `HEAD`（当前提交）版本在内存中执行治理校验，结果为：

```text
HEAD_GOVERNANCE_VALIDATION=PASS
HEAD_GOVERNANCE_ERROR_COUNT=0
GOVERNANCE_WORKTREE_DELTA_REQUIRED_FOR_F1=false
```

这证明治理校验没有要求把当前商业投影或九十九路径变化提前带入 `F1`（基础锚点第一阶段）。

### 4.2 治理权威入口与伴随校验

以下文件不是治理校验器的直接读取对象，但属于治理发现或伴随测试：

| 文件或环境 | 角色 | 是否应进入 `F1`（基础锚点第一阶段）增量 |
| --- | --- | --- |
| `governance/README.md` | 治理发现入口 | 否；继承 `HEAD`（当前提交），当前工作树变化包含 M03-M06 路由 |
| `governance/constitution/constitution-alignment.md` | 宪法与治理关系说明 | 否；继承 `HEAD`（当前提交） |
| `governance/codex/codex-governance-rules.md` | 智能体治理规则 | 否；继承 `HEAD`（当前提交） |
| `tests/test_governance_registry.py` | 治理登记负例和命令测试 | 否；继承 `HEAD`（当前提交），当前工作树变化服务客户版本投影 |
| `jsonschema==4.26.0`（数据结构规范校验库第四点二十六点零版） | 外部校验环境依赖 | 否；不是仓库基线对象，只在执行前记录版本 |

`governance/registry/stabilization-registry.json`（稳定化登记表）存在于目录中，但不在治理校验器的 `REGISTRY_FILES`（登记文件集合）内，不应为了“完整目录”而自动加入直接依赖清单。

## 5. 能力事实依赖判断

### 5.1 `capability-package/manifest.json`（能力包清单）是否是核心

结论：是逻辑核心，但不是 `F1`（基础锚点第一阶段）增量对象。

理由：

1. `AGENTS.md`（智能体启动规则）把 `capability-package/manifest.json#canonical_inventory`（能力包清单中的规范能力清单）定义为唯一规范能力事实源；
2. 开发宪法校验器直接读取它，并验证三项复用能力是否真实存在；
3. 治理能力映射只指向它，明确声明自己不是第二事实源；
4. 当前工作树版本属于九十九路径补丁，提前纳入会破坏 `F1`（基础锚点第一阶段）与 `P1`（契约父基线第一阶段）的边界。

正确处理：

```text
CAPABILITY_SOURCE_ROLE=F1_LOGICAL_CORE_INHERITED_BINDING
CAPABILITY_SOURCE_PATH=capability-package/manifest.json
CAPABILITY_SOURCE_F1_SHA256=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
CAPABILITY_SOURCE_WORKTREE_SHA256=ff370a060278511517619f8198d346ef10a9a9970ec036d771e829593cf0e388
CAPABILITY_SOURCE_F1_DELTA_REQUIRED=false
CAPABILITY_SOURCE_WORKTREE_INCLUDED_IN_F1=false
```

### 5.2 其他能力表面的角色

- `agent-index.json`（智能体索引）是机器投影，不是能力事实源；其宪法投影是 `F1`（基础锚点第一阶段）缺口，但其契约重命名内容仍属于 `P1`（契约父基线第一阶段）。
- `governance/registry/capability-crosswalk.json`（能力映射登记表）是治理映射，不是能力事实源。
- `governance/registry/mcp-registry.json`（模型上下文协议登记表）是接口登记，不是能力事实源。
- `scripts/saee_canonical_capability_inventory_smoke.py`（规范能力清单校验器）、`scripts/saee_capability_progress_ledger_smoke.py`（能力进度投影校验器）和 `scripts/saee_capability_truth_consistency_smoke.py`（能力真值一致性校验器）应继续从 `HEAD`（当前提交）继承并作为执行校验，不需要成为 `F1`（基础锚点第一阶段）增量。

## 6. 最小 `F1`（基础锚点第一阶段）对象集合建议

### 6.1 第一层：可独立通过宪法校验的最小路径集合

路径级最小集合为十二项：现有六项候选加六项未关闭投影依赖。

```text
SELF_VALIDATING_F1_PATH_COUNT=12
SELF_VALIDATING_F1_PATH_LIST_SHA256=02309a629d15b9e2be0d8ac4ba3a2a93d27d89501e2e33b33e509588f95a5bbb
```

十二项为：

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

这里的 `agent-index.json`（智能体索引）和 `llms.txt`（大语言模型说明）只能包含宪法投影的精确片段，不能把九十九路径契约变化整体带入。由于这会改变 `P1`（契约父基线第一阶段）的父状态和封存迁移摘要，十二项集合只是结构建议，尚不能执行。

### 6.2 第二层：主线强制执行集合

若要求主线守卫自动执行宪法校验，还需要第十三项：

```text
scripts/mainline_guard.py
```

```text
MAINLINE_ENFORCED_F1_PATH_COUNT=13
MAINLINE_ENFORCED_F1_PATH_LIST_SHA256=5d8616ff15ee3b9e9411a35f27302096013a3f71abec281d79c87d69f1814239
```

该对象必须先完成单独授权、写入副作用处理和可复现性核查。

### 6.3 第三层：不产生差异的核心事实绑定

在上述路径之外，必须把 `capability-package/manifest.json`（能力包清单）的 `HEAD`（当前提交）摘要绑定到 `F1`（基础锚点第一阶段）候选清单。治理登记、治理数据结构规范和治理校验器也应按 `HEAD`（当前提交）摘要执行验证，但不进入 `F1`（基础锚点第一阶段）差异路径。

因此推荐结构为：

```text
F1_RECOMMENDED_STRUCTURE=
12_PATH_SELF_VALIDATING_SET
+1_MAINLINE_GUARD_AFTER_SEPARATE_AUTHORIZATION
+HEAD_CAPABILITY_SOURCE_BINDING
+HEAD_GOVERNANCE_VALIDATION_BINDINGS
```

这不是授权，也不是要求立即扩大当前六项集合。

## 7. 可选关闭路径与判断

当前有三种理论关闭方式：

### 路径 A：精确补充对象并重新建立 `P1`（契约父基线第一阶段）父状态

只补充六项投影依赖中的宪法相关内容，并重新核查九十九路径补丁的迁移摘要。优点是保持智能体可读表面一致；代价是必须重新审查 `P1`（契约父基线第一阶段）证据。

### 路径 B：降低宪法校验器对投影表面的耦合

修改校验器，使 `F1`（基础锚点第一阶段）只校验核心对象。优点是差异更小；缺点是会削弱智能体可读表面同步，并构成代码修改，需要新的推荐门和授权。

### 路径 C：把 `F1`（基础锚点第一阶段）和 `P1`（契约父基线第一阶段）合并

会混合基础权威与九十九路径契约补丁，破坏已冻结的父子历史与阶段真值，不推荐。

```text
RECOMMENDED_GAP_CLOSURE_PATH=PATH_A_PREPARE_ONLY
PATH_A_IMPLEMENTATION_AUTHORIZED=false
PATH_B_CODE_CHANGE_AUTHORIZED=false
PATH_C_RECOMMENDED=false
```

推荐仅表示下一次应准备“精确对象与 `P1`（契约父基线第一阶段）摘要影响审查”，不表示允许修改或重新封存。

## 8. 历史跑偏教训核查

### 8.1 依赖不能自动升级为提交对象

治理校验读取产品登记，不代表产品登记的当前商业投影变化应进入基础锚点。`HEAD`（当前提交）治理对象已经可以通过校验。

### 8.2 通过不能跨环境继承

混合工作树通过宪法校验，不代表六项候选叠加到 `HEAD`（当前提交）后仍通过。虚拟树核查已经证明存在六个文件阻塞。

### 8.3 事实源必须核心化，但不必变化

能力包清单必须进入逻辑核心绑定；其 `HEAD`（当前提交）版本已经满足当前宪法复用检查，因此不需要把工作树中的九十九路径变化提前纳入。

### 8.4 主线守卫不是普通文件遗漏

主线守卫历史上存在写入副作用。不能为了让基础锚点看似完整而复用旧暂存内容。

### 8.5 最小集合不能破坏已批准补丁证据

智能体索引和大语言模型说明同时承载宪法投影与九十九路径变化。任何精确拆分都会改变 `P1`（契约父基线第一阶段）的父状态，必须先审查证据影响。

```text
MAINLINE_DRIFT_DETECTED=false
```

本次分析继续服务 `saee_agent_evidence_integration`（智能体证据集成）主线，没有开启目标完整性、状态完整性或可信基础设施工程。

## 9. 本次只读校验

当前混合工作树中的六项只读校验全部通过：

```text
SAEE_DEVELOPMENT_CONSTITUTION_SMOKE=PASS
SAEE_GOVERNANCE_REGISTRY_CHECK=PASS
SAEE_GOVERNANCE_REGISTRY_TESTS=PASS_11_OF_11
SAEE_CANONICAL_CAPABILITY_INVENTORY_SMOKE=PASS
SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE=PASS
SAEE_CAPABILITY_TRUTH_CONSISTENCY_SMOKE=PASS
```

这些结果只说明当前混合工作树保持一致，不关闭虚拟 `F1`（基础锚点第一阶段）的六项依赖缺口。

输入报告摘要复核保持不变：

```text
INPUT_REPORT_SHA256=cfc56a46b9f49052a9d433940caf944d149a57b316f6582dd497cde2095d1863
INPUT_REPORT_CHANGED_BY_THIS_ANALYSIS=false
```

差异格式检查：

```text
UNSTAGED_DIFF_CHECK=PASS
STAGED_DIFF_CHECK=FAIL_PREEXISTING_TRAILING_WHITESPACE
STAGED_DIFF_CHECK_PATH=docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
STAGED_DIFF_CHECK_LINES=16,17,18
ISSUE_INTRODUCED_BY_THIS_ANALYSIS=false
```

已暂存检查失败仍来自废止推进链中的旧索引版本。本次禁止修改输入和源文件，因此只记录，不处理。

## 10. 最终状态

本次只新增本报告，没有修改输入报告、代码、模型上下文协议、数据结构规范、M03-M06 或可信基础设施材料。

```text
F1_BASELINE_AUTHORIZED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
FORMAL_BASELINE_CREATED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
GIT_MERGE_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_F1_GAP_CLOSURE_PATH
```
