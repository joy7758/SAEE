# SAEE 基础锚点精确范围审查

日期：2026-07-17

## 0. 结论

本次审查完成了六个指定文件对象的逐字段、逐段落和逐差异片段范围判断。

结论不是“六个文件全部进入 `F1`（基础锚点第一阶段）”。真实边界为：

1. 三个对象的当前工作树差异纯粹服务开发宪法、治理环境和证据子系统边界，应归入 `F1_REQUIRED`（必须进入基础锚点）；
2. 三个对象在同一文件内混合了 `F1`（基础锚点第一阶段）、`P1`（契约父基线第一阶段）、`HEAD`（当前提交）继承内容或另行授权内容，整文件必须归入 `SEPARATE_AUTHORIZATION_REQUIRED`（需要单独授权）；
3. 没有任何混合文件可以通过整文件暂存进入 `F1`（基础锚点第一阶段）；
4. `P1`（契约父基线第一阶段）内容、M03-M06（智能体证据集成第三至第六里程碑）材料和架构真值表面对齐对象不得被基础锚点顺带吸收。

```text
FOUNDATION_ANCHOR_PRECISION_SCOPE_REVIEW_STATUS=COMPLETE
REVIEWED_FILE_COUNT=6
F1_REQUIRED_FILE_COUNT=3
P1_ONLY_FILE_COUNT=0
HEAD_INHERIT_ONLY_FILE_COUNT=0
SEPARATE_AUTHORIZATION_REQUIRED_FILE_COUNT=3
F1_MIXED_SURFACE_FILE_COUNT=3
F1_BASELINE_READY=false
MAINLINE_DRIFT_DETECTED=false
```

这里的 `COMPLETE`（完成）只表示范围审查完成，不表示基础锚点、契约父基线、暂存或提交已获授权。

## 1. 输入、快照和审查方法

### 1.1 输入绑定

```text
CURRENT_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
INPUT_OBJECT_SELECTION=reports/SAEE_FOUNDATION_ANCHOR_OBJECT_SELECTION.md
INPUT_OBJECT_SELECTION_SHA256=cfc56a46b9f49052a9d433940caf944d149a57b316f6582dd497cde2095d1863
INPUT_GAP_ANALYSIS=reports/SAEE_FOUNDATION_ANCHOR_GAP_ANALYSIS.md
INPUT_GAP_ANALYSIS_SHA256=e07b7bcf970ec0a8e0d0cd84d02d3ee470a5ea5e431632294862a4fd2f1badb8
```

为区分旧暂存链、九十九路径批准补丁和当前工作树，本次同时比较：

- `HEAD`（当前提交）内容；
- `INDEX`（暂存区）内容；
- 九十九路径补丁的 `BASELINE`（应用前基线）内容；
- 九十九路径补丁的 `POST`（应用后）内容；
- 当前 `WORKTREE`（工作树）内容。

### 1.2 分类规则

| 分类 | 中文含义 | 判定规则 |
| --- | --- | --- |
| `F1_REQUIRED` | 必须进入基础锚点 | 当前差异是宪法定义、宪法投影或必要治理环境，不携带其他阶段语义 |
| `P1_ONLY` | 只属于契约父基线 | 当前差异只服务九十九路径内部契约迁移 |
| `HEAD_INHERIT_ONLY` | 继承当前提交 | `HEAD`（当前提交）内容已经足够，不需要把当前工作树差异带入基础锚点 |
| `SEPARATE_AUTHORIZATION_REQUIRED` | 需要单独授权 | 同一对象混合多种阶段角色，或包含尚未获授权的架构、商业、迁移或历史对象 |

整文件分类采用最严格规则：只要同一文件混合两类以上增量语义，就不能因为其中一段属于 `F1`（基础锚点第一阶段）而把整文件判为 `F1_REQUIRED`（必须进入基础锚点）。

## 2. 总体分类

| 文件对象 | 整体分类 | 结论摘要 |
| --- | --- | --- |
| `agent-index.json`（智能体索引） | `SEPARATE_AUTHORIZATION_REQUIRED` | 同时包含宪法机器投影、九十九路径契约迁移投影、商业状态对象和当前提交继承内容 |
| `llms.txt`（大语言模型说明） | `SEPARATE_AUTHORIZATION_REQUIRED` | 同时包含五行宪法投影、六行 M03-M06（第三至第六里程碑）材料、九十九路径生态投影和当前提交继承内容 |
| `docs/product/SAEE_MODULE_REGISTRY.md`（SAEE 模块登记表） | `SEPARATE_AUTHORIZATION_REQUIRED` | 宪法归属内容与尚未授权的 ARO（历史多义缩写）和身份参考真值对齐对象共存 |
| `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md`（免疫治理平面） | `F1_REQUIRED` | 当前新增段落只表达宪法归属、非执行权力、未迁移边界和复用优先规则 |
| `.codex/current_state.md`（编码智能体当前状态） | `F1_REQUIRED` | 当前新增内容只表达宪法权威、主线边界和分阶段真值 |
| `.codex/rules.md`（编码智能体规则） | `F1_REQUIRED` | 当前新增内容只建立宪法优先、能力清单优先、防重复建设和校验顺序 |

