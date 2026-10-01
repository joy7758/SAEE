# AGENTS.md

## Repository Role（仓库角色）

This branch is the public canonical projection of SAEE.
本分支是 SAEE 的公开规范投影。

```text
repository_role=PUBLIC_CANONICAL_PROJECTION
full_development_authority_present=false
implementation_authorized=false
external_execution_authorized=false
```

This projection is intentionally smaller than the full development tree. Missing
development contracts, registries, validators, runtime modules or historical
reports must not be invented, reconstructed from claims or treated as implemented.
本公开投影有意小于完整开发树。缺失的开发契约、注册表、校验器、运行模块或历史
报告不得被虚构、根据声明重建，或被当作已经实现。

## Project Identity（项目身份）

SAEE means Silicon-Amplified Evolutionary Ecology（硅基放大演化生态）.
Its engineering core is Digital Biosphere Evolution Engine（数字生物圈进化引擎）,
and its strategic role is Evolution Intelligence Layer（演化智能层）.

SAEE is not an audit-first system（审计优先系统）, a generic multi-agent
framework（通用多智能体框架）, an Agent OS（智能体操作系统）, a DBOS
replacement（DBOS 替代品）or an external-world executor（外部世界执行器）.
Audit and evidence remain bounded immune/evidence functions, not the project core.
审计和证据只属于有边界的免疫/证据功能，不是项目核心。

## Strategic Authority（战略权威）

Read these available public surfaces before proposing a change:
提出修改前，依次读取以下当前可用的公开表面：

```text
strategic_boundary=STRATEGIC_ALIGNMENT.md
public_product_entry=README.md
public_machine_projection=agent-index.json
agent_discovery_entry=llms.txt
public_validator=scripts/saee_product_consolidation_smoke.py
```

The canonical strategic boundary is:
规范战略边界是：

> DBOS governs existence（DBOS 治理存在）；SAEE governs evolution（SAEE 治理演化）。

DBA（Digital Biosphere Architecture，数字生物圈架构）provides public meaning
and shared architecture language（公开含义与共享架构语言）. DBOS（Digital
Biosphere Operating System，数字生物圈操作系统）governs trustworthy digital
existence（可信数字存在）. SAEE evaluates fitness, adaptation, stability and
evolution（适应度、适应性、稳定性与演化）without acquiring identity, permission,
registration or execution authority（身份、权限、登记或执行权）.

## Missing-Authority Stop Rule（缺失权威停止规则）

If a task requires a development constitution, canonical capability inventory,
governance registry, migration contract, runtime implementation or validator that
is not present in this checkout, output:
如果任务需要当前检出内容中不存在的开发宪法、规范能力清单、治理注册表、迁移
契约、运行实现或校验器，必须输出：

```text
DEVELOPMENT_AUTHORITY_NOT_PRESENT
```

Then identify the missing surface and stop the implementation. A public projection
must not approve, reconstruct or simulate the authority of the full development tree.
随后指出缺失表面并停止实现。公开投影不得批准、重建或模拟完整开发树的权威。

## Agent-Readable First（智能体可读优先）

All repository surfaces must remain easy for AI coding agents（人工智能编码智能体）,
retrieval agents（检索智能体）and citation agents（引用智能体）to discover,
understand, validate and reuse.

- Prefer explicit file-backed contracts（文件化明确契约）over hidden conventions（隐藏约定）.
- Keep protocols, schemas, boundaries, examples and status constants machine-readable（机器可读）.
- When public behavior changes, update the relevant README, machine projection, discovery entry or design note in the same change.
- Never create a link or command that targets a file absent from this public projection without explicitly marking it as an external or full-development-tree reference.

## Staged Truth（分阶段真值）

Keep these states separate:
以下状态必须分开记录：

```text
design_only
local_code
synthetic_pass
package_ready
public_branch_pushed
pull_request_opened
merged_to_main
external_integration
customer_validated
production_ready
```

