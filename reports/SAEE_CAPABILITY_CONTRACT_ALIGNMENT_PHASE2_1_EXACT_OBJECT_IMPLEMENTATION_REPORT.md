# SAEE Capability Contract Alignment（能力契约收敛）Phase 2.1（第二阶段一点一）精确对象实施报告

日期：2026-07-17

## 1. 结论

根据人工授权：

```text
APPROVE_EXACT_INTERNAL_OBJECT_MIGRATION=true
```

本次在既有 Phase 2.1（第二阶段一点一）隔离工作区内，只迁移了两个已确认活动内部对象：

1. `PROJECT_STATUS.md` 当前状态区块中的两个内部字段名；
2. `agent-readable.md` 第 74 行中的内部排演能力引用。

公开 `saee.evaluate_agent_run`（智能体运行评估）、公开 MCP（模型上下文协议）、公开 Schema（数据结构规范）、发布真值文档、两个站点智能体索引和历史证据均未修改。

```text
EXACT_OBJECT_IMPLEMENTATION_STATUS=COMPLETE
ACTIVE_INTERNAL_OBJECTS_MIGRATED=true
ACTIVE_CALLERS_MIGRATED=true
INTERNAL_RENAME_COMPLETE=true
UNAUTHORIZED_OBJECTS_CHANGED=false
PATCH_APPROVED_FOR_MERGE=false
MERGE_EXECUTED=false
```

`INTERNAL_RENAME_COMPLETE=true` 只表示本次已识别活动内部名称迁移在隔离补丁中完成，不表示补丁已经通过人工审查、获准合并或进入主工作区。

## 2. 实施位置与基线

本次继续使用已经保留的隔离实施根：

```text
/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001
```

实施目录：

```text
baseline/
workspace/
evidence/
```

没有把隔离补丁复制到主工作区。主工作区只新增本报告。

## 3. 精确预映像

实施前两个目标文件摘要：

```text
PROJECT_STATUS_PRE_SHA256=59a7d6355372a5813479e8999e6a3e3b3784927af6c1773f347b05f8afcb9dea
AGENT_READABLE_PRE_SHA256=2337c2d1039343da035f4f8349f2294e0f9d7053e10408a137e2a505b2618ddb
```

排除两个目标文件后的隔离工作区完整文件清单摘要：

```text
OTHER_FILES_PRE_MANIFEST_SHA256=2e292abe318a71e539cb39d57ded07ad64002b4bf711e6fbe8f6f6e5a6126b0f
```

证据文件：

```text
/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001/evidence/exact-object-pre-targets.sha256
/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001/evidence/exact-object-pre-other-files.sha256
```

## 4. 实际修改

### 4.1 `PROJECT_STATUS.md`

只执行：

```text
evaluate_agent_run_available
-> evaluate_rehearsal_run_available

evaluate_agent_run_mcp_tool_registered
-> evaluate_rehearsal_run_mcp_tool_registered
```

修改后的准确行：

```text
242:`evaluate_rehearsal_run_available=true`, `agent_callable_runtime=true`,
244:`evaluate_rehearsal_run_mcp_tool_registered=true`,
```

修改后摘要：

```text
PROJECT_STATUS_POST_SHA256=1e7ad05ad458cd27dd88b7c5dd9f0f2ad5db7d74745f379c9e51248899382502
```

将这两个字段准确反向映射后，文件摘要恢复为实施前摘要，证明没有其他内容变化：

```text
PROJECT_STATUS_REVERSE_PROJECTION_SHA256=59a7d6355372a5813479e8999e6a3e3b3784927af6c1773f347b05f8afcb9dea
PROJECT_STATUS_EXACT_CHANGE_PROVEN=true
```

### 4.2 `agent-readable.md` 第 74 行

只执行：

```text
evaluate_agent_run
-> evaluate_rehearsal_run
```

该替换只发生在描述“固定内部排演运行”的当前句子中。`evaluate_evidence`（证据评估）、公开 `saee.evaluate_agent_run`（智能体运行评估）、`direct_codex_evaluation_supported=false`、试点次数和历史事实均保持不变。

修改后摘要：

```text
AGENT_READABLE_POST_SHA256=802adc295c92958ab3227b131df1dac5b9a27cb801abb37079370224a1a2262a
```

将第 74 行内部名称准确反向映射后，文件摘要恢复为实施前摘要：

```text
AGENT_READABLE_REVERSE_PROJECTION_SHA256=2337c2d1039343da035f4f8349f2294e0f9d7053e10408a137e2a505b2618ddb
AGENT_READABLE_EXACT_CHANGE_PROVEN=true
```

## 5. 未授权对象保护

实施后再次生成排除两个目标文件的完整文件清单，并与实施前逐条比较：

```text
OTHER_FILES_POST_MANIFEST_SHA256=2e292abe318a71e539cb39d57ded07ad64002b4bf711e6fbe8f6f6e5a6126b0f
OTHER_FILES_PRE_POST_IDENTICAL=true
UNAUTHORIZED_OBJECTS_CHANGED=false
```

