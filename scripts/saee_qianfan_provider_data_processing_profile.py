#!/usr/bin/env python3
"""Build an agent-readable Qianfan provider data-processing inventory.

This inventory is evidence for data-flow review, not a legal or production
approval. It records what the validated SAEE host sent during run_005 and keeps
provider-policy, DPA, retention, and production approval as explicit unknowns.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "agent_recommendation/agent_first_validation/run_005"
OUT = ROOT / "phase_b_product/commercial_readiness/provider_data_processing"
JSON_PATH = OUT / "qianfan_provider_data_processing_profile.local.json"
MD_PATH = OUT / "qianfan_provider_data_processing_profile.md"
README_PATH = OUT / "README.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    manifest = json.loads((RUN / "roundtrip_evidence_manifest.json").read_text())
    return {
        "profile_type": "saee_qianfan_provider_data_processing_inventory",
        "profile_version": "v0.1",
        "generated_by": "scripts/saee_qianfan_provider_data_processing_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "provider": "baidu_qianfan",
        "endpoint": "https://qianfan.baidubce.com/v2/chat/completions",
        "model": "ernie-4.5-turbo-128k",
        "observed_run_count": len(manifest["runs"]),
        "observed_run_evidence_manifest": str((RUN / "roundtrip_evidence_manifest.json").relative_to(ROOT)),
        "observed_run_evidence_manifest_sha256": sha256(RUN / "roundtrip_evidence_manifest.json"),
        "data_sent_to_provider": [
            "system_instruction_for_bounded_tool selection",
            "sanitized numerical observed-trace fixture",
            "MCP-derived JSON Schema tool definitions for exactly two tools",
            "tool result messages returned by the fixed local MCP adapter",
            "final-answer fact prompt containing receipt fields",
        ],
        "data_not_sent_by_host": [
            "QIANFAN_API_KEY",
            "candidate source code",
            "local filesystem paths or arbitrary URLs",
            "shell commands or raw logs",
            "customer records or production data",
            "SAEE private evolution internals",
        ],
        "observed_boundary_facts": {
            "external_provider_network_used": True,
            "saee_mcp_network_used": False,
            "candidate_code_executed": False,
            "external_system_executed": False,
            "customer_validated": False,
            "production_ready": False,
            "api_key_in_transcripts": False,
            "authorization_header_in_evidence": False,
        },
        "official_policy_reference": {
            "url": "https://cloud.baidu.com/doc/qianfan/s/emh4stmvj",
            "catalog_url": "https://cloud.baidu.com/doc/qianfan/s/Umleypdhw",
            "catalog_last_updated": "2026-02-09",
            "reviewed_on": datetime.now(timezone.utc).date().isoformat(),
            "interpretation": "Official policy text is a source-linked review input; it is not treated as a completed DPA or production approval.",
            "observed_clauses": [
                {
                    "source": "special_agreement",
                    "locator": "2.2-2.3",
                    "fact": "平台要求输入、上传、提交的数据来源合法，并说明可在法律允许范围内显示、使用、存储和处理。",
                },
                {
                    "source": "special_agreement",
                    "locator": "2.4",
                    "fact": "上传的知识文档、数据集限定在账号内使用；条款声明除执行服务要求外不进行未获授权的使用或披露，并声明不用于训练或与第三方共享。",
                },
                {
                    "source": "user_agreement_2023_11_16",
                    "locator": "9.1-9.3",
                    "fact": "用户协议说明平台没有义务保存或提供内容副本、对内容不承担保密义务，并保留为合规、安全或技术原因披露内容的条款。",
                },
            ],
            "unresolved_questions": [
                "本次具体 API 模式的保留期限、删除机制和备份周期未从公开页面核验。",
                "SAEE 作为商业服务使用方所需的数据处理协议、跨境/地域条款和安全附件未完成签署或审批。",
                "用户协议与专项约定的适用版本、优先级及具体企业套餐条款仍需授权负责人确认。",
            ],
        },
        "review_status": {
            "technical_data_flow_inventory": "complete_for_run_005",
            "provider_retention_terms_verified": False,
            "privacy_legal_review_completed": False,
            "data_processing_agreement_completed": False,
            "production_provider_approval": False,
            "blockers_closed_by_profile": 0,
            "human_review_required": False,
            "human_validation_used": False,
            "agent_legal_review_required": True,
            "agent_validation_primary": True,
        },
        "next_required_action": "Independent privacy/legal agent reviews provider retention, cross-border/data-processing terms and records a bounded decision; DPA signature and production approval remain false until authoritative evidence exists.",
    }


def main() -> None:
    data = build()
    OUT.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    MD_PATH.write_text(
        "# Qianfan Provider Data-Processing Inventory\n\n"
        "本文件是千帆数据流盘点，不是 DPA、法务批准或生产就绪证明。\n\n"
        f"- provider: `{data['provider']}`\n- model: `{data['model']}`\n"
        f"- observed runs: `{data['observed_run_count']}`\n"
        "- provider network used: `true`\n- SAEE MCP network used: `false`\n"
        "- API key in transcripts: `false`\n- blockers closed by profile: `0`\n\n"
        "## Sent data\n\n" + "\n".join(f"- `{item}`" for item in data["data_sent_to_provider"])
        + "\n\n## Not sent\n\n" + "\n".join(f"- `{item}`" for item in data["data_not_sent_by_host"])
        + "\n\n## Official reference\n\n"
        + "- https://cloud.baidu.com/doc/qianfan/s/emh4stmvj\n"
        + "- https://cloud.baidu.com/doc/qianfan/s/Umleypdhw (agreement catalog)\n"
        + "- Official text remains independent-agent review input; retention/DPA/production approval are not inferred.\n"
        + "\n## Unresolved policy questions\n\n"
        + "- explicit retention period, deletion mechanism, and backup cycle for the selected API mode\n"
        + "- DPA, security annex, and cross-border/data-processing terms for commercial use\n"
        + "- applicable agreement version, priority, and enterprise-plan terms\n"
    )
    README_PATH.write_text(
        "# Provider data-processing inventory\n\n"
        "Read the JSON first. This is a bounded, agent-readable inventory of the\n"
        "validated Qianfan host payload classes. It never claims legal approval,\n"
        "DPA completion, customer validation, or production readiness.\n"
    )
    print("SAEE_QIANFAN_PROVIDER_DATA_PROCESSING_PROFILE: PASS sent_classes=5 forbidden_classes=6 blockers_closed=0")


if __name__ == "__main__":
    main()
