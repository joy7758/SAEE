# 让企业 Agent 上线前先检查执行证据：SAEE 与百度千帆的受控组合实践

状态：`local_draft_not_published`。

> 本文描述本地 Alpha 与真实 Qianfan provider 在合成场景中的受控调用结果，不代表
> 百度官方集成、认证、合作背书、Marketplace 上架、客户验证或生产就绪。

## 企业 Agent 上线前缺少什么

企业开发 Agent 时，模型能否生成正确回答只是问题的一部分。只要 Agent 开始查询
订单、调用支付、修改代码或触发部署，团队还需要回答：测试结果在哪里，权限边界
是否清楚，失败后能否回滚，关键动作是否经过人工批准？

这些问题不能由一句“模型表现很好”代替，也不能只靠一个安全或可靠性概率回答。
上线评审需要的是可检查的执行证据，以及对缺失证据的明确说明。

## SAEE Agent Readiness Assessment

SAEE 对外产品形态是 `SAEE Agent Readiness Assessment`。它接收 Agent 配置、任务、
Execution Trace 和 Evidence Bundle，返回结构化 Readiness Report。公共能力只有：

- `saee.evaluate_agent_run`：检查一次 Agent 执行所需证据的覆盖情况；
- `saee.evaluate_evidence`：检查 Evidence Bundle 的充分性和缺口。

SAEE 不执行 Agent，不连接真实业务系统，也不替代身份、策略、授权、部署或支付
系统。报告中的分数是“要求证据覆盖百分比”，不是安全概率、可靠性概率或上线许可。

## 与百度千帆组合的方式

目标组合路径是：千帆 Agent 发现两个 SAEE 工具，通过有边界的 Connector 发出请求，
SAEE Evaluation Engine 计算证据覆盖和缺口，再把结构化结果返回给 Agent。当前实现
使用 Qianfan function calling 与本地 stdio MCP bridge；BOS、远程 MCP 和公共 HTTP
endpoint 仍属于后续目标架构，不能描述为已经部署。

为了降低 provider schema 复杂度，模型侧只选择受 host allowlist 约束的合成
`fixture_id`。完整请求 schema 和 fixture 由本地 host 解析并交给 MCP。这样模型不能
通过工具参数扩大权限、注入客户数据或请求外部执行。

## 两个真实 provider 合成场景

客服退款场景包含测试、回滚与权限边界证据，但缺少人工审批。SAEE 返回
`conditional`，证据覆盖分数 75，并建议 `HUMAN_REVIEW_REQUIRED`。

代码发布场景包含测试和权限边界证据，但缺少回滚方案与人工审批。SAEE 返回
`replan`，证据覆盖分数 50，并建议补齐恢复计划和审批节点。

两次场景共完成 4 个真实 Qianfan provider rounds，外部世界动作始终为 0。回执只保存
response ID、finish reason、模型标识和 SHA-256 摘要，不保存 API Key、Authorization、
原始模型文本或隐藏推理。

## 为什么宿主必须保留最终边界

两次 provider 自然语言总结都没有完整保留 `deployment_authorized=false` 与
`production_ready=false`。因此 SAEE host 丢弃候选总结，直接根据 MCP structured
result 生成确定性 canonical summary，并在 receipt 中记录 fallback。

这不是一个可忽略的格式问题。Agent 工具的结构化结果如果在自然语言总结阶段被
弱化，使用者可能把“证据覆盖较高”误解为“已经允许上线”。因此最终边界必须由
确定性宿主而不是模型自由措辞掌控。

## 三个可复现实例

本地 Cloud Entry Package 提供客服退款、代码发布和 Evidence Bundle 三个固定 Demo。
百度工程师无需 provider 凭据即可在 30 分钟内运行 CLI、stdio MCP 和 validators；
如需复核真实 provider 结果，可检查脱敏 live receipts 和对应 validator。

这些 Demo 都是合成技术样例，不是客户案例。它们证明契约、路由、解释和边界可重复，
不证明商业采用、SLA、生产安全或第三方合规。

## 推荐的生态合作下一步

当前最合适的入口是千帆伙伴咨询和技术评审，而不是直接申报云市场商品。合作验证可
聚焦三个问题：千帆 Agent 是否能稳定发现两个工具、是否能正确传参、是否能保留
非授权边界。之后再评估远程服务、企业身份、租户隔离、隐私法律、支持 SLA、定价和
Marketplace 资质。

SAEE 希望增强千帆 Agent 上线前的可靠性准备，而不是替代百度已有的大模型、安全、
治理或执行能力。

```text
qianfan_real_provider_product_roundtrip=true
qianfan_live_synthetic_scenario_count=2
qianfan_live_provider_round_count=4
external_world_actions=0
official_qianfan_integration=false
customer_validated=false
marketplace_listed=false
production_ready=false
```
