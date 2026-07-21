# SAEE Capability Contract Alignment（能力契约收敛）Phase 2.1（第二阶段一点一）人工授权记录准备

## 1. 当前决定

```text
AUTHORIZATION_RECORD_PREPARATION_STATUS=COMPLETE
AUTHORIZATION_RECORD_TYPE=HUMAN_DECISION_PENDING
PATCH_DECISION=PATCH_REQUIRES_ADJUSTMENT
HUMAN_APPROVAL_RECORDED=false
IMPLEMENTATION_AUTHORIZED=false
RENAME_EXECUTED=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
PUBLIC_CAPABILITY_UNCHANGED=true
PUBLIC_MCP_UNCHANGED=true
PUBLIC_SCHEMA_UNCHANGED=true
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
```

本文件只准备 Phase 2.1（第二阶段一点一）实施授权记录，不构成人工批准。
在人工填写授权标识、授权所有者并明确确认全部边界前，不得开始调整补丁或执行迁移。

## 2. 授权依据与当前问题

依据：

```text
ADJUSTMENT_PLAN=reports/SAEE_CAPABILITY_CONTRACT_ALIGNMENT_PHASE2_1_ADJUSTMENT_PLAN.md
ADJUSTMENT_PLAN_SHA256=f271f1dcb26daa457c1de037df5fc9285497261dd010bd7b6cbb08ed60773641
PATCH_REVIEW=reports/SAEE_CAPABILITY_CONTRACT_ALIGNMENT_PHASE2_PATCH_REVIEW.md
PATCH_REVIEW_SHA256=3f594326037c854094758e42242baedd7292a14eaa4d99bb187bd5fefb9c3a7f
```

Phase 2（第二阶段）补丁的主要内部运行链已经能够工作，但当前仍不能合并，原因是：

1. 九个需要迁移的 D3（第三类额外授权）文件尚未获得逐文件授权；
2. 十六个已分类文件尚未绑定到准确白名单；
3. 三个额外实现文件中的有界兼容逻辑需要准确授权解释；
4. 历史结果校验存在全对象递归名称替换；
5. `agent-index.json`（智能体索引）混入时间戳、键重排和历史建议字段噪声；
6. 当前活动真值和智能体可读投影仍存在旧内部名称。

本次请求只关闭上述迁移完整性缺口，不重新设计评估器，不新增能力，也不改变公开契约。

## 3. 拟申请的授权身份

以下字段必须由人类填写，智能体不得代填：

```text
APPROVE_PHASE2_1_INTERNAL_CONTRACT_ALIGNMENT=<human-supplied-true>
AUTHORIZATION_ID=<human-supplied-id>
HUMAN_AUTHORITY_OWNER_ID=<human-supplied-owner-id>
AUTHORIZATION_TIMESTAMP=<human-supplied-timestamp>
AUTHORIZATION_SCOPE=PHASE2_1_MINIMAL_INTERNAL_CONTRACT_ALIGNMENT_ONLY
AUTHORIZATION_CONSUMPTION=ONE_ATTEMPT_ONLY
```

当前这些字段尚未由人类填写，因此：

```text
HUMAN_AUTHORIZATION_RECORDED=false
IMPLEMENTATION_AUTHORIZED=false
```

## 4. 拟授权范围

### 4.1 九个 D3（第三类额外授权）内部迁移文件

若人工批准，允许对以下九个文件执行已冻结的内部名称迁移：

