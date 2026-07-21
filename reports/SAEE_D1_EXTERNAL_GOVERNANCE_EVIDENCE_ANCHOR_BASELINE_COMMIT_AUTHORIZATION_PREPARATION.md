# SAEE D1 External Governance Evidence Anchor Baseline Commit Authorization Preparation

## 1. 文件定位

本文件只准备 D1（外部治理证据锚点）基线提交的人工授权决定，不是授权本身，不执行暂存、提交、合并或推送。

```text
D1_AUTHORIZATION_PREPARATION_STATUS=COMPLETE
D1_CANDIDATE_INDEPENDENT_REVIEW=PASS
D1_CANDIDATE_COMMIT_READINESS=READY_PENDING_EXPLICIT_AUTHORIZATION
D1_BASELINE_COMMIT_AUTHORIZED=false
D1_BASELINE_CREATED=false
```

## 2. 决定选项

### 选项 A（推荐）

授权在 D1 隔离候选中建立一个仅含三项精确路径的非授权证据锚点提交。

```text
DECISION_OPTION_A=APPROVE_D1_BASELINE_COMMIT_CREATION
RECOMMENDED=true
AUTHORIZATION_TOKEN=APPROVE_D1_BASELINE_COMMIT_CREATION=true
```

推荐理由：

- D1 父节点、路径、权限和散列已独立复算通过；
- D1 能使 C1（智能体证据候选）的外部治理依赖可重现；
- D1 不是能力事实源，不授权 M-07（第七迁移阶段），不改变运行时、MCP（模型上下文协议）或 Schema（数据结构规范）；
- 先建立 D1 证据父系，再决定 C1 提交，可避免无历史锚点的隐式依赖。

### 选项 B

保留当前未提交候选，不建立 D1 历史锚点。

```text
DECISION_OPTION_B=HOLD_D1_CANDIDATE_WITHOUT_COMMIT
RECOMMENDED=false
```

影响：C1 可以继续做本地复现验证，但其三项外部治理依赖仍没有持久历史父系，C1 不应进入提交授权。

## 3. 候选与父节点绑定

```text
D1_CANDIDATE_PATH=/Users/zhangbin/Documents/文稿 - runtime-node-01/SAEE-d1-external-governance-evidence-anchor-isolated-001
D1_REQUIRED_PARENT=f8eb7fd05b3f97b86fb753b3ba05e9b86686558c
D1_REQUIRED_PARENT_ROLE=P1_CONTRACT_PARENT_BASELINE
D1_REQUIRED_PATH_COUNT=3
D1_REQUIRED_MANIFEST_SHA256=8a4cdc72986784788320056ea7a5b2dbbc04a298c312b41a494f52e792ed7973
D1_REQUIRED_ROLE=NON_AUTHORIZING_EXTERNAL_GOVERNANCE_EVIDENCE_ANCHOR
```

依据报告：

```text
CONSTRUCTION_REPORT_SHA256=c4e641181102a17495c615b93abb124d6a5b73d3bc0f403501bd0a351519cd65
INDEPENDENT_REVIEW_SHA256=3efa89161fe0269ab53ce8b7ae6bd5c968d9f841386fac29dcc5927b1be8b6e1
```

## 4. 唯一允许的提交路径

| 路径 | 权限 | SHA-256（安全散列算法二百五十六位） |
| --- | ---: | --- |
| `governance/migration/agent-evidence-migration-crosswalk.v1.json` | `644` | `1b49bff4488059c26facfacf874fa67bfd6775861d251d14cc2ec66c6018c519` |
| `governance/migration/agent-evidence-schema-compatibility.v1.json` | `644` | `b88c35aaffda6d120f39b7150d8eb1965c30c7d713b193b229510adbf4ecc0ae` |
| `governance/migration/saee-three-version-integration-plan.v1.json` | `644` | `15cce213d3e51631f7e57a19fc2daec8ce6d8deee9094ef6701da1d04c009ef6` |

