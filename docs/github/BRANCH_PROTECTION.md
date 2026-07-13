# Branch Protection
# 分支保护

This file records GitHub settings that cannot be fully enforced by repository files alone.
本文件记录无法仅靠仓库文件完整执行的 GitHub 设置。

Enable these settings on the default branch after the repository is created on GitHub:
在 GitHub 创建仓库后，对默认分支启用以下设置：

- Require pull request before merging.
- 合并前必须创建 Pull Request（拉取请求）。
- Require review from Code Owners.
- 必须经过 CODEOWNERS（代码负责人）审核。
- Require status checks to pass.
- 必须通过状态检查。
- Require `Mainline Guard`.
- 必须通过 `Mainline Guard`。
- Require `Tests`.
- 必须通过 `Tests`。
- Restrict force pushes.
- 限制强制推送。

## Why This Exists

`AGENTS.md`, ADRs, and GitHub templates define the SAEE mainline. Branch protection makes those files harder to bypass.
`AGENTS.md`、ADR 和 GitHub 模板定义 SAEE 主线。分支保护让这些文件更难被绕过。

## Boundary

This local file does not prove GitHub branch protection is enabled.
此本地文件不证明 GitHub 分支保护已经启用。

Record live GitHub branch-protection evidence separately after the repository is published.
仓库发布后，应单独记录 GitHub 在线分支保护证据。

