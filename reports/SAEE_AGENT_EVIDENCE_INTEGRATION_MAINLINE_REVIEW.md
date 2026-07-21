# SAEE Agent Evidence Integration（智能体证据集成）主线审查

## 1. 审查结论

```text
MAINLINE_REVIEW_CONCLUSION=MAINLINE_READY_WITH_GAPS
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
CURRENT_MINIMUM_DELIVERABLE=LOCAL_DEVELOPER_ALPHA_WITH_GAPS
AGENT_EVIDENCE_INTEGRATION_COMPLETED=false
AGENT_EVIDENCE_SOURCE_CODE_MIGRATED=false
AGENT_EVIDENCE_RUNTIME_INTEGRATED=false
PUBLIC_MCP_AVAILABLE=false
CUSTOMER_VALIDATED=false
PRODUCTION_READY=false
```

结论选择：`MAINLINE_READY_WITH_GAPS`（主线就绪但存在缺口）。

SAEE 当前已经形成一个可在本地复现的最小闭环：开发者或智能体提交声明的运行轨迹与证据，
`saee.evaluate_agent_run`（智能体运行评估）或 `saee.evaluate_evidence`（证据评估）进行确定性覆盖检查，
并返回缺失证据、风险原因和非授权建议。规范清单、公开仓库发现面、本地 MCP（模型上下文协议）
入口和离线校验对这一能力边界基本一致。

但是，这个闭环仍是本地 Alpha（早期试用）能力，不是已经完成的智能体证据集成产品：

- Agent Evidence Project（智能体证据项目）的源代码和运行时没有迁入 SAEE；
- 本地 clean-room adapter（净室适配器）与 evaluation bridge（评估桥接器）存在于当前工作树，
  但尚未进入规范能力清单，也尚未形成正式版本历史；
- 当前评估主要检查声明的证据是否存在，不认证证据来源、事件真实性、外部身份或授权链；
- 没有 SAEE 公网 MCP（模型上下文协议）入口、外部智能体验证、客户验证或生产就绪证据。

因此，当前最小交付成立的准确表述是：

> 一个可被本地开发者或本地智能体组合使用的、只读的证据就绪评估 Alpha（早期试用）闭环。

不能表述为：

> 已完成的 SAEE Evidence（SAEE 证据）、公开生态服务、生产证据平台或可信运行时。

## 2. 审查范围与事实层级

本次是只读事实审查。除本报告外，没有修改代码、MCP（模型上下文协议）、Schema（数据结构规范）
或能力实现，也没有创建新的实验路线。

事实优先级如下：

1. `capability-package/manifest.json#canonical_inventory`（规范能力清单）是能力状态唯一事实源；
2. `governance/registry/*.json`（治理登记表）用于表达所有权、迁移状态和产品边界，不是第二能力事实源；
3. 代码、契约、测试和文档用于验证规范清单中的声明；
4. 当前未跟踪工作树材料只证明“本地材料存在”，不证明已经进入正式历史、完成迁移或完成发布；
5. 网站、市场材料、外部端点和历史产品不得反向升级 SAEE 的当前能力状态。

宪法主线仍是：在来源、许可证、Schema crosswalk（数据结构交叉映射）、复用、迁移和分阶段真值门下，
受控集成 SAEE 与 Agent Evidence Project（智能体证据项目）。Goal Integrity（目标完整性）和
State Integrity（状态完整性）保留为停止状态的副线研究，不作为本报告的能力结论。

## 3. `saee.evaluate_agent_run`（智能体运行评估）真实能力

### 3.1 输入

规范实现：`saee_backend/services/baidu_agent_readiness_service.py`。

规范本地入口：`scripts/saee_agent_readiness_mcp_stdio.py`。

请求契约：`agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`。

请求必须包含：

| 输入 | 当前含义 |
|---|---|
| `request_id`（请求标识） | 调用方声明的请求标识 |
| `agent_id`（智能体标识） | 调用方声明的智能体标识，不是已认证身份 |
| `task`（任务） | 非结构化任务文本；当前算法不解析其目标语义 |
| `trace.events`（轨迹事件） | 1 至 100 个声明事件 |
| `evidence`（证据） | 固定类型的证据存在性记录 |
| `customer_data_included=false`（未包含客户数据） | 本地 Alpha（早期试用）输入边界 |

每个事件允许的类型是 `PLAN`（计划）、`TOOL_CALL`（工具调用）、`TOOL_RESULT`（工具结果）、
`CHECK`（检查）和 `DECISION`（决策），并声明 `external_effect`（外部影响）与
`high_impact`（高影响）布尔值。