| 文件 | 允许的唯一变化 |
|---|---|
| `agent-interface/architecture/saee-agent-readiness-architecture.v1.json` | 只迁移两个当前内部真值字段名 |
| `docs/architecture/SAEE_AGENT_READINESS_ARCHITECTURE_V1.md` | 只迁移当前内部语义；历史事实保留；公开目标明确保持公开命名空间 |
| `scripts/saee_agent_readiness_architecture_smoke.py` | 只同步准确真值断言、无效变体和状态输出 |
| `ecosystem/mcp-entry-package-v1/mcp-tools.json` | 只迁移内部工具 `name` |
| `ecosystem/mcp-entry-package-v1/agent-usage-guide.md` | 只同步内部工具选择规则和名称说明 |
| `ecosystem/participant-package-v0.1/capability-reference.json` | 只迁移 `operations[0]`；保持 `public_service=false` |
| `agent-interface/ecosystem/saee-first-validation-candidate-matrix.v0.1.json` | 只迁移三处 `required_capabilities` 数组元素 |
| `agent-interface/ecosystem/saee-volcengine-capability-mapping.v0.1.json` | 只迁移 `DESIGN_ONLY`（仅设计）投影中的内部名称 |
| `docs/ecosystem/SAEE_VOLCENGINE_ARK_INTEGRATION_STRATEGY.md` | 只同步上述仅设计投影；不得升级外部集成主张 |

以下第十个 D3（第三类额外授权）对象不在允许修改范围：

```text
agent-interface/ecosystem/saee-baidu-cloud-marketplace-entry-plan.v1.0.json
REFERENCE_CLASS=PUBLIC_OPERATION
CHANGE_AUTHORIZED=false
BYTE_FOR_BYTE_PROTECTION_REQUIRED=true
```

### 4.2 十六个已分类白名单文件

若人工批准，允许以下文件只按 Phase 2.1（第二阶段一点一）调整计划中冻结的准确对象迁移：

1. `agent-readable.md`；
2. `scripts/saee_agent_rehearsal_design_partner_protocol_smoke.py`；
3. `examples/ecosystem-demo-v1/mcp-demo.md`；
4. `examples/ecosystem-demo-v1/agent-flow.md`；
5. `examples/ecosystem-demo-v1/result-example.json`；
6. `examples/ecosystem-demo-v1/README.md`；
7. `examples/ecosystem-demo-v1/scenario/coding-agent-preflight.json`；
8. `examples/agent-integrations/mcp-client-example/client_flow.md`；
9. `examples/agent-integrations/mcp-client-example/README.md`；
10. `examples/agent-integrations/mcp-client-example/example_config.json`；
11. `docs/ecosystem/SAEE_ECOSYSTEM_ENTRY_PACKAGE_REVIEW.md`；
12. `docs/release/SAEE_CAPABILITY_VERSION_POLICY.md`；
13. `docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_DEMO.md`；
14. `docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_PROTOCOL.md`；
15. `docs/public/SAEE_AGENT_NATIVE_CAPABILITY_SURFACE.md`；
16. `ecosystem/first-validation-candidate-package-v1/candidate-profile.md`。

除第十五项外，其余十五个内部文件只允许同步内部排演名称、发现预期、活动调用和对应测试。
第十五项公开说明文件只允许把公开操作写全为 `saee.evaluate_agent_run`（智能体运行评估）和
`saee.evaluate_evidence`（证据评估）；不得改变公开能力状态、输入、输出或语义。

`agent-readable.md`（智能体可读汇总）不得手工全局替换，只能从已授权来源确定性更新。

```text
D3_INTERNAL_FILES_REQUESTED=9
CLASSIFIED_ALLOWLIST_FILES_REQUESTED=16
AUTOMATIC_ALLOWLIST_EXPANSION=false
```

### 4.3 三个额外实现文件的有界兼容逻辑

若人工批准，以下三个文件仍仅允许名称、固定身份、准确引用和有界兼容逻辑：

| 文件 | 允许 | 禁止 |
|---|---|---|
| `saee_backend/services/agent_run_capability.py` | 内部固定身份值和内部结果身份引用 | 算法、原因码、证据判断、输入输出 |
| `saee_backend/services/capability_runtime/capability_registry_loader.py` | 已登记旧内部来源的准确名称兼容解析 | 新能力路由、公开别名、额外协议 |
| `saee_backend/services/capability_truth_consistency_validator.py` | 已登记内部字段的准确名称兼容和状态分类 | 全对象归一化、放宽公开真值、改变能力数量 |

