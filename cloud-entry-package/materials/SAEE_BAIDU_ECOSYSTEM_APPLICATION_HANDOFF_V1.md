# 百度智能云生态申请人工交接包 v1.0

状态：`local_handoff_ready_external_action_not_authorized`。

## 已准备材料

- 产品身份：`docs/product/SAEE_PRODUCT_IDENTITY_V1.md`
- 产品技术包：`cloud-entry-package/README.md`
- 10 页白皮书：`output/pdf/SAEE_Baidu_Cloud_Technical_Whitepaper_v1.0.pdf`
- 3 分钟 Demo：`output/video/SAEE_Baidu_Cloud_Demo_v1.0.mp4`
- 本地 Release 候选：`release/SAEE-v0.1-alpha/release-manifest.json`
- 商业包装草案：`cloud-entry-package/materials/SAEE_BAIDU_COMMERCIAL_PACKAGING_DRAFT_V1.md`

## 尚需人工完成

- 填写并核验法定主体、百度账号、官网和联系人；
- 选择公开许可证并审阅首个 commit 范围；
- 审批真实 Qianfan 产品验证、公开价格和对外声明；
- 分项授权 tag、push、GitHub Release、百度联系与申请提交。

授权记录必须写入
`agent-interface/ecosystem/saee-baidu-external-action-authorization-gate.v1.json`。
一个动作的批准不得自动扩展到其他动作。

```text
application_materials_local=true
application_ready=false
external_action_authorized=false
baidu_partner_contacted=false
marketplace_submission=false
```
