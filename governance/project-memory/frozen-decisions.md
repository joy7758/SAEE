# Frozen Decisions

Frozen Decisions（冻结决策）不得由 AI Agent 自行解除。任何变更必须按照
`memory-policy.md` 创建 Decision Change Proposal（决策变更提案）并获得明确人工确认。

## F-001

主题：

SAEE 与 Agent Evidence Receipt 的关系

状态：

FROZEN

决定：

Agent Evidence Receipt 在宪法架构层属于 `SAEE Evidence and Immune
Subsystem`（SAEE 证据与免疫子系统）。它不是简单插件，也不是与 SAEE 平行竞争的
完全独立产品；该归属不等于直接代码合并。

边界：

- 源仓库、Git 历史、许可证、runtime、public MCP 和 marketplace 状态继续保持独立，直到各自迁移门通过。
- `source_code_migrated=false`。
- `runtime_integrated=false`。
- 不得用架构归属替代来源、部署或运行证据。

禁止重新讨论：

不得在没有 Decision Change Proposal 的情况下重新提出“完全无关”或“立即整仓合并”路线。

权威依据：

- `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
- `governance/decisions/ADR-0002-agent-evidence-boundary.md`

---

## F-002

主题：

SAEE 最终三个客户版本

状态：

FROZEN

决定：

SAEE 与 Agent Evidence Project 完成受控合并后的最终客户版本固定为：

```text
SAEE Evidence
      ↓
SAEE Evaluation
      ↓
SAEE Governance
```

边界：

- 三个名称是目标产品族，不表示当前三个版本均已注册、实现或发布。
- `SAEE Governance` 是最终目标客户版本之一；当前 registry 尚未因此自动升级。
- 当前产品、subsystem 和 capability 事实仍以对应 registry 与 canonical inventory 为准。
- 不得由该目标推导 merge completed、customer validation、product launch 或 production readiness。

禁止重新讨论：

不得在没有新证据和 Decision Change Proposal 的情况下反复重建三个版本的数量、名称或主线定位。

权威依据：

- `governance/registry/product-registry.json`
- `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md`

---

## F-003

主题：

SAEE 自我治理原则

状态：

FROZEN

决定：

SAEE 可以评估自身变化，但不能批准自身变化。自用评估只能产生 decision context
（决策上下文），不能产生 execution authority（执行权力）或 release authority（发布权力）。

禁止重新讨论：

不得把 Dogfooding PASS、`CONTINUE` 或本地 validator PASS 自动升级为提交、发布、部署或外部动作授权。

权威依据：

- `reports/dogfooding/SAEE_DOGFOODING_PHASE0_5_1_REPORT.md`
- `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`

---

## F-004

主题：

治理与主线/产品关系

状态：

FROZEN

决定：

治理服务产品演化，不能把监督、测试或治理本身提升为项目主线。`SAEE Governance`
可以是三个最终客户版本之一，但它不是全部 SAEE，也不得取代“SAEE 与 Agent
Evidence 受控合并”的主线。治理层必须强化 Evolutionary Archive / Rollback Immune
System（演化档案 / 回滚免疫系统），同时保留 Digital Biosphere Evolution Engine
（数字生物圈进化引擎）的工程核心。

禁止重新讨论：

不得把 SAEE 重构为 audit-first system（审计优先系统）或只有治理副线的纯治理平台。

权威依据：

- `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
- `governance/README.md`

---

## F-005

主题：

Agent Evidence 不直接合并代码

状态：

FROZEN

决定：

SAEE 与 Agent Evidence Project 通过版本化契约、schema crosswalk、adapter 和明确
边界连接。迁移前先复用现有 SAEE canonical capabilities；禁止整仓复制或建立平行
receipt stack。

边界：

- 必须先通过 source provenance、license、compatibility 和 schema crosswalk 门。
- 只能逐项决定 `reuse / adapt / migrate / deprecate`。
- 当前不迁移代码、不集成 runtime、不改变 MCP。

禁止重新讨论：

不得以目录相邻、品牌归属或共同 host 作为直接代码合并依据。

权威依据：

- `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
- `governance/decisions/ADR-0002-agent-evidence-boundary.md`