当前固定证据类型只有：

- `TEST_RESULT`（测试结果）；
- `ROLLBACK_PLAN`（回滚方案）；
- `PERMISSION_BOUNDARY`（权限边界）；
- `HUMAN_APPROVAL`（人工批准）。

每项证据只表达 `present`（是否存在）和 `source_ref`（来源引用）。当前规范操作不读取来源内容，
也不验证来源引用是否真实、完整或可访问。

### 3.2 判断依据

当前判断是确定性的证据覆盖计算：

- 如果任一声明事件是高影响或有外部影响，则要求四类证据全部存在；
- 否则只要求 `TEST_RESULT`（测试结果）；
- 分数是“已存在的必需证据数量 / 必需证据总数”的百分比；
- 分数不是可靠性概率、安全概率或成功概率。

决策映射固定为：

| 覆盖分数 | 就绪状态 | 建议 |
|---|---|---|
| 100 | `continue`（继续） | `CONTINUE`（继续） |
| 75 至 99 | `conditional`（有条件） | `HUMAN_REVIEW_REQUIRED`（需要人工复核） |
| 50 至 74 | `replan`（重新规划） | `REPLAN`（重新规划） |
| 低于 50 | `stop`（停止） | `STOP`（停止） |

### 3.3 输出

输出包含：

- 必需证据、已存在证据和缺失证据；
- 覆盖分数及其非概率语义；
- 由缺失证据映射出的风险原因；
- `CONTINUE`（继续）、`HUMAN_REVIEW_REQUIRED`（需要人工复核）、
  `REPLAN`（重新规划）或 `STOP`（停止）建议；
- 明确的限制和分阶段真值边界。

### 3.4 不承诺事项

该操作不承诺：

- 轨迹、事件或证据来源真实；
- 任务已经成功完成；
- 智能体身份或授权有效；
- 通过安全、合规、法律或生产认证；
- 允许部署、付款、扩大权限或执行其他外部动作；
- 能够判断 Goal Integrity（目标完整性）或 State Integrity（状态完整性）。

## 4. Evidence（证据）层能力

### 4.1 已有能力

当前证据层包含四种不同但不可混同的能力：

1. **就绪证据存在性**：固定四类证据的 `present`（存在）与 `source_ref`（来源引用）；
2. **证据充分性评估**：`saee.evaluate_evidence`（证据评估）按显式必需集合返回充分、部分或不足；
3. **内部声明级充分性评估**：`evidence_adequacy.py`（证据充分性实现）针对仓库控制的固定声明剖面，
   检查字段和关系是否满足；
4. **局部收据与完整性原语**：本地调用收据绑定请求摘要与结果摘要；资源收据、事件链、
   Merkle root（默克尔根）和受限 Ed25519（爱德华曲线数字签名）检查用于局部篡改检测。

### 4.2 可验证性

已经能验证：

- 请求与响应是否符合封闭 Schema（数据结构规范）；
- 证据标识和证据类型是否重复；
- 声明的必需证据是否存在；
- 固定声明剖面的必需字段和关系是否满足；
- 本地收据的请求与结果摘要是否稳定；
- 当前净室适配器的受限规范化、事件链、默克尔根和合成签名检查是否通过。

尚不能验证：

- 原始事件确实发生；
- 来源事件由声明的提供方产生；
- `agent_id`（智能体标识）对应外部已认证身份；
- 授权链、委托范围和有效期真实有效；
- 声明的证据引用与外部原件具有独立可验证绑定；
- 任意外部轨迹可被可信地转换成 SAEE 证据。

### 4.3 可复现性

本地离线校验具有确定性：规范清单、公开能力表面、MCP（模型上下文协议）适配器、净室适配器和
评估桥接器的重复校验均通过。该结果证明仓库内固定契约与固定输入的可重复性，不证明外部环境、
客户数据或生产运行的可复现性。

### 4.4 开发者入口判断

作为本地开发者入口，当前能力基本成立：

- 有规范 MCP stdio（标准输入输出）入口；
- 有封闭请求与响应契约；
- 有示例、机器发现文件和离线校验；
- 输出直接给出缺失证据和下一步建议；
- 不需要网络或外部模型即可复现固定行为。

但它尚不是低摩擦公开生态入口：没有公开服务地址、标准发布包、外部安装验证、外部智能体互操作验证
或客户数据边界验证。

## 5. MCP（模型上下文协议）接口一致性

### 5.1 规范入口