任何需要新增算法分支、能力分支或协议分支的变化都超出授权，必须停止。

### 4.4 活动调用方同步

允许同步的活动调用方只包括已经进入 Phase 2（第二阶段）迁移地图、九个 D3（第三类额外授权）文件、
十六个白名单文件和三个额外实现文件中的现有引用。

允许变化限于：

- 内部工具标识；
- 内部固定能力标识；
- 内部路由和发现预期；
- 内部演示、模拟器和测试预期；
- 对公开与内部名称边界的必要说明。

发现任何新的活动调用方时：

```text
STOP_REQUIRED=true
ALLOWLIST_EXPANSION_AUTOMATIC=false
NEW_HUMAN_AUTHORIZATION_REQUIRED=true
```

### 4.5 精确语义验证

若人工批准，允许调整现有验证器以执行准确路径、准确对象指针和准确字段比较。

特别允许：

- 只对已登记历史字段构造临时兼容投影；
- 断言同一对象其他位置不存在未登记旧内部名称；
- 把剩余命中分类为公开操作、历史事实、局部实现符号或活动内部操作；
- 对公开契约、历史证据和能力数量执行前后比较。

明确禁止：

```text
GLOBAL_RECURSIVE_NAME_REPLACEMENT=false
WHOLE_OBJECT_UNBOUNDED_NORMALIZATION=false
UNCLASSIFIED_OLD_NAME_REFERENCE_ALLOWED=false
```

## 5. 继续禁止的范围

无论未来是否批准本记录，以下事项均不在授权范围：

1. 修改规范公开 `saee.evaluate_agent_run`（智能体运行评估）；
2. 修改公开 MCP（模型上下文协议）工具、入口、发现对象或别名归属；
3. 修改公开 Schema（数据结构规范）请求、响应、字段、必填项或类型；
4. 修改任何字段语义；
5. 修改内部或公开评估算法、原因码或证据判断逻辑；
6. 新增能力、评估器、协议、字段或第三套契约；
7. 重写历史报告、发布快照、既有证据或封存结果；
8. 修改 SAEE Development Constitution（SAEE 开发宪法）、治理注册表或
   Agent Evidence Integration（智能体证据集成）主线材料；
9. 重新开启 Goal Integrity（目标完整性）或 State Integrity（状态完整性）副线；
10. 执行部署、发布、外部网络动作或客户数据处理；
11. 自动执行 `git add`（暂存）、`git commit`（提交）、`git push`（推送）或 `merge`（合并）；
12. 自动重试、自动扩大白名单或自动更换基线。

```text
PUBLIC_CAPABILITY_CHANGE_NOT_AUTHORIZED=true
PUBLIC_MCP_CHANGE_NOT_AUTHORIZED=true
PUBLIC_SCHEMA_CHANGE_NOT_AUTHORIZED=true
SCHEMA_FIELD_SEMANTIC_CHANGE_NOT_AUTHORIZED=true
EVALUATION_ALGORITHM_CHANGE_NOT_AUTHORIZED=true
NEW_CAPABILITY_NOT_AUTHORIZED=true
NEW_PROTOCOL_NOT_AUTHORIZED=true
HISTORICAL_EVIDENCE_REWRITE_NOT_AUTHORIZED=true
GOAL_INTEGRITY_RESTART_NOT_AUTHORIZED=true
```

## 6. 实施前置条件

即使人类未来填写批准字段，实施开始前仍必须同时满足：

- [ ] 创建新的干净隔离工作区，不复用第一次实施副本；
- [ ] 绑定人工接受的基线提交或只读基线快照；
- [ ] 记录基线树摘要；
- [ ] 冻结准确命中登记表；
- [ ] 冻结实际修改文件白名单；
- [ ] 冻结公开保护文件实施前摘要；
- [ ] 冻结历史证据保护摘要；
- [ ] 绑定失败证据保存位置和非破坏性回滚点；
- [ ] 确认时间戳、键重排、历史建议字段和缓存文件不进入补丁；
- [ ] 确认 `UNRESOLVED=0`（未解决对象数量为零）；
- [ ] 记录一次性授权标识和授权所有者。