授权若获批，只允许对上述三项路径执行精确暂存，不允许使用全仓库或全目录暂存。

## 5. 冻结的提交信息

```text
D1_COMMIT_MESSAGE=基线：建立 D1 非授权外部治理证据锚点
D1_COMMIT_COUNT=1
D1_COMMIT_PARENT_COUNT=1
D1_COMMIT_PARENT=f8eb7fd05b3f97b86fb753b3ba05e9b86686558c
```

提交信息不得宣称能力实现、M-07 授权、运行时集成、合并完成或生产就绪。

## 6. 授权后允许的操作

仅当人工明确记录以下状态后，才允许在 D1 隔离候选中执行：

```text
APPROVE_D1_BASELINE_COMMIT_CREATION=true
```

允许：

1. 对三项精确路径执行版本控制系统暂存；
2. 使用冻结信息建立一次 D1 提交；
3. 提交后重新验证父节点、路径集、权限、散列和 C1 可复现性；
4. 在 SAEE 主工作区生成一份未提交的 D1 基线建立报告。

## 7. 明确禁止

即使选项 A 获批，仍然禁止：

- 修改三项文件的字节、路径或权限；
- 暂存或提交第四项路径；
- 提交 C1 的二十四项候选文件；
- 合并 D1 或 C1；
- 推送任何分支或提交；
- 修改公开能力、MCP（模型上下文协议）、Schema（数据结构规范）、字段语义或评估算法；
- 将 D1 解释为能力源、授权源或生产证据；
- 启动 M-07、Goal Integrity（目标完整性）、State Integrity（状态完整性）或 Trust Infrastructure（可信基础设施）工程。

## 8. 提交前必须失败关闭的检查

任何一项不满足都必须停止，不得自动修复：

```text
D1_HEAD_MATCH_REQUIRED_PARENT=true
D1_TRACKED_CHANGE_COUNT=0
D1_STAGED_CHANGE_COUNT=0
D1_UNTRACKED_PATH_COUNT=3
D1_PATH_SET_MATCH=true
D1_PERMISSION_MATCH=true
D1_EXACT_OBJECT_HASHES_MATCH=true
D1_EXTERNAL_GOVERNANCE_MANIFEST_MATCH=true
D1_JSON_PARSE_PASS=true
D1_IS_CAPABILITY_SOURCE=false
D1_AUTHORIZES_M07=false
C1_REPRODUCIBILITY_WITH_D1=PASS
```

## 9. 提交后验证要求

若未来获得授权并完成提交，必须记录：

```text
D1_COMMIT_HASH=<new commit hash>
D1_PARENT_HASH=f8eb7fd05b3f97b86fb753b3ba05e9b86686558c
D1_COMMITTED_PATH_COUNT=3
D1_COMMITTED_PATH_SET_MATCH=true
D1_COMMITTED_OBJECT_HASHES_MATCH=true
D1_WORKTREE_CLEAN=true
C1_MERGE_READINESS_UNIT_TESTS_WITH_COMMITTED_D1=18/18_PASS
C1_FULL_UNIT_TESTS_WITH_COMMITTED_D1=68/68_PASS
D1_IS_CAPABILITY_SOURCE=false
D1_AUTHORIZES_M07=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
```

## 10. 当前边界

```text
ENGINEERING_CORE=DIGITAL_BIOSPHERE_EVOLUTION_ENGINE
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
MAINLINE_DRIFT_DETECTED=false
CURRENT_CAPABILITY_UNCHANGED=true
NEW_CAPABILITY_CREATED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
C1_COMMIT_AUTHORIZED=false
D1_BASELINE_COMMIT_AUTHORIZED=false
MERGE_EXECUTED=false
PUSH_EXECUTED=false
```

## 11. 下一步

```text
RECOMMENDED_DECISION=APPROVE_D1_BASELINE_COMMIT_CREATION
NEXT_ACTION=HUMAN_DECISION_ON_D1_BASELINE_COMMIT_AUTHORIZATION
```
