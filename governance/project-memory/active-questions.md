# Active Questions

本文件只记录尚未解决的问题。已有 Frozen Decision 的主题不得重复放入本文件。

## Q-001

问题：

Family A 如何安全形成独立提交？

状态：

OPEN

阻塞：

- Mainline Guard 可复现性和只读性修复尚未进入当前历史。
- Family A 当前只有 staged authorization，没有 commit authorization。
- Family A staged index 仍是 Constitution 1.1.0；明确人类指令产生的 1.1.1 主线修正当前保持 unstaged，旧 snapshot 已不是当前完整宪法。

下一证据：

在独立 stabilization branch/worktree 中前移既有幂等性修复，把 Family A 与
Constitution 1.1.1 主线修正按可审计顺序重建，连续验证主线后再申请提交授权。

---

## Q-002

问题：

Alibaba 商品 68657 的当前状态最终如何统一？

状态：

OPEN

阻塞：

当前项目记忆没有 L1 控制台证据，且历史表面包含 review、rejected/repair 等不同阶段表达。

下一证据：

由已授权的人类重新读取 Alibaba 控制台，记录带时间戳的权威状态，再单独治理 Family B。

---

## Q-003

问题：

Phase 1 Capability Alignment 何时启动？

状态：

BLOCKED

条件：

Phase 0.5 Gate 完成，Family A 与 Family B 历史边界可审计，且没有未解决的主线可复现性 blocker。

---

## Q-V2-002

问题：

是否正式启动 Constitution v2 authority migration？

状态：

BLOCKED

阻塞：

- `V2-F-001` 至 `V2-F-005` 已对齐为 `APPROVED_DESIGN_DIRECTION`，但不是 Frozen
  Decision、Constitution Amendment 或 active authority；
- 尚未建立 clean isolated `MIGRATION_BASELINE_COMMIT`；
- immutable input manifest、完整角色任命、rollback reference 与人类 G1
  reconfirmation 尚未完成；
- G1 仍未生效，Phase 0.5.7A 仍未授权，Authority Migration 未执行；
- Phase 0.5 状态与既有 formal-history blockers 未由本次决策事实对齐改变。

下一证据：

完成并独立验证 Pre-G1 baseline、manifest、role assignment 和 rollback reference 后，
由 Human Authority Owner 对精确 hashes、allowlist 和 scope 重新确认 G1。该确认最多授权
Commit A/B 的 inactive-family construction/validation，不自动授权 authority switch。
