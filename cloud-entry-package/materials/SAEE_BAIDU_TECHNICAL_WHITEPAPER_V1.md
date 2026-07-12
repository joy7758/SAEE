# SAEE Agent Readiness Platform

## 百度智能云生态技术白皮书 v1.0

SAEE 智能体上线准备平台

面向百度千帆 Agent 工作流的本地技术评审版

- 文档状态：`local_review_alpha`
- 公共操作：`saee.evaluate_agent_run`、`saee.evaluate_evidence`
- 官方千帆集成：`false`
- 百度生态申请：`false`
- 生产就绪：`false`

<!-- PAGE_BREAK -->

## 1. 企业 Agent 上线前的可靠性缺口

企业已经能够用大模型和工具快速构建 Agent，但“能够完成一次任务”并不等于“具备进入真实业务的证据”。退款、发布、权限变更和外部 API 调用均可能把局部错误放大成业务后果。

- 单次成功不能证明长期稳定、恢复能力或权限边界。
- Trace 记录了发生什么，但不能自动证明证据是否充分。
- 工具可用性不等于调用权限或部署批准。
- 缺少回滚、审批和权限证据时，Agent 不应被默认为可上线。

SAEE 的第一产品不控制 Agent，也不替代百度安全、身份或执行系统。它在独立授权之前提供结构化的上线准备上下文。

<!-- PAGE_BREAK -->

## 2. 产品定位与两个公共契约

对外品牌统一为 `SAEE Agent Readiness Platform / SAEE 智能体上线准备平台`。首个可购买形态是 `SAEE Agent Readiness Assessment / SAEE 智能体上线可靠性评估服务`。

公共产品面严格只有两个只读操作：

1. `saee.evaluate_agent_run`：评估一次声明的 Agent 运行、必需证据覆盖和风险信号。
2. `saee.evaluate_evidence`：针对明确的必需证据集合，计算覆盖、缺口和原因码。

`rehearse_agent`、`describe_saee` 与 `compare_observed_traces` 保留为内部工程或调试资产，不进入百度产品工具列表。MCP 是分发适配器，不是产品本身。

<!-- PAGE_BREAK -->

## 3. Evidence Coverage 方法

当前 Alpha 使用四类可发现、可解释的上线准备证据：

- `TEST_RESULT`：受控测试或验证结果；
- `ROLLBACK_PLAN`：恢复或回滚计划；
- `PERMISSION_BOUNDARY`：工具、资源和外部 API 权限边界；
- `HUMAN_APPROVAL`：高影响动作前的人工审批节点。

高影响或外部效果运行要求四类证据全部声明。分数是“已具备的必需证据类型 / 必需证据类型总数”的百分比。它不是可靠概率、安全概率、认证结论或上线批准。

输出同时保留 `missing_evidence`、`risks`、`recommendation` 与 truth boundary，便于调用 Agent 正确解释并拒绝越界推论。

<!-- PAGE_BREAK -->

## 4. 百度版产品架构

[[IMAGE:architecture.png]]

目标组合架构从 BOS 脱敏对象引用开始，经百度千帆与 Agent 应用进入 SAEE Connector；Connector 只转发两个只读评估操作。Evaluation Engine 检查声明的 Trace 元数据和证据覆盖，Evidence Analysis 生成缺口与原因，最后形成有边界报告。当前 Alpha 没有访问 BOS，图中的 BOS 是目标组合层而不是已完成集成。

Human Authorization 是独立虚线门：任何部署、退款、支付、权限扩大、合同或市场提交都不由 SAEE 结果自动触发。

<!-- PAGE_BREAK -->

## 5. Qianfan Function Calling 与 MCP 适配

产品 MCP 名称使用稳定的点号命名：

- `saee.evaluate_agent_run`
- `saee.evaluate_evidence`

考虑厂商 function name 约束，Qianfan host 使用下划线别名，并通过显式 crosswalk 映射：

- `saee_evaluate_agent_run` → `saee.evaluate_agent_run`
- `saee_evaluate_evidence` → `saee.evaluate_evidence`

宿主只接受 checked-in 合成 fixture；模型不能提供路径、URL、命令、代码、密钥或客户记录。Provider key 只从进程环境读取，并从 MCP 子进程环境移除。

当前已完成本地 fake-provider function-calling roundtrip；真实产品 roundtrip 仍为 `false`，因为安全凭据文件尚未配置 Qianfan key。

<!-- PAGE_BREAK -->

## 6. 两个百度易理解 Demo

[[IMAGE:screenshots/customer-service-result.png]]

### 智能客服退款 Agent

测试、回滚和权限证据存在，但缺少人工审批。结果为 `readiness=conditional`、`score=75`、`HUMAN_REVIEW_REQUIRED`。退款或支付不会执行。

### 代码发布 Agent

测试与权限证据存在，但缺少回滚计划和人工审批。结果为 `readiness=replan`、`score=50`、`REPLAN`。代码部署不会执行。

两个 Demo 都是本地合成输入，不是客户案例、真实 Agent 验证或百度官方兼容证明。

<!-- PAGE_BREAK -->

## 7. 数据、同意与非授权边界

Cloud Entry Package 默认失败关闭：

- `customer_data_included` 必须为 `false`；
- 不接收凭据、个人记录、支付记录或未批准生产日志；
- `source_ref` 只作为声明，不由本地 Alpha 抓取；
- Trace 与 Evidence 的真实性没有被独立验证；
- 所有响应固定保留 `deployment_authorized=false`；
- 安全、合规、法律与生产认证均不在输出范围内。

任何真实 provider 凭据使用、云上传、伙伴联系、公开发布、价格发布和 Marketplace 提交，都需要单独的人类授权记录。

<!-- PAGE_BREAK -->

## 8. 当前工程与运营成熟度

已完成：

- 冻结外部产品身份和两个公共操作；
- 两工具本地 stdio MCP 与 CLI；
- Qianfan function alias crosswalk；
- 客服、编码和证据包三个版本化 Demo；
- 30 分钟 Cloud Entry Package 验收；
- 本地产品页和 Agent-readable 页面构建测试。

仍缺失：远程 MCP、公共 HTTP endpoint、生产认证与租户隔离、隐私/法律批准、正式安全评审、运营告警与 SLA、客户验证、官方千帆集成和百度市场上架。

因此当前阶段是 `local_review_alpha`，不是生产服务。

<!-- PAGE_BREAK -->

## 9. 百度生态进入路线与合作边界

推荐顺序：技术资产 → 百度可运行本地 Demo → 受控生态合作验证 → 联合方案包装 → 云市场商品。不要直接把当前 Alpha 申报为 Marketplace 商品。

第一阶段交付是 Agent Readiness Assessment，而不是泛化治理平台或通用 Agent 基础设施。商业建议价格仍只是待 owner 审核的内部假设，不是公开报价。

下一项外部动作必须经过显式授权：

1. 配置并运行一次合成 Qianfan 产品 roundtrip；
2. 人工审阅白皮书、产品页、Demo 视频与 Git Release 范围；
3. 决定是否公开 Release、联系百度生态或提交合作申请；
4. 在法律、运营、定价与客户验证完成前保持 `production_ready=false`。

SAEE 的工程核心继续是 Digital Biosphere Evolution Engine；本产品投影强化演化闭环的感知、性状提取、适应度评估与回滚免疫，而不是 audit-first 重构。
