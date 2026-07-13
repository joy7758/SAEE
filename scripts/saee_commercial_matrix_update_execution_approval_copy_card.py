#!/usr/bin/env python3
"""Create a local copy card for the exact matrix-update approval phrase.

This is a human-facing helper for the current commercial blocker path. It does
not write approval input, execute a matrix update, close blockers, publish
pricing, enable checkout, or claim production readiness.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_DIR = COMMERCIAL_DIR / "matrix_update_requests"

PHRASE_INTAKE = OUT_DIR / "commercial_matrix_update_execution_approval_phrase_intake.local.json"
APPROVAL_VALIDATION = OUT_DIR / "commercial_matrix_update_execution_approval_validation.local.json"
APPLIER = OUT_DIR / "commercial_matrix_update_execution_applier.local.json"
GAP_MATRIX = COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json"
HUMAN_FILLED = OUT_DIR / "commercial_matrix_update_execution_approval_input.human_filled.local.json"

OUT_JSON = OUT_DIR / "commercial_matrix_update_execution_approval_copy_card.local.json"
OUT_MD = OUT_DIR / "commercial_matrix_update_execution_approval_copy_card.md"
OUT_HTML = OUT_DIR / "commercial_matrix_update_execution_approval_copy_card.html"
OUT_AUDIT = OUT_DIR / "commercial_matrix_update_execution_approval_copy_card_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_GATE.md"

AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"

EXACT_APPROVAL_PHRASE = (
    "批准矩阵更新执行：仅应用 review-ready markers，不关闭 blocker，不发布价格页，不启用 checkout，不声明生产可用。"
)

FALSE_FLAGS = {
    "human_filled_approval_written": False,
    "human_execution_approved": False,
    "ready_for_matrix_update_execution": False,
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_copy_card": 0,
    "open_blocker_count_reduced": False,
    "pricing_page_published": False,
    "checkout_enabled": False,
    "customer_payment_collected": False,
    "revenue_validated": False,
    "development_permission_granted": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def ensure_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in text.splitlines():
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")


def build_payload() -> dict[str, Any]:
    phrase_intake = read_json(PHRASE_INTAKE)
    approval = read_json(APPROVAL_VALIDATION)
    applier = read_json(APPLIER)
    gap = read_json(GAP_MATRIX)

    human_filled_exists = HUMAN_FILLED.exists()
    open_blocker_count = int(gap.get("open_blocker_count", gap.get("production_blocker_count", 0)) or 0)
    source_ready = (
        applier.get("status") == "hold_human_execution_approval_required"
        and approval.get("ready_for_matrix_update_execution") is False
        and not human_filled_exists
        and open_blocker_count >= 1
    )
    status = (
        "ready_for_exact_phrase_human_approval_no_execution"
        if source_ready
        else "hold_matrix_update_copy_card_source_state_changed"
    )
    return {
        "commercial_matrix_update_execution_approval_copy_card_v0_1": True,
        "card_type": "local_exact_phrase_copy_helper_no_execution",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Give the human reviewer one local Chinese copy card for the exact "
            "matrix-update execution approval phrase."
        ),
        "exact_phrase_required": True,
        "exact_approval_phrase": EXACT_APPROVAL_PHRASE,
        "human_filled_approval_path": rel(HUMAN_FILLED),
        "human_filled_approval_exists": human_filled_exists,
        "source_phrase_intake": rel(PHRASE_INTAKE),
        "source_phrase_intake_status": phrase_intake.get("status"),
        "source_approval_validation": rel(APPROVAL_VALIDATION),
        "source_approval_validation_status": approval.get("status"),
        "source_applier": rel(APPLIER),
        "source_applier_status": applier.get("status"),
        "open_blocker_count": open_blocker_count,
        "copy_card_html": rel(OUT_HTML),
        "copy_card_markdown": rel(OUT_MD),
        "next_human_action": (
            "If matrix review-ready marker execution is desired, send the exact "
            "approval phrase back to Codex. Codex must then run the phrase intake, "
            "approval validator, dry run, and applier checks in order."
        ),
        "recommended_command_after_phrase_received": (
            "python3 scripts/saee_commercial_matrix_update_execution_approval_phrase_intake.py "
            "--phrase '<EXACT_APPROVAL_PHRASE>' --write-human-filled"
        ),
        **FALSE_FLAGS,
    }


def write_markdown(payload: dict[str, Any]) -> None:
    OUT_MD.write_text(
        f"""# SAEE Commercial Matrix Update Execution Approval Copy Card v0.1

