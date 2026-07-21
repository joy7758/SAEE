# SAEE C1 智能体证据外部治理依赖独立审查

日期：2026-07-17

## 1. 审查目的

本报告独立复核 C1（第一阶段候选）24 项对象的构造完整性，并判断：一个正式历史基线能否接受当前未显式声明、只能通过临时挂载满足的三项外部治理依赖。

本轮只读审查，不修改候选，不修改代码，不暂存、不提交、不推送、不合并。

```text
CURRENT_STAGE=PHASE_3_C1_BOUND_EXTERNAL_DEPENDENCY_INDEPENDENT_REVIEW
C1_BASELINE_CREATED=false
C1_COMMIT_AUTHORIZED=false
```

## 2. 独立重建结果

隔离候选：

```text
C1_ISOLATED_WORKTREE=/Users/zhangbin/Documents/SAEE-c1-agent-evidence-baseline-isolated-001
C1_PARENT_HASH=f8eb7fd05b3f97b86fb753b3ba05e9b86686558c
C1_PARENT_IS_P1=true
C1_DETACHED_HEAD=true
C1_UNTRACKED_PATH_COUNT=24
C1_TRACKED_CHANGE_COUNT=0
C1_STAGED_PATH_COUNT=0
```

独立计算结果：

```text
C1_SELECTED_SORTED_PATH_SET_SHA256=b7d657de9a7585dc8c805ec057a1740fcc5d489be572a939530e42b9468a15eb
C1_SELECTED_SORTED_MANIFEST_SHA256=061fa332e28dfd12dd68ec2cb45ce225a562d121b9b44a381fb84b5c15a6f853
C1_PATH_SET_MATCH=true
C1_MANIFEST_MATCH=true
C1_D_CLASS_PRESENT_COUNT=0
C1_P1_PUBLIC_SURFACE_CHANGE_COUNT=0
```

公开事实表面复核范围：

- `capability-package/manifest.json`
- `governance/registry/mcp-registry.json`
- `agent-index.json`

以上对象相对 P1（契约父基线第一阶段）没有变化。候选构造精确，未混入三项 D 类对象，也未改变公开能力、公开 MCP（模型上下文协议）或规范能力清单。

## 3. 外部治理依赖诊断

候选内的迁移就绪校验器固定从仓库根目录读取以下对象：

```text
governance/migration/agent-evidence-migration-crosswalk.v1.json
governance/migration/agent-evidence-schema-compatibility.v1.json
governance/migration/saee-three-version-integration-plan.v1.json
```

但是三项对象均被明确排除在 24 项 C1 候选之外。当前命令行只提供 `--source-root` 和 `--offline`，没有显式治理依赖根目录参数。

候选内相关冻结对象：

```text
scripts/saee_agent_evidence_merge_readiness_check.py
SHA256=69fac456a1e70c902864180835455eee7c037a5b9ed335cc9d1727fce968bad3

tests/test_agent_evidence_merge_readiness.py
SHA256=39b873133b71de4a8f8b43ff87540abc9960a0d779cb02c67d56e4184eefebf6
```

直接从 24 项候选运行离线校验的结果：

```text
DIRECT_CANDIDATE_MERGE_READINESS_PASS=false
DIRECT_CANDIDATE_EXIT_CODE=1
DIRECT_FAILURE_REASON=MISSING_EXCLUDED_D_CLASS_GOVERNANCE_DEPENDENCIES
```

对应单元测试也在集合初始化和子进程校验中读取同一仓库根目录，因此正式检出该候选后，不能仅凭候选内容复现已经声明的完整验证结果。

此前临时挂载三项散列绑定只读对象后取得的 13/13 和 63/63 通过结果是真实的条件性验证证据，但它证明的是：

> 候选在特定外部治理输入存在时可通过验证。

它不证明：

> 候选自身已经携带清晰、稳定、可复现的外部依赖契约。

## 4. 三种方案比较

### 方案一：直接接受当前 24 项候选

优点：

- 不改变冻结路径和散列；
- 不纳入 D 类对象；
- 已有条件性验证通过证据。

阻塞：

- 外部依赖挂载方法只记录在主工作区未跟踪构造报告中，不属于候选；
- 候选内校验器没有显式依赖注入入口；
- 直接检出后的校验失败，容易把条件性通过误读为自包含通过。

结论：不适合作为当前正式基线提交方案。

### 方案二：显式注入外部治理依赖根目录

建议另行精确授权，只调整以下两个冻结对象：

