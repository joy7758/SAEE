# SAEE F1 校验器最小新增授权包准备

日期：2026-07-17

## 0. 结论

本文件为 F1（基础锚点第一阶段）自验证闭环准备六项最小精确授权候选。候选被绑定为一个不可拆分的 `1.1.1` 目标集合；五个完整文件按整文件字节和 `SHA-256`（安全散列算法二百五十六位）绑定，`AGENTS.md`（智能体规则文件）只按第 47—80 行的精确片段绑定。

本文件不批准构造、暂存、提交或建立 F1。任何一项未批准、散列变化或版本混用，都必须使后续构造失败关闭。

```text
F1_VALIDATOR_MINIMUM_ADDITIONAL_AUTHORIZATION_PACKAGE_STATUS=COMPLETE
AUTHORIZATION_CANDIDATE_COUNT=6
TARGET_VERSION_SET=1.1.1_ONLY
TARGET_SET_ATOMIC=true
OLD_STAGED_1_1_0_EXCLUDED=true
AUTHORIZATION_DECISION=PENDING_HUMAN_CONFIRMATION
F1_CONSTRUCTION_AUTHORIZED=false
F1_BASELINE_AUTHORIZED=false
MAINLINE_DRIFT_DETECTED=false
```

## 1. 输入与依据

```text
BASE_HEAD=f6ac41f4b068377e7778e8c3d83b99bd8382debc
SCOPE_REVIEW=reports/SAEE_F1_CONSTITUTION_VALIDATOR_DEPENDENCY_SCOPE_REVIEW.md
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
```

依赖范围审查确认：

- 六项既有 F1 精确对象负责校验器的投影表面；
- `README.md`（项目说明）、`.codex/context.md`（编码智能体上下文）和规范能力清单可以从 `HEAD`（当前提交）原样继承；
- 当前缺口严格等于本授权包的六项；
- P1（契约父基线第一阶段）直接依赖数量为零。

## 2. 统一版本规则

只允许以下一致目标：

```text
constitution_contract_version=1.1.1
constitution_schema_version=1.1.1
constitution_validator_expected_version=1.1.1
program_mainline=saee_agent_evidence_integration
target_customer_versions=SAEE_Evidence;SAEE_Evaluation;SAEE_Governance
```

禁止：

- 使用暂存区旧 `1.1.0` 校验器；
- 使用暂存区旧 `1.1.0`机器契约；
- 使用暂存区旧 `1.1.0` 数据结构规范；
- 把旧宪法正文或旧推荐门与当前 `1.1.1` 校验器组合；
- 单独批准其中一项后直接构造；
- 用当前主工作区整文件替代本报告绑定的目标内容。

```text
MIXED_VERSION_SET_ALLOWED=false
PARTIAL_TARGET_SET_CONSTRUCTION_ALLOWED=false
CURRENT_INDEX_AS_TARGET_SOURCE_ALLOWED=false
```

## 3. 候选总表

| 编号 | 路径与范围 | 目标类型 | 目标 `SHA-256`（安全散列算法二百五十六位） | P1 边界 |
| --- | --- | --- | --- | --- |
| `F1-VD-01` | `scripts/saee_development_constitution_smoke.py` 全文件 | 完整文件 | `8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550` | 不包含九十九路径验证 |
| `F1-VD-02` | `agent-interface/governance/saee-development-constitution.v1.1.json` 全文件 | 完整文件 | `df200d13ec90ce5dd57cedb4ceab83b1c2a5b751b68af35a1a749f39db15f8a0` | 不包含内部能力名称迁移 |
| `F1-VD-03` | `schemas/saee-development-constitution.schema.v1.1.json` 全文件 | 完整文件 | `dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86` | 不修改公开或内部能力数据结构规范 |
| `F1-VD-04` | `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` 全文件 | 完整文件 | `37d9adb3049c5fdd871460f6756240a177264e4442cc38252786e9d7c86f378c` | 不包含 P1 实施状态 |
| `F1-VD-05` | `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` 全文件 | 完整文件 | `1bc493e03e3158e2d984308a78efa80cde131a5b9ee2142449695c807433ee9c` | 不授权 P1 实施或合并 |
| `F1-VD-06` | `AGENTS.md:47-80` | 精确片段 | `0ff92cee0427e6e6b3e207544c153a6bab82f214d3998e16b224f58d46da8c42` | 不复制 `AGENTS.md` 其他当前变化 |

## 4. 每项授权候选

### 4.1 F1-VD-01：开发宪法校验器

```text
PATH=scripts/saee_development_constitution_smoke.py
SCOPE=WHOLE_FILE
TARGET_LINE_COUNT=263
TARGET_BYTE_COUNT=11893
TARGET_SHA256=8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550
TARGET_VERSION=1.1.1
```

目标内容：附录 A 的完整 Python（蟒蛇编程语言）文件。

排除内容：

- 暂存区 `1.1.0` 版本；
- 任何主线守卫接线变化；
- 任何文件写入或生成物逻辑；
- 任何 P1 名称迁移校验；
- 任何 M03-M06（第三至第六里程碑）校验；
- 任何模型调用、网络访问或外部执行。

P1 边界：该校验器只验证开发宪法和既有表面令牌，不验证 `evaluate_rehearsal_run`（内部排演运行评估）迁移。

### 4.2 F1-VD-02：开发宪法机器契约

```text
PATH=agent-interface/governance/saee-development-constitution.v1.1.json
SCOPE=WHOLE_FILE
TARGET_LINE_COUNT=106
TARGET_BYTE_COUNT=4229
TARGET_SHA256=df200d13ec90ce5dd57cedb4ceab83b1c2a5b751b68af35a1a749f39db15f8a0
TARGET_VERSION=1.1.1
```

目标内容：附录 B 的完整 JSON（轻量数据交换格式）对象。

排除内容：

- 暂存区 `1.1.0` 版本；
- 任何能力新增或能力状态更新；
- 任何源代码迁移完成主张；
- 任何运行时集成完成主张；
- 任何 P1 内部工具名称或兼容映射。

P1 边界：`canonical_inventory_change=none_this_change` 必须保持；契约收敛补丁不进入本对象。

### 4.3 F1-VD-03：开发宪法数据结构规范

```text
PATH=schemas/saee-development-constitution.schema.v1.1.json
SCOPE=WHOLE_FILE
TARGET_LINE_COUNT=153
TARGET_BYTE_COUNT=6488
TARGET_SHA256=dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86
TARGET_VERSION=1.1.1
```

目标内容：附录 C 的完整 JSON（轻量数据交换格式）数据结构规范。

排除内容：

- 暂存区 `1.1.0` 版本；
- 请求、响应或 MCP（模型上下文协议）数据结构规范变化；
- 新能力字段；
- P1 内部工具标识；
- 外部数据结构规范引用解析或网络依赖。

P1 边界：本对象只描述开发宪法机器契约，不属于公开或内部能力接口数据结构规范。

### 4.4 F1-VD-04：开发宪法正文

