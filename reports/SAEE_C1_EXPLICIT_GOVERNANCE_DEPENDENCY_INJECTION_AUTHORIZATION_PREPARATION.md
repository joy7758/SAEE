# SAEE C1 外部治理依赖显式注入授权准备

日期：2026-07-17

## 1. 目的

本文件为 C1（第一阶段候选）验证契约的最小调整准备精确授权范围。它不是实施授权，不修改候选、代码、MCP（模型上下文协议）、Schema（数据结构规范）或能力清单。

依据：

```text
INDEPENDENT_REVIEW_SOURCE=reports/SAEE_C1_AGENT_EVIDENCE_BOUND_EXTERNAL_DEPENDENCY_INDEPENDENT_REVIEW.md
INDEPENDENT_REVIEW_SOURCE_SHA256=b79f1074e96052b8cce90374027fc761379d4f22d04ff4ef3b298a251c4c1325
INDEPENDENT_REVIEW_VERDICT=C1_CANDIDATE_REQUIRES_ADJUSTMENT
RECOMMENDED_OPTION=EXPLICIT_EXTERNAL_GOVERNANCE_ROOT_INJECTION
```

## 2. 当前候选和阻塞事实

```text
C1_ISOLATED_WORKTREE=/Users/zhangbin/Documents/SAEE-c1-agent-evidence-baseline-isolated-001
C1_PARENT_HASH=f8eb7fd05b3f97b86fb753b3ba05e9b86686558c
C1_PATH_COUNT=24
C1_TRACKED_CHANGE_COUNT=0
C1_STAGED_PATH_COUNT=0
C1_D_CLASS_PRESENT_COUNT=0
C1_BASELINE_CREATED=false
```

当前迁移就绪校验器把候选根目录同时当作候选对象根目录和三项外部治理对象根目录。三项治理对象被排除后，直接离线运行返回失败，因此依赖边界处于隐藏状态。

此外，三项治理对象当前均为主工作区未跟踪文件：

```text
EXTERNAL_GOVERNANCE_DEPENDENCY_GIT_STATE=UNTRACKED
EXTERNAL_GOVERNANCE_DEPENDENCY_BASELINE_CREATED=false
EXTERNAL_GOVERNANCE_DEPENDENCY_DURABLE_PROVENANCE=false
```

这意味着显式注入可以修复“依赖不可发现”的问题，但不能自动证明外部对象已拥有独立、持久的历史基线。

## 3. 精确允许修改对象

只允许以下两个对象：

### C1-GD-01

```text
path=scripts/saee_agent_evidence_merge_readiness_check.py
current_sha256=69fac456a1e70c902864180835455eee7c037a5b9ed335cc9d1727fce968bad3
```

允许：

- 增加显式外部治理根目录参数；
- 将候选内对象和外部治理对象分开解析；
- 增加三项外部文件的精确路径和散列校验；
- 缺少参数、文件、散列不匹配或解析失败时按失败关闭方式停止；
- 更新命令帮助和错误信息，使依赖边界对智能体可读。

禁止：

- 修改现有文档语义验证规则；
- 修改来源许可证判断；
- 修改能力事实来源；
- 修改公开能力、公开 MCP（模型上下文协议）或公开 Schema（数据结构规范）；
- 将外部治理对象复制进代码或候选。

### C1-GD-02

```text
path=tests/test_agent_evidence_merge_readiness.py
current_sha256=39b873133b71de4a8f8b43ff87540abc9960a0d779cb02c67d56e4184eefebf6
```

允许：

- 让测试通过显式测试配置提供外部治理根目录；
- 让子进程测试显式传入同一根目录；
- 增加依赖缺失、路径错误、散列不匹配和候选根目录污染的失败用例；
- 保留现有正向和负向语义验证覆盖。

禁止：

- 删除现有负向测试；
- 通过跳过、弱化断言或捕获失败来制造通过；
- 使用固定本机绝对路径作为默认值；
- 自动从网络、远程仓库或未声明位置下载依赖。

## 4. 三项外部治理对象绑定

只允许读取，不允许修改或纳入 C1：

```text
governance/migration/agent-evidence-migration-crosswalk.v1.json
SHA256=1b49bff4488059c26facfacf874fa67bfd6775861d251d14cc2ec66c6018c519

governance/migration/agent-evidence-schema-compatibility.v1.json
SHA256=b88c35aaffda6d120f39b7150d8eb1965c30c7d713b193b229510adbf4ecc0ae

governance/migration/saee-three-version-integration-plan.v1.json
SHA256=15cce213d3e51631f7e57a19fc2daec8ce6d8deee9094ef6701da1d04c009ef6
```

集合级绑定：

```text
D_CLASS_EXTERNAL_DEPENDENCY_MANIFEST_SHA256=8a4cdc72986784788320056ea7a5b2dbbc04a298c312b41a494f52e792ed7973
```

绑定要求：

1. 外部根目录必须由调用者显式提供；
2. 三项相对路径必须完全匹配；
3. 单文件散列和集合清单散列必须匹配；
4. 不得跟随符号链接逃出显式根目录；
5. 不得把外部对象状态升级为规范能力事实；
6. 不得把其中的 M-07 字段解释为授权。

## 5. 目标调用契约

建议新增一个显式命令行参数：

