# SAEE 基础锚点精确授权准备包

日期：2026-07-17

## 0. 状态与结论

本文件根据 `reports/SAEE_FOUNDATION_ANCHOR_PRECISION_SCOPE_REVIEW.md`（SAEE 基础锚点精确范围审查）生成六项 `F1`（基础锚点第一阶段）精确授权候选。

本文件是授权准备包，不是授权记录，不建立 `F1`（基础锚点第一阶段），也不允许执行暂存、提交、推送或 `P1`（契约父基线第一阶段）重建。

```text
FOUNDATION_ANCHOR_EXACT_AUTHORIZATION_PREPARATION_STATUS=COMPLETE
EXACT_AUTHORIZATION_CANDIDATE_COUNT=6
EXACT_AUTHORIZATION_DECISION=NOT_RECORDED
EXACT_AUTHORIZATION_GRANTED=false
F1_BASELINE_CREATED=false
P1_CONTRACT_BASELINE_CREATED=false
MAINLINE_DRIFT_DETECTED=false
```

六项候选分为：

1. 三项可直接绑定当前工作树精确差异片段；
2. 两项必须按对象或段落重建，禁止整文件纳入；
3. 一项必须采用仅包含已确认 `F1`（基础锚点第一阶段）事实的候选目标，不能携带尚未授权的架构真值表面对齐对象。

## 1. 权威输入与失效规则

### 1.1 输入绑定

```text
CURRENT_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
PRECISION_SCOPE_REVIEW=reports/SAEE_FOUNDATION_ANCHOR_PRECISION_SCOPE_REVIEW.md
PRECISION_SCOPE_REVIEW_SHA256=5ac822ef5c975e74d4d552128f9b9a4bf4ba33da32ef7df0e45522a817673896
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
```

### 1.2 失效规则

下列任一条件发生时，本准备包必须失效并重新生成：

- 六个来源文件中任一当前 `SHA-256`（安全散列算法二百五十六位）发生变化；
- 当前提交发生变化；
- 行位置变化且无法由目标内容逐字匹配；
- 九十九路径补丁、M03-M06（第三至第六里程碑）或架构真值表面对齐内容被混入候选；
- 未来授权记录没有逐项记录接受或拒绝决定。

行号只用于人工定位。授权对象由文件散列、精确内容和排除内容共同确定，不能只靠行号匹配。

## 2. 授权候选总表

| 编号 | 文件 | 当前范围 | 候选类型 | 当前文件 `SHA-256`（安全散列算法二百五十六位） | 整文件允许进入 `F1`（基础锚点第一阶段） |
| --- | --- | --- | --- | --- | --- |
| `F1-EA-01` | `docs/architecture/IMMUNE_GOVERNANCE_PLANE.md`（免疫治理平面） | 第 27-42 行 | 当前精确片段 | `96beb8caf1bc483a6181c987500bae0d69703c103f459cd8880787d9e6b4c08c` | 否 |
| `F1-EA-02` | `.codex/current_state.md`（编码智能体当前状态） | 第 9-11、21、31-32、46-47 行 | 当前非连续精确片段 | `c70123abe45061080ee20a84aeaa0cec29f5ab4b092c4cbead608878ababf343` | 否 |
| `F1-EA-03` | `.codex/rules.md`（编码智能体规则） | 第 3-12、39-46 行 | 当前非连续精确片段 | `c16108b4c15d597e9639fe02a16f2dab42960915d7774dd4328c964a77bcbbd3` | 否 |
| `F1-EA-04` | `agent-index.json`（智能体索引） | 第 22366-22390 行的顶层对象 | 机器对象精确重建 | `4ba882f0466086f31ab35b99c169c95ea8aff20ddad45812428ba75d9e85dc67` | 否 |
| `F1-EA-05` | `llms.txt`（大语言模型说明） | 第 24-28 行 | 当前连续精确片段 | `cba95a8925a13914ff310e5cd47642324df8f08f59b0b00f0eb606b121dbb04b` | 否 |
| `F1-EA-06` | `docs/product/SAEE_MODULE_REGISTRY.md`（SAEE 模块登记表） | 第 10、24、28 行中的 `F1` 事实 | 候选目标精确重建 | `eb47a4ade538ab77c18123440c345e26e90664ff72badba5491e1348b4b241da` | 否 |

