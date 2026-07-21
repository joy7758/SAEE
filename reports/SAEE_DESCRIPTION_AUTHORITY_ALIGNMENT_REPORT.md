# SAEE Description Authority Alignment Report

```text
phase=6.0-F1
report_type=Description_Authority_Alignment_Analysis
review_mode=READ_ONLY_ANALYSIS_WITH_REPORT_ONLY_OUTPUT
analysis_date=2026-07-15
active_constitution=SAEE Development Constitution v1.1
```

## Executive Decision

SAEE 已经具有可用的能力事实真源，但尚未形成清晰、全仓一致的“描述权威图”。当前
核心能力事实没有分裂：
`capability-package/manifest.json#canonical_inventory` 仍是唯一能力事实源，两个现行
公开本地操作仍为 `saee.evaluate_agent_run` 与 `saee.evaluate_evidence`。规范 MCP 运行面
也仍只暴露这两个只读工具。

真正的问题发生在投影层：根 `README.md`、`llms.txt`、`agent-index.json`、旧 public
discovery 文件、Capability Package 兼容合同、release/交付快照与历史 docs 同时保留了
不同阶段的命名、定位和入口。它们各自多半能追溯到真实历史，但没有统一、机器可判定
的 section-level（分段级）权威标签。Agent 若只读取其中一个深层或旧入口，可能把兼容
ID、内部 Tool 或历史产品名误判为当前公开能力。

因此本阶段结论不是“重写全部描述”，也不是“另建一个总描述真源”，而是：

> 建立分域唯一权威、单向投影、历史不可反向覆盖的 Description Authority Map；在
> Phase 6.0-F2 由人工审核一个最小 allowlist，优先修复当前发现入口和现行投影，保留
> 历史 lineage，不做全仓批量改写。

```text
DESCRIPTION_AUTHORITY_MODEL=SCOPED_CANONICAL_SOURCES_WITH_ONE_WAY_PROJECTIONS
CANONICAL_CAPABILITY_FACT_INTEGRITY=PASS
CURRENT_PROJECTION_ALIGNMENT=PARTIAL
HISTORICAL_DESCRIPTION_DRIFT=HIGH
CURRENT_AGENT_MISREAD_RISK=MEDIUM_HIGH
SECOND_CAPABILITY_SOURCE_DETECTED=false
MAINLINE_DRIFT_DETECTED=false
PROGRAM_MAINLINE_CHANGED=false
```

本分析是受控集成主线的 Agent-readable 支撑治理，不替代或提升为项目主线。Phase
6.0-F 先前发现的 `MAINLINE_DRIFT_DETECTED` 及其纠正继续有效：描述优化只能支持
`SAEE Evaluation` 和 SAEE / Agent Evidence Project 受控集成，不能成为新的全局核心。

## 1. Scope, Method and Truth Boundary

### 1.1 本阶段执行范围

本阶段只创建本报告。没有修改 Constitution、Project Memory、capability manifest、
schema、MCP、代码、README、`agent-index.json`、`llms.txt`、Product Registry 或任何
现有文件；没有执行迁移、功能扩展、外部集成、发布或 Git 写入动作。

### 1.2 读取与检索方法

审查按以下顺序进行：

1. 读取 v1.1 Constitution、governance 入口与 Codex rules，确定身份、主线和事实边界；
2. 读取 Phase 6.0-F 与 Phase 6.0-E2 报告，保留已经验证的 Agent 误判证据；
3. 读取 `manifest#canonical_inventory`、governance registries、规范 schemas、当前 MCP
   adapter、`.mcp.json`、`agent-index.json#capability_progress_ledger_v1` 与 `llms.txt`；
4. 枚举全部 README、`docs/` 与 `scripts/` 路径，执行 capability ID、产品定位、
   Non-Claims 和 MCP 关键词扫描；
5. 对命中当前/旧 ID、当前/旧产品定位、公开入口和 runtime 描述的文件进行定向读取；
6. 将“历史存在”“兼容别名”“当前投影冲突”分开判定，不从关键词计数直接推断冲突。

盘点规模：

| Scope | 文件数 | 审查方式 |
|---|---:|---|
| README 文件 | 142 | 全路径/标题盘点、全文关键词扫描、命中项定向读取 |
| `docs/` 文件 | 844 | 全路径盘点、全文关键词扫描、权威/产品/public/生态命中项定向读取 |
| `scripts/` 文件 | 995 | 全路径盘点、描述与 capability/MCP 关键词扫描、当前 runtime/validator 定向读取 |
| JSON Schema | 160 | 全路径盘点；现行两操作的四个 Qianfan request/response schema 定向读取 |

关键词命中只是发现信号。例如 `docs/` 中大量 `audit` 来自合法的证据审查、商业审查或
安全审查记录，不能据此认定 SAEE 被重新定位为 Audit Platform。只有当命中项位于当前
发现入口、没有历史/兼容标签，并与规范边界冲突时，本报告才将其认定为当前描述冲突。

### 1.3 本报告不建立新事实

本报告是评估证据，属于 Derived/Historical governance artifact，不是 capability、产品、
MCP 或 schema 真源。报告中的建议不能修改现行状态，也不授权 Phase 6.0-F2 执行更新。