最终证据文件：

```text
/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001/evidence/exact-object-final-other-files.sha256
/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001/evidence/exact-object-post-targets.sha256
```

## 6. 发布、公开和历史保护

### 6.1 公开能力

规范公开能力对象前后摘要一致：

```text
PUBLIC_CAPABILITY_BASELINE_SHA256=49dc5bc674bc1b4e0c372e9b3f46226296432e01072b9cb56377112f8c4f08a8
PUBLIC_CAPABILITY_WORKSPACE_SHA256=49dc5bc674bc1b4e0c372e9b3f46226296432e01072b9cb56377112f8c4f08a8
PUBLIC_CAPABILITY_CHANGED=false
```

### 6.2 公开 MCP（模型上下文协议）

规范和兼容公开 MCP（模型上下文协议）对象前后摘要一致：

```text
PUBLIC_MCP_BASELINE_SHA256=aa2f49af14d34c39f25cbf619d59532b97dbaddc582b82e6c11aa351f4fe1db8
PUBLIC_MCP_WORKSPACE_SHA256=aa2f49af14d34c39f25cbf619d59532b97dbaddc582b82e6c11aa351f4fe1db8
PUBLIC_MCP_CHANGED=false
```

公开工具仍为：

```text
saee.evaluate_agent_run
saee.evaluate_evidence
```

### 6.3 公开 Schema（数据结构规范）

以下公开 Schema（数据结构规范）与基线逐字节一致：

```text
schemas/saee-public-capability-surface.schema.v0.1.json
agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json
agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json
```

```text
PUBLIC_SCHEMA_CHANGED=false
SCHEMA_FIELD_SEMANTICS_CHANGED=false
```

### 6.4 发布真值文档与历史证据

发布真值文档摘要保持：

```text
RELEASE_TRUTH_DOCUMENT_SHA256=1bc20454a6d60cb61910f9e89111535c7408c28e3aff039bbee1ffd8151fed83
RELEASE_TRUTH_DOCUMENT_CHANGED=false
```

以下保护目录与只读基线一致：

```text
release/
phase_b_product/
docs/pilot/results/
agent-interface/pilot/
agent-interface/release/
output/
```

```text
HISTORICAL_EVIDENCE_CHANGED=false
RELEASE_SNAPSHOT_CHANGED=false
```

### 6.5 站点公开索引

主站点仓库仍为干净状态，两份索引均保持原摘要：

```text
SITE_PUBLIC_AGENT_INDEX_SHA256=b83c1b81e085cc509d9a0d9af29e78a48d54776416db53f7be61928f0a39087a
SITE_DIST_AGENT_INDEX_SHA256=b83c1b81e085cc509d9a0d9af29e78a48d54776416db53f7be61928f0a39087a
SITE_WORKTREE_CLEAN=true
PUBLIC_PROJECTION_CHANGED=false
```

## 7. 活动对象与残留名称分类

两个此前阻塞的活动对象已经不再包含旧内部名称：

```text
PROJECT_STATUS_ACTIVE_OLD_FIELDS=0
AGENT_READABLE_LINE_74_ACTIVE_OLD_REFERENCES=0
ACTIVE_INTERNAL_OBJECTS_MIGRATED=true
```

剩余 `evaluate_agent_run` 命中继续属于以下允许类别：

- `PUBLIC_OPERATION`（公开操作）：规范 `saee.evaluate_agent_run` 及其公开别名；
- `HISTORICAL_FACT`（历史事实）：旧版本标题、发布记录、冻结测试输入和旧文件名；
- `LOCAL_IMPLEMENTATION_SYMBOL`（局部实现符号）：仍由内部路由以新内部契约名调用的函数符号；
- `PUBLIC_PROJECTION_FROZEN`（公开投影冻结）：不属于内部迁移范围的站点发现快照；
- `EXACT_HISTORY_COMPATIBILITY`（准确历史兼容）：只对已登记冻结发布对象执行的有界兼容映射。

没有把“仓库内零旧字符串”作为完成标准，也没有使用递归名称替换。

## 8. 验证结果

以下隔离工作区验证通过：

```text
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
python3 scripts/saee_development_constitution_smoke.py
python3 scripts/saee_capability_progress_ledger_smoke.py
python3 scripts/saee_canonical_capability_inventory_smoke.py
python3 scripts/saee_agent_evidence_merge_readiness_check.py
python3 scripts/saee_agent_readiness_architecture_smoke.py
python3 scripts/saee_agent_capability_alpha_smoke.py
python3 scripts/saee_capability_truth_consistency_smoke.py
python3 scripts/saee_capability_runtime_smoke.py
python3 scripts/saee_capability_mcp_adapter_smoke.py
python3 scripts/saee_capability_http_adapter_smoke.py
python3 scripts/saee_ecosystem_demo_smoke.py
python3 scripts/saee_first_external_validation_simulation_smoke.py
python3 scripts/saee_mcp_ecosystem_dry_integration_smoke.py
python3 scripts/saee_agent_rehearsal_design_partner_protocol_smoke.py
python3 scripts/mainline_guard.py
```

