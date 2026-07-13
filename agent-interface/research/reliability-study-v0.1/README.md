# SAEE Reliability Study v0.1 Reproducibility Package

本目录是引用式复现入口，不复制实验对象或 Provider 响应。

## 从这里开始

1. 读取 `manifest.v0.1.json`；
2. 按 `references[].path` 解析场景、Agent Profiles、配置、Schema 和冻结结果；
3. 核验有 SHA-256 的数据与契约对象；
4. 运行离线验证；
5. 只有在自行提供合法 Provider 凭据并接受费用后，才运行真实重复实验。

## 离线验证

```bash
python3 scripts/saee_reliability_publication_smoke.py
python3 scripts/saee_agent_reliability_smoke.py
```

离线验证不访问网络、不需要 API Key，也不会改写冻结结果。

## 真实复现边界

`python3 scripts/saee_agent_reliability_study.py` 会调用真实 Volcengine Ark API，并覆盖仓库内结果与产品报告。运行前应复制冻结产物或使用独立工作区。

本包不含密钥、Provider 原始 payload、隐藏推理、私有日志或客户数据。它不是可执行环境快照，也不保证未来 Provider 模型版本可用。

## 解释边界

- 30 次已执行不等于 30 次契约成功；
- `study_complete=true` 表示研究计划完整记录；
- 样本内一致性不等于总体可靠性概率；
- 本包不生成排行榜、认证或生产预测。
