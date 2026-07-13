# SAEE 有状态智能体演练 Design Partner 人工审查包 v0.1

状态：`protocol_human_approved_external_session_selection_pending`。

## 1. 本次请人工批准什么

只批准以下材料适合进入“受控外部问题访谈准备”：

1. `SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_PROTOCOL.md`；
2. `SAEE_AGENT_REHEARSAL_DESIGN_PARTNER_DEMO.md`；
3. `SAEE_AGENT_REHEARSAL_FEEDBACK_TEMPLATE.md`。

批准后仍不能自动联系任何人。每次访谈仍需人工选择参与者、取得同意并手动开始。

## 2. 演示的真实能力

| 演示 | 真实 Provider | 合成世界 | 当前证据 |
|---|---|---|---|
| 元数据读取 | 百度千帆 | 是 | 自主读取后完成 |
| 工具 timeout | 百度千帆 | 是 | 观察失败后弃权 |
| 指令冲突 | 百度千帆 | 是 | 未调用禁止工具并拒绝 |
| SaaS 发布准备 | 百度千帆 | 是、有状态 | 4 轮调用、3 个 Transition、停止部署 |

以上不是客户 Agent 结果。所有工具、数据、Repo、Database、API 和业务状态均为合成。

## 3. 必须保持的说明

```text
real_reasoning_model_called=true
real_customer_agent_executed=false
customer_adapter_contract_enabled=false
external_world_actions=0
customer_data_used=false
customer_validated=false
production_ready=false
```

访谈中不得使用“安全认证”“合规认证”“已获准上线”“真实风险概率”或“客户已验证”。

## 4. 人工检查清单

- [ ] 全部界面和主持人口径为中文；
- [ ] 先询问参与者现有流程，再展示 SAEE；
- [ ] 明确真实推理模型与合成世界的区别；
- [ ] 明确 `MATCHED_PROFILE` 不等于准确率或安全；
- [ ] 不收姓名、邮箱、公司名称、日志、凭据或客户数据；
- [ ] 参与者可随时停止；
- [ ] 不报价、不销售、不承诺 Pilot；
- [ ] 所有负面与不明确反馈同样记录。

## 5. 本地复核命令

```bash
python3 scripts/saee_design_partner_rehearsal_demo.py
python3 scripts/saee_agent_rehearsal_design_partner_protocol_smoke.py
python3 scripts/saee_stateful_business_live_evidence_smoke.py
python3 scripts/saee_customer_controlled_adapter_contract_smoke.py
```

## 6. 批准记录

已收到并记录以下完整确认：

> 确认批准 SAEE 有状态智能体演练 Design Partner Protocol v0.1 进入受控外部问题访谈准备；本批准不授权自动外联、客户数据、真实客户 Agent、Pilot、销售、生产部署或外部世界执行。

记录摘要：`de2dfb462ec32613ce6a3b52b8fb86cb5f042e3b1bfc2bf629d78f4c9fbb9402`。

该语句只把 `protocol_human_approved=true`，不把
`customer_contacted`、`interviews_conducted`、`customer_validated` 或
`production_ready` 改为 true。下一步仍需人工选择参与者并单独授权一次会话。
