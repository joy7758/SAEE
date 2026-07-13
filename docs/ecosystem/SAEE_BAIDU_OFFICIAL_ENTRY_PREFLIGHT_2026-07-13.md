# SAEE 百度智能云官方入口 Preflight（2026-07-13）

本文件起始于百度智能云官方页面的只读核验，现已追加千帆伙伴咨询提交记录。
该记录不是百度合作通过、官方集成、Marketplace 入驻或上架证明。

## 推荐入口顺序

### 1. 千帆伙伴咨询——首选

官方入口：<https://cloud.baidu.com/survey/qianfanpartnerconsultation.html?track=C841333>

官方表单明确用于千帆平台咨询或生态合作，收集行业、产品形态、服务能力、希望
获得的合作权益、公司名称、联系人、职位和手机。SAEE 对应的候选填写方向是：

- 产品形态：`服务`，是否同时选 `SaaS` 由负责人决定；
- 服务能力：`产品集成`；
- 合作权益：`应用场景共建`、`技术赋能提升`；
- 合作叙事：增强千帆 Agent 上线前可靠性，不替代百度治理或授权。

百度联系与申请提交已获授权。Owner 随后提供公司行业、公司名称、联系人、职位、
手机与联系同意；这些值已用于官方表单，但没有复制进本次申请回执或父仓库
public allowlist。独立站点仓库中的既有公开字段属于另一治理范围。

申请字段已固定为机器可读 payload：
`agent-interface/ecosystem/saee-baidu-partner-consultation-application.v1.json`。
其 validator 在提交前保持 fail-closed。提交后仓库仅保存脱敏 receipt：已观察到
官方成功分支配置的千帆产品页跳转，但页面未提供 backend submission ID 或持久成功
文本。伙伴咨询与 Marketplace 入驻仍严格分开。

### 2. 百度智能云技术/产品合作伙伴——第二阶段

官方入口：<https://cloud.baidu.com/partner/apply.html>

表单要求单位名称、性质、官网、地址、业务类型、资质证明、产品方案附件、合作
方向、服务类别、计划投放产品、支持热线、规模与负责人信息，并涉及协议接受。
当前 Word 产品方案包可作为附件候选，但营业执照、主体、支持和协议决定仍缺失。

### 3. 合作伙伴产品认证——合作后

官方说明：<https://cloud.baidu.com/partner/product-certification.html>

官方评估维度包括百度产品应用、技术架构、完整技术服务和公司主体资质；前提是
先注册为合作伙伴并提交认证申请。当前只具备本地技术架构，不能宣称认证准备完成。

### 4. 云市场服务商入驻——后置，不作为第一动作

条件：<https://cloud.baidu.com/doc/Market/s/ojy6wl8sd>

流程：<https://cloud.baidu.com/doc/Market/s/9jy6y1c8f>

官方条件包括公司资质、联系人、10 人以上技术及客服团队、2 年以上行业经验、
不少于 5×8 在线服务、协议、与百度云资源的产品关系、软件著作权，以及专用企业
实名百度智能云账号。当前这些条件没有充分证据，因此不推荐直接申请云市场。

逐条件脱敏矩阵：
`agent-interface/ecosystem/saee-baidu-marketplace-qualification-matrix.v1.json`。
当前 `verified=0/7`、`partial=1/7`、`missing=6/7`。已有营业执照观察记录和其他
云厂商企业认证只能作为公司资质的部分外部证据，不能替代百度云市场接受；公司
成立年限不能替代 2 年相关行业服务，支持流程 dry run 也不能替代真实 5×8 人员。

## 当前推荐结论

```text
qianfan_partner_consultation=submitted_redirect_acknowledged
general_partner_application=conditional_after_qualification_packet
product_certification=do_not_recommend_before_partner_registration_and_service_evidence
direct_cloud_marketplace=do_not_recommend_currently
official_pages_checked=true
external_form_opened=true
form_fields_filled=true
agreement_accepted=true
external_contact=true
submission=true
submission_redirect_observed=true
backend_submission_id_available=false
marketplace_submission=false
marketplace_qualification_verified_count=0
marketplace_qualification_complete=false
```
