# SAEE Capability Contract Alignment（SAEE 能力契约收敛）实施前人工审查

## 1. 审查结论

```text
CAPABILITY_CONTRACT_ALIGNMENT_HUMAN_REVIEW_STATUS=COMPLETE
REVIEW_VERDICT=READY_FOR_HUMAN_DECISION_WITH_CONDITIONS
IMPLEMENTATION_READINESS=CONDITIONAL_NOT_READY_TO_EXECUTE
IMPLEMENTATION_AUTHORIZED=false
```

中文结论：最小重命名方案在方法上可接受，可以提交人工决定；但当前不能实施。

未实施的原因不是方案本身错误，而是以下授权和执行条件尚未同时满足：

1. 当前 `Phase 1 Capability Alignment`（第一阶段能力对齐）仍未获授权；
2. 当前工作区存在大量既有修改，不能把契约改名直接混入现有工作区；
3. 旧内部名称的活动调用方仍是 `usage_evidence=UNKNOWN`（使用证据未知）；
4. 公开契约冻结摘要、实施文件白名单和历史证据排除清单尚未绑定到一次性人工授权；
5. 尚未记录独立回滚点和失败证据保存位置。

本审查不授予实施权。只有人类对本报告第 7 节的精确条件作出明确确认后，才可以准备一次新的受控实施授权。

## 2. 审查边界

本次只审查：

1. 重命名边界；
2. 风险；
3. 回滚方式；
4. 历史证据保护方式；
5. 实施授权条件。

本次没有：

- 修改代码；
- 修改接口；
- 修改 Schema（数据结构规范）；
- 修改 MCP（模型上下文协议）；
- 修改公开能力；
- 创建新能力；
- 执行重命名；
- 重新开启 Goal Integrity（目标完整性）副线。

## 3. 重命名边界审查

### 3.1 允许提交人工决定的最小变化

```text
CURRENT_INTERNAL_OPERATION=evaluate_agent_run
TARGET_INTERNAL_OPERATION=evaluate_rehearsal_run
TARGET_INTERNAL_CAPABILITY_ID=internal.saee.evaluate_rehearsal_run
TARGET_INTERNAL_HTTP_PATH=/capabilities/evaluate-rehearsal-run
```

中文含义：只把现有内部排演运行评估的机器身份改成明确的排演语义名称。

允许未来授权覆盖的变化只有：

- 内部能力包中的操作名；
- 内部 MCP（模型上下文协议）工具名；
- 内部 HTTP（超文本传输协议）路径和操作标识；
- 现有内部 Schema（数据结构规范）中的固定名称、固定能力标识和引用路径；
- 内部运行时路由、调用收据和适配器中的操作常量；
- 当前内部测试、当前机器投影和当前内部文档中的对应名称。

这些变化必须复用 `saee_backend/services/agent_run_capability.py` 中的现有内部评估逻辑。

### 3.2 永久排除的公开能力

以下公开契约必须保持不变：

```text
PUBLIC_OPERATION=saee.evaluate_agent_run
PUBLIC_ALIAS=evaluate_agent_run
PUBLIC_IMPLEMENTATION=saee_backend/services/baidu_agent_readiness_service.py
PUBLIC_ENTRYPOINT=scripts/saee_agent_readiness_mcp_stdio.py
```

不得改变：

- `saee.evaluate_agent_run`（智能体运行评估）的名称；
- 公开请求字段、证据类型、响应字段和推荐值；
- 公开规范实现；
- 千帆兼容路由；
- `.mcp.json` 中的公开规范入口；
- `.well-known/saee-capability-index.json` 中的公开发现事实；
- 公开能力清单中该能力的实现状态、生命周期和公开角色。

无命名空间别名 `evaluate_agent_run`（智能体运行评估）只保留给公开规范能力，内部活动工具不得继续占用。

### 3.3 不属于必要改名的内容

- 模块作用域内部函数 `saee_backend/services/agent_run_capability.py#evaluate_agent_run`；
- 内部评估算法；
- 排演运行输入事实；
- 固定证据充分性剖面；
- 原因码、限制和非授权边界；
- 公开能力的任何行为。

如果实施过程中必须修改上述内容，应立即停止；那已经不是最小重命名。

## 4. 风险审查

