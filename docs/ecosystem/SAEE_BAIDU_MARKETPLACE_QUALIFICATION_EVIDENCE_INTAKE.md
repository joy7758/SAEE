# SAEE 百度云市场资格证据入口 v1.0

本入口只记录脱敏证据引用，不把营业执照、人员名单、合同、手机号、邮箱、身份证、
账号标识或协议正文复制到仓库。它用于准备资格复核，不会自动更新资格矩阵、接受
协议、提交 Marketplace 或声明百度已接受资质。

## 使用方法

1. 复制
   `agent-interface/ecosystem/saee-baidu-marketplace-qualification-evidence-intake.template.v1.json`
   到仓库外的 owner-controlled 工作区。
2. 每个 criterion 只填写 `owner-held://` 脱敏别名，或引用仓库内已有的脱敏
   `repo://` receipt；不得填写绝对路径、网络 URL 或原始个人数据。
3. 运行：

```bash
python3 scripts/saee_baidu_marketplace_qualification_evidence_intake_validator.py \
  --input /path/to/sanitized-intake.json
```

4. Validator `valid` 只表示引用格式、边界和计数有效；不表示证据真实、百度接受、
   资格完成或允许提交。只有外部 provider receipt 与独立 owner review 可以推动矩阵。

## 当前预填状态

- `company_qualification`：仅有营业执照的 owner-held 引用和另一云厂商脱敏企业认证
  receipt，仍为 `partial_reference_only`；
- 其余 6 项：`not_provided`；
- `provider_accepted_count=0`；
- `qualification_updated_by_intake=false`；
- `marketplace_submission=false`。

```text
raw_evidence_stored_in_repository=false
personal_data_stored=false
absolute_paths_allowed=false
network_urls_allowed=false
provider_acceptance_inferred=false
production_ready=false
```
