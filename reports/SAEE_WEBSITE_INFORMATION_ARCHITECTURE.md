# SAEE Website Information Architecture

中文名称：SAEE 网站信息架构<br>
版本：`v1.0`<br>
目标域名：`https://redcrag.cn/`<br>
阶段：`PHASE_1_CATEGORY_POSITIONING`

```text
WEBSITE_ROLE=CATEGORY_ENTRY_AND_TRUTHFUL_ECOSYSTEM_FRONT_DOOR
WEBSITE_IS_PRODUCT_RUNTIME=false
WEBSITE_DEPLOYMENT_IS_PRODUCT_LAUNCH=false
CURRENT_FUTURE_SEPARATION_REQUIRED=true
GOAL_INTEGRITY_SECONDARY_LANE=STOPPED
```

## 1. 网站任务

网站首要任务不是展示软件功能，而是在访问者进入后 30 秒内完成三个认知动作：

1. 理解企业 Agent 正从短任务走向长期、多 Agent、自主运行；
2. 理解新的基础设施缺口是身份、证据、状态、记忆和责任无法长期连续；
3. 理解 SAEE 正在建设这一方向，但当前只实现了受限 Evidence / Evaluation 能力。

网站必须同时服务人类访问者和检索/编码 Agent。人类首页负责类别理解，机器可读表面负责精确能力事实与调用边界。

## 2. 视觉与交互原则

参考 `agenttrust.io` 的可借鉴原则，而不是复制其品牌、文案或产品主张：

- 白色/浅中性色背景，深色正文与单一绿色强调色；
- 首屏采用“类别标签 + 一句话问题 + 简洁解释 + 双 CTA + 证据卡”；
- 使用边框、留白、圆角卡片和紧凑 monospace 状态标签；
- 一屏只解释一个主要关系；
- 用可读的 system diagram 代替装饰性插画；
- CTA 指向 Whitepaper、Architecture 和 GitHub，不假装已有 trial 或 production platform；
- 避免当前站点的大面积营销渐变、夸张产品推荐和未分层的能力堆叠。

SAEE 自有视觉建议：

- 主色：`trust green`，用于 future category 和关键关系；
- 深色：近黑绿色，用于架构、状态与 footer；
- 中性色：白、浅灰绿、细边框；
- 状态色：Current Capability 使用深绿色；Future Direction 使用浅绿色/虚线；Missing 或 Not Implemented 使用琥珀色；
- 图形语言：continuity line、state transition、identity node、evidence receipt；
- 禁止把 future node 画成已连接、已运行或已通过的 production topology。

## 3. 顶级导航

```text
Why Trust Infrastructure
Architecture
Current vs Future
Whitepaper
Ecosystem
Developers
```

中文站点显示：

```text
为什么需要
可信架构
当前与未来
白皮书
生态入口
开发者
```

主要 CTA：`阅读白皮书大纲`<br>
次要 CTA：`查看 GitHub`<br>
边界 CTA：`查看当前能力`

不使用 `开始试用`、`立即购买`、`企业级已就绪` 等缺乏当前证据的 CTA。

## 4. Homepage 信息顺序

### H1 — Category Hero

Eyebrow：`MULTI-AGENT LONG-RUNNING TRUST INFRASTRUCTURE`

主标题：

> 让企业不只部署 Agent，<br>
> 还能够长期信任它们。

说明：

> 当 Agent 开始长期运行、彼此协作并持续改变状态，企业需要一层基础设施来连接身份、执行证据、状态连续性与治理。SAEE 正在建设这一方向。

Hero truth chips：

- `Future infrastructure direction`
- `Current evidence evaluation is bounded`
- `Not production ready`

Hero visual：`Trust Continuity Record`，展示 Identity、Goal、State、Memory、Evidence、Responsibility 六个字段，其中 Current/Future 状态清晰可见。

### H2 — The Shift

标题：`Agent 已经从工具变成长期运行的行为主体。`

三列：

1. Long-running：任务跨越会话、进程和时间；
2. Multi-agent：handoff 与 delegation 传播目标和权限；
3. Autonomous：系统可以在较少人工介入下持续行动。

### H3 — The Enterprise Trust Gap

标题：`真正的阻力不是 Agent 不会做，而是企业无法持续证明它仍应该做。`

六个问题卡：Identity、Goal、State、Memory、Evidence、Responsibility。

### H4 — Why Existing Layers Are Not Enough

四列责任边界：

- Framework：organize execution；
- Observability：show signals；
- IAM：grant access；
- SAEE future direction：interpret continuity and evidence relationships。

固定说明：`SAEE composes with these layers. It does not replace them.`

### H5 — Future Architecture

主链：

`Agent Identity → Execution Evidence → State Continuity → Multi-Agent Governance → Trust Decision Context`

