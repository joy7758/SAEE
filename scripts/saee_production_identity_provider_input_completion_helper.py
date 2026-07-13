#!/usr/bin/env python3
"""Prepare production identity-provider input completion materials.

This helper turns the current production identity-provider approval-input
validator gaps into a human-fillable completion sheet. It does not select or
contact an identity provider, fetch JWKS, validate production tokens, enable
production auth, collect evidence, close blockers, launch product, or claim
production readiness.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_production_identity_provider_approval_input_validator import (
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    REQUIRED_TEXT_FIELDS,
    build_validation,
    write_json,
)
from scripts.saee_production_identity_provider_decision_packet import TARGET_KEYS


AUTH_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"
OUTPUT_JSON = AUTH_DIR / "production_identity_provider_input_completion.local.json"
OUTPUT_MD = AUTH_DIR / "production_identity_provider_input_completion.md"
OUTPUT_CSV = AUTH_DIR / "production_identity_provider_input_completion.csv"
GENERATED_INPUT = AUTH_DIR / "production_identity_provider_decision_input.human_filled.local.json"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER_RECOMMENDATION_GATE.md"
)

CSV_FIELDS = [
    "item_id",
    "field_path",
    "item_type",
    "required_value",
    "current_value",
    "source",
    "complete",
    "human_instruction",
]

FALSE_FLAGS: dict[str, bool] = {
    "production_identity_provider_selected": False,
    "production_identity_provider_available": False,
    "production_identity_provider_configured": False,
    "identity_provider_contacted": False,
    "identity_provider_contacted_by_codex": False,
    "jwks_fetched": False,
    "jwks_fetched_by_codex": False,
    "production_tokens_validated_by_codex": False,
    "tokens_validated_in_production": False,
    "production_auth_enabled": False,
    "production_auth_ready": False,
    "oauth_oidc_available": False,
    "rbac_available": False,
    "rbac_enforced_in_production": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "development_permission_granted": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "product_launched": False,
    "public_sdk_released": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
}

REVIEW_FLAG_ARGUMENTS = {
    "production_identity_provider_selected": "confirm_production_identity_provider_selected",
    "identity_provider_admin_owner_named": "confirm_identity_provider_admin_owner_named",
    "oidc_issuer_verified": "confirm_oidc_issuer_verified",
    "oidc_audience_approved": "confirm_oidc_audience_approved",
    "jwks_rotation_policy_reviewed": "confirm_jwks_rotation_policy_reviewed",
}

SOURCE_NOTE_ARGUMENTS = {
    "production_identity_provider_selected": "source_note_production_identity_provider_selected",
    "identity_provider_admin_owner_named": "source_note_identity_provider_admin_owner_named",
    "oidc_issuer_verified": "source_note_oidc_issuer_verified",
    "oidc_audience_approved": "source_note_oidc_audience_approved",
    "jwks_rotation_policy_reviewed": "source_note_jwks_rotation_policy_reviewed",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER: "
            f"FAIL {path} must contain a JSON object"
        )
    return data


def current_template() -> dict[str, Any]:
    return read_json(DEFAULT_INPUT_PATH)


def current_validation() -> dict[str, Any]:
    if DEFAULT_OUTPUT_PATH.exists():
        return read_json(DEFAULT_OUTPUT_PATH)
    return build_validation(DEFAULT_INPUT_PATH)


def bool_arg(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def nonempty_arg(args: argparse.Namespace, name: str) -> str:
    value = getattr(args, name)
    return value.strip() if isinstance(value, str) else ""


def missing_generation_args(args: argparse.Namespace) -> list[str]:
    required_text_args = [
        "human_reviewer_name",
        "review_date",
        "selected_provider_name",
        "decision_summary",
        "selected_provider_slot",
        "candidate_source_note",
    ]
    missing = [
        "--" + name.replace("_", "-")
        for name in required_text_args
        if not nonempty_arg(args, name)
    ]
    for name in REVIEW_FLAG_ARGUMENTS.values():
        if getattr(args, name) is not True:
            missing.append("--" + name.replace("_", "-") + " true")
    for name in SOURCE_NOTE_ARGUMENTS.values():
        if not nonempty_arg(args, name):
            missing.append("--" + name.replace("_", "-"))
    return missing


def generate_human_filled_input(
    template: dict[str, Any],
    args: argparse.Namespace,
    output_path: Path,
) -> dict[str, Any]:
    missing = missing_generation_args(args)
    if missing:
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER: FAIL "
            "human-filled input generation requires " + ", ".join(missing)
        )

    data = copy.deepcopy(template)
    data["input_status"] = "human_filled_identity_provider_local_input"
    data["human_reviewer_name"] = nonempty_arg(args, "human_reviewer_name")
    data["review_date"] = nonempty_arg(args, "review_date")
    data["selected_provider_name"] = nonempty_arg(args, "selected_provider_name")
    data["decision_summary"] = nonempty_arg(args, "decision_summary")

    data["evidence_review"] = {key: True for key in TARGET_KEYS}
    data["source_notes_by_key"] = {
        key: nonempty_arg(args, arg_name)
        for key, arg_name in SOURCE_NOTE_ARGUMENTS.items()
    }
    data["boundary_review"] = {
        flag: False for flag in data.get("boundary_review", {}).keys()
    }

    slots = data.get("candidate_provider_slots", [])
    if not isinstance(slots, list):
        slots = []
    selected_slot_id = nonempty_arg(args, "selected_provider_slot")
    selected_slot_found = False
    for raw_slot in slots:
        if not isinstance(raw_slot, dict):
            continue
        if raw_slot.get("slot_id") != selected_slot_id:
            continue
        raw_slot["provider_name"] = data["selected_provider_name"]
        raw_slot["oidc_supported"] = True
        raw_slot["admin_owner_named"] = True
        raw_slot["issuer_reviewed"] = True
        raw_slot["audience_reviewed"] = True
        raw_slot["jwks_rotation_reviewed"] = True
        raw_slot["human_source_note"] = nonempty_arg(args, "candidate_source_note")
        selected_slot_found = True
    if not selected_slot_found:
        raise SystemExit(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER: FAIL "
            f"selected provider slot not found: {selected_slot_id}"
        )
    data["candidate_provider_slots"] = slots
    data["generation_note"] = (
        "Generated from explicit human-provided identity-provider decision fields "
        "by the local completion helper. This does not contact an identity provider, "
        "fetch JWKS, validate production tokens, enable production auth, collect "
        "evidence, close blockers, or claim production readiness."
    )
    write_json(output_path, data)
    return data


def text_value(template: dict[str, Any], field: str) -> str:
    value = template.get(field, "")
    return value.strip() if isinstance(value, str) else ""


def source_note_value(template: dict[str, Any], key: str) -> str:
    notes = template.get("source_notes_by_key", {})
    if not isinstance(notes, dict):
        return ""
    value = notes.get(key, "")
    return value.strip() if isinstance(value, str) else ""


def evidence_value(template: dict[str, Any], key: str) -> bool:
    review = template.get("evidence_review", {})
    return isinstance(review, dict) and review.get(key) is True


def selected_slot_complete(template: dict[str, Any]) -> bool:
    selected = text_value(template, "selected_provider_name")
    slots = template.get("candidate_provider_slots", [])
    if not selected or not isinstance(slots, list):
        return False
    for raw_slot in slots:
        if not isinstance(raw_slot, dict):
            continue
        if str(raw_slot.get("provider_name", "")).strip() != selected:
            continue
        return (
            bool(str(raw_slot.get("human_source_note", "")).strip())
            and raw_slot.get("oidc_supported") is True
            and raw_slot.get("admin_owner_named") is True
            and raw_slot.get("issuer_reviewed") is True
            and raw_slot.get("audience_reviewed") is True
            and raw_slot.get("jwks_rotation_reviewed") is True
        )
    return False


def completion_rows(template: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in REQUIRED_TEXT_FIELDS:
        value = text_value(template, field)
        rows.append(
            {
                "item_id": f"PIDP-TEXT-{field}",
                "field_path": field,
                "item_type": "required_text_field",
                "required_value": "non_empty_text",
                "current_value": value,
                "source": rel(DEFAULT_INPUT_PATH),
                "complete": bool(value),
                "human_instruction": (
                    f"Fill `{field}` in the identity-provider decision input template."
                ),
            }
        )

    for key in TARGET_KEYS:
        value = evidence_value(template, key)
        rows.append(
            {
                "item_id": f"PIDP-EVIDENCE-{key}",
                "field_path": f"evidence_review.{key}",
                "item_type": "evidence_review_flag",
                "required_value": "true_after_human_review",
                "current_value": str(value).lower(),
                "source": rel(DEFAULT_INPUT_PATH),
                "complete": value,
                "human_instruction": (
                    "Set this evidence review flag to true only after a human "
                    "has reviewed supporting identity-provider evidence."
                ),
            }
        )

    for key in TARGET_KEYS:
        value = source_note_value(template, key)
        rows.append(
            {
                "item_id": f"PIDP-NOTE-{key}",
                "field_path": f"source_notes_by_key.{key}",
                "item_type": "source_note",
                "required_value": "non_empty_human_source_note",
                "current_value": value,
                "source": rel(DEFAULT_INPUT_PATH),
                "complete": bool(value),
                "human_instruction": (
                    "Add a short source note explaining the human-reviewed "
                    f"basis for `{key}`."
                ),
            }
        )

    rows.append(
        {
            "item_id": "PIDP-SLOT-selected_provider_slot",
            "field_path": "candidate_provider_slots[selected_provider_name]",
            "item_type": "selected_provider_slot",
            "required_value": "selected slot has provider name, source note, and OIDC review booleans true",
            "current_value": "complete" if selected_slot_complete(template) else "",
            "source": rel(DEFAULT_INPUT_PATH),
            "complete": selected_slot_complete(template),
            "human_instruction": (
                "Fill the candidate slot that matches `selected_provider_name`: "
                "provider_name, human_source_note, oidc_supported, admin_owner_named, "
                "issuer_reviewed, audience_reviewed, and jwks_rotation_reviewed."
            ),
        }
    )
    return rows


def build_payload(template: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    rows = completion_rows(template)
    completed = sum(1 for row in rows if row["complete"])
    input_complete = completed == len(rows) and validation.get("input_complete") is True
    payload: dict[str, Any] = {
        "production_identity_provider_input_completion_helper_v0_1": True,
        "helper_type": "saee_production_identity_provider_input_completion_helper",
        "helper_version": "v0.1",
        "helper_scope": "local_identity_provider_human_input_completion_sheet",
        "target_blocker_id": "production_identity_provider",
        "status": (
            "ready_for_identity_provider_approval_input_validator"
            if input_complete
            else "hold_human_identity_provider_input_required"
        ),
        "completion_sheet_ready": True,
        "input_complete": input_complete,
        "builder_ready": False,
        "required_item_count": len(rows),
        "completed_item_count": completed,
        "missing_item_count": len(rows) - completed,
        "missing_required_text_fields": validation.get(
            "missing_required_text_fields", []
        ),
        "missing_evidence_review": validation.get("missing_evidence_review", []),
        "missing_source_notes": validation.get("missing_source_notes", []),
        "selected_candidate_missing_fields": validation.get(
            "selected_candidate_missing_fields", []
        ),
        "source_input_template": rel(DEFAULT_INPUT_PATH),
        "source_validation_output": rel(DEFAULT_OUTPUT_PATH),
        "completion_json": rel(OUTPUT_JSON),
        "completion_report": rel(OUTPUT_MD),
        "completion_csv": rel(OUTPUT_CSV),
        "generated_input_supported": True,
        "default_generated_input": rel(GENERATED_INPUT),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": (
            "scripts/saee_production_identity_provider_input_completion_helper.py"
        ),
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_builder_request_required": True,
        "blockers_closed_by_helper": 0,
        "next_action": (
            "A human should fill production_identity_provider_decision_input.template.json "
            "using the completion CSV/report, then rerun the approval input validator. "
            "Do not contact identity providers, fetch JWKS, validate production tokens, "
            "enable production auth, or close blockers from this helper."
        ),
        "items": rows,
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "complete": str(row["complete"]).lower(),
                }
            )


def write_report(payload: dict[str, Any]) -> None:
    rows = payload["items"]
    lines = [
        "# SAEE Production Identity Provider Input Completion Helper",
        "",
        f"Status: {payload['status']}.",
        "",
        "This helper expands the current production identity-provider approval-input gaps into a human-fillable checklist. It does not select or contact an identity provider, fetch JWKS, validate production tokens, enable production auth, collect evidence, close blockers, launch product, or claim production readiness.",
        "",
        "## Summary",
        "",
        f"- helper_type: {payload['helper_type']}",
        f"- helper_scope: {payload['helper_scope']}",
        f"- target_blocker_id: {payload['target_blocker_id']}",
        f"- completion_sheet_ready: {str(payload['completion_sheet_ready']).lower()}",
        f"- required_item_count: {payload['required_item_count']}",
        f"- completed_item_count: {payload['completed_item_count']}",
        f"- missing_item_count: {payload['missing_item_count']}",
        f"- input_complete: {str(payload['input_complete']).lower()}",
        f"- builder_ready: {str(payload['builder_ready']).lower()}",
        "- production_identity_provider_selected: false",
        "- identity_provider_contacted: false",
        "- jwks_fetched: false",
        "- production_auth_enabled: false",
        "- production_ready: false",
        "- blockers_closed_by_helper: 0",
        "",
        "## Missing Human Inputs",
        "",
        "| Item ID | Field Path | Type | Required Value | Complete | Human Instruction |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {item_id} | `{field_path}` | {item_type} | {required_value} | {complete} | {human_instruction} |".format(
                item_id=row["item_id"],
                field_path=row["field_path"],
                item_type=row["item_type"],
                required_value=row["required_value"],
                complete=str(row["complete"]).lower(),
                human_instruction=row["human_instruction"],
            )
        )
    lines.extend(
        [
            "",
            "## How To Use",
            "",
            "1. Fill `phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.template.json` using the missing rows above.",
            "2. Or generate a separate local input file from explicit human-provided fields with `python3 scripts/saee_production_identity_provider_input_completion_helper.py --generate-input ...`.",
            "3. Rerun `python3 scripts/saee_production_identity_provider_approval_input_validator.py --input <human_filled_input.json>`.",
            "4. Continue only if that validator returns `validation_status: pass` and a separate evidence-builder request is explicitly approved.",
            "",
            "## Boundary",
            "",
            "- production_identity_provider_selected: false",
            "- identity_provider_contacted: false",
            "- jwks_fetched: false",
            "- tokens_validated_in_production: false",
            "- production_auth_enabled: false",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    TOP_DOC.write_text(
        f"""# SAEE Production Identity Provider Input Completion Helper v0.1

