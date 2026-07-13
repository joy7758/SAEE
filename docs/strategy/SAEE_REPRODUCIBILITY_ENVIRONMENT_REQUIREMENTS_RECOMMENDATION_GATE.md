# SAEE Reproducibility Environment Requirements v0.1 推荐门

```yaml
recommendation_gate:
  feature_or_direction: SAEE Reproducibility Environment Requirements v0.1
  target_customer_need: 在不依赖开发者机器隐含状态的前提下理解并检查本地合成研究产物验证环境
  answer: recommend
  reasons_to_recommend:
    - jsonschema 与 pydantic 已在现有依赖清单和机器可读 manifest 中显式声明
    - Python 语法下限、实际观察版本和未正式声明的支持范围被明确分开
    - 离线 smoke 不安装依赖、不联网、不创建虚拟环境、不执行外部命令
  reasons_not_to_recommend:
    - 不推荐把该能力表述为跨版本兼容、第三方复现、生产部署或认证
  decomposition:
    - blocker: jsonschema 仅存在于开发机而没有仓库依赖声明
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: 在 saee_backend/requirements.txt 与复现 manifest 中声明约束
      acceptance_criteria: 离线 smoke 同时确认依赖行和 manifest 字段
      status: fixed
    - blocker: 当前 Python 观察版本可能被误读为最低支持版本
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: 分离语法下限、观察版本和正式支持状态
      acceptance_criteria: manifest 和文档保留 not_formally_declared 及无版本矩阵边界
      status: fixed
    - blocker: 尚无独立 clean-room 与 Python 版本矩阵证据
      subsystem: Evolutionary Archive / Rollback Immune System
      fix_task: 后续由独立 CI/环境验证任务处理
      acceptance_criteria: 在此之前保持 external_reproduction_completed=false
      status: deferred
  final_decision: 仅推荐用于本地、合成、离线 artifact 验证环境透明度；不得升级为生产或外部验证声明
  evidence:
    docs:
      - docs/REPRODUCIBILITY_ENVIRONMENT_REQUIREMENTS.md
      - docs/REPRODUCE_SAEE_EXPERIMENT.md
    tests:
      - scripts/saee_environment_requirements_smoke.py
    examples:
      - agent-interface/reproducibility/saee-reproducibility-manifest.v0.1.json
```

## Required Design Check

1. 强化 `Evolutionary Archive / Rollback Immune System`：使本地研究产物的验证环境可发现、可比较、可拒绝不完整声明。
2. 改善 archive 与 rollback，而不改变感知、分叉、变异或选择语义。
3. 保留安全、许可证、供应链和权限边界：无网络、无安装、无外部代码执行、无权限扩大。
4. 风险可控：该功能明确是免疫/证据子系统，不把 SAEE 重构为审计优先系统。
