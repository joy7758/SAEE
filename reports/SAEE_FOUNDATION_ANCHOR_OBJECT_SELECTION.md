# SAEE 基础锚点对象选择

日期：2026-07-17

## 0. 结论

本次只读审查以 `reports/SAEE_CURRENT_WORKSPACE_TRUTH_RECONSTRUCTION.md` 中冻结的 A 类一百四十八项为选择母集。结论是：可以从其中识别出六项 `F1`（基础锚点第一阶段）核心增量候选，但当前不能授权或建立 `F1`（基础锚点第一阶段）。

六项候选只覆盖：开发宪法人类可读文件、机器契约、数据结构规范、推荐门、宪法校验器和 `AGENTS.md`（智能体启动规则）中的主线规则。九十九路径补丁、M03-M06 材料、可信基础设施未来研究、历史报告和商业投影均未进入该候选增量。

规范能力清单、智能体索引投影和模型上下文协议登记表是 `F1`（基础锚点第一阶段）最终树必须继承的事实面，但它们当前属于九十九路径 `P1`（契约父基线第一阶段）补丁。为保持父子历史边界，`F1`（基础锚点第一阶段）只能继承 `HEAD`（当前提交）版本并绑定摘要，不能提前包含其工作树变化。

```text
FOUNDATION_ANCHOR_OBJECT_SELECTION_STATUS=COMPLETE
FROZEN_A_CLASS_SOURCE_COUNT=148
F1_MINIMAL_DELTA_CANDIDATE_COUNT=6
F1_MINIMAL_DELTA_CANDIDATE_PATH_LIST_SHA256=7425a4a6753b16786a4c9778764173f4db2eb1a60776112164208d1500963b57
F1_MINIMAL_DELTA_CANDIDATE_MANIFEST_SHA256=c9d82fa63f19c7cb1b7803ed234eadd011dd186abb0c959650e842782dbf5194
F1_OBJECT_SET_COMPLETE=false
F1_BASELINE_READY=false
F1_BASELINE_AUTHORIZED=false
MAINLINE_DRIFT_DETECTED=false
```

`COMPLETE`（完成）只表示对象选择审查完成；`false`（否）表示候选集合尚未满足独立基线执行条件。

## 1. 审查边界与当前快照

```text
REPOSITORY_ROOT=/Users/zhangbin/Documents/SAEE
CURRENT_BRANCH=feat/canonical-capability-inventory-routing-v1
CURRENT_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
A_CLASS_SOURCE_REPORT=reports/SAEE_CURRENT_WORKSPACE_TRUTH_RECONSTRUCTION.md
A_CLASS_PATH_LIST_SHA256=792adab40cbee8b7d87f828178bb7ffc4d3afd04b3755e0bdad2bf8d15884520
```

本次创建报告前，当前可见工作区状态为：

```text
STAGED_PATH_COUNT=12
UNSTAGED_PATH_COUNT=160
UNTRACKED_PATH_COUNT=181
VISIBLE_DIRTY_PATH_COUNT=346
```

冻结报告中的 A 类一百四十八项是选择母集，不是对当前全部工作区变化重新分类。当前总变化数量已经低于冻结时点；本次仅重新核查与 `F1`（基础锚点第一阶段）相关对象，未把其他对话或后续变化自动纳入 A 类。

本次没有执行暂存、提交、推送、合并、索引清理或工作树恢复。

## 2. “包含”的精确定义

Git（版本控制系统）提交的最终树天然继承父提交中的大量文件。若把“`F1`（基础锚点第一阶段）不得包含历史报告或商业投影”解释为最终树中不得存在这些父文件，就必须删除父提交已有内容，这既不符合本次授权，也会制造额外变化。

因此本次采用两层定义：

