#!/usr/bin/env python3
"""Generate local production evidence JSON templates for SAEE launch review.

The generated files are placeholders for future human-provided evidence. They
do not close commercial blockers, contact external services, execute runtime
logic, or claim production readiness.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable, NamedTuple


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.production_auth_evidence import (
    AUTH_IDP_KEYS,
    FORBIDDEN_TRUE_KEYS as AUTH_FORBIDDEN_TRUE_KEYS,
    OAUTH_OIDC_KEYS,
    RBAC_KEYS,
)
from saee_backend.services.production_billing_revenue_evidence import (
    FORBIDDEN_TRUE_KEYS as BILLING_FORBIDDEN_TRUE_KEYS,
    INVOICE_PROCESS_KEYS,
    PAYMENT_PROVIDER_KEYS,
    PRICING_PAGE_KEYS,
    REFUND_POLICY_KEYS,
    TAX_REVIEW_KEYS,
    TENANT_BILLING_ISOLATION_KEYS,
)
from saee_backend.services.production_customer_validation_evidence import (
    BOUNDARY_REVIEW_KEYS,
    CLAIM_PERMISSION_KEYS,
    CUSTOMER_VALUE_KEYS,
    FORBIDDEN_TRUE_KEYS as CUSTOMER_VALIDATION_FORBIDDEN_TRUE_KEYS,
    PILOT_RESULT_KEYS,
)
from saee_backend.services.production_data_operations_evidence import (
    FORBIDDEN_TRUE_KEYS as DATA_OPS_FORBIDDEN_TRUE_KEYS,
    RESTORE_POLICY_KEYS,
    RESTORE_TEST_KEYS,
)
from saee_backend.services.production_operations_evidence import (
    EXTERNAL_ALERT_DELIVERY_KEYS,
    FORBIDDEN_TRUE_KEYS as OPERATIONS_FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS as OPERATIONS_ON_CALL_KEYS,
    PRODUCTION_MONITORING_KEYS,
)
from saee_backend.services.production_privacy_security_legal_evidence import (
    DPA_KEYS,
    FORBIDDEN_TRUE_KEYS as PRIVACY_SECURITY_LEGAL_FORBIDDEN_TRUE_KEYS,
    FORMAL_SECURITY_REVIEW_KEYS,
    PRIVACY_LEGAL_REVIEW_KEYS,
    VULNERABILITY_MANAGEMENT_KEYS,
)
from saee_backend.services.production_support_evidence import (
    CUSTOMER_SUPPORT_KEYS,
    FORBIDDEN_TRUE_KEYS as SUPPORT_FORBIDDEN_TRUE_KEYS,
    ON_CALL_KEYS as SUPPORT_ON_CALL_KEYS,
    SLA_KEYS,
    SUPPORT_CONTACT_KEYS,
)
from saee_backend.services.production_tenant_storage_evidence import (
    FORBIDDEN_TRUE_KEYS as TENANT_STORAGE_FORBIDDEN_TRUE_KEYS,
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
)


TEMPLATE_DIR = ROOT / "phase_b_product/commercial_readiness/production_evidence_templates"


class EvidenceTemplateSpec(NamedTuple):
    name: str
    filename: str
    env_var: str
    type_key: str
    type_value: str
    blocker_ids: tuple[str, ...]
    groups: tuple[tuple[str, tuple[str, ...]], ...]
    forbidden_true_keys: tuple[str, ...]


TEMPLATE_SPECS: tuple[EvidenceTemplateSpec, ...] = (
    EvidenceTemplateSpec(
        name="Production Auth Evidence",
        filename="production_auth_evidence.template.json",
        env_var="SAEE_PRODUCTION_AUTH_EVIDENCE_PATH",
        type_key="auth_evidence_type",
        type_value="production_auth_evidence",
        blocker_ids=("production_identity_provider", "oauth_oidc", "rbac"),
        groups=(
            ("production_identity_provider", AUTH_IDP_KEYS),
            ("oauth_oidc", OAUTH_OIDC_KEYS),
            ("rbac", RBAC_KEYS),
        ),
        forbidden_true_keys=AUTH_FORBIDDEN_TRUE_KEYS,
    ),
    EvidenceTemplateSpec(
        name="Production Support/SLA Evidence",
        filename="production_support_sla_evidence.template.json",
        env_var="SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH",
        type_key="support_evidence_type",
        type_value="production_support_sla_evidence",
        blocker_ids=("support_contact", "customer_support", "sla", "on_call_rotation"),
        groups=(
            ("support_contact", SUPPORT_CONTACT_KEYS),
            ("customer_support", CUSTOMER_SUPPORT_KEYS),
            ("sla", SLA_KEYS),
            ("on_call_rotation", SUPPORT_ON_CALL_KEYS),
        ),
        forbidden_true_keys=SUPPORT_FORBIDDEN_TRUE_KEYS,
    ),
    EvidenceTemplateSpec(
        name="Production Data Operations Evidence",
        filename="production_data_operations_evidence.template.json",
        env_var="SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH",
        type_key="data_operations_evidence_type",
        type_value="production_data_operations_evidence",
        blocker_ids=("restore_tested", "production_restore_policy"),
        groups=(
            ("restore_test", RESTORE_TEST_KEYS),
            ("production_restore_policy", RESTORE_POLICY_KEYS),
        ),
        forbidden_true_keys=DATA_OPS_FORBIDDEN_TRUE_KEYS,
    ),
    EvidenceTemplateSpec(
        name="Production Operations Evidence",
        filename="production_operations_evidence.template.json",
        env_var="SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH",
        type_key="operations_evidence_type",
        type_value="production_operations_evidence",
        blocker_ids=("production_monitoring", "external_alert_delivery", "on_call_rotation"),
        groups=(
            ("production_monitoring", PRODUCTION_MONITORING_KEYS),
            ("external_alert_delivery", EXTERNAL_ALERT_DELIVERY_KEYS),
            ("on_call_rotation", OPERATIONS_ON_CALL_KEYS),
        ),
        forbidden_true_keys=OPERATIONS_FORBIDDEN_TRUE_KEYS,
    ),
    EvidenceTemplateSpec(
        name="Production Privacy/Security/Legal Evidence",
        filename="production_privacy_security_legal_evidence.template.json",
        env_var="SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH",
        type_key="privacy_security_legal_evidence_type",
        type_value="production_privacy_security_legal_evidence",
        blocker_ids=(
            "formal_security_review",
            "privacy_legal_review",
            "data_processing_agreement",
            "vulnerability_management",
        ),
        groups=(
            ("formal_security_review", FORMAL_SECURITY_REVIEW_KEYS),
            ("privacy_legal_review", PRIVACY_LEGAL_REVIEW_KEYS),
            ("data_processing_agreement", DPA_KEYS),
            ("vulnerability_management", VULNERABILITY_MANAGEMENT_KEYS),
        ),
        forbidden_true_keys=PRIVACY_SECURITY_LEGAL_FORBIDDEN_TRUE_KEYS,
    ),
    EvidenceTemplateSpec(
        name="Production Billing/Revenue Evidence",
        filename="production_billing_revenue_evidence.template.json",
        env_var="SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH",
        type_key="billing_revenue_evidence_type",
        type_value="production_billing_revenue_evidence",
        blocker_ids=(
            "pricing_page",
            "payment_provider",
            "invoice_process",
            "tax_review",
            "refund_policy",
            "tenant_billing_isolation",
        ),
        groups=(
            ("pricing_page", PRICING_PAGE_KEYS),
            ("payment_provider", PAYMENT_PROVIDER_KEYS),
            ("invoice_process", INVOICE_PROCESS_KEYS),
            ("tax_review", TAX_REVIEW_KEYS),
            ("refund_policy", REFUND_POLICY_KEYS),
            ("tenant_billing_isolation", TENANT_BILLING_ISOLATION_KEYS),
        ),
        forbidden_true_keys=BILLING_FORBIDDEN_TRUE_KEYS,
    ),
    EvidenceTemplateSpec(
        name="Production Tenant Storage Evidence",
        filename="production_tenant_storage_evidence.template.json",
        env_var="SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH",
        type_key="tenant_storage_evidence_type",
        type_value="production_tenant_storage_evidence",
        blocker_ids=("tenant_storage_isolation",),
        groups=(
            ("tenant_storage_model", TENANT_STORAGE_MODEL_KEYS),
            ("tenant_isolation_tests", TENANT_ISOLATION_TEST_KEYS),
            ("tenant_operations", TENANT_OPERATIONS_KEYS),
            ("tenant_security_privacy", TENANT_SECURITY_PRIVACY_KEYS),
        ),
        forbidden_true_keys=TENANT_STORAGE_FORBIDDEN_TRUE_KEYS,
    ),
    EvidenceTemplateSpec(
        name="Production Customer Validation Evidence",
        filename="production_customer_validation_evidence.template.json",
        env_var="SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH",
        type_key="customer_validation_evidence_type",
        type_value="production_customer_validation_evidence",
        blocker_ids=("pilot_results", "customer_validated"),
        groups=(
            ("pilot_results", PILOT_RESULT_KEYS),
            ("customer_value", CUSTOMER_VALUE_KEYS),
            ("claim_permission", CLAIM_PERMISSION_KEYS),
            ("boundary_review", BOUNDARY_REVIEW_KEYS),
        ),
        forbidden_true_keys=CUSTOMER_VALIDATION_FORBIDDEN_TRUE_KEYS,
    ),
)


def _unique(items: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def _template_payload(spec: EvidenceTemplateSpec) -> dict[str, object]:
    required_fields = _unique(key for _, keys in spec.groups for key in keys)
    payload: dict[str, object] = {
        "template_type": "saee_production_evidence_template",
        "template_version": "v0.1",
        "template_status": "placeholder_only",
        "evidence_scope": spec.name,
        "env_var": spec.env_var,
        "covered_blocker_ids": list(spec.blocker_ids),
        "human_review_required": "yes",
        "instructions": (
            "Set required evidence fields to true only after separate human "
            "review confirms the evidence. Keep all forbidden true fields false."
        ),
        spec.type_key: spec.type_value,
        "required_evidence_groups": {
            group_name: list(keys) for group_name, keys in spec.groups
        },
        "forbidden_true_fields": list(spec.forbidden_true_keys),
    }
    for key in required_fields:
        payload[key] = False
    for key in spec.forbidden_true_keys:
        payload[key] = False
    return payload


def _index_payload() -> dict[str, object]:
    return {
        "template_pack_type": "saee_production_evidence_template_pack",
        "template_pack_version": "v0.1",
        "template_status": "placeholder_only",
        "production_evidence_template_pack_v0_1": True,
        "template_count": len(TEMPLATE_SPECS),
        "production_blockers_closed_by_templates": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "evidence_templates": [
            {
                "name": spec.name,
                "filename": spec.filename,
                "env_var": spec.env_var,
                "type_key": spec.type_key,
                "type_value": spec.type_value,
                "covered_blocker_ids": list(spec.blocker_ids),
            }
            for spec in TEMPLATE_SPECS
        ],
    }


def _readme_text() -> str:
    rows = "\n".join(
        f"| {spec.filename} | `{spec.env_var}` | {', '.join(spec.blocker_ids)} |"
        for spec in TEMPLATE_SPECS
    )
    return f"""# SAEE Production Evidence Templates v0.1