## 2. Description Source Inventory

### 2.1 描述来源总表

| 来源 | 当前回答的问题 | 权威类别 | 责任边界 | 发现 |
|---|---|---|---|---|
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | SAEE 是什么、工程核心/主线/禁止事项是什么 | A — scoped canonical authority | 理论身份、工程核心、项目主线、系统级 Non-Negotiables | 现行权威；不承担逐项 capability 状态 |
| `governance/registry/product-registry.json` | 产品族、产品角色与 staged status 是什么 | A — scoped product fact | 产品注册表范围内的产品事实；不得成为 capability 源 | 当前目标族为 `SAEE Evidence / SAEE Evaluation / SAEE Governance`，并明确非 production |
| `capability-package/manifest.json#canonical_inventory` | 当前有哪些能力、状态、生命周期、route、claim/non-claim | A — canonical capability fact | 唯一能力事实源 | 完整且 validator 通过 |
| 现行 request/response JSON Schemas | 精确输入、输出、required、enum 与结构是什么 | A — canonical contract fact | 精确数据合同；不能自行改变 capability 身份或状态 | 四个现行 schema 与两个能力对应 |
| `governance/registry/mcp-registry.json` | MCP surface 的 canonical/compatibility/internal/legacy 分类是什么 | B — governance crosswalk | 分类与导航；必须服从 manifest，不是第二 MCP/capability 真源 | 分类清晰，现行规范面唯一 |
| `governance/registry/capability-crosswalk.json` | capability 如何映射 Layer/implementation/owner | B — governance crosswalk | crosswalk 明示 `crosswalk_is_capability_source=false` | 与 manifest 现行两项一致 |
| `saee_backend/services/qianfan_readiness_mcp_adapter.py#tool_definitions` | runtime 的 `tools/list` 实际给 Agent 什么名称、描述、schema | B — executable projection | 必须精确投影 manifest + schema；不能反向定义 capability | 现行两 Tool 对齐，有最小措辞缺口 |
| `scripts/saee_agent_readiness_mcp_stdio.py` | 如何启动规范本地 MCP | B/C — executable route | 规范启动 wrapper；可调用性须由 manifest + runtime 验证共同确认 | 当前规范 route |
| `.mcp.json` | Agent 客户端如何找到并启动 MCP | C — discovery/configuration hint | 连接配置，不包含 capability 描述 | 无描述冲突，不应塞入产品文案 |
| `agent-index.json#capability_progress_ledger_v1` | Agent 如何机器读取 capability 状态投影 | C — machine projection | status-only projection；不能复制描述或路线图作为事实 | 9/9 状态与 manifest 一致 |
| `agent-index.json` 其他区段 | 历史阶段、实验、产品与生态状态 | C/D — mixed projection/history | 只能按区段读取；不可把整文件当当前描述真源 | 存在旧 ID 和大量历史 `recommended_next_pr` |
| `llms.txt` 顶部规则/指针块 | LLM 从哪里开始读、使用什么规则 | C — discovery hint | 只维护 authority pointer、startup rule、duplicate-build rule | canonical pointer 正确；产品名/旧 front door 仍混杂 |
| `llms.txt` 其余区段 | 历史阶段和产物索引 | D — historical ledger/index | lineage 与检索；不得覆盖顶部规则或 manifest | 包含多个历史命名世代 |
| 根 `README.md` 顶部当前产品块 | 人和 Agent 如何快速理解现行外部能力 | B — derived description | 应从 Constitution、product registry、manifest 和 schema 派生 | 当前两 Tool 与 Non-Claims 正确 |
| 根 `README.md` 深层阶段记录 | 项目历史、实验、商业与交付记录 | D — embedded history | 同一文件内应明确与现行 front matter 分区 | 多世代定位和旧 front door 并存 |
| 其他 README、`docs/` | 人类、开发者、客户、生态的场景化解释 | B 或 D | 依文档日期、scope、status 和引用真源判定 | 当前文档与历史文档混合 |
| `.well-known/saee-capability-index.json` | repository-public discovery | C — discovery hint | 应只 route 到现行 canonical IDs，或明确标为 compatibility | 当前仍列两个旧 capability IDs |
| `agent-interface/public/saee-public-capability-surface.v0.1.json` | 旧 public capability surface | D — historical/compatibility | 不得作为当前 capability authority | 旧 ID + 当前 operation ID 混合 |
| `capability-package/mcp-tool.json` | Capability Package 内部/兼容 Tool 合同 | D/B — internal compatibility projection | 不属于规范 public MCP；必须显式保留 internal 身份 | 无 namespace 的三 Tool，包括 contract-only `rehearse_agent` |
| release、cloud handoff 与复制 README | 某一时间点的冻结交付/发布候选 | D — immutable snapshot | 保留快照 lineage；不得作为 live source | 复制了当时 README 和旧定位 |
| `reports/` | 某次审计、计划、验证的证据 | D — evidence/history | 描述当次输入和结论，不修改当前 capability | 不得作为 current lookup 起点 |

### 2.2 当前规范能力事实

`manifest#canonical_inventory` 当前明确：

