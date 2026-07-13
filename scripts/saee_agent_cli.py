#!/usr/bin/env python3
"""Agent-native JSON interface for the public SAEE MVP descriptor simulator.

The CLI never executes candidate code, contacts external systems, or imports
the private SAEE core. Stdout is always a single JSON object.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import ValidationError

from saee_backend.models.request import ScenarioBatchRequest
from saee_backend.observed_trace_adapter import (
    ObservedTraceBundle,
    evaluate_observed_trace_bundle,
)
from saee_backend.services.experiment_service import ExperimentService
from saee_backend.storage.memory_db import MemoryExperimentStore


MANIFEST = ROOT / "agent-interface/agent-manifest.json"
CLI_VERSION = "0.1.0"
MODE = "synthetic_descriptor_simulation"
FORMULA = "0.50 * stability_score + 0.30 * survival_score - 0.20 * risk_score"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def emit(payload: dict[str, Any], output: Path | None = None) -> None:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)


def error_payload(error_type: str, message: str) -> dict[str, Any]:
    return {
        "saee_agent_error_v0_1": True,
        "schema_version": CLI_VERSION,
        "error_type": error_type,
        "message": message,
        "evaluation_performed": False,
        "external_calls_made": False,
        "candidate_code_executed": False,
        "private_core_exposed": False,
        "production_ready": False,
    }


def evaluate(input_path: Path) -> dict[str, Any]:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("input JSON must be an object")
    request = ScenarioBatchRequest.model_validate(raw)
    normalized_request = request.model_dump(mode="json")
    request_hash = sha256_json(normalized_request)

    service = ExperimentService(MemoryExperimentStore())
    summary = service.run_experiment(request)
    experiment_id = summary.experiment_id
    reports = {
        "evaluation_summary": summary.model_dump(mode="json"),
        "stability_reports": [item.model_dump(mode="json") for item in service.get_stability(experiment_id)],
        "failure_mode_reports": [item.model_dump(mode="json") for item in service.get_failures(experiment_id)],
        "survival_curves": [item.model_dump(mode="json") for item in service.get_survival(experiment_id)],
        "comparison_ranking": service.get_ranking(experiment_id).model_dump(mode="json"),
    }
    content_hash = sha256_json(reports)
    return {
        "saee_agent_evaluation_receipt_v0_1": True,
        "schema_version": CLI_VERSION,
        "receipt_id": f"saee-receipt-{request_hash[:16]}",
        "evaluation_mode": MODE,
        "request_sha256": request_hash,
        "content_sha256": content_hash,
        "provenance": {
            "input_kind": "non_executable_agent_descriptors",
            "descriptor_text_affects_simulation": True,
            "observed_agent_trace_evaluation": False,
            "candidate_code_executed": False,
            "external_calls_made": False,
            "private_core_loaded": False,
            "scoring_formula": FORMULA,
            "engine": "saee_public_mvp_descriptor_simulator_v0.1",
        },
        **reports,
        "truth_boundary": {
            "empirical_agent_behavior_validated": False,
            "production_ready": False,
            "product_launched": False,
            "customer_validated": False,
            "external_agent_execution": False,
            "private_core_exposed": False,
        },
    }


def evaluate_traces(input_path: Path) -> dict[str, Any]:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("input JSON must be an object")
    bundle = ObservedTraceBundle.model_validate(raw)
    return evaluate_observed_trace_bundle(bundle)


def main() -> int:
    parser = argparse.ArgumentParser(prog="saee-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("describe", help="Print the canonical agent manifest as JSON.")
    evaluate_parser = subparsers.add_parser("evaluate", help="Run local synthetic descriptor evaluation.")
    evaluate_parser.add_argument("--input", required=True, type=Path)
    evaluate_parser.add_argument("--output", type=Path)
    trace_parser = subparsers.add_parser(
        "evaluate-traces",
        help="Evaluate a sanitized file-backed observed trace bundle without executing agents.",
    )
    trace_parser.add_argument("--input", required=True, type=Path)
    trace_parser.add_argument("--output", type=Path)
    resource_parser = subparsers.add_parser(
        "validate-resource-resolution",
        help="Validate a local synthetic resource-resolution receipt without network or execution.",
    )
    resource_parser.add_argument("--input", required=True, type=Path)
    adequacy_parser = subparsers.add_parser(
        "validate-evidence-adequacy",
        help="Evaluate a closed synthetic evidence package against a canonical adequacy profile.",
    )
    adequacy_parser.add_argument(
        "--profile",
        required=True,
        choices=[
            "RESOURCE_AUTHENTICITY",
            "AUTHORIZED_AGENT_ACTION",
            "HUMAN_OVERSIGHT",
            "EXECUTION_BOUNDARY",
        ],
    )
    adequacy_parser.add_argument("--input", required=True, type=Path)
    trace_candidate_parser = subparsers.add_parser(
        "evaluate-trace-candidate",
        help="Map a closed synthetic OpenTelemetry-style event into candidate evidence and evaluate adequacy.",
    )
    trace_candidate_parser.add_argument(
        "--profile",
        required=True,
        choices=[
            "RESOURCE_AUTHENTICITY",
            "AUTHORIZED_AGENT_ACTION",
            "HUMAN_OVERSIGHT",
            "EXECUTION_BOUNDARY",
        ],
    )
    trace_candidate_parser.add_argument("--input", required=True, type=Path)
    benchmark_parser = subparsers.add_parser(
        "benchmark-evidence-adequacy",
        help="Run the local synthetic Evidence Adequacy Benchmark Profile v0.1.",
    )
    benchmark_parser.add_argument("--input", required=True, type=Path)
    prototype_parser = subparsers.add_parser(
        "run-evaluation-prototype",
        help="Run the controlled offline SAEE evaluation prototype on canonical synthetic scenarios.",
    )
    prototype_parser.add_argument("--input", required=True, type=Path)
    readiness_parser = subparsers.add_parser(
        "review-pilot-readiness",
        help="Review a local SAEE pilot readiness matrix without executing or approving a pilot.",
    )
    readiness_parser.add_argument("--input", required=True, type=Path)
    gap_parser = subparsers.add_parser(
        "review-pilot-gaps",
        help="Review a local NO_GO pilot gap plan without resolving gaps or authorizing execution.",
    )
    gap_parser.add_argument("--input", required=True, type=Path)
    acquisition_parser = subparsers.add_parser(
        "review-evidence-acquisition-plan",
        help="Review future pilot evidence requirements without acquiring evidence or creating approval.",
    )
    acquisition_parser.add_argument("--input", required=True, type=Path)
    assurance_case_parser = subparsers.add_parser(
        "run-assurance-case",
        help="Run the local synthetic SAEE Evidence Case Object vertical slice without executing an Agent.",
    )
    assurance_case_parser.add_argument("--input", required=True, type=Path)
    review_report_parser = subparsers.add_parser(
        "generate-review-report",
        help="Generate a bounded local synthetic evidence adequacy review report.",
    )
    review_report_parser.add_argument("--input", required=True, type=Path)
    commercial_assessment_parser = subparsers.add_parser(
        "generate-commercial-assessment",
        help="Generate a bounded Chinese-first assessment from local SAEE reliability artifacts.",
    )
    commercial_assessment_parser.add_argument("--input", required=True, type=Path)
    subparsers.add_parser(
        "capability-list",
        help="List canonical capability facts from the checked-in Capability Package manifest.",
    )
    capability_show_parser = subparsers.add_parser(
        "capability-show",
        help="Show one exact canonical capability id or alias.",
    )
    capability_show_parser.add_argument("capability_id")
    capability_resolve_parser = subparsers.add_parser(
        "capability-resolve",
        help="Resolve one exact capability id or alias to its unique canonical interface.",
    )
    capability_resolve_parser.add_argument("capability_id")
    capability_resolve_parser.add_argument("--interface", required=True, choices=["mcp", "cli", "http", "python"])
    subparsers.add_parser(
        "capability-validate",
        help="Validate the canonical inventory and bounded repository projections.",
    )
    args = parser.parse_args()

    try:
        if args.command == "describe":
            emit(json.loads(MANIFEST.read_text(encoding="utf-8")))
            return 0
        if args.command in {
            "capability-list",
            "capability-show",
            "capability-resolve",
            "capability-validate",
        }:
            from saee_backend.services.capability_runtime.canonical_capability_inventory import (
                CANONICAL_SOURCE,
                get_capability,
                load_canonical_inventory,
                normalize_inventory,
                resolve_interface,
                validate_repository_inventory,
            )

            if args.command == "capability-list":
                inventory = normalize_inventory(load_canonical_inventory())
                emit(
                    {
                        "canonical_source": CANONICAL_SOURCE,
                        "capabilities": [
                            {
                                "capability_id": item["capability_id"],
                                "implementation_status": item["implementation_status"],
                                "lifecycle_status": item["lifecycle_status"],
                                "canonical_entrypoint": item["canonical_entrypoint"],
                            }
                            for item in inventory["capabilities"]
                        ],
                        "production_ready": False,
                    }
                )
                return 0
            if args.command == "capability-show":
                emit(
                    {
                        "canonical_source": CANONICAL_SOURCE,
                        "capability": get_capability(args.capability_id),
                        "production_ready": False,
                    }
                )
                return 0
            if args.command == "capability-resolve":
                emit(resolve_interface(args.capability_id, args.interface))
                return 0
            errors = validate_repository_inventory()
            emit(
                {
                    "canonical_source": CANONICAL_SOURCE,
                    "valid": not errors,
                    "errors": errors,
                    "validation_only": True,
                    "production_ready": False,
                }
            )
            return 0 if not errors else 2
        if args.command == "validate-resource-resolution":
            from saee_backend.services.resource_resolution_receipt import (
                validate_resource_resolution_json,
            )

            result = validate_resource_resolution_json(args.input.read_text(encoding="utf-8"))
            emit(result)
            return 0 if result["valid"] else 2
        if args.command == "validate-evidence-adequacy":
            from saee_backend.services.evidence_adequacy import (
                evaluate_evidence_adequacy_json,
            )

            result = evaluate_evidence_adequacy_json(
                args.profile,
                args.input.read_text(encoding="utf-8"),
            )
            emit(result)
            return 0 if result["result"] == "PASS" else 2
        if args.command == "evaluate-trace-candidate":
            from saee_backend.services.otel_candidate_mapping import (
                evaluate_trace_candidate_json,
            )

            result = evaluate_trace_candidate_json(
                args.profile,
                args.input.read_text(encoding="utf-8"),
            )
            emit(result)
            return 0 if result["trace_mapping_result"] in {"PASS", "PARTIAL"} else 2
        if args.command == "benchmark-evidence-adequacy":
            from saee_backend.services.evidence_adequacy_benchmark import (
                run_evidence_adequacy_benchmark_path,
            )

            result = run_evidence_adequacy_benchmark_path(args.input)
            emit(result)
            return 0 if (
                result["expected_result_matches"] == f"{result['total_cases']}/{result['total_cases']}"
                and result["missing_evidence_accuracy"] == f"{result['total_cases']}/{result['total_cases']}"
                and result["reason_code_accuracy"] == f"{result['total_cases']}/{result['total_cases']}"
                and result["false_positive_count"] == 0
                and result["boundary_violation_count"] == 0
            ) else 2
        if args.command == "run-evaluation-prototype":
            from saee_backend.services.saee_evaluation_prototype import (
                run_evaluation_prototype_path,
            )

            result = run_evaluation_prototype_path(args.input)
            emit(result)
            return 0 if (
                result["scenario_count"] >= 8
                and result["condition_count"] == 4
                and result["reference_result_matches"]
                == f"{result['evaluation_record_count']}/{result['evaluation_record_count']}"
                and result["boundary_violation_count"] == 0
            ) else 2
        if args.command == "review-pilot-readiness":
            from saee_backend.services.pilot_readiness import (
                review_pilot_readiness_path,
            )

            result = review_pilot_readiness_path(args.input)
            emit(result)
            return 0
        if args.command == "review-pilot-gaps":
            from saee_backend.services.pilot_gap_tracking import (
                review_pilot_gap_plan_path,
            )

            result = review_pilot_gap_plan_path(args.input)
            emit(result)
            return 0
        if args.command == "review-evidence-acquisition-plan":
            from saee_backend.services.pilot_evidence_acquisition import (
                review_evidence_acquisition_plan_path,
            )

            result = review_evidence_acquisition_plan_path(args.input)
            emit(result)
            return 0
        if args.command == "run-assurance-case":
            from saee_backend.services.saee_evidence_case import (
                run_assurance_case_path,
            )

            result = run_assurance_case_path(args.input)
            emit(result)
            return 0 if (
                result["candidate_count"] >= 2
                and result["scenario_count"] >= 2
                and result["truth_boundary"]["network_calls"] == 0
                and result["truth_boundary"]["subprocess_started"] is False
                and result["truth_boundary"]["deployment_authorized"] is False
                and result["truth_boundary"]["production_ready"] is False
            ) else 2
        if args.command == "generate-review-report":
            from saee_backend.services.review_report_generator import (
                generate_review_report_path,
            )

            report = generate_review_report_path(args.input)
            emit(
                {
                    "SAEE_EVIDENCE_REVIEW_REPORT_RESULT": True,
                    "report": report,
                    "truth_boundary": {
                        "synthetic_only": True,
                        "customer_data_used": False,
                        "commercial_service_delivered": False,
                        "deployment_authorized": False,
                        "production_ready": False,
                    },
                }
            )
            return 0
        if args.command == "generate-commercial-assessment":
            from saee_backend.services.commercial_assessment_service import (
                generate_commercial_assessment_path,
            )

            response = generate_commercial_assessment_path(args.input)
            emit({"SAEE_COMMERCIAL_ASSESSMENT_SERVICE_RESULT": True, "response": response})
            return 0
        receipt = evaluate_traces(args.input) if args.command == "evaluate-traces" else evaluate(args.input)
        emit(receipt, args.output)
        return 0
    except FileNotFoundError as exc:
        emit(error_payload("input_not_found", str(exc)))
    except json.JSONDecodeError as exc:
        emit(error_payload("invalid_json", str(exc)))
    except ValidationError as exc:
        emit(
            error_payload(
                "schema_validation_error",
                json.dumps(exc.errors(include_context=False), ensure_ascii=False),
            )
        )
    except (OSError, ValueError) as exc:
        emit(error_payload("evaluation_error", str(exc)))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