1. `F1_DELTA`（基础锚点增量）：`F1`（基础锚点第一阶段）相对 `HEAD`（当前提交）实际新增或修改的路径；禁止包含九十九路径补丁、M03-M06、可信基础设施、历史报告和商业投影。
2. `F1_FINAL_TREE_INHERITANCE`（基础锚点最终树继承）：从 `HEAD`（当前提交）继承的既有文件；只绑定关键权威摘要，不把继承文件误写成 `F1`（基础锚点第一阶段）新增内容。

```text
F1_DELTA_CONTAINS_99_PATH_PATCH=false
F1_DELTA_CONTAINS_M03_M06=false
F1_DELTA_CONTAINS_TRUST_INFRASTRUCTURE=false
F1_DELTA_CONTAINS_HISTORICAL_REPORTS=false
F1_DELTA_CONTAINS_COMMERCIAL_PROJECTION=false
CAPABILITY_SOURCE_BINDING_MODE=INHERIT_HEAD
```

## 3. A 类一百四十八项筛选账目

| A 类子集 | 数量 | `F1`（基础锚点第一阶段）处理 | 数量核对 |
| --- | ---: | --- | ---: |
| 九十九路径契约补丁 | 99 | 三项基础相关事实面仅继承 `HEAD`（当前提交）；其余九十六项全部排除 | 99 |
| M03-M06 有效对象 | 24 | 全部排除，保持后续独立基线 | 24 |
| 可信基础设施未来研究 | 9 | 全部排除，只保持未来研究身份 | 9 |
| 当前主线只读报告 | 5 | 全部排除，不把报告变成基础权威 | 5 |
| 当前宪法与治理权威候选 | 11 | 六项进入核心增量候选，五项排除或延期 | 11 |
| 合计 | 148 | 集合不重叠 | 148 |

```text
A_CLASS_SELECTION_ACCOUNTED=148/148
A_CLASS_SELECTION_OVERLAP_COUNT=0
A_CLASS_UNCLASSIFIED_COUNT=0
```

## 4. 六项 `F1`（基础锚点第一阶段）核心增量候选

下表的“进入 `F1`（基础锚点第一阶段）”表示进入候选增量，不表示已获暂存或提交授权。`AM` 表示索引中是新增对象、工作树又有后续修改；当前索引版本不得复用。

