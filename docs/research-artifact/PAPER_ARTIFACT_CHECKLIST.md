# SAEE Paper Artifact Checklist v0.1

状态：`local_paper_support_package_not_submitted`

## 研究定义

- [x] Research question 已定义；
- [x] 研究对象限定为 observation、evidence object、relationship adequacy 和 bounded claim evaluation；
- [x] 明确该架构是 SAEE 演化档案／回滚免疫子系统，不是项目核心重构；
- [x] 未声明新标准、规范采纳或系统优越性。

## 架构与材料

- [x] Architecture 已记录；
- [x] schemas、examples、fixtures、profiles、benchmarks、scripts、reproducibility 用途已记录；
- [x] 机器可读 artifact manifest 已建立；
- [x] 未来 Figure 1 至 Figure 4 的内容和禁止性表达已定义；
- [x] agent-readable README、`llms.txt` 和 `agent-index.json` 有发现入口。

## 实验

- [x] Experiments 已记录；
- [x] 12 个场景、4 类 claim、4 个证据级别已记录；
- [x] 5 PASS、7 FAIL、0 个策划数据集 false positive、0 个边界违规已记录；
- [x] 关系反例已说明；
- [x] Synthetic limitations 已明确；
- [x] 未把固定回归计数描述为现实准确率、性能或统计泛化。

## 复现

- [x] Commands 可由仓库现有 Makefile 发现；
- [x] Environment 已声明；
- [x] `jsonschema` 与 `pydantic` 依赖已声明；
- [x] Python 3.10 技术下限与正式支持状态已分离；
- [ ] 独立 clean-room 环境已复现；
- [ ] Python 固定版本矩阵已通过；
- [ ] 第三方已独立验证。

## 声明边界

- [x] Claims bounded；
- [x] No unsupported standards claims；
- [x] 未声明监管合规、法律有效性或认证；
- [x] 未声明真实发布者、真实审批或真实外部事件已经证明；
- [x] `production_ready=false`；
- [x] `external_validation=false`；
- [x] `publication_status=not_submitted`。

## 发布与投稿状态

- [ ] 论文草稿已完成；
- [ ] 作者已批准投稿；
- [ ] 论文已提交；
- [ ] arXiv 已上传；
- [ ] DOI 已创建；
- [ ] GitHub release 已创建；
- [ ] publication tag 已创建。

未勾选项是明确的后续工作或外部状态，不得从本地文件存在性推断为已经完成。
