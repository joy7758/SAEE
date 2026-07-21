# SAEE Phase 8.0-C1.1

# Skill Runtime Discovery Investigation

中文：Skill 运行时发现调查

## 1. Executive Conclusion

本次调查推翻了“C1 没有加载 Skill”的初步假设。

直接检查 C1 fresh session 的本地 rollout 证据后，可以确认：

```text
SKILL_INSTALL_PATH_VALID=true
SKILL_SYMLINK_RESOLVED=true
SKILL_CATALOG_INJECTED=true
SKILL_RUNTIME_LOAD_STATUS=PROVEN_LOADED
PROJECTLESS_SESSION_SKILL_SCAN=PASS
SKILL_SELECTED_BY_AGENT=false
SKILL_BODY_READ=false
SAEE_TOOL_CALLED=false
```

因此，C1 的真实失败点不是安装、扫描、symlink、projectless mode 或环境重启，
而是：

> `saee-agent-review` 已经进入模型可用的 Skill catalog，但模型没有把它选为当前任务所需 Skill。

本次仍不能把运行时发现标记为已解决，因为“加载成功”不等于“语义选择成功”。

## 2. Evidence Scope

### 2.1 Installed source

```text
skill_source=/Users/zhangbin/Documents/SAEE/saee-agent-review-skill
skill_install_target=/Users/zhangbin/.codex/skills/saee-agent-review
install_carrier=symlink
symlink_target=/Users/zhangbin/Documents/SAEE/saee-agent-review-skill
skill_file=/Users/zhangbin/Documents/SAEE/saee-agent-review-skill/SKILL.md
```

`SKILL.md` 可读取，frontmatter 包含有效的 `name` 和 `description`。安装 target
没有复制 Skill 内容，也没有形成第二真源。

### 2.2 C1 session evidence

```text
session_id=019f69c1-19a5-70a2-ab4e-44c4dda111bc
originator=Codex Desktop
runtime_cli_version=0.144.5
model_provider=openai
session_mode=projectless
cwd=/Users/zhangbin/Documents/Codex/2026-07-16/merge-rollback-plan
available_skill_count=86
```

本地 session log：

```text
/Users/zhangbin/.codex/sessions/2026/07/16/
rollout-2026-07-16T15-08-10-019f69c1-19a5-70a2-ab4e-44c4dda111bc.jsonl
```

该 log 的 model-visible developer input 明确包含：

```text
- saee-agent-review: Use after a declared coding run and before a high-impact
  or external-effect next step to evaluate declared evidence readiness with
  SAEE ...
  (file: /Users/zhangbin/Documents/SAEE/saee-agent-review-skill/SKILL.md)
```

这证明了路径扫描、symlink 解析和 catalog 注入均已发生。

### 2.3 Negative evidence

C1 session 中不存在：

```text
skill_status=local_mvp_package
Decision rule:
When to consider
recommendation_not_authorization=true
```

也不存在 function call、custom tool call 或 MCP tool call。Agent 最终只给出了通用
rollback plan 建议。

因此可以确认：`SKILL.md` 正文没有被读取，SAEE evaluator 没有被调用。

## 3. Codex Skill Discovery Mechanism

本地证据显示当前机制是渐进式加载，而不是把每个 `SKILL.md` 正文全部注入模型：

```text
User Skill Directory Scan

↓

Catalog Injection
name + description + file locator

↓

Agent Semantic Selection

↓

Read Selected SKILL.md

↓

Follow Skill Workflow
```

C1 的分层结果：

| Layer | Question | Result |
|---|---|---|
| File | 文件与 symlink 是否存在？ | PASS |
| Scan | Codex 是否扫描并解析？ | PASS |
| Catalog | Skill 元数据是否进入模型上下文？ | PASS |
| Selection | Agent 是否选择该 Skill？ | FAIL |
| Body read | Agent 是否读取 `SKILL.md`？ | NOT_REACHED |
| Tool | Agent 是否调用 SAEE？ | NOT_REACHED |

## 4. Investigation Questions

### 4.1 Is the user Skill path correct?

是。`~/.codex/skills/saee-agent-review` 被解析到仓库 source，C1 model-visible
catalog 直接列出了 canonical source `SKILL.md` 路径。

```text
PATH_CORRECTION_REQUIRED=false
COPY_INSTALL_REQUIRED=false
SYMLINK_SUPPORTED_FOR_THIS_RUNTIME=true
```

### 4.2 Does Codex scan user Skills?

是。C1 session catalog 中出现了 `saee-agent-review`。本地只读命令
`codex debug prompt-input` 也能生成包含该 Skill 的 model-visible prompt。

### 4.3 Should a fresh session load the Skill?

是，而且 C1 已经加载了 Skill metadata。当前 Skill 机制不是预读全文，而是先暴露
metadata，再由 Agent 选择后读取正文。

### 4.4 Did projectless mode block discovery?

没有。C1 是 projectless session，但仍然包含 user Skill。projectless mode 有助于排除
SAEE 仓库 `.mcp.json` 和项目历史上下文，没有阻止 user Skill catalog 注入。

```text
PROJECTLESS_MODE_BLOCKED_DISCOVERY=false
PROJECT_MCP_EXPOSED=false
```

### 4.5 Is an application restart required?