| 文件路径 | `HEAD`（当前提交）状态 | 工作树状态 | 当前工作树 SHA-256（安全散列算法二百五十六位） | 进入 `F1`（基础锚点第一阶段） | 是否需要单独授权 |
| --- | --- | --- | --- | --- | --- |
| `AGENTS.md` | 已跟踪；摘要 `1dfbfbc6812358d38587add9fc1366744c8aec0049f7b0e5fb271994ff29bad0` | ` M`，仅未暂存修改 | `dda93831c03be32b0698c51bea04b9b6fff045f96c5912db61d08406626bceae` | 是，主线与副线优先级规则 | 是，需 `F1`（基础锚点第一阶段）实施授权 |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | 不存在 | `AM`，旧索引与工作树分叉 | `37d9adb3049c5fdd871460f6756240a177264e4442cc38252786e9d7c86f378c` | 是，宪法人类可读权威 | 是，且只能使用工作树摘要 |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | 不存在 | `AM`，旧索引与工作树分叉 | `df200d13ec90ce5dd57cedb4ceab83b1c2a5b751b68af35a1a749f39db15f8a0` | 是，宪法机器契约 | 是，且只能使用工作树摘要 |
| `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | 不存在 | `AM`，旧索引与工作树分叉 | `1bc493e03e3158e2d984308a78efa80cde131a5b9ee2142449695c807433ee9c` | 是，智能体推荐门 | 是，且只能使用工作树摘要 |
| `schemas/saee-development-constitution.schema.v1.1.json` | 不存在 | `AM`，旧索引与工作树分叉 | `dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86` | 是，机器契约结构约束 | 是，且只能使用工作树摘要 |
| `scripts/saee_development_constitution_smoke.py` | 不存在 | `AM`，旧索引与工作树分叉 | `8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550` | 条件性是，宪法确定性校验器 | 是；依赖阻塞关闭后才能进入 |

六项路径清单按字节排序后的摘要为：

```text
F1_MINIMAL_DELTA_CANDIDATE_PATH_LIST_SHA256=7425a4a6753b16786a4c9778764173f4db2eb1a60776112164208d1500963b57
```

按“路径、文件权限、当前工作树 SHA-256（安全散列算法二百五十六位）”绑定的候选清单摘要为：

```text
F1_MINIMAL_DELTA_CANDIDATE_MANIFEST_SHA256=c9d82fa63f19c7cb1b7803ed234eadd011dd186abb0c959650e842782dbf5194
```

## 5. 五项 A 类权威候选不进入 `F1`（基础锚点第一阶段）

| 文件路径 | `HEAD`（当前提交）状态 | 工作树状态 | 当前工作树 SHA-256（安全散列算法二百五十六位） | 是否进入 `F1`（基础锚点第一阶段） | 是否需要单独授权 |
| --- | --- | --- | --- | --- | --- |
| `governance/README.md` | 已跟踪；摘要 `87e0adc4e37810242aabe1df5e9a7c10e5d157ce01a1e40f28dd1be86f9f7078` | ` M` | `93d09d9d7e9651280a1a7132f8c1f122e29131cef4c15e93845558c1924d8b80` | 否；当前修改引入 M03-M06 和项目记忆入口 | 未来若纳入需单独授权 |
| `governance/registry/product-registry.json` | 已跟踪；摘要 `4ab926b5439c11fa0c86d4b0d35a15aa6cddfcd71e040449e1c69f54034a7921` | ` M` | `62c9ee638a4e763e60d2290cdf6fa2bbeabf93373ced8fa4af084203146a316d` | 否；当前修改是客户版本和产品投影 | 未来产品登记变更需单独授权 |
| `governance/schemas/product.schema.json` | 已跟踪；摘要 `055b68b204e11c9df8d70fab07d68de1efefeb891a75aceb4acf46a8ac191f79` | ` M` | `d4e7f2c6948819d40b9f8df8ca1f8b37098a966f120997623420909b37ab5323` | 否；服务于上述产品投影 | 是，不能借基础锚点修改产品结构规范 |
| `scripts/saee_governance_registry_check.py` | 已跟踪；摘要 `de6b113f62a61c2bfda12b42d8b571ce97022869221bfb20f54a1a56df8b3607` | ` M` | `06beb37f671e6bfdd4b47a39514aa86db74679e33648098bb9ac44ff77c520d5` | 否；当前差异校验产品目标版本 | 是，需与产品登记变更共同决定 |
| `tests/test_governance_registry.py` | 已跟踪；摘要 `068fbc202aee7dd50eb3b842f49b9a8ff97d815e0d190b15620de80a604c6ff8` | ` M` | `25c017806c73ee1d1c98906e593a82f910ad0a80f01c5b13fd24f72971f822b1` | 否；当前差异测试产品目标版本 | 是，需与产品登记变更共同决定 |

这些文件的父提交版本会自然留在最终树中，但它们的当前工作树变化不属于 `F1`（基础锚点第一阶段）增量。

## 6. 九十九路径中三项基础相关事实面

九十九路径补丁中的以下三项与基础权威有关，但不能进入 `F1`（基础锚点第一阶段）增量：

| 文件路径 | `HEAD`（当前提交）状态 | 工作树状态 | `HEAD`（当前提交）SHA-256（安全散列算法二百五十六位） | `F1`（基础锚点第一阶段）处理 | 是否需要单独授权 |
| --- | --- | --- | --- | --- | --- |
| `capability-package/manifest.json` | 已跟踪 | ` M`，属于九十九路径补丁 | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` | 继承 `HEAD`（当前提交），作为当前规范能力事实源 | 工作树变化只可由 `P1`（契约父基线第一阶段）授权 |
| `agent-index.json` | 已跟踪 | `MM`，旧索引与九十九路径工作树版本分叉 | `90f870a8cb6400096052def1615c878ea03c7558aef85c23d20618e1c5b8cccc` | 继承 `HEAD`（当前提交），不使用当前索引或工作树版本 | 是，`P1`（契约父基线第一阶段）另行授权 |
| `governance/registry/mcp-registry.json` | 已跟踪 | ` M`，属于九十九路径补丁 | `fdeda93c44104c61efcdcea2ea2703a919630a68b2af96b12438d45834258a76` | 继承 `HEAD`（当前提交），不提前迁移内部标识 | 是，`P1`（契约父基线第一阶段）另行授权 |

