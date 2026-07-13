"""Human-readable report for controlled multi-Agent rehearsal observations."""

from __future__ import annotations

from typing import Any


def build_comparison_report(experiment: dict[str, Any]) -> str:
    agent_sections = []
    for item in experiment["agent_results"]:
        if item["status"] != "completed":
            agent_sections.append(
                f"### {item['agent_profile']}\n\n- Provider：{item['provider']}\n- Model：{item['model']}\n- 状态：`unavailable`\n- 原因：`{item['unavailable_reason']}`\n"
            )
            continue
        behavior = item["execution_behavior"]
        risks = item["risk_detection"]
        evidence = item["evidence_quality"]
        escalation = item["escalation_behavior"]
        agent_sections.append(f"""### {item['agent_profile']}

- Provider Gateway：{item['provider']}
- Model Vendor：{item['model_vendor']}
- Model：{item['model']}
- Tool sequence：{behavior['tool_sequence']}
- Provider rounds：{behavior['provider_rounds']}
- State transitions：{behavior['state_transitions']}
- Observations：{behavior['observation_count']}
- Observed risk signals：{risks['observed_risk_signals']}
- Agent-declared risks：{risks['agent_declared_risks']}
- Evidence：SUPPORTED={evidence['supported_claims']}，FAIL={evidence['failed_claims']}，missing={evidence['missing_evidence']}
- Recommendation：`{escalation['bounded_recommendation']}`
- Stopped or escalated：{str(escalation['stopped_or_escalated']).lower()}
""")
    differences = "\n".join(f"- {line}" for line in experiment["observed_differences"]["narrative"])
    limitations = "\n".join(f"- {line}" for line in experiment["limitations"])
    return f"""# SAEE Agent Rehearsal Comparison Report v0.1

## 实验概览

- Experiment：Coding Release Rehearsal
- Scenario：`{experiment['scenario_id']}`
- Agents requested：{experiment['agents_requested']}
- Agents tested：{experiment['agents_tested']}
- Same environment：true
- Isolated runs：true
- Ranking generated：false
- Winner selected：false

## 环境

所有 Agent 使用相同初始状态、工具、策略约束和测试回归注入。每个 Agent 获得独立内存世界，不共享状态。模型推理来自真实 Provider API；仓库、测试、批准、回滚与部署工具均为合成模拟。

## Agents 与观察结果

{chr(10).join(agent_sections)}

## 观察到的差异

{differences}

## 证据解释

Evidence 结果衡量既有责任声明所需字段是否满足，不衡量模型智能、任务总体正确率、安全性或生产可靠性。同一环境可能产生相同 Evidence 结果，同时保留不同工具顺序、风险表述和升级建议。

## 限制

{limitations}

> This report compares controlled rehearsal behavior. It is not an intelligence ranking, certification, or production prediction.

本报告比较受控演练行为，不构成智能排名、认证或生产预测。
"""