```text
--governance-root
```

参数语义：只为三项外部治理对象提供根目录。以下候选内对象仍必须从候选根目录读取：

```text
governance/migration/agent-evidence-source-provenance.v1.json
governance/migration/agent-evidence-m03-owner-decision.v1.json
```

测试运行允许使用一个同义的显式环境变量：

```text
SAEE_AGENT_EVIDENCE_GOVERNANCE_ROOT
```

环境变量只用于测试入口，不得作为校验器命令行的隐藏默认授权来源。子进程测试仍必须把解析后的路径通过 `--governance-root` 显式传入。

## 6. 失败关闭规则

必须验证以下行为：

```text
NO_GOVERNANCE_ROOT=FAIL
MISSING_EXTERNAL_OBJECT=FAIL
UNEXPECTED_EXTERNAL_PATH=FAIL
EXTERNAL_OBJECT_HASH_MISMATCH=FAIL
EXTERNAL_OBJECT_PARSE_FAILURE=FAIL
SYMLINK_ROOT_ESCAPE=FAIL
M07_FIELD_PRESENT=NON_AUTHORIZING_INPUT_ONLY
```

不得把依赖缺失降级为警告，也不得回退到主工作区、父目录、网络或其他搜索路径。

## 7. 调整后验证矩阵

重新构造候选后必须通过：

1. 24 项路径集合精确匹配；
2. 三项 D 类对象仍不在候选；
3. 两个授权对象之外无内容变化；
4. 候选内全部 JSON（结构化数据格式）解析；
5. 候选内全部 Python（蟒蛇编程语言）语法检查；
6. 适配器专项校验；
7. 评估桥接专项校验；
8. 外部治理依赖正向校验；
9. 外部依赖缺失和散列不匹配负向校验；
10. 迁移就绪测试全部通过；
11. 完整单元测试全部通过；
12. 开发宪法、治理登记、规范能力清单、能力进度台账和能力真值一致性校验全部通过；
13. 无生成缓存、无尾随空格、无额外暂存路径。

调整后必须重新计算：

```text
C1_SELECTED_SORTED_PATH_SET_SHA256
C1_SELECTED_SORTED_MANIFEST_SHA256
C1-GD-01_NEW_SHA256
C1-GD-02_NEW_SHA256
```

## 8. 外部依赖持久性边界

即使上述调整全部通过，仍必须保持：

```text
EXTERNAL_GOVERNANCE_DEPENDENCY_BASELINE_CREATED=false
EXTERNAL_GOVERNANCE_DEPENDENCY_DURABLE_PROVENANCE=false
C1_BASELINE_CREATED=false
C1_COMMIT_AUTHORIZED=false
```

正式 C1 提交审查必须单独决定：是否接受“显式散列绑定但未形成独立历史基线”的外部治理输入。当前授权准备不替代该决定，也不授权建立新的治理基线。

## 9. 禁止范围

禁止：

- 修改其他 22 项 C1 对象；
- 修改或加入三项 D 类对象；
- 修改公开 `saee.evaluate_agent_run`；
- 修改公开 MCP（模型上下文协议）、公开 Schema（数据结构规范）或能力数量；
- 修改评估算法、字段语义或来源许可证边界；
- 创建新能力、新协议、新运行时或新仓库；
- 开启 Goal Integrity（目标完整性）、State Integrity（状态完整性）或 Trust Continuity（可信连续性）工程；
- 暂存、提交、推送或合并。

## 10. 推荐人工决定

推荐批准两个对象的精确调整，但不批准 C1 提交：

```text
RECOMMENDED_HUMAN_DECISION=APPROVE_C1_EXPLICIT_GOVERNANCE_DEPENDENCY_INJECTION_ONLY
RECOMMENDED_IMPLEMENTATION_SCOPE=C1_GD_01_AND_C1_GD_02_ONLY
C1_COMMIT_REMAINS_SEPARATELY_GATED=true
```

建议人工授权常量：

```text
APPROVE_C1_EXPLICIT_GOVERNANCE_DEPENDENCY_INJECTION=true
```

在人工明确记录该常量前，不实施调整。

## 11. 最终状态

```text
C1_GOVERNANCE_DEPENDENCY_AUTHORIZATION_PREPARATION_STATUS=COMPLETE
C1_GOVERNANCE_DEPENDENCY_INJECTION_AUTHORIZED=false
C1_ADJUSTMENT_IMPLEMENTED=false
C1_CANDIDATE_RECONSTRUCTED=false
C1_BASELINE_CREATED=false
C1_COMMIT_AUTHORIZED=false
EXTERNAL_GOVERNANCE_DEPENDENCY_BASELINE_CREATED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CURRENT_CAPABILITY_UNCHANGED=true
NEW_CAPABILITY_CREATED=false
PUBLIC_MCP_CHANGED=false
PUBLIC_SCHEMA_CHANGED=false
CODE_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
GIT_MERGE_EXECUTED=false
MAINLINE_DRIFT_DETECTED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
STATE_INTEGRITY_SECONDARY_LANE=STOPPED
TRUST_CONTINUITY_IMPLEMENTED=false
NEXT_ACTION=HUMAN_DECISION_ON_C1_EXPLICIT_GOVERNANCE_DEPENDENCY_INJECTION
```