```text
WHOLE_FILE_AUTHORIZATION_ALLOWED=false
EXACT_OBJECT_OR_HUNK_AUTHORIZATION_REQUIRED=true
```

## 3. `F1-EA-01`：免疫治理平面

### 3.1 路径、范围与摘要

```text
PATH=docs/architecture/IMMUNE_GOVERNANCE_PLANE.md
CURRENT_LINE_RANGE=27-42
CURRENT_FILE_SHA256=96beb8caf1bc483a6181c987500bae0d69703c103f459cd8880787d9e6b4c08c
SELECTED_CONTENT_SHA256=170f36930014500506291ae1fb21758f5da3b41dd9a227c4ad99bbab3243cfd4
CANDIDATE_CLASS=F1_REQUIRED
```

### 3.2 目标内容

以下内容为未来授权候选的逐字目标。英文技术词用于保持源文件一致，含义为：智能体证据项目归属、证据完整性、来源、回滚和非执行权力边界。

```markdown
## Agent Evidence Project Integration

`Agent Evidence Project`（历史产品名 `Agent Evidence Receipt`，历史源仓库
`agent-evidence-layer`）在 `SAEE Development Constitution v1.1` 下正式归属本平面，
其角色是 `SAEE Evidence and Immune Subsystem` 的 receipt、integrity、provenance
与 source-completeness 来源。

该归属强化 observation → evidence → fitness → archive → rollback 链路，但不产生
execution authority。当前 `constitutional_ownership=implemented`，同时保持
`source_code_migrated=false`、`runtime_integrated=false`、
`external_integration_validated=false`、`customer_validated=false` 和
`production_ready=false`。

未来迁移必须先复用规范能力清单中的现有 evidence / trace / receipt 能力，再通过
source provenance、schema crosswalk、internal adapter 与 ledger synchronization 门；
禁止把旧仓库整包复制为第二套证据栈。
```

中文语义：智能体证据项目在宪法上属于 SAEE 证据与免疫子系统；该归属不产生执行权力，不证明源代码迁移、运行时集成、外部验证、客户验证或生产就绪；未来迁移必须复用现有证据、轨迹和收据能力。

### 3.3 排除内容及原因

- 第 1-26 行：从 `HEAD`（当前提交）继承，不形成 `F1`（基础锚点第一阶段）差异；
- 任何执行权力、运行时集成或生产就绪主张：当前证据不支持；
- 任何九十九路径契约名称：属于 `P1`（契约父基线第一阶段）；
- 任何 M03-M06（第三至第六里程碑）适配器或桥接器事实：需要独立正式基线决定。

## 4. `F1-EA-02`：编码智能体当前状态

### 4.1 路径、范围与摘要

```text
PATH=.codex/current_state.md
CURRENT_LINE_RANGES=9-11;21;31-32;46-47
CURRENT_FILE_SHA256=c70123abe45061080ee20a84aeaa0cec29f5ab4b092c4cbead608878ababf343
SELECTED_CONTENT_SHA256=b1f798824d7aa5884734032af43025a0da822be630afeb435b826c6e2cfd6f3f
CANDIDATE_CLASS=F1_REQUIRED
```

### 4.2 目标内容

以下八行为逐字目标；中文语义紧随其后。

```markdown
- `SAEE Development Constitution v1.1` is the active repository development authority.
- The Agent Evidence Project is constitutionally owned by `SAEE Evidence and Immune Subsystem`.
- Evidence-project source-code migration and unified runtime integration have not been performed.
- Constitutional integration of the Agent Evidence Project into SAEE architecture and governance.
- Enforce constitution-first, canonical-inventory-first and reuse-before-build development.
- Keep future evidence-source migration behind provenance, schema crosswalk, internal adapter and ledger gates.
- `source_code_migrated=false`
- `runtime_integrated=false`
```

中文语义：开发宪法是当前仓库开发权威；智能体证据项目已完成宪法归属，但未完成源代码迁移和统一运行时集成；后续工作必须先查规范能力清单、优先复用，并通过来源、数据结构交叉映射、内部适配器和台账同步门。

### 4.3 排除内容及原因

- 文件其余当前状态：从 `HEAD`（当前提交）继承；
- 商业就绪、客户验证和产品发布状态：不是本次基础锚点授权对象；
- 任何“迁移已完成”表述：与当前分阶段真值冲突；
- M03-M06（第三至第六里程碑）实现状态：不得由当前状态文件提前升级为正式基线。