其余九十六项九十九路径补丁全部排除，不逐项升级为 `F1`（基础锚点第一阶段）候选。

```text
P1_CONTRACT_PATCH_PATH_COUNT=99
F1_DELTA_P1_PATH_INTERSECTION=0
F1_FINAL_TREE_CAPABILITY_SOURCE_PRESENT=true
F1_FINAL_TREE_CAPABILITY_SOURCE_SHA256=fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70
```

## 7. 从 `HEAD`（当前提交）继承的稳定基础对象

以下对象不在 A 类一百四十八项变化母集中，因为当前工作树与 `HEAD`（当前提交）一致。它们无需成为 `F1`（基础锚点第一阶段）增量，只需在未来隔离候选中校验摘要：

| 文件路径 | `HEAD`（当前提交）与工作树 SHA-256（安全散列算法二百五十六位） | 角色 |
| --- | --- | --- |
| `governance/constitution/constitution-alignment.md` | `dd38b8beb3f0f7d34d1c8f62a5d928b92e288e20311672526ddb5d73f52ec9f1` | 宪法对齐说明 |
| `governance/registry/asset-registry.json` | `dfadbdd8a71ca964c26f1286c1adfe255c98013f21199356b313de7d11375307` | 资产登记事实 |
| `governance/registry/repository-registry.json` | `ff2803f97a05677658f5f6674a0cdd698a38d4cc3c5c974ceeee42923301b961` | 仓库登记事实 |
| `governance/registry/capability-crosswalk.json` | `e215d18ee54957666e33f0387951e2db9b533ef19819cee8c7e06cdd421528da` | 能力映射参考 |
| `governance/codex/codex-governance-rules.md` | `20f7382dd94459ce299488fad9e4ed8aaa836f75d53378937471421a48099b18` | 执行规则 |
| `scripts/saee_canonical_capability_inventory_smoke.py` | `06224ef7190b25f66c41338a0d58add46a6f4d8d8e8939c2a8b62ce245962cb3` | 规范能力清单校验 |
| `scripts/saee_capability_progress_ledger_smoke.py` | `d03bdc56532278eba9cd40d5f5542e4ff3bfe584a3cdb1998f53b56403c526a2` | 能力进度投影校验 |
| `scripts/saee_capability_truth_consistency_smoke.py` | `d8cf89edd7f56effc90f3165ee17a518b427859cec45d3180ad6ddaa80a36c1c` | 能力真值一致性校验 |

## 8. 尚未关闭的验证依赖

当前 `scripts/saee_development_constitution_smoke.py`（开发宪法校验器）在混合工作树中可以通过，但它检查的表面不只来自六项候选。如果只把六项候选叠加到 `HEAD`（当前提交），以下六项依赖仍不能满足：