整文件层没有 `P1_ONLY`（只属于契约父基线）或 `HEAD_INHERIT_ONLY`（继承当前提交）对象，不代表这两类内容不存在；它们存在于三个混合文件的内部范围中。

## 3. `agent-index.json`（智能体索引）

### 3.1 快照事实

```text
HEAD_SHA256=90f870a8cb6400096052def1615c878ea03c7558aef85c23d20618e1c5b8cccc
RETIRED_INDEX_SHA256=1452cfac9bac6f3eca9824f1c02299ddf64099e22d52ffa59c464e866cc06a7f
APPROVED_PATCH_BASELINE_SHA256=1ac0a832019d48dd3f40ef7f594c96938d9394f793fee8de06d1d8a429c61740
APPROVED_PATCH_POST_SHA256=4ba882f0466086f31ab35b99c169c95ea8aff20ddad45812428ba75d9e85dc67
CURRENT_WORKTREE_SHA256=4ba882f0466086f31ab35b99c169c95ea8aff20ddad45812428ba75d9e85dc67
POST_MATCHES_WORKTREE=true
```

九十九路径批准补丁的应用后对象与当前工作树逐字节一致。旧暂存区内容不是当前授权来源，只能作为已废止推进链的取证参考。

### 3.2 字段级分类

| 当前对象或差异范围 | 位置 | 分类 | 判断 |
| --- | ---: | --- | --- |
| `development_constitution_v1_1` | 当前第 22366 行开始 | `F1_REQUIRED` | 是开发宪法的机器可读投影，包含主线、副线、目标客户版本、漂移响应和未迁移边界 |
| `saee_agent_capability_alpha_v0_1` | 当前第 33819 行开始 | `P1_ONLY` | 当前内容包含内部 `evaluate_rehearsal_run`（排演运行评估）迁移结果 |
| `saee_agent_readiness_architecture_v1` | 当前第 34044 行开始 | `P1_ONLY` | 包含内部能力可用性和模型上下文协议工具注册名称迁移 |
| `saee_agent_readiness_benchmark_v0_1` | 当前第 34092 行开始 | `P1_ONLY` | 包含内部评估链名称迁移 |
| `saee_capability_service_package_v1` | 当前第 34490 行开始 | `P1_ONLY` | 包含内部能力包操作名称迁移 |
| `saee_evaluate_rehearsal_run_mcp_capability_v0_1` | 当前第 34746 行开始 | `P1_ONLY` | 是九十九路径补丁中由旧内部对象迁移后的活动对象 |
| 九十九路径补丁中旧 `saee_evaluate_agent_run_mcp_capability_v0_1` 的删除 | 应用前对象 | `P1_ONLY` | 删除本身是契约迁移的一部分，不属于 `F1`（基础锚点第一阶段） |
| `commercial_trial_operator_status_v0_1` | 当前第 20355 行开始 | `SEPARATE_AUTHORIZATION_REQUIRED` | 属于商业运行状态投影，与基础锚点和契约迁移均无直接关系 |
| 其余未发生相关变化的顶层对象 | 当前文件其余范围 | `HEAD_INHERIT_ONLY` | 继承 `HEAD`（当前提交），不得为了构造完整文件而重新授权 |

`HEAD`（当前提交）到旧暂存区的十四项叶字段差异全部位于 `development_constitution_v1_1`。`HEAD`（当前提交）到九十九路径应用前基线的二十二项叶字段差异只涉及该宪法对象和商业状态对象。九十九路径应用前到应用后的五十六项叶字段差异只涉及内部契约迁移对象。

### 3.3 最终判断

```text
AGENT_INDEX_WHOLE_FILE_CLASSIFICATION=SEPARATE_AUTHORIZATION_REQUIRED
AGENT_INDEX_F1_EXACT_OBJECT=development_constitution_v1_1
AGENT_INDEX_P1_CONTRACT_OBJECTS_PRESENT=true
AGENT_INDEX_UNRELATED_COMMERCIAL_OBJECT_PRESENT=true
AGENT_INDEX_WHOLE_FILE_F1_STAGING_ALLOWED=false
```

