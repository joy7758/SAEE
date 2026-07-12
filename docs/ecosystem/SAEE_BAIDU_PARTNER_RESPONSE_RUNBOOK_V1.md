# SAEE 百度千帆伙伴反馈跟踪 Runbook v1.0

状态：`waiting_for_initial_baidu_response`。

千帆伙伴咨询已提交并记录脱敏 receipt。官方页面没有公开响应 SLA、backend
submission ID 或持久确认文本，因此本项目不虚构“几日内回复”，也不自动重复提交。

## 当前动作

等待百度通过 owner 已同意的联系方式反馈。收到电话、短信、邮件或其他官方反馈后，
只记录：收到时间、渠道、可追溯来源引用、脱敏摘要与百度明确表达的决定。不要把原始
邮件、通话录音、手机号或其他个人数据复制到父仓库。

## 状态转移

1. `waiting_for_initial_baidu_response`
   - 没有反馈证据时保持本状态；
   - 不把页面跳转解释为合作批准。
2. `response_received_human_review_required`
   - 仅在存在可追溯百度反馈后进入；
   - 负责人判断是技术评审请求、补充材料、延期还是拒绝。
3. `technical_review_handoff_candidate`
   - 百度明确请求技术评审后进入；
   - 上传文件、共享仓库、安排会议或再次传输联系人数据仍需新的动作授权。
4. `deferred_or_declined_recorded`
   - 如百度延期或拒绝，原样记录，不改写为合作机会已验证。
5. `follow_up_ready_human_send_gate`
   - 只有负责人显式授权 follow-up 后进入；
   - tracker 本身不发送消息或创建自动提醒。

## 反馈接收模板

```text
收到时间=
渠道=电话/短信/邮件/其他
来源引用=本地可追溯记录，不填写手机号或原始私信
脱敏摘要=
百度明确决定=technical_review_request/material_request/deferred/declined/other
请求的下一动作=
```

## 边界

```text
qianfan_partner_consultation_submitted=true
baidu_response_received=false
baidu_partnership_approved=false
automated_follow_up_authorized=false
marketplace_submission=false
marketplace_listed=false
customer_validated=false
production_ready=false
```