| Capability ID | Implementation | Lifecycle | Canonical route | 核心 Non-Claims |
|---|---|---|---|---|
| `saee.evaluate_agent_run` | `implemented` | `active` | `scripts/saee_agent_readiness_mcp_stdio.py#saee.evaluate_agent_run` | trace 未认证；不授权部署；没有 public service/customer validation/production readiness |
| `saee.evaluate_evidence` | `implemented` | `active` | `scripts/saee_agent_readiness_mcp_stdio.py#saee.evaluate_evidence` | PASS 不证明真实事件；不是 authorization/certification/legal accountability；没有 public service/customer validation/production readiness |

规范 MCP 为 `saee.agent_readiness_mcp_stdio`，classification 为
`canonical_public`，stability 为 `alpha`，`publicly_deployed=false`。这里的
`public` 表示 public contract/audience，不表示公网部署。

### 2.3 精确输入输出归属

Capability Manifest 决定 capability 身份和 route；以下 schema 决定精确数据形状：

| Operation | Request required | Response required（摘要） |
|---|---|---|
| `saee.evaluate_agent_run` | `request_id`, `agent_id`, `task`, `trace`, `evidence`, `customer_data_included` | capability/operation、readiness、score semantics、required/present/missing evidence、risks、recommendation、limitations、truth boundary |
| `saee.evaluate_evidence` | `request_id`, `evidence_bundle`, `required_evidence_types`, `customer_data_included` | capability/operation、evidence quality、coverage score、required/present/missing evidence、reason codes、limitations、truth boundary |

因此“input/output 属于 Category A”不意味着复制 schema 到 manifest。正确关系是 manifest
持有规范 capability/route，schema 持有规范 shape，validator 验证两者连接；任何 README、
MCP description 或 Agent packet 都只能派生摘要。

## 3. Authority Ranking and Description Authority Map

### 3.1 第一性原理：不是一份万能文件，而是分域唯一权威

单一文件不应同时承载 theory identity、product status、capability inventory、schema、
runtime discovery、商业叙述和历史 lineage。否则任何小改动都会把不同生命周期绑在一起，
形成新的巨型真源。SAEE 应采用 scoped authority graph（分域权威图）：

```text
Constitution v1.1
  owns: theory identity / engineering core / mainline / non-negotiables
        |
        +--> Product Registry
        |      owns: product-family and product-state facts
        |
        +--> capability-package/manifest.json#canonical_inventory
               owns: capability IDs / status / lifecycle / routes / claims / non-claims
                         |
                         +--> JSON Schemas
                         |      own: exact request/response shape
                         |
                         +--> canonical MCP tools/list
                         |      projects: currently invocable local Tool surface
                         |
                         +--> agent-index ledger / .mcp.json / llms top
                         |      project: discovery and startup hints
                         |
                         +--> README / current docs / examples
                                project: human and Agent explanation

Historical reports / releases / copied handoff assets
  preserve lineage only; never flow upward into current facts
```

关键规则：每个事实域只能有一个 canonical owner；所有箭头单向向下；B/C/D 不得反向
覆盖 A；任何 crosswalk、report 或 generated packet 都不得被升级成第二 capability 源。

### 3.2 四类权威等级

| Category | 定义 | 允许内容 | 禁止行为 |
|---|---|---|---|
| A — Canonical Fact | 在明确 scope 内决定当前事实 | identity、product state、capability ID/status/route、schema shape | 不允许另一个 projection 覆盖；不允许跨 scope 冒充总真源 |
| B — Derived Description | 从 A 派生的解释或可执行投影 | README、产品文档、MCP Tool description、治理 crosswalk | 不得创造新 ID/status/claim；必须能追溯到 A |
| C — Discovery Hint | 帮 Agent 找到 A/B 或启动 runtime | `.mcp.json`、llms 顶部 pointer、agent-index status projection、`.well-known` route | 不得复制成独立事实；不得把 internal/historical route 写成默认 current route |
| D — Historical / Deprecated | 保留当时事实、实验或兼容 lineage | reports、release snapshot、旧 public surface、旧 product generation | 不得静默重写历史；不得无标签进入当前 discovery |

### 3.3 问题到权威的唯一映射

| Agent 问题 | 第一读取面 | 必要校验 | 非权威面 |
|---|---|---|---|
| SAEE 的最高身份/核心是什么？ | v1.1 Constitution | governance alignment | README slogan、历史产品文案 |
| 目标产品族/当前产品状态是什么？ | Product Registry | Constitution/staged-truth rules | 历史市场材料、单次报告 |
| SAEE 当前有什么 capability？ | `manifest#canonical_inventory` | canonical inventory validator | README、llms 详情、agent-index 历史块 |
| capability 的 input/output 是什么？ | manifest route 指向的规范 schema | schema/runtime smoke | prose example、旧 OpenAPI/package contract |
| 当前规范 MCP 能调用什么？ | manifest canonical MCP surface + runtime `tools/list` | exact tool count/name/schema conformance | `.mcp.json` 文本、旧三 Tool package、legacy MCP |
| Agent 如何发现/启动？ | `.mcp.json` + manifest canonical route | 本地 initialize/tools-list smoke | 历史 `agent-manifest` front door |
| 人类如何理解？ | 当前 README front matter / current product doc | 追溯 manifest/registry/Constitution | 历史报告或复制 README |

