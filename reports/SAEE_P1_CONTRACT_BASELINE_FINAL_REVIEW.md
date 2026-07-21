# SAEE P1 契约父基线最终审查与建立结果

日期：2026-07-17

## 1. 结论

P1（契约父基线第一阶段）隔离候选已经从指定 F1（基础锚点第一阶段）提交准确构造，九十九路径集合、权限和批准后目标状态摘要全部匹配，且测试运行没有污染候选或 F1 工作区。

首次验证发现三项依赖问题。后续精确审查确认：两个缺失脚本分别属于旧项目记忆验证面和 M03-M06（第三至第六里程碑）未来子基线验证面，不是 P1 提交闭环；排演协议所需的四个运行对象则属于封存验证夹具，可以临时挂载验证而不进入提交。按该边界修正后，全部 P1 相关校验、公开契约测试、专门 JSON（数据交换格式）解析、规范引用检查和完整单元测试均通过，候选仍严格保持九十九路径。

```text
P1_BASELINE_REVIEW_VERDICT=BASELINE_CREATED_AND_PUSHED
P1_CANDIDATE_CONSTRUCTION_STATUS=COMPLETE
P1_CANDIDATE_VALIDATION_STATUS=PASS
P1_BASELINE_CREATED=true
P1_BASELINE_VALIDATED=true
P1_COMMIT_HASH=f8eb7fd05b3f97b86fb753b3ba05e9b86686558c
P1_BRANCH=agent/p1-contract-baseline-v1
P1_COMMIT_AUTHORIZED=true
PUSH_AUTHORIZED=true
PUSH_EXECUTED=true
MERGE_EXECUTED=false
```

人工提交与推送授权来自当前对话的明确目标“修正问题，完成推送”，不来自本报告或评估建议。

## 2. 来源与父节点

```text
P1_ISOLATED_WORKTREE=/Users/zhangbin/Documents/SAEE-p1-contract-baseline-isolated-001
P1_PARENT_HASH=80898a4b9311e6c48f55c068abd6401014ca9cb8
P1_PARENT_IS_F1=true
INITIAL_WORKTREE_CLEAN=true
DETACHED_HEAD=true
```

权威来源：

```text
APPROVED_ROOT=/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001
APPROVED_BASELINE=/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001/baseline
APPROVED_WORKSPACE=/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001/workspace
APPROVED_PATH_LIST=/Users/zhangbin/Documents/SAEE-contract-alignment-phase2-1-attempt-001/evidence/phase2-1-final-changed-paths.txt
```

权威报告散列：

```text
FINAL_PATCH_REVIEW_SHA256=3bfbd07d0ac9d8c94fad29653ca55e88f097ca067c62aacfa4abea15c89ab694
APPLY_REPORT_SHA256=9ddcf7b2121f19c25a7d288aa8782e8500861fb72b81fc1c44e9b7ec48d8fcd7
```

构造前独立核验：

```text
P1_PATH_COUNT=99
P1_PATH_LIST_SHA256=1a19103a9b0f6b97d69ae65dd56c376ec985bb62972ce9e9bc0f51086e34fa32
P1_POST_STATE_MANIFEST_SHA256=c5d5bc5f4fe6b2a6fb41f7082d6ac9a344ed31f382772648d02a9cf6e08328c3
APPROVED_BASELINE_MISSING_PATH_COUNT=0
APPROVED_WORKSPACE_MISSING_PATH_COUNT=0
APPROVED_PATHS_CHANGED_IN_TRANSITION=99/99
APPROVED_MODE_MISMATCH_COUNT=0
```

目标状态清单使用每行“路径、权限、文件内容 SHA-256（安全散列算法二百五十六位）”的制表符分隔形式独立复算；结果与冻结摘要完全一致。

## 3. 构造方法与边界

使用封存路径清单作为唯一输入，把批准工作副本中的九十九个目标对象机械应用到从 F1 提交创建的新分离式工作树。没有从主工作区差异、主工作区暂存区、记忆或语义推断重建对象。

