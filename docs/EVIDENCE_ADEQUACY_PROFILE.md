# SAEE 证据充分性剖面 v0.1

## 目的

schema 合法只能说明对象结构符合契约；收据摘要一致只能说明声明字段在当前规范化规则下没有发生未被发现的变化。两者都不能自动回答“这些材料是否足以支持某个责任声明”。

SAEE Evidence Adequacy Profile v0.1 把声明类型、必需证据字段、必需关系和稳定失败原因写成智能体可检索的文件化剖面。评估器离线读取一个合成证据包，先检查证据是否存在，再检查引用、时间、范围或因果绑定是否一致。

“SAEE does not prove that an event happened merely because a record exists. SAEE evaluates whether the available evidence is sufficient to support a defined accountability claim.”

“SAEE不会因为存在一条记录就证明事件一定发生。SAEE评估的是现有证据是否足以支持一个明确的责任声明。”

## 三个不同问题

1. **证据存在**：输入中是否带有目标字段。
2. **证据有效**：相关对象是否通过自身 schema、摘要或语义验证。
3. **证据满足剖面**：有效证据之间是否满足该声明要求的引用、范围、时间或因果关系。

v0.1 的 `PASS` 只回答第三个问题的本地剖面部分。输出始终保留：

```json
{
  "profile_requirements_satisfied": true,
  "accountability_claim_established": false
}
```

因此不能把 `PASS` 解读为事件真实发生、身份已独立验证、授权在外部系统中真实有效，或已经形成法律事实认定。

## 四个声明剖面

### `RESOURCE_AUTHENTICITY`

检查证据包是否包含一个通过现有资源解析验证器的收据，并覆盖请求资源、解析 URI、发布者身份声明、内容摘要和策略决定引用。名称沿用任务约定，但它只评估“真实性相关证据是否满足本地剖面”，不独立证明真实发布者或真实外部资源。

### `AUTHORIZED_AGENT_ACTION`

除字段存在性外，还检查：

- action 与 policy decision 的 `agent_id`、`action_id` 一致；
- decision 是 `allow`；
- action 时间位于授权有效窗口内；
- 授权范围覆盖动作请求范围。

### `HUMAN_OVERSIGHT`

除具名审批引用外，还要求风险摘要、审批时看到的证据引用、批准范围、批准时间和动作绑定。审批必须发生在动作之前，批准范围必须覆盖动作范围。合成记录不证明真实人类实际参与。

### `EXECUTION_BOUNDARY`

要求资源绑定、执行效果和显式因果链接同时存在，并使 receipt、effect、content digest、resolved URI 和 sandbox 引用相互一致。v0.1 只检查合成关系，不执行资源，也不声称真实执行效果发生。

## 为什么不是普通字段检查器

只补齐字段仍会失败的情况包括：

- action 与策略决定属于不同智能体或不同动作；
- 动作发生在授权有效期之外；
- 策略或人工批准范围不覆盖动作范围；
- 人工批准晚于动作；
- 资源摘要、解析 URI、效果引用或因果链接不一致；
- 内嵌资源收据的 SHA-256 或收据摘要无法重算通过。

这些检查仍是有限的本地语义规则，不是通用逻辑证明器。

## 验证命令

```bash
python3 scripts/saee_agent_cli.py validate-evidence-adequacy \
  --profile RESOURCE_AUTHENTICITY \
  --input agent-interface/examples/evidence-adequacy/resource_authenticity_pass.json
```

支持的 `--profile`：

- `RESOURCE_AUTHENTICITY`
- `AUTHORIZED_AGENT_ACTION`
- `HUMAN_OVERSIGHT`
- `EXECUTION_BOUNDARY`

`PASS` 返回退出码 `0`；`FAIL` 返回退出码 `2`。完整聚焦检查：

```bash
python3 scripts/saee_evidence_adequacy_smoke.py
```

## 当前限制

- 只接受仓库内四个固定 v0.1 剖面，不动态加载任意代码或外部剖面。
- 不访问网络、DNS、注册表、身份系统、策略引擎或外部时间源。
- 不验证真实人类身份、发布者身份、授权撤销状态或签名材料。
- 不形成法律认定、监管合规、安全认证或生产就绪结论。
- `RESOURCE_AUTHENTICITY` 的通过仍受资源解析收据自身“发布者未独立验证”边界限制。
- `EXECUTION_BOUNDARY` 只验证合成引用一致性，不证明因果关系在现实运行时成立。
- 当前没有实现 OpenTelemetry 或 IETF 映射。

本剖面属于数字生物圈的演化档案／回滚免疫子系统，用于提高选择依据的可复核性；它不是 SAEE 的工程核心，也不改变“数字生物可以观察外部世界，但不能直接执行外部世界”的边界。