## 4. Conflict Detection

### 4.1 总体冲突矩阵

| ID | 冲突类型 | 严重度 | 证据 | 判定 |
|---|---|---:|---|---|
| DESC-001 | Capability ID 冲突 | HIGH | `.well-known`、旧 public surface、public quickstart 仍列 `saee.agent-reliability` / `saee.evidence-evaluation`；历史还含 `saee.evidence-adequacy` 与无 namespace 名称 | 对当前 discovery 构成真实歧义；作为 manifest alias/history 本身不构成第二事实 |
| DESC-002 | Public/Internal Tool 混淆 | HIGH | 规范 MCP 是两个 namespaced Tool；`capability-package/mcp-tool.json` 是三个无 namespace Tool，含 contract-only `rehearse_agent` | internal 分类在 manifest/registry 中正确，但直接读取旧合同的 Agent 可能误判为当前 public surface |
| DESC-003 | 产品定位世代冲突 | MEDIUM-HIGH | 当前出现 `Agent Readiness Capability`、`Agent Readiness Platform`、`Agent Readiness Assessment`、`Agent Reliability Capability Layer`、`Agent Reliability Framework` | 其中部分是 product/offer/layer 的合法不同 scope，但多数入口缺少 scope/date/status 标签，Agent 无法稳定区分 |
| DESC-004 | 当前 front door 冲突 | HIGH | manifest/`.mcp.json` 指向规范两 Tool route；README/llms 仍称 `agent-interface/agent-manifest.json` 为 canonical front door，而该文件列出 `describe_saee`、`compare_observed_traces` 等旧 surface | 这是当前入口级冲突，不应继续让 `canonical` 一词同时指向两套不同用途的入口 |
| DESC-005 | README 内部时态冲突 | MEDIUM-HIGH | README 顶部是当前 Capability/两 Tool；深层保留 Platform、Reliability Layer、旧 MCP、历史阶段与复制式长 ledger | 人类可借上下文理解，检索 Agent 可能只命中旧片段并当成当前事实 |
| DESC-006 | `llms.txt` 混合权威 | MEDIUM-HIGH | 顶部 canonical capability pointer 正确；同一文件又含旧产品名、旧 front door 和大量历史阶段叙述 | section-level pointer 正确但 whole-file authority 不成立 |
| DESC-007 | `agent-index.json` 混合权威 | MEDIUM | ledger 投影 9/9 一致；其他区段含旧 ID 和历史 `recommended_next_pr` | 只允许 `#capability_progress_ledger_v1` 作为 status projection；整文件不能当 capability 描述源 |
| DESC-008 | Non-Claims 可见性不一致 | MEDIUM | manifest、当前 product doc、root front matter 与 MCP initialize 均保持不授权；但旧/短 discovery 条目不总是同时写明不执行、不保证、不认证 | 未发现规范 active surface 的肯定式授权/认证主张；风险是遗漏边界造成过度推断，而非 canonical claim 已冲突 |
| DESC-009 | MCP 描述精度缺口 | MEDIUM | runtime 两 Tool ID、tool count、read-only annotations 和 non-authorization 均对齐；description 仍偏 deployment-specific，未直接呈现 input 缺失时 abstain 及负路由 | 是 selection wording gap，不是 capability 或 runtime 行为冲突 |
| DESC-010 | Audit/Security/Trust 关键词误报风险 | LOW-MEDIUM | docs/scripts 存在大量 audit/security 词，但大多描述审查动作或明确 Non-Claims | 不得批量替换；仅处理把 SAEE 本身肯定定位成 scanner/certifier/authority 的当前入口，当前未发现这种 active canonical 声明 |

### 4.2 Capability Naming

当前唯一规范操作名：

```text
saee.evaluate_agent_run
saee.evaluate_evidence
```

以下名称必须按不同角色处理：

| 名称 | 当前角色 | 是否可作为当前 public capability ID |
|---|---|---|
| `evaluate_agent_run` | exact alias / internal package operation | NO |
| `evaluate_evidence` | exact alias / internal package operation | NO |
| `saee.evidence-evaluation` | manifest 中的 compatibility alias | NO |
| `saee.evidence-adequacy` | manifest 中的 compatibility alias | NO |
| `saee.agent-reliability` | 旧 package/product capability identity，不是 canonical inventory current operation | NO |
| `rehearse_agent` / `saee.rehearse_agent` | internal contract-only / canonical inventory `design_only`, `experimental` | NO |
| `describe_saee` / `compare_observed_traces` | legacy internal MCP | NO |

Alias 的存在用于 deterministic resolution，不等于允许 discovery surface 把 alias 与 canonical
ID 并列成两个当前能力。当前 `.well-known` 与旧 public surface 正在制造这种歧义。

### 4.3 Product Language

需要先分层，而不是选一个词覆盖全部：

