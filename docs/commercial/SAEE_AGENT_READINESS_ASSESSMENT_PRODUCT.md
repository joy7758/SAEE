# SAEE Agent Readiness Assessment

## 产品问题

> 这个智能体在真实部署前，能否在指定工作流和受控场景中可靠完成任务？

SAEE Agent Readiness Assessment 把既有受控演练、可靠性评估和证据充分性能力组织成一个固定范围的本地评估产品。它不增加新 Runtime。

## 目标客户

首要客户假设是 Agent Builder（智能体开发团队）：

- AI 创业公司；
- Agent SaaS 团队；
- 企业内部 Agent 开发团队。

当前只是客户假设，`customer_validated=false`、`market_validation=false`。

## 输入

- 一个 Agent 工作流描述；
- 一个明确任务场景；
- 经批准的执行记录或受控演练结果；
- 相关 Evidence 与评估 Profile 引用。

原有 Commercial Assessment Service 继续读取仓库内 Benchmark Result、Run Manifest 和 Reliability Assessment。

阿里云市场交付桥 v0.1 已增加严格的规范化材料接入：仅允许一个工作流、一个场景、事件摘要和证据存在性声明，并要求来源授权与脱敏声明。它拒绝原始客户内容、个人信息、密钥、代码、任意 URL、权限扩大和 `customer_data_included=true`。该桥复用 `saee.evaluate_agent_run`，不创建新 Runtime。当前尚未发生真实客户交付或验收。

## 输出

- 可靠性发现；
- 证据充分性与缺失证据；
- 失败分类与理由码；
- 有边界的改进建议；
- 输入摘要绑定与限制声明。

允许的建议只有：`CONTINUE`、`REPLAN`、`HUMAN_REVIEW_REQUIRED`、`STOP`。建议是评估上下文，不是部署授权。

## 固定范围工作流

```text
Agent + Workflow + Scenario + Execution Record
                    ↓
             SAEE Assessment
                    ↓
Reliability Findings + Evidence Findings + Recommendations
```

## 不提供

- 认证或合规结论；
- 实时授权和运行时阻断；
- 生产部署批准；
- 绝对安全保证；
- 最佳 Agent 排名；
- 客户成功或收入证明。

## 当前状态

```text
commercial_product_design=true
assessment_package=true
production_service=false
public_service=false
commercial_delivery_completed=false
customer_validated=false
market_validation=false
```

Marketplace 交付桥入口：

- 说明：`docs/commercial/SAEE_ALIBABA_MARKETPLACE_DELIVERY_BRIDGE_V0_1.md`
- 接入 schema：`agent-interface/commercial/saee-marketplace-assessment-intake.schema.v0.1.json`
- 验证：`python3 scripts/saee_marketplace_assessment_delivery_smoke.py`