| 依赖对象 | 当前来源 | `F1`（基础锚点第一阶段）处理 |
| --- | --- | --- |
| `llms.txt` | 九十九路径 `P1`（契约父基线第一阶段）补丁 | 禁止提前带入；`HEAD`（当前提交）缺少校验器要求的主线与目标版本表述 |
| `agent-index.json` | 九十九路径 `P1`（契约父基线第一阶段）补丁且索引分叉 | 禁止提前带入；`HEAD`（当前提交）缺少校验器要求的宪法投影 |
| `.codex/rules.md` | 已废止旧暂存链 | 不在 A 类一百四十八项内，需单独决定 |
| `.codex/current_state.md` | 已废止旧暂存链 | 不在 A 类一百四十八项内，需单独决定 |
| `docs/product/SAEE_MODULE_REGISTRY.md` | 已废止旧暂存链 | 不在 A 类一百四十八项内，需单独决定 |
| `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md` | 已废止旧暂存链 | 不在 A 类一百四十八项内，需单独决定 |

`README.md`（项目说明）和 `.codex/context.md`（智能体上下文）所需表述已经存在于 `HEAD`（当前提交），无需进入增量。规范能力清单也可以使用 `HEAD`（当前提交）版本完成三项能力复用检查。

因此，混合工作树中的校验通过不能证明六项候选在独立 `F1`（基础锚点第一阶段）树中会通过。

```text
CURRENT_MIXED_WORKTREE_CONSTITUTION_SMOKE_PASS=true
ISOLATED_F1_CONSTITUTION_SMOKE_PROVEN=false
F1_VALIDATION_DEPENDENCY_BLOCKER_COUNT=6
F1_OBJECT_SET_COMPLETE=false
```

另有 `scripts/mainline_guard.py`（主线守卫）当前仅处于已废止旧索引修改状态，不属于 A 类一百四十八项。它不能被本次选择自动纳入：

```text
MAINLINE_GUARD_A_CLASS_MEMBER=false
MAINLINE_GUARD_CURRENT_STATUS=STAGED_FROM_RETIRED_CHAIN
MAINLINE_GUARD_F1_INCLUDED=false
MAINLINE_GUARD_REQUIRES_SEPARATE_AUTHORIZATION=true
```

## 9. 排除对象确认

### 9.1 M03-M06

二十四项 A 类有效 M03-M06 对象全部排除，继续等待父基线完成后的独立决策。

```text
M03_M06_A_CLASS_OBJECT_COUNT=24
M03_M06_INCLUDED_IN_F1=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
```

### 9.2 可信基础设施未来研究

九项未来研究对象全部排除，不进入当前工程历史锚点。

```text
TRUST_INFRASTRUCTURE_A_CLASS_OBJECT_COUNT=9
TRUST_INFRASTRUCTURE_INCLUDED_IN_F1=false
FUTURE_RESEARCH_ONLY=true
```

### 9.3 当前主线只读报告

五项报告保持事实输入身份，不成为宪法或能力事实权威。

```text
CURRENT_READONLY_REPORT_COUNT=5
CURRENT_READONLY_REPORTS_INCLUDED_IN_F1=false
```

### 9.4 商业投影

产品登记表、产品结构规范及其当前校验变化均排除。目标客户版本表述只保留在宪法候选中，不能由此推导产品已经实现、发布或完成客户验证。

```text
COMMERCIAL_PROJECTION_INCLUDED_IN_F1=false
CUSTOMER_VERSION_TARGET_IS_IMPLEMENTATION_CLAIM=false
```

## 10. 授权与建立条件

本次不建议直接授权建立 `F1`（基础锚点第一阶段）。未来至少需要：

1. 人工确认六项核心候选及其当前工作树摘要；
2. 决定校验器依赖采用“精确补充授权”还是“降低校验器对非基础表面的耦合”；后者属于修改，不能由本报告执行；
3. 单独决定 `scripts/mainline_guard.py`（主线守卫）的旧暂存内容，不得默认复用；
4. 在全新隔离工作区从 `CURRENT_HEAD`（当前提交）重建候选，不使用当前十二项旧索引；
5. 确认 `F1`（基础锚点第一阶段）差异路径与九十九路径补丁交集为零；
6. 在隔离候选中运行全部只读校验并保存失败结果；
7. 再申请独立暂存和提交授权。