| Scope | 应服从的事实 | 当前风险 |
|---|---|---|
| Theory Identity | `Silicon-Amplified Evolutionary Ecology` | 不得被 Trust、Reliability 或 Readiness 反向取代 |
| Engineering Core | `Digital Biosphere Evolution Engine` | 不得被 audit/evaluation 产品投影取代 |
| Target Product Family | `SAEE Evidence / SAEE Evaluation / SAEE Governance` | 是 target，不是已发布/已生产 |
| Current external capability projection | 当前 root/current product doc 使用 `SAEE Agent Readiness Capability` | 与旧 `Platform`/`Reliability Layer` 缺少清晰 successor/compatibility 关系 |
| First offer/service language | `Agent Readiness Assessment` 等商业交付名 | 不能反向成为 capability ID 或项目最高身份 |

`docs/product/SAEE_PRODUCT_IDENTITY_V1.md` 自称 frozen external brand
`SAEE Agent Readiness Platform`，而更新的 root/current capability doc 使用
`SAEE Agent Readiness Capability`。Product Registry 又以 `SAEE Evaluation` 描述当前本地
两操作投影。这不是简单拼写问题，而是 product generation/scope 没有机器可读 successor
关系。Phase F2 必须先由人工确定 current external label、offer label、target-family label
各自的 scope，再改入口，不能由 Codex 任选一个词全仓替换。

### 4.4 Non-Claims

当前规范事实保持以下边界：

- 不授权部署、付款、发送、权限扩大或任何外部行动；
- 不执行外部世界；
- 不认证 trace、Evidence 来源或真实事件；
- 不提供安全/合规认证、法律责任结论或可靠性概率保证；
- local/synthetic/alpha/package-ready 不等于 public deployment、customer validation 或
  production readiness；
- 不替代 IAM、Policy、Observability、Security Scanner 或 Execution Platform。

当前 canonical manifest、规范 MCP initialize instruction、当前 product doc 与 root 顶部
没有发现肯定式授权、保证或认证冲突。真正缺口是短 description/discovery hint 没有稳定
携带最小 Non-Claims，导致 Agent 可能从 `readiness`、`CONTINUE`、`SUFFICIENT` 或
`reliability` 推导出越权含义。

### 4.5 MCP Surface

现行 runtime 投影结论：

```text
canonical_surface=saee.agent_readiness_mcp_stdio
public_tool_count=2
tool_ids_exact=true
read_only_annotations=true
deployment_authorization=false
publicly_deployed=false
```

`.mcp.json` 只配置启动命令，不负责 capability description。规范 runtime 的两条 description
与 manifest 语义一致，但比 Phase 6.0-E2/F 的 selection rule 更短：没有直接说“缺少
required trace/evidence 时不要调用”，也没有对 Customer policy/send 和 Procurement
purchase authority 提供负路由。这是 F2 可评审的 description-only 候选，不授权改变 Tool
数量、schema、transport、permissions 或行为。

## 5. Historical Drift Analysis

### 5.1 漂移世代

| 历史世代/表面 | 当时语言 | 当前处理 |
|---|---|---|
| Evidence Adequacy research | `saee.evidence-adequacy`, `evaluate_evidence_adequacy` | 保留 lineage；作为 alias/internal implementation reference，不作为 public ID |
| Reliability package/framework | `saee.agent-reliability`, `Agent Reliability Framework`, 无 namespace package operations | 标记 historical/internal compatibility；不得覆盖 current two-tool surface |
| Public capability v0.1 | `saee.agent-reliability` + `saee.evidence-evaluation` | 当前 discovery 不应继续将二者列作 canonical capability IDs |
| Legacy observed-trace MCP | `describe_saee`, `compare_observed_traces`, `compare_candidates` | 保留 internal legacy；不得称为 current canonical Agent front door |
| Readiness Platform productization | `SAEE Agent Readiness Platform` | 需要人工决定其与 current Capability、Assessment、`SAEE Evaluation` 的 scope/successor 关系 |
| Reliability Capability Layer ecosystem strategy | `Agent Reliability Capability Layer` | 保留历史策略证据；当前入口不得无标签复用 |
| Current Readiness Capability | `SAEE Agent Readiness Capability` + 两个 namespaced operations | 当前最清晰的外部 capability projection，但仍需与 Product Registry/旧 frozen brand 对齐 |

### 5.2 为什么历史不能直接删除或重写

旧 ID、旧产品名和旧实验描述证明了 SAEE 的演化路径，也被 release、report、test、schema
和外部材料引用。批量重写会破坏：

- Git/history 与 artifact digest 的可解释性；
- historical report 在当时输入下的真实性；
- release/cloud handoff snapshot 的可复现性；
- alias、migration 和 caller identification 所需的 lineage；
- Agent 判断“当前事实”和“历史事实”的能力。

正确做法是给当前入口建立 canonical pointer、给旧入口增加 machine-readable
`historical/compatibility/internal` disposition 或 successor route；不是把所有旧字符串替换为
新字符串。

## 6. First-Principles Check

### 6.1 为什么必须统一描述权威

Agent 的决策链不是“阅读一段广告语”，而是：发现 -> 选择 -> 组装 input -> 调用 -> 解释
output -> 决定是否继续。当不同入口对 identity、Tool、input 或 authority boundary 给出不同
答案时，错误会沿整条链传播。统一的目标不是每个文件逐字相同，而是每个事实只有一个
owner，所有投影都可验证地指回 owner。

