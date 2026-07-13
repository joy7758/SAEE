#!/usr/bin/env python3
"""Record exact human approval for the bounded four-builder batch request.

The intake never executes builders. Default behavior restores a waiting state
and emits a blank human template. A human approval record is written only when
the exact phrase, reviewer, reference, and explicit write flag are present.
"""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request"
REQUEST = OUT / "batch_request.local.json"
TEMPLATE = OUT / "batch_approval.template.json"
INTAKE = OUT / "batch_approval_intake.local.json"
CANONICAL_HUMAN_APPROVAL = OUT / "batch_approval.human_filled.local.json"
COPY_MD = OUT / "batch_approval_copy_card.md"
COPY_HTML = OUT / "batch_approval_copy_card.html"
BOUNDARY = OUT / "batch_approval_boundary_audit.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"

EXACT_PHRASE = (
    "批准本地批量证据 builder 执行：仅运行 production_monitoring、"
    "production_restore_policy、formal_security_review、pricing_page 四个 builder，"
    "不关闭 blocker，不联系任何人，不发布，不声明生产可用。"
)

TARGET_IDS = [
    "production_monitoring",
    "production_restore_policy",
    "formal_security_review",
    "pricing_page",
]

FALSE_FLAGS = {
    "builders_executed": 0,
    "blockers_closed": 0,
    "blocker_closure_authorized": False,
    "customer_contacted": False,
    "vendor_contacted": False,
    "external_calls_made": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "private_core_exposed": False,
}


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_template(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "commercial_evidence_builder_batch_approval_input_v0_1": True,
        "human_reviewer_name": "",
        "approval_reference": "",
        "approval_date": "",
        "exact_approval_phrase": "",
        "approve_four_local_builders_only": False,
        "approved_target_blocker_ids": request.get("target_blocker_ids", []),
        "confirm_no_blocker_closure": False,
        "confirm_no_external_contact": False,
        "confirm_no_publication": False,
        "confirm_no_production_readiness_claim": False,
        "confirm_separate_execution_step_required": False,
        **FALSE_FLAGS,
    }