Status: `{payload['status']}`

This local card makes the current human approval point explicit. It does not
write the human-filled approval file and does not execute a matrix update.

## Exact Phrase To Copy

`{EXACT_APPROVAL_PHRASE}`

## What Happens If The Human Sends This Phrase Later

Codex may then run the separate phrase intake and validation path. The matrix
applier still only applies review-ready markers and must keep blockers open.

## Current Truth

- human_filled_approval_exists: `{str(payload['human_filled_approval_exists']).lower()}`
- human_execution_approved: `false`
- ready_for_matrix_update_execution: `false`
- matrix_update_executed: `false`
- canonical_gap_matrix_modified: `false`
- blocker_closure_authorized: `false`
- blockers_closed_by_copy_card: `0`
- open_blocker_count: `{payload['open_blocker_count']}`
- production_ready: `false`
- customer_validated: `false`
- product_launched: `false`

## Boundary

This card does not publish pricing, enable checkout, contact customers, call
external services, modify runtime/backend/kernel/API schema, expose private
core, or claim production readiness.
""",
        encoding="utf-8",
    )


def write_html(payload: dict[str, Any]) -> None:
    phrase = html.escape(EXACT_APPROVAL_PHRASE)
    status = html.escape(str(payload["status"]))
    OUT_HTML.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SAEE 矩阵更新批准复制卡</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f4;
      --ink: #171717;
      --muted: #62625d;
      --line: #deded7;
      --panel: #ffffff;
      --accent: #0f6f5c;
      --warn: #8a5a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.55;
    }}
    main {{
      max-width: 920px;
      margin: 0 auto;
      padding: 56px 20px;
    }}
    h1 {{
      font-size: clamp(32px, 5vw, 56px);
      line-height: 1.06;
      letter-spacing: 0;
      margin: 0 0 18px;
    }}
    .lead {{
      font-size: 20px;
      color: var(--muted);
      max-width: 720px;
      margin: 0 0 32px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 24px;
      box-shadow: 0 18px 60px rgba(0, 0, 0, 0.06);
    }}
    .status {{
      display: inline-flex;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 12px;
      color: var(--warn);
      background: #fffaf0;
      font-size: 14px;
      margin-bottom: 20px;
    }}
    textarea {{
      width: 100%;
      min-height: 116px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      font: 18px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
      color: var(--ink);
      background: #fbfbf8;
    }}
    button {{
      margin-top: 14px;
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      background: var(--ink);
      color: white;
      font-size: 16px;
      cursor: pointer;
    }}
    button:focus-visible {{
      outline: 3px solid rgba(15, 111, 92, 0.28);
      outline-offset: 2px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 22px;
    }}
    .item {{
      border-top: 1px solid var(--line);
      padding-top: 12px;
      color: var(--muted);
    }}
    .item strong {{
      display: block;
      color: var(--ink);
      font-size: 15px;
    }}
    .note {{
      margin-top: 24px;
      color: var(--muted);
      font-size: 15px;
    }}
  </style>
</head>
<body>
  <main>
    <h1>只差一句明确授权</h1>
    <p class="lead">这一步只允许记录 review-ready 标记，不关闭 blocker，不发布价格页，不启用 checkout，也不声明生产可用。</p>
    <section class="panel">
      <div class="status">当前状态：{status}</div>
      <label for="phrase"><strong>需要复制并发回 Codex 的完整句子</strong></label>
      <textarea id="phrase" readonly>{phrase}</textarea>
      <button type="button" onclick="copyPhrase()">复制这句话</button>
      <div class="grid">
        <div class="item"><strong>矩阵更新</strong>未执行</div>
        <div class="item"><strong>Blocker</strong>不会被关闭</div>
        <div class="item"><strong>生产可用</strong>仍为 false</div>
        <div class="item"><strong>客户验证</strong>仍为 false</div>
      </div>
      <p class="note">复制后，把这句话原样发给 Codex。Codex 仍需先跑批准入口、验证器、dry run 和 applier 检查。</p>
    </section>
  </main>
  <script>
    async function copyPhrase() {{
      const el = document.getElementById('phrase');
      el.select();
      try {{
        await navigator.clipboard.writeText(el.value);
      }} catch (err) {{
        document.execCommand('copy');
      }}
    }}
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_audit(payload: dict[str, Any]) -> None:
    OUT_AUDIT.write_text(
        """# SAEE Commercial Matrix Update Execution Approval Copy Card Boundary Audit

