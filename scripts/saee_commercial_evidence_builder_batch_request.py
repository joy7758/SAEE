#!/usr/bin/env python3
"""Generate a bounded human approval request for four local evidence builders.

This request generator never executes builders. It only proves that the four
source validators pass and publishes an exact, reviewable approval scope.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request"
SUMMARY_PATH = OUT / "batch_request.local.json"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"

EXACT_PHRASE = (
    "批准本地批量证据 builder 执行：仅运行 production_monitoring、"
    "production_restore_policy、formal_security_review、pricing_page 四个 builder，"
    "不关闭 blocker，不联系任何人，不发布，不声明生产可用。"
)

TARGETS = [
    {
        "blocker_id": "production_monitoring",
        "validator": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_approval_input_validation.local.json",
        "input": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json",
        "builder_output": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_builder_output.local.json",
        "command": "python3 scripts/saee_production_monitoring_evidence_builder.py --input phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json",
    },
    {
        "blocker_id": "production_restore_policy",
        "validator": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input_validation.local.json",
        "input": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json",
        "builder_output": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_evidence_builder_output.local.json",
        "command": "python3 scripts/saee_production_restore_policy_evidence_builder.py --input phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json",
    },
    {
        "blocker_id": "formal_security_review",
        "validator": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_validation.local.json",
        "input": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json",
        "builder_output": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_builder_output.local.json",
        "command": "python3 scripts/saee_formal_security_review_evidence_builder.py --input phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json",
    },
    {
        "blocker_id": "pricing_page",
        "validator": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_approval_input_validation.local.json",
        "input": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json",
        "builder_output": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_builder_output.local.json",
        "command": "python3 scripts/saee_pricing_page_evidence_builder.py --input phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json",
    },
]

FALSE_FLAGS = {
    "batch_execution_authorized": False,
    "evidence_collection_authorized": False,
    "blocker_closure_authorized": False,
    "customer_contacted": False,
    "vendor_contacted": False,
    "external_calls_made": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "private_core_exposed": False,
}


def read_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {relative_path}")
    return data


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def target_record(target: dict[str, str]) -> dict[str, Any]:
    validation = read_json(target["validator"])
    builder_output = read_json(target["builder_output"])
    validator_passed = validation.get("validation_status") == "pass"
    builder_ready = validation.get("builder_ready") is True
    input_complete = validation.get("input_complete") is True
    builder_still_hold = builder_output.get("status") == "hold"
    return {
        **target,
        "validator_passed": validator_passed,
        "builder_ready": builder_ready,
        "input_complete": input_complete,
        "builder_output_status_before_request": builder_output.get("status", "unknown"),
        "builder_still_hold": builder_still_hold,
        "included_in_request": validator_passed and builder_ready and input_complete and builder_still_hold,
        "execution_authorized": False,
        "builder_executed_by_request": False,
        "blocker_closed_by_request": False,
    }


def build_summary() -> dict[str, Any]:
    targets = [target_record(target) for target in TARGETS]
    ready_count = sum(item["included_in_request"] for item in targets)
    status = (
        "ready_for_exact_human_batch_builder_execution_approval"
        if ready_count == len(TARGETS)
        else "hold_batch_builder_sources_not_ready"
    )
    return {
        "commercial_evidence_builder_batch_request_v0_1": True,
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "request_scope": "four_validator_passed_local_commercial_evidence_builders_only",
        "target_count": len(targets),
        "ready_target_count": ready_count,
        "target_blocker_ids": [item["blocker_id"] for item in targets],
        "targets": targets,
        "exact_human_approval_phrase_required": True,
        "exact_human_approval_phrase": EXACT_PHRASE,
        "approval_phrase_provided": False,
        "approval_phrase_matches_exactly": False,
        "human_approval_recorded": False,
        "builders_executed_by_request": 0,
        "blockers_closed_by_request": 0,
        "separate_builder_execution_step_required": True,
        "separate_blocker_closure_review_required": True,
        "next_human_action": (
            "Review the four target rows and, only if the scope is approved, provide the exact human approval phrase in a separate approval-intake step."
        ),
        **FALSE_FLAGS,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    rows = []
    for item in summary["targets"]:
        rows.append(
            f"| `{item['blocker_id']}` | {str(item['validator_passed']).lower()} | "
            f"{str(item['builder_ready']).lower()} | `{item['builder_output_status_before_request']}` | "
            f"`{item['command']}` |"
        )
    return f"""# SAEE Commercial Evidence Builder Batch Request

Status: `{summary['status']}`.

This packet requests one bounded human review for four local evidence builders.
It does not approve or execute them.

| Blocker | Validator pass | Builder ready | Current output | Command after separate approval |
| --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Exact Human Approval Phrase

```text
{EXACT_PHRASE}
```

## Boundary

- batch_execution_authorized: false
- builders_executed_by_request: 0
- blocker_closure_authorized: false
- blockers_closed_by_request: 0
- customer_contacted: false
- vendor_contacted: false
- external_calls_made: false
- product_launched: false
- production_ready: false
- customer_validated: false

