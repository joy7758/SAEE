# SAEE 百度千帆生态公开 Demo 包 v1.0

状态：`local_publication_ready_external_publication_not_authorized`。

这是三个可公开展示的合成 Demo 索引，不是客户案例、百度官方认证、千帆原生 MCP
兼容证明或 Marketplace 上架材料。所有输入均为固定合成数据，运行只调用本地只读
评估能力，不连接支付、代码托管、部署或其他真实业务系统。

## 1. 智能客服退款 Agent

- 输入：`../demo/customer-service-refund/request.json`
- 固定结果：`conditional`，证据覆盖分数 `75`
- 关键缺口：`HUMAN_APPROVAL`
- 展示重点：支付类动作前需要明确人工审批节点。

```bash
python3 scripts/saee_baidu_readiness.py evaluate-agent-run \
  --input cloud-entry-package/demo/customer-service-refund/request.json
```

## 2. 代码 Agent 发布准备

- 输入：`../demo/coding-agent-release/request.json`
- 固定结果：`replan`，证据覆盖分数 `50`
- 关键缺口：`ROLLBACK_PLAN`、`HUMAN_APPROVAL`
- 展示重点：测试通过不等于具备发布授权。

```bash
python3 scripts/saee_baidu_readiness.py evaluate-agent-run \
  --input cloud-entry-package/demo/coding-agent-release/request.json
```

## 3. Evidence Bundle 充分性

- 输入：`../demo/evaluate-evidence/request.json`
- 固定结果：`PARTIAL`
- 展示重点：区分证据存在、证据充分和外部授权。

```bash
python3 scripts/saee_baidu_readiness.py evaluate-evidence \
  --input cloud-entry-package/demo/evaluate-evidence/request.json
```

## 千帆真实调用证据

客服和编码两个场景已各完成一次真实 Qianfan function-calling 产品 roundtrip，合计
4 个 provider rounds。脱敏回执位于
`agent-interface/qianfan/live-validation/`，不保存凭据或原始模型文本。该证据只证明
受控合成场景中的真实 provider 调用，不证明官方千帆集成、客户采用或生产就绪。

## 发布前检查

```bash
python3 scripts/saee_baidu_publication_package_smoke.py
python3 scripts/saee_baidu_entry_acceptance.py
```

发布前还必须获得对应渠道授权。当前 Git tag、push、GitHub Release、千帆社区发布
和技术文章发布均未授权。

```text
synthetic_data_only=true
external_world_actions=0
public_demos_published=false
official_qianfan_integration=false
marketplace_submission=false
customer_validated=false
production_ready=false
```