- Local copy card generated.
- No human-filled approval file written.
- No matrix update executed.
- No canonical gap matrix modified.
- No blocker closed.
- No pricing page published.
- No checkout enabled.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No production-ready claim added.
""",
        encoding="utf-8",
    )


def update_surfaces(payload: dict[str, Any]) -> None:
    TOP_DOC.write_text(
        f"""# SAEE Commercial Matrix Update Execution Approval Copy Card v0.1

commercial_matrix_update_execution_approval_copy_card_v0_1: true
status: {payload['status']}

Purpose: expose the exact human approval phrase through a local Chinese copy
card. This is a convenience layer only; it does not write approval input,
execute matrix updates, close blockers, publish pricing, enable checkout, or
claim production readiness.

Entrypoints:

- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.html`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.local.json`
- `scripts/saee_commercial_matrix_update_execution_approval_copy_card.py`
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Matrix Update Execution Approval Copy Card Gate

answer: {payload['status']}

reason: The current matrix-update path is blocked on exact human approval. This
card makes the exact phrase easier to copy but does not execute any approval or
matrix update.

boundary:
- human_filled_approval_written: false
- human_execution_approved: false
- ready_for_matrix_update_execution: false
- matrix_update_executed: false
- canonical_gap_matrix_modified: false
- blocker_closure_authorized: false
- blockers_closed_by_copy_card: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: Human may send the exact approval phrase if review-ready marker
execution is desired.
""",
        encoding="utf-8",
    )
    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.html",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_approval_copy_card.py",
        "/scripts/saee_commercial_matrix_update_execution_approval_copy_card_smoke.py",
    ]:
        ensure_line(LLMS, line)
    index = read_json(AGENT_INDEX)
    index["commercial_matrix_update_execution_approval_copy_card_v0_1"] = {
        "status": payload["status"],
        "card_type": payload["card_type"],
        "exact_phrase_required": True,
        "human_filled_approval_written": False,
        "human_execution_approved": False,
        "ready_for_matrix_update_execution": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_copy_card": 0,
        "open_blocker_count": payload["open_blocker_count"],
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "entrypoints": {
            "html": rel(OUT_HTML),
            "json": rel(OUT_JSON),
            "markdown": rel(OUT_MD),
            "boundary_audit": rel(OUT_AUDIT),
            "runner": "scripts/saee_commercial_matrix_update_execution_approval_copy_card.py",
            "smoke": "scripts/saee_commercial_matrix_update_execution_approval_copy_card_smoke.py",
        },
    }
    write_json(AGENT_INDEX, index)


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_markdown(payload)
    write_html(payload)
    write_audit(payload)
    update_surfaces(payload)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_COPY_CARD: PASS "
        f"status={payload['status']} "
        "human_execution_approved=false matrix_update_executed=false "
        "blockers_closed_by_copy_card=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
