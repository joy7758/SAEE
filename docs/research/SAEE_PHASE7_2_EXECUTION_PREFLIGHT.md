# SAEE Phase 7.2 Execution Status

## 当前结论

Phase 7.2 已通过离线预检并完成新增 30 次真实模型调用。

```text
implementation_ready=true
offline_preflight_passed=true
additional_real_model_runs_attempted=30
additional_real_model_runs_required=30
combined_runs_available=75
execution_complete=true
blocking_condition=null
```

## 已验证内容

- 既有 45 次 Phase 7.0 Run Manifest 和 Assessment 可被只读加载。
- 新增重复索引固定为 `4`、`5`，已执行 30 次调用。
- 45 次基础观察与 30 次新增观察已合并为 75 个唯一 `run_id`。
- 每条新增 Run Manifest 必须保存 `recovery_opportunity_observed`。
- Task、Recovery、Boundary、Evidence、Assessment Availability 五个维度遵循 Phase 7.1 纠正语义。
- 新增运行完成 21 次，合同失败或不可用 9 次；合并 Corpus 完成 53 次，失败或不可用 22 次。
- 离线验证不访问网络、不执行外部 Tool、不产生排名或部署结论。

## 为什么不改用千帆完成本批扩展

千帆目录已观察到 DeepSeek 和 GLM 等多供应商模型，但没有与冻结矩阵相同的三项模型身份，尤其不包含本批使用的豆包模型身份。替换 Provider 或模型会把“增加重复次数”变成“更换实验条件”，破坏 Phase 7.2 的比较契约。

因此执行保持：

- `qianfan_substitution_allowed=false`
- 不把 Provider 不等价替换包装成扩展基准
- 不把离线假客户端结果写成真实模型结果
- 只在 75 个唯一 Manifest、100% Manifest 覆盖和 100% 失败分类覆盖成立后声明执行完成

## 执行入口

复核命令：

```bash
python3 scripts/saee_extended_internal_reliability_benchmark_smoke.py
```

凭据未写入报告、Manifest、日志或 Agent Discovery 表面。