production_identity_provider_input_completion_helper_v0_1: true
status: {payload['status']}
target_blocker_id: production_identity_provider
completion_sheet_ready: true
input_complete: {str(payload['input_complete']).lower()}
builder_ready: false
blockers_closed_by_helper: 0
production_identity_provider_selected: false
identity_provider_contacted: false
jwks_fetched: false
production_auth_enabled: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This helper converts current `production_identity_provider` approval-input
gaps into local human-fillable completion materials.

It is recommended for local human input completion only. It is not recommended
for production identity-provider selection, identity-provider contact, JWKS
fetching, production token validation, auth enablement, evidence collection,
blocker closure, launch, or production-readiness claims.

## Outputs

- completion JSON: `{rel(OUTPUT_JSON)}`
- completion report: `{rel(OUTPUT_MD)}`
- completion CSV: `{rel(OUTPUT_CSV)}`
- generated input supported: true
- default generated input: `{rel(GENERATED_INPUT)}`

## Run

```bash
python3 scripts/saee_production_identity_provider_input_completion_helper.py
```

To generate a separate local validator input from explicit human-provided
fields, pass `--generate-input` with all required text, confirmation, and source
note arguments. The generated file must still be checked by the approval input
validator and does not close blockers by itself.

## Boundary

This helper does not modify runtime, backend, kernel, API schema, landing page,
or private core. It does not call external services, contact identity
providers, fetch JWKS, validate production tokens, enable production auth, close
blockers, contact customers, launch product, or claim production readiness.
""",
        encoding="utf-8",
    )


def write_gate(payload: dict[str, Any]) -> None:
    GATE.write_text(
        f"""# SAEE Production Identity Provider Input Completion Helper Recommendation Gate