```text
WHOLE_REPOSITORY_COPIED=false
MAIN_WORKSPACE_INDEX_USED=false
AUTO_FORMAT_EXECUTED=false
AUTO_FIX_EXECUTED=false
CONTRACT_REGENERATED=false
ALLOWLIST_EXPANDED=false
GIT_ADD_EXECUTED=true
GIT_COMMIT_EXECUTED=true
GIT_MERGE_EXECUTED=false
GIT_PUSH_EXECUTED=true
```

## 4. 九十九路径完整清单

以下机器路径保持原样：

```text
001 PROJECT_STATUS.md
002 README.md
003 agent-index.json
004 agent-interface/architecture/saee-agent-readiness-architecture.v1.json
005 agent-interface/capabilities/saee-evaluate-agent-run-capability.v0.1.json
006 agent-interface/capabilities/saee-evaluate-agent-run-output.v0.1.schema.json
007 agent-interface/ecosystem/first-validation-simulation-scenarios/02-successful-tool-invocation.json
008 agent-interface/ecosystem/saee-first-validation-candidate-matrix.v0.1.json
009 agent-interface/ecosystem/saee-volcengine-capability-mapping.v0.1.json
010 agent-interface/http/saee-capability-http-adapter.v0.1.json
011 agent-interface/integration/examples/authorization-confusion-agent.json
012 agent-interface/integration/examples/correct-mcp-agent.json
013 agent-interface/integration/examples/result-overinterpretation-agent.json
014 agent-interface/mcp/invocation-evaluation/examples/boundary-aware-agent.json
015 agent-interface/mcp/invocation-evaluation/examples/correct-mcp-agent.json
016 agent-interface/mcp/invocation-evaluation/examples/invalid-mcp-caller.json
017 agent-interface/mcp/invocation-evaluation/examples/response-overinterpretation-agent.json
018 agent-interface/mcp/invocation-evaluation/examples/wrong-tool-selection-agent.json
019 agent-interface/mcp/mcp-dry-integration-scenarios/RELIABILITY_ASSESSMENT_TASK.json
020 agent-interface/mcp/saee-capability-mcp-adapter.v0.1.json
021 agent-interface/mcp/saee-capability-mcp-stdio-config.v0.1.json
022 agent-interface/mcp/saee-evaluate-agent-run-mcp-capability.v0.1.json
023 agent-interface/mcp/saee-mcp-evaluate-agent-run-request.v0.1.schema.json
024 agent-interface/mcp/saee-mcp-evaluate-agent-run-response.v0.1.schema.json
025 agent-readable.md
026 capability-package/README.md
027 capability-package/capability-card.json
028 capability-package/examples/evaluate-agent-run.json
029 capability-package/limitations.md
030 capability-package/manifest.json
031 capability-package/mcp-tool.json
032 capability-package/openapi.yaml
033 docs/CAPABILITY_INVENTORY.md
034 docs/architecture/SAEE_AGENT_CAPABILITY_ALPHA.md
035 docs/architecture/SAEE_AGENT_READINESS_ARCHITECTURE_V1.md
036 docs/architecture/SAEE_CAPABILITY_HTTP_ADAPTER_ALPHA.md
037 docs/architecture/SAEE_CAPABILITY_MCP_ADAPTER_ALPHA.md
038 docs/architecture/SAEE_CAPABILITY_RUNTIME_ALPHA.md
039 docs/architecture/SAEE_EVALUATE_AGENT_RUN_MCP_CAPABILITY.md
040 docs/architecture/SAEE_LOCAL_MCP_PROTOTYPE.md
041 docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_DEMO.md
042 docs/commercial/SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_PROTOCOL.md
043 docs/ecosystem/SAEE_ECOSYSTEM_ENTRY_PACKAGE_REVIEW.md
044 docs/ecosystem/SAEE_FIRST_EXTERNAL_VALIDATION_SIMULATION.md
045 docs/ecosystem/SAEE_MCP_DRY_INTEGRATION_VALIDATION.md
046 docs/ecosystem/SAEE_VOLCENGINE_ARK_INTEGRATION_STRATEGY.md
047 docs/public/SAEE_AGENT_NATIVE_CAPABILITY_SURFACE.md
048 docs/release/SAEE_CAPABILITY_VERSION_POLICY.md
049 ecosystem/first-validation-candidate-package-v1/candidate-profile.md
050 ecosystem/mcp-entry-package-v1/agent-usage-guide.md
051 ecosystem/mcp-entry-package-v1/mcp-tools.json
052 ecosystem/participant-package-v0.1/capability-reference.json
053 examples/agent-integrations/mcp-client-example/README.md
054 examples/agent-integrations/mcp-client-example/client_flow.md
055 examples/agent-integrations/mcp-client-example/example_config.json
056 examples/ecosystem-demo-v1/README.md
057 examples/ecosystem-demo-v1/agent-flow.md
058 examples/ecosystem-demo-v1/mcp-demo.md
059 examples/ecosystem-demo-v1/result-example.json
060 examples/ecosystem-demo-v1/scenario/coding-agent-preflight.json
061 governance/registry/mcp-registry.json
062 llms.txt
063 saee_backend/services/agent_integration_evaluator.py
064 saee_backend/services/agent_run_capability.py
065 saee_backend/services/capability_http_adapter/http_request_handler.py
066 saee_backend/services/capability_mcp_adapter.py
067 saee_backend/services/capability_runtime/capability_invocation.py
068 saee_backend/services/capability_runtime/capability_registry_loader.py
069 saee_backend/services/capability_runtime/capability_router.py
070 saee_backend/services/capability_runtime/invocation_receipt.py
071 saee_backend/services/capability_truth_consistency_validator.py
072 saee_backend/services/ecosystem_demo_validator.py
073 saee_backend/services/ecosystem_entry_package_validator.py
074 saee_backend/services/first_external_validation_simulation.py
075 saee_backend/services/local_mcp_server.py
076 saee_backend/services/mcp_agent_run_tool_handler.py
077 saee_backend/services/mcp_ecosystem_discovery_simulator.py
078 saee_backend/services/mcp_ecosystem_dry_integration.py
079 saee_backend/services/mcp_result_interpretation_validator.py
080 schemas/saee-capability-http-response.schema.v0.1.json
081 schemas/saee-capability-invocation-receipt.schema.v0.1.json
082 schemas/saee-capability-invocation-response.schema.v0.1.json
083 schemas/saee-ecosystem-validation-candidate.schema.v0.1.json
084 schemas/saee-mcp-dry-integration-trace.schema.v0.1.json
085 schemas/saee-synthetic-mcp-agent.schema.v0.1.json
086 scripts/saee_agent_capability_alpha_smoke.py
087 scripts/saee_agent_readiness_architecture_smoke.py
088 scripts/saee_agent_rehearsal_design_partner_protocol_smoke.py
089 scripts/saee_capability_http_adapter_smoke.py
090 scripts/saee_capability_http_demo.py
091 scripts/saee_capability_mcp_adapter_smoke.py
092 scripts/saee_capability_runtime_demo.py
093 scripts/saee_capability_runtime_smoke.py
094 scripts/saee_capability_service_package_smoke.py
095 scripts/saee_evaluate_agent_run.py
096 scripts/saee_evaluate_agent_run_mcp_smoke.py
097 scripts/saee_first_external_validation_simulation_smoke.py
098 scripts/saee_local_mcp_prototype_smoke.py
099 scripts/saee_mcp_ecosystem_dry_integration_smoke.py
```

