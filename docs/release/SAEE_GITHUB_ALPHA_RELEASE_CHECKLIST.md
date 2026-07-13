# SAEE GitHub Alpha Release Checklist

本清单是人工发布门，不执行发布动作。

| 检查项 | 状态 | 证据/说明 |
|---|---|---|
| README complete | PASS | `release/saee-agent-reliability-framework-alpha-v0.1/README.md` |
| LICENSE checked | **HOLD** | 仓库根目录未发现 `LICENSE`；必须由维护者选择许可证。 |
| version tagged | NOT_CREATED | 禁止在本任务中执行 `git tag`。 |
| examples runnable | LOCAL_VALIDATION_REQUIRED | `examples/public-demo/README.md` 与 Alpha smoke 提供本地入口。 |
| limitations clear | PASS | `release/saee-agent-reliability-framework-alpha-v0.1/limitations.md` |
| no secrets | LOCAL_SCAN_REQUIRED | 发布前需再次运行仓库范围敏感值检查。 |
| no unsupported claims | LOCAL_VALIDATION_REQUIRED | `scripts/saee_alpha_positioning_release_smoke.py` |
| external publication authorization | NOT_AUTHORIZED | 本任务不授权 push、PR 或 GitHub Release。 |

## 发布前人工门

只有在以下条件全部满足后，才能另行请求公开发布授权：

1. 维护者明确选择并添加许可证；
2. 本清单所有 `HOLD` 被关闭；
3. 验证命令全部通过；
4. 人工确认公开文件范围、版本号和发布说明；
5. 单独授权 `tag`、`push` 和 GitHub Release。

当前：`github_release_ready=false`、`github_release_created=false`。