answer: recommend
recommend_for_local_human_input_completion: true
recommend_for_production: false
recommend_for_identity_provider_selection: false
recommend_for_identity_provider_contact: false
recommend_for_jwks_fetch: false
recommend_for_token_validation: false
recommend_for_auth_enablement: false
recommend_for_blocker_closure: false

## Reason

This helper is useful because the current `production_identity_provider`
approval-input validator is on hold and requires human-filled fields before any
separate evidence-builder request can be considered.

## Scope

- status: {payload['status']}
- completion_sheet_ready: true
- generated_input_supported: true
- input_complete: {str(payload['input_complete']).lower()}
- builder_ready: false
- blockers_closed_by_helper: 0
- production_identity_provider_selected: false
- identity_provider_contacted: false
- jwks_fetched: false
- production_auth_enabled: false
- production_ready: false

## Boundary

The helper is not recommended for production use. It is a local completion aid
only. Even when `--generate-input` is used with explicit human-provided fields,
the generated input must pass the separate validator and still does not
authorize execution, evidence collection, provider contact, JWKS fetch,
production token validation, auth enablement, blocker closure, or commercial
launch.
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-input", action="store_true")
    parser.add_argument("--output-input", default=str(GENERATED_INPUT))
    parser.add_argument("--human-reviewer-name", default="")
    parser.add_argument("--review-date", default="")
    parser.add_argument("--selected-provider-name", default="")
    parser.add_argument("--decision-summary", default="")
    parser.add_argument("--selected-provider-slot", default="idp_candidate_a")
    parser.add_argument("--candidate-source-note", default="")
    parser.add_argument(
        "--confirm-production-identity-provider-selected",
        type=bool_arg,
        default=False,
    )
    parser.add_argument(
        "--confirm-identity-provider-admin-owner-named",
        type=bool_arg,
        default=False,
    )
    parser.add_argument("--confirm-oidc-issuer-verified", type=bool_arg, default=False)
    parser.add_argument("--confirm-oidc-audience-approved", type=bool_arg, default=False)
    parser.add_argument(
        "--confirm-jwks-rotation-policy-reviewed",
        type=bool_arg,
        default=False,
    )
    parser.add_argument("--source-note-production-identity-provider-selected", default="")
    parser.add_argument("--source-note-identity-provider-admin-owner-named", default="")
    parser.add_argument("--source-note-oidc-issuer-verified", default="")
    parser.add_argument("--source-note-oidc-audience-approved", default="")
    parser.add_argument("--source-note-jwks-rotation-policy-reviewed", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    template = current_template()
    generated_path = Path(args.output_input)
    if not generated_path.is_absolute():
        generated_path = ROOT / generated_path
    if args.generate_input:
        generate_human_filled_input(template, args, generated_path)
    validation = current_validation()
    payload = build_payload(template, validation)
    write_json(OUTPUT_JSON, payload)
    write_csv(payload["items"])
    write_report(payload)
    write_top_doc(payload)
    write_gate(payload)
    if args.generate_input:
        print(
            "SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER: PASS "
            f"generated_input={rel(generated_path)}"
        )
    else:
        print("SAEE_PRODUCTION_IDENTITY_PROVIDER_INPUT_COMPLETION_HELPER: PASS")


if __name__ == "__main__":
    main()
