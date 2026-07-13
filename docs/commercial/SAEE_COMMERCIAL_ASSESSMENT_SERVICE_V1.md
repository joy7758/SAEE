# SAEE 商业评估服务 v1

## 定位

SAEE 商业评估服务把受控智能体演练的 Run Manifest、可靠性 Assessment 和 Evidence Adequacy 结果投影为中文、机器可读的审查响应。

它回答：

- 当前选定 Agent 与场景有哪些可评估观察？
- 哪些维度出现通过、部分、失败或未评估状态？
- 失败属于合同、模型响应、工具、环境、证据还是授权关系？
- 下一轮应补充什么观察或证据？

它不回答：

- 哪个模型最好；
- 系统是否绝对安全或合规；
- 是否应自动批准部署；
- 是否构成法律结论或认证。

## Agent 调用入口

```bash
python3 scripts/saee_agent_cli.py generate-commercial-assessment \
  --input agent-interface/commercial/examples/saee-commercial-assessment-request.v1.0.json
```

生成可保存的本地响应：

```bash
python3 scripts/saee_commercial_assessment_service.py \
  --input agent-interface/commercial/examples/saee-commercial-assessment-request.v1.0.json \
  --output agent-interface/commercial/examples/saee-commercial-assessment-response.v1.0.json
```

## 输入契约

请求必须引用三个仓库内对象：

1. 基准结果；
2. Run Manifest 集；
3. Reliability Assessment 集。

请求还必须给出 Agent Profile 和 Scenario ID 的非空选择范围。路径穿越、空范围、客户数据、部署决策请求和非中文主界面都会被拒绝。

## 输出契约

输出包含：

- 五个独立可靠性维度；
- 失败类型及解释边界；
- Evidence Adequacy 的 `PASS`、`FAIL`、`NOT_ASSESSED` 计数；
- 后续审查动作；
- 三个输入文件的 SHA-256 绑定；
- 明确限制与真值边界。

不提供总分，因为总分会掩盖场景差异和证据缺口。

## 当前阶段

```text
service_stage=local_agent_callable_validated_service
commercial_delivery_completed=false
customer_validated=false
external_validation_completed=false
deployment_authorized=false
production_ready=false
```

Phase 7.2 已形成 75-run Corpus，Phase 7.3 已生成 SHA-256 研究包，Phase 8 已完成 9 个三轮智能体验证会话。因此，该服务可在“本地、受控合成证据、无外部动作”范围内推荐。它仍不是客户交付、市场验证或生产 SaaS。