## 5. 路径、内容与权限核验

```text
P1_CHANGED_PATH_COUNT=99
P1_PATH_SET_MATCH=true
P1_PATH_LIST_SHA256_MATCH=true
P1_POST_STATE_MANIFEST_SHA256_MATCH=true
P1_EXTRA_PATH_COUNT=0
P1_MISSING_PATH_COUNT=0
P1_CONTENT_MISMATCH_COUNT=0
P1_PERMISSION_MATCH=true
P1_NON_0644_PATH_COUNT=0
P1_UNTRACKED_PATH_COUNT=0
```

`git diff --name-status`（版本控制系统差异名称与状态）显示九十九项均为 `M`（已修改），没有新增、删除或权限变化。

`git diff --stat`（版本控制系统差异统计）结果：

```text
99 files changed, 307 insertions(+), 244 deletions(-)
```

`git diff --check`（版本控制系统差异格式检查）结果为通过。因为相对 F1 没有新增或未跟踪对象，`git diff --no-index --check`（无索引差异格式检查）不适用；不存在用普通差异检查遗漏新增文件的问题。

## 6. F1 对象未变化证明

九十九路径与十二项 F1 路径只有两个整文件重叠：`agent-index.json` 和 `llms.txt`。这两个文件允许被 P1 修改，但其 F1 精确对象必须保持不变。

