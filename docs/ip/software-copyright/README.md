# SAEE 软件著作权申请包

本目录是 `SAEE智能体就绪评估软件 V1.0` 的本地、fail-closed 申请准备入口。

## 当前结论

```text
applicant=山西游骑兵电子商务有限公司
application_materials_prepared_local=true
owner_legal_fields_complete=true
ownership_declaration_prepared=true
ownership_declaration_signed_or_sealed=false
ownership_verified=false
source_version_committed=true
portal_login_performed=false
files_uploaded=false
application_submitted=false
certificate_issued=false
```

## Agent 入口

1. 先读 `SAEE_SOFTWARE_COPYRIGHT_APPLICATION_MANIFEST_V1.json`。
2. 用 `SAEE_SOFTWARE_COPYRIGHT_SOURCE_MANIFEST_V1.json` 核对源程序文件与哈希。
3. 运行 `python3 scripts/saee_software_copyright_application_pack_smoke.py`。
4. 只有在公司签字或盖章、企业登记现状复核并取得单独外部提交授权后，才能进入门户上传。

## 本地文档

- `SAEE智能体就绪评估软件V1.0_申请字段底稿.docx`
- `SAEE智能体就绪评估软件V1.0_用户操作说明书.docx`
- `SAEE智能体就绪评估软件V1.0_权属与申请确认书.docx`
- `SAEE智能体就绪评估软件V1.0_源程序鉴别材料.docx`

这些文档不是中国版权保护中心签发的证书，也不证明申请已提交、受理或获证。

## 已采用的推荐值

- 开发方式：独立开发 / 自主研发。
- 权利取得方式：原始取得；权利范围：全部权利。
- 开发完成日期：2026-07-13。
- 发表状态：未发表。公开 SAEE 抽象层不等于本申请冻结的 V1.0 候选源程序已经发表。
- 交存方式：普通交存；候选源程序不足60页，提交全部源程序鉴别材料。

## 隐私与证据

- 住宅邮寄地址、电话和电子邮箱仅写入 git-excluded 的本地私密 manifest 与 DOCX，不写入公开 manifest。
- 营业执照副本由申请人提供并仅用于申请材料；公开 manifest 只记录主体一致性字段、SHA-256 和副本日期，不记录工作台文件名或路径。
- 2026-07-13 尝试实时访问国家企业信用信息公示系统时被浏览器客户端拦截，因此提交前仍需复核登记现状。

## 申请边界

- 著作权人候选主体：山西游骑兵电子商务有限公司。
- 软件是 Digital Biosphere Evolution Engine 的 Agent Readiness 产品投影，不替换 SAEE 工程核心。
- 申请材料强化 Evolutionary Archive / Rollback Immune System 的权属与版本档案，不把项目改写为 audit-first 系统。
- 登记不等于 `production_ready=true`、`customer_validated=true`、`marketplace_listed=true`。