| 风险 | 后果 | 控制条件 | 当前状态 |
|---|---|---|---|
| 误改公开规范入口 | 外部智能体提交错误请求或误解响应 | 公开文件摘要冻结；公开校验前后完全一致 | 未绑定 |
| 半迁移 | 文档、工具列表和运行时出现新旧名称混用 | 单一文件白名单内同步完成；不分散实施 | 未绑定 |
| 旧调用方中断 | 内部调用失败 | 实施前完成活动调用方检索和使用证据记录 | 未完成 |
| 兼容别名继续制造双语义 | 契约表面仍不稳定 | 旧内部名称不得出现在活动工具发现列表 | 已在方案中定义，未实施 |
| 历史证据被重写 | 过去结果失去可审计性 | 禁止全局替换；历史目录加入排除清单 | 未绑定 |
| 规范清单内部区误改公开区 | 公开能力事实发生非授权变化 | 对 `canonical_inventory`（规范能力清单）公开区建立前后摘要比较 | 未绑定 |
| 现有脏工作区归因混乱 | 无法证明哪些变化属于改名 | 只在独立、干净、可回滚的工作区实施 | 未满足 |
| 改名演变成新能力 | 重复建设并扩大范围 | 禁止新增能力清单项、评估器和第三套契约 | 已冻结，未授权 |
| 副线重新扩张 | 契约收敛被 Goal Integrity（目标完整性）替代 | 保持副线停止；实施只服务证据与评估主线 | 已冻结 |

当前综合风险判断：

```text
RISK_LEVEL=MEDIUM_UNTIL_BINDINGS_COMPLETE
PUBLIC_CONTRACT_RISK_TOLERANCE=ZERO
HISTORICAL_REWRITE_TOLERANCE=ZERO
```

中文含义：在授权绑定完成前风险为中等；公开契约变化和历史证据重写的容忍度均为零。

## 5. 回滚方式审查

### 5.1 回滚前提

未来实施不得直接使用当前混合修改工作区。实施前必须建立：

1. 干净、隔离的工作区；
2. 可验证的基线 `commit`（提交）标识；
3. 精确文件白名单；
4. 白名单文件实施前摘要清单；
5. 公开契约文件单独摘要清单；
6. 失败证据保存位置。

### 5.2 回滚触发条件

出现以下任一情况立即停止并回滚本次专用改名补丁：

- 公开能力名称、请求、响应或行为发生变化；
- 任一活动内部发现面仍把旧名解释为排演语义；
- 任一校验失败且原因不能限定为已知的历史快照；
- 发现未登记的活动调用方；
- 需要修改评估算法或增加字段；
- 需要修改白名单之外的文件；
- 出现主线漂移或副线扩张。

### 5.3 回滚动作

1. 停止继续修改，不自动重试；
2. 保存失败时的差异、校验输出和文件摘要；
3. 只撤销本次独立改名补丁，不触碰用户原有修改；
4. 恢复到实施前基线；
5. 重新运行公开能力和治理校验；
6. 输出失败报告，等待新的人工作出决定。

禁止使用会破坏用户修改的 `git reset --hard`（Git 强制重置）或无范围恢复命令。

```text
AUTOMATIC_RETRY_ALLOWED=false
DESTRUCTIVE_ROLLBACK_ALLOWED=false
FAILED_ATTEMPT_EVIDENCE_PRESERVED=true
```

## 6. 历史证据保护方式

### 6.1 默认不可修改范围

以下目录和材料默认视为历史证据或冻结投影：

- `reports/**`（报告目录），本次新增的审查链文件除外；
- `release/**`（发布快照目录）；
- `phase_b_product/**`（第二阶段产品快照目录）；
- 已封存的实验收据、执行结果和试验观察；
- 旧云入口交付包和旧生态候选包，除非另有明确当前投影授权；
- 既有 `commit`（提交）历史。

### 6.2 保护规则

1. 禁止仓库范围全局替换；
2. 只允许修改人工授权白名单中的当前活动文件；
3. 历史文件保留旧名称，因为旧名称是当时真实状态；
4. 当前索引如需解释历史名称，只能增加指向新名称的说明，不能改写旧证据正文；
5. 文件移动或重命名必须保留来源关系和替代关系；
6. 实施后重新检索全部命中，并把每个剩余旧名称分类为公开别名、内部模块函数或历史证据；
7. 无法分类的剩余命中视为阻塞，不得宣布契约一致。

```text
GLOBAL_SEARCH_REPLACE_ALLOWED=false
HISTORICAL_REPORT_REWRITE_ALLOWED=false
RELEASE_SNAPSHOT_REWRITE_ALLOWED=false
WRITE_ONCE_EVIDENCE_PRESERVED=true
```

## 7. 实施授权条件

### 7.1 技术条件