## 5. `F1-EA-03`：编码智能体规则

### 5.1 路径、范围与摘要

```text
PATH=.codex/rules.md
CURRENT_LINE_RANGES=3-12;39-46
CURRENT_FILE_SHA256=c16108b4c15d597e9639fe02a16f2dab42960915d7774dd4328c964a77bcbbd3
SELECTED_CONTENT_SHA256=5ed8f0fd2e045e3f80b6c350a12499d5bceaf3e87cc4e0544af4b0981398420e
CANDIDATE_CLASS=F1_REQUIRED
```

### 5.2 目标内容

```markdown
## Constitutional Authority

Every Codex change must follow `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`.
Resolve `capability-package/manifest.json#canonical_inventory`, run the duplicate-build
check and the Agent Recommendation Gate, identify the affected evolution subsystem,
and define claims, non-claims and staged truth before changing behavior.

The Agent Evidence Project belongs to `SAEE Evidence and Immune Subsystem`.
This ownership does not mean its source code or runtime has been migrated. Reuse
existing SAEE evidence / trace / receipt capabilities before proposing migration.
1. Check `.codex/current_state.md`.
2. Read the development constitution and canonical capability inventory.
3. Run the duplicate-build and Agent Recommendation gates.
4. Check task scope.
5. Confirm allowed and forbidden files.
6. Run `python3 scripts/saee_development_constitution_smoke.py` for constitutional,
   architecture, product-boundary or evidence-subsystem changes.
