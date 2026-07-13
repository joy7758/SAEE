#!/usr/bin/env python3
"""Build the Phase 7.3 research artifact from a completed Phase 7.2 corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"agent-interface/research/reliability-framework-v1.1"
STATUS=OUT/"SAEE_PHASE7_3_STATUS.json"
PHASE7_2_STATUS=ROOT/"agent-interface/reliability/benchmark-runs/v1.1/SAEE_PHASE7_2_EXECUTION_STATUS.json"
MANIFEST=OUT/"manifest.v1.0.json"
README=OUT/"README.md"
REPORT=ROOT/"docs/research/SAEE_AGENT_RELIABILITY_RESEARCH_REPORT_V1.md"
SCHEMA=ROOT/"schemas/saee-agent-reliability-research-artifact-manifest.schema.v1.0.json"
SOURCE_REFS=[
    "agent-interface/reliability/saee-extended-internal-reliability-benchmark-result.v1.1.json",
    "agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-new-run-manifests.v1.1.json",
    "agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-combined-run-manifests.v1.1.json",
    "agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-assessments.v1.1.json",
    "agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-failure-distribution.v1.1.json",
    "agent-interface/reliability/methodology/saee-internal-reliability-methodology-review.v1.0.json",
    "docs/research/SAEE_EXTENDED_INTERNAL_RELIABILITY_BENCHMARK_REPORT_V1_1.md"
]


def load(path: Path) -> dict: return json.loads(path.read_text(encoding="utf-8"))
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifact() -> dict:
    status=load(PHASE7_2_STATUS)
    if status.get("execution_complete") is not True: raise ValueError("PHASE7_2_EXTENDED_BENCHMARK_INCOMPLETE")
    paths=[ROOT/ref for ref in SOURCE_REFS]
    if not all(path.is_file() for path in paths): raise ValueError("PHASE7_2_ARTIFACT_MISSING")
    result=load(paths[0]); manifests=load(paths[2])["run_manifests"]; assessments=load(paths[3])["assessments"]; failures=load(paths[4])
    if result.get("combined_runs_attempted")!=75 or len(manifests)!=75 or len(assessments)!=75: raise ValueError("PHASE7_2_CORPUS_COUNT_INVALID")
    manifest={"manifest_version":"1.0","artifact_id":"saee-agent-reliability-research-artifact-v1","source_benchmark_id":"saee-extended-internal-reliability-v1.1","run_count":75,"methodology_review_reference":"agent-interface/reliability/methodology/saee-internal-reliability-methodology-review.v1.0.json","report_reference":"docs/research/SAEE_AGENT_RELIABILITY_RESEARCH_REPORT_V1.md","sources":[{"reference":ref,"sha256":sha(path)} for ref,path in zip(SOURCE_REFS,paths)],"limitations":["Internal controlled synthetic benchmark only.","Five repetitions per cell do not establish a population reliability probability.","Provider, model, Adapter, and scenario effects remain partially confounded.","Scenario-specific Evidence Adequacy profiles are not interchangeable.","Contract failure is not a security or intelligence conclusion.","No customer, production, certification, compliance, legal, or deployment claim is established."],"truth_boundary":{"internal_benchmark":True,"public_benchmark":False,"peer_reviewed":False,"publicly_published":False,"ranking_generated":False,"certification":False,"population_reliability_probability_established":False,"external_validation_completed":False,"production_ready":False}}
    errors=list(Draft202012Validator(load(SCHEMA)).iter_errors(manifest))
    if errors: raise ValueError(f"PHASE7_3_MANIFEST_INVALID:{errors[0].message}")
    dimensions="\n".join(f"- `{name}`: {values}" for name,values in result["dimension_statistics"].items())
    failure_lines="\n".join(f"- `{name}`: {count}" for name,count in failures["counts"].items()) or "- 未观察到分类失败"
    report=f"""# SAEE Agent Reliability Research Report v1

## 摘要

本研究使用统一 SAEE Reliability Framework，对三个真实推理模型 Agent 在五个受控合成场景中执行 75 次观察，每个 Agent×场景单元重复五次。研究关注 Task、Recovery、Boundary、Evidence 和 Assessment Availability 五个独立维度，不生成总分、模型排名或胜者。

## 研究问题

1. Agent 是否完成固定场景合同？
2. 在明确恢复机会存在时，Agent 是否采取可观察恢复行为？
3. Agent 是否保持场景声明的权限与安全边界？
4. 当前证据关系是否满足相应 Evidence Adequacy Profile？
5. 结构化评估合同是否可用？

## 方法

- agents=3
- scenarios=5
- repetitions_per_cell=5
- total_runs=75
- run_manifest_coverage=100%
- failure_taxonomy_coverage=100%
- external_world_actions=false

Task Reliability 与 Evidence Reliability 分离。Recovery Reliability 只在 Run Manifest 明确记录恢复机会时评估。所有合同失败和 Provider 不可用均保留。

## 维度结果

{dimensions}

## 失败分布

{failure_lines}

失败类型可重叠；不将合同失败解释为安全失败，也不将模型响应失败解释为通用智能能力失败。

## 主要发现

- 可靠性必须按场景、维度和证据引用分层表达，不能压缩成单一模型分数。
- Assessment Availability 是 Agent Interface Reliability 的可观察组成部分。
- Evidence Adequacy 可以在行为差异存在时保持独立解释，但 PASS 不证明事实发生或系统安全。
- 未显式注入恢复机会时，Recovery 保持 NOT_ASSESSED 比推导“恢复成功”更可靠。

## 限制

{chr(10).join('- '+item for item in manifest['limitations'])}

## 真值边界

- internal_benchmark=true
- public_benchmark=false
- peer_reviewed=false
- publicly_published=false
- ranking_generated=false
- certification=false
- external_validation_completed=false
- production_ready=false
"""
    readme="""# SAEE Agent Reliability Research Artifact v1

机器入口：`manifest.v1.0.json`。所有来源均为仓库内相对路径并绑定 SHA-256。

验证：

```bash
python3 scripts/saee_agent_reliability_research_report_smoke.py
```

本包不含 API Key、原始 Provider 内容、隐藏推理、客户数据或生产结论。
"""
    OUT.mkdir(parents=True,exist_ok=True); MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); REPORT.write_text(report,encoding="utf-8"); README.write_text(readme,encoding="utf-8")
    STATUS.write_text(json.dumps({"status_version":"1.0","phase":"7.3","builder_ready":True,"phase7_2_dependency_complete":True,"research_artifact_generated":True,"report_generated":True,"blocking_condition":None,"peer_reviewed":False,"publicly_published":False,"ranking_generated":False,"production_ready":False},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return manifest


def main() -> int:
    manifest=build_artifact(); print("SAEE_AGENT_RELIABILITY_RESEARCH_REPORT_RESULT"); print(f"run_count={manifest['run_count']}"); print(f"source_bindings={len(manifest['sources'])}"); print("ranking_generated=false\npublicly_published=false\nproduction_ready=false"); return 0


if __name__=="__main__": raise SystemExit(main())
