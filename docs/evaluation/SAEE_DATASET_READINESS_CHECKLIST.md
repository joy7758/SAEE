# SAEE Pilot Dataset Readiness Checklist v0.1

当前状态：`NOT_READY`。

只有以下条件全部有文件化证据时，未来数据集才可评估为 `READY`：

- [ ] **Source approved**：数据源已明确选择并获所有者批准。
- [ ] **Permissions clear**：许可、使用条款、同意范围和派生使用权限清晰。
- [ ] **Privacy review complete**：个人数据、敏感信息、最小化、访问、保留和删除均已审查。
- [ ] **Schema frozen**：四类 schema 已版本冻结，变更和迁移规则已确定。
- [ ] **Annotation protocol approved**：码本、双标、裁决和一致性目标已批准。
- [ ] **Validation pipeline tested**：结构、跨实体引用、泄漏与质量检查已在批准的合成 pilot 上测试。

当前六项全部未完成。存在 schema 文件只表示规范草案可验证，不表示 schema 已冻结；内存合成 smoke 不表示数据集存在或 validation pipeline 已完成 pilot 测试。

以下任一情况要求保持 `NOT_READY`：来源未选、权限不明、隐私审查未完成、schema 可变、标签协议未批准、validation pipeline 未测试。

