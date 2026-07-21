# DataHub Agent Hackathon 报名准备度报告

```text
report_date=2026-07-18
DATAHUB_HACKATHON_RECOMMENDATION=RECOMMEND
recommendation_scope=REGISTRATION_ONLY
final_project_submission_recommendation=CONDITIONAL
registration_status=REGISTERED_VERIFIED
registration_verified_date=2026-07-18
project_submission_status=NOT_STARTED
```

## 1. 赛事真实性

DataHub Agent Hackathon 是当前开放的官方 Devpost 在线赛事。官方主页、规则、时间表与
资源页均可访问。报名和项目提交截止时间为 2026-08-10 17:00 ET，对应中国页面显示的
2026-08-11 05:00 GMT+8。赛事要求新项目、真实使用 DataHub OSS 及指定 agent 能力之一、
公开代码仓库、顶层 Apache-2.0 许可证、项目说明和少于三分钟的公开视频。

证据与检索日期见
`docs/competition/DATAHUB_AGENT_HACKATHON_REVIEW.md`。

## 2. SAEE 匹配度

```text
challenge_fit=HIGH
recommended_challenge=Metadata-Aware Code Generation & Development
existing_saee_capability_fit=HIGH
current_datahub_implementation_fit=NONE_YET
```

SAEE 的 canonical capability inventory、agent-readable contracts、duplicate-build prevention
和 canonical implementation routing 与元数据感知开发高度匹配。DataHub 可提供编码智能体
所需的上下文，SAEE 可核验规范能力事实并引导复用。

匹配不等于集成已经存在。当前 DataHub extension（扩展）只是参赛设计。

## 3. 预计竞争优势

- 从“生成更多代码”转向“先发现、核验并复用已有能力”；
- 规范清单、机器可读接口与 staged truth 已有仓库事实基础；
- `REUSE` 场景短、可视、易于在三分钟内讲清；
- 具有明确 non-claims，避免把 metadata（元数据）当成授权或生产证明；
- 可以用公开、合成或仓库自有元数据完成演示，不要求客户或个人数据。

## 4. 风险与门槛

### 报名风险

- 资格、法定成年、所在地、雇主/学校约束必须由参赛者本人确认；
- Official Rules 与 Devpost Terms 必须由本人确认；
- 表单中的团队、获知渠道与 DataHub 熟悉程度属于本人事实，不能由 Codex 代为证明。

### 最终提交阻塞项

```text
DATAHUB_INTEGRATION_IMPLEMENTED=false
NEW_PROJECT_PERIOD_EVIDENCE_READY=false
SAEE_ROOT_LICENSE_SELECTED=false
PUBLIC_APACHE_2_REPOSITORY_READY=false
PUBLIC_TEST_ACCESS_READY=false
DEMO_VIDEO_READY=false
FINAL_SUBMISSION_AUTHORIZED=false
```

其中许可证是实质性阻塞：当前 SAEE 根仓库没有已选定的 root license（根许可证），不能
为了比赛擅自把现有主线整体改成 Apache-2.0。可选方案需要另行决策，例如创建边界清楚、
只含本届新扩展的 Apache-2.0 公开仓库，并明确披露其与既有 SAEE 资产的关系。

## 5. 需要人工填写或确认的信息

加入赛事所需的以下事项已经由本人确认：

1. 以 `Working solo` 参赛；
2. 通过 `Devpost` 获知赛事；
3. DataHub 熟悉程度为 `I'm new to DataHub`；
4. 选择 `Metadata-Aware Code Generation & Development`；
5. 保持 marketing updates 不勾选；
6. 满足法定成年、地域、雇主/学校及其他资格要求；
7. 已阅读并同意 Official Rules 与 Devpost Terms。

最终项目提交阶段还需要人工决定或提供：团队信息、公开仓库归属、Apache-2.0 许可边界、
公开视频账号、项目测试入口，以及最终提交授权。

## 6. 决策

```text
registration_decision=RECOMMEND
registration_result=REGISTERED_VERIFIED
project_build_decision=CONDITIONAL
final_submission_decision=DO_NOT_SUBMIT_YET
```

理由：赛事真实、仍在报名期且赛题与 SAEE 高度匹配；加入赛事不会改变当前能力事实，
也不构成项目发布或最终提交。但 DataHub 集成、许可证、公开仓库、测试资产和视频尚未
完成，因此最终项目提交必须保持关闭。

## 7. 停止条件

报名已经由 Devpost 的 `Thanks for registering!` 回执验证。报名成功后也不自动创建项目、
创建新能力、修改主线代码、修改 MCP、修改 Schema 或点击最终项目提交。

```text
DATAHUB_HACKATHON_PREPARATION_COMPLETE=true
DATAHUB_HACKATHON_REGISTRATION_COMPLETE=true
WAITING_FOR_HUMAN_REGISTRATION_ATTESTATION=false
WAITING_FOR_HUMAN_FINAL_SUBMISSION_APPROVAL=true
```