未来若授权 `F1`（基础锚点第一阶段），只能选择 `development_constitution_v1_1` 的精确对象内容，并重建目标索引；不得把旧暂存区文件或当前工作树整文件直接当作基础锚点。

## 4. `llms.txt`（大语言模型说明）

### 4.1 快照事实

```text
HEAD_SHA256=bd8cdf41a0323a5585698b99c7273054dc5cc248972b0bec94da4f2f7416e6e7
APPROVED_PATCH_BASELINE_SHA256=e73c61c1bec1282f49ab5f012f77ae83e195b0a19d3688e5e2c90f036b971e07
APPROVED_PATCH_POST_SHA256=cba95a8925a13914ff310e5cd47642324df8f08f59b0b00f0eb606b121dbb04b
CURRENT_WORKTREE_SHA256=cba95a8925a13914ff310e5cd47642324df8f08f59b0b00f0eb606b121dbb04b
POST_MATCHES_WORKTREE=true
```

### 4.2 段落级分类

| 当前行范围或内容 | 分类 | 判断 |
| --- | --- | --- |
| 第 24-28 行：项目主线、副线、目标客户版本、目标版本真值和主线漂移规则 | `F1_REQUIRED` | 五行均是开发宪法的智能体可读投影 |
| 第 29-34 行：迁移计划、来源授权、净室适配器、适配器校验、评估桥接和迁移真值 | `SEPARATE_AUTHORIZATION_REQUIRED` | 属于 M03-M06（第三至第六里程碑）材料，本任务明确禁止修改或纳入 |
| 第 5042、5051、5063、5065、5075、5349、5366、5378、5391、5656 行附近的内部名称迁移段落 | `P1_ONLY` | 属于九十九路径补丁的生态和契约投影，不得进入 `F1`（基础锚点第一阶段） |
| `HEAD`（当前提交）已有的其余内容 | `HEAD_INHERIT_ONLY` | 继续继承，不需要形成 `F1`（基础锚点第一阶段）差异 |

### 4.3 最终判断

```text
LLMS_WHOLE_FILE_CLASSIFICATION=SEPARATE_AUTHORIZATION_REQUIRED
LLMS_F1_EXACT_LINE_RANGE=24-28
LLMS_M03_M06_LINE_RANGE=29-34
LLMS_P1_PROJECTION_PRESENT=true
LLMS_WHOLE_FILE_F1_STAGING_ALLOWED=false
```

五行宪法投影可以成为未来精确授权对象，但不能复用当前整文件状态。否则会同时提前吸收 M03-M06（第三至第六里程碑）和九十九路径契约投影。

## 5. `docs/product/SAEE_MODULE_REGISTRY.md`（SAEE 模块登记表）

### 5.1 快照事实

```text
HEAD_SHA256=bf8b64a9d734575f50965829a1427fe86fa16bc782453d0e45328d04a654e982
CURRENT_WORKTREE_SHA256=eb47a4ade538ab77c18123440c345e26e90664ff72badba5491e1348b4b241da
```

### 5.2 与架构真值表面对齐的关系

已有 `reports/SAEE_ARCHITECTURE_TRUTH_SURFACE_OBJECT_INVENTORY.md`（架构真值表面对齐对象清单）把当前模块登记表中的四个精确对象分为：

- `MR-01`：第 10 行，证据与免疫子系统来源中裸写 ARO（历史多义缩写），需要未来精确授权；
- `MR-02`：第 11 行，智能体身份表述需要收敛为 Identity Reference（身份参考），需要未来精确授权；
- `MR-03`：第 24 行，宪法归属与未迁移、未集成边界准确，应保持；
- `MR-04`：第 28 行，发现地图、历史、许可证和来源边界准确，应保持。

### 5.3 精确分类

| 当前对象 | 分类 | 判断 |
| --- | --- | --- |
| 第 10 行中的 `SAEE Evidence and Immune Subsystem`（SAEE 证据与免疫子系统）归属和 `agent-evidence-layer` 历史来源 | `F1_REQUIRED` | 开发宪法校验需要的模块归属投影 |
| 第 10 行中的裸写 ARO（历史多义缩写） | `SEPARATE_AUTHORIZATION_REQUIRED` | 需先完成术语真值对齐，不能由基础锚点授权替代 |
| 第 11 行智能体身份表述 | `SEPARATE_AUTHORIZATION_REQUIRED` | 属于架构真值表面对齐，不是本次基础锚点缺口 |
| 第 24 行宪法归属和未迁移边界 | `F1_REQUIRED` | 是基础锚点所需的分阶段真值 |
| 第 28 行发现地图和来源边界 | `F1_REQUIRED` | 支撑宪法归属不等于源代码迁移 |
| 其余 `HEAD`（当前提交）已有内容 | `HEAD_INHERIT_ONLY` | 不需要形成基础锚点差异 |