每个节点标记 `Future Direction`。如果展示当前能力，只能在 Execution Evidence 下显示一个独立的 `Current bounded local evaluation` 标签。

### H6 — Current Capability / Future Direction

左右双栏：

| Current Capability | Future Direction |
|---|---|
| Local declared run evidence readiness | Authenticated Agent Identity |
| Closed evidence bundle adequacy check | Trusted Memory |
| Allowlisted synthetic mapping | Longitudinal State Continuity |
| Deterministic bounded reason codes | Multi-Agent Governance |
| Recommendation, not Authorization | Responsibility Decision Context |

底部固定：`Website narrative does not change canonical capability facts.`

### H7 — Evidence-to-Trust Interpretation

用一条系统关系说明：

`Runtime / A2A / MCP / Telemetry / Identity → SAEE Interpretation → IAM / Policy / Human Authority`

SAEE 区域只使用 `interpret / evaluate / expose gaps / recommend`，不使用 `execute / approve / enforce / punish`。

### H8 — Ecosystem Entry

三张卡：

- Agent Frameworks：共同研究跨 checkpoint continuity；
- Cloud Agent Platforms：共同定义可信运行证据与责任边界；
- Developer Ecosystem：Whitepaper、Architecture、GitHub、agent-readable entry。

所有平台名称都必须带：`示例性生态对象，不代表官方合作或集成。`

### H9 — Research and Standards

展示 NIST、A2A、MCP、OpenTelemetry、SPIFFE、SCITT 等一手标准入口，说明 SAEE 研究 standards composition，不创造平行 transport 或 identity standard。

### H10 — Final CTA

标题：`未来的企业 Agent，需要连续可信，而不只是一次成功。`

CTA：

- 阅读 Whitepaper Outline；
- 查看 Architecture Overview；
- 进入 GitHub；
- 了解 Current Capability。

## 5. 路由架构

| Route | 人类目的 | 主要内容 | Truth boundary |
|---|---|---|---|
| `/` | 类别入口 | 问题、类别、架构、Current/Future | 未来定位不等于实现 |
| `/architecture` | 技术理解 | 分层、对象、standards composition | architecture hypothesis |
| `/current-vs-future` | 防止误解 | canonical current facts 与 future matrix | inventory-derived |
| `/whitepaper` | 行业定义 | 白皮书大纲与来源 | outline, not publication |
| `/ecosystem` | 合作理解 | Framework/Cloud/Developer entry | no partnership claims |
| `/for-agents` | Agent-readable entry | current operations、contracts、machine links | preserve existing current facts |
| `/research` | 研究依据 | 精选研究与状态边界 | submission != publication |
| `/security` | 公共安全边界 | disclosure policy、security status | no formal audit claim |

Phase 1 可以先以首页 anchor sections 实现 `/architecture`、`/current-vs-future`、`/whitepaper` 和 `/ecosystem` 的核心内容；独立 route 是后续内容深化，不得因此创建新的产品能力。

## 6. Agent-Readable 信息架构

现有稳定入口继续保留：

- `/llms.txt`；
- `/.well-known/agent-index.json`；
- canonical capability manifest；
- `/for-agents`；
- raw JSON canonical URLs。

Phase 1 需要确保机器入口能够读取：

- category：`Multi-Agent Long-Running Trust Infrastructure`；
- project stage：`future_direction_category_positioning`；
- current capability pointers；
- future direction non-claims；
- architecture and whitepaper links；
- ecosystem contact route；
- `production_ready=false`。

本阶段不修改 MCP implementation 或 capability Schema。机器可读叙事变更必须继续引用 canonical inventory，不能成为第二事实源。

## 7. SEO 与分享语义

Title：`SAEE｜多智能体长期运行可信基础设施`

Description：

`SAEE 正在研究和建设面向企业长期运行、多智能体协作系统的可信基础设施方向，连接 Agent Identity、Execution Evidence、State Continuity 与 Governance。当前仅具备受限的本地证据评估能力，尚未生产就绪。`

关键词：

- Multi-Agent Trust Infrastructure；
- Long-Running AI Agents；
- Agent Identity；
- Agent Execution Evidence；
- Agent State Continuity；
- Multi-Agent Governance；
- 可信智能体基础设施；
- 智能体长期运行。

Open Graph 必须与实际首页一致，不使用产品 UI 截图冒充未来平台。

## 8. 上线前内容门

```text
HOMEPAGE_CATEGORY_CLEAR=true
CURRENT_FUTURE_SEPARATED=true
CANONICAL_CAPABILITY_FACTS_MATCH=true
FUTURE_ARCHITECTURE_LABELLED=true
PRODUCTION_CLAIMS_PRESENT=false
UNVERIFIED_PARTNERSHIP_CLAIMS_PRESENT=false
MCP_IMPLEMENTATION_CHANGED=false
MAINLINE_CODE_CHANGED=false
```
