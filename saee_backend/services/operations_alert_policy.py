"""Local alert-candidate policy for SAEE public-shell operations.

This module turns local request-audit telemetry into deterministic alert
candidates for human review. It does not send alerts, call external services,
tail live logs, inspect request bodies, inspect credentials, or inspect
private core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.services.operations_telemetry import build_operations_telemetry_snapshot


AlertSeverity = Literal["info", "warning", "critical"]

DEFAULT_ERROR_COUNT_THRESHOLD = 1
DEFAULT_ERROR_RATE_THRESHOLD = 0.05
DEFAULT_P95_LATENCY_MS_THRESHOLD = 2000.0


@dataclass(frozen=True)
class AlertCandidate:
    alert_id: str
    severity: AlertSeverity
    condition: str
    observed_value: float | int | None
    threshold: float | int | None
    action_required: str
    manual_review_required: bool = True

    def as_dict(self) -> dict[str, object]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity,
            "condition": self.condition,
            "observed_value": self.observed_value,
            "threshold": self.threshold,
            "action_required": self.action_required,
            "manual_review_required": self.manual_review_required,
        }


def _candidate(
    alert_id: str,
    severity: AlertSeverity,
    condition: str,
    observed_value: float | int | None,
    threshold: float | int | None,
    action_required: str,
) -> AlertCandidate:
    return AlertCandidate(
        alert_id=alert_id,
        severity=severity,
        condition=condition,
        observed_value=observed_value,
        threshold=threshold,
        action_required=action_required,
    )


def evaluate_operations_alert_policy(
    settings: SaeeBackendSettings = SETTINGS,
    tenant_id: str | None = None,
) -> dict[str, object]:
    """Return local alert candidates from aggregate request metadata only."""

    telemetry = build_operations_telemetry_snapshot(settings, tenant_id=tenant_id)
    event_count = int(telemetry.get("event_count") or 0)
    error_count = int(telemetry.get("error_count") or 0)
    duration_p95 = telemetry.get("duration_ms_p95")
    error_rate = round(error_count / event_count, 6) if event_count else 0.0

    alerts: list[AlertCandidate] = []
    findings: list[dict[str, object]] = [
        {
            "check_id": "local_alert_policy_available",
            "severity": "info",
            "passed": True,
            "message": "local alert-candidate policy is available for human review only",
        },
        {
            "check_id": "external_alert_delivery_disabled",
            "severity": "info",
            "passed": True,
            "message": "no webhook, email, pager, chat, or external alert delivery is configured",
        },
        {
            "check_id": "no_request_body_or_secret_inspection",
            "severity": "info",
            "passed": True,
            "message": "alert policy uses aggregate metadata and does not inspect bodies, credentials, or private core",
        },
    ]

    if event_count == 0:
        findings.append(
            {
                "check_id": "no_events_observed",
                "severity": "info",
                "passed": True,
                "message": "no local request audit events are available for alert-candidate evaluation",
            }
        )

    if error_count >= DEFAULT_ERROR_COUNT_THRESHOLD:
        alerts.append(
            _candidate(
                "local_error_count_threshold",
                "warning",
                "5xx response count meets or exceeds the local review threshold",
                error_count,
                DEFAULT_ERROR_COUNT_THRESHOLD,
                "review request-audit metadata and incident runbook before any preview use",
            )
        )

    if error_rate >= DEFAULT_ERROR_RATE_THRESHOLD and event_count > 0:
        alerts.append(
            _candidate(
                "local_error_rate_threshold",
                "warning",
                "5xx response rate meets or exceeds the local review threshold",
                error_rate,
                DEFAULT_ERROR_RATE_THRESHOLD,
                "inspect local aggregate telemetry and defer public use until reviewed",
            )
        )

    if isinstance(duration_p95, (int, float)) and duration_p95 >= DEFAULT_P95_LATENCY_MS_THRESHOLD:
        alerts.append(
            _candidate(
                "local_latency_p95_threshold",
                "warning",
                "p95 request duration meets or exceeds the local review threshold",
                float(duration_p95),
                DEFAULT_P95_LATENCY_MS_THRESHOLD,
                "review latency trend locally before controlled preview",
            )
        )

    return {
        "alert_policy_type": "local_public_shell_alert_policy",
        "telemetry_source": "request_audit_jsonl",
        "local_alert_policy_available": True,
        "alert_candidates_generated": True,
        "alert_count": len(alerts),
        "alerts": [alert.as_dict() for alert in alerts],
        "findings": findings,
        "event_count": event_count,
        "error_count": error_count,
        "error_rate": error_rate,
        "tenant_scope_filter_applied": bool(telemetry.get("tenant_scope_filter_applied")),
        "tenant_id_raw_filter_recorded": False,
        "duration_ms_p95": duration_p95,
        "external_alert_delivery_available": False,
        "alerting_available": False,
        "production_monitoring_available": False,
        "operations_telemetry_external_export_available": False,
        "incident_response_runbook_available": True,
        "support_readiness_v0_1": True,
        "support_runbook_available": True,
        "support_case_template_available": True,
        "support_sla_draft_available": True,
        "support_response_targets_documented": True,
        "support_contact_configured": False,
        "customer_support_available": False,
        "production_support_available": False,
        "on_call_rotation_available": False,
        "sla_available": False,
        "support_process_available": False,
        "production_operations_ready": False,
        "body_inspected": False,
        "credentials_inspected": False,
        "private_core_inspected": False,
        "private_core_exposed": settings.private_core_exposed,
        "production_ready": settings.production_ready,
        "customer_validated": settings.customer_validated,
        "product_launched": settings.product_launched,
        "public_sdk_released": settings.public_sdk_released,
        "api_schema_modified": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
        "next_action": "use alert candidates for local human review only; configure real monitoring and alert delivery before production use",
    }
