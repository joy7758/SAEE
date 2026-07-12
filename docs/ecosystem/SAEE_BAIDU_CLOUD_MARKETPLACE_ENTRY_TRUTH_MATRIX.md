# SAEE 百度智能云市场实施真值矩阵 v1.0

本矩阵把 `Cloud Marketplace Entry Plan v1.0` 的目标拆成可核验状态。它是实施
台账，不是百度官方接纳、合作或上架证明。

| 要求 | 当前证据 | 当前状态 | 完成证据 |
|---|---|---|---|
| 对外品牌冻结 | 六个一级 Agent surface 已同步 | `completed_local` | README、状态、Capability Card、OpenAPI、MCP、llms、agent-index 使用同一产品身份 |
| 公共 API 仅两个 | Capability Card、OpenAPI 与 MCP 严格为两个 | `completed_local` | Validator 拒绝第三个公共工具 |
| 内部调试工具降级 | `rehearse_agent`、`describe_saee`、`compare_observed_traces` 不在产品包 | `completed_local` | 只保留 internal/debug 语义 |
| Qianfan Adapter | 两工具 stdio MCP、host alias、离线模拟与两组真实 Qianfan 合成场景回执 | `real_provider_synthetic_roundtrip_pass` | 2 个场景、4 个 provider rounds；官方集成仍为 `false` |
| 客服 Demo | 合成退款场景请求、响应和截图 | `completed_local_synthetic` | CLI/MCP 一致性通过 |
| 编码 Demo | 合成发布场景请求、响应和截图 | `completed_local_synthetic` | CLI/MCP 一致性通过 |
| Cloud Entry Package | 完整本地包与 30 分钟路径 | `completed_local_validated` | `scripts/saee_cloud_entry_package_smoke.py` 通过 |
| 产品介绍页 | `sites/saee-commercial` 本地构建与 10 项测试通过 | `completed_local_not_published` | 未部署、未宣称官网上线 |
| 技术白皮书 | 10 页 A4 PDF 与 Markdown 真源 | `completed_local_validated` | 页面渲染、文本与边界抽检通过 |
| 3 分钟 Demo 视频 | 180.021 秒 H.264/AAC、9 场景、字幕与 manifest | `completed_local_validated` | 抽帧、音轨时长和 SHA256 通过 |
| Git Alpha Release | `main` 本地基线 commit `c0cf49e` 已创建；许可证暂不公开 | `local_commit_complete_public_release_withheld` | 未授权 tag、push 或 GitHub Release |
| 定价 | 建议价仅来自目标文件 | `human_review_required` | owner 批准价格记录；发布另需授权 |
| 百度生态合作申请 | 官方入口已核验；千帆伙伴咨询为首选；Word 方案包已渲染核验；联系和提交已获授权 | `company_contact_inputs_required` | 补全不可推断的公司/联系人字段并满足实名认证后提交 |
| 云市场直接入驻 | 官方条件要求主体、10+ 技术/客服、2+ 年经验、5×8 支持、软著和专用实名账号 | `do_not_recommend_currently` | 每一条件均有来源证据后再评估，不把千帆咨询等同入驻 |

## 当前阶段结论

```text
overall_status=phases_0_to_3_local_complete_real_qianfan_synthetic_roundtrip_phase_4_company_input_gate
recommendation=conditional
marketplace_submission=false
marketplace_listed=false
customer_validated=false
production_ready=false
external_action_authorized=true
external_action_authorization_scope_limited=true
```

## 下一最小验收

下一步是在已授权范围内补全企业与联系人信息并提交千帆伙伴咨询。许可证保持
暂不公开；tag、push、GitHub Release 与公开价格仍未授权，不得执行。