任一条件未满足：

```text
EXECUTION_WORKSPACE_READY=false
IMPLEMENTATION_MUST_NOT_START=true
```

## 7. 实施后必须完成的验证

### 7.1 公开能力保护

必须证明：

```text
PUBLIC_CAPABILITY_UNCHANGED=true
PUBLIC_MCP_UNCHANGED=true
PUBLIC_SCHEMA_UNCHANGED=true
PUBLIC_PROTECTED_FILES_EQUAL=13/13
PUBLIC_TOOL_COUNT=2
PUBLIC_TOOLS=saee.evaluate_agent_run;saee.evaluate_evidence
PUBLIC_ALIAS_OWNERSHIP_CHANGED=false
```

公开保护文件、规范公开能力对象以及两个公开或兼容 MCP（模型上下文协议）对象必须逐字节或逐对象一致。

### 7.2 内部迁移完整性

必须证明：

```text
INTERNAL_RENAME_COMPLETE=true
ACTIVE_INTERNAL_OLD_NAME_HITS=0
UNCLASSIFIED_OLD_NAME_REFERENCES=0
ACTIVE_CALLERS_MIGRATED=true
INTERNAL_TOOL_DISCOVERY_CONSISTENT=true
```

旧名称仍可存在于公开能力、历史事实和局部实现符号中，但每个命中必须出现在冻结分类表中。

### 7.3 演示、模拟器和已有验证

必须证明：

```text
DEMO_VALIDATION_PASS=true
SIMULATOR_VALIDATION_PASS=true
EXISTING_VALIDATIONS_PASS=true
MAINLINE_GUARD_PASS=true
```

验证必须包含当前演示、内部 MCP（模型上下文协议）工具发现、模拟器、运行时、规范能力清单、
能力真值一致性、项目记忆、治理注册表、开发宪法和能力进度台账检查。

### 7.4 语义与历史保护

必须证明：

```text
SCHEMA_FIELD_SEMANTICS_CHANGED=false
EVALUATION_ALGORITHM_CHANGED=false
REASON_CODES_CHANGED=false
HISTORICAL_EVIDENCE_UNCHANGED=true
RELEASE_SNAPSHOT_UNCHANGED=true
NO_NEW_CAPABILITY=true
CAPABILITY_COUNT=9
AGENT_INDEX_UNRELATED_NOISE=0
ALLOWLIST_VIOLATIONS=0
IGNORED_CACHE_CHANGES=0
GLOBAL_RECURSIVE_NAME_REPLACEMENT_USED=false
```

技术验证通过不自动升级为合并授权。实施完成后必须停止并进入新的只读补丁人工审查。

## 8. 失败与回滚条件

出现以下任一情况立即停止：

- 任一公开保护摘要变化；
- 任一公开请求、响应、工具或能力对象变化；
- 发现新的白名单外活动调用方；
- 任一旧名称命中无法分类；
- 需要修改算法、字段语义、能力数量或协议；
- 历史证据发生变化；
- `agent-index.json`（智能体索引）产生无关变化；
- 演示、模拟器、专项校验或主线守卫失败；
- 出现主线漂移或副线重启。

回滚规则：

1. 保留失败尝试、命令、差异和验证输出；
2. 只处理新的隔离工作区，不触碰主工作区已有用户修改；
3. 不使用 `git reset --hard`（Git 强制重置）；
4. 不自动重试；
5. 回到人工接受的基线并等待新授权。

```text
AUTOMATIC_RETRY_ALLOWED=false
DESTRUCTIVE_ROLLBACK_ALLOWED=false
FAILED_ATTEMPT_EVIDENCE_PRESERVED=true
```

## 9. 一次性消费规则

