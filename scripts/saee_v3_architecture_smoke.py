#!/usr/bin/env python3
"""Offline contract smoke for the accepted SAEE v3 L3 architecture projection."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs/architecture/SAEE_V3_SYSTEM_ARCHITECTURE_SPEC.md"
PROPOSAL_PATH = ROOT / "docs/architecture/SAEE_V3_EVOLUTION_PROPOSAL.md"
FINAL_ARCHITECTURE_PATH = ROOT / "docs/architecture/FINAL_ARCHITECTURE_SPEC.md"
SCHEMA_PATH = ROOT / "agent-interface/architecture/saee-deployment-assurance-case.v0.1.schema.json"
MANIFEST_PATH = ROOT / "agent-interface/architecture/saee-v3-system-architecture.v0.1.json"
GATE_PATH = ROOT / "docs/strategy/SAEE_V3_SYSTEM_ARCHITECTURE_RECOMMENDATION_GATE.md"

FALSE_BOUNDARIES = (
    "canonical_three_layer_architecture_modified",
    "final_architecture_spec_replaced",
    "lcr_reds_modified",
    "saee_mp_modified",
    "runtime_modified",
    "website_modified",
    "architecture_implemented",
    "risk_model_implemented",
    "external_agent_executed_by_saee",
    "customer_data_processed",
    "post_deployment_monitoring_available",
    "continuous_assurance_implemented",
    "customer_validated",
    "commercial_ready",
    "production_ready",
)


class V3ArchitectureError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise V3ArchitectureError(code, detail)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(document: dict[str, Any]) -> dict[str, Any]:
    require(document.get("saee_v3_system_architecture_v0_1") is True, "V3_ARCHITECTURE_IDENTITY_INVALID", "root marker")
    require(document.get("architecture_version") == "3.0-draft", "V3_ARCHITECTURE_VERSION_INVALID", "version")
    require(document.get("status") == "accepted_architecture_projection_phase1_local_only", "V3_ARCHITECTURE_STATUS_INVALID", "status")
    require(document.get("scope") == "layer_3_deployment_assurance_projection", "V3_ARCHITECTURE_SCOPE_INVALID", "scope")
    for field in FALSE_BOUNDARIES:
        require(document.get(field) is False, "V3_ARCHITECTURE_BOUNDARY_INVALID", field)
    require(document.get("architecture_projection_accepted") is True, "V3_ARCHITECTURE_ACCEPTANCE_INVALID", "architecture projection")
    require(document.get("phase1_local_synthetic_vertical_slice_implemented") is True, "V3_ARCHITECTURE_PHASE1_INVALID", "phase 1")
    layers = document.get("layers")
    require(isinstance(layers, list) and len(layers) == 9, "V3_ARCHITECTURE_LAYERS_INVALID", "nine layers")
    require([item.get("layer") for item in layers] == list(range(9)), "V3_ARCHITECTURE_LAYERS_INVALID", "layer order")
    require(layers[3].get("name") == "External Agent Runtime Boundary", "V3_ARCHITECTURE_RUNTIME_BOUNDARY_INVALID", "layer 3")
    require(
        layers[3].get("future_receive_only_adapters") == ["Runtime Adapter", "Memory Adapter", "Tool Trace Adapter"],
        "V3_ARCHITECTURE_RUNTIME_ADAPTERS_INVALID",
        "receive-only adapters",
    )
    require(layers[7].get("name") == "Risk Estimation", "V3_ARCHITECTURE_RISK_NAME_INVALID", "layer 7")
    require(layers[8].get("name") == "Decision Support", "V3_ARCHITECTURE_DECISION_NAME_INVALID", "layer 8")
    feedback = document.get("feedback_loop")
    require(isinstance(feedback, dict), "V3_ARCHITECTURE_FEEDBACK_INVALID", "feedback")
    for field in ("direct_runtime_control", "automatic_production_change", "automatic_lcr_reds_or_saee_mp_mutation"):
        require(feedback.get(field) is False, "V3_ARCHITECTURE_FEEDBACK_INVALID", field)
    require(document.get("risk_formula") == "Rs=P*I*X*(1-C)+U;Rtotal=sum(w*Rs)", "V3_ARCHITECTURE_RISK_FORMULA_INVALID", "formula")
    require(document.get("mvp_phase") == "PHASE_1_LOCAL_SYNTHETIC_VERTICAL_SLICE_IMPLEMENTED", "V3_ARCHITECTURE_MVP_PHASE_INVALID", "MVP phase")
    return document


def synthetic_case() -> dict[str, Any]:
    refs = lambda prefix: [f"synthetic:{prefix}:001"]
    criterion = {
        "criterion_id": "criterion-stability", "measurement_method_ref": "method-synthetic",
        "direction": "higher_is_better", "threshold": 0.7, "aggregation_rule": "mean-by-scenario",
        "missing_data_behavior": "INCREASE_UNCERTAINTY", "invalid_behavior": "ABSTAIN",
        "business_relevance": "Synthetic contract fixture only.", "limitations": ["No real performance claim."],
    }
    return {
        "saee_deployment_assurance_case_v0_1": True,
        "schema_version": "0.1.0",
        "architecture_version": "3.0-draft",
        "case_id": "case-synthetic-001",
        "created_at": "2026-01-01T00:00:00Z",
        "case_status": "synthetic_review_only",
        "governance_contract": {
            "governance_contract_id": "governance-synthetic-001", "policy_ref": "policy-synthetic",
            "evaluation_authorization_ref": "authorization-synthetic", "data_permission_ref": "permission-synthetic",
            "version_refs": refs("version"), "risk_class": "MEDIUM", "audit_requirement_ref": "audit-synthetic",
            "retention_and_deletion_ref": "retention-synthetic", "stop_authority_ref": "stop-synthetic",
            "execution_approved": False,
        },
        "task_contract": {
            "task_contract_id": "task-contract-synthetic", "objective": "Evaluate a synthetic customer-support scenario.",
            "prohibited_objectives": ["No external execution."], "task_category": "customer-support", "channel": "offline-synthetic",
            "language": "zh-CN", "candidate_refs": refs("candidate"), "context_policy_ref": "context-synthetic",
            "tool_policy_ref": "tool-policy-synthetic", "memory_policy_ref": "memory-policy-synthetic",
            "business_impact_class": "MEDIUM", "acceptance_criteria": refs("acceptance"),
            "explicit_exclusions": ["No production traffic."],
        },
        "environment_contract": {
            "environment_contract_id": "environment-contract-synthetic", "environment_version": "environment-v001",
            "scenario_refs": refs("scenario"), "distribution_basis": "synthetic", "user_simulation_refs": refs("user-sim"),
            "business_change_refs": refs("change"), "fault_refs": refs("fault"), "deployment_grounded": False,
        },
        "runtime_boundary": {
            "execution_owner": "approved_researcher_sandbox", "sandbox_ref": "sandbox-synthetic",
            "allowed_tool_refs": refs("tool"), "network_policy": "denied", "saee_executes_external_world": False,
            "unknown_external_code_allowed": False, "permission_expansion_allowed": False,
        },
        "observation_contract": {
            "observation_contract_id": "observation-synthetic", "metric_names": ["latency", "tool_call", "failure"],
            "trace_refs": refs("trace"), "state_change_refs": refs("state"), "sanitized": True, "observation_is_evidence": False,
        },
        "evaluation_contract": {
            "evaluation_contract_id": "evaluation-contract-synthetic", "task_contract_ref": "task-contract-synthetic",
            "environment_contract_ref": "environment-contract-synthetic", "candidate_refs": refs("candidate"),
            "data_source_ref": "data-source-synthetic", "sample_manifest_ref": "sample-manifest-synthetic",
            "testing_criteria": [criterion], "negative_and_adversarial_coverage_refs": refs("negative-coverage"),
            "grader_refs": refs("grader"), "repeat_policy_ref": "repeat-policy-synthetic", "stop_condition_refs": refs("stop"),
            "explicit_exclusions": ["No real customer data."], "expected_output_schema_ref": "schema-output-synthetic",
        },
        "evidence_contract": {
            "evidence_contract_id": "evidence-contract-synthetic", "evaluation_contract_ref": "evaluation-contract-synthetic",
            "input_refs": refs("input"), "output_refs": refs("output"), "observation_refs": refs("observation"),
            "receipt_refs": refs("receipt"), "authorization_and_oversight_refs": refs("oversight"),
            "version_manifest_ref": "version-manifest-synthetic", "grader_manifest_ref": "grader-manifest-synthetic",
            "timestamp": "2026-01-01T00:05:00Z", "content_digest": "a" * 64, "relationship_refs": refs("relationship"),
            "privacy_and_retention_refs": refs("privacy"), "adequacy_result": "PASS", "truth_boundary_ref": "truth-synthetic",
        },
        "risk_contract": {
            "risk_contract_id": "risk-contract-synthetic", "formula_version": "Rs=P*I*X*(1-C)+U;Rtotal=sum(w*Rs)",
            "scenario_risks": [{"scenario_ref": "synthetic:scenario:001", "weight": 1.0, "failure_estimate": 0.2, "business_impact": 0.5, "exposure": 0.5, "control_effectiveness": 0.2, "uncertainty_penalty": 0.1, "scenario_risk": 0.14}],
            "aggregate_risk": 0.14, "deploy_threshold": 0.1, "hold_threshold": 0.3,
            "critical_evidence_gate_passed": True, "confidence": "LOW", "limitations": ["Synthetic arithmetic declaration only."],
        },
        "decision_contract": {
            "decision_contract_id": "decision-synthetic", "recommendation": "RETEST",
            "scenario_scope": "Synthetic offline customer-support scenario only.", "recommended_candidate_ref": "synthetic:candidate:001",
            "allowed_use": ["Local research review."], "prohibited_use": ["No production deployment."],
            "main_failure_triggers": refs("failure-trigger"), "required_controls": refs("control"), "confidence": "LOW",
            "evidence_refs": refs("evidence"), "retest_condition": "Retest after uncertainty is reduced.",
            "expires_at": "2026-02-01T00:00:00Z", "customer_execution_authorized": False,
        },
        "feedback_contract": {
            "enabled": False, "feedback_source_refs": [], "data_permission_refs": [], "next_task_version_ref": "task-next-synthetic",
            "direct_runtime_control": False, "automatic_production_change": False, "automatic_core_mutation": False,
        },
        "truth_boundary": {
            "architecture_implemented": False, "risk_model_implemented": False, "real_agent_executed_by_saee": False,
            "customer_data_processed": False, "post_deployment_monitoring_available": False,
            "continuous_assurance_implemented": False, "external_validation_completed": False,
            "customer_validated": False, "production_ready": False,
        },
    }


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def main() -> None:
    for path in (SPEC_PATH, PROPOSAL_PATH, FINAL_ARCHITECTURE_PATH, SCHEMA_PATH, MANIFEST_PATH, GATE_PATH):
        require(path.is_file(), "V3_ARCHITECTURE_FILE_MISSING", str(path))
    manifest = read_json(MANIFEST_PATH)
    result = validate_manifest(copy.deepcopy(manifest))

    spec = SPEC_PATH.read_text(encoding="utf-8")
    for section in range(1, 14):
        require(f"## {section}." in spec, "V3_ARCHITECTURE_SECTION_MISSING", str(section))
    for layer in range(9):
        require(f"Layer {layer}:" in spec, "V3_ARCHITECTURE_LAYER_DOC_MISSING", str(layer))
    for token in ("Evaluation Contract Specification", "Evidence Contract Specification", "JSON Schema Contract", "Risk Estimation Specification", "MVP Development Roadmap", "SAEE Evidence Case Object"):
        require(token in spec, "V3_ARCHITECTURE_CONTRACT_DOC_MISSING", token)
    require("SAEE does not directly execute the external world." in spec, "V3_ARCHITECTURE_RUNTIME_BOUNDARY_INVALID", "external execution principle")

    final_spec = FINAL_ARCHITECTURE_PATH.read_text(encoding="utf-8")
    require("L1 (Theory) -> L2 (Protocol) -> L3 (Runtime)" in final_spec, "V3_CANONICAL_ARCHITECTURE_DRIFT", "canonical dependency")
    require("Only Layer 1 defines SAEE identity." in final_spec, "V3_CANONICAL_ARCHITECTURE_DRIFT", "canonical authority")

    schema = read_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    require(schema.get("additionalProperties") is False, "V3_SCHEMA_NOT_STRICT", "root additionalProperties")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    case = synthetic_case()
    validator.validate(case)
    negatives = []
    extra = copy.deepcopy(case); extra["unexpected"] = True; negatives.append(extra)
    executes = copy.deepcopy(case); executes["runtime_boundary"]["saee_executes_external_world"] = True; negatives.append(executes)
    authorized = copy.deepcopy(case); authorized["decision_contract"]["customer_execution_authorized"] = True; negatives.append(authorized)
    production = copy.deepcopy(case); production["truth_boundary"]["production_ready"] = True; negatives.append(production)
    feedback = copy.deepcopy(case); feedback["feedback_contract"]["automatic_core_mutation"] = True; negatives.append(feedback)
    require(all(not validator.is_valid(item) for item in negatives), "V3_SCHEMA_NEGATIVE_ACCEPTED", "schema boundaries")

    invalid_manifests: list[tuple[dict[str, Any], str]] = []
    implemented = copy.deepcopy(manifest); implemented["status"] = "implemented"; invalid_manifests.append((implemented, "V3_ARCHITECTURE_STATUS_INVALID"))
    replaced = copy.deepcopy(manifest); replaced["final_architecture_spec_replaced"] = True; invalid_manifests.append((replaced, "V3_ARCHITECTURE_BOUNDARY_INVALID"))
    executed = copy.deepcopy(manifest); executed["external_agent_executed_by_saee"] = True; invalid_manifests.append((executed, "V3_ARCHITECTURE_BOUNDARY_INVALID"))
    ready = copy.deepcopy(manifest); ready["production_ready"] = True; invalid_manifests.append((ready, "V3_ARCHITECTURE_BOUNDARY_INVALID"))
    for candidate, expected in invalid_manifests:
        try:
            validate_manifest(candidate)
        except V3ArchitectureError as exc:
            require(exc.code == expected, "V3_REASON_CODE_UNSTABLE", f"expected {expected}, got {exc.code}")
        else:
            raise V3ArchitectureError("V3_INVALID_MANIFEST_ACCEPTED", expected)

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    require(not imported_roots(Path(__file__)).intersection(forbidden), "V3_EXTERNAL_CAPABILITY_IMPORT", "forbidden import")

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_manifest(copy.deepcopy(manifest))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "V3_ARCHITECTURE_NON_DETERMINISTIC", "manifest")

    print("SAEE_V3_ARCHITECTURE_SMOKE: PASS")
    print("valid_manifest_cases=1/1")
    print("invalid_manifest_cases=4/4")
    print("schema_valid_cases=1/1")
    print("schema_negative_cases=5/5")
    print("architecture_layers=9/9")
    print("spec_sections=13/13")
    print("deterministic_runs=5/5")
    print("status=accepted_architecture_projection_phase1_local_only")
    print("architecture_projection_accepted=true")
    print("phase1_local_synthetic_vertical_slice_implemented=true")
    print("canonical_three_layer_architecture_modified=false")
    print("final_architecture_spec_replaced=false")
    print("architecture_implemented=false")
    print("risk_model_implemented=false")
    print("external_agent_executed_by_saee=false")
    print("post_deployment_monitoring_available=false")
    print("continuous_assurance_implemented=false")
    print("customer_validated=false")
    print("production_ready=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")


if __name__ == "__main__":
    main()
