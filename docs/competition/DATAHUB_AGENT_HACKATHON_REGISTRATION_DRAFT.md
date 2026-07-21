# DataHub Agent Hackathon 报名与参赛材料草稿

```text
draft_date=2026-07-18
registration_form_status=SUBMITTED_VERIFIED
registration_verified_date=2026-07-18
project_draft_status=PREPARATION_ONLY
project_submission_status=NOT_STARTED
final_submission_authorized=false
```

## 1. Devpost 加入赛事表单草稿

以下是建议选择，不代表参赛者本人已作出资格或条款声明：

| 表单字段 | 建议值 | 状态 |
| --- | --- | --- |
| Teammates（队友） | `Working solo` | 已由本人确认 |
| How did you hear about this?（获知渠道） | `Devpost` | 已由本人确认 |
| DataHub familiarity（熟悉程度） | `I'm new to DataHub` | 已由本人确认 |
| Challenge（赛题） | `Metadata-Aware Code Generation & Development` | 已由本人确认 |
| Marketing updates（营销更新） | 不勾选 | 已由本人确认 |
| Eligibility agreement（资格声明） | 已确认 | 已由本人确认 |
| Official Rules / Devpost Terms（规则与条款） | 已同意 | 已由本人确认 |

以上选择经参赛者本人确认后已完成报名。Devpost 页面显示 `Thanks for registering!`。
加入赛事不等于提交项目，也不授权最终 `Submit`（提交）动作。

## 2. 项目身份

**Title（标题）**

> SAEE Evolution Capability Router

**中文标题**

> SAEE 进化能力路由器

**Subtitle（副标题）**

> An agent-readable capability truth and reuse layer for reliable AI development

**中文副标题**

> 面向可靠 AI 开发的智能体可读能力事实与复用层

```text
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
ENGINEERING_CORE=Digital Biosphere Evolution Engine
CURRENT_CAPABILITY_UNCHANGED=true
FUTURE_RESEARCH_ONLY=true
```

禁止把项目改写为通用 AI Agent 平台、Agent Runtime、Agent Governance Platform、
自动授权系统或企业智能体管理系统。

## 3. Short description（短介绍）

Coding agents are becoming capable of modifying complex repositories, but they need reliable
knowledge of existing capabilities, lifecycle states, and canonical implementations.

编码智能体正在获得修改复杂代码库的能力，但它们需要可靠理解已有能力、生命周期状态
和规范实现。

SAEE helps agents discover existing capabilities, route to canonical implementations, and prevent
duplicate construction while preserving staged truth.

SAEE 帮助智能体发现已有能力、连接规范实现，并在保持阶段事实边界的同时阻止重复建设。

## 4. DataHub-specific pitch（DataHub 专项介绍）

This hackathon project proposes a bounded DataHub context extension for SAEE. DataHub OSS provides
metadata context about repository capabilities to an AI coding agent. SAEE then checks that context
against its canonical capability inventory and routes the agent to an existing implementation when
one is already present. The goal is to prevent duplicate construction without turning metadata into
an authorization or production-readiness claim.

本届黑客松项目拟为 SAEE 构建一个边界明确的 DataHub 上下文扩展。DataHub OSS 向 AI
编码智能体提供仓库能力元数据上下文；SAEE 再用规范能力清单核验该上下文。当等价能力
已经存在时，将智能体路由到已有实现。目标是在不把元数据升级为授权或生产就绪声明的
前提下阻止重复建设。

```text
text_status=DRAFT
described_datahub_extension_status=NOT_IMPLEMENTED
preexisting_saee_assets_must_be_disclosed=true
```

## 5. Demo storyboard（演示脚本）

演示对象使用真实存在的 `saee.evaluate_agent_run`，不虚构 identity-service 等不存在的
案例。

1. Developer（开发者）要求 AI coding agent 增加 agent-run evidence evaluation（智能体
   运行证据评估）能力。
2. Agent 准备创建新实现，并先通过 DataHub agent context（智能体上下文）查询仓库元数据。
3. DataHub 返回与 `saee.evaluate_agent_run` 相关的 capability metadata。
4. SAEE 查询 `capability-package/manifest.json#canonical_inventory` 并核对规范事实。
5. 因为能力已经存在，演示返回 `REUSE`，并展示：
   - `capability_status`；
   - `canonical_implementation`；
   - `reason_codes`；
   - `non_claims`。