```text
scripts/saee_agent_evidence_merge_readiness_check.py
tests/test_agent_evidence_merge_readiness.py
```

最小目标：

1. 为校验器增加显式、失败关闭的外部治理根目录输入；
2. 继续把候选自身根目录用于来源冻结和所有候选内对象；
3. 对三项外部对象进行精确路径与散列绑定；
4. 让测试同时验证：依赖存在时通过、缺失时明确失败、散列不匹配时明确失败；
5. 保持现有判断算法、字段语义、公开 MCP（模型上下文协议）和公开 Schema（数据结构规范）不变。

优点：依赖从隐藏前提变成智能体可读、机器可验证的正式契约，不需要把三项 D 类对象纳入 C1。

代价：两个冻结对象的散列会改变，必须重新授权、重新构造并重新审查候选。

结论：推荐。

### 方案三：把三项 D 类对象纳入候选

该方案会把路径数量从 24 项扩大，并固化仍含活动 M-07 字段的治理对象，包括：

```text
design M-07 SAEE Governance customer contract without copying source text or integrating external runtime
design the M-07 SAEE Governance customer contract while preserving separate integrity, adequacy, authenticity and authorization claims
design_M-07_governance_customer_contract_under_recommendation_gate
```

这会违反已冻结范围，并可能把未来工作建议带入正式基线。结论：拒绝。

## 5. 独立结论

```text
INDEPENDENT_REVIEW_VERDICT=C1_CANDIDATE_REQUIRES_ADJUSTMENT
C1_CONSTRUCTION_EXACTNESS=PASS
C1_BOUND_DEPENDENCY_EVIDENCE=VALID_CONDITIONAL_EVIDENCE
C1_FORMAL_BASELINE_READINESS=NOT_READY
RECOMMENDED_OPTION=EXPLICIT_EXTERNAL_GOVERNANCE_ROOT_INJECTION
```

候选不是功能失败，也没有发生主线漂移。需要调整的是验证契约：三项外部治理输入必须从临时挂载惯例升级为显式、失败关闭、散列绑定的依赖接口。

当前阶段没有授权修改两个冻结对象，因此本报告不执行调整，也不批准提交。

## 6. 精确后续授权建议

若人工决定继续，应只授权：

```text
ALLOW_ONLY:
- scripts/saee_agent_evidence_merge_readiness_check.py
- tests/test_agent_evidence_merge_readiness.py

CHANGE_TYPE:
- explicit external governance dependency injection
- exact path and hash binding
- fail-closed validation
- corresponding tests
```

继续禁止：

- 将三项 D 类对象加入候选；
- 修改判断算法；
- 修改字段语义；
- 修改公开能力、公开 MCP（模型上下文协议）或公开 Schema（数据结构规范）；
- 创建新能力或新协议；
- 开启 Goal Integrity（目标完整性）、State Integrity（状态完整性）或 Trust Continuity（可信连续性）工程；
- 暂存、提交、推送或合并。

调整后必须从 P1 重新构造 24 项候选，重新冻结两个变化对象的散列，并重新执行全部专项、完整和治理验证。

## 7. 不声明事项

本报告不声明：

- C1 已经建立或获得提交授权；
- 三项 D 类对象属于 C1；
- M-07 已获得授权；
- Agent Evidence（智能体证据）已经完成运行时集成；
- 新能力、公开 MCP（模型上下文协议）或公开 Schema（数据结构规范）已经产生；
- Trust Continuity（可信连续性）已经实现。

## 8. 最终状态

```text
C1_INDEPENDENT_REVIEW_STATUS=COMPLETE
INDEPENDENT_REVIEW_VERDICT=C1_CANDIDATE_REQUIRES_ADJUSTMENT
C1_CANDIDATE_PATH_COUNT=24
C1_CANDIDATE_PATH_SET_MATCH=true
C1_CANDIDATE_MANIFEST_MATCH=true
C1_CANDIDATE_SELF_CONTAINED=false
C1_BASELINE_CREATED=false
C1_COMMIT_AUTHORIZED=false
C1_ADJUSTMENT_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CURRENT_CAPABILITY_UNCHANGED=true
NEW_CAPABILITY_CREATED=false
PUBLIC_MCP_CHANGED=false
PUBLIC_SCHEMA_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
GIT_MERGE_EXECUTED=false
MAINLINE_DRIFT_DETECTED=false
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
STATE_INTEGRITY_SECONDARY_LANE=STOPPED
TRUST_CONTINUITY_IMPLEMENTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_C1_EXPLICIT_GOVERNANCE_DEPENDENCY_INJECTION
```