The exact phrase authorizes only a later local builder execution step. It never
authorizes blocker closure, publication, external contact, or production claims.
"""


def render_html(summary: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(item['blocker_id'])}</code></td>"
        f"<td>{str(item['validator_passed']).lower()}</td>"
        f"<td>{str(item['builder_ready']).lower()}</td>"
        f"<td><code>{html.escape(item['builder_output_status_before_request'])}</code></td>"
        f"<td><code>{html.escape(item['command'])}</code></td>"
        "</tr>"
        for item in summary["targets"]
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAEE 批量证据 Builder 审批请求</title>
<style>
:root{{--bg:#f6f3eb;--panel:#fffdf8;--ink:#15211d;--muted:#60706a;--line:#d8d3c8;--accent:#0b6e52}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.6}}
main{{width:min(1180px,calc(100% - 32px));margin:auto;padding:42px 0 60px}}h1{{font-size:clamp(34px,5vw,62px);line-height:1.05;margin:0 0 14px}}p{{color:var(--muted)}}.pill{{display:inline-block;padding:6px 10px;background:#e5f2ed;color:var(--accent);border-radius:999px;font-weight:700;font-size:12px}}
.card{{margin-top:20px;padding:22px;background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:auto}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}code{{overflow-wrap:anywhere}}.phrase{{padding:18px;background:#13241e;color:#d9ffac;border-radius:12px;font-family:ui-monospace,SFMono-Regular,monospace}}ul{{color:var(--muted)}}
</style></head><body><main>
<span class="pill">只生成审批请求 · 不执行</span><h1>四个本地证据 builder，<br>一次做范围审查。</h1>
<p>四个来源 validator 均已通过，builder 输出仍为 hold。此页面不运行任何命令。</p>
<section class="card"><table><thead><tr><th>Blocker</th><th>Validator</th><th>Ready</th><th>Output</th><th>审批后命令</th></tr></thead><tbody>{rows}</tbody></table></section>
<section class="card"><h2>精确人工批准短语</h2><div class="phrase">{html.escape(EXACT_PHRASE)}</div><p>仅在人工审查四行范围后使用；它本身不执行 builder。</p></section>
<section class="card"><h2>不能由本请求完成</h2><ul><li>不关闭 blocker，不发布，不联系客户或供应商。</li><li>不把本地 evidence output 说成生产运行证据。</li><li>不声明 production-ready、customer-validated 或 launched。</li></ul></section>
</main></body></html>"""


def render_boundary() -> str:
    return """# SAEE Commercial Evidence Builder Batch Request Boundary Audit

- Request generation only.
- Target count is exactly four.
- No builder process is invoked.
- No evidence collection is authorized.
- No blocker closure is authorized.
- No customer or vendor contact is performed.
- No publication or production-readiness claim is added.
- A separate exact human approval intake is required before any execution.
"""


def update_agent_index(summary: dict[str, Any]) -> None:
    data = read_json("agent-index.json")
    data["commercial_evidence_builder_batch_request_v0_1"] = {
        "status": summary["status"],
        "request_scope": summary["request_scope"],
        "target_count": summary["target_count"],
        "ready_target_count": summary["ready_target_count"],
        "target_blocker_ids": summary["target_blocker_ids"],
        "exact_human_approval_phrase_required": True,
        "human_approval_recorded": False,
        "builders_executed_by_request": 0,
        "blockers_closed_by_request": 0,
        "entrypoints": {
            "json": "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_request.local.json",
            "markdown": "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_request.md",
            "html": "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_request.html",
            "gate": "docs/strategy/SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_REQUEST_GATE.md",
            "generator": "scripts/saee_commercial_evidence_builder_batch_request.py",
            "smoke": "scripts/saee_commercial_evidence_builder_batch_request_smoke.py",
        },
        **FALSE_FLAGS,
    }
    write_json(AGENT_INDEX, data)


def append_llms() -> None:
    additions = [
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/README.md",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_request.local.json",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_request.md",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_request.html",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/BOUNDARY_AUDIT.md",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_REQUEST_GATE.md",
        "/scripts/saee_commercial_evidence_builder_batch_request.py",
        "/scripts/saee_commercial_evidence_builder_batch_request_smoke.py",
    ]
    text = LLMS.read_text(encoding="utf-8")
    lines = text.splitlines()
    for item in additions:
        if item not in lines:
            lines.append(item)
    write(LLMS, "\n".join(lines) + "\n")


def insert_status_block(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = f"<!-- BEGIN {marker} -->"
    end = f"<!-- END {marker} -->"
    wrapped = f"{start}\n\n{block.strip()}\n\n{end}"
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        write(path, before + wrapped + after)
    else:
        first_break = text.find("\n") + 1
        write(path, text[:first_break] + "\n" + wrapped + "\n" + text[first_break:])


def update_root_surfaces(summary: dict[str, Any]) -> None:
    block = f"""## Commercial Evidence Builder Batch Request

Four validator-passed local evidence builders are grouped into one bounded
human review request at
`phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_request.html`.
Current status is `{summary['status']}` with `target_count=4`,
`human_approval_recorded=false`, `builders_executed_by_request=0`, and
`blockers_closed_by_request=0`. This is not execution or production evidence.
The exact-phrase intake is
`phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_approval_intake.local.json`;
its default status is
`waiting_for_exact_human_batch_builder_execution_approval_phrase` and it also
executes zero builders.
"""
    for filename in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "agent-readable.md"]:
        insert_status_block(ROOT / filename, "SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_REQUEST", block)
    changelog = """- Added a bounded four-target commercial evidence-builder batch request. It records validator-passed scope and an exact human approval phrase while executing zero builders and closing zero blockers."""
    insert_status_block(ROOT / "CHANGELOG.md", "SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_REQUEST", changelog)


def main() -> None:
    summary = build_summary()
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(SUMMARY_PATH, summary)
    write(OUT / "README.md", render_markdown(summary))
    write(OUT / "batch_request.md", render_markdown(summary))
    write(OUT / "batch_request.html", render_html(summary))
    write(OUT / "BOUNDARY_AUDIT.md", render_boundary())
    update_agent_index(summary)
    append_llms()
    update_root_surfaces(summary)
    print(
        "SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_REQUEST: PASS "
        f"status={summary['status']} targets={summary['target_count']} "
        "builders_executed=0 blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