```text
F1_AGENT_INDEX_CONSTITUTION_OBJECT_SHA256=a1ff98c78b569b492501368d8983992d171532debfafa62d811160bd94de4f78
F1_LLMS_AUTHORITY_RANGE_SHA256=2f0fce7ef9eb350b52d8275d4c991e2cfe6101970bb3f7131c880b0b5e81d30d
F1_NON_OVERLAP_FULL_FILE_MISMATCH_COUNT=0
F1_OBJECTS_UNCHANGED=true
```

测试后再次核验：

```text
F1_WORKTREE_HEAD=80898a4b9311e6c48f55c068abd6401014ca9cb8
F1_WORKTREE_STATUS_COUNT=0
P1_POST_TEST_CONTENT_MISMATCH_COUNT=0
P1_POST_TEST_MANIFEST_SHA256=c5d5bc5f4fe6b2a6fb41f7082d6ac9a344ed31f382772648d02a9cf6e08328c3
P1_POST_TEST_UNTRACKED_COUNT=0
P1_POST_TEST_BYTECODE_CACHE_COUNT=0
```

## 7. 契约语义核验

规范状态：

```text
INTERNAL_OPERATION_NAMES=evaluate_rehearsal_run;evaluate_evidence;rehearse_agent
PUBLIC_OPERATION_NAMES=saee.evaluate_agent_run;saee.evaluate_evidence
CANONICAL_CAPABILITY_COUNT_F1=9
CANONICAL_CAPABILITY_COUNT_P1=9
CANONICAL_CAPABILITY_COUNT_UNCHANGED=true
NEW_CAPABILITY_CREATED=false
```

两个规范公开能力对象在 F1 与 P1 中的规范化散列完全相同：

```text
SAEE_EVALUATE_AGENT_RUN_CANONICAL_OBJECT_SHA256=4bf039e802006f866b41962f65606b1b55b7b007c5527be22e121dd2d5f5ecea
SAEE_EVALUATE_EVIDENCE_CANONICAL_OBJECT_SHA256=50f5e03c149fff53f81a71b4dc6a5e87aa342da969c7654ec125d92b7e3637bd
PUBLIC_CAPABILITY_CHANGED=false
```

公开 MCP（模型上下文协议）入口和三份公开 Schema（数据结构规范）逐文件比较均与 F1 相同：

```text
PUBLIC_MCP_CHANGED=false
PUBLIC_SCHEMA_CHANGED=false
SCHEMA_FIELD_SEMANTICS_CHANGED=false
```

九十九路径全文扫描结果：