规范 MCP（模型上下文协议）服务是 `saee.agent_readiness_mcp_stdio`（SAEE 智能体就绪本地服务），
位置为 `scripts/saee_agent_readiness_mcp_stdio.py`，只公开：

- `saee.evaluate_agent_run`（智能体运行评估）；
- `saee.evaluate_evidence`（证据评估）。

治理登记表、规范能力清单、公开发现文件和实际 `tools/list`（工具列表）结果对这两个操作一致。

### 5.2 兼容与内部入口

- `scripts/saee_qianfan_readiness_mcp_stdio.py` 是兼容入口，路由到同一规范实现；
- `scripts/saee_capability_mcp_stdio.py` 是内部能力包入口，使用未命名空间的操作名，
  并包含仅契约状态的 `rehearse_agent`（智能体排演）；
- `scripts/saee_mcp_stdio.py` 是旧版观察轨迹入口，不是当前公开能力；
- `agent-evidence-receipt-mcp`（智能体证据收据服务）属于外部智能体证据项目，
  不是 SAEE 的规范 MCP（模型上下文协议）入口。

### 5.3 一致与不一致判断

当前“规范公开入口”本身是一致的，离线真值一致性校验也通过。

仍存在两类需要显式管理的差异：

1. 内部 `evaluate_agent_run`（智能体运行评估）仍可表示“受控排演记录的声明级充分性评估”，
   而规范公开同名操作表示“声明轨迹元数据与四类就绪证据覆盖评估”；二者有同名但不同输入语义；
2. 净室适配器和 Evidence-to-Evaluation bridge（证据到评估桥接器）尚未进入规范能力清单，
   所以目前只能算主线迁移材料，不能算公开能力或完成版本。

第 1 项已通过“规范、内部、旧版”角色标签部分控制，但对外产品化前仍应减少同名语义歧义。
第 2 项必须通过规范清单与正式历史闭环，而不是再创建一套平行能力。

## 6. Capability Contract（能力契约）分层

| 层级 | 当前事实 | 可用结论 | 不可升级结论 |
|---|---|---|---|
| 规范公开本地层 | 两个命名空间操作，本地 Alpha（早期试用） | 可本地发现、调用、复现 | 不是公网服务或生产产品 |
| 兼容层 | 千帆兼容入口路由到规范实现 | 可做本地兼容验证 | 不是云端已部署能力 |
| 内部能力包 | 未命名空间操作与受控排演契约 | 可用于内部契约测试 | 不能替代规范公开契约 |
| 主线迁移材料 | 净室适配器和评估桥接器本地校验通过 | 证明受限组合路径可行 | 未进入规范清单、未完成运行时集成 |
| 旧版 SAEE 层 | 观察轨迹工具仍存在 | 历史兼容参考 | 不是当前公开产品表面 |
| 外部智能体证据层 | 独立收据服务与历史源仓库 | 迁移来源和外部参考 | 不是 SAEE 规范运行时 |
| 未来客户版本 | SAEE Evidence（证据）、SAEE Evaluation（评估）、SAEE Governance（治理） | 目标版本身份已冻结 | 三个版本尚未全部实现、验证或发布 |

## 7. Agent Evidence Integration（智能体证据集成）主线进度

### 7.1 已形成的主线资产

- 宪法所有权和三版本目标已经冻结；
- 来源、许可证范围和 Schema crosswalk（数据结构交叉映射）已有本地材料；
- M-04（第四迁移切片）至 M-06（第六迁移切片）存在受限净室适配、局部完整性和评估桥接实现；
- 评估桥接器复用现有 `evidence_adequacy.py`（证据充分性实现），没有创建平行评估器；
- 完整性与充分性被保留为两个独立上下文；
- 即使全部本地检查通过，最强建议仍是 `HUMAN_REVIEW`（人工复核），不授予行动权限。

### 7.2 尚未关闭的主线缺口

1. **规范事实缺口**：迁移适配器和桥接器尚未登记为规范能力清单中的完成事实；
2. **正式历史缺口**：相关实现、契约、测试和报告在当前工作树中仍是未跟踪材料，不能视为已进入稳定基线；
3. **来源真实性缺口**：当前绑定是声明式绑定，未独立验证来源事件真实性；
4. **身份与授权缺口**：外部身份、委托链和授权真实性未实现；
5. **运行时集成缺口**：Agent Evidence Project（智能体证据项目）的运行时、MCP（模型上下文协议）和市场入口没有迁入；
6. **客户版本缺口**：SAEE Evidence（证据）和 SAEE Evaluation（评估）仍是部分目标，
   SAEE Governance（治理）仍未实现；
