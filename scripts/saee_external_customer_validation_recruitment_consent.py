#!/usr/bin/env python3
"""Prepare the external customer validation recruitment and consent packet."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = BASE / "external_customer_validation_recruitment_consent"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_RECRUITMENT_CONSENT_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


SUMMARY = {
    "external_customer_validation_recruitment_consent_v0_1": True,
    "status": "prepared_for_human_outreach_no_contact_by_codex",
    "packet_type": "manual_external_customer_validation_recruitment_consent",
    "current_goal_blocker": "customer_validated",
    "planned_external_sessions": 1,
    "human_outreach_required": True,
    "human_session_required": True,
    "codex_may_contact_customer": False,
    "codex_contacted_customer": False,
    "customer_contacted_by_codex": False,
    "human_session_performed": False,
    "human_result_entered": False,
    "customer_validated": False,
    "production_ready": False,
    "product_launched": False,
    "public_sdk_released": False,
    "private_core_exposed": False,
    "external_model_api_called": False,
    "blockers_closed_by_packet": 0,
    "next_human_action": "Human selects one real external customer or target user, sends the invitation manually, records consent, runs the interview, then fills the existing session entry template.",
    "entrypoints": {
        "readme": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/README.md",
        "invitation": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md",
        "screening": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md",
        "consent": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md",
        "boundary_audit": "phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/BOUNDARY_AUDIT.md",
        "gate": "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_RECRUITMENT_CONSENT_GATE.md",
        "runner": "scripts/saee_external_customer_validation_recruitment_consent.py",
        "smoke": "scripts/saee_external_customer_validation_recruitment_consent_smoke.py",
    },
}


README = """# SAEE External Customer Validation Recruitment and Consent Packet v0.1

Status: prepared_for_human_outreach_no_contact_by_codex.

This packet lowers the remaining customer-validation blocker by giving a human
operator a plain invitation, participant screening checklist, and consent /
boundary script for one real external customer or target-user session.

It is not customer validation evidence by itself. Codex does not send the
message, contact anyone, run the interview, infer feedback, close blockers,
launch product, or claim production readiness.

## Use Order

1. Read `PARTICIPANT_SCREENING_CHECKLIST.md`.
2. Choose one real external customer or target user.
3. Manually adapt and send `INVITATION_MESSAGE_DRAFT.md`.
4. Before the session, read `CONSENT_AND_BOUNDARY_SCRIPT.md`.
5. Run the existing interview script:
   `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_interview_script.md`.
6. Enter the result with the existing workbench or session-entry template.

## State

```yaml
external_customer_validation_recruitment_consent_v0_1: true
status: prepared_for_human_outreach_no_contact_by_codex
current_goal_blocker: customer_validated
codex_may_contact_customer: false
customer_contacted_by_codex: false
human_session_performed: false
customer_validated: false
production_ready: false
product_launched: false
private_core_exposed: false
blockers_closed_by_packet: 0
```
"""


INVITATION = """# SAEE External Customer Validation Invitation Message Draft

Use this only as a human-edited draft. Codex does not send it.

## Short Chinese Draft

你好，我正在验证一个用于比较多个 AI 智能体、自动化工作流或决策策略长期稳定性的工具，名字叫 SAEE。

我想请你用大约 20 分钟看一个本地演示或截图，然后回答几个问题：你是否看得懂它给出的排名、推荐对象、失败摘要和部署前风险提示；这些信息是否会影响你上线、暂缓或重测某个方案。

这不是销售沟通，也不会要求你提供源码、密钥、生产数据、客户数据或内部流程细节。你可以完全基于虚构或脱敏场景回答。

当前 SAEE 还不是生产可用产品，也没有公开 SDK。本次只验证它的表达和决策价值是否对目标用户有帮助。

如果你愿意参与，我会先说明记录范围和边界，再开始访谈。

## Send Rules

- Sender must be a human operator, not Codex.
- Send to one real external customer or target user only for Run 001.
- Do not promise production readiness.
- Do not imply customer validation is already complete.
- Do not request secrets, source code, production data, or customer data.
- Do not publish the participant name, company, or quote without separate permission.
"""


SCREENING = """# SAEE Participant Screening Checklist

Use this before inviting a participant.

## Good Fit

The participant is a good fit if at least one is true:

- They compare multiple AI agents, workflow versions, prompt strategies, or decision policies.
- They care about pre-deployment risk, long-term stability, failure modes, or repeat-run reliability.
- They can judge whether ranking, recommended option, failure summary, survival curve, or deployment advice would help a real decision.

## Not A Good Fit For This Session

Do not count the session as customer validation if the participant:

- Is only the founder or an internal-only reviewer.
- Only wants single-run tracing, logging, or span inspection.
- Only wants prompt debugging or prompt scoring.
- Only wants production monitoring, alerting, or incident response.
- Only wants a full quant trading platform.
- Requires production deployment, public SDK, or private core access before they can evaluate the concept.

## Data Safety

Stop or redirect the session if the participant wants to provide:

- Source code.
- API keys, passwords, or credentials.
- Production data.
- Customer data.
- Private workflow internals.
- Regulated personal information.

## Minimum Record Needed

For Run 001, one qualified external customer or target-user session is enough to
produce an importable evidence entry, but it does not automatically make SAEE
production-ready.
"""


CONSENT = """# SAEE Consent and Boundary Script

Read this before the human-run external customer or target-user session.

## Plain Consent Script

