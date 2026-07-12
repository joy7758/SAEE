# SAEE 百度智能云官方入口 Preflight（2026-07-13）

本文件基于百度智能云官方页面的只读核验结果。它不是申请、咨询、联系、协议
接受或入驻证明。

## 推荐入口顺序

### 1. 千帆伙伴咨询——首选

官方入口：<https://cloud.baidu.com/survey/qianfanpartnerconsultation.html?track=C841333>

官方表单明确用于千帆平台咨询或生态合作，收集行业、产品形态、服务能力、希望
获得的合作权益、公司名称、联系人、职位和手机。SAEE 对应的候选填写方向是：

- 产品形态：`服务`，是否同时选 `SaaS` 由负责人决定；
- 服务能力：`产品集成`；
- 合作权益：`应用场景共建`、`技术赋能提升`；
- 合作叙事：增强千帆 Agent 上线前可靠性，不替代百度治理或授权。

当前已获得百度联系与申请提交授权。仍缺公司行业、公司名称、联系人、职位、
手机、实名认证与联系同意；这些值不可从仓库或路径推断，不能代填。

申请字段已固定为机器可读 payload：
`agent-interface/ecosystem/saee-baidu-partner-consultation-application.v1.json`。
其 validator 会在任一必填值或联系同意缺失时保持
`ready_for_submission=false`，并把伙伴咨询与 Marketplace 入驻严格分开。

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

## 当前推荐结论

```text
qianfan_partner_consultation=recommend_after_company_contact_input_and_explicit_authorization
general_partner_application=conditional_after_qualification_packet
product_certification=do_not_recommend_before_partner_registration_and_service_evidence
direct_cloud_marketplace=do_not_recommend_currently
official_pages_checked=true
external_form_opened_for_read_only_inspection=true
form_fields_filled=false
agreement_accepted=false
external_contact=false
submission=false
```