def build_intake(
    request: dict[str, Any], phrase: str, reviewer: str, reference: str, write_approved: bool
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    request_ready = (
        request.get("status") == "ready_for_exact_human_batch_builder_execution_approval"
        and request.get("target_blocker_ids") == TARGET_IDS
        and request.get("ready_target_count") == 4
    )
    phrase_provided = bool(phrase)
    phrase_matches = phrase == EXACT_PHRASE
    metadata_complete = bool(reviewer.strip() and reference.strip())
    approval_record_ready = request_ready and phrase_matches and metadata_complete and write_approved
    status = (
        "exact_human_batch_builder_execution_approval_recorded_no_execution"
        if approval_record_ready
        else (
            "hold_approval_metadata_required"
            if phrase_matches and not metadata_complete
            else "waiting_for_exact_human_batch_builder_execution_approval_phrase"
        )
    )
    summary = {
        "commercial_evidence_builder_batch_approval_intake_v0_1": True,
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_request": str(REQUEST.relative_to(ROOT)),
        "request_ready": request_ready,
        "target_count": 4,
        "approved_target_blocker_ids": TARGET_IDS,
        "exact_approval_phrase_required": True,
        "exact_approval_phrase": EXACT_PHRASE,
        "phrase_provided": phrase_provided,
        "phrase_matches_exactly": phrase_matches,
        "approval_metadata_complete": metadata_complete,
        "human_approval_record_written": approval_record_ready,
        "batch_builder_execution_approved": approval_record_ready,
        "builder_execution_authorized": approval_record_ready,
        "separate_execution_step_required": True,
        "next_human_action": (
            "Run only a separately implemented and separately invoked four-builder executor, then review outputs."
            if approval_record_ready
            else "Review the four-target request and provide the exact approval phrase with reviewer and approval reference."
        ),
        **FALSE_FLAGS,
    }
    record = None
    if approval_record_ready:
        record = {
            "commercial_evidence_builder_batch_human_approval_v0_1": True,
            "status": "approved_four_local_builders_pending_separate_execution",
            "human_reviewer_name": reviewer.strip(),
            "approval_reference": reference.strip(),
            "approval_date": datetime.now(timezone.utc).date().isoformat(),
            "exact_approval_phrase": phrase,
            "approve_four_local_builders_only": True,
            "approved_target_blocker_ids": TARGET_IDS,
            "confirm_no_blocker_closure": True,
            "confirm_no_external_contact": True,
            "confirm_no_publication": True,
            "confirm_no_production_readiness_claim": True,
            "confirm_separate_execution_step_required": True,
            "batch_builder_execution_approved": True,
            "builder_execution_authorized": True,
            **FALSE_FLAGS,
        }
    return summary, record


def render_copy_card(summary: dict[str, Any]) -> str:
    return f"""# SAEE Four-Builder Batch Approval Copy Card

Status: `{summary['status']}`.

After reviewing the four request rows, a human may copy this exact phrase:

```text
{EXACT_PHRASE}
```

Required metadata:

- human reviewer name
- approval reference

Boundary: the approval authorizes only a separate later local execution step.
It executes zero builders, closes zero blockers, contacts no one, publishes
nothing, and does not claim production readiness.
"""


def render_html(summary: dict[str, Any]) -> str:
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SAEE 批量 Builder 批准短语</title><style>body{{margin:0;background:#f6f3eb;color:#15211d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{width:min(900px,calc(100% - 32px));margin:auto;padding:48px 0}}.card{{padding:24px;background:#fffdf8;border:1px solid #d8d3c8;border-radius:14px}}h1{{font-size:clamp(34px,6vw,60px);line-height:1.05}}.phrase{{padding:20px;background:#13241e;color:#d9ffac;border-radius:12px;font-family:ui-monospace,SFMono-Regular,monospace;overflow-wrap:anywhere}}p,li{{color:#60706a}}</style></head><body><main><h1>人工批准可以被记录，<br>但不会自动执行。</h1><section class="card"><p>当前状态：<code>{html.escape(summary['status'])}</code></p><h2>精确短语</h2><div class="phrase">{html.escape(EXACT_PHRASE)}</div><ul><li>还需要 reviewer 与 approval reference。</li><li>本页面不提交、不运行 builder、不关闭 blocker。</li><li>批准后仍需独立 executor。</li></ul></section></main></body></html>"""


def update_agent_index(summary: dict[str, Any]) -> None:
    data = read_json(AGENT_INDEX)
    data["commercial_evidence_builder_batch_approval_intake_v0_1"] = {
        "status": summary["status"],
        "target_count": 4,
        "approved_target_blocker_ids": TARGET_IDS,
        "exact_approval_phrase_required": True,
        "human_approval_record_written": summary["human_approval_record_written"],
        "batch_builder_execution_approved": summary["batch_builder_execution_approved"],
        "builder_execution_authorized": summary["builder_execution_authorized"],
        "separate_execution_step_required": True,
        "builders_executed": 0,
        "blockers_closed": 0,
        "entrypoints": {
            "template": "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_approval.template.json",
            "intake": "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_approval_intake.local.json",
            "copy_card": "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_approval_copy_card.html",
            "runner": "scripts/saee_commercial_evidence_builder_batch_approval_intake.py",
            "smoke": "scripts/saee_commercial_evidence_builder_batch_approval_intake_smoke.py",
        },
        **{key: value for key, value in FALSE_FLAGS.items() if key not in {"builders_executed", "blockers_closed"}},
    }
    write_json(AGENT_INDEX, data)


def append_llms() -> None:
    additions = [
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_approval.template.json",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_approval_intake.local.json",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_approval_copy_card.md",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_approval_copy_card.html",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_approval_boundary_audit.md",
        "/scripts/saee_commercial_evidence_builder_batch_approval_intake.py",
        "/scripts/saee_commercial_evidence_builder_batch_approval_intake_smoke.py",
    ]
    lines = LLMS.read_text(encoding="utf-8").splitlines()
    for item in additions:
        if item not in lines:
            lines.append(item)
    write(LLMS, "\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phrase", default="")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--approval-reference", default="")
    parser.add_argument("--write-human-approved", action="store_true")
    parser.add_argument("--human-approved-output", default=str(CANONICAL_HUMAN_APPROVAL))
    args = parser.parse_args()

    request = read_json(REQUEST)
    template = build_template(request)
    summary, record = build_intake(
        request, args.phrase.strip(), args.reviewer, args.approval_reference, args.write_human_approved
    )
    write_json(TEMPLATE, template)
    write_json(INTAKE, summary)
    write(COPY_MD, render_copy_card(summary))
    write(COPY_HTML, render_html(summary))
    write(
        BOUNDARY,
        "# SAEE Batch Approval Intake Boundary Audit\n\n"
        "- exact phrase plus reviewer and reference required\n"
        "- separate executor required\n- builders_executed: 0\n- blockers_closed: 0\n"
        "- blocker_closure_authorized: false\n- external_calls_made: false\n"
        "- production_ready: false\n",
    )
    if record is not None:
        write_json(Path(args.human_approved_output), record)
    update_agent_index(summary)
    append_llms()
    print(
        "SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_APPROVAL_INTAKE: PASS "
        f"status={summary['status']} approval_record_written={str(summary['human_approval_record_written']).lower()} "
        "builders_executed=0 blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
