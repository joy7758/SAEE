# Rejected Options

Rejected Options（已拒绝方案）记录已经审查并否决的路线。拒绝原因的适用范围必须保留，
不得把局部否决扩大为永久禁止任何未来提案。

## R-001

方案：

直接合并 Agent Evidence 代码

状态：

REJECTED

原因：

整仓复制或直接合并会破坏产品、来源、许可证、runtime 和 marketplace 边界，并绕过
SAEE 现有能力复用与迁移门。

适用范围：

拒绝“无 provenance/schema crosswalk 的直接合并”，不禁止未来经过正式迁移门的逐项 adapt/migrate。

---

## R-002

方案：

SAEE 完全自我修改并批准自身变化

状态：

REJECTED

原因：

违反外部约束和授权分离原则。SAEE 可以评估变化，但不能从自己的评估产生提交、发布、部署或现实动作授权。

适用范围：

允许本地、只读、受控的 Dogfooding 评估；不允许自我授权。

---

## R-003

方案：

把治理无限扩展为项目目标

状态：

REJECTED

原因：

治理服务产品和演化闭环，不替代 Digital Biosphere Evolution Engine。无限治理扩张会把 SAEE 推回 audit-first framing。

适用范围：

不禁止必要的安全、历史真实性、回滚和 Agent-readable governance。

---

## R-004

方案：

直接把 `joy7758/SAEE` 作为 canonical remote

状态：

REJECTED

原因：

本地历史与公开仓库的 lineage 尚未建立，直接继承 canonical authority 会产生历史丢失和错误同步风险。

适用范围：

拒绝自动或直接指定。未来可以通过单独 lineage/recovery proposal、完整历史核对和人工授权重新评估 remote。

权威依据：

- `governance/decisions/ADR-0001-canonical-source.md`