7. Run task-specific validation.
```

中文语义：所有编码智能体修改必须先读开发宪法和规范能力清单，执行防重复建设与智能体推荐门，识别演化子系统并保持主张、非主张和分阶段真值；证据项目归属不等于源代码或运行时已迁移；涉及宪法、架构、产品边界或证据子系统的变化必须运行宪法校验。

### 5.3 排除内容及原因

- 文件其余规则：从 `HEAD`（当前提交）继承；
- 新权限、新执行入口或新能力：本对象只约束开发顺序；
- 九十九路径契约迁移规则：不属于基础锚点；
- 主线守卫实现：`scripts/mainline_guard.py`（主线守卫）仍需单独授权和可复现性审查。

## 6. `F1-EA-04`：智能体索引宪法对象

### 6.1 路径、范围与摘要

```text
PATH=agent-index.json
CURRENT_LINE_RANGE=22366-22390
OBJECT_POINTER=/development_constitution_v1_1
CURRENT_FILE_SHA256=4ba882f0466086f31ab35b99c169c95ea8aff20ddad45812428ba75d9e85dc67
CANONICAL_OBJECT_SHA256=a1ff98c78b569b492501368d8983992d171532debfafa62d811160bd94de4f78
CANDIDATE_CLASS=SEPARATE_AUTHORIZATION_REQUIRED
```

`CANONICAL_OBJECT_SHA256`（规范对象安全散列）按键排序并压缩为单行后计算，用于避免空白和缩进变化干扰对象身份。

### 6.2 目标内容

```json
{
  "agent_evidence_project_role": "evidence_and_immune_subsystem",
  "canonical_document": "docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md",
  "canonical_inventory_change": "none_this_change",
  "constitution_version": "1.1.1",
  "constitutional_ownership": "implemented",
  "contract": "agent-interface/governance/saee-development-constitution.v1.1.json",
  "engineering_core": "Digital Biosphere Evolution Engine",
  "mainline_drift_response": "raise_correction_recommendation",
  "overall_classification": "partial",
  "production_ready": false,
  "program_mainline": "integrate_saee_and_agent_evidence_project_under_migration_gates",
  "program_secondary": "use_saee_to_supervise_and_test_the_integration_process",
  "recommendation_gate": "docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md",
  "runtime_integrated": false,
  "schema": "schemas/saee-development-constitution.schema.v1.1.json",
  "smoke_command": "python3 scripts/saee_development_constitution_smoke.py",
  "source_code_migrated": false,
  "status": "active_repository_development_authority",
  "target_customer_versions": [
    "SAEE Evidence",
    "SAEE Evaluation",
    "SAEE Governance"
  ]
}
```

中文语义：该对象只投影开发宪法权威、智能体证据项目归属、主线、副线、漂移处理、目标客户版本和未迁移边界；它不改变规范能力清单。

### 6.3 排除内容及原因

- `agent-index.json`（智能体索引）中的全部其他顶层对象：从 `HEAD`（当前提交）、`P1`（契约父基线第一阶段）或其他独立状态面继承；
- 内部 `evaluate_rehearsal_run`（排演运行评估）相关对象：属于九十九路径契约迁移；
- `commercial_trial_operator_status_v0_1`：属于商业运行状态，需要独立授权；
- 旧暂存区的整文件内容：旧推进链已废止，不能作为当前授权来源；
- 递归名称替换或整文件覆盖：会破坏对象级边界。

## 7. `F1-EA-05`：大语言模型说明宪法投影

### 7.1 路径、范围与摘要

```text
PATH=llms.txt
CURRENT_LINE_RANGE=24-28
CURRENT_FILE_SHA256=cba95a8925a13914ff310e5cd47642324df8f08f59b0b00f0eb606b121dbb04b
SELECTED_CONTENT_SHA256=2f0fce7ef9eb350b52d8275d4c991e2cfe6101970bb3f7131c880b0b5e81d30d
CANDIDATE_CLASS=SEPARATE_AUTHORIZATION_REQUIRED
```

### 7.2 目标内容

```text
Constitutional program mainline: controlled SAEE and Agent Evidence Project integration under provenance, license, schema-crosswalk, reuse, migration and staged-truth gates.
Constitutional program secondary: use SAEE to supervise, test and assess the integration process; this lane cannot displace the mainline or approve its own changes.
Target customer versions: SAEE Evidence; SAEE Evaluation; SAEE Governance.
Target-version truth: the three customer versions are targets, not claims of current implementation, customer validation, launch or production readiness.
Mainline drift rule: if a Commander prompt, role prompt, roadmap or local task elevates governance, testing, audit or another secondary lane above the integration mainline, emit MAINLINE_DRIFT_DETECTED and recommend correction; role prompts do not override the Constitution.
```

中文语义：主线是在来源、许可证、数据结构交叉映射、复用、迁移和分阶段真值门下集成 SAEE 与智能体证据项目；副线只能监督和测试主线；三个客户版本只是目标；角色提示不能覆盖宪法；发现副线替代主线时必须报告漂移并建议纠正。

### 7.3 排除内容及原因

- 第 29-34 行：属于 M03-M06（第三至第六里程碑）迁移、适配器和桥接器材料；
- 内部 `evaluate_rehearsal_run`（排演运行评估）名称迁移段落：属于九十九路径 `P1`（契约父基线第一阶段）补丁；
- 文件其余内容：从 `HEAD`（当前提交）或后续独立基线继承；
- 整文件暂存：会把三个阶段的真值压入一个基础锚点。

## 8. `F1-EA-06`：模块登记表中的已确认基础事实

### 8.1 路径、范围与摘要

```text
PATH=docs/product/SAEE_MODULE_REGISTRY.md
CURRENT_RELEVANT_LINES=10;24;28
CURRENT_FILE_SHA256=eb47a4ade538ab77c18123440c345e26e90664ff72badba5491e1348b4b241da
CURRENT_RELEVANT_LINES_SHA256=af1f94202b32cc8b4e57d32a0024dd1581c2ed818ffbda33336861198e574803
PROPOSED_F1_TARGET_SHA256=c4c3df5aef9a12dead75b21ab1de102e434098f6d72a59f23ecdeec062b65e9e
CANDIDATE_CLASS=SEPARATE_AUTHORIZATION_REQUIRED
```

当前相关行的安全散列与候选目标不同，原因是当前第 10 行包含裸写 ARO（历史多义缩写）；候选目标只保留已确认的 `F1`（基础锚点第一阶段）事实。该差异必须由未来人工授权明确接受，不能由本准备包自动生效。

### 8.2 候选目标内容

```markdown
| SAEE Evidence and Immune Subsystem | `agent-evidence-layer`（历史产品名 `Agent Evidence Receipt`）、当前 Evidence Adequacy | 证据收据、完整性、充分性与回滚免疫支持 | 否 | 部分 |

`agent-evidence-layer` 的架构归属已由 `SAEE Development Constitution v1.1` 纳入 SAEE，但其源代码历史和仓库边界在迁移门完成前继续保留。当前只可声明 `constitutional_ownership=implemented`；不得据此声明 `source_code_migrated=true`、`runtime_integrated=true` 或新增规范 capability 已实现。

