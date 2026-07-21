# SAEE Constitution Authority Migration Checklist

```text
checklist_id=SAEE_CONSTITUTION_AUTHORITY_MIGRATION_CHECKLIST
current_phase=Phase_0.5.4
checklist_status=PREPARATION_COMPLETE_FUTURE_GATES_OPEN
migration_ready=false
authority_switch_authorized=false
authority_switch_executed=false
```

勾选项只表示可验证事实，不表示后续阶段被授权。未勾选项不得由计划、draft 或 validator
PASS 自动视为完成。

## Phase 0.5.4 — Preparation package

- [x] 收到 `V2-F-001` 至 `V2-F-005` 的明确人工批准，作为本准备包输入。
- [x] 收到 Phase 0.5.4 文件范围授权。
- [x] 读取 v1.1、V2 Decision Packet、migration plan、Project Memory、Frozen Decisions、
  canonical inventory 与 `AGENTS.md`。
- [x] 创建 non-normative successor draft。
- [x] 创建 authority pointer map、term crosswalk、shadow validation plan 与本 checklist。
- [x] 保持 v1.1 active authority、capability facts、schema、MCP、code 与 product status 不变。
- [ ] 把本准备包误写为 active v2 authority（必须保持未勾选）。

## Before migration

### Human approval

- [x] 五项 V2 设计决定已获人工批准。
- [ ] 通过受控 DCP/decision log 将 approved/frozen 状态同步到既有 Project Memory 真值面。
- [ ] 人工批准具体 v2 version、完整 successor file allowlist 与 owner。
- [ ] 人工批准 Phase 0.5.5 shadow validation 执行。
- [ ] 人工批准 future authority activation batch。

### History stable

- [ ] Phase 0.5 formal-history blockers 已在独立流程关闭。
- [ ] 使用 clean、isolated、reproducible migration branch/worktree。
- [ ] 记录 HEAD、branch、status、tracked/untracked scope 与 baseline hashes。
- [ ] v1.1 Constitution、contract、schema、gate、validator 与历史 commit 均有不可变 baseline。
- [ ] rollback owner、验收人和 correction-commit 流程已确认。

### Truth surfaces aligned

- [ ] approved decisions、Frozen Decisions、decision log 与 active questions 一致。
- [ ] current authority pointers 全部一致指向 v1.1。
- [ ] canonical inventory digest 已记录，authority batch expected change 为 `NO_CHANGE`。
- [ ] target customer versions 恰为 Evidence / Evaluation / Governance。
- [ ] Autonomous 仅为 future horizon。
- [ ] Agent Evidence source/runtime/external/product staged truth 未被升级。
- [ ] MCP canonical/compatibility/internal 分类 baseline 已记录。

### Validators ready

- [x] v1.1 deterministic validator 已存在。
- [x] governance、Project Memory 与 capability-ledger validators 已存在。
- [ ] 具体 v2 closed schema 与 deterministic validator 已建立并通过正/负例。
- [ ] Authority Consistency Check 已建立并通过 mixed-pointer negative cases。
- [ ] shadow evidence package schema、reason codes 与 deterministic repeatability 已确认。

## During migration

### Successor added

- [ ] 新增具体版本的 v2 Constitution；不覆盖 v1.1。
- [ ] 新增匹配的 machine contract、closed schema、recommendation gate 与 validator。
- [ ] 记录 `supersedes` relationship、effective commit 候选与 historical status。
- [ ] v1.1 与 v2 shadow validation 同时 PASS。
- [ ] canonical inventory before/after digest 相同。

### Pointer update

- [ ] 获得独立 activation authorization。
- [ ] 在一个原子 batch 内更新全部 active pointer surfaces。
- [ ] 无 mixed v1.1/v2 active pointers。
- [ ] `mainline_guard.py` 同时保留 mainline、history 与 consistency guard。
- [ ] 未混入 capability、MCP、code、product、website 或 ecosystem change。

### Schema validation and smoke tests

- [ ] v1.1 historical family validation PASS。
- [ ] v2 Constitution contract/schema validation PASS。
- [ ] identity、capability、product、term、non-claims、ecosystem assertions PASS。
- [ ] 所有 required negative cases 被确定性拒绝。
- [ ] governance registry、Project Memory、capability ledger 与 mainline guard PASS。
- [ ] `git diff --check` PASS，且 diff 只包含授权文件。

## After migration

### Authority check

- [ ] 所有 active pointers 指向同一具体 v2 family。
- [ ] v1.1 family 完整保留并明确 historical/superseded。
- [ ] effective commit、validation receipt 与 human approval 已记录。
- [ ] canonical capability facts、product/MCP/external-system staged truth 未被自动升级。

### Rollback test

- [ ] 用 disposable simulation 验证 correction/revert commit 可恢复全部 v1.1 active pointers。
- [ ] rollback 不删除 v2 artifacts、不重写历史、不使用 destructive reset。
- [ ] rollback 后 v1.1 validator、governance、ledger 与 mainline guard PASS。
- [ ] failure reason、rollback commit 与 unresolved blocker 可审计。

### Documentation sync

- [ ] `AGENTS.md`、`.codex/`、`llms.txt`、README、governance README 与 `agent-index.json`
  authority entries 一致。
- [ ] Product Architecture、term crosswalk、Project Memory 与 registries 依次完成独立授权同步。
- [ ] 新 authority 文本不使用未限定历史缩写；历史资产名称仍可检索和引用。
- [ ] 三个客户版本及 Autonomous non-claim 一致。
- [ ] 生态材料保持 capability/interface/channel 分层与 staged truth。

## Current gate result

```text
PREPARATION_PACKAGE_CREATED=true
V2_DECISIONS=APPROVED
HISTORY_STABLE=NOT_CONFIRMED
TRUTH_SURFACES_ALIGNED=NOT_COMPLETE
V2_VALIDATORS_READY=false
SHADOW_VALIDATION_EXECUTED=false
MIGRATION_READY=false
AUTHORITY_SWITCH=NOT_EXECUTED
NEXT_ACTION=SHADOW_VALIDATION_REVIEW
```