这次访谈的目的，是判断 SAEE 的本地演示和结果表达是否能帮助你理解多个 AI 智能体、工作流或策略版本的长期稳定性和部署前风险。

我只会记录摘要、评分和非敏感意见。请不要提供源码、密钥、生产数据、客户数据或内部机密流程。

你可以随时跳过问题或停止访谈。你的反馈只会作为 SAEE 商用准备的内部验证材料，除非另行获得你的明确许可，不会公开你的姓名、公司或原话。

SAEE 当前不是生产可用产品，也没有公开 SDK。本次访谈不会要求你上线使用，也不会形成采购承诺。

## Boundary Confirmation

Before continuing, confirm:

- Participant understands this is feedback, not a production rollout.
- Participant will not share secrets or production/customer data.
- Participant agrees that only summary feedback and scores may be recorded.
- Participant understands SAEE private core details will not be disclosed.

## Required Flags After Session

These flags must remain false unless a real issue occurred and is explicitly recorded:

```yaml
secrets_collected: false
production_data_collected: false
customer_data_uploaded: false
private_core_disclosed: false
production_ready_claim_made: false
```
"""


BOUNDARY = """# SAEE External Customer Validation Recruitment Consent Boundary Audit

- Codex did not contact customers.
- Codex did not send invitations.
- Codex did not run an external customer session.
- Codex did not collect customer data.
- Codex did not infer customer feedback.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No landing page interaction modified.
- No private core exposed.
- No product launched.
- No public SDK released.
- No production-ready claim added.
- No customer-validation claim added.
- No blocker closed.

Final decision: boundary safe for a manual human outreach preparation packet.
"""


GATE_TEXT = """# SAEE External Customer Validation Recruitment Consent Gate

answer: prepared_for_human_outreach_no_contact_by_codex

reason: The remaining commercial blocker is `customer_validated`. This packet
prepares a human-safe invitation, screening checklist, and consent script for
one real external customer or target-user session without contacting anyone or
claiming validation.

boundary:

- codex_may_contact_customer: false
- customer_contacted_by_codex: false
- human_session_performed: false
- customer_validated: false
- production_ready: false
- product_launched: false
- private_core_exposed: false
- blockers_closed_by_packet: 0

next_action: A human operator may manually invite one qualified external
customer or target user, record consent, run the existing interview script, and
enter the session result into the existing session-entry workflow.
"""


STATUS_BLOCK = """## External Customer Validation Recruitment and Consent Packet v0.1

- `external_customer_validation_recruitment_consent_v0_1=true`
- Status: `prepared_for_human_outreach_no_contact_by_codex`.
- Purpose: provide a human-safe invitation draft, participant screening
  checklist, and consent script for the first real external customer or
  target-user validation session.
- Current blocker: `customer_validated`.
- Boundary: `codex_may_contact_customer=false`,
  `customer_contacted_by_codex=false`, `human_session_performed=false`,
  `customer_validated=false`, `production_ready=false`,
  `product_launched=false`, `private_core_exposed=false`, and
  `blockers_closed_by_packet=0`.
"""


LLMS_PATHS = [
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/README.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/INVITATION_MESSAGE_DRAFT.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/PARTICIPANT_SCREENING_CHECKLIST.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/CONSENT_AND_BOUNDARY_SCRIPT.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_recruitment_consent/BOUNDARY_AUDIT.md",
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + block.rstrip() + "\n", encoding="utf-8")


def update_llms() -> None:
    text = LLMS.read_text(encoding="utf-8") if LLMS.exists() else ""
    missing = [p for p in LLMS_PATHS if p not in text]
    if missing:
        LLMS.write_text(text.rstrip() + "\n" + "\n".join(missing) + "\n", encoding="utf-8")


def update_agent_index() -> None:
    data = json.loads(AGENT_INDEX.read_text(encoding="utf-8")) if AGENT_INDEX.exists() else {}
    data["external_customer_validation_recruitment_consent_v0_1"] = SUMMARY
    AGENT_INDEX.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    write(OUT / "external_customer_validation_recruitment_consent.local.json", json.dumps(SUMMARY, indent=2, ensure_ascii=False))
    write(OUT / "README.md", README)
    write(OUT / "INVITATION_MESSAGE_DRAFT.md", INVITATION)
    write(OUT / "PARTICIPANT_SCREENING_CHECKLIST.md", SCREENING)
    write(OUT / "CONSENT_AND_BOUNDARY_SCRIPT.md", CONSENT)
    write(OUT / "BOUNDARY_AUDIT.md", BOUNDARY)
    write(GATE, GATE_TEXT)
    update_llms()
    update_agent_index()
    append_once(ROOT / "README.md", "external_customer_validation_recruitment_consent_v0_1=true", STATUS_BLOCK)
    append_once(ROOT / "PROJECT_STATUS.md", "external_customer_validation_recruitment_consent_v0_1=true", STATUS_BLOCK)
    append_once(ROOT / "ROADMAP.md", "external_customer_validation_recruitment_consent_v0_1=true", STATUS_BLOCK)
    append_once(ROOT / "CHANGELOG.md", "external_customer_validation_recruitment_consent_v0_1=true", STATUS_BLOCK)
    append_once(ROOT / "agent-readable.md", "external_customer_validation_recruitment_consent_v0_1=true", STATUS_BLOCK)
    print("SAEE_EXTERNAL_CUSTOMER_VALIDATION_RECRUITMENT_CONSENT: READY")


if __name__ == "__main__":
    main()