```text
PATH=docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
SCOPE=WHOLE_FILE
TARGET_LINE_COUNT=335
TARGET_BYTE_COUNT=14590
TARGET_SHA256=37d9adb3049c5fdd871460f6756240a177264e4442cc38252786e9d7c86f378c
TARGET_VERSION=1.1.1
```

目标内容：附录 D 的完整 Markdown（标记文本）文件。

排除内容：

- 暂存区旧正文；
- 未来可信基础设施实现；
- Goal Integrity（目标完整性）或 State Integrity（状态完整性）工程化；
- P1 已完成、M03-M06 已形成基线或产品已实现的主张；
- 当前工作区其他治理、商业或生态投影。

P1 边界：正文只规定受控合并纪律和目标客户版本，不证明 P1 已建立或迁移已完成。

### 4.5 F1-VD-05：开发宪法推荐门

```text
PATH=docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md
SCOPE=WHOLE_FILE
TARGET_LINE_COUNT=103
TARGET_BYTE_COUNT=5330
TARGET_SHA256=1bc493e03e3158e2d984308a78efa80cde131a5b9ee2142449695c807433ee9c
TARGET_VERSION=1.1.1
```

目标内容：附录 E 的完整 Markdown（标记文本）文件。

排除内容：

- 暂存区旧推荐门；
- P1 实施授权；
- 源代码迁移授权；
- 运行时集成授权；
- 客户验证、发布或生产就绪结论；
- 自动外部动作授权。

P1 边界：`recommend`（推荐）只适用于宪法归属和受控迁移纪律，不等于批准 P1 修改。

### 4.6 F1-VD-06：智能体规则精确主线段落

```text
PATH=AGENTS.md
SCOPE=LINES_47_80_ONLY
TARGET_LINE_COUNT=34
TARGET_SHA256=0ff92cee0427e6e6b3e207544c153a6bab82f214d3998e16b224f58d46da8c42
TARGET_VERSION=1.1.1_PROGRAM_MAINLINE_PROJECTION
WHOLE_FILE_AUTHORIZED=false
```

目标内容：附录 F 的 34 行精确片段。

排除内容：

- `AGENTS.md`（智能体规则文件）第 1—46 行；
- 第 81 行及之后全部内容；
- 当前文件中的其他规则、商业逻辑或能力说明变化；
- 任何 P1、M03-M06 或未来研究文字。

P1 边界：本片段只投影宪法主线、副线、三个目标版本和漂移纠正义务，不包含内部能力名称迁移。

## 5. 旧暂存 1.1.0 排除清单

以下暂存对象明确排除，不能成为构造来源：

| 编号 | 旧暂存对象 `SHA-256` | 排除原因 |
| --- | --- | --- |
| `F1-VD-01` | `26575dd8784bbabeb9df7b02a230970a280cf6edcaf8c60d01d64535f050c553` | 校验器期望版本仍为 `1.1.0`，缺少主线和目标版本校验 |
| `F1-VD-02` | `1d94a4ffe9dfcda56e4d12d2c2a2673a51b63531f40cb807427f0a587bb086ea` | 机器契约版本为 `1.1.0` |
| `F1-VD-03` | `868d0f74690026ac6a24ed295a6f0b561001cda551a05fe9af8d32e52bd774dc` | 数据结构规范版本为 `1.1.0` |
| `F1-VD-04` | `12ec2c53108d34c1334c1d2b3cf9e13726661de4ba888e01df671287140ad669` | 缺少当前主线、客户版本和纠偏章节 |
| `F1-VD-05` | `f294c22b9a2114023fce2a9099c2e23af4f990e4a12108182d7c62168d6f50b0` | 缺少主线纠偏推荐记录 |

```text
OLD_STAGED_OBJECT_COUNT=5
OLD_STAGED_OBJECTS_AUTHORIZED=false
OLD_STAGED_OBJECTS_ALLOWED_AS_CONSTRUCTION_SOURCE=false
```

## 6. 原子授权和失败关闭规则

人工决定必须逐项记录，但构造许可只能在六项全部批准后成立：

```text
F1-VD-01=APPROVE|REJECT
F1-VD-02=APPROVE|REJECT
F1-VD-03=APPROVE|REJECT
F1-VD-04=APPROVE|REJECT
F1-VD-05=APPROVE|REJECT
F1-VD-06=APPROVE|REJECT
```

如果任一项不是 `APPROVE`（批准），则：

```text
VALIDATOR_DEPENDENCY_SET_APPROVED=false
F1_SELF_VALIDATION_READY=false
F1_CONSTRUCTION_AUTHORIZED=false
```

即使六项均获批准，也只允许在现有隔离候选上精确增加这六项，并重新运行四项校验；不得自动建立基线、暂存或提交。

## 7. 当前参考验证

当前工作树中的统一 `1.1.1` 集合已只读运行：

```text
python3 scripts/saee_development_constitution_smoke.py
```

结果：

```text
CURRENT_WORKTREE_REFERENCE_VALIDATION_PASS=true
schema_cases=1/1
negative_cases=7/7
deterministic_runs=10/10
evolution_subsystems=9/9
canonical_reuse_routes=3/3
```

这只证明附录目标内容与当前其余依赖可以组成可运行参考闭环，不是人工批准或 F1 基线证据。

## 8. 全局排除边界

```text
P1_INCLUDED=false
NINETY_NINE_PATH_PATCH_INCLUDED=false
M03_M06_INCLUDED=false
TRUST_INFRASTRUCTURE_INCLUDED=false
GOAL_INTEGRITY_INCLUDED=false
STATE_INTEGRITY_INCLUDED=false
CAPABILITY_INVENTORY_CHANGED=false
NEW_CAPABILITY_CREATED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
SOURCE_FILES_MODIFIED=false
```

## 9. 附录：精确目标内容

### 附录 A：F1-VD-01

目标路径：`scripts/saee_development_constitution_smoke.py`

目标 `SHA-256`：`8e4b43ace4547caafdea508e6dde067dc43c5187336bb548f48e43a2735b2550`

