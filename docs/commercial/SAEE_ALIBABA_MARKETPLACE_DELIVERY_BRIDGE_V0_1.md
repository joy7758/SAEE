# SAEE 阿里云市场评估交付桥 v0.1

## 作用

该桥把“1 个 AI Agent 工作流 + 1 个场景”的规范化材料接入现有
`saee.evaluate_agent_run`，生成以下本地交付候选物：

1. `assessment-bundle.json`：机器可读评估结果；
2. `assessment-report.zh-CN.md`：中文报告；
3. `delivery-receipt.prepared.json`：待人工边界复核的准备凭证；
4. `delivery-receipt.final.json`：完成人工复核和本地源文件删除后的待交付凭证。

它不创建新评估 Runtime，不修改现有评分语义，也不把本地处理升级为
阿里云市场交付、客户验收、客户验证或生产服务。

## 何时使用

- 客户需求严格限定为一个工作流和一个场景；
- 只提交规范化事件摘要和证据存在性声明；
- 提交方确认来源已授权、材料已脱敏；
- 不包含个人信息、密钥、原始对话、原始日志、代码、可执行内容或任意 URL；
- 交付由人工通过阿里云市场服务流完成。

## 何时不使用

- 需要 SAEE 连接、运行、部署或控制客户 Agent；
- 需要读取原始生产日志、提示词、消息、附件或数据库；
- 需要安全认证、合规结论、法律意见或部署批准；
- 需要多租户 SaaS、实时监控或运行时阻断；
- 无法确认材料授权、脱敏或本地删除要求。

## 契约

- 接入 schema：
  `agent-interface/commercial/saee-marketplace-assessment-intake.schema.v0.1.json`
- 评估包 schema：
  `agent-interface/commercial/saee-marketplace-assessment-bundle.schema.v0.1.json`
- 交付凭证 schema：
  `agent-interface/commercial/saee-marketplace-delivery-receipt.schema.v0.1.json`
- 示例：
  `agent-interface/commercial/examples/saee-marketplace-assessment-intake.v0.1.json`
- 服务：`saee_backend/services/marketplace_assessment_delivery.py`
- CLI：`scripts/saee_marketplace_assessment_delivery.py`

## 两阶段流程

### 1. Prepare

```bash
python3 scripts/saee_marketplace_assessment_delivery.py prepare \
  --input /protected/intake/request.json \
  --output-dir /protected/output/order-001
```

该阶段验证材料、运行现有只读评估、生成 JSON 和中文报告。源文件不会自动
删除，凭证保持：

```text
stage=prepared_for_human_review
human_boundary_review.completed=false
local_source_deletion.completed=false
marketplace_delivery.ready=false
```

### 2. Finalize

人工核对范围、结论、限制和禁止声明后，显式执行：

```bash
python3 scripts/saee_marketplace_assessment_delivery.py finalize \
  --prepared-receipt /protected/output/order-001/delivery-receipt.prepared.json \
  --input /protected/intake/request.json \
  --intake-root /protected/intake \
  --reviewer-role-token owner-boundary-reviewer
```

Finalize 会重新校验评估包、报告和源文件摘要，只允许删除声明的 intake root
内的普通文件，拒绝符号链接、路径越界和摘要漂移。成功后：

```text
stage=reviewed_ready_for_marketplace_delivery
human_boundary_review.completed=true
local_source_deletion.completed=true
marketplace_delivery.ready=true
marketplace_delivery.completed=false
customer_validated=false
production_ready=false
```

`ready=true` 只表示本地候选交付物可进入人工阿里云市场服务流，不表示已经
上传、交付、验收或结算。

## 验证

```bash
python3 scripts/saee_marketplace_assessment_delivery_smoke.py
```

当前验证覆盖：确定性、现有 operation 委托、schema、客户可读报告、个人信息
与 URL 筛查、禁止原始客户数据、禁止额外字段、符号链接拒绝、intake root
路径边界、摘要防篡改、人工复核和本地删除。

## 真值边界

```text
normalized_customer_metadata_used=true
raw_customer_data_used=false
pii_absence_verified_by_saee=false
trace_authenticity_verified=false
marketplace_delivery_completed=false
commercial_service_delivered=false
customer_validated=false
production_ready=false
```