### 6.2 不统一会造成什么 Agent 误判

| 误判 | 触发源 | 后果 |
|---|---|---|
| 调用不存在或非公开的 Tool | 旧三 Tool MCP、legacy `agent-manifest` | invocation failure，或误入 internal contract |
| 把 alias 当成另一项 capability | `.well-known`/public v0.1 旧 ID | 重复建设、重复注册或错误 compose |
| 把 Evidence coverage 当可靠性概率/安全证明 | Reliability/Trust 类旧产品语言 | 过度信任 output，越过独立授权门 |
| 输入不足仍调用 | 短 MCP description 未写 abstention | Customer 场景式 selection error，产生无意义评估 |
| 把 `CONTINUE`/`SUFFICIENT` 当允许执行 | Non-Claims 在短入口不可见 | 付款、发送、部署等权威混淆 |
| 把 local alpha 当 public integration | public contract、public surface、marketplace material 混读 | 虚假 external/production claim |
| 把 Readiness 产品投影当 SAEE 最高身份 | Platform/Capability 文案脱离 Constitution | 项目重新滑向 evaluation/audit-first framing |

Phase 6.0-E2 已提供真实证据：单一 Codex Agent family 在 canonical packet 条件下总体
`PASS_WITH_LIMITATIONS`，但 Customer 场景在承认输入不足时仍选择了
`saee.evaluate_agent_run`，Procurement 场景的排除也不够坚决。这支持“描述选择摩擦存在”，
不支持“能力有缺陷”或“全生态 discoverability 已验证”。

### 6.3 最小需要修复什么

最小修复不是扩展 capability，而是按优先级闭合四个入口歧义：

1. **Current lookup pointer**：让 current README/llms discovery 只把
   `manifest#canonical_inventory` + `.mcp.json`/规范 MCP route 称为当前能力入口；旧
   `agent-manifest` 明确降为 legacy/internal front door。
2. **Canonical ID routing**：`.well-known` 和 current public discovery 只输出两个规范
   operation ID，或将旧 capability IDs 明确标为 compatibility aliases 并给 successor。
3. **Product scope labels**：由人工冻结 Theory/Core/target family/current capability/offer
   五个 scope，解决 Capability、Platform、Assessment、Reliability Layer 的无标签并存。
4. **Selection boundary**：只在获批的 manifest/current product doc/MCP description 投影中
   补足 required-input abstention、Customer/Procurement negative routing 和最小 Non-Claims。

不需要新 capability、新 schema、新 MCP、新 manifest、新 product、批量历史重写或大规模
README 重构。

## 7. Update Rules

### 7.1 未来每次描述变更的判定顺序

任何描述更新前必须依次回答：

1. **Scope**：这是 theory、product、capability、schema、runtime、discovery 还是 history？
2. **Category**：A/B/C/D 哪一类？
3. **Owner**：该 scope 的 canonical owner 文件是什么？
4. **Fact or wording**：是否改变 ID、status、lifecycle、input/output、route、claim/non-claim？
5. **Duplication**：仓库是否已有等价字段、文档、Tool 或 route？
6. **Staged truth**：是否把 local/synthetic/package/review/public/production 混成一个状态？
7. **Non-Claims**：是否保持不授权、不执行、不保证、不认证及相邻系统边界？
8. **Projection set**：哪些被批准的 B/C 投影必须由 A 同步，哪些历史 D 必须保持不动？
9. **Validation**：什么离线 validator 能证明 A 与投影仍一致？

### 7.2 谁可以修改什么

| 角色 | 可做 | 不可做 |
|---|---|---|
| Human constitutional/product authority | 批准 identity/product generation、F2 allowlist 和 consequential public wording | 不能让报告或角色提示绕过 Constitution/事实证据 |
| Canonical fact maintainer（经明确授权） | 先修改对应 A 类 owner，再同步获批投影 | 不得在 README/llms/MCP description 先创造事实 |
| Runtime/MCP maintainer（经明确授权） | 使 `tools/list` 名称、schema、description 符合 manifest/schema | 不得增加 Tool、扩大权限或把 runtime 变成 capability authority |
| Documentation/discovery maintainer（经明确授权） | 从 A 派生 B/C，加入 source pointer、scope、status、as-of/successor | 不得改 status、删除 lineage、把旧 alias 宣称为 current |
| Validator | fail closed 检查 tool count、IDs、routes、schema、projection、Non-Claims | 不得自行批准语义或修改事实 |
| Report/release owner | 保留当时证据与 hash | 不得把历史 snapshot 当 live source，也不得静默重写 |

所有角色均指职责，不代表当前已经指派个人，也不构成本报告对任何修改的授权。

### 7.3 Canonical-first 规则

- 若 capability 事实变化：先改 `manifest#canonical_inventory`，同一 change 同步必要的
  schema/runtime/ledger/current docs，并运行 canonical/ledger validators。
- 若只是 wording：不得改 status/ID/schema；仍须证明 wording 可从 manifest/schema 推导。
- 若 MCP description 变化：它是代码中的 runtime projection，必须通过 exact
  `initialize`、`tools/list`、input/output schema 与 two-tool smoke。