Status: placeholder templates only; no production blocker is closed.

This directory contains machine-readable JSON templates for future
human-provided production launch evidence. The templates are generated from the
existing local evidence readiness services so field names match the go/no-go
readers.

| Template | Environment variable | Covered blockers |
| --- | --- | --- |
{rows}

## Boundary

- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No customer contacted.
- No external service called.
- No product launched.
- No production readiness claim made.
- No customer validation claim made.

The templates are intentionally initialized with required evidence fields set to
`false`. A human reviewer must replace placeholders only after real evidence
exists and after separate approval.
"""


def _env_example_text() -> str:
    lines = [
        "# SAEE production evidence template path example.",
        "# Placeholder templates do not close blockers until humans provide real evidence.",
        "SAEE_SUPPORT_CONTACT=replace-with-human-approved-support-contact",
    ]
    for spec in TEMPLATE_SPECS:
        lines.append(
            f"{spec.env_var}=phase_b_product/commercial_readiness/production_evidence_templates/{spec.filename}"
        )
    return "\n".join(lines) + "\n"


def generate_templates() -> None:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    for spec in TEMPLATE_SPECS:
        path = TEMPLATE_DIR / spec.filename
        path.write_text(
            json.dumps(_template_payload(spec), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    (TEMPLATE_DIR / "PRODUCTION_EVIDENCE_TEMPLATE_INDEX.json").write_text(
        json.dumps(_index_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (TEMPLATE_DIR / "README.md").write_text(_readme_text(), encoding="utf-8")
    (TEMPLATE_DIR / "PRODUCTION_EVIDENCE_ENV.example").write_text(
        _env_example_text(), encoding="utf-8"
    )


def main() -> None:
    generate_templates()
    print(
        "SAEE_PRODUCTION_EVIDENCE_TEMPLATES_GENERATED: "
        f"templates={len(TEMPLATE_SPECS)} dir={TEMPLATE_DIR.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
