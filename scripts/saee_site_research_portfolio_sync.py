#!/usr/bin/env python3
"""Build the public-safe research and patent portfolio for the SAEE site."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_LEDGER = Path.home() / "GitHub" / "MANUSCRIPT_STATUS.md"
OUTPUT = ROOT / "sites/saee-commercial/public/research-portfolio.json"
PATENT_LEDGER = ROOT / "agent-interface/registry/public-patent-ledger.json"

PUBLIC_MANUSCRIPT_SELECTION = [
    {
        "line": "Digital Biosphere / Supercomputing",
        "group": "核心理论",
        "relevance": "为长期变化、竞争与生态世界模型提供理论来路。",
    },
    {
        "line": "SAEE / ALIFE 2026 LBA",
        "group": "核心理论",
        "relevance": "直接描述 SAEE 的反思性演化对象与长期稳定性问题。",
    },
    {
        "line": "JAAMAS / synthetic multi-agent parasitic transition benchmark",
        "group": "长期评估",
        "relevance": "用多智能体寄生转变基准检验长期退化与失败模式。",
    },
    {
        "line": "JSS / structural reviewability observational study",
        "group": "执行证据",
        "relevance": "研究真实智能体开发运行怎样形成可复核结构。",
    },
    {
        "line": "CSI / EEOAP",
        "group": "执行证据",
        "relevance": "定义可由验证器检查的智能体操作证据记录。",
    },
    {
        "line": "SP&E / agent-evidence practical experience",
        "group": "工程实现",
        "relevance": "记录从运行轨迹到证据验证工具的工程经验。",
    },
    {
        "line": "UDI-DICOM / JDIM-JIIM",
        "group": "应用验证",
        "relevance": "已发表的医疗影像证据映射工作，验证结构化证据方法的应用价值。",
    },
    {
        "line": "Public DICOM Metadata Audit / JDIM-JIIM",
        "group": "应用验证",
        "relevance": "用公开数据审计检验证据准备度，当前仍处大修阶段。",
    },
]

PUBLIC_PATENT_SELECTION = [
    {
        "id": "PAT-004",
        "group": "运行时控制",
        "relevance": "直接面向 API、RPA 与工具调用的多步智能体执行链。",
    },
    {
        "id": "PAT-008",
        "group": "生命周期",
        "relevance": "围绕智能体生命周期收据图验证与异常恢复边界。",
    },
    {
        "id": "PAT-009",
        "group": "高风险操作",
        "relevance": "围绕证据配置、校验与执行阻断，直接对应行动前判断。",
    },
    {
        "id": "PAT-010",
        "group": "执行证据",
        "relevance": "围绕智能体执行证据包的生成与离线验证。",
    },
    {
        "id": "PAT-013",
        "group": "策略约束",
        "relevance": "覆盖证据生成、策略约束、验证与问责的完整链路。",
    },
    {
        "id": "PAT-014",
        "group": "证据准入",
        "relevance": "围绕声明级证据准入和生命周期增量复验。",
    },
    {
        "id": "PAT-015",
        "group": "可信上下文",
        "relevance": "围绕逐陈述支持映射和智能体可信上下文构建。",
    },
]


def table_rows(block: str, expected_columns: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in block.splitlines():
        if not line.startswith("|"):
            continue
        columns = [cell.strip() for cell in line.strip("|").split("|")]
        if len(columns) < expected_columns:
            continue
        if columns[0] in {"线索", "---"} or columns[0].startswith("---"):
            continue
        rows.append(columns)
    return rows


def category(status: str) -> str:
    lowered = status.lower()
    if "在线发表" in status:
        return "published"
    if "major revisions requested" in lowered:
        return "major_revision"
    if any(token in status for token in ("拒稿", "关闭", "撤回", "取消提交")):
        return "closed_or_rewrite"
    if "不活跃" in status:
        return "historical_or_tracking"
    if any(token in lowered for token in ("活跃投稿", "active submission", "投稿已收到", "投稿确认；gmail", "under review")):
        return "active_or_tracking"
    return "historical_or_tracking"


def main() -> None:
    text = MANUSCRIPT_LEDGER.read_text(encoding="utf-8")
    main_block = text.split("\n## 状态表\n", 1)[1].split("\n## 范围外活跃状态占位", 1)[0]
    b4_block = text.split("\n## 范围外活跃状态占位", 1)[1].split("\n## 基线提醒", 1)[0]
    main_rows = table_rows(main_block, 8)
    b4_rows = table_rows(b4_block, 7)

    manuscripts = [
        {
            "line": row[0],
            "title": row[1],
            "venue": row[3],
            "status": row[4],
            "category": category(row[4]),
        }
        for row in main_rows
    ]
    b4 = [
        {
            "line": row[0],
            "title": row[1],
            "venue": row[3],
            "status": row[4],
            "category": category(row[4]),
        }
        for row in b4_rows
    ]
    patent_ledger = json.loads(PATENT_LEDGER.read_text(encoding="utf-8"))
    manuscript_lines = {item["line"] for item in manuscripts}
    patent_ids = {item["id"] for item in patent_ledger["records"]}
    missing_manuscripts = [item["line"] for item in PUBLIC_MANUSCRIPT_SELECTION if item["line"] not in manuscript_lines]
    missing_patents = [item["id"] for item in PUBLIC_PATENT_SELECTION if item["id"] not in patent_ids]
    if missing_manuscripts or missing_patents:
        raise ValueError(
            f"public selection references missing records: manuscripts={missing_manuscripts} patents={missing_patents}"
        )

    data = {
        "portfolio_id": "saee.public-research-ip-portfolio.v1",
        "synced_at": "2026-07-13",
        "organization": {
            "name": "山西游骑兵电子商务有限公司",
            "contact_name": "张斌",
            "public_phone": "18518485118",
        },
        "positioning": {
            "zh": "SAEE 不是孤立的单点程序，而是建立在持续研究、可复现实验、论文投稿反馈和专利储备之上的智能体上线准备评估技术。",
            "claim_boundary": "Research and patent-preparation assets support the engineering lineage; they do not by themselves prove production readiness, customer validation, patent grant, or universal scientific validity.",
        },
        "manuscript_summary": {
            "main_ledger_route_count": len(manuscripts),
            "high_risk_ai_placeholder_count": len(b4),
            "published_count": sum(item["category"] == "published" for item in manuscripts),
            "major_revision_count": sum(item["category"] == "major_revision" for item in manuscripts),
            "active_or_tracking_count": sum(item["category"] == "active_or_tracking" for item in manuscripts),
            "ledger_last_verified": "2026-07-06",
        },
        "manuscripts": manuscripts,
        "high_risk_ai_placeholder": b4,
        "patent_summary": {
            **patent_ledger["summary"],
            "ledger_source_file": patent_ledger["source"]["file_name"],
            "ledger_source_modified_at": patent_ledger["source"]["source_modified_at"],
            "public_claim": "15 user-ledger patent records; statuses are shown as recorded and do not imply grant or confirmed filing without official documents",
        },
        "patents": patent_ledger["records"],
        "public_selection": {
            "selection_policy": "Show only records with direct SAEE capability relevance or strong applied evidence-readiness value; preserve the full ledgers for machine verification.",
            "complete_manuscript_ledger_preserved": True,
            "complete_patent_ledger_preserved": True,
            "selected_manuscript_route_count": len(PUBLIC_MANUSCRIPT_SELECTION),
            "selected_patent_record_count": len(PUBLIC_PATENT_SELECTION),
            "manuscripts": PUBLIC_MANUSCRIPT_SELECTION,
            "patents": PUBLIC_PATENT_SELECTION,
        },
        "patent_truth_boundary": patent_ledger["truth_boundary"],
        "truth_boundary": {
            "all_manuscripts_published": False,
            "all_active_routes_peer_review_confirmed": False,
            "all_patents_formally_filed": False,
            "patents_granted": False,
            "production_ready": False,
            "customer_validated": False,
        },
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "SAEE_SITE_RESEARCH_PORTFOLIO_SYNC: PASS "
        f"manuscripts={len(manuscripts)} active_or_tracking={data['manuscript_summary']['active_or_tracking_count']} "
        f"patent_records={data['patent_summary']['record_count']} "
        f"confirmed_formal_filings={data['patent_summary']['confirmed_formal_filing_count']} "
        f"selected_manuscripts={data['public_selection']['selected_manuscript_route_count']} "
        f"selected_patents={data['public_selection']['selected_patent_record_count']}"
    )


if __name__ == "__main__":
    main()