- 若 authority pointer/startup rule 变化：才允许改 `AGENTS.md` 或 `llms.txt` 顶部规则块。
- 若 agent-index capability facts 变化：只同步
  `agent-index.json#capability_progress_ledger_v1`；不得把 description 或 roadmap 复制进去。
- `.mcp.json` 只在启动 route/config 变化时修改，不用于存放产品描述。
- D 类历史文件不原地“现代化”；使用 successor/deprecation/disposition metadata 或当前入口
  redirect。

## 8. Safe Future Modification Path

### Gate F2-0 — Human scope decision

人工先审查并冻结：

- current external capability label；
- Platform/Capability/Assessment/`SAEE Evaluation` 的 scope 关系；
- 当前 Agent front door；
- 是否允许修正 `.well-known`/public discovery；
- 是否允许仅更新 MCP description string；
- exact file allowlist 与明确 denylist。

在此 gate 前：`DESCRIPTION_UPDATE_AUTHORIZED=false`。

### Gate F2-1 — Isolated baseline

在干净、隔离、可回滚的 baseline 上记录 HEAD、branch、input hashes、status snapshot 和
rollback reference。不得“清理”当前 dirty worktree，也不得把既有用户变更纳入描述更新。

### Gate F2-2 — Current-surface patch only

候选最小更新顺序：

1. 先确认 A 类 facts 不变；
2. 修正 current discovery pointer 与旧 front door disposition；
3. 修正 current public discovery 的 canonical ID routing；
4. 对获批 current product/README/MCP description 增加一致 selection/non-claim wording；
5. 不修改历史 report、release、copied handoff README、旧 experiment result；
6. 不新增 capability、schema、MCP surface、代码行为或外部 claim。

该列表是 review candidate，不是执行 allowlist。F2 必须给出 exact paths 后才可能授权。

### Gate F2-3 — Conformance validation

至少验证：

- manifest canonical inventory 9/9 与 ledger 9/9；
- canonical MCP 仍恰好两个 namespaced Tool；
- four request/response schemas 未漂移；
- `.mcp.json` 仍只指向规范 wrapper；
- current README/product/MCP 对 scope、input precondition、abstention、Non-Claims 一致；
- old IDs 只能作为 alias/history/internal 出现，不能作为 current public canonical ID；
- local/public/customer/production staged truth 未升级；
- 多 Agent/provider discoverability 必须是另行授权实验，不能由字符串更新自动宣称通过。

### Gate F2-4 — Human acceptance

Human reviewer 对 diff、validator 证据、历史保留与 rollback 点作出接受决定。未通过时只回滚
F2 allowlist 内的变更，不触碰 v1.1 history、Evidence lineage 或当前 capability truth。

## 9. Risks and Guardrails

| 风险 | 当前等级 | Guardrail |
|---|---:|---|
| 新建“描述总表”成为第二 capability source | HIGH | 只建立 pointer/rule，不复制 live facts；validator 检查 source role |
| 全仓替换旧词破坏历史 | HIGH | D 类 immutable；只加 disposition/successor 或修 current route |
| current product name 未经人工选定就由 Codex 冻结 | HIGH | F2-0 human decision required |
| runtime description 改动意外改变 Tool/schema/behavior | MEDIUM-HIGH | exact file allowlist + MCP smoke + diff review |
| `agent-index`/`llms` 大规模同步造成巨型真源 | HIGH | 只按 section role 修改；ledger status-only，llms top pointer-only |
| `public_contract=true` 被误读成公网部署 | MEDIUM-HIGH | 每个 current public discovery 携带 `publicly_deployed=false` |
| audit/security 关键词机械清洗改变合法证据语义 | MEDIUM | context-based review，禁止 blanket replacement |
| 当前 dirty worktree 混入 F2 | HIGH | isolated baseline、pre/post hash、report-only current phase |

## 10. Input Integrity and Baseline

关键输入 SHA-256：