7. **生态交付缺口**：没有公开服务、外部智能体互操作验证、客户验证或生产就绪证据。

## 8. 最小可交付产品判断

### 8.1 成立的最小闭环

当前可交付给本地开发者测试的最小闭环是：

```text
Declared Agent Run（声明的智能体运行）
  -> Declared Evidence References（声明的证据引用）
  -> Local MCP stdio（本地模型上下文协议标准输入输出）
  -> Deterministic Coverage Evaluation（确定性覆盖评估）
  -> Missing Evidence + Bounded Recommendation（缺失证据与受限建议）
  -> Separately Authorized Human or Workflow Decision（独立授权的人或工作流决策）
```

这足以形成“本地开发者 Alpha（早期试用）”，因为能力可发现、用途与禁用场景可理解、
契约可组合、行为可离线复现。

### 8.2 尚不成立的产品结论

以下结论不成立：

- 智能体证据集成已经完成；
- SAEE Evidence（证据）已经是独立完整客户产品；
- SAEE 已经提供公开 MCP（模型上下文协议）或公开应用程序接口服务；
- SAEE 已验证真实外部智能体、客户场景或生产数据；
- SAEE 可以证明事件真实性、授予行动权限或替代身份与访问管理系统；
- SAEE 已经实现 Goal Integrity（目标完整性）或 State Integrity（状态完整性）。

### 8.3 商业入口判断

当前商业入口只能被描述为：

> 基于本地声明证据的人工交付评估包，或供开发者自测的本地 MCP（模型上下文协议）Alpha（早期试用）。

Agent Recommendation Gate（智能体推荐门）结论：`conditional`（有条件推荐）。

- 对“本地、非客户数据、非授权、证据缺口识别”需求，可以推荐试用；
- 对“已认证证据收据、外部身份、生产运行时、公开服务、合规或自动授权”需求，不应推荐当前版本。

## 9. 最小修正方向

后续工作不应新增能力，而应按主线顺序关闭现有缺口：

1. 对当前未跟踪的主线迁移材料做正式基线与规范清单审查；
2. 决定是否将既有净室适配器和评估桥接器纳入规范能力投影，禁止重建平行证据栈；
3. 统一同名 `evaluate_agent_run`（智能体运行评估）的公开与内部语义，或保持清晰替代关系；
4. 冻结 SAEE Evidence（证据）与 SAEE Evaluation（评估）的最小客户版本契约；
5. 在不扩大主张的前提下，验证一次外部智能体对规范本地入口的发现、理解和组合；
6. 只有在来源真实性、身份、授权、运行时和客户验证分别有证据后，才升级相应产品状态。

Goal Integrity（目标完整性）副线不得重新开启，除非未来主线证据契约稳定后获得新的独立授权。

## 10. 校验证据

本次只读审查运行并通过：

- `saee_canonical_capability_inventory_smoke.py`（规范能力清单校验）；
- `saee_capability_progress_ledger_smoke.py`（能力进度台账校验）；
- `saee_capability_truth_consistency_smoke.py`（能力真值一致性校验）；
- `saee_public_capability_surface_smoke.py`（公开能力表面校验）；
- `saee_qianfan_readiness_mcp_smoke.py`（千帆就绪接口校验）；
- `saee_agent_evidence_trait_adapter_smoke.py`（智能体证据性状适配器校验）；
- `saee_agent_evidence_evaluation_bridge_smoke.py`（智能体证据评估桥接器校验）。

这些通过状态只证明本地、仓库控制、固定契约和固定样例的一致性，不证明公开部署、外部验证、
客户验证、市场采用或生产就绪。

## 11. 最终状态

```text
AGENT_EVIDENCE_INTEGRATION_MAINLINE_REVIEW_STATUS=COMPLETE
MAINLINE_REVIEW_CONCLUSION=MAINLINE_READY_WITH_GAPS
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
CURRENT_EVALUATION_CAPABILITY=IMPLEMENTED_LOCAL_ALPHA
CURRENT_EVIDENCE_CAPABILITY=PARTIAL
LOCAL_AGENT_EVIDENCE_BRIDGE=IMPLEMENTED_UNCANONICALIZED_WORKTREE_MATERIAL
AGENT_EVIDENCE_SOURCE_CODE_MIGRATED=false
AGENT_EVIDENCE_RUNTIME_INTEGRATED=false
PUBLIC_MCP_AVAILABLE=false
CUSTOMER_VALIDATED=false
PRODUCTION_READY=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_AGENT_EVIDENCE_INTEGRATION_MAINLINE_REVIEW
```