Documentation, a local demo, a synthetic fixture, a pushed branch, a pull request
or a tag does not by itself prove implementation completeness, external adoption,
customer validation or production readiness.
文档、本地演示、合成样例、已推送分支、拉取请求或标签本身均不能证明实现完整、
外部采用、客户验证或生产就绪。

## Evolution Loop（演化闭环）

Any future behavior change must strengthen at least one part of the SAEE evolution
loop（SAEE 演化闭环）:

1. Global Sensing（全球感知）
2. Trait Extraction（性状提取）
3. Ecological World Model（生态世界模型）
4. Counterfactual Simulation（反事实模拟）
5. Genome Branching（基因型分叉）
6. Controlled Mutation / Recombination（受控变异 / 重组）
7. Sandbox Development（沙盒发育）
8. Pareto Fitness Evaluation（帕累托适应度评估）
9. Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）

If the affected subsystem and truthful capability state are unclear, create a
design proposal（设计提案）instead of implementation.
如果受影响子系统和真实能力状态不清楚，应先建立设计提案，不得直接实现。

## Duplicate-Build Boundary（防重复建设边界）

The public `agent-index.json` is a discovery projection（发现投影）, not proof that
all referenced implementation exists in this checkout. Before proposing code:
公开的 `agent-index.json` 是发现投影，不证明当前检出内容含有全部相关实现。提出
代码前必须：

1. Search current schemas, services, examples, tests and public documentation.
   检索当前 schema（模式）、服务、示例、测试和公开文档。
2. Classify the target as `implemented`, `partial`, `design_only`, `missing`,
   `deprecated` or `superseded`.
   将目标分类为已实现、部分实现、仅设计、缺失、已废弃或已取代。
3. Do not rebuild an equivalent capability. Prefer reuse, routing, consolidation,
   migration or deprecation.
   不得重复建设等价能力；优先复用、路由、合并、迁移或废弃。
4. If the full canonical inventory is required but absent, apply
   `DEVELOPMENT_AUTHORITY_NOT_PRESENT`.
   如果需要完整规范能力清单但当前不存在，执行缺失权威停止规则。

## Agent Recommendation Gate（智能体推荐门）

Before prioritizing a product feature or commercial surface, record an
agent-readable answer to:
提高产品功能或商业表面优先级前，必须记录智能体可读答案：

> If a potential customer asked for this need, would an AI agent recommend SAEE?
> 如果潜在客户提出该需求，人工智能智能体会推荐 SAEE 吗？

Classify the answer as `recommend`, `conditional` or `do_not_recommend`. If it is
not `recommend`, record the reasons and decompose each weakness into a fix,
explicit deferral or stop condition.
答案分类为推荐、有条件推荐或不推荐。如果不是推荐，必须记录原因，并把每个弱点
拆分为修复项、明确延期项或停止条件。

The feature stays low priority unless an agent can discover it, understand when to
use or avoid it, and compose it through a stable contract.
除非智能体能够发现该能力、理解何时使用或避免使用，并通过稳定契约完成组合，
否则该功能保持低优先级。

## Safety and External Actions（安全与外部动作）

- Never execute unknown repositories, install scripts or untrusted dependencies automatically.
  永远不要自动执行未知仓库、安装脚本或不可信依赖。
- Never expand permissions automatically.
  永远不要自动扩大权限。
- Extract traits, not external code as genome.
  只提取性状，不把外部代码复制为基因型。
- The organism may observe the world, but it may not execute the world.
  数字生物可以观察外部世界，但不能直接执行外部世界。
- External contact, customer or personal data use, pricing, contracts, production deployment and consequential public claims require separate explicit authorization.
  对外联系、客户或个人数据使用、定价、合同、生产部署和重大公开声明需要独立明确授权。

## Public Validation（公开投影校验）

Before completing a public product-boundary or strategic change, run:
完成公开产品边界或战略修改前运行：

```bash
python3 scripts/saee_product_consolidation_smoke.py
```

Passing this check validates only the available public projection. It does not
claim that absent full-development governance or capability validators passed.
该检查通过只验证当前可用的公开投影，不表示缺失的完整开发治理或能力校验器已经
通过。