本次最小对象选择没有把校验缺口伪装为已就绪，也没有为通过校验而扩大对象集合。

```text
F1_SELECTION_RECOMMENDATION=ACCEPT_CORE_SET_BUT_CLOSE_VALIDATION_DEPENDENCIES_FIRST
F1_STAGING_AUTHORIZED=false
F1_COMMIT_AUTHORIZED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
```

其中建议常量表示“接受核心集合，但先关闭校验依赖”，不表示执行授权。

## 11. 历史跑偏教训核查

### 11.1 旧暂存不等于当前真值

五项新宪法对象的索引摘要都不同于工作树摘要。任何未来动作只能从本报告绑定的工作树内容重建，不能沿用旧索引。

### 11.2 混合工作树通过不等于隔离基线通过

当前宪法校验器会读取九十九路径补丁和旧暂存链中的表面；当前通过不能替代独立候选验证。

### 11.3 基础锚点不能吞并父补丁

规范能力清单是事实源，但它的当前工作树变化属于九十九路径补丁。`F1`（基础锚点第一阶段）继承 `HEAD`（当前提交）版本即可，不能以“能力事实必需”为由提前吸收 `P1`（契约父基线第一阶段）。

### 11.4 治理对象不等于都应进入治理提交

治理说明、产品登记、产品结构规范和测试虽然都与治理有关，但当前差异分别包含 M03-M06 路由或商业投影，不符合基础锚点的最小边界。

### 11.5 报告完成不等于基线授权

本报告只完成选择和阻塞识别。任何暂存、提交、推送、合并或清理仍需明确人工授权。

```text
MAINLINE_DRIFT_DETECTED=false
```

本次继续服务 `saee_agent_evidence_integration`（智能体证据集成）主线，没有重启目标完整性、状态完整性或可信基础设施工程。

## 12. 本次只读校验

使用 `PYTHONDONTWRITEBYTECODE=1`（禁止写入 Python 字节码）运行五项当前混合工作树校验，全部通过：

```text
SAEE_DEVELOPMENT_CONSTITUTION_SMOKE=PASS
SAEE_GOVERNANCE_REGISTRY_CHECK=PASS
SAEE_CANONICAL_CAPABILITY_INVENTORY_SMOKE=PASS
SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE=PASS
SAEE_CAPABILITY_TRUTH_CONSISTENCY_SMOKE=PASS
CANONICAL_CAPABILITY_COUNT=9
PROGRAM_MAINLINE=saee_agent_evidence_integration
SOURCE_CODE_MIGRATED=false
RUNTIME_INTEGRATED=false
PRODUCTION_READY=false
```

这些结果只证明当前混合工作树内部一致，不能替代未来隔离 `F1`（基础锚点第一阶段）候选的重新验证。宪法校验输出中的 `mainline_drift_correction_required=true` 表示“发现主线漂移时必须纠正”的规则，不表示本次检测到主线漂移。

差异格式检查结果：

```text
UNSTAGED_DIFF_CHECK=PASS
STAGED_DIFF_CHECK=FAIL_PREEXISTING_TRAILING_WHITESPACE
STAGED_DIFF_CHECK_PATH=docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
STAGED_DIFF_CHECK_LINES=16,17,18
ISSUE_INTRODUCED_BY_THIS_REVIEW=false
```

已暂存检查失败来自废止推进链中的旧索引版本；当前工作树版本不含该三处尾随空格。本次禁止修改索引或宪法文件，因此只记录，不越权修复。

## 13. 本次动作与最终状态

本次只新增本报告；没有修改代码、模型上下文协议、数据结构规范、M03-M06 或可信基础设施材料。

```text
F1_BASELINE_AUTHORIZED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
M03_M06_CHANGED=false
TRUST_INFRASTRUCTURE_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
GIT_MERGE_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_F1_OBJECT_SELECTION_AND_VALIDATION_DEPENDENCIES
```