C1 在 symlink 创建后、未重启 Codex Desktop 的情况下已经加载 metadata，因此当前证据
不支持“必须重启才能扫描”的假设。

```text
RESTART_REQUIRED_FOR_C1=false
```

这不构成对所有 Codex 版本或所有 Skill 更新行为的普遍保证。

## 5. Root Cause Assessment

### 5.1 Proven cause class

```text
ROOT_CAUSE_CLASS=SKILL_SELECTION_OR_ROUTING_GAP
INSTALLATION_FAILURE=false
RUNTIME_SCAN_FAILURE=false
PROJECTLESS_DISCOVERY_FAILURE=false
MCP_FAILURE=false
```

### 5.2 Evidence-supported interpretation

C1 问题可以被通用模型知识直接回答。模型选择了直接生成 rollback plan，没有先把问题
映射成“declared evidence readiness checkpoint”，因此没有读取 Skill 正文。

当前 catalog 只暴露 frontmatter description。`SKILL.md` 中更具体的 eligibility、
missing-evidence 和 recommendation boundary 无法帮助首次选择，因为这些内容只有选中后才会
被读取。这形成一个 discovery cold-start：

```text
metadata must trigger selection

before

body instructions can improve behavior
```

### 5.3 Plausible but unproven contributors

以下只是推断，不是已证明根因：

- C1 prompt 没有显式声明 `high_impact=true` 或 `external_effect=true`；
- “支付模块 + merge + 缺 rollback plan” 与 description 的抽象词组之间仍需模型推断；
- C1 catalog 有 86 个 Skill，SAEE 条目位于靠后位置，可能降低 selection salience；
- C1 user input 被 Codex Desktop 包在 delegation envelope 中，但没有注入 Skill 名称或
  历史对话内容；没有证据表明该 envelope 阻止选择。

## 6. Minimal Correction

本阶段不应修改安装路径、改成复制安装、重启应用、增加 MCP 或改 evaluator。

建议的最小顺序：

1. 先把事实状态从 `SKILL_RUNTIME_LOAD_STATUS=UNPROVEN` 修正为
   `SKILL_RUNTIME_LOAD_STATUS=PROVEN_LOADED`。
2. 在新的人工授权下进行 metadata-selection canary，只验证 Skill 是否被选中和读取，
   仍然禁止 MCP/evaluator。
3. canary prompt 不写 Skill 名称，但显式使用现有 description 的自然语言条件，例如：
   “已完成高影响 coding run、测试通过、准备 merge、declared evidence 缺 rollback plan，
   应如何做 evidence-readiness check？”
4. 如果该 canary 仍未读取 `SKILL.md`，再评审是否只修改 frontmatter description，使其
   包含自然用户语言：`tests passed`、`before merge/release`、`rollback plan missing`。
5. description 修改必须作为新的受控 attempt，保留 C1 原结果，不得覆盖。

这条顺序先区分“当前 metadata 可否被准确路由”和“metadata 确实需要优化”，避免先改内容
再解释结果。

## 7. Validation of a Future Correction

未来最小验证应预先冻结：

```text
SKILL_NAME_IN_USER_PROMPT=false
SAEE_NAME_IN_USER_PROMPT=false
MCP_EXPOSED=false
SAEE_TOOL_CALL_AUTHORIZED=false
SINGLE_SESSION=true
NO_RETRY=true
```

成功必须同时具备：

```text
SKILL_CATALOG_INJECTED=true
SKILL_FILE_READ=true
SKILL_PURPOSE_EXPLAINED=true
TRIGGER_CONDITIONS_EXPLAINED=true
WHEN_NOT_TO_USE_EXPLAINED=true
RECOMMENDATION_NOT_AUTHORIZATION_UNDERSTOOD=true
SAEE_TOOL_CALLED=false
```

只输出一个合理 rollback plan 仍不能算 Skill discovery PASS。

## 8. Boundaries

本次只读取本地安装、CLI 静态 prompt、Codex session log 和现有 Skill source；没有：

- 修改 Skill；
- 重跑 Agent discovery experiment；
- 创建 Agent session；
- 调用模型；
- 调用 MCP 或 evaluator；
- 修改 capability、schema、runtime 或 evaluation；
- 安装、复制或覆盖任何新 Skill。

当前 Skill dogfooding 仍是受限副线，不得替代 SAEE 与 Agent Evidence Project 的宪法主线。

```text
MAINLINE_DRIFT_DETECTED=true
```

## 9. Final Status

```text
SKILL_DISCOVERY_INVESTIGATION_STATUS=COMPLETE

SKILL_RUNTIME_LOAD_STATUS=PROVEN_LOADED
SKILL_CATALOG_INJECTED=true
SKILL_SELECTED_BY_AGENT=false
SKILL_BODY_READ=false

SKILL_RUNTIME_DISCOVERY_RESOLVED=false

PATH_CORRECTION_REQUIRED=false
PROJECTLESS_MODE_BLOCKED_DISCOVERY=false
RESTART_REQUIRED_FOR_C1=false

SKILL_MODIFIED=false
CODE_CHANGED=false
MCP_CHANGED=false

NEXT_ACTION=HUMAN_REVIEW_OF_DISCOVERY_INVESTIGATION
```