This registry is a discovery map, not a package manager, dependency resolver, monorepo manifest, trust registry or execution graph. The Agent Evidence Project is owned by SAEE as its Evidence and Immune Subsystem while source repositories retain their histories, licenses and provenance until an explicit migration gate completes.
```

中文语义：模块登记表只确认智能体证据项目属于 SAEE 证据与免疫子系统，并保留当前证据充分性来源；宪法归属不等于源代码迁移、运行时集成或新增规范能力；该登记表只是发现地图，不是包管理器、依赖解析器、单一仓库清单、信任登记表或执行图。

### 8.3 排除内容及原因

- 当前第 10 行中的裸写 ARO（历史多义缩写）：尚需架构真值表面精确授权，不属于本次 `F1`（基础锚点第一阶段）事实；
- 第 11 行智能体身份表述：属于 Identity Reference（身份参考）真值对齐，不属于当前基础锚点；
- 把 ARO（历史多义缩写）扩写为审计参考、运行观察和证据层的完整术语方案：属于未来架构真值表面对齐；
- 模块登记表其余内容：从 `HEAD`（当前提交）继承；
- 整文件授权：会把尚未审查的模块说明变化带入基础锚点。

### 8.4 失败关闭规则

如果人工不明确接受上述候选目标，执行方必须：

```text
MODULE_REGISTRY_F1_CANDIDATE_ACCEPTED=false
MODULE_REGISTRY_INCLUDED_IN_F1=false
```

不得退回当前第 10 行整行，也不得自行创造新的 ARO（历史多义缩写）解释。

## 9. 全局排除清单

以下对象不在六项精确授权候选内：

- 九十九路径契约收敛补丁的任何代码、公开投影、内部工具发现或测试变化；
- M03-M06（第三至第六里程碑）的二十七项材料及其适配器、桥接器、校验器和测试；
- Trust Infrastructure（可信基础设施）未来研究材料；
- `scripts/mainline_guard.py`（主线守卫）；
- `capability-package/manifest.json`（能力包清单）的当前工作树版本；
- 商业状态、发布状态、历史证据和公开产品投影；
- 任何新能力、新协议、新数据结构规范或运行时集成。

不进入 `F1`（基础锚点第一阶段）的原因统一为：不属于基础宪法定义和必要治理环境，或仍需独立事实、迁移、架构、商业、历史或可复现性授权。

## 10. 未来人工授权记录要求

未来人工授权必须逐项记录：

```text
F1-EA-01=APPROVE|REJECT
F1-EA-02=APPROVE|REJECT
F1-EA-03=APPROVE|REJECT
F1-EA-04=APPROVE|REJECT
F1-EA-05=APPROVE|REJECT
F1-EA-06=APPROVE|REJECT
```

其中 `APPROVE`（批准）只批准本包记录的精确内容，不批准整文件；`REJECT`（拒绝）必须让该对象继续停留在 `F1`（基础锚点第一阶段）之外。

即使六项全部批准，也只表示允许准备隔离的 `F1`（基础锚点第一阶段）候选差异。它不自动授权：

- 修改来源文件；
- 暂存、提交或推送；
- 建立正式历史锚点；
- 重建 `P1`（契约父基线第一阶段）；
- 合并九十九路径补丁；
- 建立 M03-M06（第三至第六里程碑）正式基线。

## 11. 跑偏教训核查

本准备包保持对象级边界，没有重新打开目标完整性、状态完整性、可信基础设施或实验治理副线。

前序推进链的适用教训为：

1. 整文件授权会掩盖智能体索引和大语言模型说明中的混合阶段内容；
2. 旧暂存区可以提供取证参考，但不能提供当前授权；
3. 定向校验通过不等于主线守卫可复现，也不等于提交获得授权；
4. 授权准备、授权决定、差异构造、暂存、提交和父基线建立必须分开。

```text
MAINLINE_DRIFT_DETECTED=false
OLD_STAGING_AUTHORITY_REUSED=false
WHOLE_FILE_AUTHORIZATION_GRANTED=false
```

## 12. 最终状态

本次只新增本授权准备包。六个来源文件均未修改。

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
NEXT_ACTION=HUMAN_REVIEW_OF_FOUNDATION_ANCHOR_EXACT_AUTHORIZATION_PACKAGE
```