第 10 行在同一行内同时包含 `F1_REQUIRED`（必须进入基础锚点）和 `SEPARATE_AUTHORIZATION_REQUIRED`（需要单独授权）内容。因此不能把该行当前版本或整个文件直接纳入 `F1`（基础锚点第一阶段）。

### 5.4 最终判断

```text
MODULE_REGISTRY_WHOLE_FILE_CLASSIFICATION=SEPARATE_AUTHORIZATION_REQUIRED
MODULE_REGISTRY_F1_FACTS_PRESENT=true
MODULE_REGISTRY_ARCHITECTURE_ALIGNMENT_PENDING=true
MODULE_REGISTRY_WHOLE_FILE_F1_STAGING_ALLOWED=false
```

该对象必须先获得精确术语对齐授权，或为 `F1`（基础锚点第一阶段）构造一个不携带裸写 ARO（历史多义缩写）和身份扩张主张的最小差异片段。

## 6. `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md`（免疫治理平面）

### 6.1 快照事实

```text
HEAD_SHA256=b3ec55a41cc4567f4d3d4493e77dbf51790178a7e2004b34e9081d7f6d1a137d
CURRENT_WORKTREE_SHA256=96beb8caf1bc483a6181c987500bae0d69703c103f459cd8880787d9e6b4c08c
```

### 6.2 精确分类

| 当前范围 | 分类 | 判断 |
| --- | --- | --- |
| 第 1-26 行 | `HEAD_INHERIT_ONLY` | 已存在于 `HEAD`（当前提交），继续继承 |
| 第 27-42 行 | `F1_REQUIRED` | 只新增智能体证据项目的宪法归属、非执行权力、未迁移状态、复用优先和禁止平行证据栈规则 |

新增段落没有引入新能力、运行时集成、公开接口或生产主张，也没有携带九十九路径契约迁移内容。

```text
IMMUNE_GOVERNANCE_PLANE_CLASSIFICATION=F1_REQUIRED
IMMUNE_GOVERNANCE_PLANE_F1_LINE_RANGE=27-42
```

## 7. `.codex/current_state.md`（编码智能体当前状态）

### 7.1 快照事实

```text
HEAD_SHA256=1831cdda02766e888603a8c63dd281abf9761bc71d224cfff2ebbd78fa804c69
CURRENT_WORKTREE_SHA256=c70123abe45061080ee20a84aeaa0cec29f5ab4b092c4cbead608878ababf343
```

### 7.2 精确分类

| 当前范围 | 分类 | 判断 |
| --- | --- | --- |
| 第 9-11 行 | `F1_REQUIRED` | 冻结开发宪法权威、证据项目归属和未迁移边界 |
| 第 21 行 | `F1_REQUIRED` | 只声明宪法归属完成，不声明源代码或运行时迁移 |
| 第 31-32 行 | `F1_REQUIRED` | 冻结宪法优先、规范能力清单优先、复用优先和迁移门 |
| 第 46-47 行 | `F1_REQUIRED` | 明确 `source_code_migrated=false` 和 `runtime_integrated=false` |
| 其余内容 | `HEAD_INHERIT_ONLY` | 继承 `HEAD`（当前提交） |

```text
CODEX_CURRENT_STATE_CLASSIFICATION=F1_REQUIRED
CODEX_CURRENT_STATE_GOVERNANCE_ENVIRONMENT_REQUIRED=true
```

该文件是智能体启动时的活动状态面。缺少它会让编码智能体读取到宪法文件，却无法从当前状态面确认主线和未迁移事实。

## 8. `.codex/rules.md`（编码智能体规则）

### 8.1 快照事实

```text
HEAD_SHA256=7965a546693189043a50a6d025abb2ad0db5292ea62dca95f47c2280a7a2341e
CURRENT_WORKTREE_SHA256=c16108b4c15d597e9639fe02a16f2dab42960915d7774dd4328c964a77bcbbd3
```

### 8.2 精确分类

| 当前范围 | 分类 | 判断 |
| --- | --- | --- |
| 第 3-12 行 | `F1_REQUIRED` | 建立宪法权威、规范能力清单、防重复建设、推荐门和未迁移边界 |
| 第 39-46 行 | `F1_REQUIRED` | 把宪法、能力清单和宪法校验加入修改前顺序 |
| 其余内容 | `HEAD_INHERIT_ONLY` | 继承 `HEAD`（当前提交） |