```text
evaluate_agent_run_MATCH_LINES=73
evaluate_agent_run_MATCH_FILES=24
evaluate_rehearsal_run_MATCH_LINES=214
evaluate_rehearsal_run_MATCH_FILES=98
saee.evaluate_agent_run_MATCH_LINES=29
saee.evaluate_agent_run_MATCH_FILES=11
saee.evaluate_evidence_MATCH_LINES=25
saee.evaluate_evidence_MATCH_FILES=10
BARE_OLD_NAME_MATCH_LINES=28
BARE_OLD_NAME_MATCH_FILES=13
```

二十八个旧裸名称命中已逐项分类：

1. 十项为内部 Python（蟒蛇编程语言）函数符号或准确别名绑定；对外及内部操作身份均已映射到新名称；
2. 八项为准确历史结果兼容或历史字段验证；额外命中会使校验失败；
3. 一项为规范公开能力的兼容别名；不覆盖规范公开入口；
4. 六项为明确标注“历史内部名称”的说明；
5. 三项为已废弃的历史 `recommended_next_pr`（历史建议字段）元数据。

未发现把旧裸名称作为新的活动内部操作标识、公开工具标识或第三个评估器的命中。

边界文本核验：

```text
RECOMMENDATION_AUTHORIZATION_BOUNDARY_FILE_HITS=15
EVIDENCE_REALITY_BOUNDARY_FILE_HITS=12
RECOMMENDATION_UPGRADED_TO_AUTHORIZATION=false
EVIDENCE_EQUATED_WITH_REALITY=false
COMPATIBILITY_OVERRIDES_CANONICAL=false
```

## 8. 校验与测试结果

所有已运行 Python（蟒蛇编程语言）命令均设置 `PYTHONDONTWRITEBYTECODE=1`，避免生成字节码。下表保留首次验证结果，作为依赖分类修正前的过程证据；表中“通过、失败、跳过”按命令或测试用例计数。