| Input | SHA-256 |
|---|---|
| `reports/SAEE_AGENT_CAPABILITY_DESCRIPTION_OPTIMIZATION_PLAN.md` | `96b64dcd635df90627714f06c4174d2bd433207a4821bb32f32a4fee9d0b63db` |
| `reports/SAEE_AGENT_DISCOVERABILITY_EXECUTION_REPORT.md` | `3c390b92332f64834b966c21885d245eb23fb12bf61e08cffd66fa7fd7c0a4ba` |
| `capability-package/manifest.json` | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` |
| `agent-index.json` | `1ac0a832019d48dd3f40ef7f594c96938d9394f793fee8de06d1d8a429c61740` |
| `llms.txt` | `e73c61c1bec1282f49ab5f012f77ae83e195b0a19d3688e5e2c90f036b971e07` |
| `.mcp.json` | `b14e0dc3565840095584810974a8337f5debb1c757b47ebf8f58247eca6f80e2` |
| `README.md` | `20c727ac05fe7b17c1b82d25525b29d7efdf412b45abf74062a044ce6289e711` |
| `docs/CAPABILITY_INVENTORY.md` | `327f834192476f930ce1b4c8ba14c9397349afd3b9540643a2876ef83846df5c` |
| `docs/product/SAEE_AGENT_READINESS_CAPABILITY_V2.md` | `0c0696a080d295b24f9a3a67714a2c292ac87df9e98baa677a10cb2cf6371d3b` |
| `governance/registry/product-registry.json` | `62c9ee638a4e763e60d2290cdf6fa2bbeabf93373ced8fa4af084203146a316d` |
| `governance/registry/mcp-registry.json` | `fdeda93c44104c61efcdcea2ea2703a919630a68b2af96b12438d45834258a76` |
| `saee_backend/services/qianfan_readiness_mcp_adapter.py` | `0203087c1e26c2a7c7cca28f5f2c5ffb4a7069d52c7c9b2b9adecf7ca5a06c86` |

工作区基线：

```text
HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
BRANCH=feat/canonical-capability-inventory-routing-v1
BASELINE_STATUS_ENTRIES_ALL_FILES=102
BASELINE_STATUS_SHA256=fe5b03a3518d5507a239a339e9d662af804bc8a68d8c21085b73eaab3da9c7b2
BASELINE_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
BASELINE_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
TARGET_REPORT_EXISTED_AT_BASELINE=false
```

当前工作区已有 102 条非本阶段状态。本阶段不清理、不吸收、不解释这些用户/既有变更；
以排除新报告后的 status 与 staged/unstaged patch hash 不变作为边界证据。

## 11. Validation

全部规定项及两项附加 capability 一致性检查通过：

| Command | Result |
|---|---|
| `python3 scripts/saee_project_memory_check.py` | PASS — `files=8/8`, `v2_principles=3`, `capability_fact_source_unchanged=true`, `production_ready=false` |
| `python3 scripts/saee_governance_registry_check.py` | PASS — `registries=6/6`, `schemas=4/4`, `capabilities=9`, `mcp_entries=5`, canonical MCP=`saee.agent_readiness_mcp_stdio`, `production_ready=false` |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS — `negative_cases=7/7`, `evolution_subsystems=9/9`, program mainline preserved, `audit_first_reframe=false`, `production_ready=false` |
| `python3 scripts/saee_canonical_capability_inventory_smoke.py` | PASS — `capabilities=9/9`, `mcp_surfaces=4/4`, canonical public MCP=`1/1`, `negative_cases=16/16`, public endpoint=`false` |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS — `surfaces=6/6`, `capability_statuses=9/9`, `duplicate_build_prevention=true`, `production_ready=false` |
| `git diff --check` | PASS |
| new report no-index whitespace check | PASS |

工作区边界复核：

```text
FINAL_STATUS_ENTRIES_ALL_FILES=103
FINAL_STATUS_ENTRIES_EXCLUDING_NEW_REPORT=102
FINAL_STATUS_EXCLUDING_NEW_REPORT_SHA256=fe5b03a3518d5507a239a339e9d662af804bc8a68d8c21085b73eaab3da9c7b2
FINAL_STAGED_PATCH_SHA256=31ad98d051bbfa53ce3b5d00f78f896e808dc1c0d3ee4ac62d67a1027d4bae7f
FINAL_UNSTAGED_PATCH_SHA256=d44ecf7871a1816fc9c1f9c203bb9e0a664638e54c5666ad8090643c8ef3ff1a
ONLY_NEW_TASK_PATH=reports/SAEE_DESCRIPTION_AUTHORITY_ALIGNMENT_REPORT.md
TARGET_REPORT_TRACKED=false
STAGED_TASK_FILES=0
TASK_CREATED_FILE_COUNT=1
TASK_MODIFIED_EXISTING_FILE_COUNT=0
```

排除唯一新报告后，status、staged patch 与 unstaged patch hash 均与基线一致。这证明本阶段
没有吸收或修改现有 102 条工作区状态；唯一新增路径保持 untracked，未执行 `git add`。

## 12. Final Status

`DESCRIPTION_AUTHORITY_ALIGNMENT_STATUS=COMPLETE` 表示本阶段分析报告完整，不表示描述已
更新或 F2 已授权。`FILES_MODIFIED=false` 按本任务约定表示没有修改任何预先存在的文件；
本阶段唯一 filesystem output 是新增本报告。

```text
DESCRIPTION_AUTHORITY_ALIGNMENT_STATUS=COMPLETE
DESCRIPTION_AUTHORITY_CURRENT_ALIGNMENT=PARTIAL
DESCRIPTION_UPDATE_AUTHORIZED=false
CANONICAL_CAPABILITY_SOURCE=capability-package/manifest.json#canonical_inventory
CANONICAL_CAPABILITY_SOURCE_UNCHANGED=true
SECOND_CAPABILITY_SOURCE_CREATED=false
REPORT_CREATED=true
EXISTING_FILES_MODIFIED=false
FILES_MODIFIED=false
CAPABILITY_CHANGED=false
MCP_CHANGED=false
CODE_CHANGED=false
SCHEMA_CHANGED=false
CONSTITUTION_CHANGED=false
PROJECT_MEMORY_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
AGENT_INDEX_CHANGED=false
LLMS_TXT_CHANGED=false
README_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
NEXT_ACTION=HUMAN_REVIEW_OF_DESCRIPTION_AUTHORITY_ALIGNMENT
```