人工授权前必须全部满足：

- [ ] `Phase 1 Capability Alignment`（第一阶段能力对齐）实施边界获得独立确认；
- [ ] 活动调用方盘点完成，旧内部名称的使用证据不再是未知；
- [ ] 公开契约文件摘要已冻结；
- [ ] 实施文件白名单已冻结；
- [ ] 历史证据排除清单已冻结；
- [ ] 独立干净工作区与基线提交已绑定；
- [ ] 回滚点和失败证据位置已绑定；
- [ ] 不新增能力、不改算法、不增加字段的边界再次确认；
- [ ] 公开、内部、兼容、治理和主线校验命令已冻结；
- [ ] Goal Integrity（目标完整性）副线继续停止。

### 7.2 人工授权记录必须明确包含

```text
APPROVE_CAPABILITY_CONTRACT_MINIMAL_RENAME=true
AUTHORIZATION_ID=<human-supplied-id>
HUMAN_AUTHORITY_OWNER_ID=<human-supplied-owner-id>
KEEP_PUBLIC_CAPABILITY_UNCHANGED=true
RESERVE_UNQUALIFIED_ALIAS_FOR_PUBLIC_CAPABILITY=true
ALLOW_INTERNAL_OPERATION_RENAME=true
ALLOW_EXISTING_INTERNAL_SCHEMA_IDENTIFIER_RENAME=true
ALLOW_INTERNAL_MCP_TOOL_RENAME=true
ALLOW_INTERNAL_HTTP_ROUTE_RENAME=true
REUSE_EXISTING_INTERNAL_EVALUATOR=true
NEW_CAPABILITY_NOT_AUTHORIZED=true
PUBLIC_CONTRACT_CHANGE_NOT_AUTHORIZED=true
HISTORICAL_EVIDENCE_REWRITE_NOT_AUTHORIZED=true
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
GIT_COMMIT_NOT_AUTHORIZED=true
GIT_PUSH_NOT_AUTHORIZED=true
```

其中带尖括号的标识必须由人类填写，不能由智能体代填。

该授权只能消费一次。实施完成或首次失败后自动失效；重试需要新的人工授权。

### 7.3 当前决定

本报告没有收到上述授权记录，因此：

```text
HUMAN_AUTHORIZATION_RECORDED=false
IMPLEMENTATION_AUTHORIZED=false
```

## 8. 指挥官命令核查与跑偏教训

```text
MAINLINE_DRIFT_DETECTED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

本次命令服务 SAEE Evidence（SAEE 证据）与 SAEE Evaluation（SAEE 评估）主线，没有把治理、测试或
Goal Integrity（目标完整性）副线提升为项目主线。

前几次跑偏的教训继续作为人工审查约束：

1. 计划完成不等于实施授权；
2. 局部名称修复不能扩展成新能力或新架构；
3. 严谨性要求不能演变成新的治理系统；
4. 不能为了名称整洁而改写历史事实；
5. 不能在使用证据未知时假设没有调用方；
6. 不能在混合修改工作区中制造无法归因的实施结果；
7. 当前评估主线必须优先于状态完整性研究副线。

## 9. 非主张

本审查不表示：

- 人工已经批准实施；
- 重命名已经开始；
- 代码、接口、数据结构规范或公开能力已经变化；
- 契约已经达到 `CONTRACT_ALIGNED`（契约一致）；
- 外部开发者验证、客户验证、产品发布或生产就绪已经成立。

## 10. 最终状态

```text
CAPABILITY_CONTRACT_ALIGNMENT_HUMAN_REVIEW_STATUS=COMPLETE
REVIEW_VERDICT=READY_FOR_HUMAN_DECISION_WITH_CONDITIONS
MINIMAL_RENAME_BOUNDARY_ACCEPTABLE=true
RISK_REVIEW_COMPLETE=true
ROLLBACK_REVIEW_COMPLETE=true
HISTORICAL_EVIDENCE_PROTECTION_REVIEW_COMPLETE=true
AUTHORIZATION_CONDITIONS_DEFINED=true
HUMAN_AUTHORIZATION_RECORDED=false
IMPLEMENTATION_AUTHORIZED=false
CODE_CHANGED=false
INTERFACE_CHANGED=false
SCHEMA_CREATED=false
SCHEMA_CHANGED=false
MCP_CHANGED=false
PUBLIC_CAPABILITY_CHANGED=false
NEW_CAPABILITY_CREATED=false
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_DECISION_ON_CAPABILITY_CONTRACT_MINIMAL_RENAME
```