| 序号 | 完整命令 | 退出码 | 通过 | 失败 | 跳过 | 警告与说明 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `python3 scripts/saee_project_memory_check.py` | 2 | 0 | 1 | 0 | 脚本不在 F1 或九十九路径中 |
| 2 | `python3 scripts/saee_governance_registry_check.py` | 0 | 1 | 0 | 0 | 无 |
| 3 | `python3 scripts/saee_development_constitution_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 4 | `python3 scripts/saee_capability_progress_ledger_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 5 | `python3 scripts/saee_canonical_capability_inventory_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 6 | `python3 scripts/saee_agent_evidence_merge_readiness_check.py` | 2 | 0 | 1 | 0 | 脚本不在 F1 或九十九路径中 |
| 7 | `python3 scripts/saee_agent_readiness_architecture_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 8 | `python3 scripts/saee_agent_capability_alpha_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 9 | `python3 scripts/saee_capability_truth_consistency_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 10 | `python3 scripts/saee_capability_runtime_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 11 | `python3 scripts/saee_capability_mcp_adapter_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 12 | `python3 scripts/saee_capability_http_adapter_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 13 | `python3 scripts/saee_ecosystem_demo_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 14 | `python3 scripts/saee_first_external_validation_simulation_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 15 | `python3 scripts/saee_mcp_ecosystem_dry_integration_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 16 | `python3 scripts/saee_agent_rehearsal_design_partner_protocol_smoke.py` | 1 | 0 | 1 | 0 | 缺少被排除的 `output/controlled-rehearsal/qianfan-baseline-metadata-v0.2.run.json` |
| 17 | `python3 scripts/saee_evaluate_agent_run_mcp_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 18 | `python3 scripts/saee_local_mcp_prototype_smoke.py` | 0 | 1 | 0 | 0 | 无 |
| 19 | `python3 scripts/saee_public_capability_surface_smoke.py` | 0 | 1 | 0 | 0 | 两个公开操作保持一致 |
| 20 | `python3 scripts/saee_qianfan_readiness_mcp_smoke.py` | 0 | 1 | 0 | 0 | 两个公开操作调用通过 |
| 21 | `python3 scripts/saee_evidence_adequacy_smoke.py` | 0 | 1 | 0 | 0 | 一项 `DeprecationWarning`（弃用警告）；不影响退出结果 |
| 22 | `python3 scripts/saee_capability_service_package_smoke.py` | 0 | 1 | 0 | 0 | 能力包引用通过 |
| 23 | `python3 -m unittest discover -s tests -v` | 0 | 12 | 0 | 0 | 十二项单元测试通过 |

命令级汇总：

```text
COMMAND_COUNT=23
COMMAND_PASS_COUNT=20
COMMAND_FAIL_COUNT=3
COMMAND_SKIP_COUNT=0
UNIT_TEST_CASES_PASS=12
UNIT_TEST_CASES_FAIL=0
UNIT_TEST_CASES_SKIP=0
```

证据充分性校验的内部计数：

```text
profile_schema_cases=4/4
positive_cases=4/4
negative_cases=4/4
adversarial_cases=16/16
deterministic_runs=20/20
existing_receipt_regressions=3/3
network_calls=0
```

### 8.1 首次停止时尚未执行的检查

发现第一项超范围依赖后，本轮不再新增验证动作。以下专门检查未单独执行：

```text
DEDICATED_JSON_MANIFEST_PARSE_CHECK=NOT_RUN_IN_INITIAL_ATTEMPT
DEDICATED_REFERENCE_PATH_CONSISTENCY_CHECK=NOT_RUN_IN_INITIAL_ATTEMPT
MAINLINE_GUARD_RERUN=NOT_RUN_KNOWN_WRITE_SIDE_EFFECT
```

其中多项已通过校验会间接解析 JSON（JavaScript 对象表示法）和清单，但不能把间接覆盖写成专门检查已完成。`scripts/mainline_guard.py`（主线守卫）在此前封存补丁审查中通过，但因其已知会写入生成状态，本轮没有让它改变待审候选。

### 8.2 启动器说明

第一次测试批处理启动器因包含临时目录清理命令而被安全策略拒绝；第二次启动器因使用了 Zsh（Z 外壳）保留的关联数组名而在任何测试执行前退出。两次均没有改动仓库。第三次启动器使用新的临时日志目录并实际产生上表结果。这两项属于执行器准备事件，不计入候选测试通过或失败数量。

### 8.3 边界修正后的最终复验

两个缺失校验器不再作为 P1 必须项：

```text
scripts/saee_project_memory_check.py=P1_SCOPE_NOT_APPLICABLE
scripts/saee_agent_evidence_merge_readiness_check.py=M03_M06_CHILD_BASELINE_ONLY
```

该分类没有删除失败证据，也没有把失败改写为通过；它纠正的是验证器与历史层级的错误绑定。

排演协议校验使用封存批准前后均一致的四个运行夹具临时验证。四个夹具的 SHA-256（安全散列算法二百五十六位）为：

```text
qianfan-baseline-metadata-v0.2.run.json=5e87a32b2d4e6d90d994d0e80736999115ad42df6769f63766a2b1e506a011c2
qianfan-tool-timeout-v0.2.run.json=91afd132908bec4d1d7b851b2a755bda95a9a7fcb05ca1ea14df3ce95b71ab5c
qianfan-instruction-conflict-v0.2.run.json=a42669c023512de57a2520e2c673439453144afc4829d51341ccc757823c87a6
qianfan-saas-release-readiness.v0.3.run.json=2d6141d05fad8d3c299f280e9719db9920de98b92c1684c675ab72da12120e37
```

夹具没有暂存、提交或留在候选的未跟踪集合中。校验结果：

```text
SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_PROTOCOL_SMOKE=PASS
profiles=3/3
metrics=6/6
demo_cases=4/4
benchmark_cases=20/20
invalid_cases=10/10
review_boundary_cases=6/6
session_gate_boundary_cases=10/10
deterministic_runs=5/5
POST_FIXTURE_CLEANUP_UNTRACKED_COUNT=0
```

随后重新运行二十条 P1 相关命令，结果：

```text
FINAL_RELEVANT_COMMAND_COUNT=20
FINAL_RELEVANT_COMMAND_PASS=20
FINAL_RELEVANT_COMMAND_FAIL=0
FINAL_RELEVANT_COMMAND_SKIP=0
UNIT_TEST_CASES_PASS=12
UNIT_TEST_CASES_FAIL=0
UNIT_TEST_CASES_SKIP=0
```

专门解析与引用检查：

```text
JSON_PARSE_TOTAL=38
JSON_PARSE_FAIL=0
CANONICAL_REFERENCE_COUNT=42
CANONICAL_REFERENCE_MISSING_COUNT=0
GIT_DIFF_CHECK=PASS
```

`scripts/mainline_guard.py`（主线守卫）仍未重跑，因为它存在已确认的生成状态写入副作用；本轮已经逐项运行与 P1 相关的只读核心校验，不能把避免写入解释为验证失败。

## 9. 修正记录

### 9.1 两个既有校验脚本的层级纠正

以下文件存在于主工作区的其他推进材料中，但不属于 F1 提交，也不属于批准九十九路径：

```text
scripts/saee_project_memory_check.py
scripts/saee_agent_evidence_merge_readiness_check.py
```

把它们复制进候选会违反九十九路径精确范围，并可能混入 M03-M06 或其他未授权主线材料，因此没有复制。最终复验不再错误要求 P1 自身包含它们。

### 9.2 排演协议夹具外置

`scripts/saee_agent_rehearsal_design_partner_protocol_smoke.py` 读取：

```text
output/controlled-rehearsal/qianfan-baseline-metadata-v0.2.run.json
```

`output/` 属于本次明确排除范围。没有补造或提交这些文件；仅从批准工作副本临时挂载四个逐散列验证夹具，校验通过后精确移除。

### 9.3 结论

三个首次失败已经通过“验证器层级纠正”和“封存夹具外置”解决，没有改变九十九路径内容，也没有增加提交对象。

```text
ACTIVE_VALIDATION_BLOCKER_COUNT=0
SCOPE_EXPANSION_EXECUTED=false
P1_FULL_VALIDATION_PASS=true
```

## 10. 排除范围核验

```text
NEW_F1_CHANGE_INCLUDED=false
M03_M06_INCLUDED=false
AGENT_EVIDENCE_FORMAL_BASELINE_INCLUDED=false
TRUST_CONTINUITY_RESEARCH_INCLUDED=false
ACADEMIC_SUBMISSION_INCLUDED=false
COMMERCIAL_POSITIONING_INCLUDED=false
ARCHITECTURE_REUNIFICATION_REPORT_INCLUDED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
STATE_INTEGRITY_SECONDARY_LANE=STOPPED
TRUST_CONTINUITY_IMPLEMENTED=false
NEW_MCP_TOOL_CREATED=false
NEW_SCHEMA_CREATED=false
NEW_RUNTIME_CREATED=false
NEW_PRODUCT_CAPABILITY_CREATED=false
NEW_GOVERNANCE_CAPABILITY_CREATED=false
MAIN_WORKSPACE_UNTRACKED_FILES_INCLUDED=false
```

## 11. 架构真值

```text
ENGINEERING_CORE=DIGITAL_BIOSPHERE_EVOLUTION_ENGINE
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
READINESS_ARCHITECTURE_ROLE=L3_PRODUCT_AND_EVALUATION_PROJECTION
CANONICAL_CAPABILITY_COUNT_UNCHANGED=true
NEW_CAPABILITY_CREATED=false
TRUST_CONTINUITY_IMPLEMENTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
STATE_INTEGRITY_SECONDARY_LANE=STOPPED
PUBLIC_NETWORK_MCP_DEPLOYED=false
PRODUCTION_READY=false
MAINLINE_DRIFT_DETECTED=false
```

本轮没有把 Readiness Architecture（就绪架构）升级为工程核心，也没有把 Trust Continuity（可信连续性）写成当前能力。

## 12. SAEE 智能体审查边界

本轮处于构造运行后、人工提交授权前的高影响检查点，因此读取了本地 SAEE 智能体审查技能并核对其适用边界。规范操作可以从能力清单解析，但当前会话没有已配置的 SAEE MCP（模型上下文协议）连接，因此没有虚构工具调用或返回值。

```text
SAEE_AGENT_REVIEW_SKILL_USED=true
SAEE_CANONICAL_OPERATION_RESOLVED=true
SAEE_MCP_RUNTIME_AVAILABLE=false
SAEE_TOOL_CALLED=false
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
```

基于当时已声明证据，技能边界内的适当建议为 `HUMAN_REVIEW_REQUIRED`（需要人工审查）；它不构成提交批准。随后当前对话给出了明确的人类提交与推送授权，实际操作依据该授权执行，而不是依据技能建议自动升级权限。

## 13. 剩余风险

1. 以前的最终补丁审查在包含更多未提交工作区材料的环境中运行了两个非 P1 校验脚本；本轮已经纠正层级，但未来基线设计仍应在预注册时绑定每个校验器所属历史层。
2. 排演协议校验依赖外置运行夹具；本轮已使用散列封存方式验证，但夹具尚未成为独立、长期可复用的测试资产包。
3. 旧裸函数符号仍作为准确兼容实现细节存在。当前验证表明它没有覆盖规范操作，但未来若删除兼容符号，需要新的迁移授权。
4. `jsonschema.RefResolver`（JSON 数据结构引用解析器）产生一项弃用警告；当前不是失败，但未来依赖升级可能成为维护问题。
5. GitHub（代码托管平台）远端主分支与本地 F1/P1 历史没有共同祖先；P1 可以作为独立基线分支推送，但不能把该推送自动解释为可直接合并的拉取请求。

## 14. 不声明事项

本报告不证明：

- P1 已合并到远端 `main`、创建标签或成为发布版本；
- 独立基线分支等于可直接合并的拉取请求；
- 公开 MCP 已部署到网络；
- 外部智能体互操作、客户验证或生产就绪已经完成；
- SAEE 已实现完整可信连续性、目标完整性、状态完整性、自主治理或授权系统；
- 证据等于完整现实；
- 评估建议等于人类授权。

## 15. 最终状态

```text
P1_CANDIDATE_CONSTRUCTION_STATUS=COMPLETE
P1_PARENT_IS_F1=true
P1_PARENT_HASH=80898a4b9311e6c48f55c068abd6401014ca9cb8
P1_COMMIT_HASH=f8eb7fd05b3f97b86fb753b3ba05e9b86686558c
P1_BRANCH=agent/p1-contract-baseline-v1
P1_PATH_COUNT=99
P1_PATH_SET_MATCH=true
P1_POST_STATE_MANIFEST_SHA256_MATCH=true
P1_PERMISSION_MATCH=true
F1_OBJECTS_UNCHANGED=true
P1_FULL_VALIDATION_PASS=true
P1_BASELINE_REVIEW_VERDICT=BASELINE_CREATED_AND_PUSHED
P1_BASELINE_CREATED=true
P1_BASELINE_VALIDATED=true
P1_COMMIT_AUTHORIZED=true
PUSH_AUTHORIZED=true
PUSH_REMOTE=https://github.com/joy7758/SAEE.git
PUSH_BRANCH=agent/p1-contract-baseline-v1
PUSH_EXECUTED=true
REMOTE_BRANCH_HASH=f8eb7fd05b3f97b86fb753b3ba05e9b86686558c
REMOTE_HASH_MATCH=true
PR_CREATED=false
PR_NOT_CREATED_REASON=UNRELATED_HISTORIES_BASELINE_BRANCH
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
MERGE_EXECUTED=false
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_PUSHED_P1_BASELINE
```