```text
CODEX_RULES_CLASSIFICATION=F1_REQUIRED
CODEX_RULES_GOVERNANCE_ENVIRONMENT_REQUIRED=true
```

该文件不是产品能力或契约迁移对象，而是让后续编码智能体在修改前遵守开发宪法的必要治理环境。

## 9. 精确范围决定

### 9.1 可进入未来 `F1`（基础锚点第一阶段）授权包的对象

以下对象的范围判断已经收敛，但本报告不授予实施权：

```text
F1_REQUIRED_CURRENT_DELTA_OBJECTS=
docs/architecture/IMMUNE_GOVERNANCE_PLANE.md:27-42
.codex/current_state.md:9-11,21,31-32,46-47
.codex/rules.md:3-12,39-46
```

### 9.2 必须精确重建或另行授权的混合对象

```text
SEPARATE_AUTHORIZATION_REQUIRED_OBJECTS=
agent-index.json#development_constitution_v1_1
llms.txt:24-28
docs/product/SAEE_MODULE_REGISTRY.md#F1_constitution_projection_after_term_alignment
```

这里的“另行授权”不是授权整文件，而是要求未来授权记录绑定精确对象、来源快照、目标内容和排除内容。

### 9.3 明确排除

以下内容不得进入 `F1`（基础锚点第一阶段）：

- `agent-index.json`（智能体索引）中的内部 `evaluate_rehearsal_run`（排演运行评估）契约迁移对象；
- `agent-index.json`（智能体索引）中的商业运行状态对象；
- `llms.txt`（大语言模型说明）中的九十九路径生态投影；
- `llms.txt`（大语言模型说明）第 29-34 行 M03-M06（第三至第六里程碑）材料；
- 模块登记表中尚未授权的 ARO（历史多义缩写）术语对齐和身份参考对齐；
- 九十九路径补丁本身；
- M03-M06（第三至第六里程碑）对象；
- Trust Infrastructure（可信基础设施）未来研究材料。

## 10. 与 `P1`（契约父基线第一阶段）的边界

本次确认：九十九路径补丁应用后的 `agent-index.json`（智能体索引）和 `llms.txt`（大语言模型说明）与当前工作树逐字节一致，但这不允许 `F1`（基础锚点第一阶段）复制当前整文件。

正确的父子关系必须是：

```text
HEAD（当前提交）
  ↓
F1（只包含获授权的基础宪法对象和必要治理环境）
  ↓
P1（在重新计算父状态后应用获批准的九十九路径契约补丁）
```

如果未来 `F1`（基础锚点第一阶段）改变了两个混合文件的父内容，九十九路径补丁的父状态和散列必须重新绑定；不得沿用旧散列声称补丁未经变化。

## 11. 未扩大对象

`scripts/mainline_guard.py`（主线守卫）虽然是主线强制执行依赖，但不在本次指定的六个审查对象中。本报告不重新分类、不授权、不修改该文件。它继续保持：

```text
MAINLINE_GUARD_SEPARATE_AUTHORIZATION_REQUIRED=true
MAINLINE_GUARD_INCLUDED_IN_THIS_REVIEW=false
```

`capability-package/manifest.json`（能力包清单）继续作为 `F1`（基础锚点第一阶段）的逻辑核心事实，从 `HEAD`（当前提交）继承，不形成本次增量：

```text
CAPABILITY_SOURCE_ROLE=F1_LOGICAL_CORE_INHERITED_BINDING
CAPABILITY_SOURCE_F1_DELTA_REQUIRED=false
```

## 12. 跑偏教训核查

本次没有检测到主线漂移。任务直接服务于 `saee_agent_evidence_integration`（智能体证据集成）主线的基础历史锚点准备。

但前序推进链提供了三项必须保留的教训：

1. 文件级授权不能替代对象级授权；`agent-index.json`（智能体索引）和 `llms.txt`（大语言模型说明）必须按字段或段落拆分；
2. 已废止暂存链只能作为证据，不能自动恢复为当前授权；
3. “校验需要读取某文件”不等于“该文件当前全部工作树变化都应进入基础锚点”。

```text
MAINLINE_DRIFT_DETECTED=false
SECONDARY_LANE_PROMOTED=false
SCOPE_EXPANSION_EXECUTED=false
```

## 13. 权限与最终状态

本次只新增本审查报告。未修改六个被审查对象，未执行暂存、提交、推送、合并、基础锚点建立、契约父基线建立、九十九路径补丁修改或 M03-M06（第三至第六里程碑）修改。

```text
F1_BASELINE_AUTHORIZED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_FOUNDATION_ANCHOR_PRECISION_SCOPE
```
