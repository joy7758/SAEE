#!/usr/bin/env python3
"""Smoke test the SAEE Scenario Template Layer v1.0."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = ROOT / "phase_b_product/scenario_templates"
LANDING = ROOT / "phase_b_product/landing"

TEMPLATES = [
    "ai_agent_deployment",
    "customer_service_ai",
    "sales_agent",
    "commercial_design",
    "business_strategy",
]
REQUIRED_KEYS = [
    "scenario_id:",
    "display_name:",
    "description:",
    "target_customer:",
    "decision_question:",
    "candidate_input:",
    "simulation_environment:",
    "stress_factors:",
    "evaluation_focus:",
    "output_report:",
    "business_value:",
]
FORBIDDEN_CLAIMS = [
    "production_ready: true",
    "production_ready_claim: true",
    "customer_validated: true",
    "customer_validation_claim: true",
    "external_validation_claim: true",
    "private_core_exposed: true",
    "public_sdk_released: true",
    "product_launched: true",
]
FORBIDDEN_PATHS = [
    "saee_backend/core/",
    "saee_v1_0/",
    "schemas/saee_mvp_api.schema.json",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_SCENARIO_TEMPLATE_SMOKE: FAIL {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require_yaml_list_value(text: str, key: str) -> None:
    start = text.find(key)
    require(start >= 0, f"missing {key}")
    tail = text[start:].split("\n", 8)
    require(any(line.strip().startswith("- ") for line in tail[1:]), f"{key} must contain list values")


def main() -> None:
    require(SCENARIO_DIR.is_dir(), "scenario template directory missing")
    read(SCENARIO_DIR / "README.md")
    schema = read(SCENARIO_DIR / "schema.yaml")
    for key in REQUIRED_KEYS:
        require(key in schema, f"schema missing {key}")

    registry_path = SCENARIO_DIR / "registry.json"
    registry = json.loads(read(registry_path))
    require(registry.get("scenario_template_layer") == "v1.0", "registry layer mismatch")
    for key in [
        "core_runtime_modified",
        "backend_decision_logic_modified",
        "api_schema_modified",
        "private_core_exposed",
        "production_ready_claim",
        "customer_validation_claim",
    ]:
        require(registry.get(key) is False, f"registry {key} must be false")
    scenarios = registry.get("scenarios")
    require(isinstance(scenarios, list), "registry scenarios must be a list")
    require([item.get("id") for item in scenarios] == TEMPLATES, "registry scenario order mismatch")
    require(all(item.get("enabled") is True for item in scenarios), "all scenarios must be enabled")

    for scenario_id in TEMPLATES:
        template_path = SCENARIO_DIR / f"{scenario_id}.yaml"
        text = read(template_path)
        for key in REQUIRED_KEYS:
            require(key in text, f"{template_path.name} missing {key}")
        require(f"scenario_id: {scenario_id}" in text, f"{template_path.name} scenario_id mismatch")
        for key in ["candidate_input:", "stress_factors:", "evaluation_focus:", "output_report:"]:
            require_yaml_list_value(text, key)
        for forbidden in FORBIDDEN_CLAIMS:
            require(forbidden not in text, f"{template_path.name} forbidden claim {forbidden}")

    index = read(LANDING / "index.html")
    app = read(LANDING / "app.js")
    css = read(LANDING / "styles.css")
    for token in [
        "choose-scenario",
        "选择你的决策场景",
        "AI 部署前评估",
        "AI 客服可靠性测试",
        "AI 销售助手测试",
        "商业设计方案评估",
        "商业策略压力测试",
        "运行现有 SAEE 决策循环",
    ]:
        require(token in index, f"landing missing {token}")
    for scenario_id in TEMPLATES:
        require(scenario_id in app, f"app.js missing {scenario_id}")
    for token in ["scenario-template-grid", "scenario-template-card", "scenario-flow"]:
        require(token in css, f"styles.css missing {token}")
    require("fetch(apiUrl" in app, "landing must still call existing API URL")
    require("/experiment/run" in app, "landing must still use existing decision endpoint")

    boundary = read(ROOT / "docs/strategy/SAEE_SCENARIO_TEMPLATE_BOUNDARY.md")
    for token in [
        "does not modify",
        "SAEE evaluation engine",
        "runtime",
        "backend decision logic",
        "API schema",
        "private core",
    ]:
        require(token in boundary, f"boundary doc missing {token}")
    combined = "\n".join([schema, json.dumps(registry), index, app, css, boundary])
    for forbidden in FORBIDDEN_CLAIMS:
        require(forbidden not in combined, f"forbidden claim found: {forbidden}")
    for forbidden_path in FORBIDDEN_PATHS:
        require(forbidden_path not in combined, f"forbidden path claim found: {forbidden_path}")

    agent_index = json.loads(read(ROOT / "agent-index.json"))
    require("scenario_template_layer_v1_0" in agent_index, "agent-index missing scenario entry")
    entry = agent_index["scenario_template_layer_v1_0"]
    require(entry.get("status") == "complete", "agent-index scenario status mismatch")
    require(entry.get("core_runtime_modified") is False, "agent-index core_runtime_modified must be false")
    require(entry.get("backend_decision_logic_modified") is False, "agent-index backend flag must be false")
    require(entry.get("api_schema_modified") is False, "agent-index API schema flag must be false")
    require(entry.get("private_core_exposed") is False, "agent-index private core flag must be false")

    llms = read(ROOT / "llms.txt")
    for token in [
        "/phase_b_product/scenario_templates/README.md",
        "/phase_b_product/scenario_templates/registry.json",
        "/phase_b_product/scenario_templates/schema.yaml",
        "/docs/strategy/SAEE_SCENARIO_TEMPLATE_BOUNDARY.md",
        "/scripts/saee_scenario_template_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    print("SAEE_SCENARIO_TEMPLATE_SMOKE: PASS")


if __name__ == "__main__":
    main()