```text
PUBLIC_PROTECTION_VALIDATION=PASS
INTERNAL_TOOL_DISCOVERY_VALIDATION=PASS
ACTIVE_INTERNAL_OBJECT_VALIDATION=PASS
DEMO_VALIDATION=PASS
SIMULATOR_VALIDATION=PASS
MAINLINE_GUARD=PASS
GLOBAL_RECURSIVE_NAME_REPLACEMENT_USED=false
```

## 9. 验证副作用与恢复

主线守卫通过，但其内部若干商业状态协调器写入了本地生成文件，并刷新了 `agent-index.json`（智能体索引）。这些变化不属于本次授权。

精确清单比较发现该副作用后，立即停止继续验证，并执行以下恢复：

1. 所有商业本地生成文件从只读基线恢复；
2. `agent-index.json`（智能体索引）恢复到实施前摘要；
3. 两个获授权对象保持迁移结果；
4. 再次比较排除两个目标文件后的完整清单。

恢复后的 `agent-index.json`（智能体索引）摘要与实施前完全一致：

```text
AGENT_INDEX_PRE_SHA256=4ba882f0466086f31ab35b99c169c95ea8aff20ddad45812428ba75d9e85dc67
AGENT_INDEX_FINAL_SHA256=4ba882f0466086f31ab35b99c169c95ea8aff20ddad45812428ba75d9e85dc67
MAINLINE_GUARD_GENERATED_SIDE_EFFECTS_DETECTED=true
MAINLINE_GUARD_GENERATED_SIDE_EFFECTS_RESTORED=true
UNAUTHORIZED_OBJECTS_CHANGED=false
```

这次副作用说明：验证通过和补丁纯净是两个独立结论；主线守卫通过不能替代验证后差异复核。

## 10. 最终隔离补丁摘要

最终隔离工作副本相对只读基线共有 99 个差异文件。相比停止时的 98 个差异文件，只新增 `PROJECT_STATUS.md`；`agent-readable.md` 已在原候选补丁中，本次只增加第 74 行的准确对象变化。

最终清单：

```text
/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001/evidence/phase2-1-final-changed-paths.txt
FINAL_CHANGED_FILE_COUNT=99
FINAL_CHANGED_PATHS_SHA256=1a19103a9b0f6b97d69ae65dd56c376ec985bb62972ce9e9bc0f51086e34fa32
PYC_REMAINING=0
PYCACHE_DIRS_REMAINING=0
```

## 11. 指挥官命令核查

本次只收敛智能体证据与评估主线中的内部契约名称，没有修改公开能力、增加产品层、扩大协议或重新启动目标完整性副线。

```text
PROGRAM_MAINLINE=saee_agent_evidence_integration
IMPLEMENTATION_SCOPE=EXACT_INTERNAL_OBJECT_MIGRATION_ONLY
MAINLINE_DRIFT_DETECTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

前几轮教训继续有效：

1. 文件授权不等于对象授权；
2. 历史名称、公开名称和当前内部名称必须分别处理；
3. 技术验证通过不等于补丁纯净；
4. 实施完成不等于合并授权；
5. 任何验证器生成噪声都必须从补丁中剔除。

## 12. 未执行事项

```text
MAIN_WORKSPACE_IMPLEMENTATION_CODE_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
MERGE_EXECUTED=false
PUBLIC_RELEASE_EXECUTED=false
```

没有修改主工作区现有实现文件；没有暂存、提交、推送或合并隔离补丁。

## 13. 最终状态

```text
PHASE2_1_EXACT_OBJECT_IMPLEMENTATION_REPORT_STATUS=COMPLETE
IMPLEMENTATION_AUTHORIZED=true
EXACT_OBJECT_IMPLEMENTATION_STATUS=COMPLETE
ACTIVE_INTERNAL_OBJECTS_MIGRATED=true
ACTIVE_CALLERS_MIGRATED=true
INTERNAL_RENAME_COMPLETE=true
UNAUTHORIZED_OBJECTS_CHANGED=false
PUBLIC_CAPABILITY_CHANGED=false
PUBLIC_MCP_CHANGED=false
PUBLIC_SCHEMA_CHANGED=false
SCHEMA_FIELD_SEMANTICS_CHANGED=false
EVALUATION_ALGORITHM_CHANGED=false
HISTORICAL_EVIDENCE_CHANGED=false
PUBLIC_PROJECTION_CHANGED=false
NEW_CAPABILITY_CREATED=false
CAPABILITY_COUNT=9
PATCH_APPROVED_FOR_MERGE=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_PATCH_REVIEW_OF_PHASE2_1_FINAL_ISOLATED_PATCH
```