未来人类批准后，该授权只能用于一次新的隔离实施尝试，并在下列任一事件发生时失效：

- 实施成功并生成实施报告；
- 首次停止或失败；
- 实际修改范围需要扩大；
- 基线、公开保护摘要或授权所有者变化；
- 需要执行合并、提交或推送。

```text
AUTHORIZATION_REUSABLE=false
RETRY_REQUIRES_NEW_AUTHORIZATION=true
MERGE_REQUIRES_SEPARATE_HUMAN_REVIEW=true
COMMIT_REQUIRES_SEPARATE_AUTHORIZATION=true
PUSH_REQUIRES_SEPARATE_AUTHORIZATION=true
```

## 10. 人工决定区

人类若决定批准，必须明确提供以下全部值：

```text
APPROVE_PHASE2_1_INTERNAL_CONTRACT_ALIGNMENT=true
AUTHORIZATION_ID=<human-supplied-id>
HUMAN_AUTHORITY_OWNER_ID=<human-supplied-owner-id>
ACCEPT_D3_INTERNAL_FILE_SCOPE=true
ACCEPT_CLASSIFIED_ALLOWLIST_FILE_SCOPE=true
ACCEPT_BOUNDED_COMPATIBILITY_LOGIC=true
ACCEPT_EXACT_SEMANTIC_VALIDATION=true
KEEP_PUBLIC_CAPABILITY_UNCHANGED=true
KEEP_PUBLIC_MCP_UNCHANGED=true
KEEP_PUBLIC_SCHEMA_UNCHANGED=true
KEEP_HISTORICAL_EVIDENCE_UNCHANGED=true
NO_RECURSIVE_NAME_REPLACEMENT=true
NO_NEW_CAPABILITY=true
NO_ALGORITHM_CHANGE=true
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

未完整收到上述人工决定前，本记录保持：

```text
HUMAN_APPROVAL_RECORDED=false
IMPLEMENTATION_AUTHORIZED=false
```

## 11. 指挥官命令核查

```text
PROGRAM_MAINLINE=saee_agent_evidence_integration
IMPLEMENTATION_SCOPE=CONTRACT_ALIGNMENT_ONLY
MAINLINE_DRIFT_DETECTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

本次授权准备只服务 Agent Evidence（智能体证据）与 Evaluation（评估）主线的能力契约稳定性，
没有把治理记录变成新能力，也没有重新开启目标完整性研究。

前几轮教训继续冻结：

1. 计划完成不等于人工授权；
2. 技术验证通过不等于迁移完整；
3. 实施完成不等于补丁可以合并；
4. 实施后解释不能替代实施前白名单；
5. 递归替换不能作为传播面完整性证据；
6. 无关生成噪声不得混入受控补丁。

## 12. 非主张

本文件不表示：

- 人工已经批准 Phase 2.1（第二阶段一点一）实施；
- 代码、MCP（模型上下文协议）或 Schema（数据结构规范）已经改变；
- 内部重命名已经执行；
- 补丁已经获准合并、提交或推送；
- 公开能力已经变化；
- 新能力、新协议或新产品方向已经成立；
- SAEE（硅基放大演化生态）已经外部可用、客户验证完成或生产就绪。

## 13. 最终状态

```text
PHASE2_1_HUMAN_AUTHORIZATION_PREPARATION_STATUS=COMPLETE
AUTHORIZATION_RECORD_CREATED=true
HUMAN_APPROVAL_RECORDED=false
IMPLEMENTATION_AUTHORIZED=false
RENAME_EXECUTED=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
PUBLIC_CAPABILITY_UNCHANGED=true
PUBLIC_MCP_UNCHANGED=true
PUBLIC_SCHEMA_UNCHANGED=true
SCHEMA_FIELD_SEMANTICS_CHANGED=false
EVALUATION_ALGORITHM_CHANGED=false
NEW_CAPABILITY_CREATED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_AND_DECISION_ON_PHASE2_1_AUTHORIZATION
```