````python
#!/usr/bin/env python3
"""Validate SAEE Development Constitution v1.1 and its truth boundaries."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "agent-interface/governance/saee-development-constitution.v1.1.json"
SCHEMA_PATH = ROOT / "schemas/saee-development-constitution.schema.v1.1.json"
CONSTITUTION_PATH = ROOT / "docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md"
INVENTORY_PATH = ROOT / "capability-package/manifest.json"

EXPECTED_LOOP = [
    "global_sensing",
    "trait_extraction",
    "ecological_world_model",
    "counterfactual_simulation",
    "genome_branching",
    "controlled_mutation_recombination",
    "sandbox_development",
    "pareto_fitness_evaluation",
    "evolutionary_archive_rollback_immune_system",
]
EXPECTED_CAPABILITIES = {
    "saee.evaluate_evidence",
    "saee.general_trace_normalization",
    "saee.trusted_trace_to_evidence_conversion",
}
EXPECTED_PROGRAM_TASKS = {
    "mainline": "integrate_saee_and_agent_evidence_project_under_migration_gates",
    "secondary": "use_saee_to_supervise_and_test_the_integration_process",
    "secondary_cannot_displace_mainline": True,
    "self_assessment_cannot_self_approve": True,
    "role_prompt_cannot_override_mainline": True,
    "drift_response": "raise_correction_recommendation",
}
EXPECTED_CUSTOMER_VERSIONS = [
    "SAEE Evidence",
    "SAEE Evaluation",
    "SAEE Governance",
]
EXPECTED_TRUTH = {
    "source_code_migrated": False,
    "runtime_integrated": False,
    "external_integration_validated": False,
    "customer_validated": False,
    "product_launched": False,
    "production_ready": False,
}
SURFACE_TOKENS = {
    "AGENTS.md": (
        "SAEE Development Constitution v1.1",
        "agent-interface/governance/saee-development-constitution.v1.1.json",
        "python3 scripts/saee_development_constitution_smoke.py",
        "Constitutional Program Mainline",
        "SAEE Evidence / SAEE Evaluation / SAEE Governance",
    ),
    "README.md": (
        "SAEE Development Constitution v1.1",
        "SAEE Evidence and Immune Subsystem",
    ),
    "llms.txt": (
        "Development constitution: docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md",
        "Agent Evidence Project role: SAEE Evidence and Immune Subsystem",
        "Constitutional program mainline: controlled SAEE and Agent Evidence Project integration",
        "Target customer versions: SAEE Evidence; SAEE Evaluation; SAEE Governance",
    ),
    ".codex/rules.md": (
        "SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md",
        "SAEE Evidence and Immune Subsystem",
    ),
    ".codex/context.md": (
        "Digital Biosphere Evolution Engine",
        "Source-code migration and unified runtime integration remain false",
    ),
    ".codex/current_state.md": (
        "SAEE Development Constitution v1.1",
        "source_code_migrated=false",
        "runtime_integrated=false",
    ),
    "docs/product/SAEE_MODULE_REGISTRY.md": (
        "agent-evidence-layer",
        "SAEE Evidence and Immune Subsystem",
    ),
    "docs/architecture/IMMUNE_GOVERNANCE_PLANE.md": (
        "Agent Evidence Project",
        "source_code_migrated=false",
    ),
}


def validate_contract(value: Any, inventory_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["CONTRACT_ROOT_INVALID"]
    if value.get("constitution_id") != "saee-development-constitution-v1.1":
        errors.append("CONSTITUTION_ID_INVALID")
    if value.get("version") != "1.1.1":
        errors.append("VERSION_INVALID")
    authority = value.get("authority", {})
    if authority.get("engineering_core") != "Digital Biosphere Evolution Engine":
        errors.append("ENGINEERING_CORE_INVALID")
    if authority.get("theory_identity") != "Silicon-Amplified Evolutionary Ecology":
        errors.append("THEORY_IDENTITY_INVALID")
    mission = value.get("mission", {})
    if mission.get("audit_first_reframe") is not False:
        errors.append("AUDIT_FIRST_REFRAME_INVALID")
    if mission.get("evidence_role") != "supports_evolutionary_selection_archive_and_rollback":
        errors.append("EVIDENCE_ROLE_INVALID")
    if value.get("evolution_loop") != EXPECTED_LOOP:
        errors.append("EVOLUTION_LOOP_INVALID")
    if value.get("program_tasks") != EXPECTED_PROGRAM_TASKS:
        errors.append("PROGRAM_TASKS_INVALID")
    if value.get("target_customer_versions") != EXPECTED_CUSTOMER_VERSIONS:
        errors.append("TARGET_CUSTOMER_VERSIONS_INVALID")

    integration = value.get("evidence_subsystem_integration", {})
    expected_integration = {
        "saee_role": "evidence_and_immune_subsystem",
        "overall_classification": "partial",
        "constitutional_ownership": "implemented",
        "source_code_adoption": "not_performed",
        "runtime_integration": "not_performed",
        "canonical_inventory_change": "none_this_change",
    }
    for key, expected in expected_integration.items():
        if integration.get(key) != expected:
            errors.append(f"INTEGRATION_{key.upper()}_INVALID")
    resolved = set(integration.get("capabilities_to_resolve_at_read_time", []))
    if resolved != EXPECTED_CAPABILITIES:
        errors.append("REUSE_CAPABILITY_SET_INVALID")
    if not resolved.issubset(inventory_ids):
        errors.append("REUSE_CAPABILITY_NOT_IN_CANONICAL_INVENTORY")
    non_claims = integration.get("non_claims", [])
    if not isinstance(non_claims, list) or len(non_claims) < 8:
        errors.append("NON_CLAIMS_INCOMPLETE")

    external = value.get("external_action_boundary", {})
    if external != {
        "observes_world": True,
        "executes_world": False,
        "decision_context_is_authority": False,
        "explicit_authorization_required": True,
    }:
        errors.append("EXTERNAL_ACTION_BOUNDARY_INVALID")
    if value.get("truth_boundary") != EXPECTED_TRUTH:
        errors.append("STAGED_TRUTH_BOUNDARY_INVALID")
    return errors


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))["canonical_inventory"]
    inventory_ids = {item["capability_id"] for item in inventory["capabilities"]}

    require(schema.get("title") == "SAEE Development Constitution v1.1", "schema title")
    require(schema.get("additionalProperties") is False, "closed schema root")
    require(set(schema.get("required", [])) == set(contract), "schema root coverage")
    require(validate_contract(contract, inventory_ids) == [], "valid constitution rejected")

    invalid_cases: list[tuple[str, dict[str, Any], str]] = []
    audit_first = copy.deepcopy(contract)
    audit_first["mission"]["audit_first_reframe"] = True
    invalid_cases.append(("audit-first reframe", audit_first, "AUDIT_FIRST_REFRAME_INVALID"))
    false_migration = copy.deepcopy(contract)
    false_migration["truth_boundary"]["source_code_migrated"] = True
    invalid_cases.append(("false source migration", false_migration, "STAGED_TRUTH_BOUNDARY_INVALID"))
    false_runtime = copy.deepcopy(contract)
    false_runtime["truth_boundary"]["runtime_integrated"] = True
    invalid_cases.append(("false runtime integration", false_runtime, "STAGED_TRUTH_BOUNDARY_INVALID"))
    execute_world = copy.deepcopy(contract)
    execute_world["external_action_boundary"]["executes_world"] = True
    invalid_cases.append(("external execution", execute_world, "EXTERNAL_ACTION_BOUNDARY_INVALID"))
    duplicate_route = copy.deepcopy(contract)
    duplicate_route["evidence_subsystem_integration"]["capabilities_to_resolve_at_read_time"] = ["saee.new_receipt_stack"]
    invalid_cases.append(("duplicate route", duplicate_route, "REUSE_CAPABILITY_SET_INVALID"))
    displaced_mainline = copy.deepcopy(contract)
    displaced_mainline["program_tasks"]["secondary_cannot_displace_mainline"] = False
    invalid_cases.append(("secondary displaces mainline", displaced_mainline, "PROGRAM_TASKS_INVALID"))
    wrong_versions = copy.deepcopy(contract)
    wrong_versions["target_customer_versions"] = ["SAEE Evidence", "SAEE Evaluation", "SAEE Autonomous"]
    invalid_cases.append(("wrong customer versions", wrong_versions, "TARGET_CUSTOMER_VERSIONS_INVALID"))
    for name, invalid, expected in invalid_cases:
        errors = validate_contract(invalid, inventory_ids)
        require(expected in errors, f"negative case not rejected: {name}")

    canonical = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(10):
        repeated = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        require(validate_contract(repeated, inventory_ids) == [], "deterministic validation")
        require(
            json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical,
            "deterministic canonical form",
        )

    constitution = CONSTITUTION_PATH.read_text(encoding="utf-8")
    for token in (
        "Digital Biosphere Evolution Engine",
        "SAEE Evidence and Immune Subsystem",
        "source_code_migrated",
        "signature_valid=true",
        "audit_first_reframe=false",
        "capability-package/manifest.json#canonical_inventory",
        "program_mainline=saee_agent_evidence_integration",
        "SAEE Governance",
        "MAINLINE_DRIFT_DETECTED",
    ):
        require(token in constitution, f"constitution token missing: {token}")
    gate = GATE_PATH.read_text(encoding="utf-8")
    for token in ("## Initial Result", "answer: conditional", "## Final Result", "`recommend`"):
        require(token in gate, f"recommendation gate token missing: {token}")
    for relative_path, tokens in SURFACE_TOKENS.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for token in tokens:
            require(token in text, f"surface token missing: {relative_path}: {token}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    index_entry = index.get("development_constitution_v1_1", {})
    require(index_entry.get("contract") == str(CONTRACT_PATH.relative_to(ROOT)), "agent-index contract pointer")
    require(index_entry.get("agent_evidence_project_role") == "evidence_and_immune_subsystem", "agent-index evidence role")
    require(
        index_entry.get("program_mainline")
        == "integrate_saee_and_agent_evidence_project_under_migration_gates",
        "agent-index program mainline",
    )
    require(
        index_entry.get("target_customer_versions") == EXPECTED_CUSTOMER_VERSIONS,
        "agent-index target customer versions",
    )
    require(index_entry.get("production_ready") is False, "agent-index production boundary")

    print("SAEE_DEVELOPMENT_CONSTITUTION_SMOKE: PASS")
    print("schema_cases=1/1")
    print(f"negative_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=10/10")
    print("evolution_subsystems=9/9")
    print("canonical_reuse_routes=3/3")
    print("agent_evidence_project_role=evidence_and_immune_subsystem")
    print("program_mainline=saee_agent_evidence_integration")
    print("program_secondary=saee_supervises_and_tests_integration")
    print("target_customer_versions=3/3")
    print("mainline_drift_correction_required=true")
    print("source_code_migrated=false")
    print("runtime_integrated=false")
    print("external_world_execution=false")
    print("audit_first_reframe=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
````

### 附录 B：F1-VD-02

目标路径：`agent-interface/governance/saee-development-constitution.v1.1.json`

目标 `SHA-256`：`df200d13ec90ce5dd57cedb4ceab83b1c2a5b751b68af35a1a749f39db15f8a0`

````json
{
  "$schema": "../../schemas/saee-development-constitution.schema.v1.1.json",
  "constitution_id": "saee-development-constitution-v1.1",
  "version": "1.1.1",
  "authority": {
    "canonical_document": "docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md",
    "effective_date": "2026-07-14",
    "engineering_core": "Digital Biosphere Evolution Engine",
    "theory_identity": "Silicon-Amplified Evolutionary Ecology"
  },
  "mission": {
    "primary": "Operate a controlled digital biosphere evolution loop for sensing, trait extraction, world modeling, counterfactual simulation, branching, variation, sandbox development, fitness selection, archive and rollback.",
    "evidence_role": "supports_evolutionary_selection_archive_and_rollback",
    "audit_first_reframe": false
  },
  "program_tasks": {
    "mainline": "integrate_saee_and_agent_evidence_project_under_migration_gates",
    "secondary": "use_saee_to_supervise_and_test_the_integration_process",
    "secondary_cannot_displace_mainline": true,
    "self_assessment_cannot_self_approve": true,
    "role_prompt_cannot_override_mainline": true,
    "drift_response": "raise_correction_recommendation"
  },
  "target_customer_versions": [
    "SAEE Evidence",
    "SAEE Evaluation",
    "SAEE Governance"
  ],
  "evolution_loop": [
    "global_sensing",
    "trait_extraction",
    "ecological_world_model",
    "counterfactual_simulation",
    "genome_branching",
    "controlled_mutation_recombination",
    "sandbox_development",
    "pareto_fitness_evaluation",
    "evolutionary_archive_rollback_immune_system"
  ],
  "agent_readable_rule": {
    "required": true,
    "first_class_surfaces": [
      "README.md",
      "agent-index.json",
      "llms.txt",
      "capability_manifests",
      "schema_registries",
      "examples",
      "cli_tool_interfaces",
      "offline_validators"
    ]
  },
  "evidence_subsystem_integration": {
    "project_name": "Agent Evidence Project",
    "legacy_product_name": "Agent Evidence Receipt",
    "legacy_source_repository_name": "agent-evidence-layer",
    "saee_role": "evidence_and_immune_subsystem",
    "overall_classification": "partial",
    "constitutional_ownership": "implemented",
    "source_code_adoption": "not_performed",
    "runtime_integration": "not_performed",
    "canonical_inventory_change": "none_this_change",
    "capabilities_to_resolve_at_read_time": [
      "saee.evaluate_evidence",
      "saee.general_trace_normalization",
      "saee.trusted_trace_to_evidence_conversion"
    ],
    "claims": [
      "The Agent Evidence Project is constitutionally owned by SAEE as its Evidence and Immune Subsystem.",
      "Evidence receipts may provide bounded integrity, provenance and completeness context to evaluation, selection, archive and rollback."
    ],
    "non_claims": [
      "The legacy source repository has been copied or migrated into this repository.",
      "A unified SAEE evidence runtime has been integrated.",
      "A hash or valid signature proves that the described event occurred in the real world.",
      "Evidence evaluation authorizes execution, deployment or external action.",
      "External interoperability or customer validation has been completed.",
      "The subsystem is production ready or publicly launched.",
      "The controlled SAEE and Agent Evidence source or runtime merge has completed.",
      "The three target customer versions are implemented, customer validated, launched or production ready."
    ]
  },
  "development_gates": [
    "canonical_inventory_resolution",
    "duplicate_build_check",
    "evolution_subsystem_design_check",
    "agent_recommendation_gate",
    "standards_and_supply_chain_boundary_check",
    "claims_non_claims_and_staged_truth",
    "schema_negative_and_deterministic_validation"
  ],
  "external_action_boundary": {
    "observes_world": true,
    "executes_world": false,
    "decision_context_is_authority": false,
    "explicit_authorization_required": true
  },
  "truth_boundary": {
    "source_code_migrated": false,
    "runtime_integrated": false,
    "external_integration_validated": false,
    "customer_validated": false,
    "product_launched": false,
    "production_ready": false
  }
}
````

### 附录 C：F1-VD-03

目标路径：`schemas/saee-development-constitution.schema.v1.1.json`

目标 `SHA-256`：`dc2d259a0936d0dc0d74b6279c840cfd62e524c9a7e88db56247995ab0b31d86`

````json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://saee.local/schemas/saee-development-constitution.schema.v1.1.json",
  "title": "SAEE Development Constitution v1.1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "$schema",
    "constitution_id",
    "version",
    "authority",
    "mission",
    "program_tasks",
    "target_customer_versions",
    "evolution_loop",
    "agent_readable_rule",
    "evidence_subsystem_integration",
    "development_gates",
    "external_action_boundary",
    "truth_boundary"
  ],
  "properties": {
    "$schema": {"type": "string", "const": "../../schemas/saee-development-constitution.schema.v1.1.json"},
    "constitution_id": {"type": "string", "const": "saee-development-constitution-v1.1"},
    "version": {"type": "string", "const": "1.1.1"},
    "authority": {
      "type": "object",
      "additionalProperties": false,
      "required": ["canonical_document", "effective_date", "engineering_core", "theory_identity"],
      "properties": {
        "canonical_document": {"type": "string"},
        "effective_date": {"type": "string", "format": "date"},
        "engineering_core": {"type": "string", "const": "Digital Biosphere Evolution Engine"},
        "theory_identity": {"type": "string", "const": "Silicon-Amplified Evolutionary Ecology"}
      }
    },
    "mission": {
      "type": "object",
      "additionalProperties": false,
      "required": ["primary", "evidence_role", "audit_first_reframe"],
      "properties": {
        "primary": {"type": "string"},
        "evidence_role": {"type": "string", "const": "supports_evolutionary_selection_archive_and_rollback"},
        "audit_first_reframe": {"type": "boolean", "const": false}
      }
    },
    "program_tasks": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "mainline",
        "secondary",
        "secondary_cannot_displace_mainline",
        "self_assessment_cannot_self_approve",
        "role_prompt_cannot_override_mainline",
        "drift_response"
      ],
      "properties": {
        "mainline": {"type": "string", "const": "integrate_saee_and_agent_evidence_project_under_migration_gates"},
        "secondary": {"type": "string", "const": "use_saee_to_supervise_and_test_the_integration_process"},
        "secondary_cannot_displace_mainline": {"type": "boolean", "const": true},
        "self_assessment_cannot_self_approve": {"type": "boolean", "const": true},
        "role_prompt_cannot_override_mainline": {"type": "boolean", "const": true},
        "drift_response": {"type": "string", "const": "raise_correction_recommendation"}
      }
    },
    "target_customer_versions": {
      "type": "array",
      "minItems": 3,
      "maxItems": 3,
      "uniqueItems": true,
      "prefixItems": [
        {"const": "SAEE Evidence"},
        {"const": "SAEE Evaluation"},
        {"const": "SAEE Governance"}
      ],
      "items": false
    },
    "evolution_loop": {
      "type": "array",
      "minItems": 9,
      "maxItems": 9,
      "uniqueItems": true,
      "items": {"type": "string"}
    },
    "agent_readable_rule": {
      "type": "object",
      "additionalProperties": false,
      "required": ["required", "first_class_surfaces"],
      "properties": {
        "required": {"type": "boolean", "const": true},
        "first_class_surfaces": {"type": "array", "minItems": 7, "uniqueItems": true, "items": {"type": "string"}}
      }
    },
    "evidence_subsystem_integration": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "project_name",
        "legacy_product_name",
        "legacy_source_repository_name",
        "saee_role",
        "overall_classification",
        "constitutional_ownership",
        "source_code_adoption",
        "runtime_integration",
        "canonical_inventory_change",
        "capabilities_to_resolve_at_read_time",
        "claims",
        "non_claims"
      ],
      "properties": {
        "project_name": {"type": "string", "const": "Agent Evidence Project"},
        "legacy_product_name": {"type": "string", "const": "Agent Evidence Receipt"},
        "legacy_source_repository_name": {"type": "string", "const": "agent-evidence-layer"},
        "saee_role": {"type": "string", "const": "evidence_and_immune_subsystem"},
        "overall_classification": {"type": "string", "enum": ["implemented", "partial", "design_only", "missing", "deprecated", "superseded"]},
        "constitutional_ownership": {"type": "string", "const": "implemented"},
        "source_code_adoption": {"type": "string", "const": "not_performed"},
        "runtime_integration": {"type": "string", "const": "not_performed"},
        "canonical_inventory_change": {"type": "string", "const": "none_this_change"},
        "capabilities_to_resolve_at_read_time": {"type": "array", "minItems": 3, "uniqueItems": true, "items": {"type": "string"}},
        "claims": {"type": "array", "minItems": 2, "items": {"type": "string"}},
        "non_claims": {"type": "array", "minItems": 8, "items": {"type": "string"}}
      }
    },
    "development_gates": {"type": "array", "minItems": 7, "uniqueItems": true, "items": {"type": "string"}},
    "external_action_boundary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["observes_world", "executes_world", "decision_context_is_authority", "explicit_authorization_required"],
      "properties": {
        "observes_world": {"type": "boolean", "const": true},
        "executes_world": {"type": "boolean", "const": false},
        "decision_context_is_authority": {"type": "boolean", "const": false},
        "explicit_authorization_required": {"type": "boolean", "const": true}
      }
    },
    "truth_boundary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["source_code_migrated", "runtime_integrated", "external_integration_validated", "customer_validated", "product_launched", "production_ready"],
      "properties": {
        "source_code_migrated": {"type": "boolean", "const": false},
        "runtime_integrated": {"type": "boolean", "const": false},
        "external_integration_validated": {"type": "boolean", "const": false},
        "customer_validated": {"type": "boolean", "const": false},
        "product_launched": {"type": "boolean", "const": false},
        "production_ready": {"type": "boolean", "const": false}
      }
    }
  }
}
````

### 附录 D：F1-VD-04

目标路径：`docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`

目标 `SHA-256`：`37d9adb3049c5fdd871460f6756240a177264e4442cc38252786e9d7c86f378c`

````markdown
# SAEE 开发宪法 v1.1

## SAEE Development Constitution v1.1

```text
constitution_id=saee-development-constitution-v1.1
effective_date=2026-07-14
authority=repository_development_governance
engineering_core=Digital Biosphere Evolution Engine
agent_evidence_project_role=evidence_and_immune_subsystem
audit_first_reframe=false
external_world_execution=false
production_ready=false
program_mainline=saee_agent_evidence_integration
program_secondary=saee_supervises_and_tests_integration
target_customer_versions=SAEE_Evidence;SAEE_Evaluation;SAEE_Governance
```

机器契约：`agent-interface/governance/saee-development-constitution.v1.1.json`<br>
Schema：`schemas/saee-development-constitution.schema.v1.1.json`<br>
推荐门：`docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md`<br>
确定性校验：`python3 scripts/saee_development_constitution_smoke.py`

## 序言：宪法解决什么

本宪法是 SAEE 的产品真源约束、技术方向约束、Codex 工作规则、变更审查标准和架构决策依据。它约束未来开发，不以人员配置、融资计划、组织规模或销售流程作为技术优先级依据。

智能体的发现、理解、调用、验证和推荐是能力方向的主要验证结果；人员不是能力偏好或技术战略完成的前置条件。对外联系、客户数据、合同、定价、权限扩张、生产部署和重大公开声明仍属于后果性外部动作，必须经过独立的明确授权门。

## 第一章：最高身份与根本使命

### 第一条：最高身份

SAEE 的理论身份是 `Silicon-Amplified Evolutionary Ecology`，工程核心是 `Digital Biosphere Evolution Engine`。

SAEE 的根本使命不是单独判断一项 Agent 行动是否具有证据，而是构造一个受控数字生物圈，使候选系统能够被感知、提取性状、建模、反事实模拟、分叉、变异、沙盒发育、选择、归档和回滚。

证据评估服务于演化选择和回滚免疫，不得取代演化闭环成为项目唯一使命。

### 第二条：唯一允许的核心闭环

每次修改必须强化至少一个环节：

1. Global Sensing（全球感知）
2. Trait Extraction（性状提取）
3. Ecological World Model（生态世界模型）
4. Counterfactual Simulation（反事实模拟）
5. Genome Branching（基因型分叉）
6. Controlled Mutation / Recombination（受控变异 / 重组）
7. Sandbox Development（沙盒发育）
8. Pareto Fitness Evaluation（帕累托适应度评估）
9. Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）

如果无法说明强化哪一环，停止编码并先写 evolution proposal（演化提案）。

## 第二章：Agent-Readable First

### 第三条：智能体可读层是一级产品表面

协议、schema、能力清单、模块边界、状态、示例、CLI / Tool 接口、非主张和离线校验器必须文件化、可发现、可解析、可调用、可引用。

行为改变必须在同一次变更中同步相关 README、schema、`agent-index.json`、`llms.txt`、能力清单或设计说明。隐藏约定不得成为唯一契约。

### 第四条：能力进入优先级前的三个问题

1. 智能体能否发现这项能力？
2. 智能体能否理解何时使用、何时不使用？
3. 智能体能否通过稳定契约把它组合进工作流？

任一答案不是明确的 `yes` 时，默认降低优先级；安全、法律、供应链完整性或架构必需项除外，但必须记录例外和缺失的智能体可读工作。

## 第三章：智能体证据项目正式归属

### 第五条：归属决定

`Agent Evidence Project`（历史产品名 `Agent Evidence Receipt`，历史源仓库名 `agent-evidence-layer`）从本宪法起不再被定义为 SAEE 的平行竞争产品。它在 SAEE 中的正式角色是：

```text
SAEE Evidence and Immune Subsystem
SAEE 证据与免疫子系统
```

该归属是架构和治理层的正式合并。源代码历史、许可证、commit、发布记录和独立仓库可以在完成迁移门之前保留，不得用品牌归属替代代码来源证明。

### 第六条：在演化闭环中的位置

```text
Observation / Rehearsal Output
              ↓
Normalization + Provenance Envelope
              ↓
Evidence Object / Evidence Receipt
              ↓
Integrity + Completeness Verification
              ↓
Evidence Adequacy Evaluation
              ↓
Fitness Context / Selection Evidence
              ↓
Evolutionary Archive / Rollback Decision
```

证据子系统为 sensing、simulation、fitness、archive 和 rollback 提供可复核上下文。它不得直接批准、拒绝或执行外部世界动作。

### 第七条：纳入范围

允许纳入的职责：

- 规范化后的 Agent 运行事件与 artifact 清单；
- Evidence Object、Evidence Receipt 和 verification receipt；
- canonicalization、digest、签名验证结果、provenance 和 source completeness；
- 证据引用、组合、确定性校验和篡改检测；
- 为 Evidence Adequacy、fitness selection、lineage archive 和 rollback 提供输入。

不得由此推导的职责：

- 通用 tracing / APM / observability 平台；
- IAM、OAuth、RBAC、Cloud IAM 或执行授权；
- 自动部署、Agent Runtime 或外部动作执行；
- 法律事实认定、合规认证或责任裁决；
- 仅凭 hash 或 signature 证明原始事件真实、完整或由声明主体产生。

`signature_valid=true` 最多说明被验证的签名关系成立；它不自动等于 `event_authentic=true`、`source_identity_authenticated=true`、`complete=true` 或 `legally_proven=true`。

### 第八条：当前分阶段真值

本次更新的目标分类是 `partial`：

- 宪法归属：`implemented`；
- SAEE 内已有 Evidence Adequacy、局部 receipt 与 observed-trace 能力：必须复用；
- `agent-evidence-layer` 源代码纳入 SAEE：`design_only`，本次未复制；
- 统一运行时接入：`missing`；
- 可信 trace 到 evidence 的完整转换：以 `capability-package/manifest.json#canonical_inventory` 的实时状态为准；
- 外部互操作、客户验证与生产就绪：未由本宪法建立。

```text
source_code_migrated=false
runtime_integrated=false
external_integration_validated=false
customer_validated=false
product_launched=false
production_ready=false
```

能力事实只能从规范清单读取。本节不得被解释为对 `canonical_inventory` 的替代快照。

## 第四章：防重复建设与迁移纪律

### 第九条：先复用，再迁移，最后才新增

任何证据项目代码迁移前，必须先解析并复用以下规范能力或其后继项：

- `saee.evaluate_evidence`；
- `saee.general_trace_normalization`；
- `saee.trusted_trace_to_evidence_conversion`；
- `saee_backend/services/resource_resolution_receipt.py`；
- `agent-interface/schemas/*receipt*`；
- `docs/standards/SAEE_AGENT_RECEIPT_*`。

存在等价实现时，不得复制一份新实现。只能选择规范路由、adapter、合并、迁移或废弃，并用 ADR 记录来源、许可证、兼容性、替代关系和删除条件。

### 第十条：证据项目迁移门

1. `CONSTITUTIONAL_INTEGRATION`：本宪法和机器契约通过校验。
2. `SOURCE_PROVENANCE_FREEZE`：从干净、可复现的 source commit 建立文件和许可证 manifest。
3. `SCHEMA_CROSSWALK`：逐项判定 reuse / adapt / migrate / deprecate，禁止整仓复制。
4. `INTERNAL_ADAPTER`：只在 SAEE 内部边界接入，保持无外部执行和最小权限。
5. `CANONICAL_CAPABILITY_UPDATE`：代码、schema、测试、Agent-readable 表面和台账一致后，才能先改规范清单再改机器投影。
6. `EXTERNAL_VALIDATION`：与本地测试、合成 pass、package-ready、customer validation 和 production readiness 分开记录。

未通过前一门，不得宣称后一门完成。

## 第五章：标准优先但不虚构合规

### 第十一条：标准对齐顺序

在适用且已核对具体版本时，优先使用：

- OpenTelemetry：trace 与 resource 语义；
- MCP：Agent 能力发现和调用运输；
- JSON Schema：对象交换与离线验证；
- SPDX / CycloneDX：来源、许可证与供应链描述。

概念相似不等于合规，mapping 不等于 adoption，local validation 不等于 interoperability。任何外部标准声明必须记录规范版本、来源、字段 crosswalk、差异和测试证据。

## 第六章：开发前强制协议

### 第十二条：每次修改必须先回答

1. 影响哪个演化子系统？
2. 是否改善 sensing、branching、variation、selection、archive 或 rollback？
3. 影响哪个规范对象、schema、接口或 capability？
4. 规范清单当前把目标分类为什么？
5. 是否存在可复用实现；删除或废弃什么重复能力？
6. 智能体是否会向目标需求推荐 SAEE；若不是 `recommend`，阻塞点如何拆解？
7. 是否保持 safety、license、supply-chain 和 permission 边界？
8. 是否把项目推回 audit-first 或 generic agent framework？
9. 本次明确的 claims、non-claims 和 staged truth 是什么？
10. 哪些确定性、negative 和 schema 校验证明变更成立？

无法回答时，不得修改行为代码。

### 第十三条：Codex 启动句

未来 SAEE 修改任务应从以下约束开始：

```text
You are modifying SAEE under SAEE Development Constitution v1.1.
Resolve the canonical capability inventory, run duplicate-build validation,
identify the affected evolution subsystem, execute the Agent Recommendation
Gate, define claims and non-claims, preserve staged truth, and run deterministic
validation before completion.
```

## 第七章：测试与真值宪法

### 第十四条：可验证、可解释、可限制

每项能力必须具有 schema validation、negative cases、deterministic validation、稳定 reason code 或等价解释，以及明确 non-claims。

以下状态永久分开：

```text
design_only
local_implementation
synthetic_pass
package_ready
external_integration
customer_validated
production_ready
```

不得从前一状态自动升级到后一状态。

## 第八章：不可逾越边界

### 第十五条：数字生物可观察世界，但不得执行世界

SAEE 可以接收受控观察、模拟、评估和归档材料，但不得自动：

- 执行未知外部仓库或安装脚本；
- 扩大权限；
- 把外部代码复制为 genome；
- 联系客户或使用客户/个人数据；
- 批准部署、签署合同、发布重大声明或执行现实动作。

提取 traits，不复制 code。Evidence 和 Evaluation 产生 decision context，不产生 execution authority。

## 第九章：修宪与执行

### 第十六条：宪法优先级

本宪法低于安全、法律和显式用户授权边界，高于 roadmap、商业计划、历史推荐字段和局部模块惯例。发生冲突时，先停止修改并记录 ADR 或修宪提案。

### 第十七条：修宪条件

修宪必须同时更新：

- 本文件；
- `agent-interface/governance/saee-development-constitution.v1.1.json` 或其后继版本；
- `AGENTS.md` 与 `llms.txt` 的权威指针；
- `agent-index.json` 的机器入口；
- 推荐门和确定性 smoke。

修宪本身不更新任何能力实现状态。能力事实仍必须先更新 `capability-package/manifest.json#canonical_inventory`，再同步 `agent-index.json#capability_progress_ledger_v1`。

## 第十章：主线任务、客户版本与纠偏义务

### 第十八条：当前项目主线

SAEE 当前项目主线是：在保留来源、许可证、供应链、权限、runtime 和 staged truth
边界的前提下，完成 SAEE 与 Agent Evidence Project 的受控合并。

这里的“合并”不是整仓复制，也不是用架构归属冒充代码迁移完成。它必须依次通过
source provenance freeze、schema crosswalk、reuse/adapt/migrate/deprecate 判定、内部
adapter、canonical capability update 和外部验证门。

```text
program_mainline=saee_agent_evidence_integration
merge_completed=false
source_code_migrated=false
runtime_integrated=false
```

Digital Biosphere Evolution Engine 仍是工程核心；当前主线说明项目正在完成什么，不把
SAEE 重构为 audit-first system。

### 第十九条：最终三个客户版本目标

受控合并完成后的目标客户版本固定为三个：

1. `SAEE Evidence`：面向证据对象、收据、来源、完整性与免疫档案的客户版本。
2. `SAEE Evaluation`：面向就绪度、证据充分性、可靠性与选择上下文的客户版本。
3. `SAEE Governance`：面向受控变更、决策边界、演化档案与回滚治理的客户版本。

这是 target product family（目标产品族），不是当前发布状态。除非规范产品注册表、
代码、契约、测试、客户验证和发布证据一致，不得声称三个版本已经实现、可购买、已
发布或生产就绪。

```text
target_customer_version_count=3
target_customer_versions=SAEE_Evidence;SAEE_Evaluation;SAEE_Governance
three_versions_implemented=false
three_versions_customer_validated=false
three_versions_product_launched=false
```

### 第二十条：副线任务与 Dogfooding 边界

副线任务是利用 SAEE 监督、测试并评估 SAEE 与 Agent Evidence 的合并过程。这既是
合并治理，也是对 SAEE 自身 sensing、evaluation、archive 和 rollback 能力的测试。

副线只能产生 evidence、assessment、drift signal 和 correction recommendation；不能
批准自己的变更，也不能取代主线。不得因为治理报告、validator、Dogfooding 或测试
数量增长，就把“监督测试合并”改写为项目最终目标。

```text
program_secondary=saee_supervises_and_tests_integration
secondary_displaces_mainline=false
self_assessment_authorizes_change=false
```

### 第二十一条：指令漂移纠偏

Commander、role prompt、roadmap、历史报告或局部任务说明都不能覆盖本章主线。任何
AI Agent 发现任务把治理、测试、审计、商业表面或其他副线提升为主线，或者让合并
失去受控迁移边界时，必须：

1. 明确输出 `MAINLINE_DRIFT_DETECTED`；
2. 指出偏离了哪一条主线或 truth boundary；
3. 提出回到“受控合并 → 三个客户版本目标”的修正建议；
4. 在人类明确修改宪法前，不得用角色服从替代宪法判断。

纠偏义务不授权 Agent 拒绝安全、法律或明确人类外部动作 gate，也不授权自行执行代码
迁移、发布或部署。
````

### 附录 E：F1-VD-05

目标路径：`docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md`

目标 `SHA-256`：`1bc493e03e3158e2d984308a78efa80cde131a5b9ee2142449695c807433ee9c`

````markdown
# SAEE 开发宪法 v1.1 推荐门

## Initial Result

```yaml
recommendation_gate:
  feature_or_direction: SAEE Development Constitution v1.1 and Agent Evidence Project integration
  target_customer_need: 让智能体能够发现、组合并复核 SAEE 的演化评估与证据能力，同时防止重复建设和证据优先重构
  answer: conditional
  reasons_to_recommend:
    - Agent Evidence Project 的 receipt、integrity、provenance 和 completeness 能力可强化 Evolutionary Archive / Rollback Immune System
    - 文件化宪法可让编码、检索和引用智能体在修改前解析同一组边界
  reasons_not_to_recommend:
    - 旧 v1.0 草案把可信证据判断写成 SAEE 唯一使命，会把 Digital Biosphere Evolution Engine 推回 audit-first
    - SAEE 已有 evaluate_evidence、receipt 和局部 trace normalization，直接复制会重复建设
    - agent-evidence-layer 当前不能作为已完成迁移或规范 SAEE capability 的证据
    - signature 与 digest 不能证明原始事件真实性、身份真实性或记录完整性
  decomposition:
    - blocker: audit_first_identity_conflict
      subsystem: architecture_governance
      fix_task: 恢复 Digital Biosphere Evolution Engine 为最高工程核心，把证据放入免疫子系统
      acceptance_criteria: 宪法和机器契约同时声明 audit_first_reframe=false
      status: fixed
    - blocker: duplicate_implementation_risk
      subsystem: capability_governance
      fix_task: 强制读取 canonical_inventory 并列出必须复用的规范能力
      acceptance_criteria: 台账 smoke 通过且宪法包含 reuse-before-build 迁移门
      status: fixed
    - blocker: source_provenance_not_frozen
      subsystem: evidence_and_immune_subsystem
      fix_task: 未来从干净 commit 生成 source/license manifest 后再做逐文件迁移
      acceptance_criteria: SOURCE_PROVENANCE_FREEZE gate 有可复现 manifest
      status: deferred
    - blocker: runtime_and_trust_chain_missing
      subsystem: evidence_and_immune_subsystem
      fix_task: 未来以 adapter 和 canonical inventory 变更分别证明运行时接入与 trusted trace conversion
      acceptance_criteria: code、schema、tests、Agent-readable surfaces 与 ledger 一致
      status: deferred
    - blocker: staged_truth_ambiguity
      subsystem: architecture_governance
      fix_task: 将宪法归属、代码迁移、运行时接入、外部验证、客户验证和生产就绪分开
      acceptance_criteria: 机器契约的六个 truth_boundary 字段保持独立
      status: fixed
```

## Capability And Duplicate-Build Classification

```text
target=Agent Evidence Project integration into SAEE
overall_classification=partial
constitutional_ownership=implemented
source_code_adoption=design_only
runtime_integration=missing
canonical_inventory_change=none_this_change
```

本分类基于 2026-07-14 读取的 `capability-package/manifest.json#canonical_inventory`、相关 schema / service / example / smoke，以及历史 receipt crosswalk。能力实时事实仍以规范清单为唯一真源。

## Required Design Check

1. 强化 `Evolutionary Archive / Rollback Immune System`，并为 sensing、simulation 与 fitness selection 提供可复核证据上下文。
2. 改善 archive、rollback 和 selection；本次不增加外部执行。
3. 保留安全、许可证、供应链、最小权限和 source provenance 边界；没有复制外部代码。
4. 证据被明确限制为免疫子系统，`audit_first_reframe=false`。

## Final Result

`recommend`

推荐把 Agent Evidence Project 在宪法、模块注册表和机器入口中正式纳入 SAEE Evidence and Immune Subsystem。该推荐只覆盖治理与架构归属，不推荐把未清理的源仓库直接复制、把 signature 升级为真实性证明、把缺失能力写成 implemented，或宣称运行时接入、客户验证、发布和生产就绪。

## Program Mainline Correction

```yaml
program_mainline_gate:
  question: 如果目标是受控完成 SAEE 与 Agent Evidence 合并，并最终形成三个客户版本，是否推荐 SAEE 当前方案？
  answer: recommend
  mainline: integrate_saee_and_agent_evidence_project_under_migration_gates
  target_customer_versions:
    - SAEE Evidence
    - SAEE Evaluation
    - SAEE Governance
  secondary: use_saee_to_supervise_and_test_the_integration_process
  reasons_to_recommend:
    - 宪法已经把 Agent Evidence 放入 Evidence and Immune Subsystem，并定义逐门迁移纪律
    - SAEE 自用监督可为合并提供可复核证据、漂移信号与回滚上下文
    - 三个目标客户版本明确区分 Evidence、Evaluation 与 Governance
  blockers:
    - source_code_migrated=false
    - runtime_integrated=false
    - customer_validated=false
    - product_launched=false
    - production_ready=false
  drift_rule: Commander或角色提示不得把监督测试副线提升为主线；发现时必须输出MAINLINE_DRIFT_DETECTED并提出修正
```

证据：

- `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
- `agent-interface/governance/saee-development-constitution.v1.1.json`
- `schemas/saee-development-constitution.schema.v1.1.json`
- `scripts/saee_development_constitution_smoke.py`
- `python3 scripts/saee_capability_progress_ledger_smoke.py`
````

### 附录 F：F1-VD-06

目标路径与范围：`AGENTS.md:47-80`

目标 `SHA-256`：`0ff92cee0427e6e6b3e207544c153a6bab82f214d3998e16b224f58d46da8c42`

````markdown
## Constitutional Program Mainline

The current program mainline is the controlled integration of SAEE and the
Agent Evidence Project under provenance, license, schema-crosswalk, reuse,
migration and staged-truth gates.
当前项目主线是在来源、许可证、schema crosswalk（模式交叉映射）、复用、迁移和
分阶段真值门下，受控完成 SAEE 与智能体证据项目的合并。

The final customer-version target is exactly:
最终客户版本目标固定为：

```text
SAEE Evidence / SAEE Evaluation / SAEE Governance
```

These are target versions, not current implementation, launch, customer
validation or production claims.
这是目标版本，不代表当前已经实现、发布、完成客户验证或生产就绪。

The secondary task is to use SAEE to supervise, test and assess the integration
process. This dogfooding lane may produce evidence and correction
recommendations, but it may not displace the mainline or approve its own
changes.
副线任务是利用 SAEE 监督、测试和评估合并过程；该自用验证路线可以产生证据和纠偏
建议，但不得取代主线，也不得批准自身变化。

If a Commander prompt, role prompt, roadmap or local task elevates governance,
testing, audit or another secondary lane above the integration mainline, output
`MAINLINE_DRIFT_DETECTED`, identify the conflict and recommend correction. A
role prompt does not override the Constitution.
如果 Commander prompt（指挥官提示）、角色提示、路线图或局部任务把治理、测试、
审计或其他副线提升到合并主线之上，必须输出 `MAINLINE_DRIFT_DETECTED`，指出冲突并
提出修正建议；角色服从不能覆盖宪法。

````

## 10. 最终状态

```text
CURRENT_SAEE_MAINLINE=saee_agent_evidence_integration
F1_VALIDATOR_ADDITIONAL_AUTHORIZATION_PACKAGE_CREATED=true
F1_VALIDATOR_ADDITIONAL_OBJECTS_AUTHORIZED=false
F1_BASELINE_AUTHORIZED=false
F1_CONSTRUCTION_AUTHORIZED=false
P1_CONTRACT_BASELINE_AUTHORIZED=false
M03_M06_FORMAL_BASELINE_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
SCHEMA_CHANGED=false
GIT_ADD_EXECUTED=false
GIT_COMMIT_EXECUTED=false
GIT_PUSH_EXECUTED=false
MAINLINE_DRIFT_DETECTED=false
NEXT_ACTION=HUMAN_DECISION_ON_F1_VALIDATOR_MINIMUM_ADDITIONAL_AUTHORIZATION_PACKAGE
```