6. Agent 停止平行建设，转而使用规范接口。

该 storyboard（演示脚本）只有在 DataHub 接入、输出格式与端到端路径真实实现并通过本地
验证后才能录制为成果；当前只能标记为 `DESIGN_ONLY`。

## 6. 建议视频结构（少于 3 分钟）

- 0:00–0:20：重复建设问题与项目一句话定位；
- 0:20–0:45：DataHub 中的仓库能力元数据；
- 0:45–1:45：Agent 请求、DataHub 上下文查询、SAEE 规范清单核验；
- 1:45–2:20：`REUSE`、规范实现、原因代码与 non-claims；
- 2:20–2:45：真实边界、复现方式与项目价值。

## 7. 最终提交资产清单

```text
project_description=DRAFTED
readme=EXISTING_SAEE_README_NOT_YET_ADAPTED
public_repository=NOT_PREPARED
apache_2_license=BLOCKED_BY_LICENSE_DECISION
datahub_integration=NOT_IMPLEMENTED
sample_inputs_outputs=NOT_PREPARED
demo_video=NOT_RECORDED
screenshots=NOT_PREPARED
architecture_diagram=NOT_PREPARED
test_access=NOT_PREPARED
preexisting_code_disclosure=DRAFTED_IN_PRINCIPLE
```

OpenAI Build Week（OpenAI 构建周）的文字定位与非声明边界可以作为参考，但不得修改
已经提交的 OpenAI 版本，也不得直接复用其“已提交”状态、截图、视频或外部验证声明。

## 8. 赛期技术落地路径

此路径是后续实现准备，不是当前能力声明：

1. 按 DataHub Quickstart（快速入门）在隔离环境启动 DataHub OSS；
2. 只使用公开、合成或仓库自有 capability metadata（能力元数据）；
3. 选择 DataHub Skills 或 Agent Context Kit 作为首个 agent-readable（智能体可读）入口；
4. 建立最小 DataHub metadata → SAEE canonical resolver（规范解析器）适配层；
5. 用 `saee.evaluate_agent_run` 的真实规范事实完成 `REUSE` 端到端场景；
6. 保存样例输入、样例输出、版本、commit 与 non-claims；
7. 完成可复现说明后再制作演示视频。

官方技术入口：

- DataHub Quickstart：https://docs.datahub.com/docs/quickstart
- DataHub Skills：https://docs.datahub.com/docs/dev-guides/agent-context/skills
- DataHub Agent Context：https://docs.datahub.com/docs/dev-guides/agent-context/agent-context

## 9. Pre-existing asset disclosure（既有资产披露）草稿

> SAEE and its canonical capability inventory predate this hackathon. The submitted hackathon work,
> if completed, will be limited to the new DataHub context extension, its integration code, fixtures,
> tests, documentation, and demo assets created during the official submission period. Pre-existing
> SAEE capabilities will be used as disclosed dependencies and will not be claimed as new hackathon
> development.

中文：SAEE 及其规范能力清单早于本届赛事存在。若最终完成提交，本届新增成果仅限于
官方提交期内创建的 DataHub 上下文扩展、集成代码、fixtures（测试样本）、测试、文档与
演示资产。既有 SAEE 能力只作为明确披露的依赖使用，不声明为本届新开发成果。

## 10. 评审材料映射

| 评审标准 | 需要提供的直接证据 | 当前状态 |
| --- | --- | --- |
| Use of DataHub | DataHub OSS 启动与 agent context 调用记录 | `NOT_PREPARED` |
| Technical Execution | 适配层、测试、可复现步骤 | `NOT_PREPARED` |
| Originality | metadata → canonical reuse decision 的差异化说明 | `DRAFTED` |
| Real-World Usefulness | 防重复建设场景与前后对比 | `DRAFTED` |
| Submission Quality | README、公开仓库、视频、样例输入/输出 | `NOT_PREPARED` |

```text
registration_complete=true
project_creation_authorized=false
implementation_authorized=false
final_submission_authorized=false
```
