# SAEE Software Copyright Application Recommendation Gate v1.0

## Recommendation question

如果潜在客户或生态平台需要核验 SAEE 软件权属，我们是否推荐由山西游骑兵电子商务有限公司申请 `SAEE智能体就绪评估软件 V1.0` 的计算机软件著作权登记？

```yaml
recommendation_gate:
  feature_or_direction: SAEE智能体就绪评估软件V1.0软件著作权登记
  target_customer_need: 可核验的软件权属证明与云市场准入材料
  answer: recommend
  reasons_to_recommend:
    - 当前两项公开只读能力已有明确代码、Schema、示例和离线验证
    - 登记证书可形成权属初步证明并解除部分软件渠道的证书门槛
    - 申请包可通过文件哈希、源程序清单和说明书由智能体复核
  reasons_not_to_recommend:
    - 外部门户提交前仍需公司签字或盖章并复核企业当前登记状态
  decomposition:
    - blocker: applicant_legal_fields_missing
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: 由申请主体提供营业执照与法定字段并完成一致性核验
      acceptance_criteria: 申请表、营业执照和主体名称完全一致
      resolution: 2026-07-13已从营业执照回填统一社会信用代码、注册地址、法定代表人等字段；私密联系方式保存在git-excluded本地文件
      status: resolved
    - blocker: source_version_not_committed
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: 将申请切片纳入版本控制并冻结commit与SHA-256清单
      acceptance_criteria: 源程序鉴别材料与冻结清单哈希一致
      resolution: 候选源程序已纳入Git且状态干净；manifest记录Git HEAD与SHA-256 freeze_id
      status: resolved
    - blocker: ownership_and_confidentiality_review_open
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: 核验开发组织关系、第三方来源和专利/商业秘密交存策略，并生成公司确认书
      acceptance_criteria: 公司书面确认权属且决定普通交存、例外交存或封存
      resolution: 已采用独立开发、原始取得、全部权利与普通交存；确认书已生成，待公司签字或盖章
      status: resolved_for_local_pack_pending_signature
  final_decision: 推荐申请并已完成本地材料；公司签字或盖章、登记现状复核及单独外部授权后方可登录、上传和提交
```

## Agent-native three-question gate

1. Discoverable: `yes`，申请 manifest、源程序 manifest、说明书和 smoke 均为文件化入口。
2. Understandable: `yes`，软件用途、非用途、两项公开操作和外部动作边界明确。
3. Composable: `yes`，字段、源程序、说明书、确认书与离线 smoke 已形成稳定本地契约；签字/盖章及最终外部授权仍由人类保留。

## Required evolution design check

- 强化子系统：Evolutionary Archive / Rollback Immune System，同时支持生态选择所需的权属证据。
- 改善：archive、rollback、selection；不改变科学对象和进化闭环。
- 安全、许可证、供应链、权限边界保持不变；未自动安装依赖或扩大权限。
- `audit_first_reframe=false`；软著登记是权属/版本档案，不是项目核心。
